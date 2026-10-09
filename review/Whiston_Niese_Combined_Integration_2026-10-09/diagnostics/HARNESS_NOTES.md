# Initial harness findings

1. The initial clean assertion saw the new untracked verification script itself. Initial Git status was verified clean before any writes. The corrected baseline excludes only this additive packet; all tracked hashes and both indices are compared independently.
2. Default system Python lacks lxml. Validation was rerun successfully with the bundled dependency Python; no installation or source change was made.
3. Initial Back/Forward checks waited only for viewing level, so two Niese states could be confused while rendering. INTERACTION_INITIAL_TIMING_QA.json/log preserve that attempt. Final checks require a new render revision and exact identity before comparing complete pane text.
4. The built DEH reader correctly retained the test-only baseline=1 parameter in generated comparison links. PROTECTED_TEST_QUERY_DIFFERENCE.json records the entire difference. Final differential checks compare the old/current renderer and normalize only that injected parameter in comparison links; all source state and other URL parameters remain checked.
5. The historical Alignment gate used pre-VIII/X a480215. In VIII its empty milestones differ from the approved canonical renderer's displayed Niese numerals. ALIGNMENT_PRE_VIII_X_DIFFERENCE.json and logs preserve evidence. Final complete Book/Alignment DOM checks use canonical ad3158b, the correct pre-combination authority, and pass without stripping numerals or changing production.

All final accepted results are at the packet root. Initial INTERACTION_FAILURE/DIFFERENCE artifacts at the root are test-attempt diagnostics; the final PROTECTED_INTERACTION_QA.json and INTERACTION_QA.json supersede them. No failed attempt is represented as a successful run.
