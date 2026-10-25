/** Check the exact accepted English DEH projection with real source and engine. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {validateDehEnglishSourceProjection} from '../deh-english-publication.mjs';
import {buildBundle, createEngine} from '../engine.mjs';

const require = createRequire(import.meta.url), lunr = require('../vendor/lunr.cjs');
const repository = path.resolve(fileURLToPath(new URL('../../../', import.meta.url)));
const read = relative => JSON.parse(fs.readFileSync(path.join(repository, relative), 'utf8'));
const manifest = read('bin/search/config/deh-english-pollard.json');
const books = new Map(manifest.books.map(spec => {
  const stem = `bin/search/data/deh-english-pollard/book-${String(spec.number).padStart(2, '0')}`;
  return [spec.number, {corpus: read(stem + '.corpus.json'), report: read(stem + '.extraction-report.json')}];
}));
const fresh = (number = 1) => ({number, ...structuredClone(books.get(number)), manifest: structuredClone(manifest)});
const verify = (input, root = repository) => validateDehEnglishSourceProjection(input.corpus, input.report, input.manifest,
  input.manifest.books.find(spec => spec.number === input.number), root);
const tokens = text => Array.from(text.matchAll(/[\p{L}\p{N}][\p{L}\p{M}\p{N}]*/gu), match => match[0]);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const phraseAcross = pair => [...tokens(pair[0].text).slice(-4), ...tokens(pair[1].text).slice(0, 4)].join(' ');

test('English DEH source gate verifies all five books and all 558 original citation paragraphs', () => {
  for (const [index, [sections, count]] of [[215, 40804], [73, 17142], [70, 18640], [79, 17259], [121, 42207]].entries()) {
    assert.deepEqual(verify(fresh(index + 1)), {status: 'PASS', sections, tokens: count, sourceDocuments: 1, restoredParagraphs: sections});
  }
});

test('English DEH records reject altered words, labels, source alignment, reader selection and boundaries', async t => {
  for (const [label, mutate] of [
    ['invented running word', input => { input.corpus[0].text += ' invented'; }],
    ['removed punctuation', input => { input.corpus[0].text = input.corpus[0].text.replace(',', ''); }],
    ['leaked citation label', input => { input.corpus[0].text = '[Prol.1] ' + input.corpus[0].text; }],
    ['wrong stable ordinal', input => { input.corpus[0].section++; }],
    ['wrong local chapter', input => { input.corpus[3].chapter++; }],
    ['wrong local paragraph', input => { input.corpus[3].paragraph++; }],
    ['Niese citation scheme', input => { input.corpus[0].citationScheme = 'niese'; }],
    ['wrong citation label', input => { input.corpus[0].citationLabel = 'I.1.1'; }],
    ['wrong Prologue identity', input => { input.corpus[0].citation.prologue = false; }],
    ['wrong English identity', input => { input.corpus[0].sourceId = 'latin-deh1-num1'; }],
    ['wrong aligned Latin identity', input => { input.corpus[0].sourceSameAs = '#latin-deh1-num2'; }],
    ['lost aligned Latin identity', input => { delete input.corpus[0].sourceSameAs; }],
    ['lost original identity kind', input => { delete input.corpus[0].sourceIdentityKind; }],
    ['lost explicit English choice', input => { delete input.corpus[0].readerLink.params.english; }],
    ['wrong English edition choice', input => { input.corpus[0].readerLink.params.english = 'whiston'; }],
    ['ordinal instead of local URL unit', input => { input.corpus[3].readerLink.params.unit = 4; }],
    ['wrong URL work', input => { input.corpus[0].url = input.corpus[0].url.replace('/deh/', '/bellum-judaicum/'); }],
    ['changed edition', input => { input.corpus[0].edition = 'Ussani (1932)'; }],
    ['changed language', input => { input.corpus[0].language = 'Latin'; }],
    ['reordered records', input => { [input.corpus[0], input.corpus[1]] = [input.corpus[1], input.corpus[0]]; }],
    ['changed global order', input => { input.corpus[0].order++; }],
    ['invented editorial deletion', input => { input.corpus[0].editorialMarks = [{kind: 'del', start: 0, end: 1, text: 'I'}]; }],
    ['invented text gap', input => { input.corpus[0].textGaps = [{offset: 1, kind: 'gap'}]; }],
    ['invented phrase boundary', input => { input.corpus[1].breakBefore = true; }],
    ['lost Prologue boundary', input => { delete input.corpus[3].breakBefore; }],
    ['invented inline phrase break', input => { input.corpus[3].phraseBreaks = [10]; }],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input);
    assert.throws(() => verify(input), /record text, source identity, reader metadata or phrase boundary differs/u);
  });
});

