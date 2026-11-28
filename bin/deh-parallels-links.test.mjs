import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {test} from "node:test";
import {dehComparisonUrl, dehReadingUrl, josephusParallelBooks} from "../assets/js/dehParallelLinks.js";

const data = JSON.parse(readFileSync(new URL("../assets/data/deh-josephus-concordance.json", import.meta.url)));
const dehBase = "https://example.test/project/deh/";

for (const work of ["BJ", "AJ"]) {
  test(`${work} reverse lookup agrees with every closed reference in the concordance`, () => {
    const books = josephusParallelBooks(data, work);
    for (const [book, sections] of books) {
      for (const [section, matches] of sections) {
        const expected = data.records.flatMap(record => {
          const refs = record.josephus.targets.filter(ref => ref.work === work && ref.book === book
            && section >= ref.section_start && section <= ref.section_end);
          return refs.length ? [[record.id, {
            record, supplementary: refs.every(ref => ref.relationship_role === "supplementary_parallel")
          }]] : [];
        });
        assert.deepEqual([...matches], expected, `${work} ${book}.${section}`);
      }
    }
    for (const record of data.records) {
      for (const ref of record.josephus.targets.filter(target => target.work === work)) {
        for (let section = ref.section_start; section <= ref.section_end; section++) {
          assert(books.get(ref.book)?.get(section)?.has(record.id), `${work} ${ref.book}.${section} → ${record.id}`);
        }
      }
    }
  });
}

test("comparison links keep a valid originating section within a range", () => {
  const record = data.records.find(record => record.id === "deh-2-5-2");
  const url = dehComparisonUrl(dehBase, record, {work: "AJ", reference: "18.64", source: "aj_niese"});
  assert.equal(url.pathname, "/project/deh/");
  assert.deepEqual(Object.fromEntries(url.searchParams), {
    book: "2", chapter: "5", unit: "2", parallel: "deh-2-5-2", "deh-source": "pollard",
    "parallel-work": "AJ", "aj-source": "aj_niese", "parallel-ref": "18.64"
  });
  assert.equal(dehReadingUrl(url, record).href, `${dehBase}?book=2&chapter=5&unit=2`);
  const wrongWork = dehComparisonUrl(url, record, {work: "BJ", reference: "18.64"});
  assert(!wrongWork.searchParams.has("parallel-ref"));
  assert(!wrongWork.searchParams.has("aj-source"));
  assert.equal(wrongWork.searchParams.get("bj-source"), "whiston");
  const wrongSection = dehComparisonUrl(url, record, {work: "AJ", reference: "18.65"});
  assert(!wrongSection.searchParams.has("parallel-ref"));
});
