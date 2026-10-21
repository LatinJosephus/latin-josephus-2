/** Independent, hash-pinned source projection for Whiston Contra Apionem I–II. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';

const COLLECTION = 'contra-apionem-english-whiston';
const ROMANS = ['I', 'II'];
const CONTRACTS = [
  ['2c7731cf1eb2f4b70ff2177ef192b7b0452bf2871de023ab405ec83b60f6125a', 320, 18497, 35, 35, 0],
  ['12d006e8e0b296f84f5ef50ae7aa50c781ffe1b8821def5840e82cd317a7b467', 296, 18356, 41, 42, 2],
].map(([sha256, sections, tokens, chapters, whistonSections, inlineWhistonSections], index) => ({book: index + 1,
  sha256, sections, tokens, chapters, whistonSections, inlineWhistonSections,
  path: `assets/xml/contra-apionem/English/book-${String(index + 1).padStart(2, '0')}.xml`}));
const RULES = {
  boundaries: 'The accepted English p@n and xml:id define each Niese section. No boundaries or missing ranges are inferred from another language.',
  text: 'Preserve every running source character and punctuation; trim only section-edge whitespace. The TEI header and structural milestone numbers are not running text. No spelling repair or note invention.',
  sourceIdentity: 'Each original English xml:id identifies its complete source paragraph and Niese section.',
  structuralMarkers: 'Retain Niese chapter and Whiston-section milestone attributes and positions. The inline Whiston milestones in II.109 and II.112 contribute no words; all surrounding text and tails remain searchable.',
  editorialMarkup: 'Literal brackets and punctuation remain part of the original text. No additions, deletions, gaps or editorial annotations are inferred from their appearance or from another edition.',
  phraseBoundaries: 'Physically consecutive Niese sections and chapter or Whiston divisions remain joinable in whole-book scope. Phrases never cross books or editions.',
  coordinates: 'All sourcePieces, section and inline milestone coordinates are zero-based original-text UTF-16 offsets, end exclusive.',
};
const digest = value => createHash('sha256').update(value).digest('hex');
const equal = (a, b, message) => assert.deepEqual(a, b, `Whiston Contra Apionem ${message}`);
const require = (value, message) => assert(value, `Whiston Contra Apionem ${message}`);
const words = text => Array.from(text.matchAll(/[\p{L}\p{N}][\p{L}\p{M}\p{N}]*/gu), match => match[0]);
const range = last => Array.from({length: last}, (_, index) => index + 1);

