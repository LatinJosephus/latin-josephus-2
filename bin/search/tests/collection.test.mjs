import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { buildBundle, QueryError } from "../engine.mjs";
import { createCollection, CollectionLoadError } from "../collection.mjs";

const lunr = createRequire(import.meta.url)("../vendor/lunr.cjs");
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
const BELLUM = "bellum-latin-cardwell";
const ANTIQUITIES = "antiquities-latin-synthetic";
const EDITION = "bellum-latin-synthetic";
const GREEK = "bellum-greek-synthetic";
const B = (number) => `${BELLUM}:${number}`;
const A = (number) => `${ANTIQUITIES}:${number}`;
const E = (number) => `${EDITION}:${number}`;
const G = (number) => `${GREEK}:${number}`;
const total = (entries) => ({ books: entries.length, sections: entries.reduce((n, x) => n + x.sections, 0), tokens: entries.reduce((n, x) => n + x.tokens, 0), bytes: entries.reduce((n, x) => n + x.bytes, 0) });

function definition(metadata, books) {
  let order = 0;
  return { metadata, books: books.map(([number, label, texts]) => ({
    number, label, records: texts.map((text, index) => ({
      id: `${metadata.id}-${number}-${index + 1}`, book: number, section: index + 1,
      work: metadata.work, language: metadata.language, edition: metadata.edition,
      order: order++, text, url: `/${metadata.readerPath}?book=${number}#${index + 1}`,
    })),
  })) };
}

function definitions(multiple = false) {
  const baseline = definition({ id: BELLUM, work: "bellum", label: "Bellum Judaicum", citationPrefix: "Bellum", language: "Latin", edition: "Cardwell (1837)", readerPath: "bellum-judaicum/" }, [
    [1, "Book I", ["Rex alpha Judaei viri. Ultima", "verba Roma."]],
    [2, "Book II", ["Regina beta. Prima nova.", "rex Roma"]],
    [3, "Book III", ["Pax Roma. tertia."]],
  ]);
  if (!multiple) return [baseline];
  // These are invented, tiny corpora. No Antiquities or other edition source
  // is included in the published catalog merely because it is tested here.
  return [baseline,
    definition({ id: ANTIQUITIES, work: "antiquities", label: "Antiquitates Judaicae", citationPrefix: "Antiquities", language: "Latin", edition: "Synthetic test edition", readerPath: "antiquitates-judaicae/" }, [
      [1, "Book I", ["Antiquus gamma. Initium", "orbis Roma."]],
      [20, "Book XX", ["Vicesimus Roma."]],
    ]),
    definition({ id: EDITION, work: "bellum", label: "Bellum Judaicum", citationPrefix: "Bellum", language: "Latin", edition: "Synthetic test edition", readerPath: "bellum-judaicum/" }, [
      [1, "Book I", ["Versionis delta. Pax Roma."]],
    ]),
    definition({ id: GREEK, work: "bellum", label: "Bellum Judaicum", citationPrefix: "Bellum", language: "Greek", edition: "Synthetic test edition", readerPath: "bellum-judaicum/" }, [
      [1, "Book I", ["Ἰώσηπος λόγος Roma."]],
    ]),
  ];
}

function dehDefinition() {
  const source = definition({ id: "deh-latin-ussani", work: "deh", label: "De excidio", citationPrefix: "De excidio", language: "Latin", edition: "Ussani (1932)", readerPath: "deh/", citationScheme: "chapter-paragraph", unitLabel: "citation unit", unitLabelPlural: "citation units" }, [
    [1, "Book I and Prologue", ["prologus finis", "initium Cenedaei."]],
  ]);
  Object.assign(source.books[0].records[0], { chapter: 0, paragraph: 1, citationLabel: "Prol.1", citationScheme: "chapter-paragraph", sourceId: "latin-deh1-num1", editorialMarks: [] });
  Object.assign(source.books[0].records[1], { chapter: 1, paragraph: 1, citationLabel: "I.1.1", citationScheme: "chapter-paragraph", sourceId: "latin-deh1-num2", breakBefore: true, editorialMarks: [{kind:"supplied",start:10,end:12,text:"ne"}] });
  return source;
}

