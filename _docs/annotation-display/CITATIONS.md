# Verified citation mapping

The generated lookup is `assets/data/alignment-citations.json`. Regenerate with `python -B bin/build-annotation-citations.py`; check reproducibility with the same command plus `--check`. No scholarly XML is written.

## Evidence and method

The generator reads the canonical Latin XML and, where present, the existing certified `assets/xml/antiquities/niese/*.json` identity registries. SHA-256 provenance for every input appears at the lookup's top level; every mapping lists its contributing paths. The lookup is a disposable presentation derivative, not a second maintained segmentation authority.

For ordinary segmentation the generator reads actual paragraph citation labels and internal `milestone unit="niese"` elements. It intersects observed section spans with narrative character positions. Inline notes, apparatus and citation-label text cannot create narrative coverage. The last observed section extends to the actual end of the book, without deriving an end from a subsequent unit number.

Where certified fragment spans exist, their explicit start/end locators take precedence over inherited labels. Suppressed labels remain suppressed. Interpolation spans are excluded. Unavailable sections are not manufactured. The resolver lists separate actual intervals when coverage is not contiguous. Legacy chapter-level source references receive the union of the verified coverage of their actual constituent paragraphs; they are not silently narrowed to the first paragraph.

The numeric suffix of an alignment ID supplies an existing navigation key only. It is never used to calculate a Niese identity.

| Work and canonical unit | Public citation |
|---|---|
| Antiquities `latin-book01-num27` | Book 1, Niese §§27–33 |
| Bellum `latin-bellum1-num27` | Book 1, Niese §§27–29 |
| Bellum `latin-bellum1-num30` | Book 1, Niese §30 |
| Antiquities `latin-book11-num321` | Book 11, Niese §§321–326, 342 |
| Antiquities `latin-book11-num346` | Book 11, Niese §§346–347 |
| Antiquities `latin-book20-num266` | Book 20, Niese §§266–268 |
| Bellum `latin-bellum1-num670` | Book 1, Niese §§670–673 |
| Bellum `latin-bellum7-num454` | Book 7, Niese §§454–455 |
| DEH `latin-deh1-num78` | I.26.3 |

## Shared interface

`ManuscriptAnnotations.resolveAlignmentCitation(work, alignmentUnitId, options)` returns the original work key and ID, a readable citation, citation system, start/end boundaries, explicit intervals, navigation target, verification status and provenance. `includeWork: true` adds a work label outside the work-specific reader; `lang: 'fr'` selects French labels. Separate work namespaces prevent the same number from aliasing across corpora. `setCitationData` supplies the generated lookup; the reader loads it lazily when apparatus exists.

The established Bellum route is `/bellum-judaicum/`. DEH navigation uses its chapter-local unit reference. Existing reader source preferences are retained by passage links. In fragment views, an annotation still cites its full original unit; “View passage” opens that whole unit before highlighting it. No annotation is assigned to a word, sentence or first Niese section alone.

## Association exceptions

2,937 of 2,958 manuscript reading records have verified citations. The remaining 21 have defective or absent source associations. They are not mapped by inferred numerical or verbal similarity. Their source-book display says “Textual citation not verified”, retains the exact source reference and offers no invented passage link.

The exceptions comprise four records whose Antiquities I passage reference is `#LeidenUBVLF17`; ten other Antiquities I records with absent passage references; one Antiquities VI record with `#ChartresBMMs29`; one Antiquities VII record with `book-03#latin-book03-num9`; three Antiquities VIII records with absent references; one Bellum I record with `#BernBBMs183`; and one Bellum III record with no passage reference.

The [record-level register](notation-qa.json) identifies each source book, manuscript reference, original notation and stable display anchor. These are documented exceptions requiring source-level editorial decisions in a separate task. This implementation preserves them unchanged.
