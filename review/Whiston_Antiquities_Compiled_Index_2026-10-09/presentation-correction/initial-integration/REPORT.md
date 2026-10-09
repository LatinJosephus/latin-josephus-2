# Whiston’s Antiquities chapter headings: compiled-index implementation

9 October 2026. **GO for human browser review.** All twenty books and 256 approved 1856 chapter headings are implemented through the unchanged source-specific contents reader. The registry has 59 records: all 39 earlier records and exactly 20 new Whiston records. No JavaScript, CSS, narrative XML, structural registry, existing ID, sameAs, source numeral or segmentation changed. No empty anchors were required.

Worktree: `C:\workspace\LatinJosephus-Whiston-Index-Integration-20261009`. Branch: `codex/whiston-antiquities-compiled-index`. Base HEAD: `a48021588e0840330388a6055a97bd0f7c2cf827`. Canonical v2-development HEAD and origin remain identical to the base, clean. No later integrated commit was found. Changes remain unstaged and uncommitted; no merge, rebase, push or Git configuration change occurred.

The human editor expressly approved William Whiston’s translation, *The Works of Flavius Josephus*, Auburn and Rochester: Alden & Beardsley, 1856, as the governing witness and **Whiston’s chapter headings (compiled index)** as the site designation. The per-book arrangement is editorial. The companion and visible registry note make that distinction explicit. No claim is made about the first edition’s advertised Contents or exact 1737 wording.

| Book | Headings | Exact source/TEI match | Both-theme reader |
|---|---:|---|---|
| 1 | 22 | PASS | PASS |
| 2 | 16 | PASS | PASS |
| 3 | 15 | PASS | PASS |
| 4 | 8 | PASS | PASS |
| 5 | 11 | PASS | PASS |
| 6 | 14 | PASS | PASS |
| 7 | 15 | PASS | PASS |
| 8 | 15 | PASS | PASS |
| 9 | 14 | PASS | PASS |
| 10 | 11 | PASS | PASS |
| 11 | 8 | PASS | PASS |
| 12 | 11 | PASS | PASS |
| 13 | 16 | PASS | PASS |
| 14 | 16 | PASS | PASS |
| 15 | 11 | PASS | PASS |
| 16 | 11 | PASS | PASS |
| 17 | 13 | PASS | PASS |
| 18 | 9 | PASS | PASS |
| 19 | 9 | PASS | PASS |
| 20 | 11 | PASS | PASS |
| **Total** | **256** | **PASS** | **40 complete displays** |

The original 343-file audit retains manifest SHA-256 `6c74c1e98987483b4193a34f457f2671429ef93e5050b1e114ddd83a86b7aa08`; all 342 manifest entries verify. The 107-file Book III supplement retains manifest SHA-256 `356f8dbaece44e1c686a98f6e4c5b59dbc2c4818341e4aa9fd4986f350175591`; all 106 entries verify. Each manifest excludes itself. Their recorded 78/78 and 37/37 QA checks pass; relevant manifest, inventory, derived-text and schema checks were reproduced without running historical scripts that would rewrite their packets. Both packets remained unchanged after implementation. Curated byte-identical text/provenance mirrors plus complete original manifests are retained under authority/; original immutable scans remain in the fully hash-verified external locations. See ARCHIVAL_PROVENANCE.json and SOURCE_AUTHORITY.md.

Nineteen companions use the original approved TEI proposals; Book III uses the final derived companion. Only explicitly documented proposal/approval/publication-status prose was updated. All historical heading text, labels, order, book titles, interval material, pointers, and source metadata remain intact. IMPLEMENTATION_MANIFEST.json records each replacement and source/output hash; validate.py reverses the documented metadata changes and proves exact derivation. SOURCE_ENTRY_CONCORDANCE.json gives all 256 literal headings, source labels and image/page locators.

III.8 reads **OF THE PRIESTHOOD OF AARON**, without a terminal full stop. III.15 retains the complete certified clause, six specified commas and final point. V.3 reads **WHO RULED OVER THEM FORTY YEARS.** The historical canonical Book V contents-like list remains byte-identical and unregistered; it is not used as the new index authority. The absence of explicit narrative chapter headings in canonical English IX–XX does not obstruct these independent companions: all twelve indexes load and render their accepted headings.

Data QA executed **201 successful checks**: both packet manifests/inventories, archival equality, all twenty companions and registry against TEI All Relax NG, exact heading/label/ID sequence, truthful edition metadata, no speculative narrative links, and the exact twenty-record insertion with every original registry byte recoverable. All 256 heading readings are securely source established, with documented edition/digital variants preserved in the archival collation. No unresolved heading-reading decision remains.

