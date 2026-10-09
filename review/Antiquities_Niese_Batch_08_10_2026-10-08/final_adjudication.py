"""Freeze approved VIII/X review plans. Writes review artifacts only; no Git mutation.
The prior scripts and NO-GO observations are historical checkpoints.
"""
import pathlib,json,hashlib,subprocess,collections,csv,sys
P=pathlib.Path(__file__).resolve().parent;W=P.parents[1]
sys.path.insert(0,str(W/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book
def sha(x):return hashlib.sha256(x).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def md(p,x):p.write_text(x.rstrip()+'\n',encoding='utf8',newline='\n')
def git(*a):return subprocess.check_output(['git','--no-optional-locks',*a],cwd=W)
authorization={'authority':'Direct user approval and implementation authorization, 2026-10-08','scope':'Isolated implementation worktree, local certification and local commits','canonical_integration':False,'push':False,'public_deployment':False}
results={}
for b,roman,count,inh,internal in [(8,'VIII',420,83,337),(10,'X',281,50,230)]:
 d=W/f'review/Antiquities_Niese_Book{roman}_2026-10-08'
 for name in ['REVIEW_CASES.md','REPORT.md','BOUNDARIES.json','QA.json','INSERTION_PLAN.json']:
  backup=d/('PRE_FINAL_'+name)
  if not backup.exists():backup.write_bytes((d/name).read_bytes())
 rows=read(d/'PRE_FINAL_BOUNDARIES.json');baseline=read(d/'BASELINE.json')
 for item in baseline['inputs'].values():assert sha((W/item['path']).read_bytes())==item['worktree_before_sha256']
 books={lang:Book(W/f'assets/xml/antiquities/{lang}/book-{b:02}.xml') for lang in ['Greek','Latin']}
 assert len(rows)==count
 for r in rows:
  r['local_implementation_authorization']=authorization;r['implementation_approved']=True;r['apply_permitted']=True;r['outstanding_editorial_decision']=False
  if b==10 and r['niese'] in [102,276]:
   n=r['niese'];r['pre_final_editorial_state']={k:r.get(k) for k in ['classification','confidence','availability','verification_reason','verification_work_state','human_decision','current_verification_category','editorial_case_status']}
   r['classification']='INTERNAL-BUT-EXACT';r['confidence']='EDITORIALLY_ADJUDICATED_WITH_RECORDED_LIMITS';r['human_decision']={'authority':authorization['authority'],'scope':'FINAL_EDITORIAL_DECISION_AND_LOCAL_IMPLEMENTATION','production_application_authorized':True,'canonical_integration_authorized':False}
   r['verification_work_state']='FINAL_EDITORIALLY_ADJUDICATED';r['current_verification_category']='GREEK_RESOLVED_LATIN_COUNTERPART_SECURE';r['editorial_case_status']='RESOLVED';r['latin_individual_verification_status']='REVIEWED_AND_EDITORIALLY_RESOLVED'
   if n==102:
    r['verification_reason']='Approved first identifiable surviving counterpart: nomine sedechiam. Leave simulet ioachim with 101 exactly as transmitted. The opening imprisonment and uncle details in Greek 102 are not explicitly recoverable in the Latin. No reconstruction; prior cut retained in history.'
    r['availability']='PRESENT_WITH_RECORDED_ALIGNMENT_LIMITS'
   else:
    r['verification_reason']='Approved partial correspondence: retain Et haec at 276 and quae omnia at 277. The concluding Greek notice of Roman rule and devastation has no identifiable counterpart in this transcription; cause undetermined. 276 remains available. No supplementation or automatic gap.'
    r['availability']='PARTIAL_CORRESPONDENCE';r['representation_question']='Resolved by direct editorial approval; partial correspondence, available.'
  if b==10 and r['niese']==18:
   r['verification_reason']='Before Turbatur: the letter, reassurance, siege and news of Ethiopian relief. After the cut: Sennacherib response, ritual/restoration material and resumed Vulcan/Pelusium account. The complete 18 interval is within latin-book10-num15; pb n=115r and cb n=1/2 are manuscript page/column markers, not paragraph boundaries. Preserve all material through the 19 cut.'
  if b==10 and r['niese']==108:
   r['verification_reason']='Unavailable in this transcription: Greek 108 describes maintaining the Babylonian alliance for eight years, repudiating its pledges and turning to the Egyptians in hope of overcoming Babylonian power. That section has no identifiable Latin counterpart. Cause undetermined. Later Egyptian material survives (including after 109); it is not all absent. Preserve the visible [VII.iii.108], which must not assert executable 108, and begin surviving 109 at Interea dum hoc cognouisset.'
  for lang,key in [('Greek','greek_locator'),('Latin','latin_locator')]:
   if loc:=r[key]:assert books[lang].locate(loc['book_offset'])==loc
 # Accepted starts did not change; ensure both complete partitions again.
 for lang,key,section,endkey in [('Greek','greek_locator','greek_section','candidate_greek_end_book_offset'),('Latin','latin_locator','candidate_latin_section','candidate_latin_end_book_offset')]:
  positioned=[r for r in rows if r[key]];s=books[lang].stream;pieces=[]
  for i,r in enumerate(positioned):
   at=r[key]['book_offset'];end=positioned[i+1][key]['book_offset'] if i+1<len(positioned) else len(s);assert at<end;r[endkey]=end;r[section]=s[at:end];pieces.append(r[section])
  assert s[:positioned[0][key]['book_offset']]+''.join(pieces)==s
 assert sum(r.get('inherited_start_retained',False) for r in rows if r['latin_locator'])==inh
 insertions=[{'niese':r['niese'],'locator':r['latin_locator'],'marker':f'<milestone unit="niese" n="{r["niese"]}"/>'} for r in rows if r['latin_locator'] and not r['inherited_start_retained']];assert len(insertions)==internal
 write(d/'BOUNDARIES.json',rows)
 cols=['book','niese','classification','confidence','availability','placement','latin_anchor_phrase','latin_paragraph_id','latin_locator','greek_locator','candidate_latin_end_book_offset','verification_reason','outstanding_editorial_decision','implementation_approved']
 with (d/'BOUNDARIES.tsv').open('w',encoding='utf8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=cols,delimiter='\t');writer.writeheader()
  for r in rows:writer.writerow({k:json.dumps(r.get(k),ensure_ascii=False) if isinstance(r.get(k),(dict,list)) else r.get(k) for k in cols})
 proposals=read(d/'ADJUDICATED_GREEK_PROPOSALS.json')
 proposals['status']='APPROVED_LOCAL_IMPLEMENTATION_UNAPPLIED';proposals['authorization']=authorization
 for p in proposals['proposals']:p['candidate_adjudicated']=True;p['production_application_authorized']=True;p['applied']=False
 write(d/'ADJUDICATED_GREEK_PROPOSALS.json',proposals)
 ids=read(d/'EXECUTABLE_IDENTITIES.json');ids['status']='APPROVED_LOCAL_IDENTITY_PLAN_UNAPPLIED';ids['authorization']=authorization
 for i,r in zip(ids['identities'],rows):i.update(availability=r['availability'],classification=r['classification'],implementation_approved=True)
 write(d/'EXECUTABLE_IDENTITIES.json',ids)
 write(d/'INSERTION_PLAN.json',{'status':'APPROVED_LOCAL_IMPLEMENTATION_UNAPPLIED','book':b,'authorization':authorization,'audit_input_sha256':baseline['inputs']['Latin']['worktree_before_sha256'],'target_source_hash_and_newline_revalidation_required':True,'approved_insertions':insertions,'approved_greek_proposals':'ADJUDICATED_GREEK_PROPOSALS.json','identity_plan':'EXECUTABLE_IDENTITIES.json','apply_permitted':True,'production_files_changed_in_audit_branch':0})
 q=read(d/'PRE_FINAL_QA.json');q.update(GO=True,implementation_approved=True,status='EDITORIALLY_APPROVED_NOT_YET_IMPLEMENTED_OR_CERTIFIED',editorial_questions=[],routine_pending=[],routine_reviewed=317 if b==8 else 224,routine_secure=317 if b==8 else 224,routine_new_questions=[],unresolved_editorial_decisions=0,current_verification_categories=dict(collections.Counter(r['current_verification_category'] for r in rows)),classifications=dict(collections.Counter(r['classification'] for r in rows)),local_implementation_authorization=authorization)
 q['classification_crosstab']={p:dict(collections.Counter(r['classification'] for r in rows if r['placement']==p)) for p in ['INHERITED_START','PROPOSED_INTERNAL_MILESTONE','NO_LATIN_START']};q['confidence_crosstab']={p:dict(collections.Counter(r['confidence'] for r in rows if r['placement']==p)) for p in ['INHERITED_START','PROPOSED_INTERNAL_MILESTONE','NO_LATIN_START']}
 q['proposed_partial_correspondence']=[];q['partial_correspondence']=[276] if b==10 else []
 for name in ['QA.json','ADJUDICATION_QA.json','AUDIT_RESULT.json']:write(d/name,q)
 write(d/'CONFIDENCE_CROSSTAB.json',{'status':'FINAL_ADJUDICATED_APPROVED_PLAN','classification':q['classification_crosstab'],'confidence':q['confidence_crosstab'],'historical_classification':read(d/'CONFIDENCE_CROSSTAB.json')['historical_classification']})
 c=read(d/'COLLATION_SUMMARY.json');c.update(status='FINAL_ADJUDICATED_APPROVED_PLAN',human_decisions_pending=[],classification_counts=q['classifications'],current_verification_categories=q['current_verification_categories'],placement_classification_crosstab=q['classification_crosstab'],placement_confidence_crosstab=q['confidence_crosstab']);write(d/'COLLATION_SUMMARY.json',c)
 write(d/'FINAL_DECISIONS.json',{'authorization':authorization,'outstanding_routine_checks':0,'outstanding_editorial_decisions':0,'new_final_decisions':[r for r in rows if b==10 and r['niese'] in [102,276]],'X18_actual_paragraph_check':'One existing paragraph, latin-book10-num15, manuscript page/column markers only.' if b==10 else None,'historical_NO_GO_records':'PRE_FINAL_* files, printed_checkpoint_state, pre_final_editorial_state, original audit commits','certified':False})
 review=f'''# Book {roman}: final adjudicated segmentation plan

**Approved for isolated local implementation and certification; not yet implemented or certified. Canonical integration, push and deployment remain unauthorized.**

Outstanding routine Latin checks: **0**. Outstanding editorial decisions: **0**. Inventory: **{count} = {inh} retained inherited starts + {internal} internal starts{ ' + unavailable 108' if b==10 else ''}**.

All prior accepted decisions and source qualifications remain operative. `PRE_FINAL_REVIEW_CASES.md` preserves the preceding unresolved packet as history; the current operative register is BOUNDARIES.json and the approved plans are INSERTION_PLAN.json, ADJUDICATED_GREEK_PROPOSALS.json and EXECUTABLE_IDENTITIES.json. Historical NO-GO records remain history, not current permission state. Printed marginal position, Loeb control and editorial word choice remain distinct, particularly VIII.110, 172 and 368. VIII.376–377 retain the independently controlled sequence.

'''
 if b==8:review+='VIII.367 is available through **et quae displucuerint sola relinquerent**, with its absent main embassy narrative and undetermined cause recorded. VIII.368 begins **Achab itaque secunda legatione**; VIII.369 uses the first repeated **nunc inquit denuo missa legatione**, preserving both repetitions and the later recap. No supplied text or automatic gap.\n'
 else:
  for n in [102,108,276,18]:review+=f'## X.{n} — resolved\n\n'+rows[n-1]['verification_reason']+'\n\n'
  review+='X.101–102 Latin: '+rows[100]['candidate_latin_section']+' **⟦102⟧** '+rows[101]['candidate_latin_section']+'\n\nX.276–277 Latin: **⟦276⟧** '+rows[275]['candidate_latin_section']+' **⟦277⟧** '+rows[276]['candidate_latin_section']+'\n'
 md(d/'REVIEW_CASES.md',review);md(d/'REPORT.md',review+'\nSource XML is unchanged on the audit branch. Exact source hashes remain in BASELINE.json. The implementation must compare actual current-canonical Git blobs and target newline/encoding before regenerating target byte locators. Local certification results will be a separate implementation packet.\n')
 md(d/'REPRODUCE.md','The final approved plan is frozen by final_adjudication.py. Run it only on the audit checkpoint with unchanged audit input hashes. Earlier generators reproduce historical NO-GO states; use a separate historical checkout for them. Implementation must regenerate byte locators against its own pinned actual target bytes.\n')
 write(d/'VERIFICATION_OBSTACLES.json',{'routine_verification_obstacles':[],'editorial_decisions_pending':[],'local_implementation_authorized':True,'canonical_integration_authorized':False,'source_provenance_qualification':'The earlier source/master search and printed authority record remain unchanged. No duplicate was substituted.','implementation_certification_pending':True})
 md(d/'ARTIFACT_STATUS.md','Current operative files: BOUNDARIES, QA, AUDIT_RESULT, COLLATION_SUMMARY, CONFIDENCE_CROSSTAB, INSERTION_PLAN, ADJUDICATED_GREEK_PROPOSALS, EXECUTABLE_IDENTITIES, FINAL_DECISIONS and REPORT/REVIEW_CASES. Local implementation and certification are approved, but not yet performed. PRE_FINAL_* files and earlier checkpoint artifacts preserve historical NO-GO states. Earlier scripts target those historical states and must not overwrite this final freeze. Source and print provenance, original candidates and all accepted evidence are retained unchanged.\n')
 results[str(b)]={k:q[k] for k in ['expected_sections','inherited_candidate_starts','proposed_milestones','unavailable','partial_survival','partial_correspondence','classifications','unresolved_editorial_decisions']}
write(P/'FINAL_ADJUDICATION.json',{'status':'APPROVED_LOCAL_IMPLEMENTATION_UNAPPLIED','authorization':authorization,'books':results,'new_Latin_milestones':567,'represented_Latin_intervals':700,'unavailable_Latin_sections':[{'book':10,'niese':108}],'outstanding_routine_checks':0,'outstanding_editorial_decisions':0,'production_changes_in_audit_branch':[],'audit_parent_HEAD':git('rev-parse','HEAD').decode().strip()})
for name in ['REPORT.md','ADJUDICATION_SUMMARY.md']:
 p=P/name;backup=P/('PRE_FINAL_'+name)
 if not backup.exists():backup.write_bytes(p.read_bytes())
 md(p,'# VIII/X final adjudicated review checkpoint\n\nApproved for isolated local implementation, certification and local commits. Canonical integration, push and deployment remain unauthorized. Zero routine checks and zero editorial decisions remain.\n\nVIII: 420 = 83 inherited + 337 internal; 367 partially survives. X: 281 = 50 inherited + 230 internal + unavailable 108; 102 and 276 retain accepted correspondence qualifications. Combined: 567 new milestones and 700 represented Latin intervals.\n\nThe audit branch contains review files only. PRE_FINAL_* artifacts and prior commits preserve historical NO-GO states and earlier proposals. FINAL_ADJUDICATION.json is the operative approval summary. Implementation will use a new worktree based on actual current canonical and must validate actual target bytes. No certification is claimed by this review checkpoint.\n')
write(P/'ADJUDICATION_SUMMARY.json',read(P/'FINAL_ADJUDICATION.json'))
md(P/'ARTIFACT_STATUS.md','FINAL_ADJUDICATION.json and FINAL_REVIEW_FILES.json govern the final approved local plan and exact review-only commit scope. The operative book registers incorporate all final decisions. Prior ADJUDICATION_VERIFICATION.json, ADJUDICATION_MODIFIED_FILES.json, follow-up QA, print summaries and PRE_FINAL_* reports describe historical states, preserved without retrospective rewriting. Existing baseline browser/regression evidence is historical; actual implementation certification must be recorded separately.\n')
md(P/'REPRODUCE.md','final_adjudication.py freezes the final approvals from PRE_FINAL_BOUNDARIES.json against pinned audit input hashes and verifies locators and partitions. It writes review files only. Previous generators reproduce earlier NO-GO checkpoints and should run only in a separate historical checkout. The future implementation must regenerate all raw-byte locators against the actual current canonical target. No script here authorizes canonical integration, push or deployment.\n')
# Exact current review scope, no production paths.
allowed=[f'review/{n}/' for n in ['Antiquities_Niese_BookVIII_2026-10-08','Antiquities_Niese_BookX_2026-10-08','Antiquities_Niese_Batch_08_10_2026-10-08']]
changed=set(git('diff','--name-only','HEAD').decode().splitlines()+git('ls-files','--others','--exclude-standard').decode().splitlines())
for prefix in allowed:changed.add(prefix+'FILE_MANIFEST.json')
changed.add((P/'FINAL_REVIEW_FILES.json').relative_to(W).as_posix());assert all(any(x.startswith(a) for a in allowed) for x in changed)
write(P/'FINAL_REVIEW_FILES.json',{'against_HEAD':git('rev-parse','HEAD').decode().strip(),'exact_paths':sorted(changed),'production_paths':[],'authorization':authorization})
for roman in ['VIII','X']:
 d=W/f'review/Antiquities_Niese_Book{roman}_2026-10-08';write(d/'FILE_MANIFEST.json',{'status':'FINAL_ADJUDICATED_APPROVED_LOCAL_PLAN','files':[{'path':f.relative_to(d).as_posix(),'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size} for f in sorted(d.rglob('*')) if f.is_file() and f.name!='FILE_MANIFEST.json']})
write(P/'FILE_MANIFEST.json',{'status':'FINAL_ADJUDICATED_REVIEW_ONLY_CHECKPOINT','files':[{'path':f.relative_to(W).as_posix(),'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size} for prefix in allowed for f in sorted((W/prefix).rglob('*')) if f.is_file() and f!=P/'FILE_MANIFEST.json']})
actual=set(git('diff','--name-only','HEAD').decode().splitlines()+git('ls-files','--others','--exclude-standard').decode().splitlines());assert actual==changed
assert git('diff','--cached','--name-only')==b''
print(json.dumps({'result':'PASS','exact_review_files':len(changed),'inventories':results},indent=2))
