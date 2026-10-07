# Book XI: current-text multi-span adjudication

The previous interpretation of Book XI as a paragraph-order defect is withdrawn. **No paragraph-reordering repair was performed or remains proposed.** All three Book XI XML files retain their original bytes, node order, text, IDs and sameAs graph.

The user supplied Levenson and Martin (2016), p. 330, identifying Ba with Group D and the sequence 311–312a; 326b–342a; 312b–326a; 342b–347, including portions of Bellum 4.105. The [publisher's chapter record](https://onlinelibrary.wiley.com/doi/10.1002/9781118325162.ch21) identifies the publication. The page-330 statement is explicitly user-supplied evidence; it was not independently re-read. No frozen source-reading judgment was reopened.

## Actual current XML

Identified paragraphs in the relevant tail occur in each alignment layer as:

304, 306, 326, 329, 340, 312, 313, 321, 343, 346.

The Latin literally prints [312a], [VIII.ii.312b], [326a], [VIII.iv.326b], [342a], [342b], [BJ 4.105a] and [BJ 4.105b]. Greek/English contain whole 312, 326 and 342 passages in larger blocks; their present editorial alignment order follows the Latin arrangement at paragraph level. This does not assert that the original Greek or English editions share the Latin manuscript's order.

The table covers all material corresponding to Antiquities 11.311–347. Numbers below describe verified current content, never ID-suffix arithmetic. English ranges identify the containing corresponding paragraphs; no new word-level English citation locator for every individual Niese section is claimed.

| Canonical material | Latin physical membership | Greek / English membership | Traditional Subchapter |
|---|---|---|---|
| 311 | num306 after its [311] | num306 after [311] | XI.viii.2 |
| 312a | num306 after [312a] | whole 312 in num312 | XI.viii.2 |
| 312b | num312 after [VIII.ii.312b] | whole 312 in num312 | XI.viii.2 |
| 313–320 | num313 | num313 | XI.viii.3 |
| 321–325 | num321 | num321 | XI.viii.4 |
| 326a | num321 after [326a], ending before [342b] | whole 326 in num326 | XI.viii.4 |
| 326b–328 | num326 | whole 326–328 in num326 | XI.viii.4 |
| 329–339 | num329 | num329 | XI.viii.5 |
| 340–342a | num340 | whole 340–342 in num340 | XI.viii.6 |
| 342b | num321 after [342b] | whole 342 in num340 | XI.viii.6 |
| 343–345 | num343 | num343 | XI.viii.6 |
| 346–347 | num346 | num346 | XI.viii.6 |
| Bellum 4.105a interpolation | num306, [BJ 4.105a] → [312a] | no corresponding insertion | retained with XI.viii.2 witness fragment |
| Bellum 4.105b interpolation | num312 opening → [VIII.ii.312b] | no corresponding insertion | retained with XI.viii.2 witness fragment |

The inherited Latin [VIII.vii.346] is preserved as current-source evidence. It is not used to invent an additional traditional Subchapter identity.

## Registered half-open spans

Every start is included; every following endpoint is excluded. `num[7]` means the existing seventh direct TEI num child of Latin num321, whose actual literal reading is [342b]. No new XPath-derived stable ID was invented.

| Identity | Latin ordered spans | Greek / English ordered spans |
|---|---|---|
| XI.viii Chapter | num304 → num326; num312 → num321/num[7]; num326 → num312; num321/num[7] → Book end | num304 → num326; num312 → num343; num326 → num312; num343 → Book end |
| XI.viii.2 | num306 → num326; num312 → num313 | same paragraph endpoints |
| XI.viii.3 | num313 → num321 | same paragraph endpoints |
| XI.viii.4 | num321 → num321/num[7]; num326 → num329 | num321 → num343; num326 → num329 |
| XI.viii.5 | num329 → num340 | same paragraph endpoints |
| XI.viii.6 | num340 → num312; num321/num[7] → Book end | num340 → num312; num343 → Book end |

Full language prefixes and locators, literal nums, SHA-256 and original paragraph order are in XI_MULTISPAN_MEMBERSHIP.json. TEI uses an ordered `vColl org="list"` of `fs type="physical-span"` values in each language locator. Both scalar and list locators use the same generic resolver.

## Presentation and preservation

Book and Alignment-unit views retain unchanged XML order. Canonical Chapter/Subchapter views assemble the registered spans in canonical order. Their visible “Canonical order from separate witness fragments” disclosure lists the fragments and links to the unchanged Book view. Latin interpolation labels and text remain in their source fragments, including both Bellum portions; they are not silently dropped. Different clones of one source paragraph retain the source identity as provenance, with duplicate DOM IDs removed only from later rendered clones. Source XML IDs remain unchanged.

The resolver also passed two Latin split-citation model tests, 326 and 342, without book-specific logic. These are model tests, not public Book XI Niese navigation expansion: Phase 1 keeps the original I–VII Niese UI coverage. Later VIII–XX citation work still requires complete source-qualified locators and explicit English context/availability states.

## Two Latin projection mismatches

The earlier Chapter VIII and Subchapter 6 mismatches were 18 trailing whitespace characters caused by nested TEI body elements: the resolver ended at the closest inner body while the independent test used the complete outer body. There was no missing lexical text, bad start locator or additional witness transposition. The generic Book-end resolver now uses the complete loaded body. All current corpus bytes remain unchanged; the restarted exhaustive projected-range checks pass.

## QA

XI_MULTISPAN_GATE_QA.json records 18/18 language ranges, two split-citation model checks, no overlapping membership within a selection, Chapter/Subchapter partition equality, preserved interpolation, disclosure, and exact baseline equality of Book/Alignment-unit paragraph views. The full restarted suite passes all 1,689 identities / 5,067 language cases: 5,034 executable ranges and 33 explicit expected Book IX unavailable cases. Book XI contributes 183 executable cases without unavailable states. No scholarly identity or independent verification status changed.
