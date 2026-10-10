"""Compile individually approved Latin cuts; pending choices never become edits.

Existing numbered or source-qualified physical points are reused. Plans are
review artifacts, not full-book availability or certificates.
"""
from reconnaissance import *
from mixed_mapper import Book

def validate(model, loc):
    assert model.locate(loc['book_offset']) == loc

def physical_points(model, records, language):
    points = []
    for row in records:
        p = row['fields'][language]
        unit = next(u for u in model.units if u['id'] == p['paragraph'])
        points.append(dict(coordinate=unit['book_start'] + int(p['offset']),
                           identity=row['id'], locator={k:v for k,v in p.items()
                           if k in ['kind','target','edge','available']}, source=p))
    return points

def main():
    for b in [18,19]:
        d=packet(b); rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'))
        model=Book(raw=(d/'frozen-inputs/Latin.xml').read_bytes())
        structural=json.loads((d/'STRUCTURAL_RECORDS.json').read_text(encoding='utf8'))
        points=physical_points(model,structural,'Latin')
        retained=[]; reused=[]; markers=[]; pending=[]; unrepresented=[]
        for row in rows:
            c=row['candidate'];n=row['number']
            if not c.get('approved'):
                pending.append(n);continue
            loc=c.get('locator')
            if not loc:
                unrepresented.append(n);continue
            validate(model,loc)
            # A matching inherited suffix at another physical point is not reuse.
            label=next((x for x in model.labels if x['book_offset']==loc['book_offset']
                        and int(re.findall(r'\d+',x['text'])[-1])==n),None)
            if label:
                retained.append(dict(number=n,locator=loc,label=label));continue
            matches=[x for x in points if x['coordinate']==loc['book_offset']]
            if matches:
                reused.append(dict(number=n,locator=loc,physical_identity=matches[0]['identity'],
                                   physical_locator=matches[0]['locator'],all_coincident_identities=matches));continue
            markers.append(dict(number=n,at=loc['raw_byte'],marker=f'<milestone unit="niese" n="{n}"/>',
                                locator=loc,approval='Governing section 5: individually reviewed secure routine cut',
                                print_evidence=row['print_evidence'],correspondence=c['correspondence']))
        assert len({x['at'] for x in markers})==len(markers)
        assert len(retained)+len(reused)+len(markers)+len(pending)+len(unrepresented)==len(rows)
        save(d/'APPROVED_SECURE_MARKER_PLAN.json',dict(book=b,baseline=BASE,
            status='APPROVED_ROUTINE_STARTS_ONLY_FULL_BOOK_GATES_PENDING',
            source_sha256=sha(model.raw),policy='Governing section 5 secure routine cuts; no pending choice applied',
            retained_starts=retained,reused_physical_starts=reused,markers=markers,
            pending_sections=pending,approved_unavailable_sections=unrepresented,
            reader_availability_changed=False,full_book_certified=False))
        print(b,'retained',len(retained),'physical reuse',len(reused),'new',len(markers),'pending',pending)
        for n in [1,257,292,263,299]:
            if n>len(rows):continue
            r=rows[n-1];print(n,r['candidate']['locator'], 'retained',next((x for x in retained if x['number']==n),None),
                            'reuse',next((x for x in reused if x['number']==n),None))
if __name__=='__main__':main()
