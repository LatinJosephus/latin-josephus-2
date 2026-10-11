# Post-release reader repair certificate

**A/B/D/E: PASS, locally certified. C: EDITORIAL HOLD, not repaired and not passed.** The user's explicit hold preserves the three original apparatus references and permits independent completion of the other packages. This is not a five-defect completion certificate.

| Package | Outcome | Final action |
|---|---|---|
| A | PASS | Native `Dark mode` button; Enter/Space, keyboard focus, real role/name/pressed state and existing persistence. |
| B | PASS | UI panel `reader-annotations`; selectors and MDB parent updated; original TEI IDs, notes and source order unchanged. |
| C | EDITORIAL HOLD | Missing UUID targets retained without invented mapping; permanent unresolved-reference register. |
| D | PASS | Shared reader initializes only where its work data and reader controls exist; general-page content and navigation preserved. |
| E | PASS | Registry-derived invalid Niese validation before selection/annotations; typed URL retained, no text substituted, real Proem 1/I.27 links. |

## Baseline and isolated branch

Canonical and directly verified remote: `4ffbc79b84806d180e9d713f9605255e7dfed73e`. Public preview: `afea19c25456c4476c37e4ce7164a2b8ed3b61c8`. Canonical renderer was `c4741903c21c4cc0e4629cdca4d951a5c64ffcab6da5e44e40aaaebcc0e3cad3`.

Branch: `fix/postrelease-reader-a11y-ids-links-startup-20261011`. Worktree: `C:\workspace\LatinJosephus-postrelease-reader-repairs-20261011`. Tested implementation tip: `951555f41c4fda1e21f7615b4a125f7036b3b55f`. An evidence-only certification commit follows; its exact final HEAD, clean status and report hashes are in `C:\workspace\LatinJosephus-postrelease-reader-repairs-runtime-20261011/HANDOFF_RECEIPT.json`.

Actual Git ancestry retains the certified VII.1 (`b48e8778b6ece616775d59a8e8949199c3ee84ef`) and VII.2–6 (`0f006764c36b36bc0cf856f6c3b11f2e4a03660c`) repairs. A/B/D/E have separate code commits; C has a separate evidence-only hold commit. CERTIFICATE.json lists exact commit ancestry.

## Fresh actual-build certification

- **7,376/7,376 actual Niese selections:** 26 Proem and 7,350 Books I–XX. Exact pane DOM, meaningful text hashes, original IDs, type and qualification arrays match a newly captured unmodified canonical baseline for every selection. All menus and book endpoints match. Zero selected-view duplicate IDs and zero console/network failures.
- **1,689 traditional, 198 Bamberg, 1,441 Alignment views:** exhaustive production selector/extent comparisons using getter-only harness exports, all exact; plus unmodified actual Book/containing-view navigation, direct links and reloads. 21 Book/contents configurations also match. This is a complete equivalent structural harness, not a claim of thousands of UI clicks.
- **8,002 cross-work Niese and 1,630 structural ranges:** exact production-renderer output comparisons in 21 work/book/witness configurations. Bellum/Cardwell/Greek, Whiston/Lodge controls and notes, DEH and Contra Apionem remain protected.
- VII.1–7: existing full Whiston source paragraphs exactly once; original wording/paragraph IDs/sameAs and contextual qualification. Four internal composite tests include VII.1–6, VII.2–6, repeated/nonsequential identity inputs, and VII.6–7. Adjacent physical English paragraphs remain separate. No public range UI or URL was introduced; Whiston remains contextual, not precise Niese segmentation.
- Positive protected checks include Proem25/26/I.27 transitions, XI312/326/342 and their two Bellum IV.105 attachments, XVI–XVII fragment boundaries, XVIII216–217, XX27–36/238, the complete XX268 AMEN trailer and Vita exclusion. Themes, pane/witness switching, note controls, keyboard, previous/next, reload and history passed.
- A: three pages/works, desktop and 390px mobile in both themes; Chrome accessibility tree, actual Tab/Enter/Space, focus outline and cross-navigation/reload persistence. General pages retain their exact baseline visible text and actual navbar navigation into/from readers.
- E: I.1, XX269, unsupported Proem27, malformed/empty/zero/negative/oversized Niese requests and unknown books retain their invalid URLs, show an accurate alert and no fabricated passage. Supported links, menus, reload and history remain accurate.

No production code changed after the frozen tested build. The rendered JS SHA-256 is `e75244c444771c733ca8ddb0d130b8f32463f59fd9460c26a5048b3669727322`. CHANGED_FILES.json records all eight source production hashes and all 251 built-asset hashes.

## Preservation and remaining issues

All **143 scholarly XML files** and **159 protected XML/data/registry inputs** are byte-identical in source and tested build. The entire 5,166-file frozen tracked manifest was checked: 5,158 original files unchanged; exactly eight production source files changed. No translations, Niese/division boundaries, source identifiers, source order, release marker, CNAME or configuration changed.

Package C still reproduces at [Book I, Bamberg 5](https://latinjosephus.github.io/antiquities/?book=1&bamberg=5): three links and two distinct malformed 404 destinations. The three target UUIDs are absent from all current scholarly XML and the searched locally available Git history under assets/xml. Exact source line/column, original markup, surviving candidate notes, search scope and limits are in UNRESOLVED_REFERENCES.json/.md. No fresh facsimile inspection or secure note mapping is claimed. Authoritative mapping evidence must precede a focused editorial approval packet.

An additional inherited Bellum Book-I `header` collision was independently observed in both baseline and final: Latin and English TEI headers share the original ID. It is unchanged and outside this repair's five packages. Thus the certificate does not claim globally unique document IDs for every pre-existing cross-work Book view. The targeted `annotations` collision is removed and all tested Antiquities selected/containing views have unique IDs.

Harness failures are preserved with their original observations/logs. They involved the newly found Bellum baseline collision, early build readiness, an assumed nonexistent main element, navbar transition timing and one wrong positive-test directory argument. Corrected real-template/path/wait checks passed without broad error suppression or extra production edits. The original focused job FAIL is retained; the corrected VII.1 source-content result is a separately documented PASS.

## Scope, reproduction and handoff

Production changes: `_includes/header.html`, `_includes/annotations-bar.html`, `_sass/_branding.scss`, `_sass/_antiquities.scss`, `_sass/_reader-ui.scss`, `assets/js/theme.js`, `assets/js/dark_mode.js`, `assets/js/renderTei.js`. Review artifacts are separately listed and hashed.

Fresh isolated Chrome profiles, loopback ports and download directories were used. The established native Ruby/Jekyll builder excludes the research archive and uses the same certified plugin policy; the builder/config and logs are included. No dependency upgrade or unsupported public route was introduced. REPRODUCE.md describes the preserved scripts and exact runtime inputs.

Review: CERTIFICATE.json, TEST_RESULTS.json, NIESE_MATRIX.csv, compressed complete captures, CHANGED_FILES.json, SOURCE_PRESERVATION.json, EVIDENCE_INDEX.md and READ_ONLY_RECEIPT.json. Compact ZIP checkpoints are integrity-indexed under `C:\workspace\LatinJosephus-postrelease-reader-repairs-runtime-20261011/checkpoints`.

**Recommendation:** review and integrate the independently certified A/B/D/E commits through a separate authorized task. Keep C on explicit editorial HOLD. Canonical and both preview checkouts/remotes are unchanged and clean; other-worker drift, if any, is recorded without touching their work. No merge, push, deployment, destructive reset or domain change was performed.
