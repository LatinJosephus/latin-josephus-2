const {test} = require('node:test');
const assert = require('node:assert/strict');
const api = require('../../assets/js/manuscriptAnnotations.js');
const inventory = require('../../_docs/annotation-source-inventory.json');
api.setCitationData(require('../../assets/data/alignment-citations.json'));
const bern = inventory.records.find(r => r.work === 'antiquities' && r.siglum === 'BernBBMs118'
  && r.alignmentUnitId === 'latin-book01-num34');
const visible = html => html.replace(/<details\b[^>]*>[\s\S]*?<\/details>/g, '');

test('Bern retains dicit and identifies preceding untranscribed material independently from abbreviation', () => {
  const before = JSON.stringify(bern), r = api.interpretManuscriptAnnotation(bern), p = r.parts[0];
  assert.equal(p.text, 'dicit'); assert.equal(p.category, 'textual');
  assert.equal(p.transcriptionStatus, 'partial'); assert(p.untranscribedBefore);
  assert.equal(p.hand, null); assert.equal(p.abbreviated, false);
  assert.equal(r.parts.length, 3); assert.equal(JSON.stringify(bern), before);
  const html = api.renderAnnotation(bern).html;
  assert(html.includes('Partly transcribed'));
  assert(!visible(html).includes('Partly transcribed'));
  assert(!visible(html).includes('[Untranscribed text]'));
  assert(!visible(html).includes('The editor confirms'));
  assert(html.includes('The editor confirms that untranscribed material precedes the surviving word dicit.'));
  assert(html.includes(`<pre>${bern.notation}</pre>`));
});
test('David remains a labelled provisional reading, never inserted into original transcription', () => {
  const r = api.interpretManuscriptAnnotation(bern);
  assert.equal(r.parts[0].provisionalReading.en, 'david [uncertain text] dicit');
  assert.equal(r.parts[0].text, 'dicit'); assert(!r.originalNotation.includes('david'));
  const html = visible(api.renderAnnotation(bern).html);
  assert(html.includes('(provisional reading)')); assert(!html.includes('Provisional reading:'));
  assert(html.includes('david <span')); assert(html.includes('[uncertain text]</span> dicit'));
});
test('Bern clarification is guarded by exact source record identity and does not reinterpret every §', () => {
  for (const r of [{...bern, siglum: 'BernBBMs50'}, {...bern, alignmentUnitId: 'latin-book01-num37'},
    {...bern, notation: '[¤2v] (§) another fragment'}]) {
    assert.equal(api.interpretManuscriptAnnotation(r).parts[0].transcriptionStatus, undefined);
  }
});
test('three recovered worksheet annotations use the approved existing unit ranges', () => {
  const records = api.getSupplementalAnnotations('antiquities', 1);
  assert.equal(records.length, 3);
  assert.deepEqual(records.map(r => r.alignmentUnitId), ['latin-book01-num27', 'latin-book01-num34', 'latin-book01-num34']);
  assert.deepEqual(records.map(r => api.resolveAlignmentCitation(r.work, r.alignmentUnitId).publicCitation),
    ['Book 1, Niese §§27–33', 'Book 1, Niese §§34–36', 'Book 1, Niese §§34–36']);
  assert.equal(new Set(records.map(api.recordAnchor)).size, 3);
});
test('each recovered component retains the exact whole worksheet cell and its own original offset', () => {
  const records = api.getSupplementalAnnotations('antiquities', 1), expected = ['.d significe. sabatum', 'de adam', 'issa si a uira diuisat'];
  records.forEach((r, i) => {
    const before = JSON.stringify(r), parsed = api.interpretManuscriptAnnotation(r);
    assert.equal(parsed.parts.length, 1); assert.equal(parsed.parts[0].text, expected[i]);
    assert.equal(parsed.parts[0].hand, 1); assert.equal(parsed.parts[0].sourceNumber, String(i + 1));
    assert.equal(parsed.parts[0].folio.reference, '1v'); assert.equal(parsed.originalNotation, r.notation);
    assert.equal(parsed.parts[0].offset, r.selectedPartOffset); assert.equal(JSON.stringify(r), before);
    assert(api.renderAnnotation(r).html.includes('Feuil1!E11'));
    assert(api.renderAnnotation(r).html.includes('Recovered worksheet annotation'));
  });
});
test('reviewed Bodmer reading uses uiro diuisa while preserving si uncertainty and original uira diuisat', () => {
  const r = api.getSupplementalAnnotations('antiquities', 1)[2], parsed = api.interpretManuscriptAnnotation(r);
  assert.equal(parsed.parts[0].text, 'issa si a uira diuisat');
  assert.equal(parsed.parts[0].displayText, 'issa si a uiro diuisa');
  const html = api.renderAnnotation(r).html;
  assert(visible(html).includes('issa si a uiro diuisa')); assert(html.includes('si remains uncertain'));
  assert(!visible(html).includes('si remains uncertain')); assert(visible(html).includes('(reviewed reading)'));
  assert(html.includes('Original recorded fragment')); assert(html.includes('issa si a uira diuisat'));
});
test('editorial additions do not leak into Bellum, other books or unconfigured DEH notation', () => {
  for (const [w,b] of [['bellum',1], ['deh',1], ['antiquities',2], ['contra-apionem',1]]) {
    assert.deepEqual(api.getSupplementalAnnotations(w,b), []);
  }
});
test('English and French distinguish partial, provisional and reviewed readings', () => {
  const html = visible(api.renderAnnotation(bern, {lang:'fr'}).html);
  assert(!html.includes('Transcription partielle')); assert(html.includes('(lecture provisoire)'));
  assert(html.includes('david <span')); assert(html.includes('[texte incertain]</span> dicit'));
  const bodmer = visible(api.renderAnnotation(api.getSupplementalAnnotations('antiquities',1)[2], {lang:'fr'}).html);
  assert(bodmer.includes('(lecture révisée)')); assert(!bodmer.includes('reste incertain'));
});
