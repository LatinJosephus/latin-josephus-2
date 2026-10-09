# Antiquities IX — local independent-work handoff

Status: **PROVISIONAL — one editorial decision pending at IX.240**. All independent scholarly review, local implementation and technical reader work is complete. This is not a readiness declaration for integration. No merge, push, preview update or deployment occurred.

The frozen base is `ad3158b7a86dea6997510b3de17f2e510c23367c`. Canonical began at that commit and was clean; its latest recorded HEAD is `ad3158b7a86dea6997510b3de17f2e510c23367c`, with no later advance and no canonical working-file changes. The isolated branch is `antiquities-niese-09` at `C:\workspace\LatinJosephus-antiquities-niese-09`. Evidence is in `C:\workspace\LatinJosephus-antiquities-niese-09\review\Antiquities_Niese_BookIX_2026-10-09`; disposable builds, logs and browser profiles are in `C:\workspace\Antiquities-Niese-09-runtime-20261009`. Actual IX browser origin was `http://127.0.0.1:8909`; protected comparison servers used separate free ports. All browser profiles belong to this assignment.

## Coverage and implementation

Niese II's independently examined opening and ending establish1–291. All291 printed starts and all232 surviving Latin candidates were individually reviewed. The actual Greek, Latin and English XML each omit51–109 behind their preserved editorial placeholder;59 identities therefore have explicit per-witness unavailability. This establishes an omission in these files, not its physical cause or a claim about the whole Latin tradition. IX.110 preserves only Jehu's concluding reply; its partial-survival notice is visible without reconstructed wording.

The Latin plan contains46 independently verified retained visible starts and186 additional milestones.185 are applied;240 is held. There are231 physical Latin source starts, of which230 render nonempty certified intervals while239–240 remain explicitly provisional. The232 surviving candidate intervals form the reviewed complete narrative partition. These counts are separate from291 selectable IX identities. Published coverage remains3157; this local build adds291 provisional selectable identities, giving3448 local selections. It does not add291 Latin text intervals.

Greek edits are explicitly limited to opening `[1]`, move181 before `τρία βέλη`, and move216 before `τὸν αὐτὸν δὲ τρόπον`. The latter two were independently checked in Loeb. No other source words, punctuation, whitespace, notes, IDs, sameAs, paragraph numbering, source contents, traditional/Bamberg divisions or English source bytes change. IX requires no inherited-label executable override. The reader changes are the IX registry path and two opt-in generic data behaviors described in SHARED_SUPPORT.md; display-settings.html is unchanged.

Exact inversion removes only added Latin milestones and reverses the authorized Greek marker edits, recovering the same frozen working-tree bytes and SHA-256 hashes used by the locators. Greek and Latin coordinate streams exclude paratext, num labels, notes, apparatus and the exact omission placeholders. The terminal `explicit liber nonus` remains in the source/display extent but is separately excluded as a subscription label. No XML-wide normalization or reserialization is used.

## Actual reader evidence

NEW_BOOK_BROWSER_QA.json records all291 real selector events, exact Greek/Latin extents, Whiston broader context, every unavailable/pending state, no duplicate executable or DOM IDs, and no unresolved IX pane links. Actual Chapter/Subchapter events cover14 chapters and54 subchapters, compared to the pinned complete baseline range projections. The inherited traditional unavailability is preserved rather than hidden. Deep links, previous/next endpoints, history, reload, English/Greek pane switching, mandatory Latin-pane behavior, and light/dark theme application pass. Production code was independently exercised at openings, omission edges,110,181,216,239–240 and291. The two110 screenshots were visually inspected: notices, text, controls and brand images render correctly in both themes.

Protected comparisons preserve3157 existing Antiquities Niese selections, all1689 traditional ranges,198 Bamberg ranges,1441 Alignment units and source contents across the preface/I–XX. Greek/Latin marker differences are stripped solely for comparison of authorized IX/VIII/X edits; all other source behavior and order remains unchanged. Cross-work checks cover14 books of Bellum, Contra Apionem and DEH. The separate Bellum gate compares9646 Whiston/Lodge book, Niese, chapter and Alignment ranges. Lodge note toggling, source switching and reload pass.

Accepted controls include all four inherited-label exceptions, VIII.367–369 and X.101–102,108–109,150–151,276–277. Greek/English remain independently available at X.108. INHERITED_ISSUES_QA.json precisely reproduces only the documented three apparatus links/two malformed Book-I targets and unsupported I.1 error, and verifies supported I.27. Passing gates report zero unexpected script, console or network diagnostics. Early sandbox loopback denial and two corrected harness assumptions are retained as historical attempts, not classified as reader defects. Local SVG MIME serving was corrected during screenshot QA; no production image change was needed.

## Decision required and closure path

DECISION_240.md links Niese printed317/PDF325 and Loeb printed126/PDF142. Each numeral identifies a line shared by two plausible clause starts. **A, recommended:** Greek240 before `ἔσται δ᾽ οὐδεὶς βουλησόμενος`, Latin before `et nullus hanc uoluntatem habebit`, keeping refusal and explanation together. **B:** retain Greek before `σώζειν γὰρ`, Latin before `dum animas suas`, assigning the refusal to239. Both exact alternatives, raw-byte/Unicode locators and239/240 extents are in DECISION_240_ALTERNATIVES.json. No user decision has been received.

After adjudication, record the user's choice in EDITORIAL_DECISIONS.json, rebuild the register, apply the remaining Latin milestone and the Greek240 move only if A is chosen, clear the temporary239–240 notices, and rerun the affected reader/preservation checks. Then commit the adjudication, final corpus operation and certification separately. The existing independent-work evidence remains valid; integration must still reconcile this frozen branch with then-current canonical.

## Scoped local commits so far

- `e227d0400285c75ac24f45e1bd27fa559efa6e28` Freeze Antiquities IX inputs and printed source authority
- `5ef8e902d3749dfbaf3ca5c9a0cbf3cb076d05e7` Review all IX boundaries and record pending section 240 choice
- `f8d5694bc4bb70076bcd95589991787335562bc7` Add IX opening identity and verify Greek cuts at 181 and 216
- `15e185d72de249750d14e7ca8d758742fffd63c5` Reuse Niese reader support for IX language availability
- `ed61ef79cfa19a238ab16e89a99e5795d4224769` Implement resolved IX Latin milestones with provisional 239-240 boundary
- `570beaa755a0367149994e8b2e6cc9e50515f627` Record IX correspondence limits and terminal-label narrative exclusion

The per-book QA/evidence commit follows these implementation commits. Its final hash and clean status are reported in the handoff response, avoiding a self-referential commit ID inside its own committed file. FILE_MANIFEST.json contains exact changed paths, frozen-input hashes, served-asset hashes and review-file hashes; the manifest excludes itself from self-hashing.
