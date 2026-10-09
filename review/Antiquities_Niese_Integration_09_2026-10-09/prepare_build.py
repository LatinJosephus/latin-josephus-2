from pathlib import Path
import json,subprocess,tarfile,hashlib
P=Path(__file__).resolve().parent;W=P.parents[1]
R=Path('C:/workspace/Antiquities-Niese-09-integration-runtime-20261009')
b=json.loads((P/'BASELINE.json').read_text(encoding='utf8'))
assert json.loads((R/'OWNERSHIP.json').read_text(encoding='utf8'))['integration_worktree']==str(W)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=W).decode().strip()
assert subprocess.run(['git','merge-base','--is-ancestor',b['certified_source_HEAD'],head],cwd=W).returncode==0
assert subprocess.run(['git','merge-base','--is-ancestor',b['canonical_initial_HEAD'],head],cwd=W).returncode==0
dest=R/'baseline';out=R/'build'
assert not (P/'BUILD_PLAN.json').exists(),'Existing completed preparation must not be overwritten'
assert not dest.exists() or not list(dest.iterdir()),'Only the empty directory from this assignment preparation may be resumed'
assert not (out/'site').exists() and not (out/'baseline-site').exists()
dest.mkdir(exist_ok=True);out.mkdir(exist_ok=True);archive=R/'canonical-before-IX.tar'
subprocess.run(['git','archive','--format=tar','-o',str(archive),b['canonical_initial_HEAD']],cwd=W,check=True)
with tarfile.open(archive) as t:t.extractall(dest,filter='data')
plan={'implementation_HEAD':head,'baseline_HEAD':b['canonical_initial_HEAD'],'archive':str(archive),
 'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'runtime':str(R),'source_read_only':True,
 'build_script':str(P/'build.sh'),'image':'sha256:dba270af6994f64e45ee3dd2b85225a2a0d01f29c04508c7a3c7c8dbf59d2a85',
 'build_configuration':'Complete repository Jekyll configuration; no omitted plugins or static refresh'}
(P/'BUILD_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf8',newline='\n')
print('Prepared fresh integration and exact current-canonical baseline builds at '+head)
