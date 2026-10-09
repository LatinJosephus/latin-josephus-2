# Book XIV: provisional implementation checkpoint

Pinned baseline: `ad3158b7a86dea6997510b3de17f2e510c23367c`. Branch: `antiquities-niese-14-15`. This book is **not ready for integration**.

Expected identities: **491**, established from the complete Greek XML census and independently inspected printed opening and terminal section. Interior print verification and Latin correspondence remain explicitly separate. Visually verified Greek rows: 183; individually reviewed Latin candidates: 183; represented starts: 182 (36 retained, 146 added milestones). Verified whole-section unavailabilities in this transcription: []. Unreviewed Latin candidates: 308.

Pending editorial decisions: 162. Full narrative partition and final Latin extent remain provisional. The final adopted starts and any unresolved predecessor intervals must not be treated as complete extents.

The only Greek citation edit is addition of the independently verified implicit opening 1 using the accepted num mechanism, after the preserved chronological contents prefix. No Greek word or existing citation marker has been moved or corrected. Latin changes insert milestones at validated original raw-byte positions. Every added milestone reverses to the same frozen UTF-8/LF input bytes; narrative wording, punctuation, spelling, whitespace, IDs, sameAs, paragraphs, traditional divisions and apparatus remain unchanged. English files remain byte-identical.

Local reader QA passed **160 adjoining intervals** on the earlier checkpoint saved under [reader-tested-checkpoint3](reader-tested-checkpoint3), with actual build hashes and corpus bytes. It checked actual selection text in all languages, IDs, chapter/subchapter coverage, deep links, reload/history, previous/next, panes and light/dark themes. Later starts recorded in this current corpus require a fresh build and reader QA. The isolated test registry enables only its reviewed checkpoint range; production availability stays disabled. See [PARTIAL_READER_QA.json](PARTIAL_READER_QA.json).

Shared protected checks passed the accepted VIII/X identity censuses, critical boundary cases, protected contents/traditional/Bamberg/Alignment routes, Whiston, Bellum/Lodge and other affected works. The shared support change only permits milestones inside anonymous paragraphs. The exact inherited Book-I apparatus targets and unsupported I.1 baseline error remain narrowly documented; no additional error was excused.

The published baseline remains **3,157 selectable identities**. Added published or production-enabled coverage is **0**; this local scholarly checkpoint does not imply new published coverage.

Review data: [BOUNDARIES.json](BOUNDARIES.json), [human review register](BOUNDARIES_REVIEW.tsv), [checkpoint certificate](CHECKPOINT_CERTIFICATE.json), [executable identity plan](EXECUTABLE_IDENTITIES.json), [source authority](SOURCE_AUTHORITY.md), [decision history](DECISION_HISTORY.json), [Latin preservation](LATIN_PARTIAL_IMPLEMENTATION.json), [file manifest](FILE_MANIFEST.json).

No canonical merge, branch push, preview update or deployment has occurred. Remaining work is the unreviewed printed/Latin candidates, pending decisions, full executable identity registry, final partition/extent checks and fresh full-book browser certification.
