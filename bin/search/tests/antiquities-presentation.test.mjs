/** Real-source Antiquities I–XX citations, reader links, editorial exports and collection integration. */
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
const originalCorpus = corpus.filter(record => record.book <= 10);
const originalAntiquitiesBooks = Array.from({length: 10}, (_, index) => `${ANT}:${index + 1}`);
const allAntiquitiesBooks = Array.from({length: 20}, (_, index) => index + 1);
const originalCollectionBooks = catalog.books.filter(book => book.collectionId !== ANT || book.number <= 10).map(book => book.id);
const readerBase = 'https://latinjosephus.github.io/';
const byCitation = new Map(corpus.map(record => [record.citationLabel, record]));
const reports = new Map(manifest.books.map(book => [book.number, read(`data/${ANT}/book-${String(book.number).padStart(2, '0')}.extraction-report.json`)]));
const collection = createCollection(catalog, lunr, {
  baseURL: new URL('https://qa.example/assets/search/'),
  fetchImpl: async url => {
    const relative = new URL(url).pathname.replace('/assets/search/', '');
    assert.match(relative, /^data\/(?:bellum-latin-cardwell|deh-latin-ussani|contra-apionem-latin-boysen|antiquities-latin-bamberg78)\/book-(?:0[1-9]|1[0-9]|20)\.bundle\.json$/);
    return new Response(readFileSync(new URL(relative, directory)));
  },
});

