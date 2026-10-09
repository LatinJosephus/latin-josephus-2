"""Record a supplied individual-review batch and recompute adopted neighbour extents."""
from pathlib import Path
import sys,json,re
from source_scope import Book,digest
from verify_locators import validate,validate_all_nodes
ROOT=Path(__file__).resolve().parents[2]
b=int(sys.argv[1]); roman={14:'XIV',15:'XV'}[b];P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
name=sys.argv[2]; reviews=json.loads((P/name).read_text()); rows=json.loads((P/'BOUNDARIES.json').read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
g=Book(raw=(P/'frozen-inputs/Greek.xml').read_bytes());l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes())
terminal_verified=(P/'TERMINAL_EXTENT.json').exists()
for n,key,phrase,page,retained,reason in reviews:
    unit=l.units[key-1] if isinstance(key,int) else next(u for u in l.units if u['id']==key)
    assert unit['text'].count(phrase)==1,(n,phrase)
    semantic=l.locate(unit['book_start']+unit['text'].index(phrase));validate(l,semantic)
    label=next((x for x in l.labels if x['unit']==unit['index']),None) if retained else None
    assert not retained or label
    physical=l.locate(label['book_offset']) if label else semantic;validate(l,physical)
    r=rows[n-1];validate(g,r['locator'])
    observation=dict(book=b,number=n,edition='Niese III (1892)',pdf_page=page,printed_page=page-72,image=f'evidence/Niese-III-PDF{page:03}.jpg',image_inspected=True,
        printed_numeral_observation='Implicit opening: no marginal 1; body chapter heading and running range independently identify the opening.' if n==1 else 'Marginal numeral visually read beside the corresponding or adjoining preceding clause; the printed line is not a word tag.',
        exact_Greek_choice=r['Greek'][:90],choice_basis='Source incipit compared with printed clause and adjoining context; retained without textual emendation.',OCR_is_authority=False)
    r.update(Latin_locator=physical,Latin_semantic_incipit_locator=semantic,Latin_anchor_phrase=phrase,Latin_paragraph_id=unit['id'] or None,
        contextTarget=unit['id'] or next(u['id'] for u in reversed(l.units[:unit['index']]) if u['id']),Latin_review_status='INDIVIDUALLY_REVIEWED',
        physical_placement_status='RETAIN_EXISTING_NUM' if label else 'ADD_INTERNAL_NIESE_MILESTONE',correspondence_status='PRESENT',
        editorial_status='ROUTINE_SOURCE_SUPPORTED',review_reason=reason,Greek_print_status='VISUALLY_REVIEWED_IDENTITY_AND_CLAUSE_CONTEXT',print_observation=observation,implementation_approved=True,reader_certified=False)
for i,r in enumerate(rows):
    if r.get('Latin_locator'):
        j=i+1
        while j<len(rows) and rows[j].get('correspondence_status')=='UNAVAILABLE':j+=1
        end=rows[j].get('Latin_locator') if j<len(rows) else None
        if end:
            start=r['Latin_locator']['book_offset'];finish=end['book_offset'];assert start<finish,(i,start,finish)
            r['Latin_interval']=dict(start=start,end=finish,text=l.stream[start:finish]);r.pop('Latin_interval_status',None)
        elif i==len(rows)-1 and terminal_verified:
            start=r['Latin_locator']['book_offset'];r['Latin_interval']=dict(start=start,end=len(l.stream),text=l.stream[start:]);r.pop('Latin_interval_status',None)
        else:r['Latin_interval_status']='Following start not yet adopted; extent remains provisional.'
save(P/'BOUNDARIES.json',rows)
adopted=[r for r in rows if r.get('Latin_locator')];plans=[dict(number=r['number'],marker=f'<milestone unit="niese" n="{r["number"]}"/>',locator=r['Latin_locator'],reason=r.get('review_reason','Explicit user approval recorded in the editorial decision packet.')) for r in adopted if r['physical_placement_status']=='ADD_INTERNAL_NIESE_MILESTONE']
save(P/'APPROVED_MARKER_PLAN_PARTIAL.json',dict(book=b,source_sha256=digest(l.raw),markers=plans,retained_starts=[r['number'] for r in adopted if r['physical_placement_status']=='RETAIN_EXISTING_NUM'],
    approved_sections=[r['number'] for r in rows if r.get('implementation_approved')],unavailable_sections=[r['number'] for r in rows if r.get('correspondence_status')=='UNAVAILABLE'],full_book_complete=False,reader_certified=False,remaining_Latin_reviews=sum(r['Latin_review_status']=='UNREVIEWED' for r in rows)))
history=json.loads((P/'DECISION_HISTORY.json').read_text());history.append(dict(kind='INDIVIDUAL_REVIEW_BATCH',input=name,sections=[r[0] for r in reviews],adopted=True,neighbour_extents_recomputed=True,planned_milestones_total=len(plans)))
save(P/'DECISION_HISTORY.json',history)
save(P/'LOCATOR_QA_PARTIAL.json',dict(status='PASS',Greek=validate_all_nodes(g),Latin=validate_all_nodes(l),adopted_boundaries=len(adopted),complete_book=False))
print(b,'adopted',len(adopted),'retained',len(adopted)-len(plans),'milestones planned',len(plans))
