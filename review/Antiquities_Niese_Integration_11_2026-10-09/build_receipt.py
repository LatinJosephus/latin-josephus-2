from pathlib import Path
import json,sys,subprocess
sys.dont_write_bytecode=True
import hashlib
def digest(raw):return hashlib.sha256(raw).hexdigest()
D=Path(__file__).resolve().parent;ROOT=D.parents[1];context=json.loads((D/'BUILD_CONTEXT.json').read_text());site=Path(context['site']);out=Path(context['build_directory']);manifest=json.loads((D/'BUILD_INPUT_MANIFEST.json').read_text())
assert 'done in' in (out/'jekyll.log').read_text() and 'done in' in (out/'baseline-jekyll.log').read_text()
static=[]
for f in manifest:
 relative=f['relative'];source=ROOT/relative;assert digest(source.read_bytes())==f['sha256'],relative
 if relative.startswith('assets/') and not source.read_bytes().startswith(b'---') and site.joinpath(relative).is_file():
  assert digest(site.joinpath(relative).read_bytes())==f['sha256'],relative;static.append(f)
receipt=dict(status='PASS',**context,production_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),build_exit_code=0,build_recipe='build.sh',fresh_full_Jekyll_build=True,static_output_checks=static,logs={p.name:digest(p.read_bytes()) for p in [out/'jekyll.log',out/'baseline-jekyll.log',out/'dependencies.log']},postbuild_asset_replacement=False,registry_injection=False)
(D/'BUILD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8',newline='\n');print(f'PASS: {len(static)} source/output checks, full builds and {receipt["production_commit"]}')
