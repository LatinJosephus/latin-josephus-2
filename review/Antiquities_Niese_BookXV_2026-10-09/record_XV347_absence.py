"""Record absence of the detailed cave-layout section in this transcription."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Antiquities_Niese_Batch_14_15_2026-10-09'))
import json
from source_scope import Book,digest
from verify_locators import validate
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'review/Antiquities_Niese_BookXV_2026-10-09'
rows=json.loads((P/'BOUNDARIES.json').read_text());l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes())
u=next(u for u in l.units if u['id']=='latin-book15-num342')
for n in [343,344,345,346,348,349]:validate(l,rows[n-1]['Latin_locator'])
note='Text corresponding to this Niese section is unavailable in this Latin transcription. The narrow entrances, spacious interiors, level ground above, and hard rock reached by guided paths have no separately identifiable counterpart here. The cause is unknown. The compact cave-and-provisions description survives in §346, and Herod’s suppression of the brigands survives in §348.'
r=rows[346]
r.update(Latin_review_status='INDIVIDUALLY_REVIEWED',physical_placement_status='NO_MILESTONE_VERIFIED_LATIN_UNAVAILABILITY',
 correspondence_status='UNAVAILABLE',editorial_status='ROUTINE_INDEPENDENTLY_VERIFIED_ABSENCE',implementation_approved=True,
 Latin_paragraph_id=u['id'],contextTarget=u['id'],reader_note=note,correspondence_limit=note,reader_certified=False,
 review_reason='The full Latin unit and Greek 342–353 were compared. Niese III 395/PDF467 and independent Loeb Greek 166–168/PDF182–184 were visually inspected. Latin’s difficillima domicilia, aquarum receptacula, deposita frumenta and muniti speluncis form the compact counterpart of Greek 346’s refuges, caves and provisions. No independently identifiable spatial-layout account of 347 lies between this and cum haec gratiam caesaris (the surviving part of 348). No milestone or reconstructed wording is introduced.',
 Greek_print_status='VISUALLY_REVIEWED_IDENTITY_AND_CLAUSE_CONTEXT',
 print_observation=dict(edition='Niese III (1892)',printed_page=395,pdf_page=467,image='evidence/Niese-III-PDF467.jpg',image_inspected=True,
  printed_numeral_observation='Right margin 347 aligned with the end of the hidden-resistance statement; the new entrance-description clause αἵ γε μὴν follows on the same line.',exact_Greek_choice=r['Greek'],OCR_is_authority=False),
 absence_context=dict(frozen_unit_text=u['text'],source_sha256=digest(l.raw),unit_sha256=digest(l.raw[u['raw_start']:u['raw_end']]),
  preceding_surviving_start=rows[345]['Latin_locator'],following_surviving_start=rows[347]['Latin_locator'],
  rejected_fictitious_cut='muniti speluncis is the cave-refuge counterpart already belonging to Greek 346; separating it as 347 would not supply the narrow-entrance and spatial-layout account.',
  claim_scope='This transcription only; no physical-loss explanation or entire-tradition claim.'))
(P/'BOUNDARIES.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(P/'ABSENCE_XV_347.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
h=json.loads((P/'DECISION_HISTORY.json').read_text())
if not any(x.get('kind')=='INDEPENDENTLY_VERIFIED_UNAVAILABILITY' and x.get('section')==347 for x in h):h.append(dict(kind='INDEPENDENTLY_VERIFIED_UNAVAILABILITY',section=347,record='ABSENCE_XV_347.json',adopted=True,no_physical_cut=True,source_context_preserved=True,cause_unknown=True))
(P/'DECISION_HISTORY.json').write_text(json.dumps(h,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print('XV.347: verified unavailability; preserved compact 346 and surviving 348.')
