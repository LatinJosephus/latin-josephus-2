# Antiquities VIII: completed local implementation and certification

**GO for review of the locally committed implementation. Canonical integration, push and public deployment remain unauthorized.** This certificate supersedes historical NO-GO status only for the accepted segmentation scope. The original audit reports and decision history are preserved unchanged from `fb8a65e2a6c7d6e5426f3b4751d30e67528b1a28`; their historical statements are not current implementation status.

Implementation base: `a48021588e0840330388a6055a97bd0f7c2cf827` on the fresh `antiquities-niese-08-10-implementation` branch. Production inputs came from the current canonical commit, including its Greek source-contents integration; no old production file was copied from the audit branch. Actual target bytes are UTF-8 without BOM, LF. They equal the frozen audit Git blobs. Canonical-checkout CRLF hashes remain separately recorded in BASELINE.json. Locators were regenerated against target mixed text nodes and checked against accepted narrative coordinates, paragraph IDs, node paths and context.

Inventory: **420 Greek sections = 83 retained Latin starts + 337 new milestones**. Represented Latin intervals: **420**. Confidence classifications: `{"EXACT": 83, "INTERNAL-BUT-EXACT": 337}`. Routine checks outstanding: **0**; editorial decisions outstanding: **0**. Confidence in a physical locator is distinct from a qualified translation correspondence.

Explicit 1 added; 59, 110, 245, 353, 368 and 409 relocated. 172 retained at καταδεεστέραν; 256, 314 and 376–377 retain the accepted source assessments. The printed 376/377 numeral anomaly is not reproduced.

VIII.367 begins at et quae displucuerint sola relinquerent and retains the surviving tail; the main embassy narrative has no identifiable counterpart and its absence has no established cause. 368 begins at the elected Ahab response. 369 begins at the first nunc inquit denuo missa legatione; both repetitions and the later recap survive unchanged. VIII.110, 172 and 368 remain editorial word choices informed by marginal print position and independent Loeb control, not unambiguous Niese word tags. The syntax/compression qualifications at 83, 87, 97, 167 and 334 remain in the frozen operative register.

The two inherited-label exceptions are in assets/xml/antiquities/niese/book-08.json and IMPLEMENTATION_QA.json. Their visible labels remain unchanged. Only executable identity recognition is suppressed, and the approved internal milestones supply the correct starts. Paragraphs, IDs, sameAs, spelling, punctuation, whitespace, apparatus and traditional/Bamberg divisions are preserved. No gap or supplied text was added.

Preservation: removing only the 337 authorized Latin milestones recovers the target input bytes exactly. Reversing the authorized Greek marker edits also recovers the corresponding input exactly. IMPLEMENTED_EXTENTS.json independently reconstructs complete narrative partitions, including narrative whitespace: no overlapping, missing or empty represented interval. Expected marker edits are separate from unchanged narrative.

Actual built-site browser certification: all **420** selector events and exact Greek/Latin intervals pass, with unique executable starts and rendered IDs. English remains explicitly broader aligned context. The shared NEW_BOOK_BROWSER_QA.json and UI_SUPPLEMENT_QA.json record deep links, reload, rendered previous/next and Back/Forward transitions, pane switching and both themes. All exceptions and partial correspondences also pass with the uninstrumented production reader. IX remains disabled and switching back restores VIII/X. X.108 keeps independently available Greek and English while displaying a Latin absence notice.

Protected regressions passed against the actual canonical build and the established range suites: 257 Chapters, 1,432 Subchapters, 5,034 executable traditional displays, 33 unavailable states, 198 Bamberg identities/594 displays, 1,441 Alignment units, all 2,456 prior Antiquities Niese selections, XI multi-span, VI.xii.8/XIII and the nine chapters lacking a printed lower 1. Current source contents/TOCs, Whiston, all 4,001 Bellum citation anchors in both Whiston and Lodge, Lodge note toggle, DEH and Contra Apionem are preserved. New-book browser results are additional to historical audit rehearsals.

| Target source | Before SHA-256 | After SHA-256 |
| --- | --- | --- |
| Greek | `010a566202b9f18d6a35528720986a89a1ceb9dd7417866696cd1e74ef85b098` | `3ae0e04f7ccb24c05bdcb166f40a143098c4f5c73be74e1edc2985b1a09cbb9e` |
| Latin | `7a94c61dc00d61c683953451c575e8166be03699510f1c7d563c2c5b74edfe5f` | `35fe3a3f9f776fddbaf69932cf509f54e9aaa3da663305716496825e6b61fc77` |

Per-book data and review records form a separate implementation commit, depending on the shared generic reader commit. The per-book availability declaration is the only shared-code change needed in that commit. Full reproducibility and shared dependency details are in ../Antiquities_Niese_Implementation_08_10_2026-10-09/REPORT.md. No unresolved issue remains within the authorized scope.
