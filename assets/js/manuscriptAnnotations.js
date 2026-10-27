/* Presentation only. Frozen TEI, original notation and associations are inputs.
   Classic script for the existing reader; CommonJS export for dependency-free QA. */
(function (root, factory) {
  const editorialEnglish = typeof module === 'object' && module.exports
    ? require('./annotationEditorialEnglish.js') : root.AnnotationEditorialEnglish;
  const api = factory(editorialEnglish);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ManuscriptAnnotations = api;
})(typeof globalThis === 'object' ? globalThis : this, function (editorialEnglish) {
  'use strict';
  let citationData = {works: {}};
  const workNames = {antiquities: 'Antiquities', bellum: 'Bellum', deh: 'De excidio'};
  const labels = {
    en: {heading: 'Manuscript annotations', about: 'About these annotations', details: 'Scholarly details',
      passage: 'View passage', manuscript: 'Manuscript', hand: 'Hand', symbolic: 'Symbolic annotation',
      untranscribable: 'Cannot be transcribed', unresolved: 'Notation requires review',
      abbreviated: 'Transcription abbreviated', abbreviationHelp: 'Only the beginning of this annotation was transcribed.',
      unknown: 'Not recorded', noId: 'No original annotation ID encoded', original: 'Original editorial notation',
      sourceId: 'Original annotation ID', unit: 'Original alignment-unit ID', siglum: 'Original manuscript siglum',
      shelfmark: 'Manuscript designation', folio: 'Full folio notation', codes: 'Editorial codes',
      completeness: 'Transcription status', recorded: 'Recorded text; completeness not otherwise specified',
      uncertainEllipsis: 'Ellipsis retained; editorial role unresolved', first: 'First recorded occurrence of this folio reference',
      subsequent: 'Folio reference without a first-occurrence marker', sourceNumber: 'Original annotation number',
      unverified: 'Textual citation not verified', annotations: 'annotations', review: 'Unresolved notation retained below',
      noTranscription: 'No transcription recorded', editorialNote: 'Editorial note'},
    fr: {heading: 'Annotations manuscrites', about: 'À propos de ces annotations', details: 'Détails scientifiques',
      passage: 'Voir le passage', manuscript: 'Manuscrit', hand: 'Main', symbolic: 'Annotation symbolique',
      untranscribable: 'Ne peut être transcrite', unresolved: 'Notation à vérifier',
      abbreviated: 'Transcription abrégée', abbreviationHelp: 'Seul le début de cette annotation a été transcrit.',
      unknown: 'Non indiqué', noId: 'Aucun identifiant original d’annotation encodé', original: 'Notation éditoriale originale',
      sourceId: 'Identifiant original de l’annotation', unit: 'Identifiant original de l’unité d’alignement',
      siglum: 'Sigle original du manuscrit', shelfmark: 'Désignation du manuscrit', folio: 'Notation complète du folio',
      codes: 'Codes éditoriaux', completeness: 'État de la transcription', recorded: 'Texte enregistré ; intégralité non précisée',
      uncertainEllipsis: 'Points de suspension conservés ; fonction éditoriale non établie',
      first: 'Première occurrence enregistrée de cette référence au folio',
      subsequent: 'Référence au folio sans marque de première occurrence', sourceNumber: 'Numéro original de l’annotation',
      unverified: 'Référence textuelle non vérifiée', annotations: 'annotations', review: 'Notation non résolue conservée ci-dessous',
      noTranscription: 'Aucune transcription enregistrée', editorialNote: 'Note éditoriale'}
  };
  const language = lang => labels[lang] ? lang : 'en';
  const t = lang => labels[language(lang)];
  const escape = text => String(text ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  // Expansions are verified against listWit and the site's manuscript repertory.
  // Shelfmark conflicts retain listWit wording and are explicitly flagged.
  const manuscripts = {
    BernBBMs50: ['Bern, Burgerbibliothek, Ms. 50', 'Burgerbibliothek', 'Ms. 50', 'M0083'],
    BernBBMs118: ['Bern, Burgerbibliothek, Ms. 118', 'Burgerbibliothek', 'Ms. 118', 'M0084'],
    BernBBMs183: ['Bern, Burgerbibliothek, Ms. 183', 'Burgerbibliothek', 'Ms. 183', 'M0082'],
    ChartresBMMs29: ['Chartres, Bibliothèque municipale, Ms. 29', 'Bibliothèque municipale', 'Ms. 29', 'M0129'],
    ColognyBodmer98: ['Cologny, Fondation Martin Bodmer, Ms. 98', 'Fondation Martin Bodmer', 'Ms. 98', 'M0139'],
    ColognyBodmer99: ['Cologny, Fondation Martin Bodmer, Ms. 99', 'Fondation Martin Bodmer', 'Ms. 99', 'M0140'],
    CopenhagenGKS1572o: ['Copenhagen, Kongelige Bibliotek, GKS 157 fol.', 'Kongelige Bibliotek', 'GKS 157 fol.', 'M0142'],
    LeidenUBVLF17: ['Leiden, Universitaire Bibliotheken, VLF 17', 'Universitaire Bibliotheken', 'VLF 17', 'M0224'],
    MilanBACimelioSP: ['Milan BA Cimelio S.P. 11/1', null, 'Cimelio S.P. 11/1', null, 'shelfmark-conflict'],
    MonzaBCMsb20: ['Monza, Biblioteca capitolare, b20/136', 'Biblioteca capitolare', 'b20/136', 'M0294'],
    RomeBAVPalLat814: ['Rome, Biblioteca Apostolica Vaticana, Pal. lat. 814', 'Biblioteca Apostolica Vaticana', 'Pal. lat. 814', 'M0495'],
    MonteCassino123: ['Montecassino, Biblioteca dell’Abbazia, Casin. 123', 'Biblioteca dell’Abbazia', 'Casin. 123', 'M0288'],
    RomeBAVPallat1992: ['Rome BAV Pal. lat. 1992', null, 'Pal. lat. 1992', null, 'shelfmark-conflict'],
    StGallSBcod627: ['St. Gallen, Stiftsbibliothek, Csg 627', 'Stiftsbibliothek', 'Csg 627', 'M0509']
  };
  const englishManuscriptNames = {
    ChartresBMMs29: 'Chartres, Municipal Library, Ms. 29',
    ColognyBodmer98: 'Cologny, Martin Bodmer Foundation, Ms. 98',
    ColognyBodmer99: 'Cologny, Martin Bodmer Foundation, Ms. 99'
  };
  function resolveManuscript(siglum, fallback, lang = 'en') {
    const row = manuscripts[siglum];
    return {siglum, displayName: (lang === 'en' && englishManuscriptNames[siglum]) || row?.[0] || fallback || siglum,
      originalDisplayName: row?.[0] || fallback || siglum, repository: row?.[1] || null,
      shelfmark: row?.[2] || null, url: row?.[3] ? `/manuscripts/#ljm-${row[3]}` : null,
      verificationStatus: row ? row[4] || 'verified' : 'unresolved'};
  }
  function setCitationData(data) { citationData = data; }
  function resolveAlignmentCitation(work, alignmentUnitId, options = {}) {
    const lang = language(options.lang), l = t(lang);
    const row = citationData.works?.[work]?.[alignmentUnitId];
    const verified = row?.status === 'verified';
    const ranges = row?.intervals || [];
    let citation = l.unverified;
    if (verified && row.citationSystem === 'deh') citation = row.citation;
    else if (verified) {
      const numbers = ranges.map(([a, b]) => a === b ? String(a) : `${a}–${b}`).join(', ');
      const sign = ranges.length === 1 && ranges[0][0] === ranges[0][1] ? '§' : '§§';
      const book = row.book === 'preface' ? (lang === 'fr' ? 'Préface' : 'Preface') : `${lang === 'fr' ? 'Livre' : 'Book'} ${row.book}`;
      citation = `${book}, Niese ${sign}${numbers}`;
    }
    const prefix = workNames[work] || work;
    let navigationTarget = null;
    if (row) {
      const unit = alignmentUnitId.match(/-num(\d+[a-z]*)$/)?.[1];
      navigationTarget = `/${work === 'bellum' ? 'bellum-judaicum' : work}/?book=${row.book}` + (unit ? (row.citationSystem === 'deh' && row.chapter != null
        ? `&chapter=${row.chapter}&unit=${row.unit}` : `&unit=${unit}`) : '') + `#${encodeURIComponent(alignmentUnitId)}`;
    }
    return {work, alignmentUnitId, publicCitation: options.includeWork ? `${prefix}, ${citation}` : citation,
      citationSystem: row?.citationSystem || (work === 'deh' ? 'deh' : 'niese'), intervals: ranges.map(r => [...r]),
      start: ranges[0]?.[0] ?? (row?.citationSystem === 'deh' ? row.citation : null),
      end: ranges.at(-1)?.[1] ?? (row?.citationSystem === 'deh' ? row.citation : null),
      navigationTarget, verificationStatus: row?.status || 'unresolved', provenance: [...(row?.provenance || [])]};
  }
  function recordAnchor(record) {
    if (record.originalId) return record.originalId;
    // A display anchor, explicitly not a newly asserted scholarly identifier.
    return ['ms-annotation', record.work, String(Number(record.sourceBook) || record.sourceBook || 'source'), record.alignmentUnitId, record.siglum, record.occurrence || 1]
      .map(v => encodeURIComponent(v || 'unknown')).join('-');
  }
  function interpretManuscriptAnnotation(record) {
    const original = record.notation ?? '';
    const result = {originalRecord: record, originalNotation: original, canonicalAnnotationId: record.originalId || null,
      alignmentUnitId: record.alignmentUnitId, anchor: recordAnchor(record), parts: [], folios: [], issues: []};
    // The Josephus key is source specific. DEH requires a separately certified adapter.
    if (!['antiquities', 'bellum'].includes(record.work)) {
      result.parts.push({notation: original, text: original, category: 'unresolved', hand: null,
        folio: null, offset: 0, abbreviated: false, issues: ['source-convention-unconfigured']});
      result.issues.push('source-convention-unconfigured');
      return result;
    }
    let folio = null, current = null, cursor = 0;
    const finish = () => {
      if (!current) return;
      current.text = current.text.trim();
      if (current.category === 'unresolved' && current.text && !current.codes.length) current.issues.push('unparsed-notation');
      if (current.category === 'textual' && /^§(?:\s|$)/u.test(current.text)) {
        current.category = 'untranscribable'; current.text = current.text.slice(1).trim();
        current.codes.push('§');
      }
      // Confirmed by the recovered instruction and its three-word example.
      // Unicode …, medial ellipses and other lengths remain unclassified.
      current.abbreviated = current.category === 'textual' && /^\S+\s+\S+\s+\S+\s*\.\.\.$/u.test(current.text);
      current.ellipsisUnresolved = /\.{2,}|…/u.test(current.text) && !current.abbreviated;
      if (current.ellipsisUnresolved) current.issues.push('ellipsis-role-unresolved');
      if (current.text || current.codes.length) result.parts.push(current);
      current = null;
    };
    const start = (offset, code = null, number = null, description = '') => {
      current = {offset, notation: '', text: '', hand: ({'@': 1, '£': 2, '¢': 3})[code] || null,
        category: code === '#' ? 'symbolic' : code === '§' ? 'untranscribable'
          : ['@', '£', '¢'].includes(code) ? 'textual' : 'unresolved',
        folio, codes: code ? [code] : [], sourceNumber: number, description, issues: []};
      if (code && !'@£¢#§'.includes(code)) current.issues.push(`unknown-code:${code}`);
      if (/[¤@£¢#§¬¦]/u.test(description)) current.issues.push('code-combination-unresolved');
    };
    const append = (text, offset) => {
      if (!text.trim() && !current) return;
      if (!current) {
        // Bare codes are structural only at the beginning of a fresh folio block.
        const bare = text.match(/^\s*([@£¢#§])(?:\s+|$)/u);
        if (bare) { start(offset, bare[1]); current.notation += bare[0]; text = text.slice(bare[0].length); }
        else start(offset);
      }
      current.text += text; current.notation += text;
    };
    const tokens = /\[¤?\d+[a-z]*\]|\[¤…\]|\([@£¢#§¬¦+?*][^()]*\)/gu;
    for (const token of original.matchAll(tokens)) {
      append(original.slice(cursor, token.index), cursor);
      const raw = token[0];
      if (raw[0] === '[') {
        finish();
        const match = raw.match(/^\[(¤?)(\d+[a-z]*)\]$/u);
        folio = {original: raw, reference: match?.[2] || null, firstOccurrence: match?.[1] === '¤',
          verified: !!match};
        result.folios.push(folio);
        if (!match) result.issues.push('folio-unresolved');
      } else {
        const match = raw.match(/^\(([@£¢#§¬¦+?*])(\d*)\s*([^()]*)\)$/u);
        // A hand followed immediately by (§) describes the same annotation.
        if (match[1] === '§' && current?.hand && !current.text.trim()) {
          current.category = 'untranscribable'; current.codes.push('§');
          current.description = match[3]; current.notation += raw;
        } else {
          finish(); start(token.index, match[1], match[2] || null, match[3]); current.notation = raw;
        }
      }
      cursor = token.index + raw.length;
    }
    append(original.slice(cursor), cursor); finish();
    for (const part of result.parts) {
      // Keep malformed/unknown notation visible and report it without inventing syntax.
      if (/[¤@£¢#§¬¦]/u.test(part.text) && part.category !== 'untranscribable') part.issues.push('literal-or-unresolved-code');
      result.issues.push(...part.issues);
    }
    return result;
  }
  function legend(lang = 'en') {
    const l = t(lang);
    const text = lang === 'fr'
      ? ['Les références textuelles couvrent l’unité d’alignement entière ; elles ne situent pas l’annotation à un mot précis.',
        'Les crochets indiquent le folio. ¤ marque uniquement la première occurrence enregistrée de chaque côté : [¤1r] et [1r] désignent tous deux le fol. 1r.',
        '@ = Main 1 ; £ = Main 2 ; ¢ = Main 3. Ce classement est propre à chaque manuscrit ; il n’identifie ni ne date un scribe. Les nombres dans (@2), par exemple, numérotent les annotations ; ils ne désignent pas la main.',
        '# = annotation symbolique ; § = annotation qui ne peut être transcrite. Ces catégories sont indépendantes de la main.',
        'Trois mots suivis de ... signalent une transcription volontairement abrégée par l’éditeur. Les autres points de suspension restent à vérifier ; aucune suite n’est reconstituée.',
        'Les codes non expliqués (notamment ¬ et ¦) et la notation originale sont conservés. La numérotation d’affichage ne constitue pas un identifiant scientifique.']
      : ['Textual citations cover the whole Latin alignment unit; they do not locate an annotation at a particular word.',
        'Bracketed references identify the folio. ¤ marks only its first recorded occurrence for each side: [¤1r] and [1r] both mean fol. 1r.',
        '@ = Hand 1; £ = Hand 2; ¢ = Hand 3. Hands are classified within each manuscript and do not identify or date a scribe. The numbers in (@2), for example, enumerate annotations; they do not identify the hand.',
        '# = symbolic annotation; § = annotation that cannot be transcribed. Category and hand are independent.',
        'Three words followed by ... indicate a transcription deliberately abbreviated by the editor. Other ellipses remain subject to review; no continuation is reconstructed.',
        'Unexplained codes (including ¬ and ¦) and the original notation are retained. Display numbers are not scholarly identifiers.'];
    return `<details class="annotation-about"><summary>${l.about}</summary>${text.map(p => `<p>${escape(p)}</p>`).join('')}</details>`;
  }
  function translateEditorialDescription(description, lang = 'en') {
    return lang === 'en' && Object.hasOwn(editorialEnglish?.descriptions || {}, description)
      ? editorialEnglish.descriptions[description] : description;
  }
  function annotationTextSegments(part, lang = 'en', work = 'antiquities') {
    const original = part.category === 'unresolved' ? part.notation.trim() : part.text;
    const literal = text => ({kind: 'recorded', text, original: text});
    if (lang !== 'en' || !editorialEnglish || !['antiquities', 'bellum'].includes(work)) return [literal(original)];
    if (Object.hasOwn(editorialEnglish.whole, original)) {
      return [{kind: 'editorial', text: editorialEnglish.whole[original], original}];
    }
    const spans = [];
    const add = (source, translated) => {
      let position = 0;
      while ((position = original.indexOf(source, position)) !== -1) {
        spans.push({start: position, end: position + source.length, translated}); position += source.length;
      }
    };
    // Exact, inspected editorial comments only. Latin abbreviation expansions
    // such as d(imitte), (milia), and uncertain readings are never translated.
    for (const [source, translated] of Object.entries({...editorialEnglish.comments, ...editorialEnglish.fragments})) add(source, translated);
    for (const [source, translated] of editorialEnglish.spans[original] || []) add(source, translated);
    if (part.category === 'unresolved' && part.description) {
      const prefix = original.match(/^\([@£¢#§¬¦+?*]\d*\s*/u)?.[0];
      if (prefix && original.slice(prefix.length, prefix.length + part.description.length) === part.description) {
        spans.push({start: prefix.length, end: prefix.length + part.description.length,
          translated: translateEditorialDescription(part.description, lang)});
      }
    }
    const segments = []; let offset = 0;
    for (const span of spans.sort((a, b) => a.start - b.start || b.end - a.end)) {
      if (span.start < offset) continue;
      if (span.start > offset) segments.push(literal(original.slice(offset, span.start)));
      segments.push({kind: 'editorial', text: span.translated, original: original.slice(span.start, span.end)});
      offset = span.end;
    }
    if (offset < original.length || !segments.length) segments.push(literal(original.slice(offset)));
    return segments;
  }
  function renderAnnotation(record, options = {}) {
    const lang = language(options.lang), l = t(lang), interpreted = interpretManuscriptAnnotation(record);
    const citation = resolveAlignmentCitation(record.work, record.alignmentUnitId, {lang});
    const ms = resolveManuscript(record.siglum, record.witnessLabel || record.siglum || l.unknown, lang);
    const number = options.startNumber || 1;
    const parts = interpreted.parts.map((part, index) => {
      const anchor = `${interpreted.anchor}-at-${part.offset}`;
      const category = part.category === 'symbolic' ? l.symbolic : part.category === 'untranscribable' ? l.untranscribable
        : part.category === 'unresolved' ? l.unresolved : !part.text ? l.noTranscription : null;
      const segments = annotationTextSegments(part, lang, record.work);
      const text = segments.map(segment => segment.kind === 'editorial'
        ? `<span class="annotation-editorial-note" lang="en">${escape(segment.text)}</span>` : escape(segment.text)).join('');
      const editorialOnly = segments.length && segments.every(segment => segment.kind === 'editorial');
      const description = translateEditorialDescription(part.description, lang);
      const codes = part.codes.map(code => `${code} = ${({'@': `${l.hand} 1`, '£': `${l.hand} 2`, '¢': `${l.hand} 3`,
        '#': l.symbolic, '§': l.untranscribable})[code] || l.unresolved}`).join('; ');
      const fields = [[l.sourceId, record.originalId || l.noId], [l.unit, record.alignmentUnitId || l.unknown],
        [l.siglum, record.siglum], [l.shelfmark, ms.originalDisplayName], [l.folio, part.folio?.original || l.unknown],
        [l.sourceNumber, part.sourceNumber || l.unknown], [l.codes, [codes, description,
          part.folio ? part.folio.firstOccurrence ? l.first : l.subsequent : ''].filter(Boolean).join('; ') || l.unknown],
        [l.completeness, part.abbreviated ? l.abbreviated : part.ellipsisUnresolved ? l.uncertainEllipsis
          : part.category === 'untranscribable' ? l.untranscribable : part.category === 'symbolic' ? l.symbolic
            : !part.text ? l.noTranscription : l.recorded]];
      if (ms.verificationStatus !== 'verified') fields.push([l.manuscript, lang === 'fr' ? 'Référence du manuscrit à vérifier ; désignation originale conservée' : 'Manuscript reference requires review; original designation retained']);
      if (record.originalAlignmentReference != null) fields.push([lang === 'fr' ? 'Référence source du passage' : 'Original passage source reference', record.originalAlignmentReference]);
      if (record.originalManuscriptReference != null) fields.push([lang === 'fr' ? 'Référence source du manuscrit' : 'Original manuscript source reference', record.originalManuscriptReference]);
      const details = `<details class="annotation-details"><summary>${l.details}</summary><dl>${fields.map(([key, value]) =>
        `<dt>${escape(key)}</dt><dd>${escape(value)}</dd>`).join('')}</dl><p>${l.original}</p><pre>${escape(interpreted.originalNotation)}</pre></details>`;
      return `<article class="manuscript-annotation" id="${escape(anchor)}" tabindex="-1" data-alignment-unit="${escape(record.alignmentUnitId)}">
        <h4><span class="annotation-number">${number + index}.</span> ${escape(citation.publicCitation)}</h4>
        ${category ? `<p class="annotation-category">${escape(category)}</p>` : ''}
        ${text ? `<p class="${editorialOnly ? 'annotation-description' : 'annotation-transcription'}"${part.category === 'textual' && !editorialOnly ? ' lang="la"' : ''}>${editorialOnly ? `${l.editorialNote}: ` : ''}${text}</p>` : ''}
        ${description ? `<p class="annotation-description" lang="${lang}">${l.editorialNote}: ${escape(description)}</p>` : ''}
        <p class="annotation-meta">${l.manuscript}: ${ms.url ? `<a href="${ms.url}">${escape(ms.displayName)}</a>` : escape(ms.displayName)}${part.folio?.reference ? ` · fol. ${escape(part.folio.reference)}` : ''}${part.hand ? ` · <span class="annotation-hand">${l.hand} ${part.hand}</span>` : ''}</p>
        ${part.abbreviated ? `<p class="annotation-status">${l.abbreviated}. ${l.abbreviationHelp}</p>` : ''}
        ${part.issues.length ? `<p class="annotation-status">${part.ellipsisUnresolved ? l.uncertainEllipsis : l.review}</p>` : ''}
        ${citation.navigationTarget ? `<a class="annotation-passage" href="${escape(citation.navigationTarget)}" data-unit="${escape(record.alignmentUnitId)}">${l.passage}</a>` : ''}${details}</article>`;
    }).join('');
    const folioOnly = !interpreted.parts.length ? `<details class="annotation-folio-record"><summary>${lang === 'fr' ? 'Référence au folio uniquement' : 'Folio reference only'}: ${escape(interpreted.originalNotation)}</summary><p>${escape(l.unit)}: ${escape(record.alignmentUnitId)}</p><p>${l.original}</p><pre>${escape(interpreted.originalNotation)}</pre></details>` : '';
    return {html: `<div class="annotation-source-record" id="${escape(interpreted.anchor)}" data-source-siglum="${escape(record.siglum)}">${parts}${folioOnly}</div>`,
      count: interpreted.parts.length, interpreted};
  }
  return {setCitationData, resolveAlignmentCitation, resolveManuscript, interpretManuscriptAnnotation,
    recordAnchor, renderAnnotation, translateEditorialDescription, annotationTextSegments, legend, labels};
});
