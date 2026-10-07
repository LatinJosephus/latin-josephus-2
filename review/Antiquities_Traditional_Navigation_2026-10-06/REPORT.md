# Antiquities traditional navigation: implementation Phase 1

**GO for human review and commit.** All required traditional-navigation QA passes. The implementation remains unstaged and uncommitted in `C:\workspace\LatinJosephus-antiquities-traditional-navigation`, branch `antiquities-traditional-navigation`, based on `f7d9142cad998e8a005adea1a22532b9a78592db`. Canonical production and frozen recovery authorities are unchanged.

## Architecture and URLs

Antiquities explicitly opts into `assets/xml/antiquities/structure.xml`. Chapter/Subchapter selectors derive from certified registry identities, with independent Greek, Latin and English start/end locators. The previous coarse Sub-chapter selector is labelled **Alignment unit**. Other works keep original adapters and navigation semantics.

| Parameter | Antiquities meaning |
|---|---|
| book | Book; preface selects Proem |
| chapter | certified traditional Chapter |
| subchapter | certified traditional lower division within Chapter, or Proem |
| niese | existing independent Niese citation navigation |
| unit | existing alignment unit, including suffix 276b |

Examples: `?book=5&chapter=3`; `?book=5&chapter=3&subchapter=2`; `?book=5&niese=179`; `?book=4&unit=276b`; `?book=preface&subchapter=2`. Irrelevant structural parameters are cleared; unrelated parameters and fragments are preserved. Scheme activation selects an explicit coordinate so reload and back/forward reproduce it. Pane toggles preserve identity. Antiquities has one configured source per language; protected works' alternate-source semantics are unchanged. No parallel legacy Chapter system or verbose traditionalChapter parameter was added.

TEI data separates persistent identity, label, parent/context, literal source reading, provenance, canonical association, independent status, confidence, availability and certified physical point. Source anomalies are data, never renderer case logic. Historical markers remain evidence and do not define new traditional menus.

## Registry and preserved source counts

257 Chapters; 1,432 Subchapters; 1,689 level rows; 1,441 certified physical positions. Proem has four lower divisions and no Chapter zero. Nine absent Loeb lower-1 openings and four Niese-only lower-1 observations remain witness-specific.

Primary source statuses remain 1,672 CONFIRMED_NIESE_START; 3 CONFIRMED_WITHIN_NIESE; 3 LOEB_NIESE_NUMBER_DISAGREEMENT; 11 NIESE_SOURCE_AMBIGUOUS; 0 UNRESOLVED. All 1,689 identities, raw readings, associations, verification statuses and human checks exactly match frozen authorities. TEI P5 4.12.0 Relax NG validation passes.

## Physical ranges and preservation

A generic resolver accepts one span or an ordered span list per language, selecting registered element edges or anchors without numeric paragraph arithmetic or visible-label parsing. Unmapped starts/ends show an unavailable state instead of nearby text. Later clones of a fragmented paragraph keep data-source-id provenance without duplicate rendered IDs; source XML IDs never change.

Only 13 empty anchors were inserted: Greek 7, Latin 3, English 3, across 12 files. Removing only those anchors recovers all pre-existing XML bytes exactly. Text, Unicode, punctuation, apparatus, IDs, sameAs, paragraph order/counts and inline markup are preserved. No Book VI, VII, IX or XI XML file changed. Paragraph totals remain Latin 1,622; Greek 1,681; English 1,600. Each layer retains 1,442 identified alignment paragraphs including Preface.

Book XI's authentic non-monotonic order is preserved; the paragraph-reordering proposal is withdrawn and none was performed. Chapter VIII has four spans per language; Subchapters 2,4,6 have two each; 3,5 have one each. Latin split 326a/b and 342a/b remain distinct physical fragments. Both Bellum 4.105 interpolation portions remain in Subchapter 2 witness fragments. Canonical views disclose assembly and link to unchanged Book view; Book/Alignment-unit views preserve witness order. Exact 311-347 membership is documented in XI_current_text_multispan_adjudication.md and XI_MULTISPAN_MEMBERSHIP.json.

VI.xiii / VI.xiii.1 now use verified Latin/English num272. VI.xii.8 uses Latin/English num271 and Greek num262/num[8]. Three expressly authorized data-only Greek alignment spans correct units 262,271,272 while preserving source XML and sameAs. V.iii.2 literal Loeb 79 and canonical 179 remain separate data, without renderer conditions.

VII.i / VII.i.1 directly select existing Latin latin-book07-num, allowing traditional navigation without repairing Greek/English #latin-book07-num1 targets. That alignment graph defect remains a separate known issue. Book IX missing source/current positions remain explicit; no text, marker or nearby substitution was invented.

