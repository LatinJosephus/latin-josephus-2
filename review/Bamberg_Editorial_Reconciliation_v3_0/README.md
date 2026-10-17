# Bamberg Editorial Reconciliation v3.0

Thirteen exact exported RMP approvals are staged on `bamberg-editorial-closeout-v3-0`, based on `bf91e314e9f9999df42b793de40bbe28c549e3c1`. This is a local editorial staging branch, not a change to active v2-development. The post-commit receipt is supplied alongside this packet to avoid a self-referential commit hash.

Read `approved_decisions.md`, `qa_report.md`, `editorial_reconciliation_summary.md` and `mechanical_readiness.md`. Machine-readable authority is `staging_correction_manifest.json`; original CSV, exact source hashes, reversible operations, full master/ledger, withheld/deferred and prospective mechanical manifests are retained.

Reproduce read-only source verification with `python -B scripts/verify_integration.py --root CHECKOUT --packet PACKET`. Git must expose the immediate accepted baseline commit. The copied `preservation_guard.py` is unchanged inherited code. Exact XML diffs and full production forward/inverse patches are in `patches/`; these are evidence, not instructions to apply unapproved proposals.

Run the installed/locked Jekyll build into a fresh disposable directory, prepare generated reader publication authorities, then run the repository’s corpus acceptance script. Do not install new dependencies or change validation logic. `scripts/display_regression.cjs` uses explicit READER_TEST_ROOT, READER_BASELINE_ROOT, READER_TEST_OUTPUT, BAMBERG_BUILD_SITE, PLAYWRIGHT_MODULE and CHROME_EXECUTABLE settings. The baseline checkout must still be the accepted unmodified development state.

Image evidence remains in the immutable original cache and the preserved v2.9 review archive. `evidence/approved_question_concordance.json` and `evidence/mechanical_source_file_hashes.json` identify crop/native hashes, coordinates and source packages. Native scans and prior archives are not duplicated.

Do not apply the remaining 53 mechanical or 56 substantive proposals, submit new questions, merge, push or publish without separate authorization. The ledger is 33 completed / 67 remaining, with 20 protected final checks. Active review_decisions.csv was not accessed.