async function run(query, options = {}, modelOptions = {}) {
  const result = await collection.search(query, {collections: [ANT], books: originalAntiquitiesBooks, scope: 'section', fold: false, ...options});
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

test('all 3415 published Antiquities I–X citations keep their narrative or Proem reader route', () => {
  assert.equal(originalCorpus.length, 3415);
  assert.equal(corpus.length, 7283);
  assert.deepEqual(manifest.books.map(book => book.number), allAntiquitiesBooks);
  assert.deepEqual(catalog.books.filter(book => book.collectionId === ANT).map(book => book.number), allAntiquitiesBooks);
  assert.equal(manifest.books[0].label, 'Book I (including Proem)');
  for (const record of originalCorpus) {
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

test('Antiquities saved selections round-trip through Book XX and preserve legacy defaults', () => {
  const state = {query: '"Historiam conscribere disponentibus"', work: ANT, book: `${ANT}:1`, scope: 'book', fold: true, view: 'concordance'};
  assert.deepEqual(locationState(searchURL(state, `${readerBase}search/`).search, catalog, ''), state);
  assert.equal(locationState(`?q=deus&work=${ANT}&book=3`, catalog, '').book, `${ANT}:3`);
  assert.equal(locationState('', catalog, '').work, BELLUM);
  assert.equal(locationState('?q=bellum&book=all', catalog, '').work, BELLUM);
  assert.equal(locationState(`?q=deus&work=${ANT}&book=10`, catalog, '').book, `${ANT}:10`);
  assert.equal(locationState(`?q=deus&work=${ANT}&book=15`, catalog, '').book, `${ANT}:15`);
  for (const book of [16, 17, 18, 19, 20]) {
    assert.equal(locationState(`?q=deus&work=${ANT}&book=${book}`, catalog, '').book, `${ANT}:${book}`);
  }
  assert.throws(() => locationState(`?q=deus&work=${ANT}&book=21`, catalog, ''), /not available/);
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

test('all published I–X editorial spans remain visible and exactly reconstruct their original text', () => {
  let additions = 0, deletions = 0, uncertain = 0;
  for (const record of originalCorpus) {
    const segments = annotatedTextSegments(record);
    assert.equal(segments.map(segment => segment.text).join(''), record.text);
    for (const mark of record.editorialMarks) {
      if (mark.kind === 'add') additions++;
      if (mark.kind === 'del') deletions++;
      if (mark.kind === 'unclear') uncertain++;
      assert.equal(record.text.slice(mark.start, mark.end), mark.text);
      assert.ok(segments.some(segment => segment.marks.includes(mark)));
    }
  }
  assert.deepEqual([additions, deletions, uncertain], [45, 30, 63]);
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

test('both Book VIII continuations preserve cross-paragraph exact phrases and their actual Niese citations', async () => {
  for (const [citation, query] of [['VIII.186', 'gratus et locuplex Huc ergo'], ['VIII.255', 'ad ierosolimam uenit ubi roboam']]) {
    const {result, model} = await run(`"${query}"`, {books: [`${ANT}:8`]});
    assert.deepEqual([result.occurrences, result.matchingUnits], [1, 1]);
    assert.equal(model.rows[0].citation, `Antiquities ${citation}`);
    assert.ok(model.rows[0].match.includes('\n\n'));
    const segment = JSON.parse(csv(model, result).rows[0].source_segments_json)[0];
    assert.deepEqual(segment.sourceIds, byCitation.get(citation).sourceIds);
  }
});

test('the 31 Book VII omissions appear in NOT-only results with source evidence and no indexed English notice', async () => {
  const {result, model} = await run('NOT *', {books: [`${ANT}:7`]});
  assert.deepEqual([result.matchingUnits, result.occurrences], [31, 0]);
  const file = csv(model, result);
  assert.deepEqual(file.rows.map(row => row.citation), Array.from({length: 31}, (_, index) => `Antiquities VII.${index + 69}`));
  for (const row of file.rows) {
    assert.equal(row.row_type, 'matching-unit');
    assert.equal(row.matched_text, '');
    assert.match(row.editorial_notes, /^Text marked as omitted in the source\./);
    const segment = JSON.parse(row.source_segments_json)[0];
    assert.deepEqual(segment.phraseBreaks, [0]);
    assert.deepEqual(segment.textGaps, [{kind: 'tei-gap', start: 0, end: 0, text: '', sourceAttributes: {reason: 'omitted'}}]);
  }
  assert.equal((await run('Omitted OR Bamberg', {books: [`${ANT}:7`]})).result.occurrences, 0);
});

test('Book IX retains its missing 51–109 range in exports without synthetic negative-only records', async () => {
  const {result, model} = await run('NOT zzzznonoccurrit', {books: [`${ANT}:9`]});
  assert.deepEqual([result.matchingUnits, result.occurrences], [232, 0]);
  const file = csv(model, result);
  assert.deepEqual(file.rows.map(row => Number(row.citation.split('.').at(-1))),
    [...Array.from({length: 50}, (_, index) => index + 1), ...Array.from({length: 182}, (_, index) => index + 110)]);
  const sources = JSON.parse(file.rows[0].selected_sources_json);
  assert.deepEqual(sources.books[0].sectionRange, [1, 291]);
  assert.deepEqual(sources.books[0].missingSections, Array.from({length: 59}, (_, index) => index + 51));
  assert.equal((await run('Blatt OR Lacuna', {books: [`${ANT}:9`]})).result.occurrences, 0);
  const firstAfter = file.rows.find(row => row.citation === 'Antiquities IX.110');
  const segment = JSON.parse(firstAfter.source_segments_json)[0];
  assert.equal(segment.text, '[…] Nam uerba uesaniae locutus est');
  assert.equal(segment.breakBefore, true);
  assert.deepEqual(segment.textGaps, [{kind: 'literal-ellipsis', start: 1, end: 2, text: '…'}]);
});

test('X108 exports the exact empty-source interval and factual note without an invented omission tag', async () => {
  const {result, model} = await run('NOT *', {books: [`${ANT}:10`]});
  assert.deepEqual([result.matchingUnits, result.occurrences], [1, 0]);
  const record = byCitation.get('X.108');
  assert.equal(emptySourceNote(record), 'No Latin text occurs between this citation label and the next Niese marker.');
  const card = buildResultCards(result, result.records)[0];
  assert.equal(card.records[0].id, record.id);
  const row = csv(model, result).rows[0];
  assert.equal(row.citation, 'Antiquities X.108');
  assert.equal(row.reader_url, `${readerBase}antiquities/?book=10&niese=108`);
  assert.match(row.editorial_notes, /^No Latin text occurs between this citation label and the next Niese marker\./);
  const segment = JSON.parse(row.source_segments_json)[0];
  assert.deepEqual(segment.emptySource, record.emptySource);
  assert.deepEqual(segment.textGaps, []);
  assert.deepEqual(segment.phraseBreaks, []);
  assert.deepEqual([segment.start, segment.end, segment.text], [0, 0, '']);
  assert.deepEqual(JSON.parse(row.selected_sources_json).books[0].emptySections, [108]);
});

test('phrases stop across VII omissions, IX lacuna and X108 while whole-book Boolean matches remain valid', async () => {
  for (const [leftCitation, rightCitation] of [['VII.68', 'VII.100'], ['IX.50', 'IX.110'], ['X.107', 'X.109']]) {
    const left = byCitation.get(leftCitation), right = byCitation.get(rightCitation);
    const words = text => text.match(/[\p{L}\p{N}][\p{L}\p{M}\p{N}]*/gu) || [];
    const before = words(left.text).slice(-3), after = words(right.text).slice(0, 3);
    const options = {books: [`${ANT}:${left.book}`], scope: 'book'};
    assert.equal((await run(`"${[...before, ...after].join(' ')}"`, options)).result.occurrences, 0);
    assert.equal((await run(`${before.at(-1)} AND ${after[0]}`, options)).result.matchingUnits, 1);
  }
});

test('uncertain periods allow normal phrase matches but the two scraped X154 word interruptions block adjacency', async () => {
  const within = await run('"efficere Tunc"', {books: [`${ANT}:10`]});
  assert.equal(within.result.occurrences, 1);
  assert.equal(within.model.rows[0].citation, 'Antiquities X.75');
  const withinSegment = JSON.parse(csv(within.model, within.result).rows[0].source_segments_json)[0];
  assert.ok(withinSegment.editorialMarks.some(mark => mark.kind === 'unclear' && mark.text === '.'));
  assert.deepEqual(withinSegment.textGaps, []);
  const across = await run('"interfecit Dum"', {books: [`${ANT}:10`], scope: 'book'});
  assert.equal(across.result.occurrences, 1);
  assert.equal(across.model.rows[0].citation, 'Antiquities X.65–66');
  for (const phrase of ['regu riter', 'sepe lisset']) {
    assert.equal((await run(`"${phrase}"`, {books: [`${ANT}:10`], scope: 'book'})).result.occurrences, 0);
    assert.ok((await run(phrase.replace(' ', ' AND '), {books: [`${ANT}:10`]})).result.hitGroups.some(group => group.recordIds.includes(byCitation.get('X.154').id)));
  }
  const literal = await run('regu', {books: [`${ANT}:10`]}, {contextWords: 4});
  const segment = JSON.parse(csv(literal.model, literal.result).rows[0].source_segments_json)[0];
  assert.ok(segment.textGaps.some(gap => gap.kind === 'source-marked-dots' && gap.text === '..'
    && gap.sourceTag === 'del' && gap.sourceAttributes.rend === 'scraping'));
});

test('unclear text spanning X199–200 and its nested expansion remain searchable with exact CSV evidence', async () => {
  const {result, model} = await run('"deus autem misericordiam habens"', {books: [`${ANT}:10`]});
  assert.equal(result.occurrences, 1);
  assert.equal(model.rows[0].citation, 'Antiquities X.200');
  const segment = JSON.parse(csv(model, result).rows[0].source_segments_json)[0];
  assert.ok(segment.editorialMarks.some(mark => mark.kind === 'unclear' && mark.sourceTag === 'unclear'));
  assert.ok(segment.sourceMarkup.some(mark => mark.kind === 'expan' && mark.text === 'misericordiam' && mark.sourceTag === 'expan'));
  for (const mark of segment.editorialMarks.concat(segment.sourceMarkup)) {
    assert.equal(byCitation.get('X.200').text.slice(mark.start, mark.end), mark.text);
  }
  assert.ok(byCitation.get('X.199').editorialMarks.some(mark => mark.kind === 'unclear'));
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

test('zero-result Antiquities CSV retains all 20 books, 56 columns, source fingerprints and query settings', async () => {
  const {result, model} = await run('zzzznonoccurrit*', {books: 'all'});
  const file = csv(model, result);
  assert.equal(result.matchingUnits, 0);
  assert.equal(file.headers.length, 56);
  assert.equal(file.exported.rowCount, 0);
  assert.equal(file.rows.length, 1);
  assert.equal(file.rows[0].row_type, 'search-summary');
  assert.equal(file.rows[0].query, 'zzzznonoccurrit*');
  assert.match(file.rows[0].editorial_notes, /Antiquities includes the Proem and Books I–XX\b/);
  const sources = JSON.parse(file.rows[0].selected_sources_json);
  assert.deepEqual(sources.collections.map(source => source.id), [ANT]);
  assert.deepEqual(sources.books.map(book => book.id), allAntiquitiesBooks.map(book => `${ANT}:${book}`));
  assert.ok(sources.books.every(book => /^[a-f0-9]{64}$/.test(book.corpusSHA256)));
  assert.deepEqual(sources.books.find(book => book.id === `${ANT}:7`).omittedSections, Array.from({length: 31}, (_, index) => index + 69));
  assert.deepEqual(sources.books.find(book => book.id === `${ANT}:9`).missingSections, Array.from({length: 59}, (_, index) => index + 51));
  assert.deepEqual(sources.books.find(book => book.id === `${ANT}:9`).sectionRange, [1, 291]);
  assert.deepEqual(sources.books.find(book => book.id === `${ANT}:10`).emptySections, [108]);
  const expectedUnavailable = new Map([[11, []], [12, [248]], [13, [213, 216]], [14, [238, 239]], [15, [338, 347]],
    [16, [77, 123, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 359, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404]],
    [17, []], [18, [216, 217]], [19, []], [20, [27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 238]]]);
  for (const [number, unavailable] of expectedUnavailable) {
    const book = sources.books.find(book => book.id === `${ANT}:${number}`);
    assert.equal(book.coverageMode, 'registered-source-spans');
    assert.deepEqual(book.unavailableSections, unavailable);
    assert.equal(book.identityRegistry, `assets/xml/antiquities/niese/book-${number}.json`);
    assert.deepEqual(book.additionalSources, [book.identityRegistry]);
    assert.equal(book.canonicalSections, manifest.books[number - 1].canonicalSections);
    assert.equal(book.citationUnits, manifest.books[number - 1].citationUnits);
  }
  const xi = sources.books.find(book => book.id === `${ANT}:11`);
  assert.deepEqual([xi.canonicalSections, xi.citationUnits, xi.primarySourceSpans, xi.interpolatedSourcePassages], [347, 349, 352, 2]);
  assert.deepEqual(xi.fragmentedSections, [72, 312, 326, 342]);
  const xvi = sources.books.find(book => book.id === `${ANT}:16`);
  assert.deepEqual([xvi.canonicalSections, xvi.citationUnits, xvi.primarySourceSpans], [380, 380, 383]);
  assert.deepEqual(xvi.fragmentedSections, [294, 295, 351]);
  assert.deepEqual(sources.books.find(book => book.id === `${ANT}:20`).sectionRange, [1, 268]);
});

test('all new source spans keep truthful reader links, portion labels and literal editorial offsets', () => {
  const records = corpus.filter(record => record.book >= 11);
  assert.equal(records.length, 3868);
  assert.equal(new Set(records.map(record => record.citationUnitId)).size, 3860);
  for (const record of records) {
    assert.equal(citationFor([record]), `Antiquities ${record.citationLabel}`);
    assert.equal(readerURL(record, readerBase), `${readerBase}antiquities/?book=${record.book}&niese=${record.readerLink.params.niese}`);
    assert.equal(readerURL(record, readerBase, {section: false}), `${readerBase}antiquities/?book=${record.book}`);
    assert.equal(record.chapter, undefined);
    const segments = annotatedTextSegments(record);
    assert.equal(segments.map(segment => segment.text).join(''), record.text);
    for (const mark of record.editorialMarks.concat(record.sourceMarkup)) {
      assert.equal(record.text.slice(mark.start, mark.end), mark.text);
    }
  }
  const portions = records.filter(record => record.book === 11 && record.section === 72);
  assert.deepEqual(portions.map(record => record.continuationRank), [2, 1, 3]);
  assert.equal(citationFor(portions), 'Antiquities XI.72 (portion 2 of 3); XI.72 (portion 1 of 3); XI.72 (portion 3 of 3)');
});

test('real XI72 Boolean evidence shares a Niese unit while CSV retains each physical portion', async () => {
  const {result, model} = await run('"Septem cantores" AND Mancipiorum', {books: [`${ANT}:11`]});
  assert.deepEqual([result.matchingUnits, result.matchingSections, result.occurrences], [1, 1, 2]);
  const rows = csv(model, result).rows;
  assert.deepEqual(rows.map(row => row.citation), ['Antiquities XI.72 (portion 2 of 3)', 'Antiquities XI.72 (portion 1 of 3)']);
  const segments = rows.flatMap(row => JSON.parse(row.source_segments_json));
  assert.deepEqual([...new Set(segments.map(segment => segment.sourceOccurrence))], ['Latin-XI-72-2', 'Latin-XI-72-1']);
  assert.ok(segments.every(segment => segment.citationUnitId === `${ANT}-11-72` && segment.fragmentCount === 3));
  assert.ok(rows.every(row => row.reader_url === `${readerBase}antiquities/?book=11&niese=72`));
});

test('the two real XI Bellum interpolations export their own identity and accepted reader association', async () => {
  for (const record of corpus.filter(record => record.sourcePassage)) {
    const words = record.text.match(/[\p{L}\p{N}][\p{L}\p{M}\p{N}]*/gu);
    const {result, model} = await run(`"${words.join(' ')}"`, {books: [`${ANT}:11`]});
    const row = csv(model, result).rows.find(row => row.citation === `Antiquities ${record.citationLabel}`);
    assert.ok(row, record.id);
    assert.equal(row.reader_url, `${readerBase}antiquities/?book=11&niese=312`);
    const segment = JSON.parse(row.source_segments_json).find(segment => segment.sourceOccurrence === record.sourceOccurrence);
    assert.ok(segment);
    assert.deepEqual(segment.sourcePassage, record.sourcePassage);
    assert.equal(segment.citationUnitId, record.id);
    assert.equal(segment.sourcePassage.AntiquitiesIdentity, false);
    assert.equal(segment.sourcePassage.association, 312);
  }
});

test('XII end subscription is source evidence while XIII intra-word gap stays visible in CSV', async () => {
  assert.equal((await run('"FLAUII IOSEPPI IUDAEICAE ANTIQUITATIS LIBER DUODECIMUS EXPLICIT"', {books: [`${ANT}:12`]})).result.occurrences, 0);
  assert.ok(byCitation.get('XII.434').text.endsWith('defunctus est.'));
  const record = byCitation.get('XIII.393');
  const incorrect = await run('ress', {books: [`${ANT}:13`]});
  assert.ok(incorrect.result.hitGroups.every(group => !group.recordIds.includes(record.id)));
  const {result, model} = await run('"s fuerant"', {books: [`${ANT}:13`]});
  const row = csv(model, result).rows.find(row => row.citation === 'Antiquities XIII.393');
  assert.ok(row);
  assert.equal(row.matched_text, 's fuerant');
  const segment = JSON.parse(row.source_segments_json).find(segment => segment.sourceId === record.sourceId);
  assert.ok(segment.textGaps.some(gap => gap.kind === 'tei-gap' && gap.start === gap.end && gap.sourceAttributes.reason === 'fading'));
});

test('the accepted XVII41–42 touching-word boundary supports an exact whole-book phrase', async () => {
  const left = byCitation.get('XVII.41'), right = byCitation.get('XVII.42');
  assert.ok(left.text.endsWith('inmaturius eleuati'));
  assert.ok(right.text.startsWith('cum igitur'));
  assert.equal(right.breakBefore, undefined);
  const query = '"eleuati cum igitur"';
  assert.equal((await run(query, {books: [`${ANT}:17`]})).result.occurrences, 0);
  const {result, model} = await run(query, {books: [`${ANT}:17`], scope: 'book'});
  assert.deepEqual([result.occurrences, result.matchingUnits], [1, 1]);
  const exported = csv(model, result).rows;
  assert.equal(exported.length, 1);
  assert.deepEqual(JSON.parse(exported[0].source_segments_json).map(segment => segment.recordId), [left.id, right.id]);
  assert.equal((await run('eleuaticum', {books: [`${ANT}:17`], scope: 'book'})).result.occurrences, 0);
});

test('a frequent Antiquities I–X word still exports all 7073 occurrences beyond the first display page', async () => {
  const {result, model} = await run('et', {}, {contextWords: 2});
  assert.equal(result.occurrences, 7073);
  assert.equal(model.rows.length, 7073);
  const firstPage = model.rows.slice(0, 50);
  assert.equal(firstPage.length, 50);
  const file = csv(model, result);
  assert.equal(file.headers.length, 56);
  assert.equal(file.exported.rowCount, 7073);
  assert.equal(file.rows.length, 7073);
  assert.equal(new Set(model.rows.map(row => row.key)).size, 7073);
  assert.ok(file.rows.every(row => row.matched_text.toLowerCase() === 'et'));
  assert.equal(file.rows.at(-1).reader_url, model.rows.at(-1).readerURL);
  assert.ok(file.rows.some(row => row.reader_url.includes('book=preface')));
  assert.deepEqual([...new Set(file.rows.map(row => Number(row.book)))], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test('the original 24 books retain separate work identities and 421 sacerdot* occurrences from 318 units', async () => {
  const {result, model} = await run('sacerdot*', {collections: 'all', books: originalCollectionBooks});
  assert.deepEqual(result.selectedCollections, [BELLUM, DEH, CA, ANT]);
  assert.equal(result.selectedBooks.length, 24);
  assert.equal(result.records.length, 8590);
  assert.equal(new Set(result.records.map(record => record.id)).size, 8590);
  assert.deepEqual([result.occurrences, result.matchingUnits], [421, 318]);
  const file = csv(model, result);
  assert.equal(file.headers.length, 56); assert.equal(file.rows.length, 421);
  assert.deepEqual([BELLUM, DEH, CA, ANT].map(id => file.rows.filter(row => row.collection_id === id).length), [35, 125, 34, 227]);
  assert.ok(file.rows.filter(row => row.collection_id === ANT).every(row => row.citation_scheme === 'niese' && row.reader_url.includes('/antiquities/')));
  const selected = JSON.parse(file.rows[0].selected_sources_json);
  assert.equal(selected.books.length, 24);
  assert.equal(selected.collections.length, 4);
  const alone = await run('sacerdot*');
  assert.deepEqual([alone.result.occurrences, alone.result.matchingUnits], [227, 200]);
  assert.deepEqual(alone.result.selectedCollections, [ANT]);
});

test('negative-only whole-book exports retain all 34 book identities and numeric Book I links', async () => {
  const {result, model} = await run('NOT zzzznonoccurrit', {collections: 'all', books: 'all', scope: 'book'});
  assert.deepEqual([result.matchingUnits, result.occurrences], [34, 0]);
  assert.equal(model.unhighlightedUnits.length, 34);
  const file = csv(model, result);
  assert.equal(file.rows.length, 34);
  assert.ok(file.rows.every(row => row.row_type === 'matching-unit' && row.matched_text === '' && row.source_segments_json === '[]'));
  const antiquities = file.rows.filter(row => row.collection_id === ANT);
  assert.deepEqual(antiquities.map(row => row.reader_url), allAntiquitiesBooks.map(book => `${readerBase}antiquities/?book=${book}`));
  assert.deepEqual(antiquities.map(row => row.citation), ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX'].map(book => `Antiquities ${book}`));
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

test('publication retains complete I–X source projections and rejects the original record metadata corruptions', () => {
  for (const spec of manifest.books.filter(book => book.number <= 10)) {
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
    [7, records => {records[68].textGaps = [];}],
    [7, records => {records[99].breakBefore = false;}],
    [8, records => {records[185].sourceIds.pop();}],
    [9, records => {records[50].breakBefore = false;}],
    [9, records => {records[50].textGaps = [];}],
    [10, records => {delete records[107].emptySource;}],
    [10, records => {records[107].emptySource.label.text = '[VII.iii.109]';}],
    [10, records => {records[107].emptySource.nextBoundary.sourceTextOffset++;}],
    [10, records => {records[108].breakBefore = false;}],
    [10, records => {records[153].textGaps[0].sourceTag = 'unclear';}],
    [10, records => {records[64].phraseBreaks = [273];}],
    [10, records => {records[199].editorialMarks.find(mark => mark.kind === 'unclear').sourceAttributes.reason = 'invented';}],
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
    [7, report => {report.coverage.omittedSections.pop();}],
    [7, report => {report.paragraphs.find(paragraph => paragraph.segments.some(segment => segment.kind === 'excluded-omission-notice')).segments.find(segment => segment.kind === 'excluded-omission-notice').text += 'x';}],
    [9, report => {report.coverage.missingSections.pop();}],
    [9, report => {report.coverage.sourceOrderIsConsecutive = true;}],
    [9, report => {report.documentReports[0].excluded.find(item => item.kind === 'lacuna-notice').text += 'x';}],
    [10, report => {report.sectionAudits[107].emptySource.interveningText = '';}],
    [10, report => {report.sectionAudits[153].textGaps[0].sourceAttributes.rend = 'strikethrough';}],
  ];
  for (const [book, mutate] of cases) {
    const changed = structuredClone(reports.get(book)); mutate(changed);
    assert.throws(() => validateAntiquitiesSourceProjection(corpus.filter(record => record.book === book), changed, manifest, manifest.books[book - 1]));
  }
  const changedSpec = {...manifest.books[0], additionalSources: []};
  assert.throws(() => validateAntiquitiesSourceProjection(corpus.filter(record => record.book === 1), reports.get(1), manifest, changedSpec));
});

test('publication verifies the new source boundaries, closures and token seam and rejects altered evidence', () => {
  for (const book of [16, 17, 18, 19, 20]) {
    validateAntiquitiesSourceProjection(corpus.filter(record => record.book === book), reports.get(book), manifest, manifest.books[book - 1]);
  }
  const recordCases = [
    [16, rows => {delete rows.find(row => row.section === 200).sourceBoundaryEvidence;}],
    [16, rows => {rows.find(row => row.section === 200).breakBefore = false;}],
    [16, rows => {rows.find(row => row.section === 200).sourceBoundaryEvidence.precedingSection = 199;}],
    [16, rows => {rows.find(row => row.section === 200).sourceBoundaryEvidence.excludedSourceSpans[0].sourceTextEnd++;}],
    [16, rows => {rows.find(row => row.section === 394).sourceIds.push('latin-book16-num395');}],
    [17, rows => {rows.find(row => row.section === 42).breakBefore = true;}],
    [20, rows => {rows.find(row => row.section === 37).sourceBoundaryEvidence.precedingEnd.sourceTextOffset++;}],
    [20, rows => {rows.find(row => row.section === 26).text += ' [Niese sections 26–37 largely missing]';}],
  ];
  for (const [book, mutate] of recordCases) {
    const changed = structuredClone(corpus.filter(row => row.book === book)); mutate(changed);
    assert.throws(() => validateAntiquitiesSourceProjection(changed, reports.get(book), manifest, manifest.books[book - 1]));
  }
  const reportCases = [
    [16, report => {report.excluded.find(item => item.sourceId === 'latin-book16-num395').text = '[??]';}],
    [16, report => {report.paragraphs.find(paragraph => paragraph.sourceId === 'latin-book16-num395').structuralMarkers[0].recordTextOffset++;}],
    [17, report => {report.coverage.registeredTokenBoundaryEvidence[0].sourceTextOffset++;}],
    [17, report => {report.coverage.registeredTokenBoundaryEvidence[0].sourceText = 'eleuati cum';}],
    [17, report => {report.coverage.rawParagraphWordSequenceSha256 = report.coverage.sourceWordSequenceSha256;}],
    [20, report => {report.excluded.find(item => item.kind === 'excluded-lacuna-notice').sourceTextEnd--;}],
    [20, report => {report.coverage.explicitSourceBoundaries = [];}],
  ];
  for (const [book, mutate] of reportCases) {
    const changed = structuredClone(reports.get(book)); mutate(changed);
    assert.throws(() => validateAntiquitiesSourceProjection(corpus.filter(row => row.book === book), changed, manifest, manifest.books[book - 1]));
  }
});
