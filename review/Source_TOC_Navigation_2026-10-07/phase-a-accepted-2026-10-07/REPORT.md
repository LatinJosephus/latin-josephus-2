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
