# Antiquities VII.2-6 Whiston context: final local repair report

PASS for all five contextual-display issues. Every section's corresponding Whiston wording survives in the unchanged first English paragraph. The candidate recovers that complete paragraph once per individual selection, and once across either combined VII.1-6 or VII.2-6 selection. The exact-segmentation-unavailable qualification remains. No translation was fabricated, rewritten, split or merged; no editorial hold or section-specific release exception is needed.

## Decision table

| Section | Diagnosis | Corrective action | Final status |
|---|---|---|---|
| VII.2 | Surviving obeisance/battle report omitted by parent-ID lookup; Greek 2 ends before Greek 3 | Recover the complete existing first paragraph once as qualified context | PASS |
| VII.3 | Surviving messenger/Saul account omitted; Whiston's existing translation phrasing is preserved | Same generic first-paragraph context recovery; no translation correction | PASS |
| VII.4 | Surviving bracelets, crown and mourning omitted; no underlying English lacuna | Recover the complete existing paragraph, including all these clauses | PASS |
| VII.5 | Surviving Jonathan/punishment material omitted; Whiston sentence continues into Greek 6 | Preserve coherent whole paragraph rather than invent a sentence/section split | PASS |
| VII.6 | Surviving execution/laments omitted; corresponding English starts within a sentence | Recover existing complete paragraph and retain contextual qualification | PASS |

Each diagnosis was separately established. `SOURCE_ASSESSMENT.md` gives the exact Greek text from its printed XML number through the next number (exclusive), or paragraph end for section 6, and the corresponding surviving English excerpt. `evidence/SOURCE_ASSESSMENT.json` preserves exact strings, offsets and source hashes. These English excerpts are semantic correspondence evidence, not newly approved English Niese segmentation. Whiston's VII.3 phrasing and the VII.5-6 semicolon construction remain as transmitted in the source.

## Before and after, and source provenance

Fresh baseline: `705aebf7a05681012d239707baed5ea2bdd806d2`, fetched and directly verified on origin/v2-development. Direct VII.2-6 baseline observations contain only the generic context notice, with zero narrative paragraphs; no surviving paragraph is merely truncated or duplicated. The underlying English XML contains every identified missing clause in `english-book07-num1`, targeting `#latin-book07-num1`. Actual Latin containing paragraph is `latin-book07-num`, with independently certified milestones 2-6. Greek has actual numbers 1-6 in `greek-book07-num1`; section 7 starts in `greek-book07-num7`.

`DISPLAY_EVIDENCE.json` supplies each exact before/after English DOM and text, observed URL, full original English paragraph, corresponding excerpt, exact Greek extent and final decision. Source-backed direct VII.1-7 tests verify every Greek extent against its original XML numbers and complete Whiston paragraph against XML. Normalised visible-text checks are supplemented by the combined renderer's exact source-DOM text equality, preserving punctuation and whitespace; all source files are independently byte-hashed.

The original issue register remains intact in canonical's historical integration review and in `evidence/ORIGINAL_VII2_6_ISSUE_REGISTER.md`. The new assessment supersedes its pending publication disposition through independently observed recovery; its original findings were not rewritten. Existing source XML IDs, sameAs relationships, numbering, provenance and paragraph boundaries remain unchanged.

## Generic implementation and range scope

The existing guarded opening-context fallback is extended from the first Niese number to any supported start physically inside that same first canonical paragraph. It still requires the actual unsuffixed first narrative ID, no existing suffixed canonical paragraph, empty normal mapping, no explicit contextual override, and exactly one witness paragraph with one explicit matching sameAs target. No Book VII number or section list is hard-coded in production.

The context renderer also accepts a list of identities for internal combined context assembly. It deduplicates source paragraph nodes before cloning and retains each source paragraph separately, with a single contextual qualification. Explicit source unavailability is retained. Both VII.1-6 and VII.2-6 return only the complete first source paragraph once; repeated/unsorted identities also deduplicate. VII.6-7 returns two complete separate source paragraphs, without merging them. Greek and Latin remain exact single-section projections; the range harness records their existing source interval extents independently.

The public reader still accepts only individual Niese IDs. No new public range selector, query parameter or user-facing combined-range capability is introduced or claimed. The requested combined ranges are tested through the actual context renderer and disposable harness as explicitly approved. The actual supported traditional VII.i.1 URL `?book=7&chapter=1&subchapter=1` supplies the existing containing interval 1-6, which remains unchanged. Chapter and Alignment projections remain unchanged. Direct URLs, previous/next, selector navigation, history and settled reloads are tested on the uninstrumented reader.

## Commits, production manifest and frozen source

- Independent source-assessment commit: `9e69d0681748cad33856486ea5ed2ab7d08518e0`.
- Independently certified implementation commit: `5e75479f0e7150b0e26ab7542fd92b42f5550eaf`.
- Local branch: `fix/antiquities-vii2-6-whiston-context`.
- Worktree: `C:\workspace\LatinJosephus-antiquities-vii2-6-whiston-context-repair`.
- A final review-only certificate commit follows. Its exact clean HEAD is recorded externally in `C:\workspace\Antiquities-VII2-6-Whiston-Repair-runtime-20261010/LOCAL_CERTIFICATION_RECEIPT.json`, avoiding recursive self-commit attribution.

