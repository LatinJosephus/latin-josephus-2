"""Authorized fast-forward promotion, normal push and direct remote-byte proof."""
from pathlib import Path
import json,hashlib,subprocess,sys,datetime,urllib.request
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
C=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
S=Path('C:/workspace/LatinJosephus-antiquities-niese-11')
R=Path('C:/workspace/Antiquities-Niese-11-integration-runtime-20261009')
def git(*a,cwd=ROOT):return subprocess.check_output(['git',*a],cwd=cwd).decode().strip()
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def gate():
 b=load(D/'BASELINE.json');cert=load(D/'CERTIFICATION.json');assert cert['result']=='PASS'
 local=git('rev-parse','HEAD',cwd=C);remote=git('ls-remote','origin','refs/heads/v2-development',cwd=C).split()[0]
 assert local==remote==b['canonical'],'Canonical advanced: incorporate it in isolation and repeat affected QA before promotion.'
 assert git('branch','--show-current',cwd=C)=='v2-development' and not git('status','--porcelain=v1',cwd=C)
 assert git('rev-parse','HEAD',cwd=S)==b['source_tip'] and git('rev-parse','antiquities-niese-11')==b['source_tip'] and not git('status','--porcelain=v1',cwd=S)
 for f in load(D/'BUILD_INPUT_MANIFEST.json'):assert sha((ROOT/f['relative']).read_bytes())==f['sha256'],f['relative']
 subprocess.run(['git','merge-base','--is-ancestor',local,'HEAD'],cwd=ROOT,check=True)
 return dict(result='PASS',checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),local=local,direct_remote=remote,source_tip=b['source_tip'],canonical_clean=True,source_clean=True,production_unchanged_since_build=True)
def main():
 mode=sys.argv[1];g=gate()
 if mode=='gate':save(D/'PROMOTION_GATE.json',g);print(json.dumps(g));return
 assert mode=='promote'
 assert not git('status','--porcelain=v1'),'Commit certification before promotion'
 tip=git('rev-parse','HEAD');manifest=load(D/'FILE_MANIFEST.json')
 for f in manifest['files']:assert sha((ROOT/f['relative']).read_bytes())==f['sha256'],f['relative']
 subprocess.run(['git','merge','--ff-only',tip],cwd=C,check=True)
 assert git('rev-parse','HEAD',cwd=C)==tip and not git('status','--porcelain=v1',cwd=C)
 subprocess.run(['git','push','origin','v2-development'],cwd=C,check=True)
 remote=git('ls-remote','origin','refs/heads/v2-development',cwd=C).split()[0];assert remote==tip
 save(R/'PROMOTION_REMOTE_HEAD.json',dict(result='REMOTE_HEAD_VERIFIED_FILE_CHECKS_PENDING',starting_gate=g,integration_tip=tip,canonical_HEAD=tip,direct_remote_HEAD=remote,fast_forward_only=True,normal_push=True))
 production=[]
 for f in load(D/'PRODUCTION_MANIFEST.json'):
  rel=f['relative'];canonical=(C/rel).read_bytes();assert sha(canonical)==f['working_sha256'],rel
  url='https://raw.githubusercontent.com/LatinJosephus/latin-josephus-2/'+remote+'/'+rel
  request=urllib.request.Request(url,headers={'User-Agent':'LatinJosephus-XI-integration-verification'})
  with urllib.request.urlopen(request,timeout=30) as response:raw=response.read();status=response.status
  assert status==200 and sha(raw)==f['git_blob_sha256'],rel
  production.append(dict(relative=rel,canonical_working_sha256=sha(canonical),direct_remote_blob_sha256=sha(raw),certified_sha256=f['working_sha256'],remote_url=url,status=status))
 b=load(D/'BASELINE.json');scope=load(D/'INCOMING_SCOPE.json');protected=0
 for f in b['files']:
  if f['relative'] in scope['production']:continue
  assert sha((C/f['relative']).read_bytes())==f['canonical_working_sha256'],f['relative'];protected+=1
 for rel in scope['review']:assert (C/rel).read_bytes()==(S/rel).read_bytes(),rel
 for f in manifest['files']:assert sha((C/f['relative']).read_bytes())==f['sha256'],f['relative']
 assert sha((C/D.relative_to(ROOT)/'FILE_MANIFEST.json').read_bytes())==sha((D/'FILE_MANIFEST.json').read_bytes())
 assert git('rev-parse','HEAD',cwd=S)==b['source_tip'] and not git('status','--porcelain=v1',cwd=S)
 clean={label:not git('status','--porcelain=v1',cwd=where) for label,where in [('canonical',C),('integration',ROOT),('source',S)]};assert all(clean.values())
 preview=load(D/'PREVIEW_REFERENCE.json');assert sha(Path(preview['path']).read_bytes())==preview['sha256']
 receipt=dict(result='PASS',promoted_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),starting_canonical=g['local'],starting_remote=g['direct_remote'],source_tip=b['source_tip'],integration_tip=tip,canonical_HEAD=git('rev-parse','HEAD',cwd=C),direct_remote_HEAD=remote,fast_forward_only=True,normal_push=True,production=production,canonical_unrelated_working_files_unchanged=protected,incoming_review_files_byte_identical=len(scope['review']),manifest_entries_verified=len(manifest['files']),clean=clean,source_branch_preserved=True,public_preview_publication=False,preview_receipt_unchanged=True,report=str(C/D.relative_to(ROOT)/'REPORT.md'),integration_report=str(D/'REPORT.md'),file_manifest=str(D/'FILE_MANIFEST.json'),certificate=str(D/'CERTIFICATION.json'),counts=load(D/'CERTIFICATION.json')['counts'])
 save(R/'PROMOTION_RECEIPT.json',receipt);print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
