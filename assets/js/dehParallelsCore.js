/* Shared publication and excerpt logic; canonical XML and editorial data are read-only. */
export const frozenSha = "c8f59a9bdfd8c49350b4d2656d1c685f4c4a63bd96450ddfd218ac3c07ca743c";
// v1 accepts the literal reviewed bytes or their exact LF checkout equivalent.
// Frozen sources reproduce their original SHA; the five approved Pollard v1.1
// files use explicit successor hashes, without rewriting the frozen concordance.
// No text/XML normalization occurs.
export const sourceIntegrityPolicy = "reviewed-crlf-or-exact-lf-v1";
export const pollardPublicationHashes = Object.freeze({
  1: "1f8a50242272c8cbb2fe2054c10e318cf00d0aab91b508eb1ca9e7a9e6a60b47",
  2: "e4c6a7357b6fcb5082b61b9528d7f8ae8a24ae2a5700fc5341752f2008218e5c",
  3: "f6c0c7ea4140e40bbe72d6a9293e5cbe6df73d15271d41d88d72a5eefd14e08c",
  4: "3f9c4873c13aae9d8adcbe11db5226eb794b2c363cc14ec106ff77dca95a6b54",
  5: "57654bac30bbc73d6447ec4180f9e51c65a6b6eb8835e1f86e15742a65188667"
});
const previousPollardHashes = Object.freeze({
  1: "6f8fd8d3250e7cc4540b7acdac9b62765e04b89b63cdd38376bd63ff9875a0c9",
  2: "49692bf96fb1b74be37a6a675e95fab19adca94cbec941b27c7872e667c1e693",
  3: "e5dc0d008801809385c8bcaf43c5ee2d42d861b572968e3ba6f6659543175d6b",
  4: "79068f7cbc2591b38fab9b36ee300d7e173ced0fab7e0dfac1668f56726445bc",
  5: "7658e545360849e75627a3ff771742d5fc06127da7613740c595c21e2aff5298"
});
export const romanBooks = ["", "I", "II", "III", "IV", "V", "VI", "VII"];
export const sources = {
  pollard: { work: "deh", language: "English", lang: "en", identity: "Pollard v1.1 — English translation of the Latin DEH." },
  ussani: { work: "deh", language: "Latin", lang: "la", identity: "Ussani (1932) — critical Latin text of DEH." },
  niese: { work: "bellum", language: "Greek", lang: "grc", identity: "Niese — Greek Bellum." },
  whiston: { work: "bellum", language: "English", lang: "en", identity: "Whiston — English translation of the Greek Bellum." },
  cardwell: { work: "bellum", language: "Latin", lang: "la", identity: "Cardwell (1837) — independent Latin translation of the Bellum." }
};
export const bjTargets = record => record.josephus.targets.filter(target => target.work === "BJ");
export const componentCitation = ref => `BJ ${romanBooks[ref.book]}.${ref.section_start}${
  ref.section_end !== ref.section_start ? `–${ref.section_end}` : ""
}`;

const positive = number => Number.isInteger(number) && number > 0;
export function publicationRecords(data) {
  if (data.status !== "reviewed_frozen" || data.review?.human_approved !== true
    || data.scope?.prologue_included !== false || !Array.isArray(data.records)
    || data.records.length !== data.scope.numbered_records) {
    throw new Error("The reviewed concordance is incomplete or unapproved.");
  }
  const ids = new Set();
  const canonicalIds = new Set();
  return data.records.filter(record => {
    const deh = record.deh;
    if (!deh || !positive(deh.book) || deh.book > 5 || !positive(deh.chapter) || !positive(deh.unit)
      || record.id !== `deh-${deh.book}-${deh.chapter}-${deh.unit}`
      || !new RegExp(`^latin-deh${deh.book}-num[1-9]\\d*$`).test(deh.xml_id)
      || ids.has(record.id) || canonicalIds.has(deh.xml_id)
      || record.josephus?.normalization_status !== "reviewed"
      || !Array.isArray(record.josephus.targets)) {
      throw new Error(`Invalid reviewed DEH identity: ${record.id}.`);
    }
    ids.add(record.id);
    canonicalIds.add(deh.xml_id);
    let previousOrder = 0;
    for (const target of record.josephus.targets) {
      if (!positive(target.order) || target.order <= previousOrder) {
        throw new Error(`Invalid reviewed component order: ${record.id}.`);
      }
      previousOrder = target.order;
      if (target.work !== "BJ") continue;
      if (!positive(target.book) || target.book > 7 || !positive(target.section_start)
        || !positive(target.section_end) || target.section_end < target.section_start
        || target.open_ended !== false || target.editorial_status !== "reviewed_recorded_parallel"
        || target.validation?.coordinate_status !== "passed" || target.validation.closed_reference !== true
        || !["Greek", "Latin", "English"].every(source => target.validation.sources?.[source] === true)
        || !["primary_parallel", "supplementary_parallel"].includes(target.relationship_role)
        || target.parenthetical !== (target.relationship_role === "supplementary_parallel")) {
        throw new Error(`Invalid reviewed BJ target: ${record.id}, component ${target.order}.`);
      }
    }
    return bjTargets(record).length > 0;
  });
}

