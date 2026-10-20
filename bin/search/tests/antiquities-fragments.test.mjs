import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {buildBundle, createEngine, tokenizeRecord, tokenizeText} from '../engine.mjs';

const require = createRequire(import.meta.url);
const lunr = require('../vendor/lunr.cjs');

function row(id, section, text, order, extra = {}) {
  return {
    id, work: 'antiquities', book: 11, section, text, order,
    language: 'Latin', edition: 'Bamberg 78',
    ...extra,
  };
}
function fragment(id, section, text, order, extra = {}) {
  return row(id, section, text, order, {
    citationUnitId: `antiquities-latin-bamberg78-11-${section}`,
    citationUnitCitation: `XI.${section}`,
    ...extra,
  });
}
const load = records => createEngine(buildBundle(records, lunr), lunr);
const evidenceIds = result => result.hitGroups.flatMap(group => group.hits.flatMap(hit => hit.spans.map(span => span.recordId)));
const sections = result => result.hitGroups.flatMap(group => group.sections);

// Physical order follows the accepted XI.72 pattern: continuation rank 2,
// other Antiquities units, then ranks 1 and 3. The Latin here is synthetic.
const displaced = [
  fragment('latin-xi-72-2', 72, 'septem cantores', 0),
  row('latin-xi-69', 69, 'alia narrantur', 1),
  row('latin-xi-71', 71, 'nunc finit', 2),
  fragment('latin-xi-72-1', 72, 'mancipia cuncta', 3),
  fragment('latin-xi-72-3', 72, 'subiugalia multa', 4),
  row('latin-xi-73', 73, 'postea ueniunt', 5),
];

test('displaced Antiquities fragments satisfy Boolean AND as one canonical citation unit', () => {
  const engine = load(displaced);
  for (const query of ['cantores AND mancipia', 'cantor* AND mancip*', '"septem cantores" AND mancipia']) {
    const result = engine.search(query);
    assert.equal(result.matchingUnits, 1, query);
    assert.equal(result.matchingSections, 1, query);
    assert.equal(result.occurrences, 2, query);
    assert.deepEqual([...new Set(evidenceIds(result))], ['latin-xi-72-2', 'latin-xi-72-1'], query);
    assert.deepEqual([...new Set(sections(result))], [72], query);
  }
  assert.equal(engine.search('cantores AND alia').matchingUnits, 0);
  assert.equal(engine.search('cantores AND alia', {scope: 'book'}).matchingUnits, 1);
});

test('NOT excludes a logical citation if any displaced fragment contains the forbidden term', () => {
  const engine = load(displaced);
  assert.equal(engine.search('cantores AND NOT mancipia').matchingUnits, 0);
  assert.equal(engine.search('NOT (mancipia OR NOT cantores)').matchingUnits, 0);
  const complement = engine.search('NOT mancipia');
  assert.equal(complement.matchingUnits, 3);
  assert.equal(complement.matchingSections, 3);
  assert.equal(complement.occurrences, 0);
  assert.deepEqual([...new Set(sections(complement))], [69, 71, 73]);
  const doubleNegative = engine.search('NOT NOT cantores');
  assert.equal(doubleNegative.matchingUnits, 1);
  assert.equal(doubleNegative.matchingSections, 1);
  assert.equal(doubleNegative.occurrences, 1);
});

test('exact phrases cannot jump over intervening units or reorder displaced fragments', () => {
  const engine = load(displaced);
  for (const scope of ['section', 'book']) {
    for (const query of ['"cantores mancipia"', '"cantor* mancip*"', '"cuncta septem"']) {
      assert.equal(engine.search(query, {scope}).occurrences, 0, `${scope}: ${query}`);
    }
  }
  assert.equal(engine.search('"cantores alia"').occurrences, 0);
  const physical = engine.search('"cantores alia narrantur nunc finit mancipia"', {scope: 'book'});
  assert.equal(physical.occurrences, 1);
  assert.equal(physical.matchingSections, 3, 'two XI.72 fragments count as one citation');
  assert.deepEqual(evidenceIds(physical), ['latin-xi-72-2', 'latin-xi-69', 'latin-xi-71', 'latin-xi-72-1']);
});

