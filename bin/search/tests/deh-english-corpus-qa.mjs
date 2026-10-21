/** Independent acceptance for all five Pollard English De excidio books.
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
const usage = 'Usage: node bin/search/tests/deh-english-corpus-qa.mjs [--smoke] [--root <repository>] [--expected-reader-sha256 <SHA-256>]';
for (let index = 0; index < args.length; index++) {
  if (args[index] === '--smoke') {assert.equal(smoke, false, usage); smoke = true;}
  else if (args[index] === '--root') {assert.ok(args[index + 1], usage); root = resolve(args[++index]);}
  else if (args[index] === '--expected-reader-sha256') {
    assert.ok(explicitReaderSHA === null && /^[a-f0-9]{64}$/i.test(args[index + 1] || ''), usage);
    explicitReaderSHA = args[++index].toLowerCase();
  } else assert.fail(usage);
}
const base = resolve(root, 'bin/search');
const collectionId = 'deh-english-pollard';
const bookId = `${collectionId}:1`;
const expectedBooks = [1,2,3,4,5];
const expectedBookTotals = [
  {book:1,sections:215,tokens:40796},{book:2,sections:73,tokens:17141},
  {book:3,sections:70,tokens:18640},{book:4,sections:79,tokens:17263},{book:5,sections:121,tokens:42204},
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
      const expanded = {...token, recordId: row.id, book: row.book, segment: row.prologue ? 'prologue' : 'narrative'};
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

function expectedLink(row, wholeBook=false) {
  return ['/deh/', String(row.book), wholeBook ? null : String(row.chapter),
    wholeBook ? null : String(row.paragraph), 'pollard', null];
}
function linkParts(value) {
  const link=new URL(value);
  return [link.pathname,link.searchParams.get('book'),link.searchParams.get('chapter'),
    link.searchParams.get('unit'),link.searchParams.get('english'),link.searchParams.get('niese')];
}
function inspectRecords(records, expected, category) {
  check(`${category}RecordCount`, records.length, expected.length);
  const romans=['I','II','III','IV','V'];
  records.forEach((record,index)=>{
    const row=expected[index],context={id:row.id};
    for(const field of ['id','book','section','order','text','sourcePath','sourceId','sourceIds',
      'sourceSameAs','chapter','paragraph','citationLabel'])check(`${category}Source${field}`,record[field],row[field],context);
    check(`${category}Version`,[record.work,record.language,record.edition],['deh','English','Pollard v1.0'],context);
    check(`${category}CitationScheme`,record.citationScheme,'chapter-paragraph',context);
    check(`${category}Citation`,record.citation,{book:romans[row.book-1],chapter:row.chapter,
      paragraph:row.paragraph,prologue:row.prologue},context);
    check(`${category}ReaderLink`,record.readerLink,{path:'deh/',params:{book:row.book,chapter:row.chapter,unit:row.paragraph,english:'pollard'}},context);
    check(`${category}ReaderURL`,linkParts(readerURL(record,'https://latinjosephus.github.io/')),expectedLink(row),context);
    check(`${category}OriginalURL`,linkParts(new URL(record.url,'https://latinjosephus.github.io/')),expectedLink(row),context);
    check(`${category}PrologueBoundaryOnly`,Boolean(record.breakBefore),row.breakBefore,context);
    check(`${category}NoSeparateProem`,record.division??null,null,context);
    check(`${category}NoInventedEditorialMarks`,record.editorialMarks,[],context);
    check(`${category}CanonicalXMLIdentity`,record.sourceIdentityKind,'xml:id',context);
    for(const field of ['sourceMarkup','textGaps','phraseBreaks'])check(`${category}NoInvented${field}`,record[field],[],context);
    check(`${category}IndependentTokenizers`,independentTokens(record.text),row.tokens,context);
  });
}
function inspectProjection(report,file,records,category) {
  check(`${category}ParagraphIDs`,report.paragraphs.map(p=>p.sourceId),file.paragraphs.map(p=>p.sourceId));
  const byId=new Map(records.map(record=>[record.id,record]));
  report.paragraphs.forEach((paragraph,index)=>{
    const expected=file.paragraphs[index],row=file.rows[index],context={sourceId:expected.sourceId};
    for(const field of ['sourceId','sourceIdentityKind','sourcePath','sourceAttributes','bookAttributes','chapterAttributes',
      'paragraphOrdinal','chapter','paragraph','citationLabel','rawText','runningText','removedPrefix'])
      check(`${category}Source${field}`,paragraph[field],expected[field],context);
    let cursor=0,restored='';
    for(const piece of paragraph.sourcePieces) {
      check(`${category}SourceContinuity`,piece.sourceStart,cursor,context);
      const text=piece.kind==='record'?byId.get(piece.recordId).text.slice(piece.recordStart,piece.recordEnd):piece.text;
      check(`${category}SourceSlice`,text,expected.rawText.slice(piece.sourceStart,piece.sourceEnd),context);
      check(`${category}SourceSliceHash`,piece.textSHA256,hash(text),context);
      if(piece.kind!=='record') {
        check(`${category}ExcludedPieceKind`,piece.kind,'excluded',context);
        if(piece.reason==='citation-label-and-preceding-whitespace')check(`${category}ExcludedPrefix`,text,expected.removedPrefix,context);
        else check(`${category}ExcludedWhitespace`,text.trim(),'',context);
      }
      cursor=piece.sourceEnd;restored+=text;
    }
    check(`${category}FullRestoration`,restored,expected.rawText,context);
    check(`${category}RestorationLength`,cursor,expected.rawLength,context);
    check(`${category}RecordProjection`,paragraph.sourcePieces.filter(p=>p.kind==='record').map(p=>
      [p.recordId,p.sourceStart,p.sourceEnd,p.recordStart,p.recordEnd]),
      [[row.id,row.paragraphStart,row.paragraphEnd,0,row.text.length]],context);
    check(`${category}SectionIDs`,paragraph.sections.map(s=>s.section),expected.sections,context);
    check(`${category}SectionSlices`,paragraph.sections.map(s=>[s.recordId,s.textStart,s.textEnd,s.leadingWhitespace,s.trailingWhitespace]),
      [[row.id,row.paragraphStart,row.paragraphEnd,expected.leadingWhitespace,expected.trailingWhitespace]],context);
    check(`${category}NoInventedEditorialSpans`,paragraph.editorialSpans,[],context);
    check(`${category}NoInventedStructuralMarkers`,paragraph.structuralMarkers,[],context);
    check(`${category}RestorationClaim`,paragraph.exactRestorationVerified,true,context);
  });
  check(`${category}ExcludedBlocks`,report.excludedBlocks.map(block=>({kind:block.kind==='release-note'?'body-note':block.kind,
    textSHA256:block.textSHA256,...(block.chapter===undefined?{}:{chapter:block.chapter})})),
    file.exclusions.map(({kind,textSHA256,chapter})=>({kind,textSHA256,...(chapter===undefined?{}:{chapter})})));
  check(`${category}Tokens`,report.counts.runningWordTokens,file.evidence.tokens);
  check(`${category}Paragraphs`,report.paragraphs.length,file.evidence.paragraphs);
  check(`${category}Chapters`,report.counts.chapterDivisionsIncludingPrologue,file.evidence.chapters);
  check(`${category}PrologueUnits`,report.counts.prologueUnits,file.evidence.prologueUnits);
  check(`${category}ExcludedLabels`,report.counts.excludedCitationLabels,file.evidence.paragraphs);
  check(`${category}ExcludedHeads`,report.counts.excludedHeadings,file.evidence.excludedHeadings);
  check(`${category}ExcludedNotes`,report.counts.excludedReleaseNotes,1);
  check(`${category}RawSequenceHash`,report.coverage.rawParagraphSequenceSha256,hash(file.paragraphs.map(p=>p.rawText).join('\n')));
  check(`${category}RestoredSequenceHash`,report.coverage.restoredParagraphSequenceSha256,hash(file.paragraphs.map(p=>p.rawText).join('\n')));
}

function validateConcordance(result,oracle,expected,tree,catalog,category='Concordance') {
  const model=buildConcordance(result,result.records,{readerBase:'https://latinjosephus.github.io/'});
  const expectedSpans=new Set([...expected.values()].flatMap(set=>[...set]));
  check(`${category}Geometries`,model.rows.map(row=>spanKey(row.spans)).sort(),[...expectedSpans].sort());
  check(`${category}NegativeUnits`,model.unhighlightedUnits.length,[...expected.values()].filter(set=>!set.size).length);
  check(`${category}CountKind`,model.countKind,tree.op==='leaf'?tree.phrase?'phrase':'word':'evidence');
  check(`${category}OccurrenceCount`,model.occurrenceCount,tree.op==='leaf'?expectedSpans.size:null);
  for(const row of model.unhighlightedUnits) {
    const first=oracle.byId.get(row.records[0].id);
    check(`${category}NegativeReader`,linkParts(row.readerURL),expectedLink(first,result.scope==='book'));
  }
  for(const row of model.rows) {
    const spans=row.spans;
    const match=spans.map((span,index)=>{
      const source=oracle.byId.get(span.recordId).text;
      return source.slice(index?0:span.start,index===spans.length-1?span.end:source.length);
    }).join(' ');
    check(`${category}OriginalMatchedText`,row.match,match,{spans});
    check(`${category}Edition`,[row.language,row.edition,row.collectionId],['English','Pollard v1.0',collectionId]);
    const first=oracle.byId.get(spans[0].recordId);
    check(`${category}PassageReader`,linkParts(row.readerURL),expectedLink(first));
  }
  const exported=exportConcordance(model,result,{catalog,exportedAt:'2026-10-21T16:00:00Z',searchURL:'https://latinjosephus.github.io/search/'});
  const csv=parseCSV(exported.text);
  check(`${category}CSVRowCount`,exported.rowCount,model.rows.length+model.unhighlightedUnits.length);
  check(`${category}CSVTotalRows`,csv.length,Math.max(1,exported.rowCount));
  for(const row of csv) {
    check(`${category}CSVQuery`,row.query,result.query);
    check(`${category}CSVQueryJSON`,JSON.parse(row.query_json),result.query);
    check(`${category}CSVScope`,row.scope,result.scope);
    check(`${category}CSVEnglishNormalization`,row.spelling_equivalence,'original spelling');
    if(row.row_type==='search-summary')continue;
    check(`${category}CSVVersion`,[row.language,row.edition,row.collection_id],['English','Pollard v1.0',collectionId]);
    const original=JSON.parse(row.original_context_json),segments=JSON.parse(row.source_segments_json);
    check(`${category}CSVOriginalContext`,original,{left:row.left_context,match:row.matched_text,right:row.right_context});
    for(const segment of segments) {
      const source=oracle.byId.get(segment.recordId);
      check(`${category}CSVSourceSegment`,segment.text,source.text.slice(segment.start,segment.end));
      check(`${category}CSVSourcePath`,segment.sourcePath,source.sourcePath);
      check(`${category}CSVSourceIDs`,[segment.sourceId,segment.sourceIds],[source.sourceId,source.sourceIds]);
      check(`${category}CSVLatinAlignment`,segment.sourceSameAs,source.sourceSameAs);
      check(`${category}CSVCitation`,[segment.citationScheme,segment.chapter,segment.paragraph,segment.citationLabel],
        ['chapter-paragraph',source.chapter,source.paragraph,source.citationLabel]);
      check(`${category}CSVNoInventedEditorialMarks`,segment.editorialMarks,[]);
    }
    if(row.row_type!=='matching-unit') {
      check(`${category}CSVJoinedContext`,segments.map(segment=>segment.joinBefore+segment.text).join(''),original.left+original.match+original.right);
      check(`${category}CSVExpectedHit`,expectedSpans.has(spanKey(JSON.parse(row.hit_spans_json))),true);
    }
  }
  check(`${category}CSVNoLatinEditorialPolicy`,csv.some(row=>/Bamberg|IX\.51[–-]109.*absent|bold green|asterisk-marked interruptions|\[supplied\]|⟦deleted⟧|generated.*dagger/i.test(row.editorial_notes||'')),false);
  const sources=JSON.parse(csv[0].selected_sources_json);
  check(`${category}CSVSelectedCollections`,sources.collections.map(c=>c.id),[collectionId]);
  check(`${category}CSVSelectedBooks`,sources.books.map(b=>b.id),[...new Set(oracle.rows.map(row=>`${collectionId}:${row.book}`))]);
  check(`${category}CSVNormalizationMetadata`,sources.normalization,
    {caseSensitive:false,spellingEquivalence:'none',foldedCollectionIds:[],literalCollectionIds:[collectionId]});
  return {model,csv};
}

const fixtures=[
  ['"A ROSE among thorns"',phrase(['A','ROSE','among','thorns'])],
  ['"A, ROSE; AMONG THORNS"',phrase(['A','ROSE','AMONG','THORNS'])],
  ['"a ros* among thorn*"',phrase(['a','ros*','among','thorn*'])],
  ['Jews',word('Jews')],['Judaea',word('Judaea')],['iudaea',word('iudaea')],['the',word('the')],
  ['Jews AND NOT Romans',and(word('Jews'),not(word('Romans')))],
  ['Jews OR Romans AND Jerusalem',or(word('Jews'),and(word('Romans'),word('Jerusalem')))],
  ['(Jews OR Romans) AND Jerusalem',and(or(word('Jews'),word('Romans')),word('Jerusalem'))],
  ['Jews Jerusalem',and(word('Jews'),word('Jerusalem'))],
  ['NOT (Jews OR NOT Romans)',not(or(word('Jews'),not(word('Romans'))))],
  ['NOT NOT Jews',not(not(word('Jews')))],['Jerusalem OR Jerus*',or(word('Jerusalem'),word('Jerus*'))],
  ['NOT zzzzpollardabsent',not(word('zzzzpollardabsent'))],['NOT *',not(word('*'))],
  ['zzzzpollardabsent',word('zzzzpollardabsent')],
];

async function main() {
  const witnessPath=preserve(resolve(base,'tests/deh-english-source-witness.py'));
  const verifierPath=preserve(resolve(base,'tests/deh-english-corpus-qa.mjs'));
  const readerPath=preserve(resolve(root,'assets/js/renderTei.js')),readerSHA=digest(readerPath);
  if(explicitReaderSHA)check('ExplicitReaderBaseline',readerSHA,explicitReaderSHA);
  const readerBaseline={expectedSha256:explicitReaderSHA||readerSHA,observedSha256:readerSHA,
    provenance:explicitReaderSHA?'explicit-argument':'observed-source-checkout',preservationDuringRunRequired:true,publicationInput:false};
  const catalogPath=preserve(resolve(base,'catalog.json')),catalog=readJSON(catalogPath);
  const config=catalog.collections.find(c=>c.id===collectionId);
  assert.ok(config,'Build Pollard English De excidio and the combined catalog before running acceptance.');
  const entries=catalog.books.filter(entry=>entry.collectionId===collectionId);
  check('OnlyAcceptedBooksPublished',entries.map(entry=>entry.number),expectedBooks);
  check('CollectionIdentity',[config.work,config.language,config.edition],['deh','English','Pollard v1.0']);
  const corpusPath=preserve(resolve(base,config.corpusPath)),extractionPath=preserve(resolve(base,config.extractionReportPath));
  const manifestPath=preserve(resolve(base,config.manifestPath));
  for(const p of ['engine.mjs','collection.mjs','concordance.mjs','ui-utils.mjs','extract-deh-english.py','vendor/lunr.cjs'])preserve(resolve(base,p));
  const sourcePaths=Object.fromEntries(expectedBooks.map(book=>[book,preserve(resolve(root,`assets/xml/deh/English/book-${String(book).padStart(2,'0')}.xml`))]));
  const latinPaths=expectedBooks.map(book=>preserve(resolve(root,`assets/xml/deh/Latin/book-${String(book).padStart(2,'0')}.xml`)));
  const witness=JSON.parse(execFileSync(process.env.SEARCH_PYTHON||process.env.PYTHON||'python3',[witnessPath,root],{encoding:'utf8',maxBuffer:128*1024*1024}));
  check('IndependentCollectionTotals',witness.totals,{books:5,sections:558,tokens:136044});
  check('IndependentBookTotals',witness.bookTotals,expectedBookTotals);
  check('IndependentLatinAlignmentInputs',witness.testSources.map(item=>item.path),latinPaths.map(path=>relative(root,path).replaceAll('\\','/')));
  const corpus=readJSON(corpusPath),extraction=readJSON(extractionPath);
  inspectRecords(corpus,witness.rows,'Indexed');
  check('CollectionCorpusHash',config.corpusSHA256,digest(corpusPath));
  check('CollectionManifestHash',config.manifestSHA256,digest(manifestPath));
  check('ExtractionTokens',extraction.counts.runningWordTokens,136044);
  check('ExtractionSections',extraction.counts.sections,558);
  check('ExtractionPublishedBooks',extraction.scope.books,expectedBooks);
  check('NoRunningCitationLabelTokens',witness.rows.some(row=>/^\[/.test(row.text)),false);
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
    const patterns=new Set(['*','**','Jew*','*Jews','J*ws','J**ews','Jerus*','*tion','*Jerus*','J*','*v*','*j*','zzzzpollardabsent*']);
    const sampled=bookOracle.vocabulary.filter(term=>term.length>=5).filter((_,i)=>i%(smoke?500:110)===0);
    for(const term of sampled){patterns.add(term.slice(0,3)+'*');patterns.add('*'+term.slice(-3));patterns.add(term.slice(0,2)+'*'+term.slice(-2));}
    for(const pattern of patterns)for(const scope of ['section','book'])verify(engine,bookOracle,word(pattern),scope,'Wildcard');
    for(let index=0;index<rows.length;index++) {
      if(smoke&&![0,1,2,3,rows.length-1].includes(index))continue;
      const row=rows[index],middle=Math.max(0,Math.floor(row.tokens.length/2)-1);
      const tree=phrase(row.tokens.slice(middle,middle+3).map(token=>token.term));
      for(const scope of ['section','book'])verify(engine,bookOracle,tree,scope,'WithinEveryUnit');
    }
    for(let index=0;index<rows.length-1;index++) {
      if(smoke&&![0,1,2,3,rows.length-2].includes(index))continue;
      const tree=phrase([...rows[index].tokens.slice(-2),...rows[index+1].tokens.slice(0,2)].map(token=>token.term));
      for(const scope of ['section','book'])verify(engine,bookOracle,tree,scope,'EveryCitationSeam');
    }
  }
  const loaded=new Set();
  const collection=createCollection(catalog,lunr,{baseURL:'https://pollard.invalid/search/',fetchImpl:async url=>{
    const p=new URL(url).pathname.replace(/^\/search\//,'');assert.ok(catalog.books.some(book=>book.path===p));loaded.add(p);
    return new Response(readFileSync(preserve(resolve(base,p))),{status:200});
  }});
  async function selectedSearch(tree,scope,fold=false,category='Collection',query=print(tree),bookNumbers=expectedBooks) {
    totalQueries++;counts[`${category}Queries`]=(counts[`${category}Queries`]||0)+1;
    const selected=bookData.filter(book=>bookNumbers.includes(book.entry.number));
    const selectedOracle=selected.length===expectedBooks.length?oracle:selected.length===1?selected[0].oracle:makeOracle(selected.flatMap(book=>book.rows));
    const result=await collection.search(query,{collections:[collectionId],books:selected.map(book=>book.entry.id),scope,fold});
    compare(result,selectedOracle.evaluate(tree,scope),selectedOracle,scope,category,query);
    check(`${category}SelectedBooks`,result.selectedBooks,selected.map(book=>book.entry.id));
    check(`${category}EnglishNeverFolds`,result.fold,false);
    check(`${category}NormalizationMetadata`,result.normalization,
      {caseSensitive:false,spellingEquivalence:'none',foldedCollectionIds:[],literalCollectionIds:[collectionId]});
    return result;
  }
  for(const query of ['Judaea','iudaea','Jews','iews','live','liue'])for(const fold of [false,true])
    await selectedSearch(word(query),'section',fold,'EnglishLiteral',query,[1]);
  check('LoaderInitiallyOnlyBookI',[...loaded],[bookData[0].entry.path]);
  for(const book of bookData) {
    for(const [label,index] of [['opening',0],['ending',book.rows.length-1]]) {
      const tree=phrase(book.rows[index].tokens.slice(0,8).map(t=>t.term));
      const result=await selectedSearch(tree,'section',false,'PublishedBookEdges',print(tree),[book.entry.number]);
      check('PublishedBookEdgeIdentity',result.hitGroups.some(group=>group.recordIds.includes(book.rows[index].id)),true,{book:book.entry.number,label});
      validateConcordance(result,book.oracle,book.oracle.evaluate(tree,'section'),tree,catalog,'PublishedBookEdgeCSV');
    }
    for(const boundary of book.file.chapters.slice(1)) {
      const i=book.rows.findIndex(row=>row.section===boundary.sections[0]);
      const tree=phrase([...book.rows[i-1].tokens.slice(-3),...book.rows[i].tokens.slice(0,3)].map(t=>t.term));
      const result=await selectedSearch(tree,'book',false,'PublishedChapterSeam',print(tree),[book.entry.number]);
      check('ChapterSeamRespectsPrologueBoundary',result.hitGroups.some(group=>group.hits.some(hit=>hit.spans.length>1
        &&hit.spans.some(span=>span.recordId===book.rows[i].id))),!book.rows[i].breakBefore,{book:book.entry.number,chapter:boundary.chapter});
    }
  }
  const first=bookData[0],example=phrase(['a','rose','among','thorns']);
  for(const scope of ['section','book']) {
    const result=await selectedSearch(example,scope,false,'PublishedPrologueExample');
    check('PrologueExampleUnique',result.occurrences,1);
    check('PrologueExampleIdentity',result.hitGroups.map(g=>g.recordIds),[[`${collectionId}-1-2`]]);
    validateConcordance(result,oracle,oracle.evaluate(example,scope),example,catalog,'PrologueExampleCSV');
    noteExample(print(example),scope,result,'Pollard English De excidio Prol.2 example');
  }
  const prologueLast=first.rows[2],narrativeFirst=first.rows[3];
  const boundaryTree=phrase([...prologueLast.tokens.slice(-4),...narrativeFirst.tokens.slice(0,4)].map(t=>t.term));
  const stopped=await selectedSearch(boundaryTree,'book',false,'ProloguePhraseBarrier');
  check('PrologueCannotContinueIntoNarrative',stopped.occurrences,0);
  const twoParts=and(phrase(first.rows[0].tokens.slice(0,8).map(t=>t.term)),phrase(narrativeFirst.tokens.slice(0,8).map(t=>t.term)));
  for(const scope of ['section','book']) {
    const result=await selectedSearch(twoParts,scope,false,'PrologueBooleanAcrossBoundary');
    check('BooleanMayRelateSameBookAcrossPrologueEnd',result.matchingUnits,scope==='book'?1:0);
    validateConcordance(result,oracle,oracle.evaluate(twoParts,scope),twoParts,catalog,'PrologueBooleanCSV');
  }
  for(const tree of [word('Jews'),word('the'),not(word('zzzzpollardabsent')),not(word('*')),word('zzzzpollardabsent'),
    and(word('Jews'),not(word('Romans'))),or(word('Jerusalem'),word('Jerus*'))])for(const scope of ['section','book']) {
    const result=await selectedSearch(tree,scope,true,'CompleteEnglish');
    validateConcordance(result,oracle,oracle.evaluate(tree,scope),tree,catalog,'CompleteEnglishCSV');
    if(tree.op==='leaf'&&['Jews','the'].includes(tree.patterns[0]))noteExample(print(tree),scope,result,'Complete English De excidio count');
  }
  for(let book=1;book<expectedBooks.length;book++) {
    const left=bookData[book-1].rows.at(-1),right=bookData[book].rows[0];
    const tree=phrase([...left.tokens.slice(-4),...right.tokens.slice(0,4)].map(t=>t.term));
    const result=await selectedSearch(tree,'book',false,'NoCrossBookPhrase');
    check('EachBookBoundaryStopsPhrase',result.occurrences,0,{book});
  }
  check('LoaderExactlyEnglishDehBooks',[...loaded].sort(),entries.map(entry=>entry.path).sort());
  const latinId='deh-latin-ussani',latinBook=`${latinId}:1`;
  for(const query of ['Judaea','iudaea','Jews','iews']) {
    const result=await collection.search(query,{collections:[latinId,collectionId],books:[latinBook,bookId],scope:'section',fold:true});totalQueries++;
    const groups=result.hitGroups.filter(g=>g.collectionId===collectionId);
    compare({...result,hitGroups:groups,matchingUnits:groups.length,occurrences:groups.reduce((n,g)=>n+g.hits.length,0),
      matchingSections:new Set(groups.flatMap(g=>g.recordIds)).size},first.oracle.evaluate(word(query),'section'),first.oracle,'section','MixedEnglishLiteral',query);
    check('MixedNormalization',result.normalization,{caseSensitive:false,spellingEquivalence:'latin-uv-ij',foldedCollectionIds:[latinId],literalCollectionIds:[collectionId]});
  }
  const noLanguageBridge=await collection.search('God AND deus',{collections:[latinId,collectionId],books:[latinBook,bookId],scope:'book',fold:false});totalQueries++;
  check('NoCrossLanguageBoolean',noLanguageBridge.matchingUnits,0);
  const englishCollections=['antiquities-english-whiston','bellum-english-whiston','contra-apionem-english-whiston',collectionId];
  const englishBookIds=englishCollections.map(id=>`${id}:1`);
  const fourWorks=await collection.search('God',{collections:englishCollections,books:englishBookIds,scope:'book',fold:true});totalQueries++;
  check('FourEnglishWorksAllDiscoverable',fourWorks.matchingBooks,englishBookIds);
  check('FourEnglishWorksNormalization',fourWorks.normalization,{caseSensitive:false,spellingEquivalence:'none',foldedCollectionIds:[],literalCollectionIds:englishCollections});
  const fourModel=buildConcordance(fourWorks,fourWorks.records,{readerBase:'https://latinjosephus.github.io/'});
  const fourCSV=parseCSV(exportConcordance(fourModel,fourWorks,{catalog,exportedAt:'2026-10-21T16:00:00Z'}).text);
  check('FourEnglishWorksDistinctCSV',[...new Set(fourCSV.map(r=>r.collection_id))],englishCollections);
  const readerPaths=['/antiquities/','/bellum-judaicum/','/contra-apionem/','/deh/'];
  for(const row of fourCSV) {
    const reader=new URL(row.reader_url),index=englishCollections.indexOf(row.collection_id);
    check('FourEnglishWorksCorrectReaderPath',reader.pathname,readerPaths[index]);
    check('FourEnglishWorksExplicitEdition',reader.searchParams.get('english'),index===3?'pollard':'whiston');
  }
  const distinctive=['"in the beginning God created"','"whereas the war"','"I suppose that by my books"','"I too have set out in writing"'];
  for(let left=0;left<distinctive.length;left++)for(let right=left+1;right<distinctive.length;right++) {
    const query=`${distinctive[left]} AND ${distinctive[right]}`;
    const result=await collection.search(query,{collections:englishCollections,books:englishBookIds,scope:'book',fold:false});totalQueries++;
    check('NoCrossWorkBoolean',result.matchingUnits,0,{query});
  }
  for(const [p,before] of checkedFiles)check('InputUnchangedDuringRun',digest(p),before,{path:relative(root,p)});
  const report={status:'PASS',generatedAt:new Date().toISOString(),independentVerifier:'bin/search/tests/deh-english-corpus-qa.mjs',readerBaseline,
    runtime:{node:process.version,...witness.runtime},source:{...witness.totals,uniqueLiteralVocabulary:oracle.vocabulary.length,bookTotals:witness.bookTotals},
    sources:witness.sources,testSources:witness.testSources,sourceCases:{sameAsLinks:740,indentedBeforeCitationLabels:217,
      chapterDivisionsIncludingPrologue:177,prologueUnits:3,excludedHeads:6,excludedReleaseNotes:5,
      inlineEditorialElements:0,literalBracketParagraphs:0},
    verifiedFiles:{corpus:evidence(corpusPath),catalog:evidence(catalogPath),engine:evidence(resolve(base,'engine.mjs')),
      collection:evidence(resolve(base,'collection.mjs')),concordance:evidence(resolve(base,'concordance.mjs')),uiUtils:evidence(resolve(base,'ui-utils.mjs')),
      verifier:evidence(verifierPath),witness:evidence(witnessPath),extractor:evidence(resolve(base,'extract-deh-english.py')),manifest:evidence(manifestPath),
      lunr:evidence(resolve(base,'vendor/lunr.cjs')),extractionReport:evidence(extractionPath),originalReader:evidence(readerPath),testSources:latinPaths.map(evidence),
      books:bookData.map(book=>({book:book.entry.number,bundle:evidence(book.paths.bundle),corpus:evidence(book.paths.corpus),
        source:evidence(book.paths.source),extractionReport:evidence(book.paths.extractionReport)}))},
    method:{source:'Independent minidom child traversal from five SHA-pinned English XML files; five separately pinned Latin files verify 740 sameAs targets and 558 identical citation labels. All 558 English paragraphs retain exact running text and actual xml:id. Every source-to-record slice and full paragraph restoration is compared, including 217 paragraphs with indentation before num.',
      tokens:'Every serialized token and original UTF-16 offset is compared with independent Python Unicode-category and JavaScript character scanners.',
      queries:'All literal vocabulary per book, one exact phrase per citation unit, every neighboring paragraph seam, every chapter seam, every book boundary, bounded wildcards and explicit Boolean trees. The Prologue end blocks phrases but permits Boolean conditions across the same book.',
      language:'English spelling remains literal with Latin-only equivalence. Latin and English De excidio stay separate editions; the four English works retain their own book identities and reader sources.',
      exports:'Exact concordance geometry, original source slices, chapter/paragraph citations, Prologue links, ordinary and negative-only CSV exports, every selected book and explicit Pollard reader parameters.'},
    counts,totalQueries,assertions,failedAssertions:0,examples,durationSeconds:Math.round((performance.now()-started)/100)/10,
    limitations:['This validates the accepted English De excidio v1.0 files, not a new translation or textual revision.','Browser interaction is verified separately.'],failures:[]};
  if(!smoke)writeFileSync(destination,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({status:smoke?'DEVELOPMENT_SMOKE_PASS':'PASS',source:report.source,totalQueries,assertions,
    durationSeconds:report.durationSeconds,report:smoke?null:relative(root,destination)},null,2));
}
try {
  if(!smoke){mkdirSync(dirname(destination),{recursive:true});writeFileSync(destination,JSON.stringify({status:'RUNNING',startedAt:new Date().toISOString(),independentVerifier:'bin/search/tests/deh-english-corpus-qa.mjs'})+'\n');}
  await main();
} catch(error) {
  if(!smoke)writeFileSync(destination,JSON.stringify({status:'FAIL',generatedAt:new Date().toISOString(),independentVerifier:'bin/search/tests/deh-english-corpus-qa.mjs',counts,totalQueries,assertions,failedAssertions:1,error:{name:error.name,message:error.message,stack:error.stack}},null,2)+'\n');
  console.error(error.stack||error.message);process.exitCode=1;
}
