"""Produce current certificates and exact staging manifests from passing QA.
Earlier audit records are copied unchanged; implementation records are additional.
"""
import pathlib,json,hashlib,shutil,subprocess
P=pathlib.Path(__file__).resolve().parent;W=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def md(p,s):p.write_text(s.strip()+'\n',encoding='utf8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=read(P/'CERTIFICATION.json');assert c['result']=='PASS'
base=c['base'];audit=c['audit_checkpoint']
review_roots=[W/f'review/Antiquities_Niese_Book{r}_2026-10-08' for r in ['VIII','X']]+[W/'review/Antiquities_Niese_Batch_08_10_2026-10-08',P]
production=['_includes/display-settings.html','assets/js/renderTei.js']+[f'assets/xml/antiquities/{l}/book-{b:02}.xml' for b in [8,10] for l in ['Greek','Latin']]+[f'assets/xml/antiquities/niese/book-{b:02}.json' for b in [8,10]]
# The frozen audit history is preserved byte-for-byte in this checkout.
frozen=[]
for rel in subprocess.check_output(['git','--no-optional-locks','ls-tree','-r','--name-only',audit],cwd=W).decode().splitlines():
 if not any(rel.startswith(str(r.relative_to(W)).replace('\\','/')+'/') for r in review_roots[:3]):continue
 old=subprocess.check_output(['git','--no-optional-locks','show',audit+':'+rel],cwd=W)
 copied=(W/rel).read_bytes();source=(pathlib.Path('C:/workspace/LatinJosephus-antiquities-niese-08-10')/rel).read_bytes()
 assert copied==source and (copied==old or copied.replace(b'\r\n',b'\n')==old),rel
 frozen.append({'path':rel,'copied_working_bytes_sha256':sha(W/rel),'audit_Git_blob_sha256':hashlib.sha256(old).hexdigest()})
write(P/'AUDIT_RECORDS_PRESERVED.json',{'review_checkpoint':audit,'files':frozen,'all_byte_exact':True})
build=pathlib.Path('C:/workspace/Antiquities-Niese-Implementation-08-10-2026-10-09/build')
for name in ['jekyll.log','baseline-jekyll.log','dependencies.log']:shutil.copyfile(build/name,P/name)
diag=P/'diagnostics';diag.mkdir(exist_ok=True)
for name in ['FAILED_BROWSER_QA.json','FAIL_cross_deh_1.json']:
 if (P/name).exists():(P/name).replace(diag/name)
md(diag/'RESOLVED.md','''# Resolved certification findings

The initial X identity check detected TEI-header folio numbers being interpreted as citation starts. The generic Antiquities collector now requires a narrative-body paragraph and excludes notes/apparatus. The site was rebuilt and all 701 new selector/rendering checks passed afterwards.

The first cross-work DEH comparison differed solely in the two disposable servers' ports within local deep-link URLs. The comparator removes each server's origin while retaining the complete link path, query and DOM. All DEH comparisons subsequently passed. These initial diagnostics are history; final QA files at the packet root are authoritative.

The Bellum source suite now takes its citation census from the complete whole-book source before exercising chapter menus. The earlier inherited harness inspected a menu prepared in chapter state and counted only 3,722 starts. The final suite covers all 4,001 citations in both Whiston and Lodge. This is a test-accounting correction, not a production change.''')
for b,roman in [(8,'VIII'),(10,'X')]:
 d=review_roots[0 if b==8 else 1];q=c['books'][str(b)];p=read(d/'IMPLEMENTATION_PRESERVATION.json');browser=read(d/'IMPLEMENTATION_BROWSER_QA.json')
 files=[s for s in c['preservation'] if s['book']==b]
 table='\n'.join(f'| {s["language"]} | `{s["target_before_sha256"]}` | `{s["target_after_sha256"]}` |' for s in files)
 greek= 'Explicit 1 added; 59, 110, 245, 353, 368 and 409 relocated. 172 retained at καταδεεστέραν; 256, 314 and 376–377 retain the accepted source assessments. The printed 376/377 numeral anomaly is not reproduced.' if b==8 else 'Explicit 1 added; 33 relocated to ὁ δὲ προφήτης ὑποτυχών.'
 qualifications='''VIII.367 begins at et quae displucuerint sola relinquerent and retains the surviving tail; the main embassy narrative has no identifiable counterpart and its absence has no established cause. 368 begins at the elected Ahab response. 369 begins at the first nunc inquit denuo missa legatione; both repetitions and the later recap survive unchanged. VIII.110, 172 and 368 remain editorial word choices informed by marginal print position and independent Loeb control, not unambiguous Niese word tags. The syntax/compression qualifications at 83, 87, 97, 167 and 334 remain in the frozen operative register.''' if b==8 else '''X.102 begins at nomine sedechiam, the first identifiable surviving counterpart; simulet ioachim remains with 101. Unexpressed opening details are qualified, without reconstruction. 108 is unavailable: its eight-year Babylonian alliance, repudiation of pledges and turn towards Egypt in hope of overcoming Babylonian power lack an identifiable Latin counterpart. Cause undetermined; later Egyptian narrative survives. 276 remains available at Et haec, with quae omnia at 277: the concluding Greek Roman-rule/devastation notice has no identifiable counterpart, cause undetermined. X.18 is entirely within latin-book10-num15; its pb/cb markers are page/column changes, not a paragraph crossing. The interval after Turbatur includes the ritual/restoration material. Preserve Cui etiam rea with 212, both nepus and nepos at 248, and both recorded discrepancies at 107.'''
 md(d/'IMPLEMENTATION_REPORT.md',f'''# Antiquities {roman}: completed local implementation and certification

**GO for review of the locally committed implementation. Canonical integration, push and public deployment remain unauthorized.** This certificate supersedes historical NO-GO status only for the accepted segmentation scope. The original audit reports and decision history are preserved unchanged from `{audit}`; their historical statements are not current implementation status.

Implementation base: `{base}` on the fresh `antiquities-niese-08-10-implementation` branch. Production inputs came from the current canonical commit, including its Greek source-contents integration; no old production file was copied from the audit branch. Actual target bytes are UTF-8 without BOM, LF. They equal the frozen audit Git blobs. Canonical-checkout CRLF hashes remain separately recorded in BASELINE.json. Locators were regenerated against target mixed text nodes and checked against accepted narrative coordinates, paragraph IDs, node paths and context.

Inventory: **{q['expected_sections']} Greek sections = {q['retained_inherited_starts']} retained Latin starts + {q['new_Latin_milestones']} new milestones{(' + unavailable 108' if b==10 else '')}**. Represented Latin intervals: **{q['represented_Latin_intervals']}**. Confidence classifications: `{json.dumps(q['confidence_counts'])}`. Routine checks outstanding: **0**; editorial decisions outstanding: **0**. Confidence in a physical locator is distinct from a qualified translation correspondence.

{greek}

{qualifications}

The two inherited-label exceptions are in assets/xml/antiquities/niese/book-{b:02}.json and IMPLEMENTATION_QA.json. Their visible labels remain unchanged. Only executable identity recognition is suppressed, and the approved internal milestones supply the correct starts. Paragraphs, IDs, sameAs, spelling, punctuation, whitespace, apparatus and traditional/Bamberg divisions are preserved. No gap or supplied text was added.

Preservation: removing only the {q['new_Latin_milestones']} authorized Latin milestones recovers the target input bytes exactly. Reversing the authorized Greek marker edits also recovers the corresponding input exactly. IMPLEMENTED_EXTENTS.json independently reconstructs complete narrative partitions, including narrative whitespace: no overlapping, missing or empty represented interval. Expected marker edits are separate from unchanged narrative.

Actual built-site browser certification: all **{browser['all_actual_selector_events_and_rendered_intervals']}** selector events and exact Greek/Latin intervals pass, with unique executable starts and rendered IDs. English remains explicitly broader aligned context. The shared NEW_BOOK_BROWSER_QA.json and UI_SUPPLEMENT_QA.json record deep links, reload, rendered previous/next and Back/Forward transitions, pane switching and both themes. All exceptions and partial correspondences also pass with the uninstrumented production reader. IX remains disabled and switching back restores VIII/X. X.108 keeps independently available Greek and English while displaying a Latin absence notice.

Protected regressions passed against the actual canonical build and the established range suites: 257 Chapters, 1,432 Subchapters, 5,034 executable traditional displays, 33 unavailable states, 198 Bamberg identities/594 displays, 1,441 Alignment units, all 2,456 prior Antiquities Niese selections, XI multi-span, VI.xii.8/XIII and the nine chapters lacking a printed lower 1. Current source contents/TOCs, Whiston, all 4,001 Bellum citation anchors in both Whiston and Lodge, Lodge note toggle, DEH and Contra Apionem are preserved. New-book browser results are additional to historical audit rehearsals.

| Target source | Before SHA-256 | After SHA-256 |
| --- | --- | --- |
{table}

Per-book data and review records form a separate implementation commit, depending on the shared generic reader commit. The per-book availability declaration is the only shared-code change needed in that commit. Full reproducibility and shared dependency details are in ../Antiquities_Niese_Implementation_08_10_2026-10-09/REPORT.md. No unresolved issue remains within the authorized scope.''')
 md(d/'IMPLEMENTATION_SOURCE_AUTHORITY.md',f'''# {roman}: authority in the implemented state

The source/provenance record in SOURCE_AUTHORITY.md is retained byte-exactly as historical audit evidence. Current adjudication authority is the operative BOUNDARIES.json and final user approvals frozen at `{audit}`. This additional document records implementation; it does not retrospectively rewrite source observations.

Niese, Flavii Iosephi Opera II (Berlin: Weidmann, 1885), {('pp.177–266; PDF185–274' if b==8 else 'pp.330–392; PDF338–400')}, controls numbering. All {q['expected_sections']} starts received print collation in the accepted audit. Loeb {('V' if b==8 else 'VI')} is independent Greek/English context, not authority for manufacturing Niese divisions from chapters. Printed marginal position, Loeb comparison and editorial word choice remain separately documented in PRINT_OBSERVATIONS.json, ADJUDICATED_GREEK_PROPOSALS.json and BOUNDARIES.json. In particular VIII.110, 172 and 368 are not asserted to be unambiguously word-tagged by Niese.

The printed opening establishes section 1 in each book. Adding its explicit label represents the existing first citation, not an extra section. The canonical Latin is the sole textual base. No supplementation, text emendation or cause of omission is inferred. Whiston is broader context.

All supplied printed PDFs, 169 saved page images and 245 frozen research files retain their hashes (shared PRINT_INPUTS_UNCHANGED.json). The prior collation has not been restarted. Current input/output hashes and reversible edits are in IMPLEMENTATION_PRESERVATION.json and the shared TARGET_BASELINE.json.''')
md(P/'READER_CHANGES.md','''# Shared generic reader dependency

renderTei.js gains a generic per-book Niese identity registry: declared availability, executable-label exceptions, unavailable language sections, broader English context targets and reader-facing correspondence notes. Metadata folio numbers and apparatus are excluded from narrative identities. Existing I–VII availability remains unchanged. New declarations are explicit keys 8 and 10; IX is absent. There are no book-specific rendering branches.

display-settings.html adds optional Antiquities Niese Previous/Next controls. Their behavior follows actual citation identities, including X.108, and disables endpoints. Chapter, Subchapter, Bamberg, Alignment and contents semantics remain unchanged.

The shared reader commit contains the generic machinery with an empty new registry declaration. The VIII commit adds only key 8; the X commit adds key 10. Each book commit includes its own data and independent certificate. Shared batch proof follows in a separate certification commit. The combined tested production reader differs from the per-book intermediate state only in those explicit availability keys.''')
scope='\n'.join('- '+x for x in production)
md(P/'REPORT.md',f'''# Antiquities VIII and X: completed isolated implementation

**Both books pass local scholarly and technical certification for the accepted scope.** No routine review or editorial decisions remain. Canonical integration, push and public deployment have not been performed or authorized. No other book was segmented.

Fresh implementation worktree: C:\\workspace\\LatinJosephus-antiquities-niese-08-10-implementation. Branch: antiquities-niese-08-10-implementation. Base: `{base}` (actual clean canonical v2-development and origin/v2-development). This includes the Greek source-contents integration and accepted TOC typography work. The audit branch remains separate, with review-only checkpoint `{audit}` and printed checkpoint `dec5f783b1af936803150536ed5aaa031b21c479` preserved.

| Book | Greek sections | Retained Latin starts | Added Latin milestones | Latin intervals | Unavailable |
| --- | ---: | ---: | ---: | ---: | --- |
| VIII | 420 | 83 | 337 | 420 | none |
| X | 281 | 50 | 230 | 280 | 108 |
| Added total | 701 | 133 | 567 | 700 | one |

Existing I–VII: 2,456 selections. Certified isolated total: **3,157 selectable Antiquities Niese sections**, comprising I–VIII and X. IX remains unavailable. This selection total is distinct from the 700 newly represented Latin intervals and X.108's addressable absence state. Qualifications at VIII.367, X.102 and X.276 remain visible; X.108 retains Greek and broader English independently. No missing text is supplied and no gap is inserted.

The audit records are brought forward byte-exactly ({len(frozen)} files; AUDIT_RECORDS_PRESERVED.json). Older NO-GO, source observations and insertion rehearsals remain historical. IMPLEMENTATION_REPORT.md in each book packet and the new shared QA files are current certification. The latest X.102 and 276 decisions, VIII.367 surviving tail, elected VIII.368 and first repetition at 369 are in the frozen operative registers. X.18 does not cross a paragraph: its manuscript pb/cb changes are inside num15. X.108's absent alliance/Egypt-turn notice is distinguished from later surviving Egyptian narrative.

All four source reversals are byte exact, with UTF-8/LF retained. Every mixed locator was re-established against actual target nodes after comparing current Git blobs with frozen inputs. All narrative, labels, IDs, sameAs, paragraphs and divisions remain intact. {c['unchanged_base_files']} other base files are unchanged, including other books, Whiston, structure.xml, source contents and TOC registry. PDFs, print images and frozen research are unchanged. CERTIFICATION.json records before/after SHA-256, identities, complete narrative partitions and built-file hashes.

Actual implementation tests (not historical baseline tests): 420 VIII and 281 X selector events; all Greek/Latin interval projections; 18 critical deep-link/history/pane/theme cases; 12 uninstrumented critical production-reader URLs; independent rendered history/endpoints; IX fallback and return; no duplicate executable starts or DOM IDs. Final new-book, regression and interaction suites record **zero browser exceptions, console errors and failed requests**. Thirty-six light/dark screenshots are retained; VIII.367 and X.108 were visually inspected, together with first/internal/final selections. The existing dark header and local missing header-logo appearance are baseline cosmetics; the new text, notices and controls remain usable. No unrelated style change was made.

Protected actual-baseline comparisons and established range checks pass: 257 traditional Chapters, 1,432 Subchapters, 5,034 executable three-language ranges, 33 unavailable states, 198 Bamberg identities/594 displays, 1,441 Alignment units, 2,456 prior Antiquities Niese selections, XI multi-span, VI.xii.8/XIII, all nine chapters lacking lower division 1, and current Latin/Greek source contents including supplied Latin XIV [V]–[XII]. Bellum's 4,001 citations are compared from complete whole-book sources in Whiston and Lodge; Greek/Latin chapter ranges, Cardwell, marginal-note toggle, DEH and Contra Apionem ranges/deep links pass. Resolved initial test findings are retained under diagnostics; final PASS results are at the packet root.

Exact production scope (eight files):

{scope}

Review scope is restricted to the two per-book packets, the accepted batch-audit packet and this new implementation packet. FILE_MANIFEST.json records every deliverable path/hash; COMMIT_SCOPE.json is the exact staged path grouping. Older certification reports were not rewritten. Per-book commits depend on the shared reader machinery; their availability entries and data are separately reviewable.

Reproduce from this worktree: use build.sh in a disposable ruby:3.3-bookworm Docker container, with the implementation and canonical sources mounted read-only and the dedicated build output mounted writable. It builds actual implementation and baseline sites separately. Then run browser-certify.cjs (new books), browser-certify.cjs --regressions, browser-certify.cjs --ui-supplement; established-regressions.test.cjs without flags and with --protected-source-gate, --followup-gate, --multispan-gate, --alignment-gate, --locator-gate, --rendered-gate; finally verify_implementation.py. Runtime paths are in the scripts. implement.py is idempotent only over pinned original/applied bytes; it is an application tool, not a general merger. Test scripts expose production functions for exhaustive comparisons; the 12 critical URL checks also load the uninstrumented production script.

Build output is C:\\workspace\\Antiquities-Niese-Implementation-08-10-2026-10-09\\build, separate from public or shared builds. The accepted inputs, exact authorized and inverse operations, build logs, QA and screenshots are retained. No unresolved issue remains within this pair's accepted segmentation scope. Subsequent work should first review these local commits and decide canonical integration; another segmentation batch was not selected.''')
# Hash manifests omit themselves and staging-scope files to avoid cycles.
def manifest(paths):return [{'path':str(p.relative_to(W)).replace('\\','/'),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(paths)]
for b,roman in [(8,'VIII'),(10,'X')]:
 d=review_roots[0 if b==8 else 1];paths=[p for p in d.rglob('*') if p.is_file() and p.name!='IMPLEMENTATION_FILE_MANIFEST.json']+[W/f'assets/xml/antiquities/{l}/book-{b:02}.xml' for l in ['Greek','Latin']]+[W/f'assets/xml/antiquities/niese/book-{b:02}.json']
 write(d/'IMPLEMENTATION_FILE_MANIFEST.json',{'scope':'PER_BOOK_IMPLEMENTATION_AND_PRESERVED_AUDIT','shared_reader_dependency':'READER_CHANGES.md','files':manifest(paths)})
all_paths=[W/x for x in production]+[p for r in review_roots for p in r.rglob('*') if p.is_file() and not(r==P and p.name in {'FILE_MANIFEST.json','COMMIT_SCOPE.json'})]
write(P/'FILE_MANIFEST.json',{'scope':'COMPLETED_LOCAL_IMPLEMENTATION','self_and_commit_scope_excluded':True,'files':manifest(all_paths)})
scope={'shared_reader':['assets/js/renderTei.js','_includes/display-settings.html',str((P/'READER_CHANGES.md').relative_to(W)).replace('\\','/')], 'VIII':['assets/js/renderTei.js']+[f'assets/xml/antiquities/{l}/book-08.xml' for l in ['Greek','Latin']]+['assets/xml/antiquities/niese/book-08.json']+[str(p.relative_to(W)).replace('\\','/') for p in sorted(review_roots[0].rglob('*')) if p.is_file()], 'X':['assets/js/renderTei.js']+[f'assets/xml/antiquities/{l}/book-10.xml' for l in ['Greek','Latin']]+['assets/xml/antiquities/niese/book-10.json']+[str(p.relative_to(W)).replace('\\','/') for p in sorted(review_roots[1].rglob('*')) if p.is_file()], 'shared_certification':[str(p.relative_to(W)).replace('\\','/') for r in review_roots[2:] for p in sorted(r.rglob('*')) if p.is_file() and p.name!='READER_CHANGES.md']}
if str((P/'COMMIT_SCOPE.json').relative_to(W)).replace('\\','/') not in scope['shared_certification']:scope['shared_certification'].append(str((P/'COMMIT_SCOPE.json').relative_to(W)).replace('\\','/'))
write(P/'COMMIT_SCOPE.json',{'base':base,'audit_checkpoint':audit,'groups':scope,'availability_staging':'shared empty registry map; VIII key 8 only; X keys 8 and 10','all_paths_explicit':True})
print(json.dumps({'manifest_files':len(all_paths),'commit_scope_counts':{k:len(v) for k,v in scope.items()},'frozen_audit_files':len(frozen)},indent=2))
