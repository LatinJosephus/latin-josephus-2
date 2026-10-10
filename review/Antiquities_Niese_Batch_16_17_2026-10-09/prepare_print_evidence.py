"""Render primary print body pages; OCR suggestions remain unreviewed."""
from pathlib import Path
import sys,json,re,unicodedata,difflib,subprocess,concurrent.futures
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower().replace('ς','σ')) if c.isalpha())
def render(job):
    src,p,out=job;out.parent.mkdir(parents=True,exist_ok=True)
    if not out.exists():subprocess.run(['pdftoppm','-f',str(p),'-l',str(p),'-singlefile','-jpeg','-r','145',src,str(out.with_suffix(''))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    return str(out)
def main():
    sources=json.loads((BATCH/'PRINTED_SOURCES.json').read_text());ocr=json.loads((BATCH/'NIESE_ALL_OCR.json').read_text());loeb=json.loads((BATCH/'LOEB_ALL_OCR.json').read_text());jobs=[]
    for b,roman,span in [(16,'XVI',(18,80)),(17,'XVII',(83,151))]:
        d=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09';pages=[x for x in ocr if span[0]<=x['pdf_page']<=span[1]]
        rows=json.loads((d/'BOUNDARIES.json').read_text());previous=span[0]
        for row in rows:
            phrase=row['Greek_candidate_interval'];phrase=re.sub(r'^περιέχει ἡ βίβλος χρόνον ἐτῶν .*?\. ','',phrase)
            q=norm(' '.join(phrase.split()[:7]));hits=[]
            for page in pages:
                if q and q in norm(page['text']):hits.append(dict(pdf_page=page['pdf_page'],score=1.0,exact_OCR=True))
            if not hits:
                q=norm(' '.join(phrase.split()[:5]))
                for page in pages:
                    if not previous-1<=page['pdf_page']<=previous+3:continue
                    tokens=page['text'].split();best=(0,0)
                    for i in range(len(tokens)):
                        ratio=difflib.SequenceMatcher(None,q,norm(' '.join(tokens[i:i+5]))).ratio()
                        if ratio>best[0]:best=(ratio,i)
                    if best[0]>.67:hits.append(dict(pdf_page=page['pdf_page'],score=round(best[0],4),exact_OCR=False,nearby=' '.join(tokens[max(0,best[1]-8):best[1]+20])))
                hits.sort(key=lambda x:x['score'],reverse=True);hits=hits[:3]
            if hits and hits[0]['score']>=.84:previous=hits[0]['pdf_page']
            row['OCR_location_suggestions']=hits
        save(d/'GREEK_OCR_LOCATORS_UNREVIEWED.json',rows)
        for p in range(span[0],span[1]+1):jobs.append((sources['Niese']['path'],p,d/f'evidence/Niese-IV-PDF{p:03}.jpg'))
        save(d/'PRINT_PAGE_CENSUS_UNREVIEWED.json',dict(pdf_span=span,printed_span=[span[0]-14,span[1]-14],pages=pages,status='OCR_LOCATOR_AID_NO_VISUAL_REVIEW_CLAIM'))
        print(b,'located suggestions',sum(bool(x['OCR_location_suggestions']) for x in rows),'/',len(rows),flush=True)
    for p in [5,17,81,82,152]:jobs.append((sources['Niese']['path'],p,BATCH/f'evidence/Niese-IV-PDF{p:03}.jpg'))
    # Loeb actual title and source endpoint pages are located from its contents.
    for p in [7,9,10,224,225,370,371,372,373,374,375,376,377,378,379,380,381,590,591,592,593]:
        jobs.append((sources['Loeb']['path'],p,BATCH/f'evidence/Loeb-VIII-PDF{p:03}.jpg'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:rendered=list(ex.map(render,jobs))
    save(BATCH/'RENDERED_SOURCE_MANIFEST.json',[dict(path=p,bytes=Path(p).stat().st_size) for p in rendered])
    print('Rendered',len(rendered),'pages; none automatically promoted to reviewed.',flush=True)
if __name__=='__main__':main()
