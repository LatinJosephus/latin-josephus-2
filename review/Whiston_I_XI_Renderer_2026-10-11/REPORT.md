# Whiston Antiquities I to XI renderer certification

The isolated prototype displays all **3,821 certified English Niese intervals correctly**. Its essential displayed-content and regression gates pass: **RENDERER-GO for this prototype**. Canonical development remains clean at `663b8ce318f0aa247d304d8eeda5b8e76e7489c6`. Books XII and XIII remain untouched. No merge, push or public deployment has occurred.

DATA-GO concerns the supplied segmentation and wording. RENDERER-GO here concerns faithful display of those supplied intervals. It does not certify new translation correspondences, a generic TEI schema, or public publication rights. Book I’s archived delivery still says NOT CERTIFIED; its 346 data checks pass and the mission supplies DATA-GO. This metadata discrepancy is preserved for reconciliation without reopening boundaries.

## Original limitation and implemented behavior

The reader loads each language independently through `fetchTei` and CETEI. Antiquities then always routed English Niese requests to `antiquitiesNieseContextView`, using Latin starts, stable alignment IDs, `sameAs`, and contextual paragraph targets. Adding English milestones could not change that route. The Antiquities exact extractor indexed Latin milestones and Greek labels or registered fragments; it did not use the new English milestones. Bellum already had a separate English milestone extractor.

Whiston’s Antiquities source configuration now explicitly enables exact extraction for the Proem and Books I–XI. The prototype reuses Bellum’s physical milestone interval extraction, with Antiquities-only handling for inline ancestor retention, inherited contextual citation labels and an exact-English notice. Each interval starts after its own marker and ends before the **next physical English marker**, or at the book’s end. Book XI therefore correctly follows physical order 1–311, 326–342, 312–325, 343–347. Numeric navigation remains governed by the canonical identity registry, independently of witness order.

Latin and Greek retain their original exact/fragment paths and qualifications. Traditional Chapters, Subchapters, Book views and Alignment units remain separate selections. English XII–XX retains the original contextual-English notice and paragraph behavior; no segmentation from the ongoing XII–XIII work is assembled.

## Book IX independent witness availability

The source is the restored-and-segmented delivery `2ce18b40ea8652e5e0d5046f10b1c39935fcdc54`. All 59 English intervals IX.51–109 display their certified restored text. Only the English availability flags and English paragraph exclusion are changed in the Niese registry. Every Greek and Latin field remains identical.

Ten inherited English Chapter/Subchapter locators now resolve to the certified English milestones at their already registered Niese starts. Alignment unit 51 binds the complete English IX.51–109 interval, ending at the English IX.110 marker. Greek and Latin omission placeholders and direct-selection notices remain unchanged; the prototype supplies no missing text in either language.

All seven restored Whiston footnotes display with their original text, identifiers and interval ownership. The English notice distinguishes the elected Alden & Beardsley 1856 printing, printed pp. 251–255, from the project’s Greek and Latin omissions. The restoration’s source and licensing qualifications are preserved in [the source receipts](source-receipts/BookIX/PROVENANCE.md).

## Implementation files and commits

The renderer changes are limited to:

- `assets/js/renderTei.js`: explicitly enabled English extraction, physical interval slicing, exact/context distinction and a Niese milestone structural locator.
- `assets/css/tei.css`: visibility of the seven restored Whiston footnotes.
- `assets/xml/antiquities/niese/book-09.json`: 59 independent English availability corrections and its English exclusion list.
- `assets/xml/antiquities/structure.xml`: ten English locators and one English alignment binding.

The twelve English XML files under `assets/xml/antiquities/English/` are assembled directly from delivery commits. Their wording and structure are not edited.

Source assembly commit: `c7525d559d7ac672d6f6e9f1e5e00a77fca5755b`.

Renderer and registry implementation commit: `33d1b7210671b33b4ebe006bd194bfcca5abe8e6`.

The final QA/report commit and reviewable binary Git patch are recorded in the recovery delivery receipt. All implementation commits are confined to `prototype/whiston-i-xi-exact-20261011` in `C:/workspace/LatinJosephus-Whiston-I-XI-Renderer-Prototype-20261011`.

## Sources and preservation

