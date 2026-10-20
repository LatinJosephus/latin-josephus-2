#!/usr/bin/env node
/**
 * Build configured text collections as independent per-book bundles.
 *   node bin/search/build-index.mjs
 *   node bin/search/build-index.mjs --catalog [config/collections.json] [catalog.json] [lunr.cjs]
 * --collection is an alias for --catalog. CLI paths use the current directory.
 * Legacy single-bundle mode is explicit:
 *   node bin/search/build-index.mjs --single [corpus.json] [bundle.json] [lunr.cjs]
 * Only configured collections are built; this never discovers other XML.
 */
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { resolve, dirname, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import { createHash } from "node:crypto";
import { buildBundle, SCHEMA_VERSION } from "./engine.mjs";
import { CATALOG_SCHEMA_VERSION, qualifiedBookId, validateCatalog } from "./collection.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const digest = (bytes) => createHash("sha256").update(bytes).digest("hex");
const recordsFrom = (bytes) => {
  const source = JSON.parse(bytes.toString("utf8"));
  const records = Array.isArray(source) ? source : source.records;
  if (!Array.isArray(records)) throw new TypeError("Corpus JSON needs an array of records.");
  return records;
};
const sourcePath = (base, value, label) => {
  if (typeof value !== "string" || !value.trim()) throw new TypeError(`${label} needs a source path.`);
  return resolve(base, value);
};
const portableRelative = (base, path) => relative(base, path).split(sep).join("/");
const sumEntries = (entries) => ({
  books: entries.length,
  sections: entries.reduce((sum, entry) => sum + entry.sections, 0),
  tokens: entries.reduce((sum, entry) => sum + entry.tokens, 0),
  bytes: entries.reduce((sum, entry) => sum + entry.bytes, 0),
});

async function writeBundle(inputBytes, outputPath, lunr) {
  const records = recordsFrom(inputBytes);
  const bundle = buildBundle(records, lunr);
  // Preserve frozen engine inputs, outputs, and independent corpus fingerprints.
  // The catalog carries collection metadata without adding it to bundle records.
  bundle.source = { corpusSHA256: digest(inputBytes), lunrVersion: lunr.version };
  const serialized = `${JSON.stringify(bundle)}\n`;
  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, serialized, "utf8");
  return { bundle, bytes: Buffer.byteLength(serialized), sha256: digest(serialized) };
}

async function buildSingle(arguments_) {
  const inputPath = resolve(arguments_[0] || resolve(here, "corpus.json"));
  const outputPath = resolve(arguments_[1] || resolve(here, "bundle.json"));
  const lunrPath = resolve(arguments_[2] || resolve(here, "vendor/lunr.cjs"));
  const result = await writeBundle(await readFile(inputPath), outputPath, require(lunrPath));
  return { outputPath, bytes: result.bytes, sha256: result.sha256, ...result.bundle.stats, ...result.bundle.source };
}

