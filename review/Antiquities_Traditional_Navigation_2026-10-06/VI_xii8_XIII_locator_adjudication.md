# VI.xii.8 → VI.xiii: current-text locator adjudication

Scope: base HEAD f7d9142cad998e8a005adea1a22532b9a78592db; current Latin/English physical locators only. The source identities, Niese associations 269/271 and CONFIRMED_NIESE_START judgments are unchanged. No historical source PDF was reopened. Frozen v1.1 is unchanged.

## Verified positions

| Boundary | Latin | English |
|---|---|---|
| VI.xii.8 / Niese 269 | latin-book06-num271, existing milestone unit=niese n=269, milestone[1], projected offset 1; Abiathar itaque abimelech… | english-book06-num271, paragraph opening offset 0; But Abiathar, the son of Ahimelech…; sameAs=#latin-book06-num271 |
| VI.xiii / VI.xiii.1 / Niese 271 | latin-book06-num272, existing milestone unit=niese n=271, milestone[1], projected offset 1; Eo siquidem tempore… | english-book06-num272, paragraph opening offset 0; About this time it was that David heard…; sameAs=#latin-book06-num272 |

Offsets use the frozen current-corpus projection convention, omitting num/milestone/pb/lb/note text. Latin has a single space after its inherited num and before each Niese milestone. The paragraph and milestone edges are existing uniquely selectable points; no additional markers are needed.

The actual base Latin labels are [XII.viii] and [XIII.i], not the earlier audit's composite suffix labels [XII.viii.271] and [XIII.i.272]. Literal labels, true Niese milestone numbers, and stable paragraph suffixes remain distinct. VI_locator_corrections.json records exact Git-blob hashes and original/replacement locator fields.

## Frozen overlay error and correction

Frozen v1.1 assigned VI.xiii and VI.xiii.1 to Latin latin-book06-num271 offset 0 and English english-book06-num271 offset 0, with Abiathar incipits. VI.xii.8 was already at Latin num271 offset 1 / English num271 offset 0. The resulting Latin end preceded the start, and the English end equalled the start.

Only the implementation registry's four Chapter XIII / XIII.1 language locators were replaced. VI.xii.8 remains at its verified existing position. The corrected endpoint is in the following num272 paragraph in both layers, making XII.8 → XIII strictly ordered. The erroneous locator fields remain recoverable in current-locator-adjudication TEI notes and this review record. This corrects the v1.1 current-text overlay, not source scholarship or citation numbering.

## Separate Alignment-unit defect gate

Both defects exist: the frozen current-text locator error and an existing cross-language alignment-selection defect.

- Latin num271 contains true Niese 269–270 / Abiathar; English num271 correctly targets it.
- Greek greek-book06-num262 contains Niese 262–270, with the Abiathar start at its eighth num, [269]. Its sameAs is only #latin-book06-num262.
- Greek greek-book06-num271 contains true Niese 271 / Κατὰ δὲ, but wrongly targets #latin-book06-num271, the Latin Abiathar paragraph.
- Greek greek-book06-num272 contains true Niese 272–274 and targets #latin-book06-num272. The matching Latin/English num272 paragraphs begin earlier, at true 271.

The base alignedSectionView builds canonical Latin target num271 and selects Greek whole paragraphs whose sameAs points there. It therefore selects the erroneous Greek num271. The partial implementation's Antiquities unit resolver also trusts this sameAs and has a mirrored-ID fallback, so the defect persists there. A selector-only preference change cannot recover the absent internal 269 span from the declared paragraph-level topology.

The screenshot independently confirms the display failure. This adjudication uses base XML and renderer topology to determine its cause; it does not treat screenshot labels or numeric suffixes as physical evidence.

## Separately authorized alignment metadata repair

Use three source-qualified Greek span bindings in scholarly structural data, consumed by a generic Antiquities alignment-range adapter:

| Canonical alignment identity | Greek start | Greek end |
|---|---|---|
| latin-book06-num262 | greek-book06-num262 paragraph opening | greek-book06-num262 / num[8] ([269]) |
| latin-book06-num271 | greek-book06-num262 / num[8] ([269], Abiathar) | greek-book06-num271 paragraph opening ([271], Κατὰ δὲ) |
| latin-book06-num272 | greek-book06-num271 paragraph opening ([271], Κατὰ δὲ) | greek-book06-num275 paragraph opening ([275]) |

These edges are all present in base XML. The num262 binding avoids repeating Abiathar in two units; the num272 binding reunites Greek 271 with 272–274 to match its Latin/English paragraph. Latin and English bindings remain unchanged. Preserve all existing IDs, sameAs values, paragraphs and text; record the original incorrect sameAs as evidence. No Book-VI conditional, paragraph split, textual rewrite or stable-ID repurposing is required.

The user explicitly authorized these three data-only Greek bindings after reviewing the proposal. They are now implemented as separate TEI alignment-range records. A generic binding lookup and the common range resolver interpret them; no renderer conditional identifies these units or this book. Focused QA must pass before full QA resumes. Registry locator correction and alignment metadata correction remain separate records and authorities.