test('physically adjacent fragments of the same citation can share an exact phrase and original spans', () => {
  // Deliberately shuffle the input array; record.order establishes continuity.
  const engine = load([displaced[5], displaced[3], displaced[0], displaced[4], displaced[2], displaced[1]]);
  for (const scope of ['section', 'book']) {
    const result = engine.search('"cuncta subiugalia"', {scope});
    assert.equal(result.occurrences, 1);
    assert.equal(result.matchingUnits, 1);
    assert.equal(result.matchingSections, 1);
    const spans = result.hitGroups[0].hits[0].spans;
    assert.deepEqual(spans.map(span => span.recordId), ['latin-xi-72-1', 'latin-xi-72-3']);
    assert.deepEqual(spans.map(span => displaced.find(record => record.id === span.recordId).text.slice(span.start, span.end)), ['cuncta', 'subiugalia']);
  }
});

test('breakBefore and explicit phrase boundaries also separate adjacent fragments of one citation', () => {
  const first = fragment('first', 72, 'prima finis', 0);
  const second = fragment('second', 72, 'initium ultima', 1);
  const alternatives = [
    [first, {...second, breakBefore: true}],
    [{...first, phraseBreaks: [first.text.length]}, second],
    [first, {...second, phraseBreaks: [0]}],
  ];
  for (const records of alternatives) {
    const engine = load(records);
    for (const scope of ['section', 'book']) {
      assert.equal(engine.search('"finis initium"', {scope}).occurrences, 0);
      assert.equal(engine.search('finis AND initium', {scope}).matchingUnits, 1);
      assert.equal(engine.search('finis AND initium', {scope}).matchingSections, 1);
    }
  }
});

test('matchingSections counts canonical units while occurrences retain all fragment evidence', () => {
  const engine = load(displaced);
  for (const scope of ['section', 'book']) {
    const one = engine.search('cantores OR mancipia OR subiugalia', {scope});
    assert.equal(one.matchingUnits, 1);
    assert.equal(one.matchingSections, 1);
    assert.equal(one.occurrences, 3);
    const two = engine.search('cantores OR mancipia OR alia', {scope});
    assert.equal(two.matchingUnits, scope === 'section' ? 2 : 1);
    assert.equal(two.matchingSections, 2);
    assert.equal(two.occurrences, 3);
  }
});

test('Bellum source-passage association does not merge interpolation evidence with Antiquities XI.312', () => {
  const records = [
    fragment('latin-xi-312-1', 312, 'ante narrationem', 0),
    fragment('antiquities-latin-bamberg78-11-BJ.IV.105a', 'BJ.IV.105a', 'uerba belli', 1, {
      citationUnitCitation: 'BJ.IV.105a',
      sourcePassage: {
        identity: 'BJ.IV.105a', occurrence: 'Latin-XI-BJ.IV.105a-1',
        AntiquitiesIdentity: false, primaryAntiquitiesFragment: false,
        association: 312, position: 'before-corresponding-portion',
        editorialStatus: 'CLOSED_USER_APPROVED',
      },
    }),
    fragment('latin-xi-312-2', 312, 'post narrationem', 2),
  ];
  const engine = load(records);
  assert.equal(engine.search('ante AND post').matchingUnits, 1);
  assert.equal(engine.search('ante AND belli').matchingUnits, 0);
  assert.equal(engine.search('ante AND belli', {scope: 'book'}).matchingUnits, 1);
  assert.deepEqual(sections(engine.search('belli')), ['BJ.IV.105a']);
  const withoutInterpolation = engine.search('NOT belli');
  assert.equal(withoutInterpolation.matchingUnits, 1);
  assert.equal(withoutInterpolation.matchingSections, 1);
  assert.deepEqual([...new Set(sections(withoutInterpolation))], [312]);
  assert.equal(engine.search('"narrationem post"').occurrences, 0);
  assert.equal(engine.search('"narrationem post"', {scope: 'book'}).occurrences, 0);
  assert.equal(engine.search('"narrationem uerba"').occurrences, 0);
  assert.equal(engine.search('"narrationem uerba"', {scope: 'book'}).occurrences, 1);
});

