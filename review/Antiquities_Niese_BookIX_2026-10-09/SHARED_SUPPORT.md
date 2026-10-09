# Minimal reader support for IX

The frozen renderer remains the implementation base. It adds IX's identity-registry path beside VIII/X, reuses the existing exact Greek/Latin view and broader Whiston context, and adds two generic opt-in data behaviors.

`excludedNarrativeParagraphs[language]` removes only explicitly listed editorial placeholder paragraphs from a derived exact Niese interval. This prevents the unnumbered IX.51–109 placeholder from being included in IX.50. Original XML and ordinary book, chapter, Bamberg and Alignment views retain the paragraph.

Context views honor a language's explicit `available: false` identity data, returning the existing structural-unavailable presentation. Thus IX.51–109 can independently report the actual English omission instead of pretending that `***` is narrative context. Other English selections retain the existing broader-context behavior, and no English source file is edited.

No display-settings change, redesign, unrelated reader fix or global configuration change is needed. The opt-in fields are absent from VIII/X registries, so their established behavior remains protected by baseline comparison. Corpus commits and this shared support commit are separate.
