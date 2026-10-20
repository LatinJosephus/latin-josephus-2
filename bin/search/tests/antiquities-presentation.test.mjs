/** Real-source Antiquities I–V citations, reader links, editorial exports and collection integration. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {createCollection} from '../collection.mjs';
import {buildConcordance, exportConcordance} from '../concordance.mjs';
import {
  buildResultCards, citationFor, readerURL, locationState, searchURL,
  editorialText, annotatedTextSegments, passageDivisionLabel, emptySourceNote,
} from '../ui-utils.mjs';
import {validateAntiquitiesSourceProjection} from '../publication.mjs';

const lunr = createRequire(import.meta.url)('../vendor/lunr.cjs');
const directory = new URL('../', import.meta.url);
const read = name => JSON.parse(readFileSync(new URL(name, directory), 'utf8'));
const ANT = 'antiquities-latin-bamberg78', BELLUM = 'bellum-latin-cardwell';
const DEH = 'deh-latin-ussani', CA = 'contra-apionem-latin-boysen';
const catalog = read('catalog.json'), corpus = read(`data/${ANT}/corpus.json`);
const manifest = read(`config/${ANT}.json`);
const readerBase = 'https://latinjosephus.github.io/';
const byCitation = new Map(corpus.map(record => [record.citationLabel, record]));
const reports = new Map(manifest.books.map(book => [book.number, read(`data/${ANT}/book-0${book.number}.extraction-report.json`)]));
const collection = createCollection(catalog, lunr, {
  baseURL: new URL('https://qa.example/assets/search/'),
  fetchImpl: async url => {
    const relative = new URL(url).pathname.replace('/assets/search/', '');
    assert.match(relative, /^data\/(?:bellum-latin-cardwell|deh-latin-ussani|contra-apionem-latin-boysen|antiquities-latin-bamberg78)\/book-0[1-7]\.bundle\.json$/);
    return new Response(readFileSync(new URL(relative, directory)));
  },
});

async function run(query, options = {}, modelOptions = {}) {
  const result = await collection.search(query, {collections: [ANT], books: 'all', scope: 'section', fold: false, ...options});
  const model = buildConcordance(result, result.records, {readerBase, ...modelOptions});
  return {result, model};
}

function csv(model, result) {
  const exported = exportConcordance(model, result, {catalog, exportedAt: '2026-10-20T00:00:00.000Z'});
  assert.equal(exported.text[0], '\uFEFF');
  const rows = [], current = []; let cell = '', quoted = false;
  for (let index = 1; index < exported.text.length; index++) {
    const character = exported.text[index];
    if (character === '"') {
      if (quoted && exported.text[index + 1] === '"') {cell += '"'; index++;}
      else quoted = !quoted;
    } else if (!quoted && character === ',') {current.push(cell); cell = '';}
    else if (!quoted && character === '\r' && exported.text[index + 1] === '\n') {
      current.push(cell); rows.push(current.splice(0)); cell = ''; index++;
    } else cell += character;
  }
  assert.equal(quoted, false); assert.equal(cell, '');
  const headers = rows.shift();
  return {headers, exported, rows: rows.map(values => {
    assert.equal(values.length, headers.length);
    const row = Object.fromEntries(headers.map((name, index) => [name, values[index]]));
    for (const name of JSON.parse(row.escaped_columns_json)) {
      assert.ok(row[name].startsWith("'")); row[name] = row[name].slice(1);
    }
    return row;
  })};
}

test('all 1710 Antiquities citations use the correct narrative or Proem reader route', () => {
  assert.equal(corpus.length, 1710);
  assert.deepEqual(manifest.books.map(book => book.number), [1, 2, 3, 4, 5]);
  assert.deepEqual(catalog.books.filter(book => book.collectionId === ANT).map(book => book.number), [1, 2, 3, 4, 5]);
  assert.equal(manifest.books[0].label, 'Book I (including Proem)');
  for (const record of corpus) {
    const proem = record.book === 1 && record.section <= 26;
    assert.equal(citationFor([record]), `Antiquities ${record.citationLabel}`);
    assert.equal(readerURL(record, readerBase), `${readerBase}antiquities/?book=${proem ? 'preface' : record.book}&niese=${record.section}`);
    assert.equal(readerURL(record, 'https://example.org/project/'), `https://example.org/project${record.url}`);
    assert.equal(readerURL(record, readerBase, {section: false}), `${readerBase}antiquities/?book=${record.book}`);
    assert.equal(record.chapter, undefined, 'a physical medieval division is not a Niese chapter label');
    assert.equal(passageDivisionLabel([record]), `${proem ? 'Proem · ' : ''}Niese section ${record.section}`);
  }
  assert.equal(citationFor(corpus.slice(0, 2)), 'Antiquities I.1–2');
  assert.equal(passageDivisionLabel(corpus.slice(0, 2)), 'Proem · Niese sections 1–2');
  assert.equal(passageDivisionLabel(corpus.slice(26, 28)), 'Niese sections 27–28');
});

test('Antiquities saved selections round-trip, preserve legacy defaults and reject unavailable Book VI', () => {
  const state = {query: '"Historiam conscribere disponentibus"', work: ANT, book: `${ANT}:1`, scope: 'book', fold: true, view: 'concordance'};
  assert.deepEqual(locationState(searchURL(state, `${readerBase}search/`).search, catalog, ''), state);
  assert.equal(locationState(`?q=deus&work=${ANT}&book=3`, catalog, '').book, `${ANT}:3`);
  assert.equal(locationState('', catalog, '').work, BELLUM);
  assert.equal(locationState('?q=bellum&book=all', catalog, '').work, BELLUM);
  assert.throws(() => locationState(`?q=deus&work=${ANT}&book=6`, catalog, ''), /not available/);
});

test('an exact Proem phrase retains original whitespace and points directly to I.1', async () => {
  const {result, model} = await run('"Historiam conscribere disponentibus"');
  assert.deepEqual([result.occurrences, result.matchingUnits], [1, 1]);
  assert.equal(model.rows[0].citation, 'Antiquities I.1');
  assert.equal(model.rows[0].match, 'Historiam conscribere  disponentibus');
  assert.equal(model.rows[0].readerURL, `${readerBase}antiquities/?book=preface&niese=1`);
  const file = csv(model, result);
  assert.equal(file.headers.length, 56);
  assert.equal(file.rows[0].matched_text, model.rows[0].match);
  const segment = JSON.parse(file.rows[0].source_segments_json)[0];
  assert.equal(segment.division, 'proem');
  assert.equal(segment.sourcePath, 'assets/xml/antiquities/Latin/preface.xml');
});

test('added and deleted letters remain literal matches with distinct editorial CSV notation', async () => {
  const addition = await run('"Post hoc secundo die"');
  assert.equal(addition.model.rows.length, 1);
  const added = csv(addition.model, addition.result).rows[0];
  assert.equal(added.citation, 'Antiquities I.30');
  assert.equal(added.matched_text, 'Post hoc secundo die');
  assert.equal(added.matched_text_editorial, 'Post hoc secund⟨o⟩ die');
  assert.match(added.editorial_notes, /added text/);
  const deletion = await run('"Post septimam uero diem"');
  assert.equal(deletion.model.rows.length, 1);
  const deleted = csv(deletion.model, deletion.result).rows[0];
  assert.equal(deleted.citation, 'Antiquities I.34');
  assert.equal(deleted.matched_text, 'Post septimam uero diem');
  assert.equal(deleted.matched_text_editorial, 'Post septima⟦m⟧ uero die⟦m⟧');
  assert.match(deleted.editorial_notes, /deleted text/);
  for (const item of [added, deleted]) {
    const segment = JSON.parse(item.source_segments_json)[0];
    const original = byCitation.get(segment.citationLabel);
    assert.ok(segment.editorialMarks.length);
    for (const mark of segment.editorialMarks) {
      assert.equal(original.text.slice(mark.start, mark.end), mark.text);
      assert.ok(original.editorialMarks.some(candidate => JSON.stringify(candidate) === JSON.stringify(mark)));
    }
  }
});

test('all source editorial spans remain visible and exactly reconstruct their original text', () => {
  let additions = 0, deletions = 0;
  for (const record of corpus) {
    const segments = annotatedTextSegments(record);
    assert.equal(segments.map(segment => segment.text).join(''), record.text);
    for (const mark of record.editorialMarks) {
      if (mark.kind === 'add') additions++;
      if (mark.kind === 'del') deletions++;
      assert.equal(record.text.slice(mark.start, mark.end), mark.text);
      assert.ok(segments.some(segment => segment.marks.includes(mark)));
    }
  }
  assert.deepEqual([additions, deletions], [19, 23]);
  assert.ok(editorialText(byCitation.get('I.30')).includes('[⟨ipsumque⟩]'));
  assert.ok(editorialText(byCitation.get('I.34')).includes('quem<⟦...⟧>'));
});

test('all six continuing medieval paragraphs remain single-section exact phrase matches', async () => {
  const fixtures = [
    ['II.95', 'pestis inuaserat misit etiam'],
    ['III.178', 'habet inscriptum Hoc est'],
    ['IV.106', 'gente suspenderet Cumque dixisset'],
    ['IV.155', 'sunt extincti Perempti sunt'],
    ['IV.276', 'in pedire Nemo blasphemet'],
    ['V.32', 'recondenda contradidit Hoc ergo'],
  ];
  for (const [citation, phrase] of fixtures) {
    const {result, model} = await run(`"${phrase}"`);
    assert.deepEqual([result.occurrences, result.matchingUnits], [1, 1], citation);
    assert.equal(model.rows[0].citation, `Antiquities ${citation}`);
    assert.ok(model.rows[0].match.includes('\n\n'), citation);
    const segment = JSON.parse(csv(model, result).rows[0].source_segments_json)[0];
    assert.deepEqual(segment.sourceIds, byCitation.get(citation).sourceIds);
    assert.equal(segment.sourceIds.length, 2);
    assert.equal(segment.text, byCitation.get(citation).text.slice(segment.start, segment.end));
  }
});

test('ordinary Niese seams allow whole-book phrases while Proem and omission boundaries stop them', async () => {
  const ordinary = '"lumen iussit Quo facto"';
  assert.equal((await run(ordinary)).result.occurrences, 0);
  const joined = await run(ordinary, {books: [`${ANT}:1`], scope: 'book'});
  assert.equal(joined.result.occurrences, 1);
  assert.equal(joined.model.rows[0].citation, 'Antiquities I.27–28');
  assert.equal(joined.model.rows[0].records.length, 2);
  for (const [phrase, book] of [['"ita conscripta In principio"', 1], ['"pro peccatis Offerunt autem"', 3]]) {
    assert.equal((await run(phrase, {books: [`${ANT}:${book}`], scope: 'book'})).result.occurrences, 0);
  }
  assert.equal((await run('conscripta AND principio', {books: [`${ANT}:1`], scope: 'book'})).result.matchingUnits, 1);
  assert.equal((await run('peccatis AND Offerunt', {books: [`${ANT}:3`], scope: 'book'})).result.matchingUnits, 1);
});

test('literal dotted interruptions preserve words and metadata without permitting phrases across them', async () => {
  const blocked = await run('"con perit"', {books: [`${ANT}:1`], scope: 'book'});
  assert.equal(blocked.result.occurrences, 0);
  const related = await run('con AND perit', {books: [`${ANT}:1`]});
  assert.ok(related.result.hitGroups.some(group => group.recordIds.includes(byCitation.get('I.53').id)));
  const literal = await run('quem', {books: [`${ANT}:1`]}, {contextWords: 4});
  const rows = csv(literal.model, literal.result).rows.filter(row => row.citation === 'Antiquities I.34');
  assert.equal(rows.length, 1);
  const segment = JSON.parse(rows[0].source_segments_json)[0];
  assert.deepEqual(segment.textGaps, byCitation.get('I.34').textGaps);
  assert.deepEqual(segment.phraseBreaks, [257]);
  assert.equal(segment.sourceMarkup.length, 3);
  assert.ok(segment.sourceMarkup.every(mark => mark.kind === 'ref' && mark.sourceAttributes.target.startsWith('note_')));
});

test('empty III.240 remains a negative-only result with explanatory text and a zero-width source gap in CSV', async () => {
  const {result, model} = await run('NOT zzzznonoccurrit', {books: [`${ANT}:3`]});
  assert.deepEqual([result.matchingUnits, result.occurrences], [322, 0]);
  assert.equal(model.rows.length, 0);
  assert.equal(model.unhighlightedUnits.length, 322);
  const gap = byCitation.get('III.240');
  assert.equal(emptySourceNote(gap), 'Text marked as omitted in the source.');
  assert.equal(emptySourceNote(byCitation.get('III.239')), '');
  const card = buildResultCards(result, result.records).find(item => item.records.some(record => record.id === gap.id));
  assert.ok(card);
  assert.equal(card.records[0].text, '');
  const file = csv(model, result), row = file.rows.find(item => item.citation === 'Antiquities III.240');
  assert.equal(file.headers.length, 56);
  assert.equal(file.rows.length, 322);
  assert.equal(row.row_type, 'matching-unit');
  assert.equal(row.matched_text, '');
  assert.equal(row.reader_url, `${readerBase}antiquities/?book=3&niese=240`);
  assert.match(row.editorial_notes, /^Text marked as omitted in the source\./);
  const segment = JSON.parse(row.source_segments_json)[0];
  assert.deepEqual([segment.start, segment.end, segment.text], [0, 0, '']);
  assert.deepEqual(segment.textGaps, gap.textGaps);
  assert.deepEqual(segment.phraseBreaks, [0]);
  assert.deepEqual(segment.sourceIds, ['latin-book03-num239']);
  assert.equal((await run('omitted', {books: [`${ANT}:3`]})).result.occurrences, 0, 'the display note is not searchable Latin');
});

test('zero-result Antiquities CSV retains all 56 columns, selected-source fingerprints and query settings', async () => {
  const {result, model} = await run('zzzznonoccurrit*');
  const file = csv(model, result);
  assert.equal(result.matchingUnits, 0);
  assert.equal(file.headers.length, 56);
  assert.equal(file.exported.rowCount, 0);
  assert.equal(file.rows.length, 1);
  assert.equal(file.rows[0].row_type, 'search-summary');
  assert.equal(file.rows[0].query, 'zzzznonoccurrit*');
  assert.match(file.rows[0].editorial_notes, /Antiquities includes the Proem and Books I–V/);
  const sources = JSON.parse(file.rows[0].selected_sources_json);
  assert.deepEqual(sources.collections.map(source => source.id), [ANT]);
  assert.deepEqual(sources.books.map(book => book.id), [1, 2, 3, 4, 5].map(book => `${ANT}:${book}`));
  assert.ok(sources.books.every(book => /^[a-f0-9]{64}$/.test(book.corpusSHA256)));
});

test('a frequent Antiquities word exports all 3177 occurrences beyond the first display page', async () => {
  const {result, model} = await run('et', {}, {contextWords: 2});
  assert.equal(result.occurrences, 3177);
  assert.equal(model.rows.length, 3177);
  const firstPage = model.rows.slice(0, 50);
  assert.equal(firstPage.length, 50);
  const file = csv(model, result);
  assert.equal(file.headers.length, 56);
  assert.equal(file.exported.rowCount, 3177);
  assert.equal(file.rows.length, 3177);
  assert.equal(new Set(model.rows.map(row => row.key)).size, 3177);
  assert.ok(file.rows.every(row => row.matched_text.toLowerCase() === 'et'));
  assert.equal(file.rows.at(-1).reader_url, model.rows.at(-1).readerURL);
  assert.ok(file.rows.some(row => row.reader_url.includes('book=preface')));
  assert.deepEqual([...new Set(file.rows.map(row => Number(row.book)))], [1, 2, 3, 4, 5]);
});

test('all four works retain separate identities and export 308 sacerdot* occurrences from 217 units', async () => {
  const {result, model} = await run('sacerdot*', {collections: 'all'});
  assert.deepEqual(result.selectedCollections, [BELLUM, DEH, CA, ANT]);
  assert.equal(result.selectedBooks.length, 19);
  assert.equal(result.records.length, 6885);
  assert.equal(new Set(result.records.map(record => record.id)).size, 6885);
  assert.deepEqual([result.occurrences, result.matchingUnits], [308, 217]);
  const file = csv(model, result);
  assert.equal(file.headers.length, 56); assert.equal(file.rows.length, 308);
  assert.deepEqual([BELLUM, DEH, CA, ANT].map(id => file.rows.filter(row => row.collection_id === id).length), [35, 125, 34, 114]);
  assert.ok(file.rows.filter(row => row.collection_id === ANT).every(row => row.citation_scheme === 'niese' && row.reader_url.includes('/antiquities/')));
  const selected = JSON.parse(file.rows[0].selected_sources_json);
  assert.equal(selected.books.length, 19);
  assert.equal(selected.collections.length, 4);
  const alone = await run('sacerdot*');
  assert.deepEqual([alone.result.occurrences, alone.result.matchingUnits], [114, 99]);
  assert.deepEqual(alone.result.selectedCollections, [ANT]);
});

test('negative-only whole-book exports retain all 19 book identities and numeric Book I links', async () => {
  const {result, model} = await run('NOT zzzznonoccurrit', {collections: 'all', scope: 'book'});
  assert.deepEqual([result.matchingUnits, result.occurrences], [19, 0]);
  assert.equal(model.unhighlightedUnits.length, 19);
  const file = csv(model, result);
  assert.equal(file.rows.length, 19);
  assert.ok(file.rows.every(row => row.row_type === 'matching-unit' && row.matched_text === '' && row.source_segments_json === '[]'));
  const antiquities = file.rows.filter(row => row.collection_id === ANT);
  assert.deepEqual(antiquities.map(row => row.reader_url), [1, 2, 3, 4, 5].map(book => `${readerBase}antiquities/?book=${book}`));
  assert.deepEqual(antiquities.map(row => row.citation), ['Antiquities I', 'Antiquities II', 'Antiquities III', 'Antiquities IV', 'Antiquities V']);
});

test('identically numbered books from different works cannot jointly satisfy an AND or phrase', async () => {
  const selected = {collections: [BELLUM, DEH, CA, ANT], books: [BELLUM, DEH, CA, ANT].map(id => `${id}:1`)};
  const bellumOnly = await run('abditissima', {...selected, scope: 'book'});
  const antiquitiesOnly = await run('abscessimus', {...selected, scope: 'book'});
  assert.deepEqual(bellumOnly.result.matchingBooks, [`${BELLUM}:1`]);
  assert.deepEqual(antiquitiesOnly.result.matchingBooks, [`${ANT}:1`]);
  for (const scope of ['section', 'book']) {
    assert.equal((await run('abditissima AND abscessimus', {...selected, scope})).result.matchingUnits, 0);
    const either = await run('abditissima OR abscessimus', {...selected, scope});
    assert.deepEqual(either.result.matchingBooks, [`${BELLUM}:1`, `${ANT}:1`]);
    assert.equal((await run('"regis hic finis fuit Historiam conscribere disponentibus"', {...selected, scope})).result.occurrences, 0);
  }
});

test('publication accepts complete source projections for all five books and rejects record metadata corruption', () => {
  for (const spec of manifest.books) {
    validateAntiquitiesSourceProjection(corpus.filter(record => record.book === spec.number), reports.get(spec.number), manifest, spec);
  }
  const cases = [
    [1, records => {records[0].sourcePath = 'assets/xml/antiquities/Latin/book-01.xml';}],
    [1, records => {records[0].readerLink.params.book = 1;}],
    [1, records => {records[0].url = '/antiquities/?book=1&niese=1';}],
    [1, records => {delete records[0].division;}],
    [1, records => {records[26].chapter = 1;}],
    [1, records => {records[33].editorialMarks[0].sourceAttributes.hand = 'invented';}],
    [1, records => {records[33].sourceMarkup[0].start++;}],
    [1, records => {records[33].sourceMarkup[0].sourceAttributes.target = 'invented';}],
    [1, records => {records[33].textGaps[0].end--;}],
    [1, records => {records[33].phraseBreaks = [];}],
    [3, records => {records[177].sourceIds.pop();}],
    [3, records => {records[239].text = 'lacuna';}],
    [3, records => {records[239].textGaps = [];}],
    [3, records => {records[239].textGaps[0].sourceAttributes.reason = 'unknown';}],
    [3, records => {records[240].breakBefore = false;}],
  ];
  for (const [book, mutate] of cases) {
    const original = corpus.filter(record => record.book === book), changed = structuredClone(original);
    mutate(changed);
    assert.throws(() => validateAntiquitiesSourceProjection(changed, reports.get(book), manifest, manifest.books[book - 1]));
  }
});

test('publication rejects corrupt source paragraph slices, omissions, source inventories and published marker audits', () => {
  const cases = [
    [1, report => {report.paragraphs[0].segments.find(segment => segment.kind === 'source-text').recordTextStart++;}],
    [1, report => {report.paragraphs[0].segments[0].sourceTextStart++;}],
    [1, report => {report.paragraphs.find(paragraph => paragraph.segments.some(segment => segment.kind === 'excluded-note')).segments.find(segment => segment.kind === 'excluded-note').text += 'x';}],
    [1, report => {report.paragraphs[0].sourcePath = 'assets/xml/antiquities/Latin/book-02.xml';}],
    [1, report => {report.sources[0].sha256 = '0'.repeat(64);}],
    [1, report => {report.sectionAudits[33].sourceMarkup[0].sourceAttributes.target = 'invented';}],
    [1, report => {report.sectionAudits[33].phraseBreaks = [];}],
    [3, report => {report.coverage.allowedEmptySections = [];}],
    [3, report => {report.coverage.allSectionTextsNonempty = true;}],
    [3, report => {report.sectionAudits[239].textGaps = [];}],
  ];
  for (const [book, mutate] of cases) {
    const changed = structuredClone(reports.get(book)); mutate(changed);
    assert.throws(() => validateAntiquitiesSourceProjection(corpus.filter(record => record.book === book), changed, manifest, manifest.books[book - 1]));
  }
  const changedSpec = {...manifest.books[0], additionalSources: []};
  assert.throws(() => validateAntiquitiesSourceProjection(corpus.filter(record => record.book === 1), reports.get(1), manifest, changedSpec));
});
