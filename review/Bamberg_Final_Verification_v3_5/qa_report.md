# v3.5 acceptance certificate

All mandatory checks pass against the exact isolated proposed source state. Parent: `123d82f631602ccad174daea38e99d6a64d3e69f`. Actual unchanged development: `f874b6a60f16c96f356abcbe070854611c49f2a3`.

- 166 production XML files parse. Six changed Latin books: II, VI, VIII, IX, XIX, XX; eleven individually authorized actions.
- Niese identity, sequence and structural position, XML IDs/references, divisions, foliation, layout and protected editorial markup are unchanged. Each minimal edit passes the whole-token protected-markup guard.
- Book XI is byte-identical to v3.4: physical witness order, split XI.312/326/342 and both Bellum IV.105 interpolations are untouched.
- Every change is bound to the preserved RMP export, stable sample ID, exact comment, original bytes, source hash and manuscript evidence. No unanswered or conditional proposal is applied.
- All 203 earlier staged actions remain exact. Cumulative total: 214 actions / 213 application units; 157 remain in actual development and 57 are on the two-commit staging series.
- Every individual edit and combined v3.5 tranche reverses byte-for-byte to v3.4; the unchanged historical v3.4 inverse then restores actual development `f874b6a60f16c96f356abcbe070854611c49f2a3`. Historical baselines have not been retargeted.
- Corpus-integrity registration: only six actual XML hashes appended; the manifest seal alone changes in the guard. Validation logic, corpus coverage, renderer and publication safeguards are unchanged. All registrations and 30 negative publication tests pass.
- Fresh Jekyll build and post-build reader-corpus acceptance pass. No new dependency or paid recognition service is used.
- Reader regressions pass: {"Book_XI_structure_views": 14, "direct_views": 8, "errors": 0, "neighbors": 12, "new_locus_views": 6, "prior_correction_views": 201, "retained": 2, "whole_books": 6}. Six full selected-passage comparisons cover all eleven actions; neighbours, complete affected books, earlier corrections and Book XI physical/logical views are included.
- 53 established historical and mechanical-safety regression tests pass with historical fixtures attached to their frozen sources.
- Nine unreviewed proposals and conditional XIII.314 remain exact, as do `pro peregrina` and the amended VI.219 insertion. Greek, English, DEH and all unrelated tracked sources remain unchanged.
- Twenty final decisions are valid: 14 confirmations, six discrepancy passages. The authoritative ledger is 100 completed / zero remaining. No extra check was requested or counted.

Machine evidence is in `qa/`, `patches/`, the source-hash manifests and the exact authorization records. The existing I.34 reference-mark issue remains OPEN and outside this correction scope. A passing build or procedural screen is not exhaustive word-by-word manuscript certification.
