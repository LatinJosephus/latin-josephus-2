const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const api = require('../../assets/js/manuscriptAnnotations.js');
const deh = require('../../assets/js/dehManuscriptAnnotations.js');
const data = require('../../assets/data/deh-annotations/annotations.json');
const citations = require('../../assets/data/alignment-citations.json');
api.setCitationData(citations); api.setDEHAnnotationData(data);
const all = [1, 2, 3, 4, 5].flatMap(book => api.getDEHAnnotations(book));
const row = number => all.find(record => record.sourceRow === number);

test('all 1917 CSV rows are represented once, with source-only display identities', () => {
  assert.equal(all.length, 1917); assert.equal(new Set(all.map(r => r.presentationId)).size, 1917);
  assert(all.every(r => r.originalId === null && r.alignmentUnitId === null));
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname, '../../_docs/deh-annotations/source.csv'))).digest('hex'), data.source.sha256);
});
test('only columns A-E are used by the display adapter', () => {
  for (const record of all) assert.deepEqual(Object.keys(record.originalCSVRow), ['manuscrit', 'folio', 'section', 'main', 'contenu']);
  const html = api.renderAnnotation(row(7)).html;
  for (const ignored of ['longueur', 'theme', 'jumeau', 'famille', 'livre', 'chapitre']) assert(!html.includes(`<dt>${ignored}</dt>`));
});
test('every imported location resolves to a whole chapter, never its first unit', () => {
  for (const record of all) {
    const citation = api.resolveAlignmentCitation('deh', record.locationTargetId);
    assert.equal(citation.verificationStatus, 'verified'); assert.equal(citation.granularity, 'chapter');
    assert.equal(citation.citationSystem, 'deh'); assert(!citation.navigationTarget.includes('&unit='));
    assert.deepEqual(citation.alignmentUnitIds, record.coveredAlignmentUnitIds);
  }
});
test('I.26 and I.26.3 remain distinct citations with independently verified boundaries', () => {
  const chapter = api.resolveAlignmentCitation('deh', 'latin-deh1-chapter26');
  assert.equal(chapter.publicCitation, 'I.26'); assert.equal(chapter.start, 'I.26.1');
  assert.equal(chapter.navigationTarget, '/deh/?book=1&chapter=26#latin-deh1-chapter26');
  assert.equal(api.resolveAlignmentCitation('deh', 'latin-deh1-num78').publicCitation, 'I.26.3');
  assert(chapter.alignmentUnitIds.includes('latin-deh1-num78'));
});
test('editor-approved 0.1 note covers all three prologue units', () => {
  const record = row(2), citation = api.resolveAlignmentCitation('deh', record.locationTargetId);
  assert.equal(record.originalAlignmentReference, '0.1'); assert.equal(record.locationTargetId, 'latin-deh1-chapter0');
  assert.equal(citation.publicCitation, 'Prologue');
  assert.deepEqual(citation.alignmentUnitIds, ['latin-deh1-num1', 'latin-deh1-num2', 'latin-deh1-num3']);
});
test('source hand numbers are manuscript-local, including differing Karlsruhe prefixes', () => {
  for (const record of all) {
    const interpreted = api.interpretManuscriptAnnotation(record);
    const suffix = record.sourceHand.match(/^\d+-(\d+)$/);
    assert.equal(interpreted.parts[0].hand, suffix ? Number(suffix[1]) : null);
  }
  const unusual = all.find(r => r.siglum === 'Karlsruhe 82' && r.sourceHand === '81-4');
  const html = api.renderAnnotation(unusual).html;
  assert(html.includes('Hand 4')); assert(html.includes('81-4')); assert(html.includes('Karlsruhe'));
});
test('non-numeric source hand codes never invent a hand', () => {
  for (const record of all.filter(r => ['in-text', '--'].includes(r.sourceHand))) {
    assert.equal(api.interpretManuscriptAnnotation(record).parts[0].hand, null);
    assert(!api.renderAnnotation(record).html.includes('class="annotation-hand"'));
  }
});
test('confirmed e caudata conversion is presentation-only and raw source remains in details', () => {
  const record = row(7), before = JSON.stringify(record), rendered = api.renderAnnotation(record);
  assert(rendered.html.includes('Iudęorum')); assert(rendered.html.includes('Iud\\c{e}orum'));
  assert.equal(rendered.interpreted.originalNotation, record.notation); assert.equal(JSON.stringify(record), before);
});
test('whole and partial untranscribed entries retain separate recorded words and original evidence', () => {
  const whole = all.find(r => r.notation === '[*]');
  assert.equal(api.interpretManuscriptAnnotation(whole).parts[0].category, 'untranscribable');
  const first = row(3), html = api.renderAnnotation(first).html;
  assert.equal(api.interpretManuscriptAnnotation(first).parts[0].category, 'textual');
  assert(html.includes('[untranscribed text]')); assert(html.includes('nostram adhibendam quam'));
  assert(html.includes('[*]')); assert(!html.includes('annotation-category">Partly transcribed'));
  const french = api.renderAnnotation(first, {lang: 'fr'}).html;
  assert(french.includes('lang="fr">[texte non transcrit]</span>'));
});
test('DEH ellipses and literal Josephus symbols never invoke the Josephus convention', () => {
  for (const record of all.filter(r => r.notation.includes('...'))) assert.equal(api.interpretManuscriptAnnotation(record).parts[0].abbreviated, false);
  const record = {...row(2), notation: '[¤1r] @ # § text'};
  const part = api.interpretManuscriptAnnotation(record).parts[0];
  assert.equal(part.category, 'textual'); assert.equal(part.text, record.notation); assert.equal(part.hand, 2);
  assert.equal(part.folio.reference, '1v');
});
test('DEH uses its own explanatory legend in both interface languages', () => {
  for (const lang of ['en', 'fr']) {
    const legend = api.legend(lang, 'deh');
    assert(legend.includes('annotation-notation-key')); assert(legend.includes('678-1')); assert(!legend.includes('@ ='));
  }
});
test('St. Gall pagination, other foliation and source manuscript links are retained', () => {
  const html = api.renderAnnotation(row(323)).html;
  assert(html.includes('p. 33')); assert(html.includes('/manuscripts/#ljm-M0508'));
  const cambrai = all.find(r => r.siglum === 'Cambrai 678');
  assert(api.renderAnnotation(cambrai).html.includes('fol. ' + cambrai.folioReference));
  for (const record of all) assert.equal(api.resolveManuscript(record.siglum).verificationStatus, 'verified');
});
test('repeated source rows are retained as distinct records with distinct anchors', () => {
  for (const group of [[336, 337], [822, 823, 824], [1805, 1806], [1851, 1852]]) {
    assert.equal(new Set(group.map(number => api.renderAnnotation(row(number)).interpreted.anchor)).size, group.length);
    assert(group.every(number => row(number).notation === row(group[0]).notation));
  }
});
test('all rendering preserves every original row and one display entry per record', () => {
  for (const record of all) {
    const snapshot = JSON.stringify(record), rendered = api.renderAnnotation(record);
    assert.equal(rendered.count, 1); assert.equal(JSON.stringify(record), snapshot);
    assert.equal(rendered.interpreted.originalRecord, record);
    assert(rendered.html.includes('data-chapter-target="' + record.locationTargetId + '"'));
    assert(!rendered.html.includes('data-alignment-unit='));
    assert(rendered.html.includes('View chapter'));
  }
});
test('invalid or duplicate dataset identities are rejected', () => {
  assert.throws(() => deh.setData({...data, convention: 'josephus'}));
  assert.throws(() => deh.setData({...data, records: [...data.records.slice(1), data.records[1]]}));
});
test('a missing DEH interpreter is reported rather than silently dropping every note', () => {
  const context = {};
  require('node:vm').runInNewContext(fs.readFileSync(path.join(__dirname, '../../assets/js/manuscriptAnnotations.js'), 'utf8'), context);
  assert.throws(() => context.ManuscriptAnnotations.setDEHAnnotationData(data), /interpreter unavailable/);
});
