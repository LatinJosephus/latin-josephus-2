"""Implement only closed routine cuts. Open cases receive a hold, never an absence decision."""
from prepare import *
from mixed_mapper import Book
rows=json.loads((PACK/'IDENTITIES.json').read_text(encoding='utf-8'))
models={l:Book(PACK/'frozen-inputs'/f'{l}.xml') for l in ['Latin','Greek','English']};l=models['Latin'];g=models['Greek']
secure={r['number']:r['candidate']['Latin_start'] for r in rows if r['Latin_review_status']=='INDIVIDUALLY_REVIEWED'}
assert len(secure)==251
all_candidate_starts={r['number']:r['candidate']['Latin_start'] for r in rows if r['candidate']['Latin_start'] is not None}
edits={lang:[] for lang in ['Latin','Greek']};registry=dict(schema=1,structuralMilestoneUnits=['chapter'],book=20,range=[1,268],suppressedLatinLabels=[],sections=[],reviewStatus='EDITORIAL_HOLD; NOT LOCALLY CERTIFIED')
expected=[]
for r in rows:
    n=r['number'];closed=n in secure;a=secure.get(n);loc=l.locate(a) if closed else None
    note=None
    if not closed:note=f'Editorial decision pending for Latin correspondence at XX.{n}. No accepted individual interval is displayed; the unchanged source remains available in containing views.'
    elif n==218:note='Partial Latin correspondence: only the concluding judgment survives; the opening hymn instruction has no identified independent counterpart.'
    elif n==266:note='Partial Latin correspondence: the autobiographical intention survives; the living-witness clause has no independently identified counterpart. No Vita text is supplied.'
    elif n==239:note='The surviving Latin opens with a relative clause whose antecedent is unresolved in the adjacent238 case.'
    section=dict(number=n,Latin=dict(available=closed,correspondence='EDITORIAL_HOLD' if not closed else 'PARTIAL' if n in [218,266] else 'PRESENT',note=note),contextTarget=loc['stable_id'] if closed else r['Latin_alignment_paragraph'])
    z=min((v for v in all_candidate_starts.values() if closed and v>a),default=len(l.stream))
    if closed:
        edits['Latin'].append(dict(number=n,original_byte=loc['raw_byte'],addition=f'<milestone unit="niese" n="{n}"/>',locator=loc,kind='routine-new-start'))
        next_secure=min((v for v in secure.values() if v>a),default=len(l.stream))
        if z!=next_secure:
            endloc=l.locate(z);target=f'niese-latin-book20-secure-end{n}';section['Latin']['endTarget']=target
            edits['Latin'].append(dict(number=n,original_byte=endloc['raw_byte'],addition=f'<anchor xml:id="{target}"/>',locator=endloc,kind='routine-exclusive-end-before-unresolved-adjacent-material'))
    registry['sections'].append(section)
    context=section['contextTarget'];english=''.join(u['text'] for u in models['English'].units if u['id']==context.replace('latin-','english-',1) or context==u['element'].get('sameAs','').lstrip('#')) if context else ''
    expected.append(dict(number=n,Greek=r['Greek_text'],Latin=l.stream[a:z] if closed else '',English=english,hold=not closed,qualification=note,start=a,end=z if closed else None))
opening=g.locate(rows[0]['Greek_start']);edits['Greek'].append(dict(number=1,original_byte=opening['raw_byte'],addition='<num>[1]</num>',locator=opening,kind='routine-implicit-opening-after-duration-notice'))
for lang,items in edits.items():
    raw=models[lang].raw;target=ROOT/f'assets/xml/antiquities/{lang}/book-20.xml';assert target.read_bytes()==raw
    out=raw
    for e in sorted(items,key=lambda e:e['original_byte'],reverse=True):k=e['original_byte'];out=out[:k]+e['addition'].encode()+out[k:]
    etree.fromstring(out);target.write_bytes(out);delta=0
    for e in sorted(items,key=lambda e:e['original_byte']):e['final_byte']=e['original_byte']+delta;delta+=len(e['addition'].encode())
save(ROOT/'assets/xml/antiquities/niese/book-20.json',registry)
save(PACK/'SECURE_INSERTIONS.json',dict(baseline=BASE,scope='Only routine accepted starts and ends; no disputed start or absence adjudicated.',original_hashes={lang:sha(m.raw) for lang,m in models.items()},edits=edits))
save(PACK/'SECURE_EXPECTED_INTERVALS.json',expected)
print('251 routine Latin starts;17 explicit editorial holds;3 ends protect unresolved adjacent material. No disputed cut applied.')
