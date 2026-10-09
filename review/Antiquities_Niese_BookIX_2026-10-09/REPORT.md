# Antiquities IX — completed local handoff

Status: **COMPLETE, locally certified and ready for coordinated integration**. The user explicitly resolved §240 as A. No editorial decisions remain. No merge, push, preview update or deployment occurred.

The frozen base is `ad3158b7a86dea6997510b3de17f2e510c23367c`. Canonical initial HEAD was `ad3158b7a86dea6997510b3de17f2e510c23367c`; latest recorded HEAD is `ad3158b7a86dea6997510b3de17f2e510c23367c`. Later advance: none. Canonical working tree: clean. The frozen inputs were not replaced by later canonical code. Branch `antiquities-niese-09` is at `C:\workspace\LatinJosephus-antiquities-niese-09`. Review evidence is `C:\workspace\LatinJosephus-antiquities-niese-09\review\Antiquities_Niese_BookIX_2026-10-09`; disposable builds, logs and isolated browser profiles are `C:\workspace\Antiquities-Niese-09-runtime-20261009`. Final QA origin: `http://127.0.0.1:8909`. Full final implementation build: `668ed06cfce878cbced07381e35851d0ffcaf662`.

## Boundary authority and arithmetic

Niese II's independently examined opening and ending establish §§1–291. All 291 printed starts and 232 surviving Latin candidates were individually reviewed. The three supplied XML witnesses omit §§51–109 behind preserved editorial placeholders, giving 59 explicit unavailable identities. This is an omission in these files; neither a physical cause nor absence across the whole Latin tradition is inferred. IX.110 preserves only Jehu's concluding reply and has a qualified partial-survival notice.

The final arithmetic is **232 represented Latin intervals = 46 retained starts + 186 new milestones**; **291 identities = 232 represented Latin intervals + 59 unavailable identities (§§51–109)**. All 232 physical starts render nonempty Latin intervals. No IX inherited visible label requires executable suppression. Published coverage remains 3,157; local IX adds 291 selectable identities, giving 3,448 local selections. The 232 Latin intervals are counted separately.

The explicit Greek marker edit list is: add implicit opening `[1]`; relocate §181 before `τρία βέλη`; relocate §216 before `τὸν αὐτὸν δὲ τρόπον`; relocate §240 before `ἔσται δ᾽`. The first two relocations were independently verified in print/control. The §240 relocation is an **explicit editorial resolution of the word-level ambiguity in the printed numeral's placement**, paired with Latin before `et nullus`. Niese printed page 317/PDF page 325 and Loeb Greek printed page 126/PDF page 142 identify a line containing both possible clause starts; neither unambiguously fixes the word cut at ἔσται. DECISION_240.md preserves the observed line, both images and alternatives. The inherited Greek cut at `σώζειν γὰρ`, paired with Latin `dum animas suas`, remains rejected alternative B in the history.

The exact frozen packet locators for A govern both marker operations. FINAL_BOUNDARY_239_241.json/.md records recomputed neighbouring extents and frozen/final Unicode and raw-byte locators. Only §§239 and 240 change extent from the preceding provisional review. §241 and every other boundary are unchanged. §§239–241 form the identical frozen narrative span without loss or duplication.

## Preservation and scope

Exact inversion removes the 186 added Latin milestones and reverses only opening 1 and Greek relocations 181, 216 and 240. It recovers the same frozen worktree bytes and SHA-256 hashes used by the locators. Original words, punctuation, whitespace, markup, apparatus, IDs, sameAs, paragraph numbering, inherited visible labels and traditional/Bamberg divisions are preserved. English source bytes and every other book are unchanged. The final subscription `explicit liber nonus` remains in the XML and terminal display, with its 20 code points separately excluded from the narrative coordinate stream. No XML-wide normalization or reserialization is used.

Only four production paths differ from the frozen base: Greek IX XML, Latin IX XML, IX identity JSON and the minimal shared reader support. SHARED_SUPPORT.md explains the IX registry and two opt-in data behaviors; its code was committed separately. display-settings.html and all other production files are unchanged. Integration must reconcile this frozen branch with then-current canonical code.