function fixture(sources = definitions()) {
  const files = new Map();
  const entries = [];
  const collections = sources.map(({ metadata, books }) => {
    const collectionEntries = books.map(({ number, label, records }) => {
      const corpusBytes = JSON.stringify(records);
      const bundle = buildBundle(records, lunr);
      bundle.source = { corpusSHA256: hash(corpusBytes), lunrVersion: lunr.version };
      const bytes = Buffer.from(JSON.stringify(bundle));
      const path = `data/${metadata.id}/book-${String(number).padStart(2, "0")}.bundle.json`;
      files.set(`/search/${path}`, bytes);
      return { id: `${metadata.id}:${number}`, collectionId: metadata.id, number, label, path, sections: records.length, tokens: bundle.stats.tokens, bytes: bytes.length, sha256: hash(bytes), corpusSHA256: bundle.source.corpusSHA256 };
    });
    entries.push(...collectionEntries);
    return { ...metadata, books: collectionEntries.map((entry) => entry.id), totals: total(collectionEntries) };
  });
  const catalog = { schemaVersion: 2, engineSchemaVersion: 1, source: { lunrVersion: lunr.version }, collections, books: entries, totals: total(entries) };
  const requests = [];
  const fetchImpl = async (url) => {
    requests.push(url.pathname);
    const bytes = files.get(url.pathname);
    return bytes ? new Response(bytes) : new Response("missing", { status: 404 });
  };
  const makeCollection = () => createCollection(catalog, lunr, { baseURL: new URL("https://example.test/search/"), fetchImpl });
  return { collection: makeCollection(), makeCollection, catalog, files, requests, sources };
}

function changeBundle(f, id, change) {
  const entry = f.catalog.books.find((entry) => entry.id === id);
  const path = `/search/${entry.path}`;
  const bundle = JSON.parse(f.files.get(path).toString("utf8"));
  change(bundle);
  const bytes = Buffer.from(JSON.stringify(bundle));
  const difference = bytes.length - entry.bytes;
  f.files.set(path, bytes);
  f.catalog.totals.bytes += difference;
  f.catalog.collections.find((collection) => collection.id === entry.collectionId).totals.bytes += difference;
  entry.bytes = bytes.length;
  entry.sha256 = hash(bytes);
}

test("DEH metadata uses chapter citations while Bellum keeps Niese labels and independent book evidence", async () => {
  const { collection } = fixture([...definitions(), dehDefinition()]);
  const deh = await collection.search("Cenedaei", {collections:["deh-latin-ussani"]});
  assert.equal(deh.hitGroups[0].unitLabel, "De excidio I.1.1");
  assert.equal(deh.hitGroups[0].citationUnitLabel, "citation unit");
  assert.equal(deh.records[1].editorialMarks[0].text, "ne");
  assert.equal((await collection.search('"finis initium"', {scope:"book",collections:["deh-latin-ussani"]})).matchingUnits, 0);
  assert.equal((await collection.search("alpha AND Cenedaei", {scope:"book"})).matchingUnits, 0);
  const all = await collection.search("Roma OR Cenedaei");
  assert.ok(all.hitGroups.some(group => group.citationScheme === "niese"));
  assert.ok(all.hitGroups.some(group => group.citationScheme === "chapter-paragraph"));
});

test("validly hashed DEH bundles reject corrupt citation and editorial-span metadata", async () => {
  for (const mutate of [
    record => {record.citationLabel = "I.99.1";},
    record => {record.citationScheme = "niese";},
    record => {record.editorialMarks[0].text = "zz";},
    record => {record.editorialMarks[0].end += 1;},
    record => {record.editorialMarks[0].kind = "unknown";},
  ]) {
    const f = fixture([dehDefinition()]);
    changeBundle(f,"deh-latin-ussani:1",bundle => mutate(bundle.records[1]));
    await assert.rejects(f.collection.search("Cenedaei"),error => error.code === "BUNDLE_INVALID" && /citations|citation|editorial/.test(error.message));
  }
});

test("selected books load only their files and merge in canonical source order", async () => {
  const { collection, requests } = fixture();
  const result = await collection.search("Roma", { books: [B(3), B(1), B(3)] });
  assert.deepEqual(result.selectedBooks, [B(1), B(3)]);
  assert.deepEqual(result.matchingBooks, [B(1), B(3)]);
  assert.deepEqual(result.selectedCollections, [BELLUM]);
  assert.deepEqual(result.hitGroups.map((group) => [group.book, group.sections]), [[1, [2]], [3, [1]]]);
  assert.equal(result.matchingUnits, 2);
  assert.equal(result.matchingSections, 2);
  assert.equal(result.occurrences, 2);
  assert.deepEqual(result.records.map((record) => [record.book, record.section]), [[1, 1], [1, 2], [3, 1]]);
  assert.deepEqual(requests, [`/search/data/${BELLUM}/book-01.bundle.json`, `/search/data/${BELLUM}/book-03.bundle.json`]);
  assert.deepEqual(collection.cachedBooks, [B(1), B(3)]);
});

