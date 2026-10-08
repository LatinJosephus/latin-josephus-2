# Greek Antiquities capitula: TOC v1.1 implementation certification

8 October 2026. GO for human browser review; implementation remains unstaged and uncommitted.

The nine accepted Greek source-paratext companions have been installed byte-for-byte from the approved audit. Nine VERIFIED source-contents records were appended without rewriting any original registry bytes. Greek Antiquities contents are now available for I–XX through the unchanged source-specific reader. No JavaScript, CSS, narrative XML, source numeral, alignment target, existing ID, sameAs, or structural registry changed.

Worktree: `C:\workspace\LatinJosephus-Greek-Capitula-Integration-20261008`. Branch: `codex/antiquities-greek-capitula-toc-v1.1`. Base and unchanged canonical HEAD/origin: `f393fa1223b38d9ca114e583fcc57d5e34425815`. Canonical branch remains v2-development, clean. No stage, commit, merge, rebase, push or Git configuration change occurred.

| Book | Entries added | Accepted source status | Implementation/schema |
|---|---:|---|---|
| 1 | 19 | PRINT_VERIFIED | PASS |
| 2 | 8 | PRINT_VERIFIED | PASS |
| 3 | 10 | PRINT_VERIFIED | PASS |
| 4 | 5 | PRINT_VERIFIED | PASS |
| 6 | 15 | PRINT_VERIFIED | PASS |
| 7 | 12 | PRINT_VERIFIED | PASS |
| 8 | 12 | PRINT_VERIFIED | PASS |
| 9 | 16 | PRINT_VERIFIED | PASS |
| 10 | 12 | PRINT_VERIFIED | PASS |
| **Total** | **109** | | **PASS** |

The 120 original audit manifest entries and all 504 separately recorded input hashes verify. The audit contains 121 files: its manifest deliberately excludes itself. Its manifest SHA-256 remains `4d5bf373b7d9d5c0d656a04b567b591446bafca9b24d4969ec98f73956c75d1b`. Full raw print/digital evidence remains at the unchanged external audit location, with a byte-identical core mirror and explicit archival reference here. No new source reading or transcription was made. See SOURCE_AUTHORITY.md and AUDIT_ARCHIVE_REFERENCE.json.

The nine companions and extended registry validate against the unchanged project TEI All Relax NG schema. All 109 item texts, literal labels, n values and item identities match the elected printed-Niese master exactly. File-byte equality additionally preserves every heading, rubric, trailer, accent, bracket and punctuation sequence. Printed and Perseus readings remain separately recoverable in the archived master/collation. Book I retains its paratext proem-summary rubric, without importing the actual general proem or narrative. Capitula remain non-clickable source lists with no asserted chapter/Niese equivalences.

Browser checks on the separately built Jekyll reader passed all nine books in both themes (18 complete lists), all 30 existing source records, nine per-book copied-URL/reload/history/pane/Chapter↔contents checks, all twenty Antiquities books in contents mode, and keyboard selection. `?book=N&view=contents` remains unchanged. Greek typography inherits the unchanged established reading stack. Long entries wrap; no contents overflow, duplicate contents DOM IDs, page errors or failed network requests were observed. Contents text contrast measured 14.05:1 light and 11.85:1 dark. Latin/English retain their own contents or neutral unavailable state. BEFORE/AFTER screenshots cover I, II, VII, IX and X in both themes, with additional final-entry captures for IX/X.

Regression results:

- Traditional: 257 Chapters, 1,432 Subchapters, 1,689 rows, 1,441 physical positions; 5,034 executable language ranges and all 33 expected Book IX unavailable states pass.
- Niese I–VII: 2,456 selections / 7,368 language DOM comparisons unchanged. VIII–X remain unavailable for public Niese navigation; new contents do not enable citation navigation.
- Bamberg: 198 identities / 594 language ranges, compact URLs, all six same-Niese/different-position pairs (18 language checks), duplicate/missing labels and negative evidence in VI–XI pass.
- Alignment: all 1,441 units / 4,323 language comparisons and Book witness order unchanged.
- Follow-up: all 257 chapter-availability transitions, nine zero-subchapter chapters, 227 structural-prefix clipping checks, VI.xii.8/XIII and XI shared notice pass.
- XI ordered multi-span membership, no duplication, interpolation retention and witness-order Book/Alignment views pass.
- Bellum: full seven-book Whiston and Lodge differential chapter/unit/Niese range suite passes; all 3,722 currently selectable Niese coordinates per source (7,444 source/coordinate comparisons) preserved; the 4,001 Lodge segmentation markers remain byte-identical. Lodge notes and source switching pass.
- DEH, Bellum and Contra Apionem: all menu-defined chapter/unit ranges match the base; five protected interaction configurations and both themes pass.

