/**
 * Independent corpus oracle for Cardwell Latin Bellum I-VII.
 * Run: node bin/search/tests/corpus-qa.mjs
 * A different reviewed reader can be selected explicitly with
 * --expected-reader-sha256 <accepted SHA-256>; unknown readers are never accepted
 * merely because they happen to be present in the checkout.
 * This deliberately imports no parser, tokenizer, or matching helpers from the
 * production engine. A separate raw-XML scanner verifies the running text;
 * Unicode token postings and an AST/set oracle verify the search independently.
 */
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { performance } from 'node:perf_hooks';
import { createEngine } from '../engine.mjs';
import { createCollection } from '../collection.mjs';
import {repositoryRelativeReportPath} from './report-path.mjs';

const suiteStarted = performance.now();
const require = createRequire(import.meta.url);
const lunr = require('../vendor/lunr.cjs');
const pilotDir = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repositoryDir = resolve(pilotDir, '../..');
const reportPath = file => repositoryRelativeReportPath(repositoryDir, file);
const collectionId = 'bellum-latin-cardwell';
const bookId = number => `${collectionId}:${number}`;
const sourceSpecs = [
  {book:1, sections:673, sha256:'24277e94089fd25c403662c01e104f0c6a437d5c0f125a21624651bd20e87240'},
  {book:2, sections:654, sha256:'6fd44eee69db8481d9f48680669c359c13b287144ae85584e7666b72b1da4b09'},
  {book:3, sections:542, sha256:'3b3a5351b63f54acbff136b431d2c1a62a7c24237de0a32f1b91ad6c5029ff49'},
  {book:4, sections:663, sha256:'8726a4d8d2408f45cf509301da0960881ed61f5699eb03f38052e87eb6bc6e98'},
  {book:5, sections:572, sha256:'b710d8acb392063cfbe3f4730ded533a38737085167cf60edacf8622bb08bd31'},
  {book:6, sections:442, sha256:'a93c32f5aa6b2254abb3783a23e2529bec47ae0b1f878d7582c5c34411a4e46b'},
  {book:7, sections:455, sha256:'c9c5cc7988aab7bfd453db3901f601dc8942a9fa1a2ac5011c6c474b624e5042'},
];
const readerPath = resolve(repositoryDir, 'assets/js/renderTei.js');
const enginePath = resolve(pilotDir, 'engine.mjs');
const collectionPath = resolve(pilotDir, 'collection.mjs');
const catalogPath = resolve(pilotDir, 'catalog.json');
const combinedCorpusPath = resolve(pilotDir, 'corpus.json');
const digest = path => createHash('sha256').update(readFileSync(path)).digest('hex');
const acceptedReaders = new Map([
  ['03bfb9b0de5e13e6b07bd638413b2b82a9ed2f7b0cc7c33eb6c09dabde3c9294', 'canonical-2026-10-14'],
  ['25c00a11818fe5a71dcbffb516aeb8a6f02c6b61c218f4e85105a12eb310d0ed', 'approved-public-preview'],
]);
const args = process.argv.slice(2);
assert.ok(args.length === 0 || (args.length === 2 && args[0] === '--expected-reader-sha256'
  && /^[a-f0-9]{64}$/i.test(args[1])),
  'Usage: node bin/search/tests/corpus-qa.mjs [--expected-reader-sha256 <accepted SHA-256>]');
const observedReaderSHA = digest(readerPath);
const explicitReaderSHA = args.length ? args[1].toLowerCase() : null;
assert.ok(explicitReaderSHA || acceptedReaders.has(observedReaderSHA),
  `Unreviewed reader baseline ${observedReaderSHA}. Review its changes before explicitly supplying --expected-reader-sha256.`);
const readerSHA = explicitReaderSHA || observedReaderSHA;
assert.equal(observedReaderSHA, readerSHA, 'Reader bytes differ from the explicitly accepted baseline.');
const readerBaseline = {
  expectedSha256: readerSHA, observedSha256: observedReaderSHA,
  provenance: explicitReaderSHA ? 'explicit-argument' : acceptedReaders.get(readerSHA),
  preservationDuringRunRequired: true,
  publicationInput: false,
  acceptedBaselineComparison: acceptedReaders.has(readerSHA) ? {
    classification: 'Substantive difference; both reviewed files use LF line endings.',
    difference: 'The public-preview reader adds antiquitiesBookNumberingDisplayCopy (117 lines) and calls it during view rendering. The canonical-2026-10-14 reader lacks that helper and call. No other differences were found.',
    consequence: 'The difference concerns Antiquities book-level numbering display. Both accepted baselines retain the same Bellum Niese extraction and URL navigation code.',
  } : null,
};
const suiteFileHashes = new Map([readerPath, enginePath, collectionPath, catalogPath, combinedCorpusPath]
  .map(path => [path, digest(path)]));