Exactly one production file changes: `assets/js/renderTei.js` (48 insertions, 32 deletions; the same lookup serves single and combined contexts). Its SHA-256 is `c4741903c21c4cc0e4629cdca4d951a5c64ffcab6da5e44e40aaaebcc0e3cad3`; baseline SHA-256 is `a29b150a95037a6e59daa8be8d65394ed245d663d51ccb64f204e4bb696ca89d`. The actual tested built asset is byte-identical to this production file. Among all 251 built assets it is the sole difference. `CHANGED_FILES.json` gives exact hashes for every task change, with its own recursive hash excluded; `BUILD_ASSET_HASHES.json` gives actual built-asset digests.

All 143 scholarly XML files, 14 Niese registries and every other 5037 original tracked worktree file remain byte-identical. Canonical's original files, the VII.1 certified source worktree and the publication worktree were independently hashed and remain unchanged. Greek, Latin, English, structure, notices, numbering and all certified Proem/I-XX editorial data are protected. The dedicated worktree uses committed bytes; legacy canonical checkout line endings are preserved, without normalization.

## Fresh full regression certificate

| Coverage | Result |
|---|---|
| Actual uninstrumented Niese selection replay | 7,376/7,376 baseline and candidate, no unexpected page/network errors |
| Proem / Antiquities I-XX | 26 / 7,350; menus, counts and every first/last ID unchanged |
| Source-neutral complete comparison | Exactly five intended English changes; 7,371 selections identical |
| Greek / Latin | Every selection DOM, text, fragment ID and notice identical |
| Already certified VII.1 and neighbouring VII.7 | Entire English DOM unchanged |
| Traditional | 1,689 unchanged |
| Bamberg | 198 unchanged |
| Alignment | 1,441 unchanged |
| Book / Contents | All 21 contexts unchanged |
| Cross-work source configurations | 21; Bellum/Cardwell/Lodge/Whiston, DEH, Contra Apionem |
| Cross-work Niese / chapter-unit projections | 8,002 / 1,630 unchanged |
| Actual containing controls / reloads | 16 passed |
| Prior focused navigation/panes/themes | 19 passed |
| Additional VII.2-6 navigation/history/reload/presentation | 15 passed, desktop/mobile light-dark |
| Context guards / combined contexts | 8 guards and 4 combined cases passed |
| Explicit exceptional controls | 77 unchanged snapshots, including XI and XX |

`REGRESSION_CERTIFICATE.json` and the 7,376-row `EXHAUSTIVE_NIESE_MATRIX.csv` are authoritative result exports. Actual Niese and focused UI/source tests use uninstrumented production functions. Structural/cross-work projections and combined calls use getter-only disposable hooks and isolated state assignments; baseline and candidate have identical hooks and unchanged selection functions. This distinction is recorded in QA provenance rather than counting projections as public clicks. Full raw Niese registers and disposable builds remain under `C:\workspace\Antiquities-VII2-6-Whiston-Repair-runtime-20261010`.

All existing XI fragment/transposition/interpolation selections, XVI-XIX displacements and source unavailability, XX.27-36/238 and the final narrative/paratext boundary, plus Proem 25-26, are unchanged in the complete comparison. `EXCEPTION_PROTECTION.json` separately indexes 77 controls and confirms that XX.269 remains absent. This certifies preservation of existing decisions, not a new printed-edition adjudication or a claimed fresh facsimile inspection.

## Independently reproduced inherited issues and retained attempts

`BASELINE_EXCEPTIONS.json` independently reproduces equal Home/About/Background startup errors, unsupported I.1's querySelector error (Book I begins at I.27), two I.34 apparatus targets returning 404, Book VII's duplicate annotations ID and the unnamed light-toggle control in both builds. These were not repaired, hidden or newly introduced.

An additional immediate-reload diagnostic shows both builds reloading the previous VII.7 URL when reload is issued before an asynchronous change to VII.6 settles. This newly reproduced baseline timing observation is separately recorded, not silently relabelled as an earlier certified exception. Settled VIΙ.6 selection, URL persistence and reload pass. It does not require an editorial hold on context recovery; further navigation hardening would be a separate task.

Raw setup failures are preserved: a wrong positive-test site argument, an early containing test before its dependency export, the disposable server's initial root-path guard, and the reload race. Successful retests are separate. None caused a production code change after the tested implementation. Build log copies normalize only evidence whitespace; original logs remain in runtime. Browser profiles, downloads, ports and caches are isolated; no other worker's environment is cleared.

## Release recommendation and authorization boundary

The five VII.2-6 context blockers are resolved with no outstanding editorial questions. Recommend proceeding to separate canonical integration and then authorized final public-preview publication and live verification, retaining the documented inherited issues. This local certificate does not certify an already deployed repaired public site.

No merge, push, deployment, rollback, canonical/source/preview content edit, settings change or unrelated cleanup occurred in this task. The final receipt records unchanged canonical and remote baseline, preserved VII.1 source branch/history, frozen preview ref, clean local branch and exact hashes. Canonical promotion and publication remain separately authorized actions.
