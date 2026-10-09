# Test harness history and limits

The browser scripts are adaptations of the accepted `review/Source_TOC_Navigation_2026-10-07/` harnesses. They serve an actual dedicated Jekyll build. Readiness and state-observation hooks are injected into the renderer response in memory. No production renderer instrumentation is written. Comparison endpoints use the pinned baseline renderer; source/XML ranges are also checked independently. Initial tests use 1cf003b; the current variants use f393fa1 and the second disposable build.

Initial diagnostic failures were resolved in the harness, with no production changes:

- A collapsed settings panel prevented interactions; the harness now opens that existing panel before control tests.
- The VI locator check initially compared a scholarly text point with its distinct display-boundary point. It now honors current `traditionalRangePoint` and paragraph-edge semantics, and verifies both the resulting range and the inherited Niese behavior. The original diagnostic is retained under `development-diagnostics/BROWSER_FAILURE.json`. `alignment_repair_applied: true` in the final VI result describes the already integrated baseline repair; it is not a change in this batch.
- A DEH comparison included the test-only `baseline=1` query in rendered internal links. The final comparison removes only that parameter from cloned links; all semantic URL parameters and path content remain compared. The original snapshots and failure are preserved under `development-diagnostics/`.
- The added availability test first checked whole-page duplicate IDs, revealing the pre-existing `annotations` collision between the converted TEI standOff and interface accordion. The final result explicitly records that issue and separately checks all text-pane IDs. It does not claim whole-page ID uniqueness. Neither new book has been implemented, so this is not waived as a successful new-book certification gate.
- The added availability test first compared a citation identity to numeric 100, while the reader stores a string. It now checks the actual value as a string.
- The first current-baseline Docker attempt encountered Windows CRLF shell-script endings. The saved build scripts now use LF; the subsequent fresh canonical build succeeds.

Final PASS artifacts replace no production file and do not certify unimplemented VIII/X views. Candidate XML parsing, candidate interval reconstruction and baseline browser QA remain distinct from new-book scholarly and reader certification.
