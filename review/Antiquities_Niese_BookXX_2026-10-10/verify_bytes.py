"""Independent byte-recovery gate, whole protected scope, original parsed topology."""
from prepare import *
from mixed_mapper import Book
def main():
    manifest_path=PACK/('APPROVED_INSERTIONS.json' if (PACK/'APPROVED_INSERTIONS.json').exists() else 'SECURE_INSERTIONS.json')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'));results={}
    for lang,edits in manifest['edits'].items():
        target=ROOT/f'assets/xml/antiquities/{lang}/book-20.xml';raw=target.read_bytes();original=(PACK/'frozen-inputs'/f'{lang}.xml').read_bytes();restored=raw
        for e in sorted(edits,key=lambda e:e['final_byte'],reverse=True):
            k=e['final_byte'];addition=e['addition'].encode();assert restored[k:k+len(addition)]==addition,(lang,e)
            restored=restored[:k]+restored[k+len(addition):]
        assert restored==original,(lang,'not byte-exact');etree.fromstring(raw)
        before=Book(raw=original);after=Book(raw=raw)
        assert before.stream==after.stream
        assert before.tree.xpath('//@sameAs')==after.tree.xpath('//@sameAs')
        old_ids=before.tree.xpath('//@xml:id');new_ids=after.tree.xpath('//@xml:id')
        assert set(old_ids).issubset(new_ids) and len(new_ids)==len(set(new_ids))
        expected_new_ids={re.search(r'xml:id="([^"]+)"',e['addition']).group(1) for e in edits if 'xml:id=' in e['addition']}
        assert set(new_ids)-set(old_ids)==expected_new_ids
        assert [u['id'] for u in before.units]==[u['id'] for u in after.units]
        for tag in ['pb','cb','lb','graphic','note','app','rdg','unclear','corr','add','del','argument','floatingText','div1','div2','trailer']:
            a=before.tree.xpath('//t:'+tag,namespaces=NS);b=after.tree.xpath('//t:'+tag,namespaces=NS)
            assert [dict(e.attrib) for e in a]==[dict(e.attrib) for e in b],(lang,tag)
        for u,v in zip(before.units,after.units):
            assert u['text']==v['text'] and dict(u['element'].attrib)==dict(v['element'].attrib)
        results[lang]=dict(status='PASS',original=sha(original),final=sha(raw),reversed=sha(restored),additions=len(edits),CRLF_before=original.count(b'\r\n'),CRLF_after=raw.count(b'\r\n'),projection_sha256=sha(before.stream.encode()),all_original_markup_restored=True,all_original_IDs_retained=True,approved_new_IDs=sorted(expected_new_ids),all_sameAs_unchanged=True)
    protected=json.loads((PACK/'PROTECTED_INPUTS.json').read_text());changed={}
    allowed={'assets/xml/antiquities/Latin/book-20.xml','assets/xml/antiquities/Greek/book-20.xml','assets/js/renderTei.js'}
    for rel,details in protected.items():
        h=sha((ROOT/rel).read_bytes())
        if h!=details['sha256']:assert rel in allowed,rel;changed[rel]=dict(original=details['sha256'],final=h)
    assert sha((ROOT/'assets/xml/antiquities/English/book-20.xml').read_bytes())==sha((PACK/'frozen-inputs/English.xml').read_bytes())
    save(PACK/'BYTE_CERTIFICATION.json',dict(status='PASS',scope=manifest_path.name,final_editorial_certification=False,BookXX=results,protected_files=len(protected),protected_scope_complete=True,changed_existing_production=changed,unchanged_English_all_books=True,unchanged_structure=True,new_registry=info(ROOT/'assets/xml/antiquities/niese/book-20.json')))
    print('PASS byte recovery and protected full production scope:',len(protected),'files')
if __name__=='__main__':main()
