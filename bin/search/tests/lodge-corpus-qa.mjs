/** Verify the searchable Lodge text against the certified XML and live reader routes. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {createCollection} from '../collection.mjs';
import {buildConcordance, exportConcordance} from '../concordance.mjs';
import {readerURL} from '../ui-utils.mjs';

const root = new URL('../../../', import.meta.url);
const readerBase = 'https://qa.invalid/preview/';
const lunr = createRequire(import.meta.url)('../vendor/lunr.cjs');
const read = name => fs.readFileSync(new URL(name, root));
const json = name => JSON.parse(read(name));
const evidence = path => {
  const bytes = read(path);
  return {path, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')};
};
const words = text => [...text.matchAll(/[\p{L}\p{N}][\p{L}\p{N}\p{M}]*/gu)].map(match => match[0]);
const normalize = word => word.normalize('NFC').toLowerCase().replaceAll('ς', 'σ').replaceAll('æ', 'ae');
const catalog = json('bin/search/catalog.json');
const search = createCollection(catalog, lunr, {
  baseURL: 'https://qa.invalid/',
  fetchImpl: async url => new Response(read('bin/search' + url.pathname)),
});

for (const config of catalog.collections.filter(entry => entry.edition === 'Lodge (1602)')) {
  const manifestPath = 'bin/search/config/' + config.id + '.json';
  const manifest = json(manifestPath);
  const sourceFiles = manifest.books.flatMap(book => [...(book.additionalSources || []), book.source]);
  const witnessPath = 'bin/search/tests/lodge-source-witness.py';
  const witness = JSON.parse(execFileSync(process.env.SEARCH_PYTHON || process.env.PYTHON || 'python3',
    [fileURLToPath(new URL(witnessPath, root)), fileURLToPath(root), ...sourceFiles],
    {encoding: 'utf8', maxBuffer: 24 * 1024 * 1024}));
  const verifiedBooks = [];
  let assertions = 0;
  let totalQueries = 0;
  function equal(actual, expected, message) {
    assertions++;
    assert.deepEqual(actual, expected, message);
  }
  for (const spec of manifest.books) {
    const entry = catalog.books.find(book => book.id === config.id + ':' + spec.number);
    const {records} = await search.loadBooks([entry.id]);
    const expected = [...(spec.additionalSources || []), spec.source].flatMap(name => witness[name]);
    equal(records.map(row => [row.section, row.sourceId, row.text]), expected, 'Lodge prose and citations in physical source order');
    equal(records.reduce((sum, row) => sum + words(row.text).length, 0), entry.tokens, 'Independent source word count');
    for (const row of records) {
      const url = new URL(readerURL(row, readerBase));
      equal(url.pathname, '/preview/' + manifest.readerPath);
      equal(Object.fromEntries(url.searchParams), {
        book: row.division === 'proem' ? 'preface' : String(spec.number), niese: String(row.section), english: 'lodge1602',
      });
      equal((row.textGaps || []).map(gap => row.text.slice(gap.start, gap.end)),
        row.text ? [...row.text.matchAll(/\[…\]/gu)].map(match => match[0]) : row.emptySource ? [] : ['']);
    }
    const sample = words(records.at(-1).text).find(word => word.length > 5);
    const run = async (query, scope = 'section', fold = false) => {
      totalQueries++;
      return search.search(query, {books: [entry.id], scope, fold});
    };
    const result = await run(sample, 'section', true);
    equal(result.occurrences, records.flatMap(row => words(row.text)).filter(word => normalize(word) === normalize(sample)).length);
    equal(result.normalization.foldedCollectionIds, [], 'English ignores Latin equivalence');
    const concordance = buildConcordance(result, records, {readerBase});
    equal(exportConcordance(concordance, result, {catalog, exportedAt: '2026-11-06T00:00:00Z'}).rowCount, result.occurrences);
    equal(concordance.rows.every(row => new URL(row.readerURL).searchParams.get('english') === 'lodge1602'), true);

    async function verifySeam(left, right, expected) {
      const query = '"' + [words(left.text).at(-1), words(right.text)[0]].join(' ') + '"';
      const crossing = (await run(query, 'book')).hitGroups.some(group =>
        group.hits.some(hit => hit.spans.length === 2 && hit.spans[0].recordId === left.id && hit.spans[1].recordId === right.id));
      equal(crossing, expected, 'Lodge whole-book phrase boundary');
    }
    const ordinary = records.findIndex((row, index) => index && row.text && records[index - 1].text &&
      !row.breakBefore && !row.textGaps && !records[index - 1].textGaps);
    await verifySeam(records[ordinary - 1], records[ordinary], true);
    if (spec.additionalSources) await verifySeam(records[25], records[26], false);
    if (spec.omittedSections) await verifySeam(records[1], records[3], false);
    verifiedBooks.push({book: spec.number, bundle: evidence('bin/search/' + entry.path),
      corpus: evidence('bin/search/' + entry.corpusPath), source: evidence(spec.source),
      ...(spec.additionalSources ? {additionalSources: spec.additionalSources.map(evidence)} : {})});
  }
  const report = {
    status: 'PASS', source: config.totals, assertions, totalQueries, failedAssertions: 0,
    readerBaseline: {publicationInput: false},
    verifiedFiles: {corpus: evidence('bin/search/' + config.corpusPath), catalog: evidence('bin/search/catalog.json'),
      engine: evidence('bin/search/engine.mjs'), collection: evidence('bin/search/collection.mjs'),
      concordance: evidence('bin/search/concordance.mjs'), uiUtils: evidence('bin/search/ui-utils.mjs'),
      extractor: evidence('bin/search/extract-lodge.py'), manifest: evidence(manifestPath), witness: evidence(witnessPath),
      verifier: evidence('bin/search/tests/lodge-corpus-qa.mjs'), books: verifiedBooks},
  };
  fs.writeFileSync(new URL('bin/search/data/' + config.id + '/qa-report.json', root), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({collection: config.id, status: report.status, ...report.source, assertions, totalQueries}));
}
