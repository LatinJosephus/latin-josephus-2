**Full DEH-side Bellum comparison — Phase 5, 2 October 2026**

Implemented in `C:\Users\Pollard_R\Git\LatinJosephus-v2-development`, on
`v2-development`. The initial HEAD was the Phase-4 freeze,
`82d36810a5bc126ad5587784579c1dfb64e8443d`. Initial status contained only the
unrelated `assets/js/renderTei.js` label edits. Another stream committed those
same bytes during QA as `b2755f88ff11b6797c6bd9cc3862f6c2490c54e5`
(“Clarify Antiquities navigation labels”). They were preserved and excluded
from the Phase-5 commit. No recovery checkout, push or deployment was used.
Phase-3/4 documentation and editorial history remain unchanged.

The authoritative file is `assets/data/deh-josephus-concordance.json`, consumed
directly by the interface. Its unchanged SHA-256 is:

```text
c8f59a9bdfd8c49350b4d2656d1c685f4c4a63bd96450ddfd218ac3c07ca743c
```

| DEH book | Reviewed numbered units | Units with BJ comparison |
| --- | ---: | ---: |
| I | 212 | 209 |
| II | 73 | 63 |
| III | 70 | 69 |
| IV | 79 | 78 |
| V | 121 | 120 |
| Total | 555 | 539 |

There are 705 published BJ components, including six supplementary components.
All 31 AJ-bearing records and 44 AJ components remain in the frozen file;
20 records contain both BJ and AJ. The publication adapter filters only BJ
targets without sorting, regrouping, merging or deduplicating them. Other-works
evidence remains untouched and has no new interface. Reverse BJ-to-DEH discovery
and AJ comparison are outside this phase.

The sixteen units without BJ targets comprise eleven AJ-only units and five
units with no BJ/AJ recorded. They have no comparison control. Requests naming
a no-BJ record retain ordinary DEH reading rather than showing an empty comparison
or borrowing another record. The three Prologue units are also excluded.

The frozen file's `publication_status` describes the Phase-4 snapshot. It was
not rewritten for this UI phase. The historical eleven-record
`assets/data/deh-bj-alignment.json` remains solely as the earlier-pilot regression
fixture used by `bin/deh-concordance.mjs`; the production interface never fetches
it. There is no second publication list or spreadsheet-derived publication data.

**Architecture and navigation**

The Jekyll book layout, CETEIcean and ordinary `renderTei.js` reader are retained.
DEH comparison remains an optional separate module listening for
`deh-view-rendered`. Shared publication validation and DOM excerpt functions now
live in `assets/js/dehParallelsCore.js`, so browser QA uses the same extractor as
the interface. Canonical XML and its existing translation `sameAs` links are
read-only; no scholarly parallels were inserted into them.

The reader adds “Compare with Bellum” immediately after each matching DEH unit.
One traversal of the rendered paragraphs uses a canonical-ID lookup, replacing
the pilot's repeated per-record scans. An actual canonical Latin paragraph must
exist before its control is added. Entry from the English pane selects Pollard;
entry from the Latin pane selects Ussani. Bellum defaults to Whiston.

The comparison navigation is Book → Chapter → Unit. Book changes select the
first eligible unit in that book; Chapter changes select the first eligible
unit in that chapter. Child menus contain only BJ-bearing entries in their
selected parent. Units use scholarly DEH citations; there is no corpus-wide flat
menu. These changes use ordinary page navigation and retain both selected sources
in the URL. Source changes within a comparison use history without changing the
record. The shared core caches selected XML and its section index within the page.

Existing `book`, `chapter`, `unit`, `parallel`, `deh-source` and `bj-source`
parameters retain their meanings. The URL identifies the DEH record, including
composites. All eleven pilot URLs now resolve from the frozen authority. Reload,
back/forward and reopening a shared URL restore the record and both sources.
Return-to-DEH restores the exact chapter-local DEH unit. Each BJ component has
its own book/Niese-start reader link, preserving the selected source. Comparison
`bj-source=niese` maps to the ordinary Bellum reader's existing `greek=current`
source key; no ordinary route or source key was renamed.

The comparison script and stylesheet have build-version URLs to prevent cached
pilot assets being combined with the full-publication HTML. The core module has
its own versioned import. Future core changes must update that import version.

