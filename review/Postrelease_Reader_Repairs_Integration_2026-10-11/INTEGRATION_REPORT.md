# Canonical integration: approved reader repairs A/B/D/E

Combined certification **PASS**, with zero new regressions. A, B, D and E are repaired. Package C is **KNOWN UNRESOLVED / EDITORIAL HOLD**, not repaired or counted as passed. Public preview publication is outside this integration.

Starting canonical/local/fetched/direct remote: `4ffbc79b84806d180e9d713f9605255e7dfed73e`. Certified source `e4005026370a2ff6ca0cf135ea5718f348db814c` was clean and independently checked against its evidence and production manifest. Actual history-preserving merge: `31785248f94432824aedfc6ba0d573f63f6f902a`; parents `ef8ede95cc19643fa0b2d2dee3ceecbe28d710d6` and `e4005026370a2ff6ca0cf135ea5718f348db814c`. No conflicts, conflict resolutions or extra production changes. The complete source history, including its baseline, implementation, editorial hold and certification commits, is preserved. VII.1 (`b48e8778b6ece616775d59a8e8949199c3ee84ef`) and VII.2–6 (`0f006764c36b36bc0cf856f6c3b11f2e4a03660c`) remain ancestors. See ANCESTRY.txt and MERGE.json. This evidence-only certification commit does not change the tested production build. Final canonical, fetched and directly verified remote commit and normal push output are sealed after promotion in `C:\workspace\Postrelease-Reader-Repairs-Integration-runtime-20261011\INTEGRATION_RECEIPT.json`.

| Package | Actual merged-reader disposition |
|---|---|
| A | PASS: named native Dark mode button, keyboard focus and Enter/Space, actual pressed state, persistence, desktop/mobile light and dark rendering (18 assertions). |
| B | PASS: unique visible `reader-annotations`, correct selectors/MDB disclosure; unchanged original TEI `annotations`, notes, highlighting and pane content. All sampled Antiquities views have unique document IDs. |
| C | KNOWN UNRESOLVED, editorial HOLD: original 3 links and 2 malformed 404 targets independently reproduced and unchanged; no guessed targets, substitute annotations or XML edits. Literal original unresolved-reference register retained. |
| D | PASS: Home, About, Background startup and actual navigation; original baseline languages TypeErrors independently reproduced, absent after integration, body content identical. |
| E | PASS: 21 positive/negative/transition assertions; invalid URLs remain invalid and unchanged, accessible explanatory notices, real Proem 1/I.27 links, no substituted passage. Supported corpus unchanged. |

Fresh native Jekyll builds were made for frozen canonical and merged source. No old generated build was copied; dependencies were not upgraded. The established image-plugin policy and loopback configuration were retained. Chrome used independent profiles, ports and downloads. All 251 integrated asset hashes match the certified source build, including renderer `e75244c444771c733ca8ddb0d130b8f32463f59fd9460c26a5048b3669727322`. Source and build digests are in PRODUCTION_MANIFEST.json. The exact eight-file source delta is PRODUCTION.diff; there were no preview release-marker, CNAME, domain or publication changes.

The first evidence-sealing attempt stopped on a manifest field-name mismatch (`status` versus the actual `result` field). This orchestration-only error was corrected and retained in ORCHESTRATION_ATTEMPTS.json. It occurred after the successful browser suites and before any canonical promotion; no production change or rerun of passing browser tests was required.

| Fresh combined regression | Result |
|---|---|
| Antiquities Niese | 7,376/7,376 (26 Proem + 7,350 I–XX), before/after; all 22,128 complete language-pane DOM/text/IDs/type/notice comparisons identical; no errors or duplicate IDs. |
| Traditional extent equivalents | 1,689/1,689 |
| Bamberg extent equivalents | 198/198 |
| Alignment extent equivalents | 1,441/1,441 |
| Book / contents configurations | 21/21 |
| Cross-work Niese | 8,002/8,002 |
| Cross-work structural | 1,630/1,630 |
| Actual containing-view controls / document IDs | 16/16 each, separately executed UI tests |
| Source preservation | 143 XML and 159 protected XML/data/registry inputs exact; 5,158/5,166 baseline files unchanged, eight approved production files changed. |

