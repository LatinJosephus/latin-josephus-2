/** Verify the English Contra Apionem source gate without changing scholarly files. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {validateWhistonContraApionemSourceProjection} from '../whiston-contra-apionem-publication.mjs';
import {buildBundle, createEngine} from '../engine.mjs';

const require = createRequire(import.meta.url), lunr = require('../vendor/lunr.cjs');
const repository = path.resolve(fileURLToPath(new URL('../../../', import.meta.url)));
const read = relative => JSON.parse(fs.readFileSync(path.join(repository, relative), 'utf8'));
const manifest = read('bin/search/config/contra-apionem-english-whiston.json');
const books = new Map(manifest.books.map(spec => {
  const stem = `bin/search/data/contra-apionem-english-whiston/book-${String(spec.number).padStart(2, '0')}`;
  return [spec.number, {corpus: read(stem + '.corpus.json'), report: read(stem + '.extraction-report.json')}];
}));
const fresh = (number = 1) => ({number, ...structuredClone(books.get(number)), manifest: structuredClone(manifest)});
const verify = (input, root = repository) => validateWhistonContraApionemSourceProjection(input.corpus, input.report, input.manifest,
  input.manifest.books.find(spec => spec.number === input.number), root);
const tokens = text => Array.from(text.matchAll(/[\p{L}\p{N}][\p{L}\p{M}\p{N}]*/gu), match => match[0]);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');

test('Whiston Contra Apionem source gate verifies all 616 English sections and paragraph restorations', () => {
  assert.deepEqual(verify(fresh(1)), {status: 'PASS', sections: 320, tokens: 18497, sourceDocuments: 1, restoredParagraphs: 320});
  assert.deepEqual(verify(fresh(2)), {status: 'PASS', sections: 296, tokens: 18356, sourceDocuments: 1, restoredParagraphs: 296});
});

test('English Contra Apionem records are checked against the accepted original text and edition', async t => {
  for (const [label, mutate] of [
    ['altered running word', input => { input.corpus[0].text += ' Invented words.'; }],
    ['removed punctuation', input => { input.corpus[0].text = input.corpus[0].text.replace(',', ''); }],
    ['wrong Niese citation', input => { input.corpus[0].section++; }],
    ['reordered records', input => { [input.corpus[0], input.corpus[1]] = [input.corpus[1], input.corpus[0]]; }],
    ['lost Whiston selection', input => { delete input.corpus[0].readerLink.params.english; }],
    ['wrong reader work', input => { input.corpus[0].readerLink.path = 'antiquities/'; }],
    ['wrong reader URL edition', input => { input.corpus[0].url = input.corpus[0].url.replace('whiston', 'lodge1602'); }],
    ['substituted Latin xml:id', input => { input.corpus[0].sourceId = 'latin-apion1-num1'; }],
    ['lost original identity kind', input => { delete input.corpus[0].sourceIdentityKind; }],
    ['invented phrase barrier', input => { input.corpus[0].breakBefore = true; }],
    ['invented inline phrase break', input => { input.corpus[0].phraseBreaks = [7]; }],
    ['invented source omission', input => { input.corpus[0].textGaps = [{offset: 7, kind: 'omission'}]; }],
    ['wrong language', input => { input.corpus[0].language = 'Latin'; }],
    ['wrong global order', input => { input.corpus[0].order++; }],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input);
    assert.throws(() => verify(input), /record text, source identity, reader metadata or phrase boundary differs/u);
  });
});

test('Both Contra Apionem books reject altered source text and metadata', async t => {
  for (const number of [1, 2]) await t.test(`Book ${number}`, () => {
    const input = fresh(number);
    input.corpus.at(-1).text += ' changed';
    assert.throws(() => verify(input), /differs from accepted XML/u);
    const wrong = fresh(number);
    wrong.corpus[0].readerLink.params.book = number + 1;
    assert.throws(() => verify(wrong), /differs from accepted XML/u);
  });
});

