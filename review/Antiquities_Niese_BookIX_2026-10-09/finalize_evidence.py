"""Freeze final IX certification after the explicit240 adjudication."""
from pathlib import Path
import json,hashlib,subprocess,shutil,sys,datetime
from mixed_mapper import Book,digest
P=Path(__file__).resolve().parent;W=P.parents[1];R=Path('C:/workspace/Antiquities-Niese-09-runtime-20261009');C=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def git(*args,where=W):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=where).decode().strip()
base=read(P/'BASELINE.json');ids=read(P/'EXECUTABLE_IDENTITIES.json');preservation=read(P/'SOURCE_PRESERVATION_QA.json');qa=read(P/'NEW_BOOK_BROWSER_QA.json');protected=read(P/'PROTECTED_BROWSER_QA.json');bellum=read(P/'PROTECTED_SOURCE_GATE_QA.json');inherited=read(P/'INHERITED_ISSUES_QA.json')
for rel,record in base['inputs'].items():
    assert digest(Path(record['snapshot']).read_bytes())==record['worktree_sha256']
    blob=subprocess.check_output(['git','show',base['base']+':'+rel],cwd=W)
    assert digest(blob)==record['git_blob_sha256']
    assert git('rev-parse',base['base']+':'+rel)==record['git_blob_id']
assert not ids['pending']
assert qa['result']=='PASS_CERTIFIED' and qa['phase']=='POST_EXPLICIT_240_RESOLUTION'
assert preservation['phase']=='POST_EXPLICIT_240_RESOLUTION'
assert read(P/'FINAL_BOUNDARY_239_241.json')['result']=='PASS'
assert read(P/'EDITORIAL_DECISIONS.json')['240']['choice']=='A'
assert protected['result']==bellum['result']==inherited['result']==preservation['result']=='PASS'
assert len(qa['actual_selector_events'])==291 and len(qa['traditional_ranges'])==68
assert not qa['errors'] and not qa['consoleErrors'] and not qa['networkFailures']
assert all(s['byte_exact_recovery'] and s['source_build_byte_equal'] for s in preservation['sources'].values())
assert preservation['reader_build_byte_equal'] and preservation['registry_build_byte_equal']
full_build_commit='668ed06cfce878cbced07381e35851d0ffcaf662'
prior_commit='5794785c61beb6fee7e7fade6275092c42ddef77'
since_prior=git('diff','--name-only',prior_commit,'HEAD','--','assets','_includes').splitlines()
assert set(since_prior)=={'assets/xml/antiquities/Greek/book-09.xml','assets/xml/antiquities/Latin/book-09.xml','assets/xml/antiquities/niese/book-09.json'}
prior_reader=read(P/'qa-history/pre-decision-5794785/BUILD_RECORD.json')['assets']['assets/js/renderTei.js']['source_sha256']
assert prior_reader==digest((W/'assets/js/renderTei.js').read_bytes())
history_dir=P/'qa-history/pre-decision-5794785'
for name in ['IX110-light.png','IX110-dark.png']:
    target=history_dir/name
    original_png=subprocess.check_output(['git','show',prior_commit+':'+str((P/name).relative_to(W)).replace('\\','/')],cwd=W)
    if target.exists():assert target.read_bytes()==original_png
    else:target.write_bytes(original_png)
prior_build=read(history_dir/'BUILD_RECORD.json')
for name,expected_hash in prior_build['log_hashes'].items():assert digest((history_dir/'build-logs'/name).read_bytes())==expected_hash
write(history_dir/'PRE_DECISION_ADDITIONAL_ARTIFACTS.json',{'scope':'PRE_EXPLICIT_240_RESOLUTION','checkpoint':prior_commit,
 'files':[{'name':str(f.relative_to(history_dir)).replace('\\','/'),'sha256':digest(f.read_bytes()),'bytes':f.stat().st_size}
          for f in sorted(list((history_dir/'build-logs').iterdir())+[history_dir/'IX110-light.png',history_dir/'IX110-dark.png'])]})
