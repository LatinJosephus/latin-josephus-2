/** Separate source accounting control. This never calls the Python projector. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
const sha = value => createHash('sha256').update(value).digest('hex');
const pins = ["8205c706d637277ee98cd4e3adbbd86ae2f13ff7128a90edd7feae2f8ecd7ae7", "829ca7017671c0420163d9ba4a77c715831185cec62d34ff6df63575a7a95164", "70ee4d7b1a6241cd9c6c4c7d5f45436942c1b0cdaebd178f395cd7102e45a9bc", "4142b77e21428258713617998c80da1047e82153dfa73ed39a0b471e231f6ac1", "4457fb8b741c5f8967466b64612fa0ba70c4dadfc35b34c8a69297a643a92be5"];
export function validateLauroSourceProjection(corpus, report, manifest, spec, root) {
  const bytes = fs.readFileSync(path.join(root, spec.source));
  assert.equal(sha(bytes), pins[spec.number-1], 'Lauro accepted reader source changed');
  const source = JSON.parse(bytes), byId = new Map(source.lines.map(line => [line.TEI_line_id, line]));
  const reconstructed = new Map(), seen = new Map();
  let lastIndex = -1, lastEnd = 0;
  for(const record of corpus) {
    assert.equal(record.citationScheme, 'source-span');
    assert.equal(record.normalizationProfile, 'early-print-it-v1');
    for(const range of record.suppliedTextRanges||[]) {assert.equal(record.text.slice(range.start,range.end),range.text);assert.equal(range.text,'[ſi]');assert(record.sourceAnnotations.some(a=>a.editoriallySuppliedNotPrinted&&a.text===range.text));}
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
      assert(line?.primary && line.emit_in_main_text);
      assert(line.source_index > lastIndex || (line.source_index === lastIndex && piece.sourceStart === lastEnd));
      lastIndex = line.source_index; lastEnd = piece.sourceEnd;
      assert.equal(piece.sourceStart, seen.get(piece.line) || 0, 'Duplicated or missing Italian source offset');
      const text = line.text_exact.slice(piece.sourceStart,piece.sourceEnd);
      assert.equal(record.text.slice(piece.recordStart,piece.recordEnd), text);
      assert.equal(sha(text), piece.textSHA256);
      assert.equal(piece.image,line.image_number);
      assert.equal(piece.acceptedSourceLineSHA256,line.text_sha256);
      assert.equal(piece.baselineRecordId,line.baseline_record_id);
      assert.deepEqual(piece.editorialAnnotations,line.editorial_annotations||[]);
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
    assert.equal(restored,record.text,'Unexplained synthetic characters in Italian record');
  }
  const primary = source.lines.filter(line=>line.primary&&line.emit_in_main_text);
  assert.equal(reconstructed.size,primary.length);
  for(const line of primary) assert.equal(reconstructed.get(line.TEI_line_id),line.text_exact);
  assert.equal(report.sourceAccounting.length,source.lines.length);
  for(let i=0;i<source.lines.length;i++) {
    const line=source.lines[i], item=report.sourceAccounting[i];
    assert.equal(item.line,line.TEI_line_id); assert.equal(item.textSHA256,sha(line.text_exact));
    assert.equal(item.classification==='indexed-running-text',Boolean(line.primary&&line.emit_in_main_text));
  }
  assert.equal(report.coverage.paragraphsExactlyRestored,primary.length);
  assert.equal(new Set(corpus.flatMap(record=>record.mappingIds)).size,source.mappings.length);
  return {lines:source.lines.length,primaryLines:primary.length,physicalPassages:corpus.length,targets:source.mappings.length};
}
