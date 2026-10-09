"""Independently reviewed missing witness-list correspondence in this transcription."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Antiquities_Niese_Batch_14_15_2026-10-09'))
from source_scope import Book,digest
from verify_locators import validate
P=Path(__file__).resolve().parent;rows=json.loads((P/'BOUNDARIES.json').read_text());l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes())
context=l.units[76:80];assert [u['id'] for u in context]==[f'latin-book14-num{n}' for n in [235,236,237,241]]
assert 'ut ciues romanos iudaeos' in context[1]['text'] and context[2]['text'].startswith('lucio lentulo et gaio marcello consulibus lentulus decretum protulit.')
validate(l,rows[236]['Latin_locator'])
for n in [238,239]:
 r=rows[n-1];note=f'Text corresponding to Niese §{n} is unavailable in this Latin transcription. The detailed witness list has no identifiable counterpart between the surviving exemption and date in §237 and Lentulus’s decree notice in §240. The cause is unknown.'
 r.update(Greek_print_status='VISUALLY_REVIEWED_IDENTITY_AND_CLAUSE_CONTEXT',Latin_review_status='INDIVIDUALLY_REVIEWED',physical_placement_status='NO_MILESTONE_VERIFIED_LATIN_UNAVAILABILITY',correspondence_status='UNAVAILABLE',editorial_status='ROUTINE_INDEPENDENTLY_VERIFIED_ABSENCE',implementation_approved=True,reader_certified=False,Latin_paragraph_id='latin-book14-num237',contextTarget='latin-book14-num237',reader_note=note,correspondence_limit=note,
 review_reason='Complete frozen Latin context 235–241 compared with Greek 235–244. Niese III284/PDF356 and independent Loeb VII576/PDF588 were visually inspected. The dating phrase closes 237; lentulus decretum protulit begins 240. No portion of either intervening named-witness list is separately identifiable here. The earlier collective Senate formula belongs to 229 in a different document and cannot supply 238–239.',
 print_observation=dict(edition='Niese III (1892)',pdf_page=356,printed_page=284,image='evidence/Niese-III-PDF356.jpg',image_inspected=True,printed_numeral_observation='Left-margin numeral beside the preceding consular date and ensuing witness list.' if n==238 else 'Left-margin 239 beside the beginning of the second portion of the named-witness list; the preceding first list continues across its printed line.',exact_Greek_choice=r['Greek'],independent_control='evidence/Loeb-PDF588.jpg',OCR_is_authority=False),
 absence_context=dict(frozen_units=[dict(id=u['id'],text=u['text'],raw_unit_sha256=digest(l.raw[u['raw_start']:u['raw_end']])) for u in context],preceding_surviving_start=rows[236]['Latin_locator'],following_surviving_phrase='lentulus decretum protulit',claim_scope='This transcription only; no claim about physical loss or the entire Latin tradition.'))
 (P/f'ABSENCE_XIV_{n}.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(P/'BOUNDARIES.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
history=json.loads((P/'DECISION_HISTORY.json').read_text());history.append(dict(kind='ROUTINE_INDEPENDENTLY_VERIFIED_UNAVAILABILITY',sections=[238,239],source='record_XIV238_239_absence.py',no_marker_inserted=True,claim_scope='This transcription only; cause unknown.'));(P/'DECISION_HISTORY.json').write_text(json.dumps(history,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print('XIV238–239: verified unavailable; no fictitious interval or cut')
