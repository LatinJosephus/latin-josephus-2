# Editorial notation inventory

Updated 27 October 2026 with the editor-confirmed [historical nine-hand key](HISTORICAL-HAND-KEY.md). Counts below are literal occurrences in the 2,958 manuscript reading records, excluding first-reading Latin incipits. Counts are not automatically counts of annotations or distinct folios.

| Notation | Antiquities | Bellum | Treatment |
|---|---:|---:|---|
| `¤` | 1,309 | 1,117 | First-folio-reference marker in recognised bracketed folio syntax; confirmed Hand 4 in parenthesised annotation prefixes, of which none occur here; malformed occurrences retained and flagged |
| `@` | 862 | 1,619 | Hand 1 in recognised annotation prefixes |
| `£` | 826 | 183 | Hand 2 in recognised annotation prefixes |
| `¢` | 225 | 33 | Hand 3 in recognised annotation prefixes |
| `#` | 1,072 | 1,028 | Symbolic annotation; supplied descriptions retained |
| `§` | 213 | 62 | Cannot be transcribed; independent of hand |
| `...` | 7 | 1 | One supported terminal three-word example; other roles unresolved |
| `…` | 82 | 29 | Retained; not automatically equated with deliberate abbreviation |
| `¬` | 26 | 20 | Hand 5 in recognised annotation prefixes; confirmed 27 October |
| `¦` | 30 | 6 | Hand 6 in recognised annotation prefixes; confirmed 27 October |
| `²` | 0 | 0 | Confirmed Hand 7; absent from current reading records |
| `³` | 1 | 1 | Hand 8 in recognised annotation prefixes; confirmed 27 October |
| `¼` | 0 | 0 | Confirmed Hand 9; absent from current reading records |

Other parenthesised prefixes include `+` (two components), `?` (two) and `*` (one). They receive no invented meaning. Asterisks and other punctuation inside transcription are retained literally. Malformed delimiters, `[@4]`, `[#triangle]`, `[¤…]`, and unusual bracketed material remain in the display and exception register. No global character replacement is performed.

## Counting and interpretation

| Interpreted components | Antiquities | Bellum | Total |
|---|---:|---:|---:|
| Textual (including one confirmed partial transcription) | 1,954 | 1,860 | 3,814 |
| Symbolic | 1,061 | 1,028 | 2,089 |
| Cannot be transcribed | 206 | 62 | 268 |
| Unresolved | 23 | 8 | 31 |
| All components | 3,244 | 2,958 | 6,202 |

The 6,202 figure is a presentation-component inventory, **not a certified total of manuscript annotations**: unresolved syntax may require editorial adjudication. The additional component compared with the earlier 6,201 count separates the explicit `(³1)yo` annotation from the preceding `tertium` in Bodmer 98. One additional reading contains only a folio reference and creates no numbered annotation. No annotation is created by a folio marker alone.

The table inventories original XML records only. The [approved Book I supplement](EDITORIAL-READINGS-20261027.md) adds three entries from one recovered worksheet cell, for 6,205 components in the combined display. Bern 118's surviving `dicit` now has partial-transcription status; its preceding untranscribed material and provisional David reading are explicitly distinguished.

Thirteen components identify a hand but supply no transcription outside the prefix description. They display “No transcription recorded”, retain the description and hand, and are not automatically classified as untranscribable or symbolic.

The recognised hand assignments are 2,472 for Hand 1, 1,009 for Hand 2, 258 for Hand 3, 46 for Hand 5, 36 for Hand 6 and two for Hand 8. No Hand 4, 7 or 9 prefixes occur in the current readings. Another 2,379 components have no identified hand. These are independent from categories. No hand is propagated to a later symbolic or untranscribable component merely because it follows a textual annotation.

There are 2,424 recognised first-folio markers, one uncertain `[¤…]` reference and one additional malformed/literal `¤` occurrence. There are 829 recognised subsequent folio references. These counts preserve the editor's encoded sequence; they are not a deduplicated count of all annotated manuscript pages. Bare numeric references such as `[4]`, references with inserted letters such as `[2av]`, and explicit folio transitions are retained. Uncertain foliation resets the current reference to unknown rather than silently inheriting the preceding folio.

## Abbreviation evidence

The supported example is Bellum I, `latin-bellum1-num31`, Chartres 29: `d(imitte) onie et ...`. Its three recorded words and ellipsis remain exact; the interface adds “Transcription abbreviated” and explains that only the beginning was transcribed.

Other examples show why a universal ellipsis replacement would be unsafe:

- Antiquities III.26, Bodmer 98: `...na descendit` begins inside a word.
- Antiquities III.39, Bodmer 98: `quoda. ent... tibi * sunt *` has a medial ellipsis.
- Antiquities VI.1, Copenhagen: `(#1 require) (#2 require) ...` follows symbolic descriptions.
- Antiquities X.186, Milan: `(§) tiui* ... tribuam et (§) ...amaritae` combines partial words and inability-to-transcribe codes.

The parser flags 123 components in 115 records for unresolved ellipsis roles, including Unicode ellipses, partial words, medial forms and different word counts. It does not describe manuscript damage or reconstruct continuations. The original instructions' general abbreviation rule is explained in the legend, while automatic classification is confined to the directly supported pattern.

## Boundaries of interpretation

Parenthesised prefixes and bare codes at a fresh block's beginning are interpreted. Special characters within recorded wording are preserved as text and flagged where their role remains uncertain. Adjacent `(@1) (§)` and bare `@ §` preserve both hand and category. Ambiguous combinations such as `(@£)` retain the complete original notation and receive a review flag.

2,801 reading records have no notation-parser issues. The complete [machine-readable report](notation-qa.json) separates notation issues, missing passage associations, manuscript-reference conflicts and folio-only evidence; its 601 exception records must not be treated as 601 failed transcriptions.
