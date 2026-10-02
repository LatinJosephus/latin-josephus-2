**DEH–Josephus reviewed concordance freeze — Phase 4, 2 October 2026**

This phase applies Richard M. Pollard's explicit human-approved adjudications to
Phase 3 (`0c95013d738ab6f471e34a1fc62d1e76e460b705`). Work began with a clean
`v2-development` worktree in the canonical `LatinJosephus-v2-development`
checkout. There were no pre-existing modified or untracked files.

The candidate was promoted by renaming it to
`assets/data/deh-josephus-concordance.json`; no duplicate candidate remains.
The Phase-3 candidate is recoverable from that historical commit. The reviewed
artifact has `status: reviewed_frozen`, `publication_status:
reviewed_not_published`, date `2026-10-02`, and exactly 555 numbered DEH units.
Its SHA-256 is:

```text
c8f59a9bdfd8c49350b4d2656d1c685f4c4a63bd96450ddfd218ac3c07ca743c
```

The machine audit also records this exact byte fingerprint. Validation checks
the artifact's bytes, raw evidence, ledger fingerprint, canonical XML snapshot,
current coordinate availability, and generated reports. The freeze is a reviewed
scholarly alignment dataset for later publication; it is not connected to the
comparison interface.

The source remains `DEH_Parallels_v0_2_2026-10-02.zip`, SHA-256
`0ef4cd8a2fd0913dcc9f857afdd883941d164f6fd6a20a75390dd40b474fa3e5`.
The student's Ussani/Mras transcription, original row/cell values, raw reference
strings, and original editorial decisions remain preserved. Both files under
`_docs/deh-concordance-source/` are byte-identical to Phase 3. Historical package
audit flags and questions describe the input evidence; current review and QA
are recorded separately. The ledger
`_docs/deh-concordance-editorial-decisions.json` retains P3-D01 and adds P4-D01
through P4-D11, with human authority and adjudication dates. No printed locus
verification or proven textual dependence is asserted by this freeze.

P4-D01 defines parenthetical targets as supplementary, non-contiguous parallels
incorporated alongside principal unparenthesized parallels. Parentheses do not
mark uncertainty. Unparenthesized targets use `primary_parallel`; parenthetical
targets use `supplementary_parallel`. These roles describe parallels, without
establishing levels of textual dependence. Source sequence, punctuation, and
typographical placement remain intact; nothing is sorted, merged, or deduplicated.

| DEH | Decision | Reviewed sequence, in source order |
| --- | --- | --- |
| II.9.2 | P3-D01, retained | Primary BJ II.402–404; supplementary (BJ II.344) |
| I.26.3 | P4-D02 | Primary BJ I.210–211; supplementary (BJ I.205) |
| I.29.3 | P4-D03 | Primary BJ I.255–257; supplementary (BJ I.248) |
| I.30.13 | P4-D04 | Primary BJ I.328–329; supplementary (BJ I.339) |
| III.8.2 | P4-D05 | Supplementary (BJ III.110–114); primary BJ III.115; BJ III.127; BJ III.132–134 |
| V.53.1 | P4-D06 | Primary BJ VII.320–322; VII.341–359; VII.323–334; VII.360–369; supplementary (BJ II.487–498); primary BJ VII.369–388; VII.335–336 |

II.9.2's raw `2.402(344)-404` is unchanged. III.8.2's supplementary component
remains first. V.53.1 retains the Book-II insertion and VII.369 in both ranges.
Neither interpolation nor displacement is encoded as an interpretation.

P4-D07 closes the second component of II.13.7 as AJ XV.38–56, after
AJ XX.247–249. P4-D08 closes IV.30.2 as BJ IV.643–644. Their original
`15.38 et sqq.` and `4.643 et sqq.` survive in raw evidence and the source-notation
segment parse. The authoritative `josephus.targets` sequence uses approved closed
endpoints and `open_ended: false`; no reviewed target is editorially open-ended.

P4-D09 encodes I.6.4's `historia uetus` as `source_label`, associated with its
sole BJ I.77–78 target (`target_orders: [1]`). The interpretation reflects DEH's
own designation of the transmitted narrative. It creates neither an additional
Josephus target nor a modern bibliographical work identity. P4-D10 encodes
I.37.4's `alii` as `alternative_tradition`, corresponding to DEH's `alii ferunt`.
It belongs to AJ XV.64 and XV.67 (`target_orders: [2, 3]`), not BJ I.439–440.
Both annotations retain their literal wording, offsets, approved interpretation,
decision ID, and date, without a stronger source-critical claim.

P4-D11 treats V.53.2's two backslashes as confirmed spreadsheet residue.
They survive only in immutable/raw source-evidence snapshots: the workbook-values
file and the record's raw-value snapshot. Reviewed `other_works.text` is empty
with `no_reference_recorded` status. No bibliographic reference or concordance
annotation is created from the residue. Twenty records retain meaningful
Other-works reference strings; those works remain unnormalized and unlinked.

Resolved package question IDs remain historical evidence under
`source.package_questions`, with explicit record-level resolutions and applied
decision IDs. No reviewed record retains an unresolved editorial question.
The original restoration I.23.2 → BJ I.187 and correction of II.11.3 to
BJ II.487, II.490–493 remain intact, including the erroneous workbook form in
raw provenance. The five blank-reference records retain the limited claim that
no BJ/AJ parallel is recorded; no stronger conclusion is added.

