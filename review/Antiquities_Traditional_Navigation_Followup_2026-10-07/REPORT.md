# Antiquities traditional navigation: human browser follow-up, 2026-10-07

The patch fixes the three original findings and the subsequent dark-mode notice contrast issue in the isolated `antiquities-traditional-navigation` worktree. It is ready for human browser review and a single follow-up commit. No commit, staging, push, merge, rebase or Git configuration change was performed.

Base: `3d6097a0de8af11d862d5a144d6c7ad16d6e9151`. Both canonical `v2-development` and the implementation branch were clean at this exact commit before the patch. Canonical remains clean at the same commit; this task wrote only in the implementation worktree. The October 6 certification directory remains unchanged (34 original files verified by SHA-256).

## Invalid blank Subchapter state

The previous Chapter-change and viewing-level handlers selected the first registered Subchapter, or `null`, while retaining Subchapter mode even when the registry returned no rows. The viewing-level radio also remained enabled.

The generic availability helper now returns to Chapter view when no Subchapter exists, clears the Subchapter state and its URL parameter, and disables the Subchapter selector and viewing-level radio for that selected Chapter. Choosing a Chapter with registered Subchapters restores availability automatically. Clearing a Proem Subchapter returns to Book view, since Proem has no invented Chapter.

All 257 Chapters were tested through the actual Chapter-change event listener, starting in a valid Subchapter view and then returning to a Chapter with Subchapters. The nine zero-Subchapter Chapters are I.v, I.ix, I.xiv, I.xv, I.xvii, I.xxii, III.iii, III.xiii and VIII.ix. The registry has **zero** selectable Subchapters in each of these nine; none has later registered lower divisions. Only actual registry labels are offered throughout the corpus. Niese-only lower-1 observations remain witness evidence and do not create Loeb Subchapter rows. Explicit invalid manual URLs still display unavailable messages and round-trip without substituting nearby text.

## Structural prefixes at exclusive range ends

VI.xii.8 previously ended immediately before Latin Niese milestone 271 inside `latin-book06-num272`; the earlier `[XIII.i]` numeral therefore remained in XII.8. The English endpoint was the opening of `english-book06-num272`, after the separate unidentified Chapter 13 heading paragraph. A citation/text start does not own the entire structural display prefix.

The registry now records an optional `boundary-start` feature separately from the unchanged citation/text locator. The generic range resolver uses that display boundary for both inclusive starts and exclusive ends. For VI.xiii / VI.xiii.1:

| Language | Retained citation/text locator | Inclusive structural display boundary |
|---|---|---|
| Latin | `latin-book06-num272`, `milestone[1]`, Niese 271 | Start of `latin-book06-num272`, including `[XIII.i]` |
| English | Start of `english-book06-num272` | Before `p[1]` in `english-book06-chapter13`, including its Chapter 13 heading |
| Greek | Start of `greek-book06-num271` | Unchanged |

Latin VI.xii.8 also includes its own `[XII.viii]` prefix at the start of `latin-book06-num271`, while its true citation 269 locator remains unchanged. The English XV.viii.4 inline endpoint now includes its own `[284]` numeral before the existing empty anchor; the preceding selection excludes it. This provides a complex-inline regression in addition to the heading-before-paragraph cases.

The current XML inspection registered **119 distinct prefix locations**: 116 explicit English chapter-heading paragraphs, two Latin contiguous numeral prefixes and one English internal numeral prefix. Coincident Chapter/Subchapter identities reuse the same prefix point; 227 language-specific locator features were added (224 English, 3 Latin). Stable wrapper/paragraph IDs and direct child edges suffice: **no new XML anchors were required**. No application code recognizes a particular book, chapter, numeral or anomaly. Heading ownership was recorded as current-text presentation data; no source judgment, status, citation coordinate or structural identity was reopened.

Focused browser checks verify that VI.xii.8 starts with the Abiathar passage in all three panes and excludes `[XIII.i]` / `CHAPTER 13`; VI.xiii and VI.xiii.1 retain their own heading/label and contain no preceding Abiathar tail. The complete range suite checks exact projected membership including display prefixes, independently checks the original text locator, and checks the **actual rendered first narrative content** after its registered prefix.

## Shared Book XI explanation

A single shared notice appears immediately before the pane container when the selected registry identity carries `reader-note`. It is outside Latin, English and Greek panes, and contains no numbered fragment diagnostics. Its wording is:

> Bamberg 78 preserves this passage in an unusual order. Levenson and Martin show that, in this part of Book XI, its manuscript family transposes sections 311–347 and also inserts material from Jewish War 4.105. Chapter and Subchapter views therefore gather the corresponding passages and display them in the order used by Niese and Loeb. Choose Book view to see Bamberg’s manuscript order.

The notice's Book-view link preserves the Book, unrelated query parameters and fragment while removing the structure/unit/citation selection. Fragment labels and the original technical presentation notes remain recoverable in registry/review data. Four affected identities carry the shared prose: XI.viii, XI.viii.2, XI.viii.4 and XI.viii.6. The renderer uses that metadata generically; it has no new Book-XI branch. The scholarship and attribution are the human-supplied Levenson–Martin (2016), p. 330 finding already accepted in the implementation record; no publication or source image was reinterpreted.

XI.viii.4 and XI.viii.6 each show exactly one shared notice, with a working Book-view link. The 18 Book-XI fragment range checks, two generic multi-span citation checks, partition checks and interpolation tests pass. Existing span membership is unchanged. Book and Alignment-unit presentation retains the physical witness order; Latin Jewish War 4.105 insertions remain in their source fragments.

