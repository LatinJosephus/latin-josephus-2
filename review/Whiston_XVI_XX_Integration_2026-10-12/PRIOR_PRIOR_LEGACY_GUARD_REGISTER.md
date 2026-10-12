# Legacy test and build guard reconciliation

Every original safeguard below is retained or replaced by a more explicit assertion. Historical source certificates and their original failed-launcher logs remain unchanged. No failure is hidden by deleting a test or disabling a build plugin.

## G01 — bin/deh-parallels-qa.mjs

**Original purpose:** Bind DEH excerpt QA to unchanged scholarly authorities.

**Existing expectation:** Every one of the historical 100 XML hashes still describes the entire current corpus.

**Validity:** Frozen concordance SHA and all 31 DEH/Bellum excerpt input hashes remain valid; Antiquities-wide historical identity is obsolete.

**Behaviour/source change:** Twelve certified English files and the reviewed IX English structural registry replace earlier Antiquities inputs; earlier canonical source/paratext releases also supersede historical hashes.

**Minimal disposition:** Hash-bind a complete 143-path reviewed manifest; parse every XML; retain every frozen excerpt authority hash and serve only its exact reviewed bytes.

**Result:** PASS: native launcher, 2,115 component checks and 8,193 displayed section occurrences.

## G02 — bin/bellum-greek-range-qa.mjs

**Original purpose:** Detect source mutation during Bellum range QA.

**Existing expectation:** Exactly 107 tracked XML files, including the historical seven Lodge additions.

**Validity:** The source-mutation safeguard is valid; the fixed tracked count is obsolete. The canonical pin already contains 286 tracked XML, including review evidence.

**Behaviour/source change:** The reviewed production corpus now contains 143 XML paths; review XML is separately preserved evidence.

**Minimal disposition:** Require the exact complete production path/hash manifest, preserve before/after hashes for every production XML, and retain all raw-XML range and baseline DOM assertions. Remove the old static-guard surgery workaround and run the repaired native static guard.

**Result:** PASS: both sources, 111 chapters, 704 subchapters and 4,001 Niese views each; Greek/direct/Latin/English parity preserved; focused state/note/history checks pass.

## G03 — bin/lodge1602-bellum-qa.mjs

**Original purpose:** Prevent unknown XML additions and malformed files, including the seven explicitly identified Lodge paths.

**Existing expectation:** Historical 100-path set plus exactly seven Lodge files, with only Antiquities Greek/Latin V differing.

**Validity:** Unknown/missing/malformed source rejection and exact seven Lodge identities remain valid; the historical current-corpus census and two-file delta are obsolete.

**Behaviour/source change:** Later pinned canonical releases and certified I–XI English assembly have explicitly reviewed additional paths and source versions.

**Minimal disposition:** Compare the current parsed corpus to the exact reviewed 143 paths; retain historical change records, the exact seven Lodge paths, unknown-file detection and malformed-Lodge rejection.

**Result:** PASS: native inventory and both negative XML checks. The browser body is verified by the complete native Lodge rendered-text suite; its frozen accepted QA document is retained.

## G04 — bin/lodge1602-bellum-qa.ps1

**Original purpose:** Independently compare Lodge against its immutable master, protect all source trees and detect deliberate corruption.

**Existing expectation:** Physical checkout bytes equal the old master/100-file snapshot and Lodge publication hash.

**Validity:** Master SHA, frozen evidence byte equality, full decoded text/whitespace/tree/ID/milestone assertions and corruption tests remain valid. Fresh Git LF differs from the reviewed CRLF bytes.

**Behaviour/source change:** Whiston source assembly is explicit; Git recovery may change only line-ending representation of unchanged non-Whiston witnesses.

**Minimal disposition:** Use the complete reviewed source guard and exact frozen publication hashes for unchanged Bellum witnesses; retain every independent master/tree assertion and all nine corruption tests.

**Result:** PASS: immutable master SHA, 4,001 HIGH Lodge intervals, 704 coarse links, 111 chapters, all nine deliberate corruption tests rejected. No guard block is removed at runtime.

## G05 — bin/reader-corpus-integrity.mjs, bin/prepare-reader-publication.mjs, bin/reader-corpus-qa.mjs, _docs/reader-corpus-integrity.json

**Original purpose:** Retain frozen publication authority hashes across fresh Git/build recovery.

**Existing expectation:** Git/build byte representation already equals the reviewed CRLF authority.

**Validity:** Every frozen SHA must still match literally. The implicit EOL assumption is false for a fresh checkout.

**Behaviour/source change:** No text, structural or frozen-hash change; exact known EOL representation is reconstructed in generated output only.

**Minimal disposition:** Accept only recorded checkout hashes, keep certified Whiston bytes exact, and restore generated publication bytes only if their literal SHA equals the frozen authority. Validate all generated XML before writing.

