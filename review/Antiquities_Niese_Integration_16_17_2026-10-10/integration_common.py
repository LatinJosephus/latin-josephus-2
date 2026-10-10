from pathlib import Path
import sys,json,hashlib,subprocess,datetime
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
CAN=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
SOURCE_ROOT=Path('C:/workspace/LatinJosephus-antiquities-niese-16-17')
R=Path('C:/workspace/Antiquities-Niese-16-17-integration-runtime-20261010')
START='cd6d69e1a3c33a7e8d5a0dabc7c0deda39d0eac9'
SOURCE='d3b8bf9f8b10aca6748d40c37fd40e582afdcba5'
SOURCE_BASE='65b3256fe202a06e33a59aa2d1dcbd7107358271'
FOLDERS=[f'review/Antiquities_Niese_{n}_2026-10-09/' for n in ['BookXVI','BookXVII','Batch_16_17']]
PRODUCTION=['assets/js/renderTei.js',*[f'assets/xml/antiquities/{l}/book-{b}.xml' for b in [16,17] for l in ['Latin','Greek']],*[f'assets/xml/antiquities/niese/book-{b}.json' for b in [16,17]]]
def git(*args,cwd=ROOT):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=cwd)
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(x):return hashlib.sha256(x).hexdigest()
def save(name,x):
    p=Path(name) if isinstance(name,Path) else D/name
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def ancestor(a,b):return subprocess.run(['git','merge-base','--is-ancestor',a,b],cwd=ROOT).returncode==0
def inventory(commit,working):
    paths=git('ls-tree','-rz','--full-tree',commit).split(b'\0');out=[]
    for entry in paths:
        if not entry:continue
        meta,path=entry.split(b'\t',1);mode,kind,oid=meta.decode().split();relative=path.decode('utf8')
        assert kind=='blob';raw=(working/relative).read_bytes()
        out.append(dict(path=relative,bytes=len(raw),sha256=sha(raw),blob=oid,mode=mode))
    return out
