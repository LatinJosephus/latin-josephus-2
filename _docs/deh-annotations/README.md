# DEH manuscript annotations — 27 October 2026

The reader integrates **1,917 supplied records from 21 manuscripts** through the existing manuscript-annotation panel. The records cover **168 chapters/prologue locations**. Every location is verified against the canonical DEH Latin chapter structure. No canonical XML or DEH↔Josephus parallel data is changed.

## Editorial instructions and source

The editor supplied `annotations DEH sans correction omission répétition ou variante.csv`. Its exact bytes are preserved in [the source snapshot](source.csv), SHA-256 `dfe4d299390481525c358b1baef864640ef700e7a94d941b91746feeed4a398d`. This snapshot is held with the implementation documentation, outside the published assets. The reader dataset includes only columns A–E.

The editor instructed this implementation to use columns A–E only: manuscript, folio, location, hand and content. Columns F–K are ignored by the display, location resolver and classification. In particular, locations are read from column C, not the redundant book/chapter columns J–K. No descriptions, themes, symbols or families are inferred from the ignored columns.

Confirmed instructions:

- Locate annotations at whole-chapter level. For example `1.26` becomes **I.26**, with the complete chapter as its destination. A note shown while reading I.26.3 retains its chapter-level citation and **View chapter** link.
- Interpret a numeric hand code by its suffix within the source manuscript: `678-1` becomes **Hand 1** in Cambrai 678. Original codes remain in Scholarly details.
- Interpret the sole `0.1` entry, Cherbourg 51 fol. 1v, `de Iosepho`, as referring to the **whole prologue**, covering the existing three units. This explicitly approved mapping is separate from source numbering.
- Display `\c{e}` as e caudata, **ę**. The original characters remain intact in the source snapshot, generated record and Scholarly details.
- Following the editor's provisional clarification, interpret `[*]` as untranscribed text. A wholly untranscribed entry uses **Cannot be transcribed**. Within a surviving transcription, a neutral **[untranscribed text]** marker separates the recorded Latin words. This does not specify the number of missing words or the cause. The provisional basis is documented in Scholarly details and the DEH explanatory key.

## Source exceptions retained

- Four groups contain five additional repeated source rows: 336–337, 822–824, 1805–1806 and 1851–1852. They remain separate records, each with its own source-row anchor. No row has been silently removed or merged.
- Sixty-eight records under Karlsruhe 82 have a hand-code prefix `81-`. Following the editor's hand-number instruction, their recorded suffix supplies the displayed hand number; the manuscript remains Karlsruhe 82. Original codes and the discrepancy are preserved in Scholarly details and the [inventory](inventory.json).
- `in-text` occurs in the hand column in 116 records; `--` in three. Neither supplies a hand number. The original field is retained in details, with no inferred hand or category.
- St. Gall 626 uses pages, as independently recorded in the existing manuscript repertory. Its references display **p.**; other witnesses display **fol.** The source's `12bv` notation is retained unchanged.
- Two entries contain ellipses: rows 578 and 737. They are retained without assigning the Josephus three-word abbreviation convention. DEH's convention is configured independently.
- All 21 manuscript names link to the existing repertory. The adapter derives repository, shelfmark and pagination from verified repertory records; it does not create or change catalogue records.

## Architecture and preservation

`bin/build-deh-annotations.py` derives the display dataset from the byte-preserved CSV and existing manuscript repertory. It retains every A–E field verbatim, the original source order and source-row number. It rejects a changed source snapshot. The generated record identity is explicitly a presentation anchor, not an original scholarly identifier.

The shared citation generator now also supplies DEH chapter targets, with all contained alignment-unit IDs and first/last textual citations verified from the frozen XML. Existing DEH paragraph citations remain unchanged. Antiquities/Bellum citation maps and the original Josephus annotation inventory remain byte/content identical.

`dehManuscriptAnnotations.js` supplies a source-specific adapter to the common annotation renderer. It never invokes the Josephus hand/folio/symbol parser. The common display retains its typography, annotation-word colour, compact native details and English/French labels. Chapters appear in textual order, with the original CSV order retained within each chapter. Source-row anchors remain stable across book, chapter and subsection views.

In Book view, the reader links and highlights whole annotated chapters. In a subsection view, the link explicitly says **annotations for this chapter**; the notes retain the whole-chapter destination. A failed dataset request produces a visible reload message rather than silently presenting an empty apparatus.

No source transcription, CSV, Latin/Greek/English/French text, scholarly identifier, Niese boundary, concordance, parallel, hosting setting, DNS or CNAME is edited.

## Verification and local review

The automated source suite passes **69 Node tests and 9 Python tests**, including independent comparisons of all 1,917 CSV records and all 177 canonical DEH chapter boundaries. Corpus, parallel, search-asset and generated-data checks also pass. The [DEH browser report](screenshots/deh-browser-qa.json) verifies all five books, all 1,917 displayed records and 168 chapter links, five unchanged Latin/English/French views, bidirectional navigation, whole-chapter highlighting, keyboard details, missing-data behaviour, light/dark modes and mobile layout. The existing 13-view/27-book Josephus browser comparisons and 13 reader/search/parallel UI checks also pass. The final delivery receipt records their exact scope.

Visual evidence: [reader in context](screenshots/deh-reader-local-preview.png), [annotation key](screenshots/deh-annotation-key.png), [light](screenshots/deh-chapter26-light.png), [dark](screenshots/deh-chapter26-dark.png), [mobile](screenshots/deh-chapter26-mobile.png), and [partial transcription](screenshots/deh-partial-source.png).

Repeat source checks with `node bin/annotations/qa.cjs`. Generate/check the adapter with `python -B bin/build-deh-annotations.py [--check]`. The browser checks in `bin/annotations/deh-browser-qa.cjs` use the existing separately installed Playwright/Chrome runtime; no site dependency is added.

Implementation branch: `feature/deh-manuscript-annotations-20261027`, based on published source `0042341a4a0193e489f78ccd9e414794ca5fbed1`. This is a local implementation for review; it has not been merged or published.