protected_applicability={'result':'PASS','scope':'Retained preceding-decision broad protected evidence; not claimed as rerun',
 'preceding_checkpoint':prior_commit,'phase':'PRE_EXPLICIT_240_RESOLUTION',
 'original_records':'qa-history/pre-decision-5794785',
 'production_paths_changed_since_preceding_checkpoint':since_prior,
 'shared_reader_sha256_unchanged':prior_reader,'all_protected_sources_and_configuration_unchanged':True,
 'post_decision_gate':'NEW_BOOK_BROWSER_QA.json: all IX selections/ranges and accepted VIII/X controls rerun'}
write(P/'PROTECTED_EVIDENCE_APPLICABILITY.json',protected_applicability)
inherited['publicationSHA256']=digest(Path(inherited['publicationPath']).read_bytes());write(P/'INHERITED_ISSUES_QA.json',inherited)
tools={'Python':{'absolute_path':sys.executable,'version':sys.version,'sha256':digest(Path(sys.executable).read_bytes())},'Node':{'absolute_path':shutil.which('node'),'version':subprocess.check_output(['node','--version']).decode().strip()},'Git':{'absolute_path':shutil.which('git'),'version':git('--version')},'Chrome':{'absolute_path':'C:/Program Files/Google/Chrome/Application/chrome.exe','sha256':digest(Path('C:/Program Files/Google/Chrome/Application/chrome.exe').read_bytes())},'Playwright':{'absolute_package':'C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright','version':read(Path('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json'))['version']},'Docker':{'engine':'29.7.2','image':'ruby:3.3-bookworm','image_id':'sha256:dba270af6994f64e45ee3dd2b85225a2a0d01f29c04508c7a3c7c8dbf59d2a85'},'Bundler':{'version':'4.0.22','source':'build.sh and dependency log'}}
write(P/'EXECUTABLE_TOOLS.json',tools)
logdir=P/'build-logs';logdir.mkdir(exist_ok=True)
for name in ['jekyll.log','baseline-jekyll.log']:shutil.copyfile(R/'build'/name,logdir/name)
assets={}
for rel in preservation['only_production_paths_changed']:
    assets[rel]={'source_sha256':digest((W/rel).read_bytes()),'served_build_sha256':digest((R/'build/site'/rel).read_bytes()),'byte_equal':(W/rel).read_bytes()==(R/'build/site'/rel).read_bytes()}
    blob=git('rev-parse',full_build_commit+':'+rel)
    assert git('hash-object','--path='+rel,str(W/rel))==blob
    assets[rel]['build_commit_Git_blob_id']=blob
assert all(v['byte_equal'] for v in assets.values())
write(P/'BUILD_RECORD.json',{'result':'PASS','phase':'POST_EXPLICIT_240_RESOLUTION','frozen_baseline':base['base'],'full_build_implementation_commit':full_build_commit,'build_script_absolute':str(P/'build.sh'),'runtime':str(R),'source_mount_read_only':True,'baseline_from_git_archive':True,'implementation_and_baseline_Jekyll_builds':'SUCCESS_EXIT_0','static_refresh':[],'preceding_build_record':'qa-history/pre-decision-5794785/BUILD_RECORD.json','assets':assets,'log_hashes':{f.name:digest(f.read_bytes()) for f in logdir.iterdir()},'tool_identities':'EXECUTABLE_TOOLS.json','QA_origin':qa['origins'][0],'final_IX_profile':str(R/'profile-ix'),'preceding_separate_profiles':[str(R/name) for name in ['profile-protected','profile-bellum','profile-inherited-issues']]})
method=[]
for rel in ['review/Antiquities_Niese_BookVIII_2026-10-08/SOURCE_AUTHORITY.md','review/Antiquities_Niese_BookX_2026-10-08/SOURCE_AUTHORITY.md','review/Antiquities_Niese_BookX_2026-10-08/mixed_mapper.py','review/Antiquities_Niese_Batch_08_10_2026-10-08/METHOD_SOURCE_MANIFEST.json','review/Antiquities_Niese_Implementation_08_10_2026-10-09/implement.py','review/Antiquities_Niese_Implementation_08_10_2026-10-09/browser-certify.cjs','review/Antiquities_Niese_Implementation_08_10_2026-10-09/established-regressions.test.cjs','review/Antiquities_Niese_Integration_08_10_2026-10-09/REPORT.md']:
    method.append({'absolute_path':str(W/rel),'sha256':digest((W/rel).read_bytes()),'Git_base_blob_id':git('rev-parse',base['base']+':'+rel),'role':'Pinned accepted methodological/control evidence'})
