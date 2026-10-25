# AJ Latin repair — QA results

25 October 2026. **GO for local review of the repair. No publication performed.**

Base: `5bb301c1b41d63c89c33a79826fc62892ac3890f`. Branch: `repair/aj-latin-display-reconciliation-20261025`.

## Boundary verification and limits

The agent reviewed the existing intended Niese targets, corresponding DEH passages, current Latin beginnings/endings, and retained qualifications. An independent XML walk verified 44 components / 140 Latin section occurrences, matching all historical selections to the recovered independent expectations. There are zero adjusted DOM paths/sides, one approved excerpt-text change (IX.216) and 164 shifted absolute endpoints. See `AJ_LATIN_BOUNDARY_AUDIT.md` for every correspondence, including the inherited unavailable XX.238 interval.

Automated checks demonstrate that the application selects the audited passages and rejects unauthorized changes. They do not establish fresh manuscript collation, new human editorial approval, or independent verification of printed Ussani/Mras references. No XSD validation, CER measurement or new transcription was performed.

## Exact tests and results

| Test | Result |
| --- | --- |
| Remote `v2-development` reread | Still `5bb301c1b41d63c89c33a79826fc62892ac3890f`; no new base required |
| Byte-preserving checkout | All 926 files under assets/bin/includes plus the corpus manifest match literal base Git blobs; all 166 XML inputs pass approved-source authority |
| Original `node bin/deh-aj-display-qa.mjs` | Expected failure before repair at Latin XIV; all nine stale pins recorded |
| `python bin/aj-latin-boundary-audit.py` | PASS: 31 records, 44 components; exact current text, paths, sides, identities, CP/U16 coordinates |
| `python bin/aj-latin-reconcile.py` | PASS: byte-exact regeneration and include checksum; 32 source hashes verified |
| `node bin/deh-aj-display-qa.mjs` after repair | PASS: 31 records, 44 components, 420 witness-section occurrences, all 32 source pins, fixed independent audit certificate |
| `node --test bin/aj-latin-reconciliation.test.mjs` | 3 tests PASS; 32 source corruptions + concordance/layer/include/certificate tampering rejected; 3 well-formed repinned path/note/exclusion mutations also rejected |
| `node bin/reader-corpus-qa.mjs` | PASS: 166 production XML parsed; 38 frozen publication inputs; 29 negative checks |
| `node --test bin/millet1556-qa.test.mjs` | 12 PASS, including all-unit/chapter mappings and corruption rejection |
| `node bin/deh-parallels-integrity-qa.mjs` | PASS: 31 sources, 62 literal/LF acceptances, 279 rejected mutations, concordance/cache/HTTP guards |
| Local configured-plugin Jekyll build | PASS, Jekyll 4.4.1 / Ruby 3.3.12, 38.214 s; all configured plugins retained; historical review archives and these reports excluded from test output |
| `node bin/prepare-reader-publication.mjs --site <site>` | PASS: approved literal publication XML restored in generated output only; search assets verified |
| Actual browser AJ interval suite | PASS: 420 section occurrences, 132 witness-components / 93 witness views, 278 Latin endpoints, 8 corrupted-source rejections |
| Actual reader Latin comparison routes | PASS: all 31 routes, accounting for 44 components / 140 Latin occurrences |
| Actual source controls | PASS: Greek, Whiston and Latin with both Ussani and Pollard; AJ to BJ switching |
| Ordinary Antiquities browser views | PASS: III.184, IX.216, XIV.54, XV.23, XVI.135, XVII.193, XVIII.63, XX.224, all three ordinary panes |
| Numbering browser checks | PASS: whole-book Latin XVI/XVIII/XIX; unique generated XVI.356/.368 and XVIII.2/.4/.6/.27 labels; renderer exact hash retained |
| Actual browser Bellum suite | PASS: 2,115 extraction checks; 1,110 DEH source checks; 21 final-boundary and 8 eligibility mutation checks; 8,193 section occurrences |
| Actual browser Millet | PASS: aligned samples in all five books; highlighting toggles; comparison/return restores French I.16.3 state |
| Special cases | PASS: XX.238 explicit unavailable message; prior P4-D07 open-reference note; IX.216 corrected text |

Browser: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36`. Browser tests ran through the permitted in-app browser against a loopback-only local development server. They are actual DOM extraction, route and control observations, not a claim based solely on static tests. Browser raw records are in `_docs/aj-latin-reconciliation/actual-browser-*.json`.

## Build and test environment

The original copied Bundler lockfile needed a local CHECKSUMS update in a disposable build environment. Installed gem versions were reused; no original checkout lockfile or configuration was edited. Build logs retain pre-existing Sass deprecations and the Faraday retry warning. Generated frozen XML was restored only in the temporary test site using the existing publication preparer. Initial sandbox-local server access was unavailable to the browser; the same loopback-only server was restarted in the host environment before successful browser certification. Reader readiness waits were corrected during QA; the final results above wait for actual passage loading.

The generated site is local test output. No GitHub Pages run, public URL update or production deployment is claimed. Greek/Whiston boundary data and source XML are unchanged. The application runtime modules and renderer are unchanged; the strict offline validator now also checks a fixed audit certificate and independently resolves the selected XML coordinates using Python 3.

## Reproduction

From this repair checkout (Python 3, Node 24, and the project's normal Ruby/Jekyll dependencies available):

```text
python bin/aj-latin-boundary-audit.py
python bin/aj-latin-reconcile.py
node bin/deh-aj-display-qa.mjs
node --test bin/aj-latin-reconciliation.test.mjs
node bin/reader-corpus-qa.mjs
node --test bin/millet1556-qa.test.mjs
node bin/deh-parallels-integrity-qa.mjs
```

Build the normal Jekyll site to an external short destination, with disk cache disabled and `review` excluded for this local reader test. The exact configured-plugin build helper, copied lockfile, log and environment receipt are preserved in the external `outputs/AJ_LATIN_REPAIR_20261025` recovery evidence. Then:

```text
node bin/prepare-reader-publication.mjs --site <generated-site>
node bin/aj-latin-local-server.mjs --site <generated-site> --out <external-evidence> --port 4025
```

In the permitted browser, open `http://127.0.0.1:4025/__qa__/` and run all AJ checks. Open `/__qa__/bj/` for the unchanged full Bellum suite. Exercise the routes and native controls listed in the saved UI evidence. The server saves browser JSON locally and binds only 127.0.0.1. Do not replace browser automation with an unrelated remote-control mechanism.

The explicit `--capture` mode of the XML audit can reproduce historical comparison evidence when supplied the recorded historical XML root and independent October 14 oracle. It does not grant approval to replace the fixed certificate. Ordinary verification and regeneration are self-contained in this repair commit.

## Preservation and release boundary

All protected source hashes are listed in `_docs/aj-latin-reconciliation/protected-source-hashes.json`. Final checkout/branch preservation, literal-byte checkout testing, exact changed-file manifest, commit identity, incremental Git bundle and recovery ZIP are recorded in the adjacent external delivery receipt. Any failure in those final delivery checks prevents GO. No push or public publication is authorized or performed.
