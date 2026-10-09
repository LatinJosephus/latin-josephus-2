# Book X: current candidate-collation status


## Follow-up after the committed candidate checkpoint

Checkpoint `da28ec5abd7084fe5199549e2e38488171505c0e` remains candidate-audit evidence; implementation is NOT APPROVED. The follow-up read all 63 Niese body pages and recorded all 281 starts in PRINT_OBSERVATIONS.json and BOUNDARIES.json. See COLLATION_SUMMARY.json for separate source, Latin-verification and editorial counts; REVIEW_CASES.md now states precise decisions. All original classifications, source hashes, candidate locators and provenance are retained.

Greek XML explicitly labels 2–281; the exact absent explicit label is 1, at the printed opening (Niese II p.330/PDF338). The opening is already the first citation, not an additional section. Proposed opening representation and later relocations are in GREEK_REPAIR_PROPOSALS.json, unapplied.

Run the batch followup_collation.py to reconstruct this addendum from the committed candidate register and saved observations; run verify_followup.py for hashes, locators, source preservation and scope. These scripts cannot independently reproduce human visual judgements. Do not rerun the older audit_book.py to overwrite this follow-up. No Greek/Latin source, renderer, registry or navigation file has been changed.

CASES.json is the preserved checkpoint input. FOLLOWUP_DECISIONS.json and REVIEW_CASES.md carry current source assessments and editorial questions.

## Preserved candidate checkpoint text

# Book X: source authority and provenance

The canonical Latin transcription is the sole textual base. Canonical Greek supplies the machine-readable section census and candidate incipits; Niese's printed edition controls numbering and the placement of Greek citation starts. A continuous XML number sequence is not independent word-boundary verification.

## Pinned input and output bytes

| Language | Canonical SHA-256 before = after | Isolated-worktree SHA-256 before = after |
| --- | --- | --- |
| Greek | `e49314528e626f47c64e507cbd6a96978419ae1765b059ed6100818e31279089` | `6e4d4495ea48de1addd6a94ca81d34044621e6ddf2e716d1b8ff6db760caa5ae` |
| Latin | `8b2104191d4dba2e7e74ca684146519ed5b5113a5e983a5ceb9a6e970f741d3a` | `e1f56d981c25bdf2f6f53842d8e624bc8e3fae22de4c4eed1dcd35ce4ce1872c` |
| English | `bdeb69c28d516cea6c44499b1dbb9d4b5ea0e4e9208e3a02c505e14a4bce925d` | `1e70950fd9d2500795c401b37b7d49fa560d3f0fd90270b11915bccd718faccf` |

The canonical checkout has CRLF line endings in these inputs; the fresh Git worktree materialized LF bytes. For all three files, replacing only canonical CRLF with LF recovers the worktree bytes exactly. This is recorded as checkout provenance, not a normalization performed by this audit. The canonical files were not changed. All candidate locators and technical rehearsals are pinned to the actual isolated-worktree bytes. `BASELINE.json` records lengths, IDs, sameAs, labels, paragraphs, divisions and milestones.

The audit started at `1cf003beeb03f7b0acf2c42057ace062cdb7ebff`. Canonical later advanced to `f393fa1223b38d9ca114e583fcc57d5e34425815` through the separately documented TOC typography change. The three Book-X inputs remain unchanged. The isolated branch was not rebased or merged; see the batch `CANONICAL_ADVANCE.json` and `REPOSITORY_INTEGRITY_QA.json`.

## Primary printed control

Benedictus Niese, ed., *Flavii Iosephi Opera*, vol. II, *Antiquitatum Iudaicarum libri VI–X* (Berlin: Weidmann, 1885).

- File: `C:\workspace\Antiquities-Niese-Batch-08-10\Niese-PDFs\Niese (1885) - Antiquities VI-X.pdf`.
- SHA-256: `040c1570bc25730fa2c98b2f9ae847646af67919b6a634c2685628601de12b44`; 400 PDF pages; 85478498 bytes.
- Book X body: printed pp. 330–392; one-based PDF pp. 338–400.
- The title, actual book opening, terminal section and subscription were inspected. The supplied file hash matches the frozen Niese source `operajosephus02joseuoft.pdf`.
- Niese span: 1–281. The current XML explicitly represents 2–281; section 1 is implicit at the verified printed opening. No section-1 num was added.

The expected count comes from the Greek census together with the independently printed opening and terminal section. The interior Greek word boundaries are not all independently collated in this packet. Search-page intervals bracket candidate locations from the frozen printed controls; they are not a claim that every intervening marginal number was read. Marginal numerals often sit on a line containing words from the preceding clause, so their horizontal/vertical placement alone cannot identify an XML word boundary.

## Independent Loeb control