const sha256 = async bytes => [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))]
  .map(byte => byte.toString(16).padStart(2, "0")).join("");

async function checkedBytes(response, expectedHash, label, allowLFCheckout = false) {
  if (!response.ok) throw new Error(`Could not load ${label}.`);
  const bytes = new Uint8Array(await response.arrayBuffer());
  let hash = await sha256(bytes);
  if (expectedHash && hash !== expectedHash && allowLFCheckout && !bytes.includes(13)) {
    // Git's LF serialization removes CR from CRLF. Reconstruct ONLY that exact
    // representation, byte for byte, and verify against the reviewed authority.
    // Bare CR, mixed endings, BOM changes and every other byte change fail closed.
    const restored = new Uint8Array(bytes.length + bytes.filter(byte => byte === 10).length);
    let offset = 0;
    for (const byte of bytes) {
      if (byte === 10) restored[offset++] = 13;
      restored[offset++] = byte;
    }
    hash = await sha256(restored);
  }
  if (!expectedHash || hash !== expectedHash) throw new Error(`${label} differs from the frozen reviewed authority.`);
  return new TextDecoder().decode(bytes);
}

export async function loadConcordance(url) {
  return JSON.parse(await checkedBytes(await fetch(url), frozenSha, "concordance"));
}

export function createTextLoader(xmlBase, hashes) {
  const cache = new Map();
  const tei = new CETEI();
  return (sourceKey, book) => {
    const key = `${sourceKey}:${book}`;
    if (!cache.has(key)) {
      const source = sources[sourceKey];
      const path = `${source.work}/${source.language}/book-${String(book).padStart(2, "0")}.xml`;
      const url = new URL(path, xmlBase);
      cache.set(key, fetch(url).then(async response => {
        let expectedHash = hashes[`assets/xml/${path}`];
        if (sourceKey === "pollard") {
          if (expectedHash !== previousPollardHashes[book]) throw new Error(`${sourceKey} Book ${book} differs from the frozen reviewed authority.`);
          expectedHash = pollardPublicationHashes[book];
        }
        const text = await checkedBytes(response, expectedHash, `${sourceKey} Book ${book}`, true);
        const xml = new DOMParser().parseFromString(text, "text/xml");
        if (xml.querySelector("parsererror")) throw new Error(`Invalid XML for ${sourceKey}.`);
        return tei.domToHTML5(xml);
      }).catch(error => {
        cache.delete(key);
        throw error;
      }));
    }
    return cache.get(key);
  };
}

export const dehParagraphs = (data, record, sourceKey) => [...data.querySelectorAll("tei-body tei-p")]
  .filter(paragraph => sourceKey === "ussani" ? paragraph.id === record.deh.xml_id
    : (paragraph.getAttribute("sameAs") || "").split(/\s+/)
      .some(target => target.split("#").pop() === record.deh.xml_id));

