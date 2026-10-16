# Bamberg editorial integration v2.0

Fifteen exact, authorized, one-byte word separators in Book XIII form the third local integration tranche. The immediate parent and reversal baseline is `865bc6e228c27ba9859d030e50d50f79eb6f222a` (v1.9). The original development baseline is separately recorded as `f13613e2e5cfc857a15b61201711211be6506279`.

The cumulative register reconciles 19 human-approved actions, 57 prior mechanical actions and 15 new mechanical actions: **91 distinct action IDs at 90 application units**. The compound XII.80 application unit covers two individually registered approved actions. All prior 76 actions remain protected, separately classified and source-bound; no settled human decision is reconsidered. The seventeen unapproved substantive proposals remain excluded, with updated byte-location/source-hash bindings only in a new derivative register.

`fifteen_applied_manifest.json` is the exclusive authorization list and exact primitive insertion register. It contains fifteen `old=""`, `new=" "` operations with exact source hashes, source offsets, marker bytes, flanking words, image/crop identifiers and T-PEN evidence. All input checks passed before application. `historical_logging_erratum.md` explains the contradictory default note without rewriting originals; it also corrects the derived XIII.247 T-PEN association to 3081/3085. Source scripts/logs remain untouched and hash-verified.

Only Book XIII XML and its existing integrity registration change. The guard module changes only its literal manifest seal, with no altered rules, coverage, behavior or renderer code. Exact forward/reverse Git diffs and machine-readable inverse operations distinguish immediate v1.9 restoration from the original development baseline.

Reproduction from a checkout containing the inherited v1.9 helper and source Git objects:

1. `python -B review/Bamberg_Editorial_Integration_v2_0/verify_v2.py --root .`
2. `python -B review/Bamberg_Editorial_Integration_v2_0/test_v2.py`
3. `python -B review/Bamberg_Editorial_Integration_v2_0/reproduce_files.py --root .` (in-memory reproduction; optional explicit `--output-dir` writes separate disposable copies only).
4. `node bin/reader-corpus-qa.mjs --root .`
5. Use the established installed/locked Ruby runtime for `bundle check` and `bundle exec jekyll build --destination BUILD_SITE --disable-disk-cache`. Use a short temporary path on Windows. Run `node bin/prepare-reader-publication.mjs --site BUILD_SITE`, then `node bin/reader-corpus-qa.mjs --root . --site BUILD_SITE`.
6. Set `BAMBERG_BUILD_SITE`, `READER_TEST_OUTPUT`, `READER_BASELINE_ROOT` (a clean v1.9 checkout), `PLAYWRIGHT_MODULE` and `CHROME_EXECUTABLE`; run `display_regression.cjs` with Node. The unchanged real-reader harness checks all fifteen targets, thirty neighbours, seventy-five previous correction loci, nine whole-book views, two retained readings and direct Book XIII entry.

The four compact manuscript contact sheets are in the external evidence archive. Native images remain in their existing immutable locations and are referenced by institutional identifiers, SHA-256 and source-pixel coordinates. No paid service, HTR training, new layout work, image archive or temporary runtime material is introduced into Git.

Human budget remains 20 completed, 80 remaining, including a protected final reserve of 20. No human question is submitted. Read the post-commit external receipt and development-readiness report before any future operation. Do not repeat the applied fifteen insertions. No merge, rebase, push, publication, other book or unapproved substantive correction is authorized.
