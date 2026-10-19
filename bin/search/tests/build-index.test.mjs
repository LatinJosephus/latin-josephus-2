import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, writeFile, mkdir, rm, access } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { buildCatalog } from "../build-index.mjs";
import { createCollection } from "../collection.mjs";

const lunr = createRequire(import.meta.url)("../vendor/lunr.cjs");
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
const encode = (value) => `${JSON.stringify(value, null, 2)}\n`;

async function fixture(t) {
  const base = await mkdtemp(join(tmpdir(), "latinjosephus-catalog-"));
  t.after(() => rm(base, { recursive: true, force: true }));
  await mkdir(join(base, "config"));
  await mkdir(join(base, "corpora"));
  const definitions = [
    ["bellum-latin-one", "bellum", "Edition one", "Bellum", "bellum-judaicum/", "alpha Roma"],
    ["antiquities-latin-one", "antiquities", "Edition one", "Antiquities", "antiquitates-judaicae/", "beta Roma"],
    ["bellum-latin-two", "bellum", "Edition two", "Bellum", "bellum-judaicum/", "gamma Roma"],
  ].map(([id, work, edition, citationPrefix, readerPath, text]) => {
    const records = [{ id: `${id}-1-1`, work, book: 1, section: 1, language: "Latin", edition, order: 0, text, url: `/${readerPath}?book=1#1` }];
    const manifest = {
      schemaVersion: 1, id, work, label: citationPrefix, citationPrefix, language: "Latin", edition, readerPath,
      corpus: `../corpora/${id}.json`, extractionReport: `../corpora/${id}.report.json`,
      books: [{ number: 1, label: "Book I", corpus: `../corpora/${id}-book-01.json`, sections: 1, sectionRange: [1, 1] }],
    };
    return { id, records, manifest };
  });
  const rewrite = async (definition) => {
    await writeFile(join(base, "config", `${definition.id}.json`), encode(definition.manifest));
    await writeFile(join(base, "corpora", `${definition.id}.json`), encode(definition.records));
    await writeFile(join(base, "corpora", `${definition.id}-book-01.json`), encode(definition.records));
    await writeFile(join(base, "corpora", `${definition.id}.report.json`), encode({ fixture: true }));
  };
  for (const definition of definitions) await rewrite(definition);
  const manifestPath = join(base, "config", "collections.json");
  const catalogPath = join(base, "catalog.json");
  await writeFile(manifestPath, encode({ schemaVersion: 1, collections: definitions.map(({ id }) => `${id}.json`) }));
  return { base, manifestPath, catalogPath, definitions, rewrite, build: () => buildCatalog({ manifestPath, catalogPath }) };
}

test("manifest-driven build namespaces overlapping book numbers and retains audit and reader metadata", async (t) => {
  const f = await fixture(t);
  const result = await f.build();
  assert.equal(result.collections, 3);
  assert.equal(result.books, 3);
  assert.equal(result.sections, 3);
  assert.equal(result.tokens, 6);
  const catalogBytes = await readFile(f.catalogPath);
  const catalog = JSON.parse(catalogBytes);
  assert.equal(result.catalogSHA256, hash(catalogBytes));
  assert.equal(catalog.schemaVersion, 2);
  assert.deepEqual(catalog.books.map((book) => book.id), ["bellum-latin-one:1", "antiquities-latin-one:1", "bellum-latin-two:1"]);
  assert.deepEqual(catalog.books.map((book) => book.path), [
    "data/bellum-latin-one/book-01.bundle.json",
    "data/antiquities-latin-one/book-01.bundle.json",
    "data/bellum-latin-two/book-01.bundle.json",
  ]);
  for (const collection of catalog.collections) {
    assert.equal(collection.manifestSHA256, hash(await readFile(join(f.base, collection.manifestPath))));
    assert.equal(collection.corpusSHA256, hash(await readFile(join(f.base, collection.corpusPath))));
    assert.equal(collection.extractionReportSHA256, hash(await readFile(join(f.base, collection.extractionReportPath))));
    assert.deepEqual(collection.books, [`${collection.id}:1`]);
  }
  const collection = createCollection(catalog, lunr, { baseURL: "https://test.example/search/", fetchImpl: async (url) => new Response(await readFile(join(f.base, url.pathname.slice("/search/".length)))) });
  const all = await collection.search("Roma");
  assert.equal(all.occurrences, 3);
  assert.deepEqual(all.matchingBooks, catalog.books.map((book) => book.id));
  assert.equal((await collection.search("alpha AND beta", { scope: "book" })).matchingUnits, 0);
  const selected = await collection.search("beta", { collections: ["antiquities-latin-one"] });
  assert.equal(selected.hitGroups[0].citationPrefix, "Antiquities");
  assert.equal(selected.hitGroups[0].readerPath, "antiquitates-judaicae/");
  assert.equal(selected.hitGroups[0].edition, "Edition one");
});

