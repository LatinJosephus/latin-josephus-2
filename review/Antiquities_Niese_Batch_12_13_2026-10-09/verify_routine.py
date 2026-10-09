"""Independent source gate for a provisional routine stage, never a certificate."""
from prepare_review import *
from record_review import independent_node
from implement_book import patch
b=int(sys.argv[1]);d=packet(b);bs=books(b)
rows=json.loads((d/'BOUNDARIES.json').read_text(encoding='utf8'))
routine=json.loads((d/'ROUTINE_IMPLEMENTATION_PRESERVATION.json').read_text(encoding='utf8'))
checks=[]
for r in routine['source_records']:
 lang=r['language'];actual=Path(r['path']).read_bytes();before=bs[lang].raw
 assert digest(actual)==r['after_sha256'] and patch(actual,r['inverse_operations'])==before
 if lang=='Latin':recovered=re.sub(rb'<milestone unit="niese" n="[1-9]\d*"/>',b'',actual)
 else:
  at=rows[0]['Greek']['locator']['raw_byte'];assert actual[at:at+14]==b'<num>[1]</num>';recovered=actual[:at]+actual[at+14:]
 assert recovered==before and Book(raw=actual).stream==bs[lang].stream
 assert actual==(RUNTIME/'site'/f'assets/xml/antiquities/{lang}/book-{b:02}.xml').read_bytes()
 locators=[row[lang]['locator'] for row in rows if row[lang]['locator']]
 for loc in locators:independent_node(bs[lang],loc);assert bs[lang].locate(loc['book_offset'])==loc
 checks.append({'language':lang,'source_sha256':digest(actual),'two_independent_exact_recovery_methods':'PASS','narrative_unchanged':'PASS','frozen_node_UTF8_locators_checked':len(locators)})
anon=rows[268]['Latin']['locator'];assert not anon['stable_id']
parsed=Book(raw=Path(routine['source_records'][1]['path']).read_bytes())
marker=parsed.tree.xpath('//t:milestone[@unit="niese" and @n="269"]',namespaces={'t':'http://www.tei-c.org/ns/1.0'});assert len(marker)==1
assert marker[0].getparent().tag.endswith('}p') and not marker[0].getparent().get('{http://www.w3.org/XML/1998/namespace}id')
baseline=json.loads((d/'BASELINE.json').read_text(encoding='utf8'))
for lang in ['Greek','Latin','English']:assert digest(bs[lang].raw)==baseline['inputs'][lang]['sha256']
for pdf in baseline['printed_sources']:assert digest(Path(pdf['path']).read_bytes())==pdf['sha256']
assert (ROOT/f'assets/xml/antiquities/English/book-{b:02}.xml').read_bytes()==bs['English'].raw
save(d/'ROUTINE_SOURCE_QA.json',{'book':b,'result':'PASS','status':'PROVISIONAL_ROUTINE_STAGE_NOT_CERTIFIED','checks':checks,'anonymous_269_ID_preserved_and_explicit_marker_found':True,'PDFs_and_frozen_inputs_unchanged':True,'English_unchanged':True,'pending_representations':routine['pending_representations'],'excluded_adjoining_extent':212,'whole_section_absence_claims':[],'mixed_content_fixtures':fixtures()})
print('PASS routine source gate',b,'pending representations remain',routine['pending_representations'])
