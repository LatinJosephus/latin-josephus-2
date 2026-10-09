# Whiston Book III adjudication — 9 October 2026

Both outstanding 1856 readings are securely resolved. III.8 has **no terminal full stop**. III.15 confirms **CONTINUE IN THE WILDERNESS FOR FORTY YEARS**, the six specified commas and the final full stop.

The accepted audit’s original proposed heading strings were correct. This supplement changes their certification and review annotations, not their wording. The original 343-file audit remains untouched.

The primary processed PDF was compared with the Toronto original colour scan and a separately held University of Illinois copy of the same 1856 Alden & Beardsley printing. The Illinois title page and library leaf were visually checked. Earlier controls were located and read at 1741 pp. 441 and 464 and 1784 pp. 87 and 100. No OCR reading determined the adopted text.

III.8’s earlier editions print a point; both 1856 copies omit it. III.15’s earlier editions differ in punctuation and capitalization, with literal brackets around the parenthetic phrase. Those variants are preserved independently. Some 1784 letters remain degraded and are expressly qualified; they are not used to manufacture certainty about 1856.

Evidence, raw digital witnesses, current canonical checks and exact pixel/page locators are in EVIDENCE_REGISTER.json, FINAL_CROP_LOCATORS.json, III_8_EVIDENCE.md and III_15_EVIDENCE.md. Source images are untouched. Enhanced crops use only documented grayscale, restrained contrast and enlargement. Adjacent-page/crop locating attempts are retained but excluded as authorities in LOCATOR_ATTEMPTS.json.

Derived files are under derived/: a complete twenty-book master, the fifteen-record Book III extract, the two-case update register and the corrected Book III TEI proposal. Only III.8 and III.15 status/provenance annotations are superseded; all other headings remain unchanged. The old provisional note and unclear wrapper are removed in the derived proposal. Original versions and identifiers remain recoverable in the accepted audit.

All 256 proposed heading texts are now ready, subject to human approval of the governing 1856 edition and the compiled-index presentation. Nothing here claims first-edition 1737 verification or implements the website.

QA.json records executed schema, entry, text, crop and preservation checks. FILE_MANIFEST.json lists all supplement files except itself; its own SHA-256 is reported separately. Reproduce with prepare_final_evidence.py, build_supplement.py, validate_supplement.py and finalize_manifest.py. Acquisition scripts save sources separately and refuse to overwrite their downloads; subsequent network images may change.

## Executed QA

37/37 checks PASS; 0 failures. All fifteen Book III headings remain present; the derived TEI passes the accepted TEI_all schema. All 256 heading strings remain unchanged. The original 343-file packet, all 595 tracked canonical files and the Git index remain byte-identical. Canonical branch/HEAD/origin/status remain unchanged. No website implementation or Git write operation occurred.
