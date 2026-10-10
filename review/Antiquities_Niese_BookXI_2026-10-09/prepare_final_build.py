from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
from mixed_mapper import digest
D=Path(__file__).resolve().parent;ROOT=D.parents[1];R=Path('C:/workspace/Antiquities-Niese-11-runtime-20261009')
suffix='-'+sys.argv[1] if len(sys.argv)>1 else ''
target=R/('final-source'+suffix);out=R/('final-build'+suffix);assert not target.exists() and not out.exists(),'Do not replace an existing build or source directory'
target.mkdir();out.mkdir();files=json.loads((D/'ALL_BASE_FILES.json').read_text(encoding='utf8'));manifest=[]
paths=[x['relative'] for x in files if not x['relative'].startswith('review/')]+['assets/xml/antiquities/niese/book-11.json']
for relative in paths:
 p=ROOT/relative;q=target/relative;q.parent.mkdir(parents=True,exist_ok=True);raw=p.read_bytes();q.write_bytes(raw);manifest.append(dict(relative=relative,bytes=len(raw),sha256=digest(raw)))
(D/'BUILD_INPUT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')
(D/'BUILD_CONTEXT.json').write_text(json.dumps(dict(source=str(target),site=str(out/'site'),baseline_site=str(out/'baseline-site'),build_directory=str(out),baseline='65b3256fe202a06e33a59aa2d1dcbd7107358271',image='ruby@sha256:dba270af6994f64e45ee3dd2b85225a2a0d01f29c04508c7a3c7c8dbf59d2a85',purpose='Fresh full Jekyll builds; no post-build asset replacement'),indent=2)+'\n',encoding='utf8',newline='\n')
print(f'Frozen {len(manifest)} production files into {target}; build output {out}')
