import {loadConcordance} from "./dehParallelsCore.js?v=20261109-bellum-i153";
import {dehComparisonUrl, josephusParallelBooks} from "./dehParallelLinks.js?v=20261127-reciprocal-parallels";

const sourcesByWork = {
  BJ: {latin: ["ussani", "cardwell"], english: ["pollard", "whiston"], greek: ["ussani", "niese"]},
  AJ: {latin: ["ussani", "aj_latin"], english: ["pollard", "aj_whiston"], greek: ["ussani", "aj_niese"]}
};
const nonNarrative = "tei-teiheader, tei-note, tei-app, tei-rdg, tei-back, .structural-unavailable, [data-original]";

const inlineLocations = (pane, section) => {
  // Section view already knows the exact reference, including a section starting mid-paragraph.
  if (section !== null) {
    const paragraph = [...pane.querySelectorAll("tei-p")].findLast(node =>
      !node.hidden && !node.closest(nonNarrative) && node.textContent.trim());
    return paragraph ? [[paragraph, [section]]] : [];
  }

  const locations = new Map();
  for (const marker of pane.querySelectorAll("[data-deh-parallel-sections]")) {
    const paragraph = marker.closest("tei-p");
    if (!paragraph || paragraph.hidden || marker.closest(nonNarrative)) continue;
    if (!locations.has(paragraph)) locations.set(paragraph, new Set());
    const sections = locations.get(paragraph);
    marker.dataset.dehParallelSections.split(" ").forEach(number => sections.add(Number(number)));
  }
  return locations;
};

const reader = document.getElementById("pane-container");
if (reader?.dataset.work) {
  const {work, dehUrl, alignmentUrl} = reader.dataset;
  const dehBase = new URL(dehUrl, window.location.href);
  const workName = work === "AJ" ? "Antiquities" : "Bellum";
  let books, pending, view;

  const updateLinks = () => {
    reader.querySelectorAll(".josephus-parallel-link").forEach(link => link.remove());
    const book = Number(view.book);
    const sections = books.get(book);
    if (!view.available || view.level === "contents-level" || !sections) return;

    const exact = view.level === "niese-level";
    const selection = exact ? view.section : null;
    if (exact && !sections.has(selection)) return;

    for (const [language, [dehSource, source]] of Object.entries(sourcesByWork[work])) {
      const pane = reader.querySelector(`#${language}`);
      if (!pane) continue;

      for (const [paragraph, numbers] of inlineLocations(pane, selection)) {
        const links = [];
        for (const section of numbers) {
          const matches = sections.get(section);
          if (!matches) continue;

          for (const {record, supplementary} of matches.values()) {
            const link = document.createElement("a");
            const reference = `${book}.${section}`;
            const destination = `DEH${matches.size > 1 ? ` ${record.deh.citation}` : ""}`;
            const qualifier = supplementary ? " (supplementary)" : "";
            link.className = "deh-parallel-link josephus-parallel-link";
            link.href = dehComparisonUrl(dehBase, record, {work, source, dehSource, reference});
            link.textContent = `Compare${exact ? "" : ` §${section}`} with ${destination}${qualifier}`;
            link.setAttribute("aria-label", `Compare ${workName} ${reference} with DEH ${record.deh.citation}${qualifier}`);
            links.push(link);
          }
        }
        if (links.length) paragraph.after(...links);
      }
    }
  };

  const viewEvent = work === "AJ" ? "antiquities-view-rendered" : "bellum-view-rendered";
  document.addEventListener(viewEvent, event => {
    // The rendered view may precede the corresponding URL update.
    view = event.detail;
    if (books) {
      updateLinks();
    } else if (!pending && view.available && view.level !== "contents-level" && Number(view.book) > 0) {
      pending = loadConcordance(alignmentUrl).then(data => {
        books = josephusParallelBooks(data, work);
        updateLinks();
      }).catch(error => {
        console.warn("Could not load DEH parallels.", error);
      }).finally(() => { pending = null; });
    }
  });
}
