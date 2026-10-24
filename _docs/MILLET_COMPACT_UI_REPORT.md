# Compact Millet DEH reader — local implementation

Completed 24 October 2026 by MilletWorkBot2. Local preview only; no push or deployment.

## Result

Global book, chapter and sub-chapter navigation occupies the first desktop row; viewing level and text-pane choices occupy the second. Hidden navigation forms and empty source-selector containers no longer reserve space. The change is scoped to DEH. Existing typography, red pane headings and other readers are retained.

The French heading is followed by a small, labelled Highlight correspondences checkbox and About, Settings, Link and Correspondence controls. Settings contains the six existing French modes, optional folio numbers, native chapter/folio navigation and the independently selectable Aligned passage menu. These are native inline disclosures, not overlays. All correspondence evidence, secondary observations and inherited editorial flags remain available.

The second passage selector is not redundant: it can select any correspondence in the book and locate its Latin target. It is now labelled Aligned passage and placed in French Settings. Selecting only a global chapter clears the global sub-chapter while the independent French selection can remain; selecting an actual global sub-chapter synchronises the texts. This existing distinction was preserved.

In a single-unit running view, the French citation appears in bold brackets, e.g. [I.43.3], at the start of the passage. In larger book/source views, the selected citation appears in the Correspondence disclosure label so it does not mislabel the beginning of the book. Citation markup sits outside exact source-line and character-offset nodes.

Display preferences and open disclosure state survive ordinary in-page navigation. Checkbox/select focus is restored after rerendering. French controls disappear with their pane. Existing URL parameter names, deep-link semantics and selection events are retained.

## Before/after measurements

Actual installed Edge 156.0.4314.42; same I.43.3 deep link, three panes, global settings fully expanded, French settings closed. Measurements wait for the accordion animation to finish. Positions are document CSS pixels, not screenshot raster dimensions.

| Viewport | Previous pane start | Revised pane start | Vertical space recovered |
|---|---:|---:|---:|
| 1440 × 900 | 687.4 | 237.1 | 450.3 |
| 1366 × 768 | 757.8 | 237.1 | 520.7 |
| 390 × 844 | 968.3 | 389.7 | 578.6 |

At desktop sizes, French begins approximately 27 pixels below Latin/English with its compact controls visible. Real source headings and source-specific material remain intact. On mobile, the established panes stack vertically; the gallery includes both the page top and a separate French-pane view.

Before screenshots were reproduced with the prior generated DEH page and the exact reader/CSS bytes from baseline commit 8fd9a486f61935d4f9177653e89fad948eeb4a40. The comparison uses the same browser, text, viewports and fonts.

## Validation

| Check | Result |
|---|---|
| Full configured Jekyll build | PASS; all configured plugins; duration recorded in BUILD_FINAL.log |
| Publication preparation and corpus guard | PASS; 166 production XML files and 38 frozen publication inputs |
| Existing Millet and search Node regressions | PASS; 65 tests, including all 11 Millet tests |
| Deterministic Millet importer, check only | PASS; nine data assets, 558 units, 19,104 source lines |
| Full existing Millet browser suite | PASS; all 558 exact canonical texts and French highlight selections; 348 cross-page units |
| Focused responsive browser suite | PASS at 1440 × 900, 1366 × 768 and 390 × 844; no horizontal overflow |
| Before/after source DOM and selected intervals | PASS; exact source strings, codepoint/UTF-16 offsets, mapping IDs and selected characters unchanged |
| Interface behaviours | PASS; one/two/three panes; keyboard controls and focus; six French modes; folios; disclosures; global and independent selection; share-link reload; history; long I.43.3 passage |
| Existing reader browser smoke tests | PASS; 10 checks covering Lodge/Whiston, Latin/Greek/English, AJ comparison and search |
| Existing DEH–Josephus integrity tests | PASS; source acceptance and corruption rejection; French-to-parallel round trip passes |
| Browser JavaScript/local asset errors | Zero in the final Millet browser runs |
| Protected site files | PASS; 179 starting hashes unchanged, including all 166 XML files, Millet data and alignment core |
| Certified master XML and alignment JSON | PASS; both match their frozen hashes |
| Generated source identity | PASS; final reader, CSS, alignment core and parallel code match source bytes |
| Whitespace/error check | PASS |

