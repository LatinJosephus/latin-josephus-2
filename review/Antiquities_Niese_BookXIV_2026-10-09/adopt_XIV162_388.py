"""One-shot recording of the direct human adjudication of XIV162A/388B."""
from pathlib import Path
import sys,json
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'Antiquities_Niese_Batch_14_15_2026-10-09'))
from source_scope import Book
from verify_locators import validate
def save(name,x):(P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
r=json.loads((P/'BOUNDARIES.json').read_text());l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes());h=json.loads((P/'DECISION_HISTORY.json').read_text())
notes={161:'The approved boundary interpretation leaves tractaretque here as the concluding verb associated with Phasael’s handling of populi negotia. Antipatrum begins the following faciebat … honorari construction at162. The difficult wording and punctuation are preserved; see162.',162:'The approved boundary begins before antipatrum, faciebat, retaining Antipatrum with the following faciebat … honorari construction. Tractaretque remains in161 as the concluding verb associated with Phasael’s handling of populi negotia. The comma after antipatrum and the difficult syntax are preserved. The later affirmative hyrcani fidem transgressus est differs from the Greek denial of disloyalty: no negative has been supplied. This interval must not be read as unqualified semantic equivalence.',387:'Distributed/reordered correspondence: quem postea interfecit, quod apto tempore referemus, the relative clause concerning the young man’s later death, survives here and corresponds to Greek XIV.388. It remains in the preserved Latin sequence before the subsequent seven-day passage corresponding to Greek XIV.387. See the reciprocal notice at388; no cause of the different ordering is inferred.',388:'Distributed/reordered correspondence: the death reference of Greek XIV.388 survives earlier within the Latin interval for387, at quem postea interfecit, quod apto tempore referemus. This interval begins with senatu uero dimisso, the senate’s dismissal and ensuing procession. The death reference is not absent and has not been moved, duplicated or rewritten; see387.'}
for n,option in [(162,'A'),(388,'B')]:
 packet=json.loads((P/f'DECISION_XIV_{n:03}.json').read_text());assert packet['status'].startswith('PENDING_USER')
 c=next(v for v in packet['options'] if v['option']==option);loc=c['locator'];validate(l,loc)
 r[n-1].update(Latin_locator=loc,Latin_semantic_incipit_locator=loc,Latin_anchor_phrase=c['phrase'],physical_placement_status='ADD_INTERNAL_NIESE_MILESTONE',physical_placement_confidence='EXPLICITLY_USER_APPROVED_EXACT_LOCATOR',Latin_review_status='INDIVIDUALLY_REVIEWED',editorial_status='USER_APPROVED_'+option,implementation_approved=True,reader_certified=False,review_reason=f'Direct human approval of {option} on 2026-10-09 using the current pinned XML locator; Greek boundaries and English preserved.')
 r[n-1]['Latin_paragraph_id']=packet['Latin_paragraph']
 r[n-1]['contextTarget']=packet['Latin_paragraph']
 reasons={'A':'Would assign the intervening seven-day clause of Greek387 to Latin388.','C':'Would open388 with the seven-day passage corresponding to Greek387.'} if n==388 else {'B':'Would leave Antipater’s name with the preceding Phasael material, separated from faciebat … honorari.','C':'Would take tractaretque away from the concluding verb associated with Phasael’s handling of populi negotia.'}
 rejected=[dict(option=k,reason=v) for k,v in reasons.items()]
 packet.update(status='USER_APPROVED_'+option,adopted_option=option,rejected_options=rejected,authority='Direct human message 2026-10-09 approving both162A and388B.',approved_physical_placement=loc,correspondence_qualification_separate_from_placement=True,reader_notes={str(v):notes[v] for v in [n-1,n]})
 save(f'DECISION_XIV_{n:03}.json',packet)
 h.append(dict(kind='EXPLICIT_USER_DECISION',section=n,adopted=option,exact_phrase=c['phrase'],exact_locator=loc,rejected_alternatives=rejected,authority=packet['authority'],reader_notes=packet['reader_notes'],Greek_boundary_changed=False,English_changed=False,source_words_changed=False,neighbouring_extents_recomputed=[n-1,n,n+1]))
 md=P/f'DECISION_XIV_{n:03}.md';txt=md.read_text().replace('No Latin cut for 162 has been adopted. All independent XIV and XV work may continue.','A was approved at the exact locator, 2026-10-09. B and C are rejected alternatives.')
 md.write_text(txt+'\n## Adopted decision and reader notices\n\n'+f'{option} approved by the human user, 2026-10-09. No Greek boundary or English change.\n\n'+'\n\n'.join(f'XIV.{v}: {notes[v]}' for v in [n-1,n])+'\n',encoding='utf8',newline='\n')
for n,s in notes.items():r[n-1].update(reader_note=s,correspondence_limit=s,correspondence_status='PARTIAL_WITH_COMPRESSION_AND_REORDERING' if n in [387,388] else 'PRESENT_WITH_TRANSMITTED_DIFFERENCE')
for n in [161,162,163,387,388,389]:
 start=r[n-1]['Latin_locator']['book_offset'];end=r[n]['Latin_locator']['book_offset'];assert start<end
 r[n-1]['Latin_interval']=dict(start=start,end=end,text=l.stream[start:end]);r[n-1].pop('Latin_interval_status',None)
assert r[160]['Latin_interval']['text'].rstrip().endswith('tractaretque')
assert r[161]['Latin_interval']['text'].startswith('antipatrum, faciebat')
assert 'hyrcani fidem transgressus est' in r[161]['Latin_interval']['text']
assert 'quem postea interfecit' in r[386]['Latin_interval']['text'] and 'Sed cum intra septimum diem' in r[386]['Latin_interval']['text']
assert r[387]['Latin_interval']['text'].startswith('senatu uero dimisso')
save('BOUNDARIES.json',r);save('DECISION_HISTORY.json',h)
plan=json.loads((P/'APPROVED_MARKER_PLAN_PARTIAL.json').read_text())
plan['markers']=[dict(number=x['number'],marker=f'<milestone unit="niese" n="{x["number"]}"/>',locator=x['Latin_locator'],reason=x['review_reason']) for x in r if x.get('Latin_locator') and x['physical_placement_status']=='ADD_INTERNAL_NIESE_MILESTONE']
plan['approved_sections']=[x['number'] for x in r if x.get('implementation_approved')];plan['remaining_Latin_reviews']=0
save('APPROVED_MARKER_PLAN_PARTIAL.json',plan)
print('162A/388B adopted, all adjoining locators/extents validated; 383 milestones planned')
