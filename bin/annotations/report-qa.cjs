/* Deterministic notation inventory and explicit exceptions. No scholarly source writes. */
const fs = require('node:fs'), path = require('node:path');
const api = require('../../assets/js/manuscriptAnnotations.js');
const citations = require('../../assets/data/alignment-citations.json');
const inventory = require('../../_docs/annotation-source-inventory.json');
api.setCitationData(citations);
const output = path.resolve(__dirname, '../../_docs/annotation-display');
fs.mkdirSync(output, {recursive: true});
const report = {sourceRecords: inventory.records.length, works: {}, exceptions: [], sourceConvention: 'Josephus editorial instructions, including the editor’s counting-system clarification supplied 26 October 2026',
  sourceXMLModified: false, canonicalAnnotationIdsEncoded: 0, displayAnchorsAreCanonicalIds: false};
const add = (object, key) => object[key] = (object[key] || 0) + 1;
for (const r of inventory.records) {
  const parsed = api.interpretManuscriptAnnotation(r), citation = api.resolveAlignmentCitation(r.work, r.alignmentUnitId);
  const ms = api.resolveManuscript(r.siglum, r.witnessLabel);
  const stats = report.works[r.work] ||= {records: 0, components: 0, folioOnlyRecords: 0, verifiedCitationRecords: 0,
    unlocatedRecords: 0, fullyInterpretedRecords: 0, categories: {}, hands: {}, codes: {}, issues: {},
    confirmedAbbreviations: 0, unresolvedEllipses: 0, firstFolioMarkers: 0, repeatedFolioReferences: 0};
  stats.records++; stats.components += parsed.parts.length;
  if (!parsed.parts.length) stats.folioOnlyRecords++;
  if (citation.verificationStatus === 'verified') stats.verifiedCitationRecords++; else stats.unlocatedRecords++;
  if (!parsed.issues.length && parsed.parts.every(p => p.category !== 'unresolved')) stats.fullyInterpretedRecords++;
  for (const folio of parsed.folios) {
    if (folio.firstOccurrence) stats.firstFolioMarkers++; else if (folio.verified) stats.repeatedFolioReferences++;
  }
  for (const part of parsed.parts) {
    add(stats.categories, part.category); add(stats.hands, String(part.hand || 'unknown'));
    for (const code of part.codes) add(stats.codes, code);
    if (part.abbreviated) stats.confirmedAbbreviations++;
    if (part.ellipsisUnresolved) stats.unresolvedEllipses++;
  }
  for (const issue of parsed.issues) add(stats.issues, issue);
  const reasons = [...new Set(parsed.issues)];
  if (citation.verificationStatus !== 'verified') reasons.push('passage-reference-unresolved');
  if (ms.verificationStatus !== 'verified') reasons.push('manuscript-' + ms.verificationStatus);
  if (!parsed.parts.length) reasons.push('folio-only-no-annotation');
  if (reasons.length) report.exceptions.push({...r, displayAnchor: parsed.anchor, reasons,
    publicCitation: citation.publicCitation, manuscriptStatus: ms.verificationStatus});
}
fs.writeFileSync(path.join(output, 'notation-qa.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({sourceRecords: report.sourceRecords, works: report.works, exceptionRecords: report.exceptions.length}, null, 2));