The initial focused probe expected a chapter-only selection to replace the independently selected correspondence. The recorded attempt timed out. The test was corrected to preserve that established distinction, then verify full global sub-chapter selection and independent correspondence selection separately; no scholarly or alignment logic was changed to satisfy the probe. The first failed probe is retained in the external records. Screenshot capture was also refined to wait for accordion completion and return to the document top before comparison.

Browser QA was performed both through actual installed Edge automation and visual inspection in the in-app browser. This is functional/presentation QA, not a new scholarly proofreading pass. No formal XSD validation or measured CER is claimed.

## Preserved state and limitations

Starting branch: millet1556-deh-integration-20261024. Starting HEAD: 8fd9a486f61935d4f9177653e89fad948eeb4a40. The working tree was clean; there were no unrelated modifications to preserve in this worktree. The original development checkout and previously issued packages were not changed.

Latin remains the mandatory pane, as in the existing reader; the single-pane test uses Latin alone. At narrow widths the panes stack. Expanded settings intentionally take space within the French pane. The pre-existing historical AJ Latin comparison pin mismatch remains: its guard refuses stale pins; AJ Greek/English and the ordinary reader pass. No source or historical pin was changed.

The existing Sass deprecation and Faraday retry warnings remain. The initial sandboxed Ruby launch failed; the installed build ran successfully with approved local access. No package installation, public push or deployment was performed.

## Exact changed files

- _includes/display-settings.html — DEH-only compact labels/class, pane order and removal of the global Millet block.
- assets/css/millet.css — DEH navigation layout, responsive wrapping, inline French controls, focus styling and citation presentation.
- assets/js/milletReader.js — French-pane controls/disclosures, focus preservation and bracketed interface citation; exact source rendering and alignment core retained.
- _pages/millet-1556.md — edition-page directions updated to the actual French-pane control locations; scholarly account and conventions retained.
- bin/millet1556-browser-qa.mjs — existing browser tests updated for controls in French Settings.
- bin/millet1556-compact-ui-qa.mjs — actual-browser before/after and focused responsive acceptance checks.
- _docs/MILLET_COMPACT_UI_REPORT.md — this report.

## Evidence and reproduction

External evidence directory:

`outputs/Millet_Site_Integration/MILLET_COMPACT_UI_20261024_WorkBot2`

It contains BEFORE_AFTER.html, full-size screenshots, starting state and protected hashes, browser results, build/test logs, generated-source identity, final commit receipt and RESUME.md. The final commit hash is in FINAL_STATE.json; this report is part of that commit.

The local preview is http://127.0.0.1:4019/deh/?book=1&chapter=43&unit=3&french=millet1556&millet-unit=latin-deh1-num188&millet-align=0 . The generated directory remains the short temporary destination recorded by the preceding integration.

Reproduction commands from this isolated worktree, using the existing configured Ruby environment and bundled Node/Playwright:

```text
node --test bin/millet1556-qa.test.mjs bin/search/tests/ui-utils.test.mjs bin/search/tests/browser-release.test.mjs bin/search/tests/deh-presentation.test.mjs
python bin/millet1556-import.py --master <certified-master-directory> --check
bundle exec jekyll build --destination <short-generated-directory> --disable-disk-cache
node bin/prepare-reader-publication.mjs --site <short-generated-directory>
node bin/reader-corpus-qa.mjs --site <short-generated-directory>
node bin/millet1556-browser-qa.mjs --base-url http://127.0.0.1:4019 --output <external-evidence>/all_units --browser-executable <installed-Edge>
node bin/millet1556-reader-regression.mjs --base-url http://127.0.0.1:4019 --output <external-evidence>/existing_reader --browser-executable <installed-Edge>
node bin/millet1556-compact-ui-qa.mjs --output <external-evidence>
```

The focused comparison requires the preserved BEFORE_DEH.html and BASELINE_I43_3.json in its external records directory, plus the baseline Git commit. It does not modify or normalise source XML or alignment data.
