# Reader corpus acceptance and publication bytes

The Whiston I–XI integration candidate uses `reader-corpus-integrity.json` to name every production XML path and its reviewed source authority. The baseline is canonical commit `663b8ce318f0aa247d304d8eeda5b8e76e7489c6`; the twelve English files come from their frozen delivery commits, and the English-only structural registry change comes from the certified renderer prototype. The guard binds the manifest itself by SHA-256. New, missing, changed or malformed XML fails acceptance, including Lodge files. Certified Whiston bytes have no line-ending exemption.

The historical DEH concordance and Lodge import manifests remain frozen. Their publication hashes bind the original reviewed CRLF representation. A fresh Git checkout may supply LF instead. The guard accepts only explicitly recorded checkout representations and reconstructs publication bytes only when the resulting literal SHA-256 equals the frozen authority. It never changes repository XML, translation wording, segmentation, or frozen hashes.

After the normal build, verify and prepare the generated directory:

```text
bundle exec jekyll build --destination <generated-directory> --disable-disk-cache
node bin/prepare-reader-publication.mjs --site <generated-directory>
node bin/reader-corpus-qa.mjs --site <generated-directory>
```

The preparation command validates every generated XML source before restoring the exact frozen byte representation of 38 DEH/Bellum/Lodge inputs. It is a required publication input check. The negative tests operate on temporary copies and retain missing-file, unexpected-file, source-corruption and frozen-authority safeguards.

The frozen concordance import tool's “changed since import” assertion remains valid and unchanged. This integration does not reimport or replace that scholarly concordance. Historical contextual-English QA receipts remain immutable evidence; the current English acceptance suite checks all 3,821 exact intervals and separately retains contextual fallback checks for Books XII–XX.
