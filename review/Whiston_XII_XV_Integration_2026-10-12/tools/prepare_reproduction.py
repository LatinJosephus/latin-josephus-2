"""Recover the baseline fixtures from immutable objects in an owned checkout."""
import pathlib,subprocess,tarfile,io,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3]; BASE=ROOT.parent
PIN='43c3626493daa6768f9fc818679214035a62a281'
target=BASE/'baseline'
assert not target.exists(),'Use a fresh independent recovery directory; baseline already exists.'
archive=subprocess.check_output(['git','-C',str(ROOT),'archive',PIN,'assets','bin','_docs'])
target.mkdir()
with tarfile.open(fileobj=io.BytesIO(archive)) as t:
 t.extractall(target,filter='data')
site=BASE/'runtime/standard-site'
if not site.exists():
 assert (BASE/'preview').is_dir(),'Place the ZIP preview beside the recovered candidate.'
 site.parent.mkdir(exist_ok=True);shutil.copytree(BASE/'preview',site)
print('Frozen baseline and local preview prepared from offline recovery inputs.')
