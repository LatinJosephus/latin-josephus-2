/** Independent, hash-pinned source projection for Whiston Bellum I–VII. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';

const COLLECTION = 'bellum-english-whiston';
const ROMANS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'];
const CONTRACTS = [
  ['39713b6768eef8e7d6ac9640255eacd962ac9677175fbc05077aafe296a1b5ec', 673, 50097, 234, 34],
  ['52c0e14514dc6ba6942a2ff98e5a87c96122f117fe0122f112b697cbfc12f941', 654, 38098, 143, 22],
  ['ced7460be53bc6f7f94e4a842f9a3c3f28624cdaaced38d433acf2f4dd3d0cd2', 542, 24777, 88, 10],
  ['b5b299ee96671784527fc1edef4777e5a766e6f9496fcfb63470874c71824c96', 663, 30489, 78, 11],
  ['5a6647478976c860b7fb771b058b4af34181eff8201d502f037f0610ca536ee7', 572, 29415, 65, 13],
  ['edf957eb0501feebbe595f44703c2caa185c9acb6d28efbe69875f3aaa8b2799', 442, 21949, 50, 10],
  ['2d2c308a500711fddad5cc7ba436f59c38890dd4988f6f5b505817e04e5b200b', 455, 20247, 46, 11],
].map(([sha256, sections, tokens, paragraphs, chapters], index) => ({book: index + 1, sha256, sections, tokens, paragraphs, chapters,
  path: `assets/xml/bellum/English/book-${String(index + 1).padStart(2, '0')}.xml`}));
const SUPPLIED_ATTRIBUTES = {reason: 'omitted', source: 'https://lexundria.com/j_bj/7.208-7.209/wst'};
const SUPPLIED_TEXT = ' were slain, to the number of one thousand seven hundred, as were the women and the children made slaves; '
  + 'but as Bassus thought he must perform the covenant, he had made with those that had surrendered the citadel, '
  + 'he let them go, and restored Eleazar to them. ';
const RULES = {
  boundaries: 'Only accepted English milestone unit=niese positions define sections; sameAs is paragraph provenance, never a boundary inference.',
  text: 'Preserve all running source characters and punctuation; trim only section-edge whitespace. No stemming, spelling repair or note invention.',
  sourceIdentity: 'The original sameAs value, including its leading #, identifies each source paragraph. It is an alignment reference, not an invented English xml:id.',
  editorialMarkup: 'The accepted supplied element at VII.208–209 is retained as searchable text with clipped UTF-16 supplied marks and its exact reason/source attributes. The nested209 milestone is respected. No phrase barrier is introduced.',
  phraseBoundaries: 'Consecutive sections, paragraphs and chapters remain joinable in whole-book scope, including embedded Book I chapter0 sections1–30 and section31. Phrases never cross books or editions.',
  coordinates: 'All sourcePieces, section, milestone and editorial coordinates are zero-based original-text UTF-16 offsets, end exclusive.',
};
const digest = value => createHash('sha256').update(value).digest('hex');
const equal = (a, b, message) => assert.deepEqual(a, b, `Whiston Bellum ${message}`);
const require = (value, message) => assert(value, `Whiston Bellum ${message}`);
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

/** XML syntax here is deliberately narrow, after the entire source hash passes. */
function paragraphProjection(contents, sourceId, book) {
  let raw = '', consumed = 0, supplied = null;
  const markers = [], editorialSpans = [];
  for (const token of contents.matchAll(/<[^>]*>|[^<]+/gu)) {
    equal(token.index, consumed, 'paragraph reader skipped source characters');
    consumed = token.index + token[0].length;
    const value = token[0];
    if (!value.startsWith('<')) {
      raw += decodeXML(value);
      continue;
    }
    const milestone = value.match(/^<milestone\b([\s\S]*?)\/\s*>$/u);
    if (milestone) {
      const attrs = attributes(milestone[1]);
      equal(Object.keys(attrs).sort(), ['n', 'unit'], 'milestone attributes differ');
      require(attrs.unit === 'niese' && /^[1-9][0-9]*$/u.test(attrs.n), 'unreviewed milestone');
      markers.push({section: Number(attrs.n), sourceTextOffset: raw.length, sourceAttributes: attrs});
      continue;
    }
    const opening = value.match(/^<supplied\b([^>]*)>$/u);
    if (opening) {
      require(!supplied && book === 7 && sourceId === '#latin-bellum7-num190', 'supplied span is outside its reviewed position');
      const attrs = attributes(opening[1]);
      equal(attrs, SUPPLIED_ATTRIBUTES, 'supplied source attributes differ');
      supplied = {kind: 'supplied', sourceStart: raw.length, sourceAttributes: attrs};
      continue;
    }
    if (/^<\/supplied\s*>$/u.test(value)) {
      require(supplied, 'unmatched supplied closing tag');
      const text = raw.slice(supplied.sourceStart);
      equal(text, SUPPLIED_TEXT, 'supplied restoration differs');
      editorialSpans.push({...supplied, sourceEnd: raw.length, text});
      supplied = null;
      continue;
    }
    require(false, `unreviewed inline element: ${value}`);
  }
  equal(consumed, contents.length, 'paragraph reader stopped early');
  require(!supplied, 'unclosed supplied element');
  return {raw, markers, editorialSpans};
}

