/**
 * Load independent book indexes from explicitly named text collections.
 * Work, language, and edition identify a collection; every book selector and
 * cache key includes its collection ID. Queries return no partial results.
 */
import { createEngine, parseQuery, SCHEMA_VERSION } from "./engine.214c7991d16b35fa6afc4934d736a6b2fe068e197066a030bef875550cf36834.mjs";
import { bookCitation, citationFor, editorialMarksFor, romanBook } from "./ui-utils.39a13121b8de63e4a70d5600a38c3aab124275b3a9dfccc0476839c330dba644.mjs";

export const CATALOG_SCHEMA_VERSION = 2;
export const qualifiedBookId = (collectionId, number) => `${collectionId}:${number}`;

export class CollectionLoadError extends Error {
  constructor(message, code, entry = null, cause = undefined) {
    super(message, cause ? { cause } : undefined);
    this.name = "CollectionLoadError";
    this.code = code;
    this.book = typeof entry === "object" ? entry?.number ?? null : null;
    this.bookId = typeof entry === "string" ? entry : entry?.id ?? null;
    this.collectionId = typeof entry === "object" ? entry?.collectionId ?? null : null;
  }
}

const yieldTurn = () => new Promise((resolve) => setTimeout(resolve, 0));
const isSHA256 = (value) => typeof value === "string" && /^[a-f0-9]{64}$/i.test(value);
const isText = (value) => typeof value === "string" && value.trim().length > 0;
const isRelativePath = (value) => isText(value) && !/^[./\\]|[\\?#:]|(?:^|\/)\.\.(?:\/|$)/.test(value);
const totalsFor = (entries) => ({
  books: entries.length,
  sections: entries.reduce((sum, entry) => sum + entry.sections, 0),
  tokens: entries.reduce((sum, entry) => sum + entry.tokens, 0),
  bytes: entries.reduce((sum, entry) => sum + entry.bytes, 0),
});

/** Validate the public catalog without downloading any book data. */
export function validateCatalog(catalog) {
  const invalid = (message) => { throw new CollectionLoadError(message, "CATALOG_INVALID"); };
  if (!catalog || catalog.schemaVersion !== CATALOG_SCHEMA_VERSION || catalog.engineSchemaVersion !== SCHEMA_VERSION
    || !Array.isArray(catalog.collections) || !catalog.collections.length
    || !Array.isArray(catalog.books) || !catalog.books.length) {
    invalid("The search catalog is incomplete or incompatible. Reload the page to obtain the current catalog.");
  }
  const collectionById = new Map();
  const versions = new Set();
  for (const collection of catalog.collections) {
    if (!collection || !isText(collection.id) || !/^[a-z][a-z0-9-]*$/.test(collection.id) || collectionById.has(collection.id)
      || ["work", "label", "citationPrefix", "language", "edition"].some((field) => !isText(collection[field]))
      || !isRelativePath(collection.readerPath) || !Array.isArray(collection.books) || !collection.books.length) {
      invalid("The search catalog contains an invalid or duplicate text collection.");
    }
    if ((collection.citationScheme !== undefined && !["niese", "chapter-paragraph"].includes(collection.citationScheme))
      || ["unitLabel", "unitLabelPlural"].some((field) => collection[field] !== undefined && !isText(collection[field]))) {
      invalid("The search catalog contains an unsupported citation scheme or citation-unit label.");
    }
    const version = JSON.stringify([collection.work, collection.language, collection.edition]);
    if (versions.has(version)) invalid("The catalog repeats the same work, language, and edition under different collection IDs.");
    versions.add(version);
    collectionById.set(collection.id, collection);
  }
  const entryById = new Map();
  const paths = new Set();
  for (const entry of catalog.books) {
    if (!entry || !collectionById.has(entry.collectionId)
      || !Number.isInteger(entry.number) || entry.number < 1
      || entry.id !== qualifiedBookId(entry.collectionId, entry.number) || entryById.has(entry.id)
      || !isText(entry.label) || !isRelativePath(entry.path) || paths.has(entry.path)
      || !Number.isInteger(entry.sections) || entry.sections < 1
      || !Number.isInteger(entry.tokens) || entry.tokens < 0
      || !Number.isInteger(entry.bytes) || entry.bytes < 1
      || !isSHA256(entry.sha256) || !isSHA256(entry.corpusSHA256)) {
      invalid("The search catalog contains an invalid or ambiguous book entry. Reload the page before searching.");
    }
    entryById.set(entry.id, entry);
    paths.add(entry.path);
  }
  const verifyTotals = (actual, entries, label) => {
    for (const [key, expected] of Object.entries(totalsFor(entries))) {
      if (actual?.[key] !== expected) invalid(`${label}'s ${key} total does not agree with its book entries.`);
    }
  };
  for (const collection of catalog.collections) {
    const entries = catalog.books.filter((entry) => entry.collectionId === collection.id).sort((a, b) => a.number - b.number);
    if (JSON.stringify(collection.books) !== JSON.stringify(entries.map((entry) => entry.id))) {
      invalid(`The book references for ${collection.label} do not match the catalog's qualified book IDs in source order.`);
    }
    verifyTotals(collection.totals, entries, collection.label);
  }
  verifyTotals(catalog.totals, catalog.books, "The catalog");
  return catalog;
}

async function sha256(bytes) {
  if (!globalThis.crypto?.subtle) {
    throw new CollectionLoadError("This browser cannot verify the search data. Open the site over HTTPS or localhost.", "VERIFICATION_UNAVAILABLE");
  }
  const hash = new Uint8Array(await globalThis.crypto.subtle.digest("SHA-256", bytes));
  return Array.from(hash, (value) => value.toString(16).padStart(2, "0")).join("");
}

function checkAborted(signal) {
  if (signal?.aborted) {
    const error = new Error("The search was cancelled.");
    error.name = "AbortError";
    throw error;
  }
}

/**
 * createCollection(catalog, lunr, {baseURL, fetchImpl})
 *
 * search(query, {collections:[id]|'all', books:[qualifiedId]|'all',
 *                scope:'section'|'book', fold, onProgress, signal})
 * Both filters default to 'all'. Explicit books outside selected collections
 * are errors. Numeric selectors are rejected even when only one work exists.
 *
 * Results add selectedBooks/matchingBooks (qualified IDs), selectedCollections/
 * matchingCollections, and records. Groups and records carry collection/citation
 * metadata. Records retain their source order and gain resultOrder for display
 * across works whose original order values may each start at zero. Passage IDs
 * must be globally unique. Negative-only book groups still carry all metadata.
 *
 * Progress: {stage:'loading'|'searching', bookId,collectionId,book,bookLabel,
 *            collectionLabel,completed,total,cached,...citation metadata}
 * Successful loads are cached; a failed load is evicted and can be retried.
 * signal is checked between shared downloads, never aborting another request's
 * use of the same download. The UI should still ignore obsolete query results.
 */
export function createCollection(catalog, lunr, options = {}) {
  validateCatalog(catalog);
  const collectionById = new Map(catalog.collections.map((collection) => [collection.id, collection]));
  const entryById = new Map(catalog.books.map((entry) => [entry.id, entry]));
  const entries = catalog.collections.flatMap((collection) => collection.books.map((id) => entryById.get(id)));
  const baseURL = new URL(options.baseURL || "./", import.meta.url);
  const fetchImpl = options.fetchImpl || globalThis.fetch?.bind(globalThis);
  if (typeof fetchImpl !== "function") throw new TypeError("A fetch implementation is required to load search data.");
  const cached = new Map();
  const inFlight = new Map();
  // Concurrent UI requests share downloads; only one new bundle is fetched,
  // parsed, and prepared at a time to keep browser memory use manageable.
  let loadQueue = Promise.resolve();

  function metadata(entry) {
    const collection = collectionById.get(entry.collectionId);
    return {
      bookId: entry.id, collectionId: collection.id, book: entry.number, bookLabel: entry.label,
      work: collection.work, collectionLabel: collection.label, citationPrefix: collection.citationPrefix,
      language: collection.language, edition: collection.edition, readerPath: collection.readerPath,
      citationScheme: collection.citationScheme || "niese",
      citationUnitLabel: collection.unitLabel || (collection.citationScheme === "chapter-paragraph" ? "citation unit" : "Niese section"),
      citationUnitLabelPlural: collection.unitLabelPlural || (collection.citationScheme === "chapter-paragraph" ? "citation units" : "Niese sections"),
    };
  }

  function label(entry) {
    const collection = collectionById.get(entry.collectionId);
    return `${collection.label}, ${entry.label} (${collection.language}; ${collection.edition})`;
  }

  function selection(bookIds, collectionIds) {
    const requestedCollections = collectionIds === undefined || collectionIds === "all"
      ? catalog.collections.map((collection) => collection.id) : Array.isArray(collectionIds) ? collectionIds : [collectionIds];
    if (!requestedCollections.length) throw new CollectionLoadError("Choose at least one text collection to search.", "EMPTY_SELECTION");
    const chosenCollections = new Set();
    for (const id of requestedCollections) {
      if (!collectionById.has(id)) throw new CollectionLoadError(`Text collection ${String(id)} is not available in this search catalog.`, "UNKNOWN_COLLECTION");
      chosenCollections.add(id);
    }
    const values = bookIds === undefined || bookIds === "all"
      ? entries.filter((entry) => chosenCollections.has(entry.collectionId)).map((entry) => entry.id)
      : Array.isArray(bookIds) ? bookIds : [bookIds];
    if (!values.length) throw new CollectionLoadError("Choose at least one book to search.", "EMPTY_SELECTION");
    const chosen = new Set();
    for (const id of values) {
      if (typeof id !== "string" || /^\d+$/.test(id)) {
        throw new CollectionLoadError(`Book ${String(id)} is ambiguous. Choose a qualified book ID such as ${entries[0].id}.`, "AMBIGUOUS_BOOK");
      }
      const entry = entryById.get(id);
      if (!entry) throw new CollectionLoadError(`Book ${id} is not available in this search catalog.`, "UNKNOWN_BOOK", id);
      if (!chosenCollections.has(entry.collectionId)) {
        throw new CollectionLoadError(`${label(entry)} is outside the selected text collections.`, "SELECTION_CONFLICT", entry);
      }
      chosen.add(id);
    }
    return entries.filter((entry) => chosen.has(entry.id));
  }

  function collectionIdsFor(selected) {
    const ids = new Set(selected.map((entry) => entry.collectionId));
    return catalog.collections.filter((collection) => ids.has(collection.id)).map((collection) => collection.id);
  }

  function notify(callback, stage, entry, completed, total, fromCache) {
    if (callback) callback({ stage, ...metadata(entry), completed, total, cached: fromCache });
  }

  function validateBundle(bundle, entry) {
    const fail = (message) => { throw new CollectionLoadError(`${label(entry)}: ${message} No partial search results have been returned.`, "BUNDLE_INVALID", entry); };
    if (bundle?.schemaVersion !== SCHEMA_VERSION || !Array.isArray(bundle.records) || !Array.isArray(bundle.tokens)
      || bundle.records.length !== entry.sections || bundle.tokens.length !== entry.sections
      || !bundle.indexes?.literal || !bundle.indexes?.folded) fail("the search data do not match the catalog.");
    if (bundle.stats?.records !== entry.sections || bundle.stats?.tokens !== entry.tokens || bundle.stats?.books !== 1
      || bundle.tokens.some((tokens) => !Array.isArray(tokens))
      || bundle.tokens.reduce((sum, tokens) => sum + tokens.length, 0) !== entry.tokens) fail("the indexed coverage is inconsistent.");
    if (bundle.source?.corpusSHA256 !== entry.corpusSHA256) fail("the corpus fingerprint does not match the catalog.");
    if (catalog.source?.lunrVersion && bundle.source?.lunrVersion !== catalog.source.lunrVersion) fail("the search-library version does not match the catalog.");
    const collection = collectionById.get(entry.collectionId);
    const ids = new Set();
    const citations = new Set();
    for (const record of bundle.records) {
      if (Number(record.book) !== entry.number || typeof record.id !== "string" || !record.id || ids.has(record.id)
        || typeof record.text !== "string" || !Number.isFinite(record.order)) fail("the passage identifiers or book references are inconsistent.");
      for (const field of ["work", "language", "edition"]) {
        if (record[field] !== collection[field]) fail("the work, language, or edition does not match the catalog.");
      }
      if (collection.citationScheme === "chapter-paragraph") {
        const expectedLabel = record.chapter === 0 ? `Prol.${record.paragraph}` : `${romanBook(record.book)}.${record.chapter}.${record.paragraph}`;
        if (record.citationScheme !== "chapter-paragraph" || !Number.isInteger(record.section) || record.section < 1
          || !Number.isInteger(record.chapter) || record.chapter < 0 || !Number.isInteger(record.paragraph) || record.paragraph < 1
          || !isText(record.sourceId) || record.citationLabel !== expectedLabel || citations.has(record.citationLabel)) {
          fail("the chapter/paragraph citations do not agree with their source records.");
        }
        citations.add(record.citationLabel);
      } else if (record.citationScheme !== undefined && record.citationScheme !== "niese") {
        fail("the passage citation scheme does not match the catalog.");
      }
      try { editorialMarksFor(record); } catch { fail("the editorial marks do not agree with their original-text offsets."); }
      ids.add(record.id);
    }
  }

  async function fetchBook(entry) {
    try {
      const response = await fetchImpl(new URL(entry.path, baseURL), { cache: "no-cache" });
      if (!response.ok) throw new CollectionLoadError(`${label(entry)} could not be loaded (HTTP ${response.status}). No partial results have been returned; please retry.`, "BOOK_LOAD_FAILED", entry);
      const bytes = new Uint8Array(await response.arrayBuffer());
      if (bytes.byteLength !== entry.bytes || await sha256(bytes) !== entry.sha256.toLowerCase()) {
        throw new CollectionLoadError(`${label(entry)} did not pass its data-integrity check. No partial results have been returned; reload the page and retry.`, "BUNDLE_INTEGRITY", entry);
      }
      await yieldTurn();
      const bundle = JSON.parse(new TextDecoder().decode(bytes));
      validateBundle(bundle, entry);
      const engine = createEngine(bundle, lunr);
      cached.set(entry.id, engine);
      return engine;
    } catch (error) {
      cached.delete(entry.id);
      if (error instanceof CollectionLoadError) throw error;
      throw new CollectionLoadError(`${label(entry)} could not be read. No partial results have been returned; please retry.`, "BOOK_LOAD_FAILED", entry, error);
    }
  }

  function loadBook(entry) {
    if (cached.has(entry.id)) return Promise.resolve(cached.get(entry.id));
    if (inFlight.has(entry.id)) return inFlight.get(entry.id);
    const pending = loadQueue.then(() => cached.get(entry.id) || fetchBook(entry));
    loadQueue = pending.catch(() => undefined);
    const tracked = pending.finally(() => inFlight.delete(entry.id));
    inFlight.set(entry.id, tracked);
    return tracked;
  }

  function collectedRecords(selected) {
    const records = [];
    const ids = new Set();
    for (const entry of selected) {
      const sorted = cached.get(entry.id).records.slice().sort((a, b) => a.order - b.order);
      for (const record of sorted) {
        if (ids.has(record.id)) {
          cached.delete(entry.id);
          throw new CollectionLoadError(`${label(entry)} repeats a passage identifier from another selected book or text version. No partial results have been returned.`, "BUNDLE_INVALID", entry);
        }
        ids.add(record.id);
        records.push({ ...record, ...metadata(entry), resultOrder: records.length });
      }
    }
    return records;
  }

  async function loadBooks(bookIds, loadingOptions = {}) {
    const selected = selection(bookIds, loadingOptions.collections);
    for (let i = 0; i < selected.length; i += 1) {
      checkAborted(loadingOptions.signal);
      const entry = selected[i];
      notify(loadingOptions.onProgress, "loading", entry, i, selected.length, cached.has(entry.id));
      checkAborted(loadingOptions.signal);
      await loadBook(entry);
      checkAborted(loadingOptions.signal);
      await yieldTurn();
    }
    notify(loadingOptions.onProgress, "loading", selected[selected.length - 1], selected.length, selected.length, true);
    return { selectedBooks: selected.map((entry) => entry.id), selectedCollections: collectionIdsFor(selected), records: collectedRecords(selected) };
  }

  async function search(query, searchOptions = {}) {
    const scope = searchOptions.scope ?? "section";
    if (scope !== "section" && scope !== "book") throw new TypeError("Search scope must be section or book.");
    // Reject syntax errors before any download. Each unchanged book engine will
    // parse the same expression independently when its turn is reached.
    parseQuery(query);
    const selected = selection(searchOptions.books, searchOptions.collections);
    // Latin spelling equivalence is a property of the selected edition. It
    // must not turn English "just" into "iust" in a mixed-language search.
    const selectedCollections = collectionIdsFor(selected);
    const foldedCollectionIds = searchOptions.fold
      ? selectedCollections.filter(id => collectionById.get(id).language === "Latin") : [];
    const fold = foldedCollectionIds.length > 0;
    const loaded = await loadBooks(selected.map((entry) => entry.id), searchOptions);
    const merged = {
      query, scope, fold,
      normalization: {caseSensitive: false, spellingEquivalence: fold ? "latin-uv-ij" : "none",
        foldedCollectionIds, literalCollectionIds: selectedCollections.filter(id => !foldedCollectionIds.includes(id))},
      selectedBooks: loaded.selectedBooks, selectedCollections: loaded.selectedCollections,
      matchingBooks: [], matchingCollections: [],
      matchingUnits: 0, matchingSections: 0, occurrences: 0,
      hitGroups: [], records: loaded.records,
    };
    const matchingEntries = [];
    for (let i = 0; i < selected.length; i += 1) {
      checkAborted(searchOptions.signal);
      const entry = selected[i];
      notify(searchOptions.onProgress, "searching", entry, i, selected.length, true);
      checkAborted(searchOptions.signal);
      let result;
      try {
        result = cached.get(entry.id).search(query, { scope, fold: foldedCollectionIds.includes(entry.collectionId) });
      } catch (error) {
        cached.delete(entry.id);
        throw new CollectionLoadError(`${label(entry)} could not be searched. No partial results have been returned; reload the page and retry.`, "BOOK_SEARCH_FAILED", entry, error);
      }
      if (result.matchingUnits) {
        merged.matchingBooks.push(entry.id);
        matchingEntries.push(entry);
      }
      merged.matchingUnits += result.matchingUnits;
      merged.matchingSections += result.matchingSections;
      merged.occurrences += result.occurrences;
      const recordById = new Map(merged.records.filter((record) => record.bookId === entry.id).map((record) => [record.id, record]));
      merged.hitGroups.push(...result.hitGroups.map((group) => {
        const mergedGroup = { ...group, unitId: `${entry.id}:${group.unitId}`, ...metadata(entry) };
        if (mergedGroup.citationScheme === "chapter-paragraph") {
          mergedGroup.unitLabel = scope === "book" ? bookCitation(mergedGroup) : citationFor(group.recordIds.map((id) => recordById.get(id)));
        }
        return mergedGroup;
      }));
      await yieldTurn();
    }
    checkAborted(searchOptions.signal);
    merged.matchingCollections = collectionIdsFor(matchingEntries);
    notify(searchOptions.onProgress, "searching", selected[selected.length - 1], selected.length, selected.length, true);
    return merged;
  }

  return {
    catalog, loadBooks, search,
    get cachedBooks() { return entries.filter((entry) => cached.has(entry.id)).map((entry) => entry.id); },
  };
}
