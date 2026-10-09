"""IX-only byte edits, independently reversible against the pinned checkout snapshots.
--language Greek or Latin scopes an application; pending decisions are never applied.
"""
from pathlib import Path
import json,sys,re,subprocess
from mixed_mapper import Book,digest,fixtures
P=Path(__file__).resolve().parent;W=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def patch(raw,ops):
    out=raw
    for o in sorted(ops,key=lambda x:(x['at'],x['delete']),reverse=True):
        old=bytes.fromhex(o['before_hex']);new=bytes.fromhex(o['after_hex']);at=o['at'];assert out[at:at+len(old)]==old
        out=out[:at]+new+out[at+len(old):]
    return out
assert subprocess.check_output(['git','branch','--show-current'],cwd=W).decode().strip()=='antiquities-niese-09'
base=read(P/'BASELINE.json');rows=read(P/'BOUNDARIES.json');plan=read(P/'GREEK_MARKER_PLAN.json');ids=read(P/'EXECUTABLE_IDENTITIES.json')
languages=[sys.argv[sys.argv.index('--language')+1]] if '--language' in sys.argv else ['Greek','Latin']
results=read(P/'IMPLEMENTATION_PRESERVATION.json') if (P/'IMPLEMENTATION_PRESERVATION.json').exists() else {'book':9,'sources':{}}
for lang in languages:
    assert lang in ['Greek','Latin'];rel=f'assets/xml/antiquities/{lang}/book-09.xml';target=W/rel
    raw=Path(base['inputs'][rel]['snapshot']).read_bytes();assert digest(raw)==base['inputs'][rel]['worktree_sha256'];book=Book(raw=raw);ops=[]
    if lang=='Latin':
        for r in rows:
            if r['Latin_locator'] and not r['inherited_start_retained'] and r['implementation_approved']:
                loc=book.locate(r['Latin_locator']['book_offset']);assert all(loc[k]==r['Latin_locator'][k] for k in loc);tag=f'<milestone unit="niese" n="{r["niese"]}"/>'.encode()
                ops.append({'niese':r['niese'],'kind':'INSERT_LATIN_MILESTONE','at':loc['raw_byte'],'delete':0,'before_hex':'','after_hex':tag.hex(),'target_locator':loc})
    else:
        loc=plan['opening_addition']['locator'];tag=b'<num>[1]</num>';ops.append({'niese':1,'kind':'ADD_IMPLICIT_OPENING_IDENTITY','at':loc['raw_byte'],'delete':0,'before_hex':'','after_hex':tag.hex(),'target_locator':loc})
        for r in plan['relocations']:
            n=r['niese'];assert rows[n-1]['implementation_approved'];tag=f'<num>[{n}]</num>'.encode();at=r['original_label']['raw_start'];end=raw.index(b'</num>',at)+6;assert raw[at:end]==tag
            ops.extend([{'niese':n,'kind':'REMOVE_OLD_GREEK_NUM_ONLY','at':at,'delete':end-at,'before_hex':tag.hex(),'after_hex':''},{'niese':n,'kind':'INSERT_VERIFIED_GREEK_NUM','at':r['chosen_locator']['raw_byte'],'delete':0,'before_hex':'','after_hex':tag.hex(),'target_locator':r['chosen_locator']}])
    output=patch(raw,ops)
    # Resume only the original or the prior output from this same recorded assignment.
    allowed=[raw,output]
    if lang in results['sources']:allowed.append(patch(raw,results['sources'][lang]['authorized_operations']))
    assert target.read_bytes() in allowed,'Unexpected target bytes; refuse overwrite'
    after=Book(raw=output);assert after.stream==book.stream
    shift=0;inverse=[]
    for o in sorted(ops,key=lambda x:(x['at'],x['delete'])):
        old=bytes.fromhex(o['before_hex']);new=bytes.fromhex(o['after_hex']);inverse.append({'at':o['at']+shift,'delete':len(new),'before_hex':new.hex(),'after_hex':old.hex()});shift+=len(new)-len(old)
    assert patch(output,inverse)==raw
    for attr in ['//@xml:id','//@sameAs']:
        assert after.tree.xpath(attr,namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})==book.tree.xpath(attr,namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})
    def structural(b):return [(e.tag,e.get('n'),e.get('type'),e.get('{http://www.w3.org/XML/1998/namespace}id')) for e in b.tree.iter() if e.tag.rsplit('}',1)[-1] in ['div1','div2','p']]
    assert structural(after)==structural(book)
    target.write_bytes(output)
    results['sources'][lang]={'absolute_path':str(target),'before_sha256':digest(raw),'after_sha256':digest(output),'authorized_operations':ops,'inverse_operations':inverse,'reversed_sha256':digest(patch(output,inverse)),'exact_source_recovery':True,'narrative_unchanged':True,'IDs_sameAs_paragraphs_divisions_unchanged':True,'UTF8':True,'BOM':output.startswith(b'\xef\xbb\xbf'),'LF':output.count(b'\n'),'CRLF':output.count(b'\r\n')}
results.update({'status':'PROVISIONAL' if ids['pending'] else 'ALL_DECISIONS_CLOSED','expected_sections':291,'represented_Latin_candidates':232,'unavailable_sections':ids['unavailable_sections'],'retained_Latin_starts':46,'implemented_Latin_milestones':len(results['sources'].get('Latin',{}).get('authorized_operations',[])),'Greek_opening_additions':1,'Greek_marker_moves':len(plan['relocations']),'pending_editorial_decisions':ids['pending'],'mixed_content_fixtures':fixtures()})
write(P/'IMPLEMENTATION_PRESERVATION.json',results)
if 'Latin' in languages:
    sections=[]
    for r in rows:
        n=r['niese'];available=r['Latin_locator'] is not None and r['implementation_approved'];note=None
        if n in [239,240] and ids['pending']:
            available=False;note='The exact boundary between IX.239 and IX.240 awaits editorial adjudication. This local implementation is provisional.'
        elif not available:note='Text corresponding to this section is unavailable in this transcription, which preserves an editorial omission placeholder for IX.51–109. The cause is not established here.'
        elif n==110:note='Only Jehu’s concluding reply survives for IX.110 in this Latin transcription. The opening account of his departure and the captains’ question has no identifiable counterpart here. The inherited ellipsis is preserved; the cause is unknown.'
        section={'number':n,'Latin':{'available':available,'correspondence':'PARTIAL' if n==110 else ('REPRESENTED' if available else 'UNAVAILABLE'),'note':note},'contextTarget':r['Latin_paragraph_id']}
        if 51<=n<=109:
            for lang in ['Greek','English']:section[lang]={'available':False,'note':f'Text corresponding to this section is unavailable in this {lang} transcription, which preserves an editorial omission placeholder for IX.51–109.'}
        sections.append(section)
    registry={'schema':1,'book':9,'range':[1,291],'status':'PROVISIONAL_PENDING_240' if ids['pending'] else 'EDITORIALLY_APPROVED_LOCAL_IMPLEMENTATION','excludedNarrativeParagraphs':{lang:[f'{lang.lower()}-book09-num51'] for lang in ['Latin','Greek','English']},'suppressedLatinLabels':ids['suppressedLatinLabels'],'sections':sections}
    write(W/'assets/xml/antiquities/niese/book-09.json',registry)
print(json.dumps({k:results[k] for k in ['status','implemented_Latin_milestones','Greek_marker_moves','pending_editorial_decisions']},indent=2))
