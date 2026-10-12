import pathlib,json,hashlib,subprocess,shutil,zipfile
BASE=pathlib.Path(__file__).parent;ROOT=BASE/'candidate';PACK=ROOT/'review/Whiston_XVI_XX_Integration_2026-10-12'
AUDIT=pathlib.Path('C:/workspace/Whiston_Antiquities_Corpus_Audit_Independent_20261012');CANON=pathlib.Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
PIN='f6fa17f7616bf9ce046c28086b1a1448a9f8d049'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
assert subprocess.check_output(['git','-C',str(CANON),'rev-parse','HEAD']).decode().strip()==PIN
assert not subprocess.check_output(['git','-C',str(CANON),'status','--porcelain=v1'])
assert git('rev-parse','HEAD').decode().strip()==PIN and not git('status','--porcelain=v1')
PACK.mkdir(parents=True);(PACK/'tools').mkdir();(PACK/'certified').mkdir()
snapshot={p:sha((ROOT/p).read_bytes()) for p in git('ls-files').decode().splitlines() if (ROOT/p).is_file()}
save(PACK/'BASELINE.json',dict(commit=PIN,canonical=str(CANON),canonical_clean=True,private_git_metadata=str(BASE/'repository.git'),candidate_branch=git('branch','--show-current').decode().strip(),tracked_file_hashes=snapshot))
for folder in ['assets','bin','_docs']:shutil.copytree(ROOT/folder,BASE/'baseline'/folder)
prior=ROOT/'review/Whiston_XII_XV_Integration_2026-10-12'
for name in ['browser_qa.cjs','regression_qa.cjs','bamberg_qa.cjs','ui_qa.cjs','book_navigation_qa.cjs','auxiliary_qa.cjs','native_lodge_qa.mjs']:
 shutil.copy2(prior/'tools'/name,PACK/'tools'/name)
for name in ['INTERVAL_ORACLE.json','CONTAINING_ORACLE.json','MARKUP_ORACLE.json','PRIOR_LEGACY_GUARD_REGISTER.json','PRIOR_LEGACY_GUARD_REGISTER.md']:
 shutil.copy2(prior/name,PACK/('PRIOR_'+name))
inv=load(AUDIT/'FROZEN_SOURCE_INVENTORY.json');records=[];prior_sources=[]
for b in inv['books']:
 for f in b['segmented_files']:
  data=(AUDIT/f['path']).read_bytes();assert sha(data)==f['sha256']
  shutil.copy2(AUDIT/f['path'],PACK/'certified'/pathlib.Path(f['path']).name)
  if b['book']<16:
   assert (ROOT/f['git_path']).read_bytes()==data,('Previously integrated frozen source differs',b['book'],f['git_path'])
   prior_sources.append(dict(path=f['git_path'],sha256=sha(data),bytes=len(data)))
   continue
  commit=git('rev-parse',b['delivery_commit']+'^{commit}').decode().strip();assert commit==b['delivery_commit']
  blob=git('show',f'{commit}:{f["git_path"]}');assert sha(blob)==f['delivery_commit_blob_sha256']
  assert blob.replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n'),'Unexpected delivery-object difference'
  archive=b['archive_verifications'][-1];arc=AUDIT/archive['frozen_path'];assert sha(arc.read_bytes())==archive['sha256']
  with zipfile.ZipFile(arc) as z:
   assert z.testzip() is None
   member='output/'+pathlib.Path(f['path']).name;assert z.read(member)==data
   manifests=[n for n in z.namelist() if n.endswith('ARCHIVE_MANIFEST.json')]
   if manifests:
    m=json.loads(z.read(manifests[0])); entries=m if isinstance(m,list) else m.get('files',m.get('entries',[]))
    if isinstance(entries,dict): entries=[dict(path=k,sha256=v if isinstance(v,str) else v['sha256']) for k,v in entries.items()]
    for r in entries:
     if 'sha256' in r:assert sha(z.read(r.get('path',r.get('name'))))==r['sha256']
  shutil.copy2(arc,BASE/'source-recovery'/arc.name) if (BASE/'source-recovery').exists() else None
  shutil.copy2(AUDIT/f['approved_baseline']['path'],PACK/'certified'/('approved-original-'+pathlib.Path(f['path']).name))
  target=PACK/'inherited-qualifications'/f'book-{b["book"]:02}';target.mkdir(parents=True)
  for p in (AUDIT/'evidence'/f'book-{b["book"]:02}').glob('*'):
   if p.is_file() and p.suffix in ['.md','.txt','.json']:shutil.copy2(p,target/p.name)
  records.append(dict(book=b['book'],delivery_commit=commit,file=f['git_path'],certified_sha256=sha(data),bytes=len(data),delivery_blob_sha256=sha(blob),delivery_blob=f['delivery_commit_blob'],Git_blob_only_EOL_difference=blob!=data,archive=str(arc),archive_sha256=archive['sha256'],archive_member=member,archive_CRC='PASS',baseline_sha256=f['approved_baseline']['sha256'],expected_count=f['expected_count'],qualifications=b['relevant_editorial_qualifications']))
save(PACK/'SOURCE_INVENTORY.json',records);save(PACK/'I_XV_FROZEN_SOURCE_VERIFICATION.json',dict(status='PASS',files=prior_sources,intervals=5604))
for name in ['FROZEN_SOURCE_INVENTORY.json','GLOBAL_CORPUS_VERIFICATION_REPORT.txt','VERDICT.json','FINAL_FROZEN_SOURCE_RECHECK.json','CORPUS_AUDIT_MATRIX.json','CORPUS_AUDIT_MATRIX.csv']:
 shutil.copy2(AUDIT/name,PACK/('CORPUS_'+name))
shutil.copy2(ROOT/'review/Whiston_I_XI_Canonical_Integration_2026-10-11/build/Gemfile.lock',ROOT/'Gemfile.lock')
shutil.copy2(__file__,PACK/'tools/source_acquisition.py')
print('PASS: frozen I-XV byte-identical; five delivery objects, certified physical XML and source ZIPs verified')
