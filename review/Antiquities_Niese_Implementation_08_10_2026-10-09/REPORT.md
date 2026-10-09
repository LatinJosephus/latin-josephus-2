# Antiquities VIII and X: completed isolated implementation

**Both books pass local scholarly and technical certification for the accepted scope.** No routine review or editorial decisions remain. Canonical integration, push and public deployment have not been performed or authorized. No other book was segmented.

Fresh implementation worktree: C:\workspace\LatinJosephus-antiquities-niese-08-10-implementation. Branch: antiquities-niese-08-10-implementation. Base: `a48021588e0840330388a6055a97bd0f7c2cf827` (actual clean canonical v2-development and origin/v2-development). This includes the Greek source-contents integration and accepted TOC typography work. The audit branch remains separate, with review-only checkpoint `fb8a65e2a6c7d6e5426f3b4751d30e67528b1a28` and printed checkpoint `dec5f783b1af936803150536ed5aaa031b21c479` preserved.

| Book | Greek sections | Retained Latin starts | Added Latin milestones | Latin intervals | Unavailable |
| --- | ---: | ---: | ---: | ---: | --- |
| VIII | 420 | 83 | 337 | 420 | none |
| X | 281 | 50 | 230 | 280 | 108 |
| Added total | 701 | 133 | 567 | 700 | one |

Existing I–VII: 2,456 selections. Certified isolated total: **3,157 selectable Antiquities Niese sections**, comprising I–VIII and X. IX remains unavailable. This selection total is distinct from the 700 newly represented Latin intervals and X.108's addressable absence state. Qualifications at VIII.367, X.102 and X.276 remain visible; X.108 retains Greek and broader English independently. No missing text is supplied and no gap is inserted.

The audit records are brought forward byte-exactly (381 files; AUDIT_RECORDS_PRESERVED.json). Older NO-GO, source observations and insertion rehearsals remain historical. IMPLEMENTATION_REPORT.md in each book packet and the new shared QA files are current certification. The latest X.102 and 276 decisions, VIII.367 surviving tail, elected VIII.368 and first repetition at 369 are in the frozen operative registers. X.18 does not cross a paragraph: its manuscript pb/cb changes are inside num15. X.108's absent alliance/Egypt-turn notice is distinguished from later surviving Egyptian narrative.

All four source reversals are byte exact, with UTF-8/LF retained. Every mixed locator was re-established against actual target nodes after comparing current Git blobs with frozen inputs. All narrative, labels, IDs, sameAs, paragraphs and divisions remain intact. 589 other base files are unchanged, including other books, Whiston, structure.xml, source contents and TOC registry. PDFs, print images and frozen research are unchanged. CERTIFICATION.json records before/after SHA-256, identities, complete narrative partitions and built-file hashes.

Actual implementation tests (not historical baseline tests): 420 VIII and 281 X selector events; all Greek/Latin interval projections; 18 critical deep-link/history/pane/theme cases; 12 uninstrumented critical production-reader URLs; independent rendered history/endpoints; IX fallback and return; no duplicate executable starts or DOM IDs. Final new-book, regression and interaction suites record **zero browser exceptions, console errors and failed requests**. Thirty-six light/dark screenshots are retained; VIII.367 and X.108 were visually inspected, together with first/internal/final selections. The existing dark header and local missing header-logo appearance are baseline cosmetics; the new text, notices and controls remain usable. No unrelated style change was made.

Protected actual-baseline comparisons and established range checks pass: 257 traditional Chapters, 1,432 Subchapters, 5,034 executable three-language ranges, 33 unavailable states, 198 Bamberg identities/594 displays, 1,441 Alignment units, 2,456 prior Antiquities Niese selections, XI multi-span, VI.xii.8/XIII, all nine chapters lacking lower division 1, and current Latin/Greek source contents including supplied Latin XIV [V]–[XII]. Bellum's 4,001 citations are compared from complete whole-book sources in Whiston and Lodge; Greek/Latin chapter ranges, Cardwell, marginal-note toggle, DEH and Contra Apionem ranges/deep links pass. Resolved initial test findings are retained under diagnostics; final PASS results are at the packet root.

Exact production scope (eight files):

- _includes/display-settings.html
- assets/js/renderTei.js
- assets/xml/antiquities/Greek/book-08.xml
- assets/xml/antiquities/Latin/book-08.xml
- assets/xml/antiquities/Greek/book-10.xml
- assets/xml/antiquities/Latin/book-10.xml
- assets/xml/antiquities/niese/book-08.json
- assets/xml/antiquities/niese/book-10.json

Review scope is restricted to the two per-book packets, the accepted batch-audit packet and this new implementation packet. FILE_MANIFEST.json records every deliverable path/hash; COMMIT_SCOPE.json is the exact staged path grouping. Older certification reports were not rewritten. Per-book commits depend on the shared reader machinery; their availability entries and data are separately reviewable.

Reproduce from this worktree: use build.sh in a disposable ruby:3.3-bookworm Docker container, with the implementation and canonical sources mounted read-only and the dedicated build output mounted writable. It builds actual implementation and baseline sites separately. Then run browser-certify.cjs (new books), browser-certify.cjs --regressions, browser-certify.cjs --ui-supplement; established-regressions.test.cjs without flags and with --protected-source-gate, --followup-gate, --multispan-gate, --alignment-gate, --locator-gate, --rendered-gate; finally verify_implementation.py. Runtime paths are in the scripts. implement.py is idempotent only over pinned original/applied bytes; it is an application tool, not a general merger. Test scripts expose production functions for exhaustive comparisons; the 12 critical URL checks also load the uninstrumented production script.

Build output is C:\workspace\Antiquities-Niese-Implementation-08-10-2026-10-09\build, separate from public or shared builds. The accepted inputs, exact authorized and inverse operations, build logs, QA and screenshots are retained. No unresolved issue remains within this pair's accepted segmentation scope. Subsequent work should first review these local commits and decide canonical integration; another segmentation batch was not selected.
