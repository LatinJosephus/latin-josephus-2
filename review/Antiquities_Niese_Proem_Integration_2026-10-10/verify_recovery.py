"""Reconcile coordinates against approved decisions; no print review or source edits."""
from prepare import *
from review_sources import Proem
import csv, io, datetime

def main():
    decisions=json.loads((PACK/'DECISION_REGISTER.json').read_text(encoding='utf-8'))
    expected=json.loads((PACK/'EXPECTED_INTERVALS.json').read_text(encoding='utf-8'))
    registry=json.loads((ROOT/'assets/xml/antiquities/niese/preface.json').read_text(encoding='utf-8'))
    assert [r['number'] for r in decisions]==[r['number'] for r in expected]==[r['number'] for r in registry['sections']]==list(range(1,27))
    assert all(r['Latin']['available'] for r in registry['sections'])
    assert registry['book']=='preface' and registry['range']==[1,26] and registry['relatedPassage']['niese']==27
    assert expected[24]['Latin'].startswith('Volentius autem') and expected[24]['Latin'].rstrip().endswith('Quod ego nunc quidem')
    assert expected[25]['Latin'].startswith('adrerum narrationem') and 'Quod' not in expected[25]['Latin']
    current=[];reconstruction={};models={l:Proem((ROOT/f'assets/xml/antiquities/{l}/preface.xml').read_bytes()) for l in ['Greek','Latin','English']}
    for l in ['Greek','Latin']:
        m=models[l];parts=[];last=None
        for row,e in zip(decisions,expected):
            a=row[l+'_start']['unicode_proem_offset'];z=row[l+'_end']['unicode_proem_offset']
            if last is not None:assert a==last
            t=m.text[a:z];assert t==row[l+'_complete_text']==e[l] and sha(t.encode())==row[l+'_extent_sha256']
            parts.append(t);last=z
        prefix=m.text[:decisions[0][l+'_start']['unicode_proem_offset']]
        assert prefix+''.join(parts)==m.text
        reconstruction[l]=dict(status='PASS',full_mixed_content_sha256=sha(m.text.encode()),leading_whitespace=prefix,contiguous_intervals=26,noncontiguous_fragments=0,full_narrative_reconstruction=True)
    for row in decisions:
        languages={}
        for l in ['Greek','Latin']:
            m=models[l];a=row[l+'_start']['unicode_proem_offset'];z=row[l+'_end']['unicode_proem_offset']
            end=m.locate(z) if row['number']<26 else dict(kind='exclusive_narrative_end',unicode_proem_offset=z,raw_UTF8_byte_offset=m.raw.index(b'<milestone unit="niese-end"') if l=='Latin' else m.units[-1]['raw_end']-4)
            languages[l]=dict(start=m.locate(a),end=end,extent_sha256=sha(m.text[a:z].encode()))
        current.append(dict(number=row['number'],languages=languages))
    for e in expected:
        assert next(u['text'] for u in models['English'].units if u['id']==e['English_context_target'])==e['English']
    assert len({r['English_context_target'] for r in expected})==4
    latin=models['Latin'];starts=latin.doc.xpath('//t:milestone[@unit="niese"]',namespaces=NS)
    inherited=latin.doc.xpath('//t:div1/t:p[@xml:id]/t:num',namespaces=NS)
    assert len(starts)==22 and len(inherited)==4
    assert len(latin.doc.xpath('//t:milestone[@unit="niese-end"]',namespaces=NS))==1
    assert len(models['Greek'].doc.xpath('//t:div1/t:p/t:num',namespaces=NS))==26
    assert not models['Greek'].doc.xpath('//t:milestone[@unit="niese"]',namespaces=NS)
    assert latin.doc.xpath('//t:div1/t:p[not(@xml:id)]/text()',namespaces=NS)[0]=='[Proemium]'
    assert 'EXPLICIT' not in latin.text and 'EXPLICIT' in ''.join(latin.doc.itertext())
    from verify_bytes import main as bytes_main
    bytes_main()
    changes=json.loads((PACK/'READER_PATCH.json').read_text(encoding='utf-8'))
    reader=(ROOT/'assets/js/renderTei.js').read_text(encoding='utf-8');reverse=reader
    for c in reversed(changes):
        assert reverse.count(c['new'])==1
        reverse=reverse.replace(c['new'],c['old'])
    assert reverse.encode()==git('show',BASE+':assets/js/renderTei.js')
    assert '[...pane.childNodes]' in reader
    production=lambda p:p.startswith(('assets/','_includes/','_layouts/','_pages/','_sass/','_data/','bin/')) or p in ['_config.yml','Gemfile','.gitattributes','.gitignore','404.html','robots.txt','CNAME']
    allowed={'assets/js/renderTei.js','assets/xml/antiquities/Latin/preface.xml','assets/xml/antiquities/niese/preface.json'}
    tree=lambda rev:{line.split('\t')[1]:line.split()[2] for line in git('ls-tree','-r','--full-tree',rev).decode().splitlines()}
    baseline=tree(BASE);head=tree('HEAD');protected={p:oid for p,oid in baseline.items() if production(p) and p not in allowed}
    assert all(head[p]==oid for p,oid in protected.items())
    assert not git('diff','HEAD','--',*[p for p in protected]).strip()
    assert set(p for p in head if production(p) and p not in baseline)<=allowed
    # Fresh manifest records exact worktree bytes as well as protected immutable objects.
    checked=[dict(path=p,git_blob=oid,worktree_sha256=sha((ROOT/p).read_bytes()),bytes=(ROOT/p).stat().st_size) for p,oid in protected.items()]
    save(PACK/'PRODUCTION_PRESERVATION.json',dict(status='PASS',baseline_commit=BASE,production_commit='4afe79be6d4ba2f8fdcf5ca1a07fda878d7a56fb',protected_existing_production_count=len(checked),protected=checked,reader_patch_exact_reversal=True,reader_baseline_sha256=sha(reverse.encode()),allowed_production_files=sorted(allowed),all_20_books_preserved=True,Book_I_320_sources_unchanged=True))
    save(PACK/'IMPLEMENTED_LOCATORS.json',current)
    save(PACK/'RECONSTRUCTION_QA.json',reconstruction)
    fields=['Niese','Greek printed start','Niese printed p','Niese PDF p','Loeb printed p','Loeb PDF p','Latin start','Latin enclosing id','Latin confidence','English context','Editorial status']
    out=io.StringIO(newline='');w=csv.writer(out,lineterminator='\n');w.writerow(fields)
    for r in decisions:w.writerow([r['number'],r['Greek_start_phrase'],r['Niese']['printed_page'],r['Niese']['PDF_page'],r['Loeb']['printed_page'],r['Loeb']['PDF_page'],r['Latin_complete_text'][:100],r['Latin_start']['xml_id'],r['Latin_cut_confidence'],r['English_context_target'],r['editorial_status']])
    (PACK/'BOUNDARIES.csv').write_text(out.getvalue(),encoding='utf-8',newline='\n')
    save(PACK/'METADATA_RECONCILIATION.json',dict(status='PASS',source_review_reopened=False,production_changed=False,source_commit='4afe79be6d4ba2f8fdcf5ca1a07fda878d7a56fb',original_records_preserved=str(ROOT/'review/Antiquities_Niese_Proem_2026-10-10'),refreshed=['BOUNDARIES.csv','IMPLEMENTED_LOCATORS.json','RECONSTRUCTION_QA.json','BYTE_CERTIFICATION.json','PRODUCTION_PRESERVATION.json'],Latin25=dict(start='Volentius autem',end='Quod ego nunc quidem',qualification=registry['sections'][24]['Latin']['note']),Latin26=dict(start='adrerum narrationem',qualification=registry['sections'][25]['Latin']['note']),intervals=26,new_Latin_starts=22,inherited_Latin_starts=4,exclusive_Latin_end=1,unavailable=0,English_context_paragraphs=4,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    print('PASS current 26 intervals, locators, boundary metadata, marker inventory, reconstruction, reader reversal and protected production')
if __name__=='__main__':main()
