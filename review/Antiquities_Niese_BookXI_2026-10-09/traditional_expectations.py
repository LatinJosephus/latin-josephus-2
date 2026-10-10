"""Derive expected containing-view narrative and populations from pinned structural data."""
from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
from lxml import etree
from mixed_mapper import Book,NS,XMLID
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
def fields(fs):
 out={}
 for f in fs.findall('t:f',NS):
  children=list(f)
  if not children:continue
  c=children[0];tag=etree.QName(c).localname
  if tag=='fs':value=fields(c)
  elif tag=='vColl':value=[fields(x) for x in c.findall('t:fs',NS)]
  else:value=''.join(c.itertext()).strip()
  out[f.get('name')]=value
 return out
def main():
 bs={l:Book(D/'inputs'/f'{l}.xml') for l in ['Latin','Greek','English']};tree=etree.parse(str(ROOT/'assets/xml/antiquities/structure.xml'));rows=[]
 allrows={item.get(XMLID):fields(item.find('t:fs',NS)) for item in tree.xpath('//t:item[t:fs[@type="traditional-boundary"]]',namespaces=NS)}
 physical={l:json.loads((D/(l.upper()+'_PHYSICAL_COVERAGE.json')).read_text(encoding='utf8')) for l in ['Latin','Greek']}
 def offset(l,locator):
  b=bs[l];loc=locator.get('boundary-start',locator)
  if loc.get('kind')=='book-end':return len(b.stream)
  assert loc.get('available')=='true';u=next(u for u in b.units if u['id']==loc['target'])
  if loc['kind']=='paragraph':return u['book_start']
  assert loc['kind']=='element-edge' and loc['edge'].startswith('num[');ordinal=int(loc['edge'][4:-1]);label=[x for x in b.labels if x['unit']==u['index']][ordinal-1];return label['book_offset']
 for id,r in allrows.items():
  if r.get('book')!='11' or r.get('context')=='Proem':continue
  result=dict(id=id,scheme=r['scheme'],chapter=r['chapter'],subchapter=r.get('subchapter'),languages={})
  for l in bs:
   loc=r[l]
   if loc.get('available')=='false':result['languages'][l]=dict(available=False);continue
   end=None if r.get('end')=='BOOK_END' else allrows[r['end']][l]
   spans=loc.get('spans',[dict(start=loc,end=r.get('endLocator') or end or dict(kind='book-end'))]);extents=[(offset(l,s['start']),offset(l,s['end'])) for s in spans];assert all(z>a for a,z in extents)
   text=''.join(bs[l].stream[a:z] for a,z in extents);membership=[]
   for a,z in extents:
    for f in physical.get(l,[]):
     x,y=f['start']['book_offset'],f['end']['book_offset']
     if x<z and y>a:membership.append(dict(number=f.get('number'),source=f.get('identity'),rank=f.get('rank',1),occurrence=f.get('occurrence'),complete=x>=a and y<=z))
   result['languages'][l]=dict(available=True,physical_spans=extents,text=text,span_count=len(spans),fragment_membership=membership,identity_population=sorted(set(f['number'] for f in membership if f['number'] is not None)),source_occurrences=[f['source'] for f in membership if f['source']])
  rows.append(result)
 assert len(rows)==61
 for id,spans in [('LOEB-11-Chapter-8-0',4),('LOEB-11-Subchapter-8-2',2),('LOEB-11-Subchapter-8-4',2),('LOEB-11-Subchapter-8-6',2)]:assert next(r for r in rows if r['id']==id)['languages']['Latin']['span_count']==spans
 (D/'TRADITIONAL_EXPECTATIONS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print('61 containing-view populations independently derived from pinned registry extents.')
if __name__=='__main__':main()
