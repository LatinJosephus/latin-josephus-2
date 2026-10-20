/**
 * LatinJosephus static concordance engine.
 *
 * Lunr owns the prebuilt word index and wildcard expansion. This module owns
 * the documented Boolean grammar, Unicode tokenization, and passage evidence.
 * Offsets always address the ORIGINAL record.text, in JavaScript string units.
 */

export const SCHEMA_VERSION = 1;
export const QUERY_LIMITS = Object.freeze({
  characters: 2000,
  terms: 64,
  nesting: 32,
  patternCharacters: 128,
  wildcardsPerPattern: 16,
});

const WORDS = /[\p{L}\p{N}][\p{L}\p{M}\p{N}]*/gu;
const PATTERN_WORDS = /[\p{L}\p{M}\p{N}*]+/gu;
const WORD_CHARACTER = /[\p{L}\p{M}\p{N}*]/u;
const QUERY_SEPARATOR = /[\s.,;:'’‘\-–—·]/u;
const OPERATORS = new Set(["AND", "OR", "NOT"]);
const CACHE_SIZE = 128;

export class QueryError extends Error {
  constructor(message, code = "INVALID_QUERY", position = 0) {
    super(message);
    this.name = "QueryError";
    this.code = code;
    this.position = position;
  }
}

/** Case-insensitive NFC word key; Greek final sigma shares its case pair. */
export function normalizeTerm(value, fold = false) {
  let term = String(value).normalize("NFC").toLowerCase().replace(/ς/g, "σ");
  if (fold) term = term.replace(/v/g, "u").replace(/j/g, "i");
  return term.normalize("NFC");
}

/** Punctuation separates words, but original character offsets are retained. */
export function tokenizeText(text) {
  return Array.from(String(text).matchAll(WORDS), (match) => ({
    term: normalizeTerm(match[0]),
    start: match.index,
    end: match.index + match[0].length,
  }));
}

/** A zero-width TEI gap may interrupt a word as well as phrase adjacency. */
export function tokenizeRecord(record) {
  const text = String(record.text);
  const offsets = [...new Set((record.textGaps || [])
    .filter(gap => gap.kind === "tei-gap" && gap.start === gap.end)
    .map(gap => gap.start))].sort((a, b) => a - b);
  if (offsets.some(offset => !Number.isInteger(offset) || offset < 0 || offset > text.length)) {
    throw new TypeError(`Invalid explicit source gap for ${record.id}.`);
  }
  if (!offsets.length) return tokenizeText(text);
  const tokens = [];
  let start = 0;
  for (const end of [...offsets, text.length]) {
    for (const token of tokenizeText(text.slice(start, end))) {
      tokens.push({ ...token, start: token.start + start, end: token.end + start });
    }
    start = end;
  }
  return tokens;
}

/** Explicit source boundaries block phrase adjacency without removing any text. */
export function phraseBreakOffsets(record, tokens = tokenizeRecord(record)) {
  if (record.phraseBreaks === undefined) return [];
  if (!Array.isArray(record.phraseBreaks)) throw new TypeError(`Invalid phrase boundaries for ${record.id}.`);
  let previous = -1;
  for (const offset of record.phraseBreaks) {
    if (!Number.isInteger(offset) || offset <= previous || offset < 0 || offset > record.text.length
      || tokens.some(token => token.start < offset && offset < token.end)) {
      throw new TypeError(`A phrase boundary must be an ordered original-text offset between words: ${record.id}.`);
    }
    previous = offset;
  }
  return record.phraseBreaks;
}

function bookKey(record) {
  // A book unit is one text version. Identical section numbers in different
  // languages or editions must never satisfy a shared AND or joined phrase.
  return `book:${encodeURIComponent(record.work)}:${encodeURIComponent(record.book)}:${encodeURIComponent(record.language || "")}:${encodeURIComponent(record.edition || "")}`;
}

function labelWork(work) {
  return work === "bellum" ? "Bellum" : work === "antiquities" ? "Antiquities" : work;
}

function sectionLabel(record) {
  return `${labelWork(record.work)} ${record.citationUnitCitation || `${record.book}.${record.section}`}`;
}

const sectionKey = record => record.citationUnitId ?? record.id;

function validateCitationUnits(records) {
  const units = new Map();
  for (const record of records) {
    const id = sectionKey(record);
    if (typeof id !== "string" || !id) throw new TypeError(`Invalid citation unit for ${record.id}.`);
    const signature = JSON.stringify([bookKey(record), String(record.section)]);
    if (units.has(id) && units.get(id) !== signature) {
      throw new TypeError(`A citation unit cannot combine works, books, versions, or section identities: ${id}.`);
    }
    units.set(id, signature);
  }
}

function buildIndex(records, tokens, lunr, fold) {
  return lunr(function () {
    // The default English stemmer, stop-word filter, and ASCII trimmer are all
    // inappropriate here. Input is already a Unicode-tokenized array of words.
    this.pipeline.reset();
    this.searchPipeline.reset();
    this.ref("id");
    this.field("text");
    for (let i = 0; i < records.length; i += 1) {
      this.add({
        id: records[i].id,
        text: tokens[i].map((token) => normalizeTerm(token.term, fold)),
      });
    }
  }).toJSON();
}

/**
 * Build a deterministic, JSON-serializable search bundle from extracted TEI
 * records. This function never changes the supplied array or record objects.
 */
export function buildBundle(inputRecords, lunr) {
  if (!Array.isArray(inputRecords) || inputRecords.length === 0) {
    throw new TypeError("The corpus must be a nonempty array of passage records.");
  }
  if (typeof lunr !== "function") throw new TypeError("A Lunr function is required.");
  const ids = new Set();
  const records = inputRecords.map((source, i) => {
    if (!source || typeof source.id !== "string" || !source.id) {
      throw new TypeError(`Corpus record ${i + 1} needs a nonempty string id.`);
    }
    if (ids.has(source.id)) throw new TypeError(`Duplicate corpus id: ${source.id}`);
    ids.add(source.id);
    if (typeof source.text !== "string" || typeof source.work !== "string" || !source.work) {
      throw new TypeError(`Record ${source.id} needs text and work strings.`);
    }
    if (source.book === undefined || source.section === undefined) {
      throw new TypeError(`Record ${source.id} needs book and section references.`);
    }
    const order = source.order ?? i;
    if (!Number.isFinite(order)) throw new TypeError(`Invalid order for ${source.id}.`);
    return { ...source, order, breakBefore: Boolean(source.breakBefore) };
  });
  validateCitationUnits(records);
  const tokens = records.map(tokenizeRecord);
  records.forEach((record, index) => phraseBreakOffsets(record, tokens[index]));
  const tokenCount = tokens.reduce((sum, group) => sum + group.length, 0);
  const vocabulary = new Set(tokens.flatMap((group) => group.map((token) => token.term)));
  return {
    schemaVersion: SCHEMA_VERSION,
    tokenizer: "unicode-words-nfc-case-v1",
    records,
    tokens,
    indexes: {
      literal: buildIndex(records, tokens, lunr, false),
      folded: buildIndex(records, tokens, lunr, true),
    },
    stats: {
      records: records.length,
      books: new Set(records.map(bookKey)).size,
      tokens: tokenCount,
      vocabulary: vocabulary.size,
    },
  };
}

function validatePattern(pattern, position) {
  if (pattern.length > QUERY_LIMITS.patternCharacters) {
    throw new QueryError(
      `A search word may contain at most ${QUERY_LIMITS.patternCharacters} characters.`,
      "PATTERN_TOO_LONG", position,
    );
  }
  const compact = pattern.replace(/\*+/g, "*");
  if ((compact.match(/\*/g) || []).length > QUERY_LIMITS.wildcardsPerPattern) {
    throw new QueryError(
      `A search word may contain at most ${QUERY_LIMITS.wildcardsPerPattern} separate wildcards.`,
      "TOO_MANY_WILDCARDS", position,
    );
  }
  return compact;
}

function lex(query) {
  if (typeof query !== "string" || !query.trim()) {
    throw new QueryError("Enter a word, a phrase, or a Boolean expression.", "EMPTY_QUERY");
  }
  if (query.length > QUERY_LIMITS.characters) {
    throw new QueryError(
      `The query is too long. Use at most ${QUERY_LIMITS.characters} characters.`,
      "QUERY_TOO_LONG", QUERY_LIMITS.characters,
    );
  }
  const tokens = [];
  let i = 0;
  let wordCount = 0;
  while (i < query.length) {
    const character = String.fromCodePoint(query.codePointAt(i));
    if (QUERY_SEPARATOR.test(character)) {
      i += character.length;
      continue;
    }
    if (character === "(" || character === ")") {
      tokens.push({ type: character, position: i });
      i += 1;
      continue;
    }
    if (character === '"') {
      const position = i;
      i += 1;
      let contents = "";
      let closed = false;
      while (i < query.length) {
        if (query[i] === '"') {
          i += 1;
          closed = true;
          break;
        }
        if (query[i] === "\\" && (query[i + 1] === '"' || query[i + 1] === "\\")) {
          contents += query[i + 1];
          i += 2;
        } else {
          contents += query[i];
          i += 1;
        }
      }
      if (!closed) throw new QueryError("Close the quoted phrase with a double quotation mark.", "UNCLOSED_PHRASE", position);
      const patterns = Array.from(contents.matchAll(PATTERN_WORDS), (match) => validatePattern(match[0], position + 1 + match.index));
      if (!patterns.length) throw new QueryError("A quoted phrase must contain at least one word.", "EMPTY_PHRASE", position);
      wordCount += patterns.length;
      tokens.push({ type: "PHRASE", patterns, raw: query.slice(position, i), position });
      continue;
    }
    if (WORD_CHARACTER.test(character)) {
      const position = i;
      let raw = "";
      while (i < query.length) {
        const next = String.fromCodePoint(query.codePointAt(i));
        if (!WORD_CHARACTER.test(next)) break;
        raw += next;
        i += next.length;
      }
      if (OPERATORS.has(raw)) tokens.push({ type: raw, position });
      else {
        wordCount += 1;
        tokens.push({ type: "TERM", patterns: [validatePattern(raw, position)], raw, position });
      }
      continue;
    }
    const hint = character === "?"
      ? "Use * for a wildcard; ? is not supported."
      : `Unexpected character “${character}”. Use words, *, AND, OR, NOT, parentheses, or a quoted phrase.`;
    throw new QueryError(hint, "UNEXPECTED_CHARACTER", i);
  }
  if (!tokens.length) throw new QueryError("Enter at least one search word.", "EMPTY_QUERY");
  if (wordCount > QUERY_LIMITS.terms) {
    throw new QueryError(`Use at most ${QUERY_LIMITS.terms} search words, including words inside phrases.`, "TOO_MANY_TERMS");
  }
  tokens.push({ type: "EOF", position: query.length });
  return tokens;
}

/** Uppercase operators; implicit AND; NOT > AND > OR. */
export function parseQuery(query) {
  const tokens = lex(query);
  let cursor = 0;
  const current = () => tokens[cursor];
  const operandStarts = (type) => ["TERM", "PHRASE", "(", "NOT"].includes(type);
  function checkDepth(depth) {
    if (depth > QUERY_LIMITS.nesting) {
      throw new QueryError(`Use at most ${QUERY_LIMITS.nesting} nested parentheses or NOT operators.`, "TOO_DEEPLY_NESTED", current().position);
    }
  }
  function unary(depth) {
    checkDepth(depth);
    const token = current();
    if (token.type === "NOT") {
      cursor += 1;
      return { type: "not", child: unary(depth + 1) };
    }
    if (token.type === "(") {
      cursor += 1;
      if (current().type === ")") throw new QueryError("Put a word or expression inside the parentheses.", "EMPTY_GROUP", token.position);
      const node = disjunction(depth + 1);
      if (current().type !== ")") throw new QueryError("Close the opening parenthesis.", "UNCLOSED_GROUP", token.position);
      cursor += 1;
      return node;
    }
    if (token.type === "TERM" || token.type === "PHRASE") {
      cursor += 1;
      return { type: "leaf", kind: token.type === "TERM" ? "term" : "phrase", patterns: token.patterns, queryText: token.raw };
    }
    const preceding = tokens[Math.max(0, cursor - 1)];
    const suffix = ["AND", "OR", "NOT"].includes(preceding.type) ? ` after ${preceding.type}` : "";
    throw new QueryError(`Expected a word, a quoted phrase, or a parenthesized expression${suffix}.`, "EXPECTED_OPERAND", token.position);
  }
  function conjunction(depth) {
    let node = unary(depth);
    while (current().type === "AND" || operandStarts(current().type)) {
      if (current().type === "AND") cursor += 1;
      node = { type: "and", left: node, right: unary(depth) };
    }
    return node;
  }
  function disjunction(depth) {
    let node = conjunction(depth);
    while (current().type === "OR") {
      cursor += 1;
      node = { type: "or", left: node, right: conjunction(depth) };
    }
    return node;
  }
  const tree = disjunction(0);
  if (current().type !== "EOF") {
    const message = current().type === ")" ? "This closing parenthesis has no matching opening parenthesis." : "Unexpected search operator.";
    throw new QueryError(message, "UNEXPECTED_TOKEN", current().position);
  }
  return tree;
}

/** Anchored glob with *=zero or more, without regular-expression backtracking. */
export function wildcardMatches(pattern, word) {
  let p = 0;
  let w = 0;
  let star = -1;
  let checkpoint = 0;
  while (w < word.length) {
    if (p < pattern.length && pattern[p] === word[w]) {
      p += 1;
      w += 1;
    } else if (p < pattern.length && pattern[p] === "*") {
      star = p;
      p += 1;
      checkpoint = w;
    } else if (star !== -1) {
      p = star + 1;
      checkpoint += 1;
      w = checkpoint;
    } else return false;
  }
  while (p < pattern.length && pattern[p] === "*") p += 1;
  return p === pattern.length;
}

function hitKey(hit) {
  return JSON.stringify(hit.spans.map((span) => [span.recordId, span.start, span.end]));
}

function deduplicateHits(hits) {
  const unique = new Map();
  for (const hit of hits) {
    const key = hitKey(hit);
    const previous = unique.get(key);
    if (!previous) {
      unique.set(key, { ...hit, queryTexts: [hit.queryText] });
    } else if (!previous.queryTexts.includes(hit.queryText)) {
      previous.queryTexts.push(hit.queryText);
    }
  }
  return [...unique.values()];
}

function intersection(left, right) {
  return new Set([...left].filter((value) => right.has(value)));
}

/** Load the bundle; Lunr indexes themselves are loaded lazily per spelling mode. */
export function createEngine(bundle, lunr) {
  if (!bundle || bundle.schemaVersion !== SCHEMA_VERSION || !Array.isArray(bundle.records) || !Array.isArray(bundle.tokens)) {
    throw new TypeError("Unsupported or incomplete search index. Rebuild the search bundle.");
  }
  if (!lunr?.Index?.load) throw new TypeError("Lunr with Index.load is required.");
  if (bundle.records.length !== bundle.tokens.length) throw new TypeError("Search records and token arrays do not agree.");
  const records = bundle.records;
  validateCitationUnits(records);
  const recordById = new Map();
  const tokenById = new Map();
  const sections = new Map();
  const foldedTokens = new Map();
  const books = new Map();
  const recordRank = new Map();
  const globalTokenIndex = new Map();
  const loaded = {};
  const lookupCache = new Map();
  for (let index = 0; index < records.length; index += 1) {
    const record = records[index];
    if (recordById.has(record.id)) throw new TypeError(`Duplicate record in search bundle: ${record.id}`);
    recordById.set(record.id, record);
    tokenById.set(record.id, bundle.tokens[index]);
    foldedTokens.set(record.id, bundle.tokens[index].map((token) => normalizeTerm(token.term, true)));
    const key = bookKey(record);
    if (!books.has(key)) books.set(key, { id: key, work: record.work, book: record.book, records: [], tokens: [] });
    books.get(key).records.push({ record, originalIndex: index });
    const unitId = sectionKey(record);
    if (!sections.has(unitId)) sections.set(unitId, { records: [] });
    sections.get(unitId).records.push(record);
  }
  let rank = 0;
  for (const book of books.values()) {
    book.records.sort((a, b) => a.record.order - b.record.order || a.originalIndex - b.originalIndex);
    let segment = 0, unitSegment = 0, previousUnit;
    for (const entry of book.records) {
      const record = entry.record;
      if (sectionKey(record) !== previousUnit) unitSegment++;
      previousUnit = sectionKey(record);
      recordRank.set(record.id, rank++);
      if (record.breakBefore) segment += 1;
      const locations = [];
      const tokens = tokenById.get(record.id);
      const breaks = phraseBreakOffsets(record, tokens);
      let boundary = 0;
      for (let tokenIndex = 0; tokenIndex < tokens.length; tokenIndex += 1) {
        while (boundary < breaks.length && breaks[boundary] <= tokens[tokenIndex].start) {
          segment += 1;
          boundary += 1;
        }
        locations.push(book.tokens.length);
        const token = { ...tokens[tokenIndex], recordId: record.id, tokenIndex, segment, unitSegment };
        book.tokens.push(token);
      }
      // A marker after the final word also separates the next citation unit.
      segment += breaks.length - boundary;
      globalTokenIndex.set(record.id, locations);
    }
  }
  for (const unit of sections.values()) unit.records.sort((a, b) => recordRank.get(a.id) - recordRank.get(b.id));

  function getIndex(fold) {
    const key = fold ? "folded" : "literal";
    if (!loaded[key]) loaded[key] = lunr.Index.load(bundle.indexes[key]);
    return loaded[key];
  }

  // Cache word-pattern postings, not a truncated vocabulary expansion. Every
  // occurrence in every matching record is checked against the actual token.
  function lookup(pattern, fold) {
    const key = `${fold ? "1" : "0"}:${pattern}`;
    if (lookupCache.has(key)) {
      const cached = lookupCache.get(key);
      lookupCache.delete(key);
      lookupCache.set(key, cached);
      return cached;
    }
    const matches = new Map();
    const results = getIndex(fold).query((query) => {
      query.term(pattern, { fields: ["text"], usePipeline: false });
    });
    for (const result of results) {
      const tokens = tokenById.get(result.ref);
      if (!tokens) throw new Error(`Index refers to an unknown passage: ${result.ref}`);
      const folded = fold ? foldedTokens.get(result.ref) : null;
      const occurrences = [];
      for (let i = 0; i < tokens.length; i += 1) {
        if (wildcardMatches(pattern, folded ? folded[i] : tokens[i].term)) {
          occurrences.push({ tokenIndex: i, start: tokens[i].start, end: tokens[i].end });
        }
      }
      if (occurrences.length) matches.set(result.ref, occurrences);
    }
    lookupCache.set(key, matches);
    if (lookupCache.size > CACHE_SIZE) lookupCache.delete(lookupCache.keys().next().value);
    return matches;
  }

  function unitsFor(postings, scope) {
    return new Set([...postings.keys()].map((id) => scope === "section" ? sectionKey(recordById.get(id)) : bookKey(recordById.get(id))));
  }

  function leafMatches(leaf, scope, fold) {
    const patterns = leaf.patterns.map((term) => normalizeTerm(term, fold));
    const postings = patterns.map((pattern) => lookup(pattern, fold));
    const result = new Map();
    const push = (unitId, hit) => {
      if (!result.has(unitId)) result.set(unitId, []);
      result.get(unitId).push({ ...hit, queryText: leaf.queryText });
    };
    if (leaf.kind === "term") {
      for (const [recordId, occurrences] of postings[0]) {
        const unitId = scope === "section" ? sectionKey(recordById.get(recordId)) : bookKey(recordById.get(recordId));
        for (const occurrence of occurrences) {
          push(unitId, { kind: "term", spans: [{ recordId, start: occurrence.start, end: occurrence.end }] });
        }
      }
      return result;
    }
    let candidates = unitsFor(postings[0], scope);
    for (let i = 1; i < postings.length && candidates.size; i += 1) candidates = intersection(candidates, unitsFor(postings[i], scope));
    if (!candidates.size) return result;

    // Anchor on the rarest phrase word. This also finds phrases crossing a
    // Niese boundary in book mode without scanning every book for each phrase.
    const sizes = postings.map((posting) => [...posting.values()].reduce((sum, list) => sum + list.length, 0));
    const anchor = sizes.indexOf(Math.min(...sizes));
    for (const [recordId, occurrences] of postings[anchor]) {
      const unitId = scope === "section" ? sectionKey(recordById.get(recordId)) : bookKey(recordById.get(recordId));
      if (!candidates.has(unitId)) continue;
      // Logical sections can have displaced portions. Phrases always follow
      // the physical source stream, even when Boolean scope is one section.
      const sequence = books.get(bookKey(recordById.get(recordId))).tokens;
      for (const occurrence of occurrences) {
        const anchorPosition = globalTokenIndex.get(recordId)[occurrence.tokenIndex];
        const start = anchorPosition - anchor;
        if (start < 0 || start + patterns.length > sequence.length) continue;
        let accepted = true;
        for (let i = 0; i < patterns.length; i += 1) {
          const token = sequence[start + i];
          if (token.segment !== sequence[start].segment
            || (scope === "section" && (token.unitSegment !== sequence[start].unitSegment
              || sectionKey(recordById.get(token.recordId)) !== unitId))) {
            accepted = false;
            break;
          }
          if (!wildcardMatches(patterns[i], normalizeTerm(token.term, fold))) {
            accepted = false;
            break;
          }
        }
        if (!accepted) continue;
        const spans = [];
        for (let i = 0; i < patterns.length; i += 1) {
          const token = sequence[start + i];
          const owner = token.recordId;
          const previous = spans[spans.length - 1];
          if (previous?.recordId === owner) previous.end = token.end;
          else spans.push({ recordId: owner, start: token.start, end: token.end });
        }
        push(unitId, { kind: "phrase", spans });
      }
    }
    return result;
  }

  function search(query, options = {}) {
    const scope = options.scope ?? "section";
    const fold = Boolean(options.fold);
    if (scope !== "section" && scope !== "book") throw new TypeError("Search scope must be section or book.");
    const tree = parseQuery(query);
    const universe = scope === "section" ? new Set(sections.keys()) : new Set(books.keys());
    const leafCache = new Map();
    function evaluate(node, negated = false) {
      if (node.type === "not") return evaluate(node.child, !negated);
      if (node.type === "leaf") {
        if (!leafCache.has(node)) leafCache.set(node, leafMatches(node, scope, fold));
        const matches = leafCache.get(node);
        if (!negated) return matches;
        return new Map([...universe].filter((id) => !matches.has(id)).map((id) => [id, []]));
      }
      // Pushing NOT through the tree applies De Morgan's rules, and preserves
      // positive evidence in expressions such as NOT NOT a / NOT(a OR NOT b).
      const operation = negated ? (node.type === "and" ? "or" : "and") : node.type;
      const left = evaluate(node.left, negated);
      const right = evaluate(node.right, negated);
      const combined = new Map();
      if (operation === "and") {
        for (const [id, hits] of left) if (right.has(id)) combined.set(id, [...hits, ...right.get(id)]);
      } else {
        for (const [id, hits] of left) combined.set(id, hits.slice());
        for (const [id, hits] of right) combined.set(id, [...(combined.get(id) || []), ...hits]);
      }
      return combined;
    }
    const results = evaluate(tree);
    const hitGroups = [];
    const touched = new Set();
    for (const [unitId, evidence] of results) {
      const hits = deduplicateHits(evidence);
      hits.sort((a, b) => {
        const firstA = a.spans[0];
        const firstB = b.spans[0];
        return recordRank.get(firstA.recordId) - recordRank.get(firstB.recordId)
          || firstA.start - firstB.start || firstA.end - firstB.end;
      });
      const recordIds = scope === "section"
        ? sections.get(unitId).records.map(record => record.id)
        : [...new Set(hits.flatMap((hit) => hit.spans.map((span) => span.recordId)))].sort((a, b) => recordRank.get(a) - recordRank.get(b));
      for (const id of recordIds) touched.add(sectionKey(recordById.get(id)));
      const source = scope === "section" ? sections.get(unitId).records[0] : books.get(unitId);
      hitGroups.push({
        unitId,
        unitLabel: scope === "section" ? sectionLabel(source) : `${labelWork(source.work)} · Book ${source.book}`,
        recordIds,
        sections: [...new Set(recordIds.map((id) => recordById.get(id).section))],
        hits,
      });
    }
    const unitRank = (group) => scope === "section"
      ? recordRank.get(sections.get(group.unitId).records[0].id)
      : recordRank.get(books.get(group.unitId).records[0].record.id);
    hitGroups.sort((a, b) => unitRank(a) - unitRank(b));
    return {
      query,
      scope,
      fold,
      matchingUnits: hitGroups.length,
      matchingSections: touched.size,
      occurrences: hitGroups.reduce((sum, group) => sum + group.hits.length, 0),
      hitGroups,
    };
  }

  return { records, search };
}
