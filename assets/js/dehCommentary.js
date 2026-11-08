const dataUrl = new URL("../data/deh-combined-commentary-en.json", import.meta.url);
const pane = document.getElementById("commentary");
const toggle = document.getElementById("commentary-pane-select");
const notes = document.getElementById("deh-commentary-notes");
const latin = document.getElementById("latin");
let catalogueRequest;
let renderVersion = 0;
let passageRendered = false;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

function loadCatalogue() {
  return catalogueRequest ||= fetch(dataUrl).then(async response => {
    if (!response.ok) throw new Error("Commentary data unavailable");
    const data = await response.json();
    if (data.schema_version !== 1 || data.work !== "deh" || !data.by_section) {
      throw new Error("Unsupported commentary data");
    }
    return data;
  }).catch(error => {
    catalogueRequest = undefined;
    throw error;
  });
}

function noteFigure(note, bodyTag) {
  const figure = element("figure");
  figure.dataset.noteId = note.id;
  const label = element("p", "deh-commentary-label", note.title || note.heading || note.lemma);
  if (note.lemma) label.lang = "la";
  if (note.heading_html || note.lemma_html) label.innerHTML = note.heading_html || note.lemma_html;
  if (label.hasChildNodes()) figure.append(label);
  const body = element(bodyTag);
  body.innerHTML = note.html;
  const reference = element("figcaption");
  reference.innerHTML = note.reference_html;
  figure.append(body, reference);
  return figure;
}

function sectionNotes(data, id, section) {
  const block = element("section", "deh-commentary-section");
  block.dataset.ussaniId = id;
  block.append(element("h4", "", section.citation));
  for (const key of data.group_order) {
    const entries = section.notes.filter(note => data.sources[note.source].group === key);
    if (!entries.length) continue;
    const group = data.groups[key];
    const source = element("div", `deh-commentary-source deh-commentary-source--${key}`);
    source.style.fontFamily = group.font_family;
    source.append(element("h5", "", group.label));
    const bodyTag = group.body_element === "blockquote" ? "blockquote" : "p";
    for (const note of entries) source.append(noteFigure(note, bodyTag));
    block.append(source);
  }
  return block;
}

function updateVisibility() {
  pane.hidden = !toggle.checked;
  pane.classList.toggle("hidden", pane.hidden);
}

function showStatus(message) {
  const status = element("p", "", message);
  status.setAttribute("role", "status");
  notes.replaceChildren(status);
}

async function refresh() {
  const version = ++renderVersion;
  updateVisibility();
  if (pane.hidden) return;
  const ids = [...latin.querySelectorAll('tei-p[id^="latin-deh"]')].map(paragraph => paragraph.id);
  if (!ids.length) {
    showStatus(passageRendered ? "No commentary for this view." : "Loading commentary…");
    return;
  }
  showStatus("Loading commentary…");
  try {
    const data = await loadCatalogue();
    if (version !== renderVersion) return;
    const visible = document.createDocumentFragment();
    for (const id of ids) {
      const section = data.by_section[id];
      if (section?.notes.length) visible.append(sectionNotes(data, id, section));
    }
    if (visible.childNodes.length) notes.replaceChildren(visible);
    else showStatus("No commentary for this passage.");
  } catch {
    if (version === renderVersion) showStatus("Commentary could not be loaded.");
  }
}

function readSelection() {
  toggle.checked = new URL(window.location.href).searchParams.get("commentary") === "1";
}

readSelection();
toggle.addEventListener("change", () => {
  const url = new URL(window.location.href);
  if (toggle.checked) url.searchParams.set("commentary", "1");
  else url.searchParams.delete("commentary");
  if (url.href !== window.location.href) window.history.pushState(window.history.state, "", url);
  refresh();
});
document.addEventListener("deh-view-rendered", () => {
  passageRendered = true;
  refresh();
});
window.addEventListener("popstate", () => {
  readSelection();
  // Wait for the reader to finish restoring the passage before showing its notes.
  renderVersion++;
  updateVisibility();
  if (!pane.hidden) showStatus("Loading commentary…");
});
refresh();
