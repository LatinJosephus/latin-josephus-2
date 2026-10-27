# DEH compatibility and integration

The common model separates textual location, folio references, annotating hands, annotation category, transcription status, source notation and identity. The compact display, manuscript-reference lookup, native scholarly details, stable presentation anchors and whole-unit navigation can be reused for DEH.

The citation lookup already reads the existing DEH Latin `<num>` labels and retains its book/chapter/section system. `latin-deh1-num78` resolves to `I.26.3`, with `/deh/?book=1&chapter=26&unit=3` as its reader destination. It never receives a Niese citation. The distinction is covered by automated tests and actual-reader comparison.

The Josephus symbol interpreter remains enabled only for Antiquities and Bellum. An unconfigured DEH record still returns unresolved notation without assigning a hand, interpreting `¤`, or imposing the recovered Josephus key. The separately configured DEH CSV adapter now interprets the structured file supplied and clarified by the editor on 27 October 2026.

The [DEH integration report](../deh-annotations/README.md) documents all 1,917 records, source preservation and the editor's instructions. Their locations are chapters, rather than alignment units: I.26 covers its complete verified chapter and never becomes I.26.3. The editor explicitly assigned the source's sole 0.1 entry to the whole prologue. The shared citation lookup now provides all 177 chapter targets alongside the existing paragraph citations.

DEH Latin/English/French files, existing DEH↔Josephus concordances, parallel data and parallel renderer files remain unchanged. The existing source and parallel-integrity guards remain part of QA. Record fields for location, folio/page, hand, category, text and source notation are independent, so other corpora can supply their own adapters without adopting either notation convention.
