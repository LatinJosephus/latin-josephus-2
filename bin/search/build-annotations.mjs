#!/usr/bin/env node
/** Search projection of the reader's existing annotation interpretation. Sources stay read-only. */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {buildBundle} from './engine.mjs';

const repository = path.resolve(fileURLToPath(new URL('../../', import.meta.url)));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const json = (root, name) => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));
export function annotationInputs(root) {
  const inventory = json(root, '_docs/annotation-source-inventory.json');
  const citations = json(root, 'assets/data/alignment-citations.json');
  for (const [name, expected] of Object.entries(citations.provenance)) {
    const bytes = fs.readFileSync(path.join(root, name));
    const lf = bytes.toString('utf8').replace(/\r\n/gu, '\n');
    assert([hash(bytes), hash(lf), hash(lf.replace(/\n/gu, '\r\n'))].includes(expected), `Stale citation evidence: ${name}`);
  }
  return [...new Set([
    '_docs/annotation-source-inventory.json', 'assets/data/alignment-citations.json',
    'assets/data/deh-annotations/annotations.json', '_docs/deh-annotations/source.csv',
    'assets/js/manuscriptAnnotations.js', 'assets/js/dehManuscriptAnnotations.js',
    'assets/js/annotationEditorialUpdates.js', 'assets/js/annotationEditorialEnglish.js',
    'bin/search/engine.mjs', 'bin/search/build-annotations.mjs',
    ...inventory.records.map(record => record.sourceFile), ...Object.keys(citations.provenance)
  ])].sort().map(name => {
    const bytes = fs.readFileSync(path.join(root, name));
    return {path: name, sha256: hash(Object.hasOwn(citations.provenance, name)
      ? bytes.toString('utf8').replace(/\r\n/gu, '\n') : bytes)};
  });
}

export function annotationRecords(root) {
  const require = createRequire(path.join(root, 'assets/js/manuscriptAnnotations.js'));
  const api = require(path.join(root, 'assets/js/manuscriptAnnotations.js'));
  api.setCitationData(json(root, 'assets/data/alignment-citations.json'));
  api.setDEHAnnotationData(json(root, 'assets/data/deh-annotations/annotations.json'));
  const originals = json(root, '_docs/annotation-source-inventory.json').records;
  const source = [], supplements = [], appended = new Set();
  for (let book = 1; book <= 20; book++) supplements.push(...api.getSupplementalAnnotations('antiquities', book));
  originals.forEach((record, index) => {
    source.push(record);
    const next = originals[index + 1];
    if (!next || next.work !== record.work || next.sourceBook !== record.sourceBook || next.alignmentUnitId !== record.alignmentUnitId) {
      for (const supplement of supplements.filter(item => item.work === record.work && item.sourceBook === record.sourceBook && item.alignmentUnitId === record.alignmentUnitId)) {
        if (!appended.has(supplement.editorialSupplementId)) {source.push(supplement); appended.add(supplement.editorialSupplementId);}
      }
    }
  });
  assert.equal(appended.size, supplements.length, 'Supplement has no existing source alignment group');
  for (let book = 1; book <= 5; book++) source.push(...api.getDEHAnnotations(book));
  const records = [];
  for (const record of source) {
    const interpreted = api.interpretManuscriptAnnotation(record);
    const citation = api.resolveAlignmentCitation(record.work, record.locationTargetId || record.alignmentUnitId, {includeWork: true});
    const manuscript = api.resolveManuscript(record.siglum, record.witnessLabel || record.siglum);
    for (const part of interpreted.parts) {
      const provisional = part.provisionalReading?.en;
      const segments = provisional || part.displayText
        ? (provisional || part.displayText).split(/(\[[^\]]+\])/u).filter(Boolean).map(text => ({text, kind: /^\[/u.test(text) ? 'gap' : 'recorded'}))
        : api.annotationTextSegments(part, 'en', record.work).map(segment => ({...segment,
          kind: segment.original === '[*]' ? 'gap' : segment.kind}));
      const description = api.translateEditorialDescription(part.description, 'en');
      if (description) segments.push({text: segments.some(segment => segment.text) ? ' · ' : '', kind: 'gap'},
        {text: description, kind: ['symbolic', 'untranscribable'].includes(part.category) ? 'recorded' : 'editorial'});
      let text = '';
      const phraseBreaks = [], displaySegments = [];
      for (const segment of segments) {
        const start = text.length;
        if (segment.kind === 'gap') {
          text += ' ';
          phraseBreaks.push(start);
          displaySegments.push({text: segment.text, kind: 'gap', start, end: start});
        } else {
          text += segment.text;
          displaySegments.push({text: segment.text, kind: segment.kind, start, end: text.length});
        }
      }
      records.push({id: `${interpreted.anchor}-at-${part.offset}`, work: record.work,
        book: Number(record.sourceBook), section: records.length + 1, order: records.length,
        text, displaySegments, phraseBreaks: [...new Set(phraseBreaks)].sort((a, b) => a - b),
        language: 'Latin', edition: 'Manuscript annotations', breakBefore: true,
        citation: citation.publicCitation, verificationStatus: citation.verificationStatus,
        passageTarget: citation.navigationTarget, alignmentUnitId: record.alignmentUnitId,
        locationTargetId: record.locationTargetId || record.alignmentUnitId,
        category: part.category, manuscript: manuscript.displayName, siglum: record.siglum,
        folio: part.folio?.reference || null, pagination: part.pagination || 'folio', hand: part.hand,
        abbreviated: part.abbreviated, readingStatus: provisional ? 'provisional reading' : part.displayText ? 'reviewed reading' : null,
        originalNotation: interpreted.originalNotation, originalFragment: part.notation,
        sourceFile: record.sourceFile || record.editorialSource || '_docs/deh-annotations/source.csv', sourceRow: record.sourceRow || null});
    }
  }
  assert.equal(new Set(records.map(record => record.id)).size, records.length, 'Duplicate annotation anchors');
  return records;
}

export function validateAnnotationBundle(root) {
  const bundle = json(root, 'bin/search/annotations.bundle.json');
  assert.deepEqual(bundle.annotationSource.inputs, annotationInputs(root), 'Annotation search is stale; run node bin/search/build-annotations.mjs');
  assert.deepEqual(bundle.records, annotationRecords(root), 'Annotation search records differ from the reader interpretation');
  return bundle;
}

export function buildAnnotationBundle(root) {
  const require = createRequire(import.meta.url);
  const bundle = buildBundle(annotationRecords(root), require('./vendor/lunr.cjs'));
  bundle.annotationSource = {schemaVersion: 1, inputs: annotationInputs(root),
    matching: 'Each annotation independently; no phrases cross gaps or editorial-field boundaries.'};
  return bundle;
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv.includes('--check')) validateAnnotationBundle(repository);
  else fs.writeFileSync(path.join(repository, 'bin/search/annotations.bundle.json'), JSON.stringify(buildAnnotationBundle(repository)) + '\n');
  const bundle = validateAnnotationBundle(repository);
  console.log(JSON.stringify({status: 'PASS', annotations: bundle.records.length,
    works: Object.fromEntries(['antiquities', 'bellum', 'deh'].map(work => [work, bundle.records.filter(record => record.work === work).length])),
    unverifiedLocations: bundle.records.filter(record => record.verificationStatus !== 'verified').length}));
}
