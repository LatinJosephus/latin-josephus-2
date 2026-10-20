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
const corpus = read('bin/search/data/antiquities-english-whiston/book-01.corpus.json');
const report = read('bin/search/data/antiquities-english-whiston/book-01.extraction-report.json');

function fresh() {
  return {corpus: structuredClone(corpus), report: structuredClone(report), manifest: structuredClone(manifest)};
}

function verify(input, root = repository) {
  return validateWhistonSourceProjection(input.corpus, input.report, input.manifest, input.manifest.books[0], root);
}

test('Whiston source gate verifies all346 actual intervals and their reversible source offsets', () => {
  assert.deepEqual(verify(fresh()), {status: 'PASS', sections: 346, tokens: 21994, sourceDocuments: 2, restoredParagraphs: 83});
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

test('Whiston source gate refuses additional pilot books and unapproved source paths', async t => {
  await t.test('test-only Book IX cannot become published scope', () => {
    const input = fresh();
    input.manifest.books.push({...input.manifest.books[0], number: 9});
    assert.throws(() => verify(input), /pilot includes an unreviewed book/u);
  });
  await t.test('Latin source cannot be substituted for Whiston', () => {
    const input = fresh();
    input.manifest.books[0].source = 'assets/xml/antiquities/Latin/book-01.xml';
    assert.throws(() => verify(input), /pilot source scope differs/u);
  });
});

test('Whiston source gate accepts CRLF equivalence but refuses actual XML changes', async t => {
  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'latin-josephus-whiston-source-'));
  t.after(() => fs.rmSync(fixture, {recursive: true, force: true}));
  const sourcePaths = [manifest.books[0].source, ...manifest.books[0].additionalSources];
  for (const relative of sourcePaths) {
    const filename = path.join(fixture, relative);
    fs.mkdirSync(path.dirname(filename), {recursive: true});
    fs.copyFileSync(path.join(repository, relative), filename);
  }
  await t.test('both files may have Windows line endings', () => {
    for (const relative of sourcePaths) {
      const filename = path.join(fixture, relative);
      fs.writeFileSync(filename, fs.readFileSync(filename, 'utf8').replace(/\r?\n/gu, '\r\n'));
    }
    assert.equal(verify(fresh(), fixture).status, 'PASS');
  });
  await t.test('source text changes fail even if their report fingerprint is refreshed', () => {
    const input = fresh(), filename = path.join(fixture, sourcePaths[0]);
    fs.writeFileSync(filename, fs.readFileSync(filename, 'utf8').replace('In the beginning', 'At the beginning'));
    const changed = fs.readFileSync(filename), fingerprint = {path: sourcePaths[0],
      sha256: createHash('sha256').update(changed).digest('hex'), bytes: changed.length};
    input.report.source = fingerprint;
    input.report.sources[1] = fingerprint;
    input.report.documentReports[1].source = fingerprint;
    assert.throws(() => verify(input, fixture), /source differs from the accepted source/u);
  });
});