| Book | English sections | Pinned delivery commit | Archived data status |
| --- | ---: | --- | --- |
| I | 346 | `b8cf6c9d36db610ea1dc4c65d070b016048262e1` | PASS; archived NOT CERTIFIED label |
| II | 349 | `3919acbd19d4ad32ef0daa0ec4ff2fbcda9b7e2f` | DATA-GO |
| III | 322 | `671cca7911745be51a7c2cc58ee9f96c404e04bd` | DATA-GO |
| IV | 331 | `02bec3048a5b397b93da0c10043394401ab6c8e8` | DATA-GO |
| V | 362 | `26d7d3edecd643d92596c03c7ff319df65cd19c2` | DATA-GO |
| VI | 378 | `97e416fbc0fd195143f73d7b10f42d2f4987cea4` | DATA-GO |
| VII | 394 | `8071050ce985a0ff69f59437ce618137c9ac192c` | DATA-GO |
| VIII | 420 | `74b8cf1b3505430ff60984d0779e7275da852e59` | DATA-GO |
| IX | 291 | `2ce18b40ea8652e5e0d5046f10b1c39935fcdc54` | DATA-GO |
| X | 281 | `8cb48664e3ec3994416d9dd9d769e0e3f41132ac` | DATA-GO |
| XI | 347 | `5c5557fc6970012251fdca083795d966c7015cfe` | DATA-GO |

Book I’s total comprises 26 Proem sections and 320 narrative sections I.27–346. [SOURCE_INVENTORY.json](SOURCE_INVENTORY.json) records every exact branch, Git blob, delivery QA hash, archive path, archive SHA-256, CRC result and verified manifest entry. All eleven recovery packages have verified sidecar checksums and contents.

| Assembled file | Exact delivery Git blob SHA-256 |
| --- | --- |
| preface.xml | `d04712a2db72f2d2c39e175591b866308f93cb15d10f4ee3be70401f7dd614eb` |
| book-01.xml | `9cd8daf04bddfd94cd96f077c0b9336135c35d017fad029a56fd08e1fc2363f3` |
| book-02.xml | `70da231aafb85aecfec0510bc7489441ca8263b45e31dd33f3ed2f20237aa584` |
| book-03.xml | `0c663f9776a1249d85ceab2ad0bfa47dc3b537864598f4855a668e23e642df44` |
| book-04.xml | `6d58dfa865b47e1a1f347f8f322f578381e6f8a407c597e2f36ae3bd120c6554` |
| book-05.xml | `a8ab9d6b66e6d4a768f3fc247240d6423d5d9687a3f1026f327f9ea387560722` |
| book-06.xml | `116338d9f8a424bfb2ec63af5531b3c72941708ae00e7f327ba8909dc1e125eb` |
| book-07.xml | `d8109c20ceca61283dd5150bf2059f3cffda924f5f82625a4e6b1073b4c60eb3` |
| book-08.xml | `609cedd3dbab1f7af831877f2aea820781e2b34b6c998ab41b3ffa6cb0fb8289` |
| book-09.xml | `d973618661bacf96f0a7ea81f1d7e44147f7826ff1d247908467b238263edc36` |
| book-10.xml | `7f4fde2921f8c5fc670d688174f5c67f81eed7c264c63af89b6c7adb0725e7eb` |
| book-11.xml | `0bdcc522c1f227dab7a61b19a4bef09a590af2bf25cbdce581277469c082acb2` |

All twelve assembled files are byte-identical to their pinned delivery Git blobs, both in the worktree and source assembly commit. Recovery outputs VI–XI use CRLF where Git stores LF; both hashes are recorded, and their complete parsed XML trees are identical. [SOURCE_PRESERVATION_QA.json](SOURCE_PRESERVATION_QA.json) verifies the restricted production diff, unchanged other witness/source blobs, unchanged Greek/Latin registry fields, and the unchanged canonical and XII–XIII worktrees.

## Actual displayed content QA

An independent Python XML-event traversal produces the expected intervals without using production JavaScript or DOM Range. Chrome drives the real Niese selector and observes completion of the real renderer. Every selection is compared for complete prose and punctuation, opening and closing boundaries, visible narrative, citation identity, footnote ownership, and unchanged canonical Greek/Latin DOM. Whitespace is normalized according to browser display; raw boundary text is retained for containing-range concatenation. Inherited contextual citation labels and UI notices are excluded from prose comparison and checked separately.

