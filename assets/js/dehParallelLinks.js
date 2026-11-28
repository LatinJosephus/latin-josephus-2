import {bjTargets, publicationRecords, sources} from "./dehParallelsCore.js?v=20261109-bellum-i153";
import {ajSources} from "./dehAntiquitiesCore.js?v=20261014-aj-v1";

const comparisonParameters = ["parallel", "deh-source", "bj-source", "parallel-work", "aj-source", "parallel-ref"];

export function dehReadingUrl(base, record) {
  const url = new URL(base);
  for (const key of ["num", "niese", ...comparisonParameters]) url.searchParams.delete(key);
  url.searchParams.set("book", record.deh.book);
  url.searchParams.set("chapter", record.deh.chapter);
  url.searchParams.set("unit", record.deh.unit);
  url.hash = "";
  return url;
}

export function parallelReference(record, work, value) {
  const match = /^([1-9]\d*)\.([1-9]\d*)$/.exec(value);
  if (!match) return null;
  const book = Number(match[1]), section = Number(match[2]);
  return record.josephus.targets.some(target => target.work === work && target.book === book
    && target.section_start <= section && section <= target.section_end) ? {book, section} : null;
}

export function dehComparisonUrl(base, record, {
  dehSource = "pollard", work = bjTargets(record).length ? "BJ" : "AJ", source, reference
} = {}) {
  const url = dehReadingUrl(base, record);
  url.searchParams.set("parallel", record.id);
  url.searchParams.set("deh-source", dehSource);
  if (work === "AJ") {
    url.searchParams.set("parallel-work", work);
    url.searchParams.set("aj-source", Object.hasOwn(ajSources, source) ? source : "aj_whiston");
  } else {
    url.searchParams.set("bj-source", sources[source]?.work === "bellum" ? source : "whiston");
  }
  if (parallelReference(record, work, reference)) url.searchParams.set("parallel-ref", reference);
  return url;
}

// A Josephus section can be covered by several references to the same DEH unit.
export function josephusParallelBooks(data, work) {
  publicationRecords(data);
  const books = new Map();
  for (const record of data.records) {
    for (const target of record.josephus.targets) {
      if (target.work !== work) continue;
      if (!books.has(target.book)) books.set(target.book, new Map());
      const sections = books.get(target.book);
      for (let number = target.section_start; number <= target.section_end; number++) {
        if (!sections.has(number)) sections.set(number, new Map());
        const matches = sections.get(number);
        const supplementary = (matches.get(record.id)?.supplementary ?? true)
          && target.relationship_role === "supplementary_parallel";
        matches.set(record.id, {record, supplementary});
      }
    }
  }
  return books;
}
