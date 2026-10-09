"""Read-only source/Git/locator checks, then write review QA and refreshed manifests.
Never stages, commits, pushes, changes source files or applies proposed markers.
"""
import pathlib,json,hashlib,subprocess,sys,collections,re
P=pathlib.Path(__file__).resolve().parent;W=P.parents[1];C=pathlib.Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
sys.path.insert(0,str(W/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,fixtures
BASE='1cf003beeb03f7b0acf2c42057ace062cdb7ebff';HEAD='39c9b60803f38806872a9c0a6a905c92ffa03d3e'
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=root)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def pinned_files(root,ref):
 count=0
 for entry in git(root,'ls-tree','-r','-z',ref).split(b'\0'):
  if not entry:continue
  meta,name=entry.split(b'\t',1);mode,kind,expected=meta.decode().split();name=name.decode('utf8');assert kind=='blob'
  raw=(root/name).read_bytes();assert expected in [blob(raw),blob(raw.replace(b'\r\n',b'\n'))],(root,name,'source differs from pinned Git blob');count+=1
 return count
advance_path=P/'CANONICAL_ADVANCE_FOLLOWUP.json'
advance=json.loads(advance_path.read_text(encoding='utf8'));CH=advance['current_canonical_HEAD']
assert git(C,'diff','--name-status',advance['previous_canonical_HEAD'],CH).decode().splitlines()==advance['changed_paths_with_status']
assert sha((P/advance['prior_provenance_record']['path']).read_bytes())==advance['prior_provenance_record']['sha256']
for item in advance['documentation']:assert sha(pathlib.Path(item['path']).read_bytes())==item['sha256']
assert git(W,'rev-parse','HEAD').decode().strip()==HEAD
assert git(W,'branch','--show-current').decode().strip()=='antiquities-niese-08-10'
assert git(C,'branch','--show-current').decode().strip()=='v2-development'
assert git(C,'rev-parse','HEAD').decode().strip()==git(C,'rev-parse','origin/v2-development').decode().strip()==CH
assert git(C,'status','--porcelain')==b''
assert git(W,'diff','--cached','--name-only')==b''
source_counts={'isolated_base_files':pinned_files(W,BASE),'current_canonical_files':pinned_files(C,CH)}
commitinfo=json.loads((P/'COMMITTED_CHECKPOINT.json').read_text(encoding='utf8'));commitcounts={}
for label,commit in commitinfo['commits'].items():
 prefix=f'review/Antiquities_Niese_Book{"VIII" if label=="8" else "X"}_2026-10-08/' if label!='batch' else 'review/Antiquities_Niese_Batch_08_10_2026-10-08/'
 files=git(W,'diff-tree','--no-commit-id','--name-only','-r',commit).decode().splitlines()
 assert all(f.startswith(prefix) for f in files),(label,files)
 message=git(W,'log','-1','--format=%B',commit).decode();assert 'Candidate audits only' in message and 'Implementation is NOT APPROVED' in message
 commitcounts[label]=len(files)
assert sum(commitcounts.values())==141
freeze=json.loads((P/'FROZEN_SOURCE_VERIFICATION.json').read_text(encoding='utf8'));frozencount=0
for packet in freeze:
 assert sha(pathlib.Path(packet['manifest']).read_bytes())==packet['manifest_sha256']
 for f in packet['files']:assert sha((pathlib.Path(packet['root'])/f['path']).read_bytes())==f['actual']==f['expected'];frozencount+=1
for name in ['METHOD_SOURCE_MANIFEST.json']:
 for x in json.loads((P/name).read_text(encoding='utf8')):assert sha(pathlib.Path(x['path']).read_bytes())==x['sha256']
for x in json.loads((P/'SOURCE_SEARCH.json').read_text(encoding='utf8'))['selected_related_resources']:assert sha(pathlib.Path(x['path']).read_bytes())==x['sha256']
pdfs=json.loads((P/'pdf-metadata.json').read_text(encoding='utf8'))
for x in pdfs:assert sha(pathlib.Path(x['path']).read_bytes())==x['sha256']
selected=json.loads((P/'SOURCE_MANIFEST.json').read_text(encoding='utf8'))['printed_sources']
source_by_kind={key:next(x for x in selected if match in x['path']) for key,match in [('Niese','Niese (1885)'),('V','V-VIII'),('VI','9-11')]}
images=[];perbook={};protected=[]
for b,roman,count in [(8,'VIII',420),(10,'X',281)]:
 d=W/f'review/Antiquities_Niese_Book{roman}_2026-10-08';rows=json.loads((d/'BOUNDARIES.json').read_text(encoding='utf8'));assert [r['niese'] for r in rows]==list(range(1,count+1))
 oldcommit=commitinfo['commits'][str(b)];oldraw=git(W,'show',f'{oldcommit}:{(d/"BOUNDARIES.json").relative_to(W).as_posix()}');old=json.loads(oldraw)
 books={lang:Book(path=W/f'assets/xml/antiquities/{lang}/book-{b:02}.xml') for lang in ['Greek','Latin']}
 nums=[int(m.group(1)) for l in books['Greek'].labels if (m:=re.fullmatch(r'\[(\d+)\]',l['text'].strip()))];assert nums==list(range(2,count+1))
 baseline=json.loads((d/'BASELINE.json').read_text(encoding='utf8'))
 for lang,item in baseline['inputs'].items():
  wr=(W/item['path']).read_bytes();cr=(C/item['path']).read_bytes()
  assert sha(wr)==item['worktree_before_sha256']==item['worktree_after_sha256'];assert sha(cr)==item['canonical_before_sha256']==item['canonical_after_sha256'];assert cr.replace(b'\r\n',b'\n')==wr
  protected.append(dict(book=b,language=lang,path=item['path'],worktree_before_sha256=item['worktree_before_sha256'],worktree_after_sha256=sha(wr),canonical_before_sha256=item['canonical_before_sha256'],canonical_after_sha256=sha(cr)))
 for row,previous in zip(rows,old):
  for key in ['classification','confidence','greek_locator','latin_locator','latin_anchor_phrase','placement','greek_start','candidate_latin_section']:
   assert row.get(key)==previous.get(key),(b,row['niese'],key,'checkpoint changed')
  assert row['human_decision'] is None and row['implementation_approved'] is False
  for lang,key in [('Greek','greek_locator'),('Latin','latin_locator')]:
   loc=row[key]
   if loc:assert books[lang].locate(loc['book_offset'])==loc,(b,row['niese'],key)
  obs=row['print_collation'];assert obs['image_inspected'] and obs['routine_image_collation_complete'];assert (d/obs['image']).exists();assert obs['printed_page']==obs['pdf_page']-8
  if p:=row.get('source_collation_reassessment'):
   assert not p['approved'] and not p['apply']
   for lang,key in [('Greek','greek_locator'),('Latin','latin_locator')]:assert books[lang].locate(p[key]['book_offset'])==p[key]
   for lang,key in [('Greek','greek_locator'),('Latin','latin_locator')]:
    at=p[key]['book_offset'];earlier=next((r[key]['book_offset'] for r in reversed(rows[:row['niese']-1]) if r[key]),-1);later=next((r[key]['book_offset'] for r in rows[row['niese']:] if r[key]),len(books[lang].stream))
    assert earlier<at<later,(b,row['niese'],lang,'proposed extent crosses neighbour')
 history=json.loads((d/'DECISION_HISTORY.json').read_text(encoding='utf8'));assert len(history)==count and all(h['checkpoint_register_sha256']==sha(oldraw) and not h['classification_changed'] and not h['confidence_changed'] and not h['applied'] for h in history)
 observations=json.loads((d/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'));assert len(observations)==count
 pageimages=list((d/'evidence/print-collation').glob('niese-II-pdf-*.jpg'));assert len(pageimages)==(90 if b==8 else 63)
 for f in sorted((d/'evidence/print-collation').iterdir()):
  if not f.is_file():continue
  n=int(re.search(r'(\d+)\.(?:png|jpg)$',f.name).group(1));kind='Niese' if f.suffix=='.jpg' else 'V' if b==8 else 'VI';source=source_by_kind[kind]
  images.append(dict(book=b,path=f.relative_to(W).as_posix(),pdf_page=n,printed_page=n-(8 if kind!='VI' else 16),source_path=source['path'],source_sha256=source['sha256'],sha256=sha(f.read_bytes()),bytes=f.stat().st_size,format='jpeg' if f.suffix=='.jpg' else 'png',dpi=150 if f.suffix=='.jpg' else 140,visually_inspected=True))
 perbook[b]={'register_records':count,'all_checkpoint_classifications_and_candidates_preserved':True,'all_original_and_proposed_mixed_content_locators_verified':True,'all_sources_byte_unchanged':True,'print_images':len(pageimages),'NO_GO':True,'new_book_browser_QA':'NOT RUN: no implementation or enablement'}
fixtures()
write(P/'PRINT_EVIDENCE_MANIFEST.json',{'sources':[{k:s[k] for k in ['path','sha256']} for s in source_by_kind.values()],'renderer':subprocess.run(['pdftoppm','-v'],capture_output=True,text=True).stderr.strip(),'images':images,'visual_review':'All 153 full Niese body pages inspected in sequential two-page body sheets; individual full pages and independent Loeb controls re-opened for discrepancies. Saved full pages preserve apparatus and page headers. Image generation does not certify a Latin cut.'})
allowed=[str((W/f'review/{name}').relative_to(W)).replace('\\','/')+'/' for name in ['Antiquities_Niese_BookVIII_2026-10-08','Antiquities_Niese_BookX_2026-10-08','Antiquities_Niese_Batch_08_10_2026-10-08']]
modified=set(git(W,'diff','--name-only','HEAD').decode().splitlines()+git(W,'ls-files','--others','--exclude-standard').decode().splitlines())
modified.update((P/name).relative_to(W).as_posix() for name in ['FOLLOWUP_QA.json','FOLLOWUP_MODIFIED_FILES.json','FILE_MANIFEST.json'])
modified.update((W/f'review/Antiquities_Niese_Book{roman}_2026-10-08/FILE_MANIFEST.json').relative_to(W).as_posix() for roman in ['VIII','X'])
assert all(any(name.startswith(p) for p in allowed) for name in modified),sorted(modified)
write(P/'FOLLOWUP_MODIFIED_FILES.json',{'status':'UNSTAGED_COLLATION_ADDENDUM','paths':sorted(modified),'production_paths':[],'checkpoint_scope_remains':'MODIFIED_FILES.json records the earlier committed 141-file checkpoint; it is not the follow-up manifest.'})
qa={'result':'PASS','scope':'Audit integrity, source preservation, mixed-content locators and file scope; not scholarly certification','canonical_branch':'v2-development','canonical_HEAD':CH,'origin_tracking_HEAD':CH,'canonical_working_tree':'CLEAN','worktree_branch':'antiquities-niese-08-10','worktree_HEAD':HEAD,'staged_files':[],'checkpoint_commit_file_counts':commitcounts,'base_files_verified':source_counts,'all_base_tracked_files_byte_or_checkout_normalization_unchanged':True,'frozen_research_files_rechecked':frozencount,'PDF_files_rechecked':len(pdfs),'inputs_and_outputs':protected,'per_book':perbook,'evidence_images':len(images),'new_milestones':0,'Greek_repairs_applied':0,'cumulative_certified_Niese_coverage':2456,'new_book_browser_tests':'NOT RUN; books remain disabled','regression_evidence':'Existing actual built-site regression/browser results retained in checkpoint; no production change in addendum.','manifest_hashes_checked':True,'followup_changes':'UNSTAGED AND UNCOMMITTED','no_push_performed':True}
write(P/'FOLLOWUP_QA.json',qa)
for b,roman in [(8,'VIII'),(10,'X')]:
 d=W/f'review/Antiquities_Niese_Book{roman}_2026-10-08';manifest={'scope':d.name,'status':'CANDIDATE_AUDIT_FOLLOWUP_NO_GO','excludes':['FILE_MANIFEST.json (self-reference)'],'source_and_output_hashes':'BASELINE.json','files':[dict(path=f.relative_to(d).as_posix(),sha256=sha(f.read_bytes()),bytes=f.stat().st_size) for f in sorted(d.rglob('*')) if f.is_file() and f.name!='FILE_MANIFEST.json']};write(d/'FILE_MANIFEST.json',manifest)
allfiles=[]
for prefix in allowed:
 for f in sorted((W/prefix).rglob('*')):
  if f.is_file() and f!=P/'FILE_MANIFEST.json':allfiles.append(dict(path=f.relative_to(W).as_posix(),sha256=sha(f.read_bytes()),bytes=f.stat().st_size))
write(P/'FILE_MANIFEST.json',{'scope':'All three candidate review packets; current collation addendum included','excludes':[(P/'FILE_MANIFEST.json').relative_to(W).as_posix()+' (self-reference)'],'source_hashes':'SOURCE_MANIFEST.json','files':allfiles})
for manifest in [W/f'review/Antiquities_Niese_Book{roman}_2026-10-08/FILE_MANIFEST.json' for roman in ['VIII','X']]+[P/'FILE_MANIFEST.json']:
 root=W if manifest.parent==P else manifest.parent
 for f in json.loads(manifest.read_text(encoding='utf8'))['files']:assert sha((root/f['path']).read_bytes())==f['sha256']
print(json.dumps({k:qa[k] for k in ['result','canonical_HEAD','worktree_HEAD','checkpoint_commit_file_counts','base_files_verified','frozen_research_files_rechecked','PDF_files_rechecked','evidence_images','followup_changes']},indent=2))
