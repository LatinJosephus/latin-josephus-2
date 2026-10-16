# Bamberg mechanical editorial integration v1.9

This is a new local mechanical tranche, based on accepted v1.8 commit `8f841d527780a3d23c73f7aa220f718c57239dda`, on branch `bamberg-mechanical-integration-v1-9`.

All 57 members of the previously ready set passed per-locus revalidation and were applied: IX 4, XII 3, XIII 3, XVI 5, XVII 36 and XVIII 6. Every edit changes only layout separators. Six XML files and the two established integrity-registration files change. The validation code differs only in its literal manifest seal; coverage, rules, renderer, Greek, translations and DEH are untouched.

All 144 original crops and corresponding native images were checked by SHA-256. Crop coordinates were independently reconstructed from the verified natives; maximum measured mean pixel error was below two intensity levels, consistent with JPEG recompression, with exact geometry. All 72 investigated loci have exact terminal/initial fragment pairs in the original T-PEN line indexes. Fresh context-exposed visual readings are recorded; no blind or unrelated-model corroboration is claimed and no substantive reading is authorized by those readings.

The fifteen held Book XIII cases were investigated separately. They are all verified mechanical missing separators, but none was applied. The separate report explains the old default-note contradiction and records evidence at every locus. All seventeen unapproved substantive proposals and original editorial registers are preserved byte-for-byte. The nineteen earlier approved edit effects remain protected and separately identified.

`mechanical_integration_manifest.json` freezes the selected 57 source-bound patches and eligibility checks. `exact_reversible_changes.json` records exact operations for all eight production files. `evidence_inventory.json` retains image IDs, source and crop hashes, exact coordinates, T-PEN traces and fresh readings. The nineteen rescaled contact sheets are supplied in the external delivery package, rather than added to Git as an image cache. Original native images remain in their existing locations.

For read-only reproduction from this worktree, run `python -B review/Bamberg_Editorial_Integration_v1_9/verify_mechanical.py --root .`, `python -B review/Bamberg_Editorial_Integration_v1_9/test_mechanical.py`, and `python -B review/Bamberg_Editorial_Integration_v1_9/reproduce_tranche.py --root .`. The last command reconstructs the eight outputs in memory; an explicit `--output-dir` can write separate disposable copies without changing source files.

Run the existing corpus guard using `node bin/reader-corpus-qa.mjs --root .`. Use the installed locked Ruby environment for `bundle check` and `bundle exec jekyll build --destination BUILD_SITE --disable-disk-cache`. Keep the destination short on Windows. Then run `node bin/prepare-reader-publication.mjs --site BUILD_SITE` and `node bin/reader-corpus-qa.mjs --root . --site BUILD_SITE`. Publication preparation affects generated files only.

The browser regression reuses the existing real reader harness. Set `BAMBERG_BUILD_SITE`, `READER_TEST_OUTPUT`, `READER_BASELINE_ROOT`, `PLAYWRIGHT_MODULE` and `CHROME_EXECUTABLE`, with the baseline pointing to the accepted, clean v1.8 worktree, and run `display_regression.cjs` with Node. It checks all new loci, six book views, fifteen unapplied held cases, eighteen prior-approved loci, two retained readings and six direct-entry book views.

Human budget: 20 completed, zero pending, 80 remaining including the protected final reserve of 20. This phase used no human manuscript checks. No other book was audited and no mechanical case was promoted by analogy with a human decision.

Stop after the new local v1.9 commit and the separate fifteen-case investigation. No merge, push, publication or active-development modification is authorized. Final commit identity, full changed-file inventory and recovery checkpoint are in the external delivery receipt, avoiding a self-referential commit hash in the frozen packet.
