**Full DEH–Josephus candidate concordance — Phase 3, 2 October 2026**

This data-only phase extends the approved Phase-2 baseline
`0e837a22d7d81ea0304c7afc315fea4735be4886` in the canonical
`LatinJosephus-v2-development` checkout on `v2-development`. Local HEAD,
`origin/v2-development`, and a read-only lookup of the remote branch all matched
that baseline before changes. The actual initial worktree inventory included
branding and Bamberg preview changes; all were preserved and excluded.

The source is `DEH_Parallels_v0_2_2026-10-02.zip`, SHA-256
`0ef4cd8a2fd0913dcc9f857afdd883941d164f6fd6a20a75390dd40b474fa3e5`.
The student reports that these references were transcribed from Ussani/Mras,
describe passages of variable extent, and follow the order relevant to DEH.
The exact printed reference locations remain unverified. Parenthetical meanings
remain unresolved except for the user's explicit II.9.2 clarification. The
package's English source values and editorial decisions are
retained byte for byte in `_docs/deh-concordance-source/`; package and entry
fingerprints are stored in the candidate and audit. Original source notation
and student interpretations remain evidence, not new site-level assertions.

The separate `assets/data/deh-josephus-concordance-candidate.json` contains exactly
555 numbered DEH records. The frozen corpus has 558 units; the three Prologue
units are excluded, and no parallels for them are invented. Every transcribed
citation is resolved against the current Latin XML's visible scholarly label,
not its spreadsheet row. Canonical Latin IDs and Pollard `sameAs` targets each
resolve uniquely. In Book I, I.1.1 is `latin-deh1-num4` and I.46.2 is
`latin-deh1-num215` after the three Prologue units.

The candidate retains the Phase-2 schema's DEH identity, raw values, row/cell
provenance, ordered `josephus.segments`, parenthetical positions, other-work
strings, applied decisions, and unresolved questions. The minimal extension
adds an ordered `josephus.targets` array and explicit annotations/unresolved
tokens. Each normalized target carries work, book, inclusive start/end, form,
order, segment position, parenthetical/open-ended status, Roman-book citation,
raw substring and offset, editorial status, and coordinate validation.

`josephus.targets` is the conservative sequence for future integration.
`josephus.segments` preserves the package's original segmented parse as evidence;
it must not be treated as approving unresolved attempts. During this phase,
Richard M. Pollard explicitly clarified II.9.2: BJ II.402–404 is the primary
parallel, followed by parenthetical supplementary BJ II.344. Project decision
P3-D01 is retained separately in `_docs/deh-concordance-editorial-decisions.json`,
with its authority, exact raw notation `2.402(344)-404`, and ordered targets.
Both normalized targets carry the confirmed roles and decision ID. The original
package parse and question Q01 remain historical evidence; an explicit
record-level resolution supersedes Q01 only for II.9.2. No meaning is inferred
for parentheses in other records. The decision file is fingerprinted in the
candidate and audit, and repeat import applies it without altering ZIP evidence.

Source order is never numerically sorted, merged, or regrouped by work/book.
I.1.4 remains `BJ I.48 → BJ I.42–44 → BJ I.47`. I.37.5 preserves
`BJ → AJ → AJ → AJ → BJ`. V.53.1 retains all seven approved components in order,
including (BJ II.487–498) and VII.369 in both supplied ranges. Automatic
comparison checks both the retained segments and normalized target sequence
against all eleven approved pilot records.

The confirmed addition I.23.2 → BJ I.187 is retained as `student_correction`,
with explicit authority, decision D04, and no fabricated original spreadsheet
row. Its canonical ID is `latin-deh1-num68`. II.11.3 retains the workbook's raw
`2.487, 290-293`, but its effective reference and targets are
`BJ II.487; BJ II.490–493`, with decision D05 and the student's confirming
authority in the retained editorial decisions.

The five empty-reference records are I.3.1, II.5.3, III.2.1, IV.5.1, and V.1.1.
They retain valid canonical identities and `no_bj_aj_parallel_recorded` status.
The safe wording is “No BJ/AJ parallel is recorded in the edition's references.”
This does not establish originality, Christian interpolation, or absence of
other sources. Three of these five records retain other-work references.