*Josephus*, vol. VI, *Jewish Antiquities*, Books IX–XI, Ralph Marcus, Heinemann/Harvard, title-page date 1958; copyright leaf records first printing 1937 and reprints 1951, 1958. Book X opens on Greek p. 156 / PDF172, English p. 157 / PDF173.

- File: `C:\workspace\Loeb Josephus Volumes\Josephus Jewish Antiquities (Books 9-11) (Ralph Marcus) (z-library.sk, 1lib.sk, z-lib.sk).pdf`.
- SHA-256: `cda46526761f421ffe3f9c2eec79b1672d5c1160dd7f51f16166c48f09736226`; 564 PDF pages; 20084436 bytes.
- Exact hash matches the frozen Loeb source. Its Greek/English contextual evidence helps test correspondence; it does not assign Niese numbers from Chapter/Subchapter boundaries.

Whiston English in the canonical repository is broader aligned context. Its 52 narrative paragraphs and 51 labels do not establish exact Niese divisions. No English Niese certification or modification is made.

## Frozen structural research

Read-only roots under `C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review`:

- `Antiquities_Loeb_Niese_Verification_2026-10-05`: freeze commit `19308a8ed937525c540827205b0c763768f5ce44`; manifest SHA-256 `1a254cd03a3cb01541cb25e2b73f6e926da7ccbb2c724f1df244363d1e323b70`. All 237 listed hashes pass and were rechecked at close. This packet includes the relevant rows, retaining their original statuses and anchors, in `FROZEN_PRINT_STARTS.json`.
- `Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06`: freeze commit `41e817680549767d36e3f80dbc825682908ea5e6`; v1.1 manifest SHA-256 `cfc898b9f051a003de7045dbf352229097855e2c39696a33213c4454be50ff11`. All 8 listed hashes pass and were rechecked. VI–XI have no certified Bamberg chapter marks; existing XML div2 containers must not be treated as contrary manuscript evidence.
- Current canonical `assets/xml/antiquities/structure.xml` remains an independent reference. Its HEAD blob and file hash are in the batch integrity ledger. It is not used to manufacture Niese starts.

Book X has 63 frozen level rows, representing 52 distinct traditional physical starts (11 Chapters and 52 lower divisions at 63 level rows). These are structural controls, not an internal-boundary census.

## Greek machine-source search and earlier segmentation

The search covered 987 files and 86 XML files in `C:\Users\Pollard_R\Git\Segmentation resources`, plus XML member names in its ZIP archives. No independently identifiable accepted VIII/X Greek master was found. The standalone Greek XML is Book VI; VI/VII copied, frozen and test versions were not substituted for VIII/X. `SOURCE_SEARCH.json` in the batch records the full search and selected related resource hashes. A missing independent master is disclosed; no master hash is invented.

The last Greek VIII/X source commits are `0e1f3f718de4dce60c2b4207fe9f40f305c708b4` (update XML files) and `a89405e80bdebfee20ef7a25ac07c21de32ed85f` (refactor for multiple books). Their canonical file hashes above pin the actual selected machine sources, without pretending that the import history certifies all boundaries.

Accepted VI history includes Greek correction `0bf6e85`, Latin insertion `b103eee`, and enablement `b11075a`; the human-approved VI249 Greek repair is distinguished from a rejected provisional location. VII history includes Greek `9849e101c7930dfa9e2003a5f681180ed47c694f`, Latin `86c5140ad36d1fd966ad80771d9200b1edf1bdf7`, and enablement/omission handling `40d2801dd8894bb960ab7a4bce264d9c04141ba8`. Their final freeze and application materials were inspected for method only. No historical VI/VII count or input hash is used as an expectation for this book.

The mixed-content mapper is byte-identical to the accepted VII read-only audit's `mixed_mapper.py`; its 14 fixtures pass. Source paths and hashes are in batch `METHOD_SOURCE_MANIFEST.json`. Current canonical renderer code takes precedence over historical scripts. The safe method preserves existing num labels and all inline markup, uses exact text/tail node and byte positions, never splits paragraphs, and requires removal of authorized new markers to recover original bytes. Scholarly approval remains separate from this technical proof.

Niese’s final running-head IX is a printer’s slip: the tenth-book subscription and surrounding Book-X text establish the identity. It is not a reason to audit or enable Book IX.

`XML_SOURCE_NOTES.json` records the actual embedded source declarations. Greek identifies Niese vol.2 (Book X explicitly adds1885), Latin identifies Bamberg Msc.Class.78 and has a TEI header, and English identifies William Whiston(1737). These declarations support provenance but do not replace independent printed boundary verification.

`STRUCTURE_REFERENCE.json` inventories all current book-specific traditional, alignment and other canonical structural locators, with their literal fields and source hash. `structure_reference.py` reproduces this independent reference; the Niese candidate mapper does not read it. Existing XML chapter containers and labels are separately preserved in `BASELINE.json`.