async function readCollection(manifestPath) {
  const manifestBytes = await readFile(manifestPath);
  const manifest = JSON.parse(manifestBytes.toString("utf8"));
  if (manifest.schemaVersion !== 1 || typeof manifest.id !== "string" || !/^[a-z][a-z0-9-]*$/.test(manifest.id)
    || ["work", "label", "citationPrefix", "language", "edition", "readerPath"].some((field) => typeof manifest[field] !== "string" || !manifest[field].trim())
    || /^[./\\]|[\\?#:]|(?:^|\/)\.\.(?:\/|$)/.test(manifest.readerPath)
    || !Array.isArray(manifest.books) || !manifest.books.length) {
    throw new Error(`Invalid collection manifest: ${manifestPath}`);
  }
  for (const field of ["citationScheme", "unitLabel", "unitLabelPlural"]) {
    if (manifest[field] !== undefined && (typeof manifest[field] !== "string" || !manifest[field].trim())) {
      throw new Error(`Invalid ${field} in collection manifest: ${manifestPath}`);
    }
  }
  const base = dirname(manifestPath);
  const corpusPath = sourcePath(base, manifest.corpus, `${manifest.id} combined corpus`);
  const extractionReportPath = sourcePath(base, manifest.extractionReport, `${manifest.id} extraction report`);
  const [corpusBytes, extractionReportBytes] = await Promise.all([readFile(corpusPath), readFile(extractionReportPath)]);
  const combined = recordsFrom(corpusBytes);
  const numbers = new Set();
  const books = [];
  for (const book of manifest.books.slice().sort((a, b) => a.number - b.number)) {
    if (!Number.isInteger(book.number) || book.number < 1 || numbers.has(book.number)
      || typeof book.label !== "string" || !book.label.trim()
      || !Number.isInteger(book.sections) || book.sections < 1) throw new Error(`Invalid or duplicate book in ${manifest.id}.`);
    numbers.add(book.number);
    const path = sourcePath(base, book.corpus, `${manifest.id} book ${book.number} corpus`);
    const bytes = await readFile(path);
    const records = recordsFrom(bytes);
    if (records.length !== book.sections) throw new Error(`${manifest.id}, book ${book.number} requires ${book.sections} sections; found ${records.length}.`);
    const coverageLists = {};
    for (const field of ["missingSections", "omittedSections", "emptySections"]) {
      if (book[field] === undefined) continue;
      const values = book[field];
      if (!Array.isArray(values) || values.some((value, index) => !Number.isInteger(value) || value < 1
        || (index > 0 && value <= values[index - 1])) || book.sectionRange === undefined) {
        throw new Error(`Invalid ${field} for ${manifest.id}, book ${book.number}.`);
      }
      coverageLists[field] = values;
    }
    if (book.sectionRange !== undefined) {
      const range = book.sectionRange;
      const missing = new Set(coverageLists.missingSections || []);
      if (!Array.isArray(range) || range.length !== 2 || range.some((value) => !Number.isInteger(value))
        || range[0] < 1 || range[0] > range[1] || range[1] - range[0] + 1 - missing.size !== book.sections
        || Object.values(coverageLists).flat().some(value => value < range[0] || value > range[1])) {
        throw new Error(`Invalid expected section range for ${manifest.id}, book ${book.number}.`);
      }
      const labels = new Set(records.map((record) => Number(record.section)));
      if (labels.size !== records.length) throw new Error(`${manifest.id}, book ${book.number} repeats a section label.`);
      for (let section = range[0]; section <= range[1]; section += 1) {
        if (missing.has(section)) {
          if (labels.has(section)) throw new Error(`${manifest.id}, book ${book.number} contains declared missing section ${section}.`);
          continue;
        }
        if (!labels.has(section)) throw new Error(`${manifest.id}, book ${book.number} is missing expected section ${section}.`);
      }
      for (let index = 1; index < records.length; index += 1) {
        const left = Number(records[index - 1].section), right = Number(records[index].section);
        if ([...missing].some(section => section > Math.min(left, right) && section < Math.max(left, right)) && !records[index].breakBefore) {
          throw new Error(`${manifest.id}, book ${book.number} needs a phrase boundary across its declared missing sections.`);
        }
      }
    }
    const documentedEmpty = coverageLists.emptySections ?? coverageLists.omittedSections;
    if (documentedEmpty !== undefined) {
      const actual = records.filter(record => record.text === "").map(record => Number(record.section)).sort((a, b) => a - b);
      const omitted = new Set(coverageLists.omittedSections || []);
      if (JSON.stringify(actual) !== JSON.stringify(documentedEmpty) || [...omitted].some(section => !actual.includes(section))
        || records.some(record => record.text === "" && (omitted.has(Number(record.section))
          ? !record.textGaps?.some(gap => gap.kind === "tei-gap" && gap.start === 0 && gap.end === 0
            && gap.text === "" && gap.sourceAttributes?.reason === "omitted")
          : record.emptySource?.kind !== "empty-source-interval"))) {
        throw new Error(`${manifest.id}, book ${book.number} has inconsistent documented empty sections.`);
      }
    }
    books.push({ ...book, path, bytes, records });
  }
  return { manifest, manifestPath, manifestBytes, corpusPath, corpusBytes, extractionReportPath, extractionReportBytes, combined, books };
}

export async function buildCatalog(options = {}) {
  const manifestPath = resolve(options.manifestPath || resolve(here, "config/collections.json"));
  const catalogPath = resolve(options.catalogPath || resolve(here, "catalog.json"));
  const outputBase = dirname(catalogPath);
  const lunrPath = resolve(options.lunrPath || resolve(here, "vendor/lunr.cjs"));
  const lunr = require(lunrPath);
  const manifestBytes = await readFile(manifestPath);
  const configuration = JSON.parse(manifestBytes.toString("utf8"));
  if (configuration.schemaVersion !== 1 || !Array.isArray(configuration.collections) || !configuration.collections.length) {
    throw new Error("The collection configuration must list at least one collection manifest.");
  }
  const sourcePaths = configuration.collections.map((path) => sourcePath(dirname(manifestPath), path, "Collection manifest"));
  if (new Set(sourcePaths).size !== sourcePaths.length) throw new Error("The configuration repeats a collection manifest.");
  const sources = await Promise.all(sourcePaths.map(readCollection));
  const collectionIds = new Set();
  const versions = new Set();
  const passageIds = new Set();
  // Validate every input before writing any bundle or replacing the catalog.
  for (const source of sources) {
    const { manifest, combined, books } = source;
    const version = JSON.stringify([manifest.work, manifest.language, manifest.edition]);
    if (collectionIds.has(manifest.id) || versions.has(version)) throw new Error("Collection IDs and work/language/edition identities must each be unique.");
    collectionIds.add(manifest.id);
    versions.add(version);
    let offset = 0;
    for (const book of books) {
      for (const record of book.records) {
        if (!record || typeof record.id !== "string" || !record.id || passageIds.has(record.id)) throw new Error(`Duplicate or invalid passage ID across configured texts: ${record?.id}`);
        passageIds.add(record.id);
        if (typeof record.text !== "string" || record.section === undefined) throw new Error(`${record.id} needs a text string and section reference.`);
        if (Number(record.book) !== book.number) throw new Error(`${record.id} has the wrong book number for its manifest.`);
        for (const field of ["work", "language", "edition"]) {
          if (record[field] !== manifest[field]) throw new Error(`${record.id}: ${field} does not match the collection manifest.`);
        }
        if (record.order !== offset) throw new Error(`${record.id} must have cumulative source order ${offset} within ${manifest.id}.`);
        if (JSON.stringify(record) !== JSON.stringify(combined[offset])) throw new Error(`Combined corpus differs from its book shard at ${record.id}.`);
        offset += 1;
      }
    }
    if (combined.length !== offset) throw new Error(`${manifest.id}: combined corpus has ${combined.length} records but its configured books contain ${offset}.`);
  }

  const enginePath = resolve(here, "engine.mjs");
  const catalog = {
    schemaVersion: CATALOG_SCHEMA_VERSION, engineSchemaVersion: SCHEMA_VERSION,
    collections: [], books: [], totals: { books: 0, sections: 0, tokens: 0, bytes: 0 },
    source: {
      manifestPath: portableRelative(outputBase, manifestPath), manifestSHA256: digest(manifestBytes),
      enginePath: portableRelative(outputBase, enginePath), engineSHA256: digest(await readFile(enginePath)),
      lunrPath: portableRelative(outputBase, lunrPath), lunrSHA256: digest(await readFile(lunrPath)), lunrVersion: lunr.version,
    },
  };
  for (const source of sources) {
    const { manifest } = source;
    const entries = [];
    for (const book of source.books) {
      const outputPath = resolve(outputBase, "data", manifest.id, `book-${String(book.number).padStart(2, "0")}.bundle.json`);
      const result = await writeBundle(book.bytes, outputPath, lunr);
      if (result.bundle.stats.books !== 1) throw new Error(`${manifest.id}, book ${book.number} contains mixed text versions.`);
      entries.push({
        id: qualifiedBookId(manifest.id, book.number), collectionId: manifest.id, number: book.number, label: book.label,
        sections: result.bundle.stats.records, tokens: result.bundle.stats.tokens, vocabulary: result.bundle.stats.vocabulary,
        bytes: result.bytes, path: portableRelative(outputBase, outputPath), sha256: result.sha256,
        corpusPath: portableRelative(outputBase, book.path), corpusSHA256: result.bundle.source.corpusSHA256,
        ...(["missingSections", "omittedSections", "emptySections"].some(field => book[field] !== undefined) ? {
          sectionRange: book.sectionRange,
          ...Object.fromEntries(["missingSections", "omittedSections", "emptySections"].filter(field => book[field] !== undefined).map(field => [field, book[field]])),
        } : {}),
      });
    }
    const { id, work, label, citationPrefix, language, edition, readerPath } = manifest;
    catalog.collections.push({
      id, work, label, citationPrefix, language, edition, readerPath, books: entries.map((entry) => entry.id),
      ...Object.fromEntries(["citationScheme", "unitLabel", "unitLabelPlural"]
        .filter((field) => manifest[field] !== undefined).map((field) => [field, manifest[field]])),
      manifestPath: portableRelative(outputBase, source.manifestPath), manifestSHA256: digest(source.manifestBytes),
      corpusPath: portableRelative(outputBase, source.corpusPath), corpusSHA256: digest(source.corpusBytes),
      extractionReportPath: portableRelative(outputBase, source.extractionReportPath), extractionReportSHA256: digest(source.extractionReportBytes),
      totals: sumEntries(entries),
    });
    catalog.books.push(...entries);
  }
  catalog.totals = sumEntries(catalog.books);
  validateCatalog(catalog);
  const serialized = `${JSON.stringify(catalog, null, 2)}\n`;
  await mkdir(outputBase, { recursive: true });
  await writeFile(catalogPath, serialized, "utf8");
  return {
    catalogPath, catalogBytes: Buffer.byteLength(serialized), catalogSHA256: digest(serialized),
    collections: catalog.collections.length, ...catalog.totals, source: catalog.source,
    bookBundles: catalog.books.map(({ id, collectionId, number, sections, tokens, bytes, path, sha256 }) => ({ id, collectionId, number, sections, tokens, bytes, path, sha256 })),
  };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const arguments_ = process.argv.slice(2);
    const mode = arguments_[0];
    if (mode && !["--catalog", "--collection", "--single"].includes(mode)) throw new Error(`Unknown build mode ${mode}; use --catalog or --single.`);
    const result = mode === "--single" ? await buildSingle(arguments_.slice(1)) : await buildCatalog({
      manifestPath: arguments_[1], catalogPath: arguments_[2], lunrPath: arguments_[3],
    });
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  } catch (error) {
    process.stderr.write(`Search index build failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
