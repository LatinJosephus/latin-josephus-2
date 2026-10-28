# Manuscript annotation search

27 October 2026 · feature/search-manuscript-annotations-20261027

The existing Search page now offers **Search in → Manuscript annotations** alongside Main texts. Annotation results support the existing Boolean grammar, quoted phrases, wildcards and optional Latin u/v and i/j equivalence. Filters select a work, book, manuscript and annotation category. An empty query browses all notes matching the filters, including entries without transcribed words. Saved search links retain the completed query and filters; CSV downloads contain every matching note, including results beyond the displayed page.

## Coverage and evidence

The generated index contains **8,122 displayed annotations**: 3,247 Antiquities, 2,958 Bellum and 1,917 De excidio. These are the reader's interpreted annotation parts, rather than counts of XML reading containers. Folio-only markers create no searchable annotation. The three approved Bodmer worksheet supplements and all separately identified DEH source rows remain present. Supplements follow their original alignment group, matching reader order.

`bin/search/build-annotations.mjs` reuses the shared reader interpreter, manuscript registry, reviewed readings, English editorial translations and verified citation lookup. Its inputs include the existing annotation inventory, unchanged canonical XML and citation authorities, the approved DEH A–E projection and original source-file fingerprint. It does not interpret ignored DEH columns or apply Josephus notation rules to DEH. The original notation and source references remain attached to each result and CSV row.

The index searches the reader's displayed recorded wording and English editorial descriptions. Provisional and reviewed readings match the current reader display. Neutral gap explanations, category labels and manuscript metadata do not contribute words to the text query; manuscript and category are separate filters. Each annotation is an independent Boolean unit. Exact phrases cannot cross an uncertain/untranscribed interval or the boundary between a transcription and an editorial description. No phrases or Boolean evidence combine different notes, works or witnesses.

Results retain Niese alignment-unit ranges for Antiquities/Bellum and whole chapters or the Prologue for DEH. Each result links to its existing `-at-<offset>` annotation anchor. **45 displayed parts** inherit the **21 previously documented XML reading-association exceptions**. Their citations remain explicitly unverified and links open the source book with the original annotation anchor; no textual location is invented.

The main-text collections, engine, corpora, bundles and catalogue remain unchanged. Annotation data are a separate, deterministic bundle loaded only in annotation mode. The existing five-module, content-addressed browser release also assigns the annotation bundle a content-derived URL, so updated code cannot accidentally load an old annotation index. The immutable v1 launcher is unchanged. Older cached search HTML receives the new controls from the current application.

## QA results

- 573 Node search tests passed, including all publication/source-change regressions and seven annotation-specific cases.
- 196 Python extraction tests passed.
- 51 existing citation/interpreter/DEH annotation tests passed.
- All ten generated-site browser scenarios passed, including empty-query category browsing, cached HTML, error/retry, reader navigation and all-results downloads.
- Citation and DEH generated-data freshness checks passed.
- Generated publication/search checks passed: 166 scholarly XML files and the certified publication inputs retained their existing representations; the 261 search assets match the approved export.
- No canonical source, source annotation, main-text search bundle, catalogue or reader code changed. The 45 inherited unverified annotation locations remain explicit.

The implementation is prepared on its isolated feature branch. It has not been merged or published.

## Rebuild and verify

For a change confined to annotations, first verify the existing citation and DEH generators with their `--check` options. Then run:

```sh
node bin/search/build-annotations.mjs
node --test --test-concurrency=1 bin/search/tests/*.test.mjs
node --input-type=module -e "import {exportSearchAssets} from './bin/search/publication.mjs'; exportSearchAssets(process.cwd());"
node bin/search/check-assets.mjs
```

The full `bin/search/build-search.mjs` workflow also rebuilds the annotation projection. `validateAnnotationBundle` refuses stale source fingerprints or a projection that differs from the reader. Publication checks retain the existing main-text corpus safeguards.

Build the generated site using the existing Jekyll workflow, then run `bin/prepare-reader-publication.mjs --site <generated-site>` to verify certified publication bytes and search assets. The new generated-site integration harness is:

```sh
node bin/annotations/annotation-search-browser.cjs <generated-site> <evidence-directory>
```

It checks reviewed and symbolic readings, DEH chapter/Prologue links, manuscript and category filters, Unicode, keyboard submission, saved-state navigation, all-results CSV export, pagination, index-load failure/retry, query failure, mobile/dark layouts and existing main-text search/concordance. Its browser runtime is a development-only dependency.

## Preservation

No canonical XML, annotation source data, citation lookup, editorial convention, manuscript record, DEH parallel, reader rendering code or production hosting configuration is changed by this feature. Main-text counts remain 1,347,222 tokens across 25,009 indexed passage records (25,001 citation units) and 68 book editions. The annotation bundle is approximately 15.2 MB uncompressed (1.23 MB with gzip) and is cached for the current annotation-search page.
