# Manuscript annotation display: reconnaissance

26 October 2026. Read-only examination preceded application changes. Base: current remote `v2-development`, `519d607b890f76bf48e427529c4278151a124326`. Feature branch: `feature/manuscript-annotation-display-v3`.

## Source and reader architecture

The site is a Jekyll application with CETEIcean and a JavaScript reader. No new framework or site dependency is required. The relevant source is `assets/xml/{antiquities,bellum}/Latin/*.xml`; the renderer is `assets/js/renderTei.js`; the bottom accordion is `_includes/annotations-bar.html`. Its existing annotation switch highlights Latin alignment units.

The apparatus uses `<app>` groups containing `<rdg>` elements. The first reading supplies a Latin passage incipit and normally a `source="#latin-…"` alignment reference. Subsequent readings contain manuscript notation and normally a `source="#manuscript-siglum"`. Several hands, numbered annotations, categories and folio sides can share one reading. Consequently a reading, an apparatus group, and an individual annotation are different counting units.

| Source | Apparatus groups | Manuscript reading records | Original annotation XML IDs |
|---|---:|---:|---:|
| Antiquities | 864 | 1,692 | 0 |
| Bellum | 549 | 1,266 | 0 |
| Total | 1,413 | 2,958 | 0 |

The group count includes empty/incipit-only groups. The 2,958 figure counts subsequent readings, including eight without a `source` attribute and one folio-only reading. First-reading incipits are never counted as manuscript annotations. Antiquities also contains 64 `<note>` elements with certainty/uncertainty or unspecified types. They remain untouched; they are not merged into or duplicated in the apparatus display. Bellum has no `<note>` elements. Manuscript reading attributes supply source references; they do not supply structured hand identifications. Certainty metadata on inline notes does not identify hands.

The previous renderer displayed raw alignment IDs and each reading's notation without interpreting the recovered key. It assumed that source references were present and manuscript witnesses could always be found. It used substring matching for passage identity, which could confuse, for example, `num27` and `num274`. The implementation now matches full IDs or complete `sameAs` tokens.

## Source-grounded examples

- Antiquities I, `latin-book01-num27`, Bern 118: `[¤2r] (@1 correction avec signe) lucem`. The hand is 1; `1` is the original annotation number; `correction avec signe` is retained as a description.
- Antiquities I, `latin-book01-num34`, Bern 118: `[¤2v] (§) dicit (@1) issa (#2 nota NT)`. This reading contains an untranscribable component, a Hand 1 textual annotation, and a symbolic annotation with its supplied description.
- Antiquities I, `latin-book01-num67`, Pal. lat. 814: `[¤2av](¢1)dicit adam diluuiam prophetasse`. The reference `2av` is retained; it is not simplified to `2v`.
- Bellum I, `latin-bellum1-num1`, Bodmer 99: `[¤1r] (@1) incipit liber XIII`.
- Bellum I, `latin-bellum1-num31`, Chartres 29: `[¤4] (#1 nota NT) (@1) d(imitte) onie et ...`. The numbered symbol and textual annotation are independent. This is the corpus's one unambiguous three-word terminal ASCII-ellipsis example.
- Bellum V, `latin-bellum5-num11`, Pal. lat. 1992: `[122v]`. This preserves folio information but encodes no annotation to count.

## Additional editorial evidence received during reconnaissance

The editor's original counting instructions supplied in this chat confirm that `(@1)` and `(@2)` enumerate separate annotations in a cell; the symbol identifies the hand. They confirm first-occurrence marking for each folio side, repeated unmarked references in later cells, and folio changes inside a cell. They also explicitly illustrate `@ §`, so category and hand must be independent.

Point 4 of that historical message says “Disons §” while giving an example ending in `...`; point 5 uses `§` for inability to transcribe. The implementation follows the examples and the recovered key: terminal `...` in the supported three-word pattern means deliberate abbreviation; `§` means cannot be transcribed. The wording conflict is recorded rather than silently erased.

## Exceptions reported before interpretation

The recovered key does **not** explain every observed pattern. See [the notation inventory](NOTATION-INVENTORY.md) and the record-level exception register in [notation-qa.json](notation-qa.json).

Follow-up of 27 October: the editor confirmed the exact historical hand sequence through Hand 9. This resolves the roles and numbers of the observed `¬`, `¦` and `³` prefixes; bracketed `¤` retains its distinct folio role. The initial uncertainty is superseded by this explicit confirmation, not by an inferred numbering scheme. See [the historical hand-key report](HISTORICAL-HAND-KEY.md) for the evidence, counts and source examples. Other malformed notation, ambiguous ellipses and source-association defects remain exceptions.

There are 21 manuscript reading records with unverified passage associations: 19 in Antiquities and two in Bellum. Defects include missing first-reading references, manuscript identifiers in passage-reference positions, and a cross-book reference whose relationship to the source-book incipit is unresolved. These records remain visible at their source-book level under “Textual citation not verified”. No reference is repaired from an incipit, neighbouring entry or apparent numerical similarity. Their original association values remain available in scholarly details and in the exception register.

Ten reading records have unresolved manuscript references, including absent references, an external alignment reference in manuscript position, and `#latin-book11-num195` used for a manuscript reading. They are retained, not reassigned to a likely witness.

Two shelfmark expansions conflict with the current manuscript repertory. `MilanBACimelioSP` names `Cimelio S.P. 11/1` in `listWit`, while the repertory has `Cimelio 1` / `II/1`. `RomeBAVPallat1992` names `Pal. lat. 1992`, while the repertory has `Vat. lat. 1992`. The source designations remain unchanged in the display. These affect 444 reading records; this is a reference-verification flag, not a claim that those transcriptions are defective.

## Preservation and identifiers

Canonical XML, symbols, folio notation, source ordering, manuscript references and original associations are inputs only. The source records contain no original annotation IDs. The interface therefore reports that fact and uses deterministic presentation anchors derived from work, source book, original passage reference, original manuscript reference and occurrence. Component anchors add the original notation's character offset. Display numbering does not determine identity. These anchors are not inserted into XML and are not represented as canonical scholarly identifiers.

All 166 production XML files are checked against the development Git bytes and the existing corpus authority guard. No canonical XML, segmentation registry, concordance, DEH parallel, hosting configuration or CNAME is changed.
