# Locally certified Antiquities VII.1 Whiston context repair

**PASS WITH PRE-EXISTING ISSUES — F001 repaired locally; ready for separately authorized canonical promotion.** No push, merge to canonical or preview deployment occurred.

## Baseline, isolation and root cause

Canonical source branch and remote remain `cf4cdb90e5fbcefbd0f2606d551d6a05100fd545`. Published preview checkout and remote remain `e846e84bc0cd9392b504f5a60f43870084e85403`. The public marker's source attribution and digest were verified at start and finish, without changing the frozen marker. The canonical remote's separate default master is recorded in the receipt; it is not the v2-development release branch. Public reproduction remains [VII.1](https://latinjosephus.github.io/antiquities/?book=7&niese=1) until separately authorized publication.

Worktree: `C:\workspace\LatinJosephus-antiquities-vii1-whiston-context-repair`. Branch: `fix/antiquities-vii1-whiston-context`. Implementation/test commit: `ac3ae682f6b84c652f0cadb4c072d242b0aea602`. Final certificate/evidence commit is this branch's tip, recorded with its clean status in `C:\workspace\Antiquities-VII1-Whiston-Repair-runtime-20261010/FINAL_RECEIPT.json`.

The fresh baseline reader independently reproduces the missing narrative. Its real settled selection is VII.1 in all three panes. `antiquitiesNieseContextView` resolves the Latin selection's containing paragraph ID `latin-book07-num`. `canonicalParagraphTargetIds` returns English's explicit normalized target `latin-book07-num1`; `alignedParagraphsForCanonicalId` rejects the unequal IDs. The read-only resolver trace records zero ordinary matches, one explicit English candidate and no real suffixed canonical paragraph. This proves lookup failure rather than source absence, clipping or pane lifecycle.

Pinned source evidence confirms Latin ID `latin-book07-num`, Greek ID `greek-book07-num1` and sameAs `#latin-book07-num1`, and English ID `english-book07-num1` and sameAs `#latin-book07-num1`. Whole-file SHA-256: Latin `007c55e567380452339dd579748bd40543897bf9d8dec7bb20c7cbafe19b6a3e`, Greek `1ecd613ea829466177ea90f6699e7f44e40fdcf7e0b219504796a7cc1862a18f`, English `48707b448f1d424ddcbf7e464dbbbceef279629a3ea3030702b042e7e4233cf7`. The original independent audit's Z001/B001/B002 failures and N132/R167 timeouts are retained unchanged with their superseding records and provenance; its previous-preview screenshot was inspected. No prior certificate substitutes for these fresh tests.

## Minimal reader change and observed result

Only `assets/js/renderTei.js` changes production behavior: one const-to-let declaration and 15 added lines. The generic fallback is confined to Niese 1, an empty ordinary lookup, no registry context override, the first narrative paragraph's unsuffixed ID, absence of the suffixed canonical ID, and exactly one explicit single-target source sameAs match. It uses the existing contextual cloning and notice. It invents no source relationship or executable start and never enters Latin/Greek exact slicing or structural projections. Eight focused fixture checks prove normal recovery and conservative rejection of missing/ambiguous sameAs, duplicate candidates, an existing suffixed canonical paragraph, a non-opening paragraph and an interior milestone.

Before: English shows only `English context: exact Niese-level segmentation is unavailable for this source.`

After: that qualification remains verbatim, followed by the complete surviving paragraph once, beginning `1. This fight proved to be on the same day whereon David was come back to Ziklag` and ending `which have continued to my own age.` The complete source-versus-render comparison is retained in `evidence/candidate-final-VII1-REGRESSION.json`; it does not claim exact English Niese segmentation. English remains type `niese-context`, with one `english-book07-num1` and no duplicate English pane IDs.

Latin still starts `Praedictum itaque praelium` and ends `asperso capite cinere,` for VII.1. Greek still starts `Συνέβη δὲ ταύτην` and ends `τὴν κεφαλὴν τέφρᾳ περιχεάμενος.` Both pane DOMs and text hashes equal the fresh baseline exactly, including after navigation and reload. The Latin source opening ID remains unchanged in the source and full Book view.

The first physical Latin paragraph also contains milestones 2–6. The requested sole VII.1 delta is enforced: the inherited empty English Niese contexts at VII.2–6 remain unchanged and outside this scoped repair. Full Book and approved traditional containing views continue to show surviving contextual English. No wider variation is waived as harmless.

## Fresh verification

The exact final reader SHA-256 is `a29b150a95037a6e59daa8be8d65394ed245d663d51ccb64f204e4bb696ca89d`; its built copy equals the committed reader bytes. All tests below ran anew against the frozen baseline and the final candidate, using loopback servers, isolated Chrome profiles and owned downloads under the runtime directory. No external account or source-state control was operated.

| Gate | Result |
| --- | --- |
| Baseline positive VII.1 English test | Expected FAIL: proves regression sensitivity |
| Final permanent positive source-English test | PASS: complete paragraph, once, qualification and contextual type retained |
| Baseline and final actual Niese dropdown selections | 7,376 each: 26 Proem + 7,350 I–XX |
| All pane DOM/text, IDs, notices and duplicate-ID counts | PASS: sole delta is VII.1 English |
| Traditional Chapter/Subchapter projections | 1,689 PASS |
| Bamberg projections | 198 PASS |
| Alignment projections | 1,441 PASS |
| Full Book and Contents views | 21 contexts each, unchanged |
| Cross-work Book/source configurations | 21 PASS |
| Cross-work Niese projections | 8002 unchanged |
| Cross-work Chapter/Alignment projections | 1630 unchanged |
| Lodge notes hide/reload/restore and Whiston switching | PASS |
| Real navigation and presentation assertions | 19 PASS |
| Real containing-view/direct-reload assertions | 16 PASS |
| Guard fixture assertions | 8 PASS |
| Supported selection browser/console/network errors | 0 |

The exhaustive matrix checks Latin/Greek exact outputs and every notice unchanged, protecting XI's canonical fragments and Bellum interpolations, XVI–XIX displaced/unavailable material, XX's unavailable 27–36/238 and exclusive ends, and Proem 25–26. Complete DOM comparison protects physical order in Book/Alignment and registered structural endpoints; it does not replace scholarly adjudications. Cross-work controls cover Bellum/Cardwell with both Whiston and Lodge, all DEH books and both Contra Apionem books.

Actual UI tests cover VII.1, VII.2, nearby selections via the exhaustive matrix, VII's last supported identity 394, VI.378 → Book VII → Niese VII.1, and VII.394 → Book VIII → Niese VIII.1. Book switching's established reset to Book view is preserved. Book VII has zero registered Bamberg rows and its control remains disabled; a supported Book XX Bamberg route was tested through the real control and direct reload. Chapter/Subchapter and first/last available Alignment URLs were obtained from actual controls. Light/dark themes were exercised at 1440 and 390 pixel widths; screenshots show complete contextual English in the correct pane.

| Context | Count | First | Last |
| --- | ---: | ---: | ---: |
| preface | 26 | 1 | 26 |
| 1 | 320 | 27 | 346 |
| 2 | 349 | 1 | 349 |
| 3 | 322 | 1 | 322 |
| 4 | 331 | 1 | 331 |
| 5 | 362 | 1 | 362 |
| 6 | 378 | 1 | 378 |
| 7 | 394 | 1 | 394 |
| 8 | 420 | 1 | 420 |
| 9 | 291 | 1 | 291 |
| 10 | 281 | 1 | 281 |
| 11 | 347 | 1 | 347 |
| 12 | 434 | 1 | 434 |
| 13 | 433 | 1 | 433 |
| 14 | 491 | 1 | 491 |
| 15 | 425 | 1 | 425 |
| 16 | 404 | 1 | 404 |
| 17 | 355 | 1 | 355 |
| 18 | 379 | 1 | 379 |
| 19 | 366 | 1 | 366 |
| 20 | 268 | 1 | 268 |

## Integrity, inherited issues and retained failures

All 143 scholarly XML files, 14 Niese registry JSON files, structure inputs, editorial notices and all 4,940 unrelated tracked baseline files are byte-identical to integration start. Canonical's 4,941 tracked files and preview's 1,051 tracked files were checked individually at start and finish; both checkouts remain clean at the frozen commits. The original independent audit files' hashes also remain unchanged. Only the dedicated worktree/branch, local reader, review evidence and runtime were written. Shared Git metadata necessarily records the authorized new worktree and local branch; no other branch/worktree was edited, reset or switched. Concurrent Book-I pilot work was inventoried read-only.

The isolated native builder produced 263 files. Only the reader differs among built assets. Two other generated outputs differ solely by build timestamps: DEH's existing CSS/JS cache-version query strings and Atom feed updated time. Their full diff is retained in `evidence/BUILD_NONASSET_DIFFERENCES.json`; DEH content and all its projections are equal. No generated site is committed or copied into publication.

The inherited duplicate `annotations` DOM ID is preserved with equal counts in both builds across the exhaustive routes. The theme control's inherited unnamed markup, Book-I apparatus targets, unsupported I.1 and Home/About/Background startup findings remain outside the repair. Their earlier independent evidence remains identifiable in `evidence/AUDIT_EVIDENCE_READ.json` and the unchanged audit directory; no broad claim that these defects are fixed is made. These unsupported/startup and apparatus routes were not rerun or waived by the supported-identity suite.

All test setup failures are retained separately. Initial reproduction attempts targeted generic Bootstrap attributes rather than the actual MDB control; the successful settled retest uses the observed `data-mdb-target`. The first exhaustive baseline attempt had settings collapsed. Focused UI attempts tried to hide mandatory Latin, access the collapsed mobile theme control, retain Niese state after a Book switch, or open unsupported Bamberg controls in VII/VIII. These are harness assumptions corrected to the actual supported UI, with raw result exports retained; no production code was changed for them. The first candidate's line-ending rewrite was caught by diff checking, restored to original LF and followed by complete fresh final-build tests. No raw independent audit failure was rewritten. `evidence/HARNESS_ATTEMPTS.json` distinguishes these setup observations from reader defects.

## Handoff

The production fix and permanent test are committed locally. `LOCAL_CERTIFICATE.json`, `EXHAUSTIVE_NIESE_MATRIX.csv`, the structural result, complete source-integrity manifest, isolation receipt and before/after screenshots certify this scoped candidate. `CHANGED_FILES.json` lists every changed file and SHA-256; the manifest omits its own recursive hash. Full raw baseline/intermediate/final route registers and disposable builds remain under `C:\workspace\Antiquities-VII1-Whiston-Repair-runtime-20261010`. Reproducible scripts and invocation instructions are in `qa/`.

No push, canonical merge, preview refresh, deployment, production domain/settings change or rollback occurred. Promote and publish only in a separately authorized task. The runtime final receipt records the final evidence commit, clean branch status and unchanged frozen canonical/public refs.
