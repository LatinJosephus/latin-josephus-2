import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import {
  buildBundle, createEngine, normalizeTerm, parseQuery, QueryError,
  tokenizeText, wildcardMatches, QUERY_LIMITS,
} from "../engine.mjs";

const require = createRequire(import.meta.url);
const lunr = require("../vendor/lunr.cjs");

function record(section, text, options = {}) {
  return {
    id: `bellum-latin-cardwell-1-${section}`, work: "bellum", book: 1,
    section, chapter: 1, text, url: `/reader#${section}`, sourceId: `p${section}`,
    order: section - 1, ...options,
  };
}

const records = [
  record(1, "Rex Roma erat; bellum bellorum. In a et non. Judaei viri."),
  record(2, "Regina Romae bellum. φιλοσοφία ἀρχή λόγος. Ultima verba"),
  record(3, "prima nova. Rex Herodes pacem amat. habebantur"),
  record(4, "At Theodorus repente venit: regis aufert, Judaeorumque."),
  record(5, "post lacunam.", { breakBefore: true }),
  record(6, "bellum rebellum bell bellorum; Roma Romam. a a a."),
];
const bundle = buildBundle(records, lunr);
const engine = createEngine(JSON.parse(JSON.stringify(bundle)), lunr);
const sections = (query, options) => engine.search(query, options).hitGroups.flatMap((group) => group.sections);
const idsOf = (result) => result.hitGroups.flatMap((group) => group.recordIds);

test("build and load preserve source and stable record lookup", () => {
  assert.equal(records[0].breakBefore, undefined, "builder must not mutate records");
  assert.equal(bundle.records.length, 6);
  assert.equal(bundle.stats.books, 1);
  assert.equal(engine.records[0].text, records[0].text);
  assert.deepEqual(sections("Rex"), [1, 3]);
  assert.deepEqual(sections("rex"), [1, 3]);
  assert.deepEqual(sections("reg"), []);
});

test("whole-word exact search retains stop words and disables stemming", () => {
  assert.deepEqual(sections("in AND et AND non"), [1]);
  assert.deepEqual(sections("a"), [1, 6]);
  assert.deepEqual(sections("bell"), [6]);
  assert.deepEqual(sections("bellum"), [1, 2, 6]);
});

test("wildcards match zero or more characters at any token position", () => {
  assert.deepEqual(sections("Roma*"), [1, 2, 6]);
  assert.deepEqual(sections("*bell*"), [1, 2, 6]);
  assert.deepEqual(sections("b*lum"), [1, 2, 6]);
  assert.deepEqual(sections("*bellum"), [1, 2, 6]);
  assert.equal(wildcardMatches("bell*", "bell"), true);
  assert.equal(wildcardMatches("b*ell", "bell"), true);
  assert.equal(wildcardMatches("*bell*", "bell"), true);
  assert.equal(wildcardMatches("b*ell", "rebell"), false);
  assert.equal(wildcardMatches("a*b*c", "abbc"), true);
  assert.equal(wildcardMatches("a*b*c", "ac"), false);
});

test("full Boolean grouping, implicit AND, and operator precedence", () => {
  assert.deepEqual(sections("(Rex OR Regina) AND Roma*"), [1, 2]);
  assert.deepEqual(sections("(Rex OR Regina) Roma*"), [1, 2]);
  assert.deepEqual(sections("Rex OR Regina AND Roma*"), [1, 2, 3]);
  assert.deepEqual(sections("Rex AND NOT Roma*"), [3]);
  assert.deepEqual(sections("Rex NOT Roma*"), [3]);
  assert.deepEqual(sections("NOT (Rex OR Regina)"), [4, 5, 6]);
  assert.deepEqual(sections("(Rex OR Regina) AND (Herodes OR bellum)"), [1, 2, 3]);
  assert.deepEqual(sections("Rex AND nonexistentword"), []);
});

test("only uppercase operators are syntax, and quotes can search reserved words", () => {
  const own = createEngine(buildBundle([record(1, "and OR NOT"), record(2, "and bellum")], lunr), lunr);
  assert.equal(own.search("and").matchingUnits, 2);
  assert.equal(own.search('"OR"').matchingUnits, 1);
  assert.equal(own.search("and AND bellum").matchingUnits, 1);
});

