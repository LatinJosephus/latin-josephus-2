"""Revalidate previously adopted raw cuts after explicitly recorded scope exclusions."""
from pathlib import Path
import json
from source_scope import Book,digest
from verify_locators import validate,validate_all_nodes
ROOT=Path(__file__).resolve().parents[2]
def save(path,x):path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
for b,roman in [(14,'XIV'),(15,'XV')]:
 P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
 l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes());g=Book(raw=(P/'frozen-inputs/Greek.xml').read_bytes())
 rows=json.loads((P/'BOUNDARIES.json').read_text())
 for r in rows:
  for key in ['Latin_locator','Latin_semantic_incipit_locator']:
   if key in r:
    old=r[key];node=next(n for n in l.nodes if old['raw_byte'] in n['raw_positions'])
    new=l.locate(node['book_start']+node['raw_positions'].index(old['raw_byte']));validate(l,new)
    assert old['raw_byte']==new['raw_byte'];r[key]=new
 for i,r in enumerate(rows):
  if not r.get('Latin_locator'):continue
  j=i+1
  while j<len(rows) and rows[j].get('correspondence_status')=='UNAVAILABLE':j+=1
  end=rows[j].get('Latin_locator') if j<len(rows) else None
  if end:
   start=r['Latin_locator']['book_offset'];finish=end['book_offset'];assert start<finish
   r['Latin_interval']=dict(start=start,end=finish,text=l.stream[start:finish]);r.pop('Latin_interval_status',None)
  elif i==len(rows)-1 and (P/'TERMINAL_EXTENT.json').exists():
   start=r['Latin_locator']['book_offset'];r['Latin_interval']=dict(start=start,end=len(l.stream),text=l.stream[start:]);r.pop('Latin_interval_status',None)
  else:r.pop('Latin_interval',None);r['Latin_interval_status']='Following start not yet adopted; extent remains provisional.'
 save(P/'BOUNDARIES.json',rows)
 planpath=P/'APPROVED_MARKER_PLAN_PARTIAL.json'
 if planpath.exists():
  plan=json.loads(planpath.read_text())
  for op in plan['markers']:op['locator']=rows[op['number']-1]['Latin_locator']
  save(planpath,plan)
 save(P/'LATIN_SCOPE_EXCLUSIONS.json',l.scope_exclusions)
 save(P/'GREEK_SCOPE_EXCLUSIONS.json',{'chronological_contents_prefix':g.excluded_prefix,'other_exclusions':g.scope_exclusions})
 save(P/'SCOPED_COORDINATE_QA.json',dict(status='PASS',Greek=validate_all_nodes(g),Latin=validate_all_nodes(l),
  Latin_stream_codepoints=len(l.stream),Greek_stream_codepoints=len(g.stream),Latin_narrative_stream_sha256=digest(l.stream.encode()),
  frozen_source_sha256=digest(l.raw),raw_cuts_unchanged=True,scope_change='Exclude marginal s/ss sigla and literal XIV X. chapter label, preserving word corrections and all original bytes.'))
 print(b,'scope and adopted cuts revalidated')
