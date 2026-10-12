import pathlib,json,hashlib,subprocess,shutil,zipfile,re
BASE=pathlib.Path(__file__).parent;ROOT=BASE/'candidate';PACK=ROOT/'review/Whiston_XII_XV_Integration_2026-10-12';AUDIT=pathlib.Path('C:/workspace/Whiston_Antiquities_Corpus_Audit_Independent_20261012');PIN='43c3626493daa6768f9fc818679214035a62a281'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
PACK.mkdir(parents=True,exist_ok=True);(PACK/'tools').mkdir(exist_ok=True);(PACK/'certified').mkdir(exist_ok=True)
assert git('rev-parse','HEAD').decode().strip()==PIN
snapshot={p:sha((ROOT/p).read_bytes()) for p in git('ls-files').decode().splitlines() if (ROOT/p).is_file()}
save(PACK/'BASELINE.json',dict(commit=PIN,canonical='C:/Users/Pollard_R/Git/LatinJosephus-v2-development',canonical_branch='v2-development',canonical_clean=True,candidate_branch=git('branch','--show-current').decode().strip(),private_git_metadata=str(BASE/'repository.git'),notice_correction_included=True,baseline_renderer_SHA256=snapshot['assets/js/renderTei.js'],tracked_file_hashes=snapshot,public_preview_commit='ddbba537cd489825e5aaab0619f2f8d73aec4780',public_preview_out_of_scope=True))
for folder in ['assets','bin','_docs']:
 shutil.copytree(ROOT/folder,BASE/'baseline'/folder)
prior=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11';new=PACK/'tools'
for name in ['browser_qa.cjs','regression_qa.cjs','auxiliary_qa.cjs']:
 shutil.copy2(prior/'tools'/name,new/name)
for name in ['INTERVAL_ORACLE.json','CONTAINING_ORACLE.json','MARKUP_ORACLE.json']:
 shutil.copy2(prior/name,PACK/('PRIOR_'+name))
for name in ['LEGACY_GUARD_REGISTER.json','LEGACY_GUARD_REGISTER.md']:
 shutil.copy2(ROOT/'review/Whiston_I_XI_Canonical_Integration_2026-10-11'/name,PACK/('PRIOR_'+name))
inv=load(AUDIT/'FROZEN_SOURCE_INVENTORY.json');records=[]
for n in range(12,16):
 b=inv['books'][n-1];f=b['segmented_files'][0];source=AUDIT/f['path'];data=source.read_bytes();assert sha(data)==f['sha256']==f['certified_physical_sha256']
 commit=git('rev-parse',b['delivery_commit']+'^{commit}').decode().strip();assert commit==b['delivery_commit'];blob=git('show',f'{commit}:{f["git_path"]}');assert blob.replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n')
 archive=b['archive_verifications'][-1];arc=AUDIT/archive['frozen_path'];assert sha(arc.read_bytes())==archive['sha256']
 with zipfile.ZipFile(arc) as z:
  assert z.testzip() is None
  member=next(m for m in z.namelist() if m=='output/'+source.name);assert z.read(member)==data
 (PACK/'certified'/source.name).write_bytes(data)
 # Restore only in owned verification copies; no text is altered.
 shutil.copy2(AUDIT/f['approved_baseline']['path'],PACK/'certified'/('approved-original-'+source.name))
 records.append(dict(book=n,delivery_commit=commit,branch=b['recorded_delivery_branch'],certified_sha256=sha(data),bytes=len(data),file=f['git_path'],audit_inventory_sha256=sha((AUDIT/'FROZEN_SOURCE_INVENTORY.json').read_bytes()),archive_sha256=archive['sha256'],archive_member=member,archive_CRC='PASS',Git_blob_EOL_only_or_exact=True,baseline_sha256=f['approved_baseline']['sha256'],HIGH=b['existing_confidence_totals']['HIGH'],MEDIUM=b['existing_confidence_totals']['MEDIUM'],qualifications=b['relevant_editorial_qualifications']))
save(PACK/'SOURCE_INVENTORY.json',records)
for name in ['FROZEN_SOURCE_INVENTORY.json','GLOBAL_CORPUS_VERIFICATION_REPORT.txt','VERDICT.json','FINAL_FROZEN_SOURCE_RECHECK.json']:
 shutil.copy2(AUDIT/name,PACK/('CORPUS_'+name))
runtime=BASE/'runtime';(runtime/'shell').mkdir(parents=True,exist_ok=True)
oldsite=pathlib.Path('C:/workspace/Whiston-I-XI-Integration-runtime-20261011/standard-site')
for route in ['antiquities','bellum-judaicum','contra-apionem','deh']:
 target=runtime/'shell'/route;target.mkdir();shutil.copy2(oldsite/route/'index.html',target/'index.html')
shutil.copytree(oldsite/'assets/css',runtime/'shell/assets/css')
shutil.copy2(ROOT/'review/Whiston_I_XI_Canonical_Integration_2026-10-11/build/Gemfile.lock',ROOT/'Gemfile.lock')
print('Frozen corrected baseline and four certified sources verified; isolated worktree prepared')
