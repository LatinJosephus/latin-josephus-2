"""Extract actual full-selection English results against independent frozen controls.

This does not run the browser again. The independent expected-context record
is derived from the untouched English XML, and every actual selection is
compared with it during FULL_READER_QA.
"""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[2];b=int(sys.argv[1]);roman={14:'XIV',15:'XV'}[b]
P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
q=json.loads((P/'FULL_READER_QA.json').read_text())
assert q['result']=='PASS' and len(q['selections'])=={14:491,15:425}[b]
assert all(s['English']=='PRESERVED_BROADER_CONTEXT_PASS' for s in q['selections'])
q['scope']='INDEPENDENT_FROZEN_ENGLISH_EXPECTATIONS_COMPARED_DURING_FULL_SELECTION_BROWSER_RUN'
q['separate_browser_run']=False
q['evidence_origin']='FULL_READER_QA.json, actual all-selection comparison; no repeated browser run or inferred display result.'
q['independent_expectation_path']=str(P/'EXPECTED_ENGLISH_CONTEXT.json')
q['independent_expectation_sha256']=hashlib.sha256((P/'EXPECTED_ENGLISH_CONTEXT.json').read_bytes()).hexdigest()
q['frozen_English_sha256']=hashlib.sha256((P/'frozen-inputs/English.xml').read_bytes()).hexdigest()
(P/'ENGLISH_CONTEXT_READER_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(roman,len(q['selections']),'actual English context comparisons recorded')