// Index each loaded source once. Only body text supplies excerpt boundaries;
// annotations in standOff/back matter never enter comparison excerpts.
export function bellumIndex(data, sourceKey, book) {
  const body = data.querySelector("tei-body");
  if (!body) throw new Error("Bellum body text is unavailable.");
  let entries;
  if (sourceKey === "niese") {
    const prefix = `greek-bellum${book}-num`;
    entries = [...body.querySelectorAll("tei-p")]
      .filter(node => node.id.startsWith(prefix) && /^[1-9]\d*$/.test(node.id.slice(prefix.length)))
      .map(node => ({ number: Number(node.id.slice(prefix.length)), node, wholeSection: true }));
  } else {
    entries = [...body.querySelectorAll('tei-milestone[unit="niese"][n]')]
      .filter(node => /^[1-9]\d*$/.test(node.getAttribute("n")))
      .map(node => ({ number: Number(node.getAttribute("n")), node, paragraph: false }));
    if (sourceKey === "cardwell") {
      const prefix = `latin-bellum${book}-num`;
      body.querySelectorAll("tei-p").forEach(node => {
        if (!node.id.startsWith(prefix)) return;
        const number = node.id.slice(prefix.length);
        if (/^[1-9]\d*$/.test(number) && new RegExp(`^\\s*\\[\\s*${number}\\s*\\]`).test(node.textContent)) {
          entries.push({ number: Number(number), node, paragraph: true });
        }
      });
    }
    entries.sort((a, b) => a.node === b.node ? 0 : (
      a.node.compareDocumentPosition(b.node) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1
    ));
  }
  // Loaded XML is SHA-checked against the frozen authority. Require complete,
  // consecutive anchors before treating the body end as a final-section boundary.
  if (!entries.length || entries.some((entry, index) => entry.number !== index + 1)) {
    throw new Error(`BJ Book ${book} has incomplete or repeated source boundaries.`);
  }
  return { entries, body };
}

export function bellumSection(index, number) {
  const start = index.entries[number - 1];
  const end = index.entries[number];
  if (!start || start.number !== number || (end && end.number !== number + 1)) {
    throw new Error(`BJ section ${number} lacks a complete source boundary.`);
  }
  const wrapper = document.createElement("tei-div2");
  wrapper.dataset.nieseSection = number;
  if (start.wholeSection) {
    const paragraph = start.node.cloneNode(true);
    const label = document.createElement("tei-num");
    label.className = "niese-generated";
    label.textContent = `[${number}] `;
    paragraph.prepend(label);
    wrapper.appendChild(paragraph);
  } else {
    const startParagraph = start.paragraph ? start.node : start.node.closest("tei-p");
    const endParagraph = end ? (end.paragraph ? end.node : end.node.closest("tei-p")) : null;
    const range = document.createRange();
    if (start.paragraph) range.setStartBefore(start.node);
    else range.setStartAfter(start.node);
    if (end) range.setEndBefore(end.node);
    else range.setEnd(index.body, index.body.childNodes.length);
    if (startParagraph && startParagraph === endParagraph) {
      if (start.paragraph) range.setStart(startParagraph, 0);
      const paragraph = startParagraph.cloneNode(false);
      paragraph.appendChild(range.cloneContents());
      wrapper.appendChild(paragraph);
    } else wrapper.appendChild(range.cloneContents());
    wrapper.querySelectorAll("tei-p").forEach(paragraph => {
      if (!paragraph.textContent.trim() && !paragraph.querySelector("tei-milestone, tei-num")) paragraph.remove();
    });
    if (!start.paragraph) {
      const label = document.createElement("tei-num");
      label.className = "niese-generated";
      label.textContent = `[${number}] `;
      wrapper.querySelector("tei-p")?.prepend(label);
    }
  }
  if (!wrapper.textContent.replace(/\[\d+\]/g, "").trim()) throw new Error(`BJ section ${number} is empty.`);
  return wrapper;
}

export function namespaceIds(fragment, prefix) {
  const elements = [fragment, ...fragment.querySelectorAll("*")];
  const ids = new Map();
  elements.forEach(element => {
    if (element.id) {
      ids.set(element.id, `${prefix}-${element.id}`);
      element.id = ids.get(element.id);
    }
  });
  elements.forEach(element => {
    const href = element.getAttribute("href");
    if (href?.startsWith("#") && ids.has(href.slice(1))) element.setAttribute("href", `#${ids.get(href.slice(1))}`);
  });
  return fragment;
}
