/**
 * Independent DEH source/index/query acceptance.
 * Run: node bin/search/tests/deh-corpus-qa.mjs
 * A reviewed reader may be selected with --expected-reader-sha256 <SHA-256>.
 * --smoke is a development check and never writes a publication QA report.
 *
 * This imports production entry points only to exercise them. The witness is
 * separately parsed with Python minidom, independently tokenized by Unicode
 * character categories, and matched by an explicit AST/set/full-scan oracle.
 * The embedded witness is part of this verifier's own checked fingerprint.
 */
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {dirname, relative, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {performance} from 'node:perf_hooks';
import {createEngine} from '../engine.mjs';
import {createCollection} from '../collection.mjs';

const require = createRequire(import.meta.url);
const lunr = require('../vendor/lunr.cjs');
const base = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const root = resolve(base, '../..');
const collectionId = 'deh-latin-ussani';
const destination = resolve(base, 'data', collectionId, 'qa-report.json');
let smoke = false, explicitReaderSHA = null;
const args = process.argv.slice(2);
const usage = 'Usage: node bin/search/tests/deh-corpus-qa.mjs [--smoke] [--expected-reader-sha256 <accepted SHA-256>]';
for (let index = 0; index < args.length; index++) {
  if (args[index] === '--smoke') {
    assert.equal(smoke, false, usage);
    smoke = true;
  } else if (args[index] === '--expected-reader-sha256') {
    assert.ok(explicitReaderSHA === null && /^[a-f0-9]{64}$/i.test(args[index + 1] || ''), usage);
    explicitReaderSHA = args[++index].toLowerCase();
  } else assert.fail(usage);
}
const started = performance.now();
const hash = value => createHash('sha256').update(value).digest('hex');
const digest = path => hash(readFileSync(path));
const readJSON = path => JSON.parse(readFileSync(path, 'utf8'));
const evidence = path => ({path: relative(root, path).replaceAll('\\', '/'), sha256: digest(path)});
const counts = {};
let assertions = 0, totalQueries = 0;
const examples = [];
const checkedFiles = new Map();
function preserve(path) {
  const resolved = resolve(path);
  if (!checkedFiles.has(resolved)) checkedFiles.set(resolved, digest(resolved));
  return resolved;
}
function check(category, actual, expected, context = {}) {
  assertions++;
  counts[category] = (counts[category] || 0) + 1;
  assert.deepEqual(actual, expected, `${category}: ${JSON.stringify(context)}`);
}

// No imports from extract-deh.py or its generated extraction report.
const pythonWitness = String.raw`
import hashlib,json,pathlib,sys,unicodedata
from xml.dom import minidom,Node
root=pathlib.Path(sys.argv[1])
romans=[None,'I','II','III','IV','V']
expected_counts=[215,73,70,79,121]
expected_tokens=[26310,11011,12091,11027,27033]
expected_hashes=[
 '690da8720b61514199f898909c06661fddc9f3c79a06eea3b392325de7924aa7',
 'cc2ac0d622d56b0ef0e9a74bfdbcb2836c8cd89defbc0a70c11f9cb6274ef25a',
 'aeb861000317b2bbeada0a0d8918499f516f1dc524257ec90d140a5e9bf066c5',
 '150fb0857b07eaa47ca0de119558ed76368d6a452c06784475b97eb15a0e10fa',
 'f97fbd0992e8a540d250963109610060a8f417cb7cd18f93d5279c82cf2fcd97']
def sha(data):return hashlib.sha256(data).hexdigest()
def children(node,tag):return [c for c in node.childNodes if c.nodeType==Node.ELEMENT_NODE and c.localName==tag]
def all_text(node):return ''.join(c.data if c.nodeType in (Node.TEXT_NODE,Node.CDATA_SECTION_NODE) else all_text(c) for c in node.childNodes)
def utf16(s):return len(s.encode('utf-16-le'))//2
def tokens(text):
 out=[];i=0
 while i<len(text):
  if unicodedata.category(text[i])[0] not in 'LN':i+=1;continue
  j=i+1
  while j<len(text) and unicodedata.category(text[j])[0] in 'LMN':j+=1
  term=unicodedata.normalize('NFC',text[i:j]).lower().replace('\u03c2','\u03c3')
  out.append({'term':unicodedata.normalize('NFC',term),'start':utf16(text[:i]),'end':utf16(text[:j])});i=j
 return out
rows=[];books=[];ids=[]
for book in range(1,6):
 path='assets/xml/deh/Latin/book-%02d.xml'%book;raw=(root/path).read_bytes()
 lf=raw.replace(b'\r\n',b'\n')
 assert b'\r' not in lf and sha(lf)==expected_hashes[book-1],('Unaccepted source',path)
 assert b'<!DOCTYPE' not in raw.upper() and b'<!ENTITY' not in raw.upper()
 dom=minidom.parseString(raw);body=dom.getElementsByTagName('body')[0];bn=children(body,'div1')[0]
 assert bn.getAttribute('n')==romans[book] and bn.getAttribute('xml:id')=='latin-deh%d'%book
 local_ids=[e.getAttribute('xml:id') for e in body.getElementsByTagName('*') if e.hasAttribute('xml:id')]
 assert len(set(local_ids))==len(local_ids);ids.extend(local_ids)
 tags={}
 for e in [body]+list(body.getElementsByTagName('*')):tags[e.localName]=tags.get(e.localName,0)+1
 assert set(tags)<=set(['body','div1','div2','head','p','num','pb','lb','del','supplied','unclear'])
 book_rows=[];ordinal=0
 for chapter in children(bn,'div2'):
  cnum=int(chapter.getAttribute('n'))
  assert chapter.getAttribute('xml:id')=='latin-deh%d-chapter%d'%(book,cnum)
  for paragraph,p in enumerate(children(chapter,'p'),1):
   ordinal+=1;sid='latin-deh%d-num%d'%(book,ordinal)
   assert p.getAttribute('xml:id')==sid
   label='Prol.%d'%paragraph if cnum==0 else '%s.%d.%d'%(romans[book],cnum,paragraph)
   nums=children(p,'num');assert len(nums)==1 and all_text(nums[0])=='['+label+']'
   parts=[];marks=[]
   def visit(node):
    if node.nodeType in (Node.TEXT_NODE,Node.CDATA_SECTION_NODE):parts.append(node.data);return
    if node.nodeType!=Node.ELEMENT_NODE:return
    kind=node.localName
    if kind=='num':return
    start=len(''.join(parts))
    if kind=='unclear':
     assert not all_text(node) and not children(node,'*');parts.append('\u2020')
    elif kind not in ['pb','lb']:
     for child in node.childNodes:visit(child)
    if kind in ['del','supplied','unclear']:
     marks.append({'kind':kind,'first':start,'last':len(''.join(parts))})
   for child in p.childNodes:visit(child)
   raw_display=''.join(parts);left=len(raw_display)-len(raw_display.lstrip());text=raw_display.strip()
   editorial=[]
   for mark in marks:
    a,b=mark['first']-left,mark['last']-left
    assert 0<=a<b<=len(text)
    m={'kind':mark['kind'],'start':utf16(text[:a]),'end':utf16(text[:b]),'text':text[a:b]}
    if mark['kind']=='unclear':m.update({'representation':'generated-dagger','sourceTag':'unclear'})
    editorial.append(m)
   editorial.sort(key=lambda m:(m['start'],-m['end'],m['kind']))
   row={'id':'deh-latin-ussani-%d-%d'%(book,ordinal),'work':'deh','book':book,'section':ordinal,
        'language':'Latin','edition':'Ussani (1932)','chapter':cnum,'paragraph':paragraph,
        'citationScheme':'chapter-paragraph','citationLabel':label,
        'citation':{'book':romans[book],'chapter':cnum,'paragraph':paragraph,'prologue':cnum==0},
        'text':text,'editorialMarks':editorial,'url':'/deh/?book=%d&chapter=%d&unit=%d'%(book,cnum,paragraph),
        'readerLink':{'path':'deh/','params':{'book':book,'chapter':cnum,'unit':paragraph}},
        'sourceId':sid,'order':len(rows),'breakBefore':book==1 and ordinal==4}
   ts=tokens(text);rows.append({'record':row,'tokens':ts});book_rows.append(row)
 assert ordinal==expected_counts[book-1]
 token_count=sum(len(row['tokens']) for row in rows if row['record']['book']==book)
 assert token_count==expected_tokens[book-1]
 books.append({'book':book,'path':path,'sha256':sha(raw),'acceptedLF_sha256':expected_hashes[book-1],
               'sections':ordinal,'tokens':token_count,'stableIds':len(local_ids),'bodyTags':tags})
assert len(rows)==558 and len(ids)==len(set(ids))==740
print(json.dumps({'books':books,'rows':rows,'stableIds':len(ids),'runtime':{'python':sys.version.split()[0],'unicode':unicodedata.unidata_version,'xmlParser':'xml.dom.minidom'}},ensure_ascii=False,separators=(',',':')))
`;

// Distinct from production tokenizeText: character-by-character, used also for
// unchanged Bellum index records in the mixed-work collection checks.
function independentTokens(text) {
  const result = [];
  let offset = 0, start = null, value = '';
  const emit = () => {
    if (start !== null) result.push({term: normalize(value), start, end: offset});
    start = null; value = '';
  };
  for (const character of text) {
    const canStart = /[\p{L}\p{N}]/u.test(character);
    const canContinue = /[\p{L}\p{M}\p{N}]/u.test(character);
    if (start !== null && canContinue) value += character;
    else {
      emit();
      if (canStart) {start = offset; value = character;}
    }
    offset += character.length;
  }
  emit();
  return result;
}
function normalize(value, fold = false) {
  let result = value.normalize('NFC').toLowerCase().replaceAll('ς', 'σ');
  if (fold) result = result.replaceAll('v', 'u').replaceAll('j', 'i');
  return result.normalize('NFC');
}
function glob(pattern, word) {
  const escaped = pattern.split('*').map(part => part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('.*');
  return new RegExp(`^(?:${escaped})$`, 'u').test(word);
}
const leaf = pattern => ({op: 'leaf', patterns: [pattern]});
const phrase = patterns => ({op: 'leaf', patterns, phrase: true});
const and = (left, right) => ({op: 'and', left, right});
const or = (left, right) => ({op: 'or', left, right});
const not = child => ({op: 'not', child});
function print(ast) {
  if (ast.op === 'leaf') return ast.phrase ? `"${ast.patterns.join(' ')}"` : ast.patterns[0];
  if (ast.op === 'not') return `NOT (${print(ast.child)})`;
  return `(${print(ast.left)} ${ast.op.toUpperCase()} ${print(ast.right)})`;
}
const identity = record => JSON.stringify([record.work, Number(record.book), record.language, record.edition]);
const spanKey = spans => JSON.stringify(spans.map(span => [span.recordId, span.start, span.end]));
function makeOracle(records, suppliedTokens) {
  const byId = new Map(records.map((record, index) => [record.id, {record, index}]));
  const tokenLists = suppliedTokens || records.map(record => independentTokens(record.text));
  const all = [];
  const segments = new Map();
  records.forEach((record, index) => {
    const key = identity(record);
    let segment = segments.get(key) || 0;
    if (record.breakBefore) segment++;
    segments.set(key, segment);
    all.push(...tokenLists[index].map(token => ({...token, recordId: record.id, recordIndex: index, bookKey: key, segment})));
  });
  const vocabulary = [...new Set(all.map(token => token.term))].sort();
  const tables = new Map([false, true].map(fold => {
    const table = new Map();
    for (const token of all) {
      const key = normalize(token.term, fold);
      if (!table.has(key)) table.set(key, []);
      table.get(key).push(token);
    }
    return [fold, table];
  }));
  const keyOf = (record, scope) => scope === 'section' ? record.id : identity(record);
  function leafMatches(ast, scope, fold) {
    const result = new Map();
    const add = (key, spans) => {
      if (!result.has(key)) result.set(key, new Set());
      result.get(key).add(spanKey(spans));
    };
    const patterns = ast.patterns.map(pattern => normalize(pattern, fold));
    if (!ast.phrase) {
      const pattern = patterns[0], table = tables.get(fold);
      const matches = pattern.includes('*') ? [...table.keys()].filter(word => glob(pattern, word)) : table.has(pattern) ? [pattern] : [];
      for (const word of matches) for (const token of table.get(word))
        add(scope === 'section' ? token.recordId : token.bookKey, [token]);
      return result;
    }
    const matchers = patterns.map(pattern => {
      if (!pattern.includes('*')) return word => word === pattern;
      const escaped = pattern.split('*').map(part => part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('.*');
      const regex = new RegExp(`^(?:${escaped})$`, 'u');
      return word => regex.test(word);
    });
    // Full sequential scan; does not share production rarest-word anchoring,
    // Lunr candidate selection, phrase match helpers, or query parser.
    for (let i = 0; i <= all.length - patterns.length; i++) {
      const first = all[i];
      let accepted = true;
      for (let j = 0; j < patterns.length; j++) {
        const token = all[i + j];
        if (token.bookKey !== first.bookKey || token.segment !== first.segment
          || (scope === 'section' && token.recordId !== first.recordId)
          || !matchers[j](normalize(token.term, fold))) {accepted = false; break;}
      }
      if (!accepted) continue;
      const spans = [];
      for (const token of all.slice(i, i + patterns.length)) {
        if (spans.at(-1)?.recordId === token.recordId) spans.at(-1).end = token.end;
        else spans.push({recordId: token.recordId, start: token.start, end: token.end});
      }
      add(scope === 'section' ? first.recordId : first.bookKey, spans);
    }
    return result;
  }
  function evaluate(ast, scope, fold, negated = false) {
    if (ast.op === 'not') return evaluate(ast.child, scope, fold, !negated);
    if (ast.op === 'leaf') {
      const hits = leafMatches(ast, scope, fold);
      if (!negated) return hits;
      return new Map([...new Set(records.map(record => keyOf(record, scope)))].filter(key => !hits.has(key)).map(key => [key, new Set()]));
    }
    const left = evaluate(ast.left, scope, fold, negated), right = evaluate(ast.right, scope, fold, negated);
    const operation = negated ? (ast.op === 'and' ? 'or' : 'and') : ast.op;
    const result = new Map();
    for (const key of new Set([...left.keys(), ...right.keys()])) {
      if (operation === 'and' && (!left.has(key) || !right.has(key))) continue;
      result.set(key, new Set([...(left.get(key) || []), ...(right.get(key) || [])]));
    }
    return result;
  }
  return {records, tokenLists, all, vocabulary, byId, evaluate};
}

function compareResults(actual, expected, oracle, options, category, query, example = false) {
  const context = {query, ...options};
  const scope = options.scope;
  check(`${category}MatchingUnits`, actual.matchingUnits, expected.size, context);
  check(`${category}Occurrences`, actual.occurrences, [...expected.values()].reduce((sum, hits) => sum + hits.size, 0), context);
  const groupKey = group => scope === 'section' ? group.recordIds[0]
    : group.work ? identity({work: group.work, book: group.book, language: group.language, edition: group.edition})
      : identity(oracle.records[0]);
  const actualGroups = new Map(actual.hitGroups.map(group => [groupKey(group), group]));
  check(`${category}UnitIdentity`, [...actualGroups.keys()].sort(), [...expected.keys()].sort(), context);
  const allTouched = new Set();
  const rank = id => oracle.byId.get(id).index;
  for (const [key, hits] of expected) {
    const group = actualGroups.get(key);
    check(`${category}Evidence`, group.hits.map(hit => spanKey(hit.spans)).sort(), [...hits].sort(), {...context, unit: key});
    const ids = scope === 'section' ? [key] : [...new Set([...hits].flatMap(hit => JSON.parse(hit).map(span => span[0])))].sort((a, b) => rank(a) - rank(b));
    ids.forEach(id => allTouched.add(id));
    check(`${category}RecordIds`, group.recordIds, ids, {...context, unit: key});
    check(`${category}Sections`, group.sections, ids.map(id => oracle.byId.get(id).record.section), {...context, unit: key});
  }
  check(`${category}MatchingSections`, actual.matchingSections, allTouched.size, context);
  if (example) examples.push({...context, matchingUnits: actual.matchingUnits, matchingSections: actual.matchingSections, occurrences: actual.occurrences});
}
function verify(engine, oracle, ast, options, category, query = print(ast), example = false) {
  totalQueries++;
  counts[`${category}Queries`] = (counts[`${category}Queries`] || 0) + 1;
  compareResults(engine.search(query, options), oracle.evaluate(ast, options.scope, options.fold), oracle, options, category, query, example);
}

const readerPath = resolve(root, 'assets/js/renderTei.js');
const acceptedReaders = new Map([
  ['03bfb9b0de5e13e6b07bd638413b2b82a9ed2f7b0cc7c33eb6c09dabde3c9294', 'canonical-2026-10-14'],
  ['25c00a11818fe5a71dcbffb516aeb8a6f02c6b61c218f4e85105a12eb310d0ed', 'approved-public-preview'],
]);
const observedReaderSHA = digest(readerPath);
const readerSHA = explicitReaderSHA || observedReaderSHA;
const readerBaseline = {expectedSha256: readerSHA, observedSha256: observedReaderSHA,
  provenance: explicitReaderSHA ? 'explicit-argument' : acceptedReaders.get(readerSHA),
  preservationDuringRunRequired: true, publicationInput: false};

async function main() {
  assert.ok(explicitReaderSHA || acceptedReaders.has(observedReaderSHA), 'Reader differs from both reviewed baseline fingerprints; review its changes before explicitly supplying --expected-reader-sha256.');
  check('ReviewedReaderBaseline', observedReaderSHA, readerSHA);
  const catalogPath = preserve(resolve(base, 'catalog.json'));
  const corpusPath = preserve(resolve(base, 'data', collectionId, 'corpus.json'));
  const catalog = readJSON(catalogPath), corpus = readJSON(corpusPath);
  const config = catalog.collections.find(collection => collection.id === collectionId);
  assert.ok(config, 'The catalog must include the DEH collection before this verifier runs.');
  const selectedEntries = catalog.books.filter(entry => entry.collectionId === collectionId);
  check('CatalogBookOrder', selectedEntries.map(entry => entry.number), [1, 2, 3, 4, 5]);
  check('CatalogCitationScheme', config.citationScheme, 'chapter-paragraph');
  preserve(readerPath); preserve(resolve(base, 'engine.mjs')); preserve(resolve(base, 'collection.mjs')); preserve(fileURLToPath(import.meta.url));
  const witness = JSON.parse(execFileSync(process.env.PYTHON || 'python3', ['-c', pythonWitness, root], {encoding: 'utf8', maxBuffer: 80 * 1024 * 1024}));
  check('CanonicalStableIds', witness.stableIds, 740);
  check('CombinedRecordCount', corpus.length, 558);
  const witnessById = new Map(witness.rows.map(row => [row.record.id, row]));
  for (const [index, row] of corpus.entries()) {
    const independent = witness.rows[index];
    check('CombinedRecordOrder', row.id, independent.record.id, {index});
    for (const [key, value] of Object.entries(independent.record))
      check('SourceRecordField', key === 'breakBefore' ? Boolean(row[key]) : row[key], value, {id: row.id, key});
    check('IndependentTokenizersAgree', independentTokens(row.text), independent.tokens, {id: row.id});
  }
  const states = [];
  const fixtures = [
    ['Iosephus', leaf('Iosephus')], ['sacerdot*', leaf('sacerdot*')], ['Cenedaei', leaf('Cenedaei')],
    ['"tamquam in spinis rosam quaerentes"', phrase(['tamquam', 'in', 'spinis', 'rosam', 'quaerentes'])],
    ['"historia uetus"', phrase(['historia', 'uetus'])],
    ['"hautquaquam dissimulandum arbitrabantur"', phrase(['hautquaquam', 'dissimulandum', 'arbitrabantur'])],
    ['"non intellexit Vnde nobis curae"', phrase(['non', 'intellexit', 'Vnde', 'nobis', 'curae'])],
    ['"sumam exordium Bello Parthico quod"', phrase(['sumam', 'exordium', 'Bello', 'Parthico', 'quod'])],
    ['"statuere ausus Quod factum Matthathias"', phrase(['statuere', 'ausus', 'Quod', 'factum', 'Matthathias'])],
    ['"nisi qu*"', phrase(['nisi', 'qu*'])], ['Iudae* OR Roman* AND sacerdot*', or(leaf('Iudae*'), and(leaf('Roman*'), leaf('sacerdot*')))],
    ['Ioseph* sacerdot* OR templ*', or(and(leaf('Ioseph*'), leaf('sacerdot*')), leaf('templ*'))],
    ['(Ioseph* OR sacerdot*) AND NOT templ*', and(or(leaf('Ioseph*'), leaf('sacerdot*')), not(leaf('templ*')))],
    ['NOT (Ioseph* OR NOT sacerdot*)', not(or(leaf('Ioseph*'), not(leaf('sacerdot*'))))],
    ['NOT NOT Iosephus', not(not(leaf('Iosephus')))],
    ['NOT zzzznonoccurrit', not(leaf('zzzznonoccurrit'))], ['NOT *', not(leaf('*'))],
    ['rex OR rex*', or(leaf('rex'), leaf('rex*'))],
    ['"tamquam in spinis rosam quaerentes" AND Parthico', and(phrase(['tamquam', 'in', 'spinis', 'rosam', 'quaerentes']), leaf('Parthico'))],
  ];
  for (const entry of selectedEntries) {
    const bookStarted = performance.now();
    const bundlePath = preserve(resolve(base, entry.path));
    const shardPath = preserve(resolve(base, entry.corpusPath));
    const sourcePath = preserve(resolve(root, `assets/xml/deh/Latin/book-${String(entry.number).padStart(2, '0')}.xml`));
    const bundle = readJSON(bundlePath), shard = readJSON(shardPath);
    const expectedRows = witness.rows.filter(row => row.record.book === entry.number);
    const records = corpus.filter(record => record.book === entry.number);
    check('ShardMatchesCombinedCorpus', shard, records, {book: entry.number});
    check('BundleMatchesShard', bundle.records, records.map(record => ({...record, breakBefore: Boolean(record.breakBefore)})), {book: entry.number});
    check('CatalogBundleHash', entry.sha256, digest(bundlePath), {book: entry.number});
    check('CatalogCorpusHash', entry.corpusSHA256, digest(shardPath), {book: entry.number});
    check('SourceFingerprint', digest(sourcePath), witness.books[entry.number - 1].sha256, {book: entry.number});
    check('AllIndexedTokenOffsets', bundle.tokens, expectedRows.map(row => row.tokens), {book: entry.number});
    check('ExpectedTokenCount', bundle.stats.tokens, witness.books[entry.number - 1].tokens, {book: entry.number});
    const oracle = makeOracle(records, expectedRows.map(row => row.tokens)), engine = createEngine(bundle, lunr);
    const wordsToTest = smoke ? oracle.vocabulary.filter((_, index) => index % Math.max(1, Math.floor(oracle.vocabulary.length / 10)) === 0) : oracle.vocabulary;
    for (const word of wordsToTest) for (const fold of [false, true])
      verify(engine, oracle, leaf(word), {scope: 'section', fold}, 'ExhaustiveVocabulary');
    for (const [query, ast] of fixtures) for (const scope of ['section', 'book']) for (const fold of [false, true])
      verify(engine, oracle, ast, {scope, fold}, 'Fixture', query, entry.number === 1 && !fold && scope === 'book');
    const sampledWords = oracle.vocabulary.filter(word => word.length >= 5).filter((_, index) => index % Math.max(1, Math.floor(oracle.vocabulary.length / (smoke ? 4 : 35))) === 0);
    const wildcardPatterns = new Set(['*', '**', 'sacerdot*', '*ae', 'i*us', '*iud*', 'r*x', 'zzzznonoccurrit*']);
    for (const word of sampledWords) {
      wildcardPatterns.add(word.slice(0, 3) + '*');
      wildcardPatterns.add('*' + word.slice(-3));
      wildcardPatterns.add(word.slice(0, 2) + '*' + word.slice(-2));
      wildcardPatterns.add(word.slice(0, 2) + '**' + word.slice(2));
    }
    for (const pattern of wildcardPatterns) for (const scope of ['section', 'book']) for (const fold of [false, true])
      verify(engine, oracle, leaf(pattern), {scope, fold}, 'Wildcard');
    const unitIndices = smoke ? [0, Math.floor(records.length / 2), records.length - 1] : records.map((_, index) => index);
    for (const index of unitIndices) {
      const tokens = oracle.tokenLists[index], start = Math.max(0, Math.floor(tokens.length / 2) - 1);
      const ast = phrase(tokens.slice(start, start + 3).map(token => token.term));
      for (const scope of ['section', 'book']) for (const fold of [false, true]) verify(engine, oracle, ast, {scope, fold}, 'WithinEveryUnit');
    }
    const seams = smoke ? [0, 1, 2, 3].filter(index => index < records.length - 1) : records.slice(1).map((_, index) => index);
    for (const index of seams) {
      const ast = phrase([...oracle.tokenLists[index].slice(-2), ...oracle.tokenLists[index + 1].slice(0, 2)].map(token => token.term));
      const matching = oracle.evaluate(ast, 'book', false);
      const ownSeam = [...matching.values()].flatMap(hits => [...hits]).some(hit => {
        const spans = JSON.parse(hit); return spans.length === 2 && spans[0][0] === records[index].id && spans[1][0] === records[index + 1].id;
      });
      check('BoundaryOracleExpectation', ownSeam, !records[index + 1].breakBefore, {book: entry.number, left: records[index].citationLabel, right: records[index + 1].citationLabel});
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, ast, {scope, fold}, records[index + 1].breakBefore ? 'PrologueBoundaryBlocked' : 'EveryAdjacentUnitBoundary');
    }
    states.push({entry, bundlePath, shardPath, sourcePath, oracle, engine, vocabularyQueries: wordsToTest.length * 2, withinBookBoundaries: seams.length});
    console.log(JSON.stringify({phase: 'DEH book complete', book: entry.number, vocabulary: oracle.vocabulary.length, queriesSoFar: totalQueries, seconds: Math.round((performance.now() - bookStarted) / 100) / 10}));
  }

  const bundleEntries = new Map(catalog.books.map(entry => [new URL(entry.path, 'https://qa.invalid/assets/search/').pathname, entry]));
  const fetchCounts = new Map();
  const fetchImpl = async url => {
    const entry = bundleEntries.get(new URL(url).pathname);
    assert.ok(entry, `Unexpected bundle request: ${url}`);
    fetchCounts.set(entry.id, (fetchCounts.get(entry.id) || 0) + 1);
    const path = preserve(resolve(base, entry.path));
    return new Response(readFileSync(path), {status: 200});
  };
  const collection = createCollection(catalog, lunr, {baseURL: 'https://qa.invalid/assets/search/', fetchImpl});
  const allEntryRecords = new Map(catalog.books.map(entry => {
    const path = preserve(resolve(base, entry.path));
    return [entry.id, readJSON(path).records];
  }));
  async function verifyCollection(ast, selected, scope, fold, category, query = print(ast), example = false) {
    totalQueries++; counts[`${category}Queries`] = (counts[`${category}Queries`] || 0) + 1;
    const selectedSet = new Set(selected), ordered = catalog.books.filter(entry => selectedSet.has(entry.id));
    const records = ordered.flatMap(entry => allEntryRecords.get(entry.id));
    const oracle = makeOracle(records);
    const expected = oracle.evaluate(ast, scope, fold);
    const collections = [...new Set(ordered.map(entry => entry.collectionId))];
    const actual = await collection.search(query, {collections, books: selected, scope, fold});
    compareResults(actual, expected, oracle, {scope, fold, selectedBooks: selected}, category, query, example);
    check(`${category}SelectionOrder`, actual.selectedBooks, ordered.map(entry => entry.id));
    const matchedIds = new Set(scope === 'section' ? [...expected.keys()] : []);
    const expectedBookIds = ordered.filter(entry => scope === 'book'
      ? expected.has(identity(allEntryRecords.get(entry.id)[0]))
      : allEntryRecords.get(entry.id).some(record => matchedIds.has(record.id))).map(entry => entry.id);
    check(`${category}MatchingBookIdentity`, actual.matchingBooks, expectedBookIds, {query, scope, fold});
    check(`${category}UniqueRecordIdentity`, new Set(actual.records.map(record => record.id)).size, records.length);
    check(`${category}GlobalResultOrder`, actual.records.map(record => record.resultOrder), records.map((_, index) => index));
    return {actual, expected};
  }
  const selections = [[selectedEntries[0].id], [selectedEntries[4].id, selectedEntries[0].id, selectedEntries[2].id], selectedEntries.map(entry => entry.id)];
  for (const selected of selections) for (const [query, ast] of fixtures.filter((_, index) => smoke ? [0, 3, 15].includes(index) : [0, 1, 3, 6, 7, 10, 12, 13, 15, 16].includes(index)))
    for (const scope of ['section', 'book']) for (const fold of [false, true])
      await verifyCollection(ast, selected, scope, fold, 'SelectedDEHCollection', query, selected.length === 5 && !fold);
  for (let index = 0; index < states.length - 1; index++) {
    const left = states[index], right = states[index + 1], selected = [left.entry.id, right.entry.id];
    const ast = phrase([...left.oracle.all.slice(-3), ...right.oracle.all.slice(0, 3)].map(token => token.term));
    const leftOnly = left.oracle.vocabulary.find(word => word.length > 4 && !right.oracle.vocabulary.includes(word));
    const rightOnly = right.oracle.vocabulary.find(word => word.length > 4 && !left.oracle.vocabulary.includes(word));
    assert.ok(leftOnly && rightOnly);
    for (const scope of ['section', 'book']) for (const fold of [false, true]) {
      const checked = await verifyCollection(ast, selected, scope, fold, 'CrossBookPhraseBlocked');
      check('CrossBookPhraseAbsent', checked.expected.size, 0, {selected});
    }
    for (const scope of ['section', 'book']) {
      const checked = await verifyCollection(and(leaf(leftOnly), leaf(rightOnly)), selected, scope, false, 'CrossBookBooleanIsolation');
      check('CrossBookBooleanAbsent', checked.expected.size, 0, {selected, leftOnly, rightOnly});
    }
  }
  const bellum = catalog.books.filter(entry => entry.collectionId === 'bellum-latin-cardwell');
  assert.equal(bellum.length, 7, 'Mixed-work acceptance expects the already accepted seven Bellum books.');
  const mixedSelections = [catalog.books.map(entry => entry.id), [selectedEntries[0].id, bellum[0].id]];
  for (const selected of mixedSelections) for (const ast of [leaf('Iosephus'), leaf('sacerdot*'), phrase(['tamquam', 'in', 'spinis', 'rosam', 'quaerentes']), not(leaf('zzzznonoccurrit'))])
    for (const scope of ['section', 'book']) for (const fold of [false, true])
      await verifyCollection(ast, selected, scope, fold, 'MixedWorkCollection', print(ast), !fold && scope === 'book');
  const bellumOracle = makeOracle(allEntryRecords.get(bellum[0].id)), dehOracle = states[0].oracle;
  const dehOnly = dehOracle.vocabulary.find(word => word.length > 4 && !bellumOracle.vocabulary.includes(word));
  const bellumOnly = bellumOracle.vocabulary.find(word => word.length > 4 && !dehOracle.vocabulary.includes(word));
  assert.ok(dehOnly && bellumOnly);
  for (const scope of ['section', 'book']) {
    const checked = await verifyCollection(and(leaf(dehOnly), leaf(bellumOnly)), [selectedEntries[0].id, bellum[0].id], scope, false, 'CrossWorkBooleanIsolation');
    check('CrossWorkBooleanAbsent', checked.expected.size, 0, {dehOnly, bellumOnly});
  }
  const mixedSeam = phrase([...bellumOracle.all.slice(-3), ...dehOracle.all.slice(0, 3)].map(token => token.term));
  for (const scope of ['section', 'book']) {
    const checked = await verifyCollection(mixedSeam, [bellum[0].id, selectedEntries[0].id], scope, false, 'CrossWorkPhraseBlocked');
    check('CrossWorkPhraseAbsent', checked.expected.size, 0);
  }
  check('BundleFetchCaching', [...fetchCounts.entries()].sort(), catalog.books.map(entry => [entry.id, 1]).sort());
  for (const invalid of [{collections: [collectionId], books: [1]}, {collections: [collectionId], books: [bellum[0].id]}]) {
    await assert.rejects(collection.search('Iosephus', invalid));
    assertions++; counts.InvalidSelectionRejected = (counts.InvalidSelectionRejected || 0) + 1;
  }
  const failedLoad = createCollection(catalog, lunr, {baseURL: 'https://qa.invalid/assets/search/', fetchImpl: async url => {
    if (new URL(url).pathname.endsWith('/deh-latin-ussani/book-05.bundle.json')) return new Response('Unavailable', {status: 404});
    return new Response(readFileSync(resolve(base, bundleEntries.get(new URL(url).pathname).path)), {status: 200});
  }});
  await assert.rejects(failedLoad.search('Iosephus', {collections: [collectionId], books: [selectedEntries[0].id, selectedEntries[4].id]}));
  assertions++; counts.MissingSelectedBookRejectsCompleteSearch = 1;
  for (const [path, sha256] of checkedFiles) check('InputUnchangedDuringQA', digest(path), sha256, {path: relative(root, path)});
  const report = {
    status: 'PASS', generatedAt: new Date().toISOString(), independentVerifier: 'bin/search/tests/deh-corpus-qa.mjs', readerBaseline,
    runtime: {node: process.versions.node, ...witness.runtime},
    source: {books: 5, sections: 558, tokens: 87472, ordinaryCitationUnits: 555, prologueCitationUnits: 3, stableIds: 740,
      uniqueLiteralVocabulary: new Set(states.flatMap(state => state.oracle.vocabulary)).size},
    sources: witness.books,
    verifiedFiles: {corpus: evidence(corpusPath), catalog: evidence(catalogPath), engine: evidence(resolve(base, 'engine.mjs')),
      collection: evidence(resolve(base, 'collection.mjs')), verifier: evidence(fileURLToPath(import.meta.url)), originalReader: evidence(readerPath),
      books: states.map(state => ({book: state.entry.number, bundle: evidence(state.bundlePath), corpus: evidence(state.shardPath), source: evidence(state.sourcePath)}))},
    method: {source: 'Independent Python minidom parse of five SHA-pinned canonical XML sources; no extractor imports or extraction-report expectations.',
      tokens: 'Python Unicode-category tokenizer checked against every indexed token and UTF-16 offset; independent JavaScript character scan agrees for all DEH units.',
      queries: 'AST/set semantics, independent regex globs, full sequential phrase scan; no production parser/matching/tokenizer used as oracle.',
      vocabulary: 'Every distinct source token in each book queried in both literal and u/v-i/j-folded modes.',
      boundaries: 'Every adjacent unit boundary checked in section/book scopes and both spelling modes; Prologue→I.1.1 is a deliberate blocked composition boundary.',
      collection: 'Actual checksum-verified bundle loading, all five DEH and mixed Bellum/DEH selections, cache, unavailable-book rejection, and ambiguous/conflicting selector rejection.'},
    boundaryCoverage: {withinBookPairs: states.reduce((sum, state) => sum + state.withinBookBoundaries, 0), legalWholeBookPairs: 552, blockedPrologueNarrativePairs: 1, bookJunctions: 4, mixedWorkJunctions: 1},
    editorialCoverage: {del: 9, suppliedInRunningText: 9, crux: 3, headingSuppliedExcluded: 1, pageMarkers: 415, lineMarkers: 176},
    counts, totalQueries, assertions, failedAssertions: 0, examples,
    durationSeconds: Math.round((performance.now() - started) / 10) / 100,
    limitations: ['Automated Node/Python verification, not browser or visual acceptance.',
      'Reader URLs checked against canonical citation/ID structure; reader pages are not opened by this verifier.',
      'DEH text is checked against frozen canonical XML, not retranscribed or recertified from page images.',
      'Mixed-work Bellum expectations are independently tokenized from the unchanged Bellum corpus records; separate Bellum source-fidelity QA remains required.',
      'Marked deleted/supplied source content remains searchable, with editorial metadata preserved.'], failures: [],
  };
  if (!smoke) writeFileSync(destination, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({status: smoke ? 'DEVELOPMENT_SMOKE_PASS' : 'PASS', source: report.source, totalQueries, assertions, failedAssertions: 0, durationSeconds: report.durationSeconds, publicationReportWritten: !smoke}));
}

if (!smoke) writeFileSync(destination, JSON.stringify({status: 'RUNNING', generatedAt: new Date().toISOString(), independentVerifier: 'bin/search/tests/deh-corpus-qa.mjs'}, null, 2) + '\n');
try { await main(); }
catch (error) {
  if (!smoke) writeFileSync(destination, JSON.stringify({status: 'FAIL', generatedAt: new Date().toISOString(), assertions,
    totalQueries, failedAssertions: 1, error: {name: error.name, message: error.message, stack: error.stack}}, null, 2) + '\n');
  console.error(error.stack || error);
  process.exitCode = 1;
}