function decodeXML(value) {
  const decoded = value.replace(/&(?:#x([a-fA-F0-9]+)|#([0-9]+)|(amp|lt|gt|quot|apos));/gu,
    (_, hex, dec, name) => hex ? String.fromCodePoint(Number.parseInt(hex, 16)) : dec ? String.fromCodePoint(Number(dec))
      : ({amp: '&', lt: '<', gt: '>', quot: '"', apos: "'"})[name]);
  require(!/&(?:#|[a-zA-Z])[a-zA-Z0-9]*;/u.test(decoded), 'source contains an unsupported XML entity');
  return decoded;
}

function attributes(value) {
  const result = {};
  let cursor = 0;
  for (const match of value.matchAll(/\s+([A-Za-z_:][A-Za-z0-9_.:-]*)\s*=\s*(?:"([^"]*)"|'([^']*)')/gu)) {
    require(value.slice(cursor, match.index).trim() === '', 'attribute reader left unparsed text');
    require(!Object.hasOwn(result, match[1]), 'duplicate XML attribute');
    result[match[1]] = decodeXML(match[2] ?? match[3]);
    cursor = match.index + match[0].length;
  }
  require(value.slice(cursor).trim() === '', 'unparsed attribute suffix');
  return result;
}

function milestone(sourceAttributes, inline = false) {
  require(/^[1-9][0-9]*$/u.test(sourceAttributes.n), 'invalid structural milestone number');
  const unit = sourceAttributes.unit;
  if (unit === 'whiston-section') equal(Object.keys(sourceAttributes).sort(), ['n', 'unit'], 'Whiston milestone attributes differ');
  else {
    require(!inline && unit === 'chapter', 'unreviewed structural milestone');
    equal(Object.keys(sourceAttributes).sort(), ['n', 'subtype', 'unit'], 'chapter milestone attributes differ');
    equal(sourceAttributes.subtype, 'niese', 'chapter milestone subtype differs');
  }
  return {unit, number: Number(sourceAttributes.n), sourceAttributes};
}

/** Deliberately narrow syntax reader, used only after the entire XML hash passes. */
function paragraphProjection(contents) {
  let raw = '', consumed = 0;
  const structuralMarkers = [];
  for (const token of contents.matchAll(/<[^>]*>|[^<]+/gu)) {
    equal(token.index, consumed, 'paragraph reader skipped source characters');
    consumed = token.index + token[0].length;
    const value = token[0];
    if (!value.startsWith('<')) {
      raw += decodeXML(value);
      continue;
    }
    const match = value.match(/^<milestone\b([\s\S]*?)\/\s*>$/u);
    require(match, 'unreviewed inline element');
    const marker = milestone(attributes(match[1]), true);
    structuralMarkers.push({unit: marker.unit, number: marker.number, sourceTextOffset: raw.length,
      sourceAttributes: marker.sourceAttributes});
  }
  equal(consumed, contents.length, 'paragraph reader stopped early');
  return {raw, structuralMarkers};
}

function coverage(paragraphs, records, sectionRange) {
  const byId = new Map(records.map(record => [record.id, record]));
  const raw = paragraphs.map(paragraph => paragraph.rawText);
  const restored = paragraphs.map(paragraph => paragraph.sourcePieces.map(piece => piece.kind === 'record'
    ? byId.get(piece.recordId).text.slice(piece.recordStart, piece.recordEnd) : piece.text).join(''));
  const sourceWords = raw.flatMap(words), indexedWords = records.flatMap(record => words(record.text));
  const sourceContent = raw.join('').replace(/\s/gu, ''), indexedContent = records.map(record => record.text).join('').replace(/\s/gu, '');
  equal(raw, restored, 'source restoration failed');
  equal(sourceWords, indexedWords, 'projection changes source words');
  equal(sourceContent, indexedContent, 'source characters were omitted');
  return {completeRange: sectionRange, missingSections: [], unexpectedSections: [], duplicateSections: [],
    allSectionTextsNonempty: records.every(record => record.text.length > 0), paragraphsExactlyRestored: paragraphs.length,
    wordSequencePreserved: true, nonWhitespaceContentPreserved: true,
    rawParagraphSequenceSha256: digest(raw.join('\n')), restoredParagraphSequenceSha256: digest(restored.join('\n')),
    sourceWordSequenceSha256: digest(sourceWords.join('\n')), indexedWordSequenceSha256: digest(indexedWords.join('\n')),
    sourceNonWhitespaceContentSha256: digest(sourceContent), indexedNonWhitespaceContentSha256: digest(indexedContent)};
}

function expectedDocument(root, contract, indexedSource) {
  const filename = path.resolve(root, contract.path), realRoot = fs.realpathSync(root);
  require(!fs.lstatSync(filename).isSymbolicLink() && fs.realpathSync(filename).startsWith(realRoot + path.sep),
    'XML is not an owned repository file');
  const bytes = fs.readFileSync(filename), normalized = Buffer.from(bytes.toString('latin1').replace(/\r\n/gu, '\n'), 'latin1');
  equal(digest(normalized), contract.sha256, `source differs from the accepted source: ${contract.path}`);
  const crlf = Buffer.from(normalized.toString('latin1').replace(/\n/gu, '\r\n'), 'latin1');
  require(indexedSource && [normalized, crlf].some(value => indexedSource.sha256 === digest(value) && indexedSource.bytes === value.length),
    'indexed source fingerprint differs');
  equal(Object.keys(indexedSource).sort(), ['bytes', 'path', 'sha256'], 'source fingerprint schema differs');
  equal(indexedSource.path, contract.path, 'source identity differs');
  const xml = normalized.toString('utf8');
  const textContainers = [...xml.matchAll(/<text\b([^>]*)>/gu)];
  equal(textContainers.length, 1, 'text container count differs');
  equal(attributes(textContainers[0][1]), {'xml:lang': 'eng'}, 'language identity differs');
  const bodies = [...xml.matchAll(/<body\b([^>]*)>([\s\S]*?)<\/body\s*>/gu)];
  equal(bodies.length, 1, 'source body count differs');
  equal(attributes(bodies[0][1]), {}, 'source body attributes differ');
  const bookDivs = [...bodies[0][2].matchAll(/<div1\b([^>]*)>([\s\S]*?)<\/div1\s*>/gu)];
  equal(bookDivs.length, 1, 'source book container count differs');
  equal(bodies[0][2].replace(bookDivs[0][0], '').trim(), '', 'unclassified text outside book');
  const parentAttributes = attributes(bookDivs[0][1]);
  equal(parentAttributes, {type: 'book', n: String(contract.book), 'xml:id': `english-apion${contract.book}`}, 'book identity differs');
  const contents = bookDivs[0][2], children = [];
  let consumed = 0;
  for (const match of contents.matchAll(/<milestone\b([^>]*?)\/\s*>|<p\b([^>]*)>([\s\S]*?)<\/p\s*>/gu)) {
    equal(contents.slice(consumed, match.index).trim(), '', 'unclassified text outside paragraphs');
    consumed = match.index + match[0].length;
    children.push(match[1] !== undefined ? {kind: 'milestone', attributes: attributes(match[1])}
      : {kind: 'paragraph', attributes: attributes(match[2]), contents: match[3]});
  }
  equal(contents.slice(consumed).trim(), '', 'unparsed book suffix');
  const records = [], paragraphs = [], structuralMarkers = [], chapters = [], whistonSections = [];
  let currentChapter = null, currentWhiston = null;
  const orderOffset = CONTRACTS.filter(source => source.book < contract.book).reduce((total, source) => total + source.sections, 0);
  for (const [bookChildIndex, child] of children.entries()) {
    if (child.kind === 'milestone') {
      const marker = milestone(child.attributes), following = children.slice(bookChildIndex + 1).find(item => item.kind === 'paragraph');
      require(following, 'trailing structural milestone without a paragraph');
      structuralMarkers.push({...marker, beforeSection: Number(following.attributes.n), previousSection: records.at(-1)?.section ?? null,
        bookChildIndex});
      if (marker.unit === 'chapter') {
        chapters.push(marker.number);
        currentChapter = marker.number;
      } else {
        whistonSections.push(marker.number);
        currentWhiston = marker.number;
      }
      continue;
    }
    const sourceAttributes = child.attributes, section = Number(sourceAttributes.n), sourceId = sourceAttributes['xml:id'];
    require(/^[1-9][0-9]*$/u.test(sourceAttributes.n), 'invalid Niese paragraph number');
    equal(sourceAttributes, {n: String(section), 'xml:id': `english-apion${contract.book}-num${section}`}, 'paragraph identity differs');
    require(currentChapter !== null && currentWhiston !== null, 'paragraph precedes its chapter or Whiston division');
    const projected = paragraphProjection(child.contents), {raw} = projected;
    const text = raw.trim(), leadingWhitespace = raw.match(/^\s*/u)[0], textStart = leadingWhitespace.length, textEnd = textStart + text.length;
    require(text.length && words(text).length, 'empty citation interval');
    const whistonSectionStart = currentWhiston;
    for (const marker of projected.structuralMarkers) {
      whistonSections.push(marker.number);
      currentWhiston = marker.number;
    }
    const record = {id: `${COLLECTION}-${contract.book}-${section}`, work: 'contra-apionem', book: contract.book, section,
      language: 'English', edition: 'Whiston', citationScheme: 'niese', citationLabel: `${ROMANS[contract.book - 1]}.${section}`,
      citation: {book: ROMANS[contract.book - 1], section}, text, editorialMarks: [], sourceMarkup: [], textGaps: [], phraseBreaks: [],
      url: `/contra-apionem/?book=${contract.book}&niese=${section}&english=whiston`,
      readerLink: {path: 'contra-apionem/', params: {book: contract.book, niese: section, english: 'whiston'}},
      sourceId, sourceIds: [sourceId], sourceIdentityKind: 'xml:id', sourcePath: contract.path, order: orderOffset + records.length};
    records.push(record);
    const sourcePieces = [];
    const excluded = (start, end) => {
      if (start === end) return;
      const fragment = raw.slice(start, end);
      require(/^\s+$/u.test(fragment), 'non-whitespace running text was excluded');
      sourcePieces.push({kind: 'excluded', reason: 'section-edge-whitespace', text: fragment,
        sourceStart: start, sourceEnd: end, textSHA256: digest(fragment)});
    };
    excluded(0, textStart);
    sourcePieces.push({kind: 'record', recordId: record.id, recordStart: 0, recordEnd: text.length,
      sourceStart: textStart, sourceEnd: textEnd, textSHA256: digest(text)});
    excluded(textEnd, raw.length);
    require(sourcePieces[0].sourceStart === 0 && sourcePieces.at(-1).sourceEnd === raw.length
      && sourcePieces.every((piece, index) => index === 0 || sourcePieces[index - 1].sourceEnd === piece.sourceStart),
    'source pieces overlap or leave an interval uncovered');
    paragraphs.push({sourceId, sourceIdentityKind: 'xml:id', sourcePath: contract.path, sourceAttributes, parentAttributes,
      paragraphOrdinal: paragraphs.length, sourceChapter: currentChapter, whistonSectionStart, whistonSectionEnd: currentWhiston,
      rawText: raw, runningText: raw, sourcePieces,
      sections: [{recordId: record.id, section, sourceStart: 0, sourceEnd: raw.length, textStart, textEnd,
        leadingWhitespace, trailingWhitespace: raw.slice(textEnd), textSHA256: digest(text)}],
      nieseMarkers: [], editorialSpans: [], structuralMarkers: projected.structuralMarkers, exactRestorationVerified: true});
  }
  equal(records.map(record => record.section), range(contract.sections), 'section order differs');
  equal(chapters, range(contract.chapters), 'chapter sequence differs');
  equal(whistonSections, range(contract.whistonSections), 'Whiston division sequence differs');
  const counts = {bodyParagraphs: paragraphs.length, narrativeParagraphs: paragraphs.length, numberedParagraphs: paragraphs.length,
    sections: records.length, runningWordTokens: records.reduce((total, record) => total + words(record.text).length, 0),
    chapterMilestones: chapters.length, whistonSectionMilestones: whistonSections.length,
    inlineWhistonSectionMilestones: paragraphs.reduce((total, paragraph) => total + paragraph.structuralMarkers.length, 0), breakBeforeUnits: 0};
  equal([counts.sections, counts.runningWordTokens, counts.inlineWhistonSectionMilestones],
    [contract.sections, contract.tokens, contract.inlineWhistonSections], 'source totals differ');
  return {records, report: {schemaVersion: 1, status: 'PASS', scope: {work: 'Contra Apionem', book: contract.book, language: 'English',
    edition: 'Whiston', unit: 'Niese section', citationScheme: 'niese'}, source: indexedSource, additionalSources: [], sources: [indexedSource],
    sourceContract: {normalizedSHA256: contract.sha256, hashMode: 'CRLF-to-LF only', verified: true}, rules: RULES, counts,
    coverage: coverage(paragraphs, records, [1, contract.sections]), excludedBlocks: [], structuralMarkers, paragraphs}};
}

/** Verify each complete corpus and reversible report directly against the accepted XML. */
export function validateWhistonContraApionemSourceProjection(corpus, report, manifest, spec, root) {
  equal([manifest.id, manifest.work, manifest.language, manifest.edition, manifest.citationScheme, manifest.readerPath],
    [COLLECTION, 'contra-apionem', 'English', 'Whiston', 'niese', 'contra-apionem/'], 'collection identity differs');
  equal(manifest.books.map(book => book.number), range(2), 'collection includes an unreviewed book');
  const contract = CONTRACTS.find(source => source.book === spec.number);
  require(contract, 'per-book report is outside the reviewed collection');
  equal([spec.sections, spec.sectionRange, spec.source, spec.additionalSources || []],
    [contract.sections, [1, contract.sections], contract.path, []], 'book source scope differs');
  const expected = expectedDocument(root, contract, report.source);
  equal(corpus, expected.records, 'record text, source identity, reader metadata or phrase boundary differs from accepted XML');
  equal(report, expected.report, 'source restoration report differs from accepted XML');
  return {status: 'PASS', sections: contract.sections, tokens: contract.tokens, sourceDocuments: 1, restoredParagraphs: contract.sections};
}
