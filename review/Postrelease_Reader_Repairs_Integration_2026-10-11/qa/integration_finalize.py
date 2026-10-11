import reader_integration as a
from pathlib import Path
import csv,gzip,json,shutil,sys,zipfile,subprocess

RESULT_FILES=['THEME_FINAL.json','PACKAGE_final_final.json','PACKAGE_E_final.json','candidate-VII1-7.json','candidate-VII1-REGRESSION.json','COMBINED_CONTEXT.json','CONTEXT_GUARDS.json','TARGETED_UI.json','VII2_6_NAVIGATION_PRESENTATION.json','KEYBOARD_FULL_SOURCE.json','PROTECTED_CONTROLS.json','FIVE_DEFECTS_candidate-final.json','GENERAL_NAVIGATION.json','COMPACT_EVIDENCE.json','CONTAINING_REAL_UI.json','CONTAINING_IDS_REAL_UI.json','APPARATUS_HOLD_COMPARISON.json','READER_FINAL_PRIOR_RESULTS.json']

def text(p,s):Path(p).write_text(s,encoding='utf8',newline='\n')
def git_blob(ref,p):return a.u.git('show',ref+':'+p)
def check_production(ref):
 source=a.u.load(a.T/'START.json')['source_production_manifest'];rows=[]
 for r in source:
  p=r['path'];h=a.u.sha((a.W/p).read_bytes());blob=a.u.sha(git_blob(ref,p))
  assert h==blob==r['final_SHA256'],p
  rows.append({'path':p,'baseline_SHA256':a.u.sha(git_blob(a.saved()['baseline'],p)),'certified_source_SHA256':r['final_SHA256'],'integrated_working_SHA256':h,'integrated_Git_blob_SHA256':blob,'Git_blob':a.u.gt('rev-parse',ref+':'+p),'bytes':(a.W/p).stat().st_size})
 return rows

