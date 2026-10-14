/* Derived AJ display only. The frozen concordance and certified XML remain read-only. */
export const ajSources = {
  aj_niese: {language: "Greek", lang: "grc", identity: "Niese — Greek Antiquitates Judaicae.", readerKey: "niese"},
  aj_latin: {language: "Latin", lang: "la", identity: "Antiquities Latin — Bamberg Msc. Class. 78 (project transcription).", readerKey: "bamberg78"},
  aj_whiston: {language: "English", lang: "en", identity: "Whiston — English translation of Greek Antiquitates Judaicae.", readerKey: "whiston"}
};
export const ajTargets = record => record.josephus.targets.filter(target => target.work === "AJ");
const sha = async bytes => [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map(b => b.toString(16).padStart(2,"0")).join("");
async function checked(url, hash, label) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Could not load ${label}.`);
  const bytes = await response.arrayBuffer();
  if (!hash || await sha(bytes) !== hash) throw new Error(`${label} differs from the AJ display authority.`);
  return new TextDecoder().decode(bytes);
}
export async function loadAjLayer(url, expectedHash, concordance) {
  const layer = JSON.parse(await checked(url, expectedHash, "AJ display layer"));
  if (layer.schema_version !== 1 || layer.concordance_sha256 !== "c8f59a9bdfd8c49350b4d2656d1c685f4c4a63bd96450ddfd218ac3c07ca743c") throw new Error("Unrecognized AJ display authority.");
  const expected = concordance.records.filter(r => ajTargets(r).length);
  if (layer.records.length !== expected.length) throw new Error("Incomplete AJ display coverage.");
  layer.records.forEach((r,i) => {
    const source = expected[i], targets = ajTargets(source);
    if (r.id !== source.id || r.deh_xml_id !== source.deh.xml_id || r.components.length !== targets.length
      || r.components.some((c,j) => JSON.stringify(c.frozen_target) !== JSON.stringify(targets[j]))) throw new Error("AJ display targets differ from the frozen concordance.");
  });
  return layer;
}
export function createAjTextLoader(xmlBase, layer) {
  const cache = new Map(), tei = new CETEI();
  return (sourceKey, book) => {
    const source = ajSources[sourceKey];
    if (!source) throw new Error("Unknown AJ witness.");
    const relative = `antiquities/${source.language}/book-${String(book).padStart(2,"0")}.xml`;
    if (!cache.has(relative)) cache.set(relative, checked(new URL(relative,xmlBase),layer.source_sha256[`assets/xml/${relative}`],`${source.identity} Book ${book}`).then(text => {
      const xml = new DOMParser().parseFromString(text,"text/xml");
      if (xml.querySelector("parsererror")) throw new Error("Invalid Antiquities XML.");
      return tei.domToHTML5(xml);
    }).catch(error => {cache.delete(relative);throw error;}));
    return cache.get(relative);
  };
}
function locate(body, point) {
  let node = body;
  for (const index of point.path) {
    node = node.children[index];
    if (!node) throw new Error("AJ certified boundary is unavailable.");
  }
  return node;
}
export function ajSection(data, section) {
  const wrapper = document.createElement("tei-div2");
  wrapper.dataset.nieseSection = section.number;
  if (!section.available) {
    const gap = document.createElement("p");gap.className = "structural-unavailable";gap.setAttribute("role","status");
    gap.textContent = section.note || "This section is unavailable in this witness. No nearby text has been substituted.";
    wrapper.dataset.sourceAvailable = "false";wrapper.append(gap);return wrapper;
  }
  const body = data.querySelector("tei-body");
  if (!body) throw new Error("AJ body is unavailable.");
  for (const span of section.spans) {
    const start = locate(body,span.start);let end = locate(body,span.end);
    // A preserved [N] immediately before the next Niese milestone belongs to
    // that next interval. Exclude its label-only prefix at the same boundary.
    if (span.end.side === "before" && end.matches('tei-milestone[unit="niese"]')) {
      let previous = end.previousSibling;
      while (previous?.nodeType === Node.TEXT_NODE && !previous.textContent.trim()) previous = previous.previousSibling;
      const numbers = previous?.nodeType === Node.ELEMENT_NODE && previous.matches("tei-num") ? previous.textContent.match(/\d+/g) : null;
      if (numbers && Number(numbers.at(-1)) === Number(end.getAttribute("n"))) end = previous;
    }
    const range = document.createRange();
    const set = (point,node,isStart) => {
      if (point.side === "before") isStart ? range.setStartBefore(node) : range.setEndBefore(node);
      else if (point.side === "after") isStart ? range.setStartAfter(node) : range.setEndAfter(node);
      else {const offset = point.side === "end" ? node.childNodes.length : 0;isStart ? range.setStart(node,offset) : range.setEnd(node,offset);}
    };
    set(span.start,start,true);set(span.end,end,false);
    if (range.collapsed) throw new Error("Empty AJ source boundary.");
    let fragment = range.cloneContents();
    // Preserve inline ancestors when both boundaries fall within a quotation or emphasis.
    let ancestor = range.commonAncestorContainer;
    if (ancestor.nodeType !== Node.ELEMENT_NODE) ancestor = ancestor.parentElement;
    const paragraph = start.closest("tei-p");
    if (paragraph && paragraph.contains(end)) {
      while (ancestor && ancestor !== paragraph) {const shell = ancestor.cloneNode(false);shell.append(fragment);fragment = shell;ancestor = ancestor.parentElement;}
      const shell = paragraph.cloneNode(false);shell.append(fragment);fragment = shell;
    }
    wrapper.append(fragment);
  }
  for (const id of section.excludedParagraphs || []) wrapper.querySelectorAll("tei-p[id]").forEach(p => {if(p.id===id)p.remove();});
  if (!wrapper.textContent.replace(/\[\s*\d+\s*\]/g,"").trim()) throw new Error("AJ excerpt is empty.");
  const label = document.createElement("tei-num");label.className="niese-generated";label.textContent=`[${section.number}] `;wrapper.prepend(label);
  if (section.note) {const note=document.createElement("p");note.className="niese-correspondence-note";note.setAttribute("role","note");note.textContent=section.note;wrapper.prepend(note);}
  return wrapper;
}
