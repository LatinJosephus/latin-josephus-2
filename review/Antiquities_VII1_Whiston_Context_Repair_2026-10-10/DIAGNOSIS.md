# Antiquities VII.1 Whiston contextual paragraph recovery

Scope: F001 only; reader-only local repair based on `cf4cdb90e5fbcefbd0f2606d551d6a05100fd545`. No editorial XML or published release changes.

The fresh unmodified baseline reproduces the empty English narrative. `antiquitiesNieseContextView` finds the Latin Niese start and its containing paragraph, `latin-book07-num`. `alignedParagraphsForCanonicalId` compares that literal ID against `canonicalParagraphTargetIds`, whose explicit normalized English `sameAs` is `latin-book07-num1`. The equality fails. The trace records zero literal matches, one explicit-target candidate and no canonical paragraph with the suffixed ID. Greek independently corroborates that same target. This is a context lookup defect, not clipping or asynchronous pane readiness.

The runtime fallback applies only when the normal lookup is empty, no registry context override is present, selection is Niese 1, the unsuffixed ID belongs to the first canonical narrative paragraph, the suffixed canonical ID does not exist, and exactly one source paragraph has exactly that explicit `sameAs` target. It clones that surviving paragraph through the existing context wrapper. It changes no IDs, sameAs attributes, starts, text or exact Latin/Greek slicing. Ambiguous targets, absent sameAs, duplicate candidates, existing suffixed canonical paragraphs and interior milestones fail closed.

The first Latin paragraph physically spans §§1–6. To satisfy the brief's sole VII.1 content-change constraint, this fallback is intentionally confined to the opening Niese selection. The inherited missing context in VII.2–6 remains unchanged and outside this repair. Book and traditional views retain the full surviving paragraph; no claim of exact English Niese segmentation is introduced.

English previously rendered only `English context: exact Niese-level segmentation is unavailable for this source.` After the repair it retains this notice and shows the complete source paragraph, from `1. This fight proved to be on the same day whereon David was come back to Ziklag` through `which have continued to my own age.` exactly once. Complete before/after evidence and source hashes are in `evidence/`.

The permanent browser regression positively asserts the full source-derived English paragraph, a single paragraph and ID, contextual view type, retained qualification and absence of duplicate English IDs. It fails on the baseline and passes on the exact final candidate. Guard tests use disposable local DOM fixtures only.
