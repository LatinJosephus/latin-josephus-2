/** Verify the Whiston pilot directly against its accepted, unchanged XML. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';

const COLLECTION = 'antiquities-english-whiston';
const XML_ID = '{http://www.w3.org/XML/1998/namespace}id';
const SOURCES = [
  {path: 'assets/xml/antiquities/English/preface.xml', proem: true, first: 1, last: 26,
    sha256: 'd04712a2db72f2d2c39e175591b866308f93cb15d10f4ee3be70401f7dd614eb'},
  {path: 'assets/xml/antiquities/English/book-01.xml', proem: false, first: 27, last: 346,
    sha256: '9cd8daf04bddfd94cd96f077c0b9336135c35d017fad029a56fd08e1fc2363f3'},
];
const digest = value => createHash('sha256').update(value).digest('hex');
const equal = (actual, expected, message) => assert.deepEqual(actual, expected, `Whiston ${message}`);
const range = (first, last) => Array.from({length: last - first + 1}, (_, index) => first + index);
const codePoints = text => Array.from(text).length;
const words = text => Array.from(text.matchAll(/[\p{L}\p{N}][\p{L}\p{M}\p{N}]*/gu), match => match[0]);
const noSpace = text => text.replace(/\s/gu, '');
const lfBytes = bytes => Buffer.from(bytes.toString('latin1').replace(/\r\n/gu, '\n'), 'latin1');

function decodeXML(text) {
  assert(!/&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[\da-fA-F]+);)/u.test(text), 'Whiston unreviewed XML entity');
  return text.replace(/&(amp|lt|gt|quot|apos|#\d+|#x[\da-fA-F]+);/gu, (_, entity) => {
    if (entity.startsWith('#')) return String.fromCodePoint(parseInt(entity.slice(entity[1] === 'x' ? 2 : 1), entity[1] === 'x' ? 16 : 10));
    return {amp: '&', lt: '<', gt: '>', quot: '"', apos: "'"}[entity];
  });
}

