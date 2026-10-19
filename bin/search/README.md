# Latin Josephus search

This directory contains the source and verification tools for the main site's
`/search/` page. Current coverage comprises two Latin collections:

- **Cardwell's *Bellum Judaicum*, Books I–VII:** 4,001 Niese sections and
  114,794 word tokens.
- **Ussani's *De excidio Hierosolymitano*, Books I–V, including the Prologue:**
  558 chapter/paragraph citation units and 87,472 word tokens.

Together these comprise **12 books, 4,559 citation units, and 202,266 word
tokens**. **Antiquities is not indexed**; it can be added after the relevant
text repairs and extraction checks are accepted. Translations are not indexed.

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
**u/v and i/j equivalence** applies to both indexed words and the query. Search
normalization preserves the original displayed text and its highlight offsets.
Accents are retained.

### Section and whole-book scope

**Section / citation-unit scope** evaluates the complete Boolean expression
within one Niese section of Bellum or one cited paragraph of De excidio. A
phrase must fit entirely within that unit.

**Whole-book scope** evaluates the complete expression within each selected book
of one work, language, and edition. Distinct Boolean terms can occur in different
sections of that book. A phrase must remain consecutive, but may cross Niese or
chapter boundaries within the book. An explicit structural boundary or textual
gap, represented by `breakBefore`, prevents a phrase from joining the text on
either side. In De excidio, the three Prologue units are searchable and can be
joined to each other in whole-book phrases, but a phrase cannot cross from the
end of the Prologue into the Book I narrative. This is a composition boundary,
not an inferred lacuna. Whole-book Boolean conditions can still relate
Prologue and narrative hits within Book I.

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

Bellum-only exports retain the established 51 columns. De excidio and mixed
exports have 56 columns: five additional fields after `reader_url` identify the
citation scheme, give editorially marked versions of the left context, matched
text, and right context, and explain the notation. The original literal text
columns remain exact. In the readable editorial columns, `[text]` marks
supplied text and `⟦text⟧` marks editorial deletion; the latter signs are export
notation, not characters inserted into the indexed Latin. `source_segments_json`
also records each source editorial span with exact UTF-16 offsets.

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

The browser first loads `catalog.json`, then downloads only the selected books.
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
cannot be confused with Bellum I. The bare page retains **Bellum, all seven
books** as its default. Choose **De excidio Hierosolymitano** for its five books,
or **All works** to search both collections.

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
changes together. The De excidio release package builds on the reviewed
concordance commits and includes their history, so it can publish from either
the earlier live search or the concordance stage. Its helper verifies the Git
objects and uses ordinary fast-forward pushes without applying a patch to the
user's working files. See the release package for its pinned commits, supported
starting states, checksums, and publication command. A patch is a review aid.

The search build **reads canonical XML without modifying it**:
`assets/xml/bellum/Latin/book-01.xml` through `book-07.xml`, and
`assets/xml/deh/Latin/book-01.xml` through `book-05.xml`. The configured source
lists, extraction reports, and independent QA record the actual source hashes.

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

### De excidio

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

## Source, generated files, and configuration

| Location | Role |
| --- | --- |
| `extract.py`, `tests/test_extract.py` | Bellum extraction and reconstruction checks. |
| `extract-deh.py`, `tests/test_extract_deh.py` | De excidio extraction, editorial annotations, and reconstruction checks. |
| `corpus.json`, `data/book-0N.corpus.json` | Generated combined and per-book original-text records. |
| `extraction-report.json`, `data/book-0N.extraction-report.json` | Generated coverage and reconstruction evidence. |
| `engine.mjs`, `vendor/` | Boolean/phrase/wildcard engine and pinned Lunr 2.3.9 with licence and provenance. |
| `collection.mjs` | Qualified selection, verified loading, caching, and independent per-book evaluation. |
| `app.mjs`, `ui-utils.mjs`, `styles.css` | Source for the browser interface, citations, links, and excerpts. |
| `config/collections.json` | Ordered registry of enabled collection manifests. |
| `config/bellum-latin-cardwell.json`, `config/deh-latin-ussani.json` | Collection metadata, corpus inputs, citation terminology, and expected coverage. |
| `config/publication.json` | Runtime export inventory, site/build inputs, and approved extraction/QA adapters. |
| `build-index.mjs`, `catalog.json` | Manifest-driven index builder and generated catalog. |
| `data/bellum-latin-cardwell/book-0N.bundle.json` | Generated independent indexes, one per book. |
| `tests/corpus-qa.mjs`, `qa-report.json` | Independent source/query verification and its current evidence. |
| `data/deh-latin-ussani/` | De excidio corpus shards, extraction reports, book indexes, and independent QA report. |
| `tests/deh-corpus-qa.mjs` | Independent De excidio XML witness, token, query, boundary, and mixed-collection checks. |
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
  "collections": ["bellum-latin-cardwell.json", "deh-latin-ussani.json"]
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

Regeneration currently requires **canonical LF XML bytes**, because the
extractor and independent verifier retain the accepted raw source fingerprints.
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
node bin/search/build-index.mjs
python3 -m unittest discover -s bin/search/tests -p 'test_*.py'
node --test bin/search/tests/*.test.mjs
node bin/search/tests/corpus-qa.mjs
node bin/search/tests/deh-corpus-qa.mjs
```

These commands alone do not refresh the published asset export; finish with
`build-search.mjs`. A custom manifest/index destination can be supplied with
`build-index.mjs --catalog <registry> <catalog> <lunr.cjs>`; `--collection` is
an alias for that mode. The explicit `--single` mode is useful for isolated
fixtures, not the main site's multi-book export.

## Adding Antiquities after the text repairs

The generic page and collection loader can remain in place while Antiquities
repairs continue. Addition should be tied to a reviewed text snapshot and its
own extraction evidence, not to a directory-wide discovery of XML files.

1. **Accept the repaired source and numbering.** Establish which main text,
   edition, languages, divisions, and section labels are included. Coordinate
   with the current repair branch and preserve its reader/display changes.
2. **Implement and review its extraction adapter.** Do not assume the Bellum
   tag structure, leading labels, continuation rules, or contiguous section
   ranges apply. Preserve physical text order and original text offsets, give
   every passage a globally unique ID, and mark omitted textual gaps with
   `breakBefore` so phrases cannot bridge them. Document source exclusions,
   continuations, labels, and any lacunae in reconstruction evidence.
3. **Add independent QA and fixtures.** Verify the accepted source hashes,
   coverage, extracted text, original highlight spans, citations, Boolean and
   wildcard behavior, phrases at valid boundaries, and exclusions at gaps.
   Include checks that Antiquities I and Bellum I remain separate. The reader
   route and numbering used in result links must match the accepted reader.
4. **Register the accepted collection.** Add its manifest to
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
