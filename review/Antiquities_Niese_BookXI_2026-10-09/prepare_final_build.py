from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
from mixed_mapper import digest
D=Path(__file__).resolve().parent;ROOT=D.parents[1];R=Path('C:/workspace/Antiquities-Niese-11-runtime-20261009')
target=R/'final-source';out=R/'final-build';assert not target.exists() and not out.exists(),'Do not replace an existing build or source directory'
target.mkdir();out.mkdir();files=json.loads((D/'ALL_BASE_FILES.json').read_text(encoding='utf8'));manifest=[]
paths=[x['relative'] for x in files if not x['relative'].startswith('review/')]+['assets/xml/antiquities/niese/book-11.json']
for relative in paths:
 p=ROOT/relative;q=target/relative;q.parent.mkdir(parents=True,exist_ok=True);raw=p.read_bytes();q.write_bytes(raw);manifest.append(dict(relative=relative,bytes=len(raw),sha256=digest(raw)))
(D/'BUILD_INPUT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')
print(f'Frozen {len(manifest)} production files into {target}; build output {out}')
