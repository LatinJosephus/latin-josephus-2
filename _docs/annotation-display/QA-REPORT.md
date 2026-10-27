# Automated QA and visual verification

Updated 27 October 2026. **PASS**, with the source and environment limitations below.

Latest Book I follow-up: **53 annotation/citation/translation tests and five Python tests pass**. The original XML inventory remains 2,958 records / 6,202 components; one component now has a confirmed partial-transcription status. Three recovered worksheet components are separately counted and displayed at their editor-reviewed citations, giving 6,205 combined display components. See [the approved editorial update report](EDITORIAL-READINGS-20261027.md). The prior certifications described below retain their recorded scope.

Concise display follow-up: browser checks verify a single provisional reading with its explanation inside Scholarly details; symbolic category and supplied description on one line; accent-coloured wording with neutral editorial qualifiers; text contrast of at least 4.5:1 in both themes; and no horizontal panel overflow at 390 pixels. The data model, original notation, component counts and associations are unchanged.

Current follow-up: **45 annotation/citation/translation tests and five Python citation/preservation tests pass**. Eleven additional tests verify the [editor-confirmed historical nine-hand key](HISTORICAL-HAND-KEY.md), context-sensitive `¤`, actual additional hand prefixes and the newly separated Hand 8 component. The ten translation tests audit all 216 source-description variants and preserve every recorded-text segment across all 2,958 readings. The existing corpus, DEH and search asset guards are rerun. The 565 search tests below are the previous certification of unchanged search code. See [ENGLISH-EDITORIAL-NOTES.md](ENGLISH-EDITORIAL-NOTES.md).

## Preservation and interpretation

| Check | Result |
|---|---|
| Original manuscript reading records | All 2,958 retained exactly once, in original source order |
| Antiquities / Bellum records | 1,692 / 1,266 |
| Verified citation records | 2,937 |
| Documented original association exceptions | 21; source references unchanged |
| Presentation components | 6,202; 31 unresolved, explicitly flagged |
| Folio-only record | One, retained without creating a numbered annotation |
| Records without notation-parser issues | 2,801 |
| Original annotation XML IDs | None encoded; no new canonical IDs created |
| Canonical XML | All 166 production files match development Git bytes and the existing authority guard |
| Source corpus, concordances, Niese registries, DEH parallel files | Preserved |

The count of components is not a certified total of manuscript annotations. Unresolved syntax remains reviewable. Unknown codes, descriptions, partial words, ellipses and malformed foliation are retained in [the exception register](notation-qa.json). Thirteen hand-labelled components supply no transcription; the display says so without inferring inability to transcribe.

## Automated tests

- **35 annotation/citation/display tests and ten translation tests passed.** These cover both work namespaces, the required Antiquities §§27–33 example, internal and final boundaries, actual non-contiguous Book XI coverage, source identity, all nine confirmed hand codes, original annotation numbers, folio transitions, independent symbolic/untranscribable categories, supported abbreviation, unresolved ellipses, malformed notation, literal Unicode characters, source immutability, stable anchors, HTML escaping, native details, manuscript conflicts and the unconfigured DEH notation adapter. Hands 4, 7 and 9 are key fixtures, not claims of observed source prefixes.
- **Five Python tests passed.** Independent small XML fixtures exercise internal milestones, final units whose IDs deliberately have misleading numeric suffixes, lacunae, certified fragment precedence, interpolation exclusion and apparatus-number exclusion. A further corpus-level test in that suite compares protected files with the development Git authority, allowing the original checkout's line-ending representation only for unmodified non-corpus files.
- **565 existing search tests passed**, with no failures, cancellations or skips. This includes existing publication rejection tests, query and concordance behaviour, metadata, citations and saved links. The full suite ran sequentially; its publication test rehashes substantial temporary source and index copies. [Complete output](qa/search-regression.txt).
- The existing corpus guard passed, parsing all **166 XML files**, checking **38 publication authorities**, and passing **34 negative preservation tests** in temporary copies. It does not mutate the repository sources.
- The existing DEH parallel-integrity guard passed: **31 sources, 62 accepted serializations**, with its corruption-rejection checks.
- Search asset checks passed for **260 assets, 68 indexed books, 25,009 sections and 1,347,222 tokens**. The generated-site publication check also passed; exact frozen publication byte representations were restored only in generated output.
- Generated citation lookup and annotation inventory passed the deterministic `--check` freshness test. Source SHA-256 provenance matched.

