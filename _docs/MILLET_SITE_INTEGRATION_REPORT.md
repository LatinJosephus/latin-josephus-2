# Millet 1556 — local DEH reader integration

Status: **implemented, built and browser tested; ready for independent verification**. This is a local feature branch. The existing Antiquities Latin comparison has a separately documented baseline hash-pin failure; its historical source authority has not been weakened to conceal that failure.

## Delivery identity

- Worker: MilletWorkBot2; 24 October 2026.
- Branch: `millet1556-deh-integration-20261024`.
- Implementation commit: `49ce06c0a9dd5f212ab78cbf4e9a04c7da5ab33c`.
- Base: `e3fe7b1a677dd340d707d544bdb7e90bc84a08cb` (the existing local `origin/v2-development` reference).
- Worktree: `C:/Users/Pollard_R/.codex/.chatgpt-projects/g-p-69862e643cc08191a8457368cb0c460f/worktrees/millet1556-deh`.
- Evidence: `C:/Users/Pollard_R/.codex/.chatgpt-projects/g-p-69862e643cc08191a8457368cb0c460f/outputs/Millet_Site_Integration/MILLET_SITE_20261024_WorkBot2`.
- Local reader: http://127.0.0.1:4019/deh/?book=1&chapter=1&unit=1&french=millet1556
- Edition guide: http://127.0.0.1:4019/deh/millet-1556/

The original `v2-development` checkout remains at its initial tracked state, eleven commits behind that local tracking reference. Its two unrelated untracked Bamberg reports remain present. There was no fetch, reset, push, deployment or public preview. A documentation commit follows the implementation commit; the final delivery receipt records both full hashes and every changed file's SHA-256.

## Implemented reading behaviour

French — Millet 1556 is an optional DEH pane. Latin and Pollard English remain the defaults. No French book asset loads until French is enabled. The manifest and individual book assets are loaded and checked lazily.

The general reader panel contains Millet's view, chapter, folio, alignment, Ussani correspondence and share controls. The French text pane contains the text and a compact selected-passage label. Text follows the main book/chapter/unit view, as in the other aligned readers. Complete text exposes the entire French book independently of Ussani segmentation; Complete source also retains paratext, dedications and marginal source material. Native chapters, preliminary matter, blank leaves and the colophon remain accessible.

The editor's subsequent display instructions supersede the original line-preserving presentation: the reading text now flows across physical lines, joins continuations at `¬`, and uses the site's edition font and size. Image numbers are absent from the reading interface. Folio labels are optional and off by default; printed folio/header text remains in the frozen XML and source data. Viewer folio labels derive from the printed header numerals and the following verso; unnumbered leaves remain explicitly unnumbered.

Source line IDs, exact Unicode and exact whitespace remain in the data and source-coordinate DOM spans. Hidden `¬` spans suppress display only. Separating spaces are separately tagged outside the frozen line payloads. In a unit/chapter reading view, unrelated parts of boundary lines remain hidden source-coordinate spans; the displayed correspondence is the recorded interval, never an inferred whole chapter. Discontinuous source intervals are signalled. The browser checks verify exact source reconstruction, codepoint/UTF-16 boundaries and actual highlighting.

Selecting a Latin unit highlights its French intervals. Selecting a French linked span locates Latin; ambiguous multiple targets offer a chooser. Deep links preserve mode, native chapter, source leaf, selected canonical unit, alignment visibility and optional folios. Josephus links reuse the existing concordance, with a tested return path to the French state.

## Certified source and provenance

Frozen master: `MILLET_USSANI_MASTER_20261024T153200Z_r1`, status `INTEGRATION_READY`.

| Authority | SHA-256 |
|---|---|
| Master XML | `594eface68456fed60140956e0986cc16c28ed7562e7eee6e6eefbda6d9dc95c` |
| Machine alignment data | `7631ce6d7a943ee8c25554236962e6f7a2cddd6c3fcc060747569bf807b949f4` |
| Source/version manifest | `37bf825918426063a487233de506694333422d97990a9b666a79ce3570252c3c` |
| Freeze receipt | `1fc9bd39e158b6fabf9bbf44c0f76f8f7d74e3f977e744627933282630146e7c` |

The master verification hashed all 1,902 manifest members, checked the recovery ZIP hash and ran the frozen read-only live verifier. All 558 Ussani units are retained: 215 / 73 / 70 / 79 / 121 by book, including all three Prologue units. The primary coverage has 16,236 source lines/fragments, 16,612 exact source intervals and 934,885 codepoints. All 19,104 nonempty source-line payloads across 582 accepted pages survive in site assets and source views, including 2,868 ancillary/paratext lines. The release retains all 5,716 `¬` markers in source data.

The 549 one-to-one, seven many-to-one and two displaced primary relations, 162 secondary annotations, four inherited attention flags, 24 ancillary questions, historically pending B001-B009 and two source notices remain intact. There are no wholly absent canonical units in this actual release. One-to-many and absent-unit support has synthetic regression fixtures; those fixtures do not create scholarly readings.