method.append({'absolute_path':str(P/'mixed_mapper.py'),'sha256':digest((P/'mixed_mapper.py').read_bytes()),'role':'Local derived mapper: exact IX placeholders and terminal subscription exclusion; 16 fixtures and independent real-source locators verified'})
write(P/'METHOD_SOURCE_MANIFEST.json',method)
summary={'book':9,'branch':git('branch','--show-current'),'frozen_base':base['base'],'canonical_initial_HEAD':base['canonical_initial_HEAD'],'canonical_latest_HEAD':git('rev-parse','HEAD',where=C),'canonical_advance':git('rev-parse','HEAD',where=C)!=base['canonical_initial_HEAD'],'canonical_status':git('status','--porcelain',where=C),'worktree':str(W),'review':str(P),'runtime':str(R),'implementation_HEAD_before_certification_commit':git('rev-parse','HEAD'),'expected_identities':291,'represented_Latin_candidates':232,'inherited_Latin_starts':46,'proposed_Latin_milestones':186,'applied_Latin_milestones':185 if ids['pending'] else 186,'actual_Latin_source_starts':preservation['sources']['Latin']['actual_starts'],'Latin_nonempty_reader_intervals':sum(e['Latin']=='REPRESENTED' for e in qa['actual_selector_events']),'Greek_nonempty_reader_intervals':sum(e['Greek']=='REPRESENTED' for e in qa['actual_selector_events']),'whole_section_unavailable':59,'unavailable_span':[51,109],'partial_surviving_sections':[110],'suppressed_IX_inherited_labels':0,'Greek_marker_additions':[1],'Greek_marker_moves':[181,216]+([240] if not ids['pending'] and read(P/'EDITORIAL_DECISIONS.json')['240']['choice']=='A' else []),'pending_editorial_decisions':ids['pending'],'adjacent_extents_held':[239,240] if ids['pending'] else [],'published_selection_baseline':3157,'local_added_selectable_identities':291,'local_selectable_total':3448,'publication_updated':False,'all_other_books_unchanged':True,'source_recovery':'BYTE_EXACT','new_book_reader_QA':qa['result'],'all_actual_IX_selector_events':291,'actual_IX_chapter_ranges':sum(r['kind']=='chapters' for r in qa['traditional_ranges']),'actual_IX_subchapter_ranges':sum(r['kind']=='subchapters' for r in qa['traditional_ranges']),'protected_Niese_selections':sum(x['identities'] for x in protected['antiquities']['niese']),'protected_traditional_ranges':sum(x['identities'] for x in protected['antiquities']['traditional']),'protected_Bamberg_ranges':sum(x['identities'] for x in protected['antiquities']['bamberg']),'protected_alignment_units':sum(x['identities'] for x in protected['antiquities']['alignment']),'protected_cross_work_books':len(protected['crossWorks']),'Bellum_witness_range_comparisons':sum(x['ranges'] for x in bellum['checks']),'QA_origin':qa['origins'][0],'technical_independent_work_complete':True,'editorial_completion':'PROVISIONAL_PENDING_240' if ids['pending'] else 'COMPLETE','ready_for_integration':not bool(ids['pending']),'no_merge_push_deploy':True,'recorded_UTC':datetime.datetime.now(datetime.UTC).isoformat()}
assert summary['Latin_nonempty_reader_intervals']==summary['actual_Latin_source_starts']==232
assert summary['inherited_Latin_starts']+summary['applied_Latin_milestones']==232
assert summary['Latin_nonempty_reader_intervals']+summary['whole_section_unavailable']==291
summary.update({'phase':'POST_EXPLICIT_240_RESOLUTION','explicit_editorial_resolution':'240:A',
 'frozen_inputs_and_Git_blobs_rechecked':True,
 'containing_final_boundary_views':qa['final_boundary_containing_views'],
 'earlier_test_results':'PRE_EXPLICIT_240_RESOLUTION; qa-history/pre-decision-5794785',
 'protected_evidence_applicability':'PROTECTED_EVIDENCE_APPLICABILITY.json',
 'final_239_241_extents':'FINAL_BOUNDARY_239_241.json'})