**Result:** PASS: 143 parsed source paths; 38 literal frozen publication hashes; missing, unexpected, corrupt source and altered manifest/concordance/Lodge authority tests all rejected.

## G06 — Gemfile, _config.yml, build/Gemfile.lock, build/im6-build-env.rb

**Original purpose:** Run the standard publication build with its required plugins/dependencies.

**Existing expectation:** RMagick and compatible native SDK available; all configured plugins load.

**Validity:** Valid and retained. Missing Windows RMagick was a pre-existing environment failure, not a renderer regression.

**Behaviour/source change:** Only isolated task dependencies are prepared; no Gemfile/config/plugin removal.

**Minimal disposition:** Build RMagick 4.3.0 against the installed ImageMagick 6 SDK in the task directory, resolve locally installed gems, then run ordinary bundle exec jekyll build with all plugins. The lock/bootstrap are review evidence only.

**Result:** PASS: bundle check; standard complete-plugin build in 112.326 seconds; generated reader inputs equivalent to the certified preview; inherited Sass warnings only.

## G07 — bin/lodge1602-bellum-browser-qa.js, bin/bellum-greek-range-browser-qa.js

**Original purpose:** Require the complete numbered chapter menu and validate actual rendered source words.

**Existing expectation:** Every nonempty chapter option is numeric and renders a chapter div.

**Validity:** Exact numeric chapters remain mandatory; the existing canonical source-contents option is a distinct paratext view.

**Behaviour/source change:** This was already present at the canonical pin. Whiston integration introduces no contents feature.

**Minimal disposition:** Allow only the explicitly known contents control alongside exact numeric chapters (including inherited chapter 0); retain numeric counts and frozen digest; additionally compare all seven Lodge contents views with the registry-selected raw XML.

**Result:** PASS: complete numbered views and frozen Lodge digest unchanged; seven exact contents checks pass; no unknown control is silently ignored.

## G08 — Historical review/* English context and IX unavailable assertions, review/BookI_Pilot_2026-10-10/scripts (original delivery archive), tools/smoke_qa.cjs, tools/xml_intervals.py

**Original purpose:** Ensure English appears exactly as the source/version enabled by that release, and preserve independent witness availability.

**Existing expectation:** I–XI direct English is contextual, VII.1–6 may recover the complete contextual paragraph, and IX.51–109 English is unavailable.

**Validity:** Correct for the frozen historical release; superseded for certified segmented I–XI. Contextual fallback remains valid for XII–XX. Greek/Latin IX omissions remain valid.

**Behaviour/source change:** Certified exact English rendering replaces paragraph context only for the explicit Proem/I–XI enablement; 59 restored IX English intervals become available independently.

**Minimal disposition:** Preserve immutable old certificates/scripts; replace current acceptance with all 3,821 exact interval hashes/boundaries plus separate 18 inherited fallback views. Fresh standard-built checks cover every restored IX interval, every Book I MEDIUM decision, VII.1–6, XI transitions, native navigation and nine fallback books.

**Result:** PASS: 3,821/3,821 independently reconciled exact displays; 119 fresh exact checks; all 59 restored IX; 10 native neighbour selections; 18 inherited and 9 fresh fallback checks. No failed contextual assertion is counted as a pass.

## G09 — bin/deh-concordance.mjs, assets/js/dehParallelsCore.js, assets/data/deh-josephus-concordance.json, bin/lodge1602-bellum-import.ps1

**Original purpose:** Prevent mutation/reimport of frozen scholarly authority and detect corpus changes after an import.

**Existing expectation:** An import candidate must still match the corpus and source authority from which it was constructed.

**Validity:** Valid; this integration does not reimport the concordance or Lodge. A historical import against a changed corpus should still refuse acceptance.

**Behaviour/source change:** Only English reader/source integration and reviewed QA corpus identity; no concordance/master authority change.

**Minimal disposition:** None. Preserve the strict importer/production assertions and every frozen data byte.

**Result:** Unchanged; frozen bytes and production module identical to pin; full native displayed extraction suite passes.

## G10 — BookI-original/SCHEMA_QA.json, BookI-original/REPORT.md

**Original purpose:** Distinguish XML parsing/project fragment conventions from generic TEI All schema conformance.

**Existing expectation:** Baseline and segmented headerless fragments both fail generic TEI All at the missing teiHeader.

**Validity:** Valid inherited qualification. It must not be relabelled schema success.

**Behaviour/source change:** No new schema diagnostic, source wording or non-milestone structure change.

**Minimal disposition:** None; preserve original failed generic-schema receipt and require all current project XML to parse.

**Result:** 143/143 production XML parse; generic TEI All remains an acknowledged pre-existing fragment limitation.
