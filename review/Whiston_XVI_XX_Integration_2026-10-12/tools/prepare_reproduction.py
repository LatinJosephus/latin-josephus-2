"""Prepare an independently recovered delivery for live browser reproduction."""
import pathlib,subprocess,shutil,json
PACK=pathlib.Path(__file__).resolve().parent.parent;ROOT=PACK.parents[1];BASE=ROOT.parent
PIN=json.loads((PACK/'BASELINE.json').read_text(encoding='utf-8-sig'))['commit'];bundle=BASE/'candidate-full.bundle'
assert bundle.exists() and not (BASE/'baseline').exists() and (BASE/'preview').is_dir()
subprocess.check_call(['git','init','--separate-git-dir',str(BASE/'baseline.git'),str(BASE/'baseline')])
g=lambda *a:subprocess.check_call(['git','-C',str(BASE/'baseline'),*a])
g('config','core.autocrlf','false');g('fetch',str(bundle),'HEAD');g('checkout','--detach',PIN)
destination=BASE/'runtime/standard-site';assert not destination.exists();shutil.copytree(BASE/'preview',destination)
print('Private pinned baseline and literal archived build ready; run browser reproduction in this recovered task')
