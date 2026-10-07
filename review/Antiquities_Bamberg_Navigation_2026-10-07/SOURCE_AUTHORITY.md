# Source authority

Implementation base: `b8d4db2938e3a61a7f75ea8fcbb06f22fc78f02d` on `antiquities-bamberg-navigation`.

Scholarly authority: recovery commit `41e817680549767d36e3f80dbc825682908ea5e6`, tag `antiquities-structure-reconciliation-v1.1` (tag resolves to that commit). Packet: `C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review\Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06`.

The eight entries in the frozen v1.1 manifest were verified before implementation. All nine scholarly files, including the manifest itself, retain their recorded hashes. The independent verification checkpoint `19308a8ed937525c540827205b0c763768f5ce44` remains provenance of the unchanged traditional registry.

No PDF, manuscript image, original human checklist or Word audit was reopened. The frozen JSON supplies all 198 decisions and all 594 independent current-text locators. Literal labels and completed human-check fields are reproduced as recorded; every frozen Bamberg row is retained verbatim as JSON evidence in its registry item. Presentational locators were compiled against actual base XML; no numeric suffix, sameAs link or shared Niese number was used to adjudicate equality.

| Scholarly file | SHA-256 |
|---|---|
| Antiquities_Bamberg_Niese_Map.csv | `146c29df6086e2dec491557a5f721726468c36dee565f4ac3ab3ac9481ecd9df` |
| Antiquities_Loeb_Bamberg_Chapter_Concordance.csv | `7ec54ee3da187e5b9a3c9abe241dbf6faf9b45cfdb3915b829491a708259533e` |
| Antiquities_Loeb_Subchapter_CurrentUnit_Concordance.csv | `a3861c470c19c1f7aba8f39e29203737a5ee5ff51b21da06b6878f7efebd046d` |
| Antiquities_Structure_Integration_Proposal.md | `2d90419b7f9dc3418ecab702fdfbc37035f805fc9b0b03fbf8d64439f5626e69` |
| Antiquities_Structure_Reconciliation.json | `3f34fa728c5a1ace9de3357173a68665878a922fdf09201fe463a196ea4c66b5` |
| Antiquities_Structure_Reconciliation_QA.md | `c2eca6fe4cec99bb9dd5ee77358f6aa0c1dcf8e568d18c793448e9904ffd20e0` |
| Antiquities_Structure_Reconciliation_Report.md | `ff26c6f6db12989852bbcd591e39b92aa0e49b5f719aaf0063cf2ad274ebb8c9` |
| Antiquities_Structure_Reconciliation_v1.1_SHA256SUMS.txt | `cfc898b9f051a003de7045dbf352229097855e2c39696a33213c4454be50ff11` |
| FREEZE.md | `c3a0d18518e7e2cf7667903a49ddc81c00a50415b7659fbfe018f22b64aeabcd` |

The existing registry's reconciliation-v1.1 bibliographical identity is reused. Bamberg record identity, label, source order, incipit, citation relationship, confidence, traditional relationship and independent language start/end coordinates remain separate fields. The new audited-coverage list explicitly records no chapter marks in VI–XI.

At Niese 230 the prompt's example says XIIIΙ/XIIII; the authoritative record B78-table1-row079 says XIII. XIII is retained without a new scholarly judgment.

A non-scholarly Windows desktop.ini changed after the initial snapshot. Its before/after hashes are recorded in INTEGRITY_QA.json. It is outside the frozen scholarly manifest and was neither written nor reverted by this task. This qualification prevents a claim that every filesystem entry in the recovery directory remained identical.
