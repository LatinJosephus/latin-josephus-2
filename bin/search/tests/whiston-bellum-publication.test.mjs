/** Exercise the strict Bellum source gate without changing scholarly files. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {validateWhistonBellumSourceProjection} from '../whiston-bellum-publication.mjs';
import {buildBundle, createEngine} from '../engine.mjs';

const require = createRequire(import.meta.url), lunr = require('../vendor/lunr.cjs');
const repository = path.resolve(fileURLToPath(new URL('../../../', import.meta.url)));
const read = relative => JSON.parse(fs.readFileSync(path.join(repository, relative), 'utf8'));
const manifest = read('bin/search/config/bellum-english-whiston.json');
const books = new Map(manifest.books.map(spec => {
  const stem = `bin/search/data/bellum-english-whiston/book-${String(spec.number).padStart(2, '0')}`;
  return [spec.number, {corpus: read(stem + '.corpus.json'), report: read(stem + '.extraction-report.json')}];
}));
const fresh = (number = 1) => ({number, ...structuredClone(books.get(number)), manifest: structuredClone(manifest)});
const verify = (input, root = repository) => validateWhistonBellumSourceProjection(input.corpus, input.report, input.manifest,
  input.manifest.books.find(spec => spec.number === input.number), root);
const tokens = text => Array.from(text.matchAll(/[\p{L}\p{N}][\p{L}\p{M}\p{N}]*/gu), match => match[0]);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');

test('Whiston Bellum source gate verifies all4001 canonical intervals and704 paragraph restorations', () => {
  const expected = [[673, 50097, 234], [654, 38098, 143], [542, 24777, 88], [663, 30489, 78],
    [572, 29415, 65], [442, 21949, 50], [455, 20247, 46]];
  for (const [index, [sections, tokens, restoredParagraphs]] of expected.entries()) {
    assert.deepEqual(verify(fresh(index + 1)), {status: 'PASS', sections, tokens, sourceDocuments: 1, restoredParagraphs});
  }
});

test('Whiston Bellum corpus text, metadata, ordering and phrase barriers are independently source-checked', async t => {
  for (const [label, mutate] of [
    ['altered running word', input => { input.corpus[0].text += ' Invented words.'; }],
    ['removed punctuation', input => { input.corpus[0].text = input.corpus[0].text.replace(',', ''); }],
    ['wrong citation', input => { input.corpus[0].section++; }],
    ['reordered records', input => { [input.corpus[0], input.corpus[1]] = [input.corpus[1], input.corpus[0]]; }],
    ['lost Whiston selection', input => { delete input.corpus[0].readerLink.params.english; }],
    ['wrong reader work', input => { input.corpus[0].readerLink.path = 'antiquities/'; }],
    ['wrong reader URL edition', input => { input.corpus[0].url = input.corpus[0].url.replace('whiston', 'lodge1602'); }],
    ['invented English xml:id', input => { input.corpus[0].sourceId = 'english-bellum1-num1'; }],
    ['lost sameAs provenance kind', input => { delete input.corpus[0].sourceIdentityKind; }],
    ['invented chapter0 phrase barrier', input => { input.corpus[30].breakBefore = true; }],
    ['invented inline phrase break', input => { input.corpus[0].phraseBreaks = [7]; }],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input);
    assert.throws(() => verify(input), /record text, editorial annotation, source identity, reader metadata or phrase boundary differs/u);
  });
});

test('Every Bellum book rejects altered source text and metadata', async t => {
  for (let number = 1; number <= 7; number++) await t.test(`Book ${number}`, () => {
    const input = fresh(number);
    input.corpus.at(-1).text += ' changed';
    assert.throws(() => verify(input), /differs from accepted XML/u);
    const wrong = fresh(number);
    wrong.corpus[0].readerLink.params.book = number + 1;
    assert.throws(() => verify(wrong), /differs from accepted XML/u);
  });
});

test('Bellum source-ledger corruption cannot pass with otherwise unchanged records', async t => {
  for (const [label, mutate] of [
    ['source slice offset', value => { value.paragraphs[0].sourcePieces[0].sourceEnd++; }],
    ['record slice offset', value => { value.paragraphs[0].sourcePieces.find(p => p.kind === 'record').recordStart++; }],
    ['missing source paragraph', value => { value.paragraphs.pop(); }],
    ['altered paragraph text', value => { value.paragraphs[0].rawText += ' '; }],
    ['altered marker offset', value => { value.paragraphs[0].nieseMarkers[0].sourceTextOffset++; }],
    ['lost sameAs source reference', value => { value.paragraphs[0].sourceAttributes.sameAs = '#wrong'; }],
    ['invented parent attribute', value => { value.paragraphs[0].parentAttributes.type = 'invented'; }],
    ['changed source contract', value => { value.sourceContract.normalizedSHA256 = '0'.repeat(64); }],
    ['unverified source contract', value => { value.sourceContract.verified = false; }],
    ['false source restoration', value => { value.coverage.restoredParagraphSequenceSha256 = '0'.repeat(64); }],
    ['false word count', value => { value.counts.runningWordTokens--; }],
    ['invented omission', value => { value.excludedBlocks = [{kind: 'note', text: 'omitted'}]; }],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input.report);
    assert.throws(() => verify(input), /source restoration report differs/u);
  });
});

