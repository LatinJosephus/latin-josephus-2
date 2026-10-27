# English editorial notes

26 October 2026. Follow-up to the manuscript annotation display redesign.

The English interface now translates the French editorial descriptions and comments. For example, `correction avec signe` displays as **Editorial note: correction with a sign**. Within recorded wording, `de pacto ad * (mot effacé?)` displays as `de pacto ad * (erased word?)`, with the editorial comment distinguished from the Latin and marked as English for screen readers.

The translation glossary explicitly accounts for all **216 distinct prefix descriptions** found in the frozen apparatus. This includes technical labels already in Latin or English, which remain unchanged. Following the [confirmed historical hand key of 27 October](HISTORICAL-HAND-KEY.md), **426 description occurrences** receive English translations and **86 editorial text spans** remain within recorded wording. Some material previously translated inside unresolved notation is now a separate prefix description, including “in a Gothic hand”. These are presentation counts, not additional manuscript annotations. The original translation-only certification counted 425 descriptions and 94 inline spans.

Source uncertainty is retained: “face?”, “possibly deterior”, “later hand”, and “13th–14th century?” do not acquire new certainty, dates or hand numbers. Where a source typo makes the position unclear (`en marge du bad`), the display says “in the margin; position unclear in the source”; it does not invent a bottom-margin location. Supplied descriptions of erasure or poor scanning are translated as the editor's observations, without applying those causes to other untranscribable annotations.

Exact phrase matching is confined to inspected editorial material. Latin expansions such as `d(imitte)`, `(milia)` and `(nomini? Nostri?)` are preserved. The source reading `rachel docet moysenà` also remains exact: its final accented character is not treated as a French comment or silently corrected. Quoted signs and suggested Latin readings inside editorial descriptions remain as recorded.

French manuscript institution names receive English display designations, such as “Chartres, Municipal Library” and “Martin Bodmer Foundation”. Their original designations remain available in scholarly details. The French interface continues to use the original French descriptions and comments.

The complete original notation, including every French word, remains unchanged in scholarly details and canonical XML. Translation preserves source ordering, identifiers, folio references, associations and citation mappings. The separate historical hand-key follow-up establishes additional hand classifications and one explicit component boundary; it does not alter the source. No DEH annotation convention is introduced.

Implementation: `assets/js/annotationEditorialEnglish.js` contains the explicit glossary; the shared annotation component applies it only in the presentation layer. Ten translation tests cover source-description coverage, mixed Latin/editorial material, exact preservation across all 2,958 reading records, uncertainty, French-mode behaviour, manuscript names and the unconfigured DEH adapter. The current suite has **45 annotation/citation/translation tests** and **five Python citation/preservation tests**. Existing corpus, DEH and search asset guards are also rerun; the search implementation and its previously certified 565-test suite are unchanged.

[English description screenshot](screenshots/english-editorial-correction.png) · [Mixed Latin/comment screenshot](screenshots/english-editorial-mixed.png).
