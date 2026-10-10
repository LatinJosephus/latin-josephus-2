"""Independent byte, tree and frozen-physical-point audit of review outputs."""
from reconnaissance import *
from mixed_mapper import Book
from collections import Counter

def main():
    protected=json.loads((PACK/'PROTECTED_INPUTS.json').read_text(encoding='utf8'));checks=[]
    for rel,old in protected.items():
        p=ROOT/rel;actual=sha(p.read_bytes());assert actual==old['sha256'],rel
        checks.append(dict(path=rel,sha256=actual,status='UNCHANGED'))
    save(PACK/'PRODUCTION_PROTECTION_QA.json',dict(status='PASS',baseline=BASE,
        production_files=len(checks),production_changes=0,files=checks,
        English_all_books_and_unrelated_works_unchanged=True,availability_unchanged=True))
    results=[]
    for b in [18,19]:
        d=packet(b);original=(d/'frozen-inputs/Latin.xml').read_bytes();candidate=(d/'review-output/Latin.xml').read_bytes()
        plan=json.loads((d/'APPROVED_SECURE_MARKER_PLAN.json').read_text(encoding='utf8'))
        # Separate inversion implementation: remove the exact new grammar from
        # output, without trusting insertion or shifted inverse coordinates.
        pattern=rb'<milestone unit="niese" n="([1-9][0-9]*)"/>'
        assert not re.search(pattern,original)
        matches=list(re.finditer(pattern,candidate));numbers=[int(m[1]) for m in matches]
        assert numbers==[x['number'] for x in sorted(plan['markers'],key=lambda x:x['at'])]
        assert re.sub(pattern,b'',candidate)==original
        old,new=Book(raw=original),Book(raw=candidate)
        assert old.stream==new.stream
        for path in ['//@xml:id','//@sameAs','//t:div1/@n','//t:div2/@n']:
            assert old.tree.xpath(path,namespaces=NS)==new.tree.xpath(path,namespaces=NS)
        assert [u['id'] for u in old.units]==[u['id'] for u in new.units]
        for query in ['//t:num','//t:pb','//t:cb','//t:argument','//t:floatingText','//t:note','//t:milestone[not(@unit="niese")]']:
            before=[etree.tostring(e,with_tail=False) for e in old.tree.xpath(query,namespaces=NS)]
            after=[etree.tostring(e,with_tail=False) for e in new.tree.xpath(query,namespaces=NS)]
            assert before==after,(b,query)
        structural=json.loads((d/'STRUCTURAL_RECORDS.json').read_text(encoding='utf8'));physical=[]
        models={l:(new if l=='Latin' else Book(raw=(d/'frozen-inputs'/f'{l}.xml').read_bytes())) for l in ['Latin','Greek','English']}
        for r in structural:
            for l,model in models.items():
                p=r['fields'][l];unit=next(u for u in model.units if u['id']==p['paragraph'])
                assert re.sub(r'\s+',' ',unit['text'][int(p['offset']):].strip()).startswith(re.sub(r'\s+',' ',p['anchor'].strip()))
                el=model.tree.xpath('//*[@xml:id=$target]',target=p['target'],namespaces=NS)[0]
                if p['kind']=='element-edge':
                    for step in p['edge'].split('/'):
                        tag,ordinal=re.fullmatch(r'([\w-]+)\[(\d+)\]',step).groups()
                        original_units=set(x.get('unit') for x in old.tree.xpath('//t:milestone',namespaces=NS))
                        children=[x for x in el if etree.QName(x).localname==tag and (tag!='milestone' or x.get('unit') in original_units)]
                        el=children[int(ordinal)-1]
                    assert el.get('unit')=='chapter'
                physical.append(dict(identity=r['id'],language=l,paragraph=p['paragraph'],offset=int(p['offset']),kind=p['kind'],target=p['target'],edge=p.get('edge'),status='UNCHANGED_PHYSICAL_LOCATOR'))
        rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'))
        for n,r in enumerate(rows,1):
            assert r['number']==n and r['print_review_status']=='VISUALLY_REVIEWED'
            ev=r['print_evidence'];assert ev['printed_page']==ev['PDF_page']-14
            assert (d/ev['image']).is_file()
        proof=dict(book=b,status='PASS_REVIEW_OUTPUT_ONLY_FULL_BOOK_NOT_CERTIFIED',
            source_sha256=sha(original),candidate_sha256=sha(candidate),independent_exact_byte_reversal=True,
            CRLF_source=original.count(b'\r\n'),CRLF_candidate=candidate.count(b'\r\n'),
            narrative_sha256=sha(old.stream.encode()),narrative_characters=len(old.stream),
            paragraphs=len(old.units),IDs=old.tree.xpath('//@xml:id'),sameAs=old.tree.xpath('//@sameAs'),
            secure_new_markers=len(matches),reused_existing_physical_starts=len(plan['reused_physical_starts']),
            retained_numeric_starts=len(plan['retained_starts']),structural_locators=physical,
            Greek_source_unchanged=True,English_source_unchanged=True,source_only_contents_and_inline_markup_unchanged=True,
            individually_reviewed_Greek=len(rows),individually_reviewed_Latin=len(rows),
            correspondence_counts=dict(Counter(r['candidate']['correspondence'] for r in rows)),
            pending_sections=plan['pending_sections'],unavailable_claims_approved=plan['approved_unavailable_sections'],
            production_applied=False,availability_enabled=False,certified=False)
        save(d/'INDEPENDENT_REVIEW_PRESERVATION_QA.json',proof);results.append(proof)
        print(b,'independent exact byte inverse PASS;',len(physical),'physical locator checks; source',sha(original),'candidate',sha(candidate))
    save(PACK/'REVIEW_PRESERVATION_SUMMARY.json',[{k:v for k,v in r.items() if k not in ['structural_locators','IDs','sameAs']} for r in results])
if __name__=='__main__':main()
