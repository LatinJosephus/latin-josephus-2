"""Independent byte reversal, XML preservation and actual registry coverage proof."""
from pathlib import Path
import sys,json,re,hashlib
from collections import Counter
from lxml import etree
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,NS,XMLID,digest
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def reverse(raw,ops):
    shift=0;undo=[]
    for op in sorted(ops,key=lambda x:x['offset']):
        old,new=op['old'].encode(),op['new'].encode()
        undo.append((op['offset']+shift,new,old));shift+=len(new)-len(old)
    for offset,new,old in sorted(undo,reverse=True):
        assert raw[offset:offset+len(new)]==new
        raw=raw[:offset]+old+raw[offset+len(new):]
    return raw
def independent_stream_and_points(tree):
    text=[];points={};length=0
    def append(value):
        nonlocal length
        if value:text.append(value);length+=len(value)
    def walk(el):
        ident=el.get(XMLID)
        if ident:points[ident]=length
        if etree.QName(el).localname not in ['num','note','app','rdg']:
            append(el.text)
            for child in el:
                if isinstance(child.tag,str):walk(child)
                append(child.tail)
    for p in tree.xpath('//t:body//t:div2[not(@n="0")]/t:p',namespaces=NS):walk(p)
    return ''.join(text),points
def main():
    book_results={};changed_allowed={'assets/js/renderTei.js'}
    for b,roman,expected in [(16,'XVI',404),(17,'XVII',355)]:
        p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
        ledger=read(p/'APPLIED_RAW_BYTE_PATCH.json');base=read(p/'BASELINE.json')
        registry_path=ROOT/ledger['registry']['relative']
        assert digest(registry_path.read_bytes())==ledger['registry']['sha256']
        registry=read(registry_path);rows=read(p/'BOUNDARIES.json')
        original_units={e.get('unit') for lang in ['Latin','Greek','English'] for e in etree.fromstring((p/f'frozen-inputs/{lang}.xml').read_bytes()).xpath('//t:milestone',namespaces=NS)}
        assert set(registry['structuralMilestoneUnits'])==original_units
        model=read(p/'RECOMMENDED_PHYSICAL_PARTITION_PENDING_EDITOR.json')
        proofs=[];models={}
        for lang in ['Latin','Greek','English']:
            before=(p/f'frozen-inputs/{lang}.xml').read_bytes()
            current=(ROOT/base['inputs'][lang]['relative']).read_bytes()
            assert digest(before)==base['inputs'][lang]['sha256']
            if lang!='English':
                recovered=reverse(current,ledger[lang]['operations']);assert recovered==before
                changed_allowed.add(base['inputs'][lang]['relative'])
                if lang=='Latin':
                    payloads={x['new'].encode() for x in ledger[lang]['operations']}
                    independently_removed=[]
                    def remove(m):
                        token=m.group();assert token in payloads;independently_removed.append(token);return b''
                    recovery2=re.sub(rb'<milestone\b[^>]*xml:id="niese-latin-book'+str(b).encode()+rb'-[^"\r\n]+"[^>]*/>',remove,current)
                    assert recovery2==before and len(independently_removed)==len(payloads)
                else:
                    assert current.count(b'<num>[1]</num>')==1
                    recovery2=current.replace(b'<num>[1]</num>',b'',1)
                    if b==17:
                        assert recovery2.count(b'<num>[31]</num>')==1
                        recovery2=recovery2.replace(b'<num>[31]</num>',b'',1)
                        point=next(x['raw_start'] for x in Book(raw=before).labels if x['text']=='[31]')
                        recovery2=recovery2[:point]+b'<num>[31]</num>'+recovery2[point:]
                    assert recovery2==before
            else:
                recovered=current;assert current==before;recovery2=current
            old_tree,new_tree=etree.fromstring(before),etree.fromstring(current)
            old_ids=[e.get(XMLID) for e in old_tree.iter() if e.get(XMLID)]
            new_ids=[e.get(XMLID) for e in new_tree.iter() if e.get(XMLID)]
            assert len(new_ids)==len(set(new_ids))
            assert [x for x in new_ids if not x.startswith('niese-latin-book')]==old_ids
            assert [(e.get(XMLID),e.get('sameAs')) for e in new_tree.iter() if e.get('sameAs')]==[(e.get(XMLID),e.get('sameAs')) for e in old_tree.iter() if e.get('sameAs')]
            models[lang]=Book(raw=current)
            proofs.append(dict(language=lang,original_sha256=digest(before),implemented_sha256=digest(current),
                ledger_reverse_sha256=digest(recovered),independent_token_reverse_sha256=digest(recovery2),
                byte_exact_recovery=True,original_xml_ids=len(old_ids),implemented_xml_ids=len(new_ids),
                original_ids_order_preserved=True,sameAs_preserved=True,
                original_CRLF=before.count(b'\r\n'),implemented_CRLF=current.count(b'\r\n'),
                original_LF=before.count(b'\n'),implemented_LF=current.count(b'\n'),
                apparatus_notes_wrappers_chapters_material_marking_and_source_TOC_protected_by_byte_recovery=True))
        assert [x['number'] for x in registry['sections']]==list(range(1,expected+1))
        actual_stream,points=independent_stream_and_points(models['Latin'].tree)
        assert actual_stream==Book(p/'frozen-inputs/Latin.xml').stream
        coverage=[0]*len(actual_stream);ranges=[];unavailable=[]
        for identity in registry['sections']:
            n=identity['number'];latin=identity['Latin']
            if not latin['available']:
                unavailable.append(n);assert not latin.get('spans');continue
            actual=[]
            for span in latin['spans']:
                a=points[span['start']['target']]
                z=len(actual_stream) if span['end']['kind']=='book-end' else points[span['end']['target']]
                assert a<z
                text=actual_stream[a:z];actual.append((a,z,text));ranges.append(dict(number=n,start=a,end=z,text=text))
                for i in range(a,z):coverage[i]+=1
            assert actual==[(x['start'],x['end'],x['text']) for x in model['fragments'][str(n)]],n
            assert all(a[1]<=z[0] for a,z in zip(actual,actual[1:])),n
        excluded=[False]*len(actual_stream)
        for x in model['excluded_literal_placeholders']:
            assert actual_stream[x['start']:x['end']]==x['text']
            for i in range(x['start'],x['end']):excluded[i]=True
        assert all(c==0 if excluded[i] else c==1 for i,c in enumerate(coverage))
        assert unavailable==model['unavailable_identities']
        Greek=models['Greek'];labels=[]
        for num in Greek.tree.xpath('//t:body//t:div2[not(@n="0")]/t:p//t:num[not(ancestor::t:note) and not(ancestor::t:app)]',namespaces=NS):
            text=''.join(num.itertext());m=re.fullmatch(r'\[(\d+)\]',text)
            if m:labels.append(int(m.group(1)))
        assert labels==list(range(1,expected+1))
        for label in Greek.labels:
            m=re.fullmatch(r'\[(\d+)\]',label['text'])
            if not m or Greek.units[label['unit']-1]['excluded_reason']:continue
            n=int(m.group(1));assert Greek.first_content(label['book_offset'])==rows[n-1]['Greek_reviewed_locator']['book_offset'],n
        report=dict(status='PASS_INDEPENDENT_SOURCE_RECOVERY_AND_ACTUAL_REGISTRY_COVERAGE',book=b,
            source_byte_proofs=proofs,logical_identities=expected,present_Latin_identities=expected-len(unavailable),
            physical_Latin_fragments=len(ranges),unavailable_identities=unavailable,
            every_included_Latin_character_covered_exactly_once=True,physical_fragment_order_preserved=True,
            independently_resolved_registry_ranges=ranges,Greek_census=labels,
            all_Greek_starts_match_individually_print_reviewed_first_words=True,
            retained_source_anchors=ledger['reused_source_anchors'],added_markers=ledger['added_marker_counts'],
            qualified_runtime_notices=ledger['qualified_runtime_notices'],no_philological_text_changes=True,
            reader_certified=False)
        save(BATCH/f'BOOK_{b}_INDEPENDENT_SOURCE_PROOF.json',report);book_results[str(b)]={k:v for k,v in report.items() if k not in ['independently_resolved_registry_ranges','Greek_census']}
        print(roman,'PASS two independent byte reversals, complete Greek census and actual registry physical coverage;',len(ranges),'Latin fragments')
    drift=[];checkout_variants=[];protected=read(BATCH/'CANONICAL_START_FILES.json')
    baseline_source=Path('C:/workspace/Antiquities-Niese-16-17-integration-runtime-20261010/baseline-source')
    for x in protected:
        canonical_git=(baseline_source/x['path']).read_bytes();raw=(ROOT/x['path']).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(canonical_git)).encode()+b'\0'+canonical_git).hexdigest()==x['blob']
        if digest(canonical_git)!=x['sha256']:
            # Capture existing clean Windows checkout translation separately.
            from integration_common import CAN
            canonical_working=(CAN/x['path']).read_bytes();assert digest(canonical_working)==x['sha256']
            assert canonical_working.replace(b'\r\n',b'\n')==canonical_git.replace(b'\r\n',b'\n')
            checkout_variants.append(dict(path=x['path'],canonical_working_sha256=x['sha256'],canonical_git_sha256=digest(canonical_git),status='PREEXISTING_CLEAN_CHECKOUT_LINE_ENDINGS_UNTOUCHED'))
        if raw!=canonical_git:drift.append(x['path'])
    assert set(drift)==changed_allowed,(drift,changed_allowed)
    save(BATCH/'CANONICAL_CHECKOUT_LINE_ENDINGS.json',checkout_variants)
    incoming=read(BATCH/'CERTIFIED_INCOMING_FILES.json')
    for x in incoming:
        if x['path']!='assets/js/renderTei.js':assert digest((ROOT/x['path']).read_bytes())==x['sha256'],x['path']
    save(BATCH/'COMBINED_SOURCE_PROOF.json',dict(status='PASS',books=book_results,canonical_start='cd6d69e1a3c33a7e8d5a0dabc7c0deda39d0eac9',pinned_files_checked=len(protected),changed_pinned_paths=drift,all_non_scope_canonical_Git_files_byte_exact=True,preexisting_clean_checkout_line_ending_differences=len(checkout_variants),canonical_working_files_untouched=True,incoming_files_checked=len(incoming),incoming_non_renderer_files_byte_exact=True,expected_combined_selectable_count=7082,reader_certified=False))
    print('PASS actual canonical baseline preservation and complete certified incoming packet')
if __name__=='__main__':main()
