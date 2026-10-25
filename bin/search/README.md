# Latin Josephus search

This directory contains the source and verification tools for the main site's
`/search/` page. Current coverage comprises four Latin collections and four English collections:

- **Cardwell's *Bellum Judaicum*, Books I–VII:** 4,001 Niese sections and
  114,794 word tokens.
- **Ussani's *De excidio Hierosolymitano*, Books I–V, including the Prologue:**
  558 chapter/paragraph citation units and 87,472 word tokens.
- **Boysen's *Contra Apionem*, Books I–II:** 616 Niese sections and
  21,018 word tokens, including the Greek words quoted in this Latin text.
- **Bamberg Msc. Class. 78 *Antiquities*, Proem and Books I–XX:** 7,273 primary
  Niese identities, two separately labelled Bellum insertions, and 265,023 word tokens. Book I includes the separately
  transmitted Proem's 26 units and 986 words.

- **Whiston English *Antiquities*, Proem and Books I–XX:** 7,376 Niese
  sections and 470,938 word tokens. The Proem accounts for 26 sections and
  1,646 tokens; Book I’s narrative supplies 320 sections and 20,348 tokens.
  Books XVI–XX add 1,772 sections and 107,819 word tokens to the accepted I–XV search.

- **Whiston English *Bellum Judaicum*, Books I–VII:** 4,001 Niese sections and
  215,072 word tokens, including Book I's embedded preface (I.1–30).

- **Whiston English *Contra Apionem*, Books I–II:** 616 Niese sections and
  36,853 word tokens.

- **Pollard English *De excidio Hierosolymitano*, version 1.1, Prologue and Books I–V:**
  558 chapter-and-paragraph citation units and 136,052 word tokens.

Together these comprise **68 book editions, 25,001 citation units, and 1,347,222
word tokens**. The indexes contain 25,009 physical records because four Bamberg
Antiquities XI identities and three XVI identities have split portions.
The Whiston English Antiquities, Bellum and Contra Apionem and Pollard English De excidio are complete; Greek editions are not indexed. Bamberg Latin Antiquities
III.240 and VII.69–99 retain their citations and the source's explicit omissions.
X.108 retains an empty interval between its citation label and the next Niese
marker, without an omission tag. IX.51–109 are absent from the accepted source;
no records or searchable Latin have been generated for them.

The Jekyll page is [`_pages/search.html`](../../_pages/search.html), with
`permalink: /search/`, the shared `default` layout, and `nav: true` for the
site's existing navigation. Its interface comes from
[`_includes/search-interface.html`](../../_includes/search-interface.html).
Browser modules, styles, indexes, and verification evidence are exported to
`assets/search/`. Edit their sources here and rebuild the export.

This README describes the source integration and its local verification; it
does not establish that a particular public deployment has been updated.

## Search rules

| Syntax | Meaning |
| --- | --- |
| `Theodor*` | A word beginning with `Theodor`; `*` can match zero or more characters. |
| `*orum`, `iud*um` | A suffix or an internal wildcard, still within one word. |
| `Theodor* OR Zenon*` | Either expression may match. |
| `Theodor* AND NOT Alexander` | The selected section or book contains the first expression and lacks the second. |
| `(Theodor* OR Zenon*) AND Alexander` | Parentheses group a Boolean expression. |
| `Theodor* Alexander` | Adjacent unquoted expressions imply `AND`. |
| `"At Theodorus repente"` | Consecutive words in the stated order. |
| `"At Theodor* repente"` | A consecutive phrase with a wildcard within one phrase word. |

Operators are uppercase `AND`, `OR`, and `NOT`. Precedence is `NOT`, then
`AND`, then `OR`; use parentheses when the intended grouping might be unclear.
Double quotes make an exact phrase rather than an unordered collection of words.
Punctuation, capitalization, and ordinary whitespace do not affect phrase
matching. A wildcard does not consume spaces or span multiple words.

Matching uses Unicode word tokens and case normalization. There is no stemming,
lemmatization, automatic correction, or removal of common words. The optional
**u/v and i/j equivalence** applies to Latin editions only, to both indexed
words and the query. English is searched literally apart from case even in
mixed selections. The control is disabled for English-only searches. Search
normalization preserves the original displayed text and its highlight offsets.
Accents are retained.

### Section and whole-book scope

**Section / citation-unit scope** evaluates the complete Boolean expression
within one Niese section of Bellum, Contra Apionem or Antiquities, one explicitly
labelled Bellum insertion in Antiquities XI, or one cited paragraph of De excidio.
A phrase must fit entirely within that unit and follow physical source order.
Split portions of the same Antiquities section share Boolean scope, but a phrase
cannot jump across intervening text to join displaced portions.

**Whole-book scope** evaluates the complete expression within each selected book
of one work, language, and edition. Distinct Boolean terms can occur in different
sections of that book. A phrase must remain consecutive, but may cross Niese or
chapter boundaries within the book. An explicit structural boundary or textual
gap, represented by `breakBefore` or an internal `phraseBreaks` offset,
prevents a phrase from joining the text on either side. In Boysen's Latin Contra Apionem,
all 25 literal asterisk clusters are conservative phrase-adjacency barriers,
including clusters inside a section or at its edge. This rule does not infer
the missing-text extent or a precise editorial meaning for every mark.
Whiston's English Contra Apionem preserves its own accepted section text and
has no such asterisk barriers. Whiston's division markers, including the two
inside II.109 and II.112, do not interrupt phrases.
In De excidio, the three Prologue units are searchable and can be
joined to each other in whole-book phrases, but a phrase cannot cross from the
end of the Prologue into the Book I narrative. This is a composition boundary,
not an inferred lacuna. Whole-book Boolean conditions can still relate
Prologue and narrative hits within Book I.

Both indexed Antiquities editions separate their Proem from the narrative:
I.1–26 are in the Proem source, and I.27 begins the narrative. In the Bamberg
Latin, literal dotted
interruptions, ellipses and the erased-dot spans in X.154 conservatively block
phrase adjacency. Phrases cannot cross the explicit omissions at III.240 and
VII.69–99, the empty citation interval X.108, or the missing range IX.51–109.
Uncertain sentence periods in X.65 and X.75 are ordinary punctuation and do
not block phrases. Ordinary Niese seams and the eight sections continued
across coarse source paragraphs in I–X remain consecutive, subject to the selected
search scope. The XI–XX rules and accepted registries are described below.

Neither Boolean conditions nor phrases combine evidence from different books,
works, languages, or editions. For example, `A AND NOT B` in whole-book scope
finds each book containing A and lacking B throughout that book. B in another
book does not exclude it. Selecting one book gives the same result for that
book as its part of an all-books search.

Matching section or book counts describe the chosen scope. Excerpt cards locate
positive terms and phrases; they are not a total word-frequency measure.
Negative-only book matches have a book identity and reader link, with no
invented occurrences or highlights. Results follow collection order, then book
and source order. The interface shows 20 excerpt cards at a time; pagination
does not truncate the query's matching vocabulary or results. Invalid or
oversized expressions produce an error rather than silently dropping terms.

### Concordance and complete-result downloads

The **Passages / Concordance** controls select two views of the same successful
query. Passages retain the existing section and excerpt cards. Concordance
shows each positive match separately, with the original word or phrase between
up to ten words of left and right context and a linked citation. Context stays
within the cited section or sections. A phrase crossing a Niese boundary is
one occurrence with a citation range; punctuation at the boundary is retained.
De excidio uses references such as `De excidio Prol.2`, `De excidio II.14.5`,
and the cross-chapter range `De excidio I.1.10–I.2.1`. Its internal sequential
record number is never presented as a Niese reference. Reader links use the
existing chapter and chapter-local paragraph parameters.
Contra Apionem uses Niese references such as `Contra Apionem I.38` and
`Contra Apionem II.186`, with `book` and `niese` reader parameters. Boysen's
chapter divisions are independent of those references and are not substituted
for Niese sections.
Both views paginate their display without truncating the underlying results.

