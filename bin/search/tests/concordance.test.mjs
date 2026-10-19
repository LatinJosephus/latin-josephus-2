import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { buildBundle, createEngine, tokenizeText } from "../engine.mjs";
import { buildConcordance, exportConcordance } from "../concordance.mjs";

const require = createRequire(import.meta.url);
const lunr = require("../vendor/lunr.cjs");
const readerBase = "https://example.org/project/";
const exportedAt = "2026-10-18T23:45:00.000Z";
function record(section, text, extra = {}) {
  return {
    id: `bellum-latin-cardwell-1-${section}`, sourceId: `latin-bellum1-num${section}`,
    work: "bellum", collectionId: "bellum-latin-cardwell", bookId: "bellum-latin-cardwell:1",
    citationPrefix: "Bellum", language: "Latin", edition: "Cardwell (1837)", readerPath: "bellum-judaicum/",
    book: 1, section, order: section - 1, text, url: `/bellum-judaicum/?book=1&niese=${section}`, ...extra,
  };
}
function search(records, query, options = {}) {
  const engine = createEngine(buildBundle(records, lunr), lunr);
  const result = { ...engine.search(query, options), records,
    selectedBooks: [...new Set(records.map((item) => item.bookId))], selectedCollections: [...new Set(records.map((item) => item.collectionId))] };
  return { result, model: buildConcordance(result, records, { readerBase, contextWords: options.contextWords ?? 10 }) };
}

// An independent RFC-4180-style reader checks embedded commas, quotes and line
// endings rather than assuming one physical line per exported result.
function parseCSV(text) {
  assert.equal(text[0], "\uFEFF");
  const output = [], row = [];
  let quoted = false, cell = "";
  for (let i = 1; i < text.length; i += 1) {
    const char = text[i];
    if (char === '"') {
      if (quoted && text[i + 1] === '"') { cell += '"'; i += 1; }
      else quoted = !quoted;
    } else if (!quoted && char === ",") { row.push(cell); cell = ""; }
    else if (!quoted && char === "\r" && text[i + 1] === "\n") {
      row.push(cell); cell = ""; output.push(row.splice(0)); i += 1;
    } else cell += char;
  }
  assert.equal(quoted, false, "all quoted cells must close");
  assert.equal(cell, "", "export must end with a record delimiter");
  const headers = output.shift();
  return { headers, rows: output.map((values) => {
    assert.equal(values.length, headers.length, "every CSV row has the full schema");
    return Object.fromEntries(headers.map((header, index) => [header, values[index]]));
  }) };
}

test("each original word occurrence gets a row, including repeated hits in one section", () => {
  const records = [record(1, "Bellum, bellum; BELLUM."), record(2, "Bellorum bell.")];
  const snapshot = JSON.stringify(records);
  const { result, model } = search(records, "bellum");
  assert.equal(model.countKind, "word");
  assert.equal(model.occurrenceCount, 3);
  assert.equal(model.positiveCount, 3);
  assert.equal(result.matchingSections, 1);
  assert.deepEqual(model.rows.map((row) => row.match), ["Bellum", "bellum", "BELLUM"]);
  assert.equal(new Set(model.rows.map((row) => row.key)).size, 3);
  assert.equal(model.rows[0].records[0], records[0], "source records remain shared, unchanged references");
  assert.equal(model.rows[0].citation, "Bellum I.1");
  assert.equal(model.rows[0].readerURL, "https://example.org/project/bellum-judaicum/?book=1&niese=1");
  assert.equal(JSON.stringify(records), snapshot);
});

test("wildcards count matching forms while retaining their source spellings", () => {
  const { model } = search([record(1, "bell bellum Bellorum rebellum")], "bell*");
  assert.equal(model.countKind, "word");
  assert.equal(model.occurrenceCount, 3, "the bare form matches zero additional characters");
  assert.deepEqual(model.rows.map((row) => row.match), ["bell", "bellum", "Bellorum"]);
});

test("quoted phrases count as phrases, including distinct overlapping occurrences", () => {
  const { model } = search([record(1, "a, a; a!")], '"a a"');
  assert.equal(model.countKind, "phrase");
  assert.equal(model.occurrenceCount, 2);
  assert.deepEqual(model.rows.map((row) => row.match), ["a, a", "a; a"]);
  assert.equal(search([record(1, "a a")], '"a"').model.countKind, "phrase");
  assert.equal(search([record(1, "a a")], "(((a)))").model.occurrenceCount, 2);
});

