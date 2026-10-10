from prepare import *
from mixed_mapper import Book
import csv
rows=json.loads((PACK/'IDENTITIES.json').read_text(encoding='utf-8'));m=Book(PACK/'frozen-inputs/Latin.xml')
assert len(rows)==268
for i,r in enumerate(rows):
    start=r['candidate']['Greek_print']['PDF_image_page'];end=rows[i+1]['candidate']['Greek_print']['PDF_image_page'] if i<267 else 334
    r['primary_print_context_pages']=[dict(PDF_image_page=p,printed_page=p-14,sha256=info(PACK/f'evidence/Niese-IV-PDF{p:03}.jpg')['sha256']) for p in range(start,end+1)]
    r['individual_review_complete']=True
    r['editorial_closed']=r['Latin_review_status'] in ['INDIVIDUALLY_REVIEWED','CLOSED_INDIVIDUAL_REVIEW']
    r['whole_witness_displacement_audit']='WHOLE_LATIN_DISPLACEMENT_AUDIT.json'
save(PACK/'IDENTITIES.json',rows)
with (PACK/'BOUNDARIES.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=['number','Niese_printed_page','Niese_PDF_image','Greek_marker_original_byte','Greek_executable_text_byte','Greek_text_node','Greek_codepoint','Latin_start_byte','Latin_codepoint','Latin_text_node','Latin_paragraph','assessment','editorial_status']
    w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
    for r in rows:
        c=r['candidate'];g=r['Greek_locator'];a=r.get('accepted_Latin');l=(a.get('locator') if a else c.get('Latin_locator')) or {}
        w.writerow(dict(number=r['number'],Niese_printed_page=c['Greek_print']['printed_page'],Niese_PDF_image=c['Greek_print']['PDF_image_page'],Greek_marker_original_byte=(r['Greek_label'] or {}).get('raw_start','IMPLICIT'),Greek_executable_text_byte=g['raw_byte'],Greek_text_node=g['text_node_path'],Greek_codepoint=g['book_offset'],Latin_start_byte=l.get('raw_byte'),Latin_codepoint=l.get('book_offset'),Latin_text_node=l.get('text_node_path'),Latin_paragraph=l.get('stable_id'),assessment=a['assessment'] if a else c['assessment'],editorial_status=r['Latin_review_status']))
save(PACK/'LATIN_PHYSICAL_SOURCE_LEDGER.json',dict(source=info(PACK/'frozen-inputs/Latin.xml'),paragraphs=[dict(id=u['id'],original_order=u['index'],raw_interval=[u['raw_start'],u['raw_end']],narrative_interval=[u['book_start'],u['book_start']+len(u['text'])],source_sha256=u['raw_hash'],source_only=u['excluded_reason'],sameAs=u['element'].get('sameAs'),text=u['text']) for u in m.units],source_only_annotation=dict(start=m.locate(m.stream.index('[Niese sections 26')),end=m.locate(m.stream.index('Darta banem particum')),text='[Niese sections 26–37 largely missing; cf. Blatt, p. 68]',classification='Literal inherited source annotation; preserved, not an absence adjudication or Niese identity.'),original_chapter_milestones=[dict(e.attrib) for e in m.tree.xpath('//t:milestone[@unit="chapter"]',namespaces=NS)],manuscript_breaks=[dict(tag=etree.QName(e).localname,attributes=dict(e.attrib)) for e in m.tree.xpath('//t:pb|//t:cb|//t:lb',namespaces=NS)]))
p=PACK/'PRINT_EVIDENCE_MANIFEST.json';manifest=json.loads(p.read_text(encoding='utf-8'))
history=json.loads((PACK/'ADJUDICATION_HISTORY.json').read_text(encoding='utf-8'))
save(PACK/'COMPLETE_PRINT_AUDIT.json',dict(status='PASS',identity_range=[1,268],individually_reviewed_Greek=268,individually_compared_Latin=268,unresolved_representation_cases=sum(h['status']!='APPROVED' for h in history),editorial_history='ADJUDICATION_HISTORY.json',printed_book_extent=dict(start_printed=276,start_PDF=290,end_printed=320,end_PDF=334),Vita_start=dict(printed=321,PDF=335,action='Inspected solely to verify work boundary; excluded from BookXX.'),source_contents_images_reviewed=[288,289,290],source_title_reviewed=5,rendered_pages_not_used_as_review=[336,337,338,339,340,341],images=[info(PACK/f'evidence/Niese-IV-PDF{p:03}.jpg') for p in [5,*range(288,336)]],warning='Every review is tied to its print image. OCR was a locating aid. Rendered image counts alone are not certification.'))
print('268-row register and separate complete physical Latin ledger written.')
