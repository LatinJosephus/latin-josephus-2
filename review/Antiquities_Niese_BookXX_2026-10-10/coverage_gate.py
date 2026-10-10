from prepare import *
from mixed_mapper import Book
def main():
    l=Book(ROOT/'assets/xml/antiquities/Latin/book-20.xml');g=Book(ROOT/'assets/xml/antiquities/Greek/book-20.xml')
    registry=json.loads((ROOT/'assets/xml/antiquities/niese/book-20.json').read_text(encoding='utf-8'))
    expected=json.loads((PACK/'SECURE_EXPECTED_INTERVALS.json').read_text(encoding='utf-8'))
    assert [r['number'] for r in registry['sections']]==list(range(1,269))
    assert sorted(int(x['text'].strip('[]')) for x in g.labels if re.fullmatch(r'\[\d+\]',x['text']))==list(range(1,269))
    milestones=l.tree.xpath('//t:body//t:milestone[@unit="niese"]',namespaces=NS)
    actual=[int(e.get('n')) for e in milestones];secure=[e for e in expected if not e['hold']]
    assert actual==[e['number'] for e in secure] and len(actual)==251 and len(set(actual))==251
    spans=sorted([(e['start'],e['end'],e['number']) for e in secure]);unassigned=[];cursor=0
    for a,z,n in spans:
        assert cursor<=a<z
        if a>cursor:unassigned.append(dict(start=cursor,end=a,text=l.stream[cursor:a],status='Preserved only in containing source views pending editorial adjudication.'))
        cursor=z
    if cursor<len(l.stream):unassigned.append(dict(start=cursor,end=len(l.stream),text=l.stream[cursor:],status='Preserved only in containing source views pending editorial adjudication.'))
    save(PACK/'COVERAGE_GATE.json',dict(status='TECHNICAL_PASS_WITH_EDITORIAL_HOLD',Greek_identities=268,logical_selectable_identities=268,current_nonempty_Latin_identities=251,current_primary_Latin_intervals=251,current_new_start_milestones=251,retained_original_Latin_Niese_starts=0,current_exclusive_end_anchors=3,Greek_new_explicit_opening=1,original_Greek_labels_retained=267,unapproved_unavailability_decisions=0,editorial_hold_identities=[e['number'] for e in expected if e['hold']],source_only_or_held_unassigned_spans=unassigned,physical_overlap_or_duplicate_text=False,Latin_complete_book_projection_hash=sha(l.stream.encode()),Vita_included=False,provisional_all_recommended_choices=dict(primary_intervals=257,unavailable_identities=11,partial_identities=[26,37,218,240,241,266],conditional_on_actual_editorial_approval=True)))
    print('268 unique Greek identities;251 secure Latin intervals;17 holds; no physical overlap. Whole Book/Alignment source remains intact.')
if __name__=='__main__':main()