| DEH book | Numbered records | BJ components | AJ components |
| --- | ---: | ---: | ---: |
| I | 212 | 237 | 20 |
| II | 73 | 86 | 21 |
| III | 70 | 91 | 1 |
| IV | 79 | 109 | 0 |
| V | 121 | 182 | 2 |
| Total | 555 | 705 | 44 |

Coverage is 555/555 uniquely resolved canonical citations and IDs, with 555
unique Pollard correspondences, zero duplicate or omitted units, and no Prologue
records. There are 749 normalized components: 743 primary and six supplementary.
All 705 BJ components are now closed and pass Niese-coordinate checks in Greek,
Cardwell Latin, and Whiston English: 2,115 successful component/source checks,
zero failures. Each source retains complete coverage of all 4,001 BJ coordinates.
These checks establish coordinate presence, without claiming full-corpus excerpt
slicing or verbal-equivalence QA.

All 44 AJ components parse structurally and are closed. Only AJ III.184 is
currently addressable through the site's Niese navigation; the other 43 occur
in 30 DEH records. This is a technical support limitation, not an editorial
defect or an invalid concordance. No unsupported URLs or textual IDs are created.

| AJ book referenced | Reviewed components | Currently addressable | Open components |
| --- | ---: | ---: | ---: |
| III | 1 | 1 | 0 |
| IX | 2 | 0 | 0 |
| XIV | 3 | 0 | 0 |
| XV | 16 | 0 | 0 |
| XVI | 1 | 0 | 0 |
| XVII | 1 | 0 | 0 |
| XVIII | 12 | 0 | 0 |
| XX | 8 | 0 | 0 |

The machine audit `_docs/deh-concordance-validation.json` includes all twenty
AJ books and the full DEH coverage summary. The restructured human report
`_docs/deh-concordance-exceptions.md` separates A: zero unresolved editorial
exceptions; B: thirty site-support limitation records (43 AJ components);
C: one provenance-only residue. Support limitations are not counted as editorial
exceptions. Unresolved parenthetical meanings, open endpoints, annotation
meanings, and semantic residue entries are all zero.

The existing dependency-free validator and PowerShell 7 XML helper are reused.
From the repository root:

```powershell
node bin/deh-concordance.mjs freeze 'C:\path\to\DEH_Parallels_v0_2_2026-10-02.zip'
node bin/deh-concordance.mjs validate
node bin/deh-concordance.mjs validate --self-test
```

`freeze` verifies source-package agreement, canonical identities, adjudications,
closed BJ coordinates, zero editorial exceptions, and pilot semantics before
writing the reviewed artifact and reports. It never publishes data through the
interface. `validate` is read-only and rejects stale fingerprints/reports.
Twenty-six in-memory negative checks passed, including lost order or parentheses,
changed endpoints, reopened BJ/AJ ranges, reintroduced uncertainty, lost authority,
incorrect annotation association, residue exposed as a reference, altered raw
notation, and changed frozen/publication status. Repeat freeze produced identical
bytes for the reviewed artifact, retained source snapshots, and generated reports.

The active pilot still loads only `assets/data/deh-bj-alignment.json` and exposes
the ten I.1 units plus V.53.1. Its data, comparison include/style, and
`dehParallels.js` module are byte-identical; new role metadata is confined to
the reviewed freeze. The existing Phase-2
parenthetical display wording remains with the active pilot for a later UI phase.
Automatic semantic comparison confirms all eleven approved correspondences,
their order, ranges, parenthetical position, and repeated VII.369 unchanged.

Browser regression QA passed: eleven units × six source combinations = 66 cases;
eleven unit reloads; eight back/forward checks across both selectors; two shared
URLs reopened and reloaded with non-default sources; independent switching
preserving the other pane's text; ordinary DEH return/reopen; and no comparison
link for reviewed I.26.3 outside the pilot. Ordinary BJ I.48 navigation also
resolved all three panes and displayed the concurrent `Niese section 48` label.
All source identities, passage IDs,
ordered components, and cloned DOM IDs passed; no browser warning/error logs
were observed. Both temporary QA tabs were closed; user tabs were preserved.

A Jekyll build with only `jekyll-responsive-image` omitted passed, retaining the
known missing `rmagick >= 2.0, < 5.0` limitation. Existing Sass, pagination, and
Faraday warnings remain. The fully configured build is not claimed to have
passed. No dependency installation or environment repair was performed.

All 100 canonical XML files remain byte-identical and Git-unchanged. The retained
source evidence and active pilot data/component files remain byte-identical.
During this phase, concurrent work changed two navigation-label strings in
`assets/js/renderTei.js`. This task did not edit that file and excluded it from
staging. Its current SHA-256 is
`739a35e2045da7d42bc765fbb041f924179cdfcef59120f54c5d203324daf355`,
identical to the built copy used by the browser QA; those tests therefore cover
the observed concurrent version. No unrelated, branding, preview, or
recovery-repository work is included. Only the promoted
concordance, decision ledger, validator, reports, and this document belong to
the local commit `Adjudicate and freeze DEH-Josephus concordance`. No push,
deployment, full-concordance UI publication, or next UI phase is included.
