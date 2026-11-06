/* Editor-approved presentation additions, 27 October 2026.
   Frozen XML and original worksheet notation remain unchanged. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.AnnotationEditorialUpdates = factory();
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const bodmerNotation = '[¤1v](@1).d significe. sabatum (@2) de adam (@3)issa si a uira diuisat';
  return {
    date: '2026-10-27',
    manuscriptAttributions: {
      date: '2026-11-06',
      reviewer: 'Jean-Félix Aubé-Pronce',
      entries: [
        {book: 1, unit: 'latin-book01-num52', sourceSiglum: '', siglum: 'LeidenUBVLF17',
          notation: '[1v] (@2) de cain et abel (@3)de cain'},
        {book: 1, unit: 'latin-book01-num148', sourceSiglum: 'book-04#latin-book04-num118', siglum: 'BernBBMs118',
          notation: '[10v] (£3) natus abraham (£4) ciuitas undicitur [¤11r] (@1) caute'},
        {book: 1, unit: 'latin-book01-num228', sourceSiglum: '', siglum: 'BernBBMs118',
          notation: '[16r] (@3) uata habrahe ad filium suum cum eum uellet immolare'},
        // The Leiden fragment is alongside the fuller Laban readings. Its
        // manuscript is identified even though its alignment ID is missing.
        {book: 1, unit: '', sourceSiglum: '', siglum: 'LeidenUBVLF17', notation: '[7r](@2)*erui *ba'},
        {book: 3, unit: 'latin-book03-num212', sourceSiglum: '', siglum: 'RomeBAVPalLat814',
          notation: '[¤32r](¢1)legem moyses scripsit'},
        {book: 8, unit: 'latin-book08-num401', sourceSiglum: '', siglum: 'MilanBACimelioSP',
          notation: '[¤138] (@1) micheas propheta (@2) *solutus'},
        {book: 11, unit: 'latin-book11-num195', sourceSiglum: 'latin-book11-num195', siglum: 'RomeBAVPalLat814',
          notation: '[¤129v](£1)pieta'}
      ]
    },
    bern: {
      work: 'antiquities', sourceBook: 1, alignmentUnitId: 'latin-book01-num34', siglum: 'BernBBMs118',
      notation: '[¤2v] (§) dicit (@1) issa (#2 nota NT)',
      explanation: {
        en: 'The editor confirms that untranscribed material precedes the surviving word dicit.',
        fr: 'L’éditeur confirme qu’un passage non transcrit précède le mot conservé dicit.'
      },
      provisionalReading: {en: 'david [uncertain text] dicit', fr: 'david [texte incertain] dicit'}
    },
    bodmer: {
      work: 'antiquities', sourceBook: 1, siglum: 'ColognyBodmer98', notation: bodmerNotation,
      source: 'Annotations - Latin Antiquities (libri I-XII).xlsx', sheet: 'Feuil1', cell: 'E11',
      facsimile: 'https://www.e-codices.unifr.ch/en/fmb/cb-0098/1v',
      entries: [
        {id: 'bodmer98-e11-1', prefix: '(@1)', alignmentUnitId: 'latin-book01-num27'},
        {id: 'bodmer98-e11-2', prefix: '(@2)', alignmentUnitId: 'latin-book01-num34'},
        {id: 'bodmer98-e11-3', prefix: '(@3)', alignmentUnitId: 'latin-book01-num34',
          displayText: 'issa si a uiro diuisa',
          explanation: {
            en: 'Reviewed reading: uiro and diuisa follow the editorial review against the project’s Latin. The worksheet word si remains uncertain.',
            fr: 'Lecture révisée : uiro et diuisa suivent la révision éditoriale fondée sur le latin du projet. Le mot si de la feuille de calcul reste incertain.'
          }}
      ]
    }
  };
});