Eight expressions contain parentheses: six reference cases and two textual
annotations. II.9.2 has the user's confirmed supplementary role. The other five
reference cases retain unresolved meaning. Clear citation syntax, including
`3.(110-114)`, can be parsed while its parenthetical meaning remains unresolved.
No confidence, interpolation, displacement, secondary-source, or approximate-match
flag is assigned.
The annotations `= historia uetus` and `= alii` retain their raw text and positions
without interpretation. II.13.7's AJ XV.38 et sqq. and IV.30.2's BJ IV.643 et sqq.
have known starts, null ends, and `open_ended: true`. No endpoints or closed
excerpts are invented. Other works remain unnormalized source strings; the two
backslashes at C555/V.53.2 are retained as residue, not counted as a reference.

Candidate and published data are deliberately separate. The interface continues
to load only `assets/data/deh-bj-alignment.json`, containing the ten I.1 records
and V.53.1. The candidate has `publication_status: candidate_only`; no renderer,
selector, comparison card, source control, or link wiring changed. It is not
loaded by the comparison interface. Later editors can review and select candidate
records for promotion in a separately approved phase; this phase does not publish
the full dataset, add AJ panes, or create Other-works links.

| DEH book | Records | With BJ | With AJ | Both | No BJ/AJ recorded | Other-work reference strings | BJ components | AJ components |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| I | 212 | 209 | 14 | 12 | 1 | 6 | 237 | 20 |
| II | 73 | 63 | 14 | 5 | 1 | 5 | 86 | 21 |
| III | 70 | 69 | 1 | 1 | 1 | 2 | 91 | 1 |
| IV | 79 | 78 | 0 | 0 | 1 | 4 | 109 | 0 |
| V | 121 | 120 | 2 | 2 | 1 | 3 | 182 | 2 |
| Total | 555 | 539 | 31 | 20 | 5 | 20 | 705 | 44 |

Work-presence counts describe the recorded source evidence;
component counts describe the conservative normalized targets. There are 749
normalized components: 705 BJ and 44 AJ, including the two confirmed II.9.2
components. Twenty-one records have
nonblank raw Other-works data: twenty reference strings plus one residue case.
There are six normalized parenthetical components (one confirmed, five unresolved
in meaning), two open components, and zero unresolved syntax records.
These are coverage statistics, not scholarly
conclusions.

All 704 closed BJ components have valid books, starts, ends, and coherent ranges.
Every section within each range resolves in Niese Greek, Cardwell Latin, and
Whiston English: 2,112 component/source checks pass, with zero failures. The one
open BJ starting coordinate also passes. Across all seven books, each source has
all 4,001 Niese anchors without gaps or duplicate anchors. Latin identity uses
confirmed paragraph-start [N] apparatus plus milestones; English uses its own
milestones. It is not inferred merely from cross-source `sameAs` links. This is
coordinate-presence validation, not a claim of complete excerpt-slicing or
verbal-equivalence QA for every candidate.

AJ parsing is separate from current site availability. The actual renderer
enables Niese navigation only for Books I–IV. The validator checks its current
configuration and canonical Latin/Greek anchors rather than inventing IDs or
links. Among the 44 AJ components, only AJ III.184 (DEH V.9.3) is currently
addressable. English at that location supplies context rather than exact Niese
segmentation. The other 43 components remain future targets; one is open-ended.

| AJ book referenced | Normalized components | Currently addressable closed components | Open components |
| --- | ---: | ---: | ---: |
| III | 1 | 1 | 0 |
| IX | 2 | 0 | 0 |
| XIV | 3 | 0 | 0 |
| XV | 16 | 0 | 1 |
| XVI | 1 | 0 | 0 |
| XVII | 1 | 0 | 0 |
| XVIII | 12 | 0 | 0 |
| XX | 8 | 0 | 0 |

The machine audit includes all twenty AJ books, including zero-reference books,
and per-book parsing/availability/open/unresolved counts. No unsupported AJ
textual ID, site link, or unverified section maximum is fabricated.

