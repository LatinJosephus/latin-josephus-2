# Greek Antiquities capitula audit — 8 October 2026

All nine missing Greek book lists are recovered and classified PRINT_VERIFIED: I, II, III, IV, VI, VII, VIII, IX and X. They contain **109 numbered source entries**, nine contents headings, nine duration formulae and one additional unnumbered Book I proem-summary rubric. Nine separate companion TEI proposals validate against the project's existing TEI schema. They are ready for incorporation after human acceptance of this packet; nothing has been installed.

The lists are source paratext. Their labels are not traditional Chapter/Subchapter, Niese citation, Bamberg division or Alignment-unit identities. No narrative target links or structural concordances have been created.

| Book | Printed entries | Perseus entries | Matching | Discrepancies | Status | Ready for integration |
| ---- | --------------: | --------------: | -------: | ------------: | ------ | --------------------- |
| I | 19 | 19 | 17 | 2 | PRINT_VERIFIED | YES, after packet acceptance |
| II | 8 | 8 | 2 | 6 | PRINT_VERIFIED | YES, after packet acceptance |
| III | 10 | 10 | 10 | 0 | PRINT_VERIFIED | YES, after packet acceptance |
| IV | 5 | 5 | 5 | 0 | PRINT_VERIFIED | YES, after packet acceptance |
| V (control) | 14 | 14 | 14 | 0 | PRINT_VERIFIED | Accepted control retained; separate encoding issue |
| VI | 15 | 15 | 15 | 0 | PRINT_VERIFIED | YES, after packet acceptance |
| VII | 12 | 12 | 10 | 2 | PRINT_VERIFIED | YES, after packet acceptance |
| VIII | 12 | 12 | 12 | 0 | PRINT_VERIFIED | YES, after packet acceptance |
| IX | 16 | 16 | 16 | 0 | PRINT_VERIFIED | YES, after packet acceptance |
| X | 12 | 12 | 10 | 2 | PRINT_VERIFIED | YES, after packet acceptance |

“Matching” and “Discrepancies” compare the elected print text with **current Perseus grc2**, after only the declared glyph/encoding equivalences. They include bracket-scope and punctuation differences; they do not suppress words or accents. Totals for the nine targets are 97 matching and 12 discrepant entries. All 109 printed labels have numeral-stroke/encoding differences from the raw digital labels, retained individually in the collation. The legacy Hopper serialization adds punctuation variants at III.7, X.5 and X.8. Canonical omissions are a separate comparison, not included in the print/current matching column.

| Book | Volume | Printed pages | PDF pages (1-based) | Source label sequence |
| --- | --- | --- | --- | --- |
| I | I | 3, 4 | 93, 94 | αʹ. βʹ. γʹ. δʹ. εʹ. ϛʹ. ζʹ. ηʹ. ϑʹ. ιʹ. ιαʹ. ιβʹ. ιγʹ. ιδʹ. ιεʹ. ιϛʹ. ιζʹ. ιηʹ. ιϑʹ. |
| II | I | 82 | 172 | αʹ. βʹ. γʹ. δʹ. εʹ. ϛʹ. ζʹ. ηʹ. |
| III | I | 157, 158 | 247, 248 | αʹ. βʹ. γʹ. δʹ. εʹ. ϛʹ. ζʹ. ηʹ. ϑʹ. ιʹ. |
| IV | I | 223 | 313 | αʹ. βʹ. γʹ. δʹ. εʹ. |
| V | I | 291, 292 | 381, 382 | αʹ. βʹ. γʹ. δʹ. εʹ. ϛʹ. ζʹ. ηʹ. ϑʹ. ιʹ. ιαʹ. ιβʹ. ιγʹ. ιδʹ. |
| VI | II | 3, 4 | 11, 12 | αʹ. βʹ. γʹ. δʹ. εʹ. ϛʹ. ζʹ. ηʹ. ϑʹ. ιʹ. ιαʹ. ιβʹ. ιγʹ. ιδʹ. ιεʹ. |
| VII | II | 88, 89 | 96, 97 | αʹ. βʹ. γʹ. δʹ. εʹ. ϛʹ. ζʹ. ηʹ. ϑʹ. ιʹ. ιαʹ. ιβʹ. |
| VIII | II | 176, 177 | 184, 185 | αʹ. βʹ. γʹ. δʹ. εʹ. ϛʹ. ζʹ. ηʹ. ϑʹ. ιʹ. ιαʹ. ιβʹ. |
| IX | II | 267, 268 | 275, 276 | αʹ. βʹ. γʹ. δʹ. εʹ. ϛʹ. ζʹ. ηʹ. ϑʹ. ιʹ. ιαʹ. ιβʹ. ιγʹ. ιδʹ. ιεʹ. ιϛʹ. |
| X | II | 328, 329, 330 | 336, 337, 338 | αʹ. βʹ. γʹ. δʹ. εʹ. ϛʹ. ζʹ. ηʹ. ϑʹ. ιʹ. ιαʹ. ιβʹ. |