| Gate | Result |
| --- | --- |
| Every English Niese selection | **3,821 / 3,821 PASS** |
| Greek and Latin presentation for those selections | **3,821 / 3,821 unchanged** |
| Restored IX.51–109 | **59 / 59 PASS** |
| Complete English files | **12 / 12 PASS** |
| Traditional Chapter and Subchapter views | **967 / 967 PASS** |
| Alignment views | **823 / 823 PASS** |
| Direct URL and Previous/Next checks, including Proem transition | **57 PASS** |
| Contextual fallback checks for XII–XX | **18 PASS** |
| Bellum displayed-content regressions, Whiston and Lodge, all seven books | **70 PASS** |
| Contra Apionem displayed-content regressions, both books | **10 PASS** |
| DEH displayed-content regressions, all five books | **25 PASS** |
| All certified anchors, line breaks and emphasis elements, including notes | **18 elements in 16 selections PASS** |
| Browser script errors and failed requests | **0** |

The boundary fixtures include Proem 1 and 26, I.27, VII.1, IX.49–52 and IX.108–111, and XI.311/312/325/326/342/343/347. All literal quotation punctuation is covered by the complete interval comparisons. [PER_SECTION_QA.csv](PER_SECTION_QA.csv) and [BROWSER_QA.json](BROWSER_QA.json) retain every section’s expected and displayed hash, opening/closing text and witness comparison. [REGRESSION_QA.json](REGRESSION_QA.json) retains every structural and cross-work result. Screenshots under `evidence/` supplement the content checks.

The existing DEH concordance extraction harness also passes **2,115 component checks**, **8,193 section occurrences**, **1,110 DEH source checks**, 21 final-boundary checks and eight eligibility guards. Lodge source switching passes all seven books at four levels, with back/forward history, note visibility and the VI.3 omission notice intact. These results are in [AUXILIARY_QA.json](AUXILIARY_QA.json).

## Remaining technical and source record issues

Three historical launchers stop at obsolete corpus-wide guards before their browser tests. One still requires 107 tracked XML files, whereas the pinned canonical commit already contains 286; the others assume a historical inventory or hashes that include subsequently changed Antiquities. Their code remains unchanged. The replacement gates compare current displayed content to the pinned canonical reader, protect unchanged source inputs, and execute the full DEH extraction harness and Lodge controls. [HISTORICAL_GUARD_AUDIT.json](HISTORICAL_GUARD_AUDIT.json) preserves the original launcher failures. Update these launchers’ scope before relying on them for future integration CI; do not weaken the production concordance guard.

DEH/Bellum’s reviewed authority hashes bind CRLF publication bytes. A fresh LF Git checkout fails that byte guard despite identical XML text and structure. The generated local preview preserves the existing reviewed byte representation for 44 unchanged cross-work XML files; no repository witness source or frozen hash is altered. [PUBLICATION_BYTE_REPRESENTATION.json](PUBLICATION_BYTE_REPRESENTATION.json) records the exact input/output hashes. Canonical integration needs a reproducible build policy for these existing hash-bound inputs.

Reconcile Book I’s historical NOT CERTIFIED packet label with the mission’s DATA-GO record. The pre-existing Greek I.272 control qualification and other scholarly qualifications remain preserved; no new scholarly boundary decision is requested. Book IX’s mixed source/licensing notices also remain applicable to any later publication.

## Controlled canonical integration

The isolated implementation is technically ready for review. Review the two implementation commits and source inventory, reconcile the Book I delivery-status record, and preserve the reviewed publication byte representation. Then, under separate authorization, integrate into a new worktree pinned to the actual canonical HEAD and rerun these gates against that state. Enable only the books whose certified sources are assembled; coordinate any later XII–XIII expansion with their independent deliveries. Review source notices and publication qualifications before any separately authorized public deployment.

## Recovery and local review

The recovery archive is `C:/workspace/Whiston-I-XI-Renderer-Delivery-20261011/Whiston-I-XI-Renderer-Prototype-Certified.zip`, with a separate SHA-256 sidecar and verification receipt. It contains the exact changed files, certification evidence, per-entry checksums, an implementation bundle with the pinned canonical prerequisite, a binary Git patch, and a runnable local reader preview. The recovery verifier checks archive CRC, every entry checksum, source identities and a local Git recovery checkout. It does not merge, push or deploy.

The generated preview is at `C:/workspace/Whiston-I-XI-Renderer-runtime-20261011/site`. `tools/preview.cjs` serves it on loopback for local review. `RECOVERY.md` supplies rebuilding and recovery instructions.
