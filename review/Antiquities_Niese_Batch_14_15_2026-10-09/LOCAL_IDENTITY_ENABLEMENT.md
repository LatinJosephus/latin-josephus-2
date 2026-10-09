# Local identity-registry enablement

The frozen reader already supports per-book Niese identity registries, qualified correspondence notes, independently unavailable Latin sections and separate Greek/English access. The local configuration adds only `15: "assets/xml/antiquities/niese/book-15.json"` to that existing map. No viewing flow or shared algorithm is changed by this entry. XIV remains outside production availability until its review and certification are complete.

XV's registry has 425 selectable identities, 423 available Latin intervals and independently verified unavailabilities 338 and 347. Source files and this book-specific data are committed separately from shared configuration. The published baseline stays at 3,157; local XV adds 425 selections, giving 3,582 locally. No publication is performed.

The fresh isolated build is `C:\workspace\Antiquities-Niese-14-15-runtime-20261009\build4\site`. XV uses its actual production registry, with no identity data injected by the QA server. `FULL_READER_QA.json` records every selection, chapter/subchapter completeness, deep links, history, pane controls, unique IDs and themes. Shared `PROTECTED_COMPLETE_EXISTING_BOOKS_BROWSER_QA_build4.json` records protected baseline behavior, including the accepted VIII/X controls. Narrow inherited Book-I exceptions remain as previously recorded.