test('Reversible source report rejects missing prefixes, changed labels, metadata and fingerprints', async t => {
  for (const [label, mutate] of [
    ['removed citation prefix', report => { report.paragraphs[0].removedPrefix = ''; }],
    ['lost indentation before label', report => { const p = report.paragraphs.find(p => p.removedPrefix.startsWith('\n')); p.removedPrefix = p.removedPrefix.trim(); }],
    ['label accidentally part of running text', report => { report.paragraphs[0].runningText = report.paragraphs[0].rawText; }],
    ['bad source piece offset', report => { report.paragraphs[0].sourcePieces[0].sourceEnd++; }],
    ['bad record offset', report => { report.paragraphs[0].sourcePieces.find(p => p.kind === 'record').recordStart++; }],
    ['missing source piece', report => { report.paragraphs[0].sourcePieces.shift(); }],
    ['altered raw source', report => { report.paragraphs[0].rawText += ' '; }],
    ['false restoration hash', report => { report.coverage.restoredParagraphSequenceSha256 = '0'.repeat(64); }],
    ['wrong sameAs attribute', report => { report.paragraphs[0].sourceAttributes.sameAs = '#latin-deh2-num1'; }],
    ['wrong book sameAs', report => { report.paragraphs[0].bookAttributes.sameAs = '#latin-deh2'; }],
    ['wrong chapter identity', report => { report.paragraphs[0].chapterAttributes['xml:id'] = 'english-deh1-chapter1'; }],
    ['missing paragraph', report => { report.paragraphs.pop(); }],
    ['false word count', report => { report.counts.runningWordTokens++; }],
    ['wrong source contract', report => { report.sourceContract.normalizedSHA256 = '0'.repeat(64); }],
    ['unverified source', report => { report.sourceContract.verified = false; }],
    ['missing excluded release note', report => { report.excludedBlocks.splice(1, 1); }],
    ['false excluded heading', report => { report.excludedBlocks[2].text = 'Invented heading'; }],
    ['false header hash', report => { report.excludedBlocks[0].textSHA256 = '0'.repeat(64); }],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input.report);
    assert.throws(() => verify(input), /source restoration report differs/u);
  });
});

test('Prologue phrases join internally but cannot continue into Book I narrative', () => {
  const corpus = books.get(1).corpus;
  for (const [left, right, expected] of [[0, 1, 1], [1, 2, 1], [2, 3, 0]]) {
    const pair = [corpus[left], corpus[right]], engine = createEngine(buildBundle(pair, lunr), lunr);
    const query = `"${phraseAcross(pair)}"`;
    assert.equal(engine.search(query, {scope: 'section'}).matchingUnits, 0);
    assert.equal(engine.search(query, {scope: 'book'}).occurrences, expected);
  }
  const pair = [corpus[2], corpus[3]], engine = createEngine(buildBundle(pair, lunr), lunr);
  const query = `"${tokens(pair[0].text).slice(-6).join(' ')}" AND "${tokens(pair[1].text).slice(0, 6).join(' ')}"`;
  assert.equal(engine.search(query, {scope: 'book'}).matchingUnits, 1);
  assert.equal(engine.search(query, {scope: 'section'}).matchingUnits, 0);
});

