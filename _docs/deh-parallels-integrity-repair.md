# DEH–Bellum source-integrity serialization repair, 12 October 2026

Baseline: `0cec37dce62153af14c550cc97aa01912b2f56a9`. Isolated candidate only;
canonical integration and publication require separate authorization.

The public comparison fails independently in DEH Books I–V. It first loads
Ussani for the selected book, checks its raw response SHA-256, and aborts before
parsing or fetching the comparison's Pollard/Bellum sources. Book I is not a
global prerequisite for Books II–V. Ordinary-reader fetches must be distinguished
from this separately verified comparison loader.

The frozen concordance at review commit
`82d36810a5bc126ad5587784579c1dfb64e8443d` binds CRLF XML. The static public
preview serves LF checkout bytes. Independently downloaded responses and recovered
review authorities prove that all 31 relevant XML files differ solely by CRLF/LF:
5 Ussani, 5 Pollard, and 7 each Niese, Cardwell and Whiston. Reconstructing CRLF
reproduces each ORIGINAL frozen hash exactly. Parsed text, markup, IDs, metadata,
boundaries and order agree. Paths and book identifiers are unchanged; fresh
requests reproduce the mismatch without browser or service-worker caching.

`reviewed-crlf-or-exact-lf-v1` keeps literal SHA verification first. For XML only,
a response with no CR bytes may additionally be checked by inserting CR before
each LF, hashing the resulting bytes, and requiring equality to the original
reviewed SHA. No decoding, XML parsing, whitespace/text normalization or expected
hash replacement participates in that check. Mixed endings, bare CR and any
other changed bytes fail closed. The concordance retains literal-byte verification
and its original SHA. Accepted LF XML is then parsed normally; XML parsing gives
the same text and structure for those proven representations.

The core import has a new version to prevent an old cached verifier from being
combined with this correction. The extraction, correspondence adapter, target
ordering, navigation, notices and source identities are otherwise unchanged.
No XML, frozen concordance, provenance record, ordinary-reader module, CSS or
publication configuration is edited.

Repeatable additional guard:

```text
node bin/deh-parallels-integrity-qa.mjs
```

This verifies 62 literal/LF source acceptances, 279 source-corruption rejections,
literal-only concordance verification, failure-cache eviction and HTTP refusal.
The established 143-XML corpus guard and 38 literal generated-publication
authorities remain unchanged. The historical scholarly-import validator still
requires its original 100-file inventory; it is run unchanged against that
independently restored snapshot, including all 26 mutation tests. Its rejection
of the later expanded canonical inventory is preserved as historical evidence,
not suppressed or rebaselined.

The task dossier is `C:\workspace\DEH-Bellum-Parallels-Repair-20261012`.
It contains actual five-book public failure/network traces; all expected/observed
hashes; independent XML text expectations; book-level native-interface receipts;
all 539 eligible records × 6 witness combinations for both serializations;
555 ordinary-unit controls, excluded/no-parallel and Prologue tests; native
navigation/history; build and cross-work evidence; original failures and retests;
review diff and recovery instructions. Its final certificate is issued only after
all required checks and offline recovery complete.

Scholarly qualifications remain as reviewed: printed Ussani/Mras references have
not been independently checked; component order follows the edition; parallels
do not assert exact equivalence, full-unit correspondence or dependence between
Latin versions. AJ evidence remains in the frozen file and is not published as
Bellum. Supplementary components and deliberate repetitions remain separate.

Rollback after a separately authorized integration: revert this isolated repair
commit in a new review branch, preserving unrelated changes. During this task
canonical and preview remain untouched; recovery uses the supplied bundle and
literal-source manifests in a new directory. Never reset or overwrite a shared
checkout.
