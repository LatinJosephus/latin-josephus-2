"""Record actually supplied individual readings, not automatic alignment guesses."""
from pathlib import Path
import sys,json,re
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,digest,NS,raw_char_positions
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def independently_validate(model,point):
    path=point['text_node_path'];tail=path.endswith('/tail()')
    expr=re.sub(r'(?<=/)([A-Za-z][A-Za-z0-9]*)(?=\[)',r't:\1',path.rsplit('/',1)[0])
    nodes=model.tree.xpath(expr,namespaces=NS);assert len(nodes)==1,path
    text=nodes[0].tail if tail else nodes[0].text
    char=text[point['node_offset']];assert char==model.stream[point['book_offset']]
    assert raw_char_positions(model.raw,point['raw_byte'],char)==[point['raw_byte']]
def main():
    b=int(sys.argv[1]);roman={16:'XVI',17:'XVII'}[b];P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
    name=sys.argv[2];reviews=json.loads((P/name).read_text());rows=json.loads((P/'BOUNDARIES.json').read_text())
    g=Book(P/'frozen-inputs/Greek.xml');l=Book(P/'frozen-inputs/Latin.xml')
    for n,pid,phrase,page,reason in reviews:
        r=rows[n-1];assert r['Latin_review_status']=='UNREVIEWED',(n,'already reviewed')
        unit=next(u for u in l.units if u['id']==pid);assert unit['text'].count(phrase)==1,(n,phrase)
        point=l.locate(unit['book_start']+unit['text'].index(phrase));independently_validate(l,point)
        greek=r['Greek_candidate_locator']
        if n==1:
            extent=re.match(r'^περιέχει ἡ βίβλος χρόνον ἐτῶν .*?\. ',g.stream)
            assert extent;greek=g.locate(extent.end())
        independently_validate(g,greek)
        r.update(Greek_reviewed_locator=greek,Greek_print_status='VISUALLY_REVIEWED_NUMBER_AND_CLAUSE_CONTEXT',
            Greek_start_choice=g.stream[greek['book_offset']:greek['book_offset']+100],Latin_locator=point,
            Latin_anchor_phrase=phrase,Latin_review_status='INDIVIDUALLY_REVIEWED',physical_placement_status='PROPOSE_APPROVED_NIESE_MILESTONE',
            correspondence_status='PRESENT_WITH_LEXICAL_VARIATION' if b==17 and n==8 else 'PRESENT',editorial_status='ROUTINE_SOURCE_SUPPORTED',
            review_reason=reason,source_sha256=digest(l.raw),implementation_approved=True,applied=False,reader_certified=False,
            print_observation=dict(edition='Niese IV (1890)',pdf_page=page,printed_page=page-14,
                image=f'evidence/Niese-IV-PDF{page:03}.jpg',image_inspected=True,
                numeral_observation='Implicit first section at body I.1; extent notice belongs to preceding paratext.' if n==1 else 'Printed marginal number inspected with whole adjoining clause; not treated as a word-level tag.',OCR_is_authority=False))
    for i,r in enumerate(rows):
        if r.get('Latin_locator') and i+1<len(rows) and rows[i+1].get('Latin_locator'):
            a=r['Latin_locator']['book_offset'];z=rows[i+1]['Latin_locator']['book_offset'];assert a<z,(i,a,z)
            r['reviewed_neighbour_extent']=dict(start=a,end=z,text=l.stream[a:z],status='EXTENT_TO_NEXT_REVIEWED_START')
    save(P/'BOUNDARIES.json',rows)
    history=json.loads((P/'DECISION_HISTORY.json').read_text());history.append(dict(kind='INDIVIDUAL_REVIEW_BATCH',sections=[x[0] for x in reviews],input=name,adopted=True,implemented=False,reader_certified=False))
    save(P/'DECISION_HISTORY.json',history)
    adopted=[x for x in rows if x['Latin_review_status']=='INDIVIDUALLY_REVIEWED']
    save(P/'APPROVED_MARKER_PLAN_PARTIAL.json',dict(book=b,source_sha256=digest(l.raw),markers=[dict(number=r['number'],locator=r['Latin_locator'],marker=f'<milestone unit="niese" n="{r["number"]}"/>') for r in adopted],
        individual_review_count=len(adopted),unreviewed_count=len(rows)-len(adopted),applied=False,full_book_complete=False,reader_certified=False))
    print(roman,'individual reviewed starts',len(adopted),'/',len(rows),'production unchanged')
if __name__=='__main__':main()
