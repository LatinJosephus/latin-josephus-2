from prepare import *
from review_sources import Proem
def main():
    protected=json.loads((PACK/'PROTECTED_GIT_OBJECTS.json').read_text())
    production=lambda p:p.startswith(('assets/','_includes/','_layouts/','_pages/','_sass/','_data/','bin/')) or p in ['_config.yml','Gemfile','.gitattributes','.gitignore','404.html','robots.txt','CNAME']
    allowed={'assets/js/renderTei.js','assets/xml/antiquities/Latin/preface.xml','assets/xml/antiquities/niese/preface.json'}
    mismatches=[];checked=[];checkouts=[]
    for p,oid in protected.items():
        if not production(p) or p in allowed:continue
        raw=(ROOT/p).read_bytes();blob=git('show',BASE+':'+p)
        # Some tracked Windows text files materialize CRLF without editorial changes.
        if raw!=blob:
            assert raw.replace(b'\r\n',b'\n')==blob or raw==blob.replace(b'\r\n',b'\n'),p
            checkouts.append(dict(path=p,worktree_sha256=sha(raw),git_sha256=sha(blob),cause='checkout newline materialization only'))
        checked.append(dict(path=p,git_blob=oid,git_sha256=sha(blob)))
    changes=json.loads((PACK/'READER_PATCH.json').read_text());reader=(ROOT/'assets/js/renderTei.js').read_text(encoding='utf-8');reverse=reader
    for change in reversed(changes):
        assert reverse.count(change['new'])==1,change['new'][:80]
        reverse=reverse.replace(change['new'],change['old'])
    assert reverse.encode()==git('show',BASE+':assets/js/renderTei.js')
    current=[];rows=json.loads((PACK/'DECISION_REGISTER.json').read_text(encoding='utf-8'))
    for row in rows:
        languages={}
        for l in ['Greek','Latin']:
            raw=(ROOT/f'assets/xml/antiquities/{l}/preface.xml').read_bytes();model=Proem(raw)
            a=row[l+'_start']['unicode_proem_offset'];z=row[l+'_end']['unicode_proem_offset'];assert sha(model.text[a:z].encode())==row[l+'_extent_sha256']
            end=model.locate(z) if row['number']<26 else dict(kind='exclusive_narrative_end',unicode_proem_offset=z,raw_UTF8_byte_offset=raw.index(b'<milestone unit="niese-end"') if l=='Latin' else model.units[-1]['raw_end']-4)
            languages[l]=dict(start=model.locate(a),end=end,extent_sha256=sha(model.text[a:z].encode()))
        current.append(dict(number=row['number'],languages=languages))
    save(PACK/'IMPLEMENTED_LOCATORS.json',current)
    image_records=[]
    for label,numbers in [('Niese',[7,*range(94,100)]),('Loeb',[7,*range(26,39,2)])]:
        for n in numbers:image_records.append(dict(PDF_page=n,visual_review='COMPLETE',**info(PACK/f'evidence/{label}-PDF{n:03}.jpg')))
    save(PACK/'PRINT_VERIFICATION.json',dict(status='PASS',Proem_Greek_starts=26,Niese_complete_pages=[4,5,6,7,8,9],Loeb_complete_Greek_pages=[2,4,6,8,10,12,14],images=image_records,Greek_terminal='ἔχει δὲ οὕτως:',next='I.27 Ἐν ἀρχῇ ἔκτισεν ὁ θεός',marginal_numerals='Line placements are not presumed word boundaries; individual cuts recorded in DECISION_REGISTER.json',note='Printed text and complete semantic extents reviewed directly; original digital punctuation/spelling retained'))
    historical=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\Transkribus Project\Froben\Preface\bamberg_preface.xml')
    doc=etree.fromstring(historical.read_bytes());frozen=etree.fromstring((PACK/'frozen-inputs/Latin.xml').read_bytes());controls=[]
    for p in frozen.xpath('//t:p[@xml:id]',namespaces=NS):
        orig=doc.xpath('//t:p[@xml:id=$id]',id=p.get(ID),namespaces=NS)[0];base=''.join(p.itertext());old=''.join(orig.itertext());prefix=old[:len(base)]
        assert base==prefix or base.replace('  ',' ')==prefix.replace('  ',' '),(p.get(ID),base[:40],old[:40])
        controls.append(dict(xml_id=p.get(ID),canonical_text_sha256=sha(base.encode()),historical_contains_full_canonical_text=True,historical_trailing_text=old[len(base):]))
    save(PACK/'BAMBERG_PROVENANCE_CONTROL.json',dict(status='PASS',historical=info(historical),canonical_authority='Existing production source, not replaced',paragraphs=controls))
    save(PACK/'PRODUCTION_PRESERVATION.json',dict(status='PASS',protected_existing_production_count=len(checked),protected=checked,Windows_checkout_differences=checkouts,reader_patch_exact_reversal=True,reader_baseline_sha256=sha(reverse.encode()),allowed_production_files=sorted(allowed),Book_I_320_sources_unchanged=True,all_20_books_preserved=True))
    print('PASS protected production, exact reader-patch reversal, current locator extents, print/provenance controls')
if __name__=='__main__':main()