test("book Boolean conditions never combine evidence from separate books", async () => {
  const { collection } = fixture();
  assert.equal((await collection.search("alpha AND beta", { books: [B(1), B(2)], scope: "book" })).matchingUnits, 0);
  const result = await collection.search("rex AND Roma", { books: [B(1), B(2)], scope: "book" });
  assert.deepEqual(result.matchingBooks, [B(1), B(2)]);
  assert.equal(result.matchingUnits, 2);
  assert.equal(result.matchingSections, 3);
  assert.equal(result.occurrences, 4);
  const section = await collection.search("rex AND Roma", { books: [B(1), B(2)], scope: "section" });
  assert.deepEqual(section.hitGroups.map((group) => [group.book, group.sections]), [[2, [2]]]);
});

test("phrases cross sections in one book but never adjacent selected books", async () => {
  const { collection } = fixture();
  const internal = await collection.search('"Ultima verba"', { books: [B(1), B(2)], scope: "book" });
  assert.equal(internal.occurrences, 1);
  assert.equal(internal.hitGroups[0].hits[0].spans.length, 2);
  assert.equal((await collection.search('"Ultima verba"', { books: [B(1), B(2)], scope: "section" })).matchingUnits, 0);
  assert.equal((await collection.search('"Roma Regina"', { books: [B(1), B(2)], scope: "book" })).matchingUnits, 0);
  assert.equal((await collection.search('"Roma Pax"', { books: [B(2), B(3)], scope: "book" })).matchingUnits, 0);
});

test("negative-only book matches carry explicit book identities without false occurrences", async () => {
  const { collection } = fixture();
  const result = await collection.search("NOT rex", { scope: "book" });
  assert.deepEqual(result.matchingBooks, [B(3)]);
  assert.equal(result.matchingUnits, 1);
  assert.equal(result.matchingSections, 0);
  assert.equal(result.occurrences, 0);
  assert.equal(result.hitGroups[0].bookId, B(3));
  assert.equal(result.hitGroups[0].bookLabel, "Book III");
  assert.deepEqual(result.hitGroups[0].hits, []);
  assert.deepEqual(result.hitGroups[0].recordIds, []);
});

test("query, scope, spelling mode and original highlight offsets survive aggregation", async () => {
  const { collection } = fixture();
  const query = '"Iudaei uiri"';
  const result = await collection.search(query, { books: [B(1), B(2)], scope: "book", fold: true });
  assert.equal(result.query, query);
  assert.equal(result.scope, "book");
  assert.equal(result.fold, true);
  assert.deepEqual(result.matchingBooks, [B(1)]);
  const span = result.hitGroups[0].hits[0].spans[0];
  assert.equal(result.records.find((record) => record.id === span.recordId).text.slice(span.start, span.end), "Judaei viri");
  assert.equal((await collection.search(query, { books: [B(1), B(2)], fold: false })).matchingUnits, 0);
});

test("successful downloads are cached and progress includes qualified text identities", async () => {
  const { collection, requests } = fixture();
  const progress = [];
  await collection.search("Roma", { books: [B(1), B(2)], onProgress: (event) => progress.push(event) });
  await collection.search("rex", { books: [B(2)] });
  assert.equal(requests.length, 2);
  assert.deepEqual(collection.cachedBooks, [B(1), B(2)]);
  assert.ok(progress.some((event) => event.stage === "loading" && event.bookId === B(1) && event.collectionId === BELLUM && event.completed === 0 && !event.cached));
  assert.ok(progress.some((event) => event.stage === "loading" && event.completed === 2 && event.total === 2));
  assert.ok(progress.some((event) => event.stage === "searching" && event.bookId === B(2) && event.completed === 2));
});

test("overlapping searches share each download and keep separate selections", async () => {
  const { collection, requests } = fixture(definitions(true));
  const [first, second] = await Promise.all([
    collection.search("Roma", { books: [B(1), A(1)] }),
    collection.search("rex", { books: [B(1)] }),
  ]);
  assert.equal(requests.filter((path) => path.includes(`/${BELLUM}/`)).length, 1);
  assert.equal(requests.filter((path) => path.includes(`/${ANTIQUITIES}/`)).length, 1);
  assert.equal(requests.length, 2);
  assert.deepEqual(first.selectedBooks, [B(1), A(1)]);
  assert.deepEqual(second.selectedBooks, [B(1)]);
  assert.deepEqual(collection.cachedBooks, [B(1), A(1)]);
});