write(P/'CERTIFICATION.json',summary)
commits=git('log','--reverse','--format=%H %s',base['base']+'..HEAD').splitlines()
report=f'''# Antiquities IX — completed local handoff

Status: **COMPLETE, locally certified and ready for coordinated integration**. The user explicitly resolved §240 as A. No editorial decisions remain. No merge, push, preview update or deployment occurred.

The frozen base is `{base['base']}`. Canonical initial HEAD was `{base['canonical_initial_HEAD']}`; latest recorded HEAD is `{summary['canonical_latest_HEAD']}`. Later advance: {'yes' if summary['canonical_advance'] else 'none'}. Canonical working tree: {'clean' if not summary['canonical_status'] else repr(summary['canonical_status'])}. The frozen inputs were not replaced by later canonical code. Branch `{summary['branch']}` is at `{W}`. Review evidence is `{P}`; disposable builds, logs and isolated browser profiles are `{R}`. Final QA origin: `{summary['QA_origin']}`. Full final implementation build: `{full_build_commit}`.

## Boundary authority and arithmetic

Niese II's independently examined opening and ending establish §§1–291. All 291 printed starts and 232 surviving Latin candidates were individually reviewed. The three supplied XML witnesses omit §§51–109 behind preserved editorial placeholders, giving 59 explicit unavailable identities. This is an omission in these files; neither a physical cause nor absence across the whole Latin tradition is inferred. IX.110 preserves only Jehu's concluding reply and has a qualified partial-survival notice.

The final arithmetic is **232 represented Latin intervals = 46 retained starts + 186 new milestones**; **291 identities = 232 represented Latin intervals + 59 unavailable identities (§§51–109)**. All 232 physical starts render nonempty Latin intervals. No IX inherited visible label requires executable suppression. Published coverage remains 3,157; local IX adds 291 selectable identities, giving 3,448 local selections. The 232 Latin intervals are counted separately.

The explicit Greek marker edit list is: add implicit opening `[1]`; relocate §181 before `τρία βέλη`; relocate §216 before `τὸν αὐτὸν δὲ τρόπον`; relocate §240 before `ἔσται δ᾽`. The first two relocations were independently verified in print/control. The §240 relocation is an **explicit editorial resolution of the word-level ambiguity in the printed numeral's placement**, paired with Latin before `et nullus`. Niese printed page 317/PDF page 325 and Loeb Greek printed page 126/PDF page 142 identify a line containing both possible clause starts; neither unambiguously fixes the word cut at ἔσται. DECISION_240.md preserves the observed line, both images and alternatives. The inherited Greek cut at `σώζειν γὰρ`, paired with Latin `dum animas suas`, remains rejected alternative B in the history.

The exact frozen packet locators for A govern both marker operations. FINAL_BOUNDARY_239_241.json/.md records recomputed neighbouring extents and frozen/final Unicode and raw-byte locators. Only §§239 and 240 change extent from the preceding provisional review. §241 and every other boundary are unchanged. §§239–241 form the identical frozen narrative span without loss or duplication.

## Preservation and scope

Exact inversion removes the 186 added Latin milestones and reverses only opening 1 and Greek relocations 181, 216 and 240. It recovers the same frozen worktree bytes and SHA-256 hashes used by the locators. Original words, punctuation, whitespace, markup, apparatus, IDs, sameAs, paragraph numbering, inherited visible labels and traditional/Bamberg divisions are preserved. English source bytes and every other book are unchanged. The final subscription `explicit liber nonus` remains in the XML and terminal display, with its 20 code points separately excluded from the narrative coordinate stream. No XML-wide normalization or reserialization is used.

Only four production paths differ from the frozen base: Greek IX XML, Latin IX XML, IX identity JSON and the minimal shared reader support. SHARED_SUPPORT.md explains the IX registry and two opt-in data behaviors; its code was committed separately. display-settings.html and all other production files are unchanged. Integration must reconcile this frozen branch with then-current canonical code.

## Final reader certification

A fresh full Jekyll build of final implementation `{full_build_commit}` and the archived frozen baseline both exited 0. The final build uses no static refresh. Every served changed asset matches final worktree bytes. BUILD_RECORD.json preserves executable identities, build provenance, logs and hashes.

The post-decision NEW_BOOK_BROWSER_QA.json passes all 291 actual IX selector events, exact Greek/Latin extents, Whiston broader context, 59 unavailable selections, complete narrative partition, final extent, IDs and pane links. All {summary['actual_IX_chapter_ranges']} chapter and {summary['actual_IX_subchapter_ranges']} subchapter events match complete pinned range projections. Chapter XI (`LOEB-09-Chapter-11-0`) and subchapter XI.3 (`LOEB-09-Subchapter-11-3`) each contain the complete resulting §§239–241 Greek and Latin intervals. Actual production selections 239, 240 and 241 and their screenshots were independently inspected after the final decision.

Deep links, previous/next, reload/history, pane/language switching and light/dark behavior pass. Unmodified production code was checked at openings, omission edges, 110, 181, 216, 239–241 and 291. The final gate reruns all four accepted inherited-label exceptions, VIII.367–369 and X.101–102, 108–109, 150–151, 276–277. X.108 Greek/English remain independently accessible. Lodge note toggling, witness switching and reload also pass. Final IX QA has zero unexpected script, console or network diagnostics.

## Earlier evidence preceding the final decision

`qa-history/pre-decision-5794785` preserves the original provisional registers, reports, build logs and QA with hashes. Earlier broad protected results precede the final §240 decision: {summary['protected_Niese_selections']} existing Niese selections, {summary['protected_traditional_ranges']} traditional ranges, {summary['protected_Bamberg_ranges']} Bamberg ranges, {summary['protected_alignment_units']} Alignment units, source contents across preface/I–XX, {summary['protected_cross_work_books']} cross-work books and {summary['Bellum_witness_range_comparisons']} Bellum Whiston/Lodge range comparisons. They are retained evidence, not claimed as newly rerun. PROTECTED_EVIDENCE_APPLICABILITY.json verifies that the shared reader, protected sources and configuration are unchanged since that checkpoint; only IX Greek/Latin XML and identity data changed. The final gate retests all affected IX selections/ranges and accepted VIII/X controls.

INHERITED_ISSUES_QA.json precisely records the documented Book-I Bamberg route's three apparatus hyperlinks/two malformed targets and unsupported I.1 error, with supported I.27 verified. No additional errors are excused by those inherited exceptions. Historical sandbox loopback denial and corrected harness assumptions remain recorded separately from passing reader evidence.

## Scoped local commits

'''+'\n'.join('- `'+c[:40]+'` '+c[41:] for c in commits)+'''\n\nThe final certification commit follows these implementation commits. Its hash and clean status are reported in the handoff response, avoiding a self-referential ID inside its own committed file. FILE_MANIFEST.json contains exact changed paths and frozen-input, served-asset and review-file hashes; it excludes itself from self-hashing.\n'''
(P/'REPORT.md').write_text(report,encoding='utf8',newline='\n')
manifest={'frozen_base':base['base'],'production_changes':assets,'Git_changed_files':sorted(set(git('diff','--name-only',base['base']).splitlines()+git('ls-files','--others','--exclude-standard').splitlines())),'review_files':[{'absolute_path':str(f),'relative_path':str(f.relative_to(W)).replace('\\','/'),'bytes':f.stat().st_size,'sha256':digest(f.read_bytes())} for f in sorted(P.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f!=P/'FILE_MANIFEST.json'],'self_hash_exclusions':['FILE_MANIFEST.json']}
write(P/'FILE_MANIFEST.json',manifest)
print(json.dumps(summary,ensure_ascii=False,indent=2))
