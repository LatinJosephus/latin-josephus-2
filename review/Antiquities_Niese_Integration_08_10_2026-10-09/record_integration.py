"""Archive only the additional canonical integration verification.
No production changes or edits to historical certification packets.
"""
import pathlib,json,hashlib,subprocess,shutil
T=pathlib.Path(__file__).resolve().parent
C=pathlib.Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
P=C/'review/Antiquities_Niese_Integration_08_10_2026-10-09'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def git(*a):return subprocess.check_output(['git','--no-optional-locks',*a],cwd=C)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
pre=read(T/'PREFLIGHT.json');q=read(T/'CANONICAL_HASH_QA.json');smoke=read(T/'CANONICAL_SMOKE_QA.json')
assert pre['result']==q['result']==smoke['result']=='PASS'
assert not git('status','--porcelain=v1')
assert git('rev-parse','HEAD').decode().strip()==pre['implementation_HEAD']
assert git('rev-parse','origin/v2-development').decode().strip()==pre['refreshed_origin']
assert any('bamberg=B78-table1-row005' in x['route'] for x in smoke['protectedURLs'])
assert not P.exists(),'Refuse to replace an existing integration packet'
P.mkdir(parents=True)
names=['PREFLIGHT.json','CANONICAL_HASH_QA.json','CANONICAL_SMOKE_QA.json','verify_integration.py','canonical-smoke.cjs','build-canonical.sh','record_integration.py']
for name in names:shutil.copyfile(T/name,P/name)
for name in ['dependencies.log','jekyll.log']:shutil.copyfile(T/'build'/name,P/name)
if (T/'CANONICAL_SMOKE_FAILURE.json').exists():
 (P/'diagnostics').mkdir();shutil.copyfile(T/'CANONICAL_SMOKE_FAILURE.json',P/'diagnostics/INITIAL_BROADER_VIEW_ASSERTION.json')
build=[]
for rel in pre['production_scope']:
 raw=git('show','HEAD:'+rel);working=(C/rel).read_bytes();assert working==raw
 if rel!='_includes/display-settings.html':assert (T/'build/canonical-site'/rel).read_bytes()==raw
 build.append({'path':rel,'certified_and_canonical_Git_SHA256':hashlib.sha256(raw).hexdigest(),'canonical_checkout_SHA256':sha(C/rel),'fresh_build_identical':rel!='_includes/display-settings.html'})
