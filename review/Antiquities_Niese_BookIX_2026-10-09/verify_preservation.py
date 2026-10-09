from pathlib import Path
import json,re,subprocess
from lxml import etree
from mixed_mapper import Book,digest
P=Path(__file__).resolve().parent;W=P.parents[1];R=Path('C:/workspace/Antiquities-Niese-09-runtime-20261009')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def patch(raw,ops):
    for o in sorted(ops,key=lambda x:(x['at'],x['delete']),reverse=True):
        old=bytes.fromhex(o['before_hex']);new=bytes.fromhex(o['after_hex']);at=o['at'];assert raw[at:at+len(old)]==old;raw=raw[:at]+new+raw[at+len(old):]
    return raw
base=read(P/'BASELINE.json');impl=read(P/'IMPLEMENTATION_PRESERVATION.json');rows=read(P/'BOUNDARIES.json');ids=read(P/'EXECUTABLE_IDENTITIES.json');results={}
for lang in ['Latin','Greek','English']:
    rel=f'assets/xml/antiquities/{lang}/book-09.xml';original=Path(base['inputs'][rel]['snapshot']).read_bytes();actual=(W/rel).read_bytes();b=Book(raw=actual);before=Book(raw=original)
    if lang!='English':recovered=patch(actual,impl['sources'][lang]['inverse_operations']);assert recovered==original
    else:recovered=actual;assert actual==original
    assert b.stream==before.stream
    assert etree.tostring(etree.fromstring(recovered))==etree.tostring(before.tree)
    # Byte equality above, rather than parsed equality, is the preservation gate.
    results[lang]={'before':digest(original),'after':digest(actual),'recovered':digest(recovered),'byte_exact_recovery':True,'narrative_stream_unchanged':True,'source_build_byte_equal':actual==(R/'build/site'/rel).read_bytes(),'stream_length':len(b.stream),'excluded_editorial_paragraphs':b.excluded}
    if lang!='English':
        locname=lang+'_locator';sectionname=lang+'_section';represented=[r for r in rows if r[locname]]
        first=represented[0][locname]['book_offset'];assert not before.stream[:first].strip();assert ''.join(r[sectionname] for r in represented)==before.stream[first:]
        results[lang]['complete_reviewed_partition']=True;results[lang]['leading_whitespace_codepoints']=first;results[lang]['reviewed_intervals']=len(represented);results[lang]['final_extent']=represented[-1][sectionname][-250:]
        if lang=='Greek':
            actual_starts={int(re.findall(r'\d+',m['text'])[-1]):b.first_content(m['book_offset']) for m in b.labels}
            assert actual_starts=={r['niese']:r['Greek_locator']['book_offset'] for r in represented}
            results[lang]['actual_starts']=len(actual_starts)
        if lang=='Latin':
            milestones=b.tree.xpath('//t:milestone[@unit="niese"]/@n',namespaces={'t':'http://www.tei-c.org/ns/1.0'});assert list(map(int,milestones))==[n for n in ids['new_milestones'] if n not in ids['pending']]
            actual_starts={int(re.findall(r'\d+',m['text'])[-1]):b.first_content(m['book_offset']) for m in b.labels}
            # Derive milestone stream positions from actual text/tail nodes, not saved byte offsets.
            for n in milestones:
                e=b.tree.xpath(f'//t:milestone[@unit="niese"][@n="{n}"]',namespaces={'t':'http://www.tei-c.org/ns/1.0'})[0]
                tag=f'<milestone unit="niese" n="{n}"/>'.encode();matches=list(re.finditer(re.escape(tag),actual));assert len(matches)==1
                node=next(node for node in b.nodes if node['raw_positions'][0]>=matches[0].end());pos=node['book_start']
                assert pos==rows[int(n)-1]['Latin_locator']['book_offset'];assert before.stream[pos:].startswith((e.tail or '')[:20]);actual_starts[int(n)]=pos
            assert len(actual_starts)==len(ids['retained_visible_starts'])+len(milestones)
            results[lang]['actual_starts']=len(actual_starts);results[lang]['implemented_milestones']=len(milestones);results[lang]['inherited_executable_labels']=len(b.labels)
for name,control in base['controls'].items():
    if 'absolute_path' in control and 'sha256' in control:assert digest(Path(control['absolute_path']).read_bytes())==control['sha256']
changed=subprocess.check_output(['git','diff','--name-only',base['base'],'--','assets','_includes'],cwd=W).decode().splitlines()
assert set(changed)=={'assets/js/renderTei.js','assets/xml/antiquities/Greek/book-09.xml','assets/xml/antiquities/Latin/book-09.xml','assets/xml/antiquities/niese/book-09.json'},changed
assert all(s['source_build_byte_equal'] for s in results.values())
assert (W/'assets/js/renderTei.js').read_bytes()==(R/'build/site/assets/js/renderTei.js').read_bytes()
assert (W/'assets/xml/antiquities/niese/book-09.json').read_bytes()==(R/'build/site/assets/xml/antiquities/niese/book-09.json').read_bytes()
write(P/'SOURCE_PRESERVATION_QA.json',{'result':'PASS','phase':'POST_EXPLICIT_240_RESOLUTION' if not ids['pending'] else 'PRE_EXPLICIT_240_RESOLUTION','frozen_base':base['base'],'pending':ids['pending'],'sources':results,'only_production_paths_changed':changed,'all_other_books_unchanged':True,'English_source_unchanged':True,'display_settings_unchanged':True,'PDF_hashes_rechecked':True,'reader_build_byte_equal':True,'registry_build_byte_equal':True})
print('PASS: byte recovery, frozen stream partition, scoped source changes and built asset checks')
