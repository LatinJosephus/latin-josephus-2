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

test('Whiston source gate verifies all 7376 actual intervals and their reversible source offsets', () => {
  const expected = [[346, 21994, 83], [349, 23020, 76], [322, 20955, 79], [331, 22900, 88], [362, 23396, 98],
    [378, 28422, 83], [394, 28285, 76], [420, 29968, 85], [291, 19074, 54], [281, 18035, 52],
    [347, 20213, 57], [434, 25083, 71], [433, 25616, 87], [491, 29186, 112], [425, 26972, 66],
    [404, 23831, 61], [355, 23725, 61], [379, 24253, 57], [366, 21575, 52], [268, 14435, 51]];
  for (const [index, [sections, tokens, restoredParagraphs]] of expected.entries()) {
    assert.deepEqual(verify(fresh(index + 1)), {status: 'PASS', sections, tokens, sourceDocuments: index ? 1 : 2, restoredParagraphs});
  }
});

test('Whiston source gate validates text and book-specific reader metadata in every newly added book', async t => {
  for (const number of [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]) await t.test(`Book ${number}`, () => {
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
  await t.test('nonexistent Book XXI cannot become published scope', () => {
    const input = fresh();
    input.manifest.books.push({...input.manifest.books[0], number: 21});
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

test('Whiston XI whole-book phrases follow accepted physical order at all three nonnumeric seams', () => {
  const records = books.get(11).corpus;
  const engine = createEngine(buildBundle(records, lunr), lunr);
  for (const [left, right, phrase] of [
    [311, 326, 'was then in years and Jaddua the high'],
    [342, 312, 'to their temple also But there was now'],
    [325, 343, 'go up to Jerusalem to whom he promised'],
  ]) {
    const query = `"${phrase}"`;
    assert.equal(engine.search(query, {scope: 'section'}).matchingUnits, 0);
    const result = engine.search(query, {scope: 'book'});
    assert.equal(result.matchingUnits, 1);
    assert.equal(result.occurrences, 1);
    assert.deepEqual(result.hitGroups.flatMap(group => group.recordIds),
      [left, right].map(section => `antiquities-english-whiston-11-${section}`));
  }
  for (const invented of ['was then in years But there was now',
    'go up to Jerusalem and Jaddua the high', 'to their temple also to whom he promised']) {
    assert.equal(engine.search(`"${invented}"`, {scope: 'book'}).matchingUnits, 0);
  }
  const reordered = fresh(11);
  reordered.corpus.sort((a, b) => a.section - b.section);
  assert.throws(() => verify(reordered), /record text, source identity, reader metadata or phrase boundary differs/u);
  const interrupted = fresh(11);
  interrupted.corpus.find(record => record.section === 326).breakBefore = true;
  assert.throws(() => verify(interrupted), /record text, source identity, reader metadata or phrase boundary differs/u);
});

test('Whiston XII and XIV retain phrases across all newly reviewed paragraph-prefix joins', () => {
  for (const [book, section, phrase, previousId, sourceId] of [
    [12, 147, 'into Phrygia The epistle was this', 'english-book12-num145', 'english-book12-num148'],
    [12, 226, 'sendeth greeting We have met', 'english-book12-num223', 'english-book12-num225'],
    [14, 237, 'calends of October In the month Quntius', 'english-book14-num236', 'english-book14-num237'],
  ]) {
    const record = books.get(book).corpus.find(record => record.section === section);
    const engine = createEngine(buildBundle([record], lunr), lunr);
    const result = engine.search(`"${phrase}"`, {scope: 'section'});
    assert.equal(result.matchingUnits, 1);
    assert.equal(result.occurrences, 1);
    assert.deepEqual(result.hitGroups.flatMap(group => group.recordIds), [record.id]);
    assert.deepEqual(record.sourceIds, [previousId, sourceId]);
  }
});

test('Whiston XII and XIV prefix text, citation assignments and source spans are independently checked', async t => {
  for (const [book, section, sourceId] of [[12, 147, 'english-book12-num148'],
    [12, 226, 'english-book12-num225'], [14, 237, 'english-book14-num237']]) {
    for (const mode of ['lost-prefix', 'reassigned-prefix', 'source-identity', 'record-offset', 'invented-marker', 'separator']) {
      await t.test(`${book}.${section}: ${mode}`, () => {
        const input = fresh(book), record = input.corpus.find(record => record.section === section);
        const paragraph = input.report.documentReports[0].paragraphs.find(paragraph => paragraph.sourceId === sourceId);
        if (mode === 'lost-prefix') record.text = record.text.split('\n\n')[0];
        else if (mode === 'reassigned-prefix') {
          const [first, prefix] = record.text.split('\n\n');
          record.text = first;
          const next = input.corpus.find(record => record.section === section + 1);
          next.text = `${prefix} ${next.text}`;
        } else if (mode === 'source-identity') record.sourceIds.pop();
        else if (mode === 'record-offset') paragraph.sourcePieces.find(piece => piece.kind === 'record').recordStart++;
        else if (mode === 'invented-marker') paragraph.nieseMarkers.unshift({section});
        else delete paragraph.recordJoin;
        assert.throws(() => verify(input), /Whiston/u);
      });
    }
  }
});

test('Whiston XII bold epithets are searchable ordinary text and XV chapter markers do not create gaps', async t => {
  for (const [section, phrase] of [[125, 'The God'], [157, 'The Just']]) {
    const record = books.get(12).corpus.find(record => record.section === section);
    assert.ok(record.text.includes(phrase));
    assert.deepEqual(record.editorialMarks, []);
    assert.deepEqual(record.sourceMarkup, []);
  }
  const xv = books.get(15);
  assert.equal(xv.report.counts.nieseMilestones, 425);
  assert.equal(xv.report.counts.structuralMarkers, 14);
  assert.equal(xv.report.paragraphs.flatMap(paragraph => paragraph.structuralMarkers)
    .filter(marker => marker.kind === 'milestone').length, 13);
  assert.ok(xv.corpus.every(record => !record.breakBefore && record.phraseBreaks.length === 0));
  for (const mode of ['lost-marker', 'changed-unit', 'shifted-offset', 'false-boundary']) await t.test(mode, () => {
    const input = fresh(15), paragraph = input.report.documentReports[0].paragraphs
      .find(paragraph => paragraph.structuralMarkers.some(marker => marker.kind === 'milestone'));
    const marker = paragraph.structuralMarkers.find(marker => marker.kind === 'milestone');
    if (mode === 'lost-marker') paragraph.structuralMarkers = paragraph.structuralMarkers.filter(item => item !== marker);
    else if (mode === 'changed-unit') marker.sourceAttributes.unit = 'niese';
    else if (mode === 'shifted-offset') marker.sourceTextOffset++;
    else input.corpus.find(record => record.section === 11).breakBefore = true;
    assert.throws(() => verify(input), /Whiston/u);
  });
});

test('Whiston XVI–XX chapter milestones retain evidence without false phrase boundaries', async t => {
  for (const [number, chapterCount, structuralCount] of [[16, 16, 20], [17, 19, 19], [18, 21, 21], [19, 8, 8], [20, 20, 20]]) {
    const original = books.get(number);
    assert.equal(original.report.counts.structuralMarkers, structuralCount);
    assert.equal(original.report.paragraphs.flatMap(paragraph => paragraph.structuralMarkers)
      .filter(marker => marker.kind === 'milestone' && marker.sourceAttributes.unit === 'chapter').length, chapterCount);
    assert.ok(original.corpus.every(record => !record.breakBefore && record.phraseBreaks.length === 0));
    await t.test(`Book ${number} altered chapter evidence is rejected`, () => {
      const input = fresh(number);
      const paragraph = input.report.documentReports[0].paragraphs.find(p => p.structuralMarkers.some(m => m.kind === 'milestone'));
      paragraph.structuralMarkers.find(marker => marker.kind === 'milestone').sourceAttributes.unit = 'niese';
      assert.throws(() => verify(input), /Whiston/u);
    });
  }
});

test('Whiston XX excludes its exact book-summary head and verifies its audit evidence', async t => {
  const original = books.get(20);
  const heading = original.report.documentReports[0].excludedBlocks.find(item => item.kind === 'structural-heading');
  assert.equal(heading.text, 'CONTAINING THE INTERVAL OF TWENTY-TWO YEARS. FROM FADUS THE PROCURATOR TO FLORUS.');
  assert.deepEqual(heading.sourceAttributes, {sameAs: '#latin-book20-chapter1-head'});
  assert.equal(heading.parentAttributes['{http://www.w3.org/XML/1998/namespace}id'], 'english-book20-chapter1');
  assert.equal(original.report.counts.excludedStructuralHeadings, 1);
  assert.ok(!original.corpus.some(record => record.text.includes(heading.text)));
  for (const mode of ['missing', 'text', 'parent', 'included-in-record']) await t.test(mode, () => {
    const input = fresh(20), blocks = input.report.documentReports[0].excludedBlocks;
    const item = blocks.find(block => block.kind === 'structural-heading');
    if (mode === 'missing') blocks.splice(blocks.indexOf(item), 1);
    else if (mode === 'text') item.text += ' changed';
    else if (mode === 'parent') item.parentAttributes.sameAs = '#another-parent';
    else input.corpus[0].text = heading.text + input.corpus[0].text;
    assert.throws(() => verify(input), /Whiston/u);
  });
});

test('Whiston XIX.363–364 use separate canonical identities and remain adjacent for whole-book phrases', () => {
  const records = books.get(19).corpus;
  const a = records.find(record => record.section === 363), b = records.find(record => record.section === 364);
  assert.ok(a.text.startsWith('Accordingly he sent Cuspins Fadus'));
  assert.ok(b.text.startsWith('But he determined, in the first place,'));
  assert.equal(a.sourceId, b.sourceId);
  assert.deepEqual(b.readerLink.params, {book: 19, niese: 364, english: 'whiston'});
  const engine = createEngine(buildBundle(records, lunr), lunr);
  assert.equal(engine.search('"into his kingdom But he determined"', {scope: 'section'}).matchingUnits, 0);
  const joined = engine.search('"into his kingdom But he determined"', {scope: 'book'});
  assert.equal(joined.matchingUnits, 1);
  assert.equal(joined.occurrences, 1);
  assert.deepEqual(joined.hitGroups.flatMap(group => group.recordIds), [a.id, b.id]);
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
  await t.test('all twenty-one indexed files may have Windows line endings', () => {
    assert.equal(sourcePaths.length, 21);
    for (const relative of sourcePaths) {
      const filename = path.join(fixture, relative);
      fs.writeFileSync(filename, fs.readFileSync(filename, 'utf8').replace(/\r?\n/gu, '\r\n'));
    }
    for (const number of manifest.books.map(book => book.number)) assert.equal(verify(fresh(number), fixture).status, 'PASS');
  });
  for (const [number, bytes, sha256, normalizedSHA256] of [
    [12, 158411, 'e28ce3914fe0e764571e049b20b5ddabfc6d3080cf6dd4537522b083be7cc83c', 'ba4808e3b5e234c2ec1bbffd3e4b662a78b2fe41c1643be3e4e7e6662d583286'],
    [17, 148192, '29a0a40375396016162920b32462f259cf3791fa6a12b4af1f6d2ed7bd41cca1', 'd6056846f61ae43003989a2d799501d5e9edb7c3b407d9292b3c89064df6a0ac'],
    [18, 150720, 'db6c960c3d27457e21b4f5cccdf5a389f6d9ecdfd927a53d1379484eeef3c67d', 'ba1529509dddf72ec82a5eda63fb95f6d0f8d88dad87c69f5cf7a431536c63fa'],
    [19, 136009, '9ce4e6116a0cbd57823e07cff97559941e9015da79d02dd0ae6b2e9c0877e129', 'e025279ffb304a08f2f960845c6dca1e09162188bffd44f541cd787ae0aaf094'],
    [20, 94225, '229c2c47f9c4f6ad19ae3b96aeb8c9fcdbe849bb4a733cf214ad0f133d28bc0e', '8f5437db04d4423b79db151603187f50400a9d41938f94394a8da744842af673'],

  ]) await t.test(`Book ${number} retains accepted raw CRLF provenance while an LF checkout projects identically`, () => {
    const input = fresh(number), relative = manifest.books.find(book => book.number === number).source;
    assert.deepEqual(input.report.source, {path: relative, bytes, sha256});
    assert.equal(input.report.documentReports[0].sourceContract.normalizedSHA256, normalizedSHA256);
    const filename = path.join(fixture, relative), original = fs.readFileSync(filename);
    const normalized = Buffer.from(original.toString('latin1').replace(/\r\n/gu, '\n'), 'latin1');
    assert.notEqual(normalized.length, original.length);
    fs.writeFileSync(filename, normalized);
    try {
      assert.equal(verify(input, fixture).status, 'PASS');
      const fingerprint = {path: relative, bytes: normalized.length,
        sha256: createHash('sha256').update(normalized).digest('hex')};
      input.report.source = fingerprint;
      input.report.sources[0] = fingerprint;
      input.report.documentReports[0].source = fingerprint;
      assert.equal(verify(input, fixture).status, 'PASS');
    } finally { fs.writeFileSync(filename, original); }
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