`_docs/deh-concordance-exceptions.md` lists only records needing review:
40 category entries across 38 unique DEH units. Categories are five unresolved
parenthetical-meaning cases, two open
references, two source annotations, thirty AJ availability records (43 target
components), and one Other-works residue. Some units occur in several categories.
Each entry gives the canonical citation/ID, original raw reference, attempted
interpretation where available, and precise review reason. BJ canonical failures
and pilot discrepancies are both zero. Print verification and exact provenance
detail remain general editorial limitations, not hundreds of repeated exceptions.

Reproduction uses the existing Node runtime and PowerShell 7 (`pwsh.exe` on PATH),
with only Node's standard library and .NET XML/ZIP APIs. No package was installed
and no persistent execution policy or environment setting was changed. The PowerShell helper
parses real XML with external resolution disabled; it is not a regex text scraper.

```powershell
node bin/deh-concordance.mjs import 'C:\path\to\DEH_Parallels_v0_2_2026-10-02.zip'
node bin/deh-concordance.mjs validate
node bin/deh-concordance.mjs validate --self-test
```

Import regenerates only the candidate, two retained evidence files, and two audit
reports after all identity, count, source, and pilot checks pass. Validation is
read-only and detects stale reports. It reparses the retained source strings and
checks the confirmed changes, complete canonical coverage, preserved substrings
and order, parenthetical/open/blank status, BJ ranges, AJ availability, and pilot
semantics. It also compares all 100 XML hashes with the import snapshot.

QA passed: 555/555 unique numbered identities; book counts 212/73/70/79/121;
zero duplicates or omissions; no Prologue candidates; preserved source evidence;
704/704 closed BJ components in all three sources; both open starts retained;
eleven matching pilot records. Fourteen negative checks rejected missing records,
duplicate IDs, reordered components, lost BJ/AJ interleaving, lost parentheses,
removed overlap, invented endpoints, reverted corrections, lost raw evidence,
stronger blank-record claims, lost confirmed supplementary roles or decision
provenance, reordered II.9.2 targets, and absent BJ endpoints.
Repeated import produced byte-identical generated files.

A build with only `jekyll-responsive-image` omitted passed. The known configured
build limitation remains missing `rmagick >= 2.0, < 5.0`, required by
`jekyll-responsive-image` 1.6.0; no claim is made that the fully configured build
passed. Existing Sass/pagination/Faraday warnings remain. Browser checks on the
rebuilt site confirmed exactly eleven selector entries, I.1.4's supplied order,
and no comparison links for candidate-only I.23.2 or II.11.3. AJ III.184 opened
with Latin/Greek excerpts and the existing English context notice. There were no
browser error/warning logs.

All 100 canonical XML files and all eight Phase-2 pilot files remained
byte-identical. All fourteen pre-existing unrelated branding/preview files were
excluded from this task's writes and staging. During the audit, concurrent work
changed `_sass/_branding.scss`, created the separate commit
`de9d196721a326590f2acb77eb42a6438c9e6c42` (Add Bamberg manuscript identity),
and removed the three temporary Bamberg preview files. This task preserved the
resulting state; it did not edit, stage, commit, or remove those paths. The ten
other surviving unrelated files matched their initial hashes. The Phase-3
commit is made after that independent branding commit, whose diff contains no
concordance or canonical XML changes.
Only these nine Phase-3 files belong to the local commit:

- `assets/data/deh-josephus-concordance-candidate.json`
- `bin/deh-concordance.mjs`
- `bin/deh-concordance-xml.ps1`
- `_docs/deh-concordance-source/workbook-values.json`
- `_docs/deh-concordance-source/editorial-decisions.json`
- `_docs/deh-concordance-editorial-decisions.json`
- `_docs/deh-concordance-validation.json`
- `_docs/deh-concordance-exceptions.md`
- `_docs/deh-concordance-phase3.md`

The commit subject is `Import and audit full DEH-Josephus concordance`. No push,
recovery-repository work, full publication, or new UI phase is included.