test("optional u/v and i/j normalization applies to indexed terms and patterns", () => {
  assert.deepEqual(sections("Iudaei"), []);
  assert.deepEqual(sections("Iudaei", { fold: true }), [1]);
  assert.deepEqual(sections("uiri", { fold: true }), [1]);
  assert.deepEqual(sections("Iudae*", { fold: true }), [1, 4]);
  assert.deepEqual(sections('"Iudaei uiri"', { fold: true }), [1]);
  assert.deepEqual(sections('"Iudaei uiri"'), []);
});

test("Greek and combining marks survive, with offsets into original text", () => {
  assert.deepEqual(sections("ΦΙΛΟΣΟΦΊΑ"), [2]);
  assert.deepEqual(sections("ἀρχή"), [2]);
  assert.deepEqual(sections("λόγος"), [2]);
  const result = engine.search("ἀρχή");
  const span = result.hitGroups[0].hits[0].spans[0];
  assert.equal(records[1].text.slice(span.start, span.end), "ἀρχή");
  assert.equal(normalizeTerm("ΛΌΓΟΣ"), normalizeTerm("λόγοσ"));
  const astral = tokenizeText("x 𐌀𐌁 y");
  assert.equal("x 𐌀𐌁 y".slice(astral[1].start, astral[1].end), "𐌀𐌁");
});

test("exact phrases use consecutive words, ignoring punctuation", () => {
  assert.deepEqual(sections('"regis aufert Judaeorumque"'), [4]);
  assert.deepEqual(sections('"regis, aufert; Judaeorumque!"'), [4]);
  assert.deepEqual(sections('"regis Judaeorumque"'), []);
  assert.deepEqual(sections('"At Theodor* repente"'), [4]);
  assert.deepEqual(sections('"At * repente"'), [4]);
  assert.deepEqual(sections('"Rex Roma" AND NOT Regina'), [1]);
  assert.equal(engine.search('"a a"').occurrences, 2, "overlapping phrases are distinct occurrences");
});

test("section and book scopes have explicitly different Boolean boundaries", () => {
  assert.equal(engine.search("Theodorus AND Regina").matchingUnits, 0);
  const book = engine.search("Theodorus AND Regina", { scope: "book" });
  assert.equal(book.matchingUnits, 1);
  assert.deepEqual(book.hitGroups[0].sections, [2, 4]);
  assert.equal(book.matchingSections, 2);
  assert.equal(engine.search("Theodorus AND NOT Regina", { scope: "book" }).matchingUnits, 0);
  assert.deepEqual(sections("Theodorus AND NOT Regina"), [4]);
});

test("book phrases can span sections and retain both original spans", () => {
  assert.equal(engine.search('"habebantur At Theodorus"').matchingUnits, 0);
  const result = engine.search('"habebantur At Theodorus"', { scope: "book" });
  assert.equal(result.matchingUnits, 1);
  assert.equal(result.matchingSections, 2);
  assert.equal(result.occurrences, 1);
  const spans = result.hitGroups[0].hits[0].spans;
  assert.deepEqual(spans.map((span) => span.recordId), [records[2].id, records[3].id]);
  assert.deepEqual(spans.map((span) => records.find((record) => record.id === span.recordId).text.slice(span.start, span.end)), ["habebantur", "At Theodorus"]);
  assert.equal(engine.search('"verba prima"', { scope: "book" }).occurrences, 1);
});

test("phrases never cross declared gaps or books", () => {
  assert.equal(engine.search('"Judaeorumque post"', { scope: "book" }).matchingUnits, 0);
  const twoBooks = [record(1, "finis libri"), record(2, "initium novi", { id: "book-2", book: 2 })];
  const own = createEngine(buildBundle(twoBooks, lunr), lunr);
  assert.equal(own.search('"libri initium"', { scope: "book" }).matchingUnits, 0);
  assert.equal(own.search("finis AND initium", { scope: "book" }).matchingUnits, 0);
});

