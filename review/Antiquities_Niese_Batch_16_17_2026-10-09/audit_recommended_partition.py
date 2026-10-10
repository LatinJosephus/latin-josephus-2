"""Independently check the UNAPPROVED recommended physical partition.

This deliberation artifact does not add markers, activate identities, or grant
editor approval. It shows that the four recommended choices can preserve the
transcription's physical order without swallowing or duplicating narrative.
"""
from pathlib import Path
import sys,json,re
from collections import Counter
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,digest

def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')

def main():
    summary={}
    for b,roman in [(16,'XVI'),(17,'XVII')]:
        p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
        rows=read(p/'BOUNDARIES.json');l=Book(p/'frozen-inputs/Latin.xml')
        points=[dict(number=r['number'],locator=r['Latin_locator'],choice='ROUTINE_ADOPTED_NOT_APPLIED')
                for r in rows if r['Latin_review_status']=='INDIVIDUALLY_REVIEWED']
        def point(n,loc,decision):
            points.append(dict(number=n,locator=loc,choice='RECOMMENDED_B_PENDING_EDITOR',decision=decision))
        if b==16:
            f='DECISION_XVI_294_295.json';decision=read(p/f)
            recommended=next(x for x in decision['alternatives'] if x['id']=='B')
            for n,ranges in recommended['ranges'].items():
                for r in ranges:point(int(n),r['start'],f)
            f='DECISION_XVI_351_355_356.json';decision=read(p/f);loc=decision['locators']
            point(351,loc['earliest_surviving_351'],f)
            point(351,loc['displaced_351_prefix'],f)
            point(355,loc['start_355'],f)
        else:
            f='DECISION_XVII_024_025.json';d=read(p/f)
            point(25,next(x for x in d['alternatives'] if x['id']=='B')['locator'],f)
            f='DECISION_XVII_075_076.json';d=read(p/f)
            point(75,d['common_start_75'],f)
            point(76,next(x for x in d['alternatives'] if x['id']=='B')['start_76'],f)
        points.sort(key=lambda x:x['locator']['book_offset'])
        offsets=[x['locator']['book_offset'] for x in points]
        assert offsets[0]==0 and len(set(offsets))==len(points)
        actual_numbers=set(x['number'] for x in points)
        absent={r['number'] for r in rows if r['correspondence_status']=='ABSENT_IN_TRANSCRIPTION'}
        assert actual_numbers==set(range(1,len(rows)+1))-absent
        ranges=[];excluded=[]
        for i,x in enumerate(points):
            a=x['locator']['book_offset'];z=points[i+1]['locator']['book_offset'] if i+1<len(points) else len(l.stream)
            text=l.stream[a:z];start=z
            if '[...]' in text:
                # Only reviewed book-XVI omissions carry these literal editorial
                # placeholders. They remain untouched in the whole-book witness.
                assert b==16 and x['number'] in [188,394]
                start=a+text.index('[...]')
                assert l.stream[start:z].replace('[...]','').strip()==''
                excluded.append(dict(start=start,end=z,text=l.stream[start:z],
                    reason='LITERAL_EDITORIAL_OMISSION_PLACEHOLDERS_AND_ADJACENT_WHITESPACE; preserved in source/whole-book view; no fabricated Latin counterpart'))
                z=start
            assert a<z
            ranges.append(dict(number=x['number'],start=a,end=z,text=l.stream[a:z],
                start_locator=x['locator'],choice=x['choice'],source_sha256=digest(l.raw)))
        coverage=[0]*len(l.stream)
        for r in ranges:
            for i in range(r['start'],r['end']):coverage[i]+=1
        exclusions=[False]*len(l.stream)
        for r in excluded:
            for i in range(r['start'],r['end']):
                assert not exclusions[i];exclusions[i]=True
        assert all(c==0 if exclusions[i] else c==1 for i,c in enumerate(coverage))
        by_number={}
        for r in ranges:by_number.setdefault(str(r['number']),[]).append(r)
        assert all(all(a['end']<=z['start'] for a,z in zip(v,v[1:])) for v in by_number.values())
        counts=Counter(r['number'] for r in ranges)
        if b==16:
            assert {n:c for n,c in counts.items() if c>1}=={294:2,295:2,351:2}
            assert by_number['355'][0]['end']==by_number['351'][1]['start']
            assert by_number['351'][1]['end']==by_number['356'][0]['start']
        data=dict(status='PASS_PHYSICAL_COVERAGE_OF_RECOMMENDED_MODEL_ONLY_PENDING_EDITOR_ADJUDICATION',
            book=b,Latin_sha256=digest(l.raw),logical_present_identities=len(by_number),
            physical_fragments=len(ranges),unavailable_identities=sorted(absent),
            fragments=by_number,excluded_literal_placeholders=excluded,
            narrative_characters_checked=sum(not x for x in exclusions),
            explicit_non_narrative_characters_excluded=sum(exclusions),
            every_included_physical_character_covered_exactly_once=True,
            each_identity_fragments_in_witness_order=True,
            text_moved=False,source_edits=False,editor_approval=False,
            reader_test=False,source_byte_recovery_after_edit=False,book_certified=False)
        save(p/'RECOMMENDED_PHYSICAL_PARTITION_PENDING_EDITOR.json',data)
        summary[str(b)]={k:data[k] for k in ['status','logical_present_identities','physical_fragments',
            'unavailable_identities','narrative_characters_checked','explicit_non_narrative_characters_excluded',
            'every_included_physical_character_covered_exactly_once','book_certified']}
        print(roman,'recommended model only:',len(by_number),'logical Latin identities,',len(ranges),
            'physical fragments; every narrative character exactly once; pending editor, not implemented')
    save(BATCH/'INDEPENDENT_RECOMMENDED_PARTITION_CHECK.json',dict(status='DELIBERATION_MODEL_ONLY_NOT_CERTIFICATION',books=summary))

if __name__=='__main__':main()
