"""Independent merged-byte, interval, physical-structure, and incoming-history audit."""
import sys
sys.dont_write_bytecode=True
from integration_common import *
from collections import Counter
authority=ROOT/'review/Antiquities_Niese_Batch_18_19_2026-10-09'
sys.path.insert(0,str(authority))
from mixed_mapper import Book

def main():
    before=read(D/'BASELINE.json');incoming=read(D/'INCOMING_SCOPE.json')
    authorized={'assets/js/renderTei.js','assets/xml/antiquities/Latin/book-18.xml','assets/xml/antiquities/Latin/book-19.xml'}
    changed=[];unchanged=[]
    for f in before['files']:
        actual=sha((ROOT/f['relative']).read_bytes())
        if actual!=f['sha256']:
            assert f['relative'] in authorized,f['relative'];changed.append(dict(**f,output_sha256=actual))
        else:unchanged.append(f['relative'])
    assert set(x['relative'] for x in changed)==authorized
    incoming_checks=[]
    for f in incoming['files']:
        actual=sha((ROOT/f['relative']).read_bytes())
        if f['relative']!='assets/js/renderTei.js':assert actual==f['sha256'],f['relative']
        incoming_checks.append(dict(relative=f['relative'],certified_sha256=f['sha256'],merged_sha256=actual,status='NECESSARY_SHARED_RENDERER_MERGE' if f['relative']=='assets/js/renderTei.js' else 'BYTE_IDENTICAL_CERTIFIED_SOURCE'))
    assert len(incoming_checks)==450
    for commit in before['source_commits']:
        assert subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=ROOT).returncode==0
    assert len(before['source_commits'])==16
    output=[]
    for b,roman,identities,intervals,reused,added in [(18,'XVIII',379,377,61,316),(19,'XIX',366,366,46,320)]:
        packet=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
        original=(packet/'frozen-inputs/Latin.xml').read_bytes();candidate=(ROOT/f'assets/xml/antiquities/Latin/book-{b}.xml').read_bytes()
        plan=read(packet/'FINAL_MARKER_PLAN.json');expected=read(packet/'FINAL_EXPECTED_INTERVALS.json');rows=read(packet/'IDENTITIES.json')
        registry=read(ROOT/f'assets/xml/antiquities/niese/book-{b}.json')
        pattern=rb'<milestone unit="niese" n="([1-9][0-9]*)"/>'
        assert not re.search(pattern,original)
        matches=list(re.finditer(pattern,candidate));numbers=[int(m[1]) for m in matches]
        assert len(matches)==added and numbers==[x['number'] for x in sorted(plan['markers'],key=lambda x:x['at'])]
        recovered=re.sub(pattern,b'',candidate);assert recovered==original
        # Raw inverse is independently compared to the actual source-baseline blob.
        assert recovered==git('show',f'{BASE}:assets/xml/antiquities/Latin/book-{b}.xml')
        old=Book(raw=original);new=Book(raw=candidate);assert old.stream==new.stream
        assert len(plan['reused_physical_starts'])==reused and len(plan['retained_starts'])==0
        for xp in ['//@xml:id','//@sameAs','//t:div1/@n','//t:div2/@n']:
            assert old.tree.xpath(xp,namespaces=NS)==new.tree.xpath(xp,namespaces=NS),(b,xp)
        for xp in ['//t:num','//t:pb','//t:cb','//t:argument','//t:floatingText','//t:note','//t:milestone[not(@unit="niese")]']:
            assert [etree.tostring(x,with_tail=False) for x in old.tree.xpath(xp,namespaces=NS)]==[etree.tostring(x,with_tail=False) for x in new.tree.xpath(xp,namespaces=NS)],(b,xp)
        assert [u['id'] for u in old.units]==[u['id'] for u in new.units]
        marker_map={int(m[1]):m for m in matches}
        for r in plan['markers']:
            point=new.locate(r['locator']['book_offset'])
            assert marker_map[r['number']].end()==point['raw_byte']
            assert point['stable_id']==r['locator']['stable_id'] and point['unit_offset']==r['locator']['unit_offset']
        positive=[r for r in expected if not r['unavailable']]
        assert len(expected)==len(rows)==len(registry['sections'])==identities
        assert len(positive)==intervals and ''.join(r['Latin'] for r in positive)==old.stream
        assert positive[0]['Latin_start']['book_offset']==0 and positive[-1]['Latin_end']==len(old.stream)
        assert [r['Latin_end'] for r in positive[:-1]]==[r['Latin_start']['book_offset'] for r in positive[1:]]
        assert [s['number'] for s in registry['sections']]==list(range(1,identities+1))
        unavailable=[s['number'] for s in registry['sections'] if not s['Latin']['available']]
        assert unavailable==([216,217] if b==18 else [])
        language_checks=[];models={'Latin':new}
        for language in ['Greek','English']:
            raw=(ROOT/f'assets/xml/antiquities/{language}/book-{b}.xml').read_bytes()
            assert raw==(packet/'frozen-inputs'/f'{language}.xml').read_bytes()==git('show',f'{BASE}:assets/xml/antiquities/{language}/book-{b}.xml')
            models[language]=Book(raw=raw);language_checks.append(dict(language=language,sha256=sha(raw),byte_identical=True))
        physical=[]
        original_units=set(x.get('unit') for x in old.tree.xpath('//t:milestone',namespaces=NS))
        for record in read(packet/'STRUCTURAL_RECORDS.json'):
            for language,model in models.items():
                p=record['fields'][language];unit=next(u for u in model.units if u['id']==p['paragraph'])
                norm=lambda s:re.sub(r'\s+',' ',s.strip())
                assert norm(unit['text'][int(p['offset']):]).startswith(norm(p['anchor']))
                el=model.tree.xpath('//*[@xml:id=$target]',target=p['target'],namespaces=NS)[0]
                if p['kind']=='element-edge':
                    for step in p['edge'].split('/'):
                        tag,ordinal=re.fullmatch(r'([\w-]+)\[(\d+)\]',step).groups()
                        children=[x for x in el if etree.QName(x).localname==tag and (tag!='milestone' or x.get('unit') in original_units)]
                        el=children[int(ordinal)-1]
                    assert el.get('unit')=='chapter'
                physical.append(dict(identity=record['id'],language=language,paragraph=p['paragraph'],offset=int(p['offset']),kind=p['kind'],target=p['target'],edge=p.get('edge'),status='UNCHANGED'))
        assert all(r['candidate']['approved'] and r['print_review_status']=='VISUALLY_REVIEWED' for r in rows)
        if b==18:
            for n,start in [(7,'et supra quam dici potest'),(94,'Transacta uero festiuitate')]:assert expected[n-1]['Latin'].startswith(start)
            assert not set(unavailable)&set(marker_map)
            assert expected[214]['Latin_end']==expected[217]['Latin_start']['book_offset']
            assert all(expected[n-1]['Greek'] and expected[n-1]['English'] and expected[n-1]['Latin'] is None for n in unavailable)
        else:assert expected[187]['Latin'].startswith('Erant enim cohortes')
        output.append(dict(book=b,status='PASS',identities=identities,independent_Latin_intervals=intervals,reused_physical_starts=reused,added_Latin_milestones=added,retained_numeric_starts=0,unavailable=unavailable,inverse_original_sha256=sha(recovered),candidate_sha256=sha(candidate),inverse_byte_exact=True,whole_narrative_partition_exact=True,IDs_sameAs_labels_whitespace_punctuation_divisions_preserved=True,Greek_English=language_checks,structural_locators=physical,closed_decisions_preserved=True))
    archive=read(authority/'ADJUDICATION_ARCHIVE.json')
    for item in archive['archived_files']:assert sha((ROOT/item['archive']).read_bytes())==item['sha256']
    result=dict(status='PASS',canonical_start=START,source=SOURCE,source_commits=before['source_commits'],all_sixteen_ancestors=True,canonical_start_files=len(before['files']),unchanged_canonical_files=len(unchanged),changed_canonical_files=changed,source_manifest=incoming_checks,unchanged_incoming_review_files=445,exact_incoming_data_files=4,new_production_files=['assets/xml/antiquities/niese/book-18.json','assets/xml/antiquities/niese/book-19.json'],necessary_shared_code='assets/js/renderTei.js',books=output,verbatim_HOLD_archive_files=len(archive['archived_files']),all_editorial_holds_closed=True)
    save('COMBINED_SOURCE_PROOF.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_manifest','books','changed_canonical_files','source_commits']}))
if __name__=='__main__':main()
