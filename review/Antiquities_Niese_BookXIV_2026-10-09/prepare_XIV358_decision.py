from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Antiquities_Niese_Batch_14_15_2026-10-09'))
from source_scope import Book,digest
from verify_locators import validate
P=Path(__file__).resolve().parent;rows=json.loads((P/'BOUNDARIES.json').read_text());l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes())
u=next(u for u in l.units if u['id']=='latin-book14-num355');start=rows[356]['Latin_locator']['book_offset'];end=rows[358]['Latin_locator']['book_offset']
options=[]
for letter,phrase in [('A','Quibus uerbis compulsus'),('B','cognitauerat pretermisit'),('C','matremque curans')]:
 loc=l.locate(u['book_start']+u['text'].index(phrase));validate(l,loc);cut=loc['book_offset']
 options.append(dict(option=letter,phrase=phrase,recommended=letter=='A',locator=loc,section357=dict(start=start,end=cut,text=l.stream[start:cut]),section358=dict(start=cut,end=end,text=l.stream[cut:end])))
packet=dict(book=14,section=358,status='PENDING_USER_DECISION',source_sha256=digest(l.raw),Latin_paragraph=u['id'],Latin=u['text'],Greek={str(n):rows[n-1]['Greek'] for n in [356,357,358,359,360]},options=options,
 print_evidence=[dict(edition='Niese III (1892)',printed_page=305,pdf_page=377,image='evidence/Niese-III-PDF377.jpg',inspected=True,numeral_position='Right margin 358 beside the preceding moral exhortation and the following biasth eis continuation. The opening counterpart is compulsion to abandon the attempt, not only care of the mother.'),dict(edition='Loeb VII (Marcus)',printed_page=636,pdf_page=648,image='evidence/Loeb-PDF648.jpg',inspected=True),dict(edition='Loeb VII English control',printed_page=637,pdf_page=649,image='evidence/Loeb-PDF649.jpg',inspected=True)],
 recommendation='A: begin at Quibus uerbis compulsus. This is the earliest explicit compulsion/abandonment counterpart of Greek358. The source interposes that phrase within the transmitted e peri ... culis sequence of the preceding moral exhortation. Preserve every byte and disclose the displaced357 tail in358, with reciprocal notes.',
 correspondence='Surviving partial/reordered correspondence, not whole-section absence. No cause of the transmitted interruption is established; no correction, relocation or reconstructed word is proposed.')
(P/'DECISION_XIV_358.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
r=rows[357];r.update(Greek_print_status='VISUALLY_REVIEWED_IDENTITY_AND_CLAUSE_CONTEXT',Latin_review_status='INDIVIDUALLY_REVIEWED',physical_placement_status='PENDING_EDITORIAL_CHOICE',correspondence_status='PARTIAL_WITH_COMPRESSION_AND_REORDERING',editorial_status='PENDING_USER_DECISION',implementation_approved=False,reader_certified=False,decision_packet='DECISION_XIV_358.json',Latin_paragraph_id=u['id'],contextTarget=u['id'],correspondence_limit=packet['correspondence'],print_observation=dict(edition='Niese III (1892)',printed_page=305,pdf_page=377,image='evidence/Niese-III-PDF377.jpg',image_inspected=True,printed_numeral_observation=packet['print_evidence'][0]['numeral_position'],exact_Greek_choice=r['Greek'],OCR_is_authority=False))
(P/'BOUNDARIES.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
history=json.loads((P/'DECISION_HISTORY.json').read_text());history.append(dict(kind='PENDING_EDITORIAL_ALTERNATIVES',section=358,packet='DECISION_XIV_358.json',recommendation='A',options=['A','B','C'],source_words_changed=False));(P/'DECISION_HISTORY.json').write_text(json.dumps(history,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
md='''# XIV.358 — transmitted interruption and alternative cuts

Recommendation: **A, before Quibus uerbis compulsus**. Greek357 gives the moral appeal against abandoning friends; Greek358 begins the compulsion to abandon Herod's attempted suicide, then care of his mother and the journey. The Latin transmits:

> Nam non hoc esse fortis siquidem, sed e peri Quibus uerbis compulsus facinus quod in se culis liberans, amatos traderet inimicis. cognitauerat pretermisit, matremque curans ...

The wording is interrupted: `e peri` and `culis liberans, amatos traderet inimicis` express material corresponding to357, while `Quibus uerbis compulsus facinus quod in se` and `cognitauerat pretermisit` express358. The cause is not established. No relocation, reconstructed wording or textual correction is proposed.

| Choice | Exact cut | Consequence |
|---|---|---|
| **A** | before `Quibus uerbis compulsus` | Starts358 at its first explicit counterpart; the displaced357 moral tail remains physically inside358. Requires reciprocal correspondence notes. |
| B | before `cognitauerat pretermisit` | Keeps the moral tail in357, while leaving the preceding358 compulsion/object wording in357 and separating it from its predicate. |
| C | before `matremque curans` | Starts358 at care of the mother; all preceding compulsion/abandonment wording corresponding to358 remains in357. |

Every option ends358 before the verified start of359, `In fuga uero nec`. Exact alternatives, Unicode/text-tail/raw UTF8 locators and both resulting intervals are in [DECISION_XIV_358.json](DECISION_XIV_358.json). Partial displaced correspondence must stay separate from confidence in any approved physical placement;358 is not absent.

Inspected primary: Niese III (1892), p305/PDF377. Inspected independent control: Loeb VII Greek p636/PDF648 and English p637/PDF649. Both place the compulsion at358's opening, but neither resolves ownership of the interposed Latin fragments.

![Niese305](evidence/Niese-III-PDF377.jpg)

![Loeb636](evidence/Loeb-PDF648.jpg)

![Loeb637](evidence/Loeb-PDF649.jpg)
'''
(P/'DECISION_XIV_358.md').write_text(md,encoding='utf8',newline='\n');print('XIV358 alternatives recorded; no marker applied')
