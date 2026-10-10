"""Independent lxml node / raw-byte checks and inverse recovery, separate from rendering."""
from pathlib import Path
import json,re,sys,subprocess
sys.dont_write_bytecode=True
from lxml import etree
from mixed_mapper import Book,digest,NS,XMLID,fixtures
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
def save(name,x):(D/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def value_at(tree,path):
 steps=path.lstrip('/').split('/');node=tree;assert steps.pop(0)=='TEI[1]'
 for step in steps:
  if step=='text()':return node.text or ''
  if step=='tail()':return node.tail or ''
  m=re.fullmatch(r'(.*)\[(\d+)\]',step);assert m,(path,step)
  tag,k=m[1],int(m[2]);children=[c for c in node if (isinstance(c,etree._Comment) if tag=='comment()' else isinstance(c.tag,str) and etree.QName(c).localname==tag)]
  node=children[k-1]
 raise ValueError('Not a text locator')
def check_loc(b,loc):
 if loc.get('kind')=='narrative-end':
  assert loc['book_offset']==len(b.stream) and b.raw[loc['raw_byte']:loc['raw_byte']+4]==b'</p>'
  value=value_at(b.tree,loc['text_node_path']);assert loc['node_offset']==len(value) and value[-1:]==b.stream[-1:]
  u=b.units[loc['paragraph']-1];assert u['id']==loc['stable_id'] and u['raw_end']==loc['raw_byte']+4
  assert loc['raw_unit_sha256']==digest(b.raw[u['raw_start']:u['raw_end']]);return
 value=value_at(b.tree,loc['text_node_path']);k=loc['node_offset'];at=loc['book_offset'];assert value[k:]==next(n['text'][k:] for n in b.nodes if n['path']==loc['text_node_path'])
 assert value[k]==b.stream[at];raw=b.raw[loc['raw_byte']:]
 c=value[k]
 if raw.startswith(b'&'):
  entity=raw[:raw.index(b';')+1];decoded=etree.fromstring(b'<x>'+entity+b'</x>').text;assert decoded==c
 elif raw.startswith(b'\r'):assert c=='\n'
 else:assert raw.startswith(c.encode('utf8'))
 u=b.units[loc['paragraph']-1];assert u['id']==loc['stable_id'] and u['xpath']==loc['xpath'];assert digest(b.raw[u['raw_start']:u['raw_end']])==loc['raw_unit_sha256']
 assert digest(etree.tostring(u['element'],encoding='utf8',with_tail=False))==loc['parsed_unit_sha256']
 assert loc['left']==b.stream[max(0,at-130):at] and loc['right']==b.stream[at:at+240]
def main():
 bs={x:Book(D/'inputs'/f'{x}.xml') for x in ['Latin','Greek','English']};outputs={x:Book(ROOT/'assets/xml/antiquities'/x/'book-11.xml') for x in bs}
 ledger=json.loads((D/'LATIN_PHYSICAL_COVERAGE.json').read_text(encoding='utf8'));gl=json.loads((D/'GREEK_PHYSICAL_COVERAGE.json').read_text(encoding='utf8'));adds=json.loads((D/'AUTHORIZED_ADDITIONS.json').read_text(encoding='utf8'))
 raw=outputs['Latin'].raw
 for op in reversed(sorted(adds,key=lambda x:x['offset'])):
  shifted=op['offset']+sum(len(x['addition'].encode()) for x in adds if x['offset']<op['offset']);tag=op['addition'].encode();assert raw[shifted:shifted+len(tag)]==tag;raw=raw[:shifted]+raw[shifted+len(tag):]
 assert raw==bs['Latin'].raw
 for lang in bs:
  before=bs[lang];after=outputs[lang];assert before.stream==after.stream
  assert before.tree.xpath('//@xml:id',namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})==[x for x in after.tree.xpath('//@xml:id',namespaces={'xml':'http://www.w3.org/XML/1998/namespace'}) if x not in {op['id'] for op in adds}]
  assert len(after.tree.xpath('//@xml:id',namespaces={'xml':'http://www.w3.org/XML/1998/namespace'}))==len(set(after.tree.xpath('//@xml:id',namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})))
  for xp in ['//@sameAs','//t:num','//t:note','//t:app','//t:div1/@*','//t:div2/@*']:
   a=before.tree.xpath(xp,namespaces=NS);z=after.tree.xpath(xp,namespaces=NS)
   if a and isinstance(a[0],etree._Element):a=[etree.tostring(e,with_tail=False) for e in a];z=[etree.tostring(e,with_tail=False) for e in z]
   assert a==z,(lang,xp)
  if lang!='Latin':assert before.raw==after.raw
 for lang,fragments in [('Latin',ledger),('Greek',gl)]:
  b=bs[lang];previous=0;outputlocs=[]
  for f in fragments:
   check_loc(b,f['start']);check_loc(b,f['end']);a=f['start']['book_offset'];z=f['end']['book_offset'];assert a==previous and z>a
   assert f['text']==b.stream[a:z];previous=z
   out=dict(occurrence=f.get('occurrence') or f'Greek-XI-{f.get("number")}',start=outputs[lang].locate(a),end=outputs[lang].locate(z) if z<len(b.stream) else outputs[lang].terminal_locator())
   check_loc(outputs[lang],out['start']);check_loc(outputs[lang],out['end']);outputlocs.append(out)
  assert previous==len(b.stream) and ''.join(f['text'] for f in fragments)==b.stream
  save(lang.upper()+'_OUTPUT_LOCATORS.json',outputlocs)
 expected=json.loads((D/'EXPECTED_SELECTIONS.json').read_text(encoding='utf8'));assert len(expected)==347
 for n in range(1,348):
  fs=sorted([f for f in ledger if f.get('number')==n],key=lambda f:f['rank']);assert [f['rank'] for f in fs]==list(range(1,len(fs)+1));assert expected[str(n)]['Latin_primary']==''.join(f['text'] for f in fs)
 sources=[f for f in ledger if f.get('role')];assert len(sources)==2 and all(f['Antiquities_identity'] is False for f in sources)
 assert all(len(expected[str(n)]['primary_occurrences'])==2 for n in [312,326,342]);assert len(expected['72']['primary_occurrences'])==3
 baseline=json.loads((D/'ALL_BASE_FILES.json').read_text(encoding='utf8'));allowed={'assets/xml/antiquities/Latin/book-11.xml','assets/js/renderTei.js','assets/css/tei.css'};changed=[]
 for f in baseline:
  actual=digest((ROOT/f['relative']).read_bytes())
  if actual!=f['sha256']:assert f['relative'] in allowed,f['relative'];changed.append(f['relative'])
 counts=json.loads((D/'EDIT_PLAN.json').read_text())['counts'];assert counts['primary_Latin_fragments']==352 and counts['source_only_fragments']==2
 report=dict(status='PASS',baseline=json.loads((D/'BASELINE.json').read_text())['baseline_commit'],fixtures=fixtures(),Latin_inverse_byte_recovery=True,Greek_inverse_byte_recovery=True,English_byte_identical=True,existing_IDs_sameAs_labels_notes_apparatus_divisions_preserved=True,all_locators_independently_validated=True,Latin_physical_occurrences=len(ledger),Greek_physical_occurrences=len(gl),Latin_physical_stream_sha256=digest(bs['Latin'].stream.encode()),Greek_physical_stream_sha256=digest(bs['Greek'].stream.encode()),full_boundary_whitespace_owned=True,overlap_or_loss=0,canonical_continuation_rank_verified=True,changed_baseline_files=changed,unrelated_baseline_files_unchanged=len(baseline)-len(changed),source_output_hashes={x:dict(source=digest(bs[x].raw),output=digest(outputs[x].raw)) for x in bs},counts=counts)
 save('SOURCE_PROOF.json',report)
 identities=json.loads((D/'IDENTITY_REGISTER.json').read_text(encoding='utf8'))
 for r in identities:r['physical_locator_status']='INDEPENDENT_LXML_TEXT_TAIL_RAW_BYTES_AND_OUTPUT_LOCATORS_VALIDATED'
 save('IDENTITY_REGISTER.json',identities);print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