test('Bellum VII208 and209 preserve the nested supplied span and its source attribution', async t => {
  const original = books.get(7);
  assert.deepEqual(original.corpus.flatMap(record => record.editorialMarks.map(mark => [record.section, mark.start, mark.end])),
    [[208, 157, 262], [209, 0, 154]]);
  for (const [label, mutate] of [
    ['lost supplied text', input => { input.corpus[207].text = input.corpus[207].text.slice(0, 157); }],
    ['lost supplied annotation', input => { input.corpus[208].editorialMarks = []; }],
    ['shifted supplied span', input => { input.corpus[207].editorialMarks[0].start++; }],
    ['reinterpreted as addition', input => { input.corpus[208].editorialMarks[0].kind = 'add'; }],
    ['lost source attribution', input => { delete input.corpus[208].editorialMarks[0].sourceAttributes.source; }],
    ['lost nested209 record', input => { input.corpus.splice(208, 1); }],
    ['false supplied phrase break', input => { input.corpus[208].breakBefore = true; }],
    ['lost nested209 marker evidence', input => {
      const paragraph = input.report.paragraphs.find(p => p.editorialSpans.length);
      paragraph.nieseMarkers = paragraph.nieseMarkers.filter(m => m.section !== 209);
    }],
    ['lost source span ledger', input => { input.report.paragraphs.find(p => p.editorialSpans.length).editorialSpans = []; }],
  ]) await t.test(label, () => {
    const input = fresh(7);
    mutate(input);
    assert.throws(() => verify(input), /Whiston Bellum/u);
  });
});

test('Bellum BookV chapter13 retains its accepted missing type attribute', () => {
  const input = fresh(5), paragraph = input.report.paragraphs.find(p => p.parentAttributes.n === '13');
  assert.deepEqual(paragraph.parentAttributes, {n: '13', sameAs: '#latin-bellum5-chapter13'});
  paragraph.parentAttributes.type = 'chapter';
  assert.throws(() => verify(input), /source restoration report differs/u);
});

test('Bellum whole-book phrases cross the embedded preface, chapter and supplied-section boundaries', () => {
  for (const [book, left, right] of [[1, 30, 31], [7, 208, 209], [7, 209, 210]]) {
    const pair = books.get(book).corpus.filter(record => [left, right].includes(record.section));
    const phrase = [...tokens(pair[0].text).slice(-3), ...tokens(pair[1].text).slice(0, 3)].join(' ');
    const engine = createEngine(buildBundle(pair, lunr), lunr);
    assert.equal(engine.search(`"${phrase}"`, {scope: 'section'}).matchingUnits, 0);
    const result = engine.search(`"${phrase}"`, {scope: 'book'});
    assert.equal(result.matchingUnits, 1);
    assert.equal(result.occurrences, 1);
    assert.deepEqual(result.hitGroups.flatMap(group => group.recordIds), pair.map(record => record.id));
  }
  const supplied = books.get(7).corpus[207];
  const engine = createEngine(buildBundle([supplied], lunr), lunr);
  assert.equal(engine.search('"were slain to the number of one thousand seven hundred"').occurrences, 1);
});

test('Bellum phrases cannot continue into another book', () => {
  const pair = [books.get(1).corpus.at(-1), books.get(2).corpus[0]];
  const phrase = [...tokens(pair[0].text).slice(-3), ...tokens(pair[1].text).slice(0, 3)].join(' ');
  const engine = createEngine(buildBundle(pair, lunr), lunr);
  assert.equal(engine.search(`"${phrase}"`, {scope: 'book'}).matchingUnits, 0);
});

test('Bellum collection cannot silently gain books or substitute another source', async t => {
  await t.test('unreviewed BookVIII', () => {
    const input = fresh();
    input.manifest.books.push({...input.manifest.books[0], number: 8});
    assert.throws(() => verify(input), /collection includes an unreviewed book/u);
  });
  await t.test('Latin source', () => {
    const input = fresh();
    input.manifest.books[0].source = 'assets/xml/bellum/Latin/book-01.xml';
    assert.throws(() => verify(input), /book source scope differs/u);
  });
});

test('Bellum XML gate accepts both line endings and rejects all seven actual source mutations', async t => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'whiston-bellum-gate-'));
  try {
    const directory = path.join(temp, 'assets/xml/bellum/English');
    fs.mkdirSync(directory, {recursive: true});
    for (const spec of manifest.books) {
      const original = fs.readFileSync(path.join(repository, spec.source));
      fs.writeFileSync(path.join(temp, spec.source), original);
    }
    for (let number = 1; number <= 7; number++) {
      await t.test(`Book${number}: CRLF and LF`, () => {
        const input = fresh(number), filename = path.join(temp, input.report.source.path);
        const original = fs.readFileSync(filename), crlf = Buffer.from(original.toString('latin1').replace(/\r\n/gu, '\n').replace(/\n/gu, '\r\n'), 'latin1');
        fs.writeFileSync(filename, crlf);
        assert.equal(verify(input, temp).status, 'PASS');
        input.report.source = {path: input.report.source.path, sha256: hash(crlf), bytes: crlf.length};
        input.report.sources = [input.report.source];
        assert.equal(verify(input, temp).status, 'PASS');
        fs.writeFileSync(filename, original);
        assert.equal(verify(input, temp).status, 'PASS');
      });
      await t.test(`Book${number}: changed source despite refreshed fingerprint`, () => {
        const input = fresh(number), filename = path.join(temp, input.report.source.path), original = fs.readFileSync(filename);
        const changed = Buffer.from(original.toString('utf8').replace('<text ', '<text altered="yes" '));
        fs.writeFileSync(filename, changed);
        input.report.source = {path: input.report.source.path, sha256: hash(changed), bytes: changed.length};
        input.report.sources = [input.report.source];
        assert.throws(() => verify(input, temp), /source differs from the accepted source/u);
        fs.writeFileSync(filename, original);
      });
    }
  } finally {
    fs.rmSync(temp, {recursive: true, force: true});
  }
});
