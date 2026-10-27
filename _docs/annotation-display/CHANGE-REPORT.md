# Change report

26 October 2026. Implementation completed on `feature/manuscript-annotation-display-v3`, based on current canonical remote `v2-development` at `519d607b890f76bf48e427529c4278151a124326`.

Implementation commit: `46ec691d6bce48af0d93191e2eca7453223fb3d8`. It contains the application changes, generated mapping, tests, reports and screenshots. A documentation-only follow-up records this identifier; the final branch HEAD is also recorded in the delivery receipt.

## Result

Historical hand-key follow-up, 27 October: the editor confirmed the exact sequence through Hand 9. The shared interpreter now recognises the additional codes in annotation prefixes, keeps the bracketed `¤` folio role distinct, and separates the explicit `(³1)yo` component in Bodmer 98. All 84 observed additional prefixes resolve as Hands 5, 6 and 8. No Hand 4, 7 or 9 annotations are invented. See [the evidence and preservation report](HISTORICAL-HAND-KEY.md). The current suite has 45 annotation/citation/translation tests and five Python citation/preservation tests, all passing.

English editorial-note follow-up: the English display now translates the inspected French descriptions and inline comments through `assets/js/annotationEditorialEnglish.js`. Original notation and Latin wording remain intact. Ten additional tests bring the annotation suite to 34 passing tests; see [the translation report](ENGLISH-EDITORIAL-NOTES.md). The original implementation commit above remains the initial redesign commit; the delivery receipt records the current branch HEAD.

The bottom reader panel now displays readable verified textual citations, prominent recorded wording, manuscript designations, separate folio references and restrained hand labels. Symbolic annotations, inability to transcribe, deliberate abbreviation, missing transcription and unresolved notation have distinct presentation. Original notation and references remain in native expandable scholarly details. The legend explains the recovered key and the editor's original counting instructions.

The shared resolver and interpreter use the existing architecture without adding a site framework or dependency. They preserve the canonical scholarly sources. Whole-unit navigation is bidirectional, original highlights remain available, and deterministic presentation anchors are independent from display numbers.

## Application and tooling files

| File | Purpose |
|---|---|
| `assets/js/manuscriptAnnotations.js` | Shared citation resolver, source-specific interpreter, manuscript registry, English/French labels and apparatus rendering |
| `assets/js/annotationEditorialEnglish.js` | Explicit English translations of inspected French editorial descriptions and inline comments |
| `assets/js/renderTei.js` | Reader integration, exact association matching, lazy lookup loading, navigation and preserved highlight controls |
| `assets/data/alignment-citations.json` | Generated citation lookup with input hashes and work-specific provenance |
| `_includes/annotations-bar.html` | Reader-facing heading and accessible panel control |
| `_includes/scripts/misc.html` | Load the shared component before the reader |
| `_sass/_manuscript-annotations.scss` | Compact, responsive, theme-aware apparatus and focus styling |
| `assets/css/main.scss` | Import apparatus styles |
| `bin/build-annotation-citations.py` | Non-destructive deterministic mapping and source inventory generation |
| `bin/annotations/annotation-qa.test.cjs` | Source-grounded resolver, interpreter and display tests |
| `bin/annotations/editorial-english.test.cjs` | Exact translation coverage and preservation of Latin/original French across the corpus |
| `bin/annotations/test_citation_generation.py` | Independent citation fixtures and protected-source comparisons |
| `bin/annotations/browser-qa.cjs` | Generated-site baseline comparisons, exhaustive reading preservation, navigation and screenshots |
| `bin/annotations/ui-smoke.cjs` | Search/saved-link, sparse-record and DEH comparison UI checks |
| `bin/annotations/qa.cjs` | Repeatable source and integrity test runner |
| `bin/annotations/report-qa.cjs` | Reproducible interpretation counts and explicit exception register |

Generated review material is `_docs/annotation-source-inventory.json` and `_docs/annotation-display/`, including the reconnaissance report, notation inventory, citation provenance, DEH assessment, QA reports, logs and before/after images. The source inventory is evidence for tests; it is not loaded by the public reader.

## Verification and limitations

The original redesign passed 594 Node/Python tests: 24 annotation tests, five Python tests and all 565 existing search tests. The English-editorial follow-up adds ten passing tests and reruns all 34 annotation tests, five preservation tests, corpus/DEH/search guards and actual-reader checks. Source and publication guards, 13 baseline/final reader comparisons, all 27 annotated-corpus books, navigation/keyboard checks, saved search links and DEH comparison loading pass. See [QA-REPORT.md](QA-REPORT.md) for exact scope, evidence and the local image-plugin build limitation.

All 2,958 reading records remain present. Verified citations cover 2,937; the other 21 retain their original defective/missing associations and are documented. The original key plus the confirmed historical hand sequence do not explain every source pattern. No unknown code, hand, manuscript identity, ellipsis role or missing passage is invented. No omitted words are supplied.

No canonical XML, original transcription, source siglum, association, Niese boundary, corpus concordance, DEH annotation or parallel, production hosting setting, DNS or CNAME has changed. No merge, push, preview publication or deployment was performed. The branch is ready for review; editorial source corrections and any later publication require separate authorization.
