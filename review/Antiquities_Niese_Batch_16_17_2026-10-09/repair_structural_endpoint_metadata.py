"""Retain every original milestone unit in frozen structural endpoint ordinals."""
from pathlib import Path
from collections import Counter
import json,hashlib
from lxml import etree
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
for b,roman in [(16,'XVI'),(17,'XVII')]:
    p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
    units={}
    for language in ['Latin','Greek','English']:
        counts=Counter(e.get('unit') for e in etree.fromstring((p/f'frozen-inputs/{language}.xml').read_bytes()).iter() if etree.QName(e).localname=='milestone')
        units[language]=[dict(unit=u,count=c) for u,c in counts.items()]
    registry_path=ROOT/f'assets/xml/antiquities/niese/book-{b}.json'
    registry=read(registry_path);assert registry['structuralMilestoneUnits']==['chapter']
    old=hashlib.sha256(registry_path.read_bytes()).hexdigest()
    registry['structuralMilestoneUnits']=['chapter',None];save(registry_path,registry)
    new=hashlib.sha256(registry_path.read_bytes()).hexdigest()
    ledger=read(p/'APPLIED_RAW_BYTE_PATCH.json');assert ledger['registry']['sha256']==old
    ledger['registry']['sha256']=new;save(p/'APPLIED_RAW_BYTE_PATCH.json',ledger)
    record=dict(kind='STRUCTURAL_ENDPOINT_METADATA_REPAIR',date='2026-10-10',original_milestone_units=units,
        reason='Actual built-reader Bamberg comparison found that unitless original image milestones were excluded from a frozen ordinal endpoint. Keep original chapter and unitless milestones; exclude new Niese milestones.',
        before_registry_sha256=old,after_registry_sha256=new,source_bytes_changed=False,scholarly_boundaries_changed=False,
        superseded_failure_reports=['CONTAINING_VIEWS_BROWSER_FAILURE.json','PROTECTED_BROWSER_FAILURE.json'],reader_certified=False)
    history=read(p/'DECISION_HISTORY.json');history.append(record);save(p/'DECISION_HISTORY.json',history)
    save(p/'STRUCTURAL_ENDPOINT_METADATA_REPAIR.json',record)
    print(roman,'retained original milestone units:',units)
