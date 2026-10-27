# English editorial notes

26 October 2026. Follow-up to the manuscript annotation display redesign.

The English interface now translates the French editorial descriptions and comments. For example, `correction avec signe` displays as **Editorial note: correction with a sign**. Within recorded wording, `de pacto ad * (mot effacé?)` displays as `de pacto ad * (erased word?)`, with the editorial comment distinguished from the Latin and marked as English for screen readers.

The translation glossary explicitly accounts for all **216 distinct prefix descriptions** found in the frozen apparatus. This includes technical labels already in Latin or English, which remain unchanged. Across the corpus, **425 description occurrences** receive English translations. The display also identifies **94 editorial text spans**, covering French parenthetical comments, complete editorial remarks, and a few malformed notations whose French words can be translated without interpreting their syntax. These are presentation counts, not additional manuscript annotations.

Source uncertainty is retained: “face?”, “possibly deterior”, “later hand”, and “13th–14th century?” do not acquire new certainty, dates or hand numbers. Where a source typo makes the position unclear (`en marge du bad`), the display says “in the margin; position unclear in the source”; it does not invent a bottom-margin location. Supplied descriptions of erasure or poor scanning are translated as the editor's observations, without applying those causes to other untranscribable annotations.

Exact phrase matching is confined to inspected editorial material. Latin expansions such as `d(imitte)`, `(milia)` and `(nomini? Nostri?)` are preserved. The source reading `rachel docet moysenà` also remains exact: its final accented character is not treated as a French comment or silently corrected. Quoted signs and suggested Latin readings inside editorial descriptions remain as recorded.

French manuscript institution names receive English display designations, such as “Chartres, Municipal Library” and “Martin Bodmer Foundation”. Their original designations remain available in scholarly details. The French interface continues to use the original French descriptions and comments.

The complete original notation, including every French word, remains unchanged in scholarly details and canonical XML. Annotation components, ordering, identifiers, folio references, hand classifications, source associations and citation mappings are unchanged. No DEH annotation convention is introduced.

Implementation: `assets/js/annotationEditorialEnglish.js` contains the explicit glossary; the shared annotation component applies it only in the presentation layer. Ten additional tests cover source-description coverage, mixed Latin/editorial material, exact preservation across all 2,958 reading records, uncertainty, French-mode behaviour, manuscript names and the unconfigured DEH adapter. All **34 annotation tests** and **five citation/preservation tests** pass. Existing corpus, DEH and search asset guards are also rerun; the search implementation and its previously certified 565-test suite are unchanged.

[English description screenshot](screenshots/english-editorial-correction.png) · [Mixed Latin/comment screenshot](screenshots/english-editorial-mixed.png).
