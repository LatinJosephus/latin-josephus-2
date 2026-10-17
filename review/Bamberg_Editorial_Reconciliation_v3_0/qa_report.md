# v3.0 editorial staging QA

**PASS.** Exactly thirteen newly human-approved actions (eleven historically substantive and two historically mechanical) affect nine Latin books: I, II, V, VI, VII, VIII, XI, XIX and XX. The accepted 91-action canonical baseline is unchanged; the isolated branch contains 104 cumulative actions at 103 application units.

| Mandatory verification | Result |
|---|---|
| Export, stable IDs, original readings, comments, sampling and image associations | 13 distinct valid explicit approvals; exact CSV hash and all original fields retained |
| Source compatibility and authorization | Exact frozen readings; only the thirteen approved source spans changed |
| XML / Niese / identifiers / cross-references / divisions | Every ordered element, attribute and structural position preserved; XML parses |
| Layout / protected editorial content / Book XI exceptional structure | Raw marker bytes and protected subtree text identical; physical order, fragments and both Bellum interpolations unchanged |
| Whole-token overlap guard | All thirteen edits clear; original guard reused without logic changes |
| Individual and combined reversal | Exact byte recovery to immediate accepted baseline for all nine XML and two registration files; separate canonical CRLF inverse retained |
| Previous corrections | All 91 prior registered effects remain exact; no overlap |
| Unapproved proposals | All remaining 109 minimal source spans preserved: 53 mechanical and 56 substantive |
| Corpus acceptance | 166 production XML parse; manifest seal valid; 38 frozen publication authorities and 30 negative/publication checks pass |
| Integrity safeguards | Only nine affected file records gain genuine new hashes, including both existing Book II EOL representations; only the literal seal changes in the guard |
| Historical safety regressions | 30 original frozen-fixture checks plus 23 inherited mechanical safety tests pass; historical fixtures unchanged |
| Fresh build | Installed, version-pinned Jekyll build passes; no dependency installation; known Sass/Faraday warnings only |
| Real reader comparisons | 143 pass: 13 changed loci, 26 neighbors, 9 whole books, 90 prior-correction views, 2 retained controls and 3 direct full-book entries |
| Other tracked sources | All 6,482 other original tracked files byte-identical to Git parent; all 6,493 active-development hashes and 22 prior archives unchanged; Greek, English, DEH and renderer sources unchanged |

Book II’s active canonical bytes use CRLF, while the clean isolated checkout and Git blob use LF. Exact old hashes and an explicit byte-offset mapping establish equivalence; both genuine resulting hashes are registered. Textual and structural comparisons are never fuzzily relocated. Inverse verification separately restores the frozen actual canonical representation and the immediate Git representation.

The initial reader navigation diagnostic for R22-03 used its inherited question label XIX.126. The XML paragraph is latin-book19-num127; the test correctly navigates XIX.127 without changing the approved patch, historical label or segmentation. The diagnostic remains in external runtime evidence, and the complete final suite passes. The known I.34 reference-mark issue remains OPEN and is not repaired.

The earlier VI.219 replacement diagnosis stays withdrawn. The final amended insertion is the exact RMP-approved action. No class-wide substantive approval is inferred. No new HTR, manuscript check, active decision-file access, merge, push or publication occurs.
