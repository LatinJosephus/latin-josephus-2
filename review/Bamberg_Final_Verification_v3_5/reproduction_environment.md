# Acceptance reproduction environment

Python 3 with the existing standard-library XML and checksum verifier; Node with the project's existing Playwright installation; installed Chrome; Ruby 3.3 with the already pinned project Gemfile and lock. No dependency or paid service was added.

The fresh build used the worktree Gemfile and the prior locked dependency set in an external build environment. Commands, from the isolated worktree:

```text
bundle check
bundle exec jekyll build --destination EXTERNAL_TEMPORARY_SITE --disable-disk-cache
node bin/prepare-reader-publication.mjs --site EXTERNAL_TEMPORARY_SITE
node bin/reader-corpus-qa.mjs --root ISOLATED_WORKTREE --site EXTERNAL_TEMPORARY_SITE
```

The preparation command operates only on the disposable built site; it does not publish. The historical lock's dependency versions and bundler version stayed exact; generated checksum metadata was permitted only in that external copy. The existing Sass/Ruby dependency deprecation warnings did not fail the build and were not repaired here.

For the unchanged real reader regression harness set `READER_TEST_ROOT` to the isolated worktree, `READER_TEST_OUTPUT` to a new external results directory, `READER_BASELINE_ROOT` to a frozen copy of v3.4 assets/xml, assets/js and assets/css, `BAMBERG_BUILD_SITE` to the fresh site, `PLAYWRIGHT_MODULE` to the installed Playwright module and `CHROME_EXECUTABLE` to installed Chrome; run `node scripts/reader_final.cjs`. The harness asserts exact authorized Latin differences, unchanged Greek/English and explicit Book XI physical/interpolation identities. No production source is patched for testing.

Historical XVII and XVIII preservation tests use the v2.1 original frozen public-assets fixture and its checksum manifest, through the existing frozen-fixture adapter. They do not target the now intentionally corrected candidate. The inherited v1.9 and v2.0 safety regressions run unchanged. Portable result copies and path-redacted derived logs are provided in qa/; original full logs remain outside the compact commit in the recovery workspace.
