# QA COMPLETE — DATA AND RENDERER VERDICTS SEPARATE

Checkpoint: D-DATA-GO-RENDERER-NO-GO
Last completed Niese section: XX.268
Branch: pilot/whiston-antiquities-book20-20261011
Git commit at export: af5da31ead93fd854cad8da8363d1ba3c91ab2e6
Original worktree: C:\workspace\LatinJosephus-BookXX-Pilot-20261011

Next action: Book XX complete. STOP. Independent corpus-wide certification is a separate task; no merge, push or deployment.

## Independent offline recovery

1. Verify the ZIP SHA-256 against its accompanying `.zip.sha256` file. Extract into a fresh directory; never overlay a canonical checkout or another book.
2. From that extracted directory run `python -B scripts/verify_archive.py --reconstruct recovered-original-book20.xml`. Python 3 and lxml are required; the bundled desktop Python used for certification is identified in RUNTIME.json. Verification itself needs no network, Git repository, canonical checkout or prior pilot.
3. This checks every CHECKSUMS.json manifest entry, original byte reconstruction, parsed text/structure, all268 intervals and frozen Greek/published-HTML identities. It also writes the reconstructed original XML to the named fresh recovery file and prints its SHA-256. For a partial checkpoint, inspect its partial STATE.json and snapshot QA instead of claiming final certification.
4. Compare output/book-20.xml and the frozen original under frozen/assets/xml/antiquities/English/. The complete ledger is BOOKXX_SEGMENTATION_LEDGER.json; all interval extents and hashes are in COMPLETE_SECTION_EXTENTS.json. FINAL_EXPORT_QA.json and OFFLINE_RECOVERY_QA.json accompany the final ZIP externally. The implementation commit is in GIT_IDENTITIES.json; the later delivery commit and final ZIP digest are recorded in the external recovery instructions to avoid a self-referential archive digest.

## Resuming an incomplete checkpoint

Originals: frozen/; retrieved raw witnesses: sources/; output XML: output/.
Boundary evidence: EXTRACTION_LEDGER.json; mapping: ALIGNMENT_LEDGER.json.
Do not repeat completed tranches. Inspect STATE.json, snapshots/, per-tranche QA, explicit decision files and ADJUDICATION_RECORDS.json. Resume only in an isolated checkout pinned to BASELINE.json. PARTIAL archives are not certified; the final offline verifier requires complete268 records.

Book XIX's final DATA-GO and offline recovery gate were independently checked before XX started. STOP after XX. No canonical merge, push, deployment or corpus-wide certification is authorized. DATA and RENDERER verdicts remain separate. The inherited renderer has no current exact-interval browser certification.
