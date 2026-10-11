# Isolated integration recovery

This package is **CANONICAL-INTEGRATION-READY**, with the scoped Book I and inherited editorial qualifications in REPORT.md. It does not authorize a canonical merge, push or public deployment. The original prototype RENDERER-GO receipt is preserved unchanged.

Verify the ZIP against its SHA-256 sidecar, then extract into a new directory. CHECKSUMS.json records the literal SHA-256 and size of every payload entry. RECOVERY_VERIFICATION.json alongside the ZIP records CRC, complete entry hashes, source preservation, bundle verification and an actual clean isolated Git recovery. Never extract over a canonical checkout or a source segmentation worktree.

For Git recovery, use a separate local repository containing prerequisite commit `663b8ce318f0aa247d304d8eeda5b8e76e7489c6`. The bundle is incremental; it does not contain the entire prior canonical history. A local clone can provide the prerequisite without remote writes:

```powershell
git clone --shared --no-checkout --config core.autocrlf=false C:/Users/Pollard_R/Git/LatinJosephus-v2-development C:/workspace/Whiston-I-XI-recovered-review
git -C C:/workspace/Whiston-I-XI-recovered-review fetch C:/path/to/extracted/integration.bundle refs/heads/integration/whiston-i-xi-certified-20261011:refs/heads/recovered-integration
git -C C:/workspace/Whiston-I-XI-recovered-review checkout recovered-integration
git -C C:/workspace/Whiston-I-XI-recovered-review status --porcelain
```

Keep `core.autocrlf=false` for literal certified Whiston recovery. Confirm HEAD against DELIVERY_RECEIPT.json and all twelve source checksums against SOURCE_INVENTORY.json. The full binary patch and focused source/renderer/guard patch are alternative review materials; do not apply either to canonical development without separate authorization and a fresh baseline reconciliation.

The preview directory is independently runnable with Node, without Jekyll or the Git prerequisite:

```powershell
$env:WHISTON_SITE='C:/path/to/extracted/preview'
$env:WHISTON_PORT='4174'
node C:/path/to/extracted/tools/preview.cjs
```

Open the local Antiquities reader at `http://127.0.0.1:4174/antiquities/?book=9&niese=51`. Proem uses `?book=preface&niese=26`; narrative uses `?book=1&niese=27`. The preview includes exact frozen publication bytes and the complete standard-built reader shell. Browser theme dependencies use the existing CDN links; this package changes no deployment configuration.

To rebuild in the recovered checkout, install the normal Gemfile dependencies, run the standard Jekyll build into a generated directory, then run `node bin/prepare-reader-publication.mjs --site <generated-directory>` and `node bin/reader-corpus-qa.mjs --site <generated-directory>`. These validate all 143 production XML and preserve 38 exact frozen publication authority hashes without editing repository XML. The review build folder records the successful complete-plugin build, local dependency lock, installer diagnostics and ImageMagick 6 SDK selection bootstrap. Those Windows paths describe the original test host; they are not portable dependencies or production configuration changes.

English interval QA is complete in PER_SECTION_QA.csv and CANDIDATE_XML_INTERVAL_QA.json. The independently verified full original traditional/alignment evidence remains under review/Whiston_I_XI_Renderer_2026-10-11. Fresh standard-built and exhaustive legacy results are in the new integration review packet. Revalidation scripts contain the original host paths; adapt those paths in a new recovery workspace before execution. Preserve every frozen source, original certificate and scholarly decision unchanged.
