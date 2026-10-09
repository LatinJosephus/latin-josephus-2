"""Apply only adopted routine milestones; never enables an incomplete book."""
from pathlib import Path
import sys,json
from source_scope import Book,digest
from verify_locators import validate
ROOT=Path(__file__).resolve().parents[2]
b=int(sys.argv[1]);assert b in [14,15];roman={14:'XIV',15:'XV'}[b]
P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
plan=json.loads((P/'APPROVED_MARKER_PLAN_PARTIAL.json').read_text())
source=(P/'frozen-inputs/Latin.xml').read_bytes();assert digest(source)==plan['source_sha256']
book=Book(raw=source);ops=[]
for row in plan['markers']:
    loc=row['locator'];validate(book,loc)
    ops.append(dict(number=row['number'],at=loc['raw_byte'],marker=row['marker'],locator=loc))
assert len({o['at'] for o in ops})==len(ops)
output=source
for op in sorted(ops,key=lambda o:o['at'],reverse=True):output=output[:op['at']]+op['marker'].encode()+output[op['at']:]
target=ROOT/f'assets/xml/antiquities/Latin/book-{b:02}.xml'
current=target.read_bytes()
if current not in [source,output]:
    previous=json.loads((P/'LATIN_PARTIAL_IMPLEMENTATION.json').read_text())
    assert digest(current)==previous['after_sha256'],'Refuse unrecorded existing modifications'
    recovered=current
    for op in sorted(previous['inverse_operations'],key=lambda o:o['at'],reverse=True):
        assert recovered[op['at']:op['at']+op['length']]==op['expected'].encode()
        recovered=recovered[:op['at']]+recovered[op['at']+op['length']:]
    assert recovered==source,'Previous checkpoint must recover the same frozen bytes'
after=Book(raw=output);assert after.stream==book.stream
assert after.tree.xpath('//@xml:id')==book.tree.xpath('//@xml:id')
assert after.tree.xpath('//@sameAs')==book.tree.xpath('//@sameAs')
assert [x['text'] for x in after.labels]==[x['text'] for x in book.labels]
inverse=[];shift=0
for op in sorted(ops,key=lambda o:o['at']):
    inverse.append(dict(number=op['number'],at=op['at']+shift,length=len(op['marker'].encode()),expected=op['marker']));shift+=len(op['marker'].encode())
recovery=output
for op in sorted(inverse,key=lambda o:o['at'],reverse=True):
    assert recovery[op['at']:op['at']+op['length']]==op['expected'].encode()
    recovery=recovery[:op['at']]+recovery[op['at']+op['length']:]
assert recovery==source
target.write_bytes(output)
q=dict(book=b,status='PARTIAL_LOCAL_CORPUS_IMPLEMENTATION_FULL_BOOK_NOT_CERTIFIED',source_path=str(target),
    source_sha256=digest(source),after_sha256=digest(output),recovered_sha256=digest(recovery),exact_byte_reversal=True,
    narrative_words_spelling_punctuation_whitespace_unchanged=True,existing_ids_sameAs_labels_paragraphs_divisions_unchanged=True,
    milestones_added=len(ops),operations=ops,inverse_operations=inverse,retained_starts=plan['retained_starts'],
    approved_sections=plan['approved_sections'],remaining_Latin_reviews=plan['remaining_Latin_reviews'],
    introduced_absence_claims=plan.get('unavailable_sections',[]),qualified_correspondence_sections=[r['number'] for r in json.loads((P/'BOUNDARIES.json').read_text()) if r.get('correspondence_status','').startswith(('PARTIAL','PRESENT_WITH'))],
    reader_availability_changed=False,reader_certified=False,registry_needed_before_enablement=True)
(P/'LATIN_PARTIAL_IMPLEMENTATION.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(b,'implemented',len(ops),'milestones; byte-exact reversal PASS; full-book certification PENDING.')
