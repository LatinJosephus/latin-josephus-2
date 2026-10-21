/** Independent acceptance for all seven Whiston Bellum books.
 * Source expectations use a separate minidom text-node witness and Unicode
 * category scanner. Query expectations use explicit Boolean trees, sequential
 * phrase scans, and a bounded wildcard matcher, without production parsing.
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
const usage = 'Usage: node bin/search/tests/whiston-bellum-corpus-qa.mjs [--smoke] [--root <repository>] [--expected-reader-sha256 <SHA-256>]';
for (let index = 0; index < args.length; index++) {
  if (args[index] === '--smoke') {assert.equal(smoke, false, usage); smoke = true;}
  else if (args[index] === '--root') {assert.ok(args[index + 1], usage); root = resolve(args[++index]);}
  else if (args[index] === '--expected-reader-sha256') {
    assert.ok(explicitReaderSHA === null && /^[a-f0-9]{64}$/i.test(args[index + 1] || ''), usage);
    explicitReaderSHA = args[++index].toLowerCase();
  } else assert.fail(usage);
}
const base = resolve(root, 'bin/search');
const collectionId = 'bellum-english-whiston';
const bookId = `${collectionId}:1`;
const expectedBooks = [1,2,3,4,5,6,7];
const expectedBookTotals = [
  {book:1,sections:673,tokens:50097},{book:2,sections:654,tokens:38098},
  {book:3,sections:542,tokens:24777},{book:4,sections:663,tokens:30489},
  {book:5,sections:572,tokens:29415},{book:6,sections:442,tokens:21949},
  {book:7,sections:455,tokens:20247},
];
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
  const romans = ['I','II','III','IV','V','VI','VII'];
  records.forEach((record,index) => {
    const row=expected[index], context={id:row.id};
    for(const field of ['id','book','section','order','text','sourcePath','sourceId','sourceIds'])
      check(`${category}Source${field}`,record[field],row[field],context);
    check(`${category}Version`,[record.work,record.language,record.edition],['bellum','English','Whiston'],context);
    check(`${category}Citation`,record.citation,{book:romans[row.book-1],section:row.section},context);
    check(`${category}ReaderLink`,record.readerLink,{path:'bellum-judaicum/',params:{book:row.book,niese:row.section,english:'whiston'}},context);
    const link=new URL(readerURL(record,'https://latinjosephus.github.io/'));
    check(`${category}ReaderURL`,[link.pathname,link.searchParams.get('book'),link.searchParams.get('niese'),link.searchParams.get('english')],
      ['/bellum-judaicum/',String(row.book),String(row.section),'whiston'],context);
    check(`${category}NoFalsePhraseBoundary`,Boolean(record.breakBefore),false,context);
    check(`${category}NoSeparateProem`,record.division??null,null,context);
    check(`${category}SuppliedMarks`,record.editorialMarks,row.editorial.map(({kind,start,end,text,sourceAttributes})=>
      ({kind,start,end,text,sourceTag:'supplied',sourceAttributes})),context);
    for(const field of ['sourceMarkup','textGaps','phraseBreaks']) check(`${category}NoInvented${field}`,record[field],[],context);
    check(`${category}IndependentTokenizers`,independentTokens(record.text),row.tokens,context);
  });
}

function inspectProjection(report,file,records,category) {
  check(`${category}ParagraphIDs`,report.paragraphs.map(p=>p.sourceId),file.paragraphs.map(p=>p.sourceId));
  const byId=new Map(records.map(record=>[record.id,record]));
  report.paragraphs.forEach((paragraph,index)=>{
    const expected=file.paragraphs[index],context={sourceId:expected.sourceId};
    check(`${category}SameAsIdentityKind`,paragraph.sourceIdentityKind,'sameAs',context);
    check(`${category}SourceAttributes`,paragraph.sourceAttributes,expected.sourceAttributes,context);
    check(`${category}RawParagraph`,paragraph.rawText,expected.rawText,context);
    let cursor=0, restored='';
    for(const piece of paragraph.sourcePieces) {
      check(`${category}SourceContinuity`,piece.sourceStart,cursor,context);
      const text=piece.kind==='record'?byId.get(piece.recordId).text.slice(piece.recordStart,piece.recordEnd):piece.text;
      check(`${category}SourceSlice`,text,expected.rawText.slice(piece.sourceStart,piece.sourceEnd),context);
      check(`${category}SourceSliceHash`,piece.textSHA256,hash(text),context);
      cursor=piece.sourceEnd;restored+=text;
    }
    check(`${category}FullRestoration`,restored,expected.rawText,context);
    check(`${category}RestorationLength`,cursor,expected.rawLength,context);
    check(`${category}RecordProjection`,paragraph.sourcePieces.filter(p=>p.kind==='record').map(p=>
      [p.recordId,p.sourceStart,p.sourceEnd,p.recordStart,p.recordEnd]),
      file.rows.filter(row=>row.sourceId===expected.sourceId).map(row=>[row.id,row.paragraphStart,row.paragraphEnd,0,row.text.length]),context);
    check(`${category}NieseMarkers`,paragraph.nieseMarkers.map(m=>[m.section,m.sourceTextOffset]),
      expected.nieseMarkers.map(m=>[m.section,m.rawOffset]),context);
    check(`${category}SectionIDs`,paragraph.sections.map(s=>s.section),expected.sections,context);
    check(`${category}EditorialSpans`,paragraph.editorialSpans,file.supplied.filter(m=>m.sourceId===expected.sourceId).map(m=>
      ({kind:m.kind,sourceStart:m.rawStart,sourceEnd:m.rawEnd,text:m.text,sourceAttributes:m.attributes})),context);
  });
  check(`${category}Tokens`,report.counts.runningWordTokens,file.evidence.tokens);
  check(`${category}Paragraphs`,report.paragraphs.length,file.evidence.paragraphs);
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
  const exported = exportConcordance(model,result,{catalog,exportedAt:'2026-10-21T12:00:00Z',searchURL:'https://latinjosephus.github.io/search/'});
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
      check(`${category}CSVEditorialEvidence`, segment.editorialMarks,
        source.editorial.filter(mark=>mark.start<segment.end&&mark.end>segment.start)
          .map(({kind,start,end,text,sourceAttributes})=>({kind,start,end,text,sourceTag:'supplied',sourceAttributes})));
    }
    if (row.row_type !== 'matching-unit') {
      check(`${category}CSVJoinedContext`, segments.map(segment => segment.joinBefore + segment.text).join(''), original.left + original.match + original.right);
      check(`${category}CSVExpectedHit`, expectedSpans.has(spanKey(JSON.parse(row.hit_spans_json))), true);
    }
  }
  // An English Bellum export must not inherit the Latin Antiquities omissions.
  check(`${category}CSVNoLatinCoverage`, csv.some(row => /Bamberg|IX\.51[–-]109.*absent|XII\.248/.test(row.editorial_notes || '')), false);
  const sources = JSON.parse(csv[0].selected_sources_json);
  check(`${category}CSVSelectedCollections`, sources.collections.map(c => c.id), [collectionId]);
  check(`${category}CSVSelectedBooks`, sources.books.map(b => b.id), [...new Set(oracle.rows.map(row => `${collectionId}:${row.book}`))]);
  check(`${category}CSVNormalizationMetadata`, sources.normalization,
    {caseSensitive:false,spellingEquivalence:'none',foldedCollectionIds:[],literalCollectionIds:[collectionId]});
  return {model,csv};
}


const fixtures = [
  ['"WHEREAS the war"',phrase(['WHEREAS','the','war'])],
  ['"WHEREAS, THE; WAR"',phrase(['WHEREAS','THE','WAR'])],
  ['"wher* the w*r"',phrase(['wher*','the','w*r'])],
  ['Jews',word('Jews')],['Judea',word('Judea')],['iudea',word('iudea')],['the',word('the')],
  ['Jews AND NOT Romans',and(word('Jews'),not(word('Romans')))],
  ['Jews OR Romans AND Jerusalem',or(word('Jews'),and(word('Romans'),word('Jerusalem')))],
  ['(Jews OR Romans) AND Jerusalem',and(or(word('Jews'),word('Romans')),word('Jerusalem'))],
  ['Jews Jerusalem',and(word('Jews'),word('Jerusalem'))],
  ['NOT (Jews OR NOT Romans)',not(or(word('Jews'),not(word('Romans'))))],
  ['NOT NOT Jews',not(not(word('Jews')))],['Jerusalem OR Jerus*',or(word('Jerusalem'),word('Jerus*'))],
  ['NOT zzzzwhistonabsent',not(word('zzzzwhistonabsent'))],['NOT *',not(word('*'))],
  ['zzzzwhistonabsent',word('zzzzwhistonabsent')],
];

async function main() {
  const witnessPath=preserve(resolve(base,'tests/whiston-bellum-source-witness.py'));
  const verifierPath=preserve(resolve(base,'tests/whiston-bellum-corpus-qa.mjs'));
  const readerPath=preserve(resolve(root,'assets/js/renderTei.js')),readerSHA=digest(readerPath);
  if(explicitReaderSHA)check('ExplicitReaderBaseline',readerSHA,explicitReaderSHA);
  const readerBaseline={expectedSha256:explicitReaderSHA||readerSHA,observedSha256:readerSHA,
    provenance:explicitReaderSHA?'explicit-argument':'observed-source-checkout',preservationDuringRunRequired:true,publicationInput:false};
  const catalogPath=preserve(resolve(base,'catalog.json')),catalog=readJSON(catalogPath);
  const config=catalog.collections.find(c=>c.id===collectionId);
  assert.ok(config,'Build Whiston Bellum and the combined catalog before running acceptance.');
  const entries=catalog.books.filter(entry=>entry.collectionId===collectionId);
  check('OnlyAcceptedBooksPublished',entries.map(entry=>entry.number),expectedBooks);
  check('CollectionIdentity',[config.work,config.language,config.edition],['bellum','English','Whiston']);
  const corpusPath=preserve(resolve(base,config.corpusPath)),extractionPath=preserve(resolve(base,config.extractionReportPath));
  const manifestPath=preserve(resolve(base,config.manifestPath));
  for(const p of ['engine.mjs','collection.mjs','concordance.mjs','ui-utils.mjs','extract-whiston-bellum.py','vendor/lunr.cjs'])preserve(resolve(base,p));
  const sourcePaths=Object.fromEntries(expectedBooks.map(book=>[book,preserve(resolve(root,`assets/xml/bellum/English/book-${String(book).padStart(2,'0')}.xml`))]));
  const witness=JSON.parse(execFileSync(process.env.SEARCH_PYTHON||process.env.PYTHON||'python3',[witnessPath,root],{encoding:'utf8',maxBuffer:128*1024*1024}));
  check('IndependentCollectionTotals',witness.totals,{books:7,sections:4001,tokens:215072});
  check('IndependentBookTotals',witness.bookTotals,expectedBookTotals);
  const corpus=readJSON(corpusPath),extraction=readJSON(extractionPath);
  inspectRecords(corpus,witness.rows,'Indexed');
  check('CollectionCorpusHash',config.corpusSHA256,digest(corpusPath));
  check('CollectionManifestHash',config.manifestSHA256,digest(manifestPath));
  check('ExtractionTokens',extraction.counts.runningWordTokens,215072);
  check('ExtractionSections',extraction.counts.sections,4001);
  check('ExtractionPublishedBooks',extraction.scope.books,expectedBooks);
  const oracle=makeOracle(witness.rows);
  const bookData=entries.map(entry=>{
    const suffix=String(entry.number).padStart(2,'0');
    const paths={bundle:preserve(resolve(base,entry.path)),corpus:preserve(resolve(base,entry.corpusPath)),
      extractionReport:preserve(resolve(base,'data',collectionId,`book-${suffix}.extraction-report.json`)),source:sourcePaths[entry.number]};
    const file=witness.indexedFiles.find(file=>file.evidence.book===entry.number),rows=file.rows;
    const records=readJSON(paths.corpus),bundle=readJSON(paths.bundle),report=readJSON(paths.extractionReport),tag=`Book${entry.number}`;
    check(`${tag}CorpusShard`,records,corpus.filter(record=>record.book===entry.number));
    inspectProjection(report,file,records,`${tag}Projection`);
    check(`${tag}BundleRecords`,bundle.records,records.map(record=>({...record,breakBefore:Boolean(record.breakBefore)})));
    check(`${tag}AllIndexedOffsets`,bundle.tokens,rows.map(row=>row.tokens));
    check(`${tag}BundleTokens`,bundle.stats.tokens,file.evidence.tokens);
    check(`${tag}CatalogBundleHash`,entry.sha256,digest(paths.bundle));
    check(`${tag}CatalogBundleBytes`,entry.bytes,readFileSync(paths.bundle).length);
    check(`${tag}CatalogCorpusHash`,entry.corpusSHA256,digest(paths.corpus));
    check(`${tag}CatalogTokens`,entry.tokens,file.evidence.tokens);
    check(`${tag}CatalogSections`,entry.sections,file.evidence.sections);
    return {entry,paths,rows,file,oracle:makeOracle(rows),engine:createEngine(bundle,lunr)};
  });
  for(const book of bookData) {
    const {rows,oracle:bookOracle,engine}=book;
    const vocabulary=smoke?bookOracle.vocabulary.filter((_,i)=>i%Math.max(1,Math.floor(bookOracle.vocabulary.length/20))===0):bookOracle.vocabulary;
    for(const term of vocabulary)verify(engine,bookOracle,word(term),'section','Vocabulary');
    for(const [query,tree] of fixtures)for(const scope of ['section','book'])verify(engine,bookOracle,tree,scope,'Fixture',query);
    const patterns=new Set(['*','**','Jew*','*Jews','J*ws','J**ews','Jerus*','*tion','*Jerus*','J*','*v*','*j*','zzzzwhistonabsent*']);
    const sampled=bookOracle.vocabulary.filter(term=>term.length>=5).filter((_,i)=>i%(smoke?400:90)===0);
    for(const term of sampled){patterns.add(term.slice(0,3)+'*');patterns.add('*'+term.slice(-3));patterns.add(term.slice(0,2)+'*'+term.slice(-2));}
    for(const pattern of patterns)for(const scope of ['section','book'])verify(engine,bookOracle,word(pattern),scope,'Wildcard');
    for(let index=0;index<rows.length;index++) {
      if(smoke&&![0,29,30,207,208,300,rows.length-1].includes(index))continue;
      const row=rows[index],middle=Math.max(0,Math.floor(row.tokens.length/2)-1);
      const tree=phrase(row.tokens.slice(middle,middle+3).map(token=>token.term));
      for(const scope of ['section','book'])verify(engine,bookOracle,tree,scope,'WithinEveryInterval');
    }
    for(let index=0;index<rows.length-1;index++) {
      if(smoke&&![0,28,29,30,206,207,208,299,rows.length-2].includes(index))continue;
      const tree=phrase([...rows[index].tokens.slice(-2),...rows[index+1].tokens.slice(0,2)].map(token=>token.term));
      for(const scope of ['section','book'])verify(engine,bookOracle,tree,scope,'EveryCitationSeam');
    }
  }
  const loaded=new Set();
  const collection=createCollection(catalog,lunr,{baseURL:'https://whiston.invalid/search/',fetchImpl:async url=>{
    const p=new URL(url).pathname.replace(/^\/search\//,'');assert.ok(catalog.books.some(book=>book.path===p));loaded.add(p);
    return new Response(readFileSync(preserve(resolve(base,p))),{status:200});
  }});
  async function selectedSearch(tree,scope,fold=false,category='Collection',query=print(tree),bookNumbers=expectedBooks) {
    totalQueries++;counts[`${category}Queries`]=(counts[`${category}Queries`]||0)+1;
    const selected=bookData.filter(book=>bookNumbers.includes(book.entry.number));
    const selectedOracle=selected.length===7?oracle:selected.length===1?selected[0].oracle:makeOracle(selected.flatMap(book=>book.rows));
    const result=await collection.search(query,{collections:[collectionId],books:selected.map(book=>book.entry.id),scope,fold});
    compare(result,selectedOracle.evaluate(tree,scope),selectedOracle,scope,category,query);
    check(`${category}SelectedBooks`,result.selectedBooks,selected.map(book=>book.entry.id));
    check(`${category}EnglishNeverFolds`,result.fold,false);
    check(`${category}NormalizationMetadata`,result.normalization,
      {caseSensitive:false,spellingEquivalence:'none',foldedCollectionIds:[],literalCollectionIds:[collectionId]});
    return result;
  }
  for(const query of ['Judea','iudea','Jews','iews','live','liue'])for(const fold of [false,true])
    await selectedSearch(word(query),'section',fold,'EnglishLiteral',query,[1]);
  check('LoaderInitiallyOnlyBookI',[...loaded],[bookData[0].entry.path]);
  for(const book of bookData) {
    for(const [label,index] of [['opening',0],['ending',book.rows.length-1]]) {
      const tree=phrase(book.rows[index].tokens.slice(0,6).map(t=>t.term));
      const result=await selectedSearch(tree,'section',false,'PublishedBookEdges',print(tree),[book.entry.number]);
      check('PublishedBookEdgeIdentity',result.hitGroups.some(group=>group.recordIds.includes(book.rows[index].id)),true,{book:book.entry.number,label});
      validateConcordance(result,book.oracle,book.oracle.evaluate(tree,'section'),tree,catalog,'PublishedBookEdgeCSV');
    }
    for(const boundary of book.file.chapters.slice(1)) {
      const i=book.rows.findIndex(row=>row.section===boundary.sections[0]);
      const tree=phrase([...book.rows[i-1].tokens.slice(-2),...book.rows[i].tokens.slice(0,2)].map(t=>t.term));
      const result=await selectedSearch(tree,'book',false,'PublishedChapterSeam',print(tree),[book.entry.number]);
      check('ChapterSeamOccurs',result.hitGroups.some(group=>group.hits.some(hit=>hit.spans.some(span=>span.recordId===book.rows[i].id))),true);
    }
  }
  const first=bookData[0],prefaceSeam=phrase([...first.rows[29].tokens.slice(-3),...first.rows[30].tokens.slice(0,3)].map(t=>t.term));
  for(const scope of ['section','book']) {
    const result=await selectedSearch(prefaceSeam,scope,false,'EmbeddedPrefaceSeam',print(prefaceSeam),[1]);
    check('EmbeddedPrefaceContinuity',result.occurrences,scope==='book'?1:0);
    validateConcordance(result,first.oracle,first.oracle.evaluate(prefaceSeam,scope),prefaceSeam,catalog,'PrefaceSeamCSV');
  }
  const suppliedBook=bookData[6],supplied208=suppliedBook.rows[207],supplied209=suppliedBook.rows[208];
  check('SuppliedClippedOffsets',[...supplied208.editorial,...supplied209.editorial].map(m=>[m.start,m.end]),[[157,262],[0,154]]);
  const suppliedCases=[phrase(['they','were','slain']),phrase(['one','thousand','seven','hundred']),
    phrase(['but','as','Bassus','thought']),phrase(['made','slaves','but','as','Bassus'])];
  for(const tree of suppliedCases)for(const scope of ['section','book']) {
    const result=await selectedSearch(tree,scope,false,'SuppliedText',print(tree),[7]);
    const exported=validateConcordance(result,suppliedBook.oracle,suppliedBook.oracle.evaluate(tree,scope),tree,catalog,'SuppliedCSV');
    const relevantRows=exported.csv.filter(row=>row.row_type!=='search-summary'&&JSON.parse(row.hit_spans_json).some(span=>
      [supplied208.id,supplied209.id].includes(span.recordId)));
    if(result.occurrences)check('SuppliedCSVRelevantHitPresent',relevantRows.length>0,true);
    for(const row of relevantRows) {
      const segments=JSON.parse(row.source_segments_json);
      const marks=segments.flatMap(segment=>segment.editorialMarks||[]);
      check('SuppliedCSVMarkPresent',marks.some(mark=>mark.kind==='supplied'),true);
      check('SuppliedCSVExactAttributes',marks.filter(mark=>mark.kind==='supplied').every(mark=>
        mark.sourceAttributes.reason==='omitted'&&mark.sourceAttributes.source==='https://lexundria.com/j_bj/7.208-7.209/wst'),true);
      check('SuppliedCSVReadableBrackets',row.matched_text_editorial.includes('['),true);
      check('SuppliedCSVLiteralNoInventedBrackets',row.matched_text.includes('['),false);
    }
  }
  const example=phrase(['a','voice','from','the','east']);
  for(const scope of ['section','book']) {
    const result=await selectedSearch(example,scope,false,'PublishedVIExample');
    check('VIExampleUnique',result.occurrences,1);
    check('VIExampleIdentity',result.hitGroups.map(g=>g.recordIds),[[`${collectionId}-6-301`]]);
    validateConcordance(result,oracle,oracle.evaluate(example,scope),example,catalog,'VIExampleCSV');
    noteExample(print(example),scope,result,'Whiston Bellum VI example');
  }
  for(const tree of [word('Jews'),word('the'),not(word('zzzzwhistonabsent')),not(word('*')),word('zzzzwhistonabsent'),
                    and(word('Jews'),not(word('Romans'))),or(word('Jerusalem'),word('Jerus*'))]) {
    for(const scope of ['section','book']) {
      const result=await selectedSearch(tree,scope,true,'CompleteEnglish');
      validateConcordance(result,oracle,oracle.evaluate(tree,scope),tree,catalog,'CompleteEnglishCSV');
      if(tree.op==='leaf'&&['Jews','the'].includes(tree.patterns[0]))noteExample(print(tree),scope,result,'Complete Bellum count');
    }
  }
  for(let book=1;book<7;book++) {
    const left=bookData[book-1].rows.at(-1),right=bookData[book].rows[0];
    const tree=phrase([...left.tokens.slice(-4),...right.tokens.slice(0,4)].map(t=>t.term));
    const result=await selectedSearch(tree,'book',false,'NoCrossBookPhrase');
    check('EachBookBoundaryStopsPhrase',result.occurrences,0,{book});
  }
  check('LoaderExactlyBellumBooks',[...loaded].sort(),entries.map(entry=>entry.path).sort());
  const latinId='bellum-latin-cardwell',latinBook=`${latinId}:1`;
  for(const query of ['Judea','iudea','Jews','iews']) {
    const result=await collection.search(query,{collections:[latinId,collectionId],books:[latinBook,bookId],scope:'section',fold:true});totalQueries++;
    const groups=result.hitGroups.filter(g=>g.collectionId===collectionId);
    compare({...result,hitGroups:groups,matchingUnits:groups.length,occurrences:groups.reduce((n,g)=>n+g.hits.length,0),
      matchingSections:new Set(groups.flatMap(g=>g.recordIds)).size},first.oracle.evaluate(word(query),'section'),first.oracle,'section','MixedEnglishLiteral',query);
    check('MixedNormalization',result.normalization,{caseSensitive:false,spellingEquivalence:'latin-uv-ij',foldedCollectionIds:[latinId],literalCollectionIds:[collectionId]});
  }
  const noLanguageBridge=await collection.search('God AND deus',{collections:[latinId,collectionId],books:[latinBook,bookId],scope:'book',fold:false});totalQueries++;
  check('NoCrossLanguageBoolean',noLanguageBridge.matchingUnits,0);
  const antiquitiesId='antiquities-english-whiston',antiquitiesBook=`${antiquitiesId}:1`;
  const twoWorks=await collection.search('God',{collections:[antiquitiesId,collectionId],books:[antiquitiesBook,bookId],scope:'book',fold:true});totalQueries++;
  check('TwoEnglishWorksBothDiscoverable',twoWorks.matchingBooks,[antiquitiesBook,bookId]);
  check('TwoEnglishWorksNormalization',twoWorks.normalization,{caseSensitive:false,spellingEquivalence:'none',foldedCollectionIds:[],literalCollectionIds:[antiquitiesId,collectionId]});
  const twoModel=buildConcordance(twoWorks,twoWorks.records,{readerBase:'https://latinjosephus.github.io/'});
  const twoCSV=parseCSV(exportConcordance(twoModel,twoWorks,{catalog,exportedAt:'2026-10-21T12:00:00Z'}).text);
  check('TwoEnglishWorksDistinctCSV',[...new Set(twoCSV.map(r=>r.collection_id))],[antiquitiesId,collectionId]);
  for(const row of twoCSV)check('TwoEnglishWorksCorrectReaderPath',new URL(row.reader_url).pathname,
    row.collection_id===collectionId?'/bellum-judaicum/':'/antiquities/');
  const workIsolation=await collection.search('"in the beginning God created" AND "whereas the war"',
    {collections:[antiquitiesId,collectionId],books:[antiquitiesBook,bookId],scope:'book',fold:false});totalQueries++;
  check('NoCrossWorkBoolean',workIsolation.matchingUnits,0);
  for(const [p,before] of checkedFiles)check('InputUnchangedDuringRun',digest(p),before,{path:relative(root,p)});
  const report={status:'PASS',generatedAt:new Date().toISOString(),independentVerifier:'bin/search/tests/whiston-bellum-corpus-qa.mjs',readerBaseline,
    runtime:{node:process.version,...witness.runtime},source:{...witness.totals,uniqueLiteralVocabulary:oracle.vocabulary.length,bookTotals:witness.bookTotals},
    sources:witness.sources,testSources:[],sourceCases:{embeddedPreface:{book:1,sections:[1,30],continuousWith:31},
      supplied: [supplied208,supplied209].map(({section,text,editorial})=>({book:7,section,text,editorial})),
      untypedChapter:{book:5,chapter:13,attributes:witness.indexedFiles[4].chapters.at(-1).attributes}},
    verifiedFiles:{corpus:evidence(corpusPath),catalog:evidence(catalogPath),engine:evidence(resolve(base,'engine.mjs')),
      collection:evidence(resolve(base,'collection.mjs')),concordance:evidence(resolve(base,'concordance.mjs')),uiUtils:evidence(resolve(base,'ui-utils.mjs')),
      verifier:evidence(verifierPath),witness:evidence(witnessPath),extractor:evidence(resolve(base,'extract-whiston-bellum.py')),manifest:evidence(manifestPath),
      lunr:evidence(resolve(base,'vendor/lunr.cjs')),extractionReport:evidence(extractionPath),originalReader:evidence(readerPath),testSources:[],
      books:bookData.map(book=>({book:book.entry.number,bundle:evidence(book.paths.bundle),corpus:evidence(book.paths.corpus),
        source:evidence(book.paths.source),extractionReport:evidence(book.paths.extractionReport)}))},
    method:{source:'Independent minidom text-node projection from seven SHA-pinned canonical XML files. All 704 paragraphs are restored exactly and every source-to-record slice is compared. Paragraph sameAs identities remain literal source anchors. The single supplied element spans VII.208–209 and its nested 209 milestone; original text, exact clipped UTF-16 offsets and attributes are retained. Book V chapter 13 keeps its absent type attribute. All 4,001 Niese units follow source order.',
      tokens:'Every serialized token and original UTF-16 offset is compared with independent Python Unicode-category and JavaScript character scanners.',
      queries:'All literal vocabulary per book, one exact phrase per section, every neighboring section seam, every chapter seam, all six book boundaries, bounded wildcards and explicit Boolean trees. Embedded I.1–30 continues into 31 in whole-book scope. Supplied text does not create a false gap.',
      language:'English spelling remains literal with Latin-only equivalence. Separate English Antiquities and Bellum book identities prevent cross-work Boolean matches and retain distinct reader paths.',
      exports:'Exact concordance geometry, source slices, editorial marks, ordinary and negative-only CSV exports, all selected books and reader parameters.'},
    counts,totalQueries,assertions,failedAssertions:0,examples,durationSeconds:Math.round((performance.now()-started)/100)/10,
    limitations:['This validates the accepted Whiston Bellum XML, not a new translation or printed-edition collation.','Browser interaction is verified separately.'],failures:[]};
  if(!smoke)writeFileSync(destination,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({status:smoke?'DEVELOPMENT_SMOKE_PASS':'PASS',source:report.source,totalQueries,assertions,
    durationSeconds:report.durationSeconds,report:smoke?null:relative(root,destination)},null,2));
}
try {
  if(!smoke){mkdirSync(dirname(destination),{recursive:true});writeFileSync(destination,JSON.stringify({status:'RUNNING',startedAt:new Date().toISOString(),independentVerifier:'bin/search/tests/whiston-bellum-corpus-qa.mjs'})+'\n');}
  await main();
} catch(error) {
  if(!smoke)writeFileSync(destination,JSON.stringify({status:'FAIL',generatedAt:new Date().toISOString(),independentVerifier:'bin/search/tests/whiston-bellum-corpus-qa.mjs',counts,totalQueries,assertions,failedAssertions:1,error:{name:error.name,message:error.message,stack:error.stack}},null,2)+'\n');
  console.error(error.stack||error.message);process.exitCode=1;
}
