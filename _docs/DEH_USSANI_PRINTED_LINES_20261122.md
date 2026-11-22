# Ussani printed line numbers

The DEH reader provides an optional **Show Ussani line numbers** setting for all
five books. Labels appear every fifth printed line, matching Ussani's marginal
counters. They are empty inline markers with margin labels: they do not impose
printed line breaks or change the Latin text. Each label identifies its printed
page and line in its accessible name and hover title. The preference is saved,
and `ussaniLines=1` enables it in a reader link.

## Source and coverage

Authority: Ussani, *CSEL* 66.1 (1932), publisher PDF:
<https://austriaca.at/0xc1aa5572%200x0041b17a.pdf>.

PDF SHA-256:
`3c2068f1c4edcb7d4df899f787c2d58f96554cd78ecc1478c0b6c6a096404d78`.
Printed page N is PDF page N + 4 (one-based).

All 415 printed text pages, pp. 3–417, were checked. The resulting maps contain
2,106 fifth-line markers:

| Book | Markers | First–last marker page |
| --- | ---: | --- |
| I | 637 | 3–128 |
| II | 266 | 128–181 |
| III | 285 | 181–238 |
| IV | 268 | 238–292 |
| V | 650 | 293–416 |

Page 417 has only four printed text lines, so it has no fifth-line marker.
Page numbers shared by two books retain the printed page's continuous numbering.
The manifest records each page's printed line count and the treatment of the
book headings. Editorial apparatus is excluded.

## Verification

Printed margin counters were inspected against the publisher's page images for
every text page. Geometric line reconstruction was checked against those
counters. Twenty-three rows of editorial apparatus misidentified by OCR were
excluded. Main-text OCR was aligned to the canonical text; straightforward
positions required an exact initial eight normalized letters and at least 85%
agreement over the forward context. A further 338 uncertain starts and 330
independent word-boundary or left-edge checks were inspected visually. Eighteen
offsets were corrected, including an independently checked pilot position.
The approved four-page pilot's 18 positions are retained.

The full reader was then checked in the browser: all 2,106 markers matched the
reviewed offsets exactly, and all 558 paragraph hashes matched. The line toggle
preserved the Latin text. Book changes, sub-chapters without a fifth-line
counter, saved preferences, and navigation to the last printed page passed.
A deliberately incorrect paragraph hash withheld that paragraph's three labels;
the verified map was restored afterward.
Mobile layout showed no horizontal overflow, and the labels were visually
checked in both light and dark themes.

## Data and maintenance

`assets/data/deh-ussani-lines/manifest.json` records coverage, source identity,
page counts, and per-book totals. The five `book-NN.json` files use stable TEI
paragraph IDs, UTF-16 offsets, paragraph SHA-256 hashes, and paragraph lengths.
Their `source_xml_git_sha256` values identify the literal Git XML bytes used.
No canonical XML, translations, main TEI renderer, or existing citation controls
were changed by this feature.

The runtime verifies the complete paragraph's text length and SHA-256 before
placing any labels. A changed or differently rendered paragraph receives no
labels. Offsets must be reviewed against the printed edition when text changes;
do not update hashes merely to silence a mismatch.

The new module and stylesheet load only in the DEH reader. The published static
reader mirrors the source templates and shares identical map, script, and
stylesheet assets. The line-number option is off initially and respects a saved
reader preference or the explicit URL parameter.
