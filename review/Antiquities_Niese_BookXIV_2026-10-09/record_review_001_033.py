"""Record individually read XIV 1–33; unreviewed rows stay explicitly unreviewed."""
from pathlib import Path
import sys,json,re
P=Path(__file__).resolve().parent; ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_Batch_14_15_2026-10-09'))
from source_scope import Book,digest
from verify_locators import validate,validate_all_nodes
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
g=Book(raw=(P/'frozen-inputs/Greek.xml').read_bytes());l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes())
reviews=json.loads((P/'REVIEWED_ANCHORS_001_033.json').read_text());rows=json.loads((P/'BOUNDARIES.json').read_text())
pages={**{n:311 for n in range(1,5)},**{n:312 for n in range(5,11)},**{n:313 for n in range(11,16)},**{n:314 for n in range(16,20)},**{n:315 for n in range(20,26)},**{n:316 for n in range(26,32)},32:317,33:317}
observations=[];plans=[]
for n,pid,phrase,reason in reviews:
    unit=next(u for u in l.units if u['id']==pid);assert unit['text'].count(phrase)==1,(n,phrase)
    semantic=l.locate(unit['book_start']+unit['text'].index(phrase));validate(l,semantic)
    # Individually accepted physical starts, not an inference from a num claim.
    inherited=next((x for x in l.labels if x['id']==pid),None) if n in [1,4,8,14,19,29] else None
    physical=l.locate(l.first_content(inherited['book_offset'])) if inherited else semantic
    validate(l,physical);r=rows[n-1];validate(g,r['locator'])
    r.update(Latin_locator=physical,Latin_semantic_incipit_locator=semantic,Latin_anchor_phrase=phrase,Latin_paragraph_id=pid,
        Latin_review_status='INDIVIDUALLY_REVIEWED',physical_placement_status='RETAIN_EXISTING_NUM' if inherited else 'ADD_INTERNAL_NIESE_MILESTONE',
        correspondence_status='PRESENT_WITH_LOCAL_COMPRESSION' if n==5 else 'PRESENT',editorial_status='ROUTINE_SOURCE_SUPPORTED',
        review_reason=reason,Greek_print_status='VISUALLY_REVIEWED_IDENTITY_AND_CLAUSE_CONTEXT',implementation_approved=True,reader_certified=False)
    page=pages[n];image=f'evidence/Niese-III-{"detail-" if page in [311,312,315] else ""}PDF{page:03}.jpg'
    observed=dict(book=14,number=n,pdf_page=page,printed_page=page-72,image=image,image_inspected=True,
        printed_numeral_observation='Implicit opening; no marginal 1; running-head range and body I.1 identify first citation.' if n==1 else 'Marginal numeral read on the line containing the corresponding clause or adjoining preceding words; numeral alignment alone is not a word delimiter.',
        exact_Greek_choice=r['Greek'][:90],choice_basis='Existing Greek start retained after direct page comparison with the preceding/following clauses.',OCR_is_authority=False)
    r['print_observation']=observed;observations.append(observed)
    if not inherited:plans.append(dict(number=n,marker=f'<milestone unit="niese" n="{n}"/>',locator=physical,source_sha256=digest(l.raw),reason=reason))
for i,r in enumerate(rows[:33]):
    end=rows[i+1].get('Latin_locator') if i<32 else None
    if end:r['Latin_interval']=dict(start=r['Latin_locator']['book_offset'],end=end['book_offset'],text=l.stream[r['Latin_locator']['book_offset']:end['book_offset']])
    else:r['Latin_interval_status']='Following 34 start not yet adopted; final extent remains provisional.'
save(P/'BOUNDARIES.json',rows);save(P/'PRINT_OBSERVATIONS_001_033.json',observations)
save(P/'APPROVED_MARKER_PLAN_001_033.json',dict(book=14,source_sha256=digest(l.raw),markers=plans,retained_starts=[r['number'] for r in rows[:33] if r['physical_placement_status']=='RETAIN_EXISTING_NUM'],
    executable_label_exceptions=[dict(paragraph='latin-book14-num25',visible_label='[II.ii.26]',visible_claim=26,actual_section=25,action='SUPPRESS_EXECUTABLE_CLAIM_PRESERVE_VISIBLE_LABEL')],
    full_book_complete=False,new_book_reader_QA='NOT_RUN',remaining_Latin_reviews=458))
save(P/'LOCATOR_QA_001_033.json',dict(status='PASS',Greek=validate_all_nodes(g),Latin=validate_all_nodes(l),individually_validated_Greek_and_Latin_boundary_pairs=33,
    character_and_byte_coordinates_distinct=True,locators_pinned_to_frozen_worktree_bytes=True,full_book_certified=False))
history=json.loads((P/'DECISION_HISTORY.json').read_text());history.append(dict(kind='ROUTINE_REVIEW_001_033',sections=list(range(1,34)),adopted=True,human_editorial_question=False,Greek_markers_moved=0,Latin_milestones_planned=len(plans)))
save(P/'DECISION_HISTORY.json',history)
print('XIV: 33 individual reviews,',len(plans),'approved additions; full-book completion remains provisional.')
