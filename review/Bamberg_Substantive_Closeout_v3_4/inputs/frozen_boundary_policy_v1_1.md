# Operative transcription policy — recovery v1.1

The user’s follow-up explicitly resolves word separation at manuscript layout boundaries:

> Where two complete words occur on opposite sides of a manuscript layout boundary, the digital transcription must preserve their separation. Where a single word continues across such a boundary, no artificial space is introduced into its reconstructed reading.

This supplements the frozen v1 policy, retained in `inputs/original_records/editorial_policy.md`, and the standing preservation instructions in `inputs/BAMBERG_TRANSCRIPTION_AUDIT_META.txt`. It does not establish a new spelling, abbreviation or punctuation policy.

| Feature | Permissible evidenced repair | Editorial normalization excluded |
|---|---|---|
| Two complete words across column/page/line boundary | Insert one separator in the existing text slot when image and retained lineation establish both words; keep the exact marker | Insert spaces around every TEI milestone |
| One word across a boundary | Preserve the reconstructed word without a space | Split `Fon/tes`, `tem/pore`, `capti/ui`, `azi/morum`, `similitu/dinem`, `calami/tas` |
| Inline Niese markers | Preserve their exact attributes, order and tree positions; edits remain within one interval | Move a marker to accommodate a preferred text division |
| Letter omission/substitution or repeated token | Correct only an unequivocal image-supported digital error with two separate blind readings | Regularize a strange form or remove an authentic scribal repetition by grammar or frequency |
| Abbreviations | Retain established expansion/retention and protected `expan`; target repairs do not introduce new expansions | Resolve uncertain contractions by lexical expectation |
| u/v, i/j, e/ę and spelling | Preserve frozen forms unless a registered manuscript reading proves a transcription error | Standardize medieval orthography or names |
| Punctuation/capitalization | Preserve frozen usage; no repairs dependent on undocumented policy | Re-punctuate or recase for readability |
| Additions, deletions, gaps, uncertainty and apparatus | Preserve all markup, attributes and enclosed editorial text | Fill protected lacunae from an edition or silently settle uncertainty |

Exactly five Book IX column separators satisfy the new rule. Each proposal inserts a literal ASCII space immediately before the existing `<cb n="2/2"/>`, without changing the marker. A manuscript layout transition is not itself a word-space character in the XML reading. The six named continued-word controls remain byte-identical.

The original transcription instructions specify line-by-line transcription, retention of ę, and ordinary certain abbreviation expansion, with uncertain expansion marked. Documentation remains incomplete for a comprehensive u/v–i/j or punctuation policy; those areas are unchanged. No new hyphenation policy is inferred. Crops are evidence extraction, not regenerated T-PEN layout polygons.
