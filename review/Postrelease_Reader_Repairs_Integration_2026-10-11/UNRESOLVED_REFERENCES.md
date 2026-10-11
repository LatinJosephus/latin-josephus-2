# Package C — permanent unresolved-reference register

Status: **EDITORIAL HOLD; not repaired and not passed.** The user explicitly accepted this disposition on 11 October 2026. The hold does not block completion of A/B/D/E.

Frozen source: 4ffbc79b84806d180e9d713f9605255e7dfed73e. Public reproduction: afea19c25456c4476c37e4ce7164a2b8ed3b61c8. Source: `assets/xml/antiquities/Latin/book-01.xml`, SHA-256 `236397efea41558911881fbc807eec7f9b01d6058bbc51610f3550c2df77b973`.

| Source location | Original reference targets |
|---|---|
| Line 35, column 501, Latin I.34 | note_837e454f963d4cd5b8428a0b985d64a8 note_1848bd9ae426435f94ce4bf1ed09c961 |
| Line 35, column 598, Latin I.34 | note_837e454f963d4cd5b8428a0b985d64a8 note_1848bd9ae426435f94ce4bf1ed09c961 note_5e738419cb1e4ad3a8b566ed1ed83808 |
| Line 35, column 733, Latin I.34 | note_837e454f963d4cd5b8428a0b985d64a8 note_1848bd9ae426435f94ce4bf1ed09c961 |

The exact raw markup, all current corpus searches, individual Git-history searches, and full surviving candidate note/apparatus markup are preserved in UNRESOLVED_REFERENCES.json. No secure correspondence links the missing UUIDs to those candidates. No note was invented, renumbered, substituted, disabled or redirected. Scholarly XML is unchanged.

The three links still reproduce in `/antiquities/?book=1&bamberg=5`; they generate two distinct malformed 404 destinations, documented in FIVE_DEFECTS_baseline.json and FIVE_DEFECTS_live.json. A correct source mapping requires editorial evidence. Adding a fragment marker to a nonexistent ID is not a repair.

Future disposition: recover authoritative target evidence, then submit a focused packet for editorial approval. A qualified unresolved-reference UI is a possible separate task; it is not authorized here.
