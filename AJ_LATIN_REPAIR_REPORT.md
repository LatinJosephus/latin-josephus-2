# AJ Latin alignment repair — implementation report

25 October 2026. **GO for local review and a separate future release decision.**

The derived DEH–Antiquities layer now accepts the approved corrected Latin witnesses. All 31 DEH records and 44 correspondence components remain intact. Every current Latin excerpt has been audited and verified in the actual browser, alongside unchanged Greek/Whiston comparisons.

## Git identity and isolation

- Repository: `LatinJosephus/latin-josephus-2`.
- Base, rechecked directly at the remote before work: `5bb301c1b41d63c89c33a79826fc62892ac3890f`.
- Branch: `repair/aj-latin-display-reconciliation-20261025`.
- Worktree: `C:/Users/Pollard_R/.codex/.chatgpt-projects/g-p-69862e643cc08191a8457368cb0c460f/worktrees/aj-latin-reconciliation-20261025`.
- Exact final commit: recorded in `C:/Users/Pollard_R/.codex/.chatgpt-projects/g-p-69862e643cc08191a8457368cb0c460f/outputs/AJ_LATIN_REPAIR_20261025/AJ_LATIN_REPAIR_COMMIT.json` and the incremental recovery bundle. The commit delivering this report is the repair commit.

All existing checkouts, branches, indexes, configurations and uncommitted files were snapshotted first. The new worktree was created with `core.autocrlf=false` and `core.longpaths=true` for that operation. The main/older source and preview working directories were not reset, cleaned, merged, rebuilt into or committed. No remotes were pushed.

## Changes

| File or group | Purpose |
| --- | --- |
| `assets/data/deh-aj-display.v1.json` | Replace eight stale Latin XML pins and the stale renderer pin with audited current authorities; record current base and fixed boundary-certificate identity. All correspondence records remain byte-equivalent as JSON values. |
| `_includes/deh-parallels.html` | Matching derived-layer checksum. |
| `bin/deh-aj-display-qa.mjs` | Retain existing guards and add fixed-certificate verification plus independent Python boundary/text/coordinate verification. |
| `bin/aj-latin-boundary-audit.py`, `bin/aj-latin-reconcile.py` | Independent XML walk and deterministic, explicit-write regeneration. |
| `bin/aj-latin-reconciliation.test.mjs` | Source/certificate corruption, repinned path/note/exclusion rejection and numbering-preservation regressions. |
| `bin/aj-latin-browser-qa.html`, `.mjs`, `bin/aj-latin-local-server.mjs` | Loopback browser extraction/coordinate checks, corrupt-response tests and evidence recording. |
| `_docs/aj-latin-reconciliation/` | Fixed per-component certification, independent browser expectations, historical/current source authority, protected-source manifest and actual QA receipts. |
| `.gitattributes` | Narrow byte-preservation rules for the repaired derivative, audit records, include and verification scripts. |
| `AJ_LATIN_BOUNDARY_AUDIT.md`, `AJ_LATIN_QA_RESULTS.md`, this report | Detailed scholarly-boundary record, tests/limitations and implementation handoff. |

## Boundary findings

No paths or sides require adjustment. The source trees preserve their historical element order and attributes, and all old intervals match the recovered independent XML expectations. Current source text and positions were independently recomputed and reviewed. At 164 available endpoints absolute character offsets differ, which is documented rather than assumed away.

One selected passage changes: AJ IX.216, used by DEH II.12.3. The inherited ` Hoc ergo tibi` fragment was already removed by approved Bamberg candidate `S27-B09-216-HOC-ERGO-TIBI`, integrated at `123d82f631602ccad174daea38e99d6a64d3e69f`. The same section markers correctly bound the corrected text. This implementation does not edit the XML.

The Latin XX.238 absence, IX exclusions, witness qualifications, multi-component order, alternative-tradition annotation and prior P4-D07 XV.38–56 excerpt remain intact. No new endpoint is invented or expanded. No new editorial question is unresolved; inherited limitations remain visible.

## Renderer and safeguards

The current renderer is retained unchanged at SHA-256 `39ded95fc3b7fdf39d9827cf513e6fc6c88922bb039435446b48b22ec4192848`. The recovered numbering helper and call remain present, and actual whole-book browser checks confirm its audited Latin labels. Keeping the verified current renderer pin resolves its stale dependency without deleting a safeguard.

The application still hashes sources before XML conversion and refuses unauthorized bytes. The strict gate additionally checks the fixed certification hash and every selected text/coordinate. A well-formed incorrect boundary with a freshly repinned include still fails. No source-modification exemption or broader line-ending acceptance was introduced.

## Validation and preserved inputs

All strict AJ checks pass. Actual browser certification covers 420 witness-section occurrences and 278 Latin boundary endpoints, all 31 Latin UI routes, eight ordinary affected-book views, Bellum regression and all five Millet books. Negative tests reject deliberate source and boundary tampering. The corpus guard parses/protects all 166 production XML files and 38 frozen publication inputs. See `AJ_LATIN_QA_RESULTS.md` for exact counts and limitations.

No Antiquities Latin XML, Ussani Latin, Pollard English, Millet French/master assets, Niese registries, frozen concordance, runtime renderer/module or unrelated asset is changed. The source hash and change manifests bind these claims. No new manuscript collation or independent adjudication of printed reference loci is claimed.

## Recovery and next action

Recovery evidence is retained at `C:/Users/Pollard_R/.codex/.chatgpt-projects/g-p-69862e643cc08191a8457368cb0c460f/outputs/AJ_LATIN_REPAIR_20261025`: initial remote/checkout snapshots, old XML and approved diffs, pre-repair failure, boundary evidence, build environment/log, actual browser records, final preservation checks, exact commit/change manifest, an incremental Git bundle based on `5bb301c1b41d63c89c33a79826fc62892ac3890f`, and a recovery ZIP.

Review this local commit. Any later public-preview candidate must be prepared separately atop its then-current remote `main`, preserving publication receipts, preview-domain metadata, exact frozen bytes and intended public scope. No push or publication was performed.
