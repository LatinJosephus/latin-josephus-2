import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {buildBundle, createEngine, phraseBreakOffsets} from '../engine.mjs';
import {buildConcordance} from '../concordance.mjs';

const require = createRequire(import.meta.url);
const lunr = require('../vendor/lunr.cjs');
const passage = (section, text, phraseBreaks = [], more = {}) => ({
  id: `ca-${section}`, work: 'contra-apionem', book: 1, section,
  language: 'Latin', edition: 'Boysen (1898)', order: section - 1,
  text, phraseBreaks, ...more,
});
const load = records => createEngine(buildBundle(records, lunr), lunr);

test('source markers interrupt exact phrases in both scopes while Boolean words remain searchable', () => {
  const records = [passage(1, 'prima uerba *** altera uerba', [12])];
  const engine = load(records);
  for (const scope of ['section', 'book']) {
    assert.equal(engine.search('"uerba altera"', {scope}).occurrences, 0);
    assert.equal(engine.search('"uerb* alter*"', {scope}).occurrences, 0);
    assert.equal(engine.search('"prima uerba"', {scope}).occurrences, 1);
    assert.equal(engine.search('"altera uerba"', {scope}).occurrences, 1);
    assert.equal(engine.search('prima AND altera', {scope}).matchingUnits, 1);
    assert.equal(engine.search('"uerba altera" OR prima', {scope}).occurrences, 1);
    assert.equal(engine.search('uerba', {scope}).occurrences, 2);
  }
  assert.equal(engine.records[0].text, records[0].text);
});

test('leading, trailing and marker-only units cannot create cross-section phrases', () => {
  const records = [
    passage(1, 'prima finis ***', [12]), passage(2, 'altera initium'),
    passage(3, '*** tertia finis', [0]), passage(4, 'quarta initium'),
    passage(5, '** *', [0]), passage(6, 'ultima uerba'),
  ];
  const engine = load(records);
  for (const query of ['"finis altera"', '"initium tertia"', '"initium ultima"']) {
    assert.equal(engine.search(query, {scope: 'book'}).occurrences, 0, query);
  }
  assert.equal(engine.search('"finis quarta"', {scope: 'book'}).occurrences, 1);
  assert.equal(engine.search('prima AND ultima', {scope: 'book'}).matchingUnits, 1);
});

test('multiple explicit boundaries work with spelling equivalence and original Unicode offsets', () => {
  const text = '𐌀𐌁 Iudaei * uiri ** Judaei';
  const record = passage(1, text, [text.indexOf('*'), text.indexOf('**')]);
  const engine = load([record]);
  for (const scope of ['section', 'book']) {
    assert.equal(engine.search('"Judaei viri"', {scope, fold: true}).occurrences, 0);
    assert.equal(engine.search('"uiri Iudaei"', {scope, fold: true}).occurrences, 0);
    const result = engine.search('"𐌀𐌁 Judaei"', {scope, fold: true});
    assert.equal(result.occurrences, 1);
    const span = result.hitGroups[0].hits[0].spans[0];
    assert.equal(text.slice(span.start, span.end), '𐌀𐌁 Iudaei');
  }
});

test('legacy bundle inputs remain unchanged when explicit phrase boundaries are absent', () => {
  const record = passage(1, 'finis, initium');
  delete record.phraseBreaks;
  const bundle = buildBundle([record], lunr);
  const frozen = JSON.stringify(bundle);
  const engine = createEngine(bundle, lunr);
  assert.equal(engine.search('"finis initium"').occurrences, 1);
  assert.equal(JSON.stringify(bundle), frozen);
  assert.equal(Object.hasOwn(bundle.records[0], 'phraseBreaks'), false);
});

test('invalid boundary metadata is rejected at build and load instead of silently changing phrases', () => {
  for (const breaks of [null, '4', [NaN], [-1], [100], [2], [4, 4], [8, 4], [4.5]]) {
    const record = passage(1, 'ante *** post', breaks);
    assert.throws(() => buildBundle([record], lunr), /phrase boundar/i);
    const bundle = buildBundle([passage(1, record.text)], lunr);
    bundle.records[0].phraseBreaks = breaks;
    assert.throws(() => createEngine(bundle, lunr), /phrase boundar/i);
  }
  assert.deepEqual(phraseBreakOffsets(passage(1, 'ante post', [0, 4, 9])), [0, 4, 9]);
});

test('concordance rejects forged phrases through internal and inter-section markers', () => {
  const records = [passage(1, 'ante *** post', [5]), passage(2, 'finis ***', [6]), passage(3, 'initium')];
  const engine = load(records);
  const forged = engine.search('ante AND post');
  forged.hitGroups[0].hits = [{kind: 'phrase', queryText: '"ante post"', spans: [{recordId: records[0].id, start: 0, end: records[0].text.length}]}];
  assert.throws(() => buildConcordance(forged, records), /phrase.*(gap|boundar)/i);
  const joined = engine.search('finis AND initium', {scope: 'book'});
  joined.hitGroups[0].hits = [{kind: 'phrase', queryText: '"finis initium"', spans: [
    {recordId: records[1].id, start: 0, end: 5}, {recordId: records[2].id, start: 0, end: 7},
  ]}];
  assert.throws(() => buildConcordance(joined, records), /phrase.*(gap|boundar)/i);
});