The exhaustive Niese replay is uninstrumented and uses real menu selections and real URL identities. Structural and cross-work suites exercise the actual production selector/extent/rendering code with getter-only access and complete source input, comparing DOM/text with the independently built baseline; these totals are not represented as individual public browser clicks. Separate uninstrumented tests cover real direct/reload/back/forward/previous/next, keyboard, pane/source switching, note disclosure, themes and containing views.

Positive full-source Whiston assertions pass for VII.1–7 and internal composites VII.1–6/VII.2–6, including reordered/repeated identities and adjacent distinct paragraphs. Existing wording, punctuation, source IDs and qualifications are preserved; each physical paragraph appears once within a selection. VII.5–6 retain the complete sentence-spanning paragraph. Whiston remains contextual, not word-exact Niese segmentation. No new public range URL or public range control is claimed.

Protected cases pass: all 26 Proem identities, repeated §25/26 and transition I.27; XI.312/.326/.342 logical fragments and Bellum IV.105 attachments with Book/Alignment physical order protected by exact structural comparison; XVI–XVII fragments and reciprocal qualifications; XVIII.216–217 Greek/context with explicit Latin unavailability; XX.27–36/238, final §268 separate full trailer through AMEN, no Vita and no supported §269. Bellum/Cardwell/Whiston/Lodge, DEH and Contra Apionem panes and source switching are preserved. See PROTECTED_CONTROLS.json and the complete pane-comparison matrix.

Only specific independently reproduced residuals remain: Package C at `/antiquities/?book=1&bamberg=5` (three original links, two unchanged 404 targets) and the Bellum Book-I source-source `header` ID collision at `/bellum-judaicum/?book=1`. Before integration Bellum duplicates were `annotations` and `header`; after, only the inherited `header` remains. This is not a claim of global duplicate-ID freedom for every work. Fresh supported-selection/general-page/navigation suites have zero new page, console or network errors; deliberate visits to the two C 404 destinations are recorded separately. No blanket baseline error waiver is applied.

Exact production hashes (Git bytes and isolated working/build bytes verified):

| Production source file | SHA-256 |
|---|---|
| _includes/annotations-bar.html | `f5f6f314a497369e2ee943ae87e0df0c8c123c9f844b49b77bc77355b17556c8` |
| _includes/header.html | `3268ce45d5e4752a7365686c09cec694b56942bc0a44420c142db09a77d99b52` |
| _sass/_antiquities.scss | `743bf696e2f6d0a89a413c325f3f77879d58d560f5c2435d714dc1ece72a9fc3` |
| _sass/_branding.scss | `002bacd85616620a1bcc987308e65d3fe52dd7147c0334b3c82bf55d4fc0ae08` |
| _sass/_reader-ui.scss | `aa2144eb17023033a5f8051e46b8c7506fd507c4521a5f4b02d92c3df138f3ab` |
| assets/js/dark_mode.js | `7f8cb70ed5198033a0c0daa938d7e8dcc044776eb5137d4098e0661ebc889b86` |
| assets/js/renderTei.js | `e75244c444771c733ca8ddb0d130b8f32463f59fd9460c26a5048b3669727322` |
| assets/js/theme.js | `281771146ce240bdf69520decbac713d2aefbf8a1b23e58ca6444bc49c12e982` |

Recommend canonical promotion of A/B/D/E. Package C requires independent apparatus recovery and editorial authorization, and is not a blocker to these authorized maintenance fixes. The public preview remains `afea19c25456c4476c37e4ce7164a2b8ed3b61c8`; publishing these repairs requires a separate publication task. Final promotion/ref/cleanliness checks are recorded in the external integration receipt.