The original redesign certification comprises **594 Node/Python tests**, plus the existing corpus/integrity guards and browser checks. The English-editorial and historical-key follow-ups add 21 tests. Current source-level checks rerun all 45 annotation/citation/translation tests and five Python tests, while the 565-test certification of unchanged search code is retained. These are 615 tests across those certification runs; the search suite is not claimed as rerun for this follow-up. [Repeatable check summary](qa/checks.json).

## Actual reader and navigation

[Browser certification](screenshots/browser-qa.json) passed with zero JavaScript errors in either selected baseline or final views:

- Thirteen baseline/final reader comparisons retained exactly the same Latin, Greek and English pane text after excluding the new navigation controls. They include book, chapter, alignment-unit and Niese views; the Antiquities Proem; irregular Book XI coverage; book-final units; DEH and Contra Apionem.
- All **27 Antiquities/Bellum books** were opened. Every source reading appeared once, with exact original notation, source order and unique display anchors, including unlocated records and the folio-only record.
- Native scholarly details opened and closed with Enter. Text-to-annotation links opened the panel and focused the target entry. Annotation-to-text links highlighted the whole associated alignment unit. Existing highlighting switched on and off. Permanent passage links survived reload.
- [Final UI smoke tests](qa/ui-smoke.json) executed an actual search, reloaded its saved URL, followed its result into the Bellum reader, checked Hand 2 with no supplied transcription, and opened a DEH comparison that loaded its Josephus text. All passed with zero JavaScript errors.

## Visual checks

The main browser run produced 22 screenshots covering ten before/after examples plus desktop dark mode and mobile dark mode. Additional English-editorial, approved Book I and concise-layout images are available in the [screenshot index](SCREENSHOTS.md).

Images were inspected after rendering. They include actual Hands 1, 2, 3, 5, 6 and 8, the newly separated Bodmer component, several annotations on the same folio side, symbolic and untranscribable entries, and the supported Chartres abbreviated transcription. Hands 4, 7 and 9 are absent from the source readings and are not fabricated for screenshots. Panel spacing and focus offsets were corrected during the initial visual review. Theme transitions were disabled only during screenshot capture, so captured colours represent the settled interface. Mobile panel overflow was checked at 390 pixels.

## Local build and limits

Both unchanged baseline and redesigned sites were generated with the installed Jekyll 4.4.1 builder. The local environment lacks the native `rmagick` dependency of the existing `jekyll-responsive-image` plugin, so the default Bundler build cannot be certified on this machine. The test build follows the repository's established reader-QA adapter: omit that one image plugin and exclude historical `review` archives. No new responsive images are used. Product Gemfile, production configuration, hosting and CNAME are unchanged. Existing Sass deprecation and pagination warnings remain.

The 21 original passage-association defects, ten unresolved manuscript references, two shelfmark conflicts, unexplained symbols and ambiguous ellipses require editorial decisions outside this presentation task. They are documented rather than silently corrected. English/French labels are supplied through a small dictionary selected from the document language; no site-wide language switch or new localisation framework is introduced.

Run `node bin/annotations/qa.cjs` to repeat the source-level checks. For full search regression, run `node --test --test-concurrency=1 bin/search/tests/*.test.mjs`. Browser scripts use a separately installed Playwright/Chrome runtime; set `LJ_PLAYWRIGHT_MODULE` if necessary. After segmentation changes, regenerate the lookup and run `--check`; the existing frozen publication pipeline has not been rewritten.
