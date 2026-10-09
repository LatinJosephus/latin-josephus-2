"""OCR suggestions for independently reviewed Greek starts. No automatic promotion."""
from pathlib import Path
import json, re, sys, unicodedata, difflib, concurrent.futures, subprocess
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]
BATCH=Path(__file__).resolve().parent
sys.path.insert(0,str(BATCH)); from inspect_sources import packet,render
def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFD',s.lower().replace('ς','σ')) if c.isalpha())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def run():
    src=json.loads((BATCH/'NIESE_SOURCE.json').read_text())['primary']['path']
    doc=PdfReader(src); jobs=[]
    for b,span,loebpages in [(14,(311,402),[460,461,714,715]),(15,(405,481),[18,19,222,223])]:
        d=packet(b); rows=json.loads((d/'BOUNDARIES.json').read_text()); pages=[]
        for p in range(span[0],span[1]+1):
            text=doc.pages[p-1].extract_text()
            pages.append(dict(pdf_page=p,printed_page=p-72,OCR=text,normalized=norm(text)))
            jobs.append((src,p,d/f'evidence/Niese-III-PDF{p:03}.jpg'))
        save(d/'NIESE_BODY_OCR.json',pages)
        previous_page=span[0]
        for row in rows:
            phrase=row['Greek']; words=phrase.split(); needle=norm(' '.join(words[:8])); candidates=[]
            for page in pages:
                at=page['normalized'].find(needle)
                if at>=0:candidates.append(dict(pdf_page=page['pdf_page'],exact_OCR=True,score=1.0))
            if not candidates:
                for page in pages:
                    if not previous_page-1<=page['pdf_page']<=previous_page+3:continue
                    tokens=page['OCR'].split(); q=norm(' '.join(words[:5])); best=(0,0)
                    for i in range(len(tokens)):
                        val=difflib.SequenceMatcher(None,q,norm(' '.join(tokens[i:i+5]))).ratio()
                        if val>best[0]:best=(val,i)
                    if best[0]>.68:candidates.append(dict(pdf_page=page['pdf_page'],exact_OCR=False,score=round(best[0],4),nearby_OCR=' '.join(tokens[max(0,best[1]-12):best[1]+30])))
                candidates.sort(key=lambda x:x['score'],reverse=True);candidates=candidates[:3]
            row['OCR_location_suggestions']=candidates
            if candidates and candidates[0]['score']>=.85:previous_page=candidates[0]['pdf_page']
        save(d/'GREEK_OCR_LOCATORS.json',rows); save(d/'NIESE_BODY_OCR.json',pages)
        controls=json.loads((d/'PRINTED_SOURCES.json').read_text()); loeb=PdfReader(controls['Loeb']['path'])
        evidence=[]
        for p in loebpages:
            evidence.append(dict(pdf_page=p,OCR=loeb.pages[p-1].extract_text()))
            jobs.append((controls['Loeb']['path'],p,d/f'evidence/Loeb-body-PDF{p:03}.jpg'))
        save(d/'LOEB_ENDPOINT_OCR.json',evidence)
        print(b,'OCR candidates',sum(bool(x['OCR_location_suggestions']) for x in rows),'/',len(rows),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: list(ex.map(lambda j:render(*j),jobs))
    print('All body images rendered. OCR is an aid, not print verification.',flush=True)
if __name__=='__main__': run()