function coverage(paragraphs, records, sectionRange) {
  const byId = new Map(records.map(record => [record.id, record]));
  const raw = paragraphs.map(paragraph => paragraph.rawText);
  const restored = paragraphs.map(paragraph => paragraph.sourcePieces.map(piece => piece.kind === 'record'
    ? byId.get(piece.recordId).text.slice(piece.recordStart, piece.recordEnd) : piece.text).join(''));
  const sourceWords = raw.flatMap(words), indexedWords = records.flatMap(record => words(record.text));
  const sourceContent = raw.join('').replace(/\s/gu, ''), indexedContent = records.map(record => record.text).join('').replace(/\s/gu, '');
  equal(raw, restored, 'source restoration failed');
  equal(sourceWords, indexedWords, 'milestones split or change source words');
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
  const bodies = [...normalized.toString('utf8').matchAll(/<body\b([^>]*)>([\s\S]*?)<\/body\s*>/gu)];
  equal(bodies.length, 1, 'source body count differs');
  equal(attributes(bodies[0][1]), {}, 'source body attributes differ');
  const bookDivs = [...bodies[0][2].matchAll(/<div1\b([^>]*)>([\s\S]*?)<\/div1\s*>/gu)];
  equal(bookDivs.length, 1, 'source book container count differs');
  equal(bodies[0][2].replace(bookDivs[0][0], '').trim(), '', 'unclassified text outside book');
  equal(attributes(bookDivs[0][1]), {n: String(contract.book), subtype: 'English', type: 'book'}, 'book identity differs');
  const chapters = [...bookDivs[0][2].matchAll(/<div2\b([^>]*)>([\s\S]*?)<\/div2\s*>/gu)];
  equal(bookDivs[0][2].replace(/<div2\b[^>]*>[\s\S]*?<\/div2\s*>/gu, '').trim(), '', 'unclassified text outside chapters');
  equal(chapters.length, contract.chapters, 'chapter count differs');
  const records = [], paragraphs = [], orderOffset = CONTRACTS.filter(x => x.book < contract.book).reduce((total, x) => total + x.sections, 0);
  for (const [chapterIndex, chapter] of chapters.entries()) {
    const parentAttributes = attributes(chapter[1]), chapterNumber = String(chapterIndex + (contract.book === 1 ? 0 : 1));
    const wantedAttributes = {n: chapterNumber, sameAs: `#latin-bellum${contract.book}-chapter${chapterNumber}`};
    if (!(contract.book === 5 && chapterNumber === '13')) wantedAttributes.type = 'chapter';
    equal(parentAttributes, wantedAttributes, 'chapter identity differs');
    const sourceParagraphs = [...chapter[2].matchAll(/<p\b([^>]*)>([\s\S]*?)<\/p\s*>/gu)];
    require(sourceParagraphs.length > 0, 'empty chapter');
    equal(chapter[2].replace(/<p\b[^>]*>[\s\S]*?<\/p\s*>/gu, '').trim(), '', 'unclassified text outside paragraphs');
    for (const match of sourceParagraphs) {
      const sourceAttributes = attributes(match[1]), sourceId = sourceAttributes.sameAs;
      equal(Object.keys(sourceAttributes), ['sameAs'], 'paragraph attributes differ');
      require(new RegExp(`^#latin-bellum${contract.book}-num[1-9][0-9]*$`, 'u').test(sourceId)
        && !paragraphs.some(p => p.sourceId === sourceId), 'missing or duplicate paragraph identity');
      const projected = paragraphProjection(match[2], sourceId, contract.book);
      const {raw, markers, editorialSpans} = projected, sourcePieces = [], sections = [];
      require(markers.length && !raw.slice(0, markers[0].sourceTextOffset).trim(), 'narrative precedes the first Niese marker');
      const excluded = (start, end) => {
        if (start === end) return;
        const text = raw.slice(start, end);
        require(/^\s+$/u.test(text), 'non-whitespace running text was excluded');
        sourcePieces.push({kind: 'excluded', reason: 'section-edge-whitespace', text, sourceStart: start, sourceEnd: end, textSHA256: digest(text)});
      };
      excluded(0, markers[0].sourceTextOffset);
      for (const [index, marker] of markers.entries()) {
        const start = marker.sourceTextOffset, end = markers[index + 1]?.sourceTextOffset ?? raw.length;
        const fragment = raw.slice(start, end), text = fragment.trim(), leadingWhitespace = fragment.match(/^\s*/u)[0];
        require(text.length && words(text).length, 'empty citation interval');
        const textStart = start + leadingWhitespace.length, textEnd = textStart + text.length;
        const editorialMarks = editorialSpans.flatMap(mark => {
          const a = Math.max(textStart, mark.sourceStart), b = Math.min(textEnd, mark.sourceEnd);
          return a < b ? [{kind: mark.kind, start: a - textStart, end: b - textStart, text: raw.slice(a, b),
            sourceTag: 'supplied', sourceAttributes: mark.sourceAttributes}] : [];
        });
        const section = marker.section, roman = ROMANS[contract.book - 1];
        const record = {id: `${COLLECTION}-${contract.book}-${section}`, work: 'bellum', book: contract.book, section,
          language: 'English', edition: 'Whiston', citationScheme: 'niese', citationLabel: `${roman}.${section}`,
          citation: {book: roman, section}, text, editorialMarks, sourceMarkup: [], textGaps: [], phraseBreaks: [],
          url: `/bellum-judaicum/?book=${contract.book}&niese=${section}&english=whiston`,
          readerLink: {path: 'bellum-judaicum/', params: {book: contract.book, niese: section, english: 'whiston'}},
          sourceId, sourceIds: [sourceId], sourceIdentityKind: 'sameAs', sourcePath: contract.path, order: orderOffset + records.length};
        records.push(record);
        excluded(start, textStart);
        sourcePieces.push({kind: 'record', recordId: record.id, recordStart: 0, recordEnd: text.length,
          sourceStart: textStart, sourceEnd: textEnd, textSHA256: digest(text)});
        excluded(textEnd, end);
        sections.push({recordId: record.id, section, sourceStart: start, sourceEnd: end, textStart, textEnd,
          leadingWhitespace, trailingWhitespace: fragment.slice(leadingWhitespace.length + text.length), textSHA256: digest(text)});
      }
      require(sourcePieces[0].sourceStart === 0 && sourcePieces.at(-1).sourceEnd === raw.length
        && sourcePieces.every((piece, index) => index === 0 || sourcePieces[index - 1].sourceEnd === piece.sourceStart),
      'source pieces overlap or leave an interval uncovered');
      paragraphs.push({sourceId, sourceIdentityKind: 'sameAs', sourcePath: contract.path, sourceAttributes, parentAttributes,
        paragraphOrdinal: paragraphs.length, rawText: raw, runningText: raw, sourcePieces, sections,
        nieseMarkers: markers, editorialSpans, structuralMarkers: [], exactRestorationVerified: true});
    }
  }
  equal(records.map(record => record.section), range(contract.sections), 'section order differs');
  equal(records.filter(record => record.editorialMarks.length).map(record => record.section), contract.book === 7 ? [208, 209] : [],
    'supplied interval inventory differs');
  const counts = {bodyParagraphs: paragraphs.length, narrativeParagraphs: paragraphs.length, numberedParagraphs: paragraphs.length,
    sections: records.length, runningWordTokens: records.reduce((total, record) => total + words(record.text).length, 0), nieseMilestones: records.length,
    chapterDivisions: chapters.length, suppliedSpans: paragraphs.reduce((n, p) => n + p.editorialSpans.length, 0),
    suppliedRecordMarks: records.reduce((n, record) => n + record.editorialMarks.length, 0), breakBeforeUnits: 0};
  equal([counts.sections, counts.runningWordTokens, counts.narrativeParagraphs], [contract.sections, contract.tokens, contract.paragraphs], 'source totals differ');
  return {records, report: {schemaVersion: 1, status: 'PASS', scope: {work: 'Bellum Judaicum', book: contract.book, language: 'English',
    edition: 'Whiston', unit: 'Niese section', citationScheme: 'niese', includesEmbeddedPreface: contract.book === 1},
    source: indexedSource, additionalSources: [], sources: [indexedSource],
    sourceContract: {normalizedSHA256: contract.sha256, hashMode: 'CRLF-to-LF only', verified: true}, rules: RULES, counts,
    coverage: coverage(paragraphs, records, [1, contract.sections]), excludedBlocks: [], paragraphs}};
}

/** Verify the entire per-book corpus and reversible report against accepted XML. */
export function validateWhistonBellumSourceProjection(corpus, report, manifest, spec, root) {
  equal([manifest.id, manifest.work, manifest.language, manifest.edition, manifest.citationScheme, manifest.readerPath],
    [COLLECTION, 'bellum', 'English', 'Whiston', 'niese', 'bellum-judaicum/'], 'collection identity differs');
  equal(manifest.books.map(book => book.number), range(7), 'collection includes an unreviewed book');
  const contract = CONTRACTS.find(source => source.book === spec.number);
  require(contract, 'per-book report is outside the reviewed collection');
  equal([spec.sections, spec.sectionRange, spec.source, spec.additionalSources || []],
    [contract.sections, [1, contract.sections], contract.path, []], 'book source scope differs');
  const expected = expectedDocument(root, contract, report.source);
  equal(corpus, expected.records, 'record text, editorial annotation, source identity, reader metadata or phrase boundary differs from accepted XML');
  equal(report, expected.report, 'source restoration report differs from accepted XML');
  return {status: 'PASS', sections: contract.sections, tokens: contract.tokens, sourceDocuments: 1, restoredParagraphs: contract.paragraphs};
}
