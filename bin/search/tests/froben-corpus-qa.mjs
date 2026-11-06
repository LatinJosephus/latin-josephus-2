/** Verify the Froben index against the published reader data, without importing its extractor. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {createCollection} from '../collection.mjs';
import {buildConcordance, exportConcordance} from '../concordance.mjs';
import {readerURL, romanBook} from '../ui-utils.mjs';

const root = new URL('../../../', import.meta.url);
const lunr = createRequire(import.meta.url)('../vendor/lunr.cjs');
const id = 'antiquities-latin-froben1524';
const readerBase = 'https://qa.invalid/preview/';
const read = name => fs.readFileSync(new URL(name, root));
const json = name => JSON.parse(read(name));
const manifestPath = 'bin/search/config/' + id + '.json';
const manifest = json(manifestPath);
const catalog = json('bin/search/catalog.json');
const config = catalog.collections.find(item => item.id === id);
const collection = createCollection(catalog, lunr, {
  baseURL: 'https://qa.invalid/',
  fetchImpl: async url => new Response(read('bin/search' + url.pathname)),
});
const evidence = path => {
  const bytes = read(path);
  return {path, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')};
};
const words = text => Array.from(text.matchAll(/[\p{L}\p{N}][\p{L}\p{M}\p{N}]*/gu), match => match[0]);
let assertions = 0;
let totalQueries = 0;
function equal(actual, expected, description) {
  assertions++;
  assert.deepEqual(actual, expected, description);
}

function sourceDivision(source) {
  const data = json(source);
  const {start, end} = data.book.spans[0];
  const pages = [];
  const lines = [];
  let active = false;
  for (const page of data.pages) {
    let hasBody = false;
    for (const row of page.rows) {
      const first = page.image === start[0] && row.id === start[1];
      const last = page.image === end[0] && row.id === end[1];
      if (first) active = true;
      if (active && row.role === 'body' && !row.joinedInto) {
        const text = Array.from(row.text).slice(first ? start[2] : 0, last ? end[2] : undefined).join('').trim();
        if (text) {
          lines.push(text);
          hasBody = true;
        }
      }
      if (last) active = false;
    }
    if (hasBody) pages.push({image: page.image, display: page.display});
  }
  return {data, pages, text: lines.join('\n').replace(/¬\n|\n/gu, seam => seam === '\n' ? ' ' : '')};
}

const bookEvidence = [];
const examples = [];
for (const spec of manifest.books) {
  const entry = catalog.books.find(book => book.id === id + ':' + spec.number);
  const {records} = await collection.loadBooks([entry.id]);
  const divisions = [...(spec.additionalSources || []), spec.source].map(sourceDivision);
  for (const {data, pages, text} of divisions) {
    const proem = data.book.id === 'preface';
    const selected = records.filter(record => (record.division === 'proem') === proem);
    equal(selected.map(record => record.sourceImage), pages.map(page => page.image), 'All and only the pages with prose are indexed');
    equal(selected.map(record => record.text).join(' '), text, 'Prose and spelling survive page projection in physical order');
    for (const [index, page] of pages.entries()) {
      const record = selected[index];
      equal(record.citationLabel, (proem ? 'Proem' : romanBook(spec.number)) + ', ' + page.display);
      const link = new URL(readerURL(record, readerBase));
      equal(link.pathname, '/preview/antiquities/');
      equal(Object.fromEntries(link.searchParams), {
        book: data.book.id, froben: '1', 'froben-view': 'page',
        'froben-location': 'froben-image-' + page.image, 'froben-pages': '1',
      });
    }
  }

  const query = words(records.at(-1).text).find(word => word.length > 6).toLowerCase();
  const run = async (value, scope, fold = false) => {
    totalQueries++;
    return collection.search(value, {books: [entry.id], scope, fold});
  };
  const result = await run(query, 'section');
  const model = buildConcordance(result, records, {readerBase});
  const export_ = exportConcordance(model, result, {catalog, exportedAt: '2026-11-06T00:00:00Z'});
  equal(result.occurrences, records.flatMap(record => words(record.text))
    .filter(word => word.normalize('NFC').toLowerCase().replaceAll('ς', 'σ') === query.normalize('NFC').replaceAll('ς', 'σ')).length);
  equal(export_.rowCount, result.occurrences);
  equal(model.rows.every(row => new URL(row.readerURL).searchParams.get('froben-view') === 'page'), true);
  examples.push({book: spec.number, query, occurrences: result.occurrences});

  const pair = records.slice(-2);
  const phrase = '"' + [words(pair[0].text).at(-1), words(pair[1].text)[0]].join(' ') + '"';
  const pageMatch = await run(phrase, 'section');
  const bookMatch = await run(phrase, 'book');
  const crosses = output => output.hitGroups.some(group => group.hits.some(hit =>
    hit.spans.length === 2 && hit.spans[0].recordId === pair[0].id && hit.spans[1].recordId === pair[1].id));
  equal(crosses(pageMatch), false);
  equal(crosses(bookMatch), true);

  if (spec.number === 1) {
    const narrative = records.findIndex(record => !record.division);
    const before = records[narrative - 1], after = records[narrative];
    const seam = '"' + [words(before.text).at(-1), words(after.text)[0]].join(' ') + '"';
    const separated = await run(seam, 'book');
    equal(separated.hitGroups.some(group => group.hits.some(hit =>
      hit.spans.some(span => span.recordId === before.id) && hit.spans.some(span => span.recordId === after.id))), false);
    const folded = await run('"vnam nec"', 'section', true);
    equal(folded.hitGroups.some(group => group.recordIds.includes(records[0].id)), true);
    const negative = await run('NOT zzzznonoccurrit', 'book');
    const missing = buildConcordance(negative, records, {readerBase}).unhighlightedUnits;
    equal(missing.length, 1);
    equal(Object.fromEntries(new URL(missing[0].readerURL).searchParams),
      {book: '1', froben: '1', 'froben-view': 'book'});
  }

  bookEvidence.push({book: spec.number, bundle: evidence('bin/search/' + entry.path),
    corpus: evidence('bin/search/' + entry.corpusPath), source: evidence(spec.source),
    ...(spec.additionalSources ? {additionalSources: spec.additionalSources.map(evidence)} : {})});
}

const report = {
  status: 'PASS', source: config.totals, assertions, totalQueries, failedAssertions: 0, examples,
  readerBaseline: {publicationInput: false},
  verifiedFiles: {
    corpus: evidence('bin/search/' + config.corpusPath),
    catalog: evidence('bin/search/catalog.json'),
    engine: evidence('bin/search/engine.mjs'),
    collection: evidence('bin/search/collection.mjs'),
    concordance: evidence('bin/search/concordance.mjs'),
    uiUtils: evidence('bin/search/ui-utils.mjs'),
    extractor: evidence('bin/search/extract-froben.py'),
    manifest: evidence(manifestPath),
    verifier: evidence('bin/search/tests/froben-corpus-qa.mjs'),
    books: bookEvidence,
  },
};
fs.writeFileSync(new URL('bin/search/data/' + id + '/qa-report.json', root), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({status: report.status, ...report.source, assertions, totalQueries}));