test("a missing work rejects the entire query and retry reuses other works' cached books", async () => {
  const { collection, files, requests } = fixture(definitions(true));
  const path = `/search/data/${ANTIQUITIES}/book-01.bundle.json`;
  const correct = files.get(path);
  files.delete(path);
  await assert.rejects(collection.search("Roma", { books: [B(1), A(1), E(1)] }), (error) => error instanceof CollectionLoadError && error.bookId === A(1) && error.collectionId === ANTIQUITIES && error.code === "BOOK_LOAD_FAILED");
  assert.deepEqual(collection.cachedBooks, [B(1)]);
  assert.equal(requests.length, 2, "the later edition is not loaded after failure");
  files.set(path, correct);
  const result = await collection.search("Roma", { books: [B(1), A(1), E(1)] });
  assert.deepEqual(result.matchingBooks, [B(1), A(1), E(1)]);
  assert.equal(result.matchingUnits, 3);
  assert.deepEqual(collection.cachedBooks, [B(1), A(1), E(1)]);
  assert.equal(requests.filter((url) => url.includes(`/${BELLUM}/`)).length, 1);
  assert.equal(requests.filter((url) => url.includes(`/${ANTIQUITIES}/`)).length, 2);
});

test("same-length corrupt bytes fail SHA-256 validation and can be retried", async () => {
  const { collection, files } = fixture();
  const path = `/search/data/${BELLUM}/book-02.bundle.json`;
  const correct = files.get(path);
  const corrupt = Buffer.from(correct);
  corrupt[100] ^= 1;
  files.set(path, corrupt);
  await assert.rejects(collection.search("Roma", { books: [B(1), B(2)] }), { code: "BUNDLE_INTEGRITY", book: 2, bookId: B(2) });
  assert.deepEqual(collection.cachedBooks, [B(1)]);
  files.set(path, correct);
  assert.equal((await collection.search("Roma", { books: [B(1), B(2)] })).matchingUnits, 2);
});

test("validly hashed bundles with wrong book, work, edition, or language are rejected", async () => {
  for (const [field, value] of [["book", 2], ["work", "bellum"], ["edition", "Cardwell (1837)"], ["language", "Greek"]]) {
    const f = fixture(definitions(true));
    changeBundle(f, A(1), (bundle) => { bundle.records[0][field] = value; });
    const collection = f.makeCollection();
    await assert.rejects(collection.search("Roma", { books: [B(1), A(1)] }), { code: "BUNDLE_INVALID", book: 1, bookId: A(1), collectionId: ANTIQUITIES });
    assert.deepEqual(collection.cachedBooks, [B(1)]);
  }
});

test("invalid queries and ambiguous or conflicting selections fail before downloading", async () => {
  const { collection, requests } = fixture(definitions(true));
  await assert.rejects(collection.search("rex AND", { books: [B(1)] }), QueryError);
  await assert.rejects(collection.search("rex", { books: [] }), { code: "EMPTY_SELECTION" });
  await assert.rejects(collection.search("rex", { collections: [] }), { code: "EMPTY_SELECTION" });
  await assert.rejects(collection.search("rex", { books: [B(1), B(7)] }), { code: "UNKNOWN_BOOK" });
  await assert.rejects(collection.search("rex", { collections: ["unknown"] }), { code: "UNKNOWN_COLLECTION" });
  for (const books of [[1], ["1"], 1]) await assert.rejects(collection.search("rex", { books }), { code: "AMBIGUOUS_BOOK" });
  await assert.rejects(collection.search("rex", { collections: [BELLUM], books: [A(1)] }), { code: "SELECTION_CONFLICT", bookId: A(1) });
  assert.deepEqual(requests, []);
});

test("cancellation between books stops stale downloads while retaining successful cache", async () => {
  const { collection, requests } = fixture();
  const controller = new AbortController();
  await assert.rejects(collection.search("Roma", {
    books: [B(1), B(2), B(3)], signal: controller.signal,
    onProgress: ({ stage, bookId }) => { if (stage === "loading" && bookId === B(2)) controller.abort(); },
  }), { name: "AbortError" });
  assert.equal(requests.length, 1);
  assert.deepEqual(collection.cachedBooks, [B(1)]);
  assert.equal((await collection.search("Roma", { books: [B(1)] })).matchingUnits, 1);
});

