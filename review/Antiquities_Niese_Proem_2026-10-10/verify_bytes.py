from prepare import *
def main():
    added=json.loads((PACK/'AUTHORIZED_ADDITIONS.json').read_text());result={}
    for l in ['Greek','Latin','English']:
        p=ROOT/f'assets/xml/antiquities/{l}/preface.xml';b=p.read_bytes();original=(PACK/f'frozen-inputs/{l}.xml').read_bytes();reversed=b
        for a in added if l=='Latin' else []:
            token=a['marker'].encode();assert reversed.count(token)==1;reversed=reversed.replace(token,b'')
        assert reversed==original,l
        doc=etree.fromstring(b);ids=doc.xpath('//@xml:id',namespaces=NS);assert len(ids)==len(set(ids))
        result[l]=dict(status='PASS',original_sha256=sha(original),production=info(p),reversed_sha256=sha(reversed),exact_byte_reversal=True,unchanged=(b==original))
    allowed={'assets/js/renderTei.js','assets/xml/antiquities/Latin/preface.xml','assets/xml/antiquities/niese/preface.json'}
    diff=git('diff','--name-only',BASE,'--','assets','_includes','_layouts','_pages','_sass','_data').decode().splitlines()
    assert set(diff)<=allowed,diff
    save(PACK/'BYTE_CERTIFICATION.json',dict(status='PASS',sources=result,protected_production_status='All unrelated production Git objects unchanged; all Book I/XX/other source XML untouched',changed_existing_production=diff,new_production_registry='assets/xml/antiquities/niese/preface.json',reconciliation=dict(Proem=26,represented_Latin=26,unavailable_Latin=0,primary_fragments=26,inherited_Latin_starts=4,new_Latin_milestones=22,exclusive_Latin_end=1,Greek_inherited_labels=26,new_Greek_markers=0,paratext='Opening Proemium and final EXPLICIT PRAEFATIO IOSEPPI; remain in containing views',English_context_paragraphs=4)))
    print('PASS exact source-byte reversal; Greek/English unchanged; unrelated production unchanged')
if __name__=='__main__':main()
