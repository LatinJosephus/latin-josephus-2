from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Antiquities_Niese_Batch_14_15_2026-10-09'))
import json
from source_scope import Book,digest
from verify_locators import validate
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'review/Antiquities_Niese_BookXIV_2026-10-09'
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
r=json.loads((P/'BOUNDARIES.json').read_text());l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes());u=next(u for u in l.units if u['id']=='latin-book14-num158')
def loc(text):
 assert u['text'].count(text)==1
 v=l.locate(u['book_start']+u['text'].index(text));validate(l,v);return v
start=loc('Cum uero aemulatio');end=l.locate(next(u for u in l.units if u['id']=='latin-book14-num163')['book_start']);validate(l,end)
options=[]
for key,phrase,recommended,reason in [
 ('A','antipatrum, faciebat',True,'Starts at Antipater, the first explicit new subject matter of Greek 162. Leaves tractaretque as a difficult tail in 161; preserves every letter, comma and space without reconstruction.'),
 ('B','faciebat ab omni gente',False,'Starts at the honour-producing predicate, leaving Antipater’s name in 161 although it corresponds to Greek 162.'),
 ('C','tractaretque antipatrum',False,'Keeps the difficult verb and following object together in 162, but takes the preceding action word out of 161’s account of Phasael’s handling of public affairs.')]:
 v=loc(phrase);options.append(dict(option=key,phrase=phrase,recommended=recommended,locator=v,reason=reason,
 section161=dict(start=start['book_offset'],end=v['book_offset'],text=l.stream[start['book_offset']:v['book_offset']]),
 section162=dict(start=v['book_offset'],end=end['book_offset'],text=l.stream[v['book_offset']:end['book_offset']])))
packet=dict(book=14,section=162,status='PENDING_USER_EDITORIAL_DECISION',source_sha256=digest(l.raw),Latin_paragraph='latin-book14-num158',Latin=u['text'],
 Greek={str(n):r[n-1]['Greek'] for n in [160,161,162,163]},options=options,recommendation='A',
 printed_references=[dict(edition='Niese III (1892)',printed_page=270,pdf_page=342,image='evidence/Niese-III-PDF342.jpg',inspected=True,
 observation='162 in left margin at the line beginning τὴν ἐξουσίαν. The new clause ταῦτ᾽ Ἀντίπατρον follows the prior clause’s punctuation on that line.'),
 dict(edition='Loeb VII, Marcus, supplied 1966 edition',printed_page=534,pdf_page=546,image='evidence/Loeb-PDF546.jpg',inspected=True,
 observation='162 in left margin beside φερόμενος, ending 161’s administrative clause. ταῦτ᾽ is later on that line before Ἀντίπατρον on the next.')],
 contextual_review='Latin 158–167 and Greek 158–175 individually read. Greek 161 describes Phasael’s conduct; 162 turns to the resulting honours of Antipater. The Latin has the preserved sequence tractaretque antipatrum, faciebat. No punctuation correction, replacement with tractaret. quae or reconstructed word is authorized. The source also reverses Greek 162’s denial of disloyalty; retain transgressus est without correction.',
 correspondence_status='PRESENT_WITH_SYNTAX_AND_WORDING_DIFFERENCE',placement_status='PENDING_EDITORIAL_CHOICE',reader_certified=False)
save('DECISION_XIV_162.json',packet)
r[161].update(Latin_review_status='INDIVIDUALLY_REVIEWED_PENDING_CUT',physical_placement_status='PENDING_EDITORIAL_CHOICE',
 correspondence_status=packet['correspondence_status'],editorial_status='PENDING_USER_DECISION',Greek_print_status='VISUALLY_REVIEWED_IDENTITY_AND_CLAUSE_CONTEXT',decision_packet='DECISION_XIV_162.json',implementation_approved=False,reader_certified=False)
save('BOUNDARIES.json',r)
md='''# XIV.162 — exact cut in difficult preserved syntax

Recommendation: **A, immediately before `antipatrum, faciebat`**. This gives 162 its earliest explicit Antipater counterpart. The difficult preceding `tractaretque` remains in 161. Record the syntax limitation separately from the placement decision.

Greek 161 describes Phasael’s conduct toward Jerusalem and public affairs. Greek 162 says these events brought Antipater royal honours; it then says his success did not impair his loyalty to Hyrcanus. The Latin reads:

> ... et ierosolimi tas fauores sibi parabat, dum et ciuitatem haberet et populi negotia non ignoraret, tractaretque antipatrum, faciebat ab omni gente tamquam esset omnium dominus, honorari tamen ex tali claritate qualia saepius contingunt, hyrcani fidem transgressus est.

| Choice | Exact start of 162 | Effect |
|---|---|---|
| **A** | `antipatrum, faciebat` | Starts at the first Antipater counterpart. Leaves the difficult `tractaretque` as the preceding tail. |
| B | `faciebat ab omni gente` | Starts at the honours predicate; leaves the Antipater name with 161. |
| C | `tractaretque antipatrum` | Keeps the difficult verb/object sequence together, but takes the prior action word into 162. |

The Latin’s punctuation and wording remain unchanged under every choice. In particular, no replacement with `tractaret. quae antipatrum` is proposed, and `transgressus est` remains even though Greek denies disloyalty. This is surviving correspondence with a wording/syntax difference, not an absence.

Exact raw-byte, text/tail-node and Unicode locators, and the resulting complete intervals through the start of 163, are in [DECISION_XIV_162.json](DECISION_XIV_162.json). Greek identity and the shift to Antipater are independently confirmed by the inspected print:

![Niese III p270, PDF342](evidence/Niese-III-PDF342.jpg)

![Loeb VII p534, PDF546](evidence/Loeb-PDF546.jpg)

No Latin cut for 162 has been adopted. All independent XIV and XV work may continue.
'''
(P/'DECISION_XIV_162.md').write_text(md,encoding='utf8',newline='\n')
history=json.loads((P/'DECISION_HISTORY.json').read_text());history.append(dict(kind='EDITORIAL_ALTERNATIVES',section=162,packet='DECISION_XIV_162.json',adopted=False,recommendation='A'));save('DECISION_HISTORY.json',history)
print('XIV.162 alternatives prepared; no Latin cut adopted.')
