/** Independent acceptance for Whiston Antiquities Proem and Books I-X.
 * Expected source text and tokens come from the separately fingerprinted
 * minidom witness, never from the production extractor or engine. Query
 * expectations use explicit trees, a sequential phrase scan, and a small
 * independent wildcard matcher. XI is exercised only in memory.
 */
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync, mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {dirname, relative, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {performance} from 'node:perf_hooks';

let root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
let smoke = false, explicitReaderSHA = null;
const args = process.argv.slice(2);
const usage = 'Usage: node bin/search/tests/whiston-corpus-qa.mjs [--smoke] [--root <repository>] [--expected-reader-sha256 <SHA-256>]';
for (let index = 0; index < args.length; index++) {
  if (args[index] === '--smoke') {assert.equal(smoke, false, usage); smoke = true;}
  else if (args[index] === '--root') {assert.ok(args[index + 1], usage); root = resolve(args[++index]);}
  else if (args[index] === '--expected-reader-sha256') {
    assert.ok(explicitReaderSHA === null && /^[a-f0-9]{64}$/i.test(args[index + 1] || ''), usage);
    explicitReaderSHA = args[++index].toLowerCase();
  } else assert.fail(usage);
}
const base = resolve(root, 'bin/search');
const collectionId = 'antiquities-english-whiston';
const bookId = `${collectionId}:1`;
const expectedBooks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const expectedBookTotals = [
  {book:1,sections:346,tokens:21994}, {book:2,sections:349,tokens:23020},
  {book:3,sections:322,tokens:20955}, {book:4,sections:331,tokens:22900},
  {book:5,sections:362,tokens:23396},
  {book:6,sections:378,tokens:28422}, {book:7,sections:394,tokens:28285},
  {book:8,sections:420,tokens:29968}, {book:9,sections:291,tokens:19074},
  {book:10,sections:281,tokens:18035},
];
const acceptedPriorBookHashes = {
  1:{corpus:'5d94451f1363230e0578d995ece458dd8a4b40e56064487f1362194de21404f0',extractionReport:'5ff96ccfd1a08a6abdc3a37e6e832db53db7d9f9a7e12c6eb02bfee6130e53a9',bundle:'8957992760eaeffdd875e9d061d046ef3190401e3dafb876866dce7d0c415fe1'},
  2:{corpus:'7000e802415b3246a14e3fb9fc0c5e40490fb8fa31351c228aaf31353b7b663f',extractionReport:'3eab5244d80df012cfc7c5dec46a78be90ba3b805c759c009954eed8cb18f6ab',bundle:'1202b7653d8ca9195206e15bc950f29b049595cad789001df99aefb8daaa991c'},
  3:{corpus:'26e09b435952e06b7911a4d985b44ede81bdc291ea10d18a8218f79f340fd36b',extractionReport:'67acd98bdc96a4e357fdfac47276f375f021c5e917f2b42e5c08d151213afa6c',bundle:'1637aa21fc1237308145f03661839ac7fd1fa10b0a637e19b4cd9ab8825526fc'},
  4:{corpus:'108edd83587cf34f2a901a74ba92bd7821f0b64a7555b505a9f7f855b42d1d78',extractionReport:'e771f5e133a471447489a16f08b1d2fedab03356f6543143e9858ee637dae500',bundle:'d80b924343825fbf4af9eccd0309cb4a04eec15725ab2573b27a362d0839206b'},
  5:{corpus:'fb309ee22dc2f98b65d189679657219fc808b00e64fa5737ecb8e7044e876a80',extractionReport:'d59fe5d530f2a5ea401957dc2d1bcdf542670711b98c9d2c2b19b20e670d7d6a',bundle:'d5ede93651b7500c387f3332eb8f1ae77570e9ad9de9813548a798415cbdb6f8'},
};
const destination = resolve(base, 'data', collectionId, 'qa-report.json');
const require = createRequire(import.meta.url);
const lunr = require(resolve(base, 'vendor/lunr.cjs'));
const {createEngine, buildBundle} = await import(pathToFileURL(resolve(base, 'engine.mjs')));
const {createCollection} = await import(pathToFileURL(resolve(base, 'collection.mjs')));
const {buildConcordance, exportConcordance} = await import(pathToFileURL(resolve(base, 'concordance.mjs')));
const {readerURL} = await import(pathToFileURL(resolve(base, 'ui-utils.mjs')));
const started = performance.now();
const hash = value => createHash('sha256').update(value).digest('hex');
const digest = path => hash(readFileSync(path));
const readJSON = path => JSON.parse(readFileSync(path, 'utf8'));
const evidence = path => ({path: relative(root, path).replaceAll('\\', '/'), sha256: digest(path), bytes: readFileSync(path).length});
const counts = {}, examples = [], checkedFiles = new Map();
let assertions = 0, totalQueries = 0;
function preserve(path) {const full = resolve(path); if (!checkedFiles.has(full)) checkedFiles.set(full, digest(full)); return full;}
function check(category, actual, expected, context = {}) {
  assertions++; counts[category] = (counts[category] || 0) + 1;
  assert.deepEqual(actual, expected, `${category}: ${JSON.stringify(context)}`);
}
function noteExample(query, scope, result, purpose) {
  examples.push({query, scope, matchingUnits: result.matchingUnits, occurrences: result.occurrences, purpose});
}

const normalize = value => value.normalize('NFC').toLowerCase().replaceAll('ς', 'σ').normalize('NFC');
function independentTokens(text) {
  const output = []; let start = null, offset = 0;
  for (const char of [...text, ' ']) {
    const continues = /[\p{L}\p{M}\p{N}]/u.test(char);
    if (start !== null && !continues) {
      output.push({term: normalize(text.slice(start, offset)), start, end: offset}); start = null;
    }
    if (start === null && /[\p{L}\p{N}]/u.test(char)) start = offset;
    offset += char.length;
  }
  return output;
}
// A bounded dynamic-programming glob matcher. '*' consumes zero or more
// Unicode characters inside a token; it never supplies a word boundary.
function glob(pattern, word) {
  const letters = [...word]; let previous = Array(letters.length + 1).fill(false); previous[0] = true;
  for (const char of pattern) {
    const next = Array(letters.length + 1).fill(false);
    if (char === '*') {
      next[0] = previous[0];
      for (let i = 1; i <= letters.length; i++) next[i] = previous[i] || next[i - 1];
    } else for (let i = 1; i <= letters.length; i++) next[i] = previous[i - 1] && char === letters[i - 1];
    previous = next;
  }
  return previous[letters.length];
}
const word = pattern => ({op: 'leaf', patterns: [pattern], phrase: false});
const phrase = patterns => ({op: 'leaf', patterns, phrase: true});
const and = (left, right) => ({op: 'and', left, right});
const or = (left, right) => ({op: 'or', left, right});
const not = child => ({op: 'not', child});
function print(tree) {
  if (tree.op === 'leaf') return tree.phrase ? `"${tree.patterns.join(' ')}"` : tree.patterns[0];
  if (tree.op === 'not') return `NOT (${print(tree.child)})`;
  return `(${print(tree.left)} ${tree.op.toUpperCase()} ${print(tree.right)})`;
}
const spanKey = spans => JSON.stringify(spans.map(span => [span.recordId, span.start, span.end]));
function makeOracle(rows) {
  const byId = new Map(rows.map((row, index) => [row.id, {...row, index}]));
  const all = [], table = new Map();
  rows.forEach(row => {
    for (const token of row.tokens) {
      const expanded = {...token, recordId: row.id, book: row.book, segment: row.proem ? 'proem' : 'narrative'};
      all.push(expanded);
      if (!table.has(token.term)) table.set(token.term, []);
      table.get(token.term).push(expanded);
    }
  });
  const vocabulary = [...table.keys()].sort();
  const unit = (token, scope) => scope === 'section' ? token.recordId : `book:${token.book}`;
  const universe = scope => [...new Set(rows.map(row => scope === 'section' ? row.id : `book:${row.book}`))];
  function leaves(tree, scope) {
    const result = new Map();
    const add = (key, spans) => {if (!result.has(key)) result.set(key, new Set()); result.get(key).add(spanKey(spans));};
    const patterns = tree.patterns.map(normalize);
    if (!tree.phrase) {
      const pattern = patterns[0];
      const terms = pattern.includes('*') ? vocabulary.filter(term => glob(pattern, term)) : [pattern];
      for (const term of terms) for (const token of table.get(term) || []) add(unit(token, scope), [token]);
      return result;
    }
    const matchers = patterns.map(pattern => pattern.includes('*') ? term => glob(pattern, term) : term => term === pattern);
    for (let start = 0; start <= all.length - patterns.length; start++) {
      const first = all[start]; let accepted = true;
      for (let index = 0; index < patterns.length; index++) {
        const token = all[start + index];
        if (token.book !== first.book || token.segment !== first.segment
          || (scope === 'section' && token.recordId !== first.recordId) || !matchers[index](token.term)) {accepted = false; break;}
      }
      if (!accepted) continue;
      const spans = [];
      for (const token of all.slice(start, start + patterns.length)) {
        if (spans.at(-1)?.recordId === token.recordId) spans.at(-1).end = token.end;
        else spans.push({recordId: token.recordId, start: token.start, end: token.end});
      }
      add(unit(first, scope), spans);
    }
    return result;
  }
  function evaluate(tree, scope, negative = false) {
    if (tree.op === 'not') return evaluate(tree.child, scope, !negative);
    if (tree.op === 'leaf') {
      const found = leaves(tree, scope);
      return negative ? new Map(universe(scope).filter(key => !found.has(key)).map(key => [key, new Set()])) : found;
    }
    const left = evaluate(tree.left, scope, negative), right = evaluate(tree.right, scope, negative);
    const needsBoth = (tree.op === 'and') !== negative;
    const result = new Map();
    for (const key of new Set([...left.keys(), ...right.keys()])) {
      if (needsBoth && (!left.has(key) || !right.has(key))) continue;
      result.set(key, new Set([...(left.get(key) || []), ...(right.get(key) || [])]));
    }
    return result;
  }
  return {rows, byId, all, vocabulary, table, evaluate};
}

function compare(actual, expected, oracle, scope, category, query) {
  const context = {query, scope};
  check(`${category}Units`, actual.matchingUnits, expected.size, context);
  check(`${category}Occurrences`, actual.occurrences, [...expected.values()].reduce((sum, set) => sum + set.size, 0), context);
  const groups = new Map(actual.hitGroups.map(group => [scope === 'section' ? group.recordIds[0] : `book:${group.book ?? oracle.rows[0].book}`, group]));
  check(`${category}UnitIdentity`, [...groups.keys()].sort(), [...expected.keys()].sort(), context);
  const touched = new Set();
  for (const [key, hits] of expected) {
    const group = groups.get(key);
    check(`${category}Evidence`, group.hits.map(hit => spanKey(hit.spans)).sort(), [...hits].sort(), {...context, unit: key});
    const ids = scope === 'section' ? [key] : [...new Set([...hits].flatMap(hit => JSON.parse(hit).map(span => span[0])))].sort((a, b) => oracle.byId.get(a).index - oracle.byId.get(b).index);
    check(`${category}Records`, group.recordIds, ids, {...context, unit: key});
    ids.forEach(id => touched.add(id));
  }
  check(`${category}Sections`, actual.matchingSections, touched.size, context);
}
function verify(engine, oracle, tree, scope, category, query = print(tree), example = false) {
  totalQueries++; counts[`${category}Queries`] = (counts[`${category}Queries`] || 0) + 1;
  const result = engine.search(query, {scope, fold: false});
  compare(result, oracle.evaluate(tree, scope), oracle, scope, category, query);
  if (example) noteExample(query, scope, result, category);
  return result;
}

function inspectRecords(records, expected, category) {
  check(`${category}RecordCount`, records.length, expected.length);
  records.forEach((record, index) => {
    const row = expected[index], context = {id: row.id};
    for (const field of ['id', 'book', 'section', 'order', 'text', 'sourcePath', 'sourceId', 'sourceIds'])
      check(`${category}Source${field}`, record[field], row[field], context);
    check(`${category}Version`, [record.work, record.language, record.edition], ['antiquities', 'English', 'Whiston'], context);
    check(`${category}Citation`, record.citation, {book: ({1:'I',2:'II',3:'III',4:'IV',5:'V',6:'VI',7:'VII',8:'VIII',9:'IX',10:'X',11:'XI'})[row.book], section: row.section, ...(row.proem ? {proem:true} : {})}, context);
    check(`${category}ReaderLink`, record.readerLink, {path:'antiquities/', params:{book:row.readerBook, niese:row.section, english:'whiston'}}, context);
    const link = new URL(readerURL(record, 'https://latinjosephus.github.io/'));
    check(`${category}ReaderURL`, [link.pathname, link.searchParams.get('book'), link.searchParams.get('niese'), link.searchParams.get('english')],
      ['/antiquities/', String(row.readerBook), String(row.section), 'whiston'], context);
    check(`${category}SourceDivision`, record.division ?? null, row.proem ? 'proem' : null, context);
    check(`${category}PhraseBarrier`, Boolean(record.breakBefore), row.book === 1 && row.section === 27, context);
    for (const field of ['editorialMarks','sourceMarkup','textGaps','phraseBreaks']) check(`${category}NoInvented${field}`, record[field], [], context);
    check(`${category}IndependentTokenizers`, independentTokens(record.text), row.tokens, context);
  });
}

function inspectProjection(report, files, records, category) {
  const expectedParagraphs = files.flatMap(file => file.paragraphs);
  const expectedRows = files.flatMap(file => file.rows);
  const recordById = new Map(records.map(record => [record.id, record]));
  check(`${category}ParagraphIDs`, report.paragraphs.map(p => p.sourceId), expectedParagraphs.map(p => p.sourceId));
  report.paragraphs.forEach((paragraph, index) => {
    const expected = expectedParagraphs[index], context = {sourceId:expected.sourceId};
    check(`${category}RawParagraph`, paragraph.rawText, expected.rawText, context);
    let cursor = 0, restored = '';
    for (const piece of paragraph.sourcePieces) {
      check(`${category}SourceContinuity`, piece.sourceStart, cursor, context);
      const value = piece.kind === 'record' ? recordById.get(piece.recordId).text.slice(piece.recordStart, piece.recordEnd) : piece.text;
      check(`${category}SourceSlice`, value, expected.rawText.slice(piece.sourceStart, piece.sourceEnd), context);
      check(`${category}SourceSliceHash`, piece.textSHA256, hash(value), context);
      cursor = piece.sourceEnd; restored += value;
    }
    check(`${category}ExactRestoration`, restored, expected.rawText, context);
    check(`${category}RestorationLength`, cursor, expected.rawLength, context);
    const projected = paragraph.sourcePieces.filter(piece => piece.kind === 'record').map(piece =>
      [piece.recordId, piece.sourceStart, piece.sourceEnd, piece.recordStart, piece.recordEnd]);
    const witnessed = expectedRows.filter(row => row.sourceIds.includes(expected.sourceId)).flatMap(row => row.sourceSegments
      .filter(segment => segment.sourceId === expected.sourceId).map(segment =>
        [row.id, segment.rawStart, segment.rawEnd, segment.start, segment.end]));
    check(`${category}IndependentProjection`, projected, witnessed, context);
    const joinedRow = expectedRows.find(row => row.paragraphJoins?.some(join => join.afterSourceId === expected.sourceId));
    const join = joinedRow?.paragraphJoins.find(join => join.afterSourceId === expected.sourceId);
    check(`${category}ParagraphSections`, paragraph.sections.map(section => section.section), expected.sections, context);
    if (join) {
      check(`${category}ContinuationIdentity`, paragraph.continuationOf,
        {recordId:joinedRow.id,section:joinedRow.section,previousSourceId:join.beforeSourceId,nextSourceId:expectedParagraphs[index+1].sourceId,
          ...(expected.nieseSections.length?{firstMilestone:expected.nieseSections[0],nextSection:expectedParagraphs[index+1].nieseSections[0]}:{})}, context);
      check(`${category}NoInventedContinuationMarker`, paragraph.nieseMarkers.map(marker=>marker.section), expected.nieseSections, context);
      check(`${category}DocumentedParagraphJoin`, paragraph.recordJoin,
        {kind:'paragraph-separator',recordId:joinedRow.id,start:join.start,end:join.end,text:join.text}, context);
      check(`${category}ParagraphJoinText`, recordById.get(joinedRow.id).text.slice(join.start,join.end), join.text, context);
      check(`${category}ContinuationRecordOffset`, paragraph.sections.filter(section=>section.recordId===joinedRow.id).map(section=>section.recordOffset), [join.end], context);
      check(`${category}LaterParagraphIntervalsNotShifted`, paragraph.sections.filter(section=>section.recordId!==joinedRow.id).map(section=>section.recordOffset ?? 0), Array(expected.nieseSections.length).fill(0), context);
    } else {
      check(`${category}NoUnexpectedContinuation`, paragraph.continuationOf ?? null, null, context);
      check(`${category}NoUnexpectedJoin`, paragraph.recordJoin ?? null, null, context);
      check(`${category}ExplicitMarkerIdentity`, paragraph.nieseMarkers.map(marker => marker.section), expected.nieseSections, context);
    }
  });
  check(`${category}TokenCount`, report.counts.runningWordTokens, expectedRows.reduce((sum,row) => sum + row.tokens.length,0));
  check(`${category}HeadingExclusions`, report.counts.excludedHeadingParagraphs, files.reduce((sum,file) => sum + file.evidence.excludedHeadings,0));
  check(`${category}LabelExclusions`, report.counts.excludedCitationLabels, files.reduce((sum,file) => sum + file.evidence.excludedLabels,0));
  check(`${category}FootnoteExclusions`, report.counts.excludedFootnotes, files.reduce((sum,file) => sum + file.exclusions.filter(e => e.kind === 'note' && e.sourceId).length,0));
  check(`${category}ContinuationCount`, report.counts.continuationParagraphs || 0, expectedRows.reduce((sum,row) => sum + (row.paragraphJoins?.length || 0),0));
}

// Small RFC-style reader used only to audit the actual exported bytes. It
// understands quoted embedded commas/newlines and doubled quotes.
function parseCSV(text) {
  assert.equal(text[0], '\uFEFF');
  const rows = []; let row = [], cell = '', quoted = false;
  for (let i = 1; i < text.length; i++) {
    const char = text[i];
    if (char === '"') {
      if (quoted && text[i + 1] === '"') {cell += '"'; i++;} else quoted = !quoted;
    } else if (char === ',' && !quoted) {row.push(cell); cell = '';}
    else if (char === '\r' && text[i + 1] === '\n' && !quoted) {row.push(cell); rows.push(row); row = []; cell = ''; i++;}
    else cell += char;
  }
  assert.equal(quoted, false); assert.equal(cell, ''); assert.equal(row.length, 0);
  const columns = rows.shift(); assert.equal(new Set(columns).size, columns.length);
  return rows.map(cells => {
    assert.equal(cells.length, columns.length);
    const result = Object.fromEntries(columns.map((column,index) => [column,cells[index]]));
    for (const column of JSON.parse(result.escaped_columns_json)) {
      assert.equal(result[column][0], "'"); result[column] = result[column].slice(1);
    }
    return result;
  });
}
function validateConcordance(result, oracle, expected, tree, catalog, category = 'Concordance') {
  const model = buildConcordance(result, result.records, {readerBase:'https://latinjosephus.github.io/'});
  const expectedSpans = new Set([...expected.values()].flatMap(set => [...set]));
  check(`${category}Geometries`, model.rows.map(row => spanKey(row.spans)).sort(), [...expectedSpans].sort());
  check(`${category}NegativeUnits`, model.unhighlightedUnits.length, [...expected.values()].filter(set => !set.size).length);
  check(`${category}CountKind`, model.countKind, tree.op === 'leaf' ? tree.phrase ? 'phrase' : 'word' : 'evidence');
  check(`${category}OccurrenceCount`, model.occurrenceCount, tree.op === 'leaf' ? expectedSpans.size : null);
  for (const row of model.unhighlightedUnits) {
    const first = oracle.byId.get(row.records[0].id), link = new URL(row.readerURL);
    check(`${category}NegativeReader`, [link.searchParams.get('book'),link.searchParams.get('niese'),link.searchParams.get('english')],
      [String(result.scope === 'book' ? first.book : first.readerBook),result.scope === 'book' ? null : String(first.section),'whiston']);
  }
  for (const row of model.rows) {
    const spans = row.spans;
    const match = spans.map((span,index) => {
      const source = oracle.byId.get(span.recordId).text;
      return source.slice(index ? 0 : span.start, index === spans.length - 1 ? span.end : source.length);
    }).join(' ');
    check(`${category}OriginalMatchedText`, row.match, match, {spans});
    check(`${category}Edition`, [row.language,row.edition,row.collectionId], ['English','Whiston',collectionId]);
    const first = oracle.byId.get(spans[0].recordId), link = new URL(row.readerURL);
    check(`${category}PassageReader`, [link.searchParams.get('book'),link.searchParams.get('niese'),link.searchParams.get('english')],
      [String(first.readerBook),String(first.section),'whiston']);
  }
  const exported = exportConcordance(model,result,{catalog,exportedAt:'2026-10-20T12:00:00Z',searchURL:'https://latinjosephus.github.io/search/'});
  const csv = parseCSV(exported.text);
  check(`${category}CSVRowCount`, exported.rowCount, model.rows.length + model.unhighlightedUnits.length);
  check(`${category}CSVTotalRows`, csv.length, Math.max(1,exported.rowCount));
  for (const row of csv) {
    check(`${category}CSVQuery`, row.query, result.query);
    check(`${category}CSVQueryJSON`, JSON.parse(row.query_json), result.query);
    check(`${category}CSVScope`, row.scope, result.scope);
    check(`${category}CSVEnglishNormalization`, row.spelling_equivalence, 'original spelling');
    if (row.row_type === 'search-summary') continue;
    check(`${category}CSVVersion`, [row.language,row.edition,row.collection_id], ['English','Whiston',collectionId]);
    const original = JSON.parse(row.original_context_json), segments = JSON.parse(row.source_segments_json);
    check(`${category}CSVOriginalContext`, original, {left:row.left_context,match:row.matched_text,right:row.right_context});
    for (const segment of segments) {
      const source = oracle.byId.get(segment.recordId);
      check(`${category}CSVSourceSegment`, segment.text, source.text.slice(segment.start,segment.end));
      check(`${category}CSVSourcePath`, segment.sourcePath, source.sourcePath);
    }
    if (row.row_type !== 'matching-unit') {
      check(`${category}CSVJoinedContext`, segments.map(segment => segment.joinBefore + segment.text).join(''), original.left + original.match + original.right);
      check(`${category}CSVExpectedHit`, expectedSpans.has(spanKey(JSON.parse(row.hit_spans_json))), true);
    }
  }
  // A Whiston-only export must not inherit the Latin manuscript's omissions.
  check(`${category}CSVNoLatinCoverage`, csv.some(row => /Bamberg|IX\.51[–-]109.*absent|XII\.248/.test(row.editorial_notes || '')), false);
  const sources = JSON.parse(csv[0].selected_sources_json);
  check(`${category}CSVSelectedCollections`, sources.collections.map(c => c.id), [collectionId]);
  check(`${category}CSVSelectedBooks`, sources.books.map(b => b.id), [...new Set(oracle.rows.map(row => `${collectionId}:${row.book}`))]);
  check(`${category}CSVNormalizationMetadata`, sources.normalization,
    {caseSensitive:false,spellingEquivalence:'none',foldedCollectionIds:[],literalCollectionIds:[collectionId]});
  return {model,csv};
}

const fixtures = [
  ['"In the beginning God created"', phrase(['In','the','beginning','God','created'])],
  ['"IN, THE; BEGINNING—GOD created"', phrase(['IN','THE','BEGINNING','GOD','created'])],
  ['"in the begin* God creat*"', phrase(['in','the','begin*','God','creat*'])],
  ['"those who undertake"', phrase(['those','who','undertake'])],
  ['God', word('God')], ['Judea',word('Judea')], ['iudea',word('iudea')], ['the',word('the')],
  ['God AND NOT man',and(word('God'),not(word('man')))],
  ['God OR Moses AND Abraham',or(word('God'),and(word('Moses'),word('Abraham')))],
  ['(God OR Moses) AND Abraham',and(or(word('God'),word('Moses')),word('Abraham'))],
  ['God Abraham',and(word('God'),word('Abraham'))],
  ['NOT (God OR NOT Abraham)',not(or(word('God'),not(word('Abraham'))))],
  ['NOT NOT Abraham',not(not(word('Abraham')))],
  ['Abraham OR Abra*',or(word('Abraham'),word('Abra*'))],
  ['NOT zzzzwhistonabsent',not(word('zzzzwhistonabsent'))],
  ['NOT *',not(word('*'))], ['zzzzwhistonabsent',word('zzzzwhistonabsent')],
];

async function main() {
  const witnessPath = preserve(resolve(base,'tests/whiston-source-witness.py'));
  const verifierPath = preserve(resolve(base,'tests/whiston-corpus-qa.mjs'));
  const readerPath = preserve(resolve(root,'assets/js/renderTei.js'));
  const readerSHA = digest(readerPath);
  if (explicitReaderSHA) check('ExplicitReaderBaseline',readerSHA,explicitReaderSHA);
  const readerBaseline = {expectedSha256:explicitReaderSHA || readerSHA,observedSha256:readerSHA,
    provenance:explicitReaderSHA ? 'explicit-argument' : 'observed-source-checkout',preservationDuringRunRequired:true,publicationInput:false};
  const catalogPath = preserve(resolve(base,'catalog.json'));
  const catalog = readJSON(catalogPath), config = catalog.collections.find(c => c.id === collectionId);
  assert.ok(config,'Build the Whiston I-X collection and catalog before running acceptance.');
  const entries = catalog.books.filter(entry => entry.collectionId === collectionId);
  check('OnlyAcceptedBooksPublished',entries.map(entry => entry.number),expectedBooks);
  check('EnglishCollectionIdentity',[config.work,config.language,config.edition],['antiquities','English','Whiston']);
  const corpusPath = preserve(resolve(base,config.corpusPath));
  const extractionPath = preserve(resolve(base,config.extractionReportPath));
  const manifestPath = preserve(resolve(base,config.manifestPath));
  const runtimePaths = ['engine.mjs','collection.mjs','concordance.mjs','ui-utils.mjs','extract-whiston.py','vendor/lunr.cjs'];
  runtimePaths.forEach(path => preserve(resolve(base,path)));
  const sourcePaths = Object.fromEntries(['preface',...expectedBooks.map(book=>`book-${String(book).padStart(2,'0')}`),'book-11']
    .map(stem => [stem,preserve(resolve(root,`assets/xml/antiquities/English/${stem}.xml`))]));
  const witness = JSON.parse(execFileSync(process.env.SEARCH_PYTHON || process.env.PYTHON || 'python3',[witnessPath,root],{encoding:'utf8',maxBuffer:40*1024*1024}));
  check('IndependentCollectionTotals',witness.totals,{books:10,sections:3474,tokens:236049});
  check('IndependentBookTotals',witness.bookTotals,expectedBookTotals);
  const corpus = readJSON(corpusPath), extraction = readJSON(extractionPath);
  inspectRecords(corpus,witness.rows,'Indexed');
  check('CollectionCorpusHash',config.corpusSHA256,digest(corpusPath));
  check('CollectionManifestHash',config.manifestSHA256,digest(manifestPath));
  check('ExtractionTokens',extraction.counts.runningWordTokens,236049);
  check('ExtractionSections',extraction.counts.sections,3474);
  check('ExtractionPublishedBooks',extraction.scope.books,expectedBooks);
  const oracle = makeOracle(witness.rows);
  const bookData = entries.map(entry => {
    const suffix = String(entry.number).padStart(2,'0');
    const paths = {bundle:preserve(resolve(base,entry.path)),corpus:preserve(resolve(base,entry.corpusPath)),
      extractionReport:preserve(resolve(base,'data',collectionId,`book-${suffix}.extraction-report.json`)),source:sourcePaths[`book-${suffix}`]};
    const rows = witness.rows.filter(row => row.book === entry.number), files = witness.indexedFiles.filter(file => file.evidence.book === entry.number);
    const records = readJSON(paths.corpus), bundle = readJSON(paths.bundle), report = readJSON(paths.extractionReport);
    const total = expectedBookTotals.find(total => total.book === entry.number), tag = `Book${entry.number}`;
    check(`${tag}CorpusShard`,records,corpus.filter(record => record.book === entry.number));
    inspectProjection(report,files,records,`${tag}Projection`);
    check(`${tag}BundleMatchesCorpus`,bundle.records,records.map(record => ({...record,breakBefore:Boolean(record.breakBefore)})));
    check(`${tag}AllIndexedTokenOffsets`,bundle.tokens,rows.map(row => row.tokens));
    check(`${tag}BundleTokens`,bundle.stats.tokens,total.tokens);
    check(`${tag}CatalogBundleHash`,entry.sha256,digest(paths.bundle));
    check(`${tag}CatalogBundleBytes`,entry.bytes,readFileSync(paths.bundle).length);
    check(`${tag}CatalogCorpusHash`,entry.corpusSHA256,digest(paths.corpus));
    check(`${tag}CatalogTokens`,entry.tokens,total.tokens);
    check(`${tag}CatalogSections`,entry.sections,total.sections);
    if(acceptedPriorBookHashes[entry.number]) for(const [kind,sha256] of Object.entries(acceptedPriorBookHashes[entry.number]))
      check('PriorBookAssetUnchanged',digest(paths[kind]),sha256,{book:entry.number,kind});
    return {entry,paths,rows,files,oracle:makeOracle(rows),engine:createEngine(bundle,lunr)};
  });
  for (const book of bookData) {
    const {rows,oracle:bookOracle,engine} = book;
    const vocabulary = smoke ? bookOracle.vocabulary.filter((_,i) => i % Math.max(1,Math.floor(bookOracle.vocabulary.length/20)) === 0) : bookOracle.vocabulary;
    for (const term of vocabulary) verify(engine,bookOracle,word(term),'section','Vocabulary');
    for (const [query,tree] of fixtures) for (const scope of ['section','book']) verify(engine,bookOracle,tree,scope,'Fixture',query);
    const patterns = new Set(['*','**','God*','*God','G*d','G**od','creat*','*tion','*creat*','J*','*v*','*j*','zzzzwhistonabsent*']);
    const sampled = bookOracle.vocabulary.filter(term => term.length >= 5).filter((_,i) => i % (smoke ? 400 : 90) === 0);
    for (const term of sampled) {patterns.add(term.slice(0,3)+'*');patterns.add('*'+term.slice(-3));patterns.add(term.slice(0,2)+'*'+term.slice(-2));}
    for (const pattern of patterns) for (const scope of ['section','book']) verify(engine,bookOracle,word(pattern),scope,'Wildcard');
    for (let index = 0; index < rows.length; index++) {
      if (smoke && ![0,25,26,120,275,rows.length-1].includes(index)) continue;
      const row = rows[index], middle = Math.max(0,Math.floor(row.tokens.length/2)-1);
      const tree = phrase(row.tokens.slice(middle,middle+3).map(token => token.term));
      for (const scope of ['section','book']) verify(engine,bookOracle,tree,scope,'WithinEveryInterval');
    }
    for (let index = 0; index < rows.length-1; index++) {
      if (smoke && ![0,24,25,26,50,274,275,rows.length-2].includes(index)) continue;
      const left = rows[index], right = rows[index+1];
      const tree = phrase([...left.tokens.slice(-2),...right.tokens.slice(0,2)].map(token => token.term));
      for (const scope of ['section','book']) verify(engine,bookOracle,tree,scope,'EveryCitationSeam');
    }
  }
  const firstBook = bookData[0], firstOracle = firstBook.oracle;
  const proemSeam = phrase([...firstBook.rows[25].tokens.slice(-2),...firstBook.rows[26].tokens.slice(0,2)].map(token => token.term));
  check('ProemPhraseCannotCross',verify(firstBook.engine,firstOracle,proemSeam,'book','ProemSeam',print(proemSeam),true).matchingUnits,0);
  const acrossProemBoolean = and(phrase(firstBook.rows[25].tokens.slice(-2).map(t => t.term)),phrase(firstBook.rows[26].tokens.slice(0,2).map(t => t.term)));
  check('BooleanMayRelateProemAndNarrative',verify(firstBook.engine,firstOracle,acrossProemBoolean,'book','ProemBoolean').matchingUnits,1);
  const continuationPhrase = phrase(['wrong','way','In','like','manner']);
  const fourthBook = bookData[3];
  for (const scope of ['section','book']) check('IV276ParagraphContinuationSearchable',
    verify(fourthBook.engine,fourthBook.oracle,continuationPhrase,scope,'ContinuationPhrase',print(continuationPhrase),true).occurrences,1);
  const eighthBook = bookData[7], eighthContinuationPhrase = phrase(['to','Jerusalem','Now','when','Rehoboam']);
  for(const scope of ['section','book']) check('VIII255ParagraphContinuationSearchable',
    verify(eighthBook.engine,eighthBook.oracle,eighthContinuationPhrase,scope,'NewContinuationPhrase',print(eighthContinuationPhrase),true).occurrences,1);
  const continued255=eighthBook.rows.find(row=>row.section===255),continuation255=continued255.sourceSegments.find(segment=>segment.sourceId==='english-book08-num255');
  check('VIII255ContinuationCoordinates',[continuation255.rawStart,continuation255.rawEnd,continuation255.start,continuation255.end],[3,226,203,426]);
  check('VIII255ContinuationTokens',continued255.tokens.filter(token=>token.start>=continuation255.start).length,42);
  for(const [book,first,last] of [[7,69,99],[9,51,109],[10,108,108]]) {
    const retained=bookData[book-1].rows.filter(row=>row.section>=first&&row.section<=last);
    check('EnglishCoverageIndependentOfLatinOmissions',retained.map(row=>row.section),Array.from({length:last-first+1},(_,index)=>first+index),{book});
    check('EnglishRetainedIntervalsNonempty',retained.every(row=>row.tokens.length>0),true,{book});
  }

  // Exercise the production loader (including its SHA check and per-language
  // dispatch), not only a directly instantiated low-level search engine.
  const loaded = new Set();
  const collection = createCollection(catalog,lunr,{baseURL:'https://whiston.invalid/search/',fetchImpl:async url => {
    const path = new URL(url).pathname.replace(/^\/search\//,'');
    assert.ok(catalog.books.some(book => book.path === path)); loaded.add(path);
    return new Response(readFileSync(preserve(resolve(base,path))),{status:200});
  }});
  async function selectedSearch(tree,scope,fold=false,category='Collection',query=print(tree),bookNumbers=[1]) {
    totalQueries++;counts[`${category}Queries`]=(counts[`${category}Queries`]||0)+1;
    const selected = bookData.filter(book => bookNumbers.includes(book.entry.number));
    const selectedOracle = selected.length === expectedBooks.length ? oracle : selected.length === 1 ? selected[0].oracle : makeOracle(selected.flatMap(book => book.rows));
    const result = await collection.search(query,{collections:[collectionId],books:selected.map(book => book.entry.id),scope,fold});
    compare(result,selectedOracle.evaluate(tree,scope),selectedOracle,scope,category,query);
    check(`${category}SelectedBooks`,result.selectedBooks,selected.map(book => book.entry.id));
    check(`${category}EnglishNeverFolds`,result.fold,false);
    check(`${category}NormalizationMetadata`,result.normalization,
      {caseSensitive:false,spellingEquivalence:'none',foldedCollectionIds:[],literalCollectionIds:[collectionId]});
    return result;
  }
  for (const query of ['Judea','iudea','Jews','iews','live','liue']) for (const fold of [false,true])
    await selectedSearch(word(query),'section',fold,'EnglishLiteral');
  check('LoaderInitiallyRequestsOnlyBookI',[...loaded],[firstBook.entry.path]);
  const concordanceTrees = [word('God'),phrase(['in','the','beginning']),phrase(['in','the','begin*']),
    phrase([...firstBook.rows[26].tokens.slice(-2),...firstBook.rows[27].tokens.slice(0,2)].map(t=>t.term)),
    acrossProemBoolean,or(word('Abraham'),word('Abra*')),not(word('zzzzwhistonabsent')),word('zzzzwhistonabsent')];
  for (const tree of concordanceTrees) for (const scope of ['section','book']) {
    const result = await selectedSearch(tree,scope,true,'ConcordanceSearch');
    validateConcordance(result,firstOracle,firstOracle.evaluate(tree,scope),tree,catalog);
  }
  const openings = [
    {book:2,tree:phrase(['After','the','death','of','Isaac'])},
    {book:3,tree:phrase(['When','the','Hebrews','had','obtained'])},
    {book:4,tree:phrase(['Now','this','life','of','the','Hebrews'])},
    {book:5,tree:phrase(['When','Moses','was','taken','away'])},
    {book:6,tree:phrase(['When','the','Philistines','had','taken','the','ark'])},
    {book:7,tree:phrase(['This','fight','proved','to','be','on','the','same','day'])},
    {book:8,tree:phrase(['We','have','already','treated','of','David'])},
    {book:9,tree:phrase(['WHEN','Jehoshaphat','the','king','was','come','to','Jerusalem'])},
    {book:10,tree:phrase(['IT','was','now','the','fourteenth','year'])},
  ];
  for (const {book,tree} of openings) {
    const data = bookData[book-1];
    for (const scope of ['section','book']) {
      const result = await selectedSearch(tree,scope,true,'NewBookOpening',print(tree),[book]);
      validateConcordance(result,data.oracle,data.oracle.evaluate(tree,scope),tree,catalog,'NewBookExport');
      check('NewBookOpeningUnique',result.occurrences,1,{book,query:print(tree)});
      check('NewBookOpeningCitation',result.hitGroups[0].hits[0].spans[0].recordId,`${collectionId}-${book}-1`);
      if(scope === 'section') noteExample(print(tree),scope,result,`Book ${book} opening`);
    }
    const allResult = await selectedSearch(tree,'section',false,'CombinedBookSelection',print(tree),expectedBooks);
    check('OpeningRemainsOneAcrossAllBooks',allResult.occurrences,1,{book});
  }
  for (const query of ['Judea','iudea','Jews','iews','live','liue']) for (const fold of [false,true])
    await selectedSearch(word(query),'section',fold,'AllEnglishLiteral',query,expectedBooks);
  for (const tree of [word('God'),continuationPhrase,eighthContinuationPhrase,not(word('zzzzwhistonabsent')),word('zzzzwhistonabsent')]) {
    for (const scope of ['section','book']) {
      const result = await selectedSearch(tree,scope,true,'AllBookConcordanceSearch',print(tree),expectedBooks);
      const exported = validateConcordance(result,oracle,oracle.evaluate(tree,scope),tree,catalog,'AllBookConcordance');
      if(tree === continuationPhrase) {
        check('ContinuationCSVRetainsParagraphBreak',exported.csv[0].matched_text,'wrong way.\n\nIn like manner');
        check('ContinuationCSVRetainsBothSourceIDs',JSON.parse(exported.csv[0].source_segments_json)[0].sourceIds,
          ['english-book04-num276','english-book04-num276b']);
      }
      if(tree === eighthContinuationPhrase) {
        check('VIII255CSVRetainsParagraphBreak',exported.csv[0].matched_text,'to Jerusalem.\n\nNow when Rehoboam');
        check('VIII255CSVRetainsBothSourceIDs',JSON.parse(exported.csv[0].source_segments_json).find(segment=>segment.recordId===continued255.id).sourceIds,
          ['english-book08-num251','english-book08-num255']);
      }
    }
  }
  for (let index=0;index<bookData.length-1;index++) {
    const left = bookData[index].rows.at(-1), right = bookData[index+1].rows[0];
    const tree = phrase([...left.tokens.slice(-4),...right.tokens.slice(0,4)].map(token => token.term));
    for(const scope of ['section','book']) {
      const result = await selectedSearch(tree,scope,false,'CrossBookPhraseBoundary',print(tree),expectedBooks);
      check('NoPhraseCrossesBooks',result.matchingUnits,0,{left:left.book,right:right.book,scope});
    }
  }
  for(const scope of ['section','book']) {
    const differentBooks = and(openings[0].tree,openings[1].tree);
    check('NoBooleanMatchesAcrossBooks',(await selectedSearch(differentBooks,scope,false,'CrossBookBoolean',print(differentBooks),expectedBooks)).matchingUnits,0);
    const alternatives = or(openings[0].tree,openings[1].tree);
    const result = await selectedSearch(alternatives,scope,false,'CrossBookAlternatives',print(alternatives),expectedBooks);
    check('SameNumberedSectionsRemainSeparate',result.matchingUnits,2);
    check('AlternativesPreserveBookIdentity',result.matchingBooks,[`${collectionId}:2`,`${collectionId}:3`]);
    validateConcordance(result,oracle,oracle.evaluate(alternatives,scope),alternatives,catalog,'CrossBookExport');
  }
  check('HeadingPhraseExcluded',(await selectedSearch(phrase(['Containing','the','interval']),'book',false,'HeadingExclusion',
    '"Containing the interval"',expectedBooks)).matchingUnits,0);
  const ninthBook=bookData[8],ninthFile=ninthBook.files[0];
  const notes=ninthFile.exclusions.filter(item=>item.kind==='note'&&item.sourceId);
  check('IXPublishedFootnoteCount',notes.length,7);
  check('IXRestoredHeadingsExcluded',ninthFile.exclusions.filter(item=>item.kind==='heading'&&item.sourceId).map(item=>item.sourceId),
    ['english-book09-restored-heading-05','english-book09-restored-heading-06']);
  for(const note of notes) {
    const tree=phrase(independentTokens(note.text).slice(0,6).map(token=>token.term));
    check('IXFootnoteAbsent',verify(ninthBook.engine,ninthBook.oracle,tree,'book','PublishedFootnote').matchingUnits,0);
    const row=ninthBook.rows.find(row=>row.section===note.section);
    const before=row.sourceSegments.filter(segment=>segment.rawEnd<=note.rawStart).at(-1);
    const after=row.sourceSegments.find(segment=>segment.rawStart>=note.rawEnd);
    if(before&&after) {
      const left=row.tokens.filter(token=>token.end<=before.end).slice(-2),right=row.tokens.filter(token=>token.start>=after.start).slice(0,2);
      if(left.length&&right.length) {
        const bridge=phrase([...left,...right].map(token=>token.term));
        const result=await selectedSearch(bridge,'section',false,'PublishedFootnoteAdjacency',print(bridge),[9]);
        check('IXFootnoteBridgeRetainsSection',result.hitGroups.some(group=>group.recordIds.includes(row.id)),true,{section:row.section});
        validateConcordance(result,ninthBook.oracle,ninthBook.oracle.evaluate(bridge,'section'),bridge,catalog,'FootnoteBridgeCSV');
      }
    }
  }
  for(const [book,section,tree] of [
    [9,51,phrase(['Elisha','also','sent','a','hasty','message'])],
    [9,51,phrase(['to','Joram','and','exhorted','him'])],
    ...[[7,69],[7,99],[9,109],[10,108]].map(([book,section])=>[book,section,phrase(bookData[book-1].rows.find(row=>row.section===section).tokens.slice(0,6).map(token=>token.term))]),
  ]) {
    const data=bookData[book-1];
    const result=await selectedSearch(tree,'section',false,'RestoredEnglishCoverage',print(tree),[book]);
    check('RestoredEnglishCitationFound',result.hitGroups.some(group=>group.recordIds.includes(`${collectionId}-${book}-${section}`)),true,{book,section});
    validateConcordance(result,data.oracle,data.oracle.evaluate(tree,'section'),tree,catalog,'RestoredEnglishCSV');
    if(book===9&&section===51)noteExample(print(tree),'section',result,'Published restored IX.51 and footnote exclusion');
  }
  const tenthBook=bookData[9];
  for(const formatting of tenthBook.files[0].formatting) {
    const row=tenthBook.rows.find(row=>row.section===formatting.section),segment=row.sourceSegments.find(segment=>segment.rawStart===formatting.rawStart&&segment.rawEnd===formatting.rawEnd);
    check('XTransparentFormattingSourceText',segment?.text,formatting.text,{section:row.section});
    const at=row.tokens.findIndex(token=>token.start===segment.start);
    const tree=phrase(row.tokens.slice(Math.max(0,at-2),at+3).map(token=>token.term));
    const result=await selectedSearch(tree,'section',false,'TransparentFormatting',print(tree),[10]);
    check('XFormattingDoesNotBreakPhrase',result.hitGroups.some(group=>group.recordIds.includes(row.id)),true,{section:row.section});
    validateConcordance(result,tenthBook.oracle,tenthBook.oracle.evaluate(tree,'section'),tree,catalog,'TransparentFormattingCSV');
  }
  const salutation=phrase(['Solomon','Hiram','To','King','Solomon','It','is','fit']);
  check('VIIIInlineSalutationAcrossLineBreaks',verify(eighthBook.engine,eighthBook.oracle,salutation,'section','InlineLetterHeading',print(salutation),true).occurrences,1);
  check('LoaderRequestsExactlyPublishedEnglishBooks',[...loaded].sort(),entries.map(entry => entry.path).sort());

  const latinId='antiquities-latin-bamberg78',latinBook=`${latinId}:1`;
  for (const query of ['Judea','iudea','Jews','iews']) {
    const mixed = await collection.search(query,{collections:[latinId,collectionId],books:[latinBook,bookId],scope:'section',fold:true});
    totalQueries++;
    const englishGroups=mixed.hitGroups.filter(group=>group.collectionId===collectionId);
    const english={...mixed,hitGroups:englishGroups,matchingUnits:englishGroups.length,
      occurrences:englishGroups.reduce((sum,group)=>sum+group.hits.length,0),
      matchingSections:new Set(englishGroups.flatMap(group=>group.recordIds)).size};
    compare(english,firstOracle.evaluate(word(query),'section'),firstOracle,'section','MixedEnglishLiteral',query);
    check('MixedHasLatinNormalization',mixed.fold,true);
    check('MixedNormalizationMetadata',mixed.normalization,
      {caseSensitive:false,spellingEquivalence:'latin-uv-ij',foldedCollectionIds:[latinId],literalCollectionIds:[collectionId]});
  }
  const isolation=await collection.search('God AND deus',{collections:[latinId,collectionId],books:[latinBook,bookId],scope:'book',fold:false});totalQueries++;
  check('NoBooleanMatchesAcrossLanguages',isolation.matchingUnits,0);
  const alternatives=await collection.search('God OR deus',{collections:[latinId,collectionId],books:[latinBook,bookId],scope:'book',fold:false});totalQueries++;
  check('BothLanguagesRemainDiscoverable',alternatives.matchingBooks,[latinBook,bookId]);
  const mixedExportResult=await collection.search('God OR deus',{collections:[latinId,collectionId],books:[latinBook,bookId],scope:'book',fold:true});totalQueries++;
  const mixedModel=buildConcordance(mixedExportResult,mixedExportResult.records,{readerBase:'https://latinjosephus.github.io/'});
  const mixedCSV=parseCSV(exportConcordance(mixedModel,mixedExportResult,{catalog,exportedAt:'2026-10-20T12:00:00Z'}).text);
  check('MixedCSVNormalizationLabel',[...new Set(mixedCSV.map(row=>row.spelling_equivalence))],['Latin: u/v and i/j equivalent; other languages: original spelling']);
  check('MixedCSVBothEditions',[...new Set(mixedCSV.map(row=>`${row.language}/${row.edition}`))],['Latin/Bamberg Msc. Class. 78','English/Whiston']);
  check('MixedCSVNormalizationMetadata',JSON.parse(mixedCSV[0].selected_sources_json).normalization,mixedExportResult.normalization);
  for(const query of ['Judea','iudea','Moses','liue']) {
    const mixed = await collection.search(query,{collections:[latinId,collectionId],books:[latinBook,...entries.map(entry=>entry.id)],scope:'section',fold:true});
    totalQueries++;
    const groups = mixed.hitGroups.filter(group=>group.collectionId===collectionId);
    const english = {...mixed,hitGroups:groups,matchingUnits:groups.length,
      occurrences:groups.reduce((sum,group)=>sum+group.hits.length,0),matchingSections:new Set(groups.flatMap(group=>group.recordIds)).size};
    compare(english,oracle.evaluate(word(query),'section'),oracle,'section','MixedAllEnglishLiteral',query);
    check('MixedAllEnglishLiteralCollections',mixed.normalization.literalCollectionIds,[collectionId]);
  }

  // The Book XI source remains test-only. Running the production extractor
  // here exercises it; all expected text and positions are independently
  // supplied by the witness loaded above.
  const testProduction = JSON.parse(execFileSync(process.env.SEARCH_PYTHON || process.env.PYTHON || 'python3',['-c',
    'import importlib.util,json,pathlib,sys\nr=pathlib.Path(sys.argv[1]);s=importlib.util.spec_from_file_location("whiston_test",r/"bin/search/extract-whiston.py");m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\nout=[]\nfor n in (11,):\n p=f"assets/xml/antiquities/English/book-{n:02d}.xml";rows,report=m.extract_document((r/p).read_bytes(),book_number=n,source_path=p);out.append({"book":n,"records":rows,"report":report})\nprint(json.dumps(out,ensure_ascii=False))',root],
    {encoding:'utf8',maxBuffer:40*1024*1024}));
  for (let index=0;index<testProduction.length;index++) {
    const actual=testProduction[index], witnessed=witness.testSources[index], tag=`TestOnly${actual.book}`;
    inspectRecords(actual.records,witnessed.rows,tag);
    inspectProjection(actual.report,[witnessed],actual.records,`${tag}Projection`);
    const testOracle=makeOracle(witnessed.rows),testEngine=createEngine(buildBundle(actual.records,lunr),lunr);
    check('OnlyXIFutureWitness',actual.book,11);
    for(const [leftNumber,rightNumber] of [[311,326],[342,312],[325,343],[311,312],[325,326],[342,343]]) {
        const left=witnessed.rows.find(row=>row.section===leftNumber),right=witnessed.rows.find(row=>row.section===rightNumber);
        const tree=phrase([...left.tokens.slice(-3),...right.tokens.slice(0,3)].map(token=>token.term));
        const result=verify(testEngine,testOracle,tree,'book','TestOnlyPhysicalOrder');
        const adjacent=witnessed.rows.indexOf(right)===witnessed.rows.indexOf(left)+1;
        check('XIPhysicalNotNumericalSeams',result.matchingUnits,adjacent?1:0,{left:leftNumber,right:rightNumber});
    }
  }
  for(const [path,before] of checkedFiles)check('InputUnchangedDuringRun',digest(path),before,{path:relative(root,path)});
  const report={status:'PASS',generatedAt:new Date().toISOString(),independentVerifier:'bin/search/tests/whiston-corpus-qa.mjs',readerBaseline,
    runtime:{node:process.version,...witness.runtime},source:{...witness.totals,uniqueLiteralVocabulary:oracle.vocabulary.length,proemSections:26,narrativeSections:3448,bookTotals:witness.bookTotals},
    sources:witness.sources,testSources:witness.testSources.map(file=>({...file.evidence,purpose:'Book XI physical order and non-numerical phrase seams; not published.'})),
    sourceCases:{restoredIX:{sections:59,range:[51,109],excludedInlineNotes:7,excludedRestoredHeadings:2},
      paragraphContinuations:[{book:4,section:276,sourceIds:['english-book04-num276','english-book04-num276b']},
        {book:8,section:255,sourceIds:continued255.sourceIds,continuationTokens:42,continuationRecordRange:[203,426],paragraphSeparatorRange:[201,203]}],
      formattingX:tenthBook.files[0].formatting.map(({section,text,attributes})=>({section,text,attributes,treatment:'Running text; not editorial addition'})),
      preservedPriorBooks:Object.keys(acceptedPriorBookHashes).map(Number)},
    verifiedFiles:{corpus:evidence(corpusPath),catalog:evidence(catalogPath),engine:evidence(resolve(base,'engine.mjs')),
      collection:evidence(resolve(base,'collection.mjs')),concordance:evidence(resolve(base,'concordance.mjs')),uiUtils:evidence(resolve(base,'ui-utils.mjs')),
      verifier:evidence(verifierPath),witness:evidence(witnessPath),extractor:evidence(resolve(base,'extract-whiston.py')),manifest:evidence(manifestPath),
      lunr:evidence(resolve(base,'vendor/lunr.cjs')),extractionReport:evidence(extractionPath),originalReader:evidence(readerPath),
      testSources:[evidence(sourcePaths['book-11'])],
      books:bookData.map(book=>({book:book.entry.number,bundle:evidence(book.paths.bundle),corpus:evidence(book.paths.corpus),source:evidence(book.paths.source),
        ...(book.entry.number===1?{additionalSources:[evidence(sourcePaths.preface)]}:{}),extractionReport:evidence(book.paths.extractionReport)}))},
    method:{source:'Independent minidom text-node projection from twelve SHA-pinned XML files; eleven published inputs and one explicitly test-only input. Every source-to-record slice and exact paragraph restoration is checked, including the markerless IV.276 paragraph and the pre-milestone VIII.255 continuation with their explicit paragraph separators. The Book I-V corpora, extraction reports and search bundles remain byte-for-byte identical to the accepted prior release. Book IX restored text is published; its seven inline footnotes and restored headings are excluded. Book X transparent bold formatting preserves running text without inventing editorial additions.',
      tokens:'Every indexed Unicode word and original UTF-16 offset independently scanned in Python and JavaScript and compared with each serialized book index.',
      queries:'All literal vocabulary per book, one exact phrase per interval, every neighboring citation seam, all nine book boundaries, bounded wildcard and explicit Boolean fixtures. Expected ASTs and sequential phrase scans do not import production parsing/tokenization. Published Book IX footnote exclusions, phrases across excluded notes, restored English intervals and Book X transparent formatting have focused checks. Combined selections preserve distinct same-numbered sections and keep phrases and Boolean conditions inside their own book.',
      language:'English-only and mixed English/Latin collection requests verify Latin-only spelling equivalence and separate Boolean scopes.',
      exports:'Concordance geometry, original context, reader parameters, source slices, source fingerprints, CSV decoding, negative-only units and zero-result summaries.'},
    counts,totalQueries,assertions,failedAssertions:0,examples,durationSeconds:Math.round((performance.now()-started)/100)/10,
    limitations:['Coverage is the accepted Whiston Proem and Books I-X XML only; XI is a future-expansion test witness, not a published book.',
      'This source/query acceptance does not establish a new translation text or collate printed editions; browser interaction is verified separately.'],failures:[]};
  if(!smoke)writeFileSync(destination,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({status:smoke?'DEVELOPMENT_SMOKE_PASS':'PASS',source:report.source,totalQueries,assertions,durationSeconds:report.durationSeconds,report:smoke?null:relative(root,destination)},null,2));
}

try {
  if(!smoke){mkdirSync(dirname(destination),{recursive:true});writeFileSync(destination,JSON.stringify({status:'RUNNING',startedAt:new Date().toISOString(),independentVerifier:'bin/search/tests/whiston-corpus-qa.mjs'})+'\n');}
  await main();
} catch(error) {
  if(!smoke)writeFileSync(destination,JSON.stringify({status:'FAIL',generatedAt:new Date().toISOString(),independentVerifier:'bin/search/tests/whiston-corpus-qa.mjs',counts,totalQueries,assertions,failedAssertions:1,error:{name:error.name,message:error.message,stack:error.stack}},null,2)+'\n');
  console.error(error.stack || error.message);process.exitCode=1;
}
