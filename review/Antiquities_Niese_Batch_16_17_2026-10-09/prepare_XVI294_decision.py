"""Exact alternatives for the newly observed XVI294/295 displacement."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'review/Antiquities_Niese_BookXVI_2026-10-09'
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,digest
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
l=Book(P/'frozen-inputs/Latin.xml');rows=json.loads((P/'BOUNDARIES.json').read_text())
u=next(u for u in l.units if u['id']=='latin-book16-num293')
phrases=['Aestuabat etiam','conabatur defuncto','Interea obado','Caesar autem aretae','Ille uero cum donis']
points={s:l.locate(u['book_start']+u['text'].index(s)) for s in phrases}
def span(a,z):return dict(start=points[a],end=points[z],text=l.stream[points[a]['book_offset']:points[z]['book_offset']])
a,b,c,d,z=phrases
packet=dict(book=16,sections=[293,294,295,296],status='PENDING_EDITOR_ADJUDICATION_NO_DISPUTED_REPRESENTATION_APPLIED',
 source_sha256=digest(l.raw),Greek={str(n):rows[n-1]['Greek_candidate_interval'] for n in range(293,297)},complete_Latin_paragraph=u['text'],
 finding='Latin gives Herod’s concern about Syllaeus, then Syllaeus’s bid and court gifts, then Aeneas/Aretas’s accession, then Caesar’s displeasure at that accession. Greek294 gives the concern and accession;295 gives Syllaeus’s bid and Caesar’s displeasure. These survive in different order. Obadas’s death is also repeated locally and must remain literal.',
 alternatives=[dict(id='A',ranges={'294':[span(a,d)],'295':[span(d,z)]},consequence='Contiguous physical selections:294 includes the earlier Syllaeus bid from295;295 begins with Caesar’s displeasure. Explicit reciprocal qualification records295’s bid surviving earlier. No claim of absence or complete exact correspondence.'),
 dict(id='B',ranges={'294':[span(a,b),span(c,d)],'295':[span(b,c),span(d,z)]},consequence='Two fragments each, shown in unchanged physical witness order.294’s first fragment ends inside the transmitted relative construction; explain the reattached syntax. Preserve all words once, including repeated Obadas death wording; explicit ends prevent swallowing.')],
 recommended='B',recommendation_reason='Keeps both surviving components under their corresponding Greek identities without reordering the witness, duplicating words or suppressing the Aretas accession. The source itself reattaches clauses; the view must disclose its fragments and qualifications.',
 printed_evidence=[dict(edition='Niese IV (1890)',pdf_page=n,printed_page=n-14,image=f'evidence/Niese-IV-PDF{n:03}.jpg',inspected=True) for n in [63,64]],
 previous_start=rows[292]['Latin_locator'],next_start=points[z],implementation_approved=False,applied=False,certified=False)
save(P/'DECISION_XVI_294_295.json',packet)
(P/'DECISION_XVI_294_295.txt').write_text('''XVI.294/295 — displaced succession material

Pending editor decision. No disputed representation applied.
Niese IV (1890), pp.49–50 / PDF63–64 visually inspected.

Greek294: Herod's concern about Syllaeus, Obadas's death, Aeneas/Aretas accession.
Greek295: Syllaeus's bid and court gifts, Caesar's displeasure with Aretas.

Latin sequence in num293:
Aestuabat etiam de fileo cui credebatur a caesare, qui presens romae
conabatur defuncto obabo rege arabum in regno succedere multis caesari
promissis pecuniis aliisque in aula potentibus. Interea obado moriente
dinea qui post areta dictus est regnum aripuit. Caesar autem aretae
minabatur quod regnare presumpsisset prius quam sibi de hoc scriberet.

A: contiguous294 Aestuabat→Caesar,295 Caesar→Ille uero cum donis.
Qualify the earlier-surviving295 bid within294, reciprocally. This preserves
whole clauses but the294 selection contains part of Greek295.

B (recommended):294 gets Aestuabat→conabatur plus Interea→Caesar;
295 gets conabatur→Interea plus Caesar→Ille uero cum donis.
Show each pair in physical source order with explicit fragment/end notices.
The first294 fragment ends within a relative construction; qualify this.
No words are moved or duplicated, including the repeated Obadas-death detail.

JSON retains full Greek293–296, entire Latin paragraph, all locators/hashes,
adjoining starts and literal proposed extents. Cause of difference undetermined.
''',encoding='utf8',newline='\n')
h=json.loads((P/'DECISION_HISTORY.json').read_text());h.append(dict(kind='EDITORIAL_DISPLACEMENT_REPRESENTATION',sections=[294,295],packet='DECISION_XVI_294_295.json',recommendation='B',status='PENDING'))
save(P/'DECISION_HISTORY.json',h)
print('Concrete294/295 representation packet prepared; no production changes.')
