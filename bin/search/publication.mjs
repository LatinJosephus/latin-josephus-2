/** Source, evidence, and publication checks for the static search export. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {editorialMarksFor} from './ui-utils.mjs';
import {phraseBreakOffsets, tokenizeRecord} from './engine.mjs';
import {planBrowserRelease, BROWSER_LAUNCHER_NAME} from './browser-release.mjs';
import {validateWhistonSourceProjection} from './whiston-publication.mjs';
import {validateWhistonBellumSourceProjection} from './whiston-bellum-publication.mjs';

export const SOURCE_DIRECTORY = 'bin/search';
export const ASSET_DIRECTORY = 'assets/search';
export const MANIFEST_NAME = 'publication-manifest.json';
export const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
export const jsonBytes = value => Buffer.from(JSON.stringify(value, null, 2) + '\n');
const posix = value => value.split(path.sep).join('/');
const equal = (actual, expected, message) => assert.deepEqual(actual, expected, message);
const sorted = values => [...values].sort();
const sectionRange = (first, last) => Array.from({length: last - first + 1}, (_, index) => first + index);
// Latin-1 preserves every byte while changing only the two-byte CRLF sequence.
const lfBytes = bytes => Buffer.from(bytes.toString('latin1').replace(/\r\n/gu, '\n'), 'latin1');

/** Resolve repository-owned paths, including config-relative ../, without escaping the base. */
export function inside(base, relative, {directory = false, exists = true} = {}) {
  assert(typeof relative === 'string' && relative.length && !relative.includes('\\') &&
    !/[\0?#]/u.test(relative) && !path.isAbsolute(relative), `Invalid relative path: ${relative}`);
  const absolute = path.resolve(base, relative);
  assert(absolute.startsWith(path.resolve(base) + path.sep) || (directory && absolute === path.resolve(base)),
    `Path leaves its owned directory: ${relative}`);
  if (exists) {
    const stat = fs.lstatSync(absolute);
    assert(!stat.isSymbolicLink(), `Search inputs and exports must not be symlinks: ${relative}`);
    assert(directory ? stat.isDirectory() : stat.isFile(), `Wrong file type: ${relative}`);
    const real = fs.realpathSync(absolute), realBase = fs.realpathSync(base);
    assert(real.startsWith(realBase + path.sep) || (directory && real === realBase),
      `Path resolves outside its owned directory: ${relative}`);
  }
  return absolute;
}

function listing(base, prefix = '') {
  return fs.readdirSync(inside(base, prefix || '.', {directory: true}), {withFileTypes: true})
    .sort((a, b) => a.name.localeCompare(b.name, 'en')).flatMap(entry => {
      const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
      assert(!entry.isSymbolicLink(), `Search directories must not contain symlinks: ${relative}`);
      if (entry.isDirectory()) {
        if (entry.name === '__pycache__' || entry.name === '.pytest_cache') return [];
        return listing(base, relative);
      }
      assert(entry.isFile(), `Unexpected file type in search directory: ${relative}`);
      return [relative];
    });
}

export function evidence(root, relative) {
  const absolute = inside(root, relative), bytes = fs.readFileSync(absolute);
  return {path: posix(path.relative(root, absolute)), sha256: sha256(bytes), bytes: bytes.length};
}

function readJSON(base, relative) {
  return JSON.parse(fs.readFileSync(inside(base, relative), 'utf8'));
}

function checkEvidence(root, item, context) {
  assert(item && /^[a-f0-9]{64}$/u.test(item.sha256), `Missing SHA-256: ${context}`);
  const actual = evidence(root, item.path);
  equal(actual.sha256, item.sha256, `Stale or changed ${context}: ${item.path}`);
  if (item.bytes !== undefined) equal(actual.bytes, item.bytes, `Wrong byte count: ${item.path}`);
  return actual;
}

function xmlInputEvidence(root, relative) {
  const filename = inside(root, relative), canonical = lfBytes(fs.readFileSync(filename));
  return {path: posix(path.relative(root, filename)), sha256: sha256(canonical),
    bytes: canonical.length, hashMode: 'crlf-to-lf'};
}

/** Match the exact indexed source hash to an LF/CRLF representation of unchanged current bytes. */
function checkIndexedXML(root, item, context) {
  assert(item && /^[a-f0-9]{64}$/u.test(item.sha256), `Missing source SHA-256: ${context}`);
  const current = fs.readFileSync(inside(root, item.path)), canonical = lfBytes(current);
  const crlf = Buffer.from(canonical.toString('latin1').replace(/\n/gu, '\r\n'), 'latin1');
  const indexedRepresentation = [canonical, crlf].find(bytes => sha256(bytes) === item.sha256);
  assert(indexedRepresentation, `Stale or changed ${context}: ${item.path} (comparison allows LF/CRLF only)`);
  if (item.bytes !== undefined) equal(indexedRepresentation.length, item.bytes, `Wrong indexed byte count: ${item.path}`);
  return {...xmlInputEvidence(root, item.path), indexedSHA256: item.sha256, indexedBytes: indexedRepresentation.length};
}

export function loadPublicationConfig(root) {
  const base = inside(root, SOURCE_DIRECTORY, {directory: true});
  const config = readJSON(base, 'config/publication.json');
  equal(config.schemaVersion, 1, 'Unsupported publication config');
  for (const key of ['runtime', 'siteInputs', 'hookInputs']) {
    assert(Array.isArray(config[key]) && config[key].length, `Missing publication ${key}`);
    equal(new Set(config[key]).size, config[key].length, `Duplicate publication ${key}`);
  }
  const registry = readJSON(base, config.registry);
  equal(registry.schemaVersion, 1, 'Unsupported collection registry');
  assert(Array.isArray(registry.collections) && registry.collections.length, 'Empty collection registry');
  const registryDirectory = path.dirname(inside(base, config.registry));
  const collections = registry.collections.map(relative => {
    // Collection filenames are relative to the registry; resolved files still belong to bin/search.
    const filename = inside(registryDirectory, relative);
    const manifestPath = posix(path.relative(base, filename));
    const manifest = readJSON(base, manifestPath);
    assert(typeof manifest.id === 'string' && manifest.id.length, 'Collection has no ID');
    const adapter = config.collections?.[manifest.id];
    assert(adapter, `No approved extraction/QA adapter for collection ${manifest.id}`);
    inside(base, adapter.extractor);
    inside(base, adapter.verifier);
    inside(base, adapter.outputDirectory, {directory: true});
    assert(Array.isArray(adapter.sources) && adapter.sources.length, `No approved sources for ${manifest.id}`);
    for (const relative of adapter.sources) inside(root, relative);
    for (const relative of adapter.testSources || []) inside(root, relative);
    return {manifestPath, manifest, adapter};
  });
  equal(new Set(collections.map(c => c.manifest.id)).size, collections.length, 'Duplicate collection ID');
  equal(sorted(Object.keys(config.collections)), sorted(collections.map(c => c.manifest.id)),
    'Publication adapters and the collection registry disagree');
  return {base, config, registry, collections};
}

/** Hash code/config membership too, so adding a module or configured source invalidates the export. */
export function sourceInputs(root, sourcePaths = []) {
  const {base, config, collections} = loadPublicationConfig(root);
  const files = listing(base).filter(relative => !relative.startsWith('data/') &&
    (/\.(?:mjs|js|cjs|py|css|html)$/u.test(relative) || relative.startsWith('config/') || relative.startsWith('vendor/')));
  const paths = new Set([...files.map(relative => `${SOURCE_DIRECTORY}/${relative}`),
    ...config.siteInputs, ...config.hookInputs, ...collections.flatMap(c => [...c.adapter.sources, ...(c.adapter.testSources || [])]), ...sourcePaths]);
  const indexedXML = new Set(collections.flatMap(c => [...c.adapter.sources, ...(c.adapter.testSources || [])]));
  return sorted(paths).map(relative => indexedXML.has(relative) ? xmlInputEvidence(root, relative) : evidence(root, relative));
}

export function unitTestCommands(root) {
  const base = inside(root, SOURCE_DIRECTORY, {directory: true});
  const tests = listing(inside(base, 'tests', {directory: true}));
  const nodeTests = tests.filter(name => name.endsWith('.test.mjs')).map(name => `${SOURCE_DIRECTORY}/tests/${name}`);
  const pythonTests = tests.filter(name => /^test_.*\.py$/u.test(name));
  assert(nodeTests.length && pythonTests.length, 'Expected the search unit test suites');
  return [
    {runtime: 'python3', arguments: ['-m', 'unittest', 'discover', '-s', `${SOURCE_DIRECTORY}/tests`, '-p', 'test_*.py']},
    {runtime: 'node', arguments: ['--test', ...nodeTests]},
  ];
}

/** Keep DEH's reader display and reversible XML text projection explicitly distinct. */
function validateDehSourceProjection(corpus, report, manifest, spec) {
  const roman = ['', 'I', 'II', 'III', 'IV', 'V'][spec.number];
  const originals = [], displays = [];
  let generated = 0;
  const marksByKind = {del: 0, supplied: 0, unclear: 0};
  equal(report.paragraphs.length, corpus.length, 'DEH source audit omits a citation unit');
  for (let index = 0; index < corpus.length; index++) {
    const record = corpus[index], audit = report.paragraphs[index];
    assert(Number.isInteger(record.chapter) && record.chapter >= 0 &&
      Number.isInteger(record.paragraph) && record.paragraph > 0, `Invalid DEH citation: ${record.id}`);
    const prologue = record.chapter === 0;
    assert(!prologue || (spec.number === 1 && record.section <= 3), 'Unexpected DEH Prologue unit');
    const label = prologue ? `Prol.${record.paragraph}` : `${roman}.${record.chapter}.${record.paragraph}`;
    equal(record.citationScheme, manifest.citationScheme, `DEH citation scheme differs: ${record.id}`);
    equal(record.citationLabel, label, `DEH scholarly citation differs: ${record.id}`);
    equal(record.sourceId, `latin-deh${spec.number}-num${record.section}`, `DEH stable identity differs: ${record.id}`);
    equal(record.citation, {book: roman, chapter: record.chapter, paragraph: record.paragraph, prologue},
      `DEH structured citation differs: ${record.id}`);
    equal(record.url, `/deh/?book=${spec.number}&chapter=${record.chapter}&unit=${record.paragraph}`,
      `DEH chapter-local reader URL differs: ${record.id}`);
    equal(record.readerLink, {path: 'deh/', params: {book: spec.number, chapter: record.chapter, unit: record.paragraph}},
      `DEH structured reader link differs: ${record.id}`);
    equal(Boolean(record.breakBefore), spec.number === 1 && record.section === 4,
      `DEH Prologue/narrative boundary differs: ${record.id}`);
    equal(audit.sourceId, record.sourceId, 'DEH source projection audit has the wrong unit');
    equal(audit.citationLabel, label, 'DEH source projection audit has the wrong citation');
    assert(Array.isArray(record.editorialMarks), `DEH editorial metadata is missing: ${record.id}`);
    let cursor = 0, previousEnd = 0, sourceText = '';
    for (const mark of record.editorialMarks) {
      assert(Object.hasOwn(marksByKind, mark.kind) && Number.isInteger(mark.start) && Number.isInteger(mark.end) &&
        mark.start >= previousEnd && mark.end > mark.start && mark.end <= record.text.length,
      `Invalid or overlapping DEH editorial span: ${record.id}`);
      equal(record.text.slice(mark.start, mark.end), mark.text, `DEH editorial text differs: ${record.id}`);
      marksByKind[mark.kind]++;
      if (mark.kind === 'unclear') {
        equal([mark.text, mark.representation, mark.sourceTag], ['†', 'generated-dagger', 'unclear'],
          `Unrecognized DEH generated display glyph: ${record.id}`);
        sourceText += record.text.slice(cursor, mark.start);
        cursor = mark.end;
        generated++;
      }
      previousEnd = mark.end;
    }
    sourceText += record.text.slice(cursor);
    equal(sha256(Buffer.from(record.text)), audit.displayTextSha256, `DEH display-text audit differs: ${record.id}`);
    equal(sha256(Buffer.from(sourceText)), audit.sourceProjectionSha256, `DEH source projection differs: ${record.id}`);
    originals.push(sourceText);
    displays.push(record.text);
  }
  const nonWhitespaceHash = texts => sha256(Buffer.from(texts.join('').replace(/\s/gu, '')));
  equal(nonWhitespaceHash(originals), report.coverage.sourceProjectionNonWhitespaceContentSha256,
    'DEH reversible source-text fingerprint differs');
  equal(report.coverage.sourceProjectionNonWhitespaceContentSha256,
    report.coverage.sourceNonWhitespaceContentSha256,
    'DEH source projection and original-source fingerprints differ');
  equal(nonWhitespaceHash(displays), report.coverage.displayNonWhitespaceContentSha256,
    'DEH actual display-text fingerprint differs');
  equal(sha256(Buffer.from(displays.join('\n'))), report.coverage.displayTextSequenceSha256,
    'DEH display-text order differs');
  equal(report.coverage.sourceProjectionExactlyRestoresSource, true, 'DEH original-source projection is unverified');
  equal(generated, report.coverage.generatedDisplayGlyphs, 'DEH generated-glyph count differs');
  equal(generated, report.counts.generatedCruxGlyphs, 'DEH crux count differs');
  equal([marksByKind.del, marksByKind.supplied, marksByKind.unclear],
    [report.counts.deletedSpans, report.counts.suppliedSpans, report.counts.cruxMarkers],
    'DEH editorial annotation coverage differs');
}

/** Bind Boysen's exact text, Niese identities and marked phrase interruptions. */
export function validateCaSourceProjection(corpus, report, manifest, spec) {
  const roman = spec.number === 1 ? 'I' : 'II';
  const displays = [], originals = [], counts = {add: 0, q: 0, foreign: 0, markers: 0, breakBefore: 0};
  const digest = value => sha256(Buffer.from(value));
  equal(report.paragraphs.length, corpus.length, 'CA source audit omits a Niese section');
  for (let index = 0; index < corpus.length; index++) {
    const record = corpus[index], audit = report.paragraphs[index], label = `${roman}.${index + 1}`;
    equal(record.citationScheme, manifest.citationScheme, `CA citation scheme differs: ${record.id}`);
    equal(record.citationLabel, label, `CA citation differs: ${record.id}`);
    equal(record.sourceId, `latin-apion${spec.number}-num${index + 1}`, `CA stable identity differs: ${record.id}`);
    equal(record.citation, {book: roman, section: index + 1}, `CA structured citation differs: ${record.id}`);
    equal(record.url, `/contra-apionem/?book=${spec.number}&niese=${index + 1}`, `CA reader URL differs: ${record.id}`);
    equal(record.readerLink, {path: 'contra-apionem/', params: {book: spec.number, niese: index + 1}},
      `CA structured reader link differs: ${record.id}`);
    equal(record.chapter, undefined, 'CA Niese units must not be assigned one misleading Boysen chapter');
    equal(audit.sourceId, record.sourceId, 'CA source audit identifies a different section');
    equal(audit.citationLabel, label, 'CA source audit has a different citation');
    equal(audit.displayTextSha256, digest(record.text), `CA display fingerprint differs: ${record.id}`);
    equal(audit.sourceProjectionSha256, digest(record.text), `CA source projection differs: ${record.id}`);
    equal(audit.removedPrefix, '', 'CA text must not lose a fabricated leading citation label');
    assert(/^\s*$/u.test(audit.leadingWhitespace) && /^\s*$/u.test(audit.trailingWhitespace), 'CA restoration may only reinstate edge whitespace');
    const original = audit.leadingWhitespace + record.text + audit.trailingWhitespace;
    const characters = Array.from(original), left = Array.from(audit.leadingWhitespace).length;
    equal(audit.rawTextCharacters, characters.length, 'CA raw character count differs');
    equal(audit.rawTextSha256, digest(original), `CA raw paragraph restoration differs: ${record.id}`);
    equal(audit.exactRestorationVerified, true, 'CA raw paragraph restoration was not verified');
    const sourceMarks = [], additions = [];
    for (const mark of audit.inlineMarks) {
      assert(['add', 'q', 'foreign'].includes(mark.kind), 'Unrecognized CA source markup');
      const first = mark.sourceTextStart, last = mark.sourceTextEnd;
      assert(Number.isInteger(first) && Number.isInteger(last) && first >= left && last > first
        && last <= characters.length - Array.from(audit.trailingWhitespace).length, 'CA source markup is outside the running text');
      const start = characters.slice(left, first).join('').length, end = characters.slice(left, last).join('').length;
      const converted = {kind: mark.kind, start, end, text: record.text.slice(start, end)};
      if (mark.kind === 'add') additions.push({...converted, sourceTag: 'add'});
      else sourceMarks.push({...converted, ...(mark.kind === 'foreign' ? {language: mark.language} : {})});
      if (mark.kind === 'foreign') equal(mark.language, 'grc', 'Unexpected language in CA foreign text');
      counts[mark.kind]++;
    }
    equal(record.editorialMarks, additions, `CA source addition differs: ${record.id}`);
    equal(record.sourceMarkup, sourceMarks, `CA quotation or foreign text differs: ${record.id}`);
    const gaps = Array.from(record.text.matchAll(/\*(?:\s*\*)*/gu), match => ({
      start: match.index, end: match.index + match[0].length, text: match[0], kind: 'literal-asterisks',
    }));
    equal(record.textGaps, gaps, `CA literal marker coverage differs: ${record.id}`);
    equal(record.phraseBreaks, gaps.map(gap => gap.start), `CA phrase boundaries differ: ${record.id}`);
    equal(audit.textGaps, gaps, 'CA source audit marker ranges differ');
    equal(audit.phraseBreaks, record.phraseBreaks, 'CA source audit phrase boundaries differ');
    const annotations = (audit.sourceAttributes.ana || '').split(/\s+/u).filter(Boolean);
    equal(record.sourceAnnotations || [], annotations, 'CA accepted source annotations differ');
    const breakBefore = spec.number === 1 && [119, 147].includes(index + 1);
    equal(annotations.includes('#niese-boundary-within-preceding-lacuna'), breakBefore, 'CA preceding-lacuna annotation differs');
    equal(Boolean(record.breakBefore), breakBefore, 'CA declared section boundary differs');
    counts.markers += gaps.length;
    counts.breakBefore += Number(breakBefore);
    displays.push(record.text); originals.push(original);
  }
  const text = displays.join(''), content = digest(text.replace(/\s/gu, ''));
  for (const key of ['sourceNonWhitespaceContentSha256', 'indexedNonWhitespaceContentSha256',
    'sourceProjectionNonWhitespaceContentSha256', 'displayNonWhitespaceContentSha256']) {
    equal(report.coverage[key], content, `CA original text coverage differs: ${key}`);
  }
  equal(report.coverage.rawParagraphSequenceSha256, digest(originals.join('\n')), 'CA raw source order differs');
  equal(report.coverage.displayTextSequenceSha256, digest(displays.join('\n')), 'CA display text order differs');
  equal(report.coverage.generatedDisplayGlyphs, 0, 'CA must not generate display characters');
  equal(report.coverage.sourceProjectionExactlyRestoresSource, true, 'CA source restoration is unverified');
  equal([counts.add, counts.q, counts.foreign, counts.markers, counts.breakBefore],
    [report.counts.addedSpans, report.counts.quotationSpans, report.counts.foreignSpans,
      report.counts.asteriskMarkerClusters, report.counts.breakBeforeUnits], 'CA markup and phrase-boundary totals differ');
}

const REGISTERED_BOOKS = {
  11: {last: 347, canonical: 347, spans: 352, inserts: 2, tokens: 11589, unavailable: [], fragmented: [72, 312, 326, 342], registry: 'b89420a9520192d592d9166eb5cc340b1d1dd13e68b7641514be6e9dd36fc309'},
  12: {last: 434, canonical: 433, spans: 433, inserts: 0, tokens: 13683, unavailable: [248], fragmented: [], registry: '6a181082bdebef79324aed4023ce532fc3086abbf1196a9a73a539ccb5a6d02a'},
  13: {last: 433, canonical: 431, spans: 431, inserts: 0, tokens: 13803, unavailable: [213, 216], fragmented: [], registry: '00601dd32d0cc836beb45129cdc507608ced05de305b6e4d46899571b515ead1'},
  14: {last: 491, canonical: 489, spans: 489, inserts: 0, tokens: 15148, unavailable: [238, 239], fragmented: [], registry: '99361742e1e0aa7fe77ee61b879b283a6ec30692fb006d953ee5700050ab06f9'},
  15: {last: 425, canonical: 423, spans: 423, inserts: 0, tokens: 12223, unavailable: [338, 347], fragmented: [], registry: 'b2c39132e1e6d24ee94eb23fcee549ab104e4f92b3f89e7aa972b22a3f453f35'},
  16: {last: 404, canonical: 380, spans: 383, inserts: 0, tokens: 10471, unavailable: [77, 123, ...sectionRange(189, 199), 359, ...sectionRange(395, 404)], fragmented: [294, 295, 351], registry: '4255de34279ae13ff2da174421db8f98a9fbac37e66cf53bd4728cf46ae6fbfb'},
  17: {last: 355, canonical: 355, spans: 355, inserts: 0, tokens: 15287, unavailable: [], fragmented: [], registry: '0613bbbd33166e805ca4f412f182b1ee9a5a166e1a302b3a9d011b44331a7a5f'},
  18: {last: 379, canonical: 377, spans: 377, inserts: 0, tokens: 15306, unavailable: [216, 217], fragmented: [], registry: 'fdc0324aed5d8309cae28178c945ec0b1ea406a54f8a4625355ac6c69ef1e501'},
  19: {last: 366, canonical: 366, spans: 366, inserts: 0, tokens: 11791, unavailable: [], fragmented: [], registry: '7404cee1c29f29f991da2d30553a5259a446d9f576286b69365a717fac32dcc9'},
  20: {last: 268, canonical: 257, spans: 257, inserts: 0, tokens: 7864, unavailable: [...sectionRange(27, 36), 238], fragmented: [], registry: '3542ef335653869483d9f62c41ce14687ab0845b47f5045eb428aef7b65094c3'},
};
const REGISTERED_COVERAGE_FIELDS = ['coverageMode', 'canonicalSections', 'citationUnits', 'primarySourceSpans',
  'interpolatedSourcePassages', 'fragmentedSections', 'unavailableSections', 'identityRegistry', 'additionalSources'];

/** Bind the new discontinuities and the one touching-word seam to their source evidence. */
function validateRegisteredBoundaryEvidence(corpus, report, spec, registry) {
  const xmlId = '{http://www.w3.org/XML/1998/namespace}id';
  const digest = text => sha256(Buffer.from(text));
  const primary = `assets/xml/antiquities/Latin/book-${spec.number}.xml`;
  const byId = new Map(corpus.map(record => [record.id, record]));
  const markers = report.paragraphs.flatMap(paragraph => (paragraph.structuralMarkers || [])
    .map(marker => ({sourceId: paragraph.sourceId, ...marker})));
  const sourceExclusions = report.excluded.filter(item =>
    ['excluded-source-gap-notation', 'excluded-lacuna-notice'].includes(item.kind));
  const gapKind = 'excluded-source-gap-notation';
  const expectedExclusions = spec.number === 16 ? [
    [gapKind, 'latin-book16-num188', 59, 64, '[...]', 'milestone', {[xmlId]: 'niese-latin-book16-end188', unit: 'niese-range-end', n: '188'}],
    [gapKind, 'latin-book16-num194', 0, 5, '[...]', 'p', {[xmlId]: 'latin-book16-num194'}],
    [gapKind, 'latin-book16-num395', 0, 5, '[...]', 'milestone', {[xmlId]: 'niese-latin-book16-end394', unit: 'niese-range-end', n: '394'}],
  ] : spec.number === 20 ? [
    ['excluded-lacuna-notice', 'latin-book20-num34', 0, 56,
      '[Niese sections 26–37 largely missing; cf. Blatt, p. 68]', 'anchor', {[xmlId]: 'niese-latin-book20-end26'}],
  ] : [];
  const exclusionTuple = item => [item.kind, item.sourceId, item.sourceTextStart,
    item.sourceTextEnd, item.text, item.sourceTag, item.sourceAttributes];
  equal(sourceExclusions.map(exclusionTuple), expectedExclusions, 'Antiquities delimited source exclusion inventory differs');
  const paragraphExclusions = report.paragraphs.flatMap(paragraph => paragraph.segments
    .filter(segment => [gapKind, 'excluded-lacuna-notice'].includes(segment.kind))
    .map(segment => ({sourceId: paragraph.sourceId, ...segment})));
  equal(paragraphExclusions.map(exclusionTuple), expectedExclusions, 'Antiquities exclusion restoration inventory differs');
  for (const exclusion of sourceExclusions) {
    equal(exclusion.textSha256, digest(exclusion.text), 'Antiquities source exclusion text differs');
    assert(exclusion.sourceXPath, 'Antiquities source exclusion locator is missing');
  }
  const expectedClosures = spec.number === 16 ? [
    [188, 'latin-book16-num188', 'niese-latin-book16-end188', 59, 58],
    [394, 'latin-book16-num395', 'niese-latin-book16-end394', 0, 236],
  ] : spec.number === 20 ? [[26, 'latin-book20-num34', 'niese-latin-book20-end26', 0, 43]] : [];
  if (spec.number >= 16) {
    const closures = markers.filter(marker => /-end\d+$/u.test(marker.sourceAttributes?.[xmlId] || ''));
    equal(closures.map(marker => [marker.section, marker.sourceId, marker.sourceAttributes[xmlId],
      marker.sourceTextOffset, marker.recordTextOffsetUTF16]), expectedClosures, 'Antiquities explicit closing anchor inventory differs');
    for (const marker of closures) {
      const record = byId.get(marker.recordId);
      assert(record && record.section === marker.section, 'Antiquities closing anchor has the wrong preceding record');
      equal(marker.recordTextOffsetUTF16, record.text.length, 'Antiquities closing anchor does not end its preceding record');
      equal(marker.recordTextOffset, Array.from(record.text).length, 'Antiquities closing anchor character offset differs');
      const entry = registry.sections.find(item => item.number === marker.section).Latin;
      equal(entry.endTarget ?? entry.spans?.at(-1)?.end?.target, marker.sourceAttributes[xmlId],
        'Antiquities closing anchor differs from the accepted registry');
    }
  }
  const expectedBoundary = spec.number === 16 ? [188, 200,
    'Literal [...] notation occurs after XVI.188 and before XVI.200 in the accepted transcription.'] :
    spec.number === 20 ? [26, 37,
      'The accepted XX.26 end anchor precedes an inherited missing-text annotation before XX.37.'] : null;
  const boundaryRecords = corpus.filter(record => record.sourceBoundaryEvidence);
  equal(boundaryRecords.length, expectedBoundary ? 1 : 0, 'Antiquities source-boundary evidence coverage differs');
  for (const record of corpus) {
    if (!record.sourceBoundaryEvidence) equal(record.breakReason, undefined, 'Unreviewed registered boundary explanation');
  }
  if (expectedBoundary) {
    const [preceding, following, reason] = expectedBoundary;
    const record = boundaryRecords[0], boundary = record.sourceBoundaryEvidence;
    equal([record.section, record.breakReason], [following, reason], 'Antiquities registered boundary explanation differs');
    equal([boundary.kind, boundary.sourcePath, boundary.precedingSection, boundary.followingSection],
      ['registered-source-discontinuity', primary, preceding, following], 'Antiquities source-boundary identity differs');
    equal(corpus[corpus.indexOf(record) - 1].section, preceding, 'Antiquities source-boundary predecessor differs');
    equal(boundary.qualification, 'This explicit source boundary blocks phrase adjacency; the cause and extent of absent Latin are not inferred.',
      'Antiquities source-boundary qualification differs');
    for (const [edge, section, closing] of [[boundary.precedingEnd, preceding, true], [boundary.followingStart, following, false]]) {
      const marker = markers.find(item => item.sourceId === edge.sourceId && item.sourceXPath === edge.sourceXPath);
      assert(marker, 'Antiquities source-boundary controlling marker is missing');
      equal(edge, {sourceId: marker.sourceId, sourceXPath: marker.sourceXPath, sourceTag: marker.kind,
        sourceAttributes: marker.sourceAttributes, sourceTextOffset: marker.sourceTextOffset}, 'Antiquities source-boundary marker evidence differs');
      equal(marker.section, section, 'Antiquities source-boundary marker owns the wrong section');
      equal(closing ? marker.sourceAttributes[xmlId] : marker.sourceAttributes.n,
        closing ? `niese-latin-book${spec.number}-end${section}` : String(section), 'Antiquities source-boundary marker identity differs');
    }
    equal(boundary.excludedSourceSpans, sourceExclusions.slice(0, spec.number === 16 ? 2 : 1),
      'Antiquities source-boundary excluded source evidence differs');
  }
  for (const coverage of [report.coverage, ...report.documentReports.map(document => document.coverage)]) {
    equal(coverage.explicitSourceBoundaries || [], boundaryRecords.map(record => record.sourceBoundaryEvidence),
      'Antiquities source-boundary coverage evidence differs');
    const tokenBoundaries = coverage.registeredTokenBoundaryEvidence || [];
    equal(tokenBoundaries.length, spec.number === 17 ? 1 : 0, 'Antiquities registered token-boundary inventory differs');
    if (spec.number === 17) {
      const seam = tokenBoundaries[0];
      equal(seam, {kind: 'registered-section-token-boundary', sourcePath: primary, sourceId: 'latin-book17-num32',
        sourceXPath: '/TEI[1]/text[1]/body[1]/div1[1]/div2[4]/p[1]/milestone[13]', sourceTag: 'milestone',
        sourceAttributes: {unit: 'niese', n: '42', [xmlId]: 'niese-latin-book17-42'},
        sourceTextOffset: 3308, flatTextOffset: 3308,
        precedingRecordId: 'antiquities-latin-bamberg78-17-41', followingRecordId: 'antiquities-latin-bamberg78-17-42',
        sourceText: 'eleuaticum', precedingText: 'eleuati', followingText: 'cum',
        qualification: 'The adopted Niese boundary separates two search tokens without inserting or changing a source character. Whole-book phrase adjacency remains available.'},
        'Antiquities accepted touching-word seam evidence differs');
      assert(byId.get(seam.precedingRecordId).text.endsWith('eleuati') && byId.get(seam.followingRecordId).text.startsWith('cum '),
        'Antiquities accepted touching-word seam text differs');
      equal(coverage.rawParagraphWordSequenceSha256, 'fa071c65ff0457d19cb3cd77fe06da544990f5964cd70ff0923b79ce30f94453',
        'Antiquities XVII raw paragraph word evidence differs');
      equal(coverage.registeredBoundaryWordSequenceSha256, coverage.sourceWordSequenceSha256,
        'Antiquities XVII adopted-boundary word evidence differs');
    }
    equal(coverage.sourceWordSequenceSha256, coverage.indexedWordSequenceSha256, 'Antiquities registered source words differ');
    equal(coverage.wordSequencePreserved, true, 'Antiquities registered source words are unverified');
    equal(coverage.nonWhitespaceContentPreserved, true, 'Antiquities registered source characters are unverified');
  }
}

/** XI–XX bind physical text spans to the accepted witness identity registries. */
function validateRegisteredAntiquities(corpus, report, manifest, spec, root) {
  const accepted = REGISTERED_BOOKS[spec.number];
  assert(accepted, 'Unreviewed registered Antiquities book');
  const roman = {11: 'XI', 12: 'XII', 13: 'XIII', 14: 'XIV', 15: 'XV',
    16: 'XVI', 17: 'XVII', 18: 'XVIII', 19: 'XIX', 20: 'XX'}[spec.number];
  const primary = `assets/xml/antiquities/Latin/book-${spec.number}.xml`;
  const registryPath = `assets/xml/antiquities/niese/book-${spec.number}.json`;
  equal(spec.coverageMode, 'registered-source-spans', 'Antiquities physical span coverage mode differs');
  equal([spec.source, spec.identityRegistry, spec.additionalSources], [primary, registryPath, [registryPath]], 'Antiquities registry input inventory differs');
  equal(spec.sectionRange, [1, accepted.last], 'Antiquities registered canonical range differs');
  equal([spec.sections, spec.canonicalSections, spec.citationUnits, spec.primarySourceSpans, spec.interpolatedSourcePassages],
    [accepted.spans + accepted.inserts, accepted.canonical, accepted.canonical + accepted.inserts, accepted.spans, accepted.inserts],
    'Antiquities physical/canonical coverage counts differ');
  equal(spec.unavailableSections, accepted.unavailable, 'Antiquities unavailable identity inventory differs');
  equal(spec.fragmentedSections, accepted.fragmented, 'Antiquities fragmented identity inventory differs');
  const registryBytes = lfBytes(fs.readFileSync(inside(root, registryPath)));
  equal(sha256(registryBytes), accepted.registry, 'Antiquities accepted identity registry changed');
  const registry = JSON.parse(registryBytes.toString('utf8'));
  equal(report.identityRegistry.path, registryPath, 'Antiquities registry fingerprint path differs');
  equal(checkIndexedXML(root, report.identityRegistry, 'Antiquities registry fingerprint').sha256, accepted.registry,
    'Antiquities normalized registry fingerprint differs');
  equal(report.additionalSources, [report.identityRegistry], 'Antiquities registry fingerprint inventory differs');
  const unavailable = registry.sections.filter(item => item.Latin?.available === false);
  equal(unavailable.map(item => item.number), accepted.unavailable, 'Registry unavailable identities differ');
  equal(report.coverage.unavailableSections, accepted.unavailable, 'Antiquities unavailable coverage differs');
  equal(report.coverage.unavailableIdentities, unavailable, 'Antiquities unavailable identity qualifications differ');
  equal(report.coverage.fragmentedSections, accepted.fragmented, 'Antiquities fragmented coverage differs');
  equal(report.coverage.physicalSourceOrderPreserved, true, 'Antiquities physical source order is unverified');
  equal(report.coverage.allowedEmptySections, [], 'Registered unavailable identities must not fabricate empty records');
  equal(report.coverage.generatedDisplayGlyphs, 0, 'Antiquities must not generate running text');
  equal(report.sectionAudits.length, corpus.length, 'Antiquities registered section audit is incomplete');
  const registryByNumber = new Map(registry.sections.map(item => [item.number, item]));
  const byId = new Map(corpus.map(record => [record.id, record]));
  const identities = new Map();
  const gapInventory = [];
  const digest = text => sha256(Buffer.from(text));
  for (let index = 0; index < corpus.length; index++) {
    const record = corpus[index], audit = report.sectionAudits[index];
    assert(record.text.length > 0, 'Registered available source spans must contain Latin text');
    equal(record.sourcePath, primary, 'Registered source record uses the wrong XML');
    equal(record.citationScheme, 'niese', 'Antiquities registered citation scheme differs');
    equal(record.chapter, undefined, 'A physical division cannot replace a canonical Niese identity');
    equal(record.citation, {book: roman, section: record.section}, 'Antiquities registered structured citation differs');
    const unitId = `${manifest.id}-${spec.number}-${record.section}`;
    equal(record.citationUnitId, unitId, 'Antiquities logical citation unit differs');
    if (!identities.has(record.section)) identities.set(record.section, []);
    identities.get(record.section).push(record);
    let readerSection = record.section, label = `${roman}.${record.section}`;
    if (record.sourcePassage) {
      const passage = registry.sourcePassages?.find(item => item.identity === record.section);
      assert(passage, 'Unreviewed Antiquities inserted source passage');
      equal(record.sourcePassage, passage, 'Antiquities inserted passage metadata differs from registry');
      equal(record.sourceOccurrence, passage.occurrence, 'Antiquities inserted occurrence differs');
      equal(record.id, unitId, 'Antiquities inserted stable record identity differs');
      equal([passage.AntiquitiesIdentity, passage.primaryAntiquitiesFragment], [false, false], 'An inserted Bellum passage cannot acquire an Antiquities identity');
      readerSection = passage.association;
      label = `${roman}, interpolated Bellum ${String(record.section).replace(/^BJ\./u, '')}`;
      equal(record.citationUnitCitation, label, 'Antiquities inserted unit citation differs');
    } else {
      const entry = registryByNumber.get(record.section);
      assert(entry?.Latin?.available === true, 'A record refers to unavailable or unregistered Latin');
      equal(record.citationUnitCitation, label, 'Antiquities canonical unit citation differs');
      const spans = (entry.Latin.spans || []).filter(span => span.role !== 'interpolation');
      if (spans.length > 1) {
        const occurrenceIndex = spans.findIndex(span => (span.occurrence ?? span.start?.target) === record.sourceOccurrence);
        assert(occurrenceIndex >= 0, 'Antiquities split occurrence is missing from registry');
        const occurrence = spans[occurrenceIndex];
        equal([record.continuationRank, record.fragmentCount], [occurrence.continuationRank ?? occurrenceIndex + 1, spans.length], 'Antiquities split portion metadata differs');
        equal(record.id, `${unitId}-${record.sourceOccurrence}`, 'Antiquities split stable record identity differs');
        label += ` (portion ${record.continuationRank} of ${record.fragmentCount})`;
      } else {
        equal(record.id, unitId, 'Antiquities stable canonical record identity differs');
        equal(record.fragmentCount, undefined, 'Unreviewed Antiquities split portion');
      }
    }
    equal(record.citationLabel, label, 'Antiquities registered display citation differs');
    equal(record.readerLink, {path: 'antiquities/', params: {book: spec.number, niese: readerSection}}, 'Antiquities registered reader route differs');
    equal(record.url, `/antiquities/?book=${spec.number}&niese=${readerSection}`, 'Antiquities registered reader URL differs');
    assert(Array.isArray(record.sourceIds) && record.sourceIds.length, 'Antiquities source locators are missing');
    equal(record.sourceId, record.sourceIds[0], 'Antiquities source locator order differs');
    equal(audit.recordId, record.id, 'Antiquities registered audit identity differs');
    equal(audit.sourceBoundaryEvidence, record.sourceBoundaryEvidence, 'Antiquities source-boundary audit differs');
    equal(audit.displayTextSha256, digest(record.text), 'Antiquities registered display text differs');
    for (const key of ['section', 'sourcePath', 'sourceIds', 'editorialMarks', 'sourceMarkup', 'textGaps', 'phraseBreaks', 'citationUnitId'])
      equal(audit[key], record[key], `Antiquities registered metadata differs: ${record.id}.${key}`);
    editorialMarksFor(record);
    for (const mark of record.editorialMarks) assert(['add', 'del', 'unclear'].includes(mark.kind) && mark.sourceTag === mark.kind && mark.sourceAttributes, 'Unreviewed Antiquities editorial mark');
    for (const mark of record.sourceMarkup) {
      assert(['s', 'ref', 'corr', 'expan'].includes(mark.kind) && mark.sourceTag === mark.kind && mark.sourceAttributes
        && Number.isInteger(mark.start) && Number.isInteger(mark.end) && mark.start >= 0 && mark.end > mark.start && mark.end <= record.text.length,
        'Invalid Antiquities transparent source markup');
      equal(record.text.slice(mark.start, mark.end), mark.text, 'Antiquities transparent source text differs');
    }
    for (const gap of record.textGaps) {
      assert(Number.isInteger(gap.start) && Number.isInteger(gap.end) && gap.start >= 0 && gap.end >= gap.start && gap.end <= record.text.length, 'Invalid Antiquities source gap offset');
      equal(record.text.slice(gap.start, gap.end), gap.text, 'Antiquities source gap text differs');
      if (gap.kind === 'tei-gap') {
        equal([gap.start, gap.end, gap.text], [gap.start, gap.start, ''], 'An encoded empty gap must not invent source text');
        gapInventory.push([record.section, gap.kind, gap.sourceAttributes?.reason]);
      } else {
        equal(gap.kind, 'literal-dots', 'Unreviewed registered Antiquities literal interruption');
        assert(/^\.(?:\s*\.)+$/u.test(gap.text), 'Antiquities dotted interruption contains running letters');
        const marking = spec.number === 20 ? 'unclear' : 'add';
        assert(record.editorialMarks.some(mark => mark.kind === marking && mark.start <= gap.start && mark.end >= gap.end
          && (spec.number !== 20 || mark.sourceAttributes?.reason === 'damage')), 'Antiquities dotted interruption lacks its accepted source marking');
        gapInventory.push([record.section, gap.kind]);
      }
    }
    equal(record.phraseBreaks, [...new Set(record.textGaps.map(gap => gap.start))].sort((a, b) => a - b), 'Antiquities registered phrase barriers differ');
    phraseBreakOffsets(record);
    const sourceBreak = (spec.number === 16 && record.section === 200) || (spec.number === 20 && record.section === 37);
    equal(Boolean(record.breakBefore), sourceBreak, 'Antiquities source discontinuity differs from the delimited interruption inventory');
    equal(audit.breakBefore, sourceBreak, 'Antiquities registered source boundary audit differs');
  }
  equal([...identities.keys()].filter(Number.isInteger).sort((a, b) => a - b), sectionRange(1, accepted.last).filter(number => !accepted.unavailable.includes(number)), 'Antiquities available canonical identity coverage differs');
  for (const [section, records] of identities) {
    const expected = (registryByNumber.get(section)?.Latin?.spans || []).filter(span => span.role !== 'interpolation');
    if (expected.length > 1) equal(sorted(records.map(record => record.sourceOccurrence)), sorted(expected.map(span => span.occurrence ?? span.start?.target)), 'Antiquities split occurrence coverage differs');
    else equal(records.length, 1, 'Antiquities source identity is duplicated');
  }
  equal(gapInventory, ({11: [], 12: [[8, 'tei-gap', 'hole'], [35, 'tei-gap', 'hole']], 13: [[393, 'tei-gap', 'fading']],
    14: [19, 28, 31, 35, 40, 45, 65, 68, 76, 78, 221, 439].map(section => [section, 'literal-dots']), 15: [],
    16: [[170, 'tei-gap', undefined]], 17: [], 18: [], 19: [], 20: [[263, 'literal-dots']]})[spec.number], 'Antiquities registered gap inventory differs');
  const firstOccurrences = new Set();
  let subscriptions = 0;
  const restored = report.paragraphs.map(paragraph => {
    let cursor = 0, text = '';
    for (const segment of paragraph.segments) {
      equal(segment.sourceTextStart, cursor, 'Antiquities registered paragraph restoration has a gap or overlap');
      let part;
      if (segment.kind === 'source-text') {
        const record = byId.get(segment.recordId);
        assert(record && record.section === segment.section && record.sourceIds.includes(paragraph.sourceId), 'Antiquities registered source slice belongs to the wrong occurrence');
        firstOccurrences.add(record.id);
        part = Array.from(record.text).slice(segment.recordTextStart, segment.recordTextEnd).join('');
        equal(digest(part), segment.textSha256, 'Antiquities registered source slice changed');
      } else {
        assert(['excluded-label', 'excluded-note', 'trimmed-edge-whitespace', 'excluded-chapter-annotation', 'excluded-book-subscription',
          'excluded-source-gap-notation', 'excluded-lacuna-notice'].includes(segment.kind), 'Unreviewed registered paragraph exclusion');
        part = segment.text;
        if (segment.kind === 'trimmed-edge-whitespace') assert(/^\s*$/u.test(part), 'Antiquities discarded source letters as whitespace');
        if (segment.kind === 'excluded-chapter-annotation') equal([spec.number, part], [15, 'I'], 'Unreviewed chapter annotation exclusion');
        if (segment.kind === 'excluded-book-subscription') {
          equal([spec.number, paragraph.sourceId, part, segment.sourceTag, segment.sourceAttributes?.unit],
            [12, 'latin-book12-num426', 'Flauii iosepp FLAUII IOSEPPI IUDAEICAE ANTIQUITATIS LIBER DUODECIMUS EXPLICIT', 'milestone', 'niese-end'],
            'Unreviewed closing subscription exclusion');
          subscriptions++;
        }
      }
      equal(Array.from(part).length, segment.sourceTextEnd - segment.sourceTextStart, 'Antiquities registered restored offset differs');
      text += part; cursor = segment.sourceTextEnd;
    }
    equal(cursor, paragraph.rawTextCharacters, 'Antiquities registered raw paragraph coverage differs');
    equal(digest(text), paragraph.rawTextSha256, 'Antiquities registered paragraph was not exactly restored');
    equal(paragraph.exactRestorationVerified, true, 'Antiquities registered paragraph restoration is unverified');
    return text;
  });
  equal([...firstOccurrences], corpus.map(record => record.id), 'Antiquities physical passage order differs from its source paragraphs');
  equal(subscriptions, spec.number === 12 ? 1 : 0, 'Antiquities closing subscription coverage differs');
  for (const coverage of [report.coverage, ...report.documentReports.map(document => document.coverage)]) {
    equal(coverage.rawParagraphSequenceSha256, digest(restored.join('\n')), 'Antiquities registered raw paragraph order differs');
    equal(coverage.restoredParagraphSequenceSha256, digest(restored.join('\n')), 'Antiquities registered restoration sequence differs');
    equal(coverage.displayTextSequenceSha256, digest(corpus.map(record => record.text).join('\n')), 'Antiquities registered physical text sequence differs');
    equal(coverage.sourceProjectionExactlyRestoresSource, true, 'Antiquities registered source projection is unverified');
  }
  equal(corpus.reduce((sum, record) => sum + tokenizeRecord(record).length, 0), accepted.tokens, 'Antiquities registered word count differs');
  validateRegisteredBoundaryEvidence(corpus, report, spec, registry);
}

/** Check the accepted Antiquities I–XX snapshot, including omissions and registered physical fragments. */
export function validateAntiquitiesSourceProjection(corpus, report, manifest, spec, root = fileURLToPath(new URL('../../', import.meta.url))) {
  equal(manifest.citationScheme, 'niese', 'Antiquities requires Niese citations');
  if (spec.number >= 11) return validateRegisteredAntiquities(corpus, report, manifest, spec, root);
  assert(sectionRange(1, 10).includes(spec.number), 'Unreviewed Antiquities book');
  const roman = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'][spec.number];
  const primary = `assets/xml/antiquities/Latin/book-${String(spec.number).padStart(2, '0')}.xml`;
  const additional = spec.number === 1 ? ['assets/xml/antiquities/Latin/preface.xml'] : [];
  const omissions = spec.number === 3 ? [240] : spec.number === 7 ? sectionRange(69, 99) : [];
  const intervals = spec.number === 10 ? [108] : [];
  const missing = spec.number === 9 ? sectionRange(51, 109) : [];
  equal(spec.missingSections || [], missing, 'Antiquities declared missing citations differ');
  equal(spec.omittedSections || [], spec.number === 7 ? omissions : [], 'Antiquities declared omissions differ');
  equal(spec.emptySections || [], intervals, 'Antiquities declared empty intervals differ');
  equal(report.coverage.missingSections, missing, 'Antiquities missing-citation evidence differs');
  equal(report.coverage.sourceOrderIsConsecutive, missing.length === 0, 'Antiquities citation continuity differs');
  if (spec.number > 5) {
    equal(report.coverage.omittedSections, omissions, 'Antiquities omission coverage differs');
    equal(report.coverage.emptySourceIntervals, intervals, 'Antiquities empty-interval coverage differs');
  }
  equal(spec.source, primary, 'Antiquities manifest has the wrong source');
  equal(spec.additionalSources || [], additional, 'Antiquities Proem inventory differs');
  equal(report.sources.map(source => source.path), [...additional, primary], 'Antiquities source reading order differs');
  equal(report.documentReports.map(document => document.source), report.sources, 'Antiquities document fingerprints differ');
  equal(report.sectionAudits.length, corpus.length, 'Antiquities section audit is incomplete');
  equal(report.paragraphs.length, report.counts.numberedParagraphs, 'Antiquities paragraph audit is incomplete');
  equal(report.coverage.generatedDisplayGlyphs, 0, 'Antiquities must not generate running text');
  equal(report.coverage.sourceProjectionExactlyRestoresSource, true, 'Antiquities restoration is unverified');
  const empty = corpus.filter(record => record.text === '').map(record => record.section);
  equal(empty, [...omissions, ...intervals], 'Unexpected empty Antiquities section');
  equal(report.coverage.allowedEmptySections, empty, 'Antiquities empty-section evidence differs');
  equal(report.coverage.allSectionTextsNonempty, empty.length === 0, 'Antiquities nonempty-text evidence is inaccurate');
  const bySection = new Map(corpus.map(record => [record.section, record]));
  const digest = text => sha256(Buffer.from(text));
  let sourceGaps = 0, omissionNotices = 0;
  const literalGaps = [];
  for (let index = 0; index < corpus.length; index++) {
    const record = corpus[index], audit = report.sectionAudits[index];
    const proem = spec.number === 1 && record.section <= 26, readerBook = proem ? 'preface' : spec.number;
    equal(record.id, `${manifest.id}-${spec.number}-${record.section}`, 'Antiquities stable citation identity differs');
    equal(record.citationScheme, 'niese', 'Antiquities citation scheme differs');
    equal(record.citationLabel, `${roman}.${record.section}`, 'Antiquities citation label differs');
    equal(record.citation, {book: roman, section: record.section, ...(proem ? {proem: true} : {})}, 'Antiquities structured citation differs');
    equal(record.chapter, undefined, 'A coarse medieval division cannot define a Niese section chapter');
    equal(record.division, proem ? 'proem' : undefined, 'Antiquities Proem identity differs');
    equal(record.sourcePath, proem ? additional[0] : primary, 'Antiquities record has the wrong XML document');
    equal(record.readerLink, {path: 'antiquities/', params: {book: readerBook, niese: record.section}}, 'Antiquities reader route differs');
    equal(record.url, `/antiquities/?book=${readerBook}&niese=${record.section}`, 'Antiquities reader URL differs');
    assert(Array.isArray(record.sourceIds) && record.sourceIds.length, 'Antiquities source paragraph identities are missing');
    equal(record.sourceId, record.sourceIds[0], 'Antiquities first source paragraph differs');
    equal(audit.recordId, record.id, 'Antiquities section audit has the wrong identity');
    equal(audit.displayTextSha256, digest(record.text), 'Antiquities display text differs from source audit');
    for (const key of ['section', 'sourcePath', 'sourceIds', 'editorialMarks', 'sourceMarkup', 'textGaps', 'phraseBreaks', 'emptySource'])
      equal(record[key], audit[key], `Antiquities source metadata differs: ${record.id}.${key}`);
    if (intervals.includes(record.section)) {
      equal(record.emptySource, {kind: 'empty-source-interval', sourcePath: primary, sourceId: 'latin-book10-num108',
        label: {sourceTag: 'num', sourceAttributes: {}, text: '[VII.iii.108]', sourceTextStart: 0, sourceTextEnd: 13},
        nextBoundary: {sourceTag: 'milestone', sourceAttributes: {unit: 'niese', n: '109'}, sourceTextOffset: 14},
        interveningText: ' '}, 'Antiquities empty interval has different source evidence');
      equal([record.text, record.textGaps, record.phraseBreaks], ['', [], []], 'An empty interval cannot invent Latin or an encoded gap');
    } else equal(record.emptySource, undefined, 'Unreviewed Antiquities empty source interval');
    editorialMarksFor(record);
    for (const mark of record.editorialMarks) {
      assert(['add', 'del', ...(spec.number > 5 ? ['unclear'] : [])].includes(mark.kind) && mark.sourceTag === mark.kind && mark.sourceAttributes,
        'Antiquities editorial source tag or attributes differ');
    }
    for (const mark of record.sourceMarkup) {
      assert(['ref', 's', ...(spec.number > 5 ? ['corr', 'expan'] : [])].includes(mark.kind) && mark.sourceTag === mark.kind && mark.sourceAttributes &&
        Number.isInteger(mark.start) && Number.isInteger(mark.end) && mark.start >= 0 && mark.end > mark.start && mark.end <= record.text.length,
        'Invalid Antiquities transparent source span');
      equal(record.text.slice(mark.start, mark.end), mark.text, 'Antiquities transparent source text differs');
    }
    for (const gap of record.textGaps) {
      if (gap.kind === 'tei-gap') {
        assert(omissions.includes(record.section) && record.text === '', 'Unexpected Antiquities encoded omission');
        equal(gap, {kind: 'tei-gap', start: 0, end: 0, text: '', sourceAttributes: {reason: 'omitted'}}, 'Antiquities omission metadata differs');
        sourceGaps++;
      } else {
        assert(['literal-dots', 'literal-ellipsis', 'source-marked-dots'].includes(gap.kind), 'Unreviewed Antiquities phrase gap');
        assert(Number.isInteger(gap.start) && Number.isInteger(gap.end) && gap.start >= 0 && gap.end > gap.start && gap.end <= record.text.length,
          'Invalid Antiquities dotted interruption offsets');
        equal(record.text.slice(gap.start, gap.end), gap.text, 'Antiquities dotted interruption differs');
        if (gap.kind === 'literal-ellipsis') equal(gap.text, '…', 'Antiquities ellipsis differs');
        else assert(/^\.(?:\s*\.)*$/u.test(gap.text), 'Antiquities gap contains non-dot running text');
        if (gap.kind === 'source-marked-dots') {
          equal([spec.number, record.section, gap.sourceTag, gap.sourceAttributes],
            [10, 154, 'del', {hand: '?', rend: 'scraping'}], 'Unreviewed Antiquities source-marked interruption');
          assert(record.editorialMarks.some(mark => mark.kind === 'del' && mark.start === gap.start && mark.end === gap.end &&
            mark.text === gap.text && JSON.stringify(mark.sourceAttributes) === JSON.stringify(gap.sourceAttributes)),
          'Antiquities scraped interruption has no corresponding source span');
        } else {
          equal(gap.sourceTag, undefined, 'A literal Antiquities gap cannot invent a source tag');
          equal(gap.sourceAttributes, undefined, 'A literal Antiquities gap cannot invent source attributes');
        }
        literalGaps.push([record.section, gap.kind]);
      }
    }
    equal(record.phraseBreaks, [...new Set(record.textGaps.map(gap => gap.start))].sort((a, b) => a - b), 'Antiquities phrase barriers differ');
    phraseBreakOffsets(record);
    const breakBefore = (spec.number === 1 && record.section === 27) || (spec.number === 3 && [240, 241].includes(record.section)) ||
      (spec.number === 7 && record.section >= 69 && record.section <= 100) ||
      (spec.number === 9 && record.section === 110) || (spec.number === 10 && [108, 109].includes(record.section));
    equal(Boolean(record.breakBefore), breakBefore, 'Antiquities composition or omission boundary differs');
    equal(audit.breakBefore, breakBefore, 'Antiquities source boundary audit differs');
  }
  equal(literalGaps, ({1: [[34, 'literal-dots'], [53, 'literal-dots']], 2: [[80, 'literal-dots'], [93, 'literal-dots']],
    3: [], 4: [[84, 'literal-dots'], [84, 'literal-dots']], 5: [], 6: [],
    7: [[68, 'literal-ellipsis'], [140, 'literal-ellipsis'], [141, 'literal-ellipsis'], [378, 'literal-dots']],
    8: [[54, 'literal-ellipsis']], 9: [[110, 'literal-ellipsis']],
    10: [[154, 'source-marked-dots'], [154, 'source-marked-dots']]})[spec.number], 'Antiquities phrase-gap inventory differs');
  equal(sourceGaps, omissions.length, 'Antiquities encoded omission count differs');
  for (const document of report.documentReports) {
    const paragraphs = report.paragraphs.filter(paragraph => paragraph.sourcePath === document.source.path);
    const records = corpus.filter(record => record.sourcePath === document.source.path);
    equal(paragraphs.length, document.counts.numberedParagraphs, 'Antiquities source document paragraph count differs');
    equal(records.length, document.counts.sections, 'Antiquities source document section count differs');
    const restored = paragraphs.map(paragraph => {
      let cursor = 0, text = '';
      for (const segment of paragraph.segments) {
        equal(segment.sourceTextStart, cursor, 'Antiquities paragraph restoration has a gap or overlap');
        let part;
        if (segment.kind === 'source-text') {
          const record = bySection.get(segment.section);
          assert(record && record.sourcePath === paragraph.sourcePath && record.sourceIds.includes(paragraph.sourceId), 'Antiquities restored segment has the wrong source paragraph');
          part = Array.from(record.text).slice(segment.recordTextStart, segment.recordTextEnd).join('');
          equal(digest(part), segment.textSha256, 'Antiquities restored running text differs');
        } else {
          assert(['excluded-label', 'excluded-note', 'trimmed-edge-whitespace', 'excluded-omission-notice'].includes(segment.kind), 'Unreviewed Antiquities restoration segment');
          part = segment.text;
          if (segment.kind === 'trimmed-edge-whitespace') assert(/^\s*$/u.test(part), 'Antiquities trimmed source letters');
          if (segment.kind === 'excluded-omission-notice') {
            equal([spec.number, part, segment.sourceTag, segment.sourceAttributes], [7, ' Omitted in Bamberg MS', '#text', {}],
              'Antiquities omission notice exclusion differs');
            omissionNotices++;
          }
        }
        equal(Array.from(part).length, segment.sourceTextEnd - segment.sourceTextStart, 'Antiquities restored source offset differs');
        text += part; cursor = segment.sourceTextEnd;
      }
      equal(cursor, paragraph.rawTextCharacters, 'Antiquities raw paragraph coverage differs');
      equal(digest(text), paragraph.rawTextSha256, 'Antiquities raw paragraph is not exactly restored');
      equal(paragraph.exactRestorationVerified, true, 'Antiquities paragraph restoration was not verified');
      return text;
    });
    const coverage = document.coverage;
    equal(coverage.missingSections, missing, 'Antiquities source document missing citations differ');
    equal(coverage.sourceOrderIsConsecutive, missing.length === 0, 'Antiquities source document citation continuity differs');
    const lacunaNotices = document.excluded.filter(item => item.kind === 'lacuna-notice');
    equal(lacunaNotices, spec.number === 9 ? [{kind: 'lacuna-notice', sourceId: 'latin-book09-num51',
      sourceAttributes: {'{http://www.w3.org/XML/1998/namespace}id': 'latin-book09-num51'},
      text: '[Lacuna 51–109; cf. Blatt, p. 67]', textSha256: digest('[Lacuna 51–109; cf. Blatt, p. 67]'), missingSections: missing}] : [],
    'Antiquities excluded lacuna notice differs');
    for (const key of ['wordSequencePreserved', 'nonWhitespaceContentPreserved', 'sourceProjectionExactlyRestoresSource'])
      equal(coverage[key], true, `Antiquities document coverage failed: ${key}`);
    equal(coverage.paragraphsExactlyRestored, paragraphs.length, 'Antiquities document restoration count differs');
    for (const key of ['rawParagraphSequenceSha256', 'restoredParagraphSequenceSha256'])
      equal(coverage[key], digest(restored.join('\n')), 'Antiquities raw source order differs');
    const displays = records.map(record => record.text), content = digest(displays.join('').replace(/\s/gu, ''));
    for (const key of ['sourceNonWhitespaceContentSha256', 'indexedNonWhitespaceContentSha256', 'sourceProjectionNonWhitespaceContentSha256', 'displayNonWhitespaceContentSha256'])
      equal(coverage[key], content, `Antiquities running text coverage differs: ${key}`);
    const words = displays.flatMap(text => Array.from(text.matchAll(/[\p{L}\p{N}][\p{L}\p{M}\p{N}]*/gu), match => match[0]));
    for (const key of ['sourceWordSequenceSha256', 'indexedWordSequenceSha256']) equal(coverage[key], digest(words.join('\n')), 'Antiquities source word sequence differs');
    equal(words.length, document.counts.runningWordTokens, 'Antiquities document word count differs');
    equal(coverage.displayTextSequenceSha256, digest(displays.join('\n')), 'Antiquities display order differs');
  }
  equal(omissionNotices, spec.number === 7 ? 6 : 0, 'Antiquities omission notice count differs');
}

const extractedSources = book => [book.source, ...(book.additionalSources || [])];

/** Validate the generated index against current configs, XML, corpora, and extraction evidence. */
export function validateSearchSources(root, {qa = true} = {}) {
  const context = loadPublicationConfig(root), {base, config, collections} = context;
  const artifacts = new Map();
  function artifact(relative, expectedHash, role = 'evidence') {
    const filename = inside(base, relative), normalized = posix(path.relative(base, filename));
    const item = evidence(root, `${SOURCE_DIRECTORY}/${normalized}`);
    if (expectedHash !== undefined) equal(item.sha256, expectedHash, `Stale source artifact: ${normalized}`);
    const existing = artifacts.get(normalized);
    if (existing) equal(existing.sha256, item.sha256, `Conflicting export: ${normalized}`);
    else artifacts.set(normalized, {path: normalized, source: item.path, sha256: item.sha256, bytes: item.bytes, role});
    return {item, value: () => readJSON(base, normalized), relative: normalized};
  }
  for (const relative of config.runtime) artifact(relative, undefined, 'runtime');
  artifact('config/publication.json');
  const provenance = readJSON(base, 'vendor/provenance.json');
  for (const [filename, hash] of Object.entries(provenance.files)) artifact(`vendor/${filename}`, hash, 'runtime');
  const catalogArtifact = artifact(config.catalog, undefined, 'catalog');
  const catalog = catalogArtifact.value();
  equal(catalog.schemaVersion, 2, 'Rebuild the search catalog with schema 2');
  assert(Array.isArray(catalog.collections) && Array.isArray(catalog.books), 'Invalid search catalog');
  equal(catalog.source.manifestPath, config.registry, 'Catalog uses a different registry');
  artifact(catalog.source.manifestPath, catalog.source.manifestSHA256);
  artifact(catalog.source.enginePath, catalog.source.engineSHA256, 'runtime');
  artifact(catalog.source.lunrPath, catalog.source.lunrSHA256, 'runtime');
  equal(catalog.source.lunrVersion, provenance.version, 'Lunr provenance version differs');
  equal(catalog.collections.map(c => c.id), collections.map(c => c.manifest.id), 'Catalog collection order differs from registry');
  const allIds = new Set(), sources = [], audits = [], expectedBookIds = [];
  const totals = {books: 0, sections: 0, tokens: 0, bytes: 0};
  for (const configured of collections) {
    const {manifest, manifestPath, adapter} = configured;
    const collection = catalog.collections.find(c => c.id === manifest.id);
    equal(collection.manifestPath, manifestPath, `Wrong collection manifest: ${manifest.id}`);
    artifact(manifestPath, collection.manifestSHA256);
    const configuredPath = relative => posix(path.relative(base, path.resolve(path.dirname(inside(base, manifestPath)), relative)));
    equal(collection.corpusPath, configuredPath(manifest.corpus), `Wrong combined corpus: ${manifest.id}`);
    equal(collection.extractionReportPath, configuredPath(manifest.extractionReport), `Wrong extraction report: ${manifest.id}`);
    const combined = artifact(collection.corpusPath, collection.corpusSHA256).value();
    const report = artifact(collection.extractionReportPath, collection.extractionReportSHA256).value();
    assert(Array.isArray(combined), `Corpus must be a record array: ${manifest.id}`);
    equal(report.status, 'PASS', `Extraction did not pass: ${manifest.id}`);
    equal(report.corpus.sha256, collection.corpusSHA256, 'Extraction report describes a different corpus');
    equal(report.counts.books, manifest.books.length, 'Extraction book count differs from collection');
    equal(report.coverage.paragraphsExactlyRestored, report.counts.narrativeParagraphs ?? report.counts.numberedParagraphs, 'Incomplete paragraph restoration');
    for (const key of ['wordSequencePreserved', 'nonWhitespaceContentPreserved', 'globalIdsUnique', 'globalOrderIsConsecutive'])
      equal(report.coverage[key], true, `Extraction coverage failed: ${key}`);
    if (manifest.id === 'antiquities-latin-bamberg78') {
      const emptySections = [{book: 3, section: 240}, ...sectionRange(69, 99).map(section => ({book: 7, section})), {book: 10, section: 108}];
      equal(report.coverage.allSectionTextsNonempty, false, 'Antiquities must report its empty intervals accurately');
      equal(report.coverage.allowedEmptySections, emptySections, 'Unreviewed empty Antiquities citation');
      equal(report.coverage.missingSectionsByBook, {'9': sectionRange(51, 109), ...Object.fromEntries(Object.entries(REGISTERED_BOOKS)
        .filter(([, book]) => book.unavailable.length).map(([number, book]) => [number, book.unavailable]))}, 'Antiquities missing-citation summary differs');
      equal(combined.filter(record => record.text === '').map(record => ({book: record.book, section: record.section})),
        emptySections, 'Unexpected missing Antiquities running text');
    } else equal(report.coverage.allSectionTextsNonempty, true, 'Extraction coverage failed: allSectionTextsNonempty');
    for (const key of ['id', 'work', 'label', 'citationPrefix', 'language', 'edition', 'readerPath'])
      equal(collection[key], manifest[key], `Catalog metadata differs: ${manifest.id}.${key}`);
    for (const key of ['citationScheme', 'unitLabel', 'unitLabelPlural'])
      equal(collection[key], manifest[key], `Catalog citation metadata differs: ${manifest.id}.${key}`);
    equal(collection.books, manifest.books.map(book => `${manifest.id}:${book.number}`), 'Collection book identities differ');
    equal(report.books.map(book => book.book), manifest.books.map(book => book.number), 'Extraction book order differs');
    equal(sorted(report.books.flatMap(book => extractedSources(book).map(source => source.path))), sorted(adapter.sources),
      `Extracted XML differs from the approved source list: ${manifest.id}`);
    const collectionTotals = {books: 0, sections: 0, tokens: 0, bytes: 0};
    let order = 0;
    for (const spec of manifest.books) {
      const id = `${manifest.id}:${spec.number}`;
      expectedBookIds.push(id);
      const book = catalog.books.find(candidate => candidate.id === id);
      assert(book, `Catalog omits ${id}`);
      equal(book.collectionId, manifest.id, `Wrong book collection: ${id}`);
      equal(book.number, spec.number, `Wrong book number: ${id}`);
      equal(book.label, spec.label, `Wrong book label: ${id}`);
      const hasCoverageMetadata = ['missingSections', 'omittedSections', 'emptySections', 'coverageMode'].some(field => spec[field] !== undefined);
      equal(book.sectionRange, hasCoverageMetadata ? spec.sectionRange : undefined, `Catalog coverage differs: ${id}.sectionRange`);
      for (const field of ['missingSections', 'omittedSections', 'emptySections', ...REGISTERED_COVERAGE_FIELDS])
        equal(book[field], spec[field], `Catalog coverage differs: ${id}.${field}`);
      equal(book.corpusPath, configuredPath(spec.corpus), `Wrong book corpus: ${id}`);
      const corpus = artifact(book.corpusPath, book.corpusSHA256).value();
      const extracted = report.books.find(candidate => candidate.book === spec.number);
      equal(extracted.corpus.path, book.corpusPath, 'Extraction corpus path differs');
      equal(extracted.corpus.sha256, book.corpusSHA256, 'Extraction corpus hash differs');
      equal(extracted.corpus.records, corpus.length, 'Extraction record count differs');
      const bookReportArtifact = artifact(extracted.extractionReport.path, extracted.extractionReport.sha256);
      equal(bookReportArtifact.item.bytes, extracted.extractionReport.bytes, 'Extraction report size differs');
      const bookReport = bookReportArtifact.value();
      equal(bookReport.status, 'PASS', `Book extraction failed: ${id}`);
      equal(bookReport.source, extracted.source, 'Combined and per-book source fingerprints differ');
      equal(bookReport.additionalSources || [], extracted.additionalSources || [], 'Combined and per-book additional source fingerprints differ');
      equal((extracted.additionalSources || []).map(source => source.path), spec.additionalSources || [], 'Additional XML differs from the collection manifest');
      for (const source of extractedSources(extracted)) sources.push(checkIndexedXML(root, source, `${id} XML`));
      equal(bookReport.coverage.paragraphsExactlyRestored, bookReport.counts.narrativeParagraphs ?? bookReport.counts.numberedParagraphs, 'Book has incomplete paragraph restoration');
      if (manifest.id !== 'antiquities-latin-bamberg78') for (const [a, b] of [['rawParagraphSequenceSha256', 'restoredParagraphSequenceSha256'],
        ['sourceWordSequenceSha256', 'indexedWordSequenceSha256'],
        ['sourceNonWhitespaceContentSha256', 'indexedNonWhitespaceContentSha256']])
        equal(bookReport.coverage[a], bookReport.coverage[b], `Source coverage differs: ${id}.${a}`);
      equal(bookReport.coverage.missingSections, spec.unavailableSections || spec.missingSections || [], `${id}: missingSections`);
      for (const key of ['unexpectedSections', 'duplicateSections']) equal(bookReport.coverage[key], [], `${id}: ${key}`);
      equal(bookReport.coverage.completeRange, spec.sectionRange, `Section range differs: ${id}`);
      equal(corpus.length, spec.sections, `Corpus section count differs: ${id}`);
      if (manifest.id === 'deh-latin-ussani') validateDehSourceProjection(corpus, bookReport, manifest, spec);
      if (manifest.id === 'contra-apionem-latin-boysen') validateCaSourceProjection(corpus, bookReport, manifest, spec);
      if (manifest.id === 'antiquities-latin-bamberg78') validateAntiquitiesSourceProjection(corpus, bookReport, manifest, spec, root);
      if (manifest.id === 'antiquities-english-whiston') validateWhistonSourceProjection(corpus, bookReport, manifest, spec, root);
      if (manifest.id === 'bellum-english-whiston') validateWhistonBellumSourceProjection(corpus, bookReport, manifest, spec, root);
      const bundleArtifact = artifact(book.path, book.sha256, 'bundle');
      equal(bundleArtifact.item.bytes, book.bytes, `Bundle byte count differs: ${id}`);
      const bundle = bundleArtifact.value();
      equal(bundle.schemaVersion, catalog.engineSchemaVersion, `Bundle schema differs: ${id}`);
      equal(bundle.source.corpusSHA256, book.corpusSHA256, `Bundle uses stale corpus: ${id}`);
      equal(bundle.source.lunrVersion, catalog.source.lunrVersion, `Bundle Lunr version differs: ${id}`);
      equal(bundle.records.length, corpus.length, `Bundle record count differs: ${id}`);
      equal(bundle.stats.records, book.sections, `Catalog section count differs: ${id}`);
      equal(bundle.stats.tokens, book.tokens, `Catalog token count differs: ${id}`);
      equal(bundle.stats.vocabulary, book.vocabulary, `Catalog vocabulary count differs: ${id}`);
      equal(book.tokens, bookReport.counts.runningWordTokens, `Extracted word count differs: ${id}`);
      const acceptedSections = spec.sectionRange && spec.coverageMode !== 'registered-source-spans'
        ? sectionRange(...spec.sectionRange).filter(section => !(spec.missingSections || []).includes(section)) : null;
      if (acceptedSections) equal(acceptedSections.length, corpus.length, `Accepted section range differs: ${id}`);
      // Whiston's range defines citation identities, not a sortable narrative.
      // Its source projection above pins every section's actual physical order,
      // including XI's displaced sequence. Keep the complete identity check here.
      const sourceOrderedWhiston = manifest.id === 'antiquities-english-whiston';
      if (acceptedSections && sourceOrderedWhiston)
        equal(corpus.map(record => record.section).sort((a, b) => a - b), acceptedSections,
          `Accepted section identities differ: ${id}`);
      for (let index = 0; index < corpus.length; index++, order++) {
        const record = corpus[index], indexed = bundle.records[index];
        for (const [key, value] of Object.entries(record)) equal(indexed[key], value, `Bundle record differs: ${record.id}.${key}`);
        equal(record, combined[order], `Combined corpus differs at ${record.id}`);
        equal(record.order, order, `Corpus order differs at ${record.id}`);
        equal(record.book, spec.number, `Corpus book differs at ${record.id}`);
        for (const key of ['work', 'language', 'edition']) equal(record[key], manifest[key], `Wrong version at ${record.id}`);
        if (acceptedSections && !sourceOrderedWhiston) equal(record.section, acceptedSections[index], `Section order differs at ${record.id}`);
        assert(!allIds.has(record.id), `Duplicate passage ID: ${record.id}`);
        allIds.add(record.id);
      }
      collectionTotals.books++;
      for (const key of ['sections', 'tokens', 'bytes']) collectionTotals[key] += book[key];
    }
    equal(combined.length, order, `Combined corpus has unconfigured records: ${manifest.id}`);
    equal(report.counts.sections, order, 'Extraction section total differs');
    equal(collection.totals, collectionTotals, `Collection totals differ: ${manifest.id}`);
    for (const key of Object.keys(totals)) totals[key] += collectionTotals[key];
    let qaSummary;
    if (qa) {
      qaSummary = validateQaReport(root, {catalog, collection, configured, report});
      artifact(adapter.qaReport, qaSummary.sha256);
    }
    audits.push({id: manifest.id, totals: collectionTotals,
      extractionReport: {path: collection.extractionReportPath, sha256: collection.extractionReportSHA256},
      sourceFiles: report.books.flatMap(book => extractedSources(book).map(source => source.path)), ...(qaSummary ? {qa: qaSummary} : {})});
  }
  equal(catalog.books.map(book => book.id), expectedBookIds, 'Catalog contains missing, extra, or reordered books');
  equal(catalog.totals, totals, 'Catalog totals differ');
  equal(new Set(sources.map(source => source.path)).size, sources.length, 'A source XML is repeated across collections');
  return {...context, catalog, totals, sources, audits, artifacts: [...artifacts.values()].sort((a, b) => a.path.localeCompare(b.path, 'en'))};
}

export function validateQaReport(root, {catalog, collection, configured, report}) {
  const {manifest, adapter} = configured;
  const base = inside(root, SOURCE_DIRECTORY, {directory: true});
  const qa = readJSON(base, adapter.qaReport);
  equal(qa.status, 'PASS', `Independent QA did not pass: ${manifest.id}`);
  equal(qa.failedAssertions, 0, 'Independent QA has failed assertions');
  assert(qa.assertions > 0 && qa.totalQueries > 0, 'Independent QA has no recorded checks');
  equal(qa.source.books, collection.totals.books, 'Independent QA book total differs');
  equal(qa.source.sections, collection.totals.sections, 'Independent QA section total differs');
  equal(qa.source.tokens, collection.totals.tokens, 'Independent QA token total differs');
  const expected = {corpus: collection.corpusPath, catalog: 'catalog.json', engine: catalog.source.enginePath,
    collection: 'collection.mjs', verifier: adapter.verifier};
  if (manifest.id === 'contra-apionem-latin-boysen') expected.witness = 'tests/ca-source-witness.py';
  if (manifest.id === 'antiquities-latin-bamberg78') expected.witness = 'tests/antiquities-source-witness.py';
  if (manifest.id === 'antiquities-english-whiston') Object.assign(expected, {
    witness: 'tests/whiston-source-witness.py', concordance: 'concordance.mjs', uiUtils: 'ui-utils.mjs',
    extractor: adapter.extractor, manifest: configured.manifestPath,
  });
  if (manifest.id === 'bellum-english-whiston') Object.assign(expected, {
    witness: 'tests/whiston-bellum-source-witness.py', concordance: 'concordance.mjs', uiUtils: 'ui-utils.mjs',
    extractor: adapter.extractor, manifest: configured.manifestPath,
  });
  for (const [key, relative] of Object.entries(expected)) {
    equal(qa.verifiedFiles?.[key]?.path, `${SOURCE_DIRECTORY}/${relative}`, `Independent QA omits current ${key}`);
    checkEvidence(root, qa.verifiedFiles[key], `independent QA ${key}`);
  }
  equal((qa.verifiedFiles.testSources || []).map(item => item.path), adapter.testSources || [],
    'Independent QA omits its configured test-only sources');
  for (const item of qa.verifiedFiles.testSources || []) checkIndexedXML(root, item, 'test-only QA XML');
  // Reader preservation belongs to the historical QA run, not to future search index freshness.
  equal(qa.readerBaseline?.publicationInput, false, 'QA must distinguish historical reader evidence from search inputs');
  equal(qa.verifiedFiles.books?.map(book => book.book), manifest.books.map(book => book.number), 'Independent QA book set differs');
  for (const verified of qa.verifiedFiles.books) {
    const book = catalog.books.find(book => book.id === `${manifest.id}:${verified.book}`);
    const extracted = report.books.find(book => book.book === verified.book);
    for (const [key, expectedPath] of [['bundle', `${SOURCE_DIRECTORY}/${book.path}`],
      ['corpus', `${SOURCE_DIRECTORY}/${book.corpusPath}`], ['source', extracted.source.path]]) {
      equal(verified[key]?.path, expectedPath, `Independent QA uses wrong ${key} for ${book.id}`);
      if (key === 'source') checkIndexedXML(root, verified[key], `independent QA ${key}`);
      else checkEvidence(root, verified[key], `independent QA ${key}`);
    }
    equal((verified.additionalSources || []).map(source => source.path), (extracted.additionalSources || []).map(source => source.path),
      `Independent QA omits an additional source for ${book.id}`);
    for (const source of verified.additionalSources || []) checkIndexedXML(root, source, 'independent QA additional source');
  }
  const item = evidence(root, `${SOURCE_DIRECTORY}/${adapter.qaReport}`);
  return {path: adapter.qaReport, sha256: item.sha256, status: 'PASS',
    assertions: qa.assertions, queries: qa.totalQueries, failedAssertions: 0,
    readerEvidenceIsHistorical: true};
}

export function publicationPlan(root) {
  const validated = validateSearchSources(root);
  const browser = planBrowserRelease(root);
  const artifacts = [...validated.artifacts, ...browser.artifacts].sort((a, b) => a.path.localeCompare(b.path, 'en'));
  equal(new Set(artifacts.map(item => item.path)).size, artifacts.length, 'Browser and canonical exports collide');
  assert(validated.config.runtime.includes(BROWSER_LAUNCHER_NAME), 'The versioned browser launcher is not an approved runtime');
  const manifest = {
    schemaVersion: 1, status: 'PASS',
    generatedBy: `${SOURCE_DIRECTORY}/build-search.mjs`,
    sourceDirectory: SOURCE_DIRECTORY, assetDirectory: ASSET_DIRECTORY,
    catalog: validated.config.catalog,
    inputs: sourceInputs(root, validated.sources.map(source => source.path)),
    collections: validated.audits, totals: validated.totals,
    validation: {sourceAndArtifactHashes: 'PASS', extractionCoverage: 'PASS', independentCorpusQA: 'PASS',
      xmlCheckoutComparison: 'CRLF-to-LF only; extraction and QA reports retain exact indexed-source hashes',
      unitTests: {status: 'PASS', commands: unitTestCommands(root)},
      readerHashIsPublicationInput: false},
    browserRelease: browser.descriptor,
    artifacts,
  };
  return {...validated, manifest, bytes: jsonBytes(manifest), artifacts, generatedContents: browser.contents};
}

/** Export audited sources and deterministic browser projections; delete only previously owned obsolete files. */
export function exportSearchAssets(root, plan = publicationPlan(root)) {
  const output = inside(root, ASSET_DIRECTORY, {directory: true, exists: false});
  fs.mkdirSync(output, {recursive: true});
  inside(root, ASSET_DIRECTORY, {directory: true});
  const previousPath = path.join(output, MANIFEST_NAME);
  const previous = fs.existsSync(previousPath) ? readJSON(output, MANIFEST_NAME) : null;
  if (previous) equal(previous.schemaVersion, 1, 'Unrecognized existing publication manifest');
  const oldOwned = new Set([MANIFEST_NAME, ...(previous?.artifacts || []).map(item => item.path)]);
  const newOwned = new Set([MANIFEST_NAME, ...plan.artifacts.map(item => item.path)]);
  for (const relative of listing(output)) {
    assert(oldOwned.has(relative) || (newOwned.has(relative) && !previous),
      `Unmanaged file in ${ASSET_DIRECTORY}; review it before exporting: ${relative}`);
  }
  for (const item of plan.artifacts) {
    const source = fs.readFileSync(inside(root, item.source));
    equal(sha256(source), item.generated ? item.sourceSHA256 : item.sha256, `Source changed during export: ${item.source}`);
    const bytes = item.generated ? plan.generatedContents.get(item.path) : source;
    assert(Buffer.isBuffer(bytes), `Missing generated browser output: ${item.path}`);
    equal(sha256(bytes), item.sha256, `Generated browser output changed: ${item.path}`);
    equal(bytes.length, item.bytes, `Generated browser output has the wrong length: ${item.path}`);
    const target = inside(output, item.path, {exists: false});
    fs.mkdirSync(path.dirname(target), {recursive: true});
    fs.writeFileSync(target, bytes);
  }
  for (const obsolete of oldOwned) {
    if (newOwned.has(obsolete)) continue;
    const filename = inside(output, obsolete, {exists: false});
    if (fs.existsSync(filename)) fs.unlinkSync(inside(output, obsolete));
  }
  fs.writeFileSync(previousPath, plan.bytes);
  return verifySearchAssets(root);
}

/** Read-only gate used before Jekyll and after it, including established reader publication. */
export function verifySearchAssets(root, {site} = {}) {
  const plan = publicationPlan(root);
  const output = inside(root, ASSET_DIRECTORY, {directory: true});
  equal(fs.readFileSync(inside(output, MANIFEST_NAME)), plan.bytes,
    'Search export is stale. Run node bin/search/build-search.mjs and commit its generated assets.');
  const expectedFiles = sorted([MANIFEST_NAME, ...plan.artifacts.map(item => item.path)]);
  equal(sorted(listing(output)), expectedFiles, 'Search export inventory has missing or extra files');
  for (const item of plan.artifacts) checkEvidence(output, item, 'exported search asset');
  const result = {status: 'PASS', assets: plan.artifacts.length + 1, ...plan.totals,
    sourceFiles: plan.sources.length, publicationManifestSHA256: sha256(plan.bytes),
    sourceXML: plan.sources.map(item => ({path: item.path, indexedSHA256: item.indexedSHA256,
      worktreeSHA256: evidence(root, item.path).sha256, normalizedSHA256: item.sha256, hashMode: item.hashMode}))};
  if (site) {
    const destination = path.resolve(site);
    assert(destination !== path.resolve(root) && !path.resolve(root).startsWith(destination + path.sep),
      'Generated site must be separate from repository sources');
    const siteAssets = inside(destination, ASSET_DIRECTORY, {directory: true});
    equal(sorted(listing(siteAssets)), expectedFiles, 'Generated search inventory differs from approved export');
    equal(fs.readFileSync(inside(siteAssets, MANIFEST_NAME)), plan.bytes, 'Generated publication manifest differs');
    for (const item of plan.artifacts) checkEvidence(siteAssets, item, 'generated search asset');
    const representations = [];
    for (const item of plan.sources) {
      const source = fs.readFileSync(inside(root, item.path));
      const generated = fs.readFileSync(inside(destination, item.path));
      // The established reader publication may restore approved CRLF bytes. No words or punctuation may change.
      equal(generated.toString('latin1').replace(/\r\n/gu, '\n'), source.toString('latin1').replace(/\r\n/gu, '\n'),
        `Generated indexed XML text differs: ${item.path}`);
      representations.push({path: item.path, sourceSHA256: sha256(source), generatedSHA256: sha256(generated),
        lineEndingRepresentationOnly: !source.equals(generated)});
    }
    const html = fs.readFileSync(inside(destination, 'search/index.html'), 'utf8');
    assert(!html.includes('{% include') && !html.includes('{{ '), 'Search page contains unrendered Liquid');
    assert(/<main\b[^>]*\bid=["']lj-search["']/u.test(html), 'Generated page has no search interface');
    assert(/<script\b[^>]*\btype=["']module["'][^>]*\bsrc=["'][^"']*assets\/search\/launch-v1\.mjs["'][^>]*>/u.test(html) &&
      /<link\b[^>]*\bid=["']search-styles["'][^>]*\bhref=["'][^"']*assets\/search\/styles\.css["'][^>]*>/u.test(html),
      'Generated search page must load its versioned launcher and replaceable stylesheet');
    assert(!/<script\b[^>]*\bsrc=["'][^"']*assets\/search\/(?:app\.mjs|vendor\/lunr\.min\.js)["']/u.test(html),
      'Generated search page must not load an unversioned search app or library');
    result.generatedSite = destination;
    result.generatedXML = representations;
  }
  return result;
}