function attributes(text) {
  const result = {}, pattern = /([A-Za-z_:][\w:.-]*)\s*=\s*(["'])([\s\S]*?)\2/gu;
  for (const match of text.matchAll(pattern)) {
    const key = match[1] === 'xml:id' ? XML_ID : match[1];
    assert(!Object.hasOwn(result, key), 'Whiston duplicate XML attribute');
    result[key] = decodeXML(match[3]);
  }
  assert(text.replace(pattern, '').trim() === '', 'Whiston unreviewed XML attributes');
  return result;
}

/** A deliberately narrow XML token reader, usable only after the source hash pin passes. */
function paragraphProjection(contents) {
  let raw = '', flat = '', label = null, consumed = 0;
  const spans = [], exclusions = [], markers = [], structures = [];
  for (const token of contents.matchAll(/<[^>]*>|[^<]+/gu)) {
    equal(token.index, consumed, 'source token reader left an unparsed character');
    consumed += token[0].length;
    if (!token[0].startsWith('<')) {
      const text = decodeXML(token[0]);
      if (!label) {
        spans.push({rawStart: raw.length, rawEnd: raw.length + text.length,
          flatStart: flat.length, flatEnd: flat.length + text.length});
        flat += text;
      }
      raw += text;
      continue;
    }
    if (/^<num(?:\s|>)/u.test(token[0])) {
      assert(label === null, 'Whiston nested citation labels are unreviewed');
      const opening = /^<num\b([^>]*)>$/u.exec(token[0]);
      assert(opening && !opening[1].endsWith('/'), 'Whiston unreviewed citation label');
      label = {rawStart: raw.length, sourceAttributes: attributes(opening[1])};
    } else if (/^<\/num\s*>$/u.test(token[0])) {
      assert(label, 'Whiston citation label has no opening element');
      exclusions.push({kind: 'excluded', reason: 'citation-label', text: raw.slice(label.rawStart),
        sourceStart: label.rawStart, sourceEnd: raw.length, sourceAttributes: label.sourceAttributes});
      label = null;
    } else {
      assert(label === null, 'Whiston markup inside a citation label is unreviewed');
      const structural = /^<(milestone|anchor|lb)\b([^>]*)\/\s*>$/u.exec(token[0]);
      assert(structural, `Whiston unreviewed narrative token: ${token[0].slice(0, 80)}`);
      const sourceAttributes = attributes(structural[2]);
      const offsets = {sourceAttributes, sourceTextOffset: raw.length, runningTextOffset: flat.length};
      if (structural[1] === 'milestone') {
        equal(sourceAttributes.unit, 'niese', 'milestone unit differs');
        assert(/^[1-9]\d*$/u.test(sourceAttributes.n), 'Whiston milestone identity is invalid');
        markers.push({section: Number(sourceAttributes.n), ...offsets});
      } else structures.push({kind: structural[1], ...offsets});
    }
  }
  equal(consumed, contents.length, 'source token reader stopped early');
  equal(label, null, 'citation label is not closed');
  return {raw, flat, spans, exclusions, markers, structures};
}

function expectedRecord(text, section, sourceId, source, order) {
  const readerBook = source.proem ? 'preface' : 1;
  return {id: `${COLLECTION}-1-${section}`, work: 'antiquities', book: 1, section,
    language: 'English', edition: 'Whiston', citationScheme: 'niese', citationLabel: `I.${section}`,
    citation: {book: 'I', section, ...(source.proem ? {proem: true} : {})},
    text, editorialMarks: [], sourceMarkup: [], textGaps: [], phraseBreaks: [],
    url: `/antiquities/?book=${readerBook}&niese=${section}&english=whiston`,
    readerLink: {path: 'antiquities/', params: {book: readerBook, niese: section, english: 'whiston'}},
    sourceId, sourceIds: [sourceId], sourcePath: source.path, order,
    ...(source.proem ? {sourceDivision: 'proem', division: 'proem'} : {}),
    ...(section === 27 ? {breakBefore: true, breakReason: 'Book I narrative begins after the separately transmitted Proem.'} : {}),
  };
}

function expectedPieces(projected, intervals, byId) {
  const pieces = projected.exclusions.map(piece => ({...piece}));
  for (const span of projected.spans) {
    const cuts = [...new Set([span.flatStart, span.flatEnd, ...intervals.flatMap(interval => [interval.start, interval.end])
      .filter(offset => span.flatStart < offset && offset < span.flatEnd)])].sort((a, b) => a - b);
    for (let index = 0; index + 1 < cuts.length; index++) {
      const left = cuts[index], right = cuts[index + 1];
      const sourceStart = span.rawStart + left - span.flatStart, sourceEnd = sourceStart + right - left;
      const interval = intervals.find(item => item.start <= left && right <= item.end);
      const piece = interval
        ? {kind: 'record', recordId: interval.recordId, recordStart: left - interval.start,
          recordEnd: right - interval.start, sourceStart, sourceEnd}
        : {kind: 'excluded', reason: right <= intervals[0].flatStart ? 'pre-marker-label-punctuation' : 'section-edge-whitespace',
          text: projected.raw.slice(sourceStart, sourceEnd), sourceStart, sourceEnd};
      pieces.push(piece);
    }
  }
  pieces.sort((a, b) => a.sourceStart - b.sourceStart || a.sourceEnd - b.sourceEnd);
  let restored = '', cursor = 0;
  for (const piece of pieces) {
    equal(piece.sourceStart, cursor, 'independent restoration ledger is not contiguous');
    const text = piece.kind === 'record' ? byId.get(piece.recordId).text.slice(piece.recordStart, piece.recordEnd) : piece.text;
    equal(text, projected.raw.slice(piece.sourceStart, piece.sourceEnd), 'independent record slice differs from source');
    piece.textSHA256 = digest(text);
    restored += text;
    cursor = piece.sourceEnd;
  }
  equal(restored, projected.raw, 'independent paragraph restoration differs from XML');
  return pieces;
}

function coverage(paragraphs, records, sectionRange, includeOrder = false) {
  const sourceWords = paragraphs.flatMap(paragraph => words(paragraph.runningText));
  const indexedWords = records.flatMap(record => words(record.text));
  const sourceContent = paragraphs.map(paragraph => noSpace(paragraph.runningText)).join('');
  const indexedContent = records.map(record => noSpace(record.text)).join('');
  equal(sourceWords, indexedWords, 'source and citation word sequences differ');
  equal(sourceContent, indexedContent, 'source and citation characters differ');
  const raw = paragraphs.map(paragraph => paragraph.rawText).join('\n');
  return {completeRange: sectionRange, ...(includeOrder ? {sourceSectionOrder: records.map(record => record.section)} : {}),
    missingSections: [], unexpectedSections: [], duplicateSections: [], allSectionTextsNonempty: true,
    paragraphsExactlyRestored: paragraphs.length, wordSequencePreserved: true, nonWhitespaceContentPreserved: true,
    rawParagraphSequenceSha256: digest(raw), restoredParagraphSequenceSha256: digest(raw),
    sourceWordSequenceSha256: digest(sourceWords.join('\n')), indexedWordSequenceSha256: digest(indexedWords.join('\n')),
    sourceNonWhitespaceContentSha256: digest(sourceContent), indexedNonWhitespaceContentSha256: digest(indexedContent)};
}

function sourceDocument(root, source, indexedSource, orderOffset) {
  const filename = path.resolve(root, source.path), realRoot = fs.realpathSync(root);
  assert(!fs.lstatSync(filename).isSymbolicLink() && fs.realpathSync(filename).startsWith(realRoot + path.sep),
    'Whiston XML is not an owned repository file');
  const bytes = fs.readFileSync(filename), canonical = lfBytes(bytes);
  equal(digest(canonical), source.sha256, `source differs from the accepted source: ${source.path}`);
  const crlf = Buffer.from(canonical.toString('latin1').replace(/\n/gu, '\r\n'), 'latin1');
  assert(indexedSource && [canonical, crlf].some(value => indexedSource.sha256 === digest(value) && indexedSource.bytes === value.length),
    `Whiston indexed source fingerprint differs: ${source.path}`);
  equal(indexedSource.path, source.path, 'source identity differs');
  equal(Object.keys(indexedSource).sort(), ['bytes', 'path', 'sha256'], 'source fingerprint schema differs');
  const xml = canonical.toString('utf8'), bodies = [...xml.matchAll(/<body\b[^>]*>([\s\S]*?)<\/body\s*>/gu)];
  equal(bodies.length, 1, 'accepted source needs exactly one body');
  const body = bodies[0][1], paragraphs = [], records = [], excludedBlocks = [];
  const counts = {bodyParagraphs: 0, narrativeParagraphs: 0, excludedHeadingParagraphs: 0, excludedFootnotes: 0,
    excludedCitationLabels: 0, excludedSourceNotes: 0, nieseMilestones: 0, structuralMarkers: 0};
  const notes = [...body.matchAll(/<note\b([^>]*)>([\s\S]*?)<\/note\s*>/gu)];
  equal(notes.length, 1, 'source notice count differs');
  const noteText = decodeXML(notes[0][2]);
  equal(noteText.trim(), 'William Whiston (1737)', 'source notice differs');
  excludedBlocks.push({kind: 'source-note', text: noteText, sourceAttributes: attributes(notes[0][1])});
  counts.excludedSourceNotes++;
  for (const match of body.matchAll(/<p\b([^>]*)>([\s\S]*?)<\/p\s*>/gu)) {
    const sourceAttributes = attributes(match[1]), ordinal = counts.bodyParagraphs++;
    const projected = paragraphProjection(match[2]);
    if (!projected.markers.length) {
      assert(!sourceAttributes[XML_ID] && /^(?:BOOK\b|CHAPTER\b|CONTAINING\b|Antiquities of the Jews -- Preface$)/iu.test(projected.raw.trim()),
        'Whiston unreviewed heading');
      excludedBlocks.push({kind: 'heading', text: projected.raw, sourceAttributes, paragraphOrdinal: ordinal});
      counts.excludedHeadingParagraphs++;
      continue;
    }
    const sourceId = sourceAttributes[XML_ID];
    assert(sourceId && !paragraphs.some(paragraph => paragraph.sourceId === sourceId), 'Whiston missing or duplicate paragraph identity');
    const prefix = projected.flat.slice(0, projected.markers[0].runningTextOffset);
    assert(/^[\s.]*$/u.test(prefix), 'Whiston running words precede the first marker');
    const intervals = [], sections = [];
    for (let index = 0; index < projected.markers.length; index++) {
      const marker = projected.markers[index], flatStart = marker.runningTextOffset;
      const flatEnd = projected.markers[index + 1]?.runningTextOffset ?? projected.flat.length;
      const fragment = projected.flat.slice(flatStart, flatEnd), text = fragment.trim();
      assert(text.length, 'Whiston accepted citation interval is empty');
      const leading = fragment.match(/^\s*/u)[0], start = flatStart + leading.length, end = start + text.length;
      const record = expectedRecord(text, marker.section, sourceId, source, orderOffset + records.length);
      records.push(record);
      intervals.push({recordId: record.id, start, end, flatStart});
      sections.push({recordId: record.id, section: marker.section, leadingWhitespace: leading,
        trailingWhitespace: fragment.slice(leading.length + text.length), textSHA256: digest(text),
        flatStartCodePoints: codePoints(projected.flat.slice(0, flatStart)), flatEndCodePoints: codePoints(projected.flat.slice(0, flatEnd)),
        textStartCodePoints: codePoints(projected.flat.slice(0, start)), textEndCodePoints: codePoints(projected.flat.slice(0, end))});
    }
    const sourcePieces = expectedPieces(projected, intervals, new Map(records.map(record => [record.id, record])));
    paragraphs.push({sourceId, sourcePath: source.path, paragraphOrdinal: ordinal,
      rawText: projected.raw, runningText: projected.flat.slice(prefix.length), sourcePieces, sections,
      nieseMarkers: projected.markers, structuralMarkers: projected.structures, exactRestorationVerified: true});
    counts.narrativeParagraphs++;
    counts.excludedCitationLabels += projected.exclusions.length;
    counts.nieseMilestones += projected.markers.length;
    counts.structuralMarkers += projected.structures.length;
  }
  equal(records.map(record => record.section), range(source.first, source.last), 'accepted citation sequence differs');
  Object.assign(counts, {sections: records.length, runningWordTokens: records.reduce((total, record) => total + words(record.text).length, 0),
    numberedParagraphs: counts.narrativeParagraphs, breakBeforeUnits: records.filter(record => record.breakBefore).length});
  return {records, report: {schemaVersion: 1, status: 'PASS', scope: {work: 'Antiquities', book: 1, language: 'English',
    edition: 'Whiston', unit: 'Niese section', citationScheme: 'niese', proem: source.proem}, source: indexedSource,
    sourceContract: {normalizedSHA256: source.sha256, hashMode: 'CRLF-to-LF only', verified: true}, counts,
    coverage: coverage(paragraphs, records, [source.first, source.last], true), excludedBlocks, paragraphs}};
}

/** This gate accepts the per-book extraction report; no IX/XI test source can enter the pilot. */
export function validateWhistonSourceProjection(corpus, report, manifest, spec, root) {
  equal([manifest.id, manifest.work, manifest.language, manifest.edition, manifest.citationScheme, manifest.readerPath],
    [COLLECTION, 'antiquities', 'English', 'Whiston', 'niese', 'antiquities/'], 'collection identity differs');
  equal(manifest.books.map(book => book.number), [1], 'pilot includes an unreviewed book');
  equal([spec.number, spec.sections, spec.sectionRange, spec.source, spec.additionalSources],
    [1, 346, [1, 346], SOURCES[1].path, [SOURCES[0].path]], 'pilot source scope differs');
  equal([report.schemaVersion, report.status, report.scope], [1, 'PASS', {work: 'Antiquities', book: 1, language: 'English',
    edition: 'Whiston', unit: 'Niese section', citationScheme: 'niese', includesProem: true}], 'book report scope differs');
  assert(Array.isArray(report.documentReports) && report.documentReports.length === 2, 'Whiston document reports are incomplete');
  const documents = SOURCES.map((source, index) => sourceDocument(root, source, report.documentReports[index].source, index ? 26 : 0));
  const expected = documents.flatMap(document => document.records), paragraphs = documents.flatMap(document => document.report.paragraphs);
  equal(corpus, expected, 'record text, source identity, reader metadata or phrase boundary differs from accepted XML');
  equal(report.documentReports, documents.map(document => document.report), 'per-document audit differs from accepted XML');
  equal(report.paragraphs, paragraphs, 'source paragraph restoration evidence differs from accepted XML');
  equal(report.sources, documents.map(document => document.report.source), 'source list differs');
  equal(report.source, documents[1].report.source, 'narrative fingerprint differs');
  equal(report.additionalSources, [documents[0].report.source], 'Proem fingerprint differs');
  const counts = {};
  for (const document of documents) for (const [key, value] of Object.entries(document.report.counts)) counts[key] = (counts[key] || 0) + value;
  equal(report.counts, counts, 'extraction counts differ from actual source');
  equal(report.coverage, coverage(paragraphs, expected, [1, 346]), 'source preservation hashes differ from actual source');
  equal([counts.sections, counts.runningWordTokens, counts.narrativeParagraphs], [346, 21994, 83], 'reviewed pilot totals differ');
  return {status: 'PASS', sections: counts.sections, tokens: counts.runningWordTokens, sourceDocuments: 2, restoredParagraphs: paragraphs.length};
}