**Sources and editorial display**

| Pane | Source | Description |
| --- | --- | --- |
| DEH English | Pollard v1.0 | English translation of the Latin DEH |
| DEH Latin | Ussani (1932) | Critical Latin text of DEH |
| Bellum English | Whiston | English translation of the Greek Bellum |
| Bellum Latin | Cardwell (1837) | Independent Latin translation of the Bellum |
| Bellum Greek | Niese | Greek Bellum |

English–English remains the default when no source state is supplied. All six
combinations are equally available. The introductory text identifies the Greek
Bellum as underlying the DEH adaptation. It makes no claim that Cardwell is the
source of DEH or that Whiston translates Cardwell.

The authoritative `primary_parallel` and `supplementary_parallel` roles drive
display. Each supplementary component has the explicit note “Supplementary
parallel”; the pilot's unresolved-parentheses wording is removed. Visible BJ
citations use Roman books and en dashes. Components remain distinct, including
the supplementary-first III.8.2, inline supplementary II.9.2, and all seven
V.53.1 components. VII.369 is displayed twice in V.53.1, as supplied. There is no
sentence/word alignment or claim that a parallel covers an entire DEH unit.

The approved conservative provenance is unchanged:

> Parallels transcribed from the references in Ussani/Mras. Printed references
> have not yet been independently verified. Reference order follows the edition.
> A parallel indicates corresponding material, not exact verbal equivalence,
> full-unit correspondence, or dependence between the Latin versions.

**Publication safety and extraction**

The loader checks the actual concordance bytes against the frozen SHA before
accepting the data. The adapter validates reviewed identities, unique IDs,
closed BJ coordinates, source-existence validation, roles and authoritative
target order. A selected canonical DEH target is checked again before display.
The selected XML files are SHA-checked against the frozen XML manifest. Failures
produce a visible comparison error with an ordinary-reader return link.

Bellum indexing uses only body text. Greek excerpts clone their complete Niese
paragraph. Cardwell uses confirmed paragraph-start [N] labels and internal
milestones; Whiston uses its own milestones, never inferred Cardwell `sameAs`
boundaries. Latin/English DOM Ranges clone text between consecutive anchors.
Complete consecutive source indexes and XML hash verification permit a final
section to end at the body boundary, excluding standOff/back matter. Component
indexes namespace cloned IDs, including overlapping and repeated sections.

**Completed QA**

- The frozen validator passed, including its 26 mutation self-tests.
- All 555 records loaded; the actual filtered count was 539, with 705 BJ
  components and sixteen excluded no-BJ records. Prologue was excluded.
- Every BJ component was actually extracted in Niese, Cardwell and Whiston:
  **2,115 successful checks, zero failures**. Extracted text matched an
  independent canonical text-node traversal, rather than only testing coordinate
  presence. This covered 8,193 section occurrences, preserving repetitions.
- Both DEH sources passed extraction and canonical identity checks for every
  reviewed unit: 1,110 checks. All 21 Bellum final-book boundaries passed, and
  eight publication-eligibility corruption tests were rejected.
- Browser reader audits covered all 555 units in both DEH sources: exactly
  539 correct controls per source and none for the sixteen no-BJ units or
  Prologue. Ten return/entry tests across all five books preserved the exact
  citation, pane source and Whiston default. Explicit no-BJ comparison URLs
  for I.3.1 and AJ-only II.13.7 safely showed ordinary reading.
- Twelve representative records × all six source combinations = 72 browser
  cases, plus twelve reloads. The sample included I.1.1, I.1.3, I.1.4, I.1.10,
  I.23.2, I.26.3, I.37.4, II.9.2, II.11.3, III.8.2, IV.30.2 and V.53.1.
  These cover every DEH book, single/range/multi-range/reordered targets,
  supplementary roles, cross-book composites, overlap and BJ+AJ filtering.
  Independent source changes preserved the other pane's text and component order.
- All eleven legacy pilot URLs and the English–English default passed.
  Source history in both directions, reopening a shared composite URL, and
  fifteen Book/Chapter/Unit navigation checks across the five books passed.
- All seven V.53.1 component links were opened in all three Bellum sources:
  21 actual reader links passed, with comparison text matching the ordinary
  reader at each starting coordinate, including the Book II supplement.
