"""Count actual final XML starts and recover physical spans independently of totals."""
from prepare import *
from mixed_mapper import Book
from xml.parsers import expat

def projected_marker_offsets(model):
    points=[];parser=expat.ParserCreate()
    def start(name,attrs):
        tag=name.split(':')[-1]
        if (tag=='milestone' and attrs.get('unit')=='niese') or (tag=='anchor' and attrs.get('xml:id','').startswith('niese-')):
            byte=parser.CurrentByteIndex
            offset=sum(sum(p<byte for p in node['raw_positions']) for node in model.nodes)
            points.append(dict(tag=tag,attributes=attrs,raw_byte=byte,book_offset=offset))
    parser.StartElementHandler=start;parser.Parse(model.raw,True)
    return points

def main():
    l=Book(ROOT/'assets/xml/antiquities/Latin/book-20.xml');g=Book(ROOT/'assets/xml/antiquities/Greek/book-20.xml')
    old_l=Book(PACK/'frozen-inputs/Latin.xml');old_g=Book(PACK/'frozen-inputs/Greek.xml')
    registry=json.loads((ROOT/'assets/xml/antiquities/niese/book-20.json').read_text(encoding='utf-8'))
    expected=json.loads((PACK/'FINAL_EXPECTED_INTERVALS.json').read_text(encoding='utf-8'))
    assert [r['number'] for r in registry['sections']]==list(range(1,269))
    assert sorted(int(x['text'].strip('[]')) for x in g.labels if re.fullmatch(r'\[\d+\]',x['text']))==list(range(1,269))
    assert g.stream==old_g.stream and l.stream==old_l.stream
    points=projected_marker_offsets(l);starts=[p for p in points if p['tag']=='milestone'];anchors=[p for p in points if p['tag']=='anchor']
    old_starts=old_l.tree.xpath('//t:milestone[@unit="niese"]',namespaces=NS)
    old_anchors=old_l.tree.xpath('//t:anchor',namespaces=NS)
    available=[s for s in registry['sections'] if s['Latin']['available']];unavailable=[s['number'] for s in registry['sections'] if not s['Latin']['available']]
    actual_numbers=[int(p['attributes']['n']) for p in starts]
    assert actual_numbers==[s['number'] for s in available] and len(set(actual_numbers))==len(actual_numbers)
    assert unavailable==list(range(27,37))+[238]
    spans=[]
    for i,p in enumerate(starts):
        n=int(p['attributes']['n']);section=registry['sections'][n-1]
        a=p['book_offset'];end_id=section['Latin'].get('endTarget')
        z=next(q['book_offset'] for q in anchors if q['attributes']['xml:id']==end_id) if end_id else starts[i+1]['book_offset'] if i+1<len(starts) else len(l.stream)
        e=expected[n-1]
        assert (a,z)==(e['start'],e['end']) and l.stream[a:z]==e['Latin'] and a<z
        spans.append(dict(number=n,start=a,end=z,characters=z-a,text_sha256=sha(l.stream[a:z].encode()),start_raw_byte=p['raw_byte'],endTarget=end_id))
    gaps=[];cursor=0
    for span in spans:
        a,z=span['start'],span['end'];assert cursor<=a,'Overlapping physical Latin intervals'
        if a>cursor:gaps.append(dict(start=cursor,end=a,text=l.stream[cursor:a],status='SOURCE_ONLY_INHERITED_ANNOTATION',locator=old_l.locate(cursor)))
        cursor=z
    if cursor<len(l.stream):gaps.append(dict(start=cursor,end=len(l.stream),text=l.stream[cursor:]))
    assert len(gaps)==1 and gaps[0]['text']=='[Niese sections 26–37 largely missing; cf. Blatt, p. 68] '
    assert gaps[0]['locator']['stable_id']=='latin-book20-num34'
    assert sum(s['characters'] for s in spans)+sum(gap['end']-gap['start'] for gap in gaps)==len(l.stream)
    assert all(s['Latin']['correspondence']!='EDITORIAL_HOLD' for s in registry['sections'])
    chapters={lang:len(Book(ROOT/f'assets/xml/antiquities/{lang}/book-20.xml').tree.xpath('//t:milestone[@unit="chapter"]',namespaces=NS)) for lang in ['Greek','Latin','English']}
    assert chapters==dict(Greek=20,Latin=20,English=20)
    save(PACK/'COVERAGE_GATE.json',dict(status='PASS',count_method='Actual parsed XML and Expat marker byte positions, independently mapped to original mixed text; registry and reviewed intervals checked afterward.',Greek_identities=len(g.labels),logical_selectable_identities=len(registry['sections']),nonempty_Latin_identities=len(available),primary_Latin_intervals=len(spans),primary_Latin_fragments=len(spans),new_Latin_start_milestones=len(starts)-len(old_starts),retained_original_Latin_Niese_starts=len(old_starts),new_exclusive_end_anchors=len(anchors)-len(old_anchors),new_Greek_opening_labels=len(g.labels)-len(old_g.labels),retained_original_Greek_labels=len(old_g.labels),unavailable_identities=unavailable,partial_identities=[s['number'] for s in registry['sections'] if s['Latin']['correspondence']=='PARTIAL'],additional_qualified_identities=[59,239],old_legacy_chapter_milestones=chapters,source_only_unassigned_spans=gaps,physical_intervals=spans,physical_overlap_or_duplicate_text=False,Latin_complete_book_projection_hash=sha(l.stream.encode()),Latin_projection_characters=len(l.stream),assigned_Latin_characters=sum(s['characters'] for s in spans),source_only_characters=sum(gap['end']-gap['start'] for gap in gaps),Vita_included=False,editorial_holds=0))
    print('PASS actual counts:',len(g.labels),'Greek identities;',len(spans),'Latin fragments;',len(unavailable),'unavailable; source-only annotation fully accounted.')

if __name__=='__main__':main()
