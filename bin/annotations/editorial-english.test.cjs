const {test} = require('node:test');
const assert = require('node:assert/strict');
const api = require('../../assets/js/manuscriptAnnotations.js');
const glossary = require('../../assets/js/annotationEditorialEnglish.js');
const inventory = require('../../_docs/annotation-source-inventory.json');
const make = notation => ({work: 'antiquities', sourceBook: 1, alignmentUnitId: 'latin-book01-num27',
  siglum: 'BernBBMs118', occurrence: 1, notation});
const mainDisplay = html => html.replace(/<details\b[^>]*>[\s\S]*?<\/details>/g, '');
test('the requested correction description is English, with the original preserved in details', () => {
  const r = inventory.records.find(r => r.notation === '[¤2r] (@1 correction avec signe) lucem');
  assert(r);
  const rendered = api.renderAnnotation(r);
  assert(mainDisplay(rendered.html).includes('Editorial note: correction with a sign'));
  assert(!mainDisplay(rendered.html).includes('correction avec signe'));
  assert(rendered.html.includes('<pre>[¤2r] (@1 correction avec signe) lucem</pre>'));
  assert.equal(rendered.interpreted.parts[0].text, 'lucem');
});
test('every observed prefix description has an explicitly inspected glossary entry', () => {
  const descriptions = new Set(inventory.records.flatMap(r => api.interpretManuscriptAnnotation(r).parts.map(p => p.description).filter(Boolean)));
  assert.equal(descriptions.size, 216);
  assert.deepEqual([...descriptions].sort(), Object.keys(glossary.descriptions).sort());
  assert.equal(api.translateEditorialDescription('corrections effacées en marge'), 'erased corrections in the margin');
  assert.equal(api.translateEditorialDescription('signe inconnu'), 'unknown sign');
});
test('mixed French comments are translated separately from literal Latin text', () => {
  const part = api.interpretManuscriptAnnotation(make('[1r] (@1) de pacto ad * (mot effacé?)')).parts[0];
  const segments = api.annotationTextSegments(part);
  assert.deepEqual(segments, [
    {kind: 'recorded', text: 'de pacto ad * ', original: 'de pacto ad * '},
    {kind: 'editorial', text: '(erased word?)', original: '(mot effacé?)'}
  ]);
  const html = api.renderAnnotation(make('[1r] (@1) de pacto ad * (mot effacé?)')).html;
  assert(html.includes('class="annotation-editorial-note" lang="en">(erased word?)'));
  assert.equal(part.text, 'de pacto ad * (mot effacé?)');
});
test('Latin expansions, source diacritics and literal words are never globally replaced', () => {
  for (const text of ['d(imitte) onie et ...', '(milia) hominum', 'rachel docet moysenà', 'verbum croix in textu', '(nomini? Nostri?)']) {
    const part = api.interpretManuscriptAnnotation(make('[1r] (@1) ' + text)).parts[0];
    assert.deepEqual(api.annotationTextSegments(part), [{kind: 'recorded', text, original: text}]);
  }
});
test('whole French editorial remarks and partial mixed remarks do not fabricate Latin', () => {
  assert.deepEqual(api.annotationTextSegments({category: 'textual', text: 'illisible'}),
    [{kind: 'editorial', text: 'illegible', original: 'illisible'}]);
  assert.deepEqual(api.annotationTextSegments({category: 'untranscribable', text: 'illisible moyses'}), [
    {kind: 'editorial', text: 'illegible', original: 'illisible'},
    {kind: 'recorded', text: ' moyses', original: ' moyses'}
  ]);
  assert.equal(api.translateEditorialDescription('XIII-XIV s.?'), '13th–14th century?');
  assert.equal(api.translateEditorialDescription('visage?'), 'face?');
});
test('unknown notation remains unresolved while its French description is translated', () => {
  const r = make('[1r] (¬1 pas médiévale) Menandes [#croix)');
  const parsed = api.interpretManuscriptAnnotation(r);
  const visible = mainDisplay(api.renderAnnotation(r).html);
  assert(visible.includes('not medieval')); assert(visible.includes('[#cross)'));
  assert(visible.includes('¬1')); assert(visible.includes('Menandes'));
  assert(parsed.issues.includes('unknown-code:¬')); assert.equal(parsed.parts[0].hand, null);
  assert.equal(parsed.originalNotation, r.notation);
});
test('French mode retains the original editorial descriptions and comments', () => {
  const r = make('[1r] (@1 correction avec signe) lucem (en marge du bas)');
  const html = mainDisplay(api.renderAnnotation(r, {lang: 'fr'}).html);
  assert(html.includes('correction avec signe')); assert(html.includes('(en marge du bas)'));
  assert(!html.includes('correction with a sign'));
});
test('the complete corpus retains every original character and all recorded-text segments', () => {
  let changedDescriptions = 0, editorialSpans = 0;
  for (const r of inventory.records) {
    const before = JSON.stringify(r), parsed = api.interpretManuscriptAnnotation(r);
    for (const part of parsed.parts) {
      const expected = part.category === 'unresolved' ? part.notation.trim() : part.text;
      const segments = api.annotationTextSegments(part, 'en', r.work);
      assert.equal(segments.map(s => s.original).join(''), expected);
      for (const s of segments) {
        if (s.kind === 'recorded') assert.equal(s.text, s.original);
        else editorialSpans++;
      }
      if (api.translateEditorialDescription(part.description) !== part.description) changedDescriptions++;
    }
    assert.equal(JSON.stringify(r), before);
    assert.equal(parsed.originalNotation, r.notation);
  }
  assert.equal(changedDescriptions, 425); assert.equal(editorialSpans, 94);
});
test('French institutional designations have English display names and retained originals', () => {
  const ms = api.resolveManuscript('ChartresBMMs29');
  assert.equal(ms.displayName, 'Chartres, Municipal Library, Ms. 29');
  assert(ms.originalDisplayName.includes('Bibliothèque municipale'));
  assert(api.resolveManuscript('ChartresBMMs29', null, 'fr').displayName.includes('Bibliothèque municipale'));
  assert(api.resolveManuscript('ColognyBodmer99').displayName.includes('Martin Bodmer Foundation'));
});
test('unconfigured future DEH notation is not translated through the Josephus adapter', () => {
  const r = {...make('[1r] @ lucem (en marge du bas)'), work: 'deh'};
  const p = api.interpretManuscriptAnnotation(r).parts[0];
  assert.equal(api.annotationTextSegments(p, 'en', 'deh').map(s => s.text).join(''), r.notation);
});
