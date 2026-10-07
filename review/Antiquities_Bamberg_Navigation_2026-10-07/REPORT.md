# Bamberg navigation implementation review — 2026-10-07

GO for human browser review and a follow-up commit. Changes are unstaged and uncommitted in `C:\workspace\LatinJosephus-antiquities-bamberg-navigation` on `antiquities-bamberg-navigation`, based on `b8d4db2938e3a61a7f75ea8fcbb06f22fc78f02d`. The canonical v2-development source checkout, HEAD and origin reference remain unchanged and its Git status is clean. No push, merge, rebase, staging, commit or Git-configuration change occurred.

## Architecture and reader behavior

Bamberg division is an independent Antiquities viewing level, backed by a new TEI-P5-valid list in the existing structure.xml registry. Its unique option values and application-state identities remain exact frozen source-record identities. Public URLs serialize their numeric source rows, for example `?book=13&bamberg=76` resolves to `B78-table1-row076`. The parser also accepts the old verbose form and zero-padded numeric inputs; the writer always emits the compact numeric form. They do not derive from manuscript numerals, Niese numbers, XPath or offsets. Previous/Next follows the registered physical source order. The existing generic per-language range/multi-span resolver is reused; only its endpoint lookup now includes both independent registries. No source-specific book/label conditional or exception table was added.

The template emits Bamberg controls only on Antiquities. Books with records enable the selector and viewing level; VI–XI disable them, with ordinary book changes falling back to Book view. Returning to a book with records restores availability. Invalid, empty or cross-book manual identities yield an explicit unavailable state and no substitute passage. Changing navigation scheme removes stale owned parameters while retaining unrelated query parameters and fragments.

All manuscript labels remain as recorded. Book I lacks II; XIII contains two literal III records (row069 and row070), distinguished by short incipits but different persistent option values. XII is labelled unnumbered, with enlarged-H evidence retained and no supplied numeral. XIV [XXVIII?], XIII XXIII and historical IIII/VIIII/XVIIII forms remain unchanged. XVIII VI → VIIII contains no synthetic VII/VIII. XV.[XII] is at certified 323 and XVI.XX at internal 368 in the num367 environment. Full evidence and confidence remain in data.

| Book | Bamberg options |
|---|---:|
| 1 | 18 |
| 2 | 3 |
| 3 | 11 |
| 4 | 5 |
| 5 | 13 |
| 6 | 0 |
| 7 | 0 |
| 8 | 0 |
| 9 | 0 |
| 10 | 0 |
| 11 | 0 |
| 12 | 1 |
| 13 | 21 |
| 14 | 27 |
| 15 | 13 |
| 16 | 20 |
| 17 | 19 |
| 18 | 19 |
| 19 | 8 |
| 20 | 20 |

Total: 198 physical identities; 172 citation-start and 26 internal-to-Niese boundaries; zero unresolved and zero unavailable language counterparts. Relationships to traditional Chapter starts remain 75 exact, 117 Bamberg-only and six shared-Niese/different-position pairs. The Niese-230 pair's frozen label is XIII, whereas the task example called it XIIII; the source reading is retained.

## Exact locators and authorized empty anchors

All 594 frozen locators passed exact projected-offset and literal-anchor checks against the actual base XML. Existing certified traditional points, paragraph/inline edges and identified anchors were reused. Fifty-three empty TEI anchors were necessary: 15 Latin, 10 Greek, 28 English, in 22 files. Stable b78-language-source-record IDs and corresp links identify their registry records. MARKERS.json records exact insertion bytes, original byte positions and per-file counts.

Removing only those documented empty anchors reproduces every prior XML byte and hash exactly. There is no paragraph splitting, text/numeral/apparatus rewrite, ID or sameAs change, node reordering, or replacement of existing markers. Paragraph counts remain Latin 1,622; Greek 1,681; English 1,600. Book XI order and Book IX/VII inputs remain byte-identical. The complete prior registry bytes are retained; Bamberg and audited-coverage lists are appended. No Bamberg counterpart required multiple spans in this batch: source order is strictly increasing for each available language, and the existing multi-span capability remains intact for the traditional system.

## Exhaustive results

| Gate | Result |
|---|---|
| Bamberg physical starts and exact complete ranges | 594/594 PASS |
| Bamberg identities / URL round-trip / source-order controls / pane switching | 198/198 PASS |
| Compact URLs: actual copy/load, browser reload, exact frozen identity and back/forward | 198/198 PASS; verbose and padded aliases normalize |
| Final division to same-book end | 14 books × 3 languages = 42 PASS |
| Shared-Niese/different-physical-position pairs | 6 pairs / 18 language checks PASS |
| Book I straddling decisions | row008, row010, row012, row013; 12 language checks PASS |
| VI–XI audited absence and ordinary fallback | All six books PASS |
| Malformed Bamberg URLs | 4/4 explicit unavailable PASS |
| Duplicate III identity / reload / history / keyboard | PASS |
| Traditional registry | 257 Chapters; 1,432 Subchapters; 1,689 rows; 1,441 positions |
| Traditional executable ranges | 5,034 PASS |
| Book IX expected unavailable states | 33 PASS |
| Traditional Chapter availability / no fabricated lower 1 | 257 PASS; nine empty-subchapter Chapters retained |
| Heading/prefix ownership | 227 PASS; VI.xii.8 and VI.xiii/1 retained |
| Book XI canonical multi-span selections | 18 language ranges PASS; interpolation and witness views retained |
| Enabled Niese I–VII | 2,456 selections / 7,368 three-pane comparisons PASS |
| Alignment units and Book witness order | 1,441 unit identities and 21 Book/Proem views unchanged |
| Book VI explicit Greek alignment bindings | Three retained; adjacent-unit and Niese 269/271 checks PASS |
| DEH | 1,239 differential ranges PASS |
| Bellum Judaicum default navigation | 1,441 differential ranges PASS |
| Contra Apionem | 693 differential ranges PASS |
| Bellum Whiston/Lodge broad range suite | 10,340 ranges including 7,444 Niese ranges PASS |
| Protected-work pane/URL/history/keyboard/theme behavior | Four configurations PASS |
| Rendered identities, unique DOM IDs, URLs | PASS |
| Bamberg controls in light/dark themes | PASS; minimum measured contrast 5.33:1 |
| Existing shared Book XI notice | Unchanged; both themes and Book-view route PASS |
| Registry TEI P5, XML and topology integrity | PASS |

