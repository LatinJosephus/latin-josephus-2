from pathlib import Path
import json,hashlib,subprocess,collections
V=Path(__file__).resolve().parent;R=V.parents[1];A=Path(r'C:\workspace\LatinJosephus-Greek-Capitula-Audit-20261008')
def read(n):return json.loads((V/n).read_text(encoding='utf-8-sig'))
def dump(n,d):(V/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,s):(V/n).write_text(s.rstrip()+'\n',encoding='utf-8')
data=read('DATA_QA.json');browser=read('BUILT_SITE_BROWSER_QA.json');reg=read('REGRESSION_BROWSER_QA.json');bam=read('BAMBERG_BROWSER_QA.json');align=read('ALIGNMENT_ALL_QA.json');follow=read('FOLLOWUP_GATE_QA.json');multi=read('XI_MULTISPAN_GATE_QA.json');interaction=read('INTERACTION_QA.json');bellum=read('PROTECTED_SOURCE_GATE_QA.json');integrity=read('INTEGRITY_QA.json');imp=read('IMPLEMENTATION_MANIFEST.json');archive=read('AUDIT_ARCHIVE_REFERENCE.json')
for q in [data,browser,bam,align,follow,interaction,bellum,integrity]:assert q['result']=='PASS'
assert not reg['errors'] and reg['traditional']['rows']==1689 and reg['traditional']['executable']==5034 and reg['traditional']['unavailable']==33
assert sum(x['selections'] for x in reg['niese'].values())==2456 and sum(x['alignment_units'] for x in align['checks'])==1441
assert browser['new_entries']==109 and browser['theme_displays']==18 and browser['existing_records']==30
assert len(bellum['checks'])==14 and all(q['result']=='PASS' for q in bellum['checks'])
assert all(sum(q['niese'] for q in bellum['checks'] if q['source']==witness)==3722 for witness in ['whiston','lodge1602'])
canon_old={r['path']:r['original_sha256'] for r in integrity['canonical_files']};canon_new={r['path']:r['final_sha256'] for r in integrity['canonical_files']}
invhash=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()
integrity['canonical_original_inventory_sha256']=invhash(canon_old);integrity['canonical_final_inventory_sha256']=invhash(canon_new);assert invhash(canon_old)==invhash(canon_new);dump('INTEGRITY_QA.json',integrity)
source=read('audit-authority/GREEK_CAPITULA_MASTER.json');inputqa=read('AUDIT_INPUT_INTEGRITY_QA.json');ns=read('SAME_NIESE_DIFFERENT_POSITION_QA.json')
summary={'result':'PASS','base':integrity['canonical_HEAD'],'data_checks':data['checks_passed'],'audit_manifest_entries':120,'audit_manifest_self_excluded':True,'audit_original_files':121,'audit_inputs_verified':inputqa['inputs_verified'],'new_companions':9,'new_entries':109,'per_book':data['per_book'],'registry_before':30,'registry_after':39,'Greek_Antiquities_books':20,'renderer_CSS_changes':0,'new_narrative_anchors':0,'browser':{'new_books':9,'themes':2,'new_theme_displays':18,'all_existing_source_records_exact':30,'per_book_URL_history_interaction_checks':9,'book_switches':19,'keyboard':'PASS','page_errors':len(browser['pageErrors']),'failed_requests':len(browser['failedRequests']),'contents_contrast_light':14.05,'contents_contrast_dark':11.85,'VIII_X_public_Niese_still_disabled':True},'traditional':reg['traditional'],'Niese_I_VII':{'selections':2456,'language_comparisons':7368,'differential_DOM':'PASS'},'Bamberg':{'identities':198,'language_displays':594,'same_Niese_different_position_pairs':6,'pair_language_checks':18,'compact_URLs':'PASS'},'Alignment_units':{'identities':1441,'language_comparisons':4323,'Book_and_witness_order':'PASS'},'followup':{'all_chapter_availability_checks':257,'zero_subchapter_chapters':9,'structural_prefix_checks':len(follow['prefixChecks']),'VI_xii8_XIII_languages':3,'XI_notice_cases':2,'URL_cases':4},'XI_multispan':{'traditional_language_ranges':len(multi['checks']),'generic_citation_checks':len(multi['citationChecks']),'interpolations_preserved':True},'Bellum_source_regression':bellum,'cross_work':reg['crossWork'],'interaction_configurations':len(interaction['checks']),'protected_preexisting_worktree_files':498,'protected_preexisting_XML_files':113,'canonical_files_identical':499,'original_certifications_unchanged':True,'audit_packet_unchanged':True,'no_staged_changes':True,'new_source_changes_only':'Nine companions and nine-record registry extension','human_review':'GO','deferred_questions':['Existing Book V [στιγμα] encoding: separate editorial hold; no alteration.'],'build_qualification':'Disposable Jekyll build excluded review archive and disabled disk cache. Only jekyll-responsive-image omitted from temporary plugin options because local rmagick dependency is unavailable. Production config untouched.','visual_qualification':'New contents panes are legible and wrap in both themes. The unchanged site chrome has a pale title surface/low-contrast title in dark screenshots; the same pre-existing chrome is visible in BEFORE captures. It is outside this data-only integration and was not altered.'}
dump('QA.json',summary);dump('BROWSER_QA.json',browser)
archive['verified_after_implementation']=120;archive['verified_original_inputs_after_implementation']=504;archive['original_manifest_sha256_after']=h(A/'FILE_MANIFEST.json');dump('AUDIT_ARCHIVE_REFERENCE.json',archive)
rows=imp['production_changes'];counts=data['per_book'];table='\n'.join(f'| {b} | {n} | PRINT_VERIFIED | PASS |' for b,n in counts.items());filetable='\n'.join(f'| `{r["path"]}` | {r.get("entries", "9 records added")} | `{r["after_sha256"]}` |' for r in rows)
put('REPORT.md',f'''# Greek Antiquities capitula: TOC v1.1 implementation certification

8 October 2026. GO for human browser review; implementation remains unstaged and uncommitted.

The nine accepted Greek source-paratext companions have been installed byte-for-byte from the approved audit. Nine VERIFIED source-contents records were appended without rewriting any original registry bytes. Greek Antiquities contents are now available for I–XX through the unchanged source-specific reader. No JavaScript, CSS, narrative XML, source numeral, alignment target, existing ID, sameAs, or structural registry changed.

Worktree: `{R}`. Branch: `codex/antiquities-greek-capitula-toc-v1.1`. Base and unchanged canonical HEAD/origin: `{integrity['canonical_HEAD']}`. Canonical branch remains v2-development, clean. No stage, commit, merge, rebase, push or Git configuration change occurred.

| Book | Entries added | Accepted source status | Implementation/schema |
|---|---:|---|---|
{table}
| **Total** | **109** | | **PASS** |

The 120 original audit manifest entries and all 504 separately recorded input hashes verify. The audit contains 121 files: its manifest deliberately excludes itself. Its manifest SHA-256 remains `4d5bf373b7d9d5c0d656a04b567b591446bafca9b24d4969ec98f73956c75d1b`. Full raw print/digital evidence remains at the unchanged external audit location, with a byte-identical core mirror and explicit archival reference here. No new source reading or transcription was made. See SOURCE_AUTHORITY.md and AUDIT_ARCHIVE_REFERENCE.json.

The nine companions and extended registry validate against the unchanged project TEI All Relax NG schema. All 109 item texts, literal labels, n values and item identities match the elected printed-Niese master exactly. File-byte equality additionally preserves every heading, rubric, trailer, accent, bracket and punctuation sequence. Printed and Perseus readings remain separately recoverable in the archived master/collation. Book I retains its paratext proem-summary rubric, without importing the actual general proem or narrative. Capitula remain non-clickable source lists with no asserted chapter/Niese equivalences.

Browser checks on the separately built Jekyll reader passed all nine books in both themes (18 complete lists), all 30 existing source records, nine per-book copied-URL/reload/history/pane/Chapter↔contents checks, all twenty Antiquities books in contents mode, and keyboard selection. `?book=N&view=contents` remains unchanged. Greek typography inherits the unchanged established reading stack. Long entries wrap; no contents overflow, duplicate contents DOM IDs, page errors or failed network requests were observed. Contents text contrast measured 14.05:1 light and 11.85:1 dark. Latin/English retain their own contents or neutral unavailable state. BEFORE/AFTER screenshots cover I, II, VII, IX and X in both themes, with additional final-entry captures for IX/X.

Regression results:

- Traditional: 257 Chapters, 1,432 Subchapters, 1,689 rows, 1,441 physical positions; 5,034 executable language ranges and all 33 expected Book IX unavailable states pass.
- Niese I–VII: 2,456 selections / 7,368 language DOM comparisons unchanged. VIII–X remain unavailable for public Niese navigation; new contents do not enable citation navigation.
- Bamberg: 198 identities / 594 language ranges, compact URLs, all six same-Niese/different-position pairs (18 language checks), duplicate/missing labels and negative evidence in VI–XI pass.
- Alignment: all 1,441 units / 4,323 language comparisons and Book witness order unchanged.
- Follow-up: all 257 chapter-availability transitions, nine zero-subchapter chapters, {len(follow['prefixChecks'])} structural-prefix clipping checks, VI.xii.8/XIII and XI shared notice pass.
- XI ordered multi-span membership, no duplication, interpolation retention and witness-order Book/Alignment views pass.
- Bellum: full seven-book Whiston and Lodge differential chapter/unit/Niese range suite passes; all 3,722 currently selectable Niese coordinates per source (7,444 source/coordinate comparisons) preserved; the 4,001 Lodge segmentation markers remain byte-identical. Lodge notes and source switching pass.
- DEH, Bellum and Contra Apionem: all menu-defined chapter/unit ranges match the base; five protected interaction configurations and both themes pass.

All 499 canonical tracked files retain their initial SHA-256 values and canonical index is unchanged. All 498 protected pre-existing worktree files, including 113 XML files and all prior certifications, retain their own checkout hashes. Git initially checked out 109 files with LF in place of canonical CRLF; only line-ending serialization differs between those initial checkouts, and neither checkout was normalized. Individual before/after hashes are in INTEGRITY_QA.json. Canonical inventory digest (sorted path-to-SHA mapping, UTF-8 compact JSON) is unchanged: `{invhash(canon_old)}`.

Only the following ten production source paths changed; all other new files belong to this certification directory:

| Path | Added population | Final SHA-256 |
|---|---:|---|
{filetable}

Registry original SHA-256: `{rows[-1]['before_sha256']}`. Registry final SHA-256: `{rows[-1]['after_sha256']}`. No source anchors were required.

Build qualification: Jekyll 4.4.1 generated a disposable site outside the repository, with disk cache disabled and research review files excluded. Its local responsive-image dependency rmagick is missing, so that unrelated plugin alone was omitted in temporary build options. Production configuration and layouts were not edited. The source-specific reader, XML, CSS, fonts and other installed plugins were used. Browser observation hooks were injected in memory only; baseline screenshots use the base registry over the otherwise identical disposable build.

The unchanged site chrome shows a pale title surface with low-contrast title text in dark mode, also visible before integration. The new contents panes pass contrast checks. This pre-existing chrome issue is outside the authorized data-only change and remains untouched.

Deferred editorial issue: the existing Greek V `[στιγμα]` encoding remains unchanged and separately documented in DEFERRED_BOOK_V.md. No outstanding source decision blocks these nine lists. Initial test-harness assertions were corrected to allow Book I’s approved paratext rubric and to open collapsed settings before interacting with pane controls; diagnostic outputs were retained. No production repair was necessary.

Reproduction: run validate.py and integrity.py with the bundled Python/lxml; build_disposable.rb with Jekyll into a temporary destination; prepare_browser.py then built-site.test.cjs for real-build TOC tests. Run regression.test.cjs normally and with --alignment-all-gate, --followup-gate, --multispan-gate, --protected-source-gate; bamberg-regression.test.cjs and interaction-regression.test.cjs provide the remaining checks. Scripts write only this new review directory and disposable build. implement.py is the original clean-worktree copy/insertion operation, not an in-place retranscription tool. certify.py collects successfully executed results and refreshes this review manifest.
''')
printed='\n'.join(f'- `{p}` — SHA-256 `{d["sha256"]}` ({d["bytes"]} bytes).' for p,d in source['sources']['printed'].items())
put('SOURCE_AUTHORITY.md',f'''# Source and archival authority

The accepted print-verified audit at `{A}` controls this data-only integration. It is retained unchanged. Its manifest SHA-256 is `4d5bf373b7d9d5c0d656a04b567b591446bafca9b24d4969ec98f73956c75d1b`: all 120 output entries, its explicit self-exclusion, 121-file inventory and all 504 recorded input hashes verify. See AUDIT_INPUT_INTEGRITY_QA.json and INTEGRITY_QA.json.

Archival arrangement: the complete external audit remains at its recorded path; do not remove or rewrite it when accepting this implementation. This directory mirrors its original manifest, report, authority, master, collation, review, plan and QA byte-for-byte in audit-authority/. The nine production companions are also byte-identical audit TEI proposals. AUDIT_ARCHIVE_REFERENCE.json records their linkage to the external packet, whose manifest enumerates every raw digital file, print-page image and audit script. This explicit hash-verified arrangement preserves the full evidence without copying PDFs or retranscribing sources into production.

The printed-Niese readings elected in the audit govern. Perseus is preserved as a separate collated digital witness; it was not silently substituted. The audit’s print glyph, punctuation, bracket-scope and Unicode policy remains intact. Full collation and genuine control issue are retained in the original documents. No source PDF was visually reopened or reinterpreted; original files were read only for integrity hashing.

Recorded printed edition scans:

{printed}

The I–V and VI–X scans provide the nine newly installed lists. Later-volume metadata in the accepted master is retained as context, not new transcription work. Current Perseus edition identity: `{source['sources']['perseus_current_edition']}`; requested historical identity: `{source['sources']['perseus_requested_legacy_identity']}`; official source repository snapshot: `{source['sources']['official_repository_commit']}`. Raw readings and digital-source hashes remain in the mirrored master and full external manifest.

The original proposals’ audit-stage publication/header language is deliberately preserved as historical provenance. This implementation record supplies their subsequent installation status; no historical audit document was rewritten. TEI schema: review/Antiquities_Traditional_Navigation_2026-10-06/tei_all.rng, SHA-256 `{h(R/'review/Antiquities_Traditional_Navigation_2026-10-06/tei_all.rng')}`.

Existing Greek V/XI–XX, Bamberg Latin, Lodge, deferred Whiston and other declarations remain independent and unchanged. Capitula source labels are not navigation identities. Book V’s separate control issue remains deferred, with no effect on the nine accepted books.
''')
put('REGISTRY_DIFF.md','''# Nine-record source-contents extension

The existing 30 item records, their attributes, order, text and byte serialization remain untouched. Nine new item/fs records from the approved proposal were inserted immediately before the existing closing list tag. Removing precisely the documented inserted byte interval reproduces the previous registry bytes.

Each new record has work=antiquities; language=Greek; witness=niese; status=VERIFIED; its own book number and companion path; selector `tei-div[type="contents"]`. These records register independent source paratext, not chapter or citation identities. No note, availability, path or source declaration of an earlier witness was changed.

'''+ '\n'.join(f'- `contents-antiquities-niese-{int(b):02}` → `assets/xml/antiquities/paratext/niese/book-{int(b):02}-contents.xml` ({n} entries).' for b,n in counts.items())+f'''

Population: 30 → 39 verified source records; Greek Antiquities: 11 → 20 books. Latin and English availability unchanged.

Before: `{rows[-1]['before_sha256']}`.
After: `{rows[-1]['after_sha256']}`.
Insertion byte offset: {rows[-1]['insertion_byte_offset']}; inserted bytes: {rows[-1]['insertion_byte_length']}.

The full reproducible registry diff follows:

```diff
'''+subprocess.check_output(['git','--no-optional-locks','-C',str(R),'diff','--','assets/xml/source-contents.xml'],text=True,encoding='utf-8')+'\n```\n')
# Every new implementation/review file is enumerated except this self-referential manifest.
outputs=[]
for p in sorted((p for p in V.rglob('*') if p.is_file() and p.name!='FILE_MANIFEST.json'),key=lambda p:p.relative_to(R).as_posix()):outputs.append({'path':p.relative_to(R).as_posix(),'sha256':h(p),'bytes':p.stat().st_size,'role':'implementation_review'})
for row in rows:
 p=R/row['path'];outputs.append({'path':row['path'],'sha256':h(p),'bytes':p.stat().st_size,'role':'production_source','before_sha256':row['before_sha256']})
