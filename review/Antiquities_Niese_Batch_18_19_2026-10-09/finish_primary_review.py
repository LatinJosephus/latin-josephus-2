from reconnaissance import *
from mixed_mapper import Book

def main():
    d=packet(19);rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'))
    g=Book(raw=(d/'frozen-inputs/Greek.xml').read_bytes());l=Book(raw=(d/'frozen-inputs/Latin.xml').read_bytes())
    r=rows[0];original={k:r[k] for k in ['Greek_start','Greek_text','Greek_locator']}
    at=g.stream.index('Γάιος');assert at==48
    r.update(Greek_start=at,Greek_text=g.stream[at:r['Greek_end']],Greek_locator=g.locate(at),Greek_physical_start=dict(target='trad-greek-LOEB-19-Chapter-1-0',edge='after',reason='Reuse existing narrative-opening anchor; preserved duration notice remains outside exact section1.'))
    rows[-1]['print_evidence'].update(continuation_PDF_page=287,continuation_printed_page=273,continuation_image='evidence/Niese-IV-PDF287.jpg',terminal_observation='Entire final narrative to ἐπαρχίας read through printed p273. No next-book material borrowed; XX Argumenta separately begins p274/PDF288 and XX body p276/PDF290.')
    save(d/'IDENTITIES.json',rows)
    save(d/'OPENING_AND_PARATEXT_REVIEW.json',dict(book=19,implicit_identity=1,original_machine_candidate=original,corrected_narrative_start=r['Greek_locator'],source_notice=g.stream[:at],notice_disposition='All source characters including [στιγμα] retained; duration notice excluded only from exact narrative1. The printed notice is at the end of Argumenta on p210/PDF224.',existing_anchor=r['Greek_physical_start'],opening_print=dict(PDF_page=225,printed_page=211,examined=True,image='evidence/Niese-IV-PDF225.jpg'),source_TOC_print_pages=[210],source_TOC_PDF_pages=[224],TOC_visually_reviewed=True,source_TOC_read=True,Latin_TOC='Literal I–VIII, combined V/VI paragraph, mixed-content VII interlinear addition and image/page/column milestones individually read and retained. None are Niese starts.',nested_topology='No argument/floatingText in XIX; source witness note retained. XVIII nested arguments are separately frozen and protected.',Greek_terminal='No final subscription in printed XIX p273 or current Greek XML; final narrative ends with removal from province.',Latin_terminal='Closes after eos ex illa regione migrauit. No end marker required to distinguish additional material.',next_book_control=dict(Argumenta_PDF_pages=[288,289,290],body_PDF_page=290,visually_examined=True,book20_bytes_protected=True)))
    nav=ROOT/'review/Antiquities_Bamberg_Navigation_2026-10-07'
    navfiles=['REPORT.md','SOURCE_AUTHORITY.md','BASELINE.json','CURRENT_LOCATOR_GATE_QA.json','BAMBERG_BOUNDARY_QA.json','SAME_NIESE_DIFFERENT_POSITION_QA.json','FILE_MANIFEST.json','BROWSER_QA.json']
    save(PACK/'NAVIGATION_AUTHORITY_PROVENANCE.json',dict(base=BASE,source='Committed October7 Bamberg navigation certification; historical claims are controlled by current byte/locator checks and independent actual baseline-reader results.',files=[dict(**info(nav/f),baseline_git_blob=git('rev-parse',f'{BASE}:review/Antiquities_Bamberg_Navigation_2026-10-07/{f}').decode().strip()) for f in navfiles],historical_commit='087c0bf',traditional_refinement='b8d4db2',current_physical_locator_checks='EXPECTED_STRUCTURAL_RANGES.json and DISTINCT_PHYSICAL_POINT_PROOF.json',current_live_checks='BASELINE_STRUCTURAL_BROWSER.json',read_report=True))
    evidence=json.loads((PACK/'PRINT_EVIDENCE_MANIFEST.json').read_text(encoding='utf8'))
    evidence.update(visual_inspection_complete=True,scope='XVIII and XIX all body pages and source contents, title pages, XIX→XX transition controls. Loeb case pages recorded separately; rendering alone never counts as review.',explicitly_inspected_Niese_PDF_pages=list(range(152,291)),title_pages_inspected=[5],independent_Loeb_title_PDF_page=7)
    save(PACK/'PRINT_EVIDENCE_MANIFEST.json',evidence)
    result=[]
    for b,last,body in [(18,379,[154,223]),(19,366,[225,287])]:
        d=packet(b);a=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8')); lm=Book(raw=(d/'frozen-inputs/Latin.xml').read_bytes())
        assert len(a)==last and all(z['candidate'] and z['print_review_status']=='VISUALLY_REVIEWED' for z in a)
        inspected={z['Latin_alignment_paragraph'] for z in a};remaining=[dict(id=u['id'],text=u['text']) for u in lm.units if u['id'] not in inspected]
        assert all(not z['text'] for z in remaining)
        positive=[z for z in a if z['candidate'].get('locator')]
        assert all(x['candidate']['locator']['book_offset']<y['candidate']['locator']['book_offset'] for x,y in zip(positive,positive[1:])),b
        pending=[z['number'] for z in a if not z['candidate'].get('approved')]
        x=dict(book=b,status='PRIMARY_SOURCE_REVIEW_COMPLETE_EDITORIAL_GATES_PENDING',Greek_individually_reviewed=last,Latin_individually_reviewed=last,Latin_narrative_alignment_paragraphs=len(inspected),uninspected_mapper_units=remaining,uninspected_mapper_unit_note='Only excluded chapter0 units; source-only contents separately read.',printed_body_PDF_pages=body,Niese_independent_print_inspection=True,Latin_candidates_strictly_ordered=True,positive_candidates=len(positive),pending_editorial_identities=pending,production_applied=False,reader_certified=False,policy='Secure routine cuts approved under governing §5; unresolved alternatives require the requested human choice. No pending choice is inferred from silence.')
        save(d/'PRIMARY_REVIEW_COMPLETE.json',x);result.append(x)
        ps=json.loads((d/'PRINTED_SOURCES.json').read_text(encoding='utf8'));ps.update(visual_review_complete=True,primary_review_manifest='PRIMARY_REVIEW_COMPLETE.json');save(d/'PRINTED_SOURCES.json',ps)
    save(PACK/'PRIMARY_REVIEW_SUMMARY.json',result)
    print(json.dumps([dict(book=z['book'],reviewed=z['Greek_individually_reviewed'],positive_candidates=z['positive_candidates'],pending=z['pending_editorial_identities']) for z in result]))
if __name__=='__main__':main()