For a single word, wildcard, or quoted phrase, the result summary distinguishes
**occurrences** from matching sections or books. A section containing five
instances contributes five occurrences and one matching section. For a
compound Boolean query, the concordance shows positive evidence in units that
satisfy the complete query. Its rows are not a word-frequency total: a phrase
and a contained word can be distinct evidence, and the terms of a whole-book
query can occur in different sections. Negative-only matches retain their
unit identity and reader link without an invented occurrence.

**Download all results (CSV)** exports every matching result, including those
beyond the displayed page and matching units with no positive hits. The file
starts with readable citation, Latin context, matched text, edition, and reader
link columns. Later columns record the query, selected works and books, scope,
spelling mode, search link, export time, and text/index fingerprints. Original
source offsets and text segments are included for checking an exported match.
The download reflects the last successful query; editing the form without
submitting it does not relabel those results. A new search or an error disables
the previous download until another query succeeds.

Bellum-only exports retain the established 51 columns. De excidio, Contra Apionem, and mixed
exports have 56 columns: five additional fields after `reader_url` identify the
citation scheme, give editorially marked versions of the left context, matched
text, and right context, and explain the notation. The original literal text
columns remain exact. In the readable editorial columns, `[text]` marks
supplied text, `⟦text⟧` marks editorial deletion, and `⟨text⟩` marks a source
addition. These delimiters are export notation, not characters inserted into
the indexed Latin. `source_segments_json` also records each source editorial
span with exact UTF-16 offsets. For Contra Apionem it retains overlapping
quotation and foreign-language markup, literal asterisk spans, phrase-break
offsets, and source boundary annotations. Source brackets and asterisks remain
literal in all text columns; the legend explains the added export notation.

CSV is UTF-8 with a byte-order mark for spreadsheet compatibility. Fields are
quoted and embedded quotation marks and line endings are preserved. A scalar
cell that could be interpreted as a spreadsheet formula receives a leading
apostrophe; the affected columns are identified, with exact underlying values
also recorded as JSON. This affects the spreadsheet representation, not the
indexed or displayed text.

The `concordance.mjs` module consumes the engine's hit spans directly. It
does not derive occurrences from merged highlights, excerpt cards, or the DOM,
and it does not change the query grammar, tokenizer, indexes, or scholarly XML.

### Loading and saved links

The browser’s versioned launcher selects a content-addressed module graph and
its matching, content-addressed catalog, then downloads only the selected books.
The canonical `catalog.json` remains a source/audit artifact.
Successful downloads are cached for the session. Each bundle's byte length,
SHA-256 fingerprint, coverage, and text-version identity must match the catalog.
If a selected book is missing or inconsistent, the entire query fails; retrying
can reuse the books already verified. An older query cannot overwrite the
results of a newer query.

Saved links preserve `q`, `work`, `book`, `scope=book` when selected, `fold=1`
when spelling equivalence is enabled, and `view=concordance` for that view.
`work` identifies a collection, for
example `bellum-latin-cardwell`, or `all`. `book` identifies a qualified book,
for example `bellum-latin-cardwell:1`, or `all`.

Legacy query parameters without `work` continue to select Bellum. If both
`work` and `book` are absent from a link with a query, the original Book I
behavior is retained. Legacy explicit numeric books and `book=all` are also
resolved within Bellum. New links include collection identity so De excidio I
and Contra Apionem I cannot be confused with Bellum I. The bare page retains **Bellum, all seven
books** as its default. Choose **De excidio Hierosolymitano** for its five books,
**Contra Apionem** for its two books, **Antiquities I–XX, including Proem** for
all twenty Bamberg Latin Antiquities books, **Antiquities · English · Whiston**
for the English Proem and Books I–XX, **Bellum Judaicum · English · Whiston**
for all seven English Bellum books, **Contra Apionem · English · Whiston**
for both English Contra Apionem books, **De excidio Hierosolymitano · English · Pollard v1.1**
for its Prologue and all five books, or **All works** to search all eight collections.
Proem passage links use `antiquities/?book=preface&niese=N`; whole-Book-I links
use `antiquities/?book=1`.

The page uses ES modules, `fetch`, and browser WebCrypto. Serve it over HTTPS or
localhost; opening a local HTML file with a `file:` URL is unsupported. The
runtime uses the bundled Lunr library and no external search service or CDN.
Jekyll's `relative_url` handling preserves the configured base path in the
search asset URLs and outgoing reader links. The unchanged reader itself uses
root-path `WORKS` keys and has not been certified for hosting under a path
prefix. The site's existing root-hosted deployment does not require that
prefixed-reader support.

## Canonical source and coverage

