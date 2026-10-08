# Source contents integration Phase B

Date: 2026-10-08. **GO for human browser review.** The human editor’s per-source authorization supersedes the Phase-A global implementation stop. The complete accepted census remains unchanged in SOURCE_TOC_CENSUS.csv / .json. Its original report, authority document and QA/manifest are preserved byte-for-byte in phase-a-accepted-2026-10-07. The historical report follows this amendment.

Worktree: `C:\workspace\LatinJosephus-source-toc-navigation`. Branch: source-toc-navigation. Base: `087c0bf651037d83c5156495836510d250bdcf09`. Canonical remains clean on the required HEAD and origin. Nothing is staged, committed, merged or pushed.

## Reader coverage

| Work | Witness | Books enabled |
|---|---|---|
| Antiquities | Greek / Niese | V, XI–XX |
| Antiquities | Latin / Bamberg Msc.Class.78 | II–V, XIII, XV–XX |
| Bellum Judaicum | English / Lodge 1602 | I–VII |

There are 29 eligible book/witness combinations in the separately dated 104-row status matrix. Source existence, transcription verification, encoding and publication eligibility are separate fields. Whiston, Cardwell and other insufficiently verified sources remain deferred. Pollard’s five DEH books retain the accepted no-source-TOC result. Latin Antiquities XIV retains SR-061: its contents/narrative paragraph is neither split nor adjudicated. Greek XIV contents are available independently.

Existing source chapter-zero/list blocks are reused as paratext, never reconstructed from navigation. Lodge’s seven printed lists retain their 136 entries and anomalous printed numbering. Canonical IV displays the existing printed IV and V lists; V displays printed VI; VI displays printed VII. Canonical VII uses that complete printed-VII list from its unchanged location in canonical VI, with an explicit printed-book scope note. No subset is generated from reader chapters.

## New Bamberg text and supplements

The governing file is `C:\workspace\Bamberg TOC books 2-5\Bamberg Msc. Class. 78 - TOC - bks. 2, 3, 4, 5.docx` (19,987 bytes), SHA-256 `2726e418ce518f964261a98d02e9a94b736a4f584208b6844d606e012eb683c9`. The four new companion TEI files contain exactly 32 entries:

| Book | Entries | Blatt supplements |
|---|---:|---:|
| II | 3 | 2 |
| III | 11 | 42 |
| IV | 5 | 19 |
| V | 13 | 0 |

II–IV are the human editor’s double-checked marginal transcriptions. V is the governing improved main-text transcription. The source images/folios specified in the Word file are retained in TEI provenance; no fresh manuscript adjudication was undertaken.

The extraction resolves document defaults, inherited paragraph/character styles, OOXML italic toggle properties and direct run formatting. Adjacent italic runs are coalesced without assuming word boundaries. All 64 contiguous italic spans have TEI counterparts: 63 lexical spans use supplied with reason=lost, source=#blatt, resp=#human-editor and italic rendition; one leading whitespace-only italic span before II.II is retained as hi. It is not counted as supplied manuscript letters. Every entry’s complete text, labels, order and surrounding Latin match the Word extraction exactly. All five new XML files validate against the project-retained official TEI P5 schema.

Only II–IV carry the reader note: “Italicized text has been supplied from Blatt’s edition where trimming of the manuscript margins has removed words.” The local project bibliography identifies Franz Blatt, ed., The Latin Josephus (Aarhus, 1958); precise supplement page references were not supplied and are not invented.

Book V’s 26 entry comparisons against earlier Word and Google Sites HTML yield 13 variance records. The new Word governs every import. No chapter numbering/entry-boundary difference or consequential encoding uncertainty blocks V. Literal unusual readings and transcription notation remain unchanged, including factus factusque in II, [...]si in IV, and the insertion notation in V. The editorial register preserves these for review without silently repairing them.

## Generic reader and URLs

A TEI feature-structure index at assets/xml/source-contents.xml registers work, book, witness, verification status, exact source XML block and provenance. Four source-specific Bamberg companion files supply new paratext. No source contents text is stored in JavaScript and no book-specific renderer conditions were added. Existing XML and structure.xml are untouched.

Table of contents is the first Chapter option wherever a verified source is available. It has distinct view=contents semantics, never a chapter identity. Entering removes conflicting chapter/subchapter/bamberg/niese/unit/num parameters while retaining book, source selection, unrelated preferences and fragments. Numbered Chapter selection exits contents mode. Book switching retains contents when eligible and otherwise falls back to Book view. Every pane displays its own source or the neutral unavailable message. Entries are non-clickable.

