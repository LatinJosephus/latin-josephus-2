"""Constants and byte/Git helpers for this isolated canonical integration."""
from pathlib import Path
import hashlib,json,subprocess,sys,shutil,re
from lxml import etree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
ROOT=D.parents[1]
CANON=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
SOURCE_ROOT=Path(r'C:\workspace\LatinJosephus-antiquities-niese-18-19')
R=Path(r'C:\workspace\Antiquities-Niese-18-19-integration-runtime-20261010')
START='08f46c0fdfa4639d49c0b13559fa590b6cce314b'
SOURCE='5aa64ebc1d3281287e247f359b5718918ffb9de6'
BASE='9527578f361d48adb3094110254e627292bca2c5'
BRANCH='antiquities-niese-18-19-integration'
NS={'t':'http://www.tei-c.org/ns/1.0'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(name,x):
    p=Path(name)
    if not p.is_absolute():p=D/p
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def info(p):
    raw=p.read_bytes();return dict(path=str(p),bytes=len(raw),sha256=sha(raw),CRLF=raw.count(b'\r\n'),LF_without_CR=raw.count(b'\n')-raw.count(b'\r\n'),BOM=raw.startswith(b'\xef\xbb\xbf'))
def tree(commit):
    result={}
    for item in git('ls-tree','-r','-z',commit).split(b'\0'):
        if not item:continue
        metadata,path=item.split(b'\t',1);mode,kind,oid=metadata.decode().split()
        assert kind=='blob';result[path.decode()]=dict(mode=mode,oid=oid)
    return result
def assert_blob(raw,oid):assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==oid