## Final reader certification

A fresh full Jekyll build of final implementation `668ed06cfce878cbced07381e35851d0ffcaf662` and the archived frozen baseline both exited 0. The final build uses no static refresh. Every served changed asset matches final worktree bytes. BUILD_RECORD.json preserves executable identities, build provenance, logs and hashes.

The post-decision NEW_BOOK_BROWSER_QA.json passes all 291 actual IX selector events, exact Greek/Latin extents, Whiston broader context, 59 unavailable selections, complete narrative partition, final extent, IDs and pane links. All 14 chapter and 54 subchapter events match complete pinned range projections. Chapter XI (`LOEB-09-Chapter-11-0`) and subchapter XI.3 (`LOEB-09-Subchapter-11-3`) each contain the complete resulting §§239–241 Greek and Latin intervals. Actual production selections 239, 240 and 241 and their screenshots were independently inspected after the final decision.

Deep links, previous/next, reload/history, pane/language switching and light/dark behavior pass. Unmodified production code was checked at openings, omission edges, 110, 181, 216, 239–241 and 291. The final gate reruns all four accepted inherited-label exceptions, VIII.367–369 and X.101–102, 108–109, 150–151, 276–277. X.108 Greek/English remain independently accessible. Lodge note toggling, witness switching and reload also pass. Final IX QA has zero unexpected script, console or network diagnostics.

## Earlier evidence preceding the final decision

`qa-history/pre-decision-5794785` preserves the original provisional registers, reports, build logs and QA with hashes. Earlier broad protected results precede the final §240 decision: 3157 existing Niese selections, 1689 traditional ranges, 198 Bamberg ranges, 1441 Alignment units, source contents across preface/I–XX, 14 cross-work books and 9646 Bellum Whiston/Lodge range comparisons. They are retained evidence, not claimed as newly rerun. PROTECTED_EVIDENCE_APPLICABILITY.json verifies that the shared reader, protected sources and configuration are unchanged since that checkpoint; only IX Greek/Latin XML and identity data changed. The final gate retests all affected IX selections/ranges and accepted VIII/X controls.

INHERITED_ISSUES_QA.json precisely records the documented Book-I Bamberg route's three apparatus hyperlinks/two malformed targets and unsupported I.1 error, with supported I.27 verified. No additional errors are excused by those inherited exceptions. Historical sandbox loopback denial and corrected harness assumptions remain recorded separately from passing reader evidence.

## Scoped local commits

- `e227d0400285c75ac24f45e1bd27fa559efa6e28` Freeze Antiquities IX inputs and printed source authority
- `5ef8e902d3749dfbaf3ca5c9a0cbf3cb076d05e7` Review all IX boundaries and record pending section 240 choice
- `f8d5694bc4bb70076bcd95589991787335562bc7` Add IX opening identity and verify Greek cuts at 181 and 216
- `15e185d72de249750d14e7ca8d758742fffd63c5` Reuse Niese reader support for IX language availability
- `ed61ef79cfa19a238ab16e89a99e5795d4224769` Implement resolved IX Latin milestones with provisional 239-240 boundary
- `570beaa755a0367149994e8b2e6cc9e50515f627` Record IX correspondence limits and terminal-label narrative exclusion
- `5794785c61beb6fee7e7fade6275092c42ddef77` Certify independent IX reader work and preserve pending 240 handoff
- `a68859cf3de2d03ece2b56b78d74b59d9dbdca9a` Adjudicate IX 240 at the refusal clause and preserve rejected cut B
- `4a5399058ce240a52fe58e3af877b7e5194c0030` Relocate Greek IX 240 to the explicitly adjudicated word boundary
- `668ed06cfce878cbced07381e35851d0ffcaf662` Complete IX Latin segmentation with milestone 240 and closed availability

The final certification commit follows these implementation commits. Its hash and clean status are reported in the handoff response, avoiding a self-referential ID inside its own committed file. FILE_MANIFEST.json contains exact changed paths and frozen-input, served-asset and review-file hashes; it excludes itself from self-hashing.
