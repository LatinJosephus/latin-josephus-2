/** Test the Whiston source gate using copies; accepted scholarly XML is never edited. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {validateWhistonSourceProjection} from '../whiston-publication.mjs';
import {buildBundle, createEngine} from '../engine.mjs';

const require = createRequire(import.meta.url);
const lunr = require('../vendor/lunr.cjs');

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

test('Whiston source gate verifies all 3474 actual intervals and their reversible source offsets', () => {
  const expected = [[346, 21994, 83], [349, 23020, 76], [322, 20955, 79], [331, 22900, 88], [362, 23396, 98],
    [378, 28422, 83], [394, 28285, 76], [420, 29968, 85], [291, 19074, 54], [281, 18035, 52]];
  for (const [index, [sections, tokens, restoredParagraphs]] of expected.entries()) {
    assert.deepEqual(verify(fresh(index + 1)), {status: 'PASS', sections, tokens, sourceDocuments: index ? 1 : 2, restoredParagraphs});
  }
});

test('Whiston source gate validates text and book-specific reader metadata in every newly added book', async t => {
  for (const number of [2, 3, 4, 5, 6, 7, 8, 9, 10]) await t.test(`Book ${number}`, () => {
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
  await t.test('test-only Book XI cannot become published scope', () => {
    const input = fresh();
    input.manifest.books.push({...input.manifest.books[0], number: 11});
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

test('Whiston VIII.255 preserves a phrase across its paragraph join within section scope', () => {
  const records = structuredClone(books.get(8).corpus.slice(254, 256));
  const engine = createEngine(buildBundle(records, lunr), lunr);
  const sameSection = engine.search('"to Jerusalem Now when Rehoboam"', {scope: 'section', fold: false});
  assert.equal(sameSection.matchingUnits, 1);
  assert.equal(sameSection.occurrences, 1);
  assert.deepEqual(sameSection.hitGroups.flatMap(group => group.recordIds), ['antiquities-english-whiston-8-255']);
  assert.deepEqual(records[0].sourceIds, ['english-book08-num251', 'english-book08-num255']);
  assert.ok(records[0].text.includes('to Jerusalem.\n\nNow when Rehoboam'));
  const crossesCitation = '"on their side But Shemaiah"';
  assert.equal(engine.search(crossesCitation, {scope: 'section'}).matchingUnits, 0);
  assert.equal(engine.search(crossesCitation, {scope: 'book'}).matchingUnits, 1);
});

test('Whiston VIII.255 partial-paragraph continuation evidence is independently verified', async t => {
  for (const [label, mutate] of [
    ['lost continuation prefix', value => { value.corpus[254].text = value.corpus[254].text.split('\n\n')[0]; }],
    ['prefix wrongly reassigned to section256', value => {
      const [first, prefix] = value.corpus[254].text.split('\n\n');
      value.corpus[254].text = first;
      value.corpus[255].text = `${prefix} ${value.corpus[255].text}`;
    }],
    ['lost original paragraph identity', value => { value.corpus[254].sourceIds.pop(); }],
    ['invented source milestone255', value => {
      value.report.documentReports[0].paragraphs.find(paragraph => paragraph.sourceId === 'english-book08-num255')
        .nieseMarkers.unshift({section: 255, sourceTextOffset: 3, runningTextOffset: 1, sourceAttributes: {unit: 'niese', n: '255'}});
    }],
    ['wrong continuation source slice', value => {
      value.report.paragraphs.find(paragraph => paragraph.sourceId === 'english-book08-num255')
        .sourcePieces.find(piece => piece.kind === 'record').recordStart++;
    }],
    ['undocumented paragraph separator', value => {
      delete value.report.paragraphs.find(paragraph => paragraph.sourceId === 'english-book08-num255').recordJoin;
    }],
    ['continuation offset incorrectly inherited by section256', value => {
      value.report.paragraphs.find(paragraph => paragraph.sourceId === 'english-book08-num255').sections[1].recordOffset = 203;
    }],
  ]) await t.test(label, () => {
    const input = fresh(8);
    mutate(input);
    assert.throws(() => verify(input), /Whiston/u);
  });
});

test('Whiston IX retains restored narrative and excludes footnotes with exact evidence', async t => {
  for (const [label, mutate] of [
    ['inherited Latin51–109 omission', value => { value.corpus.splice(50, 59); }],
    ['footnote introduced into narrative', value => {
      const note = value.report.paragraphs.flatMap(paragraph => paragraph.sourcePieces).find(piece => piece.reason === 'whiston-footnote');
      value.corpus[50].text += ` ${note.text}`;
    }],
    ['footnote source evidence omitted', value => {
      const paragraph = value.report.documentReports[0].paragraphs.find(item => item.sourcePieces.some(piece => piece.reason === 'whiston-footnote'));
      paragraph.sourcePieces = paragraph.sourcePieces.filter(piece => piece.reason !== 'whiston-footnote');
    }],
    ['restored chapter heading evidence omitted', value => {
      value.report.documentReports[0].excludedBlocks = value.report.documentReports[0].excludedBlocks
        .filter(block => block.sourceAttributes.rend !== 'whiston-chapter-heading');
    }],
    ['invented gap in restored narrative', value => { value.corpus[50].breakBefore = true; }],
  ]) await t.test(label, () => {
    const input = fresh(9);
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
  await t.test('all eleven indexed files may have Windows line endings', () => {
    assert.equal(sourcePaths.length, 11);
    for (const relative of sourcePaths) {
      const filename = path.join(fixture, relative);
      fs.writeFileSync(filename, fs.readFileSync(filename, 'utf8').replace(/\r?\n/gu, '\r\n'));
    }
    for (const number of manifest.books.map(book => book.number)) assert.equal(verify(fresh(number), fixture).status, 'PASS');
  });
  for (const number of manifest.books.map(book => book.number)) await t.test(`Book ${number} source changes fail despite a refreshed fingerprint`, () => {
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