outputs.sort(key=lambda x:x['path'])
dump('FILE_MANIFEST.json',{'date':'2026-10-08','base':integrity['canonical_HEAD'],'worktree':str(R),'audit_manifest_sha256':archive['original_manifest_sha256'],'self_exclusion':'This implementation FILE_MANIFEST.json only; the archived audit-authority/FILE_MANIFEST.json is included.','outputs':outputs,'entry_count':len(outputs),'production_source_count':10,'notes':'Individual unchanged canonical/worktree before/after hashes are in INTEGRITY_QA.json. Full external source audit is retained by the hash-verified archival arrangement.'})
# Include the archived manifest, whose filename is deliberately the same.
manifest=read('FILE_MANIFEST.json'); archived=V/'audit-authority/FILE_MANIFEST.json'
if not any(r['path']==archived.relative_to(R).as_posix() for r in manifest['outputs']):
 manifest['outputs'].append({'path':archived.relative_to(R).as_posix(),'sha256':h(archived),'bytes':archived.stat().st_size,'role':'unchanged_audit_manifest_copy'});manifest['outputs'].sort(key=lambda x:x['path']);manifest['entry_count']=len(manifest['outputs']);dump('FILE_MANIFEST.json',manifest)
for row in manifest['outputs']:assert h(R/row['path'])==row['sha256'],row['path']
print(json.dumps({'result':'PASS','review_manifest_entries_verified':manifest['entry_count'],'manifest_sha256':h(V/'FILE_MANIFEST.json'),'source_changes':10,'canonical_inventory_sha256':invhash(canon_old)}))
