"""Read-only targeted prose and topology inspection; does not adopt boundaries."""
from pathlib import Path
import sys,json,re
from lxml import etree
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,NS

def model(b,l):return Book(ROOT/f'assets/xml/antiquities/{l}/book-{b}.xml')

def overview():
    reg=etree.parse(str(ROOT/'assets/xml/antiquities/structure.xml'))
    for b in [16,17]:
        print('BOOK',b)
        for lang in ['Greek','Latin','English']:
            m=model(b,lang)
            print(lang,'paragraphs',len(m.units),'narrative',sum(not u['excluded_reason'] for u in m.units),'chars',len(m.stream),'labels',len(m.labels))
            print('opening:',m.stream[:450]);print('ending:',m.stream[-450:])
            for t in ['div2','floatingText','argument','gap','unclear','corr','note','milestone']:
                els=m.tree.xpath(f'//t:{t}',namespaces=NS)
                if t=='milestone':print(t,[(x.get('unit'),x.get('n')) for x in els if x.get('unit')]);continue
                if t in ['div2','argument','floatingText']:print(t,[(dict(x.attrib),len(''.join(x.itertext()))) for x in els]);continue
                print(t,len(els))
        for item in reg.xpath('//t:list/t:item',namespaces=NS):
            fields=item.xpath('t:fs/t:f[t:string]',namespaces=NS)
            d={f.get('name'):''.join(f.itertext()).strip() for f in fields}
            if d.get('book')!=str(b):continue
            if d.get('canonical-niese') not in (['1','235','356','368'] if b==16 else ['1','106','146','299']):continue
            print('STRUCTURAL',json.dumps(dict(id=item.get('{http://www.w3.org/XML/1998/namespace}id'),fields=d),ensure_ascii=False))
            for f in item.xpath('t:fs/t:f[t:fs]',namespaces=NS):
                print(f.get('name'),json.dumps({v.get('name'):''.join(v.itertext()).strip() for v in f.xpath('t:fs/t:f',namespaces=NS)},ensure_ascii=False))

def passage(b,first,last):
    g=model(b,'Greek');l=model(b,'Latin');e=model(b,'English')
    labels=[x for x in g.labels if re.fullmatch(r'\[\d+\]',x['text']) and not g.units[x['unit']-1]['excluded_reason']]
    starts={int(x['text'][1:-1]):g.first_content(x['book_offset']) for x in labels};starts.setdefault(1,0)
    for n in range(first,last+1):
        at=starts[n];unit=g.locate(at)['stable_id'];end=starts.get(n+1,len(g.stream))
        print('GREEK',n,unit,g.stream[at:end])
    ids={g.locate(starts[n])['stable_id'].split('-num')[-1] for n in range(first,last+1)}
    # Include full aligned context and neighbour paragraphs for actual review.
    for lang,m in [('Latin',l)]:
        indices=[i for i,u in enumerate(m.units) if u['id'].split('-num')[-1] in ids]
        if not indices:continue
        for i in range(max(0,min(indices)-1),min(len(m.units),max(indices)+2)):
            u=m.units[i]
            if u['excluded_reason']:continue
            print(lang,u['index'],u['id'],u['text'])

if len(sys.argv)==1:overview()
else:passage(*map(int,sys.argv[1:]))
