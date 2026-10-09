"""Distinguish retained numeral positions from semantic incipits; preserve whitespace."""
from pathlib import Path
import json
from source_scope import Book
from verify_locators import validate
ROOT=Path(__file__).resolve().parents[2]
for b,roman in [(14,'XIV'),(15,'XV')]:
 p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09';rows=json.loads((p/'BOUNDARIES.json').read_text());l=Book(raw=(p/'frozen-inputs/Latin.xml').read_bytes());changes=[]
 for r in rows:
  if r.get('physical_placement_status')=='RETAIN_EXISTING_NUM':
   label=next(v for v in l.labels if v['id']==r['Latin_paragraph_id']);physical=l.locate(label['book_offset']);validate(l,physical)
   if physical['raw_byte']!=r['Latin_locator']['raw_byte']:changes.append(dict(number=r['number'],previous=r['Latin_locator'],actual=physical,kind='RETAINED_NUM_COORDINATE_CORRECTION_NO_XML_EDIT'))
   r['Latin_locator']=physical;r['retained_num_raw_byte']=label['raw_start'];r['retained_num_text']=label['text']
 if b==15:
  r=rows[0];physical=l.locate(0);validate(l,physical)
  if physical['raw_byte']!=r['Latin_locator']['raw_byte']:changes.append(dict(number=1,previous=r['Latin_locator'],actual=physical,kind='OPENING_MILESTONE_BEFORE_PRESERVED_LEADING_SPACE'))
  r['Latin_locator']=physical
  plan=json.loads((p/'APPROVED_MARKER_PLAN_PARTIAL.json').read_text());next(x for x in plan['markers'] if x['number']==1)['locator']=physical
  (p/'APPROVED_MARKER_PLAN_PARTIAL.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 (p/'BOUNDARIES.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 (p/'PHYSICAL_WHITESPACE_COORDINATES.json').write_text(json.dumps(dict(book=b,changes=changes,semantic_incipits_unchanged=True,narrative_bytes_unchanged=True,reason='Executable markers delimit narrative whitespace as well as words. Retained num positions include their following whitespace; the new XV opening milestone precedes its original leading space, so all narrative characters belong to the partition.'),ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 h=json.loads((p/'DECISION_HISTORY.json').read_text());h.append(dict(kind='PHYSICAL_VS_SEMANTIC_COORDINATE_AUDIT',record='PHYSICAL_WHITESPACE_COORDINATES.json',sections=[x['number'] for x in changes],narrative_bytes_unchanged=True));(p/'DECISION_HISTORY.json').write_text(json.dumps(h,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 print(b,'physical whitespace coordinate changes',len(changes))