All 499 canonical tracked files retain their initial SHA-256 values and canonical index is unchanged. All 498 protected pre-existing worktree files, including 113 XML files and all prior certifications, retain their own checkout hashes. Git initially checked out 109 files with LF in place of canonical CRLF; only line-ending serialization differs between those initial checkouts, and neither checkout was normalized. Individual before/after hashes are in INTEGRITY_QA.json. Canonical inventory digest (sorted path-to-SHA mapping, UTF-8 compact JSON) is unchanged: `8f59a0df05ce16500d49e0da7de4e77c90a2dad8624b8dacf85fa2181cca8626`.

Only the following ten production source paths changed; all other new files belong to this certification directory:

| Path | Added population | Final SHA-256 |
|---|---:|---|
| `assets/xml/antiquities/paratext/niese/book-01-contents.xml` | 19 | `a207dc793d50629e1b4968fd657780194221104b50d6cd87f8423a0e4c8e0c0f` |
| `assets/xml/antiquities/paratext/niese/book-02-contents.xml` | 8 | `8bbf9b91615d94ae48f398fede9f9e388709f22414463a804d08836cb36f8339` |
| `assets/xml/antiquities/paratext/niese/book-03-contents.xml` | 10 | `ec18224bd0dff88d173f6e9b7afffbf98e0b3fd3a58fb210ea302afc4eb664a3` |
| `assets/xml/antiquities/paratext/niese/book-04-contents.xml` | 5 | `cdd115cf3e8622d23ef2ac2146c99d14457b3108f05042dc1da6566ac89dea18` |
| `assets/xml/antiquities/paratext/niese/book-06-contents.xml` | 15 | `86ff06efecf4cbb1ceff5621ccf70c7b6e7c23b2033b1df6950c1e0c6bd92534` |
| `assets/xml/antiquities/paratext/niese/book-07-contents.xml` | 12 | `6135c8e95ebd6ae4fb829797dca284869eb105f098964db61b88c75641b1f768` |
| `assets/xml/antiquities/paratext/niese/book-08-contents.xml` | 12 | `16fa639cb136f6c81984a45f177a1f8cbb12b00952b80a2499b3d8c3870a13f6` |
| `assets/xml/antiquities/paratext/niese/book-09-contents.xml` | 16 | `01f556da6bf7f2443500f0de8f3183640e44075681449f55b66cf98ab06c83d0` |
| `assets/xml/antiquities/paratext/niese/book-10-contents.xml` | 12 | `2d9fb947ef225ae9159b1d39715c0c7660bd3b4998f9e574705b4a9ff7fb51ab` |
| `assets/xml/source-contents.xml` | 9 records added | `3baa8ef1b2e9137b9fbabf3de22d42aca8c3818d4b66d6efe3e239bac9b12092` |

Registry original SHA-256: `3d75560ebb1c5aa67647cb735e7d23de05eaa29fbeb6705c47719ca5a6d063f4`. Registry final SHA-256: `3baa8ef1b2e9137b9fbabf3de22d42aca8c3818d4b66d6efe3e239bac9b12092`. No source anchors were required.

Build qualification: Jekyll 4.4.1 generated a disposable site outside the repository, with disk cache disabled and research review files excluded. Its local responsive-image dependency rmagick is missing, so that unrelated plugin alone was omitted in temporary build options. Production configuration and layouts were not edited. The source-specific reader, XML, CSS, fonts and other installed plugins were used. Browser observation hooks were injected in memory only; baseline screenshots use the base registry over the otherwise identical disposable build.

The unchanged site chrome shows a pale title surface with low-contrast title text in dark mode, also visible before integration. The new contents panes pass contrast checks. This pre-existing chrome issue is outside the authorized data-only change and remains untouched.

Deferred editorial issue: the existing Greek V `[στιγμα]` encoding remains unchanged and separately documented in DEFERRED_BOOK_V.md. No outstanding source decision blocks these nine lists. Initial test-harness assertions were corrected to allow Book I’s approved paratext rubric and to open collapsed settings before interacting with pane controls; diagnostic outputs were retained. No production repair was necessary.

Reproduction: run validate.py and integrity.py with the bundled Python/lxml; build_disposable.rb with Jekyll into a temporary destination; prepare_browser.py then built-site.test.cjs for real-build TOC tests. Run regression.test.cjs normally and with --alignment-all-gate, --followup-gate, --multispan-gate, --protected-source-gate; bamberg-regression.test.cjs and interaction-regression.test.cjs provide the remaining checks. Scripts write only this new review directory and disposable build. implement.py is the original clean-worktree copy/insertion operation, not an in-place retranscription tool. certify.py collects successfully executed results and refreshes this review manifest.
