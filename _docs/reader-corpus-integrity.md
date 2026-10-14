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

## Lodge Antiquities Book II data-only registration

One reviewed production path is added: `assets/xml/antiquities/English/Lodge1602/book-02.xml`. Its deterministic derivative hash is 69ed805eb0585ec8b93f4d330a2c69c52f5fb5aae72d583fcd8e180eade5d729. The new record binds the byte-frozen scholarly master/register/manifest, independent inverse ledger and data validation receipt. All 143 previous inventory records, accepted hashes, Whiston authorities, DEH concordance and Lodge Bellum authorities remain unchanged. The guard changes only its exact reviewed inventory seal to 36c6475919da7a91ed0e5bf30ea745fc062d4430db00fadf70d7a897702f3ad8.

This records data-layer acceptance only. Lodge is not yet selectable in Antiquities; renderer/browser certification remains WorkBot 7B. No publication build or deployment is recorded. The importer and independent verifier are `bin/lodge1602-antiquities-import.py` and `bin/lodge1602-antiquities-qa.py`; the latter independently restores both frozen scholarly and original extraction bytes. New Lodge Antiquities byte-preservation rules are limited to the nine added paths in `.gitattributes`.

## Lodge Antiquities Proem and Books I, III–V batch

The five additional XML records bind 1,361 identities to the frozen scholarly ZIP
`21ee32b9f6d5e375ced2839e9cacc9b2e77619a93ddd105fb83280c22282c783`.
All 144 earlier records, including Book II, retain their exact contents. The new
inventory seal is `cb0c8aa0477e30e8876a9794cb0524fae59b4691b9907bef4cba515cf465f3a0`.
The same importer and independent verifier accept `--unit proem`, `book-01`,
`book-03`, `book-04` or `book-05`. Omitting it retains the Book II adapter.
Each batch validation receipt independently restores the frozen master and
certified extraction byte for byte, replays every text/tail coordinate and
exclusive interval, and compares every native mixed-content attachment.
The reader offers Lodge only for the Proem and Books I–V. Original printed
chapters remain independent of project chapter and Bamberg context navigation.
Browser certification is recorded separately from these data-only receipts.

## Lodge Antiquities Books VI–X

Five further records bind 1,764 identities to frozen scholarly ZIP
`804662293e12910f00e955835217ffd9d504eaef700dbf37a1795310dc91b146`.
All 149 earlier records and protected source bytes remain unchanged. The existing
importer and independent verifier now also accept `book-06` through `book-10`.
Lodge is available for the Proem and Books I–X; XI–XX remain unavailable.

Only X.238 has an approved empty interval, at TCP byte 1970937. Its frozen
register and human log authorize `NO_SEPARATE_COUNTERPART`; the reader adds a
Lodge-specific notice outside source character data. X.239 retains its proper
text once. Every other interval must be nonempty. Historical confidence remains
1,759 HIGH, four MEDIUM and one LOW, with all five difficult treatments approved.

Books XI–XV add five frozen Lodge XML derivatives (2,130 identities), with complete independent inverse and section-coordinate receipts. All 154 earlier inventory records remain unchanged; the inventory now contains 159 XML files.
