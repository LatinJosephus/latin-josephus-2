"""Verify current review-only candidate audit; write QA/manifests only.
Never stages, commits, writes production XML, enables navigation or pushes.
"""
import pathlib,json,hashlib,subprocess,sys,re,csv,ast,collections
P=pathlib.Path(__file__).resolve().parent;W=P.parents[1];C=pathlib.Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
sys.path.insert(0,str(P));sys.path.insert(0,str(W/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,fixtures
from candidate_adjudication import CHECKPOINT,LATIN,GREEK
BASE='1cf003beeb03f7b0acf2c42057ace062cdb7ebff'
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=root)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def old(p):return git(W,'show',f'{CHECKPOINT}:{p.relative_to(W).as_posix()}')
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def pinned_files(root,ref):
 count=0
 for entry in git(root,'ls-tree','-r','-z',ref).split(b'\0'):
  if not entry:continue
  meta,name=entry.split(b'\t',1);mode,kind,expected=meta.decode().split();name=name.decode('utf8');assert kind=='blob'
  raw=(root/name).read_bytes();assert expected in [blob(raw),blob(raw.replace(b'\r\n',b'\n'))],(root,name,'pinned source changed');count+=1
 return count

assert git(W,'rev-parse','HEAD').decode().strip()==CHECKPOINT
assert git(W,'branch','--show-current').decode().strip()=='antiquities-niese-08-10'
assert git(W,'diff','--cached','--name-only')==b''
advance=read(P/'CANONICAL_ADVANCE_FOLLOWUP.json');CH=advance['current_canonical_HEAD']
assert git(C,'rev-parse','HEAD').decode().strip()==git(C,'rev-parse','origin/v2-development').decode().strip()==CH
assert git(C,'branch','--show-current').decode().strip()=='v2-development' and git(C,'status','--porcelain')==b''
assert git(C,'diff','--name-status',advance['previous_canonical_HEAD'],CH).decode().splitlines()==advance['changed_paths_with_status']
assert sha((P/advance['prior_provenance_record']['path']).read_bytes())==advance['prior_provenance_record']['sha256']
for x in advance['documentation']:assert sha(pathlib.Path(x['path']).read_bytes())==x['sha256']
source_counts={'isolated_base':pinned_files(W,BASE),'current_canonical':pinned_files(C,CH)}
accepted=json.loads(old(P/'FOLLOWUP_MODIFIED_FILES.json'))['paths']
committed=git(W,'diff-tree','--no-commit-id','--name-only','-r',CHECKPOINT).decode().splitlines()
assert sorted(committed)==sorted(accepted) and len(committed)==221
message=git(W,'log','-1','--format=%B',CHECKPOINT).decode();assert 'Audit-only' in message and 'Implementation is NOT APPROVED' in message
commitinfo=read(P/'COMMITTED_CHECKPOINT.json');prior_counts={}
for label,commit in commitinfo['commits'].items():
 prefix=f'review/Antiquities_Niese_Book{"VIII" if label=="8" else "X"}_2026-10-08/' if label!='batch' else 'review/Antiquities_Niese_Batch_08_10_2026-10-08/'
 names=git(W,'diff-tree','--no-commit-id','--name-only','-r',commit).decode().splitlines();assert all(n.startswith(prefix) for n in names)
 msg=git(W,'log','-1','--format=%B',commit).decode();assert 'Candidate audits only' in msg and 'Implementation is NOT APPROVED' in msg;prior_counts[label]=len(names)
assert sum(prior_counts.values())==141
frozen=0
for packet in read(P/'FROZEN_SOURCE_VERIFICATION.json'):
 assert sha(pathlib.Path(packet['manifest']).read_bytes())==packet['manifest_sha256']
 for x in packet['files']:assert sha((pathlib.Path(packet['root'])/x['path']).read_bytes())==x['actual']==x['expected'];frozen+=1
for x in read(P/'METHOD_SOURCE_MANIFEST.json'):assert sha(pathlib.Path(x['path']).read_bytes())==x['sha256']
for x in read(P/'SOURCE_SEARCH.json')['selected_related_resources']:assert sha(pathlib.Path(x['path']).read_bytes())==x['sha256']
pdfs=read(P/'pdf-metadata.json')
for x in pdfs:assert sha(pathlib.Path(x['path']).read_bytes())==x['sha256']
images=read(P/'PRINT_EVIDENCE_MANIFEST.json')['images'];assert len(images)==169
for x in images:assert sha((W/x['path']).read_bytes())==x['sha256']

protected=[];results={}
for b,roman,expected,routine_count,inherit,milestones in [(8,'VIII',420,317,83,337),(10,'X',281,224,50,230)]:
 d=W/f'review/Antiquities_Niese_Book{roman}_2026-10-08';rows=read(d/'BOUNDARIES.json');previous=json.loads(old(d/'BOUNDARIES.json'));q=read(d/'ADJUDICATION_QA.json');history=read(d/'ADJUDICATION_HISTORY.json')
 assert [r['niese'] for r in rows]==list(range(1,expected+1))
 assert (d/'PRINT_CHECKPOINT_REVIEW_CASES.md').read_bytes()==old(d/'REVIEW_CASES.md')
 assert len(history)==expected and all(x['checkpoint_register_sha256']==sha(old(d/'BOUNDARIES.json')) and not x['source_XML_changed'] for x in history)
 books={lang:Book(W/f'assets/xml/antiquities/{lang}/book-{b:02}.xml') for lang in ['Greek','Latin']}
 nums=[int(m.group(1)) for x in books['Greek'].labels if (m:=re.fullmatch(r'\[(\d+)\]',x['text'].strip()))];assert nums==list(range(2,expected+1))
 for lang,item in read(d/'BASELINE.json')['inputs'].items():
  wr=(W/item['path']).read_bytes();cr=(C/item['path']).read_bytes();assert sha(wr)==item['worktree_before_sha256']==item['worktree_after_sha256'];assert sha(cr)==item['canonical_before_sha256']==item['canonical_after_sha256'];assert cr.replace(b'\r\n',b'\n')==wr
  protected.append({'book':b,'language':lang,'path':item['path'],'worktree_before_sha256':item['worktree_before_sha256'],'worktree_after_sha256':sha(wr),'canonical_before_sha256':item['canonical_before_sha256'],'canonical_after_sha256':sha(cr)})
 routine=[r['niese'] for r in previous if r['verification_work_state']=='GREEK_COLLATED_LATIN_CANDIDATE_AWAITING_INDIVIDUAL_VERIFICATION'];notes=read(d/'LATIN_INDIVIDUAL_REVIEWS.json')
 assert len(routine)==routine_count and set(map(int,notes))==set(routine) and q['routine_pending']==[]
 assert len({x['assessment'] for x in notes.values()})==routine_count
 for n,note in notes.items():
  assert note['status'] in ['SECURE','OPEN'] and len(note['assessment'])>25 and 'not inferred from Greek verification' in note['method']
  assert rows[int(n)-1]['individual_Latin_review']==note
 assert [int(n) for n,x in notes.items() if x['status']=='OPEN']==([] if b==8 else [276])
 assert q['inherited_candidate_starts']==inherit and q['proposed_milestones']==milestones and q['routine_reviewed']==routine_count
 assert q['new_milestones_applied']==q['Greek_repairs_applied']==q['source_files_written']==0 and q['implementation_approved'] is False
 for r,pr,h in zip(rows,previous,history):
  assert not r['implementation_approved'] and not r['apply_permitted']
  assert r['printed_checkpoint_state']['classification']==pr['classification'] and r['printed_checkpoint_state']['confidence']==pr['confidence'] and r['printed_checkpoint_state']['latin_locator']==pr['latin_locator']
  assert r['printed_checkpoint_reassessment']==pr.get('source_collation_reassessment') and r['print_collation']==pr['print_collation']
  assert r['print_collation']['routine_image_collation_complete'] and r['print_collation']['image_inspected']
  assert r['operative_source_assessment']['routine_print_collation_complete'] and r['independent_source_evidence']['remaining_print_work'] is None
  assert r['historical_print_start_verified']==pr.get('print_start_verified') and r['Greek_start_awaiting_print_verification'] is False
  for lang,key in [('Greek','greek_locator'),('Latin','latin_locator')]:
   if loc:=r[key]:assert books[lang].locate(loc['book_offset'])==loc,(b,r['niese'],key)
  keys=['greek_locator','latin_locator','latin_anchor_phrase','classification','confidence','placement','verification_work_state','candidate_latin_end_book_offset','availability']
  actual={k:{'before':pr.get(k),'after':r.get(k)} for k in keys if pr.get(k)!=r.get(k)};assert h['changes']==actual
  if r['classification']!=pr['classification']:assert r['human_decision'] or r.get('individual_Latin_review',{}).get('status')=='SECURE'
 for n,phrase in LATIN[b].items():
  r=rows[n-1];assert books['Latin'].stream[r['latin_locator']['book_offset']:].startswith(phrase) and r['human_decision'] and not r['human_decision']['production_application_authorized']
 for lang,key,section,endkey in [('Greek','greek_locator','greek_section','candidate_greek_end_book_offset'),('Latin','latin_locator','candidate_latin_section','candidate_latin_end_book_offset')]:
  positioned=[r for r in rows if r[key]];stream=books[lang].stream;fragments=[]
  for i,r in enumerate(positioned):
   at=r[key]['book_offset'];end=positioned[i+1][key]['book_offset'] if i+1<len(positioned) else len(stream)
   assert at<end and r[endkey]==end and r[section]==stream[at:end] and r[section].strip();fragments.append(r[section])
  assert stream[:positioned[0][key]['book_offset']]+''.join(fragments)==stream
 additions=[(r['latin_locator']['raw_byte'],f'<milestone unit="niese" n="{r["niese"]}"/>'.encode()) for r in rows if r['latin_locator'] and not r['inherited_start_retained']];assert len(additions)==milestones and len({at for at,t in additions})==milestones
 raw=books['Latin'].raw;rehearsal=raw
 for at,tag in sorted(additions,reverse=True):rehearsal=rehearsal[:at]+tag+rehearsal[at:]
 from lxml import etree
 parsed=Book(raw=rehearsal);assert parsed.stream==books['Latin'].stream
 assert parsed.tree.xpath('//@xml:id',namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})==books['Latin'].tree.xpath('//@xml:id',namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})
 assert parsed.tree.xpath('//@sameAs')==books['Latin'].tree.xpath('//@sameAs')
 restored=rehearsal
 for at,tag in additions:assert restored.count(tag)==1;restored=restored.replace(tag,b'',1)
 assert restored==raw and sha(rehearsal)==q['Latin_rehearsal_sha256'] and sha(restored)==q['Latin_source_sha256']
 identities=read(d/'EXECUTABLE_IDENTITIES.json');overrides=identities['displaced_inherited_claims'];assert sorted(x['visible_claim'] for x in overrides)==([187,255] if b==8 else [108,151])
 assert sum(x['retained_executable_start'] for x in identities['visible_label_inventory'])==inherit
 assert len(identities['identities'])==expected and len([x for x in identities['identities'] if x['locator']])==inherit+milestones
 assert list(csv.DictReader((d/'BOUNDARIES.tsv').open(encoding='utf8'),delimiter='\t')) and len(list(csv.DictReader((d/'BOUNDARIES.tsv').open(encoding='utf8'),delimiter='\t')))==expected
 if b==8:
  assert rows[366]['availability']=='PARTIAL_SURVIVAL' and rows[366]['printed_checkpoint_state']['classification']=='UNAVAILABLE'
  assert rows[366]['candidate_latin_section'].strip()=='et quae displucuerint sola relinquerent.'
  assert all(r['classification'] in ['EXACT','INTERNAL-BUT-EXACT'] for r in rows)
  for n in [110,172,368]:
   assert rows[n-1]['Niese_unambiguous_word_tag'] is False
   control=rows[n-1]['operative_source_assessment']['separate_print_and_Loeb_controls'];assert (d/control['image']).is_file()
  n=rows[368];unit=books['Latin'].units[n['latin_locator']['paragraph']-1];assert unit['text'].count('nunc inquit denuo missa legatione')==2 and unit['text'].index('nunc inquit denuo missa legatione')==n['latin_locator']['unit_offset']
 else:
  assert rows[107]['classification']=='UNAVAILABLE' and rows[107]['latin_locator'] is None
  assert rows[101]['human_decision'] is None and rows[101]['classification']=='REQUIRES_ADJUDICATION' and rows[101]['latin_anchor_phrase']=='nomine sedechiam' and rows[100]['candidate_latin_section'].rstrip().endswith('simulet ioachim')
  assert rows[275]['boundary_start_secure'] and rows[275]['availability']=='PARTIAL_CORRESPONDENCE_PROPOSED' and rows[275]['classification']=='REQUIRES_ADJUDICATION'
  assert 'Cui etiam rea' in rows[211]['candidate_latin_section'] and 'Cui etiam rea' not in rows[212]['candidate_latin_section']
  assert rows[247]['candidate_latin_section'].startswith('nepus nepos')
  matches=[books['Latin'].locate(m.start()) for m in re.finditer('roman',books['Latin'].stream,re.I)];assert len(matches)==1 and 'lingua romana' in matches[0]['left'][-10:]+matches[0]['right']
 assert q['current_verification_categories']==dict(collections.Counter(r['current_verification_category'] for r in rows)) and q['Greek_starts_awaiting_print_verification']==0
 results[str(b)]={'expected_sections':expected,'inherited_starts':inherit,'candidate_milestones':milestones,'routine_individual_reviews':routine_count,'secure_routine_reviews':q['routine_secure'],'open_editorial_records':[] if b==8 else [102,276],'verification_categories':q['current_verification_categories'],'every_mixed_content_locator_verified':True,'complete_Greek_and_Latin_narrative_partition':True,'rehearsal_XML_parses':True,'byte_invariance':True,'unchanged_ids_and_sameAs':True,'NO_GO':True}

