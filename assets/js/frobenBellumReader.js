import {
  modes, preferences, locationState, element, flowHeading, indexText, sliceRows, appendReading,
  selectControl, checkbox, frobenControls, pageSteps, latinTargets, correspondingUnits, correspondenceDetails
} from "./frobenReader.js?v=20261126-froben-bellum";

const pane = document.getElementById("froben");
const toggle = document.getElementById("froben-pane-select");
const latin = document.getElementById("latin");
const targetClass = "froben-cardwell-target";
const heading = () => element("h3", "Latin: Froben 1524");
const scanLink = (page, label) => element("a", label,
  {href: page.facsimile, target: "_blank", rel: "noopener noreferrer"});
const pageLabel = page => page.display.startsWith("Image ") ? page.display : page.display + " · Image " + page.image;
const chapterLabel = chapter => chapter.kind === "chapter-heading"
  ? chapter.label + " · " + flowHeading(chapter.rubric) : chapter.label;
const unitNumber = id => id.split("-num").at(-1);
const unitLabel = id => "Cardwell alignment unit " + unitNumber(id);

function start() {
  let state = locationState();
  let navigation;
  let request;
  let data;
  let index;
  let generation = 0;
  let settingsOpen = false;
  let correspondenceOpen = false;
  toggle.checked = state.enabled;

  function writeUrl(push = false) {
    const url = new URL(location.href);
    preferences.forEach(key => url.searchParams.delete(key));
    if (state.enabled) {
      url.searchParams.set("froben", "1");
      if (state.mode !== "running") {
        url.searchParams.set("froben-view", state.mode);
        if (state.location) url.searchParams.set("froben-location", state.location);
      }
      if (state.unit) url.searchParams.set("froben-unit", state.unit);
      if (state.pages) url.searchParams.set("froben-pages", "1");
      if (!state.highlight) url.searchParams.set("froben-align", "0");
    }
    if (url.href !== location.href) history[push ? "pushState" : "replaceState"](null, "", url);
  }

  function entries(mode) {
    return {book: data.frobenBooks, division: data.divisions, page: data.pages}[mode];
  }

  function selectionAt(mode, point) {
    if (mode === "running") return null;
    const candidates = entries(mode);
    const offset = index.point(point).offset;
    const contains = entry => {
      const span = entry.span || entry.spans[0];
      return index.point(span.start).offset <= offset && offset < index.point(span.end).offset;
    };
    const selected = candidates.find(contains);
    if (selected || mode !== "division") return selected || candidates[0];
    const book = data.frobenBooks.find(contains);
    return candidates.find(chapter => chapter.frobenBook === book?.id) || candidates[0];
  }

  function update(changes) {
    Object.assign(state, changes);
    writeUrl(true);
    render();
  }

  function unitUrl(id) {
    const unit = index.byId.get(id);
    const url = new URL(location.href);
    ["chapter", "subchapter", "niese", "bamberg", "view", "num", "froben-unit"]
      .forEach(key => url.searchParams.delete(key));
    url.searchParams.set("book", unit.book.replace("latin-bellum", ""));
    url.searchParams.set("unit", unitNumber(id));
    url.hash = "";
    return url;
  }

  function chooseUnit(id, locate = false) {
    if (!index.units.has(id)) return;
    const target = latinTargets(latin, id)[0];
    if (locate && !target) {
      location.assign(unitUrl(id).href);
      return;
    }
    update({unit: id});
    if (locate) target.scrollIntoView({block: "center"});
  }

  function clearHighlights() {
    latin.querySelectorAll("." + targetClass).forEach(node => node.classList.remove(targetClass));
  }

  function render() {
    const focus = pane.contains(document.activeElement) ? document.activeElement.id : "";
    settingsOpen = pane.querySelector("#froben-settings")?.open ?? settingsOpen;
    correspondenceOpen = pane.querySelector("#froben-correspondence")?.open ?? correspondenceOpen;
    const canonicalBook = index.byId.get("latin-bellum" + navigation.book);
    const active = navigation.available ? index.byId.get(state.unit || navigation.target) : null;
    const start = (active || canonicalBook || data.books[0]).spans[0].start;
    let selected = active;
    if (state.mode !== "running") {
      selected = entries(state.mode).find(entry => entry.id === state.location) || selectionAt(state.mode, start);
      state.location = selected.id;
    }
    const span = selected && (selected.span || selected.spans[0]);
    const page = span && data.pages.find(entry => entry.image === span.start[0]);
    const nativeBook = state.mode === "book" ? selected : index.byId.get(selected?.frobenBook);

    const {controls, settings, share} = frobenControls({
      about: pane.dataset.about, settingsOpen, onSettingsToggle: open => { settingsOpen = open; },
      highlight: state.highlight, onHighlight: highlight => update({highlight})
    });
    settings.append(selectControl("froben-view", "Froben display", Object.entries(modes), state.mode,
      mode => update({mode, location: selectionAt(mode, span?.start || start)?.id || null})));
    if (nativeBook) {
      settings.append(selectControl("froben-book", "Printed book", data.frobenBooks.map(book => [book.id, book.label]),
        nativeBook.id, id => update({location: state.mode === "book" ? id :
          data.divisions.find(chapter => chapter.frobenBook === id).id})));
    }
    if (state.mode === "division") {
      const chapters = data.divisions.filter(chapter => chapter.frobenBook === selected.frobenBook);
      settings.append(selectControl("froben-division", "Printed division", chapters.map(item => [item.id, chapterLabel(item)]),
        selected.id, id => update({location: id})));
    }
    if (state.mode === "page") {
      const folios = new Map();
      for (const item of data.pages) {
        folios.set(item.display, (folios.get(item.display) || 0) + 1);
      }
      const pages = data.pages.map(item => [item.id, folios.get(item.display) > 1 ? pageLabel(item) : item.display]);
      settings.append(selectControl("froben-page", "Scan page", pages, selected.id, id => update({location: id})),
        pageSteps(data.pages, selected.id, id => update({location: id})));
    }
    settings.append(checkbox("froben-pages", "Show printed page labels", state.pages, pages => update({pages})));
    const units = data.subchapters.filter(unit => unit.book === canonicalBook?.id);
    settings.append(selectControl("froben-unit", "Aligned passage", [["", "Follow the reader"],
      ...units.map(unit => [unit.id, unitLabel(unit.id)])], state.unit, unit => {
      if (unit) chooseUnit(unit, true);
      else update({unit: null});
    }));

    const {related, targets} = correspondingUnits(index, active, canonicalBook?.id);
    clearHighlights();
    if (state.highlight) {
      targets.forEach(id => latinTargets(latin, id).forEach(node => node.classList.add(targetClass)));
    }
    controls.append(correspondenceDetails({
      targets, label: unitLabel, href: id => unitUrl(id).href,
      open: correspondenceOpen, onToggle: open => { correspondenceOpen = open; },
      message: "Select a passage or alignment unit to see its recorded correspondences."
    }));

    const reading = element("section", undefined, {id: "froben-source", lang: "la",
      "aria-label": "Froben Latin transcription"});
    if (state.pages && page) {
      const locator = element("p", undefined, {class: "froben-locator", lang: "en"});
      locator.append(scanLink(page, pageLabel(page)));
      reading.append(locator);
    }
    if (span) {
      const shown = new Set();
      const intervals = state.highlight ? [...related, ...index.links] : [];
      const formatNiese = state.mode === "running" ? label => label.split(".").at(-1) : label => label;
      for (const interval of selected.spans || [span]) {
        appendReading(reading, sliceRows(index, interval, false), state.pages, shown, scanLink, intervals,
          index.nieseStarts, formatNiese);
      }
    } else {
      reading.append(element("p", "Choose a passage in the reader or a printed Froben division.",
        {class: "froben-notice", lang: "en", role: "status"}));
    }
    reading.addEventListener("click", event => {
      const target = event.target.closest("[data-froben-targets]");
      if (target && window.getSelection()?.type !== "Range") chooseUnit(target.dataset.frobenTargets.split(" ")[0], true);
    });
    pane.replaceChildren(heading(), controls, reading);
    if (state.mode === "page" && page?.marginalia.length) {
      const notes = element("details", undefined, {class: "froben-marginalia"});
      notes.append(element("summary", "Printed marginalia"),
        element("p", page.marginalia.join("\n"), {lang: "la"}));
      pane.append(notes);
    }
    let citation = nativeBook ? selected.label : null;
    if (state.mode === "page") citation = [selectionAt("book", span.start).label, pageLabel(page)].join(", ");
    if (state.mode === "running" && state.unit && active) citation = "Cardwell " + active.label;
    if (citation) pane.dataset.citationReference = citation;
    else delete pane.dataset.citationReference;
    pane.dataset.frobenReady = navigation.book;
    pane.dataset.frobenSelection = selected?.id || "";
    writeUrl();
    share.href = location.href;
    if (focus) document.getElementById(focus)?.focus({preventScroll: true});
  }

  async function refresh() {
    const version = ++generation;
    pane.hidden = !state.enabled;
    pane.classList.toggle("hidden", !state.enabled);
    delete pane.dataset.frobenReady;
    if (!state.enabled) {
      clearHighlights();
      return;
    }
    if (!navigation) return;
    try {
      if (!data) {
        pane.replaceChildren(heading(), element("p", "Loading Froben text…", {role: "status"}));
        request ||= fetch(pane.dataset.bellumSource).then(response => {
          if (!response.ok) throw new Error("The Froben text is unavailable.");
          return response.json();
        }).catch(error => {
          request = null;
          throw error;
        });
        const loaded = await request;
        if (version !== generation) return;
        index = indexText({...loaded, alignmentUnits: loaded.subchapters}, entry => entry.label);
        data = loaded;
      }
      if (state.unit && (!index.units.has(state.unit) ||
          index.byId.get(state.unit).book !== "latin-bellum" + navigation.book)) state.unit = null;
      render();
    } catch (error) {
      if (version === generation) pane.replaceChildren(heading(), element("p", error.message, {role: "alert"}));
    }
  }

  document.addEventListener("bellum-view-rendered", event => {
    if (navigation && navigation.target !== event.detail.target) state.unit = null;
    navigation = event.detail;
    refresh();
  });
  toggle.addEventListener("change", () => {
    state.enabled = toggle.checked;
    writeUrl(true);
    refresh();
  });
  latin.addEventListener("click", event => {
    if (!state.enabled || !index || event.target.closest("a") || window.getSelection()?.type === "Range") return;
    const paragraph = event.target.closest("tei-p[id], tei-p[sameAs]");
    if (!paragraph) return;
    const ids = [paragraph.id, ...(paragraph.getAttribute("sameAs") || "").split(/\s+/).map(id => id.replace(/^#/, ""))];
    const unit = ids.find(id => index.units.has(id));
    if (unit) chooseUnit(unit);
  });
  window.addEventListener("popstate", () => {
    state = locationState();
    toggle.checked = state.enabled;
    navigation = undefined;
    refresh();
  });
  refresh();
}

if (pane?.dataset.bellumSource && toggle && latin) start();