test("Boolean evidence deduplicates equal geometry but preserves overlaps and operand identities", () => {
  const records = [record(1, "Rex Roma Rex.")];
  const { model } = search(records, 'Rex OR Rex* OR "Rex" OR "Rex Roma"');
  assert.equal(model.countKind, "evidence");
  assert.equal(model.occurrenceCount, null);
  assert.equal(model.positiveCount, 3);
  assert.deepEqual(model.rows.map((row) => row.match), ["Rex", "Rex Roma", "Rex"]);
  assert.deepEqual(model.rows[0].queryTexts, ["Rex", "Rex*", '"Rex"']);
  assert.equal(search(records, "Rex AND Rex").model.positiveCount, 2);
  assert.equal(search(records, "NOT NOT Rex").model.occurrenceCount, null, "Boolean syntax is not labelled a word frequency");
});

test("only evidence from successful Boolean branches appears", () => {
  const records = [record(1, "rex Roma"), record(2, "regina Roma")];
  const { model } = search(records, "(rex AND absent) OR regina");
  assert.deepEqual(model.rows.map((row) => row.match), ["regina"]);
  assert.equal(model.positiveCount, 1);
  assert.equal(model.occurrenceCount, null);
});

test("a NOT-only section is an explicit matching unit, with no invented occurrence", () => {
  const records = [record(1, "rex"), record(2, "regina, Roma.")];
  const { model, result } = search(records, "NOT rex");
  assert.equal(model.rows.length, 0);
  assert.equal(model.positiveCount, 0);
  assert.equal(model.occurrenceCount, null);
  assert.equal(model.unhighlightedUnits.length, 1);
  const unit = model.unhighlightedUnits[0];
  assert.equal(unit.kind, "matching-unit");
  assert.equal(unit.scope, "section");
  assert.equal(unit.citation, "Bellum I.2");
  assert.deepEqual(unit.spans, []);
  assert.equal(unit.match, "");
  const row = parseCSV(exportConcordance(model, result, { exportedAt }).text).rows[0];
  assert.equal(row.row_type, "matching-unit");
  assert.equal(row.matched_text, "");
  assert.equal(row.occurrence_count, "");
  assert.equal(JSON.parse(row.source_segments_json)[0].text, records[1].text);
});

test("a NOT-only book with empty engine recordIds retains its complete unit identity", () => {
  const records = [record(1, "rex"), record(2, "regina")];
  const { result, model } = search(records, "NOT absent", { scope: "book" });
  assert.deepEqual(result.hitGroups[0].recordIds, []);
  assert.equal(model.rows.length, 0);
  assert.equal(model.unhighlightedUnits.length, 1);
  const unit = model.unhighlightedUnits[0];
  assert.equal(unit.citation, "Bellum I");
  assert.equal(unit.readerURL, "https://example.org/project/bellum-judaicum/?book=1");
  assert.deepEqual(unit.records, records);
  const exported = parseCSV(exportConcordance(model, result, { exportedAt }).text).rows;
  assert.equal(exported.length, 1);
  assert.equal(exported[0].row_type, "matching-unit");
  assert.deepEqual(JSON.parse(exported[0].source_segments_json), [], "a whole book is not fabricated as a match excerpt");
  assert.deepEqual(JSON.parse(exported[0].record_ids_json), records.map((item) => item.id));
  const group = result.hitGroups[0];
  const merged = { ...result, hitGroups: [{ ...group, ...records[0], unitId: `bellum-latin-cardwell:1:${group.unitId}` }] };
  assert.equal(buildConcordance(merged, records, { readerBase }).unhighlightedUnits[0].edition, "Cardwell (1837)");
});

test("mixed positive and negative-only Boolean units are all represented in export", () => {
  const { result, model } = search([record(1, "rex"), record(2, "regina"), record(3, "Roma")], "rex OR NOT regina");
  assert.equal(model.rows.length, 1);
  assert.equal(model.unhighlightedUnits.length, 1);
  const rows = parseCSV(exportConcordance(model, result, { exportedAt }).text).rows;
  assert.deepEqual(rows.map((row) => [row.citation, row.row_type]), [["Bellum I.1", "positive-evidence"], ["Bellum I.3", "matching-unit"]]);
  assert.ok(rows.every((row) => row.occurrence_count === ""));
});

