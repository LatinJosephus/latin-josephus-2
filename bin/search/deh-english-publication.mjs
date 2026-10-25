/** Independently restore Pollard v1.1 English DEH from the exact accepted XML. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';

const COLLECTION = 'deh-english-pollard';
const ROMANS = ['I', 'II', 'III', 'IV', 'V'];
const CONTRACTS = [
  ['1f8a50242272c8cbb2fe2054c10e318cf00d0aab91b508eb1ca9e7a9e6a60b47', 215, 40804, 47, 2, 'Book I', 'English translation, version 1.1: Prologue and Book I chapters 1–46, ending at [I.46.2].'],
  ['b87360225888e3e66950905eb047bded590302bb28b2b0f4c43fdbf8b089db2c', 73, 17142, 18, 1, 'Book II', 'English translation, version 1.1: complete Book II, chapters 1–18, [II.1.1]–[II.18.1].'],
  ['f6c0c7ea4140e40bbe72d6a9293e5cbe6df73d15271d41d88d72a5eefd14e08c', 70, 18640, 26, 1, 'BOOK III', 'English translation, version 1.1: complete Book III, chapters 1–26, [III.1.1]–[III.26.4].'],
  ['1e5bf28ece4f00954924fe5aa9a704e647289a0c83e7e08ca99944b8412c0370', 79, 17259, 33, 1, 'BOOK IV', 'English translation, version 1.1: complete Book IV, chapters 1–33, [IV.1.1]–[IV.33.3].'],
  ['4df33b9d0409644e5f9f2bcacb87ca507e5ff2272d72d1a0b1c73e14f2484c91', 121, 42207, 53, 1, 'BOOK V', 'English translation, version 1.1: complete Book V, chapters 1–53, [V.1.1]–[V.53.2].'],
].map(([sha256, sections, tokens, chapters, headings, heading, releaseNote], index) => ({book: index + 1,
  sha256, sections, tokens, chapters, headings, heading, releaseNote,
  path: `assets/xml/deh/English/book-${String(index + 1).padStart(2, '0')}.xml`}));
const BREAK_REASON = 'The separately labelled Prologue ends before Book I narrative.';
const TRANSLATION_NOTE_UNITS = {1: [31, 36, 70, 141], 2: [73], 3: [36, 47], 4: [], 5: [72]};
const RULES = {
  boundaries: 'Each accepted English xml:id and num label identify one complete chapter/paragraph citation unit. section is its stable paragraph ordinal within the book, never a Niese section.',
  text: 'Exclude the verified num label together with its preceding whitespace; trim only running-text edge whitespace. Preserve every other original running character, punctuation and internal whitespace. No spelling repair or generated text.',
  sourceIdentity: 'Retain each original English xml:id and its exact sameAs reference to the aligned Latin element. English text is extracted from its own source, not reconstructed from Latin.',
  excludedBlocks: 'The complete TEI header, verified body release note and exact chapter/book headings are metadata outside running text. Their source evidence is retained.',
  editorialMarkup: 'The accepted English paragraphs contain a leading num element and plain running text. Eight approved uncertainty notes are excluded from search and preserved in the source restoration ledger. No Latin additions, deletions, gaps or dagger representations are inherited. Unknown body markup stops extraction.',
  phraseBoundaries: 'Physically consecutive paragraphs and chapters remain joinable in whole-book scope. The Prologue-to-Book-I transition has breakBefore=true. Phrases never cross books, works or editions.',
  coordinates: 'All sourcePieces and section coordinates are zero-based original-text UTF-16 offsets, end exclusive. rawText includes the removed num label and its preceding whitespace; runningText excludes that prefix.',
  readerRoute: '/deh/?book={book}&chapter={chapter}&unit={paragraph}&english=pollard; chapter 0 is the Prologue and unit is chapter-local.',
};
const digest = value => createHash('sha256').update(value).digest('hex');
const equal = (a, b, message) => assert.deepEqual(a, b, `English DEH ${message}`);
const require = (value, message) => assert(value, `English DEH ${message}`);
const words = text => Array.from(text.matchAll(/[\p{L}\p{N}][\p{L}\p{M}\p{N}]*/gu), match => match[0]);
const range = last => Array.from({length: last}, (_, index) => index + 1);

