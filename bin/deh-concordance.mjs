/** Reviewed concordance freeze/audit only. No UI publication or canonical text writes. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const files = {
  concordance: 'assets/data/deh-josephus-concordance.json',
  workbook: '_docs/deh-concordance-source/workbook-values.json',
  decisions: '_docs/deh-concordance-source/editorial-decisions.json',
  projectDecisions: '_docs/deh-concordance-editorial-decisions.json',
  audit: '_docs/deh-concordance-validation.json',
  exceptions: '_docs/deh-concordance-exceptions.md',
  pilot: 'assets/data/deh-bj-alignment.json'
};
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const readJSON = name => JSON.parse(read(name));
const json = value => JSON.stringify(value, null, 2) + '\n';
const hash = value => createHash('sha256').update(value).digest('hex');
const write = (name, value) => {
  fs.mkdirSync(path.dirname(path.join(root, name)), { recursive: true });
  fs.writeFileSync(path.join(root, name), value);
};
const native = args => JSON.parse(execFileSync('pwsh.exe', [
  '-NoProfile', '-File',
  path.join(root, 'bin/deh-concordance-xml.ps1'), ...args
], { encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }));
const roman = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX'];
const expectedBooks = [212, 73, 70, 79, 121];
const noParallelKeys = ['1.3.1', '2.5.3', '3.2.1', '4.5.1', '5.1.1'];
let projectEditorial;
const citation = ref => `${ref.work} ${roman[ref.book]}.${ref.section_start}${ref.open_ended ? ' et sqq.' : ref.section_end === ref.section_start ? '' : `–${ref.section_end}`}`;

function canonicalIndex(corpus) {
  assert.equal(corpus.deh.length, 558, 'Canonical corpus must contain 558 units');
  assert.equal(new Set(corpus.latin_ids).size, 558, 'Duplicate canonical DEH IDs');
  const index = new Map();
  for (const unit of corpus.deh) {
    const prol = unit.citation.match(/^Prol\.([1-3])$/);
    if (prol) {
      assert.equal(unit.book, 1);
      assert.equal(unit.xml_id, `latin-deh1-num${prol[1]}`);
      continue;
    }
    const match = unit.citation.match(/^([IVX]+)\.(\d+)\.(\d+)$/);
    assert.ok(match, `Unrecognized canonical citation: ${unit.citation}`);
    assert.equal(match[1], roman[unit.book]);
    const key = `${unit.book}.${Number(match[2])}.${Number(match[3])}`;
    assert.ok(!index.has(key), `Duplicate canonical DEH citation: ${key}`);
    assert.equal(corpus.english_targets.filter(id => id === unit.xml_id).length, 1, `Pollard identity: ${key}`);
    index.set(key, { work: 'DEH', book: unit.book, chapter: Number(match[2]), unit: Number(match[3]), citation: unit.citation, key, xml_id: unit.xml_id });
  }
  assert.equal(index.size, 555);
  assert.equal(index.get('1.1.1').xml_id, 'latin-deh1-num4');
  assert.equal(index.get('1.46.2').xml_id, 'latin-deh1-num215');
  return index;
}

// Split only outside parentheses. Never sort the scholarly target sequence.
function splitExpression(expression) {
  const result = [];
  let depth = 0, start = 0, separator = null;
  const add = end => {
    const raw = expression.slice(start, end), literal = raw.trim();
    assert.ok(literal, `Empty fragment: ${expression}`);
    result.push({ literal, separator_before: separator, expression_offset: start + raw.indexOf(literal) });
  };
  for (let i = 0; i < expression.length; i++) {
    if (expression[i] === '(') depth++;
    if (expression[i] === ')') depth--;
    assert.ok(depth >= 0 && depth <= 1, `Unsupported parentheses: ${expression}`);
    if (!depth && [',', '+'].includes(expression[i])) { add(i); separator = expression[i]; start = i + 1; }
  }
  assert.equal(depth, 0, `Unclosed parenthesis: ${expression}`);
  add(expression.length);
  return result;
}

function parsePlain(value, scope, allowBookOnly = false) {
  let text = value.trim();
  const work = text.match(/^(BJ|AJ)\s+/);
  if (work) { scope.work = work[1]; scope.book = null; text = text.slice(work[0].length); }
  if (allowBookOnly && /^\d+\.$/.test(text)) { scope.book = Number(text.slice(0, -1)); return null; }
  const match = text.match(/^(?:(\d+)\.)?(\d+)(?:\s*-\s*(\d+))?(?:\s+(et sqq\.))?$/);
  assert.ok(match, `Unparsed source token: ${value}`);
  if (match[1]) scope.book = Number(match[1]);
  assert.ok(Number.isInteger(scope.book), `Missing book: ${value}`);
  assert.ok(!(match[3] && match[4]), `Conflicting endpoint: ${value}`);
  return { work: scope.work, book: scope.book, section_start: Number(match[2]), section_end: match[4] ? null : Number(match[3] || match[2]), open_ended: Boolean(match[4]) };
}

// Preserve the package's original segmented parse as evidence. The separate
// targets array below is the conservative normalized sequence for future use.
function parseSegments(expression) {
  if (!expression) return [];
  const scope = { work: 'BJ', book: null };
  return splitExpression(expression).map((segment, index) => {
    const matches = [...segment.literal.matchAll(/\(([^()]*)\)/g)];
    const outerReference = parsePlain(segment.literal.replace(/\([^()]*\)/g, '').trim(), scope, true);
    const parentheses = matches.map(match => {
      const content = match[1].trim(), end = match.index + match[0].length;
      const annotation = { literal: match[0], content, offset_start: match.index, offset_end_exclusive: end,
        placement: !outerReference ? 'whole_reference' : segment.literal.slice(end).trim() ? 'within_reference' : 'suffix', editorial_meaning: 'unresolved' };
      return content.startsWith('=') ? { ...annotation, kind: 'text_annotation' }
        : { ...annotation, kind: 'parenthetical_reference', reference: parsePlain(content, { ...scope }) };
    });
    assert.ok(outerReference || parentheses.length);
    return { order: index + 1, ...segment, unparenthesized_reference: outerReference, parentheses };
  });
}

function sourceRecords(workbook, decisions, corpus) {
  const canonical = canonicalIndex(corpus);
  assert.equal(decisions.confirmed.find(d => d.id === 'D04')?.references, '1.187');
  assert.equal(decisions.confirmed.find(d => d.id === 'D05')?.before, '2.487, 290-293');
  assert.equal(decisions.confirmed.find(d => d.id === 'D05')?.after, '2.487, 490-493');
  assert.equal(workbook.length, 1);
  assert.equal(workbook[0].name, 'Equivalences');
  const values = workbook[0].values;
  assert.equal(values.length, 555, 'Expected header and 554 source rows');
  const records = [];
  const make = (row, raw, added = false) => {
    const key = added ? '1.23.2' : raw[0].trim();
    assert.ok(canonical.has(key), `Source citation does not resolve: ${key}`);
    const sourceText = added ? null : raw[1];
    let effectiveText = added ? '1.187' : sourceText.trim();
    const applied = [];
    if (added) applied.push('D04');
    if (key === '2.11.3') { assert.equal(row, 255); assert.equal(effectiveText, '2.487, 290-293'); effectiveText = '2.487, 490-493'; applied.push('D05'); }
    if (key === '5.53.1') applied.push('D06');
    const otherText = added ? '' : raw[2].trim();
    return {
      id: `deh-${key.replaceAll('.', '-')}`, deh: canonical.get(key),
      source: added ? { kind: 'student_correction', workbook_row: null, cells: null, raw_values: null,
        authority: 'Student answer 7, supplied 2026-10-02', inserted_after_original_row: 65 }
        : { kind: 'student_transcription_of_edition', workbook_row: row,
          cells: { deh: `Equivalences!A${row}`, josephus: `Equivalences!B${row}`, other_works: `Equivalences!C${row}` },
          raw_values: { deh: raw[0], josephus: sourceText, other_works: raw[2] } },
      josephus: { effective_text: effectiveText, status: effectiveText ? 'references_recorded' : 'no_bj_aj_parallel_recorded', segments: parseSegments(effectiveText) },
      other_works: { text: otherText, status: otherText === '\\\\' ? 'apparent_non_bibliographic_residue' : otherText ? 'reference_recorded_unparsed' : 'no_reference_recorded' },
      applied_decisions: applied,
      unresolved_questions: decisions.unresolved.filter(q => (q.cells || []).some(cell => cell === `B${row}` || cell === `C${row}`) || q.cell === `B${row}` || q.cell === `C${row}`).map(q => q.id)
    };
  };
  for (let i = 1; i < values.length; i++) {
    assert.equal(values[i].length, 3);
    assert.ok(values[i].every(value => typeof value === 'string'));
    records.push(make(i + 1, values[i]));
    if (i + 1 === 65) records.push(make(null, null, true));
  }
  assert.equal(records.length, 555);
  assert.equal(new Set(records.map(r => r.deh.key)).size, 555, 'Duplicate DEH record');
  assert.deepEqual(new Set(records.map(r => r.deh.key)), new Set(canonical.keys()), 'Omitted numbered DEH unit');
  assert.deepEqual([1, 2, 3, 4, 5].map(b => records.filter(r => r.deh.book === b).length), expectedBooks);
  return records;
}

function readerConfiguration() {
  const code = read('assets/js/renderTei.js').split('"/antiquities/":')[1]?.split('"/bellum-judaicum/":')[0];
  assert.ok(code, 'Could not locate Antiquities reader configuration');
  const books = code.match(/nieseBooks:\s*\[([^\]]+)\]/);
  const ranges = code.match(/nieseRanges:\s*\{([^}]+)\}/);
  assert.ok(books && ranges, 'Could not read current Niese navigation configuration');
  return { books: books[1].split(',').map(s => Number(s.trim())), ranges: Object.fromEntries([...ranges[1].matchAll(/(\d+):\s*\[(\d+),\s*(\d+)\]/g)].map(m => [m[1], [Number(m[2]), Number(m[3])]])) };
}

function resolve(ref, corpus, configuration) {
  assert.ok(['BJ', 'AJ'].includes(ref.work));
  assert.ok(Number.isInteger(ref.book) && ref.book > 0 && ref.book <= (ref.work === 'BJ' ? 7 : 20));
  assert.ok(Number.isInteger(ref.section_start) && ref.section_start > 0);
  assert.equal(ref.open_ended, ref.section_end === null);
  if (!ref.open_ended) assert.ok(Number.isInteger(ref.section_end) && ref.section_end >= ref.section_start);
  const coordinates = Array.from({ length: ref.open_ended ? 1 : ref.section_end - ref.section_start + 1 }, (_, i) => ref.section_start + i);
  if (ref.work === 'BJ') {
    const coverage = Object.fromEntries(['Greek', 'Latin', 'English'].map(language => {
      const available = new Set(corpus.bellum[ref.book]?.[language] || []);
      return [language, coordinates.every(n => available.has(n))];
    }));
    return { coordinate_status: Object.values(coverage).every(Boolean) ? 'passed' : 'failed', sources: coverage, closed_reference: !ref.open_ended };
  }
  const range = configuration.ranges[ref.book];
  const enabled = configuration.books.includes(ref.book);
  const covered = enabled && range && coordinates.every(n => n >= range[0] && n <= range[1] &&
    ['Latin', 'Greek'].every(language => corpus.antiquities[ref.book][language].includes(n)));
  return { coordinate_status: 'parsed_aj_reference', site_niese_addressable: Boolean(covered && !ref.open_ended),
    reason: !enabled ? 'Niese navigation is not enabled for this AJ book.' : !covered ? 'At least one coordinate is absent from the current Latin/Greek Niese anchors.' : ref.open_ended ? 'No endpoint is supplied for the open reference.' : 'Current Niese navigation resolves the closed reference; English provides context, not exact Niese segmentation.' };
}

function normalize(record, corpus, configuration) {
  const reviewed = structuredClone(record);
  const recordDecisions = projectEditorial.confirmed.filter(d => d.deh === record.deh.key);
  for (const decision of recordDecisions) assert.equal(record.josephus.effective_text, decision.raw_source_notation, `Adjudicated source notation changed: ${record.deh.citation}`);
  const parentheticalDecision = recordDecisions.find(d => d.targets);
  const closure = recordDecisions.find(d => d.topic === 'closed_endpoint');
  const annotationDecision = recordDecisions.find(d => d.topic === 'source_annotation');
  const targets = [], annotations = [], unresolved = [];
  const add = (sourceRef, segment, rawToken, offset, parenthesis = null) => {
    let ref = { ...sourceRef };
    if (sourceRef.open_ended && closure) {
      assert.deepEqual([sourceRef.work, sourceRef.book, sourceRef.section_start],
        [closure.closed_target.work, closure.closed_target.book, closure.closed_target.section_start]);
      ref = { ...ref, section_end: closure.closed_target.section_end, open_ended: false };
    }
    const decision = parentheticalDecision || (sourceRef.open_ended ? closure : null);
    targets.push({
      order: targets.length + 1, segment_order: segment.order, ...ref,
      form: ref.open_ended ? 'open_range' : ref.section_start === ref.section_end ? 'single_section' : 'closed_range',
      parenthetical: Boolean(parenthesis), parenthetical_placement: parenthesis?.placement || null,
      relationship_role: parenthesis ? 'supplementary_parallel' : 'primary_parallel',
      normalized_citation: `${parenthesis ? '(' : ''}${citation(ref)}${parenthesis ? ')' : ''}`,
      raw_token: rawToken, expression_offset: offset,
      editorial_status: 'reviewed_recorded_parallel',
      ...(decision ? { editorial_decision: decision.id, adjudication_date: decision.adjudication_date || projectEditorial.date } : {}),
      validation: resolve(ref, corpus, configuration)
    });
  };
  for (const segment of record.josephus.segments) {
    if (segment.parentheses.some(p => p.placement === 'within_reference')) {
      const decision = parentheticalDecision;
      if (decision) {
        assert.equal(segment.literal, decision.raw_source_notation);
        assert.equal(record.josephus.segments.length, 1);
        assert.equal(segment.parentheses.length, 1);
        for (const target of decision.targets) {
          const { parenthetical, relationship_role, ...ref } = target;
          const parenthesis = parenthetical ? segment.parentheses[0] : null;
          add(ref, segment, parenthesis?.literal || segment.literal,
            segment.expression_offset + (parenthesis?.offset_start || 0), parenthesis);
        }
        continue;
      }
      // An unknown inline notation still requires a human decision.
      unresolved.push({ segment_order: segment.order, raw_token: segment.literal, expression_offset: segment.expression_offset,
        reason: 'Parenthesis interrupts a reference. The package parse attempt is retained in segments, but no normalized target is endorsed.',
        package_parse_attempt: { outer: segment.unparenthesized_reference, parentheses: segment.parentheses } });
      continue;
    }
    if (segment.unparenthesized_reference) {
      const rawToken = segment.literal.slice(0, segment.parentheses[0]?.offset_start ?? segment.literal.length).trim();
      add(segment.unparenthesized_reference, segment, rawToken, segment.expression_offset);
    }
    for (const parenthesis of segment.parentheses) {
      if (parenthesis.kind === 'text_annotation') {
        assert.ok(annotationDecision, `Unadjudicated annotation: ${record.deh.citation}`);
        assert.equal(parenthesis.content, `= ${annotationDecision.annotation.raw_value}`);
        annotations.push({ segment_order: segment.order, raw_token: parenthesis.literal,
          expression_offset: segment.expression_offset + parenthesis.offset_start, content: parenthesis.content,
          ...annotationDecision.annotation, interpretation: annotationDecision.decision,
          editorial_status: 'human_approved_annotation', editorial_decision: annotationDecision.id,
          adjudication_date: annotationDecision.adjudication_date });
      }
      else add(parenthesis.reference, segment, parenthesis.literal, segment.expression_offset + parenthesis.offset_start, parenthesis);
    }
  }
  if (parentheticalDecision) assert.deepEqual(targets.map(t => ({ work: t.work, book: t.book,
    section_start: t.section_start, section_end: t.section_end, open_ended: t.open_ended,
    parenthetical: t.parenthetical, relationship_role: t.relationship_role })), parentheticalDecision.targets,
  `Parenthetical adjudication disagrees with source order: ${record.deh.citation}`);
  for (const segment of reviewed.josephus.segments) for (const parenthesis of segment.parentheses) {
    parenthesis.editorial_meaning = parenthesis.kind === 'parenthetical_reference' ? 'supplementary_parallel' : annotationDecision.annotation.type;
  }
  if (recordDecisions.length) {
    reviewed.applied_editorial_decisions = recordDecisions.map(d => d.id);
    reviewed.resolved_package_questions = recordDecisions.map(d => ({
      id: d.supersedes_package_question_for_this_record, scope: 'this_record', editorial_decision: d.id
    }));
    reviewed.source.package_questions = [...record.unresolved_questions];
    reviewed.unresolved_questions = record.unresolved_questions.filter(q => !reviewed.resolved_package_questions.some(r => r.id === q));
  }
  const residue = recordDecisions.find(d => d.topic === 'provenance_only_residue');
  if (residue) {
    assert.equal(record.source.raw_values.other_works.trim(), residue.raw_other_works);
    reviewed.other_works = { text: '', status: 'no_reference_recorded' };
  }
  return { ...reviewed, josephus: { ...reviewed.josephus,
    normalization_status: unresolved.length ? 'partial_requires_review' : 'reviewed', targets, annotations, unresolved_tokens: unresolved } };
}

function pilotSemantics(records) {
  return records.map(r => ({ id: r.id, deh: r.deh, targets: r.josephus.segments.flatMap(s => [
    ...(s.unparenthesized_reference ? [{ ...s.unparenthesized_reference, parenthetical: false }] : []),
    ...s.parentheses.filter(p => p.reference).map(p => ({ ...p.reference, parenthetical: true }))
  ]) }));
}

function assertPilot(records) {
  const pilot = readJSON(files.pilot);
  assert.equal(pilot.records.length, 11);
  assert.deepEqual(pilot.records.map(r => r.id), [...Array.from({ length: 10 }, (_, i) => `deh-1-1-${i + 1}`), 'deh-5-53-1']);
  const candidates = pilot.records.map(p => records.find(r => r.id === p.id));
  assert.ok(candidates.every(Boolean), 'Missing approved pilot relation');
  assert.deepEqual(pilotSemantics(candidates), pilotSemantics(pilot.records), 'STOP: candidate conflicts with approved pilot');
  if (candidates.every(r => r.josephus.targets)) {
    const normalized = candidates.map(r => ({ id: r.id, deh: r.deh, targets: r.josephus.targets.map(t => ({
      work: t.work, book: t.book, section_start: t.section_start, section_end: t.section_end, open_ended: t.open_ended, parenthetical: t.parenthetical
    })) }));
    assert.deepEqual(normalized, pilotSemantics(pilot.records), 'STOP: normalized targets conflict with approved pilot');
  }
}

function validate(candidate, workbook, decisions, corpus) {
  assert.equal(candidate.status, 'reviewed_frozen');
  assert.equal(candidate.publication_status, 'reviewed_not_published');
  assert.equal(candidate.date, '2026-10-02');
  assert.deepEqual(candidate.project_editorial_decisions, { path: files.projectDecisions, sha256: hash(read(files.projectDecisions)) }, 'Project editorial decision provenance changed');
  assert.deepEqual(candidate.canonical_xml_sha256, corpus.xml_sha256, 'Canonical XML changed since import');
  const base = sourceRecords(workbook, decisions, corpus);
  const configuration = readerConfiguration();
  const expected = base.map(r => normalize(r, corpus, configuration));
  assert.deepEqual(candidate.records, expected, 'Candidate differs from raw evidence, canonical citations, ordered parsing, or current coordinate validation');
  assert.ok(candidate.records.every(r => !r.unresolved_questions.length && !r.josephus.unresolved_tokens.length), 'STOP: a genuine unresolved editorial issue remains');
  assertPilot(candidate.records);
  assert.deepEqual(candidate.records.filter(r => !r.josephus.effective_text).map(r => r.deh.key), noParallelKeys);
  assert.ok(candidate.records.filter(r => !r.josephus.effective_text).every(r => r.josephus.status === 'no_bj_aj_parallel_recorded' && r.josephus.targets.length === 0));
  for (const r of candidate.records) for (const t of r.josephus.targets) {
    assert.equal(r.josephus.effective_text.slice(t.expression_offset, t.expression_offset + t.raw_token.length), t.raw_token, 'Lost target substring/position');
    if (t.work === 'BJ') assert.equal(t.validation.coordinate_status, 'passed', `BJ coordinate failure: ${r.deh.citation} ${t.normalized_citation}`);
    assert.equal(t.relationship_role, t.parenthetical ? 'supplementary_parallel' : 'primary_parallel');
    assert.equal(t.open_ended, false, 'STOP: an unadjudicated open target remains');
  }
  assert.deepEqual(candidate.records.find(r => r.deh.key === '1.37.5').josephus.targets.map(t => t.work), ['BJ', 'AJ', 'AJ', 'AJ', 'BJ']);
  const clarified = candidate.records.find(r => r.deh.key === '2.9.2');
  assert.equal(clarified.source.raw_values.josephus.trim(), '2.402(344)-404');
  assert.deepEqual(clarified.josephus.targets.map(t => [t.section_start, t.section_end, t.parenthetical, t.relationship_role]),
    [[402, 404, false, 'primary_parallel'], [344, 344, true, 'supplementary_parallel']], 'User-confirmed II.9.2 interpretation must be preserved');
  assert.deepEqual(candidate.records.find(r => r.deh.key === '2.13.7').josephus.targets.map(t => [t.work, t.book, t.section_start, t.section_end, t.open_ended]),
    [['AJ', 20, 247, 249, false], ['AJ', 15, 38, 56, false]]);
  assert.deepEqual(candidate.records.find(r => r.deh.key === '4.30.2').josephus.targets.map(t => [t.work, t.book, t.section_start, t.section_end, t.open_ended]),
    [['BJ', 4, 643, 644, false]]);
  const historia = candidate.records.find(r => r.deh.key === '1.6.4');
  assert.equal(historia.josephus.targets.length, 1);
  assert.deepEqual([historia.josephus.annotations[0].type, historia.josephus.annotations[0].raw_value, historia.josephus.annotations[0].target_orders], ['source_label', 'historia uetus', [1]]);
  const alii = candidate.records.find(r => r.deh.key === '1.37.4');
  assert.deepEqual([alii.josephus.annotations[0].type, alii.josephus.annotations[0].raw_value, alii.josephus.annotations[0].target_orders], ['alternative_tradition', 'alii', [2, 3]]);
  assert.ok(alii.josephus.annotations[0].target_orders.every(order => alii.josephus.targets[order - 1].work === 'AJ'));
  const residue = candidate.records.find(r => r.deh.key === '5.53.2');
  assert.deepEqual(residue.other_works, { text: '', status: 'no_reference_recorded' });
  assert.equal(residue.josephus.annotations.length, 0);
  for (let book = 1; book <= 7; book++) {
    const greek = corpus.bellum[book].Greek;
    const full = Array.from({ length: Math.max(...greek) }, (_, i) => i + 1);
    for (const language of ['Greek', 'Latin', 'English']) {
      assert.deepEqual([...corpus.bellum[book][language]].sort((a, b) => a - b), full, `Incomplete/duplicate BJ ${book} ${language} Niese anchors`);
    }
  }
  return expected;
}

const packageReferences = record => record.josephus.segments.flatMap(s => [
  ...(s.unparenthesized_reference ? [s.unparenthesized_reference] : []),
  ...s.parentheses.filter(p => p.reference).map(p => p.reference)
]);
const hasWork = (record, work) => packageReferences(record).some(r => r.work === work);

function statistics(records) {
  const targets = records.flatMap(r => r.josephus.targets);
  return {
    records: records.length,
    with_bj_recorded: records.filter(r => hasWork(r, 'BJ')).length,
    with_aj_recorded: records.filter(r => hasWork(r, 'AJ')).length,
    with_both_bj_and_aj: records.filter(r => hasWork(r, 'BJ') && hasWork(r, 'AJ')).length,
    no_bj_aj_parallel_recorded: records.filter(r => r.josephus.status === 'no_bj_aj_parallel_recorded').length,
    with_other_works_raw_data: records.filter(r => r.source.raw_values?.other_works.trim()).length,
    with_other_work_reference_strings: records.filter(r => r.other_works.status === 'reference_recorded_unparsed').length,
    normalized_other_works_residue_records: records.filter(r => r.other_works.status === 'apparent_non_bibliographic_residue').length,
    provenance_only_residue_records: records.filter(r => r.source.raw_values?.other_works.trim() === '\\\\').length,
    normalized_bj_components: targets.filter(t => t.work === 'BJ').length,
    normalized_aj_components: targets.filter(t => t.work === 'AJ').length,
    parenthetical_expressions: records.flatMap(r => r.josephus.segments.flatMap(s => s.parentheses)).length,
    parenthetical_reference_records: records.filter(r => r.josephus.segments.some(s => s.parentheses.some(p => p.reference))).length,
    normalized_parenthetical_components: targets.filter(t => t.parenthetical).length,
    supplementary_parallel_components: targets.filter(t => t.relationship_role === 'supplementary_parallel').length,
    primary_parallel_components: targets.filter(t => t.relationship_role === 'primary_parallel').length,
    unresolved_parenthetical_meaning_records: records.filter(r => r.josephus.targets.some(t => t.editorial_status === 'parenthetical_meaning_unresolved')).length,
    source_annotation_records: records.filter(r => r.josephus.annotations.length).length,
    open_ended_components: targets.filter(t => t.open_ended).length,
    unresolved_syntax_records: records.filter(r => r.josephus.unresolved_tokens.length).length,
    withheld_package_parse_components: records.flatMap(r => r.josephus.unresolved_tokens).reduce((n, u) => n + (u.package_parse_attempt.outer ? 1 : 0) + u.package_parse_attempt.parentheses.filter(p => p.reference).length, 0)
  };
}

const categoryTitles = {
  unresolved_parenthetical_syntax: 'Unresolved parenthetical syntax',
  parenthetical_meaning_unresolved: 'Parenthetical notation: meaning unresolved',
  open_ended_references: 'Open-ended references',
  source_annotations: 'Source annotations requiring interpretation'
};

function exceptions(records) {
  const result = [];
  const add = (category, record, attempted, reason, otherRaw = null) => result.push({
    category, deh: record.deh.citation, xml_id: record.deh.xml_id,
    raw_reference: record.source.raw_values?.josephus ?? null,
    ...(otherRaw !== null ? { raw_other_works: otherRaw } : {}), attempted_interpretation: attempted, reason
  });
  for (const r of records) {
    const j = r.josephus;
    if (j.unresolved_tokens.length) add('unresolved_parenthetical_syntax', r,
      j.unresolved_tokens.map(u => ({ raw: u.raw_token, package_parse_attempt: u.package_parse_attempt })),
      'The parenthesis interrupts the reference. No normalized target is emitted; the package parse attempt is evidence, not an endorsed interpretation.');
    const parenthetical = j.targets.filter(t => t.parenthetical && t.editorial_status === 'parenthetical_meaning_unresolved');
    if (parenthetical.length) add('parenthetical_meaning_unresolved', r, parenthetical.map(t => t.normalized_citation),
      'Citation syntax is parseable, but the inherited parentheses have no established editorial meaning.');
    const open = j.targets.filter(t => t.open_ended);
    if (open.length) add('open_ended_references', r, open.map(t => t.normalized_citation),
      'A starting coordinate is known; the source supplies no endpoint. A closed excerpt must not be inferred.');
    if (j.annotations.some(a => a.editorial_status !== 'human_approved_annotation')) add('source_annotations', r, j.annotations.map(a => a.raw_token),
      'The source annotation is retained without interpreting its function.');
  }
  return result;
}

function siteLimitations(records) {
  return records.flatMap(r => {
    const targets = r.josephus.targets.filter(t => t.work === 'AJ' && !t.validation.site_niese_addressable);
    return targets.length ? [{ deh: r.deh.citation, xml_id: r.deh.xml_id,
      raw_reference: r.source.raw_values.josephus,
      targets: targets.map(t => ({ citation: t.normalized_citation, reason: t.validation.reason })) }] : [];
  });
}

function sourceResidues(records) {
  return records.filter(r => r.source.raw_values?.other_works.trim() === '\\\\').map(r => ({
    deh: r.deh.citation, xml_id: r.deh.xml_id, raw_other_works: r.source.raw_values.other_works,
    evidence_snapshot: files.workbook, source_cell: r.source.cells.other_works,
    editorial_decision: 'P4-D11', treatment: 'Raw evidence only. Reviewed Other works is empty; no bibliographic reference or concordance annotation.'
  }));
}

function audit(candidate, corpus) {
  const records = candidate.records, targets = records.flatMap(r => r.josephus.targets), review = exceptions(records);
  const limitations = siteLimitations(records), residues = sourceResidues(records);
  assert.equal(review.length, 0, 'STOP: unresolved editorial exceptions prevent the reviewed freeze');
  const bj = targets.filter(t => t.work === 'BJ'), aj = targets.filter(t => t.work === 'AJ');
  const configuration = readerConfiguration();
  const ajByBook = Array.from({ length: 20 }, (_, i) => i + 1).map(book => {
    const refs = aj.filter(t => t.book === book);
    return { book, normalized_components: refs.length, niese_navigation_enabled: configuration.books.includes(book),
      closed_site_addressable: refs.filter(t => t.validation.site_niese_addressable).length,
      not_site_addressable: refs.filter(t => !t.validation.site_niese_addressable).length,
      open_ended: refs.filter(t => t.open_ended).length,
      unresolved_syntax: records.filter(r => r.josephus.unresolved_tokens.some(u => [u.package_parse_attempt.outer,
        ...u.package_parse_attempt.parentheses.map(p => p.reference)].some(ref => ref?.work === 'AJ' && ref.book === book))).length };
  });
  return {
    status: 'passed_reviewed_freeze', date: candidate.date,
    scope: 'Human-adjudicated scholarly parallels, canonical identities and Niese coordinate presence. Roles do not assert textual dependence; AJ site-support limitations do not invalidate the reviewed dataset.',
    reviewed_concordance: { path: files.concordance, sha256: hash(json(candidate)), status: candidate.status, date: candidate.date, publication_status: candidate.publication_status },
    source_package: candidate.source_package,
    project_editorial_decisions: candidate.project_editorial_decisions,
    statistics: statistics(records),
    by_deh_book: [1, 2, 3, 4, 5].map(book => ({ book, ...statistics(records.filter(r => r.deh.book === book)) })),
    deh: { numbered_units_expected: 555, uniquely_resolved: 555, duplicate_citations: 0, duplicate_ids: 0, omitted_numbered_units: 0, excluded_prologue_units: ['Prol.1', 'Prol.2', 'Prol.3'], pollard_identities_resolved: 555 },
    bellum: { normalized_closed_components: bj.filter(t => !t.open_ended).length,
      closed_components_passed: bj.filter(t => !t.open_ended && t.validation.coordinate_status === 'passed').length,
      closed_components_failed: bj.filter(t => !t.open_ended && t.validation.coordinate_status !== 'passed').length,
      open_starts_passed: bj.filter(t => t.open_ended && t.validation.coordinate_status === 'passed').length,
      closed_source_checks_passed: bj.filter(t => !t.open_ended).length * 3,
      canonical_anchor_inventory: Object.entries(corpus.bellum).map(([book, sources]) => ({ book: Number(book), Greek: sources.Greek.length, Latin: sources.Latin.length, English: sources.English.length })) },
    antiquities: { normalized_components: aj.length, site_addressable_closed: aj.filter(t => t.validation.site_niese_addressable).length,
      not_site_addressable: aj.filter(t => !t.validation.site_niese_addressable).length, by_book: ajByBook,
      qualification: 'Only current configured books and Latin/Greek Niese anchors establish addressability. English provides context rather than exact Niese segmentation. No unsupported AJ links or IDs were generated.' },
    pilot: { approved_records: 11, semantically_matching: 11, discrepancies: 0, active_data_sha256: hash(read(files.pilot)), active_scope_changed: false },
    review: { entries: review.length, unique_deh_units: new Set(review.map(r => r.xml_id)).size,
      categories: Object.fromEntries(Object.keys(categoryTitles).map(category => [category, review.filter(r => r.category === category).length])) },
    site_support_limitations: { records: limitations.length, target_components: limitations.reduce((n, r) => n + r.targets.length, 0), entries: limitations },
    provenance_only_residues: { records: residues.length, entries: residues },
    canonical_xml_files_checked: Object.keys(corpus.xml_sha256).length, canonical_xml_sha256: corpus.xml_sha256,
    exceptions: review
  };
}

function exceptionMarkdown(report) {
  const lines = ['**DEH–Josephus reviewed concordance: editorial and support report**', '',
    'Raw evidence is JSON-quoted to preserve whitespace and punctuation. Site-support limitations and provenance-only residues are separate from editorial exceptions.', '',
    '## A. Unresolved editorial exceptions', '',
    `None (${report.review.entries}). All six parenthetical cases, both inherited open references, and both source annotations have human-approved adjudications. BJ canonical failures and pilot discrepancies are both zero.`, ''];
  for (const [category, title] of Object.entries(categoryTitles)) {
    const entries = report.exceptions.filter(e => e.category === category);
    if (!entries.length) continue;
    lines.push(`### ${title} (${entries.length})`, '');
    for (const e of entries) {
      let attempted = e.attempted_interpretation;
      if (category === 'unresolved_parenthetical_syntax') attempted = attempted.map(u => [
        ...(u.package_parse_attempt.outer ? [citation(u.package_parse_attempt.outer)] : []),
        ...u.package_parse_attempt.parentheses.filter(p => p.reference).map(p => `(${citation(p.reference)})`)
      ].join('; ')).join('; ') + ' — package attempt only; withheld from normalized targets';
      else if (Array.isArray(attempted)) attempted = attempted.join('; ');
      else if (attempted === null) attempted = 'No bibliographic interpretation supplied';
      lines.push(`- **DEH ${e.deh}** — \`${e.xml_id}\``,
        `  Original BJ/AJ reference: \`${JSON.stringify(e.raw_reference)}\`.`,
        ...(e.raw_other_works !== undefined ? [`  Original Other works: \`${JSON.stringify(e.raw_other_works)}\`.`] : []),
        `  Attempted interpretation: ${attempted}${attempted.endsWith('.') ? '' : '.'}`,
        `  Review: ${e.reason}`, '');
    }
  }
  lines.push('## B. Site-support limitations', '',
    `${report.site_support_limitations.records} DEH records contain ${report.site_support_limitations.target_components} structurally valid AJ components that current Antiquities Niese navigation cannot address. These are valid reviewed parallels, not editorial defects. No unsupported URLs or textual IDs are fabricated.`, '');
  for (const r of report.site_support_limitations.entries) lines.push(
    `- **DEH ${r.deh}** — \`${r.xml_id}\``,
    `  Original BJ/AJ reference: \`${JSON.stringify(r.raw_reference)}\`.`,
    `  Reviewed AJ targets: ${r.targets.map(t => t.citation).join('; ')}.`,
    `  Support limitation: ${[...new Set(r.targets.map(t => t.reason))].join(' ')}`, '');
  lines.push('## C. Source residues / provenance-only artifacts', '',
    `${report.provenance_only_residues.records} confirmed source residue is retained only as raw evidence.`, '');
  for (const r of report.provenance_only_residues.entries) lines.push(
    `- **DEH ${r.deh}** — \`${r.xml_id}\``,
    `  Original Other works: \`${JSON.stringify(r.raw_other_works)}\`.`,
    `  Raw snapshot: \`${r.evidence_snapshot}\`, \`${r.source_cell}\`; also preserved in the record's immutable raw-value snapshot.`,
    `  Approved treatment (${r.editorial_decision}): ${r.treatment}`, '');
  return lines.join('\n').trimEnd() + '\n';
}

function selfTest(candidate, workbook, decisions, corpus) {
  const mutations = {
    missing_record: c => c.records.pop(),
    duplicate_canonical_identity: c => { c.records[1].deh.xml_id = c.records[0].deh.xml_id; },
    reordered_components: c => { c.records.find(r => r.deh.key === '1.1.4').josephus.targets.reverse(); },
    bj_aj_interleave_lost: c => { c.records.find(r => r.deh.key === '1.37.5').josephus.targets.sort((a, b) => a.work.localeCompare(b.work)); },
    parenthetical_status_lost: c => { c.records.find(r => r.deh.key === '5.53.1').josephus.targets[4].parenthetical = false; },
    overlap_removed: c => { c.records.find(r => r.deh.key === '5.53.1').josephus.targets[5].section_start = 370; },
    approved_bj_endpoint_changed: c => { c.records.find(r => r.deh.key === '4.30.2').josephus.targets[0].section_end = 663; },
    confirmed_correction_reverted: c => { c.records.find(r => r.deh.key === '2.11.3').josephus.targets[1].section_start = 290; },
    raw_evidence_lost: c => { c.records[0].source.raw_values.josephus = ''; },
    no_parallel_record_missing: c => { c.records.find(r => r.deh.key === '1.3.1').josephus.status = 'original_material'; },
    confirmed_supplementary_role_lost: c => { c.records.find(r => r.deh.key === '2.9.2').josephus.targets[1].relationship_role = 'primary_parallel'; },
    confirmed_interpretation_provenance_lost: c => { delete c.records.find(r => r.deh.key === '2.9.2').applied_editorial_decisions; },
    confirmed_inline_reference_reordered: c => { c.records.find(r => r.deh.key === '2.9.2').josephus.targets.reverse(); },
    canonical_bj_endpoint_absent: c => { c.records[0].josephus.targets[0].section_end = 9999; },
    approved_bj_range_reopened: c => { const t = c.records.find(r => r.deh.key === '4.30.2').josephus.targets[0]; t.section_end = null; t.open_ended = true; },
    approved_aj_range_reopened: c => { const t = c.records.find(r => r.deh.key === '2.13.7').josephus.targets[1]; t.section_end = null; t.open_ended = true; },
    parenthetical_uncertainty_reintroduced: c => { c.records.find(r => r.deh.key === '1.26.3').josephus.targets[1].editorial_status = 'parenthetical_meaning_unresolved'; },
    primary_role_changed: c => { c.records[0].josephus.targets[0].relationship_role = 'supplementary_parallel'; },
    supplementary_first_sequence_reordered: c => { c.records.find(r => r.deh.key === '3.8.2').josephus.targets.reverse(); },
    alii_attached_to_bj: c => { c.records.find(r => r.deh.key === '1.37.4').josephus.annotations[0].target_orders = [1]; },
    historia_made_work_identity: c => { c.records.find(r => r.deh.key === '1.6.4').josephus.annotations[0].type = 'modern_work_identity'; },
    annotation_promoted_to_target: c => { c.records.find(r => r.deh.key === '1.6.4').josephus.targets.push({ work: 'AJ', book: 1, section_start: 1, section_end: 1 }); },
    residue_exposed_as_reference: c => { c.records.find(r => r.deh.key === '5.53.2').other_works = { text: '\\\\', status: 'reference_recorded_unparsed' }; },
    frozen_status_lost: c => { c.status = 'candidate_for_editorial_review'; },
    raw_open_notation_erased: c => { c.records.find(r => r.deh.key === '2.13.7').source.raw_values.josephus = 'AJ 20.247-249, 15.38-56'; },
    publication_status_changed: c => { c.publication_status = 'published'; }
  };
  for (const [name, mutate] of Object.entries(mutations)) {
    const copy = structuredClone(candidate); mutate(copy);
    assert.throws(() => validate(copy, workbook, decisions, corpus), { name: 'AssertionError' }, `Validator accepted ${name}`);
  }
  return Object.keys(mutations);
}

function main() {
  const [command = 'validate', argument] = process.argv.slice(2);
  assert.ok(['freeze', 'validate'].includes(command), 'Usage: node bin/deh-concordance.mjs freeze <zip> | validate [--self-test]');
  if (command === 'validate') assert.ok(!argument || argument === '--self-test', 'Unknown validation option');
  projectEditorial = readJSON(files.projectDecisions);
  assert.equal(projectEditorial.version, '2');
  assert.equal(projectEditorial.date, '2026-10-02');
  assert.deepEqual(projectEditorial.confirmed.map(d => d.id), ['P3-D01', ...Array.from({ length: 11 }, (_, i) => `P4-D${String(i + 1).padStart(2, '0')}`)]);
  assert.deepEqual([projectEditorial.confirmed[1].primary_role, projectEditorial.confirmed[1].parenthetical_role], ['primary_parallel', 'supplementary_parallel']);
  assert.ok(projectEditorial.confirmed.slice(1).every(d => d.authority && d.adjudication_date === '2026-10-02'));
  const clarification = projectEditorial.confirmed[0];
  assert.equal(clarification.id, 'P3-D01');
  assert.equal(clarification.deh, '2.9.2');
  assert.equal(clarification.raw_source_notation, '2.402(344)-404');
  assert.deepEqual(clarification.targets, [
    { work: 'BJ', book: 2, section_start: 402, section_end: 404, open_ended: false, parenthetical: false, relationship_role: 'primary_parallel' },
    { work: 'BJ', book: 2, section_start: 344, section_end: 344, open_ended: false, parenthetical: true, relationship_role: 'supplementary_parallel' }
  ]);
  const parentheticalShapes = {
    '1.26.3': [[1, 210, 211, false], [1, 205, 205, true]],
    '1.29.3': [[1, 255, 257, false], [1, 248, 248, true]],
    '1.30.13': [[1, 328, 329, false], [1, 339, 339, true]],
    '3.8.2': [[3, 110, 114, true], [3, 115, 115, false], [3, 127, 127, false], [3, 132, 134, false]],
    '5.53.1': [[7, 320, 322, false], [7, 341, 359, false], [7, 323, 334, false], [7, 360, 369, false], [2, 487, 498, true], [7, 369, 388, false], [7, 335, 336, false]]
  };
  for (const [key, expected] of Object.entries(parentheticalShapes)) assert.deepEqual(
    projectEditorial.confirmed.find(d => d.deh === key).targets.map(t => [t.book, t.section_start, t.section_end, t.parenthetical]), expected,
    `Fixed parenthetical decision changed: ${key}`);
  const corpus = native(['-Mode', 'Corpus', '-RepoRoot', root]);
  let candidate, workbook, decisions;
  if (command === 'freeze') {
    assert.ok(argument && !argument.startsWith('--'), 'Supply the source ZIP path');
    const input = native(['-Mode', 'Package', '-PackagePath', path.resolve(argument)]);
    const packaged = JSON.parse(input.files['deh-parallels.json']);
    workbook = JSON.parse(input.files['source/workbook_values.json']);
    decisions = JSON.parse(input.files['editorial_decisions.json']);
    const base = sourceRecords(workbook, decisions, corpus);
    const configuration = readerConfiguration();
    assert.deepEqual(base, packaged.records, 'STOP: source package differs from source rows, confirmed decisions, or current canonical identities');
    assertPilot(base);
    candidate = {
      schema_version: '0.2', concordance_extension_version: '2', date: '2026-10-02', status: 'reviewed_frozen', publication_status: 'reviewed_not_published',
      relation_type: packaged.relation_type,
      scope: { work: 'DEH', numbered_records: 555, prologue_included: false },
      source_package: { filename: path.basename(argument), sha256: input.sha256, entry_sha256: input.hashes },
      package_provenance: packaged.provenance,
      retained_evidence: { workbook_values: files.workbook, editorial_decisions: files.decisions },
      project_editorial_decisions: { path: files.projectDecisions, sha256: hash(read(files.projectDecisions)) },
      review: { human_approved: true, authority: projectEditorial.authority, adjudication_date: projectEditorial.date,
        parallel_role_decision: 'P4-D01', phase3_baseline_commit: '0c95013d738ab6f471e34a1fc62d1e76e460b705',
        raw_evidence_retained: true, site_support_limitations_are_editorial_defects: false },
      conventions: { ...packaged.conventions,
        parentheses: 'Parenthetical targets are human-approved supplementary parallels; unparenthesized targets are primary parallels. Parentheses do not mark uncertainty or establish textual dependence. Source sequence and typographical position are preserved.',
        blank_bj_aj_display: "No BJ/AJ parallel is recorded in the edition's references.",
        normalized_targets: 'josephus.targets is the ordered reviewed sequence with adjudicated endpoints. josephus.segments preserves the source-notation parse, including inherited et sqq.; its parenthetical meanings are adjudicated. Original package questions are historical evidence under source.package_questions and have explicit record-level resolutions.',
        other_works: 'Meaningful source strings remain unnormalized. The V.53.2 backslashes survive only in immutable raw evidence snapshots; its reviewed Other works is empty.',
        aj_availability: 'AJ site-support limitations are technical limitations, not editorial defects. Parsing does not establish current Niese addressability. No unsupported site links or IDs are generated.' },
      canonical_xml_sha256: corpus.xml_sha256,
      records: base.map(r => normalize(r, corpus, configuration))
    };
    validate(candidate, workbook, decisions, corpus);
    assert.equal(exceptions(candidate.records).length, 0, 'STOP: editorial exceptions prevent the freeze');
    // All identity, coverage and pilot checks pass before any candidate write.
    write(files.workbook, input.files['source/workbook_values.json']);
    write(files.decisions, input.files['editorial_decisions.json']);
    write(files.concordance, json(candidate));
  } else {
    candidate = readJSON(files.concordance); workbook = readJSON(files.workbook); decisions = readJSON(files.decisions);
    assert.equal(hash(read(files.workbook)), candidate.source_package.entry_sha256['source/workbook_values.json'], 'Workbook evidence changed');
    assert.equal(hash(read(files.decisions)), candidate.source_package.entry_sha256['editorial_decisions.json'], 'Editorial evidence changed');
    validate(candidate, workbook, decisions, corpus);
  }
  const report = audit(candidate, corpus);
  assert.equal(hash(read(files.concordance)), report.reviewed_concordance.sha256, 'Frozen artifact bytes differ from recorded SHA-256');
  if (command === 'freeze') { write(files.audit, json(report)); write(files.exceptions, exceptionMarkdown(report)); }
  else { assert.deepEqual(readJSON(files.audit), report, 'Audit is stale'); assert.equal(read(files.exceptions), exceptionMarkdown(report), 'Exception report is stale'); }
  const rejected = argument === '--self-test' ? selfTest(candidate, workbook, decisions, corpus) : [];
  console.log(json({ status: report.status, reviewed_concordance: report.reviewed_concordance, statistics: report.statistics, deh: report.deh, bellum: report.bellum,
    antiquities: { normalized: report.antiquities.normalized_components, site_addressable: report.antiquities.site_addressable_closed, not_site_addressable: report.antiquities.not_site_addressable },
    pilot: report.pilot, review: report.review,
    site_support_limitations: { records: report.site_support_limitations.records, components: report.site_support_limitations.target_components },
    provenance_only_residues: report.provenance_only_residues.records, rejected_mutations: rejected }));
}

try { main(); } catch (error) { console.error(`Concordance audit failed: ${error.message}`); process.exitCode = 1; }
