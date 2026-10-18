# Bamberg substantive closeout v3.4

Start with `editorial_closeout_summary.md`, `qa_report.md`, `qualification_dispositions.md` and `reconciliation_manifest.json`.

The new local staging tranche contains 46 individually authorized corrections. The cumulative inventory contains 203 actions / 202 application units. One qualified approval and nine unanswered proposals remain withheld. Canonical development is unchanged.

`inputs/` preserves both RMP exports and their original fields; `decision_import_certificate.json` records hashes and reconciliation. `patches/` contains the exact forward diff, inverse diff and byte-offset inverse manifest. `scripts/verify_closeout.py --root WORKTREE --packet THIS_DIRECTORY` performs read-only structural/authorization/reversal QA; put the project's Git executable on PATH. The frozen original source commit must be locally available. `scripts/reader_closeout.cjs` uses the unchanged real reader and explicitly supplied installed browser/runtime dependencies; see its environment arguments and the QA certificate. No script is authorized to edit canonical development.

`final_verification/Bamberg_Final_Independent_Verification.html` is a standalone offline form with sixty PNG assets, explicit folio/column/vertical locations, zoom, local draft storage and user-initiated CSV import/export. `Final_Independent_Verification.md`, numbered PNGs, a printable HTML sheet, a blank decision CSV and its schema are alternatives. Twenty samples are prepared, none performed. The sample is independent of proposed correction preference and grammatical quality, subject to documented prior-review exclusions and unprotected, mapped 25-word text-slot eligibility. It is not a statistically reliable corpus-wide accuracy sample.

Native images and prior visual evidence remain in their verified shared cache and preserved v3.3 archive. Their institutional identifiers, checksums and exact crop coordinates are included; full scans and previous audit archives are not duplicated. Original decision exports are never overwritten by the review form.