def certify():
 ctx=a.saved();start=a.u.load(a.T/'START.json');merge=a.u.load(a.T/'MERGE.json');merged=a.u.gt('rev-parse','HEAD',repo=a.W)
 assert merged==merge['HEAD'] and not merge['conflicts']
 assert a.u.gt('rev-list','--parents','-n','1',merged).split()[1:]==merge['merge_parents']
 assert a.ancestor(a.SOURCE,merged) and a.ancestor(ctx['baseline'],merged)
 jobs={n:a.u.load(a.T/('QA_JOB_'+n+'.json')) for n in ['baseline','niese','structural','focused']}
 for n,j in jobs.items():
  assert j['status']=='PASS',n
  for row in j['results']:assert row['exit_code']==0 and a.u.sha(Path(row['script']).read_bytes())==row['script_SHA256']
 before=a.u.load(a.T/'baseline-NIESE.json');after=a.u.load(a.T/'candidate-final-NIESE.json')
 assert before['result']==after['result']=='COMPLETE' and len(before['rows'])==len(after['rows'])==7376
 assert not before['errors'] and not after['errors'] and before['books']==after['books']
 bm={(r['book'],r['n']):r for r in before['rows']};am={(r['book'],r['n']):r for r in after['rows']}
 assert bm.keys()==am.keys() and len(am)==7376
 for key,row in am.items():
  assert row['languages']==bm[key]['languages'],key
  assert row['duplicates']==[] and bm[key]['duplicates']==[],key
 assert before['books'][0]['count']==26 and sum(b['count'] for b in before['books'][1:])==7350
 comparison={'result':'PASS','before_commit':ctx['baseline'],'tested_merged_commit':merged,'baseline_count':7376,'integrated_count':7376,'Proem':26,'Books_I_XX':7350,'exact_three_language_DOM_text_ID_type_notice_comparisons':22128,'wrong_or_lost_selections':0,'new_duplicate_IDs':0,'errors':[],'books':after['books'],'method':'Fresh uninstrumented browser selection of every supported identity; exact complete three-pane DOM/text/IDs/type/qualification hashes compared with independently rebuilt and freshly captured canonical baseline. Public menu controls and real URL identity checked. Whiston is qualified context, not word-exact Niese segmentation.'}
 a.u.save(a.T/'NIESE_COMPARISON.json',comparison)
 st=a.u.load(a.T/'READER_FINAL_PRIOR_RESULTS.json');assert st['result']=='PASS' and not st['errors']
 assert st['totals']=={'traditional':1689,'bamberg':198,'alignment':1441}
 assert len(st['books'])==21 and all(b['contents']=='PASS' and b['result']=='PASS' for b in st['books'])
 assert sum(r['niese'] for r in st['cross_works'])==8002 and sum(r['ranges'] for r in st['cross_works'])==1630
 results={n:a.u.load(a.T/n) for n in RESULT_FILES}
 for n,d in results.items():
  if n in ['FIVE_DEFECTS_candidate-final.json','COMPACT_EVIDENCE.json','APPARATUS_HOLD_COMPARISON.json']:continue
  assert d.get('result',d.get('status'))=='PASS',n
  assert not d.get('errors'),n
 raw=results['FIVE_DEFECTS_candidate-final.json'];assert len(raw['rows'])==11
 for row in raw['rows']:
  assert not row['errors'] and not row['network'],row['route']
  dup=[item[0] for item in row['state']['duplicates']]
  assert dup==(['header'] if row['route']=='/bellum-judaicum/?book=1' else []),(row['route'],dup)
 assert len(raw['linkRequests'])==2 and all(r['status']==404 for r in raw['linkRequests'])
 hold=results['APPARATUS_HOLD_COMPARISON.json'];assert hold['status'].startswith('KNOWN UNRESOLVED') and hold['original_identifiers_preserved'] and hold['no_guessed_redirect'] and len(hold['links'])==3 and len(hold['requests'])==2
 compact=results['COMPACT_EVIDENCE.json'];assert compact['result']=='PASS' and len(compact['errors'])==2 and all(r['mode']=='baseline' for r in compact['errors'])
 for p in results['candidate-VII1-7.json']['rows']:assert p['result']=='PASS'
 for r in results['COMBINED_CONTEXT.json']['ranges']:assert r['result']=='PASS'
 assert not results['PROTECTED_CONTROLS.json']['exact_inherited_exceptions']
 manifest=a.u.load(a.T/'SOURCE_MANIFEST_VERIFICATION.json');assert manifest['status']=='PASS' and manifest['baseline_file_count']==5166 and manifest['unchanged_count']==5158 and manifest['changed_production_count']==8
 protected=a.u.load(a.T/'PROTECTED_INPUTS.json');assert protected['XML_count']==143 and protected['protected_count']==159
 for r in protected['files']:assert a.u.sha((a.W/r['path']).read_bytes())==r['SHA256']
 production=check_production(merged);build=a.u.load(a.T/'BUILD_candidate-final.json');assert build['source_commit']==merged
 assert len(build['assets'])==251
 for r in build['assets']:assert a.u.sha((a.T/'candidate-final-site'/r['path']).read_bytes())==r['SHA256']
 assert a.u.load(a.T/'BUILD_VERSION_COMPARISON.json')['result']=='PASS'
 assert sorted(a.u.gt('diff','--name-only',ctx['baseline'],merged,'--',':(exclude)review/').splitlines())==a.PRODUCTION
 assert a.u.state(a.S)['HEAD']==a.SOURCE and not a.u.state(a.S)['status']
 changed={'UTC':a.u.now(),'baseline_commit':ctx['baseline'],'tested_merged_commit':merged,'certified_source_tip':a.SOURCE,'production':production,'built_assets':build['assets'],'built_asset_count':251,'all_built_assets_match_source_certificate':True,'source_manifest_verification':'SOURCE_MANIFEST_VERIFICATION.json','protected_143_XML_159_inputs':'PROTECTED_INPUTS.json'}
 a.u.save(a.T/'PRODUCTION_MANIFEST.json',changed)
 certificate={'UTC':a.u.now(),'status':'PASS WITH SPECIFIC KNOWN UNRESOLVED ISSUES','promotion_gate':'PASS','new_regressions':0,'baseline_commit':ctx['baseline'],'tested_merged_commit':merged,'certified_source_tip':a.SOURCE,'merge_parents':merge['merge_parents'],'conflicts':[],'resolution':'Normal history-preserving merge, no conflict or additional production reconciliation; eight files match certified source exactly.','packages':{'A':'PASS','B':'PASS — reader annotation collision repaired; original source IDs untouched','C':'KNOWN UNRESOLVED — EXPLICIT EDITORIAL HOLD; 3 source links, 2 original 404 targets preserved and independently reproduced before/after','D':'PASS','E':'PASS'},'Niese':comparison,'structural':st['totals'],'Book_contents_configurations':21,'cross_work_Niese':8002,'cross_work_structural':1630,'focused_suite_counts':{n:len(d.get('checks',d.get('rows',d.get('ranges',d.get('critical',[]))))) for n,d in results.items() if n not in ['FIVE_DEFECTS_candidate-final.json','READER_FINAL_PRIOR_RESULTS.json','COMPACT_EVIDENCE.json','APPARATUS_HOLD_COMPARISON.json']},'actual_UI_containing_cases':16,'source_XML_unchanged':143,'protected_inputs_unchanged':159,'frozen_baseline_files':5166,'baseline_files_unchanged':5158,'production_changed':8,'renderer_SHA256':next(r['integrated_Git_blob_SHA256'] for r in production if r['path']=='assets/js/renderTei.js'),'built_assets_match_certified_source':251,'known_limitations':[hold['status']+'; see literal UNRESOLVED_REFERENCES packet','Bellum Book I inherited TEI source-source header collision independently reproduced before/after: annotations/header before, header only after; outside package B scope.','Combined Niese context uses the internal generic renderer/test harness; no public Niese range selection control or new public range URL is claimed.'],'browser':'Fresh isolated Chrome profiles, independent loopback ports and download directories; no original worker browser cache cleared.','build_policy':'Fresh native Ruby/Jekyll from the actual merged checkout, inherited certified responsive-image-plugin exclusion and loopback URL configuration; no dependency upgrade or copied old build.','exhaustive_harness_method':'Structural and cross-work exhaustive comparisons run actual production selection/extent code with getter-only instrumentation on all source inputs, comparing complete rendered DOM/text to fresh frozen baseline. Real containing-view clicks, direct/reload/history and accessibility/presentation tests separately uninstrumented.','QA_jobs':jobs,'public_preview':'Not modified, published or deployed; provenance and domain unchanged.','receipt_path':str(a.T/'INTEGRATION_RECEIPT.json')}
 a.u.save(a.T/'INTEGRATION_CERTIFICATE.json',certificate)
 for n in RESULT_FILES+['NIESE_COMPARISON.json','INTEGRATION_CERTIFICATE.json','PRODUCTION_MANIFEST.json','SOURCE_MANIFEST_VERIFICATION.json','PROTECTED_INPUTS.json','BUILD_baseline.json','BUILD_candidate-final.json','BUILD_VERSION_COMPARISON.json','ORCHESTRATION_ATTEMPTS.json']+[p.name for p in a.T.glob('QA_JOB_*.json')]:shutil.copy2(a.T/n,a.Q/n)
 for n in ['baseline-NIESE.json','candidate-final-NIESE.json']:
  with gzip.GzipFile(filename=str(a.Q/(n+'.gz')),mode='wb',mtime=0) as z:z.write((a.T/n).read_bytes())
 with (a.Q/'NIESE_MATRIX.csv').open('w',encoding='utf8',newline='') as f:
  fields=['book','niese','exact_local_URL','language','before_DOM_SHA256','after_DOM_SHA256','before_text_SHA256','after_text_SHA256','selection_type','source_IDs','qualification_notices','result'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for key,row in am.items():
   for lang,d in row['languages'].items():w.writerow({'book':row['book'],'niese':row['n'],'exact_local_URL':row['URL'],'language':lang,'before_DOM_SHA256':bm[key]['languages'][lang]['DOM'],'after_DOM_SHA256':d['DOM'],'before_text_SHA256':bm[key]['languages'][lang]['text'],'after_text_SHA256':d['text'],'selection_type':d['type'],'source_IDs':json.dumps(d['ids'],ensure_ascii=False),'qualification_notices':json.dumps(d['notes'],ensure_ascii=False),'result':'PASS'})
 text(a.Q/'PRODUCTION.diff',a.u.gt('diff',ctx['baseline'],merged,'--',*a.PRODUCTION)+'\n')
 text(a.Q/'COMPLETE_INTEGRATION.diff',a.u.gt('diff','--stat',ctx['baseline'],merged)+'\n')
 text(a.Q/'ANCESTRY.txt',a.u.gt('log','--reverse','--format=%H %P %s',ctx['baseline']+'..'+merged)+'\n')
 (a.Q/'qa').mkdir(exist_ok=True);(a.Q/'logs').mkdir(exist_ok=True);(a.Q/'screenshots').mkdir(exist_ok=True)
 for p in (a.T/'qa').iterdir():
  if p.is_file() and p.suffix in ['.cjs','.rb','.json','.yml']:shutil.copy2(p,a.Q/'qa'/p.name)
 shutil.copy2('integration-apparatus-hold.cjs',a.Q/'qa/integration-apparatus-hold.cjs')
 for p in (a.T/'logs').glob('*.log'):shutil.copy2(p,a.Q/'logs'/p.name)
 for p in (a.T/'screenshots').glob('COMPACT-*.png'):shutil.copy2(p,a.Q/'screenshots'/p.name)
 for n in ['THEME-final-1-1440-light.png','THEME-final-2-1440-dark.png','THEME-final-15-390-light.png','THEME-final-16-390-dark.png']:shutil.copy2(a.T/'screenshots'/n,a.Q/'screenshots'/n)
 for n in ['reader_integration.py','integration_runqa.py','integration_manifest_check.py','integration_finalize.py','postrelease_reader.py']:shutil.copy2(n,a.Q/'qa'/n)
 table='\n'.join('| '+r['path']+' | `'+r['integrated_Git_blob_SHA256']+'` |' for r in production)
 report=f'''# Canonical integration: approved reader repairs A/B/D/E

Combined certification **PASS**, with zero new regressions. A, B, D and E are repaired. Package C is **KNOWN UNRESOLVED / EDITORIAL HOLD**, not repaired or counted as passed. Public preview publication is outside this integration.

Starting canonical/local/fetched/direct remote: `{ctx['baseline']}`. Certified source `{a.SOURCE}` was clean and independently checked against its evidence and production manifest. Actual history-preserving merge: `{merged}`; parents `{merge['merge_parents'][0]}` and `{merge['merge_parents'][1]}`. No conflicts, conflict resolutions or extra production changes. The complete source history, including its baseline, implementation, editorial hold and certification commits, is preserved. VII.1 (`b48e8778b6ece616775d59a8e8949199c3ee84ef`) and VII.2–6 (`0f006764c36b36bc0cf856f6c3b11f2e4a03660c`) remain ancestors. See ANCESTRY.txt and MERGE.json. This evidence-only certification commit does not change the tested production build. Final canonical, fetched and directly verified remote commit and normal push output are sealed after promotion in `{a.T / 'INTEGRATION_RECEIPT.json'}`.

| Package | Actual merged-reader disposition |
|---|---|
| A | PASS: named native Dark mode button, keyboard focus and Enter/Space, actual pressed state, persistence, desktop/mobile light and dark rendering (18 assertions). |
| B | PASS: unique visible `reader-annotations`, correct selectors/MDB disclosure; unchanged original TEI `annotations`, notes, highlighting and pane content. All sampled Antiquities views have unique document IDs. |
| C | KNOWN UNRESOLVED, editorial HOLD: original 3 links and 2 malformed 404 targets independently reproduced and unchanged; no guessed targets, substitute annotations or XML edits. Literal original unresolved-reference register retained. |
| D | PASS: Home, About, Background startup and actual navigation; original baseline languages TypeErrors independently reproduced, absent after integration, body content identical. |
| E | PASS: 21 positive/negative/transition assertions; invalid URLs remain invalid and unchanged, accessible explanatory notices, real Proem 1/I.27 links, no substituted passage. Supported corpus unchanged. |

Fresh native Jekyll builds were made for frozen canonical and merged source. No old generated build was copied; dependencies were not upgraded. The established image-plugin policy and loopback configuration were retained. Chrome used independent profiles, ports and downloads. All 251 integrated asset hashes match the certified source build, including renderer `{certificate['renderer_SHA256']}`. Source and build digests are in PRODUCTION_MANIFEST.json. The exact eight-file source delta is PRODUCTION.diff; there were no preview release-marker, CNAME, domain or publication changes.

The first evidence-sealing attempt stopped on a manifest field-name mismatch (`status` versus the actual `result` field). This orchestration-only error was corrected and retained in ORCHESTRATION_ATTEMPTS.json. It occurred after the successful browser suites and before any canonical promotion; no production change or rerun of passing browser tests was required.

| Fresh combined regression | Result |
|---|---|
| Antiquities Niese | 7,376/7,376 (26 Proem + 7,350 I–XX), before/after; all 22,128 complete language-pane DOM/text/IDs/type/notice comparisons identical; no errors or duplicate IDs. |
| Traditional extent equivalents | 1,689/1,689 |
| Bamberg extent equivalents | 198/198 |
| Alignment extent equivalents | 1,441/1,441 |
| Book / contents configurations | 21/21 |
| Cross-work Niese | 8,002/8,002 |
| Cross-work structural | 1,630/1,630 |
| Actual containing-view controls / document IDs | 16/16 each, separately executed UI tests |
| Source preservation | 143 XML and 159 protected XML/data/registry inputs exact; 5,158/5,166 baseline files unchanged, eight approved production files changed. |

The exhaustive Niese replay is uninstrumented and uses real menu selections and real URL identities. Structural and cross-work suites exercise the actual production selector/extent/rendering code with getter-only access and complete source input, comparing DOM/text with the independently built baseline; these totals are not represented as individual public browser clicks. Separate uninstrumented tests cover real direct/reload/back/forward/previous/next, keyboard, pane/source switching, note disclosure, themes and containing views.

Positive full-source Whiston assertions pass for VII.1–7 and internal composites VII.1–6/VII.2–6, including reordered/repeated identities and adjacent distinct paragraphs. Existing wording, punctuation, source IDs and qualifications are preserved; each physical paragraph appears once within a selection. VII.5–6 retain the complete sentence-spanning paragraph. Whiston remains contextual, not word-exact Niese segmentation. No new public range URL or public range control is claimed.

Protected cases pass: all 26 Proem identities, repeated §25/26 and transition I.27; XI.312/.326/.342 logical fragments and Bellum IV.105 attachments with Book/Alignment physical order protected by exact structural comparison; XVI–XVII fragments and reciprocal qualifications; XVIII.216–217 Greek/context with explicit Latin unavailability; XX.27–36/238, final §268 separate full trailer through AMEN, no Vita and no supported §269. Bellum/Cardwell/Whiston/Lodge, DEH and Contra Apionem panes and source switching are preserved. See PROTECTED_CONTROLS.json and the complete pane-comparison matrix.

Only specific independently reproduced residuals remain: Package C at `/antiquities/?book=1&bamberg=5` (three original links, two unchanged 404 targets) and the Bellum Book-I source-source `header` ID collision at `/bellum-judaicum/?book=1`. Before integration Bellum duplicates were `annotations` and `header`; after, only the inherited `header` remains. This is not a claim of global duplicate-ID freedom for every work. Fresh supported-selection/general-page/navigation suites have zero new page, console or network errors; deliberate visits to the two C 404 destinations are recorded separately. No blanket baseline error waiver is applied.

Exact production hashes (Git bytes and isolated working/build bytes verified):

| Production source file | SHA-256 |
|---|---|
{table}

Recommend canonical promotion of A/B/D/E. Package C requires independent apparatus recovery and editorial authorization, and is not a blocker to these authorized maintenance fixes. The public preview remains `{ctx['preview']}`; publishing these repairs requires a separate publication task. Final promotion/ref/cleanliness checks are recorded in the external integration receipt.
'''
 text(a.Q/'INTEGRATION_REPORT.md',report)
 text(a.Q/'REPRODUCE.md',f'''# Reproduction and evidence

The certified actual merged production commit is `{merged}`, frozen baseline `{ctx['baseline']}`, entire source tip `{a.SOURCE}`. Production diff and exact source/build hashes are local and in PRODUCTION_MANIFEST.json. Full results are INTEGRATION_CERTIFICATE.json, NIESE_MATRIX.csv (22,128 language records), fresh raw baseline/candidate JSON gzip captures, focused JSON and logs. Source-derived expectations and existing provenance are preserved in qa and in the complete source-branch review history.

Actual test runtime: `{a.T}`; isolated source: `{a.W}`. Exact native builder and config are `qa/build.rb`, `qa/local.yml`; actual frozen output is `baseline-site` and merged output `candidate-final-site`. Do not replace either with a later build when reproducing these records. Tests start their own loopback servers and isolated Chrome profiles. `PLAYWRIGHT_MODULE={a.u.PW}`, `REPAIR_RUNTIME={a.T}`, `REPAIR_ROOT={a.W}`. The exact executed script paths, argument arrays, script hashes and outputs appear in QA_JOB_baseline/niese/structural/focused.json; execute them with `{a.u.NODE}` using runtime `qa` as working directory. Use a fresh QA_RUN_SUFFIX for each repeat. All copied test scripts and expected inputs are included in qa.

The standalone `qa/integration-apparatus-hold.cjs` independently rebuild-baseline checks the three Book-I Bamberg5 source references, actual two 404 responses, and exact unchanged final targets. Package C stays on HOLD. Its permanent source packet is UNRESOLVED_REFERENCES.md/json and must not be replaced with guessed mappings.

Internal combined-context tests deliberately expose production getters, not new public range controls. Structural/cross-work counts are complete extent/rendered equivalents, not claims of 20,000 individual GUI clicks. Niese and all focused browser checks use the unmodified served build.

The authoritative post-push receipt is `{a.T/'INTEGRATION_RECEIPT.json'}`. No preview deployment is authorized by these reproduction instructions.
''')
 index='\n'.join('- ['+p.name+'](screenshots/'+p.name+')' for p in sorted((a.Q/'screenshots').glob('*.png')))
 text(a.Q/'EVIDENCE_INDEX.md',f'''# Independent combined integration evidence

All evidence here was captured on fresh baseline/merged builds in this task. Original certified-source evidence remains intact in its own history. Complete machine-readable comparisons are NIESE_MATRIX.csv, baseline-NIESE.json.gz, candidate-final-NIESE.json.gz and source/build manifests. Logs and exact executed scripts/input expectations accompany the results. The external receipt identifies final canonical and directly verified remote refs.

APPARATUS_HOLD_COMPARISON.json records independent baseline/final C reproduction; UNRESOLVED_REFERENCES.md/json is the preserved literal editorial hold packet. PACKAGE_final_final.json records original notes/pane equality and the inherited Bellum header duplicate. COMPACT_EVIDENCE.json captures the independently reproduced baseline Home and invalid-I.1 errors; those are absent after repair. GENERAL_NAVIGATION.json additionally reproduces all three original general-page errors and unchanged body content. THEME_FINAL.json records actual keyboard, names/pressed state, responsive appearance and persistence. PROTECTED_CONTROLS.json records protected text/notice/trailer assertions, not mere HTTP status checks.

Compact viewport collections and four theme/presentation images are retained below. Large full-Book captures and browser profiles remain solely in the isolated runtime. Visually reviewed the descriptive invalid-I.1 notice/empty panes and mobile dark-mode keyboard focus screenshot; browser checks also verify desktop/mobile light/dark appearance.

{index}
''')
 evidence=[{'path':p.relative_to(a.W).as_posix(),'SHA256':a.u.sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(a.Q.rglob('*')) if p.is_file() and p.name!='EVIDENCE_MANIFEST.json']
 a.u.save(a.Q/'EVIDENCE_MANIFEST.json',{'UTC':a.u.now(),'files':evidence})
 a.u.save(a.T/'checkpoints/QA_COMPLETE.json',{'UTC':a.u.now(),'promotion_gate':'PASS','certificate_SHA256':a.u.sha((a.Q/'INTEGRATION_CERTIFICATE.json').read_bytes()),'production':production,'source_unchanged':True,'commit_pending':True})
 with zipfile.ZipFile(a.T/'checkpoints/QA_COMPLETE.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(a.Q.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(a.Q).as_posix())
 a.run('add','--','review/Postrelease_Reader_Repairs_Integration_2026-10-11',repo=a.W)
 staged=a.u.gt('diff','--cached','--name-only',repo=a.W).splitlines();assert staged and all(p.startswith('review/Postrelease_Reader_Repairs_Integration_2026-10-11/') for p in staged)
 a.run('commit','-m','Certify merged reader repairs A B D E; preserve apparatus editorial hold',repo=a.W)
 final=a.u.gt('rev-parse','HEAD',repo=a.W);assert not a.u.state(a.W)['status'];assert a.u.gt('diff','--name-only',merged,final,'--',':(exclude)review/')==''
 check_production(final)
 a.u.save(a.T/'CERTIFIED_INTEGRATION.json',{'UTC':a.u.now(),'certification_commit':final,'tested_merge':merged,'baseline':ctx['baseline'],'source':a.SOURCE,'branch':a.BR,'production':production,'certificate_SHA256':a.u.sha((a.Q/'INTEGRATION_CERTIFICATE.json').read_bytes()),'integration_clean':True,'state':'Certified and ready for final fresh canonical check/promotion'})
 print(json.dumps({'gate':'PASS','certification_commit':final,'Niese':7376,'traditional':1689,'bamberg':198,'alignment':1441,'cross_Niese':8002,'cross_structural':1630,'XML_unchanged':143,'C':'EDITORIAL HOLD'}),flush=True)

def promote():
 ctx=a.saved();cert=a.u.load(a.T/'CERTIFIED_INTEGRATION.json');final=cert['certification_commit']
 assert a.u.state(a.W)['HEAD']==final and not a.u.state(a.W)['status']
 check_production(final)
 assert a.u.state(a.S)=={'HEAD':a.SOURCE,'branch':'fix/postrelease-reader-a11y-ids-links-startup-20261011','status':''}
 a.fetch();canonical=a.u.state();fetched=a.u.gt('rev-parse','origin/v2-development');direct=a.u.gt('ls-remote','origin','refs/heads/v2-development').split()[0]
 gate={'UTC':a.u.now(),'canonical':canonical,'fetched_remote':fetched,'direct_remote':direct,'certified_integration':final,'baseline':ctx['baseline']};a.u.save(a.T/'PRE_PROMOTION.json',gate)
 assert canonical['HEAD']==fetched==direct==ctx['baseline'] and canonical['branch']=='v2-development' and not canonical['status'],'Canonical drift/user work: preserve integration; reconcile in isolation and repeat final QA before promotion'
 assert a.ancestor(ctx['baseline'],final) and a.ancestor(a.SOURCE,final)
 a.u.save(a.T/'PROMOTION_STARTED.json',{'UTC':a.u.now(),'before':canonical,'certification_commit':final,'normal_push_only':True})
 for name,args in [('FAST_FORWARD',['merge','--ff-only',final]),('NORMAL_PUSH',['push','origin','v2-development'])]:
  r=subprocess.run(['git',*args],cwd=a.R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  text(a.T/'logs'/('PROMOTION-'+name+'.log'),r.stdout.decode(errors='replace'))
  a.u.save(a.T/(name+'.json'),{'UTC':a.u.now(),'arguments':args,'exit_code':r.returncode,'output':r.stdout.decode(errors='replace')})
  assert r.returncode==0,'Safe promotion/push did not complete; preserve non-destructive state and inspect '+name
 verify()

def verify():
 ctx=a.saved();cert=a.u.load(a.T/'CERTIFIED_INTEGRATION.json');final=cert['certification_commit'];a.fetch()
 canonical=a.u.state();fetched=a.u.gt('rev-parse','origin/v2-development');direct=a.u.gt('ls-remote','origin','refs/heads/v2-development').split()[0]
 assert canonical['HEAD']==fetched==direct==final and canonical['branch']=='v2-development' and not canonical['status']
 required=[a.SOURCE,'951555f41c4fda1e21f7615b4a125f7036b3b55f','b48e8778b6ece616775d59a8e8949199c3ee84ef','0f006764c36b36bc0cf856f6c3b11f2e4a03660c',ctx['baseline']]
 ancestry={c:a.ancestor(c,fetched) for c in required};assert all(ancestry.values())
 production=[]
 for r in cert['production']:
  p=r['path'];blob=a.u.sha(git_blob(fetched,p));working=a.u.sha((a.R/p).read_bytes());assert blob==r['integrated_Git_blob_SHA256'];assert working==blob,p
  production.append({**r,'fetched_remote_Git_blob_SHA256':blob,'canonical_working_SHA256':working,'direct_remote_verified_commit':direct})
 protected=a.u.load(a.T/'PROTECTED_INPUTS.json')['files'];protected_remote=[]
 for r in protected:
  h=a.u.sha(git_blob(fetched,r['path']));assert h==r['SHA256']==a.u.sha((a.R/r['path']).read_bytes());protected_remote.append({'path':r['path'],'SHA256':h})
 assert a.u.state(a.W)=={'HEAD':final,'branch':a.BR,'status':''}
 assert a.u.state(a.S)=={'HEAD':a.SOURCE,'branch':'fix/postrelease-reader-a11y-ids-links-startup-20261011','status':''}
 assert a.u.gt('rev-parse','fix/postrelease-reader-a11y-ids-links-startup-20261011')==a.SOURCE
 start=a.u.load(a.T/'START.json');preview=a.u.gt('ls-remote','https://github.com/LatinJosephus/LatinJosephus.github.io.git','refs/heads/main').split()[0];assert preview==ctx['preview']
 for key,repo in [('preview_original','C:/workspace/LatinJosephus-Antiquities-Final-Preview-Publication-20261010'),('preview_publication','C:/workspace/LatinJosephus-Antiquities-VII1-6-Preview-Publication-20261011')]:assert a.u.state(Path(repo))==start[key]
 worktrees=a.u.protected();current={r['worktree']:r for r in worktrees};drift=[]
 for old in start['other_worktrees']:
  if Path(old['worktree']).resolve()==a.R.resolve():continue
  now=current.get(old['worktree']);
  if now!=old:drift.append({'before':old,'after':now})
 assert not drift,'Unexpected other-worker checkout drift; record and attribute before declaring preservation'
 diff=a.u.gt('diff','--name-only',ctx['baseline'],fetched,'--',':(exclude)review/').splitlines();assert sorted(diff)==a.PRODUCTION
 assert not a.u.gt('ls-tree','-r','--name-only',fetched,'.github/workflows'),'Inspect workflows before certifying no deployment trigger'
 receipt={'UTC':a.u.now(),'status':'CANONICAL INTEGRATED — NORMAL PUSH DIRECTLY VERIFIED','start_canonical_local':start['canonical']['HEAD'],'start_canonical_fetched_remote':start['fetched_remote'],'start_canonical_direct_remote':start['direct_remote'],'final_canonical_commit':final,'final_fetched_origin_v2_development':fetched,'final_direct_ls_remote_v2_development':direct,'certified_source_tip':a.SOURCE,'source_branch_preserved':True,'tested_merge':cert['tested_merge'],'merge_parents':a.u.load(a.T/'MERGE.json')['merge_parents'],'certification_commit':final,'ancestry':ancestry,'complete_source_history_preserved':True,'conflicts':[],'additional_production_reconciliation':[],'production':production,'protected_remote_inputs':protected_remote,'protected_XML_unchanged':143,'protected_inputs_unchanged':159,'baseline_manifest_count':5166,'baseline_files_unchanged':5158,'regression':{'Niese':7376,'Proem':26,'Books_I_XX':7350,'traditional':1689,'bamberg':198,'alignment':1441,'Book_contents':21,'cross_work_Niese':8002,'cross_work_structural':1630,'new_regressions':0},'packages':{'A':'PASS','B':'PASS','C':'KNOWN UNRESOLVED — EDITORIAL HOLD','D':'PASS','E':'PASS'},'inherited_Bellum_header_duplicate':'Independently reproduced, preserved, out of scope','canonical_status':canonical,'integration_status':a.u.state(a.W),'certified_source_status':a.u.state(a.S),'other_worktrees_unchanged':True,'other_worktree_states':worktrees,'public_preview_before':ctx['preview'],'public_preview_after_directly_verified':preview,'preview_checkouts_unchanged':True,'public_preview_deployed':False,'production_domain_unchanged':True,'no_force_push_reset_rebase_or_history_rewrite':True,'normal_push':a.u.load(a.T/'NORMAL_PUSH.json'),'fast_forward':a.u.load(a.T/'FAST_FORWARD.json'),'report':str(a.Q/'INTEGRATION_REPORT.md'),'certificate':str(a.Q/'INTEGRATION_CERTIFICATE.json'),'certificate_SHA256':a.u.sha((a.Q/'INTEGRATION_CERTIFICATE.json').read_bytes()),'production_manifest':str(a.Q/'PRODUCTION_MANIFEST.json'),'reproduction':str(a.Q/'REPRODUCE.md'),'rollback_reference_only':ctx['baseline'],'stopped_after_canonical_verification':True}
 a.u.save(a.T/'INTEGRATION_RECEIPT.json',receipt)
 text(a.T/'FINAL_HANDOFF.md',f'''# Final canonical integration handoff

Final canonical, fetched origin/v2-development and directly verified remote commit: `{final}`. Normal non-force push succeeded. Entire certified source `{a.SOURCE}` retained in merge ancestry. Integration and original source/canonical worktrees clean; all other original worktrees unchanged. Public preview remains `{preview}` and was not deployed.

Combined fresh certification: 7,376 Niese, 1,689 traditional, 198 Bamberg, 1,441 Alignment, 21 Book/contents, 8,002 cross-work Niese and 1,630 cross-work structural comparisons passed, with zero new regressions. 143 XML/159 protected inputs preserved. Exactly eight approved production files changed; remote blobs and canonical working bytes match the tested hashes. Package C remains KNOWN UNRESOLVED / EDITORIAL HOLD; inherited Bellum header duplicate unchanged.

Report: `{a.Q/'INTEGRATION_REPORT.md'}`. Certificate: `{a.Q/'INTEGRATION_CERTIFICATE.json'}`. Exact production/build hashes: `{a.Q/'PRODUCTION_MANIFEST.json'}`. Authoritative receipt: `{a.T/'INTEGRATION_RECEIPT.json'}`.
''')
 a.u.save(a.T/'checkpoints/PUSH_VERIFIED.json',{'UTC':a.u.now(),'final_commit':final,'receipt_SHA256':a.u.sha((a.T/'INTEGRATION_RECEIPT.json').read_bytes()),'preview':preview,'canonical_clean':True,'integration_clean':True,'source_clean':True})
 print(json.dumps({'status':receipt['status'],'final_canonical_and_direct_remote':final,'source_ancestry':a.SOURCE,'all_clean':True,'preview_unchanged':preview,'receipt':str(a.T/'INTEGRATION_RECEIPT.json')}),flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
