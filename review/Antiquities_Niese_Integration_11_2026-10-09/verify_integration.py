"""Verify exact incoming bytes and unrelated integration-start content."""
from pathlib import Path
import json,hashlib,subprocess,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
S=Path('C:/workspace/LatinJosephus-antiquities-niese-11')
C=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
def git(*a,cwd=ROOT):return subprocess.check_output(['git',*a],cwd=cwd).decode().strip()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(n,x):(D/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
 b=json.loads((D/'BASELINE.json').read_text());s=json.loads((D/'INCOMING_SCOPE.json').read_text());source=s['source_tip']
 assert git('rev-parse','antiquities-niese-11')==source and git('rev-parse','HEAD',cwd=S)==source
 assert not git('status','--porcelain=v1',cwd=S)
 subprocess.run(['git','merge-base','--is-ancestor',source,'HEAD'],cwd=ROOT,check=True)
 original=json.loads((S/'review/Antiquities_Niese_BookXI_2026-10-09/FILE_MANIFEST.json').read_text())
 for f in original['files']:assert sha((S/f['relative']).read_bytes())==f['sha256'],f['relative']
 def tree(ref):return {line.split('\t',1)[1]:line.split('\t',1)[0].split()[2] for line in git('ls-tree','-r',ref).splitlines()}
 current_tree=tree('HEAD');source_tree=tree(source)
 relatives=s['production']+s['review'];oids=[current_tree[p] for p in relatives]
 batch=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(oids)+'\n').encode(),cwd=ROOT)
 at=0;blob_hashes={}
 for oid in oids:
  end=batch.index(b'\n',at);head=batch[at:end].decode().split();assert head[:2]==[oid,'blob'];size=int(head[2])
  blob_hashes[oid]=sha(batch[end+1:end+1+size]);at=end+size+2
 incoming=[]
 for rel in s['production']+s['review']:
  a=(S/rel).read_bytes();z=(ROOT/rel).read_bytes();assert a==z,rel
  oid=current_tree[rel];assert oid==source_tree[rel],rel
  incoming.append(dict(relative=rel,role='production' if rel in s['production'] else 'certified review',working_sha256=sha(z),git_blob_oid=oid,git_blob_sha256=blob_hashes[oid]))
 protected=[]
 for f in b['files']:
  if f['relative'] in s['production']:continue
  assert sha((ROOT/f['relative']).read_bytes())==f['working_sha256'],f['relative']
  assert current_tree[f['relative']]==f['git_blob_oid'],f['relative']
  protected.append(f['relative'])
 changed=git('diff','--name-only',b['canonical'],'HEAD').splitlines()
 allowed=set(s['production']+s['review'])
 assert all(p in allowed or p.startswith('review/Antiquities_Niese_Integration_11_2026-10-09/') for p in changed)
 preview=json.loads((D/'PREVIEW_REFERENCE.json').read_text());assert sha(Path(preview['path']).read_bytes())==preview['sha256']
 save('PRODUCTION_MANIFEST.json',[x for x in incoming if x['role']=='production'])
 save('INTEGRATION_PRESERVATION.json',dict(result='PASS',canonical_start=b['canonical'],source_tip=source,tested_production_commit=git('rev-parse','HEAD'),incoming_files=len(incoming),incoming_review_files=len(s['review']),source_manifest_verified=len(original['files']),protected_baseline_files=len(protected),protected_production_files=len([p for p in protected if not p.startswith('review/')]),complete_source_ancestry=True,source_clean=True,source_branch_preserved=True,manual_conflict_resolutions=[],unrelated_bytes_and_blobs_unchanged=True,preview_receipt_unchanged=True,production_files=s['production']))
 print(json.dumps(dict(result='PASS',incoming=len(incoming),protected=len(protected),production=len(s['production']),source_clean=True)))
if __name__=='__main__':main()
