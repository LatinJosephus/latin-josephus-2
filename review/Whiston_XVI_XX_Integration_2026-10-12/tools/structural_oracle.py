"""Independent XML text-coordinate projections of registered containing views."""
import pathlib,json,re,xml.etree.ElementTree as ET,hashlib,collections
PACK=pathlib.Path(__file__).resolve().parent.parent;ROOT=PACK.parents[1]
NS='{http://www.tei-c.org/ns/1.0}';ID='{http://www.w3.org/XML/1998/namespace}id'
norm=lambda s:re.sub(r'\s+',' ',s).strip()
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def value(e):
 if e.tag==NS+'fs':return {f.get('name'):value(f[0]) for f in e}
 if e.tag==NS+'vColl':return [value(c) for c in e]
 return e.text or ''
structure=ET.parse(ROOT/'assets/xml/antiquities/structure.xml')
registries={kind:[dict(id=e.get(ID),**value(e.find(NS+'fs'))) for e in next(e for e in structure.iter(NS+'list') if e.get('type')==kind) if e.tag==NS+'item'] for kind in ['traditional-boundaries','bamberg-boundaries','alignment-ranges']}
boundary={r['id']:r for kind in ['traditional-boundaries','bamberg-boundaries'] for r in registries[kind]}
books=list(load(PACK/'CONTAINING_ORACLE.json')['whole']);rows=[];counts=collections.Counter()
for book in books:
 filename='preface.xml' if book=='preface' else f'book-{int(book):02}.xml'
 root=ET.fromstring((PACK/'certified'/filename).read_bytes());body=root.find('.//'+NS+'body')
 parts=[];positions={};ids={};pos=0
 def emit(s):
  global pos
  if s:parts.append(s);pos+=len(s)
 def walk(e):
  positions[e]=[pos,None]
  if e.get(ID):ids[e.get(ID)]=e
  if e.tag.removeprefix(NS) not in ['num','note','milestone']:
   emit(e.text)
   for c in e:walk(c);emit(c.tail)
  positions[e][1]=pos
 walk(body);text=''.join(parts)
 # Endpoints are measured from the frozen source tree, not a rendered DOM Range.
 def point(loc):
  if loc.get('kind')=='book-end':return len(text)
  loc=loc.get('boundary-start',loc)
  if loc.get('available')!='true':return None
  e=ids.get(loc['target']);assert e is not None,loc
  kind=loc['kind']
  if kind=='niese-milestone':e=next(c for c in e.iter(NS+'milestone') if c.get('unit')=='niese' and c.get('n')==loc['n'])
  if kind=='element-edge':
   registry=ROOT/f'assets/xml/antiquities/niese/{filename.replace(".xml",".json")}'
   units=load(registry).get('structuralMilestoneUnits') if registry.exists() else None
   for step in loc['edge'].split('/'):
    m=re.fullmatch(r'([\w-]+)\[(\d+)\]',step);assert m,step
    children=[c for c in e if c.tag==NS+m[1] and (m[1]!='milestone' or not units or c.get('unit') in units)]
    e=children[int(m[2])-1]
  return positions[e][1 if kind=='paragraph-end' else 0]
 def interval(row):
  loc=row['English'];end=row.get('endLocator') or boundary.get(row.get('end'),{}).get('English') or {'kind':'book-end'}
  spans=loc.get('spans') or [dict(start=loc,end=end)];out=[]
  for span in spans:
   a,b=point(span['start']),point(span['end'])
   if a is None or b is None:return None
   assert a<=b,(row['id'],a,b)
   out.append(text[a:b])
  return norm(''.join(out))
 for kind in ['traditional-boundaries','bamberg-boundaries']:
  for r in registries[kind]:
   if not ((book=='preface' and r.get('context')=='Proem') or (book!='preface' and r.get('context')!='Proem' and int(r['book'])==int(book))):continue
   expected=interval(r);scheme=r['scheme'];counts[scheme]+=1
   query=f'book={book}'
   if scheme=='bamberg':query+='&bamberg='+r['id']
   else:
    if r['chapter']:query+='&chapter='+r['chapter']
    if scheme=='subchapter':query+='&subchapter='+r['subchapter']
   rows.append(dict(book=book,scheme=scheme,id=r['id'],query=query,text=expected,readerNote=r.get('reader-note'),available=expected is not None))
 latin=ET.parse(ROOT/'assets/xml/antiquities/Latin'/filename);prefix='latin-preface-num' if book=='preface' else f'latin-book{int(book):02}-num'
 units=[]
 for e in latin.iter(NS+'p'):
  identity=e.get(ID,'')
  if identity.startswith(prefix) and identity[len(prefix):]:units.append(identity)
 assert len(units)==len(set(units))
 for identity in units:
  binding=next((r for r in registries['alignment-ranges'] if r['canonical-target']==identity and r['language']=='English'),None)
  if binding:expected=interval(dict(id=binding['id'],English=binding['start'],endLocator=binding['end']))
  else:
   ps=[e for e in body.iter(NS+'p') if identity in e.get('sameAs','').replace('#','').split() or e.get(ID)==identity.replace('latin-','english-',1)]
   expected=norm(''.join(text[positions[e][0]:positions[e][1]] for e in ps)) if ps else None
  counts['alignment']+=1
  rows.append(dict(book=book,scheme='alignment',id=identity,query=f'book={book}&num={identity[len(prefix):]}',text=expected,available=expected is not None))
 counts['book']+=1;rows.append(dict(book=book,scheme='book',id=book,query=f'book={book}',text=norm(text),available=True))
result=dict(method='Independent Python XML coordinates and frozen registry locators; no renderer extraction',counts=dict(counts),rows=rows)
(PACK/'STRUCTURAL_ORACLE.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Independent structural oracle',dict(counts))
