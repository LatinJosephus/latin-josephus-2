import os,json,subprocess,hashlib,datetime
from pathlib import Path
T=Path('C:/workspace/Antiquities-VII2-6-Whiston-Integration-runtime-20261010');W=Path('C:/workspace/LatinJosephus-antiquities-vii2-6-whiston-context-integration')
H='705aebf7a05681012d239707baed5ea2bdd806d2'
env=os.environ.copy();env['GIT_OPTIONAL_LOCKS']='0'
def git(*a):return subprocess.check_output(['git','-C',str(W),*a],env=env).decode('utf-8').strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
start=json.loads((T/'START_RECEIPT.json').read_text())
counts={}
for name,state in start['protected'].items():
 p=Path(state['path'])
 assert all(sha(p/f)==h for f,h in state['files'].items()),'Protected source changed '+name
 counts[name]=len(state['files'])
 print('PASS protected original bytes',name,counts[name],flush=True)
b=T/'baseline-source';xml={str(p.relative_to(b)).replace('\\','/'):sha(p) for p in (b/'assets/xml').rglob('*.xml')}
regs={str(p.relative_to(b)).replace('\\','/'):sha(p) for p in (b/'assets/xml/antiquities/niese').glob('*.json')}
assert len(xml)==143 and len(regs)==14
assert all(sha(W/f)==h for f,h in {**xml,**regs}.items())
assets=[]
for mode in ['baseline','candidate-final']:
 root=T/(mode+'-site');assets.append({p.relative_to(root).as_posix():sha(p) for p in (root/'assets').rglob('*') if p.is_file()})
assert assets[0].keys()==assets[1].keys()
delta=[f for f in assets[0] if assets[0][f]!=assets[1][f]]
assert delta==['assets/js/renderTei.js'],delta
production=sha(W/'assets/js/renderTei.js')
assert production==assets[1]['assets/js/renderTei.js']=='c4741903c21c4cc0e4629cdca4d951a5c64ffcab6da5e44e40aaaebcc0e3cad3'
changed=git('diff','--name-only',H,'HEAD').splitlines()
assert [f for f in changed if not f.startswith('review/')]==['assets/js/renderTei.js']
git('diff','--check',H,'HEAD')
out={'result':'PASS','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline':H,
'integration_merge':git('rev-parse','HEAD'),'production_files':delta,'production_SHA256':{delta[0]:production},
'XML_files_byte_identical':len(xml),'Niese_registry_files_byte_identical':len(regs),
'XML_SHA256':xml,'Niese_registry_SHA256':regs,'protected_original_file_counts_byte_identical':counts,
'built_asset_count':len(assets[1]),'sole_built_asset_difference':delta,'tested_source_and_built_renderer_byte_identical':True,
'canonical_original_files_are_untouched_before_promotion':True}
(T/'SOURCE_INTEGRITY.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
(T/'BUILD_ASSET_HASHES.json').write_text(json.dumps({'baseline':assets[0],'integrated':assets[1]},indent=2)+'\n',encoding='utf-8',newline='\n')
print('PASS 143 XML; 14 registries; sole production delta '+delta[0],flush=True)