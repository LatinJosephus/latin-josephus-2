"""Render read-only printed sources and extract OCR solely as a locator aid."""
from pathlib import Path
import json, subprocess, concurrent.futures
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]
BATCH=Path(__file__).resolve().parent
RUNTIME=Path(r'C:\workspace\Antiquities-Niese-14-15-runtime-20261009')
def packet(n): return ROOT/f'review/Antiquities_Niese_Book{ {14:"XIV",15:"XV"}[n]}_2026-10-09'
def render(source,page,destination,dpi=125):
    destination.parent.mkdir(parents=True,exist_ok=True)
    if not destination.exists():
        subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-jpeg','-r',str(dpi),source,str(destination.with_suffix(''))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    return str(destination)
def main():
    jobs=[]
    niese=json.loads((BATCH/'NIESE_SOURCE.json').read_text())['primary']['path']
    for b,pages in [(14,[5,306,310,311,312,398,399,401,402]),(15,[403,404,405,406,480,481])]:
        d=packet(b); src=json.loads((d/'PRINTED_SOURCES.json').read_text())
        doc=PdfReader(src['Loeb']['path'])
        preface=[]
        for i in range(min(30,len(doc.pages))):
            txt=doc.pages[i].extract_text()
            preface.append(dict(pdf_page=i+1,OCR=txt))
        (d/'LOEB_PREFACE_OCR.json').write_text(json.dumps(preface,ensure_ascii=False,indent=2),encoding='utf8')
        for p in pages: jobs.append((niese,p,d/f'evidence/Niese-III-PDF{p:03}.jpg'))
        for p in range(1,15): jobs.append((src['Loeb']['path'],p,d/f'evidence/Loeb-title-PDF{p:03}.jpg'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        result=list(ex.map(lambda j:render(*j),jobs))
    (BATCH/'INITIAL_RENDERING.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print('Rendered',len(result),'read-only source pages; visual inspection still required.')
if __name__=='__main__':main()
