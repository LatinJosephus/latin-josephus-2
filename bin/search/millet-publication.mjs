/** Separate source accounting control. This never calls the Python projector. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
const sha = value => createHash('sha256').update(value).digest('hex');
const pins = ['72bbab493ef33e407942e8189434096219e5e45d88ab532e9c40938d749b8648',
  'a47430026adb79b6d35e1c9ce20acbc13b70dfed5b06f207e7b82fff594bc6e3',
  '5c16095319a0d2a02407916235b3d5f6400a6ffb0903931a2b568b06083518fb',
  '4c528d45dc877b3e8d0213296d817a115731ff287749f19614dbb65973689046',
  'bf0e30581929a5901db6c972079cec74a3c3708d85bc8da473eca6ceb98fc7ad'];
export function validateMilletSourceProjection(corpus, report, manifest, spec, root) {
  const bytes = fs.readFileSync(path.join(root, spec.source));
  assert.equal(sha(bytes), pins[spec.number-1], 'Millet accepted reader source changed');
  const source = JSON.parse(bytes), byId = new Map(source.lines.map(line => [line.TEI_line_id, line]));
  const reconstructed = new Map(), seen = new Map();
  let lastIndex = -1, lastEnd = 0;
  for(const record of corpus) {
    assert.equal(record.citationScheme, 'source-span');
    assert.equal(record.normalizationProfile, 'early-print-fr-v1');
    assert.deepEqual(record.mappingIds, record.canonicalCorrespondences.map(item => item.mappingId));
    for(const relation of record.canonicalCorrespondences) {
      const original = source.mappings.find(mapping => mapping.id === relation.mappingId);
      assert(original);
      assert.deepEqual(relation, {mappingId:original.id, citation:original.canonical.citation,
        targetId:original.canonical.xml_id, relation:original.relation, certainty:original.certainty});
    }
    let restored = '';
    for(const piece of record.sourcePieces) {
      const line = byId.get(piece.line);
      assert(line?.primary && line.presentation_role === 'paragraph');
      assert(line.source_index > lastIndex || (line.source_index === lastIndex && piece.sourceStart === lastEnd));
      lastIndex = line.source_index; lastEnd = piece.sourceEnd;
      assert.equal(piece.sourceStart, seen.get(piece.line) || 0, 'Duplicated or missing French source offset');
      const text = line.text_exact.slice(piece.sourceStart,piece.sourceEnd);
      assert.equal(record.text.slice(piece.recordStart,piece.recordEnd), text);
      assert.equal(sha(text), piece.textSHA256);
      assert.equal(piece.image,line.image_number);
      if(restored && piece.recordStart>restored.length) restored += '\n';
      assert.equal(restored.length,piece.recordStart);
      restored += text;
      reconstructed.set(piece.line,(reconstructed.get(piece.line)||'')+text);
      seen.set(piece.line,piece.sourceEnd);
      // Verify metadata against accepted stand-off ownership for this exact span.
      for(const id of record.mappingIds) {
        assert(source.mappings.find(mapping => mapping.id===id).fragments.some(fragment => fragment.line===piece.line
          && fragment.start_utf16<=piece.sourceStart && fragment.end_utf16>=piece.sourceEnd));
      }
    }
    assert.equal(restored,record.text,'Unexplained synthetic characters in French record');
  }
  const primary = source.lines.filter(line=>line.primary&&line.presentation_role==='paragraph');
  assert.equal(reconstructed.size,primary.length);
  for(const line of primary) assert.equal(reconstructed.get(line.TEI_line_id),line.text_exact);
  assert.equal(report.sourceAccounting.length,source.lines.length);
  for(let i=0;i<source.lines.length;i++) {
    const line=source.lines[i], item=report.sourceAccounting[i];
    assert.equal(item.line,line.TEI_line_id); assert.equal(item.textSHA256,sha(line.text_exact));
    assert.equal(item.classification==='indexed-running-text',Boolean(line.primary&&line.presentation_role==='paragraph'));
  }
  assert.equal(report.coverage.paragraphsExactlyRestored,primary.length);
  assert.equal(new Set(corpus.flatMap(record=>record.mappingIds)).size,source.mappings.length);
  return {lines:source.lines.length,primaryLines:primary.length,physicalPassages:corpus.length,targets:source.mappings.length};
}
