from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
for b,roman,total in [(14,'XIV',491),(15,'XV',425)]:
 P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
 if (P/'CERTIFICATION.json').exists():
  print(b,'complete certified registry retained');continue
 rows=json.loads((P/'BOUNDARIES.json').read_text())
 if b==14:
  limits={5:'The Greek temple-precinct assault is not explicitly expressed in this Latin interval; Hyrcanus’s retreat and detention of the family survive.',
   85:'Greek §85 additionally describes prisoners taken. This Latin interval explicitly retains the three thousand killed, with no separate capture count here.',
   108:'The oath and concealed beam survive in this Latin interval; the explicit statement that Eleazar alone knew the secret is not separately expressed here.',
   113:'The Latin shortens the statement about sacred public money; the eight hundred talents and contextual inference survive.',
   117:'The Latin compresses the ethnarch’s administrative functions to a short description of the ruler.',
   132:'The Latin retains the Memphis response and subsequent visit across a paragraph boundary. Greek §132’s separate statement that the preceding group obeyed is not explicitly expressed here.'}
 else:
  limits={15:'Latin joins the population notice in Greek §14 to the honours described in §15. The cut preserves the population subject in §14 and starts §15 at hyrcanum introducing the honours.',
   36:'The Latin compresses Alexandra’s speech and its contrast between priesthood and kingship; this interval does not reproduce all Greek wording.',
   39:rows[38]['reader_note'],40:rows[39]['reader_note']}
 for n,note in limits.items():
  rows[n-1]['correspondence_status']='PARTIAL_WITH_COMPRESSION_AND_REORDERING' if b==15 and n in [39,40] else 'PRESENT_WITH_LOCAL_COMPRESSION'
  rows[n-1]['correspondence_limit']=note
  rows[n-1]['reader_note']=note
 if b==15:rows[0]['print_observation']['printed_numeral_observation']='Implicit opening: no marginal 1; body chapter heading and running range independently identify the opening.'
 exceptions=[]
 if b==14:exceptions=[dict(paragraph='latin-book14-num25',label='[II.ii.26]',visibleClaim=26,actualSection=25),
  dict(paragraph='latin-book14-num133',label='[VIII.ii.133]',visibleClaim=133,actualSection=133)]
 if b==14:
  for n in [199,230,431]:
   if rows[n-1].get('implementation_approved'):exceptions.append(dict(paragraph=f'latin-book14-num{n}',label=None,visibleClaim=n,actualSection=n,reason='Visible label is within a reviewed section or its predecessor; the adopted milestone supplies the actual executable start.'))
 # Assert the exact inherited visible label from the frozen XML, not a guess.
 if b==14:
  import sys
  sys.path.insert(0,str(Path(__file__).resolve().parent))
  from source_scope import Book
  src=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes())
  for x in exceptions:x['label']=next(v['text'].strip() for v in src.labels if v['id']==x['paragraph'])
 adopted=[]
 for r in rows:
  if not r.get('Latin_locator') and r.get('correspondence_status')!='UNAVAILABLE':break
  adopted.append(r)
 registry=dict(schema=1,book=b,range=[1,adopted[-1]['number']],full_expected_range=[1,total],status='PARTIAL_REVIEW_HARNESS_ONLY_DO_NOT_ENABLE_FULL_BOOK',
  suppressedLatinLabels=exceptions,sections=[dict(number=r['number'],Latin=dict(available=r.get('correspondence_status')!='UNAVAILABLE',correspondence=r['correspondence_status'],note=r.get('reader_note')),contextTarget=r.get('contextTarget') or r['Latin_paragraph_id']) for r in adopted])
 expected=[dict(number=r['number'],text=r['Latin_interval']['text'],locator=r['Latin_locator']) for r in adopted if r.get('Latin_interval')]
 save(P/'BOUNDARIES.json',rows);save(P/'IDENTITY_REGISTRY_PARTIAL.json',registry);save(P/'EXPECTED_REVIEWED_INTERVALS.json',expected)
 save(P/'INHERITED_LABEL_EXCEPTIONS_PARTIAL.json',exceptions)
 print(b,len(adopted),'reviewed starts;',len(expected),'complete adjoining intervals for isolated partial reader QA')