The two earlier Latin projection mismatches were 18 trailing whitespace characters due to nested inner/outer body endpoints. The generic Book-end resolver now uses the complete loaded body. No lexical text or source position was repaired.

## QA

- Full restart from Proem/Book I: **1,689/1,689 identities / 5,067 language cases**, with **5,034 executable ranges PASS** and **33 expected Book IX unavailable cases PASS**. All 257 Chapter options, 1,432 Subchapter options and 1,441 physical identities verified. Each executable incipit and complete projected span/interval matches its locator and independent physical membership.
- Book XI: **18/18 language mappings**; two split-citation model checks (Latin 326,342); no unintended overlap or duplication; exact XI.viii.4 membership; Chapter/Subchapter partition equality; retained interpolation; disclosure and witness link; exact base equality for Book/Alignment-unit paragraphs.
- Book VI: locator **2/2**; original Niese 269/271 starts **6/6**; alignment **15/15 pane starts** across five units including neighbors; exact three-span partition; five pane-switch identities; focused Niese differential **6/6**.
- Current Antiquities Niese I-VII: **2,456 selections / 7,368 language comparisons PASS** against the base renderer. Public VIII-XX coverage was not expanded. Split-citation tests demonstrate model support, not new Book XI public coverage.
- DEH/Bellum/Contra Apionem: **14 book groups / 3,373 chapter-unit range comparisons PASS**. By work: {'deh': 1239, 'bellum-judaicum': 1441, 'contra-apionem': 693}. Additional Bellum Whiston/Lodge: **14 source-book groups / 10,340 range comparisons**, including **7,444 citation selections**, PASS.
- Actual rendered exception pages: **18/18**; no duplicate DOM IDs; corrected labels; pane selection preserved; witness-order link works. Reload/back/forward, Book switching, Subchapter to Niese, Alignment unit, Proem, num276b, Book IX unavailable, Book VII opening, extra parameters and fragments PASS.
- Exact XML byte recovery, text/topology, anchor provenance, canonical checkout and frozen authorities PASS. Other-work XML, CSS/SCSS, layouts, configuration, CETEI and generated files unchanged.

The differential harness supplies HTMLCollection.forEach compatibility to the original renderer, which otherwise throws in the standalone harness. Antiquities materializes its annotation collection as an array; other-work code was left unchanged. Comparisons certify equality under that supplied compatibility. Source files were served locally without a site build or generated-file write.

## Modified files

14 existing files, plus registry and dedicated review records:

- `_includes/display-settings.html`
- `assets/js/renderTei.js`
- `assets/xml/antiquities/English/book-01.xml`
- `assets/xml/antiquities/English/book-13.xml`
- `assets/xml/antiquities/English/book-15.xml`
- `assets/xml/antiquities/Greek/book-15.xml`
- `assets/xml/antiquities/Greek/book-16.xml`
- `assets/xml/antiquities/Greek/book-17.xml`
- `assets/xml/antiquities/Greek/book-18.xml`
- `assets/xml/antiquities/Greek/book-19.xml`
- `assets/xml/antiquities/Greek/book-20.xml`
- `assets/xml/antiquities/Latin/book-13.xml`
- `assets/xml/antiquities/Latin/book-15.xml`
- `assets/xml/antiquities/Latin/book-16.xml`

- New `assets/xml/antiquities/structure.xml`.
- `review/Antiquities_Traditional_Navigation_2026-10-06/`: reports, reproducible tests, schema and evidence metadata. Exact before/after hashes and status are in FILE_MANIFEST.json and QA.json.

## Remaining scope / disposition

Bamberg navigation and public Niese VIII-XX expansion remain deferred. Book IX missing text remains explicit. Book VII's existing alignment-target defect is unrepaired; traditional navigation uses verified independent locators. Canonical assembly is disclosed and does not claim Bamberg itself has canonical order.

No staging, commit, push, merge, rebase, canonical-checkout write, frozen-packet write or Git configuration change occurred. Only the authorized isolated branch/worktree creation wrote Git administrative state. **GO for human review and commit of this isolated Phase 1 implementation.**

## Reproduction

Run bundled Python verify_integrity.py, then Node navigation.test.cjs with --locator-gate, --alignment-gate, --multispan-gate, --rendered-gate, no flag for exhaustive QA, and --protected-source-gate. Tests use installed Chrome in an isolated context. Do not rerun one-time prepare_registry.py over the existing registry. Earlier BROWSER_FAILURE.json and XI_RANGE_BLOCKER.json are labelled historical and superseded by passing reports.
