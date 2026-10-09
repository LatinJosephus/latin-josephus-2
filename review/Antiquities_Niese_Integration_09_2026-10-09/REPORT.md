# Antiquities IX — verified canonical integration

The complete certified IX branch has been merged in isolation with current canonical and passes combined-build verification. It is ready for canonical fast-forward and the explicitly authorized normal push. Public-preview refresh and deployment are outside this assignment. The handoff response reports the final directly verified canonical and remote heads after execution.

Certified source: `b2766fc0a0f9ab8dfb1c4667fbb9c5c4d6eac659` on `antiquities-niese-09`, at `C:\workspace\LatinJosephus-antiquities-niese-09`. Source branch and working files remain unchanged and clean. Its frozen base is `ad3158b7a86dea6997510b3de17f2e510c23367c`. Actual canonical and origin before preparation were `92f009a668507ece4b82bdc4040a2b40b1f2cae7` on `v2-development`, clean. That canonical advance contains the Whiston compiled-index work; every existing canonical file except the four accepted IX production paths is preserved byte-for-byte. No other worker's branch, worktree, runtime or browser session was modified.

Integration branch: `antiquities-niese-09-integration`, at `C:\workspace\LatinJosephus-antiquities-niese-09-integration`. Review: `C:\workspace\LatinJosephus-antiquities-niese-09-integration\review\Antiquities_Niese_Integration_09_2026-10-09`. Dedicated runtime: `C:\workspace\Antiquities-Niese-09-integration-runtime-20261009`. Tested merge: `967d258bae44b591bb354b89d46b917526183656`; parents: `['df3598b3ec25edf61e215f7375c5d5dbcdbc4df0', 'b2766fc0a0f9ab8dfb1c4667fbb9c5c4d6eac659']`. The full IX history is preserved as a merge parent, rather than integrating only the final §240 change. No conflict or production reconciliation was required. Canonical can advance to this tested result and its subsequent review-only certification commit by fast-forward.

## Exact scope

The incoming delta from `ad3158b7a86dea6997510b3de17f2e510c23367c` to `b2766fc0a0f9ab8dfb1c4667fbb9c5c4d6eac659` is **4 production files + 200 review files = 204 files**. INCOMING_SCOPE.json lists each path, status, Git blob identity and certified working-byte hash. All incoming files match the certified source exactly. The 200 review files are the complete accepted IX packet, including original frozen inputs, printed images, editorial history and prior/final QA.

The four incoming production paths are:

- `assets/js/renderTei.js`
- `assets/xml/antiquities/Greek/book-09.xml`
- `assets/xml/antiquities/Latin/book-09.xml`
- `assets/xml/antiquities/niese/book-09.json`

Integration-specific additions are review-only under `review/Antiquities_Niese_Integration_09_2026-10-09`; FILE_MANIFEST.json records their exact final list, count and hashes. The checkpoint, merge and final verification commits keep review-only work distinct. Production resolutions: zero. Existing Whiston contents/CSS, English narrative sources and every other book remain as current canonical.

## Accepted boundaries and preservation

Greek opening identity1 is added, and markers181,216,240 are relocated. IX.240 begins before Greek `ἔσται δ᾽` and Latin `et nullus`. The incoming DECISION_240.md retains the shared printed line and both alternatives: A is an explicit editorial resolution of the word-level ambiguity; the inherited Greek `σώζειν γὰρ` paired with Latin `dum animas suas` remains rejected B. The printed numeral is not described as unambiguously fixing the word cut. Decisions are closed.

**232 represented Latin intervals = 46 retained starts + 186 milestones. 291 identities = 232 represented Latin intervals + 59 unavailable identities (§§51–109).** IX.110 retains its qualified surviving tail. All three supplied IX witnesses omit51–109; no physical cause or tradition-wide absence is inferred. Removing only the added Latin milestones and reversing the authorized Greek marker operations recovers the exact frozen source bytes. English source bytes are unchanged. INTEGRITY_QA.json independently repeats the inverse against the actual combined source files.

## Verification of the combined implementation

A fresh complete Jekyll build of the tested merge and a fresh archived build of actual pre-integration canonical both exited0. No repository plugin was omitted and no static refresh was used. Read-only mounts and a pinned Ruby image isolate build dependencies and output in the dedicated runtime. All incoming production output hashes equal the certified IX result. Current canonical CSS, source-contents index and Whiston IX contents output hashes also match their actual retained source bytes. BUILD_RECORD.json records build provenance, logs, executable identities and output hashes. Initial preparation failures are accurately retained in PREPARATION_DIAGNOSTICS.md and are not counted as successful certification.

Because the renderer, IX XML and identity data are identical to the certified result, its exhaustive 291-selection and 68-range certification remains applicable. Fresh focused integration QA used actual events at `[1, 50, 51, 109, 110, 180, 181, 182, 215, 216, 217, 239, 240, 241, 291]`, including opening,50/51,109/110,181,216,239–241 and ending. Deep links, previous/next, Back/Forward, reload, pane toggles, IDs and exact expected Greek/Latin/English-context extents pass. Eleven critical URLs additionally pass with unmodified production code. Screenshots at IX.240 in both themes were visually inspected.

Complete resulting239–241 Greek and Latin extents are present in ChapterXI and subchapterXI.3; each entire containing pane projection equals actual canonical with only the approved marker differences removed. Protected checks include VIII.367,VIII.369,X.108 with independently available Greek/English, actual traditional/Bamberg/Alignment routes and Bellum Whiston/Lodge views compared to the current canonical build. Current Whiston/Greek contents forVIII,IX,X match their canonical projections, with English15/14/11 entries and IX Contents→Niese→Contents roundtrip. Actual menus across all20 books confirm **3,157 +291 =3,448 selectable Antiquities Niese identities**, distinct from IX's232 represented Latin intervals and59 addressable absence states. No unexpected script, console or network diagnostics occurred in the passing final gate.

## Advance and push gate

Before advancing canonical, recheck its HEAD and clean state against the frozen actual canonical state and verify origin directly. Preserve and reconcile any intervening advance rather than resetting it. Advance with `--ff-only`, verify canonical production bytes against the tested build, push only `v2-development` normally to its existing origin, and read remote HEAD directly afterward. The certified IX source branch remains fixed at `b2766fc0a0f9ab8dfb1c4667fbb9c5c4d6eac659`. No public-preview refresh or deployment is authorized or performed.
