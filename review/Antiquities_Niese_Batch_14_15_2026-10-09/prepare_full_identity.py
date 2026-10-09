"""Promote only a complete, independently partition-verified book registry."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2];b=int(sys.argv[1]);roman={14:'XIV',15:'XV'}[b]
P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
load=lambda name:json.loads((P/name).read_text())
q=load('COMPLETE_PARTITION_QA.json');assert q['status']=='PASS' and q['full_narrative_partition']
registry=load('IDENTITY_REGISTRY_PARTIAL.json');assert len(registry['sections'])==q['expected_sections']
registry.pop('status');registry.pop('full_expected_range')
for section in registry['sections']:
 assert section['Latin']['available']==(section['number'] not in q['unavailable_sections'])
target=ROOT/f'assets/xml/antiquities/niese/book-{b:02}.json'
assert not target.exists() or json.loads(target.read_text())==registry
target.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(P/'IDENTITY_REGISTRY.json').write_bytes(target.read_bytes())
print(roman,'full registry prepared; browser certification remains required')
