/* DEH's structured CSV convention. It is independent of the Josephus symbol key. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.DEHManuscriptAnnotations = api;
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const convention = 'deh-csv-20261027';
  let dataset = null;
  function setData(data) {
    if (data?.convention !== convention || data.schemaVersion !== 1
        || !Array.isArray(data.records) || data.records.length !== data.source?.recordCount
        || new Set(data.records.map(row => row.presentationId)).size !== data.records.length) {
      throw new Error('Invalid DEH manuscript annotation dataset');
    }
    dataset = data;
  }
  function resolveManuscript(siglum) {
    const row = dataset?.manuscripts[siglum];
    return row ? [row.displayName, row.repository, row.shelfmark, row.catalogueId] : null;
  }
  function recordsForBook(book) {
    return (dataset?.records || []).filter(row => row.book === Number(book))
      .sort((a, b) => a.chapter - b.chapter || a.sourceRow - b.sourceRow).map(row => ({
      work: 'deh', sourceConvention: convention, sourceBook: row.book,
      presentationId: row.presentationId, originalId: null, alignmentUnitId: null,
      locationTargetId: row.locationTargetId, locationGranularity: 'chapter',
      coveredAlignmentUnitIds: [...row.coveredAlignmentUnitIds], sourceRow: row.sourceRow,
      originalCSVRow: {...row.original}, sourceHand: row.original.main,
      originalAlignmentReference: row.original.section, siglum: row.original.manuscrit,
      notation: row.original.contenu, folioReference: row.original.folio,
      pagination: dataset.manuscripts[row.original.manuscrit]?.pagination || 'folio',
      sourceIssues: [...row.issues], chapter: row.chapter
    }));
  }
  function interpret(record) {
    if (record.work !== 'deh' || record.sourceConvention !== convention) return null;
    const original = record.notation ?? '';
    const hand = record.sourceHand?.match(/^\d+-(\d+)$/u);
    const onlyGap = /^(?:\s*\[\*\]\s*)+$/u.test(original);
    return {originalRecord: record, originalNotation: original,
      canonicalAnnotationId: record.originalId || null, alignmentUnitId: null,
      anchor: record.presentationId, folios: [], issues: [],
      parts: [{notation: original, text: original, offset: 0, codes: [], description: '',
        hand: hand ? Number(hand[1]) : null, handCode: null,
        folio: {original: record.folioReference, reference: record.folioReference, firstOccurrence: null},
        pagination: record.pagination, category: onlyGap ? 'untranscribable' : 'textual',
        transcriptionStatus: original.includes('[*]') && !onlyGap ? 'partial' : null,
        suppressCompletenessLabel: true, abbreviated: false, issues: []}]};
  }
  function textSegments(part, lang) {
    if (part.category === 'untranscribable') return [];
    return part.text.split(/(\[\*\])/u).filter(Boolean).map(segment => segment === '[*]'
      ? {kind: 'editorial', original: segment, text: lang === 'fr' ? '[texte non transcrit]' : '[untranscribed text]'}
      : {kind: 'recorded', original: segment, text: segment.replaceAll('\\c{e}', 'ę')});
  }
  function legend(lang, escape) {
    const text = lang === 'fr' ? [
      'Les références de ces annotations désignent un chapitre entier du De excidio.',
      'Les Détails scientifiques conservent les cinq champs utilisés du fichier source, leur numéro de ligne et les codes originaux de main.',
      'Les mains sont numérotées au sein de chaque manuscrit : 678-1 désigne la Main 1 de Cambrai 678. Un code non numérique n’est pas converti en numéro de main.',
      'La notation \\c{e} est affichée comme e caudata (ę). [*] est interprété comme un passage non transcrit suivant l’indication provisoire de l’éditeur. Le texte original est conservé dans les Détails scientifiques.',
      'St. Gall 626 est paginé : ses références sont affichées avec p. Les autres références suivent la colonne folio. Les points de suspension sont conservés sans appliquer la convention propre à Josèphe.'
    ] : [
      'These annotations refer to whole chapters of De excidio.',
      'Scholarly details preserve the five source fields used here, the CSV row number and original hand codes.',
      'Hands are numbered within each manuscript: 678-1 identifies Hand 1 in Cambrai 678. Non-numeric codes are not converted into hand numbers.',
      'The notation \\c{e} is displayed as e caudata (ę). [*] is interpreted as untranscribed text following the editor’s provisional clarification. Scholarly details retain the original wording.',
      'St. Gall 626 is paginated, so its references use p. Other references follow the folio column. Ellipses are preserved without applying the Josephus abbreviation convention.'
    ];
    return `<details class="annotation-about"><summary>${lang === 'fr' ? 'À propos de ces annotations' : 'About these annotations'}</summary>${text.slice(0, 2).map(p => `<p>${escape(p)}</p>`).join('')}<div class="annotation-notation-key">${text.slice(2).map(p => `<p>${escape(p)}</p>`).join('')}</div></details>`;
  }
  return {setData, recordsForBook, resolveManuscript, interpret, textSegments, legend};
});
