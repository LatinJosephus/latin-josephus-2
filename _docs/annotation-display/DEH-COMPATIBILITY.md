# DEH compatibility assessment

The common model separates textual location, folio references, annotating hands, annotation category, transcription status, source notation and identity. The compact display, manuscript-reference lookup, native scholarly details, stable presentation anchors and whole-unit navigation can be reused for DEH.

The citation lookup already reads the existing DEH Latin `<num>` labels and retains its book/chapter/section system. `latin-deh1-num78` resolves to `I.26.3`, with `/deh/?book=1&chapter=26&unit=3` as its reader destination. It never receives a Niese citation. The distinction is covered by automated tests and actual-reader comparison.

The Josephus symbol interpreter is enabled only for Antiquities and Bellum. Passing a DEH record returns unresolved notation without assigning a hand, interpreting `¤`, or imposing the recovered Josephus key. No DEH annotations are imported, generated, invented or changed. Existing DEH books continue to hide the annotation panel where no apparatus is encoded.

A future DEH annotation integration needs a verified source adapter specifying its record boundaries, canonical IDs where available, manuscript registry, notation conventions, hand classification, foliation and transcription-completeness evidence. It must establish associations to existing DEH units independently. The current renderer and model do not supply that missing editorial evidence.

DEH Latin/English files, existing DEH↔Josephus concordances, parallel data and parallel renderer files are unchanged. Representative DEH reader views match development exactly, its parallel controls remain available, and the existing parallel-integrity guard is included in QA.