Contents conversion suppresses default generated note/list decoration so source text appears exactly once. Narrative annotations/highlight controls are cleared/hidden during paratext display and restored by the ordinary reader on exit. Contents styling is scoped to .source-contents; supplied letters remain italic without inserting editorial brackets absent from the transcription. Source data are not appended to narrative ranges. The existing Lodge notes preference is registered generically for contents URL persistence.

## Verification

All 104 book/source combinations and 29 supported dropdown/copy/reload/history cases passed, including mixed availability, source and pane switching, keyboard operation and book fallback. Final light/dark displays were visually inspected. Measured normal-text contrast is 13.23:1 light / 11.85:1 dark. No duplicate DOM IDs occur in contents displays. Some baseline Book views retain a repeated source apparatus ID annotations; exact base comparisons confirm that this feature introduces none of those duplicates.

Traditional counts remain 257 Chapters, 1,432 Subchapters, 1,689 level rows and 1,441 physical positions. All 5,034 executable language ranges and 33 expected Book-IX unavailable states pass. All 257 Chapter availability states and 227 prefix/end checks pass; the nine absent-Loeb-lower-1 cases acquire no synthetic entries. VI.xii.8/XIII and XI’s multi-span membership, interpolation preservation and unchanged notice pass.

All 198 Bamberg identities / 594 language displays, compact URLs and six distinct same-Niese/different-position pairs pass. All 2,456 enabled Antiquities Niese selections / 7,368 pane comparisons match the base. All 1,441 Alignment units and Book-VI bindings match the base. Cross-work differential ranges pass: DEH 1,239; Bellum 1,441; Contra Apionem 693. The additional Whiston/Lodge suite passes 10,340 scenarios including 7,444 Niese/source comparisons. Lodge’s 4,001 segmentation markers are unchanged. Source/pane switching, notes, keyboard, themes and history pass.

All 108 pre-existing XML files are byte-identical, proving unchanged text, IDs, sameAs, milestones, topology and Book-XI order. Antiquities paragraph counts remain Latin 1,622 / Greek 1,681 / English 1,600, with 1,442 identified alignment paragraphs per layer including Proem. No new inline anchors were needed. All 48 original external authorities and the new DOCX pass hash checks. The canonical checkout remains clean at the required base. Its CRLF/LF checkout differences from the implementation worktree are documented as cross-checkout differences, not treated as source changes; no normalization occurred.

## Exact production changes

Modified: assets/js/renderTei.js; assets/css/tei.css.
New: assets/xml/source-contents.xml; assets/xml/antiquities/paratext/bamberg78/book-02-contents.xml, book-03-contents.xml, book-04-contents.xml, book-05-contents.xml.
Review evidence is confined to this existing review directory. The accepted October 6 and October 7 traditional/Bamberg certification packets remain byte-identical. No source PDF was reinterpreted, no website build was run and no recovery file was written.

Reproduction: use the bundled Python with -B for prepare_phase_b.py (Word extraction/TEI import), validate_phase_b.py (schema/text/concordance/variance/status checks) and verify_phase_b_integrity.py. Browser harnesses contents.test.cjs, regression.test.cjs, bamberg-regression.test.cjs and interaction-regression.test.cjs use installed Chrome and the real renderer/CETEI/XML. Optional regression gates are documented by their command-line names in the scripts. Historical test files are not modified. Development failures retained under development-diagnostics are superseded by the final PASS evidence.

---

# Accepted Phase A report (historical; global stop superseded above)

# Source table of contents census

**NO-GO for reader integration: the requested source-restoration gate has not passed.** Every current book/source combination has a row, but source-level verification remains open in 72 of the 104 rows. Three additional Proem files were inspected. Only this supplemental review directory is written. No source text was imported and reader behaviour has not changed.

Base: 087c0bf651037d83c5156495836510d250bdcf09. Branch: source-toc-navigation. Worktree: C:\workspace\LatinJosephus-source-toc-navigation. Canonical was clean on v2-development; HEAD and origin/v2-development matched the required base.