The nine deterministic derivatives are under `assets/data/deh-millet1556/`. `manifest.json` identifies the edition, offsets, source authority and lazy book hashes; `provenance.json` binds all other asset bytes to the freeze receipt. The delivery inventory additionally hashes provenance itself. No canonical or source XML was edited.

## Verification performed

| Check | Actual result |
|---|---|
| Deterministic importer `--check` | PASS, nine assets; 558 units; 19,104 source lines |
| Millet Node suite | PASS, 11 tests; all-unit coverage and rendering-coordinate reconstruction |
| Actual browser | PASS, Edge 156.0.4314.42; all 558 canonical texts and exact French selections |
| Cross-page mappings | PASS, 348 tested units across five books |
| Focused cases | PASS: Prologue, I.2.1, I.8.1, displaced I.16.3–4, multiple spans, unmapped preliminaries, blank leaf and colophon |
| Flowing display/general controls | PASS; hidden division markers preserve source offsets; optional folios default off |
| Navigation | PASS: native chapter/folio links, reload, history, source-to-Latin and existing parallel return |
| Responsive layout | PASS: 390px viewport, 390px document; no overflow |
| Browser errors/local HTTP errors | Zero in the final Millet test |
| Existing full DEH–Bellum harness | PASS in actual in-app browser: 2,115 BJ extraction and 1,110 DEH source checks |
| Parallel integrity mutations | PASS: 31 sources, 62 accepted representations, 279 rejected mutations |
| Existing reader smoke tests | PASS: Lodge/Whiston Bellum; Lodge/Whiston Antiquities; Lodge Contra Apionem; Greek/Latin panes; AJ Greek and English |
| Existing search | PASS in browser; 44 automated search UI/release regression tests; search publication gate passed |
| Complete configured Jekyll build | PASS, all configured plugins, latest full build 217.683 seconds |
| Publication and corpus gate | PASS: all 166 production XML files parsed; 38 frozen publication inputs verified |
| Final preservation | PASS: 15 captured baseline XML hashes and all 610 frozen XML members unchanged |
| Formal XSD / independent semantic proofreading / measured CER | Not performed; not claimed |

The first long destination failed on Windows' path-length limit in an existing static diagnostic filename. A shorter temporary destination resolved it. RMagick 4.3.0 was compiled locally against the installed ImageMagick 6.9.13; the responsive-image plugin was included, not omitted. The exact resolved `Gemfile.lock` is retained in the evidence records. Ruby 3.3.12, Bundler 4.0.22 and Node 24.19.0 were used. Existing Sass deprecation and Faraday retry warnings remain. The generated static reader files were synchronized after final QA repairs and independently checked byte-for-byte against the committed source; no XML source repair was involved.

## Known baseline limitation

`bin/deh-aj-display-qa.mjs` fails its historical pins for eight Antiquities Latin XML files (III, IX, XIV–XVIII, XX). `PREEXISTING_AJ_GUARD.json` proves each equals the base commit's bytes; the approved Bamberg correction commit predates this feature. The same historical audit also pins the old renderer file, which this feature legitimately changes. These failures are not reported as a passing historical audit.

The existing runtime correctly refuses those stale Latin AJ comparison pins. Greek and Whiston AJ comparisons work and passed the browser checks; ordinary Antiquities Latin reading and the reviewed corpus guard also pass. No source hash was silently repinned and no unverified AJ boundary was adopted. Refreshing that historical derived AJ layer against the approved Bamberg changes is a separate audit item.

## Reproduction

From this feature worktree, with Python, Node, Ruby/Bundler, ImageMagick and Playwright available:

```text
python bin/millet1556-import.py --master <frozen-master> --check
node --test bin/millet1556-qa.test.mjs
node bin/search/check-assets.mjs
bundle exec jekyll build --destination <short-generated-path> --disable-disk-cache
node bin/prepare-reader-publication.mjs --site <short-generated-path>
node bin/reader-corpus-qa.mjs --site <short-generated-path>
python -m http.server 4019 --bind 127.0.0.1 --directory <short-generated-path>
node bin/millet1556-browser-qa.mjs --base-url http://127.0.0.1:4019 --output <external-QA-dir> --browser-executable <installed-browser>
node bin/millet1556-reader-regression.mjs --base-url http://127.0.0.1:4019 --output <external-QA-dir> --browser-executable <installed-browser>
```

Use the saved lockfile for the exact tested Ruby dependency set. On this Windows host, set `GEM_PATH` to the isolated worktree `.bundle/gems` plus `C:/Ruby33-x64/lib/ruby/gems/3.3.0`, and put `C:/Program Files/ImageMagick-6.9.13-Q16` first on `PATH`. Set `NODE_PATH` if Playwright is supplied by the bundled runtime. `records/SITE_PATH.txt` identifies the current generated directory. The local server is temporary; these commands recreate it.

`MILLET_WORKBOT3_INDEPENDENT_AUDIT.md` gives the independent checks. The external delivery receipt, changed-file inventory, QA records and screenshots accompany the implementation. The audit package requires the existing base repository and certified master; it does not duplicate or modify their frozen source corpus.
