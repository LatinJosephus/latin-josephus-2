# Antiquities: display of a following paragraph's citation label

The isolated reader correction removes a label-only tail from Antiquities X.107 and four equivalent Niese selections. Canonical Latin XML, visible inherited source labels, all milestones, executable identities, wording and editorial decisions remain unchanged. The correction is ready for integration after the recorded regressions; this packet does not authorize a push or preview deployment.

The verified base is `81126ce116045433cb5cf22945cc3711701ac3ca`, with clean canonical and origin/v2-development at preflight. The correction branch is `antiquities-niese-boundary-display`; its checkout is `C:\workspace\LatinJosephus-antiquities-niese-boundary-display-20261009`. Production scope is only `assets/js/renderTei.js`. All additional files are in this review packet. Earlier scholarly and integration certificates are untouched.

The exact origin of `[VII.iii.108]` is `assets/xml/antiquities/Latin/book-10.xml`, line 75: the first `num` child of `p[@xml:id='latin-book10-num108']`, within the transmitted `div2[@n='10']`. That wrapper's number is distinct from the traditional locator VII.iii. The label occupies UTF-8 bytes 36,406–36,429 inclusive in the pinned input. The file's before/after SHA-256 is `5fda72762771755b5f6d6324e74f7d63d055ff9c911b180e15cccf61efdaec26`.

```xml
<p xml:id="latin-book10-num108"><num>[VII.iii.108]</num> <milestone unit="niese" n="109"/>Interea dum hoc cognouisset ...
```

The Latin identity registry suppresses this inherited label's executable claim to 108 and retains the true 109 milestone. Latin 108 is explicitly unavailable. Section 107 begins internally in `latin-book10-num103` at `eo quod` and ends with `quae tamen oportunius declarauimus.` Its next available Latin start is 109. The former DOM range ended before the 109 milestone, after the beginning of the next paragraph and chapter wrapper. It therefore cloned that paragraph's label and whitespace into 107. Paragraph cleanup retained this otherwise empty fragment because it contained `tei-num`. No words from 109 were included.

The renderer now examines the portion of a different ending paragraph before a leading milestone. It cuts the display before that paragraph only when removing its citation labels leaves whitespace and no other elements. Narrative, notes, apparatus, gaps, physical markers and other markup prevent this adjustment. Starts within the same paragraph and the explicit narrative-end mechanism retain their previous behavior. This is a read-only operation on a cloned display fragment; the source DOM and XML are untouched.

The systematic comparison of all **4,315 currently selectable Antiquities identities** found exactly five label-only tails:

| Niese selection | Following paragraph | Removed from that selection's display |
| --- | --- | --- |
| VI.268 | latin-book06-num271 | [XII.viii] |
| VI.270 | latin-book06-num272 | [XIII.i] |
| X.107 | latin-book10-num108 | [VII.iii.108] |
| X.149 | latin-book10-num151 | [VIII.vi.151] |
| XIII.212 | latin-book13-num213 | [VI.vii.213] |

After correction, none of those tails remains. These are the only changed Niese display projections. All three languages' narrative projections, Greek and English markup, availability notices, correspondence qualifications, selection counts, and Greek/Latin start inventories remain identical. All 148 pinned corpus/registry files remain byte-identical; the fresh build also matches all 240 checked static source assets. Existing IDs, sameAs links and Niese milestone identities are consequently unchanged.

The uninstrumented built reader passes 17 targeted Niese URLs, including every X.106–109 selection and the other affected neighbours. X.107 ends at its own transmitted sentence; X.108 still displays a Latin absence notice with independently available Greek and English; X.109 still starts at `Interea dum hoc cognouisset`. The label is neither supplied to 108 nor reassigned to another Niese identity. Seven actual broader views retain their original three-pane markup and inherited labels: X Chapter VII, VII.iii, Alignment unit 108, VIII.vi; VI XII.viii and Chapter XIII; XIII Chapter VI. Previous/next through 106–109, Back/Forward, reload, panes, unique DOM IDs, light/dark themes and asset loading pass. The before/after X.107 screenshots were visually inspected.

Protected comparisons pass all 1,689 traditional Chapter/Subchapter identities (257 + 1,432), 198 Bamberg identities, 1,441 Alignment units and all 21 Antiquities book/Proem contents projections. Bellum's 4,001 Niese citations pass under both Whiston and Lodge, with 815 chapter/unit ranges per source and the Lodge note/source controls. Twelve additional uninstrumented deep-link/reload routes cover DEH, Contra Apionem, Book XI multispan behavior, Bellum chapter views and current Whiston/source contents for III, V, XII, XIII and XX. No browser exceptions, console errors or failed assets occurred on the tested valid routes. The inherited Book-I apparatus-link and unsupported I.1 issues documented by previous packets are outside this correction.

`BASELINE.json`, `XML_ORIGIN.json`, `SOURCE_PRESERVATION_QA.json`, `BUILD_RECORD.json`, `EQUIVALENT_LEAKAGE_QA.json`, `FOCUSED_BROWSER_QA.json`, `PROTECTED_BROWSER_QA.json` and `CROSS_ROUTE_QA.json` supply the source and verification evidence. `FILE_MANIFEST.json` enumerates the exact review scope. The dedicated runtime is `C:\workspace\Antiquities-Niese-Boundary-Display-QA-20261009`; it does not use or modify the publication checkout. Its baseline is the retained certified combined XII–XIII build, qualified by exact XML/renderer bytes and the absence of production changes between its tested merge and the current base. A complete new Jekyll build tests the correction with all configured plugins.

Reproduce with `build.sh` using the recorded pinned Ruby image and readonly source mount. Run `leakage-browser.cjs --baseline`, `leakage-browser.cjs`, `focused-browser.cjs`, `protected-browser.cjs --protected` and `cross-route-browser.cjs` with the recorded installed Node/Playwright/Chrome runtime. The baseline must remain unchanged; candidate paths and output scope are recorded in `BASELINE.json`. These checks do not modify any older certification packet. `finalize.py` verifies source preservation and freezes this packet's manifest.