test("a cross-section phrase is one row with its citation range and original boundary punctuation", () => {
  const records = [record(86, "Ante haec habebantur."), record(87, "At Theodorus repente venit.")];
  assert.equal(search(records, '"habebantur At Theodorus"').model.occurrenceCount, 0);
  const { model, result } = search(records, '"habebantur At Theodorus"', { scope: "book" });
  assert.equal(model.rows.length, 1);
  assert.equal(model.occurrenceCount, 1);
  const row = model.rows[0];
  assert.equal(row.citation, "Bellum I.86–87");
  assert.equal(row.left, "Ante haec ");
  assert.equal(row.match, "habebantur. At Theodorus");
  assert.equal(row.right, " repente venit.");
  assert.deepEqual(row.spans.map((span) => span.recordId), records.map((item) => item.id));
  const exported = parseCSV(exportConcordance(model, result, { exportedAt }).text).rows[0];
  const source = JSON.parse(exported.source_segments_json);
  assert.equal(source.map((segment) => segment.joinBefore + segment.text).join(""), row.left + row.match + row.right);
  assert.deepEqual(JSON.parse(exported.hit_spans_json), row.spans);
});

test("cross-section text retains existing whitespace, punctuation-only sections, and leading punctuation", () => {
  const records = [record(1, "ante finis.\n"), record(2, " [ ] "), record(3, "« Initium post.")];
  const { model } = search(records, '"finis Initium"', { scope: "book" });
  assert.equal(model.rows[0].match, "finis.\n [ ] « Initium");
  assert.equal(model.rows[0].citation, "Bellum I.1–3");
  assert.deepEqual(model.rows[0].records, records, "intervening zero-token sections retain their text");
  assert.equal(model.rows[0].left + model.rows[0].match + model.rows[0].right, records.map((item) => item.text).join(""));
});

test("ten-word context preserves original whitespace and punctuation without exceeding the cited section", () => {
  const before = Array.from({ length: 12 }, (_, index) => `ante${index + 1}`).join("; ");
  const after = Array.from({ length: 12 }, (_, index) => `post${index + 1}`).join(",\n");
  const records = [record(1, "neighbor word"), record(2, `${before}: Bellum! ${after}.`), record(3, "following neighbor")];
  const { model } = search(records, "Bellum", { scope: "book" });
  const row = model.rows[0];
  assert.equal(tokenizeText(row.left).length, 10);
  assert.equal(tokenizeText(row.right).length, 10);
  assert.equal(row.left, `${before.slice(before.indexOf("ante3"))}: `);
  assert.equal(row.right, `! ${after.slice(0, after.indexOf("post11"))}`);
  assert.equal(row.leftTruncated, true);
  assert.equal(row.rightTruncated, true);
  assert.deepEqual(row.records, [records[1]]);
  assert.equal(row.contextSpans[0].start, records[1].text.indexOf("ante3"));
});

test("short contexts remain complete and a zero-word request has empty context", () => {
  const records = [record(1, "  [ante] Bellum: post.\r\n")];
  const normal = search(records, "Bellum").model.rows[0];
  assert.equal(normal.left, "  [ante] ");
  assert.equal(normal.right, ": post.\r\n");
  assert.equal(normal.leftTruncated, false);
  assert.equal(normal.rightTruncated, false);
  const zero = search(records, "Bellum", { contextWords: 0 }).model.rows[0];
  assert.equal(zero.left, "");
  assert.equal(zero.right, "");
  assert.equal(zero.leftTruncated, true);
  assert.equal(zero.rightTruncated, true);
});

test("declared gaps and book boundaries are never crossed by matches or contexts", () => {
  const records = [record(1, "finis"), record(2, "initium", { breakBefore: true }),
    record(1, "liber", { id: "book2", book: 2, bookId: "bellum-latin-cardwell:2" })];
  assert.equal(search(records, '"finis initium"', { scope: "book" }).model.rows.length, 0);
  assert.equal(search(records, '"initium liber"', { scope: "book" }).model.rows.length, 0);
  const { model } = search(records, "initium OR liber", { scope: "book" });
  assert.ok(model.rows.every((row) => row.left === "" && row.right === ""));
  assert.deepEqual(model.rows.map((row) => row.citation), ["Bellum I.2", "Bellum II.1"]);
  const corrupt = { query: '"finis initium"', scope: "book", hitGroups: [{ recordIds: records.slice(0, 2).map((item) => item.id), hits: [{
    kind: "phrase", spans: [{ recordId: records[0].id, start: 0, end: 5 }, { recordId: records[1].id, start: 0, end: 7 }],
  }] }] };
  assert.throws(() => buildConcordance(corrupt, records, { readerBase }), /declared text gap/);
});

