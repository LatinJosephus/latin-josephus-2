import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash, webcrypto} from 'node:crypto';

if (!globalThis.crypto) globalThis.crypto = webcrypto;
const source = await readFile(new URL('../lauroCore.js', import.meta.url), 'utf8');
const core = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
const {validateBook, indexBook, lineAtoms, utf16Offset, visibleLines, readingView,
  flowSeparator, readingParts, flowGroups, locationFromUrl, updateLauroUrl, createLauroLoader} = core;

function fixture() {
  const lines = [
    {TEI_line_id: 'H', text_exact: 'CAPITOLO PRIMO', source_index: 0, image_number: 273, source_region_type: 'heading', region_id: 'heading', primary: false},
    {TEI_line_id: 'L1', text_exact: 'ſ😀 appreſtoſ[ſi]¬', effective_text: 'ſ😀 appreſtoſſi¬', source_index: 1, image_number: 273, source_region_type: 'paragraph', region_id: 'p1', primary: true},
    {TEI_line_id: 'L2', text_exact: 'un ricetto.', source_index: 2, image_number: 273, source_region_type: 'paragraph', region_id: 'p1', primary: true},
    {TEI_line_id: 'S', text_exact: 'ar', source_index: 3, image_number: 273, source_region_type: 'footer', region_id: 'f1', primary: false, emit_in_main_text: false},
    {TEI_line_id: 'H2', text_exact: 'CAPITOLO SECONDO', source_index: 4, image_number: 274, source_region_type: 'heading', region_id: 'h2', primary: false},
    {TEI_line_id: 'L3', text_exact: 'Altra coſa.', source_index: 5, image_number: 274, source_region_type: 'paragraph', region_id: 'p2', primary: true},
  ];
  const fragment = (line, a, b) => ({line: line.TEI_line_id, start_cp: a, end_cp: b,
    start_utf16: utf16Offset(line.text_exact, a), end_utf16: utf16Offset(line.text_exact, b)});
  const target = unit => ({xml_id: `latin-deh4-num${unit}`, book: 4, chapter: 20, unit, citation: `IV.20.${unit}`});
  const first = fragment(lines[1], 0, 8), second = fragment(lines[1], 8, Array.from(lines[1].text_exact).length);
  return {schema: 'lauro1544-reader-book/1', version: 'test-v1', book: 4, lines,
    pages: [{image_number: 273, label: 'Image 273'}, {image_number: 274, folio_label: 'Folio 137 verso'}],
    divisions: [{id: 'C1', label: 'CAPITOLO PRIMO', is_native_chapter: true, chapter_start_index: 0, image_number: 273, line_refs: ['H']},
                {id: 'C2', label: 'CAPITOLO SECONDO', is_native_chapter: true, chapter_start_index: 4, image_number: 274, line_refs: ['H2']}],
    mappings: [{id: 'M1', canonical: target(1), canonical_targets: [target(1), target(2)], relation: 'one-to-many', fragments: [first]},
               {id: 'M2', canonical: target(3), relation: 'one-to-one', fragments: [second, fragment(lines[2], 0, 11)]}],
    annotations: [{id: 'A1', kind: 'editorial-supply', title: 'Editorial supplement; not printed', primary_coverage: false,
                   fragments: [fragment(lines[1], 11, 15)]}]};
}

test('validates exact diplomatic brackets independently of effective text', () => {
  const data = fixture();
  assert.equal(validateBook(data).lines.get('L1').text_exact, 'ſ😀 appreſtoſ[ſi]¬');
  const index = indexBook(data);
  const fragments = index.byLine.get('L1');
  const annotation = data.annotations[0].fragments.map(f => ({...f, annotation: 'A1'}));
  const atoms = lineAtoms(data.lines[1], fragments, annotation);
  assert.equal(atoms.map(a => a.text).join(''), data.lines[1].text_exact);
  assert(atoms.some(a => a.annotations.includes('A1')));
});

