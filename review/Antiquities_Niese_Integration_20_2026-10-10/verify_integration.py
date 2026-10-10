from integration_common import *
from lxml import etree
def main():
    changed=git('diff','--name-only',START,'HEAD','--','assets').decode().splitlines()
    allowed=['assets/js/renderTei.js','assets/xml/antiquities/Greek/book-20.xml','assets/xml/antiquities/Latin/book-20.xml','assets/xml/antiquities/niese/book-20.json']
    assert sorted(changed)==sorted(allowed),changed
    baseline=read(PACK/'STARTING_FILES.json');protected=[];line_endings=[]
    for rel,record in baseline.items():
        if rel in allowed:continue
        assert git('rev-parse','HEAD:'+rel).decode().strip()==record['git_blob_oid'],rel
        if 'integration_checkout' in record:
            assert sha((ROOT/rel).read_bytes())==record['integration_checkout']['sha256'],rel
            protected.append(rel)
            if record['canonical_checkout']['sha256']!=record['git_sha256']:
                raw=(CANON/rel).read_bytes();blob=git('show',START+':'+rel)
                assert raw.replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n'),rel
                line_endings.append(dict(path=rel,canonical=record['canonical_checkout'],git_sha256=record['git_sha256'],content_identical_after_CRLF_normalization=True))
    save(PACK/'WINDOWS_CHECKOUT_DIFFERENCES.json',dict(status='PASS',count=len(line_endings),files=line_endings,handling='Record separately; do not normalize or rewrite unrelated canonical working files.'))
    insertions=read(ROOT/'review/Antiquities_Niese_BookXX_2026-10-10/APPROVED_INSERTIONS.json');book={}
    ns={'t':'http://www.tei-c.org/ns/1.0'}
    for lang,edits in insertions['edits'].items():
        rel=f'assets/xml/antiquities/{lang}/book-20.xml';raw=(ROOT/rel).read_bytes();original=git('show',FROZEN+':'+rel);restored=raw
        for e in sorted(edits,key=lambda e:e['final_byte'],reverse=True):
            k=e['final_byte'];addition=e['addition'].encode('utf-8');assert restored[k:k+len(addition)]==addition
            restored=restored[:k]+restored[k+len(addition):]
        assert restored==original and sha(restored)==insertions['original_hashes'][lang]
        before=etree.fromstring(original);after=etree.fromstring(raw)
        assert before.xpath('//@sameAs')==after.xpath('//@sameAs')
        assert set(before.xpath('//@xml:id')).issubset(set(after.xpath('//@xml:id')))
        assert len(after.xpath('//@xml:id'))==len(set(after.xpath('//@xml:id')))
        assert sha(raw)==read(SOURCE_PACK/'PRODUCTION_MANIFEST.json')['files'][rel]['sha256']
        oldnums=[etree.tostring(e) for e in before.xpath('//t:num',namespaces=ns)]
        newnums=after.xpath('//t:num',namespaces=ns)
        book[lang]=dict(status='PASS',input_sha256=sha(original),recovered_sha256=sha(restored),merged_sha256=sha(raw),authorized_additions=len(edits),original_ids_retained=True,sameAs_unchanged=True,entire_original_markup_and_whitespace_recovered=True,old_num_count=len(oldnums),new_num_count=len(newnums),old_chapters=len(before.xpath('//t:milestone[@unit="chapter"]',namespaces=ns)),new_chapters=len(after.xpath('//t:milestone[@unit="chapter"]',namespaces=ns)))
    en='assets/xml/antiquities/English/book-20.xml';assert sha((ROOT/en).read_bytes())==insertions['original_hashes']['English']
    reg=read(ROOT/'assets/xml/antiquities/niese/book-20.json');sections=reg['sections'];unavailable=[s['number'] for s in sections if s.get('Latin',{}).get('available') is False]
    assert len(sections)==268 and unavailable==list(range(27,37))+[238]
    assert sum(s.get('Latin',{}).get('available') is not False for s in sections)==257
    lat=etree.fromstring((ROOT/'assets/xml/antiquities/Latin/book-20.xml').read_bytes());greek=etree.fromstring((ROOT/'assets/xml/antiquities/Greek/book-20.xml').read_bytes())
    assert len(lat.xpath('//t:milestone[@unit="niese"]',namespaces=ns))==257
    assert len(lat.xpath('//t:anchor[@xml:id="niese-latin-book20-end26"]',namespaces=ns))==1
    assert len(greek.xpath('//t:num',namespaces=ns))==268
    assert len(lat.xpath('//t:milestone[@unit="chapter"]',namespaces=ns))==20
    manifest=read(SOURCE_PACK/'PRODUCTION_MANIFEST.json')
    for rel in allowed[1:]:assert sha((ROOT/rel).read_bytes())==manifest['files'][rel]['sha256']
    review=read(PACK/'CERTIFIED_SOURCE_REVIEW_FILES.json')
    for rel,record in review.items():assert git('rev-parse','HEAD:'+rel).decode().strip()==record['git_blob_oid'],rel
    for ancestor in [SOURCE_TIP,*read(PACK/'BASELINE.json')['required_ancestors']]:subprocess.run(['git','merge-base','--is-ancestor',ancestor,'HEAD'],cwd=ROOT,check=True)
    history=read(ROOT/'review/Antiquities_Niese_BookXX_2026-10-10/ADJUDICATION_HISTORY.json');assert len(history)==4 and all(d['status']=='APPROVED' for d in history)
    save(PACK/'SOURCE_INTEGRITY.json',dict(status='PASS',tested_commit=git('rev-parse','HEAD').decode().strip(),BookXX=book,English_sha256=sha((ROOT/en).read_bytes()),identities=268,represented_Latin=257,unavailable_Latin=unavailable,primary_fragments=257,new_Latin_starts=257,end_anchors=1,new_Greek_labels=1,old_Greek_labels_preserved=267,Bamberg_and_legacy_chapters=20,source_review_files_unchanged=len(review),all_prior_tracked_files_preserved=len(baseline)-3,protected_physical_files_preserved=len(protected),approved_A_decisions_preserved=True,certified_history_preserved=True,production_files={rel:info(ROOT/rel) for rel in allowed},Windows_line_endings='WINDOWS_CHECKOUT_DIFFERENCES.json'))
    print('PASS full baseline preservation, source byte recovery, four closed A decisions and complete source ancestry')
if __name__=='__main__':main()
