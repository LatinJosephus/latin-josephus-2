# Confirmed historical hand key

27 October 2026. Follow-up evidence supplied by the project editor in this task.

The assistant's additional message explains that the older symbols distinguished annotating hands. The editor then explicitly confirmed the exact numbered sequence in response to the clarification question: `@ = m1, £ = m2, ¢ = m3, ¤ = m4, ¬ = m5, ¦ = m6, ² = m7, ³ = m8, ¼ = m9`. This confirmation supplies the numbers; they are not inferred from symbol shape, annotation numbers or apparent handwriting.

| Annotation-prefix code | Public label | Antiquities prefixes | Bellum prefixes |
|---|---|---:|---:|
| `@` | Hand 1 | 855 | 1,617 |
| `£` | Hand 2 | 826 | 183 |
| `¢` | Hand 3 | 225 | 33 |
| `¤` | Hand 4 | 0 | 0 |
| `¬` | Hand 5 | 26 | 20 |
| `¦` | Hand 6 | 30 | 6 |
| `²` | Hand 7 | 0 | 0 |
| `³` | Hand 8 | 1 | 1 |
| `¼` | Hand 9 | 0 | 0 |

These are parsed hand-prefix counts, not a total of distinct historical people. They exclude literal or malformed occurrences and do not include folio markers. Hand classifications remain local to each manuscript. No dating, scribal identity or shared identity across witnesses is inferred.

## Two roles for the same character

The earlier foliation instructions remain authoritative for bracketed references. `[¤1r]` means folio 1r with its first recorded occurrence marked; it does not assign Hand 4. `[1r]` identifies the same folio without that marker. No annotation is created by a folio marker alone.

The confirmed Hand 4 meaning is available for a parenthesised annotation prefix such as `(¤2)`: the code identifies Hand 4 and the digit is the original annotation number. There are no such Hand 4 prefixes in the current manuscript readings. Likewise, `²` and `¼` are not present in these records. Their mappings are covered by explicit key fixtures, not represented as newly discovered corpus annotations. Bare additional hand symbols and symbols inside ordinary recorded text are not globally converted.

## Source examples and resulting interpretation

- Antiquities I, `latin-book01-num34`, Pal. lat. 814: `[¤2r](¬1)mulier` now identifies Hand 5; folio 2r remains independent.
- Antiquities II, Leiden VLF 17: `[20v](¦ 1)exercitus aegyptiorum` identifies Hand 6 and source annotation number 1, preserving the spaced original notation.
- Antiquities III, `latin-book03-num153`, Bodmer 98: `(@1)tertium (³1)yo` contains two annotations, by Hand 1 and Hand 8. The folio is 72v in the full source reading. The additional boundary follows the explicit prefix already in the source.
- Bellum VII, `latin-bellum7-num5`, Bern 50: `[¤214v] (³1 dans une main gothique) liber paris (£2) deus meus` identifies Hands 8 and 2. The English presentation translates the supplied description as “in a Gothic hand”; it does not infer that description for other Hand 8 records.

`#` remains a symbolic annotation and `§` remains inability to transcribe. A hand code does not imply either category; conversely a category does not imply a hand. The actual Hand 6 prefix followed by `§` retains both meanings independently.

## Preservation and QA

All 2,958 original manuscript reading records, 2,937 verified citation associations and 21 documented association exceptions are preserved. There are now 6,202 presentation components, compared with 6,201 under the earlier key: the one additional component separates the explicitly marked Bodmer Hand 8 annotation `yo` from `tertium`. No source annotation was created or edited. Existing source-record anchors and earlier component offsets remain stable; display numbers may change when the source contains an additional recognised boundary.

The 84 observed additional hand prefixes resolve as Hand 5 (46), Hand 6 (36) and Hand 8 (2). Unresolved components decrease from 114 to 31. Original notation, descriptions and Unicode characters remain in scholarly details. The source-specific Josephus adapter is still not imposed on DEH.

The current automated suite contains 45 annotation/citation/translation tests plus five Python citation/preservation tests. It covers all nine mappings, the two roles of `¤`, literal symbols, the newly separated source component, spaced source numbering, category independence, full-corpus preservation and English/French output. Updated source counts and remaining exceptions are recorded in [notation-qa.json](notation-qa.json).