function decodeXML(value) {
  require(!/&(?!(?:#x[a-fA-F0-9]+|#[0-9]+|amp|lt|gt|quot|apos);)/u.test(value), 'unsupported XML entity');
  return value.replace(/&(?:#x([a-fA-F0-9]+)|#([0-9]+)|(amp|lt|gt|quot|apos));/gu,
    (_, hex, dec, name) => hex ? String.fromCodePoint(Number.parseInt(hex, 16)) : dec ? String.fromCodePoint(Number(dec))
      : ({amp: '&', lt: '<', gt: '>', quot: '"', apos: "'"})[name]);
}

function attributes(value) {
  const result = {};
  let cursor = 0;
  for (const match of value.matchAll(/\s+([A-Za-z_:][A-Za-z0-9_.:-]*)\s*=\s*(?:"([^"]*)"|'([^']*)')/gu)) {
    require(value.slice(cursor, match.index).trim() === '', 'unparsed attribute text');
    require(!Object.hasOwn(result, match[1]), 'duplicate XML attribute');
    result[match[1]] = decodeXML(match[2] ?? match[3]);
    cursor = match.index + match[0].length;
  }
  equal(value.slice(cursor).trim(), '', 'unparsed attribute suffix');
  return result;
}

function plainText(value) {
  return decodeXML(value.replace(/<[^>]*>/gu, ''));
}

function coverage(paragraphs, records, sectionRange) {
  const byId = new Map(records.map(record => [record.id, record]));
  const raw = paragraphs.map(paragraph => paragraph.rawText);
  const restored = paragraphs.map(paragraph => paragraph.sourcePieces.map(piece => piece.kind === 'record'
    ? byId.get(piece.recordId).text.slice(piece.recordStart, piece.recordEnd) : piece.text).join(''));
  const sourceWords = paragraphs.flatMap(paragraph => words(paragraph.runningText));
  const indexedWords = records.flatMap(record => words(record.text));
  const sourceContent = paragraphs.map(paragraph => paragraph.runningText).join('').replace(/\s/gu, '');
  const indexedContent = records.map(record => record.text).join('').replace(/\s/gu, '');
  equal(raw, restored, 'source restoration differs');
  equal(sourceWords, indexedWords, 'projection changes source words');
  equal(sourceContent, indexedContent, 'projection lost source characters');
  return {completeRange: sectionRange, rangeMeaning: 'stable XML paragraph ordinal, not Niese', missingSections: [],
    unexpectedSections: [], duplicateSections: [], allSectionTextsNonempty: records.every(record => record.text.length > 0),
    paragraphsExactlyRestored: paragraphs.length, wordSequencePreserved: true, nonWhitespaceContentPreserved: true,
    rawParagraphSequenceSha256: digest(raw.join('\n')), restoredParagraphSequenceSha256: digest(restored.join('\n')),
    sourceWordSequenceSha256: digest(sourceWords.join('\n')), indexedWordSequenceSha256: digest(indexedWords.join('\n')),
    sourceNonWhitespaceContentSha256: digest(sourceContent), indexedNonWhitespaceContentSha256: digest(indexedContent)};
}

/** The narrow syntax reader below is entered only after the full accepted hash passes. */
function expectedDocument(root, contract, indexedSource) {
  const filename = path.resolve(root, contract.path), realRoot = fs.realpathSync(root);
  require(!fs.lstatSync(filename).isSymbolicLink() && fs.realpathSync(filename).startsWith(realRoot + path.sep),
    'XML is not an owned repository file');
  const bytes = fs.readFileSync(filename);
  const normalized = Buffer.from(bytes.toString('latin1').replace(/\r\n/gu, '\n'), 'latin1');
  equal(digest(normalized), contract.sha256, `source differs from the accepted source: ${contract.path}`);
  const crlf = Buffer.from(normalized.toString('latin1').replace(/\n/gu, '\r\n'), 'latin1');
  require(indexedSource && [normalized, crlf].some(value => indexedSource.sha256 === digest(value) && indexedSource.bytes === value.length),
    'indexed source fingerprint differs');
  equal(Object.keys(indexedSource).sort(), ['bytes', 'path', 'sha256'], 'source fingerprint schema differs');
  equal(indexedSource.path, contract.path, 'source identity differs');
  const xml = normalized.toString('utf8');
  const headers = [...xml.matchAll(/<teiHeader\b[^>]*>([\s\S]*?)<\/teiHeader\s*>/gu)];
  const textContainers = [...xml.matchAll(/<text\b([^>]*)>/gu)];
  equal(headers.length, 1, 'header count differs');
  equal(textContainers.length, 1, 'text container count differs');
  equal(attributes(textContainers[0][1]), {}, 'text attributes differ');
  const bodies = [...xml.matchAll(/<body\b([^>]*)>([\s\S]*?)<\/body\s*>/gu)];
  equal(bodies.length, 1, 'body count differs');
  equal(attributes(bodies[0][1]), {}, 'body attributes differ');
  const contents = bodies[0][2];
  const bodyMatch = contents.match(/^\s*<note>([^<]*)<\/note>\s*<div1\b([^>]*)>([\s\S]*?)<\/div1>\s*$/u);
  require(bodyMatch, 'body note/book structure differs');
  const note = decodeXML(bodyMatch[1]), bookAttributes = attributes(bodyMatch[2]);
  equal(note, contract.releaseNote, 'release note differs');
  equal(bookAttributes, {n: ROMANS[contract.book - 1], 'xml:id': `english-deh${contract.book}`,
    sameAs: `#latin-deh${contract.book}`, subtype: 'English', type: 'book'}, 'book identity differs');
  const headerText = plainText(headers[0][1]);
  const excludedBlocks = [{kind: 'teiHeader', reason: 'metadata outside running text', textCharacters: headerText.length, textSHA256: digest(headerText)},
    {kind: 'release-note', reason: 'verified release metadata outside running text', text: note, textSHA256: digest(note)}];
  const records = [], paragraphs = [], chapters = [];
  const orderOffset = CONTRACTS.filter(source => source.book < contract.book).reduce((total, source) => total + source.sections, 0);
  let chapterConsumed = 0, headingCount = 0;
  for (const chapterMatch of bodyMatch[3].matchAll(/<div2\b([^>]*)>([\s\S]*?)<\/div2>/gu)) {
    equal(bodyMatch[3].slice(chapterConsumed, chapterMatch.index).trim(), '', 'unclassified text before chapter');
    chapterConsumed = chapterMatch.index + chapterMatch[0].length;
    const chapter = chapters.length + (contract.book === 1 ? 0 : 1), chapterAttributes = attributes(chapterMatch[1]);
    equal(chapterAttributes, {n: String(chapter), 'xml:id': `english-deh${contract.book}-chapter${chapter}`,
      sameAs: `#latin-deh${contract.book}-chapter${chapter}`, type: 'chapter'}, 'chapter identity or order differs');
    chapters.push(chapter);
    let consumed = 0, localParagraph = 0, childIndex = 0;
    for (const childMatch of chapterMatch[2].matchAll(/<head>([^<]*)<\/head>|<p\b([^>]*)>([\s\S]*?)<\/p>/gu)) {
      equal(chapterMatch[2].slice(consumed, childMatch.index).trim(), '', 'unclassified text before paragraph');
      consumed = childMatch.index + childMatch[0].length;
      if (childMatch[1] !== undefined) {
        require([0, 1].includes(chapter) && childIndex === 0, 'heading interrupts running text');
        const text = decodeXML(childMatch[1]);
        equal(text, chapter === 0 ? 'Prologue' : contract.heading, 'heading differs');
        excludedBlocks.push({kind: 'heading', chapter, reason: 'verified structural heading outside running text', text, textSHA256: digest(text)});
        headingCount++;
        childIndex++;
        continue;
      }
      childIndex++;
      localParagraph++;
      const section = records.length + 1, sourceId = `english-deh${contract.book}-num${section}`;
      const sourceSameAs = `#latin-deh${contract.book}-num${section}`, sourceAttributes = attributes(childMatch[2]);
      equal(sourceAttributes, {'xml:id': sourceId, sameAs: sourceSameAs}, 'paragraph identity or alignment differs');
      const label = chapter === 0 ? `Prol.${localParagraph}` : `${ROMANS[contract.book - 1]}.${chapter}.${localParagraph}`;
      const parts = childMatch[3].match(/^(\s*)<num>([^<]*)<\/num>([^<]*)(?:<note\b([^>]*)>([^<]*)<\/note>)?$/u);
      require(parts, 'paragraph has unreviewed inline markup or content before its label');
      equal(decodeXML(parts[2]), `[${label}]`, 'citation label differs from chapter/paragraph');
      const prefix = decodeXML(parts[1]) + decodeXML(parts[2]), runningText = decodeXML(parts[3]);
      const annotation = parts[4] === undefined ? '' : decodeXML(parts[5]);
      if (parts[4] !== undefined) {
        require(TRANSLATION_NOTE_UNITS[contract.book].includes(section) && annotation.startsWith('Translation comparison: '), 'unapproved translation note');
        equal(attributes(parts[4]), {type: 'uncertainty', source: sourceSameAs}, 'translation note attributes differ');
      }
      const runningEnd = prefix.length + runningText.length;
      const rawText = prefix + runningText + annotation, text = runningText.trim();
      require(text.length && words(text).length, 'empty citation unit');
      const textStart = prefix.length + runningText.match(/^\s*/u)[0].length, textEnd = textStart + text.length;
      const record = {id: `${COLLECTION}-${contract.book}-${section}`, work: 'deh', book: contract.book,
        section, language: 'English', edition: 'Pollard v1.1', chapter, paragraph: localParagraph,
        citationScheme: 'chapter-paragraph', citationLabel: label,
        citation: {book: ROMANS[contract.book - 1], chapter, paragraph: localParagraph, prologue: chapter === 0},
        text, editorialMarks: [], sourceMarkup: [], textGaps: [], phraseBreaks: [],
        url: `/deh/?book=${contract.book}&chapter=${chapter}&unit=${localParagraph}&english=pollard`,
        readerLink: {path: 'deh/', params: {book: contract.book, chapter, unit: localParagraph, english: 'pollard'}},
        sourceId, sourceIds: [sourceId], sourceIdentityKind: 'xml:id', sourcePath: contract.path, sourceSameAs,
        order: orderOffset + records.length};
      if (contract.book === 1 && chapter === 1 && localParagraph === 1) {
        record.breakBefore = true;
        record.breakReason = BREAK_REASON;
      }
      records.push(record);
      const sourcePieces = [{kind: 'excluded', reason: 'citation-label-and-preceding-whitespace', text: prefix,
        sourceStart: 0, sourceEnd: prefix.length, textSHA256: digest(prefix)}];
      const excluded = (start, end) => {
        if (start === end) return;
        const fragment = rawText.slice(start, end);
        require(/^\s+$/u.test(fragment), 'non-whitespace narrative was excluded');
        sourcePieces.push({kind: 'excluded', reason: 'section-edge-whitespace', text: fragment,
          sourceStart: start, sourceEnd: end, textSHA256: digest(fragment)});
      };
      excluded(prefix.length, textStart);
      sourcePieces.push({kind: 'record', recordId: record.id, recordStart: 0, recordEnd: text.length,
        sourceStart: textStart, sourceEnd: textEnd, textSHA256: digest(text)});
      excluded(textEnd, runningEnd);
      if (annotation) sourcePieces.push({kind: 'excluded', reason: 'translation-comparison-note', text: annotation,
        sourceStart: runningEnd, sourceEnd: rawText.length, textSHA256: digest(annotation)});
      require(sourcePieces[0].sourceStart === 0 && sourcePieces.at(-1).sourceEnd === rawText.length
        && sourcePieces.every((piece, index) => index === 0 || sourcePieces[index - 1].sourceEnd === piece.sourceStart), 'source ledger is discontinuous');
      paragraphs.push({sourceId, sourceIdentityKind: 'xml:id', sourcePath: contract.path, sourceAttributes, bookAttributes, chapterAttributes,
        paragraphOrdinal: paragraphs.length, chapter, paragraph: localParagraph, citationLabel: label,
        rawText, runningText, removedPrefix: prefix, sourcePieces,
        sections: [{recordId: record.id, section, sourceStart: 0, sourceEnd: rawText.length, textStart, textEnd,
          leadingWhitespace: rawText.slice(prefix.length, textStart), trailingWhitespace: rawText.slice(textEnd, runningEnd), textSHA256: digest(text)}],
        editorialSpans: [], structuralMarkers: [], exactRestorationVerified: true});
    }
    equal(chapterMatch[2].slice(consumed).trim(), '', 'unparsed chapter suffix');
    require(localParagraph > 0, 'chapter has no paragraphs');
  }
  equal(bodyMatch[3].slice(chapterConsumed).trim(), '', 'unparsed book suffix');
  equal(records.map(record => record.section), range(contract.sections), 'paragraph order differs');
  equal(chapters.length, contract.chapters, 'chapter count differs');
  equal(headingCount, contract.headings, 'heading count differs');
  const counts = {bodyParagraphs: paragraphs.length, numberedParagraphs: paragraphs.length, sections: records.length,
    runningWordTokens: records.reduce((total, record) => total + words(record.text).length, 0), chapterDivisionsIncludingPrologue: chapters.length,
    prologueUnits: records.filter(record => record.chapter === 0).length, excludedCitationLabels: records.length,
    excludedHeadings: headingCount, excludedReleaseNotes: 1,
    excludedTranslationNotes: paragraphs.filter(p => p.sourcePieces.some(piece => piece.reason === 'translation-comparison-note')).length,
    breakBeforeUnits: records.filter(record => record.breakBefore).length};
  equal([counts.runningWordTokens, counts.prologueUnits, counts.breakBeforeUnits],
    [contract.tokens, contract.book === 1 ? 3 : 0, contract.book === 1 ? 1 : 0], 'running text or Prologue totals differ');
  return {records, report: {schemaVersion: 1, status: 'PASS', scope: {work: 'De excidio Hierosolymitano', book: contract.book,
    language: 'English', edition: 'Pollard v1.1', unit: 'existing chapter/paragraph citation unit', citationScheme: 'chapter-paragraph'},
    source: indexedSource, additionalSources: [], sources: [indexedSource],
    sourceContract: {normalizedSHA256: contract.sha256, hashMode: 'CRLF-to-LF only', verified: true}, rules: RULES, counts,
    coverage: coverage(paragraphs, records, [1, contract.sections]), excludedBlocks, paragraphs}};
}

export function validateDehEnglishSourceProjection(corpus, report, manifest, spec, root) {
  equal([manifest.id, manifest.work, manifest.language, manifest.edition, manifest.citationScheme, manifest.readerPath],
    [COLLECTION, 'deh', 'English', 'Pollard v1.1', 'chapter-paragraph', 'deh/'], 'collection identity differs');
  equal(manifest.books.map(book => book.number), range(5), 'collection includes an unreviewed book');
  const contract = CONTRACTS.find(source => source.book === spec.number);
  require(contract, 'per-book report is outside the reviewed collection');
  equal([spec.sections, spec.sectionRange, spec.source, spec.additionalSources || []],
    [contract.sections, [1, contract.sections], contract.path, []], 'book source scope differs');
  const expected = expectedDocument(root, contract, report.source);
  equal(corpus, expected.records, 'record text, source identity, reader metadata or phrase boundary differs from accepted XML');
  equal(report, expected.report, 'source restoration report differs from accepted XML');
  return {status: 'PASS', sections: contract.sections, tokens: contract.tokens, sourceDocuments: 1, restoredParagraphs: contract.sections};
}
