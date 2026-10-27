const {test, beforeEach} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../..');
const api = require('../../assets/js/manuscriptAnnotations.js');
const data = require('../../assets/data/alignment-citations.json');
const inventory = require('../../_docs/annotation-source-inventory.json');
beforeEach(() => api.setCitationData(data));
const record = notation => ({work: 'antiquities', notation, alignmentUnitId: 'latin-book01-num27', siglum: 'BernBBMs50', occurrence: 1});
const parse = notation => api.interpretManuscriptAnnotation(record(notation));
test('editorial Antiquities example is verified including internal milestones', () => {
  const r = api.resolveAlignmentCitation('antiquities', 'latin-book01-num27');
  assert.equal(r.publicCitation, 'Book 1, Niese §§27–33');
  assert.deepEqual([r.start, r.end], [27, 33]);
  assert.equal(r.alignmentUnitId, 'latin-book01-num27');
  assert.equal(r.verificationStatus, 'verified');
});
test('work namespaces do not alias the same numeric suffix', () => {
  assert.equal(api.resolveAlignmentCitation('bellum', 'latin-bellum1-num27').publicCitation, 'Book 1, Niese §§27–29');
  assert.equal(api.resolveAlignmentCitation('bellum', 'latin-book01-num27').verificationStatus, 'unresolved');
  assert.equal(api.resolveAlignmentCitation('deh', 'latin-deh1-num78').publicCitation, 'I.26.3');
  assert.equal(api.resolveAlignmentCitation('deh', 'latin-deh1-num78').citationSystem, 'deh');
});
test('single, discontinuous and unknown citations never invent ranges', () => {
  assert.equal(api.resolveAlignmentCitation('bellum', 'latin-bellum1-num30').publicCitation, 'Book 1, Niese §30');
  assert.equal(api.resolveAlignmentCitation('antiquities', 'latin-book01-num999999').verificationStatus, 'unresolved');
  api.setCitationData({works: {antiquities: {unit: {book: 1, intervals: [[27, 29], [33, 33]], status: 'verified', citationSystem: 'niese'}}}});
  assert.equal(api.resolveAlignmentCitation('antiquities', 'unit').publicCitation, 'Book 1, Niese §§27–29, 33');
});
test('outside-reader labels include work and equivalent French labels', () => {
  assert.equal(api.resolveAlignmentCitation('antiquities', 'latin-book01-num27', {includeWork: true}).publicCitation, 'Antiquities, Book 1, Niese §§27–33');
  assert.equal(api.resolveAlignmentCitation('antiquities', 'latin-book01-num27', {lang: 'fr'}).publicCitation, 'Livre 1, Niese §§27–33');
});
test('book-final units and certified non-contiguous coverage retain actual boundaries', () => {
  for (const [work, id, text] of [
    ['antiquities', 'latin-book01-num345', 'Book 1, Niese §§345–346'],
    ['antiquities', 'latin-book11-num346', 'Book 11, Niese §§346–347'],
    ['antiquities', 'latin-book20-num266', 'Book 20, Niese §§266–268'],
    ['bellum', 'latin-bellum1-num670', 'Book 1, Niese §§670–673'],
    ['bellum', 'latin-bellum7-num454', 'Book 7, Niese §§454–455'],
    ['antiquities', 'latin-book11-num321', 'Book 11, Niese §§321–326, 342']
  ]) assert.equal(api.resolveAlignmentCitation(work, id).publicCitation, text);
});
test('all annotation associations have a verified citation or an explicit source exception', () => {
  let verified = 0, unlocated = 0;
  for (const r of inventory.records) {
    const citation = api.resolveAlignmentCitation(r.work, r.alignmentUnitId);
    if (citation.verificationStatus === 'verified') verified++;
    else { unlocated++; assert(inventory.citationExceptions.some(e => e.work === r.work && e.unit === r.alignmentUnitId)); }
  }
  assert.equal(verified, 2937); assert.equal(unlocated, 21);
});
test('all generated source provenance matches immutable inputs', () => {
  for (const [file, expected] of Object.entries(data.provenance)) {
    assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root, file))).digest('hex'), expected, file);
  }
});
test('first and subsequent folio references are distinct without creating annotations', () => {
  const first = parse('[¤1r] (@1) aliis babylon');
  const next = parse('[1r] (@2) quomodo prolis noe');
  assert.equal(first.parts[0].folio.reference, '1r'); assert.equal(first.parts[0].folio.firstOccurrence, true);
  assert.equal(next.parts[0].folio.reference, '1r'); assert.equal(next.parts[0].folio.firstOccurrence, false);
  assert.equal(parse('[¤1r]').parts.length, 0);
  assert.equal(parse('[122v]').parts.length, 0);
});
for (const [symbol, hand] of [['@', 1], ['£', 2], ['¢', 3]]) {
  test(`hand ${hand} comes from ${symbol}, never the annotation number`, () => {
    const part = parse(`[1r] (${symbol}4) recorded words`).parts[0];
    assert.equal(part.hand, hand); assert.equal(part.sourceNumber, '4');
  });
}
test('multiple hands and folio transitions preserve independent source order', () => {
  const r = parse('[¤1v] (@1) aliis babylon; (@2) quomodo prolis noe [¤2r] (£1) other words (¢2) more words');
  assert.deepEqual(r.parts.map(p => p.hand), [1, 1, 2, 3]);
  assert.deepEqual(r.parts.map(p => p.folio.reference), ['1v', '1v', '2r', '2r']);
  assert.deepEqual(r.parts.map(p => p.text), ['aliis babylon;', 'quomodo prolis noe', 'other words', 'more words']);
});
test('symbolic descriptions remain available and never imply an unreadable annotation or hand', () => {
  const r = parse('[¤1v] (#2 nota NT)').parts[0];
  assert.equal(r.category, 'symbolic'); assert.equal(r.hand, null); assert.equal(r.description, 'nota NT');
});
test('cannot be transcribed is independent of hand and does not invent damage', () => {
  assert.equal(parse('[1r] (§)').parts[0].hand, null);
  for (const text of ['[1r] @ §', '[1r] (@1) §', '[1r] (@1) (§)']) {
    const parts = parse(text).parts;
    assert.equal(parts.length, 1); assert.equal(parts[0].hand, 1); assert.equal(parts[0].category, 'untranscribable');
  }
  const html = api.renderAnnotation(record('[1r] (§)')).html;
  assert(html.includes('Cannot be transcribed')); assert(!/illegible|damaged|faded/i.test(html));
});
test('source-grounded ASCII ellipsis preserves exactly the three recorded words', () => {
  const source = inventory.records.find(r => r.notation.includes('d(imitte) onie et ...'));
  assert(source);
  const part = api.interpretManuscriptAnnotation(source).parts.find(p => p.abbreviated);
  assert.equal(part.text, 'd(imitte) onie et ...'); assert.equal(part.hand, 1);
});
test('other ellipses, including folio uncertainty and medial ellipses, are not indiscriminately abbreviated', () => {
  for (const text of ['[1r] (@1) cain primus pondera … instituit', '[1r] (@1) one ... two', '[1r] (@1) one two three four ...']) {
    assert.equal(parse(text).parts[0].abbreviated, false);
    assert(parse(text).parts[0].ellipsisUnresolved);
  }
  assert.equal(parse('[¤…]').parts.length, 0);
});
test('unknown notation, malformed delimiters and literal symbols stay visible', () => {
  for (const text of ['[1r] (¬1) de prima adam', '[1r] (¦2) supplied words', '[1r] (@£) text', '[10v)(#croix)(¢1)erant prompti']) {
    const r = parse(text); assert(r.issues.length); assert.equal(r.originalNotation, text);
    assert(api.renderAnnotation(record(text)).html.includes('annotation-status'));
  }
  const literal = parse('[1r] (@1) pretium £ et @ in textu').parts[0];
  assert.equal(literal.text, 'pretium £ et @ in textu'); assert.equal(literal.hand, 1);
});
test('full corpus records remain byte-for-byte strings and objects without mutation', () => {
  const anchors = new Set(); let parts = 0;
  for (const r of inventory.records) {
    const before = JSON.stringify(r); Object.freeze(r);
    const parsed = api.interpretManuscriptAnnotation(r);
    assert.equal(parsed.originalRecord, r); assert.equal(parsed.originalNotation, r.notation);
    assert.equal(JSON.stringify(r), before); assert(!anchors.has(parsed.anchor)); anchors.add(parsed.anchor);
    parts += parsed.parts.length;
    for (const p of parsed.parts) assert(r.notation.includes(p.text) || p.text === '', r.notation);
  }
  assert.equal(inventory.records.length, 2958); assert.equal(parts, 6201);
});
test('the folio-only source record is retained without a numbered article', () => {
  const r = inventory.records.find(r => r.notation === '[122v]');
  const rendered = api.renderAnnotation(r);
  assert.equal(rendered.count, 0); assert(rendered.html.includes('[122v]')); assert(!rendered.html.includes('<article'));
});
test('a hand-only record does not imply inability to transcribe, and unknown sigla stay visible', () => {
  const r = {...record('[1r] (£2 - X dans un carré)'), siglum: 'unresolved-siglum'};
  const html = api.renderAnnotation(r).html;
  assert(html.includes('No transcription recorded')); assert(html.includes('unresolved-siglum'));
  assert(!html.includes('Cannot be transcribed')); assert(html.includes('Hand 2'));
});
test('display numbers do not affect stable source anchors or original identifiers', () => {
  const r = record('[1r] (@1) words');
  assert.equal(api.renderAnnotation(r, {startNumber: 10}).interpreted.anchor, api.renderAnnotation(r).interpreted.anchor);
  assert.equal(api.recordAnchor({...r, originalId: 'preserved-id'}), 'preserved-id');
  assert(api.renderAnnotation(r).html.includes('No original annotation ID encoded'));
});
test('HTML uses escaped source text and native, keyboard-operable details', () => {
  const html = api.renderAnnotation(record('[1r] (@1) <script>alert(1)</script> & text')).html;
  assert(!html.includes('<script>')); assert(html.includes('&lt;script&gt;')); assert(html.includes('<details'));
  assert(html.includes('<summary>Scholarly details</summary>')); assert(html.includes('lang="la"'));
});
test('DEH adapter remains unconfigured even though its citations are available', () => {
  const r = api.interpretManuscriptAnnotation({...record('[¤1r] @ text'), work: 'deh'});
  assert.equal(r.parts[0].hand, null); assert.equal(r.parts[0].category, 'unresolved');
  assert(r.issues.includes('source-convention-unconfigured'));
});
test('registry expands verified manuscripts and reports shelfmark conflicts without correcting them', () => {
  assert(api.resolveManuscript('BernBBMs50').displayName.includes('Burgerbibliothek'));
  assert.equal(api.resolveManuscript('RomeBAVPallat1992').verificationStatus, 'shelfmark-conflict');
  assert(api.resolveManuscript('RomeBAVPallat1992').displayName.includes('Pal. lat. 1992'));
  assert.equal(api.resolveManuscript('unknown', 'original siglum').displayName, 'original siglum');
});
