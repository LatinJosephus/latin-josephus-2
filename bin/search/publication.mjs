/** Source, evidence, and publication checks for the static search export. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';

export const SOURCE_DIRECTORY = 'bin/search';
export const ASSET_DIRECTORY = 'assets/search';
export const MANIFEST_NAME = 'publication-manifest.json';
export const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
export const jsonBytes = value => Buffer.from(JSON.stringify(value, null, 2) + '\n');
const posix = value => value.split(path.sep).join('/');
const equal = (actual, expected, message) => assert.deepEqual(actual, expected, message);
const sorted = values => [...values].sort();
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
    ...config.siteInputs, ...config.hookInputs, ...collections.flatMap(c => c.adapter.sources), ...sourcePaths]);
  const indexedXML = new Set(collections.flatMap(c => c.adapter.sources));
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
    equal(report.coverage.paragraphsExactlyRestored, report.counts.numberedParagraphs, 'Incomplete paragraph restoration');
    for (const key of ['wordSequencePreserved', 'nonWhitespaceContentPreserved', 'globalIdsUnique', 'globalOrderIsConsecutive', 'allSectionTextsNonempty'])
      equal(report.coverage[key], true, `Extraction coverage failed: ${key}`);
    for (const key of ['id', 'work', 'label', 'citationPrefix', 'language', 'edition', 'readerPath'])
      equal(collection[key], manifest[key], `Catalog metadata differs: ${manifest.id}.${key}`);
    for (const key of ['citationScheme', 'unitLabel', 'unitLabelPlural'])
      equal(collection[key], manifest[key], `Catalog citation metadata differs: ${manifest.id}.${key}`);
    equal(collection.books, manifest.books.map(book => `${manifest.id}:${book.number}`), 'Collection book identities differ');
    equal(report.books.map(book => book.book), manifest.books.map(book => book.number), 'Extraction book order differs');
    equal(sorted(report.books.map(book => book.source.path)), sorted(adapter.sources),
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
      const source = checkIndexedXML(root, extracted.source, `${id} XML`);
      sources.push(source);
      equal(bookReport.coverage.paragraphsExactlyRestored, bookReport.counts.numberedParagraphs, 'Book has incomplete paragraph restoration');
      for (const [a, b] of [['rawParagraphSequenceSha256', 'restoredParagraphSequenceSha256'],
        ['sourceWordSequenceSha256', 'indexedWordSequenceSha256'],
        ['sourceNonWhitespaceContentSha256', 'indexedNonWhitespaceContentSha256']])
        equal(bookReport.coverage[a], bookReport.coverage[b], `Source coverage differs: ${id}.${a}`);
      for (const key of ['missingSections', 'unexpectedSections', 'duplicateSections']) equal(bookReport.coverage[key], [], `${id}: ${key}`);
      equal(bookReport.coverage.completeRange, spec.sectionRange, `Section range differs: ${id}`);
      equal(corpus.length, spec.sections, `Corpus section count differs: ${id}`);
      if (manifest.id === 'deh-latin-ussani') validateDehSourceProjection(corpus, bookReport, manifest, spec);
      if (manifest.id === 'contra-apionem-latin-boysen') validateCaSourceProjection(corpus, bookReport, manifest, spec);
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
      for (let index = 0; index < corpus.length; index++, order++) {
        const record = corpus[index], indexed = bundle.records[index];
        for (const [key, value] of Object.entries(record)) equal(indexed[key], value, `Bundle record differs: ${record.id}.${key}`);
        equal(record, combined[order], `Combined corpus differs at ${record.id}`);
        equal(record.order, order, `Corpus order differs at ${record.id}`);
        equal(record.book, spec.number, `Corpus book differs at ${record.id}`);
        for (const key of ['work', 'language', 'edition']) equal(record[key], manifest[key], `Wrong version at ${record.id}`);
        if (spec.sectionRange) equal(record.section, spec.sectionRange[0] + index, `Section order differs at ${record.id}`);
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
      sourceFiles: report.books.map(book => book.source.path), ...(qaSummary ? {qa: qaSummary} : {})});
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
  for (const [key, relative] of Object.entries(expected)) {
    equal(qa.verifiedFiles?.[key]?.path, `${SOURCE_DIRECTORY}/${relative}`, `Independent QA omits current ${key}`);
    checkEvidence(root, qa.verifiedFiles[key], `independent QA ${key}`);
  }
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
  }
  const item = evidence(root, `${SOURCE_DIRECTORY}/${adapter.qaReport}`);
  return {path: adapter.qaReport, sha256: item.sha256, status: 'PASS',
    assertions: qa.assertions, queries: qa.totalQueries, failedAssertions: 0,
    readerEvidenceIsHistorical: true};
}

export function publicationPlan(root) {
  const validated = validateSearchSources(root);
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
    artifacts: validated.artifacts,
  };
  return {manifest, bytes: jsonBytes(manifest), ...validated};
}

/** Export exact source bytes; delete only obsolete files previously owned by this exporter. */
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
    equal(sha256(source), item.sha256, `Source changed during export: ${item.source}`);
    const target = inside(output, item.path, {exists: false});
    fs.mkdirSync(path.dirname(target), {recursive: true});
    fs.writeFileSync(target, source);
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
    assert(/<script\b[^>]*\bsrc=["'][^"']*assets\/search\/app\.mjs["'][^>]*>/u.test(html) &&
      /<link\b[^>]*\bhref=["'][^"']*assets\/search\/styles\.css["'][^>]*>/u.test(html) &&
      /<script\b[^>]*\bsrc=["'][^"']*assets\/search\/vendor\/lunr\.min\.js["'][^>]*>/u.test(html),
      'Generated search page must load its search module, stylesheet, and Lunr');
    result.generatedSite = destination;
    result.generatedXML = representations;
  }
  return result;
}
