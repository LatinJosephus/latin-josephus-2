from pathlib import Path
import json,hashlib,subprocess,collections
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
PRODUCTION=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development');BASE='f7d9142cad998e8a005adea1a22532b9a78592db'
def read(n):return json.loads((D/n).read_text(encoding='utf-8'))
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args],text=True).rstrip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert git(ROOT,'rev-parse','HEAD')==git(PRODUCTION,'rev-parse','HEAD')==BASE
assert git(ROOT,'branch','--show-current')=='antiquities-traditional-navigation'
assert git(PRODUCTION,'branch','--show-current')=='v2-development'
assert not git(PRODUCTION,'status','--porcelain=v1','--untracked-files=all')
assert not git(ROOT,'diff','--cached','--name-only')
assert not git(ROOT,'diff','--check')
full=read('BROWSER_QA.json');integrity=read('INTEGRITY_QA.json');xi=read('XI_MULTISPAN_GATE_QA.json');vi=read('VI_ALIGNMENT_GATE_QA.json');rendered=read('RENDERED_GATE_QA.json');protected=read('PROTECTED_SOURCE_GATE_QA.json');baseline=read('BASELINE.json')
assert full['traditional']=={'rows':1689,'executable':5034,'unavailable':33,'byLanguage':{'Greek':1678,'Latin':1678,'English':1678},'menusChapters':257,'menusSubchapters':1432,'physical':1441}
assert not full['errors'] and integrity['result']=='PASS'
assert len(xi['checks'])==18 and all(c['result']=='PASS' for c in xi['checks'])
assert len(rendered['checks'])==18 and protected['result']=='PASS'
niese=sum(v['selections'] for v in full['niese'].values());assert niese==2456
cross=collections.Counter()
for row in full['crossWork']:assert row['result']=='PASS';cross[row['work']]+=row['ranges']
source_ranges=sum(c['ranges'] for c in protected['checks']);source_niese=sum(c['niese'] for c in protected['checks'])
status=git(ROOT,'status','--porcelain=v1','--untracked-files=all')
assert all(line[:2] in [' M','??'] for line in status.splitlines())
previous=read('QA.json');history=previous.get('diagnostic_history',{'initial_VI_locator_blocker':previous.get('prior_locator_blocker'),'previous_XI_single_interval_restart':previous.get('full_restart'),'Book_XI_defect_interpretation':'WITHDRAWN; authentic witness order','earlier_URL_history_empty_selection_failure':'RESOLVED; explicit selected coordinate now persists'})
qa={'status':'PASS_GO_FOR_HUMAN_REVIEW_AND_COMMIT','date':'2026-10-06','worktree':str(ROOT),'branch':'antiquities-traditional-navigation','base_commit':BASE,'source_authorities':{'reconciliation_v1.1_commit':'41e817680549767d36e3f80dbc825682908ea5e6','reconciliation_v1.1_tag':'antiquities-structure-reconciliation-v1.1','independent_verification_v1.0_commit':'19308a8ed937525c540827205b0c763768f5ce44','independent_verification_v1.0_tag':'antiquities-loeb-niese-verification-v1.0'},'integrity':integrity,'browser_full_restart':full,'Book_XI_multi_span_gate':xi,'Book_VI_alignment_gate':vi,'rendered_DOM_and_exception_gate':rendered,'protected_Bellum_alternative_sources_and_Niese':protected,'totals':{'traditional_level_rows':1689,'physical_positions':1441,'Chapter_menus':257,'Subchapter_menus':1432,'language_cases':5067,'exact_executable_range_checks':5034,'expected_missing_Book_IX_range_cases':33,'current_Antiquities_Niese_selections':niese,'current_Antiquities_Niese_language_comparisons':niese*3,'protected_other_work_book_groups':len(full['crossWork']),'protected_other_work_range_checks':sum(cross.values()),'additional_Bellum_source_range_checks':source_ranges,'additional_Bellum_source_Niese_selections':source_niese},'Book_XI_XML_bytes_order_text_IDs_sameAs':'UNCHANGED','Book_XI_paragraph_reordering':'WITHDRAWN_NOT_PERFORMED','Book_XI_specific_renderer_conditionals':'NONE','Niese_VIII_XX_public_expansion':'NOT_IMPLEMENTED_PER_PHASE_1_SCOPE','Bamberg_navigation':'NOT_IMPLEMENTED_PER_PHASE_1_SCOPE','Book_VII_alignment_target_graph':'UNCHANGED; new traditional registry directly selects existing latin-book07-num','no_staging_commit_push_merge_rebase_or_Git_configuration_change':True,'only_authorized_worktree_branch_creation':True,'site_build':'NOT_RUN; source browser harness used','harness_qualification':'For differential tests the old renderer receives HTMLCollection.forEach compatibility; production protected-other-work code remains unchanged. Comparisons certify equality with that supplied compatibility.','diagnostic_history':history,'final_git':{'implementation_head':BASE,'implementation_branch':'antiquities-traditional-navigation','status_short':status,'staged_files':'','diff_check':'PASS','canonical_head':BASE,'canonical_branch':'v2-development','canonical_status_short':''}}
(D/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
f=read('BROWSER_FAILURE.json');f['current_disposition']='RESOLVED; see passing BROWSER_QA.json';(D/'BROWSER_FAILURE.json').write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf-8')
source_manifest_hashes={}
for key,filename in [('reconciliation','Antiquities_Structure_Reconciliation_v1.1_SHA256SUMS.txt'),('verification','Antiquities_Loeb_Niese_Verification_SHA256SUMS.txt')]:source_manifest_hashes[key]=baseline['authorities'][key][filename]['sha256']
source_text=f'''# Source authority and implementation scope

Production base: `{BASE}` on `v2-development`, verified clean before isolated worktree creation and unchanged after implementation. Worktree: `{ROOT}`; branch: `antiquities-traditional-navigation`.

- Structural reconciliation v1.1: recovery commit `41e817680549767d36e3f80dbc825682908ea5e6`, tag `antiquities-structure-reconciliation-v1.1`.
- Independent Loeb–Niese verification v1.0: recovery commit `19308a8ed937525c540827205b0c763768f5ce44`, tag `antiquities-loeb-niese-verification-v1.0`.
- Historical frozen Loeb extraction identifier: `e03d32a`.
- Reconciliation manifest SHA-256: `{source_manifest_hashes['reconciliation']}`.
- Independent verification manifest SHA-256: `{source_manifest_hashes['verification']}`.

Existing manifests verified before preparation; complete frozen-packet inventories remain unchanged. No source PDF, manuscript image, human workbook or Word audit was reopened or altered. The registry consumes completed source metadata; the frozen packets were not copied into production. Every one of 1,689 source identities, literal labels, associations, independent statuses and physical-copy check records is machine-compared with the frozen authorities.

Chapter/Subchapter names the traditional Hudson-Havercamp division retained by Niese and substantially reproduced by Loeb. Niese citation numbers, literal printed readings, frozen extraction associations and independent verification statuses remain separate data. All nine Loeb omissions of lower 1 and four Niese-only lower-1 observations remain witness-specific; no new Loeb division is invented.

Current-text overlay corrections are separated from source judgments: VI.xiii / VI.xiii.1 Latin/English refer to existing num272; VII.i / VII.i.1 Latin directly refer to existing latin-book07-num without repairing sameAs; Book XI has ordered physical spans. The three Greek Book VI alignment bindings were separately and expressly authorized. None changes frozen v1.1 or source status.

The user supplied Levenson and Martin (2016), p.330, identifying Ba with Group D and its transposed/interpolated Book XI order. Publication identity is supported by https://onlinelibrary.wiley.com/doi/10.1002/9781118325162.ch21; the page itself was not independently re-read. The interpretation of Book XI as a corpus-order defect is withdrawn. Its XML order and all bytes remain untouched. Greek/English current editorial alignment order is distinguished from the original editions' order.

The registry uses standard TEI P5 elements: TEI, teiHeader/fileDesc, listBibl/bibl, text/body, list/item/label, fs/f/string, vColl and note/p. Ordered spans use `vColl org="list"` and nested feature structures; no private XML elements were introduced. Validation against official P5 4.12.0 Relax NG passes. Schema source: https://tei-c.org/Vault/P5/4.12.0/xml/tei/custom/schema/relaxng/tei_all.rng. All 13 new inline anchors point to certified identities in the external registry.

Canonical production uses some CRLF files; Git materialized LF in the isolated checkout. BASELINE.json distinguishes both inventories. Removing only the 13 authorized empty anchors restores every isolated-checkout XML file byte-for-byte. No pre-existing XML text, ID, sameAs, numeral, apparatus, paragraph or inline node was rewritten, moved or normalized.

This is an implementation ready for human review, not a new frozen scholarly authority. It remains unstaged and uncommitted. Public Niese navigation remains at existing I-VII coverage; VIII-XX expansion and Bamberg navigation remain future phases.
'''
(D/'SOURCE_AUTHORITY.md').write_text(source_text,encoding='utf-8')
modified=integrity['changed_existing_files']
report=f'''# Antiquities traditional navigation: implementation Phase 1

**GO for human review and commit.** All required traditional-navigation QA passes. The implementation remains unstaged and uncommitted in `{ROOT}`, branch `antiquities-traditional-navigation`, based on `{BASE}`. Canonical production and frozen recovery authorities are unchanged.

## Architecture and URLs

Antiquities explicitly opts into `assets/xml/antiquities/structure.xml`. Chapter/Subchapter selectors derive from certified registry identities, with independent Greek, Latin and English start/end locators. The previous coarse Sub-chapter selector is labelled **Alignment unit**. Other works keep original adapters and navigation semantics.

| Parameter | Antiquities meaning |
|---|---|
| book | Book; preface selects Proem |
| chapter | certified traditional Chapter |
| subchapter | certified traditional lower division within Chapter, or Proem |
| niese | existing independent Niese citation navigation |
| unit | existing alignment unit, including suffix 276b |

Examples: `?book=5&chapter=3`; `?book=5&chapter=3&subchapter=2`; `?book=5&niese=179`; `?book=4&unit=276b`; `?book=preface&subchapter=2`. Irrelevant structural parameters are cleared; unrelated parameters and fragments are preserved. Scheme activation selects an explicit coordinate so reload and back/forward reproduce it. Pane toggles preserve identity. Antiquities has one configured source per language; protected works' alternate-source semantics are unchanged. No parallel legacy Chapter system or verbose traditionalChapter parameter was added.

TEI data separates persistent identity, label, parent/context, literal source reading, provenance, canonical association, independent status, confidence, availability and certified physical point. Source anomalies are data, never renderer case logic. Historical markers remain evidence and do not define new traditional menus.

## Registry and preserved source counts

257 Chapters; 1,432 Subchapters; 1,689 level rows; 1,441 certified physical positions. Proem has four lower divisions and no Chapter zero. Nine absent Loeb lower-1 openings and four Niese-only lower-1 observations remain witness-specific.

Primary source statuses remain 1,672 CONFIRMED_NIESE_START; 3 CONFIRMED_WITHIN_NIESE; 3 LOEB_NIESE_NUMBER_DISAGREEMENT; 11 NIESE_SOURCE_AMBIGUOUS; 0 UNRESOLVED. All 1,689 identities, raw readings, associations, verification statuses and human checks exactly match frozen authorities. TEI P5 4.12.0 Relax NG validation passes.

## Physical ranges and preservation

A generic resolver accepts one span or an ordered span list per language, selecting registered element edges or anchors without numeric paragraph arithmetic or visible-label parsing. Unmapped starts/ends show an unavailable state instead of nearby text. Later clones of a fragmented paragraph keep data-source-id provenance without duplicate rendered IDs; source XML IDs never change.

Only 13 empty anchors were inserted: Greek 7, Latin 3, English 3, across 12 files. Removing only those anchors recovers all pre-existing XML bytes exactly. Text, Unicode, punctuation, apparatus, IDs, sameAs, paragraph order/counts and inline markup are preserved. No Book VI, VII, IX or XI XML file changed. Paragraph totals remain Latin 1,622; Greek 1,681; English 1,600. Each layer retains 1,442 identified alignment paragraphs including Preface.

Book XI's authentic non-monotonic order is preserved; the paragraph-reordering proposal is withdrawn and none was performed. Chapter VIII has four spans per language; Subchapters 2,4,6 have two each; 3,5 have one each. Latin split 326a/b and 342a/b remain distinct physical fragments. Both Bellum 4.105 interpolation portions remain in Subchapter 2 witness fragments. Canonical views disclose assembly and link to unchanged Book view; Book/Alignment-unit views preserve witness order. Exact 311-347 membership is documented in XI_current_text_multispan_adjudication.md and XI_MULTISPAN_MEMBERSHIP.json.

VI.xiii / VI.xiii.1 now use verified Latin/English num272. VI.xii.8 uses Latin/English num271 and Greek num262/num[8]. Three expressly authorized data-only Greek alignment spans correct units 262,271,272 while preserving source XML and sameAs. V.iii.2 literal Loeb 79 and canonical 179 remain separate data, without renderer conditions.

VII.i / VII.i.1 directly select existing Latin latin-book07-num, allowing traditional navigation without repairing Greek/English #latin-book07-num1 targets. That alignment graph defect remains a separate known issue. Book IX missing source/current positions remain explicit; no text, marker or nearby substitution was invented.

The two earlier Latin projection mismatches were 18 trailing whitespace characters due to nested inner/outer body endpoints. The generic Book-end resolver now uses the complete loaded body. No lexical text or source position was repaired.

## QA

- Full restart from Proem/Book I: **1,689/1,689 identities / 5,067 language cases**, with **5,034 executable ranges PASS** and **33 expected Book IX unavailable cases PASS**. All 257 Chapter options, 1,432 Subchapter options and 1,441 physical identities verified. Each executable incipit and complete projected span/interval matches its locator and independent physical membership.
- Book XI: **18/18 language mappings**; two split-citation model checks (Latin 326,342); no unintended overlap or duplication; exact XI.viii.4 membership; Chapter/Subchapter partition equality; retained interpolation; disclosure and witness link; exact base equality for Book/Alignment-unit paragraphs.
- Book VI: locator **2/2**; original Niese 269/271 starts **6/6**; alignment **15/15 pane starts** across five units including neighbors; exact three-span partition; five pane-switch identities; focused Niese differential **6/6**.
- Current Antiquities Niese I-VII: **2,456 selections / 7,368 language comparisons PASS** against the base renderer. Public VIII-XX coverage was not expanded. Split-citation tests demonstrate model support, not new Book XI public coverage.
- DEH/Bellum/Contra Apionem: **14 book groups / {sum(cross.values()):,} chapter-unit range comparisons PASS**. By work: {dict(cross)}. Additional Bellum Whiston/Lodge: **14 source-book groups / {source_ranges:,} range comparisons**, including **{source_niese:,} citation selections**, PASS.
- Actual rendered exception pages: **18/18**; no duplicate DOM IDs; corrected labels; pane selection preserved; witness-order link works. Reload/back/forward, Book switching, Subchapter to Niese, Alignment unit, Proem, num276b, Book IX unavailable, Book VII opening, extra parameters and fragments PASS.
- Exact XML byte recovery, text/topology, anchor provenance, canonical checkout and frozen authorities PASS. Other-work XML, CSS/SCSS, layouts, configuration, CETEI and generated files unchanged.

The differential harness supplies HTMLCollection.forEach compatibility to the original renderer, which otherwise throws in the standalone harness. Antiquities materializes its annotation collection as an array; other-work code was left unchanged. Comparisons certify equality under that supplied compatibility. Source files were served locally without a site build or generated-file write.

## Modified files

14 existing files, plus registry and dedicated review records:

'''+''.join('- `'+f+'`\n' for f in modified)+'''
- New `assets/xml/antiquities/structure.xml`.
- `review/Antiquities_Traditional_Navigation_2026-10-06/`: reports, reproducible tests, schema and evidence metadata. Exact before/after hashes and status are in FILE_MANIFEST.json and QA.json.

## Remaining scope / disposition

Bamberg navigation and public Niese VIII-XX expansion remain deferred. Book IX missing text remains explicit. Book VII's existing alignment-target defect is unrepaired; traditional navigation uses verified independent locators. Canonical assembly is disclosed and does not claim Bamberg itself has canonical order.

No staging, commit, push, merge, rebase, canonical-checkout write, frozen-packet write or Git configuration change occurred. Only the authorized isolated branch/worktree creation wrote Git administrative state. **GO for human review and commit of this isolated Phase 1 implementation.**

## Reproduction

Run bundled Python verify_integrity.py, then Node navigation.test.cjs with --locator-gate, --alignment-gate, --multispan-gate, --rendered-gate, no flag for exhaustive QA, and --protected-source-gate. Tests use installed Chrome in an isolated context. Do not rerun one-time prepare_registry.py over the existing registry. Earlier BROWSER_FAILURE.json and XI_RANGE_BLOCKER.json are labelled historical and superseded by passing reports.
'''
(D/'REPORT.md').write_text(report,encoding='utf-8')
status=git(ROOT,'status','--porcelain=v1','--untracked-files=all');files=[]
for line in status.splitlines():
 rel=line[3:];assert rel=='assets/xml/antiquities/structure.xml' or rel in modified or rel.startswith('review/Antiquities_Traditional_Navigation_2026-10-06/'),rel
 if rel.endswith('/FILE_MANIFEST.json'):continue
 p=ROOT/rel;files.append({'path':rel,'git_status':line[:2],'before_sha256':baseline['worktree'].get(rel,{}).get('sha256'),'after_sha256':sha(p),'bytes':p.stat().st_size})
manifest={'base_commit':BASE,'branch':'antiquities-traditional-navigation','status':'PASS_GO_FOR_HUMAN_REVIEW_AND_COMMIT','before_hash_basis':'Original isolated-worktree bytes; canonical inventory separately protected in BASELINE.json','files':sorted(files,key=lambda f:f['path']),'self_hash_excluded':True,'canonical_checkout':'UNCHANGED_CLEAN','unstaged_uncommitted':True}
(D/'FILE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for f in manifest['files']:assert sha(ROOT/f['path'])==f['after_sha256']
print(json.dumps({'status':qa['status'],'registry':integrity['registry'],'QA':qa['totals'],'modified_existing_files':len(modified),'manifest_entries':len(files),'unstaged':True,'canonical_clean':True,'report':str(D/'REPORT.md')},indent=2))