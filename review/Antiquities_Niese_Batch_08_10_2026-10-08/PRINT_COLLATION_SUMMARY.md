# VIII / X printed-collation addendum

**Both books remain NO-GO. No Greek or Latin changes, reader enablement or certification.**

The authorized candidate checkpoint was committed in three independent audit-only commits:

- VIII: `cc86a1d3ef3626a04b44032b9c8fc60293a44bff`
- X: `da28ec5abd7084fe5199549e2e38488171505c0e`
- Shared batch: `39c9b60803f38806872a9c0a6a905c92ffa03d3e`

All 153 Niese body pages were visually examined, covering 420 VIII starts and 281 X starts. Full page images and precise page references accompany every row. OCR was used only to find passages; PDF242 in VIII has no useful body OCR and was collated directly from its image. X281 begins at the final word ἐγὼ on PDF399 and continues PDF400.

The explicit XML label deficits are VIII.1 and X.1: both openings already have printed first-citation identities, established by the opening and running-head ranges. The unapplied proposal would represent those existing identities. Niese’s separate VIII.376/377 numeral anomaly is documented against independent Loeb control.

Recommended paired Greek/Latin relocations: VIII.59, VIII.245, VIII.353, VIII.409, X.33. Earlier candidates and neighbouring extents remain in DECISION_HISTORY.json; proposed alternatives never replace the frozen source. Word-precision obstacles remain at VIII.110 (Niese p.200/PDF208; Loeb p.630/PDF638), VIII.172 (Niese p.214/PDF222; Loeb p.662/PDF670), and VIII.368 (Niese p.256/PDF264; Loeb Greek p.768/PDF776 and English p.769/PDF777). The last affects partial survival versus unavailability at 367. No scan is unread or inaccessible. VIII.83 also has a reassessed earlier Latin dimensional counterpart.

## Independent book states

| Book | Routine print records | Named human decision records | Historical EXACT / internal / uncertain / unavailable | Applied milestones / Greek repairs |
|---|---:|---:|---|---|
| 8 | 420 | 18 | 81 / 1 / 337 / 1 | 0 / 0 |
| 10 | 281 | 11 | 46 / 1 / 233 / 1 | 0 / 0 |

The named editorial decisions are separate from routine Latin candidates still awaiting individual verification. No confidence classification was promoted by the Greek image pass. Read each book’s REVIEW_CASES.md for decisions, Greek/Latin cut contexts, mixed-content byte locators, alternatives and linked image evidence.

[Book VIII editorial packet](../Antiquities_Niese_BookVIII_2026-10-08/REVIEW_CASES.md) · [Book X editorial packet](../Antiquities_Niese_BookX_2026-10-08/REVIEW_CASES.md). Placement/classification and placement/confidence cross-tabulations are in both packets and CONFIDENCE_CROSSTAB.json.

## Integrity and existing systems

All six Greek/Latin/English input and output hashes remain unchanged; before/after values are in each BASELINE.json and the follow-up verification. The source PDFs and frozen research packets remain unchanged. Existing source provenance limitations are preserved. No renderer, availability registry, TOC, other book or other work changed. Certified Antiquities Niese coverage remains **2,456 selections in I–VII**, with **0 newly enabled**. VIII, IX and X remain unavailable in Niese mode.

The checkpoint contains actual built-site browser and regression results for the existing systems. Those historical results are retained; this addendum does not claim a new browser run or QA of VIII/X Niese displays. Production Git blobs are unchanged from the checkpoint base, so there is no renderer delta to certify.

## Scope and next review

The collation addendum is left unstaged and uncommitted. The three authorized checkpoint commits contain review files only and explicitly say implementation is not approved. No push occurred. The batch stays based on 1cf003b. CANONICAL_ADVANCE.json preserves the earlier TOC typography reconciliation. During final verification canonical advanced to a480215 through the separately documented Greek source-contents v1.1 integration; CANONICAL_ADVANCE_FOLLOWUP.json records its commits, exact scope and certification hashes. All six VIII/X narrative inputs and renderer code are unchanged. No merge or rebase occurred in this audit.

Finish these two books: decide the named source/representation questions, independently verify the remaining Latin candidates, then recompute extents and candidate arithmetic. Any later implementation requires separate approval, byte-preservation checks and actual new-book browser QA. No other batch has been selected.