fixture_result=fixtures()
allowed=[f'review/{name}/' for name in ['Antiquities_Niese_BookVIII_2026-10-08','Antiquities_Niese_BookX_2026-10-08','Antiquities_Niese_Batch_08_10_2026-10-08']]
qa={'result':'PASS','scope':'Audit integrity and preservation; not scholarly implementation or browser certification','accepted_print_checkpoint_commit':CHECKPOINT,'accepted_print_checkpoint_exact_files':len(committed),'earlier_audit_commit_file_counts':prior_counts,'worktree_branch':'antiquities-niese-08-10','worktree_HEAD':CHECKPOINT,'staged_files':[],'canonical_branch':'v2-development','canonical_HEAD':CH,'origin_tracking_HEAD':CH,'canonical_working_tree':'CLEAN','pinned_Git_blob_files_verified':source_counts,'frozen_research_files_verified':frozen,'PDF_files_verified':len(pdfs),'accepted_print_evidence_images_verified':len(images),'source_before_after':protected,'per_book':results,'mixed_content_fixtures':fixture_result,'production_changes':[],'Greek_repairs_applied':0,'Latin_milestones_applied':0,'reader_books_enabled':[],'certified_Antiquities_Niese':2456,'current_candidate_changes':'UNSTAGED AND UNCOMMITTED','new_book_browser_QA':'NOT RUN: both books disabled, no implementation. Prior actual built-site baseline evidence retained unchanged.','push_performed':False}
write(P/'ADJUDICATION_VERIFICATION.json',qa)
modified=set(git(W,'diff','--name-only','HEAD').decode().splitlines()+git(W,'ls-files','--others','--exclude-standard').decode().splitlines())
modified.add((P/'ADJUDICATION_MODIFIED_FILES.json').relative_to(W).as_posix());modified.add((P/'FILE_MANIFEST.json').relative_to(W).as_posix())
for roman in ['VIII','X']:modified.add(f'review/Antiquities_Niese_Book{roman}_2026-10-08/FILE_MANIFEST.json')
assert all(any(n.startswith(p) for p in allowed) for n in modified),sorted(modified)
write(P/'ADJUDICATION_MODIFIED_FILES.json',{'status':'UNSTAGED_AND_UNCOMMITTED_CANDIDATE_AUDIT','against_commit':CHECKPOINT,'paths':sorted(modified),'production_paths':[],'stage_permission':'No staging or further commit authorization is inferred from editorial acceptance.'})
for roman in ['VIII','X']:
 d=W/f'review/Antiquities_Niese_Book{roman}_2026-10-08'
 write(d/'FILE_MANIFEST.json',{'scope':d.name,'status':'CURRENT_ADJUDICATED_CANDIDATE_AUDIT_NO_GO','excludes':['FILE_MANIFEST.json (self-reference)'],'source_before_after_hashes':'BASELINE.json and QA.json','files':[{'path':f.relative_to(d).as_posix(),'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size} for f in sorted(d.rglob('*')) if f.is_file() and f.name!='FILE_MANIFEST.json']})
files=[]
for prefix in allowed:
 for f in sorted((W/prefix).rglob('*')):
  if f.is_file() and f!=P/'FILE_MANIFEST.json':files.append({'path':f.relative_to(W).as_posix(),'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size})
write(P/'FILE_MANIFEST.json',{'scope':'All three current candidate review packets','excludes':[(P/'FILE_MANIFEST.json').relative_to(W).as_posix()+' (self-reference)'],'files':files})
for manifest in [W/f'review/Antiquities_Niese_Book{r}_2026-10-08/FILE_MANIFEST.json' for r in ['VIII','X']]+[P/'FILE_MANIFEST.json']:
 root=W if manifest.parent==P else manifest.parent
 for x in read(manifest)['files']:assert sha((root/x['path']).read_bytes())==x['sha256']
for path in modified:
 f=W/path
 if f.suffix=='.json':read(f)
 if f.suffix=='.py':ast.parse(f.read_text(encoding='utf8'))
 assert '__pycache__' not in path
assert git(W,'diff','--cached','--name-only')==b'' and git(C,'status','--porcelain')==b''
actual=set(git(W,'diff','--name-only','HEAD').decode().splitlines()+git(W,'ls-files','--others','--exclude-standard').decode().splitlines());assert actual==modified
print(json.dumps({k:qa[k] for k in ['result','accepted_print_checkpoint_exact_files','pinned_Git_blob_files_verified','frozen_research_files_verified','PDF_files_verified','accepted_print_evidence_images_verified','per_book','current_candidate_changes']},indent=2));print('EXACT_CURRENT_REVIEW_DELTA',len(modified))
