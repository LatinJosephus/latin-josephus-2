"""Apply approved raw-byte segmentation additions and registry spans; no serializer."""
from pathlib import Path
import sys,json,re
from collections import Counter
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,digest,NS,XMLID
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
NOTES={
 (16,294):'Latin correspondence is displayed in two fragments in manuscript order. The first ends within a relative construction, and the witness repeats Obadas\'s death. Material corresponding to 295 occurs between the fragments. The cause of the arrangement is undetermined.',
 (16,295):'Latin correspondence is displayed in two fragments in manuscript order. Syllaeus\'s bid precedes the account of Aretas\'s accession corresponding to 294; Caesar\'s displeasure follows it. The cause of the arrangement is undetermined.',
 (16,351):'Two surviving Latin fragments are displayed in manuscript order: the earlier material beginning perissent, then the displaced opening clause hac oratione ... quanti arabum, transmitted after the correspondence of 355. No text is reordered; the cause of the displacement is undetermined.',
 (16,355):'The displaced opening clause corresponding to 351 follows this interval in the witness and is displayed under 351. The following 356 begins at the preserved manuscript and traditional chapter boundary.',
 (17,24):'The complete grant clause is retained here, including cui balatha nomen erat ... caedere compromisit. Its place-name corresponds to the opening of Greek 25 and already survives in this Latin interval.',
 (17,25):'Partial Latin correspondence: the place-name corresponding to the opening of Greek 25 already survives in the preceding Latin 24 grant clause. This interval begins with the summoning, Euocabat ergo eum; the name is not missing.',
 (17,75):'The complete shared command to burn the poison and Antipater\'s letter is retained here, including epistolamque antipatri and its governing conbure. The letter instruction corresponds to the opening of Greek 76 and already survives in this Latin interval.',
 (17,76):'Partial Latin correspondence: the letter instruction corresponding to the opening of Greek 76 already survives in the shared command in Latin 75. This interval begins Ego autem plurimum, reporting burning and retention. Transmitted punctuation and attribution are preserved.',
}
def note(b,r):
    if (b,r['number']) in NOTES:return NOTES[(b,r['number'])]
    if r['correspondence_status']=='ABSENT_IN_TRANSCRIPTION':
        return 'No independently surviving Latin counterpart is present in this transcription after complete-book review. The cause is undetermined.'
    if r.get('correspondence_qualifications'):
        value=r.get('correspondence_note',r['review_reason'])
        value=re.sub(r'(?:Whole|Entire|Complete|Full)[^.]*?(?:reviewed|read)\.?','',value)
        return value.strip()
    return None
def apply(raw,operations):
    result=raw
    for x in sorted(operations,key=lambda x:x['offset'],reverse=True):
        a=x['offset'];old=x['old'].encode();assert result[a:a+len(old)]==old
        result=result[:a]+x['new'].encode()+result[a+len(old):]
    return result
