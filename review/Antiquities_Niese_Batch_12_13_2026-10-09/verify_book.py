"""Independent final byte reversal, locator and exhaustive narrative partition gate."""
from prepare_review import *
from record_review import independent_node
from implement_book import patch
import subprocess
b=int(sys.argv[1]);d=packet(b);rows=json.loads((d/'BOUNDARIES.json').read_text(encoding='utf8'));baseline=json.loads((d/'BASELINE.json').read_text(encoding='utf8'));preservation=json.loads((d/'IMPLEMENTATION_PRESERVATION.json').read_text(encoding='utf8'));plan=json.loads((d/'APPROVED_MARKER_PLAN.json').read_text(encoding='utf8'));bs=books(b)
assert preservation['status']=='APPLIED_AWAITING_READER_CERTIFICATION'
assert all(r['implementation_approved'] and r['Greek']['print_status']=='VISUALLY_INSPECTED' and r['Greek']['word_boundary_status']=='XML_WORD_START_CONFIRMED_FROM_PRINT' and r['Latin']['review_status']=='INDIVIDUALLY_REVIEWED' for r in rows)
checks=[]
for lang in ['Greek','Latin']:
 original=bs[lang].raw;target=ROOT/f'assets/xml/antiquities/{lang}/book-{b:02}.xml';actual=target.read_bytes();record=next(s for s in preservation['source_records'] if s['language']==lang)
 assert digest(original)==baseline['inputs'][lang]['sha256']
 assert digest(actual)==record['after_sha256'] and patch(actual,record['inverse_operations'])==original
 # A second recovery independent of stored inverse offsets removes only inserted tags.
 if lang=='Latin':recovered=re.sub(rb'<milestone unit="niese" n="[1-9]\d*"/>|<milestone unit="niese-end"/>',b'',actual)
 else:
  assert actual.count(b'<num>[1]</num>')==original.count(b'<num>[1]</num>')+1
  at=rows[0]['Greek']['locator']['raw_byte'];assert actual[at:at+14]==b'<num>[1]</num>'
  recovered=actual[:at]+actual[at+14:]
 assert recovered==original
 parsed=Book(raw=actual);assert parsed.stream==bs[lang].stream
 for r in rows:
  if loc:=r[lang]['locator']:
   independent_node(bs[lang],loc);assert bs[lang].locate(loc['book_offset'])==loc
 for q in ['//@xml:id','//@sameAs']:
  assert parsed.tree.xpath(q,namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})==bs[lang].tree.xpath(q,namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})
 positioned=[r for r in rows if r[lang]['locator']]
 starts=[r[lang]['locator']['book_offset'] for r in positioned];assert starts==sorted(set(starts))
 intervals=[bs[lang].stream[a:z] for a,z in zip(starts,starts[1:]+[len(bs[lang].stream)])]
 assert all(x.strip() for x in intervals)
 prefix=bs[lang].stream[:starts[0]]
 assert ''.join(intervals)==bs[lang].stream[starts[0]:] and (not prefix or prefix.isspace())
 for r,interval in zip(positioned,intervals):assert interval==r[lang]['section' if lang=='Greek' else 'interval']
 checks.append({'language':lang,'expected_sections':len(rows),'physical_intervals':len(intervals),'nonempty_intervals':len(intervals),'leading_whitespace_characters':starts[0],'full_narrative_partition':'PASS','all_node_and_UTF8_locators':'PASS','exact_inverse_and_independent_tag_removal':'PASS','source_narrative_IDs_sameAs_preserved':'PASS','source_sha256_before':digest(original),'source_sha256_after':digest(actual),'build_sha256':digest((RUNTIME/'site'/f'assets/xml/antiquities/{lang}/book-{b:02}.xml').read_bytes())})
 assert checks[-1]['build_sha256']==checks[-1]['source_sha256_after']
english=ROOT/f'assets/xml/antiquities/English/book-{b:02}.xml';assert english.read_bytes()==bs['English'].raw
registry=ROOT/f'assets/xml/antiquities/niese/book-{b:02}.json';assert registry.read_bytes()==(RUNTIME/'site'/registry.relative_to(ROOT)).read_bytes()
assert (ROOT/'assets/js/renderTei.js').read_bytes()==(RUNTIME/'site/assets/js/renderTei.js').read_bytes()
fixture=Book(raw=b'<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div2><p xml:id="latin-book13-num35">III A &amp; B<add>C</add> III.D</p></div2></body></text></TEI>')
assert fixture.stream==' A & BC D'
for i in range(len(fixture.stream)):independent_node(fixture,fixture.locate(i))
save(d/'FINAL_SOURCE_QA.json',{'book':b,'result':'PASS','checks':checks,'English_bytes_unchanged':True,'English_sha256':digest(english.read_bytes()),'registry_build_sha256':digest(registry.read_bytes()),'renderer_build_sha256':digest((ROOT/'assets/js/renderTei.js').read_bytes()),'mixed_content_fixtures':fixtures(),'inline_projection_fixture':'PASS: preserved full source-node offsets across exclusions, entity, nested text/tail and multiple slices','no_independent_Latin_intervals':plan['no_independent_Latin_intervals'],'whole_section_Latin_absence_claims':[],'pending_editorial_decisions':[],'verification_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()})
print('PASS final source/partition',b)
