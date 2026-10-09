# Integration plan — proposal only

Add approved companion files at assets/xml/antiquities/paratext/whiston/book-NN-contents.xml using the existing paratext architecture. Twenty external proposed-tei files are supplied. Book III remains provisional until its two reading decisions are resolved.

The proposed TEI has div type="contents", subtype="editorially-compiled-chapter-index", the heading “Whiston’s chapter headings (compiled index)”, an editorial arrangement note, edition bibliography, book/interval headings and list/label/item in printed order. Roman labels belong to Whiston’s printed chapter system; they are not traditional navigation identities. No narrative targets or Niese equivalences are asserted. Printed asterisk/dagger pointers remain marked; their note bodies lie outside the index and are recoverable in the scans.

## Registry additions

After editorial acceptance, add twenty records to assets/xml/source-contents.xml, preserving every existing record and attribute. Use the actual project fs/f serialization:

- work: string “antiquities”.
- book: string “1” through “20”.
- language: string “English”.
- witness: string “whiston”, matching the current renderer’s registered source identity.
- status: string “VERIFIED” only after approval of the associated data.
- path: string “assets/xml/antiquities/paratext/whiston/book-NN-contents.xml”, **without a leading slash**, matching existing registry paths.
- selectors: vColl org="list" containing string `tei-div[type="contents"]`. The field name is plural.
- note: concise statement identifying the 1856 edition and editorial compilation.
- authority: identified 1856 witness and this audit.

The eventual registry count would be 59 = 39 + 20, or temporarily 58 if Book III is deferred. No existing Greek, Latin or Lodge record changes; Whiston’s previous deferral remains part of the historical review.

## Reader compatibility

No JavaScript or CSS change is required by the inspected architecture. renderTei.js already loads per-work/book/language/witness records, renders their notes, extracts companion paratext through selectors and removes links. Its outer “Table of contents” heading may remain; the companion title and note identify the editorial compilation. Existing English Coelacanth and Greek-specific typography remain untouched. If implementation reveals an incompatibility, document it before broadening scope.

Suggested reader note: “These headings come from the 1856 Auburn and Rochester printing of William Whiston’s translation. Their arrangement as an index is editorial.”

Keep view=contents, Book switching, pane/source selection and history semantics unchanged. English displays its own Whiston index and never borrows Greek or Bamberg contents. Whiston chapter labels do not become traditional Chapter/Subchapter identities. Preserve all 39 current contents records, 198 Bamberg identities, traditional navigation, Alignment units, Niese markers and URLs.

## Implementation QA and protected files

Extend tests to twenty English lists and 256 entries; exact source-to-TEI text and labels; witness availability and mixed panes; contents/Chapter/Book transitions; reload, copy URL and Back/Forward; keyboard; both themes; long-heading wrapping; non-clickable entries; duplicate DOM IDs. Re-run existing navigation suites and prove narrative text, stable IDs, sameAs and segmentation unchanged. Those browser/implementation tests were not run in this read-only mission.

Future write scope: approved companion files, source-contents.xml and a new implementation review packet. Protected: all narrative XML, structure.xml, renderer, styles, frozen/certification directories and other works. No production change has been made here.