test('an explicit zero-width TEI gap inside res+s prevents the invented indexed word ress', () => {
  const record = row('latin-xiii-393', 393, 'ress fuerant', 0, {
    book: 13, phraseBreaks: [3],
    textGaps: [{kind: 'tei-gap', start: 3, end: 3, sourceAttributes: {reason: 'fading'}}],
  });
  assert.deepEqual(tokenizeText(record.text).map(token => token.term), ['ress', 'fuerant'], 'generic plain-text tokenization is unchanged');
  const tokens = tokenizeRecord(record);
  assert.deepEqual(tokens.map(token => token.term), ['res', 's', 'fuerant']);
  assert.deepEqual(tokens.map(token => [token.start, token.end]), [[0, 3], [3, 4], [5, 12]]);
  const bundle = buildBundle([record], lunr);
  assert.equal(bundle.records[0].text, 'ress fuerant', 'the declared gap is metadata; source characters and offsets remain intact');
  assert.equal(bundle.stats.tokens, 3);
  const engine = createEngine(JSON.parse(JSON.stringify(bundle)), lunr);
  for (const scope of ['section', 'book']) {
    assert.equal(engine.search('ress', {scope}).occurrences, 0);
    assert.equal(engine.search('res', {scope}).occurrences, 1);
    assert.equal(engine.search('s', {scope}).occurrences, 1);
    assert.equal(engine.search('res AND s', {scope}).matchingUnits, 1);
    assert.equal(engine.search('"res s"', {scope}).occurrences, 0);
    assert.equal(engine.search('"re* s"', {scope}).occurrences, 0);
    assert.equal(engine.search('"s fuerant"', {scope}).occurrences, 1);
  }
});

test('zero-width gap tokenization retains JavaScript offsets after supplementary Unicode characters', () => {
  const text = '𐌀𐌁 ress fuerant';
  const gap = text.indexOf('ress') + 3;
  const record = row('unicode-gap', 393, text, 0, {
    book: 13, phraseBreaks: [gap],
    textGaps: [{kind: 'tei-gap', start: gap, end: gap, sourceAttributes: {reason: 'fading'}}],
  });
  const engine = load([record]);
  assert.equal(engine.search('ress').occurrences, 0);
  for (const query of ['res', 's']) {
    const span = engine.search(query).hitGroups[0].hits[0].spans[0];
    assert.equal(text.slice(span.start, span.end), query);
  }
  assert.equal(engine.search('"𐌀𐌁 res"').occurrences, 1);
  assert.equal(engine.search('"res s"').occurrences, 0);
});

test('citation grouping is explicit and rejects cross-section or cross-version reuse', () => {
  const ordinary = load([row('ordinary-a', 72, 'prima', 0), row('ordinary-b', 72, 'altera', 1)]);
  assert.equal(ordinary.search('prima AND altera').matchingUnits, 0, 'legacy records without a grouping key stay independent');
  const first = fragment('fragment-a', 72, 'prima', 0);
  for (const conflict of [{section: 73}, {book: 12}, {language: 'Greek'}, {edition: 'Other edition'}, {work: 'bellum'}]) {
    const second = fragment('fragment-b', 72, 'altera', 1, conflict);
    assert.throws(() => buildBundle([first, second], lunr), /citation|logical|inconsistent|conflict/i);
    const valid = buildBundle([first, fragment('fragment-b', 72, 'altera', 1)], lunr);
    Object.assign(valid.records[1], conflict);
    assert.throws(() => createEngine(valid, lunr), /citation|logical|inconsistent|conflict/i);
  }
});