test('All English DEH books permit exact phrases across ordinary chapter seams', () => {
  for (const {corpus} of books.values()) {
    const index = corpus.findIndex((record, i) => i > 0 && record.chapter !== corpus[i - 1].chapter && !record.breakBefore);
    assert(index > 0);
    const pair = [corpus[index - 1], corpus[index]], engine = createEngine(buildBundle(pair, lunr), lunr);
    const query = `"${phraseAcross(pair)}"`;
    assert.equal(engine.search(query, {scope: 'section'}).matchingUnits, 0);
    assert.equal(engine.search(query, {scope: 'book'}).occurrences, 1);
  }
});

test('English DEH phrase and Boolean evidence never crosses book or edition boundaries', () => {
  const pair = [books.get(1).corpus.at(-1), books.get(2).corpus[0]], engine = createEngine(buildBundle(pair, lunr), lunr);
  assert.equal(engine.search(`"${phraseAcross(pair)}"`, {scope: 'book'}).matchingUnits, 0);
  const query = `"${tokens(pair[0].text).slice(-6).join(' ')}" AND "${tokens(pair[1].text).slice(0, 6).join(' ')}"`;
  assert.equal(engine.search(query, {scope: 'book'}).matchingUnits, 0);
});

test('English DEH manifest cannot swap edition, ranges, sources or book order', async t => {
  for (const [label, mutate, pattern] of [
    ['wrong edition', input => { input.manifest.edition = 'Whiston'; }, /collection identity differs/u],
    ['wrong work', input => { input.manifest.work = 'bellum'; }, /collection identity differs/u],
    ['wrong scheme', input => { input.manifest.citationScheme = 'niese'; }, /collection identity differs/u],
    ['wrong source', input => { input.manifest.books[0].source = 'assets/xml/deh/Latin/book-01.xml'; }, /book source scope differs/u],
    ['truncated book', input => { input.manifest.books[0].sections--; }, /book source scope differs/u],
    ['truncated range', input => { input.manifest.books[0].sectionRange[1]--; }, /book source scope differs/u],
    ['invented sixth book', input => { input.manifest.books.push({...input.manifest.books[0], number: 6}); }, /unreviewed book/u],
    ['reordered books', input => { input.manifest.books.reverse(); }, /unreviewed book/u],
  ]) await t.test(label, () => {
    const input = fresh();
    mutate(input);
    assert.throws(() => verify(input), pattern);
  });
});

test('All five English DEH sources accept only LF/CRLF equivalence and reject rehashed alterations', async t => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'deh-english-gate-'));
  try {
    const directory = path.join(temporary, 'assets/xml/deh/English');
    fs.mkdirSync(directory, {recursive: true});
    for (const spec of manifest.books) fs.writeFileSync(path.join(temporary, spec.source), fs.readFileSync(path.join(repository, spec.source)));
    for (const number of [1, 2, 3, 4, 5]) {
      await t.test(`Book ${number}: LF and CRLF source and indexed fingerprints`, () => {
        const input = fresh(number), filename = path.join(temporary, input.report.source.path), original = fs.readFileSync(filename);
        const crlf = Buffer.from(original.toString('latin1').replace(/\r\n/gu, '\n').replace(/\n/gu, '\r\n'), 'latin1');
        fs.writeFileSync(filename, crlf);
        assert.equal(verify(input, temporary).status, 'PASS');
        input.report.source = {path: input.report.source.path, sha256: hash(crlf), bytes: crlf.length};
        input.report.sources = [input.report.source];
        assert.equal(verify(input, temporary).status, 'PASS');
        fs.writeFileSync(filename, original);
        assert.equal(verify(input, temporary).status, 'PASS');
      });
      await t.test(`Book ${number}: changed source despite updated fingerprint`, () => {
        const input = fresh(number), filename = path.join(temporary, input.report.source.path), original = fs.readFileSync(filename);
        const altered = Buffer.from(original.toString('utf8').replace('sameAs="#latin-deh', 'sameAs="#changed-latin-deh'));
        fs.writeFileSync(filename, altered);
        input.report.source = {path: input.report.source.path, sha256: hash(altered), bytes: altered.length};
        input.report.sources = [input.report.source];
        assert.throws(() => verify(input, temporary), /source differs from the accepted source/u);
        fs.writeFileSync(filename, original);
      });
    }
  } finally {
    fs.rmSync(temporary, {recursive: true, force: true});
  }
});
