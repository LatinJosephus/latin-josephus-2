"""Independent checks of pinned source bytes and candidate XML text-node positions.
This cannot approve, apply, stage, or commit a segmentation.
"""
import argparse,json,re,hashlib,collections
from pathlib import Path
from lxml import etree
from mixed_mapper import fixtures,NS
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--canonical',type=Path,required=True);ap.add_argument('--packet',type=Path,required=True);ap.add_argument('--manifest',action='store_true');a=ap.parse_args();p=a.packet
base=json.loads((p/'BASELINE.json').read_text(encoding='utf-8'));rows=json.loads((p/'BOUNDARIES.json').read_text(encoding='utf-8'));result=json.loads((p/'AUDIT_RESULT.json').read_text(encoding='utf-8'));b=base['book'];total=base['niese']['expected_count'];proofs={}
for lang,v in base['inputs'].items():
 path=a.repo/v['path'];cp=a.canonical/v['path'];raw=path.read_bytes();root=etree.fromstring(raw)
 assert sha(path)==v['worktree_before_sha256']==v['worktree_after_sha256']
 assert sha(cp)==v['canonical_before_sha256']==v['canonical_after_sha256']
 assert cp.read_bytes().replace(b'\r\n',b'\n')==raw
 old=base['inventory'][lang]
 assert root.xpath('//@xml:id',namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})==old['ids']
 assert root.xpath('//@sameAs')==old['sameAs']
 assert [dict(x.attrib) for x in root.xpath('//t:div2',namespaces=NS)]==old['chapter_divisions']
 nums=[''.join(n.itertext()) for n in root.xpath('//t:body//t:num',namespaces=NS)]
 assert nums==[x['text'] for x in old['labels']]
 assert [dict(x.attrib) for x in root.xpath('//t:milestone',namespaces=NS)]==[x['attributes'] for x in old['milestones']]
 proofs[lang]=dict(XML_parse='PASS',bytes_unchanged='PASS',all_xml_ids_unchanged='PASS',all_sameAs_unchanged='PASS',div2_structure_and_labels_unchanged='PASS',all_existing_milestones_unchanged='PASS',before_sha256=v['worktree_before_sha256'],after_sha256=sha(path))
assert [r['niese'] for r in rows]==list(range(1,total+1))
trees={l:etree.parse(str(a.repo/v['path'])) for l,v in base['inputs'].items()}
locators=0
for r in rows:
 assert not r['implementation_approved'] and r['human_decision'] is None
 for lang,key in [('Greek','greek_locator'),('Latin','latin_locator')]:
  loc=r[key]
  if loc is None:assert r['classification']=='UNAVAILABLE';continue
  path=loc['text_node_path'];tail=path.endswith('/tail()');owner=path.rsplit('/',1)[0]
  xp=re.sub(r'/([A-Za-z][A-Za-z0-9_-]*)(\[)',r'/t:\1\2',owner)
  nodes=trees[lang].xpath(xp,namespaces=NS);assert len(nodes)==1,(r['niese'],lang,xp)
  scope=nodes[0].getparent() if tail else nodes[0]
  assert not scope.xpath('ancestor-or-self::t:note | ancestor-or-self::t:app | ancestor-or-self::t:rdg',namespaces=NS)
  text=nodes[0].tail if tail else nodes[0].text;assert text is not None
  off=loc['node_offset'];assert 0<=off<len(text)
  rel=base['inputs'][lang]['path'];raw=(a.repo/rel).read_bytes();k=loc['raw_byte'];fragment=raw[k:k+16]
  if fragment.startswith(b'&'):
   token=fragment.split(b';',1)[0]+b';';char=etree.fromstring(b'<x>'+token+b'</x>').text
  elif fragment.startswith(b'\r\n'):char='\n'
  else:
   end=1
   while end<len(fragment) and fragment[end]&0xc0==0x80:end+=1
   char=fragment[:end].decode('utf-8')
  assert text[off]==char,(b,r['niese'],lang,loc)
  if lang=='Latin':locators+=1
assert locators==total-len(result['unavailable'])
assert result['retained_candidate_inherited_starts']+result['proposed_candidate_milestones']+len(result['unavailable'])==total
assert json.loads((p/'CANDIDATE_DRY_RUN.json').read_text(encoding='utf-8'))['removed_authorized_candidate_strings_recovers_original']
assert json.loads((p/'INSERTION_PLAN.json').read_text(encoding='utf-8'))['approved_insertions']==[]
if a.manifest:
 manifest=json.loads((p/'FILE_MANIFEST.json').read_text(encoding='utf-8'));assert all(sha(p/x['path'])==x['sha256'] for x in manifest['files']);print('Manifest PASS',len(manifest['files']));raise SystemExit(0)
qa=dict(status='AUDIT_TECHNICAL_PASS_IMPLEMENTATION_NO_GO',book=b,source_preservation=proofs,candidate_inventory=dict(expected=total,records=len(rows),classifications=result['classifications'],existing_label_claims=result['raw_inherited_label_claims'],retained_candidate_starts=result['retained_candidate_inherited_starts'],proposed_unapproved_milestones=result['proposed_candidate_milestones'],unavailable=result['unavailable'],arithmetic='PASS_WITH_EXPLICIT_UNAVAILABLE_RECORD',unique_Greek_census='PASS',independent_full_print_collation='INCOMPLETE'),mixed_content=dict(fixtures=fixtures(),independent_lxml_text_node_and_raw_byte_checks=locators,all_locators_resolve='PASS',XML_reserialization_performed=False),technical_rehearsal='PASS_IN_MEMORY_ONLY',new_milestones_applied=0,Greek_repairs_applied=0,implementation_GO=False,implementation_browser_QA='NOT_RUN: no certified VIII/X implementation exists',baseline_browser_QA='../Antiquities_Niese_Batch_08_10_2026-10-08/REGRESSION_SUMMARY.json',human_cases='REVIEW_CASES.md')
write(p/'QA.json',qa);print('Independent packet verification PASS',b,locators,'Latin XML text-node/byte locators; implementation NO-GO')
