# Millet — whole-chapter correspondence selection

24 October 2026; MilletWorkBot2. Local successor to compact-interface commit bf7a5803725016b52d94a7f8ff9ce99d7dec0ac1. No push or deployment.

Chapter view already displayed the French intervals for its Ussani sub-chapters, but highlighting and correspondence metadata still followed one retained unit. In the reproduced V.1 case, the Latin pane contained five units and the French pane 110 physical source lines, while only the first unit's 14 intervals were highlighted.

Chapter selection now uses the exact union of its existing canonical sub-chapter mappings. All corresponding Latin units are outlined, all matching French atoms are highlighted and the disclosure lists the chapter's constituent correspondences. Shared physical source lines appear once; partially included lines retain the same exact character boundaries. The same rule applies when the global chapter menu has changed and the sub-chapter choice is temporarily empty.

Selecting a particular Latin/French passage or an Aligned passage still inspects one unit. Settings now includes Whole Ussani chapter to restore the group. Browser history and share/reload preserve an explicitly selected individual passage through the optional millet-select=unit display-selection parameter. Existing unit links retain their canonical IDs and citations. Old chapter links containing a stale millet-unit value correctly open the chapter group unless an explicit individual-selection scope is present.

No scholarly XML, JSON mapping, source payload, canonical identifier or character offset was edited. French text rendering and the correspondence data are preserved. The small shared chapter-selection helper is also used by the existing running-text view, so display and highlighting select the same mappings.

Validation:

- All 12 Millet Node tests pass, including a test of every chapter's exact union and shared-line deduplication.
- Actual Edge browser: all 177 canonical chapter groups including the Prologue pass; together they account for all 558 units. Every selected codepoint/UTF-16 range, exact source-line string, Latin target and chapter interval union is checked.
- The existing complete browser regression passes all 558 individual selections, including 348 cross-page units, exact canonical texts and Josephus parallel return.
- Compact reader browser regression passes desktop, laptop and mobile, keyboard/focus, modes, folios, metadata, chapter/sub-chapter navigation, share links and history.
- Targeted chapter controls pass: legacy links, highlighting on/off, individual selection within a chapter, reload, Whole Ussani chapter restoration and back/forward.
- Full configured Jekyll build and generated-publication/corpus gates are recorded in the external build logs and final receipt.
- All 179 protected starting hashes are checked after application, including all 166 site XML files, the nine Millet data assets, global reader and existing parallel code. Certified master identity remains unchanged.

Exact changed files:

- assets/js/milletCore.js — reusable selection of an existing chapter's mapping records.
- assets/js/milletReader.js — chapter-wide highlight/metadata scope, independent unit selection and scope restoration.
- bin/millet1556-qa.test.mjs — all-chapter union regression.
- bin/millet1556-compact-ui-qa.mjs — expected global chapter selection updated.
- bin/millet1556-chapter-browser-qa.mjs — complete actual-browser chapter and scope/history checks.
- _docs/MILLET_CHAPTER_ALIGNMENT_FIX.md — this report.

Evidence, before/after screenshots, logs, exact source hashes and final commit receipt are in outputs/Millet_Site_Integration/MILLET_CHAPTER_ALIGNMENT_20261024_WorkBot2. Previously issued compact-interface evidence remains unchanged. The final commit hash is in FINAL_STATE.json.

This is a display-selection correction using the certified alignments, not a new scholarly alignment or proofreading pass. Existing editorial uncertainties and the pre-existing AJ Latin historical-pin limitation remain unchanged. No independent proofreading, measured CER or formal XSD validation is claimed.