def main():
    approvals=read(BATCH/'EDITOR_ADJUDICATION_ALL_B.json')
    assert approvals['status']=='ALL_FOUR_EDITORIAL_DECISIONS_CLOSED_APPROVED_B'
    totals={}
    for b,roman in [(16,'XVI'),(17,'XVII')]:
        p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
        rows=read(p/'BOUNDARIES.json');base=read(p/'BASELINE.json')
        model=read(p/'RECOMMENDED_PHYSICAL_PARTITION_PENDING_EDITOR.json')
        l,g=Book(p/'frozen-inputs/Latin.xml'),Book(p/'frozen-inputs/Greek.xml')
        latin=ROOT/base['inputs']['Latin']['relative'];greek=ROOT/base['inputs']['Greek']['relative']
        assert latin.read_bytes()==l.raw and greek.read_bytes()==g.raw,'Only apply once to immutable inputs.'
        physical=sorted([x for spans in model['fragments'].values() for x in spans],key=lambda x:x['start'])
        operations=[];locations={};counts=Counter()
        reused={}
        if b==16:
            reused={rows[355]['Latin_locator']['book_offset']:'trad-latin-LOEB-16-Chapter-11-0',
                    rows[367]['Latin_locator']['book_offset']:'b78-latin-B78-table1-row151'}
        for span in physical:
            a=span['start'];n=span['number'];counts[n]+=1
            if a in reused:
                ident=reused[a];kind='REUSED_SOURCE_ANCHOR'
                assert len(l.tree.xpath('//*[@xml:id=$id]',id=ident))==1
            else:
                ordinal=counts[n];unit='niese' if ordinal==1 else 'niese-fragment'
                ident=f'niese-latin-book{b}-{n}'+(f'-fragment{ordinal}' if ordinal>1 else '')
                marker=f'<milestone unit="{unit}" n="{n}" xml:id="{ident}"/>'
                operations.append(dict(offset=l.locate(a)['raw_byte'],old='',new=marker,identity=n,
                    book_offset=a,kind='START_MILESTONE' if ordinal==1 else 'EXTRA_FRAGMENT_ANCHOR'))
                kind=unit
            locations[a]=dict(available='true',kind='anchor',target=ident,paragraph=span['start_locator']['stable_id'])
        for omission in model['excluded_literal_placeholders']:
            a=omission['start'];owner=next(x['number'] for x in physical if x['end']==a)
            ident=f'niese-latin-book{b}-end{owner}'
            marker=f'<milestone unit="niese-range-end" n="{owner}" xml:id="{ident}"/>'
            operations.append(dict(offset=l.locate(a)['raw_byte'],old='',new=marker,identity=owner,
                book_offset=a,kind='EXPLICIT_RANGE_END_ANCHOR'))
            locations[a]=dict(available='true',kind='anchor',target=ident,paragraph=l.locate(a)['stable_id'])
        registry=dict(schema=1,structuralMilestoneUnits=['chapter',None],book=b,range=[1,len(rows)],
            suppressedLatinLabels=[],sections=[],
            provenance=dict(authority='Niese IV (1890) printed images; complete individual Latin review',
                base_commit=base['base_commit'],primary_PDF_sha256=read(BATCH/'PRINTED_SOURCES.json')['Niese']['sha256'],
                editor_approval_sha256=approvals['approval_sha256'],physical_order='PRESERVED',causes='UNDETERMINED'))
        for r in rows:
            n=r['number'];available=str(n) in model['fragments'];spans=model['fragments'].get(str(n),[])
            config=dict(available=available,correspondence=r['correspondence_status'],note=note(b,r))
            if available:
                config['spans']=[dict(start=locations[x['start']],
                    end=locations[x['end']] if x['end']<len(l.stream) else dict(kind='book-end'),
                    label=f'Physical witness fragment {i+1} of {len(spans)}') for i,x in enumerate(spans)]
                first=spans[0]['start_locator'];r['Latin_locator']=first
                r['Latin_approved_spans']=[dict(start=x['start'],end=x['end'],text=x['text']) for x in spans]
                if r['editorial_status']=='PENDING_EDITOR_ADJUDICATION':
                    r.update(Latin_review_status='INDIVIDUALLY_REVIEWED_EDITOR_APPROVED',
                        editorial_status='EDITOR_APPROVED_B',implementation_approved=True,
                        correspondence_status='PRESENT_WITH_EDITOR_APPROVED_DISPLACED_OR_REJOINED_CORRESPONDENCE')
                    config['correspondence']=r['correspondence_status']
                context=first['stable_id']
            else:
                unit=next(x for x in g.units if x['id']==r['Greek_reviewed_locator']['stable_id'])
                context=unit['element'].get('sameAs','').lstrip('#')
                assert context and any(x['id']==context for x in l.units)
            registry['sections'].append(dict(number=n,Latin=config,contextTarget=context))
            r.update(applied=True,implementation_state='APPLIED_NOT_YET_READER_CERTIFIED',reader_certified=False)
            r['registry_Latin']=config
        latin_after=apply(l.raw,operations);latin.write_bytes(latin_after)
        greek_ops=[dict(offset=rows[0]['Greek_reviewed_locator']['raw_byte'],old='',new='<num>[1]</num>',kind='EXPLICIT_OPENING_CITATION')]
        if b==17:
            decision=read(p/'DECISION_XVII_030_031.json')
            label=next(x for x in g.labels if x['text']=='[31]')
            a=label['raw_start'];z=g.raw.index(b'</num>',a)+6
            token=g.raw[a:z].decode();assert token=='<num>[31]</num>'
            greek_ops.extend([dict(offset=a,old=token,new='',kind='REMOVE_DISPLACED_31_CITATION'),
                dict(offset=decision['approved_locator']['raw_byte'],old='',new=token,kind='INSERT_PRINT_SUPPORTED_31_CITATION')])
        greek_after=apply(g.raw,greek_ops);greek.write_bytes(greek_after)
        assert Book(raw=latin_after).stream==l.stream and Book(raw=greek_after).stream==g.stream
        registry_path=ROOT/f'assets/xml/antiquities/niese/book-{b:02}.json'
        assert not registry_path.exists();save(registry_path,registry)
        save(p/'BOUNDARIES.json',rows)
        counts_actual=Counter(x['kind'] for x in operations)
        ledger=dict(book=b,status='APPLIED_AWAITING_INDEPENDENT_SOURCE_AND_READER_QA',
            Latin=dict(relative=base['inputs']['Latin']['relative'],before_sha256=digest(l.raw),after_sha256=digest(latin_after),operations=operations),
            Greek=dict(relative=base['inputs']['Greek']['relative'],before_sha256=digest(g.raw),after_sha256=digest(greek_after),operations=greek_ops),
            registry=dict(relative=registry_path.relative_to(ROOT).as_posix(),sha256=digest(registry_path.read_bytes())),
            logical_identities=len(rows),present_Latin_identities=len(model['fragments']),physical_Latin_fragments=len(physical),
            unavailable_Latin_identities=model['unavailable_identities'],reused_source_anchors=reused,
            added_marker_counts=dict(counts_actual),qualified_runtime_notices=sum(bool(x['Latin']['note']) and x['Latin']['available'] for x in registry['sections']),
            reader_certified=False)
        save(p/'APPLIED_RAW_BYTE_PATCH.json',ledger)
        history=read(p/'DECISION_HISTORY.json');history.append(dict(kind='APPROVED_SEGMENTATION_APPLIED',
            approval_record='../Antiquities_Niese_Batch_16_17_2026-10-09/EDITOR_ADJUDICATION_ALL_B.json',
            identities=len(rows),present=len(model['fragments']),unavailable=len(model['unavailable_identities']),
            physical_fragments=len(physical),added_marker_counts=dict(counts_actual),reader_certified=False))
        save(p/'DECISION_HISTORY.json',history)
        totals[str(b)]={k:ledger[k] for k in ['logical_identities','present_Latin_identities','physical_Latin_fragments','added_marker_counts','qualified_runtime_notices']}
        print(roman,'applied',len(rows),'identities;',len(physical),'physical Latin fragments;',dict(counts_actual),'reused',len(reused))
    save(BATCH/'APPLIED_BATCH_COUNTS.json',dict(status='APPLIED_NOT_YET_CERTIFIED',books=totals,prior_count=5231,added=759,total=5990))
if __name__=='__main__':main()
