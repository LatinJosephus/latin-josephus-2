# Book VII: independent traditional locator, unchanged alignment defect

The actual base-commit Latin opening is the unique paragraph `latin-book07-num`, printing [I.i.1] and beginning “Praedictum itaque praelium, gestum est die qua dauid…”. Greek and English openings contain the corresponding account of the battle and David's return, in `greek-book07-num1` and `english-book07-num1`.

The frozen current-text overlay was unmapped for Latin VII.i / VII.i.1. The implementation registry now directly references the existing Latin opening edge. This allows traditional navigation to operate without repairing the known Greek/English sameAs target #latin-book07-num1. No XML ID was renamed, no sameAs was changed, and the existing alignment-target defect remains documented for a separate task. Frozen source identities, citation association and independent source status remain unchanged. Exact evidence and replacement fields are in VII_CURRENT_LOCATOR.json.