write(P/'INTEGRATION_QA.json',{'result':'PASS','canonical_before':pre['canonical_HEAD'],'canonical_after_data_integration':q['canonical_HEAD'],'implementation_source':pre['implementation_HEAD'],'method':'FAST_FORWARD','conflicts':[],'additional_production_changes':[],'additional_changes':'This review-only integration verification packet','incoming_production_files':8,'incoming_review_files':469,'incoming_scope_verified':477,'audit_checkpoint':pre['audit_checkpoint'],'approved_audit_files_preserved':381,'certification_reused':True,'sources':build,'VIII':{'selections':420,'Latin_intervals':420,'milestones':337},'X':{'selections':281,'Latin_intervals':280,'milestones':230,'Latin_unavailable':108,'Greek_English_independently_available':True},'total_Antiquities_selections':3157,'IX_disabled':True,'canonical_focused_critical_URLs':len(smoke['criticalURLs']),'protected_route_comparisons':len(smoke['protectedURLs']),'browser_exceptions':0,'console_errors':0,'request_failures':0,'origin_refreshed_before_integration':pre['refreshed_origin'],'origin_refreshed_after_smoke':git('rev-parse','origin/v2-development').decode().strip(),'public_preview_refresh_performed':False,'deployment_performed':False,'segmentation_decisions_reopened':False})
report=f'''# Antiquities VIII/X canonical integration — 9 October 2026

The certified implementation was integrated by fast-forward from `{pre['canonical_HEAD']}` to `{pre['implementation_HEAD']}`. Canonical was clean on v2-development; refreshed origin/v2-development was at the same initial commit and remained unchanged at the post-smoke refresh. No conflicts or additional production edits occurred. A separate review-only commit records this packet before the normal push; its commit ID and the final remote confirmation are provided in the completion report.

The incoming sequence is exactly the four certified commits: 7133a3e (shared reader), 6d82c77 (VIII), 43b3320 (X), 2b07ac2 (shared certification). The separate audit checkpoint fb8a65e was not added to that sequence. Its 381 preserved review files and correct references were verified byte-exactly. Both audit and implementation branches and histories remain intact.

FILE_MANIFEST.json in the historical implementation packet verifies the exact incoming scope: eight production files and 469 review files (477 total; the historical manifest excludes only itself and COMMIT_SCOPE.json from its hash list). The eight production paths are listed with committed, checkout and build hashes in INTEGRATION_QA.json. Current canonical bytes match the certified implementation. All existing source-contents, Whiston, structural registry and other source inputs remain unchanged. Historical certification files were neither rewritten nor re-run.

VIII has 420 selections and 420 represented Latin intervals (83 retained starts, 337 milestones). X has 281 selections, 280 represented Latin intervals (50 retained starts, 230 milestones), and the independently addressable Latin absence state at 108. X.108 borrows no 109 Latin and retains Greek and broader English. The four inherited-label exceptions, VIII.367–369, X.101–102, X.150–151 and X.276–277 retain their exact certified identity, text, order and qualifications. The cumulative Antiquities Niese total is 3,157; IX remains disabled. No editorial decision was reopened.

A fresh canonical Jekyll build succeeded in the dedicated local build directory, with the canonical source mounted read-only. Built production hashes match certification. Focused smoke tests check all new-book menu and executable identity counts, 26 critical uninstrumented URLs, qualification/absence notices, reload, rendered previous/next and history, panes and themes. Fifteen protected canonical-versus-certified three-language DOM comparisons cover earlier Antiquities Niese, traditional ranges, XI multi-span, Alignment, registered Bamberg, Latin/Greek source contents including Latin XIV supplied headings, Whiston/Lodge, Bellum chapter ranges, DEH and Contra Apionem. Lodge marginal-note toggling also passes. There are zero browser exceptions, console errors or failed requests.

All 337 VIII and 230 X new internal milestones remain present once in Chapter ranges. All X markers and 328 VIII markers remain present once in applicable Subchapter ranges. The other nine VIII markers (237–245) belong to VIII.ix, which has no registered printed lower subdivisions and correctly remains Chapter-only. The initial smoke assertion assumed universal Subchapter coverage; it was corrected to respect that certified structure, without modifying production. Its diagnostic is retained separately.

Unchanged full certification is retained: all 701 new section renderings, complete narrative partitions and byte reversals; 2,456 prior Antiquities selections, 5,034 traditional displays/33 unavailable states, 198 Bamberg identities/594 displays, 1,441 Alignment units, all source contents/TOCs, 4,001 Bellum citations in both English sources and other protected behavior. The integration smoke is additional evidence on the fresh canonical build, not a claim to have repeated the entire suite.

Only this integration review packet is added beyond the certified incoming diff. No cosmetic repair, further book segmentation, public-preview refresh or deployment was performed. The build remains at C:\\workspace\\Antiquities-Niese-Integration-08-10-2026-10-09\\build\\canonical-site. Reproduce the focused checks with build-canonical.sh, verify_integration.py canonical and canonical-smoke.cjs; they read the canonical source and retained certified build. The normal push targets only origin/v2-development and must preserve any remote advance.
'''
(P/'REPORT.md').write_text(report,encoding='utf8',newline='\n')
paths=[p for p in sorted(P.rglob('*')) if p.is_file()]
write(P/'FILE_MANIFEST.json',{'scope':'ADDITIONAL_REVIEW_ONLY_CANONICAL_INTEGRATION_EVIDENCE','self_excluded':True,'files':[{'path':str(p.relative_to(C)).replace('\\','/'),'sha256':sha(p),'bytes':p.stat().st_size} for p in paths]})
paths.append(P/'FILE_MANIFEST.json');spec=T/'integration-review-paths.nul';spec.write_bytes(b'\0'.join(str(p.relative_to(C)).replace('\\','/').encode() for p in paths)+b'\0')
(T/'integration-commit.txt').write_text('Verify canonical Antiquities VIII and X integration\n\nRecord the clean fast-forward from a480215 to certified 2b07ac2, exact eight-production/469-review incoming scope and byte-preserved fb8a65e audit provenance. Retain the unchanged full certification and add focused checks from a fresh canonical build: all section identities, 26 critical URLs, 15 protected routes, complete applicable broader-view milestone coverage and independent X.108 language handling.\n\nReview-only additional evidence; no production edits, reopened segmentation, cosmetic repairs, public-preview refresh or deployment. Normal push to origin/v2-development is authorized after checks.\n',encoding='utf8',newline='\n')
print('Additional exact review scope:',len(paths),'files; no production changes')
