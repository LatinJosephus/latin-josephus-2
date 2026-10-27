# Approved Book I presentation updates

27 October 2026. Implemented on the isolated annotation feature branch after the editor requested application of the reviewed findings and a refreshed local preview.

## Bern 118, folio 2v

Original source record remains exactly `[¤2v] (§) dicit (@1) issa (#2 nota NT)`. The editor clarified that untranscribed material precedes the surviving `dicit`. Following the requested display cleanup, the first component presents one reading: **david [uncertain text] dicit (provisional reading)**. Its partial-transcription status, surviving original fragment `dicit`, editorial explanation and complete original notation are retained in Scholarly details. The main panel does not duplicate the reading or its explanation. The proposal does not replace the source transcription, resolve the unknown middle words or assign a hand.

This interpretation is guarded by the exact work, book, alignment unit, witness and original record. It is not a global reinterpretation of every § entry. The independent category and transcription-status model supports partial transcription without treating it as deliberate abbreviation.

## Recovered Bodmer 98 annotations, folio 1v

The historic worksheet `Annotations - Latin Antiquities (libri I-XII).xlsx`, Feuil1!E11, records:

`[¤1v](@1).d significe. sabatum (@2) de adam (@3)issa si a uira diuisat`

The editor agreed with the facsimile-supported locations and requested their application. A presentation supplement exposes three entries from this single original cell:

| Source component | Existing alignment unit | Public citation |
|---|---|---|
| `(@1).d significe. sabatum` | `latin-book01-num27` | Book 1, Niese §§27–33 |
| `(@2) de adam` | `latin-book01-num34` | Book 1, Niese §§34–36 |
| `(@3)issa si a uira diuisat` | `latin-book01-num34` | Book 1, Niese §§34–36 |

The third entry displays the reviewed reading `issa si a uiro diuisa`. The grammatical preference for `diuisa` uses the project's Latin account of the woman's formation from Adam; it is not inferred from automated image transcription. The worksheet's `si` remains explicitly uncertain. The full exact original cell and the original fragment `issa si a uira diuisat` remain in scholarly details alongside the source workbook/cell and the [e-codices facsimile](https://www.e-codices.unifr.ch/en/fmb/cb-0098/1v).

Their **Recovered worksheet annotation** provenance and editorial explanations appear in Scholarly details; the reviewed wording has a short inline qualification. They use stable presentation anchors derived from the worksheet entry, not invented canonical IDs or display numbers. The source offset selects each component without altering the cell. They are inserted after the existing entries for the relevant unit, preserving every original XML reading's relative order. Navigation and highlighting continue to cover entire alignment units.

Actual annotation words use the site's existing `--lj-brand-accent` colour, with the existing global theme colour as fallback. Explanatory brackets and inline reading-status labels retain the normal text colour. Both site themes retain the transcription font, so colour is an additional cue rather than the only distinction. Browser checks verify text contrast of at least 4.5:1 and wrapping at 390 pixels.

Symbolic entries combine their category and supplied description on one line, for example **Symbolic annotation: nota NT**. The label uses the normal text colour and the description uses the annotation accent colour. Entries marked as untranscribable likewise combine any supplied wording/description with their distinct category label. Neither category is inferred from the other, and entries without supplied wording show only their category.

## Source preservation and unresolved references

All 2,958 original XML reading records and their 6,202 components remain present, with 2,937 verified citations and 21 documented original association exceptions. The recovered worksheet supplies three additional display entries from one cell, for 6,205 displayed components across both sources. The Bern clarification changes one component's presentation to textual with partial transcription; it changes no source text or component boundary.

The three missing Book I UUID targets remain unresolved. The editor could not identify the original deleted-dot passage. No missing target is redirected to a manuscript note, and no existing pointer or Latin text is changed. Canonical XML, source worksheets, original symbols, identifiers, source associations, DEH annotations and parallels remain untouched. The additional associations exist only in the explicit editor-reviewed presentation supplement.

## Implementation and checks

`assets/js/annotationEditorialUpdates.js` stores the exact source cell, targeted Bern clarification and reviewed reading. The shared interpreter/rendering component keeps recorded text, editorial proposals, partial transcription and provenance independent. The reader includes the supplement in display numbering and bidirectional navigation while maintaining separate original-record and supplement counts. English/French labels cover the added states.

Eight new focused tests verify partial/provisional distinctions, exact original cell preservation, accepted citations, original component offsets, unique stable anchors, reviewed reading and uncertainty, English/French labels, and isolation from other works/books. The current suite has 53 annotation/citation/translation tests and five Python citation/preservation tests. Actual reader checks cover both affected units, original and supplemental record counts, navigation and the saved annotation fragment.
