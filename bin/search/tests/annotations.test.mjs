import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {annotationRecords, annotationInputs, validateAnnotationBundle} from '../build-annotations.mjs';
import {createEngine} from '../engine.mjs';

const root = path.resolve(fileURLToPath(new URL('../../../', import.meta.url)));
const require = createRequire(import.meta.url);
const bundle = validateAnnotationBundle(root);
const engine = createEngine(bundle, require('../vendor/lunr.cjs'));
const matching = (query, options) => new Set(engine.search(query, options).hitGroups.flatMap(group => group.recordIds));

test('all reader annotation parts are indexed once, with original identities and frozen evidence', () => {
  const before = annotationInputs(root);
  const records = annotationRecords(root);
  assert.equal(records.length, 8122);
  assert.deepEqual(['antiquities', 'bellum', 'deh'].map(work => records.filter(record => record.work === work).length), [3247, 2958, 1917]);
  assert.equal(new Set(records.map(record => record.id)).size, 8122);
  assert.deepEqual(annotationInputs(root), before);
  assert.equal(before.filter(item => item.path.endsWith('.xml')).length, 33);
  const inventory = JSON.parse(fs.readFileSync(path.join(root, '_docs/annotation-source-inventory.json')));
  for (const record of records.filter(record => record.work !== 'deh' && !record.id.includes('worksheet'))) {
    assert(inventory.records.some(source => source.notation === record.originalNotation && source.siglum === record.siglum && source.alignmentUnitId === record.alignmentUnitId));
  }
});

test('citations retain unit ranges and DEH chapter/prologue granularity', () => {
  const early = bundle.records.find(record => record.alignmentUnitId === 'latin-book01-num27');
  assert.equal(early.citation, 'Antiquities, Book 1, Niese §§27–33');
  const deh = bundle.records.filter(record => record.work === 'deh');
  assert(deh.every(record => record.alignmentUnitId === null && !record.passageTarget.includes('&unit=')));
  assert.equal(deh[0].citation, 'De excidio, Prologue');
  assert.equal(deh[0].locationTargetId, 'latin-deh1-chapter0');
  assert(deh.some(record => record.citation === 'De excidio, I.26'));
  assert.equal(bundle.records.filter(record => record.verificationStatus !== 'verified').length, 45);
  assert(bundle.records.filter(record => record.verificationStatus !== 'verified').every(record => record.passageTarget === null));
});

test('recorded wording, English descriptions, exact phrases, Boolean logic and wildcards are searchable', () => {
  const symbol = bundle.records.find(record => record.category === 'symbolic' && record.text.includes('nota NT'));
  assert(matching('"nota NT"').has(symbol.id));
  assert(matching('nota AND NT').has(symbol.id));
  assert(matching('not* AND NOT david').has(symbol.id));
  const lucem = bundle.records.find(record => record.text.includes('lucem') && record.text.includes('correction'));
  assert(matching('lucem AND correction').has(lucem.id));
  assert(!matching('"lucem correction"').has(lucem.id), 'a phrase cannot cross into an editorial description');
});

test('reviewed readings match the reader; gap labels and category names add no fabricated words', () => {
  const david = bundle.records.find(record => record.readingStatus === 'provisional reading');
  assert(matching('david AND dicit').has(david.id));
  assert(!matching('"david dicit"').has(david.id));
  assert(!matching('uncertain').has(david.id));
  assert.equal(david.originalNotation, '[¤2v] (§) dicit (@1) issa (#2 nota NT)');
  const bodmer = bundle.records.find(record => record.readingStatus === 'reviewed reading');
  assert(matching('"issa si a uiro diuisa"').has(bodmer.id));
  assert(!matching('diuisat').has(bodmer.id));
  assert.equal(bundle.records.filter(record => record.work === 'deh' && record.category === 'untranscribable').length, 21);
});

test('Unicode e caudata and original DEH source rows are preserved without indexing TeX notation', () => {
  const row = bundle.records.find(record => record.work === 'deh' && record.text.includes('Iudęorum'));
  assert(matching('Iudęorum').has(row.id));
  assert(row.originalNotation.includes('\\c{e}'));
  assert(!row.text.includes('\\c{e}'));
  const deh = JSON.parse(fs.readFileSync(path.join(root, 'assets/data/deh-annotations/annotations.json')));
  for (const original of deh.records) {
    const indexed = bundle.records.find(record => record.sourceRow === original.sourceRow);
    assert.equal(indexed.originalNotation, original.original.contenu);
    assert.equal(indexed.id, `${original.presentationId}-at-0`);
  }
});

test('no Boolean condition or phrase combines distinct notes, and Latin spelling equivalence remains optional', () => {
  const first = bundle.records.find(record => record.text.includes('lucem'));
  const term = first.text.match(/[\p{L}]+/u)[0];
  const absent = 'nonexistentannotationword';
  assert(!matching(`${term} AND ${absent}`).has(first.id));
  const david = bundle.records.find(record => record.readingStatus === 'provisional reading');
  assert(!matching('david AND issa').has(david.id), 'adjacent source notes are independent');
  const deIosepho = bundle.records.find(record => record.work === 'deh' && record.text === 'de Iosepho');
  assert(!matching('Josepho').has(deIosepho.id));
  assert(matching('Josepho', {fold: true}).has(deIosepho.id));
});

test('publication fingerprints allow line-ending representation changes and reject changed source words', t => {
  const inputs = annotationInputs(root);
  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'lj-annotation-search-'));
  t.after(() => fs.rmSync(fixture, {recursive: true, force: true}));
  for (const item of inputs) {
    const destination = path.join(fixture, item.path);
    fs.mkdirSync(path.dirname(destination), {recursive: true});
    fs.copyFileSync(path.join(root, item.path), destination);
  }
  for (const name of ['assets/xml/antiquities/Latin/book-01.xml', 'assets/xml/antiquities/niese/book-14.json']) {
    const destination = path.join(fixture, name);
    const content = fs.readFileSync(destination, 'utf8').replace(/\r\n/gu, '\n');
    fs.writeFileSync(destination, content.replace(/\n/gu, '\r\n'));
  }
  assert.deepEqual(annotationInputs(fixture), inputs);
  const xml = path.join(fixture, 'assets/xml/antiquities/Latin/book-01.xml');
  fs.appendFileSync(xml, '\n<!-- Changed scholarly source -->\n');
  assert.throws(() => annotationInputs(fixture), /Stale citation evidence/u);
});
