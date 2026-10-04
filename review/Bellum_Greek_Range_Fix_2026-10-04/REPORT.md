# Bellum Greek Chapter/Sub-chapter range repair — 4 October 2026

## Checkout and scope

Production checkout: `C:\Users\Pollard_R\Git\LatinJosephus-v2-development`.

Recorded before work:

- Branch: `v2-development`.
- HEAD: `b11075ac14272f0cda568f3bd8859cb0ba405aed`.
- `git status --short`: empty.

The supplied expected HEAD `253771e7cbaf5eede6f7d6303c632afb0c621ef4` had been superseded by the completed Antiquities VI commits. The isolated repair uses the actual clean current HEAD and retains those commits.

Repair worktree: `C:\workspace\LatinJosephus-bellum-greek-range-fix`, branch `bellum-greek-range-fix`. Its Git object store is the existing writable local mirror `C:\workspace\LatinJosephus-lodge1602-git`; the production checkout was read only throughout. Nothing was pushed.

The sole production-code change is `assets/js/renderTei.js`. No XML, witness links, English rendering, Lodge note controls, citation placement, or other work's renderer path was changed.

## Exact cause and provenance

**PRE-EXISTING** at `57b89a9d107bb76a2b30c146e401a2c76e25e4c3`.

Actual browser reproduction used each revision's renderer without moving the production branch. Bellum Latin and Greek XML have no differences between that revision and the current base. Both revisions omit I.87 in Chapter IV and in coarse unit `latin-bellum1-num86`, while direct Niese 87 displays correctly. Equivalent omissions were reproduced in Books III, VI and VII.

`selectView` sent Greek Chapter views to `alignedChapterView`, and Greek Sub-chapters to `alignedSectionView`. Those helpers compared `canonicalParagraphTargetIds` with selected **coarse Cardwell paragraph IDs**. The target resolver used `sameAs`, then a mirrored-ID fallback, then a visible-number fallback. The Greek I.86 paragraph has no `sameAs`, so its ID becomes the target `latin-bellum1-num86`. Greek I.87 similarly becomes `latin-bellum1-num87`, which is absent: I.87 starts at an internal milestone inside coarse paragraph 86. Consequently Chapter IV showed Greek 85, 86, 88, … and Sub-chapter 86 showed only Greek 86.

This was an incomplete coarse-unit alignment model, not a parser failure or a Lodge regression. No Lodge-era commit was reverted.

## Repair

The Bellum Greek Chapter/Sub-chapter path now locates the selected original canonical Cardwell paragraphs and establishes their half-open DOM range. It reuses `latinNieseStartEntries`, including both independently confirmed inherited paragraph identities and internal Niese milestones.

For every canonical Niese span, the renderer tests interval overlap with the selected Cardwell range. It includes the section already running at the range start, then every later overlapping section. It clones whole Greek `tei-p[n]` paragraphs in their canonical source order. Coarse ID suffixes locate Cardwell paragraphs only; they never establish Niese identity.

The two actual split-section boundaries in this corpus are exercised explicitly:

| Running section | Adjacent Cardwell coarse units |
|---|---|
| III.3 | `latin-bellum3-num1` → `latin-bellum3-num3` |
| VI.427 | `latin-bellum6-num420` → `latin-bellum6-num427` |

Each running Greek paragraph appears legitimately in both neighbouring Sub-chapter views. No Greek paragraph is split.

## Independent exhaustive QA

The raw-XML oracle does not call renderer helpers or use its DOM interval algorithm. It walks canonical Latin XML events, carrying the active valid Niese citation into each coarse paragraph and changing it at inherited starts or milestones. It paints each paragraph with its overlapping identities and unions these for Chapters. Canonical Greek XML supplies the ordered inventory and expected text.

Every native Chapter, Sub-chapter and direct Niese control value is driven in the actual built reader. Actual Greek identities must equal the independently expected identities **in exact order**. Canonical Latin starts and Greek inventory must also equal each book's complete contiguous section sequence.