test("works and editions with overlapping section numbers retain distinct identities and source order", () => {
  const records = [record(1, "rex", { order: 10, resultOrder: 0 }),
    record(1, "rex", { id: "latin-other-1", collectionId: "bellum-latin-other", bookId: "bellum-latin-other:1", edition: "Other", order: 0, resultOrder: 1 }),
    record(1, "rex", { id: "ant-1", work: "antiquities", collectionId: "antiquities-latin", bookId: "antiquities-latin:1", citationPrefix: "Antiquities", readerPath: "antiquities/", order: 0, resultOrder: 2 })];
  const { model, result } = search(records, "rex");
  assert.deepEqual(model.rows.map((row) => row.collectionId), records.map((item) => item.collectionId));
  assert.deepEqual(model.rows.map((row) => row.citation), ["Bellum I.1", "Bellum I.1", "Antiquities I.1"]);
  assert.equal(model.rows[2].readerURL, "https://example.org/project/antiquities/?book=1&niese=1");
  assert.equal(new Set(model.rows.map((row) => row.key)).size, 3);
  assert.deepEqual(parseCSV(exportConcordance(model, result, { exportedAt }).text).rows.map((row) => row.collection_id), records.map((item) => item.collectionId));
});

test("Greek combining marks, astral letters and optional Latin folding keep original UTF-16 spans", () => {
  const records = [record(1, "𐌀𐌁 ἀρχή. Judaei viri.")];
  const greek = search(records, "ἀρχή").model.rows[0];
  assert.equal(greek.match, "ἀρχή");
  assert.equal(greek.spans[0].start, 5);
  const astral = search(records, "𐌀𐌁").model.rows[0];
  assert.deepEqual(astral.spans, [{ recordId: records[0].id, start: 0, end: 4 }]);
  assert.equal(astral.match, "𐌀𐌁");
  const folded = search(records, '"Iudaei uiri"', { fold: true }).model.rows[0];
  assert.equal(folded.match, "Judaei viri");
  assert.equal(search(records, '"Iudaei uiri"').model.rows.length, 0);
});

test("CSV preserves commas, quotes and original newlines and neutralizes spreadsheet formula prefixes losslessly", () => {
  const records = [record(1, '=SUM(1,2)\r\nBellum, "quoted".\n+post', { edition: "@formula" })];
  const { result, model } = search(records, "-bellum");
  const file = exportConcordance(model, result, { exportedAt, searchURL: "\t=HYPERLINK(bad)" });
  assert.equal(file.mimeType, "text/csv;charset=utf-8");
  assert.equal(file.filename, "LatinJosephus-search-2026-10-18.csv");
  const { headers, rows } = parseCSV(file.text);
  assert.deepEqual(headers.slice(0, 7), ["citation", "left_context", "matched_text", "right_context", "edition", "language", "reader_url"]);
  const row = rows[0];
  assert.equal(row.left_context, "'=SUM(1,2)\r\n");
  assert.equal(row.right_context, ', "quoted".\n+post');
  assert.equal(row.edition, "'@formula");
  assert.equal(row.query, "'-bellum");
  assert.equal(row.search_url, "'\t=HYPERLINK(bad)");
  assert.deepEqual(JSON.parse(row.escaped_columns_json), ["left_context", "edition", "query", "search_url"]);
  assert.deepEqual(JSON.parse(row.original_context_json), { left: model.rows[0].left, match: model.rows[0].match, right: model.rows[0].right });
  assert.equal(JSON.parse(row.query_json), result.query);
  assert.equal(JSON.parse(row.source_segments_json)[0].text, records[0].text);
});

test("formula protection includes leading whitespace/control characters and records exactly affected columns", () => {
  const prefixes = ["=", "+", "-", "@", " \t=", "\uFEFF+", "\t", "\r", "\n"];
  for (const prefix of prefixes) {
    const { result, model } = search([record(1, `${prefix} Bellum`)], "Bellum");
    const row = parseCSV(exportConcordance(model, result, { exportedAt }).text).rows[0];
    assert.equal(row.left_context, `'${prefix} `);
    assert.ok(JSON.parse(row.escaped_columns_json).includes("left_context"));
    assert.equal(JSON.parse(row.original_context_json).left, `${prefix} `);
  }
});

