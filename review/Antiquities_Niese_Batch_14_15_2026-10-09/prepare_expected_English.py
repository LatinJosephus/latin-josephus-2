"""Derive preserved broad English contexts independently from frozen XML."""
from pathlib import Path
import json,sys
from source_scope import Book
ROOT=Path(__file__).resolve().parents[2];b=int(sys.argv[1]);roman={14:'XIV',15:'XV'}[b]
P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
source=Book(raw=(P/'frozen-inputs/English.xml').read_bytes());reg=json.loads((P/'IDENTITY_REGISTRY.json').read_text());out=[]
for s in reg['sections']:
 texts=[]
 for u in source.units:
  targets=[x.split('#')[-1] for x in (u['element'].get('sameAs') or '').split()]
  mirror=u['id'].replace('english-','latin-',1) if u['id'] else ''
  if s['contextTarget'] in targets or (not targets and mirror==s['contextTarget']):texts.append(u['text'])
 assert texts,(s['number'],s['contextTarget'])
 out.append(dict(number=s['number'],contextTarget=s['contextTarget'],text=''.join(texts)))
(P/'EXPECTED_ENGLISH_CONTEXT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(roman,len(out),'frozen English contexts')
