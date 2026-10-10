# Reproducing the local Book XX certification

Use the isolated branch and its dedicated runtime. The actual production source tested here is `2c1d9ab8e2e90270527945b83ca90da8827b72b0`, on the immutable `65b3256fe202a06e33a59aa2d1dcbd7107358271` baseline. Later branch commits contain QA and certification evidence only. The final production manifest checks that the source commit, working files, archived build source and built site share the same production bytes.

Run the following from `review/Antiquities_Niese_BookXX_2026-10-10` with the installed bundled Python/Node runtime. Each browser command starts its own local server on8920 and closes it and its isolated Chrome context afterward. Run browser commands sequentially; keep other WorkBots' ports and profiles untouched.

```text
python coverage_gate.py
python verify_bytes.py
node protected_browser.cjs final
node bookxx_browser.cjs
node combined_cases_browser.cjs
node protected_controls_browser.cjs final
node notice_visual_browser.cjs
node closure_browser.cjs
node prove_range_end.cjs final
```

The immutable baseline site and original baseline receipts are retained in the dedicated runtime and review packet. `protected_browser.cjs final` discovers the expected prior population from the actual recorded baseline menu; it does not substitute a presumed list. Its 135 Book XX containing views are compared with full-text hashes from the original built reader. The 20 legacy extents are compared as complete texts. `protected_controls_browser.cjs final` also replays all20 chapter URLs and the precisely recorded inherited Book-I exceptions.

`bookxx_browser.cjs` compares all268 complete Greek/Latin intervals and Whiston contexts against the independently reviewed raw-source ledger, including unavailable notices and exact citation labels. `combined_cases_browser.cjs` checks all four approved groups against independently prepared frozen-source combined expectations. The UI has an individual Niese selector; combined tests use the actual exact-view function and native DOM ranges over its loaded source. English context is compared per identity without inventing exact English cuts.

The primary scans, title/page evidence and exhaustive scholarly audit remain separate from these executable gates. `COMPLETE_PRINT_AUDIT.json` and `IDENTITIES.json` document the 268 individual source reviews. The initial rendering flag in `PRINT_EVIDENCE_MANIFEST.json` is historical; its explicit final-review reference identifies the complete Book XX audit. Rendered but unused Vita pages336–341 do not contribute to certification.

`build_candidate.py` archives the current isolated branch HEAD into a fresh commit-named runtime directory and runs the established disposable Jekyll builder. It never overwrites an existing runtime, alters canonical or publishes. The recorded actual build source/site paths and full build log are in `CANDIDATE_BUILD.json`; a source-copy of the final build log is retained under `evidence`. Browser observation hooks expose existing reader functions and state without changing selection boundaries or source files.

Do not rerun `record_approvals.py` against already approved history. `prepare_accepted_patch.py` is approval-gated and reverses only the recorded insertions against the frozen source before generating the approved map; `coverage_gate.py` and `verify_bytes.py` independently verify the result. The final certificate generator requires all decisions closed, all executed gates passed and identical tested production bytes. The historical HOLD report, certificate, decisions and QA remain under `history/EDITORIAL_HOLD_402ddb34b141` and in prior commits.

Coordinated integration is a separate authorized task. Reconcile the two narrow shared-reader changes with then-current canonical; preserve later XI and XVI–XIX work and rerun its combined suites. Do not replace canonical's renderer with this branch snapshot.
