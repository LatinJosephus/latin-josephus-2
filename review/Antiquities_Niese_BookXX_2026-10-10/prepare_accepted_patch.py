"""Byte insertions are gated on actual recorded editorial decisions; no default approval."""
from prepare import *
from mixed_mapper import Book
def accepted():
    history=json.loads((PACK/'ADJUDICATION_HISTORY.json').read_text(encoding='utf-8'))
    assert len(history)==4 and all(h['status']=='APPROVED' and h.get('user_response') for h in history),'Editorial holds remain open'
    return {h['case']:h['choice'] for h in history}
def make():
    decisions=accepted()
    rows=json.loads((PACK/'IDENTITIES.json').read_text(encoding='utf-8'))
    models={l:Book(PACK/'frozen-inputs'/f'{l}.xml') for l in ['Latin','Greek','English']}
    l=models['Latin'];g=models['Greek'];edits={lang:[] for lang in ['Latin','Greek']};registry=dict(schema=1,structuralMilestoneUnits=['chapter'],book=20,range=[1,268],suppressedLatinLabels=[],sections=[])
    assert decisions['026_037']=='A' and decisions['238']=='A','Unresolved representation cannot be certified'
    starts={r['number']:r['candidate']['Latin_start'] for r in rows if r['candidate']['Latin_start'] is not None}
    starts[59]=l.stream.index('habe inquit fiducia' if decisions['059']=='A' else 'inquit fiducia')
    starts[241]=l.stream.index('Is namque primus' if decisions['241']=='A' else 'cum et pontificatum tenuisset et regnum')
    annotation=l.stream.index('[Niese sections 26')
    notes={26:'Partial Latin correspondence: only the residence clause survives independently; the following inherited annotation remains in containing views.',37:'Partial Latin correspondence: only the final Artabanus destination clause survives independently.',59:'The Latin reassurance is kept together here; habe corresponds to the closing imperative of Greek58.' if decisions['059']=='A' else 'The Latin reassurance is divided at the reporting verb, following the Greek58/59 interruption.',218:'Partial Latin correspondence: only the concluding judgment survives; the opening hymn instruction has no identified independent counterpart.',239:'The surviving Latin opens with a relative clause whose Jonathan antecedent has no independent interval in238.',240:'The Latin compresses and attaches kingship wording to this sentence; the adjacent241 correspondence is reordered.' if decisions['241']=='A' else 'The Latin construction is divided before the kingship clause to follow the Greek240/241 correspondence.',241:'The Latin diadem and Alexander succession statements are compressed and reordered relative to Greek241.',266:'Partial Latin correspondence: the autobiographical intention survives; the living-witness clause has no independently identified counterpart. No Vita text is supplied.'}
    for r in rows:
        n=r['number'];unavailable=n not in starts
        note=('No independent Latin interval has been identified for this Niese section after whole-witness review; the current source preserves only partial26 and37 around this passage.' if 27<=n<=36 else 'No independent Latin interval has been identified for Jonathan’s appointment in this Niese section; the neighboring vacancy and Tryphon/Simon wording remains in237 and239.') if unavailable else notes.get(n)
        loc=l.locate(starts[n]) if not unavailable else None
        section=dict(number=n,Latin=dict(available=not unavailable,correspondence='UNAVAILABLE' if unavailable else 'PARTIAL' if n in [26,37,218,240,241,266] else 'PRESENT',note=note),contextTarget=loc['stable_id'] if loc else r['Latin_alignment_paragraph'])
        if n==26:section['Latin']['endTarget']='niese-latin-book20-end26'
        registry['sections'].append(section)
        r['accepted_Latin']=dict(start=starts.get(n),locator=loc,unavailable=unavailable,note=note,assessment='NO_INDEPENDENT_LATIN_INTERVAL' if unavailable else 'PARTIAL_CORRESPONDENCE' if n in [26,37,218,240,241,266] else r['candidate']['assessment'])
        r['Latin_review_status']='CLOSED_INDIVIDUAL_REVIEW'
        if loc:edits['Latin'].append(dict(number=n,original_byte=loc['raw_byte'],addition=f'<milestone unit="niese" n="{n}"/>',locator=loc,kind='new-start'))
    edits['Latin'].append(dict(number=26,original_byte=l.locate(annotation)['raw_byte'],addition='<anchor xml:id="niese-latin-book20-end26"/>',locator=l.locate(annotation),kind='exclusive-end-before-source-only-annotation'))
    opening=g.locate(rows[0]['Greek_start']);edits['Greek'].append(dict(number=1,original_byte=opening['raw_byte'],addition='<num>[1]</num>',locator=opening,kind='implicit-opening-after-duration-notice'))
    for lang,items in edits.items():
        raw=models[lang].raw;target=ROOT/f'assets/xml/antiquities/{lang}/book-20.xml'
        current=target.read_bytes()
        if current!=raw:
            prior=json.loads((PACK/'SECURE_INSERTIONS.json').read_text(encoding='utf-8'))['edits'][lang]
            for e in sorted(prior,key=lambda e:e['final_byte'],reverse=True):
                k=e['final_byte'];add=e['addition'].encode();assert current[k:k+len(add)]==add
                current=current[:k]+current[k+len(add):]
        assert current==raw,'Do not overwrite changes outside the certified insertion manifest'
        out=raw
        for e in sorted(items,key=lambda e:e['original_byte'],reverse=True):k=e['original_byte'];out=out[:k]+e['addition'].encode()+out[k:]
        etree.fromstring(out);target.write_bytes(out)
        delta=0
        for e in sorted(items,key=lambda e:e['original_byte']):e['final_byte']=e['original_byte']+delta;delta+=len(e['addition'].encode())
    save(ROOT/'assets/xml/antiquities/niese/book-20.json',registry)
    save(PACK/'APPROVED_INSERTIONS.json',dict(baseline=BASE,editorial_history='ADJUDICATION_HISTORY.json',original_hashes={lang:sha(m.raw) for lang,m in models.items()},edits=edits))
    save(PACK/'IDENTITIES.json',rows)
    expected=[];physical=[]
    for r in rows:
        n=r['number'];a=starts.get(n);z=annotation if n==26 else min((v for v in starts.values() if a is not None and v>a),default=len(l.stream))
        context=registry['sections'][n-1]['contextTarget'];english=''.join(u['text'] for u in models['English'].units if u['id']==context.replace('latin-','english-',1) or context in (u['element'].get('sameAs','').lstrip('#'),))
        expected.append(dict(number=n,Greek=r['Greek_text'],Latin=l.stream[a:z] if a is not None else '',English=english,unavailable=a is None,qualification=registry['sections'][n-1]['Latin']['note'],start=a,end=z if a is not None else None))
        if a is not None:physical.append(dict(number=n,start=a,end=z,start_locator=l.locate(a),end_locator=l.locate(z) if z<len(l.stream) else 'BOOK_END',text=l.stream[a:z]))
    save(PACK/'FINAL_EXPECTED_INTERVALS.json',expected);save(PACK/'LATIN_PHYSICAL_ORDER.json',physical)
    print('Inserted',len(starts),'Latin starts, one independent end anchor, one Greek implicit opening; all editorial decisions closed.')
if __name__=='__main__':make()
