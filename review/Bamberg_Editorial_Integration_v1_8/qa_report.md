# Bamberg editorial staging v1.8 — QA

All required tests passed. Source commit `ef55e7ebd6e86d886341e8fbca8403d32dfc00ac` was replayed through Git onto `f13613e2e5cfc857a15b61201711211be6506279`, the unchanged current development HEAD. No textual patch was reconstructed manually and no source passage drifted.

| Check | Measured result |
|---|---|
| Signed editorial authorization | 19 edit effects, 18 application units, 20 completed checks |
| Approved XML | All nine files parse; individually and jointly reversible |
| Niese, IDs, cross-references, divisions, layout and protected markup | Unchanged |
| XII.80 composition | `quattuor <cb n="2/2"/>digitorum`, exact column marker retained |
| Production provenance | All eleven blobs byte-identical to v1.7 |
| Integrity registration | Nine actual hashes; only the guard's manifest-seal literal differs from baseline |
| Existing-file preservation | 6,406 other staging files and all 6,417 active-development files byte-identical to baseline |
| Corpus acceptance | 166 XML parsed; 38 frozen publication inputs; 30 negative/publication checks passed |
| Historical structural regressions | 15 XVII + 15 XVIII tests passed; these are preserved-fixture tests, not new manuscript evidence |
| Locked site build | Passed in 156.095 seconds; existing deprecation warnings only |
| Real reader/browser regression | 18 locus views, nine whole-book views and two retained views passed; Greek and English display unchanged |
| Complete production inverse diff | Git reverse-application check passed; XML inverse reconstruction byte-exact |
| Historical preservation | Ten archives unchanged; source commit and signed original forms unchanged |

The development baseline equals v1.7's original parent. Thus no baseline changes affect inverse-test reproduction. All textual differences are precisely the individually approved edits. Greek, translations, DEH, renderer and unrelated existing files are byte-identical within their respective checkouts. The active checkout has pre-existing CRLF representations for some Git-normalized LF files; its complete byte inventory matches the preserved actual v1.7 development-checkout hash snapshot. A preliminary Git-blob-byte comparison detected this representation difference, and was replaced with the correct actual-checkout SHA-256 comparison; no corpus or checkout file was changed to satisfy the test.

The 51 original audit files are preserved unchanged in the source commit. Twenty-one contain workstation or temporary paths. This staging branch promotes a portable derived packet instead, referencing original Git paths and SHA-256 values; it does not promote the raw historical files or relabel derivatives as signed originals. No full-resolution images, image cache, temporary files or raw machine-specific logs are included.

The original independent signed-record verifier was also rerun unchanged against this staging worktree. Raw machine-local build logs remain in the separate local runtime folder and are excluded from the portable archive and commit.

New audit prose and structured records use LF serialization. The byte-exact production diff deliberately retains source-file CRLF payload where present; it is verified by exact reverse applicability, rather than prose whitespace lint. The additional staged-format check excludes only that patch container. All production and corpus acceptance rules remain unchanged.
