# Whiston’s Antiquities headings and contents audit

8 October 2026. Complete read-only audit of Books I–XX. No website implementation.

The proposed feature is **Whiston’s chapter headings (compiled index)**, identifying the **Auburn and Rochester: Alden & Beardsley, 1856** printing. This volume supplies 256 chapter headings in the narrative. Its backmatter contains an alphabetical index; no suitable separate Antiquities chapter-heading contents list was established in the inspected locations. This conclusion applies to that copy and the stated inspection scope. **The form of the advertised 1737 “Contents” remains unverified.** No claim that the first edition lacked contents is justified.

All twenty books and all 256 heading positions were visually inspected in the 1856 scan. **254 readings are certified; two Book III readings remain qualified.** All twenty proposed companion TEI files are well formed and pass the archived TEI_all Relax NG schema. Nineteen books have complete candidate text without an entry-level hold; Book III remains provisional. Adoption of this later printed edition as the governing index witness requires editorial approval.

| Book | Printed headings verified | Canonical headings | Gutenberg headings | Discrepancies | Source status | Integration readiness |
|---|---:|---:|---:|---:|---|---|
| 1 | 22/22 | 22 | 22 | 2 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 2 | 16/16 | 16 | 16 | 5 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 3 | 13/15 | 15 | 15 | 6 | PRINT_VERIFIED_WITH_REVIEW | Two faded readings need review |
| 4 | 8/8 | 8 | 8 | 2 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 5 | 11/11 | 11 | 11 | 6 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 6 | 14/14 | 14 | 14 | 5 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 7 | 15/15 | 15 | 15 | 7 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 8 | 15/15 | 15 | 15 | 6 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 9 | 14/14 | 0 | 14 | 7 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 10 | 11/11 | 0 | 11 | 7 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 11 | 8/8 | 0 | 8 | 5 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 12 | 11/11 | 0 | 11 | 10 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 13 | 16/16 | 0 | 16 | 10 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 14 | 16/16 | 0 | 16 | 10 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 15 | 11/11 | 0 | 11 | 8 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 16 | 11/11 | 0 | 11 | 10 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 17 | 13/13 | 0 | 13 | 7 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 18 | 9/9 | 0 | 9 | 7 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 19 | 9/9 | 0 | 9 | 5 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |
| 20 | 11/11 | 0 | 11 | 3 | PRINT_VERIFIED_WITH_VARIANT | Text ready; edition approval required |

“Discrepancies” counts heading identities with at least one lexical/textual difference against a digital witness, excluding absent canonical headings. It excludes differences involving only capitalization, ae/æ comparison, punctuation or word spacing. Exact witness readings, raw differences and comparison policies remain in WHISTON_COLLATION.json. The independently reconciled printed, Gutenberg and Chicago chapter counts are **22, 16, 15, 8, 11, 14, 15, 15, 14, 11, 8, 11, 16, 16, 11, 11, 13, 9, 9, 11 = 256**. They are not forced to equal the traditional navigation’s 257 chapters.

## Gutenberg and current project text

The accepted census’s **243 equal / 13 different** index-versus-linked-heading results are reproduced under whitespace-only comparison. Three differences concern note markers; XVI.3 is split across two heading elements; the remaining nine concern wording, spelling, punctuation or spacing. WHISTON_GUTENBERG_13_CASES.md preserves every pair and its print/canonical adjudication.

Current canonical XML explicitly retains 116 chapter headings in Books I–VIII. The 140 heading identities in IX–XX lack corresponding explicit CHAPTER headings in their current files. This is an encoding absence, not evidence that Whiston lacked those headings or that the narrative is absent. Narrative content is not substituted for missing headings. Raw book paratext, wrappers, IDs and sameAs evidence are retained in the master.

Book V’s chapter-zero contents-like list remains a project/digital witness with unestablished printed-list provenance. Its V.3 wording “Over The Forty Years” agrees with the Gutenberg linked-heading defect, while the current Gutenberg index, the 1856 print and an 1784 printed control support “them”. This supports a digital relationship; it does not recover the entire conversion pipeline or establish an authentic eighteenth-century compiled list. No documented policy of systematically discarding Whiston TOCs was recovered. An earlier note about removing editorial notes is not treated as a TOC-omission policy.

The earliest inspected project revision with the Book V list is a89405e80bdebfee20ef7a25ac07c21de32ed85f. The archived project Gutenberg file is retained byte-for-byte, SHA-256 269909b2def1aa4dc338b96f972f958ad6a950a4ab531783a0cde837a7963b68. Earlier/later lineage observations are preserved in ACCEPTED_whiston_git_lineage.json.

## Printed source qualification

1737 was bibliographically identified through Soane, Eton, Google Books and ESTC-linked resources, but no complete accessible page-image source was established. HathiTrust returned HTTP 403; the ECCO/Folger endpoint returned no usable page content. Catalogue descriptions cannot certify heading wording or the physical meaning of “Contents”.

The 1741 Google scan is **Dublin, R. Reilly for George Ewing, Vol. I**, identified from its title image. It covers Antiquities I–III, following substantial preliminary dissertations. Book I’s interval and Preface appear at p. 285, Chapter I at p. 290, and Book III ends at p. 466. The title, selected preliminary leaves, opening and final pages were visually checked. The full preliminary sequence and additional volumes were not established. No absence-of-contents claim is made for 1741.

The 1784 Newcastle volume is earlier and covers I–XX, but its impressions are faded/damaged and its final text ends at p. 706 with the catchword “here”, followed by a blank scanned page. It is incomplete at the end of XX.11. It confirms V.3’s “them” at p. 152 / PDF page 162. The consistent twenty-book candidate is therefore based on 1856, without importing earlier wording into it. This is the first located complete usable control adopted for this audit, not a claim that 1856 is the earliest surviving or potentially accessible edition.

## Integrity and reproducibility

Canonical baseline and final HEAD: **a48021588e0840330388a6055a97bd0f7c2cf827**, branch **v2-development**; origin identical; status clean. **All 595 tracked files and the Git index are byte-identical.** The 39 existing contents records are unchanged. No Greek/Latin/English XML, registry, renderer, stylesheet or tracked review file was written. No Git write operation occurred.

Executed QA: **78/78 PASS**, zero failures. Browser/navigation/theme testing was **NOT RUN**: this mission made no implementation. Production preservation is established by file and index hashes.

Run extract_all.py to reproduce the archived digital extraction; build_packet.py to combine the manual visual ledger, source comparisons and proposed TEI; validate_packet.py for counts/schema/integrity; write_reports.py for reports; finalize_manifest.py for the final inventory. Retrieval scripts and logs preserve URLs and acquisition hashes; network responses may subsequently change. Rendering scripts reproduce evidence images. Automated scripts do not replace visual source reading.

WHISTON_EDITORIAL_DECISIONS.md contains the three approval questions; WHISTON_PRINTED_CONTENTS_AUDIT.md defines the bibliographical inspection scope; WHISTON_INTEGRATION_PLAN.md describes the data-only proposal. FILE_MANIFEST.json gives the complete list of newly created files and their hashes, excluding itself to avoid recursion. Its separately reported SHA-256 identifies the manifest.
