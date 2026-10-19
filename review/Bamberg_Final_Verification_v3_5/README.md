# Bamberg Final Verification v3.5

Start with `final_scholarly_audit_certificate.md`, `final_verification_results.md` and `qa_report.md`.

This delivery preserves the completed twenty-check RMP export, reconciles the 100-check ledger, and records eleven narrowly authorized changes at six sample loci. It contains exact reversible patches, a 214-action cumulative inventory, current source hashes, a twenty-book procedural inventory and the unchanged ten-case withheld register. Development is not promoted. No new manuscript decisions or HTR work were undertaken.

`evidence/` contains the six discrepancy passages' original high-resolution crops, context images and small locators. Native images remain in the immutable shared cache; identifiers, SHA-256 hashes and coordinates are in `image_evidence_manifest.json`. The fourteen confirmed passages' original crops remain in the v3.4 viewer; all sample metadata are retained here without duplicating the whole image collection.

Reproduce source/authorization/inverse checks using Python 3: `python -B scripts/verify_final_closeout.py --root PATH_TO_ISOLATED_V3_5_WORKTREE --packet PATH_TO_THIS_DIRECTORY --output result.json`. Keep the parent v3.4 and actual-development commits available in Git. The reader harness uses the installed project Playwright/Chrome and fresh build with the documented environment variables at its start; no production renderer is altered. `qa/` holds the acceptance results, and `patches/` contains forward/inverse diffs plus the source-bound exact reversible operation register. Historical fixtures continue to use their frozen historical sources.

The source export is preserved byte-for-byte. Do not overwrite historical editorial CSVs or infer approval from a candidate's automated class. Ledger: 100 checks completed, none remaining. Nine unreviewed proposals and conditional XIII.314 remain untouched. I.34 remains a separate open reader defect.
