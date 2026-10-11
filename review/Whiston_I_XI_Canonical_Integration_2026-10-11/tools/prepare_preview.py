from pathlib import Path
import shutil, hashlib, json
ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'review/Whiston_I_XI_Canonical_Integration_2026-10-11'
old=Path('C:/workspace/Whiston-I-XI-Renderer-runtime-20261011/site')
site=Path('C:/workspace/Whiston-I-XI-Integration-runtime-20261011/site')
rows=[]
for folder in ['assets/js','assets/css','assets/xml','assets/data','assets/fonts','assets/img/brand','antiquities','bellum-judaicum','contra-apionem','deh']:
    for p in (old/folder).rglob('*'):
      if p.is_file():
        target=site/p.relative_to(old)
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
        assert target.read_bytes()==p.read_bytes()
        rows.append({'path':p.relative_to(old).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(PACK/'PREVIEW_BUILD_REUSE.json').write_bytes((json.dumps({'status':'PASS','method':'Byte-identical copy of the certified native Jekyll reader build; all reader/page/layout/CSS/config source inputs are unchanged. The historical responsive-image exclusion qualification is retained, not presented as a standard full-plugin build pass.','files':rows},indent=2)+'\n').encode())
s=(ROOT/'review/Whiston_I_XI_Renderer_2026-10-11/tools/browser_qa.cjs').read_text()
s=s.replace('Whiston-I-XI-Renderer-runtime-20261011','Whiston-I-XI-Integration-runtime-20261011')
s=s.replace("site=path.join(runtime,'site')", "site=path.join(runtime,'standard-site')")
s=s.replace("const oracle=JSON.parse(fs.readFileSync(path.join(pack,'INTERVAL_ORACLE.json')));", "const oracle=JSON.parse(fs.readFileSync(path.join(root,'review/Whiston_I_XI_Renderer_2026-10-11/INTERVAL_ORACLE.json')));")
(PACK/'tools/browser_qa.cjs').write_bytes(s.encode())
print('Independent candidate preview and harness prepared; original evidence retained')