Traditional independent-verification populations remain 1,672 confirmed-start, three confirmed-internal, three number-disagreement and 11 ambiguous rows; zero unresolved. No source anomaly or ambiguity was normalized. Public Niese coverage remains I–VII. Book VII's separate alignment-target defect and Book IX's lacuna policy remain untouched.

## Verification limits and provenance

Tests use installed Chrome, the actual renderer/CETEI, actual XML and the real selector template in a controlled reader fixture. CSS tests use the canonical compiled stylesheet with unchanged source palette/reader partials. No Jekyll build or generated-site write occurred. The same existing HTMLCollection.forEach compatibility adapter is supplied in baseline and current fixtures; new empty anchors are excluded only from differential markup snapshots. Exact bytes, text, IDs, sameAs and order are independently verified. Human review should exercise the complete local/public-preview build before commit.

Initial failures during test adaptation involved browser instrumentation scope, simple Liquid preprocessing, unavailable DEH Greek controls, asynchronous render timing and a newly added null state field. They are explicitly marked superseded diagnostics in TEST_DEVELOPMENT_LOG.json; final PASS records govern QA. No scholarly boundary was changed to make a test pass.

All 560 snapshotted canonical files, all nine scholarly frozen-packet files, and both historical review directories (34 and 26 files) retain their recorded hashes. A final repeat observed desktop.ini drift in the recovery packet. This non-scholarly metadata file was not written to or reverted by this task; INTEGRITY_QA.json records the exact before/after values. Thus scholarly integrity passes with that separately documented filesystem qualification.

## Modified source files

- _includes/display-settings.html
- assets/js/renderTei.js
- assets/xml/antiquities/English/book-01.xml
- assets/xml/antiquities/English/book-02.xml
- assets/xml/antiquities/English/book-03.xml
- assets/xml/antiquities/English/book-04.xml
- assets/xml/antiquities/English/book-05.xml
- assets/xml/antiquities/English/book-13.xml
- assets/xml/antiquities/English/book-14.xml
- assets/xml/antiquities/English/book-16.xml
- assets/xml/antiquities/Greek/book-01.xml
- assets/xml/antiquities/Greek/book-03.xml
- assets/xml/antiquities/Greek/book-04.xml
- assets/xml/antiquities/Greek/book-05.xml
- assets/xml/antiquities/Greek/book-13.xml
- assets/xml/antiquities/Greek/book-14.xml
- assets/xml/antiquities/Greek/book-16.xml
- assets/xml/antiquities/Latin/book-01.xml
- assets/xml/antiquities/Latin/book-03.xml
- assets/xml/antiquities/Latin/book-04.xml
- assets/xml/antiquities/Latin/book-05.xml
- assets/xml/antiquities/Latin/book-13.xml
- assets/xml/antiquities/Latin/book-14.xml
- assets/xml/antiquities/Latin/book-16.xml
- assets/xml/antiquities/structure.xml

The human-review URL refinement changes only renderTei.js in application source: generic compact serialization/parsing, with no registry, XML, label or provenance change. COMPACT_URL_CHANGE.json records this refinement's before/after hash. No stylesheet change was needed. All additional files are in this new review directory. FILE_MANIFEST.json records before/after source hashes and new review-file hashes. Both prior certification directories and recovery scholarly authorities are protected and unedited.

## Reproduction

From the implementation worktree, use the available Python runtime with lxml for verify_integrity.py and the Node runtime with installed Playwright/Chrome for these commands (prefix each script with the new review-directory path):

- `node compact-url.test.cjs`
- `node bamberg.test.cjs`
- `node navigation.test.cjs`
- `node navigation.test.cjs --followup-gate`
- `node navigation.test.cjs --alignment-all-gate`
- `node navigation.test.cjs --alignment-gate`
- `node navigation.test.cjs --multispan-gate`
- `node navigation.test.cjs --protected-source-gate`
- `node navigation.test.cjs --rendered-gate`
- `node interaction.test.cjs`
- `node notice-theme.test.cjs`
- `python -B verify_integrity.py`

prepare_registry.py and patch_renderer.py document compilation/application from the exact clean base; they are not rerunnable against an already-patched registry. BASELINE.json is the initial byte inventory. CURRENT_LOCATOR_GATE_QA.json and BAMBERG_BOUNDARY_QA.json preserve the mapping gate. QA.json is the complete final result index.