test('codepoint and UTF16 coordinates preserve astral and combining characters', () => {
  assert.equal(utf16Offset('ſ😀q\u0304', 2), 3);
  assert.equal(utf16Offset('ſ😀q\u0304', 4), 5);
  assert.throws(() => utf16Offset('😀', 2));
  const data = fixture();
  data.mappings[0].fragments[0].end_utf16--;
  assert.throws(() => validateBook(data), /coordinate/);
});

test('bounds, missing lines and duplicate source IDs fail closed', () => {
  let data = fixture();
  data.mappings[0].fragments[0].start_cp = -1;
  assert.throws(() => validateBook(data));
  data = fixture(); data.mappings[0].fragments[0].line = 'missing';
  assert.throws(() => validateBook(data));
  data = fixture(); data.lines.push({...data.lines[0]});
  assert.throws(() => validateBook(data), /duplicate/);
  assert.throws(() => lineAtoms({text_exact: 'abc'}, [{start_cp: 0, end_cp: 4, start_utf16: 0, end_utf16: 4}]));
});

test('multiunit and overlapping fragments never duplicate source characters', () => {
  const data = fixture(), index = indexBook(data);
  assert.equal(index.byCanonical.get('latin-deh4-num2')[0].id, 'M1');
  const fragments = [...index.byLine.get('L1'), {...index.byLine.get('L1')[0], mapping: 'M3'}];
  const atoms = lineAtoms(data.lines[1], fragments);
  assert.equal(atoms.map(a => a.text).join(''), data.lines[1].text_exact);
  assert(atoms.some(a => a.mappings.includes('M1') && a.mappings.includes('M3')));
});

test('secondary annotation cannot replace primary correspondence', () => {
  const data = fixture();
  data.annotations[0].primary_coverage = true;
  assert.throws(() => validateBook(data), /secondary/);
});

test('native chapter and source/page views retain distinct scopes', () => {
  const data = fixture();
  assert.deepEqual(visibleLines(data, {mode: 'chapter', chapter: 'C1'}).map(l => l.TEI_line_id), ['H', 'L1', 'L2']);
  assert.deepEqual(visibleLines(data, {mode: 'chapter', chapter: 'C2'}).map(l => l.TEI_line_id), ['H2', 'L3']);
  assert(visibleLines(data, {mode: 'source'}).some(l => l.TEI_line_id === 'S'));
  assert(!visibleLines(data, {mode: 'book'}).some(l => l.TEI_line_id === 'S'));
  assert(visibleLines(data, {mode: 'page', page: 273}).some(l => l.TEI_line_id === 'S'));
});

test('section running view includes only corresponding mapping intervals', () => {
  const data = fixture();
  const view = readingView(data, {mode: 'running'}, {level: 'section-level'}, 'latin-deh4-num1');
  assert.deepEqual(view.lines.map(l => l.TEI_line_id), ['L1']);
  assert.deepEqual([...view.included], ['M1']);
  const source = readingView(data, {mode: 'source'}, {level: 'section-level'}, 'latin-deh4-num1');
  assert.equal(source.included, null);
});

test('reading flow suppresses markers only in visibility, retaining exact payload', () => {
  const text = 'appreſtoſ[ſi]¬';
  const parts = readingParts(text);
  assert.equal(parts.map(p => p.text).join(''), text);
  assert.equal(parts.filter(p => !p.hidden).map(p => p.text).join(''), 'appreſtoſ[ſi]');
  assert.equal(flowSeparator('de¬', 'gli'), '');
  assert.equal(flowSeparator('fine.', 'Altra'), ' ');
  assert.equal(flowSeparator('già ', 'Altra'), '');
  assert.equal(flowGroups(fixture().lines.filter(l => l.TEI_line_id.startsWith('L')))[0].lines.length, 3);
});

test('Lauro URLs preserve Millet and unrelated reader selections', () => {
  const original = 'http://localhost/deh/?book=4&unit=54&french=millet1556&millet-view=source';
  const state = {enabled: true, mode: 'page', page: '273', chapter: null, canonical: 'latin-deh4-num54', alignment: false, folios: true};
  const url = updateLauroUrl(original, state);
  assert.equal(url.searchParams.get('french'), 'millet1556');
  assert.equal(url.searchParams.get('italian'), 'lauro1544');
  assert.deepEqual(locationFromUrl(url), state);
  const off = updateLauroUrl(url, {...state, enabled: false});
  assert.equal(off.searchParams.get('italian'), null);
  assert.equal(off.searchParams.get('french'), 'millet1556');
  assert.equal(locationFromUrl('http://localhost/deh/?italian=lauro1544&lauro-view=preliminary').mode, 'running');
});

