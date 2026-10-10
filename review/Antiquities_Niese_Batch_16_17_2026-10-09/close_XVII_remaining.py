"""Explicit reviewer decisions and unresolved cut packet; no production edits."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]; P=ROOT/'review/Antiquities_Niese_BookXVII_2026-10-09'
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,digest
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
g=Book(P/'frozen-inputs/Greek.xml'); l=Book(P/'frozen-inputs/Latin.xml')
rows=json.loads((P/'BOUNDARIES.json').read_text()); r=rows[30]
old=r['Greek_candidate_locator']; unit=next(u for u in g.units if u['id']=='greek-book17-num29')
new=g.locate(unit['book_start']+unit['text'].index('διόπερ φιλία'))
save(P/'DECISION_XVII_030_031.json',dict(status='ROUTINE_PRINT_SUPPORTED_GREEK_CLAUSE_START_APPROVED_NOT_APPLIED',
    original_candidate=old,approved_locator=new,Greek_source_sha256=digest(g.raw),
    original_intervals={str(n):rows[n-1]['Greek_candidate_interval'] for n in [29,30,31]},
    reason='The inherited marker before τε splits διόπερ φιλία τε πιστὴ. Niese IV p.75/PDF89 puts 31 alongside the line ending διόπερ φιλία; it is a marginal line number, not an exact tag before τε on the next line. The whole causal clause starts διόπερ. Independent Loeb VIII p.386/PDF402 explicitly prints 31 before διόπερ φιλία. Adopt the whole causal clause, with Latin Ob hoc, under the accepted syntax-and-print rule. The inherited candidate and raw position remain historical evidence.',
    evidence=['evidence/Niese-IV-PDF089.jpg','../Antiquities_Niese_Batch_16_17_2026-10-09/evidence/Loeb-VIII-PDF402.jpg'],
    implementation_approved=True,applied=False,certified=False))
r['Greek_candidate_locator']=new
r['Greek_candidate_interval']='διόπερ φιλία '+r['Greek_candidate_interval']
save(P/'BOUNDARIES.json',rows)
save(P/'REVIEWED_ANCHORS_031.json',[[31,'latin-book17-num29','Ob hoc fida',89,'Whole causal clause: the Niese numeral stands beside διόπερ φιλία, and Loeb independently prints 31 before διόπερ. Greek inherited τε-only cut is corrected as recorded in DECISION_XVII_030_031; Latin Ob hoc fida begins the corresponding clause. Complete Greek 29–31 and the full Latin paragraph plus neighbours reviewed.']])
u=next(u for u in l.units if u['id']=='latin-book17-num68')
starts={s:l.locate(u['book_start']+u['text'].index(s)) for s in ['Nunc itaque','epistolamque antipatri','Ego autem plurimum','Haec dicens']}
save(P/'DECISION_XVII_075_076.json',dict(status='PENDING_EDITOR_ADJUDICATION_NO_DISPUTED_CUT_APPLIED',
    Greek={str(n):rows[n-1]['Greek_candidate_interval'] for n in [74,75,76,77]},complete_Latin_paragraph=u['text'],source_sha256=digest(l.raw),
    printed_evidence=dict(Niese=dict(pdf_page=97,printed_page=83,image='evidence/Niese-IV-PDF097.jpg',inspected=True),Loeb=dict(pdf_page=422,printed_page=406,image='../Antiquities_Niese_Batch_16_17_2026-10-09/evidence/Loeb-VIII-PDF422.jpg',inspected=True,role='independent control only')),
    finding='Greek 75 orders burning the poison; 76 contains bringing/executing the instructions or letters and the report of burning most but retaining some. Latin merges poison and Antipater’s letter as two objects of one imperative: Illud uenenum ad portans epistolamque antipatri me uidente conbure. Ego autem plurimum enim igni contradens, aliquantulum reseruaui. Both portions survive, but the instruction is syntactically reattached. No cause is inferred.',
    common_start_75=starts['Nunc itaque'],next_start_77=starts['Haec dicens'],
    alternatives=[dict(id='A',start_76=starts['epistolamque antipatri'],incipit='epistolamque antipatri',consequence='Earliest literal letter correspondence begins 76 within the imperative. Its shared verb conbure, including the poison-burning counterpart of Greek 75, lands in 76. Qualify both extents.'),dict(id='B',start_76=starts['Ego autem plurimum'],incipit='Ego autem plurimum',consequence='Keep the entire imperative in 75; begin 76 with the reported burning and retention. Qualify 76 with the earlier-surviving letter instruction and reciprocal note at 75. No omission claim or duplicated text.')],
    recommended='B',recommendation_reason='Preserves the joint imperative and provides a clear narrative cut with explicit earlier-survival qualification.',implementation_approved=False,applied=False,certified=False))
(P/'DECISION_XVII_075_076.txt').write_text('''XVII.75/76 — merged Latin imperative

Status: pending editor decision; neither disputed cut applied.
Niese IV (1890), p.83 / PDF97, and independent Loeb VIII p.406 / PDF422 inspected.

Greek 75 orders burning the poison; Greek 76 includes bringing/performing
the instructions or letters and the report of burning most but retaining some.
Latin merges poison and Antipater's letter in one imperative:
Illud uenenum ad portans epistolamque antipatri me uidente conbure.
Ego autem plurimum enim igni contradens, aliquantulum reseruaui...

A: begin 76 before epistolamque antipatri. This takes the earliest literal
letter counterpart, but divides the imperative and puts its shared burn verb
and poison-burning counterpart of Greek 75 into 76. Qualify both sections.

B (recommended): begin 76 before Ego autem plurimum. Keep the whole imperative
in 75. Qualify 76 because its letter instruction survives earlier in 75; give
75 a reciprocal note. Both passages remain present; no cause is inferred.

75 begins Nunc itaque in either case; 77 begins Haec dicens. The JSON packet
preserves complete Greek 74–77, the full Latin paragraph and exact raw locators.
''',encoding='utf8',newline='\n')
history=json.loads((P/'DECISION_HISTORY.json').read_text())
history.extend([dict(kind='ROUTINE_PRINT_SUPPORTED_GREEK_START',sections=[30,31],packet='DECISION_XVII_030_031.json',status='APPROVED_NOT_APPLIED'),dict(kind='EDITORIAL_WORD_CUT_QUESTION',sections=[75,76],packet='DECISION_XVII_075_076.json',recommendation='B',status='PENDING')])
save(P/'DECISION_HISTORY.json',history)
print('XVII 31 clause decision and 75/76 concrete alternatives prepared; no production source changed.')
