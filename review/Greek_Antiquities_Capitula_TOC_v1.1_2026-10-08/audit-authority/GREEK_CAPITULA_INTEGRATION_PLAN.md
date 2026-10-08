# Data-only TOC v1.1 incorporation proposal

This plan is not implemented. Audit base: f393fa1223b38d9ca114e583fcc57d5e34425815. Reverify production before a later implementation task.

Add these nine independent TEI companion files after human acceptance:

- assets/xml/antiquities/paratext/niese/book-01-contents.xml ← proposed-tei/book-01-contents.xml (19 source entries).
- assets/xml/antiquities/paratext/niese/book-02-contents.xml ← proposed-tei/book-02-contents.xml (8 source entries).
- assets/xml/antiquities/paratext/niese/book-03-contents.xml ← proposed-tei/book-03-contents.xml (10 source entries).
- assets/xml/antiquities/paratext/niese/book-04-contents.xml ← proposed-tei/book-04-contents.xml (5 source entries).
- assets/xml/antiquities/paratext/niese/book-06-contents.xml ← proposed-tei/book-06-contents.xml (15 source entries).
- assets/xml/antiquities/paratext/niese/book-07-contents.xml ← proposed-tei/book-07-contents.xml (12 source entries).
- assets/xml/antiquities/paratext/niese/book-08-contents.xml ← proposed-tei/book-08-contents.xml (12 source entries).
- assets/xml/antiquities/paratext/niese/book-09-contents.xml ← proposed-tei/book-09-contents.xml (16 source entries).
- assets/xml/antiquities/paratext/niese/book-10-contents.xml ← proposed-tei/book-10-contents.xml (12 source entries).

Each companion uses the established TEI namespace, full teiHeader/sourceDesc, Greek language metadata and `div type="contents"` with a source heading, `list type="capitula"`, literal labels inside items and a duration trailer. Book I adds its separate unnumbered proem-summary paragraph. Roman book headings remain source text. Items are not chapter wrappers or citation milestones. The companions and the proposed registry document validate against the unchanged project `tei_all.rng`.

PROPOSED_REGISTRY_ADDITIONS.xml contains the exact nine TEI item/fs declarations to add to `assets/xml/source-contents.xml`, after acceptance. It is a standalone valid proposal container, not a replacement registry. Each item uses work=antiquities, its numeric book, language=Greek, witness=niese, status=VERIFIED, the companion path above and selector `tei-div[type="contents"]`. Registration IDs are contents-antiquities-niese-01 through04 and06 through10. They do not conflict with existing IDs. No structural-navigation identity is created.

All 30 installed source-TOC declarations remain untouched, including accepted Greek V and XI–XX, all Latin sources and Lodge. Do not rewrite their source text while adding the nine items. Do not change Antiquities structure.xml, narrative XML, source numerals, Niese milestones, sameAs, alignment topology or Bamberg records. IX/X's surviving duration-only wrappers can remain as historical encoding; registering the companion avoids showing only that fragment as the restored list.

The existing generic contents loader in renderTei.js already finds VERIFIED rows by work/book/language/witness, loads each registered XML, converts it with CETEI and clones the registered selector. Its data-processed callback avoids automatic list decoration. A `contents` div, head, list/item/label, proem paragraph and trailer are already representable. No JavaScript adjustment is indicated. Literal printed square brackets avoid the existing red strike-through treatment of tei-del and avoid falsely implying Blatt-derived supplementation. Book II's opening bracket before δʹ. and closing bracket after the trailer retain their printed scope without crossing invalid XML containment.

No CSS adjustment is indicated. The current .source-contents rule in assets/css/tei.css uses var(--lj-font-text); _sass/_typography.scss defines the existing reading stack as “LJ Coelacanth”, Georgia, “Times New Roman”, serif, shared by scholarly text including Greek with available Unicode fallback. The new source headings/items inherit this established typography. No new font or theme layer is proposed. Browser font/glyph coverage must be checked at implementation; none is claimed here.

TOC navigation remains `?book=N&view=contents`, independent of chapter/subchapter/bamberg/niese/unit. No chapter=toc value, narrative range links or capitula-to-navigation inference is added. Greek shows its own list; Latin/English continue to show their own verified source list or the existing neutral unavailable message. Do not borrow Greek into another pane.

Extend integration tests to all nine new companions and all 109 source entries, plus the19 target headings/rubric/trailers. Verify literal labels, source order, bracket scope, the Book I proem separation, II's Exodus-before-Moses-birth order, VII.5/X.4 bracketed words, IX.15–16's comma continuation and X.6's cross-page word. Compare rendered text with the audited register after only HTML whitespace folding; do not normalize Greek spelling or accents. Confirm there are no clickable item targets, duplicate DOM IDs or automatically synthesized list numbers.

Browser tests for the later task: copied/reloaded contents URLs for I–IV andVI–X; Back/Forward; Book changes; Chapter↔contents; mixed panes; source/pane toggles; keyboard selection; both themes; Greek font, numerals and bracket visibility. Existing V andXI–XX must remain byte-identical. Extend registry availability tests from 11 to 20 Greek Antiquities books without altering other witnesses.

Repeat established structural regressions after installation: 257 traditional Chapters,1432 Subchapters,198 Bamberg identities and compact row URLs,2456 currently enabled Niese selections,1441 Alignment units, XI multispan assembly, VI.xii.8/XIII clipping and all certified unavailable states. Preserve Bellum/Cardwell/Niese/Lodge, DEH and Contra Apionem behaviour. This audit changes no code and executes no browser or website build; these are future integration tests, not reported passes.

The only possible separate change is the Book V control encoding issue, which requires its own approval and is unnecessary for the nine companions. No unresolved target reading or schema extension currently requires JavaScript/CSS changes.