function runBook(spec) {
const started = performance.now();
const bookNumber = spec.book;
const paddedBook = String(bookNumber).padStart(2, '0');
const bundlePath = resolve(pilotDir, `data/${collectionId}/book-${paddedBook}.bundle.json`);
const corpusPath = resolve(pilotDir, `data/book-${paddedBook}.corpus.json`);
const sourcePath = resolve(repositoryDir, `assets/xml/bellum/Latin/book-${paddedBook}.xml`);
const sourceSHA = spec.sha256;
const testedHashes = new Map([bundlePath, corpusPath, enginePath].map(path => [path, digest(path)]));
const bundle = JSON.parse(readFileSync(bundlePath, 'utf8'));
const corpusData = JSON.parse(readFileSync(corpusPath, 'utf8'));
const records = Array.isArray(corpusData) ? corpusData : corpusData.records;
const engine = createEngine(bundle, lunr);
const counts = {};
const failures = [];
let assertionCount = 0;
let failedAssertionCount = 0;
const examples = [];

function check(category, actual, expected, context = {}) {
  assertionCount++;
  counts[category] = (counts[category] || 0) + 1;
  try { assert.deepEqual(actual, expected); }
  catch {
    failedAssertionCount++;
    if (failures.length < 50) failures.push({ category, context, actual, expected });
  }
}

check('protectedSourceHash', digest(sourcePath), sourceSHA);
check('protectedReaderHash', digest(readerPath), readerSHA);
check('bundleRecords', bundle.records, records.map(r => ({...r, breakBefore: r.breakBefore ?? false})));
check('sectionCoverage', records.map(r => r.section), Array.from({length: spec.sections}, (_, i) => i + 1));
check('uniqueRecordIds', new Set(records.map(r => r.id)).size, spec.sections);

// Independent event scanner for this SHA-pinned, deliberately limited source.
// Only div1/div2/p/milestone tags occur in the body. Unknown tags and entities
// stop verification rather than being guessed or silently flattened. This is
// separate from extract.py's XML parser and never reads its extraction report.
const entityNames = {amp: '&', lt: '<', gt: '>', apos: "'", quot: '"'};
function decodeXml(text) {
  return text.replace(/&([^;]+);/g, (_, entity) => {
    if (entity in entityNames) return entityNames[entity];
    if (/^#x[0-9a-f]+$/i.test(entity)) return String.fromCodePoint(parseInt(entity.slice(2), 16));
    if (/^#[0-9]+$/.test(entity)) return String.fromCodePoint(Number(entity.slice(1)));
    throw new Error(`Unsupported XML entity in independent oracle: ${entity}`);
  });
}
const rawXml = readFileSync(sourcePath, 'utf8');
const body = rawXml.match(/<body>([\s\S]*?)<\/body>/)?.[1];
assert.ok(body, 'The frozen XML must contain exactly identifiable body tags.');
const xmlOracle = [];
let oracleChapter = null, oracleSource = null, oracleParagraphNumber = null, oracleCurrent = null;
let oracleBuffer = '', oracleFirstFragment = false;
let citationParagraphs = 0, continuationParagraphs = 0, internalMilestones = 0;
const continuationIds = new Set(['latin-bellum3-num3', 'latin-bellum6-num427']);
function startOracleSection(number) {
  oracleCurrent = {section: number, chapter: oracleChapter, sourceId: oracleSource, text: ''};
  xmlOracle.push(oracleCurrent);
}
function flushOracle() {
  if (!oracleSource) return;
  let text = decodeXml(oracleBuffer);
  if (oracleFirstFragment) {
    const label = text.match(/^\s*\[(\d+)\]\s*/);
    if (label) {
      assert.equal(Number(label[1]), oracleParagraphNumber, 'A printed Niese label must agree with its paragraph ID.');
      startOracleSection(Number(label[1]));
      citationParagraphs++;
      text = text.slice(label[0].length);
    } else {
      assert.ok(continuationIds.has(oracleSource) && oracleCurrent,
        `Unreviewed paragraph without a Niese label: ${oracleSource}`);
      continuationParagraphs++;
    }
    text = text.replace(/^(?:CAP\.\s*[IVXLCDM]+\.\s*|\d+\.\s*)/, '');
  }
  text = text.trim();
  if (text) {
    assert.ok(oracleCurrent, 'Running text needs an explicit preceding Niese anchor.');
    oracleCurrent.text += (oracleCurrent.text ? '\n\n' : '') + text;
  }
  oracleBuffer = ''; oracleFirstFragment = false;
}
for (const match of body.matchAll(/<[^>]+>|[^<]+/g)) {
  const chunk = match[0];
  if (!chunk.startsWith('<')) { if (oracleSource) oracleBuffer += chunk; continue; }
  const name = chunk.match(/^<\/?([A-Za-z0-9]+)/)?.[1];
  assert.ok(['div1','div2','p','milestone'].includes(name), `Unsupported body tag: ${chunk}`);
  const closing = chunk.startsWith('</');
  const attributes = Object.fromEntries([...chunk.matchAll(/([A-Za-z_:][\w.:-]*)\s*=\s*(["'])(.*?)\2/g)]
    .map(a => [a[1], decodeXml(a[3])]));
  if (name === 'div2' && !closing) oracleChapter = Number(attributes.n);
  if (name === 'p' && !closing) {
    const id = attributes['xml:id'] || '';
    const number = id.match(new RegExp(`^latin-bellum${bookNumber}-num(\\d+)$`));
    oracleSource = number ? id : null;
    oracleParagraphNumber = number ? Number(number[1]) : null;
    oracleBuffer = ''; oracleFirstFragment = Boolean(number);
  } else if (name === 'milestone' && !closing) {
    assert.ok(oracleSource && attributes.unit === 'niese' && /^\d+$/.test(attributes.n));
    flushOracle(); startOracleSection(Number(attributes.n)); internalMilestones++;
  } else if (name === 'p' && closing) {
    flushOracle(); oracleSource = null; oracleParagraphNumber = null;
  }
}

check('independentXmlSections', xmlOracle.length, spec.sections);
for (let i = 0; i < records.length; i++) {
  const record = records[i];
  const expected = xmlOracle[i];
  check('independentXmlTexts', {section: record.section, chapter: record.chapter,
    sourceId: record.sourceId, text: record.text}, expected, {section: record.section});
  check('workAndBook', [record.work, record.book, record.language, record.edition],
    ['bellum', bookNumber, 'Latin', 'Cardwell (1837)'], {section: record.section});
  const url = new URL(record.url, 'https://latinjosephus.example');
  check('deepLinkParameters', {
    pathname: url.pathname, book: url.searchParams.get('book'),
    niese: url.searchParams.get('niese'), fragment: url.hash,
    extraneous: [...url.searchParams.keys()].filter(x => !['book', 'niese', 'latin'].includes(x)),
    source: url.searchParams.get('latin') || 'cardwell',
  }, {pathname: '/bellum-judaicum/', book: String(bookNumber), niese: String(i + 1),
    fragment: '', extraneous: [], source: 'cardwell'}, {section: record.section});
}

// Character-by-character token recognition is independent of engine regexes.
// JS offsets deliberately count UTF-16 code units, as DOM text ranges do.
const isTokenChar = c => /[\p{L}\p{M}\p{N}]/u.test(c);
function tokenize(text, record, recordIndex) {
  const result = [];
  let position = 0, start = -1, tokenText = '';
  const emit = () => {
    if (start >= 0) result.push({term: tokenText.normalize('NFC').toLowerCase(),
      start, end: position, recordId: record.id, section: record.section, recordIndex});
    start = -1; tokenText = '';
  };
  for (const character of text) {
    if (isTokenChar(character)) {
      if (start < 0) start = position;
      tokenText += character;
    } else emit();
    position += character.length;
  }
  emit();
  return result;
}
const tokenLists = records.map((r, i) => tokenize(r.text, r, i));
const allTokens = tokenLists.flat();
const vocabulary = [...new Set(allTokens.map(t => t.term))].sort();
const normalize = (s, fold) => {
  s = s.normalize('NFC').toLowerCase();
  return fold ? s.replaceAll('v', 'u').replaceAll('j', 'i') : s;
};
const postings = new Map([false, true].map(fold => {
  const table = new Map();
  for (const token of allTokens) {
    const term = normalize(token.term, fold);
    if (!table.has(term)) table.set(term, []);
    table.get(term).push(token);
  }
  return [fold, table];
}));
const recordIndexById = new Map(records.map((r, i) => [r.id, i]));
const canonicalSpans = spans => JSON.stringify(spans.map(s => [s.recordId, s.start, s.end]));
const spanForToken = t => ({recordId: t.recordId, start: t.start, end: t.end});

// A greedy glob machine, independent of the engine's wildcard implementation.
function wildcardMatch(pattern, text) {
  const p = [...pattern], t = [...text];
  let pi = 0, ti = 0, star = -1, backtrack = -1;
  while (ti < t.length) {
    if (pi < p.length && p[pi] === t[ti]) { pi++; ti++; }
    else if (p[pi] === '*') { star = pi++; backtrack = ti; }
    else if (star >= 0) { pi = star + 1; ti = ++backtrack; }
    else return false;
  }
  while (p[pi] === '*') pi++;
  return pi === p.length;
}
const term = value => ({type: 'leaf', patterns: [value], phrase: false});
const phrase = values => ({type: 'leaf', patterns: values, phrase: true});
const and = (a, b) => ({type: 'and', a, b});
const or = (a, b) => ({type: 'or', a, b});
const not = a => ({type: 'not', a});
function printAst(ast) {
  if (ast.type === 'leaf') return ast.phrase ? `"${ast.patterns.join(' ')}"` : ast.patterns[0];
  if (ast.type === 'not') return `NOT (${printAst(ast.a)})`;
  return `(${printAst(ast.a)} ${ast.type.toUpperCase()} ${printAst(ast.b)})`;
}
function addHit(map, unit, spans) {
  if (!map.has(unit)) map.set(unit, new Set());
  map.get(unit).add(canonicalSpans(spans));
}
function leafMatches(ast, scope, fold) {
  const result = new Map();
  const patterns = ast.patterns.map(p => normalize(p, fold));
  if (!ast.phrase) {
    const table = postings.get(fold), pattern = patterns[0];
    const matchingWords = pattern.includes('*')
      ? [...table.keys()].filter(word => wildcardMatch(pattern, word))
      : table.has(pattern) ? [pattern] : [];
    for (const word of matchingWords) for (const token of table.get(word))
      addHit(result, scope === 'book' ? 0 : token.recordIndex, [spanForToken(token)]);
    return result;
  }
  for (let start = 0; start <= allTokens.length - patterns.length; start++) {
    let found = true;
    for (let offset = 0; offset < patterns.length; offset++) {
      const token = allTokens[start + offset];
      if ((scope === 'section' && token.recordIndex !== allTokens[start].recordIndex)
        || (offset && token.recordIndex !== allTokens[start + offset - 1].recordIndex
          && records[token.recordIndex].breakBefore)
        || !wildcardMatch(patterns[offset], normalize(token.term, fold))) {
        found = false; break;
      }
    }
    if (!found) continue;
    const spans = [];
    for (let offset = 0; offset < patterns.length; offset++) {
      const token = allTokens[start + offset];
      if (spans.at(-1)?.recordId === token.recordId) spans.at(-1).end = token.end;
      else spans.push(spanForToken(token));
    }
    addHit(result, scope === 'book' ? 0 : allTokens[start].recordIndex, spans);
  }
  return result;
}
function evaluate(ast, scope, fold, negated = false) {
  if (ast.type === 'not') return evaluate(ast.a, scope, fold, !negated);
  if (ast.type === 'leaf') {
    const matches = leafMatches(ast, scope, fold);
    if (!negated) return matches;
    const inverse = new Map();
    for (let unit = 0; unit < (scope === 'book' ? 1 : records.length); unit++)
      if (!matches.has(unit)) inverse.set(unit, new Set());
    return inverse;
  }
  const left = evaluate(ast.a, scope, fold, negated);
  const right = evaluate(ast.b, scope, fold, negated);
  const op = negated ? (ast.type === 'and' ? 'or' : 'and') : ast.type;
  const result = new Map();
  for (const unit of new Set([...left.keys(), ...right.keys()])) {
    if (op === 'and' && !(left.has(unit) && right.has(unit))) continue;
    result.set(unit, new Set([...(left.get(unit) || []), ...(right.get(unit) || [])]));
  }
  return result;
}

function verifyQuery(query, ast, options, category, recordExample = false) {
  counts[`${category}Queries`] = (counts[`${category}Queries`] || 0) + 1;
  const expected = evaluate(ast, options.scope, options.fold);
  let actual;
  try { actual = engine.search(query, options); }
  catch (error) {
    check(`${category}SearchError`, String(error), null, {query, ...options});
    return;
  }
  const context = {query, ...options};
  check(`${category}MatchedUnits`, actual.matchingUnits, expected.size, context);
  const expectedOccurrences = [...expected.values()].reduce((n, hits) => n + hits.size, 0);
  check(`${category}Occurrences`, actual.occurrences, expectedOccurrences, context);
  const expectedRecordIndices = options.scope === 'section' ? [...expected.keys()] :
    [...new Set([...expected.values()].flatMap(hits => [...hits].flatMap(h =>
      JSON.parse(h).map(span => recordIndexById.get(span[0])))))];
  expectedRecordIndices.sort((a, b) => a - b);
  check(`${category}MatchedSections`, actual.matchingSections, expectedRecordIndices.length, context);
  const actualGroups = new Map(actual.hitGroups.map(group => [
    options.scope === 'book' ? 0 : recordIndexById.get(group.recordIds[0]), group]));
  check(`${category}ResultUnits`, [...actualGroups.keys()].sort((a, b) => a - b),
    [...expected.keys()].sort((a, b) => a - b), context);
  for (const [unit, hits] of expected) {
    const group = actualGroups.get(unit);
    if (!group) continue;
    check(`${category}EvidenceSpans`, [...new Set(group.hits.map(h => canonicalSpans(h.spans)))].sort(),
      [...hits].sort(), {...context, unit});
    const expectedIndices = options.scope === 'section' ? [unit] :
      [...new Set([...hits].flatMap(h => JSON.parse(h).map(span => recordIndexById.get(span[0]))))]
        .sort((a, b) => a - b);
    check(`${category}GroupSections`, group.sections, expectedIndices.map(i => records[i].section),
      {...context, unit});
    check(`${category}GroupRecordIds`, group.recordIds, expectedIndices.map(i => records[i].id),
      {...context, unit});
  }
  if (recordExample) examples.push({query, ...options,
    expectedSections: expectedRecordIndices.map(i => records[i].section),
    actualMatchingUnits: actual.matchingUnits, actualMatchingSections: actual.matchingSections,
    actualOccurrences: actual.occurrences,
  });
}

// Exhaustive literal postings checks catch removed stopwords, stemming,
// normalization discrepancies, and token loss. Each distinct source form is run
// in both explicit spelling modes against independently built postings.
for (const fold of [false, true]) for (const word of vocabulary)
  verifyQuery(word, term(word), {scope: 'section', fold}, 'literal');

const fixtures = [
  ['"At Theodorus repente"', phrase(['At','Theodorus','repente'])],
  ['"sacerdos ex Hierosolymis"', phrase(['sacerdos','ex','Hierosolymis'])],
  ['"regis aufert Judaeorumque"', phrase(['regis','aufert','Judaeorumque'])],
  ['(Theodor* OR Zenon*) AND (Alexander OR Herod*)',
    and(or(term('Theodor*'), term('Zenon*')), or(term('Alexander'), term('Herod*')))],
  ['Theodor* AND NOT Alexander', and(term('Theodor*'), not(term('Alexander')))],
  ['"nisi quod" AND bell*', and(phrase(['nisi','quod']), term('bell*'))],
  ['"habebantur At Theodorus"', phrase(['habebantur','At','Theodorus'])],
  ['"6 me miserum"', phrase(['6','me','miserum'])],
  ['"nisi qu*"', phrase(['nisi','qu*'])],
  ['Iudae*', term('Iudae*')],
  ['Theodor* Alexander OR Zenon*', or(and(term('Theodor*'), term('Alexander')), term('Zenon*'))],
  ['Theodor* OR Zenon* AND Alexander', or(term('Theodor*'), and(term('Zenon*'), term('Alexander')))],
  ['NOT (Theodor* OR NOT Alexander)', not(or(term('Theodor*'), not(term('Alexander'))))],
  ['NOT NOT Theodor*', not(not(term('Theodor*')))],
  ['(Theodor* AND zzzznonoccurrit) OR Zenon*',
    or(and(term('Theodor*'), term('zzzznonoccurrit')), term('Zenon*'))],
  ['NOT zzzznonoccurrit', not(term('zzzznonoccurrit'))],
  ['NOT *', not(term('*'))],
  ['rex OR rex*', or(term('rex'), term('rex*'))],
];
const laterExamples = {
  2: [['animas','autem','immortales'], ['tria','sunt','apud','Judaeos','genera','philosophiae']],
  3: [['incognitam','Britanniam']],
  4: [['sine','ullo','discrimine','cum','nocentibus']],
  5: [['Graecis','aliae','Latinis','literis']],
  6: [['Maria','nomine','Eleazari','filia'], ['venissent','Magna','vero'], ['Magna','vero','haec','multitudo']],
  7: [['neque','cuiquam','alii','servire','nisi','Deo'], ['facinus','invitabat','Cum','olim']],
};
for (const words of laterExamples[bookNumber] || []) {
  const ast = phrase(words); fixtures.push([printAst(ast), ast]);
}
for (const [query, ast] of fixtures) for (const fold of [false, true]) for (const scope of ['section','book'])
  verifyQuery(query, ast, {scope, fold}, 'fixture', ast.type === 'leaf' && ast.phrase);

// Check a real four-token phrase crossing every consecutive Niese boundary.
// Every phrase must have a book occurrence; section results are computed without
// assuming that an identical phrase cannot also occur elsewhere in the book.
for (let boundary = 1; boundary < records.length; boundary++) {
  const tokens = [...tokenLists[boundary - 1].slice(-2), ...tokenLists[boundary].slice(0, 2)];
  const ast = phrase(tokens.map(t => t.term));
  for (const scope of ['section','book'])
    verifyQuery(printAst(ast), ast, {scope, fold: false}, 'boundaryPhrase');
}

let randomState = 0x15441837;
function randomInt(limit) {
  randomState ^= randomState << 13;
  randomState ^= randomState >>> 17;
  randomState ^= randomState << 5;
  return (randomState >>> 0) % limit;
}
function randomLeaf() {
  if (randomInt(3) === 0) {
    const tokens = tokenLists[randomInt(tokenLists.length)];
    const length = Math.min(tokens.length, 2 + randomInt(4));
    const start = randomInt(tokens.length - length + 1);
    const words = tokens.slice(start, start + length).map(t => t.term);
    if (randomInt(3) === 0) words[randomInt(words.length)] = '*';
    return phrase(words);
  }
  let word = vocabulary[randomInt(vocabulary.length)];
  if (randomInt(3) === 0) word = word.slice(0, Math.max(1, Math.floor(word.length / 2))) + '*';
  if (randomInt(9) === 0) word = 'zzzznonoccurrit';
  return term(word);
}
function randomAst(depth = 0) {
  if (depth >= 2 || randomInt(3) === 0) return randomLeaf();
  if (randomInt(4) === 0) return not(randomAst(depth + 1));
  return (randomInt(2) ? and : or)(randomAst(depth + 1), randomAst(depth + 1));
}
for (let i = 0; i < 80; i++) {
  const ast = randomAst();
  for (const fold of [false, true]) for (const scope of ['section','book'])
    verifyQuery(printAst(ast), ast, {scope, fold}, 'randomBooleanPhrase');
}
for (let i = 0; i < 48; i++) {
  const word = vocabulary[randomInt(vocabulary.length)];
  const cut = Math.max(1, Math.floor(word.length / 2));
  const patterns = [word.slice(0, cut) + '*', '*' + word.slice(cut),
    '*' + word.slice(0, cut) + '*', word.slice(0, 1) + '*' + word.slice(-1)];
  const ast = term(patterns[i % patterns.length]);
  for (const fold of [false, true]) for (const scope of ['section','book'])
    verifyQuery(printAst(ast), ast, {scope, fold}, 'randomWildcard');
}

// Repeat the protected-content checks after loading/build-independent searches.
check('protectedSourceHash', digest(sourcePath), sourceSHA);
check('protectedReaderHash', digest(readerPath), readerSHA);
for (const [path, hash] of testedHashes)
  check('testedFileUnchangedDuringQa', digest(path), hash, {path: reportPath(path)});
const report = {
  book: bookNumber,
  status: failedAssertionCount ? 'FAIL' : 'PASS',
  generatedAt: new Date().toISOString(),
  independentVerifier: 'bin/search/tests/corpus-qa.mjs',
  source: {book: bookNumber, path: reportPath(sourcePath), sha256: digest(sourcePath),
    sections: records.length, numberedParagraphs: citationParagraphs + continuationParagraphs,
    citationParagraphs, continuationParagraphs, internalMilestones,
    tokens: allTokens.length, literalVocabulary: vocabulary.length,
    foldedVocabulary: postings.get(true).size},
  verifiedFiles: {bundle: {path: reportPath(bundlePath), sha256: digest(bundlePath)},
    corpus: {path: reportPath(corpusPath), sha256: digest(corpusPath)},
    engine: {path: reportPath(enginePath), sha256: digest(enginePath)},
    verifier: {path: reportPath(fileURLToPath(import.meta.url)), sha256: digest(fileURLToPath(import.meta.url))},
    originalReader: {path: reportPath(readerPath), sha256: digest(readerPath)}},
  method: {
    text: 'Independent strict raw-XML event scanner with entity decoding; exact per-section text comparison.',
    tokens: 'Character-by-character Unicode letter/mark/number tokenization, independent postings.',
    wildcards: 'Independent greedy glob matcher; asterisk consumes zero or more token characters.',
    boolean: 'Generated abstract syntax trees evaluated with independent sets and De Morgan negation.',
    phrases: 'Independent adjacency scan; punctuation ignored; every Niese boundary checked in both scopes.',
    seed: '0x15441837',
  },
  counts, examples,
  withinBookSeams: records.length - 1,
  assertions: assertionCount,
  failedAssertions: failedAssertionCount,
  durationSeconds: Math.round((performance.now() - started) / 10) / 100,
  limitations: [
    'Automated Node/corpus QA, not browser or visual interaction testing.',
    `Deep links verified for all ${records.length} query parameter sets and original reader syntax; destination pages not opened by this verifier.`,
    'Confirms search/extraction against the supplied XML; does not correct or re-certify Cardwell transcription against printed pages.',
    `This per-book report covers Cardwell Latin Bellum Book ${bookNumber}.`,
  ],
  failures,
};
console.log(JSON.stringify({book: bookNumber, status: report.status, sections: records.length,
  queries: Object.entries(counts).filter(([k]) => k.endsWith('Queries')).reduce((n,[,v]) => n + v, 0),
  failedAssertions: failedAssertionCount, durationSeconds: report.durationSeconds}));
return {report, records, tokenLists, allTokens, vocabulary, evaluate,
  term, phrase, and, or, not, printAst, canonicalSpans, recordIndexById};
}

const states = sourceSpecs.map(runBook);
const catalog = JSON.parse(readFileSync(catalogPath, 'utf8'));
const combinedCorpus = JSON.parse(readFileSync(combinedCorpusPath, 'utf8'));
const collectionCounts = {}, collectionFailures = [], collectionExamples = [];
let collectionAssertions = 0, collectionFailedAssertions = 0;
function collectionCheck(category, actual, expected, context = {}) {
  collectionAssertions++;
  collectionCounts[category] = (collectionCounts[category] || 0) + 1;
  try { assert.deepEqual(actual, expected); }
  catch {
    collectionFailedAssertions++;
    if (collectionFailures.length < 50) collectionFailures.push({category, context, actual, expected});
  }
}
collectionCheck('combinedCorpusTexts', combinedCorpus, states.flatMap(s => s.records));
collectionCheck('combinedGlobalOrder', combinedCorpus.map(r => r.order),
  Array.from({length:4001}, (_, i) => i));
collectionCheck('combinedUniqueIds', new Set(combinedCorpus.map(r => r.id)).size, 4001);
collectionCheck('catalogSchemaVersion',catalog.schemaVersion,2);
const ownCollections = catalog.collections.filter(c => c.id === collectionId);
const ownBooks = catalog.books.filter(b => b.collectionId === collectionId);
collectionCheck('catalogContainsSingleBellumCollection', ownCollections.length, 1);
collectionCheck('catalogCollectionIdentity',ownCollections.map(c=>({id:c.id,work:c.work,
  language:c.language,edition:c.edition,readerPath:c.readerPath,books:c.books})),
  [{id:collectionId,work:'bellum',language:'Latin',edition:'Cardwell (1837)',
    readerPath:'bellum-judaicum/',books:sourceSpecs.map(s=>bookId(s.book))}]);
collectionCheck('catalogCombinedCorpusHash',ownCollections[0].corpusSHA256,digest(combinedCorpusPath));
collectionCheck('catalogBooks', ownBooks.map(b => b.number), [1,2,3,4,5,6,7]);
for (const book of ownBooks) {
  const state = states[book.number - 1];
  collectionCheck('catalogQualifiedBookIdentity',{id:book.id,collectionId:book.collectionId},
    {id:bookId(book.number),collectionId},{book:book.number});
  collectionCheck('catalogSectionCounts', book.sections, state.records.length, {book: book.number});
  collectionCheck('catalogTokenCounts', book.tokens, state.allTokens.length, {book: book.number});
  collectionCheck('catalogBundleHash', book.sha256, state.report.verifiedFiles.bundle.sha256, {book: book.number});
  collectionCheck('catalogCorpusHash', book.corpusSHA256, state.report.verifiedFiles.corpus.sha256, {book: book.number});
}
const fetchCounts = new Map();
async function readBundleResponse(url) {
  const parsed = new URL(url);
  const match = parsed.pathname.match(/\/assets\/search\/data\/bellum-latin-cardwell\/book-(0[1-7])\.bundle\.json$/);
  if (!match) return new Response('Unknown QA resource', {status:404});
  const number = Number(match[1]);
  fetchCounts.set(number, (fetchCounts.get(number) || 0) + 1);
  return new Response(readFileSync(resolve(pilotDir, `data/${collectionId}/book-${match[1]}.bundle.json`)),
    {status:200, headers:{'Content-Type':'application/json'}});
}
const collection = createCollection(catalog, lunr, {
  baseURL:'https://qa.example/assets/search/', fetchImpl: readBundleResponse,
});
const {term,phrase,and,or,not,printAst,canonicalSpans} = states[0];
function collectionExpectation(ast, options) {
  const groups = [];
  let matchingUnits = 0, matchingSections = 0, occurrences = 0;
  for (const state of states.filter(s => options.books.includes(s.report.book))) {
    const matches = state.evaluate(ast, options.scope, options.fold);
    matchingUnits += matches.size;
    for (const [unit, hits] of [...matches].sort((a,b) => a[0] - b[0])) {
      occurrences += hits.size;
      const indices = options.scope === 'section' ? [unit] :
        [...new Set([...hits].flatMap(h => JSON.parse(h).map(span => state.recordIndexById.get(span[0]))))]
          .sort((a,b) => a-b);
      matchingSections += indices.length;
      groups.push({
        unitId: `${bookId(state.report.book)}:${options.scope === 'section' ? state.records[unit].id :
          `book:bellum:${state.report.book}:Latin:Cardwell%20(1837)`}`,
        recordIds: indices.map(i => state.records[i].id),
        sections: indices.map(i => state.records[i].section),
        evidence: [...hits].sort(),
      });
    }
  }
  return {matchingUnits, matchingSections, occurrences, groups};
}
async function verifyCollection(query, ast, options, category = 'selectedCollection', capture = false) {
  collectionCounts[`${category}Queries`] = (collectionCounts[`${category}Queries`] || 0) + 1;
  const expected = collectionExpectation(ast, options);
  let actual;
  try { actual = await collection.search(query, {...options,
    collections:[collectionId],books:options.books.map(bookId)}); }
  catch (error) { collectionCheck(`${category}Error`, error.message, null, {query,...options}); return; }
  const context = {query,...options};
  collectionCheck(`${category}Units`, actual.matchingUnits, expected.matchingUnits, context);
  collectionCheck(`${category}Sections`, actual.matchingSections, expected.matchingSections, context);
  collectionCheck(`${category}Occurrences`, actual.occurrences, expected.occurrences, context);
  collectionCheck(`${category}Books`, actual.selectedBooks, [...options.books].sort((a,b) => a-b).map(bookId), context);
  collectionCheck(`${category}Collections`,actual.selectedCollections,[collectionId],context);
  collectionCheck(`${category}MatchingCollections`,actual.matchingCollections,
    expected.matchingUnits?[collectionId]:[],context);
  collectionCheck(`${category}MatchingBooks`,actual.matchingBooks,
    [...new Set(expected.groups.map(g=>bookId(Number(g.unitId.split(':')[1]))))],context);
  collectionCheck(`${category}Groups`, actual.hitGroups.map(g => ({unitId:g.unitId,
    recordIds:g.recordIds, sections:g.sections,
    evidence:[...new Set(g.hits.map(h => canonicalSpans(h.spans)))].sort()})), expected.groups, context);
  collectionCheck(`${category}SelectedRecordIds`, actual.records.map(r => r.id),
    states.filter(s => options.books.includes(s.report.book)).flatMap(s => s.records.map(r => r.id)), context);
  collectionCheck(`${category}QualifiedGroupIdentities`,actual.hitGroups.map(g=>({bookId:g.bookId,
    collectionId:g.collectionId,book:g.book})),expected.groups.map(g=>{
      const book=Number(g.unitId.split(':')[1]);
      return {bookId:bookId(book),collectionId,book};
    }),context);
  if (capture) collectionExamples.push({query,...options, matchingUnits:actual.matchingUnits,
    matchingSections:actual.matchingSections, occurrences:actual.occurrences,
    citations:actual.hitGroups.flatMap(g => g.recordIds).map(id => {
      const r=combinedCorpus.find(r => r.id===id); return `${r.book}.${r.section}`;
    })});
}

const collectionFixtures = [
  ['"animas autem immortales"', phrase(['animas','autem','immortales'])],
  ['"incognitam Britanniam"', phrase(['incognitam','Britanniam'])],
  ['"Graecis aliae Latinis literis"', phrase(['Graecis','aliae','Latinis','literis'])],
  ['"Maria nomine Eleazari filia"', phrase(['Maria','nomine','Eleazari','filia'])],
  ['"neque cuiquam alii servire nisi Deo"', phrase(['neque','cuiquam','alii','servire','nisi','Deo'])],
  ['"venissent Magna vero"', phrase(['venissent','Magna','vero'])],
  ['"Magna vero haec multitudo"',phrase(['Magna','vero','haec','multitudo'])],
  ['"facinus invitabat Cum olim"',phrase(['facinus','invitabat','Cum','olim'])],
  ['(Roman* OR Graec*) AND Iudae*', and(or(term('Roman*'),term('Graec*')),term('Iudae*'))],
  ['NOT (Theodor* OR NOT Alexander)', not(or(term('Theodor*'),not(term('Alexander'))))],
  ['NOT zzzznonoccurrit', not(term('zzzznonoccurrit'))],
];
for (const books of [[1],[2,3],[7,1,3],[2,5,7],[1,2,3,4,5,6,7]])
  for (const [query,ast] of collectionFixtures) for (const scope of ['section','book'])
    for (const fold of [false,true])
      await verifyCollection(query,ast,{books,scope,fold},'selectedCollection',
        books.length===7 && !fold && ast.type==='leaf');

// Explicitly prohibit phrases and Boolean AND from joining two different books.
for (let seam=0; seam<states.length-1; seam++) {
  const left=states[seam],right=states[seam+1],books=[left.report.book,right.report.book];
  const words=[...left.allTokens.slice(-2),...right.allTokens.slice(0,2)].map(t=>t.term);
  const ast=phrase(words),query=printAst(ast);
  for (const scope of ['section','book']) for (const fold of [false,true]) {
    const expected=collectionExpectation(ast,{books,scope,fold});
    collectionCheck('crossBookPhraseFixtureIsAbsent',expected.matchingUnits,0,{books,query,scope,fold});
    await verifyCollection(query,ast,{books,scope,fold},'crossBookPhrase');
  }
  const leftWord=left.vocabulary.find(w=>w.length>3&&!right.vocabulary.includes(w));
  const rightWord=right.vocabulary.find(w=>w.length>3&&!left.vocabulary.includes(w));
  assert.ok(leftWord&&rightWord,'Adjacent books need exclusive words for the Boolean isolation fixture.');
  const isolated=and(term(leftWord),term(rightWord));
  for (const scope of ['section','book']) {
    const expected=collectionExpectation(isolated,{books,scope,fold:false});
    collectionCheck('crossBookBooleanFixtureIsAbsent',expected.matchingUnits,0,{books,leftWord,rightWord,scope});
    await verifyCollection(printAst(isolated),isolated,{books,scope,fold:false},'crossBookBoolean');
  }
}
collectionCheck('eachSelectedBundleFetchedOnce',[...fetchCounts.entries()].sort((a,b)=>a[0]-b[0]),
  sourceSpecs.map(s=>[s.book,1]));
const missingBookCollection=createCollection(catalog,lunr,{
  baseURL:'https://qa.example/assets/search/',fetchImpl:async url=>
    new URL(url).pathname.endsWith('/book-06.bundle.json')
      ?new Response('Unavailable',{status:404}):readBundleResponse(url),
});
let missingSelectedRejected=false;
try {await missingBookCollection.search('bell*',{collections:[collectionId],books:[bookId(1),bookId(6)],scope:'section',fold:false});}
catch {missingSelectedRejected=true;}
collectionCheck('missingSelectedBookRejectsWholeSearch',missingSelectedRejected,true);
for(const selection of [{books:[1]},{collections:['antiquities-latin'],books:'all'}]) {
  let rejected=false;
  try {await collection.search('bell*',{...selection,scope:'section',fold:false});}
  catch {rejected=true;}
  collectionCheck('unqualifiedOrUnavailableSelectionRejected',rejected,true,{selection});
}

for (const [path,hash] of suiteFileHashes)
  collectionCheck('suiteFileUnchangedDuringQa',digest(path),hash,{path:reportPath(path)});
const allCounts={};
for (const part of [...states.map(s=>s.report.counts),collectionCounts])
  for (const [key,value] of Object.entries(part)) allCounts[key]=(allCounts[key]||0)+value;
const failedAssertions=states.reduce((n,s)=>n+s.report.failedAssertions,collectionFailedAssertions);
const fileEvidence=path=>({path:reportPath(path),sha256:digest(path)});
const sourceSum=key=>states.reduce((n,s)=>n+s.report.source[key],0);
const report={
  status:failedAssertions?'FAIL':'PASS',generatedAt:new Date().toISOString(),
  independentVerifier:'bin/search/tests/corpus-qa.mjs',
  readerBaseline,
  source:{books:7,sections:sourceSum('sections'),numberedParagraphs:sourceSum('numberedParagraphs'),
    citationParagraphs:sourceSum('citationParagraphs'),continuationParagraphs:sourceSum('continuationParagraphs'),
    internalMilestones:sourceSum('internalMilestones'),tokens:sourceSum('tokens'),
    uniqueLiteralVocabulary:new Set(states.flatMap(s=>s.vocabulary)).size},
  sources:states.map(s=>s.report.source),
  verifiedFiles:{corpus:fileEvidence(combinedCorpusPath),catalog:fileEvidence(catalogPath),
    engine:fileEvidence(enginePath),collection:fileEvidence(collectionPath),
    verifier:fileEvidence(fileURLToPath(import.meta.url)),originalReader:fileEvidence(readerPath),
    books:states.map(s=>({book:s.report.book,bundle:s.report.verifiedFiles.bundle,
      corpus:s.report.verifiedFiles.corpus,source:{path:s.report.source.path,sha256:s.report.source.sha256}}))},
  books:states.map(s=>s.report),
  method:{...states[0].report.method,
    collection:'Selected-book aggregation compared with independent per-book oracle; local injected fetch exercises actual checksum validation and caching.',
    isolation:'All six book junctions tested for no phrase join; exclusive word pairs test no Boolean AND join between adjacent books.'},
  sourceIrregularities:[
    {book:3,section:3,sourceId:'latin-bellum3-num3',handling:'Printed subchapter label only before milestone 4; creates no duplicate section 3.'},
    {book:6,section:427,sourceId:'latin-bellum6-num427',handling:'Running-text continuation joins existing section 427 from paragraph 420 with a paragraph separator; creates no duplicate section 427.'},
  ],
  counts:allCounts,totalQueries:Object.entries(allCounts).filter(([k])=>k.endsWith('Queries')).reduce((n,[,v])=>n+v,0),
  withinBookSeams:states.reduce((n,s)=>n+s.report.withinBookSeams,0),
  crossBookSeams:6,collectionExamples,
  assertions:states.reduce((n,s)=>n+s.report.assertions,collectionAssertions),failedAssertions,
  durationSeconds:Math.round((performance.now()-suiteStarted)/10)/100,
  limitations:[
    'Automated Node/corpus QA, not browser or visual interaction testing.',
    'All 4,001 reader link parameter sets verified; destination pages not opened by this verifier.',
    'Checks source fidelity to the seven supplied XML files; does not re-certify their transcription against printed pages.',
    'Coverage is Cardwell Latin Bellum I-VII only.',
  ],
  failures:[...states.flatMap(s=>s.report.failures.map(f=>({book:s.report.book,...f}))),...collectionFailures],
};
writeFileSync(resolve(pilotDir,'qa-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,books:7,sections:report.source.sections,
  totalQueries:report.totalQueries,withinBookSeams:report.withinBookSeams,
  assertions:report.assertions,failedAssertions,durationSeconds:report.durationSeconds,
  failures:report.failures.slice(0,8).map(f=>({book:f.book,category:f.category,context:f.context}))},null,2));
if(failedAssertions)process.exitCode=1;
