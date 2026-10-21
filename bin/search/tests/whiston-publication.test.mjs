/** Test the Whiston source gate using copies; accepted scholarly XML is never edited. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {validateWhistonSourceProjection} from '../whiston-publication.mjs';

const repository = path.resolve(fileURLToPath(new URL('../../../', import.meta.url)));
const read = relative => JSON.parse(fs.readFileSync(path.join(repository, relative), 'utf8'));
const manifest = read('bin/search/config/antiquities-english-whiston.json');
const books = new Map(manifest.books.map(spec => {
  const stem = `bin/search/data/antiquities-english-whiston/book-${String(spec.number).padStart(2, '0')}`;
  return [spec.number, {corpus: read(`${stem}.corpus.json`), report: read(`${stem}.extraction-report.json`)}];
}));

function fresh(number = 1) {
  return {number, ...structuredClone(books.get(number)), manifest: structuredClone(manifest)};
}

function verify(input, root = repository) {
  return validateWhistonSourceProjection(input.corpus, input.report, input.manifest,
    input.manifest.books.find(book => book.number === input.number), root);
}

test('Whiston source gate verifies all1710 actual intervals and their reversible source offsets', () => {
  const expected = [[346, 21994, 83], [349, 23020, 76], [322, 20955, 79], [331, 22900, 88], [362, 23396, 98]];
  for (const [index, [sections, tokens, restoredParagraphs]] of expected.entries()) {
    assert.deepEqual(verify(fresh(index + 1)), {status: 'PASS', sections, tokens, sourceDocuments: index ? 1 : 2, restoredParagraphs});
  }
});

test('Whiston source gate validates text and book-specific reader metadata in every newly added book', async t => {
  for (const number of [2, 3, 4, 5]) await t.test(`Book ${number}`, () => {
    const input = fresh(number);
    input.corpus[0].text += ' Unreviewed words.';
    assert.throws(() => verify(input), /record text, source identity, reader metadata or phrase boundary differs/u);
    const wrongReader = fresh(number);
    wrongReader.corpus[0].readerLink.params.book = 1;
    assert.throws(() => verify(wrongReader), /record text, source identity, reader metadata or phrase boundary differs/u);
    const falseProemBoundary = fresh(number);
    falseProemBoundary.corpus[26].breakBefore = true;
    assert.throws(() => verify(falseProemBoundary), /record text, source identity, reader metadata or phrase boundary differs/u);
  });
});

test('Whiston source gate rejects altered words, punctuation and source order', async t => {
  for (const [label, mutate] of [
    ['altered running word', value => { value[0].text = value[0].text.replace('THOSE', 'THESE'); }],
    ['stripped original punctuation', value => { value[0].text = value[0].text.replace(',', ''); }],
    ['changed citation identity', value => { value[27].section = 999; }],
    ['swapped adjacent intervals', value => { [value[28], value[29]] = [value[29], value[28]]; }],
    ['invented empty interval', value => { value[30].text = ''; }],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input.corpus);
    assert.throws(() => verify(input), /record text, source identity, reader metadata or phrase boundary differs/u);
  });
});

test('Whiston source gate requires correct English reader selection and Proem boundaries', async t => {
  for (const [label, mutate] of [
    ['lost Whiston reader override', value => { delete value[0].readerLink.params.english; }],
    ['reader URL opens another edition', value => { value[27].url = '/antiquities/?book=1&niese=28'; }],
    ['Proem points to narrative book', value => { value[0].readerLink.params.book = 1; }],
    ['lost Proem division', value => { delete value[0].sourceDivision; }],
    ['lost Proem end boundary', value => { delete value[26].breakBefore; }],
    ['invented phrase interruption', value => { value[27].phraseBreaks = [5]; }],
    ['wrong original source ID', value => { value[0].sourceId = 'latin-preface-num1'; }],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input.corpus);
    assert.throws(() => verify(input), /record text, source identity, reader metadata or phrase boundary differs/u);
  });
});

test('Whiston source gate rejects inconsistent source ledgers even when records still look correct', async t => {
  for (const [label, mutate] of [
    ['shifted original-text offset', value => { value.paragraphs[0].sourcePieces[0].sourceEnd++; }],
    ['changed record slice', value => { value.paragraphs[0].sourcePieces.find(piece => piece.kind === 'record').recordStart++; }],
    ['missing source paragraph', value => { value.paragraphs.pop(); }],
    ['deleted prefix punctuation evidence', value => {
      const paragraph = value.paragraphs.find(item => item.sourceId === 'english-preface-num5');
      paragraph.sourcePieces = paragraph.sourcePieces.filter(piece => piece.reason !== 'pre-marker-label-punctuation');
    }],
    ['false milestone position', value => { value.documentReports[0].paragraphs[0].nieseMarkers[0].sourceTextOffset++; }],
    ['unverified source contract', value => { value.documentReports[0].sourceContract.verified = false; }],
    ['false restoration hash', value => { value.coverage.restoredParagraphSequenceSha256 = '0'.repeat(64); }],
    ['false token count', value => { value.counts.runningWordTokens--; }],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input.report);
    assert.throws(() => verify(input), /Whiston/u);
  });
});

test('Whiston source gate refuses unreviewed books and unapproved source paths', async t => {
  await t.test('test-only Book IX cannot become published scope', () => {
    const input = fresh();
    input.manifest.books.push({...input.manifest.books[0], number: 9});
    assert.throws(() => verify(input), /collection includes an unreviewed book/u);
  });
  await t.test('Latin source cannot be substituted for Whiston', () => {
    const input = fresh();
    input.manifest.books[0].source = 'assets/xml/antiquities/Latin/book-01.xml';
    assert.throws(() => verify(input), /book source scope differs/u);
  });
});

test('Whiston IV.276 continuation evidence is checked independently of its displayed record', async t => {
  for (const [label, mutate] of [
    ['deleted continuation text', value => { value.corpus[275].text = value.corpus[275].text.split('\n\n')[0]; }],
    ['wrong continuation source identity', value => { value.corpus[275].sourceIds.pop(); }],
    ['unrecorded paragraph separator', value => {
      delete value.report.paragraphs.find(paragraph => paragraph.sourceId === 'english-book04-num276b').recordJoin;
    }],
    ['altered synthetic separator span', value => {
      value.report.documentReports[0].paragraphs.find(paragraph => paragraph.sourceId === 'english-book04-num276b').recordJoin.end++;
    }],
    ['invented Niese milestone', value => {
      value.report.paragraphs.find(paragraph => paragraph.sourceId === 'english-book04-num276b').nieseMarkers = [{section: 276}];
    }],
    ['changed continuation record offset', value => {
      value.report.paragraphs.find(paragraph => paragraph.sourceId === 'english-book04-num276b').sections[0].recordOffset--;
    }],
  ]) await t.test(label, () => {
    const input = fresh(4);
    mutate(input);
    assert.throws(() => verify(input), /Whiston/u);
  });
});

test('Whiston source gate accepts CRLF equivalence but refuses actual XML changes', async t => {
  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'latin-josephus-whiston-source-'));
  t.after(() => fs.rmSync(fixture, {recursive: true, force: true}));
  const sourcePaths = manifest.books.flatMap(book => [book.source, ...(book.additionalSources || [])]);
  for (const relative of sourcePaths) {
    const filename = path.join(fixture, relative);
    fs.mkdirSync(path.dirname(filename), {recursive: true});
    fs.copyFileSync(path.join(repository, relative), filename);
  }
  await t.test('all six indexed files may have Windows line endings', () => {
    for (const relative of sourcePaths) {
      const filename = path.join(fixture, relative);
      fs.writeFileSync(filename, fs.readFileSync(filename, 'utf8').replace(/\r?\n/gu, '\r\n'));
    }
    for (const number of [1, 2, 3, 4, 5]) assert.equal(verify(fresh(number), fixture).status, 'PASS');
  });
  for (const number of [1, 2, 3, 4, 5]) await t.test(`Book ${number} source changes fail despite a refreshed fingerprint`, () => {
    const input = fresh(number), relative = manifest.books.find(book => book.number === number).source;
    const filename = path.join(fixture, relative), original = fs.readFileSync(filename);
    fs.appendFileSync(filename, '\n<!-- Unreviewed source change -->\n');
    try {
      const changed = fs.readFileSync(filename), fingerprint = {path: relative,
        sha256: createHash('sha256').update(changed).digest('hex'), bytes: changed.length};
      input.report.source = fingerprint;
      input.report.sources[number === 1 ? 1 : 0] = fingerprint;
      input.report.documentReports[number === 1 ? 1 : 0].source = fingerprint;
      assert.throws(() => verify(input, fixture), /source differs from the accepted source/u);
    } finally { fs.writeFileSync(filename, original); }
  });
});