test('Contra Apionem source-ledger corruption cannot pass with unchanged records', async t => {
  for (const [label, mutate] of [
    ['source slice offset', report => { report.paragraphs[0].sourcePieces[0].sourceEnd++; }],
    ['record slice offset', report => { report.paragraphs[0].sourcePieces[0].recordStart++; }],
    ['missing paragraph', report => { report.paragraphs.pop(); }],
    ['altered original paragraph text', report => { report.paragraphs[0].rawText += ' '; }],
    ['fake Niese milestone', report => { report.paragraphs[0].nieseMarkers = [{section: 1, sourceTextOffset: 0}]; }],
    ['wrong original xml:id', report => { report.paragraphs[0].sourceAttributes['xml:id'] = 'latin-apion1-num1'; }],
    ['invented parent attribute', report => { report.paragraphs[0].parentAttributes.type = 'invented'; }],
    ['wrong source chapter', report => { report.paragraphs[0].sourceChapter++; }],
    ['wrong Whiston division start', report => { report.paragraphs[0].whistonSectionStart++; }],
    ['wrong Whiston division end', report => { report.paragraphs[0].whistonSectionEnd++; }],
    ['changed source contract', report => { report.sourceContract.normalizedSHA256 = '0'.repeat(64); }],
    ['unverified source contract', report => { report.sourceContract.verified = false; }],
    ['false restoration fingerprint', report => { report.coverage.restoredParagraphSequenceSha256 = '0'.repeat(64); }],
    ['false word count', report => { report.counts.runningWordTokens--; }],
    ['invented omission', report => { report.excludedBlocks = [{kind: 'note', text: 'omitted'}]; }],
    ['lost structural milestone', report => { report.structuralMarkers.pop(); }],
    ['shifted structural milestone position', report => { report.structuralMarkers[0].beforeSection++; }],
    ['shifted physical child index', report => { report.structuralMarkers[0].bookChildIndex++; }],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input.report);
    assert.throws(() => verify(input), /source restoration report differs/u);
  });
});

test('Inline Whiston division markers in II.109 and II.112 retain every tail and exact position', async t => {
  const original = books.get(2);
  assert.deepEqual(original.report.paragraphs.flatMap(paragraph => paragraph.structuralMarkers.map(marker =>
    [paragraph.sections[0].section, marker.number, marker.sourceTextOffset])), [[109, 9, 106], [112, 10, 4]]);
  for (const [label, mutate] of [
    ['removed II.109 tail', input => { input.corpus[108].text = input.corpus[108].text.slice(0, 106); }],
    ['removed II.112 tail', input => { input.corpus[111].text = input.corpus[111].text.slice(0, 4); }],
    ['lost inline marker evidence', input => { input.report.paragraphs[108].structuralMarkers = []; }],
    ['shifted inline marker', input => { input.report.paragraphs[111].structuralMarkers[0].sourceTextOffset++; }],
    ['renumbered inline division', input => { input.report.paragraphs[108].structuralMarkers[0].number++; }],
    ['changed original division attribute', input => { input.report.paragraphs[108].structuralMarkers[0].sourceAttributes.unit = 'chapter'; }],
    ['false II.109 phrase interruption', input => { input.corpus[108].phraseBreaks = [106]; }],
    ['false II.112 phrase interruption', input => { input.corpus[111].phraseBreaks = [4]; }],
  ]) await t.test(label, () => {
    const input = fresh(2);
    mutate(input);
    assert.throws(() => verify(input), /Whiston Contra Apionem/u);
  });
});

test('Literal English brackets retain their text without invented editorial annotations', async t => {
  assert.equal([...books.values()].flatMap(book => book.corpus).filter(record => record.text.includes('[')).length, 44);
  assert.match(books.get(1).corpus[37].text, /\[as the Greeks have,\]/u);
  for (const [label, mutate] of [
    ['removed bracketed words', input => { input.corpus[37].text = input.corpus[37].text.replace('[as the Greeks have,]', ''); }],
    ['removed literal brackets', input => { input.corpus[37].text = input.corpus[37].text.replaceAll('[', '').replaceAll(']', ''); }],
    ['invented supplied annotation', input => { input.corpus[37].editorialMarks = [{kind: 'supplied', start: 106, end: 126}]; }],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input);
    assert.throws(() => verify(input), /record text, source identity, reader metadata or phrase boundary differs/u);
  });
});

test('Exact phrases cross both internal Whiston divisions without acquiring numbered labels', () => {
  for (const [section, phrase] of [[109, 'for the sacrifices what then can we say of Apion'], [112, 'us nay this miracle or piety derides us further']]) {
    const record = books.get(2).corpus[section - 1];
    const engine = createEngine(buildBundle([record], lunr), lunr);
    const result = engine.search(`"${phrase}"`);
    assert.equal(result.matchingUnits, 1);
    assert.equal(result.occurrences, 1);
    assert.equal(engine.search(`"${phrase.replace(' what ', ' 9 what ').replace(' nay ', ' 10 nay ')}"`).matchingUnits, 0);
  }
});