| Work / source | Present in production | Upstream list omitted from book | Source has no TOC | Not yet verified |
|---|---|---|---|---|
| Antiquities / Niese | 5, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 | — | — | 1, 2, 3, 4, 6, 7, 8, 9, 10 |
| Antiquities / Bamberg 78 | 13, 14, 15, 16, 17, 18, 19, 20 | 5 | — | 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12 |
| Antiquities / Whiston | — | — | — | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 |
| Bellum Judaicum / Niese | — | — | — | 1, 2, 3, 4, 5, 6, 7 |
| Bellum Judaicum / Cardwell (1837) | — | — | — | 1, 2, 3, 4, 5, 6, 7 |
| Bellum Judaicum / Whiston | — | — | — | 1, 2, 3, 4, 5, 6, 7 |
| Bellum Judaicum / Lodge (1602) | 1, 2, 3, 4, 5, 6, 7 | — | — | — |
| Contra Apionem / Niese (1889) | — | — | — | 1, 2 |
| Contra Apionem / Boysen (1898) | — | — | — | 1, 2 |
| Contra Apionem / Whiston | — | — | — | 1, 2 |
| DEH / Ussani (1932) | — | — | — | 1, 2, 3, 4, 5 |
| DEH / Pollard v1.0 | — | — | 1, 2, 3, 4, 5 | — |

Totals: **26 PRESENT_IN_PRODUCTION; 1 PRESENT_IN_AUTHORITY_OMITTED_FROM_PRODUCTION; 5 SOURCE_HAS_NO_TOC; 72 NOT_YET_VERIFIED.** The per-book evidence, production observations, authority references and actions are in SOURCE_TOC_CENSUS.csv/JSON. PRESENT does not assert list-to-navigation identity.

Already encoded source lists: Antiquities Greek V and XI–XX; Antiquities Latin XIII–XX; Lodge printed Bellum I–VII. Seven Lodge lists live in six canonical production files; the list relevant to canonical VII remains in canonical VI. Antiquities Whiston V has a list in production too, but stays NOT_YET_VERIFIED as source-print paratext. Existing encoding must not be confused with printed-source provenance.

Upstream Latin V capitula are missing from production, but the Word and HTML readings differ. Neither is silently selected. Existing Latin XIV hold SR-061 remains intact. A Whiston digital candidate is located, but source-authorized print contents/preparation provenance is not. The Gutenberg candidate contains 256 chapter links; 13 do not match their linked heading after whitespace-only comparison. Exact candidate list/heading texts are retained independently, without silent correction. Deliberate systematic omission cannot be concluded from the inspected evidence. SOURCE_AUTHORITY.md identifies the exact required source/adjudication.

The five books of the registered born-digital Pollard English translation have no source contents list. Cardwell, Niese, Boysen and Whiston rows without an attested list remain NOT_YET_VERIFIED for complete source paratext. Absence in current/frozen digital running text does not establish print-level SOURCE_HAS_NO_TOC.

## Deferred reader design

After source provenance clears, reuse existing contents/list XML where safe or use a TEI paratext companion with witness/book locators and source scope. Source text must not live in JavaScript, ordinary chapter paragraphs or a fake chapter wrapper. A generic availability index can add Table of contents first in the Chapter selector, preserve numbered options and select view=contents. Contents mode removes conflicting chapter/subchapter/bamberg/niese/unit parameters, preserves book, unrelated parameters and fragments, and follows existing history flow. Mixed panes show the selected witness's own source list or a neutral unavailability message. No entry links are inferred from navigation numbers. These are proposals only.

## QA and protected behaviour

All 107 current reader book/Proem XMLs parse. Registry populations remain 257 Chapters, 1,432 Subchapters, 1,689 level rows, 1,441 physical points and 198 Bamberg identities. Lodge source contents equality passes 7/7 lists, 136 entries.

All pre-existing worktree files remain byte-identical to the census baseline, including XML, structure.xml, renderer, templates, styles and historical review packets. Inspected external authorities also retain their exact hashes. Canonical checkout and Git index are unchanged. Source text, IDs, sameAs, milestones, segmentation and Book-XI witness order were not edited.

Browser/URL/history/theme and exhaustive navigation suites are NOT RUN because Phase B stopped before any reader change. No new browser certification or regression PASS is claimed. Antiquities traditional/Niese/Bamberg/alignment, Bellum Cardwell/Whiston/Lodge/Niese, DEH and Contra Apionem are preserved by byte identity, not re-certified through execution. Historical Bellum Greek 818 empty Whiston milestones are not treated as TOC text or activated.

Changed files: only this new census/report/QA/reproducibility packet. No source/application, recovery/frozen, existing certification or generated site file changed. Nothing staged, committed, pushed, merged or rebased. GO only for reviewing the census; NO-GO for reader integration until the source gate clears.