| Book | Chapter views | Sub-chapter views | Direct Niese views |
|---|---:|---:|---:|
| I | 34 | 234 | 673 |
| II | 22 | 143 | 654 |
| III | 10 | 88 | 542 |
| IV | 11 | 78 | 663 |
| V | 13 | 65 | 572 |
| VI | 10 | 50 | 442 |
| VII | 11 | 46 | 455 |
| **Total** | **111** | **704** | **4,001** |

The same exhaustive traversal is performed with Whiston and Lodge selected. Every Cardwell and English pane's HTML and extracted source text is compared with the unchanged current-base renderer; direct Greek pane HTML is compared too. Per-view SHA-256 records are retained in `QA.json`.

Explicit checks cover:

- I.4: Greek 86, **87**, 88 in sequence; actual I.87 text equals `greek-bellum1-num87`.
- Coarse I.86: internal-start Greek 87 present.
- First and final sections in all seven books; all Chapter transitions.
- Both adjacent coarse-unit overlap cases above.
- III.3, VI.267, VI.356, VI.427 and VII.26, with canonical owner IDs.
- Direct Greek and Latin text for all 4,001 Niese sections.
- Lodge notes, reload/navigation/source-switch persistence of `lodgeNotes=0`, I.33 citation on the prose line, and visible VI.3 omission.
- Existing `lodgeSourceStateQA`: all seven books and four levels, witness changes, history and reload.
- Existing `lodgeReaderQA("lodge1602")`: exact canonical Lodge XML source words across the whole corpus and the frozen rendered-text/ID digest.
- Frozen Lodge source-tree/master checks and all nine existing corruption-detection self-tests.

The existing unscoped Lodge static script stops on its historical 100-file inventory's Antiquities VI hash. This also fails in the unchanged production checkout. Its inventory predates the approved Antiquities VI release. The Bellum-only invocation retains all frozen-master, source-tree, 21 original Bellum XML, seven Lodge XML, linkage and self-test assertions; only that superseded non-Bellum historical loop is excluded. The repair's separate 107-file before/after SHA-256 comparison covers the actual current XML inventory.

Browser environment: installed Chrome/Chromium and the actual built page shell. Renderer, CETEI, TEI CSS and XML come from the repair checkout; compiled main CSS comes from the built site. The established offline `HTMLCollection.forEach` adapter is supplied. Unavailable external CDN shell dependencies are reported separately. An initial host omitted the compiled main CSS; this was corrected. All membership/text/DOM comparisons completed, and focused layout/control checks and final host/error checks passed with the corrected host.

## Reproduction commands

From the repair worktree, using a built site and installed Playwright/Chromium:

```powershell
$taskQaArgs = @(
  '--site', 'C:\Users\Pollard_R\Git\LatinJosephus-v2-build',
  '--module-root', 'C:\Users\Pollard_R\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules',
  '--browser', 'C:\Program Files\Google\Chrome\Application\chrome.exe'
)
node --check assets/js/renderTei.js
node bin/bellum-greek-range-qa.mjs @taskQaArgs
node bin/bellum-greek-range-qa.mjs --focused-only @taskQaArgs
node bin/bellum-greek-range-qa.mjs --existing-lodge-only @taskQaArgs
node bin/bellum-greek-range-qa.mjs --existing-static-only --master-zip C:\Users\Pollard_R\Downloads\Lodge1602_Bellum_FINAL_ADJUDICATED_20261003.zip @taskQaArgs
git diff --check
```

The default exhaustive run starts fresh. `--resume` is an explicit optional checkpoint recovery mode, guarded by content fingerprints. The historical defective comparison renderer defaults to the clean repair base `b11075a`; it remains available after the fix is committed.

## Final result

See `QA.json` for measured final counts, per-view equality evidence, fixtures, witness regressions, and all 107 before/after XML hashes. Commit message: `Fix Bellum Greek range display`. No push.