The authoritative site repository is
[LatinJosephus/latin-josephus-2](https://github.com/LatinJosephus/latin-josephus-2.git),
using its **`v2-development` source branch**. The public preview repository,
[LatinJosephus/LatinJosephus.github.io](https://github.com/LatinJosephus/LatinJosephus.github.io),
uses **`main` for generated output only**. It is separate from the authoritative
source checkout for the site's reader and ongoing Antiquities repairs.

Prepare updates in an isolated LF checkout and review source and generated
changes together. The Pollard English De excidio release adds one reviewed
commit to each already-installed Whiston Contra Apionem branch. Its helper verifies
the exact Git objects and all indexed source inputs, then uses ordinary
fast-forward pushes. The user's working files, index, settings and local
branches are preserved. Remote branches must be at the accepted base or the
reviewed final commit; the release package records those exact pins and its
publication command. Earlier local branches are accepted only when the
helper verifies their ancestry and all indexed input contents.

The search build **reads canonical XML without modifying it**:
`assets/xml/bellum/Latin/book-01.xml` through `book-07.xml`,
`assets/xml/deh/Latin/book-01.xml` through `book-05.xml`, and
`assets/xml/contra-apionem/Latin/book-01.xml` through `book-02.xml`, the accepted
Latin Antiquities sources and citation maps, and the accepted English Whiston
sources under each work's `English/` directory, plus the five accepted Pollard
files under `assets/xml/deh/English/`. The configured source lists,
extraction reports, and independent QA record the actual source hashes.

### Bellum

| Book | Niese sections |
| --- | ---: |
| I | 673 |
| II | 654 |
| III | 542 |
| IV | 663 |
| V | 572 |
| VI | 442 |
| VII | 455 |
| **Total** | **4,001** |

The Book I proem is included. The extractor excludes the TEI header, stand-off
manuscript annotations, inspected unnumbered book titles, and verified leading
printed division labels. It preserves running-text spelling, punctuation, and
internal whitespace. Each record retains its book and section identity,
reader URL, first source anchor, and order within its collection.

Actual leading `[N]` labels and internal Niese milestones establish sections.
Paragraph IDs alone do not: III.3 and VI.427 continue through later source
paragraphs. Per-book reports document these continuations, label removals, and
section-edge whitespace, allowing reconstruction of the source paragraphs.
The Book I corpus retains the approved pilot's fingerprint.

`extract.py` intentionally accepts the inspected Bellum structure and stops on
unexpected substantive content. A later accepted XML change may require an
explicit update to extraction expectations and independent QA fixtures before
regeneration will pass. These checks establish fidelity to the accepted XML;
they do not replace an editorial comparison with printed source pages.

### Ussani Latin De excidio

| Book | Citation units | Word tokens |
| --- | ---: | ---: |
| I, including Prologue | 215 | 26,310 |
| II | 73 | 11,011 |
| III | 70 | 12,091 |
| IV | 79 | 11,027 |
| V | 121 | 27,033 |
| **Total** | **558** | **87,472** |

`extract-deh.py` reads the project's accepted Ussani (1932) Latin TEI. It
includes every numbered paragraph, with the three Prologue units included in
Book I. TEI metadata, headings, and printed citation prefixes are excluded;
the cited division and stable source ID remain record metadata. Empty page and
line-break markup adds no whitespace, preserving words interrupted by printing
milestones, such as `Ro<pb/>manos` → `Romanos`.

The nine main-text `<supplied>` spans and nine `<del>` spans retain their literal
letters and distinct editorial annotations. Results display supplied letters
in brackets and deleted text with strike-through, including intra-word cases
such as `Ce[ne]daei` (II.14.5) and `Alexander` with `der` deleted (I.34.2). These
letters remain searchable, matching the displayed reader's literal text; no
alternative reading is silently substituted. A supplied passage in a heading
is excluded with that heading.

The three empty `<unclear/>` elements produce a visible critical dagger (`†`),
as in the reader. Each generated glyph is explicitly annotated and can be
removed to reconstruct the original source projection. These daggers mark
textual uncertainty, not omitted words. Search treats them as punctuation, so
a phrase may span a dagger; the dagger stays visible in results and exports.

Per-paragraph reports preserve exact source projections, display text hashes,
editorial offsets, numbering, source IDs, and edge whitespace. Publication
validation checks the reversible source/display distinction and every citation
and reader URL. An independent verifier parses the canonical XML separately,
checks every character and token offset, and compares query answers with its
own full-scan oracle. Neither extractor nor search changes the accepted XML.

### Boysen Latin Contra Apionem

| Book | Niese sections | Word tokens |
| --- | ---: | ---: |
| I | 320 | 10,657 |
| II | 296 | 10,361 |
| **Total** | **616** | **21,018** |

`extract-ca.py` reads the project's accepted Boysen (1898) Latin TEI. Every
numbered main-text paragraph supplies one Niese section. The TEI header,
headings, and bibliographical source note are excluded. The running text is
the exact paragraph text projection with only section-edge whitespace trimmed;
the extraction report records that whitespace so it can be restored. No
printed Latin reading, spelling, punctuation, or internal whitespace is repaired.

The source's quotation, three Greek foreign-language spans, literal brackets
and angle brackets, and the addition `<add>milia</add>` at I.290 are retained.
The added word is searchable and appears in bold green in search results, as
in the reader; editorial CSV columns identify it as `⟨milia⟩`. Empty page-break
markup adds no whitespace, so `praecel<pb/>lentes` at II.186 remains the single
word `praecellentes`. The accepted Latin II.278 seam stays in source order;
alignment to Greek does not relocate or duplicate its Latin text.

All 25 maximal literal asterisk clusters remain visible and prevent exact
phrases from joining words across them, in either scope. Boolean conditions
can still relate words on both sides. The source annotations before I.119 and
I.147 also retain `breakBefore`; a leading asterisk at II.12 supplies the third
blocked within-book seam. The other 611 within-book seams permit consecutive
whole-book phrases. No chapter boundary is inferred to be a gap.

`phraseBreaks` records strictly increasing UTF-16 offsets at the original
asterisk starts. `textGaps` preserves their literal spans without inventing a
gap size. These optional fields extend record metadata; unchanged Bellum and
De excidio bundle bytes remain valid. The independent CA verifier embeds a
separate minidom-based source witness and checks that its inspectable Python
copy is identical. It verifies every section, character, token offset, inline
annotation, reader reference, asterisk barrier, and adjacent section seam.

## Source, generated files, and configuration

| Location | Role |
| --- | --- |
| `extract.py`, `tests/test_extract.py` | Bellum extraction and reconstruction checks. |
| `extract-deh.py`, `tests/test_extract_deh.py` | De excidio extraction, editorial annotations, and reconstruction checks. |
| `extract-deh-english.py`, `tests/test_extract_deh_english.py` | Pollard English De excidio extraction, chapter-local citations, alignment and paragraph restoration. |
| `extract-ca.py`, `tests/test_extract_ca.py` | Contra Apionem extraction, markup, phrase barriers, and reconstruction checks. |
| `extract-antiquities.py`, `tests/test_extract_antiquities.py` | Antiquities I–XX and Proem extraction, source restoration, and gap checks. |
| `extract-whiston-bellum.py`, `tests/test_extract_whiston_bellum.py` | Whiston Bellum I–VII extraction, embedded milestones, supplied text, and exact paragraph restoration. |
| `extract-whiston-contra-apionem.py`, `tests/test_extract_whiston_contra_apionem.py` | Whiston Contra Apionem I–II extraction, exact Niese paragraph identities, and Whiston division-marker provenance. |
| `corpus.json`, `data/book-0N.corpus.json` | Generated combined and per-book original-text records. |
| `extraction-report.json`, `data/book-0N.extraction-report.json` | Generated coverage and reconstruction evidence. |
| `engine.mjs`, `vendor/` | Boolean/phrase/wildcard engine and pinned Lunr 2.3.9 with licence and provenance. |
| `collection.mjs` | Qualified selection, verified loading, caching, and independent per-book evaluation. |
| `app.mjs`, `ui-utils.mjs`, `styles.css` | Source for the browser interface, citations, links, and excerpts. |
| `config/collections.json` | Ordered registry of enabled collection manifests. |
| `config/bellum-latin-cardwell.json`, `config/deh-latin-ussani.json`, `config/contra-apionem-latin-boysen.json`, `config/antiquities-latin-bamberg78.json` | Collection metadata, corpus inputs, citation terminology, and expected coverage. |
| `config/publication.json` | Runtime export inventory, site/build inputs, and approved extraction/QA adapters. |
| `build-index.mjs`, `catalog.json` | Manifest-driven index builder and generated catalog. |
| `data/bellum-latin-cardwell/book-0N.bundle.json` | Generated independent indexes, one per book. |
| `tests/corpus-qa.mjs`, `qa-report.json` | Independent source/query verification and its current evidence. |
| `data/deh-latin-ussani/` | De excidio corpus shards, extraction reports, book indexes, and independent QA report. |
| `tests/deh-corpus-qa.mjs` | Independent De excidio XML witness, token, query, boundary, and mixed-collection checks. |
| `tests/deh-english-corpus-qa.mjs`, `tests/deh-english-source-witness.py` | Independent English De excidio witness, accepted Latin alignment, all-token and phrase checks, Prologue boundary, reader links and CSV. |
| `data/deh-english-pollard/`, `config/deh-english-pollard.json`, `deh-english-publication.mjs` | Five English De excidio indexes, original-text records, extraction/QA evidence and the strict source projection gate. |
| `data/contra-apionem-latin-boysen/` | Contra Apionem corpus shards, extraction reports, book indexes, and independent QA report. |
| `tests/ca-corpus-qa.mjs`, `tests/ca-source-witness.py` | Independent Contra Apionem XML witness, token, query, markup, and seam checks. |
| `tests/phrase-breaks.test.mjs`, `tests/ca-presentation.test.mjs` | Phrase barrier, citation, full export, and three-work compatibility tests. |
| `data/antiquities-latin-bamberg78/` | Antiquities I–XX corpus, per-book indexes, extraction evidence, and independent QA; the Proem is included in book-01. |
| `tests/antiquities-corpus-qa.mjs`, `tests/antiquities-source-witness.py`, `tests/antiquities-presentation.test.mjs` | Independent 21-document witness with ten accepted registries, all-token and query checks, Proem links, gap boundaries, editorial exports, and four-work integration. |
| `tests/whiston-bellum-corpus-qa.mjs`, `tests/whiston-bellum-source-witness.py` | Independent seven-document English Bellum witness, exhaustive word and phrase checks, supplied spans, reader links, and mixed-edition isolation. |
| `data/bellum-english-whiston/`, `config/bellum-english-whiston.json`, `whiston-bellum-publication.mjs` | Seven English Bellum indexes, original-text records, extraction/QA evidence, and the strict source projection gate. |
| `tests/whiston-contra-apionem-corpus-qa.mjs`, `tests/whiston-contra-apionem-source-witness.py` | Independent two-document English Contra Apionem witness, all-word and phrase checks, source divisions, literal brackets, reader links, and mixed-edition isolation. |
| `data/contra-apionem-english-whiston/`, `config/contra-apionem-english-whiston.json`, `whiston-contra-apionem-publication.mjs` | Two English Contra Apionem indexes, original-text records, extraction/QA evidence, and the strict source projection gate. |
| `build-search.mjs`, `publication.mjs`, `check-assets.mjs` | Rebuild orchestration, export validation, and read-only freshness checks. |
| `assets/search/` at repository root | Generated runtime and evidence export, including `publication-manifest.json`. |

### Schema and identity contracts

The **registry, collection manifests, and publication configuration use schema
1**. The **generated catalog uses schema 2**; the engine's per-book bundle
format remains schema 1. A schema-1 catalog from the preview must be rebuilt.

The registry currently contains:

```json
{
  "schemaVersion": 1,
  "collections": [
    "bellum-latin-cardwell.json",
    "deh-latin-ussani.json",
    "contra-apionem-latin-boysen.json",
    "antiquities-latin-bamberg78.json",
    "antiquities-english-whiston.json",
    "bellum-english-whiston.json",
    "contra-apionem-english-whiston.json",
    "deh-english-pollard.json"
  ]
}
```

Registry entries are relative to the registry directory. Each collection
manifest declares `id`, `work`, `label`, `citationPrefix`, `language`, `edition`,
`readerPath`, a combined `corpus`, an `extractionReport`, and ordered `books`.
Each book declares `number`, `label`, its corpus shard, expected `sections`,
and, where applicable, `sectionRange`. Corpus/report paths are relative to
that collection manifest. `readerPath` is a site-relative route without a
leading slash, such as `bellum-judaicum/`.

Optional `citationScheme`, `unitLabel`, and `unitLabelPlural` metadata allow
different citation systems. De excidio uses `chapter-paragraph` and retains
`chapter`, `paragraph`, `citationLabel`, structured `citation`, and `readerLink`
in each record. Its `section` field is an internal ordinal used for indexing,
while its visible citation and URL use the chapter-local paragraph. Editorial
`start`/`end` offsets are end-exclusive UTF-16 positions in `record.text`, the
same coordinate system used by search highlights.
Contra Apionem uses `niese` and a structured Niese citation and reader link;
its source chapter milestones are recorded as extraction evidence, not as
a potentially misleading single chapter number on a Niese record. Optional
`phraseBreaks` offsets must be within the record, strictly increasing, and
outside word interiors. They divide phrase adjacency without changing word
tokens, Boolean postings, or original hit offsets.

Collection IDs are distinct lowercase identifiers for a particular work,
language, and edition. The builder rejects duplicate IDs and duplicate
work/language/edition identities. Book IDs have the form
`<collection-id>:<book-number>`. Bundle filenames are namespaced under
`data/<collection-id>/`, so overlapping book numbers cannot overwrite one
another. Catalog `collections[].books` references these qualified IDs; flat
`books[]` entries record their metadata, file paths, sizes, and fingerprints.
Collection and overall totals use `books`, `sections`, `tokens`, and `bytes`.

Passage `record.id` values must be **globally unique across all configured
collections and books**. The current format includes the collection identity,
book, and section. The loader preserves these IDs in records and highlight
spans and rejects collisions. Result groups additionally qualify their
`unitId` with the book ID. Source `record.order` starts at zero within each
collection; returned records gain `resultOrder` for sorting across collections
without changing the original order values.

The programmatic API is:

```js
const search = createCollection(catalog, lunr, {baseURL, fetchImpl});
const result = await search.search(query, {
  collections: ['bellum-latin-cardwell'], // or 'all'; default 'all'
  books: ['bellum-latin-cardwell:1'],     // or 'all'; default 'all'
  scope: 'section',                     // or 'book'
  fold: false,
  onProgress,
  signal
});
```

`selectedBooks` and `matchingBooks` contain qualified IDs;
`selectedCollections` and `matchingCollections` contain collection IDs.
Groups and records include citation, reader, work, language, and edition
metadata. Bare numeric API book selectors and explicit books outside the
selected collections are rejected. The UI resolves legacy URL parameters
before calling this API.

## Rebuilding and checking the site

Run commands from the canonical checkout root. Required tools are:

- **Node.js** with ES modules, built-in `fetch`/`Response`, and WebCrypto. The
  automated checks for this integration used Node 24.19.0. Lunr is vendored;
  the search build does not require an npm package installation.
- **Python 3** for extraction and its unit tests; the integration checks used
  Python 3.12.14. This search pipeline uses the standard library, including
  `xml.etree.ElementTree`; **`lxml` is not a search dependency**. Separate
  editorial tools may have their own Python dependencies.
- **Ruby, Bundler, and the repository's Gemfile dependencies** for the full
  Jekyll site build. They are not needed to build and test the search indexes.

### LF regeneration and Windows publication

Regeneration requires **canonical LF XML bytes**, except for the five exact
accepted Antiquities CRLF path/hash pairs documented below. The extractor and
independent verifier retain the accepted raw source fingerprints.
Use a WSL/Linux checkout with LF XML or an isolated clone created with
`core.autocrlf=false`. `build-search.mjs` checks for CRLF in the configured XML
before changing any generated output and explains this requirement if found.
This does not require changing global Git settings or the canonical XML's
existing attributes.

An ordinary Windows checkout can **check and publish the committed search
export without rebuilding it**. For the configured indexed XML only, the
publication checks compare LF-normalized content and report its indexed,
worktree, and normalized hashes. The extraction and independent QA reports
retain the exact raw fingerprints of the source that was indexed. A change
beyond LF/CRLF representation still fails the checks.

Search source, runtime assets, the search page/include, and the two publication
hooks have narrow `-text` attributes so their hash-bound bytes remain exact on
checkout. This compatibility does not relax the runtime, bundle, template,
or code fingerprints, and does not change the existing XML attributes.

### Commands

The normal workflow is:

```sh
node bin/search/build-search.mjs
node bin/search/check-assets.mjs
bash bin/cibuild
```

`build-search.mjs` runs the configured extractors, builds the per-book indexes,
validates source and extraction evidence, runs the Python and Node unit suites,
and obtains current independent corpus QA. It reuses a PASS QA report only
when its recorded input hashes still match. It then exports the exact approved
runtime and evidence bytes to `assets/search/`, recording their source inputs
and fingerprints in `publication-manifest.json`. Source changes during a build
cause it to stop so the build can be repeated against a consistent snapshot.

Use `--force-qa` to rerun the independent verifier even when its existing report
is current. Select a Python interpreter with `--python /path/to/python3`, or
set `SEARCH_PYTHON` for that command. A fresh independent QA run checks its
reviewed reader baseline as well; if the reader has intentionally changed,
review that change before supplying
`--expected-reader-sha256 <reviewed-lowercase-sha256>`. That option records an
explicit baseline and does not edit the reader. Historical reader evidence is
not an input to ongoing search-index freshness, so a reader-only Antiquities
repair does not by itself invalidate unchanged Bellum indexes.

`check-assets.mjs` is read-only. It checks current configured source, extraction,
QA, runtime, and exported asset fingerprints and inventories. `bin/cibuild`
runs this check, `bundle exec jekyll build`, and then the generated-site check:

```sh
node bin/search/check-assets.mjs --site _site
```

When publishing already committed exports from a CRLF XML checkout, begin with
`check-assets.mjs` and `bin/cibuild`; reserve regeneration for the LF checkout.
The accepted Whiston Book XII and XVII–XX Git blobs themselves contain CRLF.
The build permits those five files only with their pinned raw SHA-256 values
and retains their original bytes in extraction provenance. It does not rewrite
the XML. Publication checks accept their LF representations through the same explicit CRLF-to-LF source comparison
used for the other indexed files; substantive changes still invalidate the index.

The final check verifies the generated page, search assets, and indexed XML.
The existing reader publication command also performs it after its established
reader-byte restoration:

```sh
node bin/prepare-reader-publication.mjs --site _site
```

Keep that command in the site's established reader publication workflow; it
operates on generated output. See
[reader corpus integrity](../../_docs/reader-corpus-integrity.md) for the reader's
separate requirements. Review and commit the search sources and generated
`assets/search/` together. A stale export fails the build checks rather than
being silently regenerated during publication.

For focused development, extraction and index construction can be run directly:

```sh
python3 bin/search/extract.py
python3 bin/search/extract-deh.py
python3 bin/search/extract-ca.py
python3 bin/search/extract-antiquities.py
node bin/search/build-index.mjs
python3 -m unittest discover -s bin/search/tests -p 'test_*.py'
node --test bin/search/tests/*.test.mjs
node bin/search/tests/corpus-qa.mjs
node bin/search/tests/deh-corpus-qa.mjs
node bin/search/tests/ca-corpus-qa.mjs
node bin/search/tests/antiquities-corpus-qa.mjs
```

These commands alone do not refresh the published asset export; finish with
`build-search.mjs`. A custom manifest/index destination can be supplied with
`build-index.mjs --catalog <registry> <catalog> <lunr.cjs>`; `--collection` is
an alias for that mode. The explicit `--single` mode is useful for isolated
fixtures, not the main site's multi-book export.

## Antiquities first batch and later five-book additions

The first batch uses the corrected Bamberg text at development commit
`5d48b5285a5fa921ec5e666f60d04216e6e9270d`. It indexes only the Proem and
Books I–V, bound to six explicitly listed XML files. The public-preview text
at `c303113430c0bd088a7dbeecebcc65997c1e0a1f` has the same source bytes.

The adapter preserves all 424 numbered source paragraphs through reversible
extraction evidence. Every running source word and non-whitespace character
is retained. Original `<add>` and `<del>` content remains searchable, with
its original attributes; `<s>` and `<ref>` spans remain distinct metadata.
In that first batch, III.240 is the only permitted empty citation and requires the source's exact
`<gap reason="omitted"/>` representation. Its English omission note is UI
text, never indexed Latin. CSV source segments retain its zero-width gap.
Titles, subscriptions, printed labels, and annotation notes are excluded with
source evidence. No medieval chapter is invented for a Niese section.

### Second batch: Books VI–X

The second batch adds five explicitly reviewed XML files at the same repaired
source snapshot. It retains all first-batch records, per-book corpora,
extraction reports and index bundles byte for byte.

| Book | Citation units | Word tokens | Coverage |
| --- | ---: | ---: | --- |
| VI | 378 | 16,460 | 1–378 |
| VII | 394 | 15,801 | 1–394, including 31 explicitly omitted empty citations at 69–99 |
| VIII | 420 | 17,810 | 1–420 |
| IX | 232 | 9,209 | 1–50 and 110–291; the source labels 51–109 as a lacuna |
| X | 281 | 10,921 | 1–281, including the empty source interval at 108 |
| Added batch | 1,705 | 70,201 | Books VI–X |

All 342 new numbered running-text paragraphs have reversible source evidence.
The six English notices `Omitted in Bamberg MS` in VII are excluded from the
Latin index with their exact source positions. IX's separate lacuna-notice
paragraph is preserved as excluded source evidence, not a synthetic Niese
record. The manifest and catalog distinguish `missingSections`,
`omittedSections` and `emptySections`; CSV coverage metadata carries them
even when a search returns no matches.

X.108 has a printed citation label followed by whitespace and the milestone
for 109. Its `emptySource` metadata preserves that exact interval and the
following marker. It has no invented TEI gap and does not assert a manuscript
omission. Negative-only searches can return an empty citation with a factual
explanation, without inventing an occurrence.

The source's explicit Niese milestones govern the irregular paragraph starts
at VI.269, VI.271 and X.150. Leading words before the milestone for VIII.187
continue VIII.186; VIII.255 is also continued across source paragraphs.
Coarse division numbers and paragraph IDs remain source evidence and do not
override these citation boundaries.

Added and deleted text remains searchable. New `<unclear>` spans also retain
all original characters and attributes, with visible uncertainty marks and
clipped offsets where a span crosses X.199–200. `<corr>` and `<expan>` preserve
their accepted running letters and source metadata. Column and image markers
are structural; annotation notes and stand-off apparatus are excluded.

There are eight new internal phrase barriers: four in VII, one in VIII,
one in IX, and the two scraped-dot spans in X.154. Ordinary uncertain sentence
periods in X.65 and X.75 remain normal punctuation. Empty intervals, explicit
omissions, the absent IX range and the Proem boundary also stop adjacency.
Whole-book Boolean conditions can still relate words on either side.

### Third batch: Books XI–XV

This batch is bound to the accepted XML and the five matching Latin Niese
identity registries. The source baseline is commit
`55bf610245860eab91166fdb7e4fba891f2c335b` on `v2-development`; the public-preview
baseline is `0b5007af00d003cf474a2e38f63c00a47eabff13`. The source XML, registries,
and canonical readers are preserved.

| Book | Available primary Niese identities | Physical search records | Word tokens | Unavailable identities |
| --- | ---: | ---: | ---: | --- |
| XI | 347 | 354 | 11,589 | None |
| XII | 433 | 433 | 13,683 | 248 |
| XIII | 431 | 431 | 13,803 | 213, 216 |
| XIV | 489 | 489 | 15,148 | 238–239 |
| XV | 423 | 423 | 12,223 | 338, 347 |
| Added batch | 2,123 | 2,130 | 66,446 | Seven identities |

XI's physical record count includes two independently labelled source passages,
**Bellum IV.105a and IV.105b**, and five extra portions of the four split
Antiquities identities **XI.72, XI.312, XI.326, and XI.342**. These passages are
indexed where they occur in the Bamberg witness. Neither Bellum insertion is
assigned a false Antiquities Niese identity. Its link opens the accepted reader
association, XI.312, which displays the corresponding labelled insertion.

The registered extraction preserves physical order, including the second portion
of XI.72 appearing before its first. Each physical portion has a unique `id`;
`citationUnitId` groups primary portions of the same canonical section for Boolean
scope and counts. `sourceOccurrence`, `continuationRank`, and `fragmentCount`
identify split portions. Exact phrases use the physical token stream in both
scopes: adjacent portions may join if the selected scope permits it, but separated
portions never acquire artificial adjacency. Citations list labelled portions
and insertions explicitly instead of implying a consecutive numeric range.

Unavailable identities do not create empty records and do not by themselves
interrupt the surviving physical text. XII.248 includes displaced correspondence
elsewhere; the other registry notes distinguish unavailable correspondence from
an established cause or physical loss. Their complete qualifications remain in
the accepted registry and extraction reports.

Three actual TEI gaps interrupt tokens and phrases: XII.8 and XII.35 are marked
`reason="hole"`, and XIII.393 is marked `reason="fading"`. The last occurs inside
`res<gap/>s`: original source characters remain intact, but search does not invent
the uninterrupted word `ress`. Twelve dotted source additions in XIV are retained
with their markup and conservatively block phrase adjacency. This does not assign
a missing-text extent or treat marginal dots as proof of an omission. No new
`breakBefore` is inferred from a skipped canonical number.

Anonymous narrative paragraphs are preserved with explicit XPath locators rather
than fabricated XML IDs. All source paragraphs are exactly reconstructed from
record slices, excluded labels/notes, and reversible edge whitespace. XV's initial
marginal chapter numeral lies before its first accepted Niese boundary and is
explicitly excluded as an annotation; its source evidence is retained. XII's
untagged nine-word closing subscription follows an explicit `niese-end` milestone;
it is excluded from search and retained in the exact paragraph reconstruction.

The catalog distinguishes `sections` (physical records), `canonicalSections`,
`citationUnits`, `primarySourceSpans`, and `interpolatedSourcePassages` for this
batch. It also exports the registry paths, fragmented identities, and unavailable
identities. CSV source segments preserve physical and logical citation metadata.
That batch used 35 pinned publication inputs: 30 Latin XML documents and
five identity-registry JSON files. CRLF/LF equivalence is accepted without changing
any canonical source file, including XIV's accepted CRLF registry.

### Fourth batch: Books XVI–XX

This batch completes the accepted Latin Antiquities transcription through Book
XX.268. The combined XI–XX publication is prepared directly from the same published
I–X source and preview baselines named above; the separate XI–XV package is not
a prerequisite. All previously prepared I–XV per-book corpora, extraction reports,
and index bundles remain byte-for-byte unchanged.

| Book | Available primary Niese identities | Physical search records | Word tokens | Unavailable identities |
| --- | ---: | ---: | ---: | --- |
| XVI | 380 | 383 | 10,471 | 77, 123, 189–199, 359, 395–404 |
| XVII | 355 | 355 | 15,287 | None |
| XVIII | 377 | 377 | 15,306 | 216–217 |
| XIX | 366 | 366 | 11,791 | None |
| XX | 257 | 257 | 7,864 | 27–36, 238 |
| Added batch | 1,735 | 1,738 | 60,719 | 37 identities |

XVI.294, XVI.295, and XVI.351 each have two registered physical portions.
Their actual accepted start targets identify the occurrences; their array order
supplies the continuation ranks where the registry does not assign separate
occurrence/rank fields. Boolean scope groups portions of one canonical identity,
while exact phrases retain physical text order. No unrelated interval becomes
consecutive merely because it shares a citation.

Two explicitly delimited source interruptions set `breakBefore`: XVI.188→200
and XX.26→37. Their `sourceBoundaryEvidence` records the accepted ending and
starting anchors, source locations, and reversibly excluded notation. Three
literal `[...]` notations in XVI occur after 188, before 200, and after the
closing anchor of 394. XX's inherited English notice about sections 26–37 is
excluded from searchable Latin. The source boundary remains recorded without
adopting the notice's wording as a new claim about the precise extent or cause
of loss. Whole-book Boolean queries can still relate surviving words on both
sides; phrases cannot bridge either interruption. CSV source segments retain
the boundary evidence and explanation.

The new internal gaps are XVI.170's empty, unqualified `<gap/>` and the two dots
in XX.263's `<unclear reason="damage">.n..</unclear>`. They preserve every supplied
source character while blocking phrase adjacency. XVI's terminal closure at
394 and XX's closure at 26 are associated with the end of the preceding record
even when the marker occurs in a later paragraph containing no text belonging
to that record. No unavailable identity receives an invented Latin record.
The accepted registry qualifications do not establish the physical or historical
cause of every unavailable correspondence.

One adopted milestone, XVII.41→42, lies between `eleuati` and `cum` without source
whitespace. The two search tokens follow the accepted section boundary, while
all source characters and display text remain unchanged. Explicit report-only
token-boundary evidence retains both the raw-paragraph word hash and the word
hash after applying that one registered boundary. The whole-book phrase
`"eleuati cum"` remains joinable; this ordinary section seam is not a gap.

In XVIII and XIX, accepted paragraph starts complement the inline Niese markers;
coarse numeric paragraph IDs do not define canonical citations. Explicit labels,
headings, notes, and the five separate book-end `<trailer>` elements are excluded.
Source additions and untagged letters inside accepted running-text spans remain
searchable, including inline Roman chapter letters. No heuristic silently removes
Roman numerals or repairs the transcription.

The complete Antiquities collection has 7,283 physical records, 7,273 primary
identities and two separately labelled Bellum insertions, with 265,023 word tokens.
The completed Latin publication has **45 pinned inputs** across its four works:
**35 Latin XML documents and ten identity-registry JSON files**. Antiquities
accounts for 21 of those XML documents (Proem and twenty books) and all ten registries.

### Adding later collections or editions

Review each proposed source snapshot before expanding coverage. Update the
relevant extractor's accepted ranges,
markup and gap inventory, manifest, publication source projection checks,
and independent witness together. Do not automatically discover and index
every XML file in the directory. The following procedure remains required:

1. **Accept the repaired source and numbering.** Establish which main text,
   edition, languages, divisions, and section labels are included. Coordinate
   with the current repair branch and preserve its reader/display changes.
2. **Implement and review its extraction adapter.** Do not assume the Bellum
   tag structure, leading labels, continuation rules, or contiguous section
   ranges apply. Preserve physical text order and original text offsets, give
   every passage a globally unique ID, and mark omitted textual gaps with
   `breakBefore` and, for intra-unit gaps, `phraseBreaks` so phrases cannot bridge them. Document source exclusions,
   continuations, labels, and any lacunae in reconstruction evidence.
3. **Add independent QA and fixtures.** Verify the accepted source hashes,
   coverage, extracted text, original highlight spans, citations, Boolean and
   wildcard behavior, phrases at valid boundaries, and exclusions at gaps.
   Include checks that Antiquities I and Bellum I remain separate. The reader
   route and numbering used in result links must match the accepted reader.
4. **Extend the accepted collection.** Update its existing manifest in
   `config/collections.json` and its collection-ID keyed adapter in
   `config/publication.json`: `extractor`, `outputDirectory`, explicit `sources`,
   `verifier`, and `qaReport`. Use separate corpus/report paths and the new
   collection's bundle namespace. Supply extraction and QA reports satisfying
   the publication checks. A registered collection without a configured
   extraction/QA adapter is refused.
5. **Rebuild, review, and test the expanded site.** Run the normal workflow,
   inspect the coverage statement, work/book choices, citations, and reader
   navigation, then publish through the site's existing process when accepted.

The shared search engine does not need to combine or retokenize the works as
one corpus. Each new book receives its own index, and each query is evaluated
within the selected text version. The enabled manifests remain the explicit
statement of public search coverage.

## Verification scope

Automated checks cover source hashes and reconstruction; exact-word postings
in both spelling modes; deterministic Boolean, wildcard, and phrase queries;
all adjacent within-book Niese boundaries; exclusion of cross-book matches;
synthetic overlapping works, editions, and languages; collection selection,
loading failures, caching and retry; original highlight offsets; citation and
saved-link parameters; and source/export freshness. Generated-site checks
also examine the page and emitted asset/XML contents.

The independent corpus verifier builds its own token postings and query oracle
rather than reusing the production parser and tokenizer as its expected
answer. Its reports identify the actual files and checks performed. Unit and
corpus tests establish program behavior for that verified snapshot, not the
editorial accuracy of every printed reading.

No browser visual or interactive end-to-end pass is claimed by these checks.
A supported-browser review should still cover rendering, keyboard use, search
submission, pagination, copying links, and navigation into the reader before
publication review is complete.


## Whiston English Antiquities I–XX and browser release consistency

The English adapter (`extract-whiston.py`) uses explicit `milestone unit="niese"`
boundaries in the accepted English `preface.xml` and `book-01.xml` through
`book-20.xml`. Printed
labels, titles and source notes are excluded; inline narrative words and all
punctuation after the controlling milestone are retained. Every raw source
paragraph is reconstructible from UTF-16 source slices and recorded exclusions.
The separate Proem's final unit cannot form a phrase with the narrative's first
unit. Boolean expressions may use evidence in both within Book I.

`whiston-publication.mjs` verifies the source projection against the accepted
XML bytes. `tests/whiston-source-witness.py` independently walks text nodes with
minidom; `tests/whiston-corpus-qa.mjs` checks every indexed word, every interval,
citation seams, cross-book isolation, representative Boolean/wildcard queries,
links and CSV. Book IX's seven inline footnotes are excluded annotations;
their anchors do not interrupt the consecutive running text. All twenty-one English
Antiquities XML files are indexed inputs, among 80 indexed publication inputs overall.
No source or reader correction is part of this search release.

| Whiston book | Niese sections | Word tokens |
| --- | ---: | ---: |
| I, including the Proem | 346 | 21,994 |
| II | 349 | 23,020 |
| III | 322 | 20,955 |
| IV | 331 | 22,900 |
| V | 362 | 23,396 |
| VI | 378 | 28,422 |
| VII | 394 | 28,285 |
| VIII | 420 | 29,968 |
| IX | 291 | 19,074 |
| X | 281 | 18,035 |
| XI | 347 | 20,213 |
| XII | 434 | 25,083 |
| XIII | 433 | 25,616 |
| XIV | 491 | 29,186 |
| XV | 425 | 26,972 |
| XVI | 404 | 23,831 |
| XVII | 355 | 23,725 |
| XVIII | 379 | 24,253 |
| XIX | 366 | 21,575 |
| XX | 268 | 14,435 |
| Total | 7,376 | 470,938 |

In IV.276, the markerless continuation paragraph `english-book04-num276b`
belongs to the same citation as `english-book04-num276`. Their running text
remains one search record with an explicit paragraph separator and reversible
source evidence for each paragraph. Phrases may cross this paragraph boundary
within section scope. Book V's repeated contents headings and chapter titles
are excluded; they do not interrupt the running narrative.

VIII.255 also spans two paragraphs. The paragraph `english-book08-num255`
begins with narrative that continues the preceding paragraph's section 255;
its first explicit milestone is 256. Those opening words remain in 255, joined
with the same explicit paragraph separator and reversible source evidence.
The phrase `"to Jerusalem Now when Rehoboam"` crosses that paragraph join within
section scope. VIII.53 retains the inline salutation around its two `<lb/>`
elements. Book X's four ordinary `<hi rend="bold">` spans retain searchable
words without being classified as editorial additions.

The English IX.51–109 passages remain included, independently of the missing
Latin range. The two restored Book IX headings and all seven inline footnotes
are excluded from running text. English VII.69–99 and X.108 also retain their
own source text. No phrase or Boolean condition can join evidence from different
books, languages or editions.

Book XI contains all 347 Niese sections in the accepted physical sequence
**1–311, 326–342, 312–325, 343–347**. Extraction and search preserve that order.
Whole-book phrases may cross 311→326, 342→312, and 325→343; they cannot invent
the numerical joins 311→312, 325→326, or 342→343. Excerpts and CSV rows name
the actual nonconsecutive citations. The example `"with one voice salute Alexander"`
finds XI.332. The publication gate independently checks the complete section
identity set and the exact source order rather than requiring numerical order.

XII.147 and XII.226 retain continuations before the following paragraphs’ first
Niese markers. XIV.237 likewise retains the twelve opening words of the next
paragraph, including the accepted spellings `Quntius` and `Mercellus`. These
joins use explicit paragraph separators and reversible source spans, just as
IV.276 and VIII.255 do. Book XII’s ordinary bold spans remain narrative words,
not editorial additions. Book XV’s thirteen empty chapter milestones retain
their structural provenance without becoming citation markers or phrase gaps.

Books XVI–XX have complete ascending Niese sequences, with no new markerless
continuations or inline footnotes. Their 282 narrative paragraphs add 1,772
sections and 107,819 tokens. The complete English source has 1,449 narrative
paragraphs. Both XIX.363 and XIX.364 have explicit accepted markers and retain
their own source text; search introduces no new segmentation decisions.
The final five books' empty chapter milestones (16, 19, 21, 8, and 20,
respectively) are structural evidence, not phrase barriers. Book XX's separate
`<head sameAs="#latin-book20-chapter1-head">` is an excluded summary heading.
The example `"the brother of Jesus"` finds XX.200. With all English Antiquities
books selected, `jews` yields 612 occurrences in 544 Niese sections.

The I–XX release preserves the accepted I–XV bundles, corpora and per-book
extraction reports, together with all 34 Latin books. Current coverage in the
loaded interface is taken from the catalog; CSV source metadata identifies the
selected books and their source fingerprints.

Public search HTML loads `launch-v1.mjs`. That launcher name is immutable:
changes to its protocol require a new filename. It fetches `browser-release.json`
with `cache: no-store`; the descriptor selects content-named JavaScript, CSS,
Lunr, and the exact catalog used by the app. `browser-release.mjs` deterministically
rewrites all five modules' static imports, so a changed dependency changes its
parents' filenames as well. Every generated file retains its canonical source
path/hash and generated path/hash in the publication manifest. CSS and Lunr use
SRI; the complete graph and catalog are checked by the publication gate.

Canonical modules remain in the exported audit inventory but public HTML must
not execute the old unversioned app or library. Book bundles retain their
existing filenames and mandatory catalog SHA-256 verification; a cached old
page cannot silently accept changed data. This design does not promise to keep
arbitrary old releases runnable indefinitely. On the first transition from the
old unversioned page, a visitor may need Ctrl+F5 once to load the new launcher.
Subsequent page starts request a fresh release descriptor.

The source build is still `node bin/search/build-search.mjs`; the build owns all
canonical and generated browser assets and removes only its obsolete owned
files. `node bin/search/check-assets.mjs --site <generated-site>` checks the
public page, complete artifact inventory, and all indexed source representations.

## Whiston English Bellum I–VII

The collection `bellum-english-whiston` indexes all seven accepted
`assets/xml/bellum/English/book-0N.xml` files. It is a separate work and edition
from Cardwell's Latin Bellum and Whiston's English Antiquities. The seven books
contain 704 narrative paragraphs and a complete ascending set of 4,001 Niese
sections. Every interval contains running text.

| Whiston Bellum book | Niese sections | Word tokens |
| --- | ---: | ---: |
| I | 673 | 50,097 |
| II | 654 | 38,098 |
| III | 542 | 24,777 |
| IV | 663 | 30,489 |
| V | 572 | 29,415 |
| VI | 442 | 21,949 |
| VII | 455 | 20,247 |
| **Total** | **4,001** | **215,072** |

The extractor uses explicit internal `milestone unit="niese"` boundaries and
retains each containing paragraph's `sameAs` identity as source provenance.
It reconstructs every original paragraph and verifies both the running-word
sequence and non-whitespace text. Book I's prefatory sections 1–30 are embedded
in the same source book. Whole-book phrases follow physical adjacency from
I.30 into I.31; the separate Antiquities Proem rule does not apply here.

The accepted Book VII source contains one `supplied` element spanning the end
of VII.208 and all of VII.209, including the nested section-209 milestone.
Both sections retain their own identities. The supplied text remains indexed
and receives a clipped `supplied` editorial mark in each record: UTF-16
offsets 157–262 in VII.208 and 0–154 in VII.209. Its `reason="omitted"` and
Lexundria `source` attributes remain attached to the marks. This markup does
not create a phrase boundary. Results display supplied text in brackets;
CSV literal columns retain the original text, and editorial columns add the
readable brackets alongside exact source annotations. No scholarly XML or
reader code is changed.

Book V's chapter-13 `div2` has an accepted `n="13"` without a `type` attribute.
The extractor explicitly recognizes that source form without repairing it.
All other expected chapter attributes, section markers, paragraph identities,
and the supplied span are checked against their accepted structure. The source
Git blobs use LF and the existing preview blobs use CRLF; their normalized
bytes match exactly. Publication accepts only this line-ending equivalence.

The new example `"a voice from the east"` occurs once, in VI.301. Reader links
include `english=whiston` for section and whole-book results. English spelling
remains literal apart from capitalization, even when Latin spelling equivalence
is selected in a mixed-language search. Boolean conditions and phrases stay
within their own work, book, and edition.

`tests/whiston-bellum-source-witness.py` independently reads the accepted XML;
`tests/whiston-bellum-corpus-qa.mjs` compares every indexed interval, word sequence,
source seam, supplied span, and the published query results. The source gate
`whiston-bellum-publication.mjs` rejects changed narrative or source markup,
including a changed supplied span. The Bellum addition brought coverage to
73 indexed inputs across six collections. Its existing Latin and Antiquities
per-book data remain unchanged from the accepted Whiston Antiquities I–XX baseline.

## Whiston English Contra Apionem I–II

The collection `contra-apionem-english-whiston` indexes the two accepted
`assets/xml/contra-apionem/English/book-0N.xml` files. It is separate from
Boysen's Latin text and from the other two Whiston works. All sections are
present in ascending source order:

| Whiston Contra Apionem book | Niese sections | Word tokens |
| --- | ---: | ---: |
| I | 320 | 18,497 |
| II | 296 | 18,356 |
| **Total** | **616** | **36,853** |

Each accepted English `p@n` already represents a single Niese section and has
its own `xml:id`, such as `english-apion1-num38`. The extractor preserves that
identity, every running character, internal whitespace, punctuation and the
literal brackets in 44 paragraphs. Only section-edge whitespace is trimmed;
the report retains it for exact paragraph restoration. The source contains no
encoded additions, deletions or gaps requiring editorial display markup.

Niese chapter and Whiston division milestones remain structural metadata.
Book I has 35 chapter and 35 Whiston division markers; Book II has 41 chapter
and 42 Whiston division markers. Two Whiston markers occur inside Niese
paragraphs: division 9 at UTF-16 offset 106 in II.109 and division 10 at offset
4 in II.112. Their following text remains part of the same section. They
contribute no searchable words and create no phrase barrier. The extraction
reports retain every marker's position and original attributes.

Exact phrases work within a section; whole-book phrases may also cross all
614 adjacent section seams, including chapter boundaries. Neither Boolean
conditions nor phrases combine different books, languages, works or editions.
English matching remains literal apart from case, and Latin u/v and i/j
equivalence does not change it. The example `"only twenty two books"` finds
I.38 while retaining the source's hyphenated `twenty-two` in its excerpt.
The word `jews` has 79 occurrences in 71 sections; `the` has 1,859 in 557.

Result and CSV links use `contra-apionem/?book=N&niese=S&english=whiston`;
whole-book links omit the Niese parameter. CSV text columns preserve original
punctuation and brackets, and source segments retain the English XML identity
and source path. The interface and CSV describe Boysen's Latin asterisk
barriers only when that edition is selected.

The independent `tests/whiston-contra-apionem-source-witness.py` parses the
accepted XML with a separate XML implementation. Its corpus verifier checks
every section, token and original-text offset, each source marker, every
adjacent seam, both internal Whiston division markers, quoted and wildcard
phrases, Boolean logic, complete CSV results and collection isolation.
`whiston-contra-apionem-publication.mjs` independently projects the pinned
canonical XML and rejects altered text, identities, structure or provenance,
even when artifact hashes have been recalculated. The Contra Apionem release verified
75 indexed inputs: 65 XML files and ten accepted citation maps. All 61 prior
book editions and their 183 corpus, extraction-report and bundle files remain
unchanged from the accepted Whiston Bellum release.

## Pollard English De excidio, Prologue and Books I–V

The `deh-english-pollard` collection indexes the five accepted English XML files
without changing their text or the reader. Its edition label, **Pollard v1.1**,
matches the canonical reader. English and Latin remain separate search editions.

| Book | Citation units | Word tokens |
| --- | ---: | ---: |
| I, including Prologue | 215 | 40,804 |
| II | 73 | 17,142 |
| III | 70 | 18,640 |
| IV | 79 | 17,259 |
| V | 121 | 42,207 |
| **Total** | **558** | **136,052** |

Each accepted paragraph already supplies an English XML identity, a printed
book–chapter–paragraph citation, and a fragment-only `sameAs` alignment to the
accepted Latin. The extractor retains those identities and the exact original
`sameAs` value. It excludes the complete leading `num` label together with any
indentation before it, rather than treating printed citation numbers as words.
Five release notes and six headings are also excluded. The accepted running
English excludes eight translation-comparison notes from search, while its
reversible ledger preserves every note verbatim. The reader displays the notes
after their English paragraphs; Latin apparatus is not transferred to English.

Every citation paragraph has a reversible text ledger. Whole-book phrases may
cross adjacent paragraphs and chapters. The three Prologue paragraphs may join
one another, but `breakBefore` on I.1.1 prevents a phrase from crossing into the
Book I narrative. Boolean conditions may still relate Prologue and narrative
words within Book I. No query combines evidence across different books or editions.

The example `"a rose among thorns"` has one occurrence, in **Prol.2**. The word
`jews` has 262 occurrences in 158 citation units. Common words are indexed;
`the` has 9,172 occurrences in 556 units. English spelling is retained apart
from case; Latin u/v and i/j equivalence does not change English matching.

Result and CSV links use `deh/?book=N&chapter=C&unit=P&english=pollard`.
The Prologue uses chapter 0; `unit` is the paragraph number within the chapter,
not the internal book-wide index ordinal. Whole-book links omit chapter and unit.
CSV source segments preserve the English source identity, exact original-text
spans, citations and `sourceSameAs` alignment string.

The independent witness uses a separate XML parser and checks every English
citation, all 740 book/chapter/paragraph `sameAs` links and their accepted Latin
targets. Those five Latin files are pinned as test inputs and remain indexed
by the existing Latin collection. The new source gate independently projects
the canonical English XML and rejects altered running text, labels, identities,
alignment or source exclusions, even if artifact fingerprints are refreshed.

The combined build verifies **80 unique indexed inputs: 70 XML files and ten
accepted citation maps**, including 35 English XML files. All 63 previous book
editions, seven collection metadata entries, and 189 per-book corpus/report/index
files remain unchanged from the accepted Whiston Contra Apionem release.