The separate Jekyll build passed. Actual built-site Chrome tests passed all twenty indexes in light/dark themes, complete heading and label counts, first/last headings, exact rendered source body, Coelacanth loading and computed font families, natural wrapping/no overflow, visible editorial provenance, non-clickable entries and no duplicate DOM IDs. Text contrast is 13.96:1 light and 11.85:1 dark. All 39 existing source contents records match their expected texts and supplements exactly. Twenty copied-URL/reload/pane/Chapter↔contents/Back-Forward checks, nineteen Book changes and keyboard selection pass. `?book=N&view=contents` semantics are unchanged; unrelated parameters/fragments survive and conflicting navigation parameters are cleared. There were no browser page errors or failed requests. Representative BEFORE/AFTER screenshots are retained; baseline capture explicitly asserts English’s pre-integration unavailable state.

Regression results:

- Traditional: 257 Chapters, 1,432 Subchapters, 1,689 level rows, 1,441 physical positions; all 5,034 executable language ranges and 33 expected Book IX unavailable states PASS.
- Antiquities Niese I–VII: all 2,456 selections / 7,368 language comparisons unchanged. Source contents availability does not enable public Niese navigation in VIII–X.
- Bamberg: all 198 identities / 594 language displays; compact URLs, six same-Niese/different-position pairs / 18 language checks, duplicate/absent/uncertain labels and VI–XI negative evidence PASS.
- Alignment: 1,441 units / 4,323 language comparisons; witness-order Book and Alignment views unchanged. Book VI explicit Greek spans remain correct.
- Follow-up: all 257 chapter availability transitions, nine zero-Subchapter chapters, 227 prefix-clipping checks, VI.xii.8/XIII in three languages and the unchanged Book XI shared notice PASS.
- Book XI: 18 traditional multi-span language ranges and two generic internal citation checks PASS, including no duplicate membership, retained interpolation, canonical assembly and witness-order Book/Alignment views.
- DEH, Bellum and Contra Apionem: fourteen menu-defined work/book configurations PASS; all base chapter/alignment ranges match. Bellum Whiston/Lodge complete source differential suites pass fourteen source/book configurations, preserving 3,722 currently selectable Niese coordinates per source (7,444 source-coordinate selections). This is a reader-selection count, not a redefinition of the accepted 4,001-section Lodge source segmentation, whose XML is byte-identical. Lodge notes/source switching and Greek range repair remain unchanged. Five protected interaction configurations in two themes PASS.

All **595 canonical tracked files**, the canonical index, HEAD, branch, origin and clean status are preserved. All **594 protected pre-existing worktree files**, including **122 XML files**, prior certifications, every narrative language layer, structure.xml, renderer and styles retain their initial checkout hashes. Worktree and canonical indices remain byte-identical to the recorded baseline. Initial isolated Git checkout differs from canonical in line endings for 109 tracked files; comparison proves these are only pre-existing CRLF/LF checkout serialization differences. Neither checkout was normalized.

Canonical original and final inventory SHA-256 are both `7336de6f97e205b5eb10d69b4ec773362c9552b711c2f6c8609186a58dfdd3e2`. Protected worktree original and final inventory SHA-256 are both `5ce6cdfcaa08d9ff7f5b58b6fc324db46220615a845b8f6cafb8a7d6bdf26dd4`. Inventory digests hash sorted path-to-SHA mappings as compact UTF-8 JSON. Per-file before/after hashes are in INTEGRITY_QA.json. Registry before: `3baa8ef1b2e9137b9fbabf3de22d42aca8c3818d4b66d6efe3e239bac9b12092`; after: `a2e0907dba627e69685b8dc41e89b082bb176b626c37bfdf8429feb0656e1272`.

Only the following 21 production source paths changed. All other new files are inside this new certification directory:

