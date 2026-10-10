from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
from PIL import Image
from mixed_mapper import digest
D=Path(__file__).resolve().parent
def save(name,x):(D/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
ledger=json.loads((D/'LATIN_PHYSICAL_COVERAGE.json').read_text(encoding='utf8'))
save('WINDOW_302_347_PHYSICAL_LEDGER.json',[f for f in ledger if f.get('number',0)>=302 or f.get('role')=='INTERPOLATION'])
rows=json.loads((D/'IDENTITY_REGISTER.json').read_text(encoding='utf8'));images=[]
for pdf in range(76,143):
 rs=[r for r in rows if r['Greek']['print_observation']['PDF']==pdf];assert rs
 p=Path(rs[0]['Greek']['image']);im=Image.open(p);images.append(dict(PDF=pdf,print=pdf-72,image=str(p),sha256=digest(p.read_bytes()),dimensions=list(im.size),identities=[r['number'] for r in rs]))
save('PRINT_IMAGE_MANIFEST.json',dict(edition='Niese III1892',source_sha256='676dcc1e9c66892d9a48177043a74fd4d63aec9932a405ba4db6d03f7cf313ab'.replace('3aec','3eca'),images=images,inspected_images=67,identities=347,source_reference='PRINTED_SOURCES.json; PDF pages1-based; images are reusable runtime references, not copies of the source volume'))
history=json.loads((D/'DECISION_HISTORY.json').read_text(encoding='utf8'))
extra=[dict(id='XI-full-individual-correspondence-review',status='CLOSED_ROUTINE_REVIEW',authority='Full Greek sections, neighbours and all nonadjacent Latin fragments; per-identity review_choices.json and IDENTITY_REGISTER.json',represented_identities=347,primary_fragments=352,unresolved=[]),dict(id='XI-current-central-traditional-disclosure',status='IMPLEMENTED_ACCEPTED_USER_POLICY',authority='User requires the Canonical order from separate witness fragments notice; b8d4db2 moves the earlier per-pane disclosure into a shared explanation banner',implementation='Keep the current shared explanation and Book link; add the specified title only when structural presentation-note data exists. No obsolete reader code or per-pane disclosure restored.'),dict(id='XI-notice-theme-contrast',status='RESOLVED_LOCAL_READER_FIX',authority='Reproduced white text on lavender in dark theme on the new notice',implementation='Use current reader palette variables for explicit-fragment notes and shared traditional banner.')]
for event in extra:
 if not any(x['id']==event['id'] for x in history):history.append(event)
save('DECISION_HISTORY.json',history)
p=D/'SOURCE_AUTHORITY.md';s=p.read_text(encoding='utf8');s=s.replace('Current status is review in progress. The347-identity census is established; complete printed-start review, Latin review, model rehearsal and actual-reader certification remain required. No completion or publication claim is made.','The source review is complete:347 printed Greek starts on67 page images,347 individually reviewed Latin correspondences,352 primary Latin fragments and2 source-only Bellum occurrences. IDENTITY_REGISTER.json is the final authority; candidate/model records are historical stages. SOURCE_PROOF.json independently certifies lossless physical accounting and reversible bytes. Final actual-reader certification and integration readiness are recorded in REPORT.md and CERTIFICATION.json. No public publication claim is made.')
p.write_text(s,encoding='utf8',newline='\n')
print('Closed source-review metadata,67 image references, decisions and final tail ledger recorded.')