- Ordinary DEH book/chapter/unit navigation, English-pane toggling and Prologue
  navigation passed. Bellum book/chapter/legacy-unit/Niese navigation, history,
  Greek-pane toggling and deep-link reload passed. Antiquities I Niese and XV
  legacy paragraph routes, and Contra Apionem I reading, passed with no comparison
  UI introduced. Existing per-language source identities remained correct.
- The observed 447-pixel viewport stacked panes and wrapped hierarchy controls
  without horizontal overflow. The in-app viewport override did not change the
  measured width, so no separate 390-pixel or desktop viewport result is claimed.
  The final comparison had no browser error/warning logs.
- JavaScript syntax and Git whitespace checks passed. All 100 XML files and
  the frozen concordance were byte-identical; the unrelated renderer also
  matched the initial snapshot. Explicit staging excluded all three classes.

The repeatable full-corpus browser QA is excluded from site publication by the
existing Jekyll `bin` exclusion:

```powershell
node bin/deh-concordance.mjs validate --self-test
node bin/deh-parallels-qa.mjs
```

Open `http://127.0.0.1:4001/` and choose “Run full concordance QA”. The read-only
local server verifies the frozen JSON and all 100 XML hashes before starting;
its browser harness imports the production core. It reports each of the 2,115
component checks, errors, coverage, DEH checks and final-boundary checks.

Detailed local evidence is saved under
`C:\Users\Pollard_R\.codex\visualizations\2026\10\02\01a0fdd9-6a57-7881-b7c1-a4f8f81d93c3`:
`phase5-initial-state.json`, `phase5-frozen-validation.json`,
`phase5-corpus-qa.json`, `phase5-browser-qa.json`,
`phase5-pilot-performance.json`, `phase5-full-performance.json`,
`phase5-protection-check.json`, `phase5-build.log`, `phase5-comparison.png`,
and the staged-diff audit. These files are outside the feature commit.

**Performance and build**

The authoritative JSON is 1,554,044 bytes (about 1.48 MiB), compared with the
20,506-byte pilot fixture. Three local I.1.4 English–English ready times were
229, 172 and 172 ms, compared with pilot times 249, 147 and 206 ms. These are
same-machine local measurements with browser/server caching, not cold production
network benchmarks. No significant local ready-time increase was observed,
but the uncompressed JSON payload is substantially larger.

Each initial comparison fetched only the selected Bellum source/book. Unselected
Bellum sources/books were not fetched or parsed. Composite passages lazily load
each requested book; ordinary DEH reading adds no Bellum XML fetch. Selected XML
and Bellum indexes are reused within a page. The existing ordinary renderer still
loads its own DEH texts; no unrelated renderer optimization was attempted.

The established Jekyll build passed with only `jekyll-responsive-image` omitted.
The fully configured build remains limited by `jekyll-responsive-image` 1.6.0
requiring missing `rmagick >= 2.0, < 5.0`. No environment repair or repository
build-configuration change was made; this is not a fully configured build pass.
Existing Sass/pagination/Faraday warnings remain.

```powershell
$env:JEKYLL_NO_BUNDLER_REQUIRE = 'true'
ruby -e "require 'jekyll'; config = Jekyll.configuration({'source'=>Dir.pwd,'destination'=>File.join(Dir.pwd,'_site')}); config['plugins'].delete('jekyll-responsive-image'); Jekyll::Site.new(config).process"
```

Phase-5 files are exactly `_docs/deh-concordance-phase5.md`,
`_includes/deh-parallels.html`, `_includes/scripts/misc.html`, `_layouts/book.html`,
`assets/css/deh-parallels.css`, `assets/js/dehParallels.js`,
`assets/js/dehParallelsCore.js`, `bin/deh-parallels-browser-qa.js` and
`bin/deh-parallels-qa.mjs`. The local commit subject is
`Publish full DEH-Bellum comparison`; its hash is supplied in the completion
report and recoverable with `git log -1 --format=%H --grep='^Publish full DEH-Bellum comparison$'`.
The feature is reversible by reverting that one commit, preserving the separate
renderer-label commit.

No concordance defect or blocking publication-code issue was found. Before an
authorized push/deployment, the existing build environment limitation and actual
production transfer/compression behaviour should be accounted for. Corpus-wide
independent philological verification remains the approved scholarly caveat.