The shared PDF directory contains all four Niese volumes. Their title pages establish I (1887, I–V), II (1885, VI–X), III (1892, XI–XV), and IV (1890, XVI–XX and Vita). All nine target lists are fully present in volumes I and II; there is no scan gap and no need to import another edition. Volumes III and IV were inventoried and their title pages checked only. Full bibliography and hashes are in SOURCE_AUTHORITY.md and FILE_MANIFEST.json.

Each heading, Roman book label, numbered entry and concluding formula was read directly from the retained page images. Extracted PDF text located pages but did not certify Greek or numerals. VISUAL_INSPECTION_REGISTER.json contains 154 ten-book component checks, including 137 target checks on 17 target contents pages; Book V adds two control pages. Sensitive punctuation, readings and bracket scope were rechecked in retained close-ups. Additional printed addenda checks are recorded separately.

Book I is not a synthetic introduction. Its contents appear on printed pp. 3–4, preceded by the Roman I and the contents heading. The unnumbered “Προοίμιον περὶ τῆς ὅλης πραγματείας.” is a contents rubric, followed by 19 labelled entries. The actual general proem begins below the duration formula on p.4/PDF94, “Τοῖς τὰς ἱστορίας συγγράφειν βουλομένοις…”, citation1. The Book I narrative begins on p.9/PDF99, “Ἐν ἀρχῇ ἔκτισεν ὁ ϑεὸς τὸν οὐρανὸν καὶ τὴν γῆν.”, citation27. The proposals contain the list and rubric only.

The elected readings follow print. I.16 has Ἁβράμου against digital Ἁβράμῳ; I.18 has διὰ against digital καὶ. II.1 lacks the digital comma after ὄντες, but retains the printed comma after κατέσχεν. Book II's continuous square-bracket group runs from immediately before δʹ. through entries4–8 and the closing formula; Perseus marks only the fourth label and closing as del. Its Exodus entry precedes its Moses-birth entry in the printed source, and that order remains. VII.5 has [καὶ], VII.6 αὐτῷ against digital αὑτῷ; X.4 has [αὐτὴν], X.9 αὐτὸν against digital αὑτὸν. IX.15 ends with a comma and IX.16 begins καὶ under its own label. X.6 crosses pp. 328–329 within Ἱεροσόλυμα; the complete list ends on p. 330, not p. 329. RESOLVED_DIFFERENCES.tsv and the collation preserve both witnesses and exact loci.

Printed editorial brackets are preserved literally, not styled as manuscript-loss supplements or silently enacted as deleted text. Critical-apparatus alternatives are not inserted into the main lists. Niese's addenda include further evidence for Book I entry4 and Latin witnesses to the I/V duration formulae, but no instruction was found to change the elected main-list readings. Book VI remains15 separately printed entries even where the apparatus reports other witnesses joining two.

Current production has empty contents wrappers in I–IV and VI–VIII. IX and X retain their duration formulae only. A full heading/first-entry search across all 114 production XML files found no displaced copy of the missing lists. The earliest two accessible revisions of each target Greek file already have these omissions or partial survivals. The exact conversion operation that discarded the lists is not established; the 2004 Perseus note-classification revision is relevant context, not proof of causation. Existing V and XI–XX registrations remain accepted controls and are unchanged.

Book V has a separate production encoding issue: a literal [στιγμα]. token trails entry5, and entry6 has ς -- rather than the printed numeral-six label. The Greek wording of all 14 control entries agrees after declared glyph equivalence. No Book V proposal or repair is included. GREEK_CAPITULA_REVIEW.md isolates the one decision requiring separate approval.

Executed QA: **91 PASS, zero FAIL**, including nine companion schema validations, one registry-fragment schema validation, exact entry/head/rubric/trailer export checks, all digital retrieval hashes, and protected-input integrity. Canonical remains branch v2-development, HEAD/origin f393fa1223b38d9ca114e583fcc57d5e34425815, clean, with the same index hash. All 499 baseline tracked files and all four PDFs are byte-identical. No source XML, registry, renderer, CSS, certification packet, other work, or other worktree was written. Ignored generated files were not part of the hash baseline; this audit made no writes to them. No Git write operation occurred.

This was an audit, not a browser implementation. No site build or navigation/browser regression is claimed. The integration plan requires only nine companion additions and nine source-contents registrations; it identifies the later browser checks. No JavaScript or CSS change is presently indicated.

The workspace is C:\workspace\LatinJosephus-Greek-Capitula-Audit-20261008. FILE_MANIFEST.json is the complete relative-path inventory and SHA-256 register for every new artifact other than itself, with all baseline source hashes. Its own SHA-256 is reported separately in the completion response. Scripts and raw downloads allow independent checking without repeating source acquisition; direct visual readings remain a separately documented scholarly step.
