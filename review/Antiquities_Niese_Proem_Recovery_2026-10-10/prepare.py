from pathlib import Path
import json, hashlib, subprocess, shutil, re
from pypdf import PdfReader
from lxml import etree
ROOT=Path(__file__).resolve().parents[2]
PACK=Path(__file__).resolve().parent
CANON=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
BASE='4f88fc1483ec14d418c678004e13bc2b6741a2b7'
RUNTIME=Path(r'C:\workspace\Antiquities-Niese-Proem-Recovery-runtime-20261010')
NS={'t':'http://www.tei-c.org/ns/1.0'}
ID='{http://www.w3.org/XML/1998/namespace}id'
def sha(x): return hashlib.sha256(x).hexdigest()
def save(p,x): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def info(p):
    b=p.read_bytes();return dict(path=str(p.resolve()),sha256=sha(b),bytes=len(b),CRLF=b.count(b'\r\n'),LF_without_CR=b.count(b'\n')-b.count(b'\r\n'),encoding='UTF-8',BOM=b.startswith(b'\xef\xbb\xbf'))
def git(*a): return subprocess.check_output(['git',*a],cwd=ROOT)
def render(p,n,label):
    out=PACK/f'evidence/{label}-PDF{n:03}.jpg';out.parent.mkdir(exist_ok=True)
    subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-singlefile','-jpeg','-r','155',str(p),str(out.with_suffix(''))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    return dict(PDF_page=n,**info(out))
def main():
    assert not (PACK/'BASELINE.json').exists()
    RUNTIME.mkdir(exist_ok=True)
    frozen=PACK/'frozen-inputs';frozen.mkdir(exist_ok=True)
    governing=Path(r'C:\Users\Pollard_R\Mon disque\Downloads from Chrome (11-08-2026 onward)\WORKBOT_Antiquities_Proem_Niese_2026-10-10.txt')
    shutil.copyfile(governing,PACK/governing.name)
    records=[]
    for l in ['Greek','Latin','English']:
        p=ROOT/f'assets/xml/antiquities/{l}/preface.xml';b=p.read_bytes();shutil.copyfile(p,frozen/f'{l}.xml')
        doc=etree.fromstring(b);ps=doc.xpath('//t:div1/t:p[@xml:id]',namespaces=NS)
        text=''.join(''.join(x.itertext()) for x in ps)
        blob=git('show',BASE+':'+p.relative_to(ROOT).as_posix())
        records.append(dict(language=l,**info(p),canonical=info(CANON/p.relative_to(ROOT)),git_blob_sha256=sha(blob),git_blob_bytes=len(blob),incipit=text[:200],explicit=text[-200:],paragraphs=[x.get(ID) for x in ps],authority='Existing canonical approved project source; user expressly authorizes reversible segmentation',extent='Antiquities I.1-26, standalone Proem'))
    pdfs=[]
    for label,p in [('Niese',Path(r'C:\workspace\Niese Antiquities\batch-01\operajosephus01joseuoft.pdf')),('Loeb',next(Path(r'C:\workspace\Loeb Josephus Volumes').glob('*I-IV*')))]:
        doc=PdfReader(p)
        pdfs.append(dict(label=label,**{**info(p),'encoding':'PDF'},pages=len(doc.pages),metadata={str(k):str(v) for k,v in doc.metadata.items()}))
        rows=[dict(PDF_page=i+1,text=doc.pages[i].extract_text()) for i in range(min(115,len(doc.pages)))]
        save(PACK/f'{label.upper()}_PAGE_TEXT.json',rows)
    files=git('ls-tree','-r','--full-tree',BASE).decode().splitlines()
    save(PACK/'PROTECTED_GIT_OBJECTS.json',{line.split('\t')[1]:line.split()[2] for line in files})
    save(PACK/'BASELINE.json',dict(frozen_base=BASE,canonical_branch='v2-development',direct_remote=BASE,remote_method='Successful read-only git ls-remote after sandbox DNS failure',worktree=str(ROOT),branch='antiquities-niese-proem',runtime=str(RUNTIME),governing=info(governing),sources=records,PDFs=pdfs,prior_population=7350,Book_I_population=320,proposed_proem_population=26,proposed_total=7376,canonical_entry_status='clean',isolation='No canonical production modification, merge, push, preview export or publication authorized'))
    print(json.dumps(dict(sources=records,PDFs=pdfs),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