test("book scope keeps languages and editions separate even within the same work and book", () => {
  const versions = [
    record(1, "finis", { id: "latin-a-1", language: "Latin", edition: "A", order: 0 }),
    record(1, "initium", { id: "greek-a-1", language: "Greek", edition: "A", order: 0 }),
    record(1, "initium", { id: "latin-b-1", language: "Latin", edition: "B", order: 0 }),
    record(2, "libri", { id: "latin-a-2", language: "Latin", edition: "A", order: 1 }),
  ];
  const own = createEngine(buildBundle(versions, lunr), lunr);
  assert.equal(own.search("finis AND initium", { scope: "book" }).matchingUnits, 0);
  assert.equal(own.search('"finis initium"', { scope: "book" }).matchingUnits, 0);
  assert.equal(own.search("finis OR initium", { scope: "book" }).matchingUnits, 3);
  assert.equal(own.search('"finis libri"', { scope: "book" }).occurrences, 1);
  assert.deepEqual(own.search('"finis libri"', { scope: "book" }).hitGroups[0].recordIds, ["latin-a-1", "latin-a-2"]);
});

test("negation uses the complete scope, and generates no false hit counts", () => {
  const section = engine.search("NOT Rex");
  assert.equal(section.matchingUnits, 4);
  assert.equal(section.matchingSections, 4);
  assert.equal(section.occurrences, 0);
  const book = engine.search("NOT missingword", { scope: "book" });
  assert.equal(book.matchingUnits, 1);
  assert.equal(book.matchingSections, 0);
  assert.equal(book.occurrences, 0);
  assert.deepEqual(book.hitGroups[0].recordIds, []);
  assert.equal(engine.search("NOT NOT Rex").occurrences, 2);
  assert.deepEqual(sections("NOT (Regina OR NOT Rex)"), [1, 3]);
});

test("hits from failed OR branches are excluded and duplicate geometry counts once", () => {
  const result = engine.search("(Rex AND missingword) OR Herodes");
  assert.equal(result.occurrences, 1);
  assert.equal(result.hitGroups[0].hits[0].queryText, "Herodes");
  assert.equal(engine.search("Rex OR Rex*").occurrences, 2);
  assert.equal(engine.search('Rex OR "Rex"').occurrences, 2);
  assert.equal(engine.search("Rex AND Rex").occurrences, 2);
  assert.equal(engine.search('Rex OR "Rex Roma"').occurrences, 3, "a phrase and a shorter overlapping word have different spans");
});

test("physical order, rather than section number, controls phrase continuity", () => {
  const ownRecords = [record(7, "third", { order: 2 }), record(9, "first", { order: 0 }), record(8, "second", { order: 1 })];
  const own = createEngine(buildBundle(ownRecords, lunr), lunr);
  const result = own.search('"first second third"', { scope: "book" });
  assert.equal(result.occurrences, 1);
  assert.deepEqual(idsOf(result), [ownRecords[1].id, ownRecords[2].id, ownRecords[0].id]);
});

test("malformed queries receive meaningful errors instead of reinterpretation", () => {
  for (const query of ["", "AND rex", "rex AND", "rex OR OR Roma", "()", "(rex", "rex)", '"rex', '"..."', "rex ?", "rex & Roma"]) {
    assert.throws(() => engine.search(query), (error) => error instanceof QueryError && error.message.length > 10 && Number.isInteger(error.position), query);
  }
  assert.throws(() => parseQuery("(".repeat(QUERY_LIMITS.nesting + 1) + "rex" + ")".repeat(QUERY_LIMITS.nesting + 1)), { code: "TOO_DEEPLY_NESTED" });
  assert.throws(() => parseQuery("a ".repeat(QUERY_LIMITS.terms + 1)), { code: "TOO_MANY_TERMS" });
  assert.throws(() => parseQuery("a".repeat(QUERY_LIMITS.characters + 1)), { code: "QUERY_TOO_LONG" });
});

test("bundle validation rejects duplicate references", () => {
  assert.throws(() => buildBundle([record(1, "a"), record(1, "b")], lunr), /Duplicate corpus id/);
});
