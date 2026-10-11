# Reproducing this local certification

Use a new isolated runtime/profile/destination for replay. Do not overwrite the frozen runtime or protected worktrees. Scripts here retain documented local paths; adapt only copied QA scripts. The baseline is canonical 705aebf; implementation is the commit in REGRESSION_CERTIFICATE.json. Review files are excluded from the native build.

Build baseline and candidate with `ruby build.rb SOURCE DESTINATION local.yml`, disabled disk cache, and write BUILD_CONTEXT.json with both destinations. Set PLAYWRIGHT_MODULE to the installed library, REPAIR_RUNTIME to the new runtime and REPAIR_ROOT to the candidate checkout. Run `node all-niese.cjs baseline` and `node all-niese.cjs candidate-final`, followed by compare.py using START_RECEIPT.json/new snapshots where applicable.

Run `node VII1-7-source-display.cjs baseline` and `node VII1-7-source-display.cjs candidate-final` for independent Greek/XML and positive full English assertions. Positive VII.1 test arguments are an absolute built-site path followed by a report mode: `node VII1-context-regression.test.cjs ABSOLUTE_SITE candidate-final`.

Run `node reader-structure-crosswork.cjs --final`. After its READER_FINAL_PRIOR_RESULTS.json export exists, run containing-real.cjs. Run targeted-ui.cjs, VII2-6-navigation.cjs, context-guards.cjs and combined-context.test.cjs. The combined test calls the actual production context renderer through getter-only hooks; no public combined-range syntax exists. Both requested ranges, repeated IDs and separate neighbouring paragraphs are asserted.

Run baseline-exceptions.cjs for independent inherited-defect comparison, and reload-race-comparison.cjs for the separate immediate-reload diagnostic. Source-integrity.py compares every protected tracked file with the start snapshot and verifies sole built-asset change, no XML edits and production-to-built byte equality. Raw complete registers, build logs and START_RECEIPT.json remain in the named runtime; review exports are concise durable evidence. The final external receipt records the certificate commit and clean states.
