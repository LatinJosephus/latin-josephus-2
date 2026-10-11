# Antiquities VII.1 Whiston repair: canonical integration certification

PASS for the explicitly accepted VII.1 canonical integration. The full first Whiston paragraph appears exactly once, retaining the notice “English context: exact Niese-level segmentation is unavailable for this source.” All 7,376 supported Niese identities pass fresh integrated-build comparison. VII.1 English is the sole content change; all Latin/Greek content and 7,375 other selections are unchanged. Five previously existing direct-view English context gaps in VII.2-6 remain, with their separate issue register and future-publication recommendation.

## Verified references and preserved history

- Canonical and directly fetched `origin/v2-development` at integration start: `cf4cdb90e5fbcefbd0f2606d551d6a05100fd545`. No v2-development drift from the reported baseline.
- Certified branch `fix/antiquities-vii1-whiston-context`: `b48e8778b6ece616775d59a8e8949199c3ee84ef`. Its implementation parent `ac3ae682f6b84c652f0cadb4c072d242b0aea602` and complete source history remain intact.
- Isolated history-preserving merge: `7dc8a633d76bff08f2d79b54bb04bc6e98d7918a`. First parent is canonical start; second parent is the exact certified source commit. Its entire Git tree equals the certified tree.
- Integration branch: `integrate/antiquities-vii1-whiston-context-20261010` in `C:\workspace\LatinJosephus-antiquities-vii1-whiston-context-integration`.
- Origin fetch/push URLs independently verified as canonical `https://github.com/LatinJosephus/latin-josephus-2.git`; not the preview repository. Remote default HEAD at start is master `9b16913bf1739eb740b0c7ce6732c0a47c87f1c3`, separately recorded from v2-development.
- Preview checkout and frozen handoff: `e846e84bc0cd9392b504f5a60f43870084e85403`. Its public release marker still attributes canonical `cf4cdb90e5fbcefbd0f2606d551d6a05100fd545`. No preview integration, push, deployment, release-marker edit, domain or settings change is authorized or performed.

This tracked report records certification before promotion. A review-only evidence commit follows the tested merge; excluded review files cannot affect the production build. The exact final canonical commit, directly verified remote branch, clean worktrees and post-push receipt are recorded in `C:\workspace\Antiquities-VII1-Whiston-Integration-runtime-20261010/INTEGRATION_RECEIPT.json` and the final report alongside it, avoiding recursive self-commit attribution.

## Actual integrated-build QA

The native Jekyll builder generated fresh canonical-baseline and integrated sites in a new runtime, with independent browser profiles, local ports, downloads and disabled disk cache. Neither frozen source nor preview checkout was used as an output destination. Browser observations check settled reader DOM/text, selected identity, fragment IDs, notices and duplicates rather than HTTP status alone. Existing responsive-image plugin exclusion matches the certified native builder; this task does not certify a preview deployment pipeline.

| Suite | Result |
|---|---|
| Fresh baseline and integrated Niese actual UI selection runs | 7,376 each; no browser/network errors |
| Proem / Antiquities I-XX | 26 / 7,350; identical menus and book endpoints |
| Full source-neutral DOM/text/fragment/notice comparison | Only VII.1 contextual English differs; all Latin/Greek equal |
| Traditional views | 1,689 unchanged |
| Bamberg views | 198 unchanged |
| Alignment views | 1,441 unchanged |
| Book / Contents | All 21 book contexts unchanged |
| Cross-work source configurations | 21; Bellum/Cardwell/Lodge/Whiston, DEH, Contra Apionem |
| Cross-work Niese and chapter/unit projections | 8,002 and 1,630 unchanged |
| Focused navigation/pane/theme checks | 19 passed; direct, reload, back/forward, previous/next, VI-VII-VIII transitions, desktop/mobile light/dark |
| Actual containing controls | 16 passed; supported views and reloads |
| Guard fixtures | 8 passed; disposable DOM only |
| Explicit exceptional controls | 77 unchanged snapshots; no XX.269 menu identity |

Exhaustive Niese and focused positive/UI tests run the actual uninstrumented renderer. Exhaustive structural and cross-work projections use getter exports and isolated selection-state assignment in a disposable test server; selection functions are not changed. Both baseline and integrated receive identical hooks. Actual containing controls and reloads additionally verify the uninstrumented UI. `evidence/QA_PROVENANCE.json` documents scope and inherited harness metadata precisely; it does not count projection calls as live Niese clicks.

### VII.1 and combined interval