| Path | Before SHA-256 | After SHA-256 |
|---|---|---|
| `assets/xml/antiquities/paratext/whiston/book-01-contents.xml` | `new` | `c707b9b533780333b7626b573887b58a3b07654b4706093dbbedba29e0cd7635` |
| `assets/xml/antiquities/paratext/whiston/book-02-contents.xml` | `new` | `65b5436a7780a455c96f7cd4665718c565fe249e24a203ffa8b6a0df83d7ef39` |
| `assets/xml/antiquities/paratext/whiston/book-03-contents.xml` | `new` | `58afab897ae09764f93fee1c3bac9dc69018618998c60a9b02ca923537cbb64d` |
| `assets/xml/antiquities/paratext/whiston/book-04-contents.xml` | `new` | `b59d6da17675f9b9d06f7febb131397394bda6e6c7285ac66a05c37eda545c85` |
| `assets/xml/antiquities/paratext/whiston/book-05-contents.xml` | `new` | `125709b86437d7b23ac28a61859acd083afeb6e71f4b6a01483abac16e8c0b20` |
| `assets/xml/antiquities/paratext/whiston/book-06-contents.xml` | `new` | `5091c878331b4909113fa70d4aa7a45ac608f00e7e6620301877657e8f0ec063` |
| `assets/xml/antiquities/paratext/whiston/book-07-contents.xml` | `new` | `8f2f748b6bf1575985447dd7b8eddbfe5db9ba0acc3c5ae70ef204103f4d0e99` |
| `assets/xml/antiquities/paratext/whiston/book-08-contents.xml` | `new` | `5ce4e38433205f10656111c777593a88c40cb003f69a6fe2da156a48ba28dde4` |
| `assets/xml/antiquities/paratext/whiston/book-09-contents.xml` | `new` | `a35722cd3645f36fabdb21f0c53f77c294f7699122534010747caa1b62792691` |
| `assets/xml/antiquities/paratext/whiston/book-10-contents.xml` | `new` | `b3dff9d8d012ed5e3b9a528222319c402a39710998816c3fb67e1ddc189b8dbc` |
| `assets/xml/antiquities/paratext/whiston/book-11-contents.xml` | `new` | `d0b5d92c83b5514351e0e07c0d53cad0b73e655cce7316a7583112203a112194` |
| `assets/xml/antiquities/paratext/whiston/book-12-contents.xml` | `new` | `ce99555835b744c535b5f39da65c3cf33bb07892b0f553d1fc917625b096441d` |
| `assets/xml/antiquities/paratext/whiston/book-13-contents.xml` | `new` | `a362e4b9be465615aad98f6b2b68188ca7551f0ccc9a58ea87e0ee2097ae094f` |
| `assets/xml/antiquities/paratext/whiston/book-14-contents.xml` | `new` | `f0065d7b90cccefa5a3199003d7dc1836e8268b01cbc747698d80a1c431ec74b` |
| `assets/xml/antiquities/paratext/whiston/book-15-contents.xml` | `new` | `3c1b2f0e717d9bbb62d0961381c35717b1d22face00db12d8471342a55550b99` |
| `assets/xml/antiquities/paratext/whiston/book-16-contents.xml` | `new` | `6348cefdffa207de3f43f6ca7132dc071983c2fcaa3435ed0fd7662c74eb4025` |
| `assets/xml/antiquities/paratext/whiston/book-17-contents.xml` | `new` | `ccad5b2f8722a747cb1a1f859d8b8c06307ccadcdc5fa61fc77947d49720c7c3` |
| `assets/xml/antiquities/paratext/whiston/book-18-contents.xml` | `new` | `a7ff174ff0c0bd82688726f6de291205dac8757bbdda8a2f3757001ee81df2bc` |
| `assets/xml/antiquities/paratext/whiston/book-19-contents.xml` | `new` | `dc989f2b1f97f63879b9f3673602296b7d0ad3a78f2ff8274736ea745cb88d7e` |
| `assets/xml/antiquities/paratext/whiston/book-20-contents.xml` | `new` | `c2128bbdd1a83105546962f092da7593b5df1ac0ad39be28d533b0b437043095` |
| `assets/xml/source-contents.xml` | `3baa8ef1b2e9137b9fbabf3de22d42aca8c3818d4b66d6efe3e239bac9b12092` | `a2e0907dba627e69685b8dc41e89b082bb176b626c37bfdf8429feb0656e1272` |

Reproduction: run validate.py and integrity.py using Python/lxml; build_disposable.rb with Jekyll into the recorded temporary destination; built-site.test.cjs using Node/Playwright for full contents/browser QA. Run regression.test.cjs normally and with --alignment-all-gate, --followup-gate, --multispan-gate and --protected-source-gate; run bamberg-regression.test.cjs and interaction-regression.test.cjs. certify.py collects successfully executed outputs and refreshes this review’s manifest. Reproduction writes only this certification directory and disposable build. Historical research/certification scripts are never run in place.

Build qualification: review material was excluded and disk caching disabled. The unrelated responsive-image plugin alone was omitted from temporary build options because local rmagick is unavailable; production configuration was not changed. In-memory test hooks expose renderer state without altering deployed JavaScript. Initial test-only selector and baseline interception mistakes were corrected and the full browser suite rerun; their diagnostics are preserved in HARNESS_ADJUSTMENTS.md. Final certified results and screenshots are from the corrected run.

An unrelated pre-existing dark-mode title/header contrast problem appears in both verified BEFORE and AFTER screenshots. The contents panes pass contrast checks. It remains untouched under the data-only scope. No outstanding editorial decision blocks these twenty indexes; 1737 contents bibliography and old canonical Book V list provenance remain independent historical questions, not current transcription holds.
