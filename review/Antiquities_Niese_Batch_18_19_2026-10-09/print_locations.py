from reconnaissance import *
import unicodedata, difflib, concurrent.futures
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower().replace('ς','σ')) if c.isalpha())
def render(source,n,out,dpi=130):
    out.parent.mkdir(parents=True,exist_ok=True)
    if not out.exists():subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-singlefile','-jpeg','-r',str(dpi),str(source),str(out.with_suffix(''))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    return info(out)
def main():
    pages=json.loads((PACK/'NIESE_PAGE_TEXT.json').read_text(encoding='utf8'))
    for p in pages:p['normalized']=norm(p['OCR'])
    for b,last in [(18,379),(19,366)]:
        d=packet(b);rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'))
        for r in rows:
            phrase=r['Greek_text'].strip()
            if r['number']==1:phrase=phrase[phrase.find('Κυρίνιος' if b==18 else 'Γάιος'):]
            needle=norm(' '.join(phrase.split()[:7]))
            hits=[p['PDF_page'] for p in pages if needle and needle in p['normalized']]
            r['print_OCR_candidates']=hits
        save(d/'IDENTITIES.json',rows)
        for n in [1,2,63,64,116,119,257,292,last-1,last]:
            if n<=last:print(b,n,rows[n-1]['print_OCR_candidates'],rows[n-1]['Greek_text'][:85])
    print('OCR locations are unverified suggestions, never printed evidence.')
if __name__=='__main__':main()
