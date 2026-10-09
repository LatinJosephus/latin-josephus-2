from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Antiquities_Niese_Batch_14_15_2026-10-09'))
import json
from source_scope import Book
from verify_locators import validate
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'review/Antiquities_Niese_BookXV_2026-10-09'
def save(name,x):(P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
packet=json.loads((P/'DECISION_XV_040.json').read_text());choice=next(c for c in packet['options'] if c['option']=='B')
l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes());loc=choice['locator'];validate(l,loc)
rows=json.loads((P/'BOUNDARIES.json').read_text())
rows[39].update(Latin_locator=loc,Latin_semantic_incipit_locator=loc,Latin_anchor_phrase=choice['phrase'],
 Latin_paragraph_id='latin-book15-num39',contextTarget='latin-book15-num39',Latin_review_status='INDIVIDUALLY_REVIEWED',
 physical_placement_status='ADD_INTERNAL_NIESE_MILESTONE',physical_placement_confidence='EXPLICITLY_USER_APPROVED_EXACT_LOCATOR',
 correspondence_status='PARTIAL_WITH_COMPRESSION_AND_REORDERING',editorial_status='USER_APPROVED_B',review_reason='Explicit user approval of B at the frozen locator; partial compressed and reordered correspondence, with reciprocal reader notes.',implementation_approved=True,reader_certified=False)
notes={39:'The Latin compresses material from Greek XV.39–40 into one removal statement. The phrase praeter legem, corresponding to the statement in Greek §40 that Herod acted unlawfully, occurs earlier and remains in this Latin interval. See the reciprocal note at XV.40.',
 40:'Partial correspondence: the Latin compresses material from Greek XV.39–40 into one removal statement. Seditiones domesticas pacando corresponds to the household-disturbance phrase within Greek §40. Praeter legem, corresponding to the statement in Greek §40 that Herod acted unlawfully, occurs earlier and remains in the Latin interval assigned to XV.39. This displayed Latin interval supplies only part of the Greek section.'}
for n,note in notes.items():rows[n-1]['reader_note']=note
for n in [39,40]:
 start=rows[n-1]['Latin_locator']['book_offset'];end=rows[n]['Latin_locator']['book_offset'];assert start<end
 rows[n-1]['Latin_interval']=dict(start=start,end=end,text=l.stream[start:end]);rows[n-1].pop('Latin_interval_status',None)
assert rows[38]['Latin_interval']['text'].rstrip().endswith('praeter legem exuit,')
assert rows[39]['Latin_interval']['text'].startswith('seditiones domesticas pacando')
assert rows[39]['Latin_interval']['text'].rstrip().endswith('fraudari,')
packet.update(status='USER_APPROVED_B',adopted_option='B',rejected_options=['A','C'],authority='Direct user reply to XV.40 decision request, 2026-10-09',
 approved_physical_placement=loc,correspondence_qualification_separate_from_placement=True,reader_notes={str(n):v for n,v in notes.items()},
 adjoining_intervals_39_40_end_before_41_verified=True)
save('BOUNDARIES.json',rows);save('DECISION_XV_040.json',packet)
history=json.loads((P/'DECISION_HISTORY.json').read_text());history.append(dict(kind='EXPLICIT_USER_DECISION',section=40,adopted='B',
 exact_phrase=choice['phrase'],exact_locator=loc,rejected_alternatives=['A','C'],authority='Direct human user reply, 2026-10-09',
 instruction='Preserve praeter legem exuit in XV.39; partial compressed/reordered correspondence in XV.40, reciprocal reader notes, exact locator and unchanged words/markup.',
 neighbouring_extents_recomputed=[39,40],following_start=41));save('DECISION_HISTORY.json',history)
plan=json.loads((P/'APPROVED_MARKER_PLAN_PARTIAL.json').read_text());plan['markers'].append(dict(number=40,marker='<milestone unit="niese" n="40"/>',locator=loc,reason='Explicit user approval of option B.'))
plan['markers'].sort(key=lambda x:x['number']);plan['approved_sections']=sorted(set(plan['approved_sections']+[40]));plan['remaining_Latin_reviews']-=1;save('APPROVED_MARKER_PLAN_PARTIAL.json',plan)
md=P/'DECISION_XV_040.md';txt=md.read_text();txt=txt.replace('# XV.40 — decision required','# XV.40 — B approved by the user, 2026-10-09').replace('No change has been adopted for 40.','The user approved B at the exact recorded locator; A and C remain as rejected alternatives in the decision history.')
txt+='\n## Adopted reader notes\n\n### XV.39\n\n'+notes[39]+'\n\n### XV.40\n\n'+notes[40]+'\n\nThe approved physical placement is recorded separately from partial correspondence. Adjoining Latin intervals 39 and 40 were recomputed and independently verified through the start of 41.\n'
md.write_text(txt,encoding='utf8',newline='\n')
print('XV.40 B adopted; exact locator and intervals 39–40 through 41 PASS.')
