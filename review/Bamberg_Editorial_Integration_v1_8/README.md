# Bamberg editorial integration v1.8

Local staging of the nineteen individually human-approved correction effects at eighteen loci in nine Latin XML files. Source: `ef55e7ebd6e86d886341e8fbca8403d32dfc00ac`. Development baseline: `f13613e2e5cfc857a15b61201711211be6506279`. Branch: `bamberg-editorial-staging-v1-8`.

All eleven production files were replayed by Git and remain byte-identical to the approved v1.7 commit. The eleven files comprise nine XML files and the two authorized integrity registrations. There are no additional corrections. No merge, push, publication or active-development modification is authorized or performed.

## Audit provenance and hygiene

The source commit remains unchanged. Its 51 audit files total 1,242,440 bytes and contain no native images; 21 contain workstation/temporary paths. They remain available unchanged as Git objects and in the original v1.7 worktree and archives. This packet is a derived portable record, with original Git paths, hashes, IDs and signed-row hashes. It is not a replacement signed editorial form. Use `git show ef55e7ebd6e86d886341e8fbca8403d32dfc00ac:review/Bamberg_Editorial_Integration_v1_7/approved_correction_manifest.json` to recover the authoritative original manifest. The source Git objects must remain available for full authorization reproduction.

`source_commit_inventory_and_hygiene.json` inventories all 62 source files and affected line numbers without redistributing private values. `approved_correction_manifest.json` records 19 effects and 18 byte-exact composed application units. `approved_production.diff` covers exactly the eleven production files. The complete staged file inventory is in the external final commit receipt; all packet file hashes are in `FILE_MANIFEST.json`.

## Reproduction

From this worktree, run `python -B review/Bamberg_Editorial_Integration_v1_8/verify_staging.py --root .`. It reads the signed historical forms directly from immutable source Git objects, verifies every approved correction and its inverse, the integrity seal and all unchanged existing files, and checks remaining proposals without applying them.

Run `node bin/reader-corpus-qa.mjs --root .`. Build with the existing locked Ruby environment using `bundle check` and `bundle exec jekyll build --destination BUILD_SITE --disable-disk-cache`. Use a short, disposable output path on Windows. Run `node bin/prepare-reader-publication.mjs --site BUILD_SITE`, then `node bin/reader-corpus-qa.mjs --root . --site BUILD_SITE`. The publication preparation operates on generated files only.

The portable `display_regression.cjs` reuses the existing reader harness. Set `BAMBERG_BUILD_SITE`, `READER_TEST_OUTPUT`, `READER_BASELINE_ROOT`, `PLAYWRIGHT_MODULE` and `CHROME_EXECUTABLE` to local runtime locations, then run it with Node. The baseline checkout must be clean at the recorded development HEAD. Only test paths are adapted; renderer and selection logic are unchanged. Installed runtimes are reused; no dependencies, paid recognition or external services were purchased.

Historical preservation suites were rerun unchanged from the preserved v1.6 XVII and XVIII packages, fifteen tests each. They test prior frozen fixtures; current staging XML also underwent its own source-bound structural and inverse checks.

## Handoff

Read `qa_report.md`, `QA_summary.json` and `compatibility_report.md`. Check the final external commit receipt before resuming; do not repeat the replay. All 57 ready mechanical proposals await separate authorization, 15 further cases remain held and all 17 substantive proposals remain withheld. Preserve original source objects and archives. Stop at this local staging commit.