test("CSV includes every occurrence beyond the display page, query settings and corpus/index fingerprints", () => {
  const records = [record(1, Array(45).fill("Bellum").join(" "))];
  const { result, model } = search(records, "bellum", { fold: true });
  const catalog = { schemaVersion: 2, engineSchemaVersion: 1,
    source: { manifestSHA256: "m".repeat(64), engineSHA256: "e".repeat(64), lunrVersion: "2.3.9" },
    collections: [{ id: "bellum-latin-cardwell", corpusSHA256: "c".repeat(64), manifestSHA256: "s".repeat(64) }],
    books: [{ id: "bellum-latin-cardwell:1", sha256: "b".repeat(64), corpusSHA256: "t".repeat(64) }] };
  const searchURL = "https://example.org/project/search/?q=bellum&work=bellum-latin-cardwell&book=all&fold=1";
  const file = exportConcordance(model, result, { exportedAt, catalog, searchURL });
  assert.equal(file.rowCount, 45);
  const { rows } = parseCSV(file.text);
  assert.equal(rows.length, 45);
  for (const row of [rows[0], rows[20], rows[44]]) {
    assert.equal(row.row_type, "occurrence");
    assert.equal(row.occurrence_count, "45");
    assert.equal(row.spelling_equivalence, "u/v and i/j equivalent");
    assert.equal(row.book_bundle_sha256, "b".repeat(64));
    assert.equal(row.book_corpus_sha256, "t".repeat(64));
    assert.equal(row.collection_corpus_sha256, "c".repeat(64));
    assert.equal(row.collection_manifest_sha256, "s".repeat(64));
    assert.equal(row.catalog_manifest_sha256, "m".repeat(64));
    assert.equal(row.engine_sha256, "e".repeat(64));
    assert.equal(row.search_url, searchURL);
    assert.equal(row.exported_at_utc, exportedAt);
    assert.deepEqual(JSON.parse(row.selected_book_ids_json), result.selectedBooks);
    assert.deepEqual(JSON.parse(row.selected_collection_ids_json), result.selectedCollections);
  }
  assert.ok(JSON.parse(rows[22].source_segments_json)[0].text.length < records[0].text.length, "each occurrence exports short context rather than redundant full sections");
});

test("a zero-result CSV retains the search settings without inventing an occurrence", () => {
  const { result, model } = search([record(1, "rex")], "absent");
  const exported = exportConcordance(model, result, { exportedAt });
  assert.equal(model.occurrenceCount, 0);
  assert.equal(exported.rowCount, 0);
  const rows = parseCSV(exported.text).rows;
  assert.equal(rows.length, 1);
  assert.equal(rows[0].row_type, "search-summary");
  assert.equal(rows[0].query, "absent");
  assert.equal(rows[0].occurrence_count, "0");
  assert.equal(rows[0].matched_text, "");
});

test("the export records fingerprints for selected books without hits, including zero-result searches", () => {
  const records = [record(1, "rex rex"), record(1, "regina", { id: "book2", book: 2, bookId: "bellum-latin-cardwell:2" })];
  const catalog = { collections: [{ id: "bellum-latin-cardwell", corpusSHA256: "collection-fingerprint" }],
    books: [{ id: "bellum-latin-cardwell:1", sha256: "first-index", corpusSHA256: "first-text" },
      { id: "bellum-latin-cardwell:2", sha256: "second-index", corpusSHA256: "second-text" }] };
  for (const query of ["rex", "absent"]) {
    const { result, model } = search(records, query);
    const rows = parseCSV(exportConcordance(model, result, { exportedAt, catalog }).text).rows;
    const sources = JSON.parse(rows[0].selected_sources_json);
    assert.deepEqual(sources.books.map((book) => [book.id, book.sha256, book.corpusSHA256]), [
      ["bellum-latin-cardwell:1", "first-index", "first-text"], ["bellum-latin-cardwell:2", "second-index", "second-text"],
    ]);
    assert.equal(sources.collections[0].corpusSHA256, "collection-fingerprint");
    assert.ok(rows.slice(1).every((row) => row.selected_sources_json === ""));
  }
});

test("invalid spans and ambiguous book identity fail explicitly instead of dropping results", () => {
  const records = [record(1, "rex")];
  const { result } = search(records, "rex");
  const bad = structuredClone(result);
  bad.hitGroups[0].hits[0].spans[0].end = 999;
  assert.throws(() => buildConcordance(bad, records, { readerBase }), /invalid original-text span/);
  assert.throws(() => buildConcordance(result, records, { readerBase, contextWords: -1 }), /nonnegative integer/);
  assert.throws(() => buildConcordance(result, [...records, records[0]], { readerBase }), /unique IDs/);
  assert.throws(() => buildConcordance({ ...result, scope: "book", hitGroups: [{ unitId: "unknown", recordIds: [], hits: [] }] }, records, { readerBase }), /missing or ambiguous/);
});
