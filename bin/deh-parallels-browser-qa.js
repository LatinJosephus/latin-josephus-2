import {
  publicationRecords, loadConcordance, createTextLoader, bjTargets,
  dehParagraphs, bellumIndex, bellumSection, namespaceIds
} from '../assets/js/dehParallelsCore.js';

const status = document.getElementById('qa-status');
const output = document.getElementById('qa-result');
const normalize = text => text.replace(/\[\s*\d+\s*\]/g, '').replace(/\s+/g, ' ').trim();
const assert = (condition, message) => { if (!condition) throw new Error(message); };

// Independent text-node traversal of the canonical body, avoiding DOM Range.
// This detects lost/extra text in the production cloneContents extraction.
function canonicalSections(index) {
  if (index.entries[0].wholeSection) return new Map(index.entries.map(entry => [entry.number, normalize(entry.node.textContent)]));
  const boundaries = new Map(index.entries.map(entry => [entry.node, entry.number]));
  const texts = new Map();
  let current;
  const visit = node => {
    if (boundaries.has(node)) current = boundaries.get(node);
    if (node.nodeType === Node.TEXT_NODE && current) texts.set(current, (texts.get(current) || '') + node.textContent);
    node.childNodes.forEach(visit);
  };
  visit(index.body);
  return new Map([...texts].map(([number, text]) => [number, normalize(text)]));
}

document.getElementById('run').addEventListener('click', async event => {
  event.target.disabled = true;
  output.textContent = '';
  delete output.dataset.complete;
  status.textContent = 'Checking the full reviewed concordance…';
  const result = { passed: false, componentChecks: [], failures: [] };
  const began = performance.now();
  try {
    const data = await loadConcordance('/assets/data/deh-josephus-concordance.json');
    const records = publicationRecords(data);
    const expected = data.records.filter(record => bjTargets(record).length);
    assert(records.length === expected.length, 'Publication coverage differs from frozen BJ targets');
    assert(records.every((record, index) => record === expected[index]), 'DEH record order changed');
    result.reviewedRecords = data.records.length;
    result.eligibleRecords = records.length;
    result.noBjRecords = data.records.filter(record => !bjTargets(record).length).map(record => record.id);
    assert(result.noBjRecords.every(id => !records.some(record => record.id === id)), 'No-BJ entry was published');
    assert(!records.some(record => /^latin-deh1-num[123]$/.test(record.deh.xml_id)), 'Prologue was published');
    result.bjComponents = records.reduce((sum, record) => sum + bjTargets(record).length, 0);
    result.supplementaryComponents = records.reduce((sum, record) => sum + bjTargets(record)
      .filter(target => target.relationship_role === 'supplementary_parallel').length, 0);
    const loadText = createTextLoader(new URL('/assets/xml/', location.href), data.canonical_xml_sha256);
    result.dehSourceChecks = 0;
    for (const record of data.records) {
      for (const source of ['ussani', 'pollard']) {
        const paragraphs = dehParagraphs(await loadText(source, record.deh.book), record, source);
        assert(paragraphs.length > 0 && paragraphs.some(paragraph => normalize(paragraph.textContent)), `${record.id}: empty ${source}`);
        if (source === 'ussani') {
          assert(paragraphs.length === 1, `${record.id}: duplicated canonical DEH target`);
          assert(paragraphs[0].querySelector('tei-num')?.textContent.trim() === `[${record.deh.citation}]`, `${record.id}: wrong canonical citation`);
        }
        result.dehSourceChecks++;
      }
    }
    result.finalBoundaryChecks = 0;
    result.sectionOccurrences = 0;
    for (const source of ['niese', 'cardwell', 'whiston']) {
      const indexes = new Map();
      const references = new Map();
      for (const record of records) {
        const targets = bjTargets(record);
        assert(targets.every((target, index) => index === 0 || target.order > targets[index - 1].order), `${record.id}: reordered BJ components`);
        for (const target of targets) {
          try {
            if (!indexes.has(target.book)) {
              const index = bellumIndex(await loadText(source, target.book), source, target.book);
              indexes.set(target.book, index);
              references.set(target.book, canonicalSections(index));
              const final = bellumSection(index, index.entries.length);
              assert(normalize(final.textContent) === references.get(target.book).get(index.entries.length), `${source}: final body boundary`);
              assert(!final.querySelector('tei-standOff, tei-back, tei-listapp'), `${source}: final excerpt includes back matter`);
              result.finalBoundaryChecks++;
            }
            const component = document.createElement('div');
            for (let section = target.section_start; section <= target.section_end; section++) {
              const excerpt = bellumSection(indexes.get(target.book), section);
              assert(Number(excerpt.dataset.nieseSection) === section, `${source}: incorrect Niese coordinate`);
              assert(normalize(excerpt.textContent) === references.get(target.book).get(section), `${source} BJ ${target.book}.${section}: text mismatch`);
              component.appendChild(namespaceIds(excerpt, `qa-${target.order}-${section}`));
              result.sectionOccurrences++;
            }
            const sections = [...component.querySelectorAll('[data-niese-section]')];
            assert(sections.length === target.section_end - target.section_start + 1, `${record.id}: incomplete range`);
            const ids = [...component.querySelectorAll('[id]')].map(node => node.id);
            assert(new Set(ids).size === ids.length, `${record.id}: duplicate excerpt IDs`);
            result.componentChecks.push({ record: record.id, order: target.order, book: target.book,
              start: target.section_start, end: target.section_end, source, passed: true });
          } catch (error) {
            result.failures.push({ record: record.id, order: target.order, source, error: error.message });
          }
        }
      }
    }
    result.eligibilityGuardChecks = 0;
    const mutations = [
      changed => { changed.status = 'unreviewed'; },
      changed => { changed.review.human_approved = false; },
      changed => { changed.scope.prologue_included = true; },
      changed => { changed.records.pop(); },
      changed => { changed.records[1].id = changed.records[0].id; },
      changed => { changed.records[0].josephus.targets[0].open_ended = true; },
      changed => { changed.records[0].josephus.targets[0].validation.sources.Greek = false; },
      changed => { changed.records[0].josephus.targets[0].relationship_role = 'uncertain'; }
    ];
    for (const mutate of mutations) {
      const changed = structuredClone(data);
      mutate(changed);
      let rejected = false;
      try { publicationRecords(changed); } catch { rejected = true; }
      assert(rejected, 'Publication accepted corrupt/unapproved data');
      result.eligibilityGuardChecks++;
    }
    assert(!result.failures.length && result.componentChecks.length === result.bjComponents * 3, 'Some BJ extraction checks failed');
    result.passed = true;
  } catch (error) {
    result.failures.push({ error: error.message });
  }
  result.elapsedMs = Math.round(performance.now() - began);
  output.textContent = JSON.stringify(result, null, 2);
  status.textContent = result.passed ? `PASS: ${result.componentChecks.length} BJ source extraction checks` : 'FAIL: inspect results';
  output.dataset.complete = 'true';
  event.target.disabled = false;
});
