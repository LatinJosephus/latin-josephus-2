const editions = new URL("../data/antiquities-froben1524/", import.meta.url);
const requests = new Map();
const modes = {
  running: "Text · current reading view",
  book: "Complete Froben text",
  division: "Printed division",
  page: "Scan page"
};
const preferences = ["froben", "froben-view", "froben-location", "froben-unit", "froben-pages", "froben-align"];

function locationState() {
  const params = new URLSearchParams(window.location.search);
  const view = params.get("froben-view");
  return {
    enabled: params.get("froben") === "1",
    mode: Object.hasOwn(modes, view) ? view : "running",
    location: params.get("froben-location"),
    unit: params.get("froben-unit"),
    pages: params.get("froben-pages") === "1",
    highlight: params.get("froben-align") !== "0"
  };
}

function bookData(book) {
  if (!requests.has(book)) {
    const filename = book === "preface" ? "preface" : `book-${book.padStart(2, "0")}`;
    requests.set(book, fetch(new URL(`${filename}.json`, editions)).then(response => {
      if (!response.ok) throw new Error("The Froben text for this book is unavailable.");
      return response.json();
    }).then(data => {
      if (data.book.id !== book) throw new Error("The Froben book file does not match the requested book.");
      return data;
    }).catch(error => {
      requests.delete(book);
      throw error;
    }));
  }
  return requests.get(book);
}

const element = (tag, text, attributes = {}) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  return node;
};
const flowHeading = text => text.replace(/¬[ \t]*\r?\n\s*/g, "").replace(/\s+/g, " ").trim();
const pointKey = ([image, id]) => `${image}:${id}`;
const unitLabel = id => `Bamberg alignment unit ${id.split("-num").at(-1)}`;
const nieseLabel = number => element("tei-num", `[${number}]`, {class: "niese-generated froben-niese-number"});

function indexBook(data) {
  const rows = [];
  const byRow = new Map();
  let offset = 0;
  for (const page of data.pages) {
    for (const row of page.rows) {
      const chars = Array.from(row.text);
      byRow.set(pointKey([page.image, row.id]), rows.length);
      rows.push({...row, chars, page, offset});
      offset += chars.length;
    }
  }
  const terminal = data.pages.at(-1).span.end;
  if (!byRow.has(pointKey(terminal))) byRow.set(pointKey(terminal), rows.length);
  const point = location => {
    const i = byRow.get(pointKey(location));
    const cp = location[2];
    if (i === undefined || cp < 0 || cp > (rows[i]?.chars.length ?? 0)) {
      throw new Error("A Froben reading location could not be resolved.");
    }
    return {i, cp, offset: (rows[i]?.offset ?? offset) + cp};
  };
  const moved = new Set();
  const placed = new Map();
  const approved = new Map();
  for (const division of data.divisions) {
    if (!division.headingSpan) continue;
    const first = point(division.headingSpan.start).i;
    const end = point(division.headingSpan.end).i;
    if (division.approvedHeading) approved.set(first, {end, text: flowHeading(division.approvedHeading)});
    if (division.headingBefore) {
      placed.set(point(division.headingBefore).i, {first, end});
      for (let i = first; i < end; i++) moved.add(i);
    }
  }
  const byId = new Map([data.book, ...data.chapters, ...data.subchapters, ...data.alignmentUnits,
    ...data.niese, ...data.divisions].map(entry => [entry.id, entry]));
  const offsets = item => (item?.spans || []).map(span => [point(span.start).offset, point(span.end).offset]);
  const units = new Map(data.alignmentUnits.filter(item => item.spans.length).map(item => [item.id, offsets(item)]));
  const links = [...units].flatMap(([id, ranges]) => ranges.map(([lo, hi]) => [lo, hi, id]));
  const nieseStarts = new Map();
  for (const {number, spans, status} of data.niese) {
    // An overlapping date phrase can label its own excerpt but is not a new section in the running text.
    if (!spans.length || status === "parallel-partial") continue;
    const {i, cp} = point(spans[0].start);
    const starts = nieseStarts.get(rows[i]) || [];
    starts.push([cp, number]);
    nieseStarts.set(rows[i], starts);
  }
  return {rows, point, moved, placed, approved, byId, offsets, units, links, nieseStarts};
}

