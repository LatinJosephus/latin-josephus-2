# Book I pilot result — NOT CERTIFIED

**Segmentation complete; NO-GO for integration.** There is one newly inserted Niese milestone for every I.1–346. Both original English files reconstruct exactly when those milestones are removed. All canonical wording, punctuation, notes, headings, IDs, pre-existing numerals, anchors and divisions survive. The production checkout and all protected texts remain unchanged.

The repository separates the proem (I.1–26) from Book I narrative (I.27–346). The deliverable retains that structure: output/preface.xml and output/book-01.xml. Neither a new assembled book nor changes to another language are needed for the English pilot. Only those two canonical source files differ on the isolated branch.

## Deliverables

| Deliverable | File |
|---|---|
| Segmented XML, 26 and 320 markers | output/preface.xml; output/book-01.xml |
| Complete 346-row ledger, with exact source text and offsets | SEGMENTATION_LEDGER.json; SEGMENTATION_LEDGER.csv |
| Untouched extraction evidence and separate normalized matching data | EXTRACTION_LEDGER.json; MATCHING_TEXT.json; extracted/ |
| Reproducible source recovery, extraction, alignment, insertion, QA and archive scripts | scripts/; REUSE.md |
| Edition, digital source, URL, licence and retrieval provenance | PROVENANCE.md; SOURCE_MANIFEST.json; sources/*.record.json |
| All 17 individual boundary decisions, alternatives and evidence | ADJUDICATION.md; ADJUDICATION_RECORDS.json |
| All inherited textual differences and Greek control qualification | SOURCE_DIFFERENCE_REVIEW.md; SOURCE_DIFFERENCES.json |
| Full section extents and Greek/canonical incipit audit | COMPLETE_SECTION_EXTENTS.json; BOUNDARY_AUDIT.md |
| Executed automated QA and reader evidence | QA.json; EXTRACTION_QA.json; SCHEMA_QA.json; RENDERER_QA.json; DIRECT_CONTEXT_MEMBERSHIP_QA.json; evidence/ |
| Immutable tranche XML, ledgers and QA | snapshots/C-050 through C-346 |
| Recovery, archive links and file checksums | RECOVERY.md; EXPORTS.json; CHECKSUMS.json |

## Source recovery

Lexundria's server-rendered HTML explicitly supplies all 346 Niese labels in span.iisec elements across 18 Book I ranges. No downloadable XML/JSON/TEI or advertised API was found on the inspected public pages/resources. The parser excludes navigation and only extracts narrative paragraphs. Whiston's paragraph numerals are preserved in exact extraction text, recorded separately and removed only in matching. The final range ending 2.0 contributes sections 337–346 and no Book II marker.

Perseus's 1856 Alden and Beardsley Whiston transcription supplies 84 coarse section divisions and 107 Whiston chapter/paragraph milestones in Book I, with no fine Niese milestone map. Its TEI and README are preserved with Perseus/Tufts attribution and CC BY-SA 4.0 licence. Lexundria identifies the translation's first publication in 1737 but does not identify its digital transcription's underlying edition or an explicit segmentation licence. No source wording replaces the project's authoritative text.

## Executed QA

| Check | Actual result |
|---|---|
| Lexundria extraction | 18 pages, 346 rows; ordered 1–346; zero skipped, duplicated or extraneous identities |
| Greek identity control | 26 proem + 320 narrative labels; identical sequence |
| XML parse and milestone convention | Both files parse; 346 empty unit=niese milestones, following Bellum English convention |
| Byte reconstruction | PASS for both complete XML files, including every original tag and character |
| Complete textual stream | Exact equality before/after; zero unexplained textual changes |
| Existing XML elements | All 107 p, 77 num, 23 div2, 2 div1, 2 note, 3 anchor and 1 lb elements retained, including attributes and order |
| Protected isolated source/renderer checks | 156/156 protected files unchanged |
| Production checksums | 158/158 files unchanged from initial production hashes |
| Boundary confidence | 329 HIGH, supported by unique long anchors and preceding context; 17 MEDIUM after individual adjudication; zero unresolved boundary candidates |
| Complete source collation | 311 sections share identical word-token sequences; 35 differ, all reviewed and preserved |
| Direct-reader routes | 346/346 tested; 346/346 include the English boundary's parent paragraph; all use the existing context policy |
| Containing-reader views | 98/98 match baseline: 2 complete views, 22 Chapters and 74 Subchapters |
| Reader errors and new duplicate IDs | Zero browser errors, zero failed external requests, no new duplicate DOM IDs |

Generic TEI All validation was also tried. Baseline and output both fail identically at the headerless project fragment root (no teiHeader); no new diagnostic is introduced. This is not presented as schema validation success. XML parsing and the project's inherited fragment conventions pass.

Baseline/output SHA-256 values (UTF-8 worktree bytes):

| File | Baseline and reconstructed | Segmented output |
|---|---|---|
| preface.xml | d89e73764466ea4ca5479257fae649523791a697964ef572cc784b2dcff82d75 | d04712a2db72f2d2c39e175591b866308f93cb15d10f4ee3be70401f7dd614eb |
| book-01.xml | 6b695035845cecbe34fcc8c0bf6ffc000945938e9fd9cfe0e1306d3b11665420 | 9cd8daf04bddfd94cd96f077c0b9336135c35d017fad029a56fd08e1fc2363f3 |

Complete text-stream SHA-256: preface 595c7733a5bb9eadf5d93c9f97b0a37ba012cfc17c1770e9cbaf15ac5cf3f0d8; narrative eaba9dc6e3f7cf4f7c77a94e816a1d859eabea6bf5411e751bcfd27e40d4addf.

## Qualifications and integration decision

1. The unchanged Antiquities renderer always routes English Niese selections through paragraph context and indexes fine milestones only for Latin. Adding English XML milestones does not make those selections exact. A separate reader integration must index English milestones, deduplicate coarse num identities, render the correct complete interval and preserve all containing views. No production renderer was changed.
2. Project Greek places I.272 earlier than Lexundria, inside the preceding quotation. Printed Niese p.65/PDF155 supports the new clause used by Lexundria. Evidence and the adopted English position are logged; Greek remains untouched. A separate Greek control adjudication is required before claiming complete cross-language agreement.
3. Existing English contains 35 sections with source differences, including substantial losses at I.260–263 and the severely damaged I.271. These are not repaired or attributed to a particular printed edition. All sections have surviving English, but their represented completeness must be acknowledged before release.
4. The full-book reader contains the inherited duplicate annotations display ID in both baseline and candidate. No new duplicate occurs. The initial harness incorrectly rejected that baseline condition; its failed results, immediate emergency archives and repaired baseline comparison are retained under history/. The resumed check retained the already completed 346-selection evidence and reran only the affected containing-view checks.

Accordingly **NO-GO for integration/certification**. The complete English segmentation is a review candidate with strong integrity evidence, not a certified replacement or a published release. Resolving those control/integration questions can reuse the existing ledger and offsets; no completed tranche should be restarted.

## Git and recovery

Initial clean development commit: cf4cdb90e5fbcefbd0f2606d551d6a05100fd545. Isolated branch: pilot/whiston-antiquities-book01-20261010. Isolated worktree: C:/workspace/LatinJosephus-BookI-Pilot-20261010. GIT_RECEIPT.json and RECOVERY.md record the implementation/export commits. No merge, push, deployment or later-book processing occurred.

A and B were exported before alignment. Seven C archives were exported immediately after validated ranges 1–50, 51–100, 101–150, 151–200, 201–250, 251–300 and 301–346. Initial network failure and reader-test failures triggered immediate local emergency exports. A/B/C copies are uploaded to the private recovery Page; final D includes all cumulative evidence and scripts. Every archive has a SHA-256 sidecar and passes ZIP integrity validation. Incomplete and uncertified exports are labelled PARTIAL — NOT CERTIFIED.

## Proposed Books II–V plan

After separate authorization, use a fresh profile/worktree for each authorized book. First recover that book's published fine HTML segmentation and verify identities against Greek. Before inserting boundaries, collate complete word extents to identify inherited losses and corrupt spellings. Use unique anchors with predecessor context; manually adjudicate any skipped-prefix, joined-word or missing-text case rather than subtracting word counts. Check challenged Greek positions against Niese print, including boundaries within lines, clauses or quotations. Preserve source wording and all existing markup.

Keep batches at ≤50 starts and export A/B/C/D independently with exact resume state. Introduce reader support through a separate reviewed integration, then verify every direct English interval plus all containing views before proposing GO. Book I's separate proem and its 17 exceptions do not carry over to another book. The pilot justifies retaining immutable raw witnesses, distinguishing extraction confidence from alignment confidence, doing full source-difference review earlier, and treating marginal numbers carefully. No work on Book II has begun.