test("all source records are checked before an invalid later collection can replace outputs", async (t) => {
  const f = await fixture(t);
  await f.build();
  const originalCatalog = await readFile(f.catalogPath);
  const bundlePath = join(f.base, "data/bellum-latin-one/book-01.bundle.json");
  const originalBundle = await readFile(bundlePath);
  f.definitions[0].records[0].text = "Changed valid earlier text";
  await f.rewrite(f.definitions[0]);
  f.definitions[2].records[0].text = null;
  await f.rewrite(f.definitions[2]);
  await assert.rejects(f.build(), /needs a text string and section reference/);
  assert.deepEqual(await readFile(f.catalogPath), originalCatalog);
  assert.deepEqual(await readFile(bundlePath), originalBundle);
});

test("collection citation terminology reaches the catalog without altering corpus records", async (t) => {
  const f = await fixture(t);
  const definition = f.definitions[1];
  Object.assign(definition.manifest, {
    citationScheme: "chapter-paragraph", unitLabel: "citation unit", unitLabelPlural: "citation units",
  });
  await f.rewrite(definition);
  await f.build();
  const catalog = JSON.parse(await readFile(f.catalogPath));
  const metadata = catalog.collections.find(collection => collection.id === definition.id);
  assert.equal(metadata.citationScheme, "chapter-paragraph");
  assert.equal(metadata.unitLabel, "citation unit");
  assert.equal(metadata.unitLabelPlural, "citation units");
  const book = catalog.books.find(book => book.collectionId === definition.id);
  const bundle = JSON.parse(await readFile(join(f.base, book.path)));
  for (const [field, value] of Object.entries(definition.records[0])) assert.deepEqual(bundle.records[0][field], value);
  definition.manifest.unitLabel = "";
  await f.rewrite(definition);
  await assert.rejects(f.build(), /Invalid unitLabel/);
});

test("duplicate passage IDs and mismatched version metadata cannot publish a catalog", async (t) => {
  const f = await fixture(t);
  const third = f.definitions[2];
  const originalId = third.records[0].id;
  third.records[0].id = f.definitions[0].records[0].id;
  await f.rewrite(third);
  await assert.rejects(f.build(), /Duplicate or invalid passage ID across configured texts/);
  await assert.rejects(access(f.catalogPath), { code: "ENOENT" });
  third.records[0].id = originalId;
  third.records[0].edition = "Wrong edition";
  await f.rewrite(third);
  await assert.rejects(f.build(), /edition does not match the collection manifest/);
  await assert.rejects(access(f.catalogPath), { code: "ENOENT" });
});

test("declared coverage and combined corpus disagreements fail without creating bundles", async (t) => {
  const f = await fixture(t);
  const second = f.definitions[1];
  second.records[0].section = 2;
  await f.rewrite(second);
  await assert.rejects(f.build(), /missing expected section 1/);
  await assert.rejects(access(join(f.base, "data")), { code: "ENOENT" });
  second.records[0].section = 1;
  await f.rewrite(second);
  await writeFile(join(f.base, "corpora", `${second.id}.json`), encode([{ ...second.records[0], text: "Different combined text" }]));
  await assert.rejects(f.build(), /Combined corpus differs from its book shard/);
  await assert.rejects(access(join(f.base, "data")), { code: "ENOENT" });
});
