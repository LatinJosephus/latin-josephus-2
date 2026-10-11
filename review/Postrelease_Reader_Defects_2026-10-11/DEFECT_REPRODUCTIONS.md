# Five current defect reproductions

Canonical base 4ffbc79b84806d180e9d713f9605255e7dfed73e; public preview afea19c25456c4476c37e4ce7164a2b8ed3b61c8. Both were independently observed in fresh browser profiles. Full raw before states, console stacks, exact hrefs, source targets, note/ID markup and screenshots are in FIVE_DEFECTS_baseline.json and FIVE_DEFECTS_live.json.

| Package | Actual before state |
|---|---|
| A | Unnamed unfocusable theme anchor; no button role, label or pressed state. |
| B | Two annotations IDs: converted Latin standOff plus UI accordion in Books XI/XX. The ID is defined only in Latin source files across all 143 XML inputs. |
| C | Three dot anchors in Latin I.34, Bamberg division 5; three absent target UUIDs; two exact malformed GET404 URLs. Source trace records all missing identifiers. No exact target mapping can be inferred from nearby notes. |
| D | Home/About/Background call reader initialization with no WORKS entry and throw on activeWork.languages. |
| E | I.1 yields null canonical selection, dereferenced by parseAnnotations. Narrative I menu starts at 27; Proem 1 is separately supported. |

VII.6 was positively checked during both baselines: complete existing first Whiston paragraph exactly once. Original audit VII.1 failure is not carried forward as a current exception.

A baseline capture initially stopped when Chromium displayed its native error for the deliberately failing local 404 target. That partial capture and script are preserved in runtime attempts/baseline-http-error; the narrow expected-link failure was then recorded explicitly and the whole baseline capture rerun. No production assertion was relaxed.
