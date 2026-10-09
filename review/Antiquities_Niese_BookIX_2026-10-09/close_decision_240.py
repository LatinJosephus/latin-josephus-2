"""Record the user's explicit resolution while retaining pre-decision evidence and both cuts."""
from pathlib import Path
import json,hashlib,datetime,shutil
P=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
history=P/'qa-history/pre-decision-5794785';history.mkdir(parents=True,exist_ok=True)
names=['NEW_BOOK_BROWSER_QA.json','PROTECTED_BROWSER_QA.json','PROTECTED_SOURCE_GATE_QA.json','INHERITED_ISSUES_QA.json','SOURCE_PRESERVATION_QA.json','BUILD_RECORD.json','CERTIFICATION.json','FILE_MANIFEST.json','REPORT.md','SOURCE_AUTHORITY.md','IMPLEMENTATION_PRESERVATION.json','BOUNDARIES.json','BOUNDARIES.md','EXPECTED_INTERVALS.json','DECISION_240_ALTERNATIVES.json','EDITORIAL_HISTORY.json']
manifest=[]
for name in names:
    src=P/name;dst=history/name
    if not dst.exists():shutil.copyfile(src,dst)
    manifest.append({'name':name,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'bytes':dst.stat().st_size})
write(history/'PRE_DECISION_EVIDENCE.json',{'scope':'PRECEDES_EXPLICIT_WORD_LEVEL_RESOLUTION_OF_IX_240','local_commit':'5794785c61beb6fee7e7fade6275092c42ddef77','editorial_state':'PROVISIONAL_PENDING_240','files':manifest})
decision={'240':{'status':'CLOSED_EXPLICIT_USER_EDITORIAL_RESOLUTION','choice':'A','recorded_at_UTC':datetime.datetime.now(datetime.UTC).isoformat(),'authority':'Direct user adjudication in this assignment on 2026-10-09','classification':'Explicit editorial resolution of the word-level ambiguity in the printed numeral placement','Greek_start':'immediately before ἔσται δ᾽','Latin_start':'immediately before et nullus','rationale':'Keep the statement that nobody will comply together with its explanation that saving their lives takes priority over saving their possessions.','printed_observation':'Niese and Loeb numerals identify a line containing both possible clause starts; the printed numeral does not unambiguously fix the cut at ἔσται.','rejected_alternative':{'choice':'B','Greek_start':'σώζειν γὰρ','Latin_start':'dum animas suas','status':'REJECTED_BY_EXPLICIT_USER_RESOLUTION','was_inherited_Greek_cut':True},'exact_locator_authority':'DECISION_240_ALTERNATIVES.json: alternatives.A'}}
write(P/'EDITORIAL_DECISIONS.json',decision)
packet=read(P/'DECISION_240_ALTERNATIVES.json');packet['status']='CLOSED_EXPLICIT_USER_EDITORIAL_RESOLUTION';packet['adopted_alternative']='A';packet['rejected_alternative']='B';packet['editorial_resolution']=decision['240']
write(P/'DECISION_240_ALTERNATIVES.json',packet)
h=read(P/'EDITORIAL_HISTORY.json');h['pending']=[];h['explicit_user_resolutions']=[decision['240']];h['prior_provisional_commit']='5794785c61beb6fee7e7fade6275092c42ddef77';h['additional_Greek_marker_relocation']=240
write(P/'EDITORIAL_HISTORY.json',h)
text=(P/'DECISION_240.md').read_text(encoding='utf8')
text=text.replace('Status: PENDING USER ADJUDICATION. All other IX work continues independently.','Status: CLOSED — A adopted by explicit user editorial resolution on 2026-10-09. This resolves the word-level ambiguity of the shared-line numeral; it does not claim that the printed numeral unambiguously fixes the cut at ἔσται.')
text=text.replace('**A, recommended:**','**A, adopted by explicit user resolution:**')
text=text.replace('Both printed lines support this placement and the paired witnesses preserve the same semantic sequence.','The shared printed line permits this reading without settling the exact word. The user chose A to keep the statement that nobody will comply together with its explanation that saving their lives takes priority over saving their possessions.')
text=text.replace('**B:**','**B, rejected alternative retained in the decision history:**')
text+='\n## Resolution and implementation authority\n\nThe user explicitly approved Greek IX.240 immediately before `ἔσται δ᾽` and Latin IX.240 immediately before `et nullus`. The exact packet locators for A govern the paired marker changes. The inherited Greek cut at `σώζειν γὰρ`, paired with Latin `dum animas suas`, remains preserved above and in EDITORIAL_HISTORY.json as rejected alternative B. The observed printed line and linked images are unchanged. Section240 is an additional Greek marker relocation alongside181 and216. Final239–241 extents and certification are recorded separately from the preceding provisional results.\n'
(P/'DECISION_240.md').write_text(text,encoding='utf8',newline='\n')
print('Explicit A resolution recorded; both printed observations/alternatives and preceding QA preserved.')
