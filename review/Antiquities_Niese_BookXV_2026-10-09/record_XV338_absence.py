"""Record independently verified unavailability without inserting a fictitious cut."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Antiquities_Niese_Batch_14_15_2026-10-09'))
import json
from source_scope import Book,digest
from verify_locators import validate
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'review/Antiquities_Niese_BookXV_2026-10-09'
rows=json.loads((P/'BOUNDARIES.json').read_text());l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes())
u=next(u for u in l.units if u['id']=='latin-book15-num331')
for n in [334,335,336,337,339,340,341]:validate(l,rows[n-1]['Latin_locator'])
assert 'ostia uero portus contra aquilonem extabant in medio autem turris erat, super quam templum caesaris' in u['text']
note='Text corresponding to this Niese section is unavailable in this Latin transcription. The left-hand foundation tower and the two joined right-hand stone blocks at the harbour entrance have no identifiable counterpart here. The cause is unknown. The north-facing entrance in §337 and the central temple site in §339 survive.'
r=rows[337]
r.update(Latin_review_status='INDIVIDUALLY_REVIEWED',physical_placement_status='NO_MILESTONE_VERIFIED_LATIN_UNAVAILABILITY',
 correspondence_status='UNAVAILABLE',editorial_status='ROUTINE_INDEPENDENTLY_VERIFIED_ABSENCE',implementation_approved=True,
 Latin_paragraph_id=u['id'],contextTarget=u['id'],reader_note=note,correspondence_limit=note,
 review_reason='Full coastal-city unit and adjoining narrative compared with Greek 331–341, Niese III 392–394/PDF464–466 and independent Loeb Greek 160–162/PDF176–178 and English 163/PDF179. The surviving named tower is 336; the north-facing entrance is 337; the central tower attached to Caesar’s temple is 339. No interval is manufactured for 338.',
 Greek_print_status='VISUALLY_REVIEWED_IDENTITY_AND_CLAUSE_CONTEXT',reader_certified=False,
 print_observation=dict(edition='Niese III (1892)',printed_page=393,pdf_page=465,image='evidence/Niese-III-PDF465.jpg',image_inspected=True,
  printed_numeral_observation='Right margin 338 aligned with the end of the preceding north-facing entrance clause and the following basis clause; the exact clause begins βάσις δὲ.',exact_Greek_choice=r['Greek'],OCR_is_authority=False),
 absence_context=dict(frozen_unit_text=u['text'],unit_sha256=u['raw_sha256'] if 'raw_sha256' in u else digest(l.raw[u['raw_start']:u['raw_end']]),
  preceding_surviving_start=rows[336]['Latin_locator'],following_surviving_start=rows[338]['Latin_locator'],claim_scope='This transcription only; no assertion of physical loss or absence in the entire Latin tradition.'))
def save(name,x):(P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
save('BOUNDARIES.json',rows);save('ABSENCE_XV_338.json',r)
h=json.loads((P/'DECISION_HISTORY.json').read_text())
if not any(x.get('kind')=='INDEPENDENTLY_VERIFIED_UNAVAILABILITY' and x.get('section')==338 for x in h):h.append(dict(kind='INDEPENDENTLY_VERIFIED_UNAVAILABILITY',section=338,record='ABSENCE_XV_338.json',adopted=True,no_physical_cut=True,source_context_preserved=True,cause_unknown=True))
save('DECISION_HISTORY.json',h)
print('XV.338: verified unavailability; no Latin milestone or invented interval.')
