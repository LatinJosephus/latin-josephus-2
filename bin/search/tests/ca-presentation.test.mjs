/** Real-source citations, source markings, complete exports and three-work integration. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {createCollection} from '../collection.mjs';
import {buildConcordance, exportConcordance} from '../concordance.mjs';
import {citationFor, readerURL, locationState, searchURL, editorialText, passageDivisionLabel} from '../ui-utils.mjs';
import {validateCaSourceProjection} from '../publication.mjs';

const lunr = createRequire(import.meta.url)('../vendor/lunr.cjs');
const directory = new URL('../', import.meta.url);
const read = name => JSON.parse(readFileSync(new URL(name, directory), 'utf8'));
const catalog = read('catalog.json'), corpus = read('data/contra-apionem-latin-boysen/corpus.json');
const manifest = read('config/contra-apionem-latin-boysen.json');
const CA = 'contra-apionem-latin-boysen', DEH = 'deh-latin-ussani', BELLUM = 'bellum-latin-cardwell';
const readerBase = 'https://latinjosephus.github.io/';
const collection = createCollection(catalog, lunr, {
  baseURL: new URL('https://qa.example/assets/search/'),
  fetchImpl: async url => {
    const relative = new URL(url).pathname.replace('/assets/search/', '');
    assert.match(relative, /^data\/(?:bellum-latin-cardwell|deh-latin-ussani|contra-apionem-latin-boysen)\/book-0[1-7]\.bundle\.json$/);
    return new Response(readFileSync(new URL(relative, directory)));
  },
});
async function run(query, options = {}) {
  const result = await collection.search(query, {collections: [CA], books: 'all', scope: 'section', fold: false, ...options});
  const model = buildConcordance(result, result.records, {readerBase});
  return {result, model};
}
function csv(model, result) {
  const exported = exportConcordance(model, result, {catalog, exportedAt: '2026-10-19T15:00:00.000Z'});
  const text = exported.text;
  assert.equal(text[0], '\uFEFF');
  const rows = [], current = []; let cell = '', quoted = false;
  for (let i = 1; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (quoted && text[i + 1] === '"') {cell += '"'; i++;}
      else quoted = !quoted;
    } else if (!quoted && c === ',') {current.push(cell); cell = '';}
    else if (!quoted && c === '\r' && text[i + 1] === '\n') {current.push(cell); rows.push(current.splice(0)); cell = ''; i++;}
    else cell += c;
  }
  assert.equal(quoted, false); assert.equal(cell, '');
  const headers = rows.shift();
  return {headers, exported, rows: rows.map(values => {
    assert.equal(values.length, headers.length);
    const row = Object.fromEntries(headers.map((name, i) => [name, values[i]]));
    for (const name of JSON.parse(row.escaped_columns_json)) {assert.ok(row[name].startsWith("'")); row[name] = row[name].slice(1);}
    return row;
  })};
}

test('all 616 CA Niese citations and links preserve the existing reader identities', () => {
  assert.equal(corpus.length, 616);
  for (const record of corpus) {
    assert.equal(citationFor([record]), `Contra Apionem ${record.citationLabel}`);
    assert.equal(readerURL(record, readerBase), new URL(record.url, readerBase).href);
    assert.equal(readerURL(record, 'https://example.org/project/'), `https://example.org/project${record.url}`);
    assert.equal(record.chapter, undefined, 'a Niese section may contain a Boysen chapter boundary');
  }
  assert.equal(citationFor(corpus.slice(0, 2)), 'Contra Apionem I.1–2');
});

test('CA saved selections round-trip without changing Bellum and DEH link interpretation', () => {
  const state = {query: '"duo et uiginti libri"', work: CA, book: `${CA}:1`, scope: 'book', fold: true, view: 'concordance'};
  assert.deepEqual(locationState(searchURL(state, `${readerBase}search/`).search, catalog, ''), state);
  assert.equal(locationState('?q=bellum&book=all', catalog, '').work, BELLUM);
  assert.equal(locationState('', catalog, '').work, BELLUM);
  assert.equal(locationState(`?q=Cenedaei&work=${DEH}&book=2`, catalog, '').book, `${DEH}:2`);
});

test('passage metadata uses CA Niese divisions and retains the other works chapter labels', () => {
  for(const record of corpus)assert.equal(passageDivisionLabel([record]), `Niese section ${record.section}`);
  const overlap=corpus.filter(record=>record.book===2&&[120,121].includes(record.section));
  assert.equal(passageDivisionLabel(overlap), 'Niese sections 120–121');
  assert.equal(passageDivisionLabel([{work:'bellum',chapter:0}]), 'Proem');
  assert.equal(passageDivisionLabel([{work:'bellum',chapter:4}]), 'Chapter 4');
  assert.equal(passageDivisionLabel([{work:'deh',citationScheme:'chapter-paragraph',chapter:0}]), 'Prologue');
  assert.equal(passageDivisionLabel([{work:'deh',chapter:1},{work:'deh',chapter:2}]), 'Across chapters');
});

test('CA word and wildcard counts export every occurrence and retain both selected books', async () => {
  const {result, model} = await run('sacerdot*');
  assert.deepEqual([result.occurrences, result.matchingUnits], [34, 30]);
  assert.deepEqual([1, 2].map(book => model.rows.filter(row => row.book === book).length), [18, 16]);
  const file = csv(model, result);
  assert.equal(file.headers.length, 56); assert.equal(file.rows.length, 34);
  assert.deepEqual(JSON.parse(file.rows[0].selected_sources_json).books.map(book => book.id), [`${CA}:1`, `${CA}:2`]);
  const second = await run('sacerdot*', {books: [`${CA}:2`]});
  const subset = csv(second.model, second.result);
  assert.equal(subset.rows.length, 16); assert.equal(subset.headers.length, 56);
  assert.ok(subset.rows.every(row => row.book === '2' && row.collection_id === CA));
});

test('all three works export 194 distinct sacerdot* occurrences with their own citation schemes', async () => {
  const {result, model} = await run('sacerdot*', {collections: 'all'});
  assert.deepEqual(result.selectedCollections, [BELLUM, DEH, CA]);
  assert.equal(result.selectedBooks.length, 14);
  assert.deepEqual([result.occurrences, result.matchingUnits], [194, 118]);
  const file = csv(model, result);
  assert.equal(file.rows.length, 194); assert.equal(file.headers.length, 56);
  assert.deepEqual([BELLUM, DEH, CA].map(id => file.rows.filter(row => row.collection_id === id).length), [35, 125, 34]);
  assert.ok(file.rows.filter(row => row.collection_id === CA).every(row => row.citation_scheme === 'niese' && row.reader_url.includes('/contra-apionem/')));
  assert.equal(JSON.parse(file.rows[0].selected_sources_json).books.length, 14);
});

test('the encoded CA addition stays literal in matches and visibly annotated in exports', async () => {
  const {result, model} = await run('"languentium milia trecenta"');
  assert.equal(model.rows.length, 1);
  const row = model.rows[0], file = csv(model, result).rows[0];
  assert.equal(row.citation, 'Contra Apionem I.290');
  assert.equal(row.match, 'languentium milia trecenta');
  assert.equal(file.matched_text_editorial, 'languentium ⟨milia⟩ trecenta');
  assert.match(file.editorial_notes, /added text/);
  const segment = JSON.parse(file.source_segments_json)[0];
  assert.deepEqual(segment.editorialMarks, corpus.find(record => record.section === 290 && record.book === 1).editorialMarks);
});

test('Greek source quotations and the printed word-internal page break retain exact searchable text', async () => {
  const greek = await run('"ἀπὸ τῆς ἱεροσυλίας"');
  assert.equal(greek.model.rows.length, 2);
  const file = csv(greek.model, greek.result);
  assert.deepEqual(file.rows.map(row => row.citation), ['Contra Apionem I.311', 'Contra Apionem I.318']);
  for (const row of file.rows) {
    assert.equal(row.matched_text, 'ἀπὸ τῆς ἱεροσυλίας');
    assert.ok(JSON.parse(row.source_segments_json)[0].sourceMarkup.some(mark => mark.kind === 'foreign' && mark.language === 'grc'));
  }
  const word = await run('praecellentes');
  assert.equal(word.model.rows.length, 1);
  assert.equal(word.model.rows[0].citation, 'Contra Apionem II.186');
  assert.equal(word.model.rows[0].match, 'praecellentes');
});

test('ordinary CA section seams allow whole-book phrases and marked seams prevent them', async () => {
  assert.equal((await run('"conscripsi quoniam"')).result.occurrences, 0);
  const ordinary = await run('"conscripsi quoniam"', {scope: 'book'});
  assert.equal(ordinary.model.rows.length, 1);
  assert.equal(ordinary.model.rows[0].citation, 'Contra Apionem I.1–2');
  assert.equal((await run('"Herculis fecit"', {scope: 'book'})).result.occurrences, 0);
  assert.equal((await run('Herculis AND fecit', {scope: 'book'})).result.matchingUnits, 1);
});

test('negative-only results retain all 14 book citations without inventing an occurrence', async () => {
  const {result, model} = await run('NOT zzzznonoccurrit', {collections: 'all', scope: 'book'});
  assert.equal(result.matchingUnits, 14); assert.equal(result.occurrences, 0);
  assert.equal(model.rows.length, 0); assert.equal(model.unhighlightedUnits.length, 14);
  const file = csv(model, result);
  assert.equal(file.rows.length, 14);
  assert.ok(file.rows.every(row => row.row_type === 'matching-unit' && row.matched_text === ''));
  assert.deepEqual(file.rows.filter(row => row.collection_id === CA).map(row => row.reader_url), [
    `${readerBase}contra-apionem/?book=1`, `${readerBase}contra-apionem/?book=2`,
  ]);
});

test('publication rejects changed CA gap, addition, citation and restoration metadata', () => {
  const original = corpus.filter(record => record.book === 1), spec = manifest.books[0];
  const report = read('data/contra-apionem-latin-boysen/book-01.extraction-report.json');
  validateCaSourceProjection(original, report, manifest, spec);
  for (const mutate of [
    records => {records[117].phraseBreaks = [];},
    records => {records[117].textGaps = [];},
    records => {records[118].breakBefore = false;},
    records => {records[289].editorialMarks = [];},
    records => {records[0].url = '/bellum-judaicum/?book=1&niese=1';},
    records => {records[0].chapter = 1;},
    records => {records[0].text += '.';},
  ]) {
    const changed = structuredClone(original); mutate(changed);
    assert.throws(() => validateCaSourceProjection(changed, report, manifest, spec));
  }
  assert.equal(editorialText(original[289]).includes('⟨milia⟩'), true);
});
