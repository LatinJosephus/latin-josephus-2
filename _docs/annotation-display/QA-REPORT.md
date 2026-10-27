# Automated QA and visual verification

26 October 2026. **PASS**, with the source and environment limitations below.

## Preservation and interpretation

| Check | Result |
|---|---|
| Original manuscript reading records | All 2,958 retained exactly once, in original source order |
| Antiquities / Bellum records | 1,692 / 1,266 |
| Verified citation records | 2,937 |
| Documented original association exceptions | 21; source references unchanged |
| Presentation components | 6,201; 114 unresolved, explicitly flagged |
| Folio-only record | One, retained without creating a numbered annotation |
| Records without notation-parser issues | 2,731 |
| Original annotation XML IDs | None encoded; no new canonical IDs created |
| Canonical XML | All 166 production files match development Git bytes and the existing authority guard |
| Source corpus, concordances, Niese registries, DEH parallel files | Preserved |

The count of components is not a certified total of manuscript annotations. Unresolved syntax remains reviewable. Unknown codes, descriptions, partial words, ellipses and malformed foliation are retained in [the exception register](notation-qa.json). Thirteen hand-labelled components supply no transcription; the display says so without inferring inability to transcribe.

## Automated tests

- **24 annotation/citation/display tests passed.** These cover both work namespaces, the required Antiquities §§27–33 example, internal and final boundaries, actual non-contiguous Book XI coverage, source identity, all three hands, original annotation numbers, folio transitions, independent symbolic/untranscribable categories, supported abbreviation, unresolved ellipses, malformed notation, literal Unicode characters, source immutability, stable anchors, HTML escaping, native details, manuscript conflicts and the unconfigured DEH notation adapter.
- **Five Python tests passed.** Independent small XML fixtures exercise internal milestones, final units whose IDs deliberately have misleading numeric suffixes, lacunae, certified fragment precedence, interpolation exclusion and apparatus-number exclusion. A further corpus-level test in that suite compares protected files with the development Git authority, allowing the original checkout's line-ending representation only for unmodified non-corpus files.
- **565 existing search tests passed**, with no failures, cancellations or skips. This includes existing publication rejection tests, query and concordance behaviour, metadata, citations and saved links. The full suite ran sequentially; its publication test rehashes substantial temporary source and index copies. [Complete output](qa/search-regression.txt).
- The existing corpus guard passed, parsing all **166 XML files**, checking **38 publication authorities**, and passing **34 negative preservation tests** in temporary copies. It does not mutate the repository sources.
- The existing DEH parallel-integrity guard passed: **31 sources, 62 accepted serializations**, with its corruption-rejection checks.
- Search asset checks passed for **260 assets, 68 indexed books, 25,009 sections and 1,347,222 tokens**. The generated-site publication check also passed; exact frozen publication byte representations were restored only in generated output.
- Generated citation lookup and annotation inventory passed the deterministic `--check` freshness test. Source SHA-256 provenance matched.

This is **594 Node/Python tests**, plus the existing corpus/integrity guards and browser checks. [Repeatable check summary](qa/checks.json).

## Actual reader and navigation

[Browser certification](screenshots/browser-qa.json) passed with zero JavaScript errors in either selected baseline or final views:

- Thirteen baseline/final reader comparisons retained exactly the same Latin, Greek and English pane text after excluding the new navigation controls. They include book, chapter, alignment-unit and Niese views; the Antiquities Proem; irregular Book XI coverage; book-final units; DEH and Contra Apionem.
- All **27 Antiquities/Bellum books** were opened. Every source reading appeared once, with exact original notation, source order and unique display anchors, including unlocated records and the folio-only record.
- Native scholarly details opened and closed with Enter. Text-to-annotation links opened the panel and focused the target entry. Annotation-to-text links highlighted the whole associated alignment unit. Existing highlighting switched on and off. Permanent passage links survived reload.
- [Final UI smoke tests](qa/ui-smoke.json) executed an actual search, reloaded its saved URL, followed its result into the Bellum reader, checked Hand 2 with no supplied transcription, and opened a DEH comparison that loaded its Josephus text. All passed with zero JavaScript errors.

## Visual checks

Fourteen screenshots cover six before/after examples plus desktop dark mode and mobile dark mode. [Screenshot index](SCREENSHOTS.md).

Images were inspected after rendering. They include actual Hand 1/Hand 3 examples, several annotations on the same folio side, symbolic and untranscribable entries, and the supported Chartres abbreviated transcription. Hand 2 and all three hand codes are exercised by source-grounded automated and actual-UI tests. Panel spacing and focus offsets were corrected during visual review. Theme transitions were disabled only during screenshot capture, so captured colours represent the settled interface. Mobile panel overflow was checked at 390 pixels.

## Local build and limits

Both unchanged baseline and redesigned sites were generated with the installed Jekyll 4.4.1 builder. The local environment lacks the native `rmagick` dependency of the existing `jekyll-responsive-image` plugin, so the default Bundler build cannot be certified on this machine. The test build follows the repository's established reader-QA adapter: omit that one image plugin and exclude historical `review` archives. No new responsive images are used. Product Gemfile, production configuration, hosting and CNAME are unchanged. Existing Sass deprecation and pagination warnings remain.

The 21 original passage-association defects, ten unresolved manuscript references, two shelfmark conflicts, unexplained symbols and ambiguous ellipses require editorial decisions outside this presentation task. They are documented rather than silently corrected. English/French labels are supplied through a small dictionary selected from the document language; no site-wide language switch or new localisation framework is introduced.

Run `node bin/annotations/qa.cjs` to repeat the source-level checks. For full search regression, run `node --test --test-concurrency=1 bin/search/tests/*.test.mjs`. Browser scripts use a separately installed Playwright/Chrome runtime; set `LJ_PLAYWRIGHT_MODULE` if necessary. After segmentation changes, regenerate the lookup and run `--check`; the existing frozen publication pipeline has not been rewritten.