function sliceRows(index, span, placeHeadings) {
  const {rows, point, moved, placed, approved} = index;
  const first = point(span.start);
  const end = point(span.end);
  const stop = end.i + Number(end.cp > 0);
  const parts = [];
  const add = (row, cp, text) => {
    if (row.role === "scan-apparatus" || row.joinedInto || !text.trim()) return;
    parts.push({row, cp, text});
  };
  for (let i = first.i; i < stop; i++) {
    const cp = i === first.i ? first.cp : 0;
    const inserted = placeHeadings && cp === 0 && placed.get(i);
    if (inserted) {
      for (let j = inserted.first; j < inserted.end; j++) add(rows[j], 0, rows[j].text);
    }
    if (moved.has(i)) continue;
    const corrected = approved.get(i);
    if (corrected && cp === 0 && corrected.end <= end.i) {
      add(rows[i], 0, corrected.text);
      i = corrected.end - 1;
      continue;
    }
    add(rows[i], cp, rows[i].chars.slice(cp, i === end.i ? end.cp : undefined).join(""));
  }
  return parts;
}

function appendReading(root, parts, pages, shown, scanLink, intervals, nieseStarts) {
  let paragraph;
  let previous;
  for (const [i, {row, cp, text}] of parts.entries()) {
    const heading = row.role === "heading";
    const sameFlow = previous && previous.heading === heading;
    if (!sameFlow) {
      paragraph = element("p", undefined, {class: heading ? "froben-heading" : "froben-paragraph"});
      root.append(paragraph);
    } else if (!previous.continues) {
      paragraph.append(" ");
    }
    const firstOnPage = !shown.has(row.page.id);
    if (firstOnPage) {
      paragraph.append(element("span", undefined, {id: row.page.id, class: "froben-page-anchor"}));
      shown.add(row.page.id);
    }
    const content = (heading ? text.replace(/^# /, "") : text).trimEnd();
    const next = parts[i + 1];
    const continues = content.endsWith("¬") && next && (next.row.role === "heading") === heading;
    const chars = Array.from(continues ? content.slice(0, -1) : content);
    const line = element("span", undefined, {class: "froben-line", "data-source-row": row.id});
    const start = row.offset + cp;
    const ranges = heading ? [] : intervals.filter(([lo, hi]) => lo < start + chars.length && hi > start);
    const cuts = new Set([0, chars.length]);
    for (const [lo, hi] of ranges) {
      cuts.add(Math.max(0, lo - start));
      cuts.add(Math.min(chars.length, hi - start));
    }
    const starts = nieseStarts.get(row) || [];
    for (const [offset] of starts) {
      if (cp <= offset && offset < cp + chars.length) cuts.add(offset - cp);
    }
    const markPage = firstOnPage && pages;
    // Put an optional page label after the continuation of a divided word.
    const afterWord = markPage && sameFlow && previous.continues;
    const wordEnd = afterWord ? chars.findIndex(char => /\s/.test(char)) : -1;
    const labelAt = afterWord ? (wordEnd < 0 ? chars.length : wordEnd) : 0;
    if (markPage) cuts.add(labelAt);
    const edges = [...cuts].sort((a, b) => a - b);
    for (let i = 0; i < edges.length; i++) {
      const lo = edges[i];
      if (markPage && lo === labelAt) {
        const label = scanLink(row.page, `[${row.page.display}]`);
        label.classList.add("froben-page-label");
        line.append(label);
      }
      if (i + 1 === edges.length) continue;
      for (const [offset, number] of starts) {
        if (offset === cp + lo) line.append(nieseLabel(number));
      }
      const hi = edges[i + 1];
      const textPart = chars.slice(lo, hi).join("");
      const matches = ranges.filter(([a, b]) => a <= start + lo && start + hi <= b);
      const targets = [...new Set(matches.map(([, , id]) => id).filter(Boolean))];
      const highlight = matches.some(([, , id]) => !id);
      if (!highlight && !targets.length) {
        line.append(textPart);
        continue;
      }
      const part = element(highlight ? "mark" : "span", textPart, {class: highlight ? "froben-aligned" : "froben-linked"});
      if (targets.length) {
        part.classList.add("froben-linked");
        part.dataset.frobenTargets = targets.join(" ");
      }
      line.append(part);
    }
    paragraph.append(line);
    previous = {heading, continues};
  }
}

function start() {
  const pane = document.getElementById("froben");
  const toggle = document.getElementById("froben-pane-select");
  const latin = document.getElementById("latin");
  if (!pane || !toggle || !latin) return;
  let state = locationState();
  let navigation;
  let data;
  let index;
  let generation = 0;
  let settingsOpen = false;
  let correspondenceOpen = false;
  toggle.checked = state.enabled;

  function writeUrl(push = false) {
    const url = new URL(window.location.href);
    preferences.forEach(key => url.searchParams.delete(key));
    if (state.enabled) {
      url.searchParams.set("froben", "1");
      if (state.mode !== "running") url.searchParams.set("froben-view", state.mode);
      if (state.location && ["division", "page"].includes(state.mode)) url.searchParams.set("froben-location", state.location);
      if (state.unit) url.searchParams.set("froben-unit", state.unit);
      if (state.pages) url.searchParams.set("froben-pages", "1");
      if (!state.highlight) url.searchParams.set("froben-align", "0");
    }
    if (url.href !== window.location.href) history[push ? "pushState" : "replaceState"]({}, "", url);
  }

  function scanLink(page, text) {
    // The Basel facsimile starts at canvas 27897205 for source image 66 and runs consecutively.
    const canvas = 27897205 + (page.image - 66);
    const href = pane.dataset.scanBase
      ? new URL(encodeURIComponent(page.file), new URL(pane.dataset.scanBase, location.href))
      : new URL(String(canvas), "https://www.e-rara.ch/bau_1/content/pageview/");
    return element("a", text, {href: href.href, target: "_blank", rel: "noopener"});
  }

  function select(id, label, values, current, change) {
    const menu = element("select", undefined, {id});
    values.forEach(([value, text]) => menu.add(new Option(text, value)));
    menu.value = current || "";
    menu.addEventListener("change", () => change(menu.value));
    const control = element("label", label, {for: id});
    control.append(menu);
    return control;
  }

  function checkbox(id, label, checked, change) {
    const input = element("input", undefined, {id, type: "checkbox"});
    input.checked = checked;
    input.addEventListener("change", () => change(input.checked));
    const control = element("label", undefined, {for: id, class: "froben-checkbox"});
    control.append(input, label);
    return control;
  }

  function update(changes) {
    Object.assign(state, changes);
    writeUrl(true);
    render();
  }

  function bambergTargets(id) {
    const key = CSS.escape(id);
    return latin.querySelectorAll(`[id="${key}"], [sameAs~="#${key}"], [sameAs~="${key}"]`);
  }

  function unitUrl(id) {
    const url = new URL(location.href);
    ["chapter", "subchapter", "niese", "bamberg", "view", "num", "froben-unit"]
      .forEach(key => url.searchParams.delete(key));
    url.searchParams.set("book", navigation.book);
    url.searchParams.set("unit", id.split("-num").at(-1));
    url.hash = "";
    return url;
  }

  function chooseUnit(id, locate = false) {
    if (!index.units.has(id)) return;
    const target = bambergTargets(id)[0];
    if (locate && !target) {
      window.location.assign(unitUrl(id).href);
      return;
    }
    update({unit: id});
    if (locate) target.scrollIntoView({block: "center"});
  }

  function render() {
    const focus = pane.contains(document.activeElement) ? document.activeElement.id : null;
    pane.replaceChildren(element("h3", "Latin: Froben 1524"));
    latin.querySelectorAll(".froben-bamberg-target").forEach(node => node.classList.remove("froben-bamberg-target"));
    const active = index.byId.get(state.unit || navigation.target);
    let selected = active;
    const native = data.divisions;
    const pages = data.pages;
    const isNative = state.mode === "division" || state.mode === "page";
    if (state.mode === "book") selected = data.book;
    if (isNative) {
      const candidates = state.mode === "division" ? native : pages;
      selected = candidates.find(entry => entry.id === state.location) || candidates[0];
      state.location = selected?.id || null;
    }

    const controls = element("div", undefined, {class: "froben-controls", "aria-label": "Froben reading controls"});
    const toolbar = element("div", undefined, {class: "froben-toolbar"});
    const settings = element("details", undefined, {id: "froben-settings"});
    settings.open = settingsOpen;
    settings.addEventListener("toggle", () => { if (settings.isConnected) settingsOpen = settings.open; });
    settings.append(element("summary", "Settings"), select("froben-view", "Froben display", Object.entries(modes),
      state.mode, mode => update({mode, location: null})));
    if (state.mode === "division") {
      settings.append(select("froben-division", "Printed division",
        native.map(d => [d.id, flowHeading(d.label || d.id)]), state.location, location => update({location})));
    }
    if (state.mode === "page") {
      settings.append(select("froben-page", "Scan page", pages.map(p => [p.id, p.display]),
        state.location, location => update({location})));
      const at = pages.findIndex(page => page.id === state.location);
      const steps = element("div", undefined, {class: "froben-toolbar"});
      for (const [delta, label] of [[-1, "Previous page"], [1, "Next page"]]) {
        const button = element("button", label, {type: "button"});
        const target = pages[at + delta];
        button.disabled = !target;
        button.addEventListener("click", () => update({location: target.id}));
        steps.append(button);
      }
      settings.append(steps);
    }
    settings.append(checkbox("froben-pages", "Show printed page labels", state.pages, pages => update({pages})));
    settings.append(select("froben-unit", "Aligned passage", [["", "Follow the reader"],
      ...[...index.units.keys()].map(id => [id, unitLabel(id)])], state.unit, unit => {
      if (unit) chooseUnit(unit, true);
      else update({unit: null});
    }));
    toolbar.append(element("a", "About", {href: pane.dataset.about, "aria-label": "About the Froben 1524 edition"}),
      settings, checkbox("froben-highlight", "Highlight correspondences", state.highlight,
      highlight => update({highlight})), element("a", "Link", {id: "froben-share", href: location.href,
      "aria-label": "Link to this Froben view"}));
    controls.append(toolbar);

    const related = active?.id === data.book.id ? [] : index.offsets(active);
    const targets = index.units.has(active?.id) ? [active.id] : [...index.units].filter(([, ranges]) =>
      ranges.some(([a, b]) => related.some(([lo, hi]) => a < hi && lo < b))).map(([id]) => id);
    if (state.highlight) {
      targets.forEach(id => bambergTargets(id).forEach(node => node.classList.add("froben-bamberg-target")));
    }
    const correspondence = element("details", undefined, {id: "froben-correspondence"});
    correspondence.open = correspondenceOpen;
    correspondence.addEventListener("toggle", () => {
      if (correspondence.isConnected) correspondenceOpen = correspondence.open;
    });
    correspondence.append(element("summary", "Correspondence"));
    if (targets.length) {
      const list = element("ul");
      for (const id of targets) {
        const li = element("li");
        li.append(element("a", unitLabel(id), {href: unitUrl(id).href}));
        list.append(li);
      }
      correspondence.append(list);
    } else {
      const message = active && active.id !== data.book.id ? "No Bamberg alignment unit is recorded for this selection."
        : "Select a passage or alignment unit to see its recorded correspondences.";
      correspondence.append(element("p", message));
    }
    controls.append(correspondence);
    pane.append(controls);

    const reading = element("section", undefined, {id: "froben-source", lang: "la",
      "aria-label": "Froben Latin transcription"});
    const spans = selected?.span ? [selected.span] : selected?.spans || [];
    const nieseNumber = selected?.id.startsWith("niese-") ? selected.number : null;
    const page = selected?.file ? selected : pages.find(p =>
      p.image === (spans[0]?.start[0] ?? selected?.location?.[0]));
    if (state.pages && page) {
      const locator = element("p", undefined, {class: "froben-locator", lang: "en"});
      locator.append(scanLink(page, `${page.display} · Image ${page.image}`));
      const signatures = page.signatures.map(s => s.label).filter(Boolean);
      if (state.mode === "page" && signatures.length) locator.append(` · Signature ${signatures.join(", ")}`);
      reading.append(locator);
    }
    if (selected?.note || !spans.length) {
      const notice = element("p", selected?.note || "Choose a shared passage, printed division, or scan page.",
        {class: "froben-notice", lang: "en", role: "note"});
      if (nieseNumber !== null && !spans.length) notice.prepend(nieseLabel(nieseNumber));
      reading.append(notice);
    }
    const shown = new Set();
    const intervals = state.highlight ? [...related, ...index.links] : [];
    let nieseStarts = index.nieseStarts;
    if (nieseNumber !== null && spans.length) {
      const {i, cp} = index.point(spans[0].start);
      nieseStarts = new Map([[index.rows[i], [[cp, nieseNumber]]]]);
    }
    for (const [i, span] of spans.entries()) {
      if (spans.length > 1) reading.append(element("p", `Fragment ${i + 1}`, {class: "froben-locator", lang: "en"}));
      appendReading(reading, sliceRows(index, span, isNative || selected.id === data.book.id),
        state.pages, shown, scanLink, intervals, nieseStarts);
    }
    reading.addEventListener("click", event => {
      const match = event.target.closest("[data-froben-targets]");
      if (!match || window.getSelection()?.type === "Range") return;
      const ids = match.dataset.frobenTargets.split(" ");
      if (ids.length === 1) {
        chooseUnit(ids[0], true);
        return;
      }
      const picker = element("div", undefined, {class: "froben-target-picker"});
      picker.append(element("p", "Choose a Bamberg alignment unit for these words."));
      for (const id of ids) {
        const button = element("button", unitLabel(id), {type: "button"});
        button.addEventListener("click", () => chooseUnit(id, true));
        picker.append(button);
      }
      correspondence.querySelector(".froben-target-picker")?.remove();
      correspondence.append(picker);
      correspondence.open = correspondenceOpen = true;
      picker.querySelector("button")?.focus();
    });
    pane.append(reading);
    pane.dataset.frobenReady = navigation.book;
    pane.dataset.frobenSelection = selected?.id || "";
    writeUrl();
    document.getElementById("froben-share").href = location.href;
    if (focus) document.getElementById(focus)?.focus({preventScroll: true});
  }

  async function refresh() {
    const version = ++generation;
    pane.hidden = !state.enabled;
    pane.classList.toggle("hidden", !state.enabled);
    delete pane.dataset.frobenReady;
    if (!state.enabled) {
      latin.querySelectorAll(".froben-bamberg-target").forEach(node => node.classList.remove("froben-bamberg-target"));
      return;
    }
    if (!navigation) return;
    const {book, available} = navigation;
    if (!available) {
      pane.replaceChildren(element("h3", "Latin: Froben 1524"),
        element("p", "Choose a supported Antiquities passage.", {role: "status"}));
      return;
    }
    try {
      if (data?.book.id !== book) {
        pane.replaceChildren(element("h3", "Latin: Froben 1524"),
          element("p", "Loading Froben text…", {role: "status"}));
        const loaded = await bookData(book);
        if (version !== generation) return;
        index = indexBook(loaded);
        data = loaded;
      }
      if (!index.units.has(state.unit)) state.unit = null;
      render();
    } catch (error) {
      if (version === generation) pane.replaceChildren(element("h3", "Latin: Froben 1524"),
        element("p", error.message, {role: "alert"}));
    }
  }

  document.addEventListener("antiquities-view-rendered", event => {
    if (navigation && (navigation.book !== event.detail.book || navigation.target !== event.detail.target)) state.unit = null;
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

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
else start();
