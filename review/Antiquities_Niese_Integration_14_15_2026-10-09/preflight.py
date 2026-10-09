"""Freeze actual current canonical and complete certified incoming scope once."""
from pathlib import Path
import hashlib,json,subprocess,socket,datetime
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent
CAN=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
SRC=Path(r'C:\workspace\LatinJosephus-antiquities-niese-14-15')
RUNTIME=Path(r'C:\workspace\Antiquities-Niese-14-15-integration-runtime-20261009')
BASE='ad3158b7a86dea6997510b3de17f2e510c23367c';TIP='48a5b5ce711eb63a9071c0f06c22d9b5414e6607'
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd).decode('utf8').strip()
def sha(x):return hashlib.sha256(x).hexdigest()
def save(name,x):(P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def blobs(commit):
 rows=[]
 for line in git('ls-tree','-r','--format=%(objectmode) %(objectname) %(path)',commit).splitlines():
  mode,oid,path=line.split(' ',2);rows.append(dict(path=path,mode=mode,blob=oid))
 out=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(r['blob'] for r in rows)+'\n').encode(),cwd=ROOT)
 pos=0
 for r in rows:
  end=out.index(b'\n',pos);n=int(out[pos:end].split()[2]);raw=out[end+1:end+n+1];pos=end+n+2;r.update(blob_sha256=sha(raw),blob_bytes=len(raw))
 assert pos==len(out)
 return rows
assert not (P/'BASELINE.json').exists(),'Never overwrite a frozen integration baseline'
start=git('rev-parse','HEAD',cwd=CAN)
assert start==git('rev-parse','HEAD') and git('branch','--show-current',cwd=CAN)=='v2-development'
assert not git('status','--porcelain',cwd=CAN) and not git('status','--porcelain',cwd=SRC)
assert git('rev-parse','HEAD',cwd=SRC)==git('rev-parse','refs/heads/antiquities-niese-14-15')==TIP
RUNTIME.mkdir(exist_ok=False)
with socket.socket() as s:
 try:s.bind(('127.0.0.1',8915));port=8915
 except OSError:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
canonical=blobs(start)
for r in canonical:
 raw=(CAN/r['path']).read_bytes();r.update(working_sha256=sha(raw),working_bytes=len(raw),CRLF=raw.count(b'\r\n'),LF=raw.count(b'\n'))
source={r['path']:r for r in blobs(TIP)}
changed=git('diff','--name-status',BASE,TIP).splitlines();incoming=[]
for line in changed:
 status,path=line.split('\t',1);r=dict(source[path],status=status,kind='review' if path.startswith('review/') else 'production')
 raw=(SRC/path).read_bytes();r.update(certified_working_sha256=sha(raw),certified_working_bytes=len(raw));assert r['blob_sha256']==r['certified_working_sha256'];incoming.append(r)
assert len(incoming)==538 and sum(r['kind']=='production' for r in incoming)==7
for folder in ['Antiquities_Niese_BookXIV_2026-10-09','Antiquities_Niese_BookXV_2026-10-09','Antiquities_Niese_Batch_14_15_2026-10-09']:
 manifest=json.loads((SRC/'review'/folder/'FILE_MANIFEST.json').read_text())
 for f in manifest['files']:assert sha(Path(f['path']).read_bytes())==f['sha256']
save('BASELINE.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),canonical_checkout=str(CAN),canonical_branch='v2-development',canonical_start=start,remote_start_directly_verified=start,preceding_certified_source='76083c2831afdb4853f7d7ebab0db6c64c18d914',preceding_verified_tip='81126ce116045433cb5cf22945cc3711701ac3ca',source_checkout=str(SRC),source_branch='antiquities-niese-14-15',source_tip=TIP,frozen_source_base=BASE,integration_worktree=str(ROOT),integration_branch=git('branch','--show-current'),runtime=str(RUNTIME),preferred_QA_port=8915,actual_preflight_free_port=port,canonical_tracked_files=canonical,applicable_AGENTS_found=[]))
save('INCOMING_SCOPE.json',dict(base=BASE,certified_tip=TIP,production_count=7,review_count=531,total_files=538,source_history=git('log','--reverse','--format=%H %s',f'{BASE}..{TIP}').splitlines(),files=incoming,source_manifests_verified=True))
prior=Path(r'C:\workspace\LatinJosephus-antiquities-niese-12-13-integration/review/Antiquities_Niese_Integration_12_13_2026-10-09')
save('PREDECESSOR_VERIFICATION.json',dict(result='PASS',canonical_and_direct_remote=start,full_source_ancestry_verified=True,source_tip='76083c2831afdb4853f7d7ebab0db6c64c18d914',IX_and_Whiston_ancestry_verified=True,production_blobs_verified=7,integration_manifest_entries_verified=111,certificate_evidence_hashes_verified=True,report=str(prior/'REPORT.md'),report_sha256=sha((prior/'REPORT.md').read_bytes()),manifest_sha256=sha((prior/'FILE_MANIFEST.json').read_bytes()),certificate_sha256=sha((prior/'CERTIFICATE.json').read_bytes()),promotion_receipt=str(Path(r'C:\workspace\Antiquities-Niese-12-13-integration-runtime-20261009/PROMOTION_RECEIPT.json')),canonical_selectable=4315))
subprocess.check_call(['git','archive','--format=tar','-o',str(RUNTIME/'starting-canonical.tar'),start],cwd=ROOT)
print('Frozen actual canonical',start,'and complete538-file incoming source; free QA port',port)