test('Whole-book phrases cross section and chapter boundaries while unit scope remains local', () => {
  for (const [book, left, right] of [[1, 5, 6], [2, 109, 110], [2, 111, 112], [2, 112, 113]]) {
    const pair = books.get(book).corpus.filter(record => [left, right].includes(record.section));
    const phrase = [...tokens(pair[0].text).slice(-3), ...tokens(pair[1].text).slice(0, 3)].join(' ');
    const engine = createEngine(buildBundle(pair, lunr), lunr);
    assert.equal(engine.search(`"${phrase}"`, {scope: 'section'}).matchingUnits, 0);
    const result = engine.search(`"${phrase}"`, {scope: 'book'});
    assert.equal(result.matchingUnits, 1);
    assert.equal(result.occurrences, 1);
    assert.deepEqual(result.hitGroups.flatMap(group => group.recordIds), pair.map(record => record.id));
  }
});

test('Contra Apionem phrases cannot continue into the second book', () => {
  const pair = [books.get(1).corpus.at(-1), books.get(2).corpus[0]];
  const phrase = [...tokens(pair[0].text).slice(-3), ...tokens(pair[1].text).slice(0, 3)].join(' ');
  assert.equal(createEngine(buildBundle(pair, lunr), lunr).search(`"${phrase}"`, {scope: 'book'}).matchingUnits, 0);
});

test('Contra Apionem collection cannot silently gain books, swap editions or substitute another source', async t => {
  for (const [label, mutate, pattern] of [
    ['unreviewed Book III', input => { input.manifest.books.push({...input.manifest.books[0], number: 3}); }, /unreviewed book/u],
    ['book order reversed', input => { input.manifest.books.reverse(); }, /unreviewed book/u],
    ['Latin source', input => { input.manifest.books[0].source = 'assets/xml/contra-apionem/Latin/book-01.xml'; }, /book source scope differs/u],
    ['different edition', input => { input.manifest.edition = 'Lodge (1602)'; }, /collection identity differs/u],
    ['different work', input => { input.manifest.work = 'bellum'; }, /collection identity differs/u],
    ['truncated range', input => { input.manifest.books[0].sectionRange = [1, 319]; }, /book source scope differs/u],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input);
    assert.throws(() => verify(input), pattern);
  });
});

test('Contra Apionem XML gate accepts LF and CRLF and rejects refreshed fingerprints for altered source', async t => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'whiston-apion-gate-'));
  try {
    const directory = path.join(temporary, 'assets/xml/contra-apionem/English');
    fs.mkdirSync(directory, {recursive: true});
    for (const spec of manifest.books) fs.writeFileSync(path.join(temporary, spec.source), fs.readFileSync(path.join(repository, spec.source)));
    for (const number of [1, 2]) {
      await t.test(`Book ${number}: LF and CRLF`, () => {
        const input = fresh(number), filename = path.join(temporary, input.report.source.path);
        const original = fs.readFileSync(filename), crlf = Buffer.from(original.toString('latin1').replace(/\r\n/gu, '\n').replace(/\n/gu, '\r\n'), 'latin1');
        fs.writeFileSync(filename, crlf);
        assert.equal(verify(input, temporary).status, 'PASS');
        input.report.source = {path: input.report.source.path, sha256: hash(crlf), bytes: crlf.length};
        input.report.sources = [input.report.source];
        assert.equal(verify(input, temporary).status, 'PASS');
        fs.writeFileSync(filename, original);
        assert.equal(verify(input, temporary).status, 'PASS');
      });
      await t.test(`Book ${number}: changed source despite a refreshed fingerprint`, () => {
        const input = fresh(number), filename = path.join(temporary, input.report.source.path), original = fs.readFileSync(filename);
        const changed = Buffer.from(original.toString('utf8').replace('<text ', '<text altered="yes" '));
        fs.writeFileSync(filename, changed);
        input.report.source = {path: input.report.source.path, sha256: hash(changed), bytes: changed.length};
        input.report.sources = [input.report.source];
        assert.throws(() => verify(input, temporary), /source differs from the accepted source/u);
        fs.writeFileSync(filename, original);
      });
    }
  } finally {
    fs.rmSync(temporary, {recursive: true, force: true});
  }
});