## Final human-review style correction

The notice's inherited dark-mode prose was light while its framework `alert-secondary` background stayed pale lavender. A new block in `_sass/_reader-ui.scss`, scoped exclusively to `#traditional-reader-notice`, now uses the existing `--lj-brand-surface`, `--lj-brand-ink`, `--lj-brand-rule` and `--lj-brand-accent` variables. Dark mode therefore uses the reader's neutral dark surface and light ink; light mode uses its light surface and dark ink. No new hard-coded application colours were introduced.

The Book-view link is underlined in both themes, retains the theme accent on hover/focus, and receives a two-pixel visible keyboard focus outline. The notice wording, placement, renderer, registry, XML and all structural selections are unchanged by this final styling step. Other alerts/notices are not selected by the new rules.

Installed Chrome tests of XI.viii.4 and XI.viii.6 pass in both themes:

| Theme | Prose/background contrast | Book-view link/background contrast |
|---|---|---|
| Light | 11.65:1 | 5.19:1 |
| Dark | 11.85:1 | 6.04:1 |

All exceed the WCAG AA 4.5:1 threshold for normal text. Hover and keyboard-focus link contrast, underline, focus outline, the working Book-view route and the unrelated-alert control also pass. Screenshots `NOTICE_THEME_light.png` and `NOTICE_THEME_dark.png` were visually inspected and are clearly legible. `NOTICE_THEME_QA.json` records computed colours and measurements.

The browser used the existing canonical compiled main stylesheet, the actual unchanged branding palette, the current reader partial (ordinary CSS), and a representative lavender alert rule reproducing the reported conflict. This performed no site build or generated-file write. Existing comprehensive structural/navigation regressions remain valid because renderer and registry SHA-256 values are unchanged from the preceding follow-up certification; this step retested the affected theme rendering and links.

## QA results

| Check | Result / coverage |
|---|---|
| Registry counts | 257 Chapters; 1,432 Subchapters; 1,689 rows; 1,441 physical identities |
| Original verification statuses | 1,672 exact-start; 3 internal; 3 number-disagreement; 11 ambiguous; 0 unresolved; unchanged |
| Chapter availability and restore | 257/257 PASS; nine zero-Subchapter cases; no fabricated lower 1 |
| Prefix ownership | 227/227 language/level-specific locators PASS; 119 unique prefix locations |
| Full executable traditional ranges | 5,034/5,034 PASS (1,678 per language) |
| Expected Book IX unavailable ranges | 33/33 PASS: 27 missing-start displays plus 6 adjacent missing-end displays |
| Niese I–VII | 2,456 selections / 7,368 language DOM comparisons PASS |
| All Antiquities Alignment units | 1,441 selections / 4,323 language DOM comparisons PASS |
| Book/Proem witness views | 21 views, all language DOMs/order match the base |
| DEH | 1,239 full menu-defined ranges match base |
| Bellum default sources | 1,441 full menu-defined ranges match base |
| Contra Apionem | 693 full menu-defined ranges match base |
| Bellum both English sources, all levels | 10,340 ranges including 7,444 citation selections match base (overlaps the default-source suite) |
| Required rendered anomaly cases | 18 cases PASS; pane toggles preserve identity/URL; no duplicate DOM IDs |
| URL/history | Reload, back/forward, Book switching, scheme transitions, Proem, `num276b`, unrelated parameters and fragments PASS; four valid/invalid manual round-trips PASS |
| Book XI | 18 range checks; two generic citation fragment checks; two shared-notice cases; witness order and interpolations retained |
| TEI registry | Official TEI P5 4.12 Relax NG validation PASS |
| Corpus integrity | All 63 Antiquities text XML files byte-identical; no node, text, ID or sameAs change |
| Topology | Latin 1,622 / Greek 1,681 / English 1,600 paragraphs; 1,442 identified paragraphs per layer |
| Historical/frozen protection | October 6 certification unchanged; both frozen manifests verify (8 + 237 entries) |
| Diff validation | No whitespace errors; only three intended existing files changed |

The browser harness serves the actual renderer, CETEI, text XML, stylesheet and display-settings include in isolated installed Chrome contexts. It does not build the site or claim to replace human review of a complete local build. The legacy HTMLCollection compatibility adapter is applied identically to certified-base and patched differential runs, as documented in the October 6 certification. Registry counts, raw evidence, original locators and all fragment membership are independently compared with the certified base, after excluding only the new presentation fields.

## Files and protection

Existing files changed:

- `assets/js/renderTei.js`: registry-driven availability, display-boundary resolver and shared metadata notice.
- `assets/xml/antiquities/structure.xml`: explicit prefix locators and shared reader prose.
- `_sass/_reader-ui.scss`: theme-aware styles scoped only to the shared traditional-navigation notice.

New files are confined to `review/Antiquities_Traditional_Navigation_Followup_2026-10-07/`. `FILE_MANIFEST.json` records before/after hashes for the three existing files and hashes every supplemental artifact except itself. The original certification packet is not reused as a write destination. Application templates, all other stylesheets, layout, configuration, generated site, CETEI, all corpus XML and all other-work files remain unchanged.

The separate Book VII alignment-target defect remains untouched; Book IX availability and lacuna handling are retained; public Niese navigation remains limited to its certified I–VII scope; Bamberg chapter navigation is not added. No stable ID, sameAs target, source numeral or scholarly structural identity changed. The original freeze packets remain immutable.

**GO for human browser review and one follow-up commit.** Leave these changes unstaged and uncommitted until that review. No push or canonical fast-forward is performed by this task.