test("work, edition, and language filters keep overlapping Book I identities separate", async () => {
  const { collection, requests } = fixture(definitions(true));
  const antiquities = await collection.search("Roma", { collections: [ANTIQUITIES] });
  assert.deepEqual(antiquities.selectedBooks, [A(1), A(20)]);
  assert.deepEqual(antiquities.selectedCollections, [ANTIQUITIES]);
  assert.deepEqual(antiquities.matchingCollections, [ANTIQUITIES]);
  assert.equal(requests.length, 2);
  assert.ok(requests.every((path) => path.includes(`/${ANTIQUITIES}/`)));
  const selected = await collection.search("Roma", { collections: [GREEK, BELLUM, EDITION], books: [G(1), E(1), B(1)] });
  assert.deepEqual(selected.selectedBooks, [B(1), E(1), G(1)]);
  assert.deepEqual(selected.selectedCollections, [BELLUM, EDITION, GREEK]);
  assert.equal(new Set(selected.hitGroups.map((group) => group.unitId)).size, 3);
  assert.deepEqual(selected.records.map((record) => record.order), [0, 1, 0, 0], "audit source order is preserved within each text version");
  assert.deepEqual(selected.records.map((record) => record.resultOrder), [0, 1, 2, 3], "display order does not interleave works");
});

test("Boolean and phrase evidence never crosses works, editions, or languages", async () => {
  const { collection } = fixture(definitions(true));
  for (const [query, books] of [
    ["alpha AND gamma", [B(1), A(1)]],
    ["alpha AND delta", [B(1), E(1)]],
    ["alpha AND λόγος", [B(1), G(1)]],
    ['"Roma Antiquus"', [B(1), A(1)]],
    ['"Roma Versionis"', [B(1), E(1)]],
    ['"Roma Ἰώσηπος"', [E(1), G(1)]],
  ]) assert.equal((await collection.search(query, { books, scope: "book" })).matchingUnits, 0, query);
  const internal = await collection.search('"Initium orbis"', { books: [B(1), A(1)], scope: "book" });
  assert.deepEqual(internal.matchingBooks, [A(1)]);
  assert.equal(internal.hitGroups[0].hits[0].spans.length, 2);
  assert.equal((await collection.search('"Initium orbis"', { collections: [ANTIQUITIES], scope: "section" })).matchingUnits, 0);
});

test("negative-only overlapping books retain correct citation, edition, and reader metadata", async () => {
  const { collection } = fixture(definitions(true));
  const result = await collection.search("NOT rex", { books: [B(1), A(1), E(1), G(1)], scope: "book" });
  assert.deepEqual(result.matchingBooks, [A(1), E(1), G(1)]);
  assert.equal(result.matchingUnits, 3);
  assert.equal(result.matchingSections, 0);
  assert.equal(result.occurrences, 0);
  assert.deepEqual(result.hitGroups.map((group) => [group.bookId, group.collectionId, group.citationPrefix, group.readerPath, group.language, group.edition]), [
    [A(1), ANTIQUITIES, "Antiquities", "antiquitates-judaicae/", "Latin", "Synthetic test edition"],
    [E(1), EDITION, "Bellum", "bellum-judaicum/", "Latin", "Synthetic test edition"],
    [G(1), GREEK, "Bellum", "bellum-judaicum/", "Greek", "Synthetic test edition"],
  ]);
  assert.ok(result.hitGroups.every((group) => group.hits.length === 0 && group.recordIds.length === 0));
  const record = result.records.find((record) => record.bookId === A(1));
  assert.equal(record.citationPrefix, "Antiquities");
  assert.equal(record.readerPath, "antiquitates-judaicae/");
  assert.equal(record.url, "/antiquitates-judaicae/?book=1#1");
});

test("catalog validation rejects duplicate identities, paths, references, and coverage totals", () => {
  const mutations = [
    (catalog) => { catalog.books[3].id = B(1); },
    (catalog) => { catalog.books[3].path = catalog.books[0].path; },
    (catalog) => { catalog.collections[1].books = [B(1), A(20)]; },
    (catalog) => { catalog.collections[2].edition = "Cardwell (1837)"; },
    (catalog) => { catalog.collections[0].totals.sections += 1; },
    (catalog) => { catalog.totals.tokens += 1; },
    (catalog) => { catalog.books[0].path = "../outside.bundle.json"; },
  ];
  for (const mutate of mutations) {
    const f = fixture(definitions(true));
    mutate(f.catalog);
    assert.throws(f.makeCollection, { code: "CATALOG_INVALID" });
    assert.deepEqual(f.requests, []);
  }
});

test("passage ID collisions across otherwise valid editions fail instead of corrupting highlight maps", async () => {
  const sources = definitions(true);
  sources[2].books[0].records[0].id = sources[0].books[0].records[0].id;
  const { collection } = fixture(sources);
  await assert.rejects(collection.search("Roma", { books: [B(1), E(1)] }), { code: "BUNDLE_INVALID", bookId: E(1) });
  assert.deepEqual(collection.cachedBooks, [B(1)]);
});
