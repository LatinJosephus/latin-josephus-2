"""Resolve ORIGINAL XML controls independently of browser DOM and new marker arithmetic."""
from prepare import *
from mixed_mapper import Book
from xml.parsers import expat
from bisect import bisect_left
models={l:Book(PACK/'frozen-inputs'/f'{l}.xml') for l in ['Latin','Greek','English']}
records=json.loads((PACK/'STRUCTURAL_CONTROLS.json').read_text(encoding='utf-8'))
byid={r['id']:r for r in records}
maps={}
for lang,m in models.items():
    parser=expat.ParserCreate();starts=[]
    parser.StartElementHandler=lambda name,attrs:starts.append(parser.CurrentByteIndex)
    parser.Parse(m.raw,True)
    elements=[e for e in m.tree.iter() if isinstance(e.tag,str)];assert len(elements)==len(starts)
    raw_by_element={e:k for e,k in zip(elements,starts)}
    positions=[(k,n['book_start']+i) for n in m.nodes for i,k in enumerate(n['raw_positions'])]
    maps[lang]=(raw_by_element,positions,[p[0] for p in positions])
def point(lang,loc):
    m=models[lang]
    assert loc['available']=='true',loc
    target=m.tree.xpath('//*[@xml:id=$v]',v=loc['target']);assert len(target)==1
    e=target[0]
    if loc['kind']=='element-edge':
        for step in loc['edge'].split('/'):
            tag,n=re.fullmatch(r'([\w-]+)\[(\d+)\]',step).groups()
            e=[c for c in e if isinstance(c.tag,str) and etree.QName(c).localname==tag][int(n)-1]
    raw_by_element,positions,raw_positions=maps[lang]
    k=raw_by_element[e];i=bisect_left(raw_positions,k)
    offset=positions[i][1] if i<len(positions) else len(m.stream)
    unit=next(u for u in m.units if u['id']==loc['paragraph'])
    assert offset-unit['book_start']==int(loc['offset']),(lang,loc,offset-unit['book_start'])
    # Frozen display incipits normalize incidental paragraph whitespace.
    normalize=lambda s:re.sub(r'\s+',' ',s).strip()
    assert normalize(m.stream[offset:]).startswith(normalize(loc['anchor'])),(lang,loc)
    return dict(book_offset=offset,raw_byte=k,kind=loc['kind'],target=loc['target'],source_locator=loc)
expected=[]
for r in records:
    if r.get('scheme') not in ['chapter','subchapter','bamberg']:continue
    languages={}
    for lang,m in models.items():
        a=point(lang,r[lang]);end=r.get('end','BOOK_END')
        z=point(lang,byid[end][lang]) if end!='BOOK_END' else dict(book_offset=len(m.stream),raw_byte=len(m.raw),kind='BOOK_END')
        assert a['book_offset']<z['book_offset']
        languages[lang]=dict(start=a,end=z,text=m.stream[a['book_offset']:z['book_offset']],source_sha256=sha(m.raw))
    expected.append(dict(id=r['id'],scheme=r['scheme'],languages=languages))
save(PACK/'INDEPENDENT_STRUCTURAL_SPANS.json',expected)
print('Independently verified',len(expected),'complete physical spans and all source offset/anchor values in three languages.')