The positive test compares the full `english-book07-num1` paragraph with its frozen XML transcription, asserts one occurrence, correct English pane, contextual type and unchanged qualification, and excludes neighbouring paragraphs/duplicate English IDs. Latin begins `Praedictum itaque praelium`; Greek begins `Συνέβη δὲ ταύτην`; both complete selected fragment DOM/text hashes match fresh canonical baseline. The original unsuffixed Latin source ID remains unchanged.

Direct route: `/antiquities/?book=7&niese=1`. Containing routes include Book VII, `/antiquities/?book=7&chapter=1` and `/antiquities/?book=7&chapter=1&subchapter=1`. The last route is the supported traditional VII.i.1 combined interval 1-6, verified from existing registry endpoints and Latin milestones. Complete English appears exactly once in each containing view. The reader accepts one positive integer Niese parameter; no unsupported `niese=1-6` URL was invented. Existing first/last Alignment units remain unchanged; Bamberg is unavailable for VII in the current supported controls, and supported XX Bamberg controls were verified instead.

### Exceptional cases and preserved baseline issues

The all-identity comparison protects every existing XI transposition/interpolation, XVI-XIX displacement/unavailability and XX exclusive-end/unavailability state. `evidence/EXCEPTION_PROTECTION.json` explicitly indexes 77 controls: Proem 1/24-26; XI 302/311-313/325-327/341-343/347; XVI 294-295/350-356; XVII 24-25/75-76/299; XVIII 7/94/215-218/257; XIX 188/292; XX unavailable 27-36/238, partial 26/37, book limits, physical boundary numbers, final qualification and 268. Every language DOM/text, fragment ID and notice equals the independently rerun frozen baseline. This verifies preservation of editorial decisions, not a fresh scholarly adjudication or facsimile inspection.

Inherited duplicate `annotations` states match baseline for all selections. Unsupported I.1, inherited Book-I apparatus targets, Home/About/Background startup findings and unnamed theme markup are unchanged and remain outside this task. They are neither repaired nor newly waived. Fresh supported-reader tests have no errors; unsupported/startup/apparatus routes are not covered by that assertion. The accepted source branch's original audit/provenance records remain intact.

## Production change and source integrity

Exactly one production file changes: `assets/js/renderTei.js`, 15 added lines and one replacement. The accepted guarded first-paragraph contextual fallback is preserved exactly, without extension to VII.2-6.

| File | SHA-256 |
|---|---|
| Baseline renderer | `665f31b0a5cfe668692490c1c1ffece09097ca4cfa69ff0e516e862e56ce2d72` |
| Integrated renderer | `a29b150a95037a6e59daa8be8d65394ed245d663d51ccb64f204e4bb696ca89d` |

All 143 scholarly XML files and 14 Niese registry files have identical pinned Git blobs and identical certified/integration checkout bytes. All certified tracked files, including the original review certificate, remain unchanged. Structure, notices, divisions, original IDs, sameAs, punctuation and text remain intact. Full evidence manifests are in `SOURCE_INTEGRITY.json`, `BUILD_ASSET_HASHES.json` and `CHANGED_FILES.json`.

Canonical has legacy CRLF checkouts for 95 unchanged inputs, including 53 XML files; fresh certified/integration checkouts use the pinned LF blobs. This is a checkout representation difference, not an edit in either repair or integration. Every original canonical byte hash was independently rechecked during QA; canonical source originals remain untouched. No line-ending normalization was performed. Initial raw cross-checkout equality failed on these differences; a subsequent manifest-key typo was corrected. Both checker attempts and the final Git-blob/byte comparison are documented; no product code was changed to make the checker pass. Committed build log copies trim trailing whitespace only; raw logs and complete route JSON remain in the separate runtime.

## VII.2-6 and publication significance

See `VII2_6_ISSUE_REGISTER.md`, `.csv` and `.json` for five individual dispositions. Underlying English is present as one shared first Whiston paragraph, but direct Niese 2-6 shows only the generic contextual notice. Book VII, Chapter I and VII.i.1 display the paragraph completely once. Getter proof shows the unsuffixed Latin parent ID and the English sameAs target mismatch; accepted fallback deliberately applies only to Niese 1. These are source-available renderer context omissions alongside the acknowledged segmentation limitation, not invented missing English or established true source correspondence differences.

They do not block this accepted canonical integration. Recommend resolving them under separate editorial authorization, or explicitly accepting a documented release exception, before a next public-preview release described as final and complete in contextual English. No extension, XML repair or deployment is included.

## Promotion boundary

After clean-state and fresh remote-drift checks, promotion is authorized only by fast-forwarding canonical to the certified integration history, normal-pushing `origin/v2-development`, fetching again and directly reading the remote branch ref. No force push, destructive reset, unrelated cleanup or preview deployment. The post-push runtime receipt supplies exact resulting commits and clean states.
