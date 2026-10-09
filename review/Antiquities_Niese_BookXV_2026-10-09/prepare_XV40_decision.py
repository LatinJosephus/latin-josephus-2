from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Antiquities_Niese_Batch_14_15_2026-10-09'))
import json
from source_scope import Book
from verify_locators import validate
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'review/Antiquities_Niese_BookXV_2026-10-09'
def save(name,data): (P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
rows=json.loads((P/'BOUNDARIES.json').read_text())
l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes())
u=next(u for u in l.units if u['id']=='latin-book15-num39')
def loc(phrase):
    assert u['text'].count(phrase)==1
    v=l.locate(u['book_start']+u['text'].index(phrase));validate(l,v);return v
start=loc('Itaque rex herodes');end=loc('quod prius antiochus')
choices=[]
for key,phrase,recommend,reason in [
 ('A','praeter legem exuit',False,'Captures the first surviving legality counterpart of Greek 40. Splits the removal predicate: section 39 ends before its verb exuit; section 40 begins with legality plus that verb.'),
 ('B','seditiones domesticas pacando',True,'Preserves the complete Latin removal predicate in 39 and starts 40 with the surviving motive and prohibition. The anticipatory praeter legem remains with 39, and must be disclosed as reordered correspondence.'),
 ('C','nam non licebat',False,'Starts only at the prohibition. Leaves both the motive and praeter legem with 39, although they correspond to Greek 40.')]:
    v=loc(phrase);choices.append(dict(option=key,phrase=phrase,recommended=recommend,locator=v,
        section39=dict(start=start['book_offset'],end=v['book_offset'],text=l.stream[start['book_offset']:v['book_offset']]),
        section40=dict(start=v['book_offset'],end=end['book_offset'],text=l.stream[v['book_offset']:end['book_offset']]),reason=reason))
data=dict(book=15,section=40,status='PENDING_USER_EDITORIAL_DECISION',Latin_paragraph='latin-book15-num39',Latin=u['text'],
 Greek={str(n):rows[n-1]['Greek'] for n in [38,39,40,41,42]},options=choices,
 printed_references=[dict(edition='Niese III (1892)',printed_page=339,pdf_page=411,image='evidence/Niese-III-PDF411.jpg',inspected=True,
 observation='40 lies in the left margin alongside the end of the preceding Babylonian sentence; the new clause starts with ἔνθεν. 41 lies beside the end of παραλαβών, before ἀλλὰ πρῶτος.'),
 dict(edition='Loeb VIII, Marcus/Wikgren, first published 1963; supplied reprint',printed_page=20,pdf_page=36,image='evidence/Loeb-PDF036.jpg',inspected=True,
 observation='40 lies alongside λωνίαν ἀπῳκίσθησαν, immediately before ἔνθεν on the same line. 41 lies alongside παραλαβών, before ἀλλὰ πρῶτος on the same line.'),
 dict(edition='Loeb English control',printed_page=21,pdf_page=37,image='evidence/Loeb-PDF037.jpg',inspected=True)],
 contextual_review='Latin sections 31-50 and Greek 31-50 inspected. The origins, family, earlier favour and prior appointment in 39-40 are compressed out here. Removal, domestic motive, illegality and prohibition survive with reordering. This is partial correspondence, not whole-section absence; no cause of compression or claim about the whole Latin tradition is inferred.',
 recommendation='B',source_sha256=l.raw_hash if hasattr(l,'raw_hash') else None,reader_certified=False)
save('DECISION_XV_040.json',data)
rows[39].update(Latin_review_status='INDIVIDUALLY_REVIEWED_PENDING_CUT',physical_placement_status='PENDING_EDITORIAL_CHOICE',
 correspondence_status='PARTIAL_WITH_REORDERING',editorial_status='PENDING_USER_DECISION',Greek_print_status='VISUALLY_REVIEWED_IDENTITY_AND_CLAUSE_CONTEXT',
 decision_packet='DECISION_XV_040.json',implementation_approved=False,reader_certified=False)
save('BOUNDARIES.json',rows)
md='''# XV.40 — decision required

Recommendation: **B, before `seditiones domesticas pacando`**. This preserves the complete removal statement in XV.39 and gives XV.40 the surviving domestic motive and legal prohibition. Disclose that `praeter legem` anticipates Greek 40 while remaining in the Latin interval for 39.

Greek 39 removes Ananel and describes his Babylonian origins. Greek 40 continues his origin, lineage, previous favour and appointment, then describes his removal to end domestic trouble, its illegality and the prohibition against removing an incumbent. Latin compresses those details into:

> Itaque rex herodes statim principatu sacerdotii anandum praeter legem exuit, seditiones domesticas pacando, nam non licebat aliquem honore semel accepto fraudari, quod prius antiochus epifanis destruxit ...

| Choice | Exact start of 40 | Effect on 39 and 40 |
|---|---|---|
| A | `praeter legem exuit` | Takes the first legality counterpart into 40, but separates 39's object from its verb `exuit`. |
| **B** | `seditiones domesticas pacando` | Keeps 39's removal predicate intact; 40 contains motive and prohibition. Qualify the anticipatory legality phrase in 39. |
| C | `nam non licebat` | Gives 40 only the prohibition; leaves the motive and legality phrase in 39. |

All choices end 40 before `quod prius antiochus`, the independently supported beginning of 41. Full node/Unicode/raw-byte locators and both resulting extents are in [DECISION_XV_040.json](DECISION_XV_040.json). No change has been adopted for 40.

Both printed controls were visually inspected: Niese III (1892), p.339 / PDF411, and Loeb VIII, Greek p.20 / PDF36 and English p.21 / PDF37. The marginal numeral locates the section; it does not resolve the reordered Latin cut.

![Niese p339](evidence/Niese-III-PDF411.jpg)

![Loeb Greek p20](evidence/Loeb-PDF036.jpg)

![Loeb English p21](evidence/Loeb-PDF037.jpg)

The transcription has surviving correspondence for 40. Whole-section absence is unsupported. No missing wording is supplied, and no physical loss or statement about the entire Latin tradition is inferred.
'''
(P/'DECISION_XV_040.md').write_text(md,encoding='utf8',newline='\n')
history=json.loads((P/'DECISION_HISTORY.json').read_text());history.append(dict(kind='EDITORIAL_ALTERNATIVES',section=40,packet='DECISION_XV_040.json',adopted=False,recommendation='B'));save('DECISION_HISTORY.json',history)
print('Prepared XV.40 alternatives; no cut adopted.')
