"""Apply only the independently printed opening Greek identity for one book."""
from pathlib import Path
import json,sys
from source_scope import Book,digest
from verify_locators import validate,validate_all_nodes
ROOT=Path(__file__).resolve().parents[2]
b=int(sys.argv[1]);assert b in [14,15]
roman={14:'XIV',15:'XV'}[b]; d=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
target=ROOT/f'assets/xml/antiquities/Greek/book-{b:02}.xml'
original=(d/'frozen-inputs/Greek.xml').read_bytes();g=Book(raw=original)
loc=g.locate(0);assert g.stream.startswith('Τῶν δὲ' if b==14 else 'Σόσσιος μὲν')
validate(g,loc);nodeqa=validate_all_nodes(g)
at=loc['raw_byte'];marker=b'<num>[1]</num>';output=original[:at]+marker+original[at:]
assert target.read_bytes() in [original,output],'Unexpected target bytes'
changed=Book(raw=output);assert changed.stream==g.stream
assert changed.tree.xpath('//@xml:id')==g.tree.xpath('//@xml:id')
assert changed.tree.xpath('//@sameAs')==g.tree.xpath('//@sameAs')
assert output[:at]+output[at+len(marker):]==original
target.write_bytes(output)
qa=dict(book=b,status='OPENING_GREEK_IDENTITY_APPLIED_ONLY_BOOK_CERTIFICATION_PENDING',marker='<num>[1]</num>',
    addition_count=1,corrections=0,moves=0,reason='Independently verified implicit printed opening identity; chronological summary above printed rule excluded.',
    Niese_printed_page=239 if b==14 else 333,Niese_PDF_page=311 if b==14 else 405,
    image=f'evidence/Niese-III-PDF{311 if b==14 else 405:03}.jpg',printed_marginal_1_glyph=False,
    locator_on_frozen_input=loc,source_sha256=digest(original),after_sha256=digest(output),reverse_sha256=digest(output[:at]+output[at+len(marker):]),
    exact_byte_recovery=True,narrative_unchanged=True,IDs_sameAs_unchanged=True,scope=nodeqa,original_chronological_summary_preserved=True,
    operation=dict(at=at,delete=0,insert=marker.decode()),inverse=dict(at=at,delete=len(marker),expected=marker.decode()),reader_certified=False)
(d/'GREEK_OPENING_IMPLEMENTATION.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(book=b,source_sha256=qa['source_sha256'],after_sha256=qa['after_sha256'],exact_byte_recovery=True,validated_nodes=nodeqa['nodes_verified'])))