test('folio conversion follows the user’s recto/verso anchors across all 417 images', () => {
  const data = {pages:Array.from({length:417},(_,i)=>({image_number:i+1}))};
  const labels=core.folioLabels(data);
  for (const [image,label] of [[1,'f. 1r'],[2,'f. 1v'],[3,'f. 2r'],[4,'f. 2v'],[28,'f. 14v'],[29,'f. 15r'],[416,'f. 208v'],[417,'f. 209r']])assert.equal(labels.get(image),label);
  assert.equal(new Set(labels.values()).size,417);
  for(let folio=1;folio<=208;folio++){
    assert.equal(labels.get(2*folio-1),`f. ${folio}r`);
    assert.equal(labels.get(2*folio),`f. ${folio}v`);
  }
  assert.throws(()=>core.folioLabel(0));assert.throws(()=>core.folioLabel(418));
});

test('ordinary s and concise editorial wording are display-only and keep offsets', () => {
  const raw='ſ😀 appreſtoſ[ſi]¬ q\u0304 ß';
  const shown=core.readerText(raw);
  assert.equal(shown,'s😀 apprestos[si]¬ q\u0304 ß');
  assert.equal(shown.length,raw.length);
  assert.equal(Array.from(shown).length,Array.from(raw).length);
  for(let i=0;i<=Array.from(raw).length;i++)assert.equal(core.utf16Offset(shown,i),core.utf16Offset(raw,i));
  const annotation={kind:'EDITORIALLY_SUPPLIED_NOT_PRINTED',original:'The ending [ſi] is editorially supplied; it is not certified as printed.'};
  assert.equal(core.editorialLabel(annotation),'The ending [si] is editorially supplied.');
  assert.equal(annotation.original,'The ending [ſi] is editorially supplied; it is not certified as printed.');
  assert(raw.includes('ſ'));
});

function loaderFixture({corrupt = false, status = 'LOCAL_PREVIEW_READY'} = {}) {
  const books = new Map();
  const records = [1, 2, 3, 4, 5].map(book => {
    const data = fixture(); data.book = book;
    const bytes = Buffer.from(JSON.stringify(data)); books.set(`book-0${book}.json`, bytes);
    return {book, path: `book-0${book}.json`, sha256: createHash('sha256').update(bytes).digest('hex')};
  });
  const manifest = {schema: 'lauro1544-reader/1', version: 'test-v1', authority: {status}, books: records};
  let requests = 0;
  return {manifest, requests: () => requests,
    fetcher: async url => {
      const filename = new URL(url).pathname.split('/').at(-1); requests++;
      if (filename === 'manifest.json') return {ok: true, json: async () => manifest};
      const bytes = corrupt ? Buffer.from('changed') : books.get(filename);
      return {ok: !!bytes, arrayBuffer: async () => Uint8Array.from(bytes).buffer};
    }};
}

test('loader verifies book hashes/version and caches only successful books', async () => {
  const fixture = loaderFixture(), loader = createLauroLoader(new URL('http://localhost/data/'), fixture.fetcher);
  const book = await loader.book(4);
  assert.equal(book.book, 4);
  assert.equal(await loader.book(4), book);
  assert.equal(fixture.requests(), 2);
  await assert.rejects(loader.book(0), /unavailable/);
});

test('loader rejects uncertified manifest and changed source bytes', async () => {
  let fixture = loaderFixture({status: 'BLOCKED'});
  await assert.rejects(createLauroLoader(new URL('http://localhost/'), fixture.fetcher).book(1), /integration checks/);
  fixture = loaderFixture({corrupt: true});
  await assert.rejects(createLauroLoader(new URL('http://localhost/'), fixture.fetcher).book(1), /integrity/);
});
