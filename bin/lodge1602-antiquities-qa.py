#!/usr/bin/env python3
"""Independent Lodge Antiquities II data verifier; never imports the converter.

ElementTree projection, approved-coordinate replay, literal partition hashes and
independent forward inverse-patch reconstruction are separate mandatory gates.
Report/browser status is explicitly data-only. Use --xml/--metadata/--ledger for
negative tests on disposable copies, never on tracked files.
"""
import argparse,base64,collections,copy,csv,hashlib,io,json,re,sys
from pathlib import Path
import xml.etree.ElementTree as ET

NS='http://www.tei-c.org/ns/1.0'; Q=lambda tag:'{'+NS+'}'+tag
ID='{http://www.w3.org/XML/1998/namespace}id';PREFIX='english-lodge1602-antiquities-book02'
HASH={'original_TCP':'3ca2646644d8c91cf35e8575a6ffbdeb5ecbd378c502f53fd9445d7da7431de6','scholarly_master':'ba43e5c5937a1c8a82a0575886d9747121600b30a6430e50f90fcf1c16772e8b','final_register':'a5b667891b6c5ae35b44b9c7b3923bcc5f886c7ae217493f4a4b0e5af2418863','freeze_manifest':'403fc33a3ac9afab206869066ffc2e07a4f7ead6c18d3dcf134c19569dbf9b7f','certified_extraction':'1d4b522760cd23d58b8bf8ff0475cb6511f57458d5f75fd1d4b0d2294c4afbaa','scholarly_zip':'65a80755ef3095ef9cbfba5482b9869fed5c29b86d6ae785cf6b2fddd6eeb1e7'}
XMLPATH='assets/xml/antiquities/English/Lodge1602/book-02.xml'; METAPATH='assets/data/lodge1602-antiquities/book-02.json'; LEDGERPATH='_docs/lodge1602-antiquities-book02-integration.json'
SOURCEPATH='_docs/lodge1602-antiquities-source/'
EXCLUDED={'note','head','argument','trailer','byline','opener','closer','signed','label'}
def sha(b):return hashlib.sha256(b).hexdigest()
def name(e):return e.tag.rsplit('}',1)[-1]
def readrows(b):return list(csv.DictReader(io.StringIO(b.decode('utf-8')),delimiter='\t'))
def parse(b):
 if b'<!DOCTYPE' in b:raise ValueError('DTD forbidden')
 return ET.fromstring(b)
def source_book(root):return root.find('.//'+Q('div')+'[@type="book"]')
def paths(root):
 result={}
 def visit(el,path):
  result[path]=el;counts=collections.Counter()
  for child in el:
   counts[name(child)]+=1;visit(child,path+'/'+name(child)+'['+str(counts[name(child)])+']')
 visit(root,'/'+name(root)+'[1]');return result

def literal_stream(root):
 """Separate recursive XML text/tail walk; milestones record zero-width offsets."""
 parents={child:parent for parent in root.iter() for child in parent};out=[];offsets={};count=0
 def excluded_ancestor(el):
  p=parents.get(el)
  while p is not None:
   if name(p) in EXCLUDED:return True
   p=parents.get(p)
  return False
 def has_p_ancestor(el):
  p=parents.get(el)
  while p is not None:
   if name(p)=='p':return True
   p=parents.get(p)
  return False
 def emit(text):
  nonlocal count
  if text:out.append(text);count+=len(text)
 def walk(el):
  if name(el) in EXCLUDED:return
  if name(el)=='milestone' and el.get('unit')=='niese':offsets[int(el.get('n'))]=count
  emit(el.text)
  for child in el:
   walk(child);emit(child.tail)
 for p in root.iter(Q('p')):
  if not excluded_ancestor(p) and not has_p_ancestor(p):walk(p)
 return ''.join(out),offsets

def erase_source_apparatus(master):
 # Freeze's certified narrow rule, independent of the production edit planner.
 pattern=rb'<milestone\b[^<>]*\bxml:id="english-lodge1602-antiquities-book02-niese\d+-pilot"[^<>]*/>|<\?lodge-(?:pilot|continuation)\b[^?]*\?>'
 removed=[]
 def replace(m):removed.append((m.start(),m.end()));return b''
 result=re.sub(pattern,replace,master)
 if len(removed)!=359:raise ValueError('Expected exactly 349 scholarly markers and 10 historical PIs')
 return result

def reverse_production(data,ledger,check):
 """Reconstruct by consuming derivative gaps/replacements left-to-right.

Does not use the builder's original-offset application algorithm or XML parser.
Every replacement must match exactly and all original offsets must form one
consistent inverse partition. Repeated zero-width PI removals retain ledger order.
"""
 out=[];cursor=0;masterpos=0;previous_master_end=0
 for i,edit in enumerate(ledger['edits']):
  start,end=edit['derivative_start'],edit['derivative_end_exclusive'];old=base64.b64decode(edit['original_b64'],validate=True);new=base64.b64decode(edit['replacement_b64'],validate=True)
  check(cursor<=start<=end<=len(data),'Inverse patch ordering '+str(i))
  check(end-start==len(new) and data[start:end]==new,'Inverse replacement bytes '+str(i))
  gap=data[cursor:start];out.append(gap);masterpos+=len(gap)
  check(edit['master_start']==masterpos and edit['master_end_exclusive']==masterpos+len(old),'Independent master partition coordinates '+str(i))
  out.append(old);masterpos+=len(old);cursor=end
 out.append(data[cursor:]);result=b''.join(out)
 check(len(result)==ledger['input_byte_length'] and len(data)==ledger['output_byte_length'],'Inverse byte lengths')
 return result

def fingerprint(el,root=True):
 return (el.tag,tuple(sorted(el.attrib.items())),el.text,None if root else el.tail,tuple(fingerprint(c,False) for c in el))

def verify(a):
 assertions=[]
 def check(ok,label):
  if not ok:raise ValueError(label)
  assertions.append(label)
 root=a.repo_root
 master=(root/(SOURCEPATH+'book-02-frozen.xml')).read_bytes();register_bytes=(root/(SOURCEPATH+'book-02-final.tsv')).read_bytes();freeze_bytes=(root/(SOURCEPATH+'book-02-freeze-manifest.json')).read_bytes()
 for kind,b in [('scholarly_master',master),('final_register',register_bytes),('freeze_manifest',freeze_bytes)]:check(sha(b)==HASH[kind],'Exact frozen evidence '+kind)
 data=(a.xml or root/XMLPATH).read_bytes();metadata_bytes=(a.metadata or root/METAPATH).read_bytes();metadata=json.loads(metadata_bytes);ledger=json.loads((a.ledger or root/LEDGERPATH).read_bytes());freeze=json.loads(freeze_bytes);register=readrows(register_bytes)
 check(metadata.get('schema')=='lodge1602-antiquities-adapter-v1' and metadata.get('schema_version')==1,'Versioned adapter schema')
 for key in ['availability','production_xml','authorities','reference_snapshot','source_counts','native_chapters','source_node_aliases','marginal_notes','sections','project_navigation_covers']:check(key in metadata,'Required adapter field '+key)
 check(metadata['authorities']==HASH and ledger['authorities']==HASH,'Independent mandatory provenance hashes')
 check(ledger['schema']=='lodge1602-antiquities-inverse-ledger-v1','Inverse ledger schema')
 check(metadata['book_key']=='2' and metadata['work']=='antiquities' and metadata['source']=='lodge1602','Source-qualified book identity')
 availability=metadata['availability'];check(availability=={'availableBookKeys':['2'],'exactNieseBooks':['2'],'proem_integrated':False,'other_books_integrated':False,'identity_range':[1,349],'whole_section_absences':[],'inherits_other_witness_availability':False},'Book II-only capabilities and independent availability')
 check(metadata['reader_browser_status']=='PENDING_WORKBOT_7B; NOT_TESTED','No fabricated browser certification')
 check(metadata['deferred_observations']['count']==197 and metadata['deferred_observations']['sha256']==freeze['packet_file_sha256']['Lodge1602_Antiquities_BookII_DEFERRED_QUERIES.tsv'],'Deferred observation authority and count')
 check(metadata['historical_confidence_counts']=={'HIGH':333,'MEDIUM':16,'LOW':0},'Historical confidence preserved')
 check(collections.Counter(r['historical_confidence'] or r['confidence'] for r in register)=={'HIGH':333,'MEDIUM':16},'Actual register historical confidence')
 check(metadata['historical_classification_counts']==freeze['historical_classification_counts'],'Historical classifications preserved')
 tree=parse(data);check(tree.tag==Q('TEI'),'TEI namespace/root')
 wrappers=tree.findall('.//'+Q('div1'));check(len(wrappers)==1 and wrappers[0].get(ID)==PREFIX,'Single Lodge book wrapper')
 book=source_book(tree);check(book is not None and book.get('n')=='2','Book II native root')
 check(all(e.get('n')!='3' for e in tree.iter(Q('div')) if e.get('type')=='book'),'No Book III source tree')
 milestones=[e for e in book.iter(Q('milestone')) if e.get('unit')=='niese'];numbers=[int(e.get('n')) for e in milestones]
 check(numbers==list(range(1,350)),'Exactly 349 unique ordered active identities; no 350')
 allids=[e.get(ID) for e in tree.iter() if e.get(ID)];check(len(allids)==len(set(allids)),'All stable XML IDs unique')
 for num,e in zip(numbers,milestones):
  check(e.get(ID)==PREFIX+'-niese'+str(num),'Stable milestone alias '+str(num));check(e.get('cert')==register[num-1]['confidence'].lower(),'Historical marker evidence confidence '+str(num));check(e.get('type')=='lodge-antiquities-certified-niese','Distinct Niese/source marker type '+str(num))
 check(not any(e.get('sameAs') for e in book.iter()),'No unverified paragraph sameAs')
 extraction=erase_source_apparatus(master);check(sha(extraction)==HASH['certified_extraction'],'Certified second-level byte reconstruction')
 original=parse(extraction);source=source_book(original);sourcepaths=paths(original);originalbookpaths={id(e):p for p,e in sourcepaths.items()}
 stream,starts=literal_stream(book);expected_stream,_=literal_stream(source)
 check(len(stream)==132602 and stream==expected_stream,'Exact 132602 literal character-data units and source wording')
 check(sha(stream.encode())=='ed69d4be091b81492a4c326696f1bf06dc70a7747ac6a036350e0f29b72d20ad','Frozen literal stream digest')
 check([starts[n] for n in numbers]==[int(r['whole_book_literal_narrative_offset']) for r in register],'All approved physical literal starts reproduced')
 check(starts[1]==25 and stream[:25].isspace(),'Original 25 pre-first whitespace units')
 sections=metadata['sections'];check([s['niese'] for s in sections]==numbers,'349 adapter identity records')
 for i,(r,s) in enumerate(zip(register,sections)):
  n=i+1;start=starts[n];end=starts[n+1] if n<349 else len(stream);part=stream[start:end]
  check(end>start and s['literal_exclusive_end']==end and s['literal_character_extent']==len(part),'Nonempty approved exclusive extent '+str(n))
  check(sha(part.encode())==s['narrative_fragment_sha256'],'Independent literal section payload '+str(n))
  check(part[:len(s['incipit'])]==s['incipit'] and part[-len(s['tail']):]==s['tail'],'Frozen section incipit/tail '+str(n))
  c=s['source_coordinate']
  for field,value in c.items():check(value==r[field],'Protected frozen coordinate '+str(n)+' '+field)
  check(s['historical_confidence']==(r['historical_confidence'] or r['confidence']) and s['historical_classification']==r['classification'],'Historical judgement retained '+str(n))
  check(s['current_boundary_review_required'] is False and not s['active_editorial_status'].startswith('PROVISIONAL'),'Closed active editorial status '+str(n))
  check(s['rationale']==r['rationale'],'Philological rationale retained '+str(n))
  if s['historical_confidence']=='MEDIUM':check(s['active_editorial_status']=='HUMAN_APPROVED','Sixteen explicit MEDIUM dispositions '+str(n))
  srcnode=sourcepaths[r['extraction_element_path']];text=getattr(srcnode,r['text_slot']) or '';offset=int(r['unicode_offset_in_text_node'])
  check(0<=offset<=len(text) and sha(text.encode())==s['source_node_sha256'],'Original Unicode source node/offset '+str(n))
  raw0=s['source_text_node_extraction_start'];raw1=s['source_text_node_extraction_end_exclusive'];rawtext=extraction[raw0:raw1];check(sha(rawtext)==s['raw_source_text_node_sha256'],'Original raw source text slot '+str(n))
  # Decode only the known original XML character-data slot; never project flattened offsets.
  decoded=''.join(ET.fromstring(b'<slot>'+rawtext+b'</slot>').itertext());check(decoded==text,'Raw and parsed source slot agree '+str(n))
  encoded_prefix=text[:offset].encode('utf-8');rawcut=int(r['extraction_raw_byte_offset'])
  # TCP uses literal UTF8 in these approved slots; reject any unsupported entity prefix.
  prefix=rawtext[:rawcut-raw0];check(''.join(ET.fromstring(b'<slot>'+prefix+b'</slot>').itertext())==text[:offset],'Independent mixed-content byte/Unicode replay '+str(n))
  check(int(r['original_TCP_raw_byte_offset'])==rawcut+267938,'Original TCP/extraction mapping '+str(n))
  rawend=int(register[i+1]['extraction_raw_byte_offset']) if n<349 else 191891
  check(s['extraction_exclusive_end_byte']==rawend and sha(extraction[rawcut:rawend])==s['raw_source_fragment_sha256'],'Exact original section mixed-content byte interval '+str(n))
 check(sum(s['literal_character_extent'] for s in sections)==132577,'Complete non-overlapping ordinary narrative partition')
 required={'printed_chapters':7,'TCP_paragraphs':33,'marginal_notes':151,'TCP_gaps':132,'page_breaks':25,'native_TCP_milestones':149,'literal_character_data_units':132602}
 counts={'printed_chapters':sum(e.get('type')=='chapter' for e in book.iter(Q('div'))),'TCP_paragraphs':len(list(book.iter(Q('p')))),'marginal_notes':sum(e.get('place')=='margin' for e in book.iter(Q('note'))),'TCP_gaps':len(list(book.iter(Q('gap')))),'page_breaks':len(list(book.iter(Q('pb')))),'native_TCP_milestones':sum(e.get('unit')!='niese' for e in book.iter(Q('milestone'))),'literal_character_data_units':len(stream)}
 check(counts==required and metadata['source_counts']==required and ledger['source_counts']==required,'All certified source feature counts')
 # Remove only documented project IDs/markers in a copy and compare EVERY source
 # tag, attribute, text/tail and nested attachment independently of inverse patches.
 aliasids={x['production_id'] for x in metadata['source_node_aliases']}
 # Preserve the Niese markers for this separate structural oracle. Literal
 # offsets alone cannot distinguish a cut before/after a zero-width source note
 # or gap. Replay only marker metadata, then compare the actual mixed-content
 # tree against the immutable master INCLUDING every approved marker position.
 approved_projection=copy.deepcopy(book)
 frozen_book=source_book(parse(master))
 frozen_markers={int(e.get('n')):e for e in frozen_book.iter(Q('milestone')) if e.get('unit')=='niese'}
 for el in approved_projection.iter():
  if el.get(ID) in aliasids:del el.attrib[ID]
  if el.tag==Q('milestone') and el.get('unit')=='niese':
   number=int(el.get('n'));el.attrib.clear();el.attrib.update(frozen_markers[number].attrib)
 check(fingerprint(approved_projection)==fingerprint(frozen_book),'Every approved physical marker placement including zero-width note/gap associations')
 projected=copy.deepcopy(book)
 for el in projected.iter():
  if el.get(ID) in aliasids:del el.attrib[ID]
 for parent in projected.iter():
  for child in list(parent):
   if child.tag==Q('milestone') and child.get('unit')=='niese':
    index=list(parent).index(child)
    if child.tail:
     if index:parent[index-1].tail=(parent[index-1].tail or '')+child.tail
     else:parent.text=(parent.text or '')+child.tail
    parent.remove(child)
 check(fingerprint(projected)==fingerprint(source),'Independent complete native tree/text/attributes/note anchors/typography')
 check(wrappers[0].tail==source.tail and book.tail is None,'Wrapper preserves original book trailing whitespace position')
 originalnodes=[e for e in source.iter()];productionnodes=[e for e in book.iter() if not(e.tag==Q('milestone') and e.get('unit')=='niese')]
 check(len(originalnodes)==len(productionnodes),'All original structural tokens accounted')
 associations=[];productionpaths=paths(tree)
 for alias in metadata['source_node_aliases']:
  pe=productionpaths[alias['production_element_path']];se=sourcepaths[alias['extraction_element_path']]
  check(pe.get(ID)==alias['production_id'] and name(pe)==alias['source_tag'],'Stable source node alias '+alias['production_id'])
  # Original source element raw bytes include all source descendants and attributes.
  raw=extraction[alias['extraction_start_byte']:alias['source_element_end_exclusive']]
  check(sha(raw)==alias['source_element_sha256'],'Native original raw element authority '+alias['production_id'])
  check(originalnodes.index(se)==productionnodes.index(pe),'Original source ordering/attachment '+alias['production_id'])
  check(alias['original_TCP_start_byte']==alias['extraction_start_byte']+267938,'Native original TCP coordinate '+alias['production_id'])
  if alias['source_tag']=='note':
   predecessors=[int(r['number']) for r in register if int(r['extraction_raw_byte_offset'])<=alias['extraction_start_byte']];assoc=predecessors[-1] if predecessors else None
   check(alias['physical_niese_interval']==assoc,'Original marginal note physical interval '+alias['production_id']);associations.append(assoc)
 check(len(associations)==151 and associations.count(None)==1,'151 notes: 150 physical intervals + one pre-II.1 context')
 check(metadata['pre_first_identity_context']['notes']==[PREFIX+'-tcp-note001'] and not metadata['pre_first_identity_context']['note_anchor_relocated'],'Opening note retains its source anchor; no Niese zero')
 check(metadata['marginal_notes']==[x for x in metadata['source_node_aliases'] if x['source_tag']=='note'],'No sidecar note omissions/duplications')
 evidence=metadata['source_evidence_nodes']
 check(collections.Counter(e['source_tag'] for e in evidence)=={'gap':132,'milestone':149},'All source gap/native milestone coordinate records')
 for evidence_node in evidence:
  old=sourcepaths[evidence_node['extraction_element_path']];new=productionpaths[evidence_node['production_element_path']]
  check(name(old)==name(new)==evidence_node['source_tag'] and old.attrib==new.attrib,'Native evidence attributes '+evidence_node['evidence_key'])
  raw=extraction[evidence_node['extraction_start_byte']:evidence_node['extraction_end_exclusive']]
  check(sha(raw)==evidence_node['source_raw_element_sha256'],'Native evidence raw position/hash '+evidence_node['evidence_key'])
  check(evidence_node['original_TCP_start_byte']==evidence_node['extraction_start_byte']+267938,'Native evidence TCP coordinate '+evidence_node['evidence_key'])
  expected_role='TCP_TRANSCRIPTION_GAP_NOT_IDENTITY_OMISSION' if name(old)=='gap' else 'ORIGINAL_TCP_MARKER_NOT_PROJECT_NIESE'
  check(evidence_node['semantic_role']==expected_role,'Source evidence/identity distinction '+evidence_node['evidence_key'])
 for i,chapter in enumerate(source.findall('./'+Q('div')+'[@type="chapter"]'),1):
  check(metadata['native_chapters'][i-1]['source_label']==''.join(chapter.find(Q('head')).itertext()),'Exact original printed chapter label '+str(i))
 contents=metadata['source_contents'];check(contents['source_tag']=='list' and len(list(sourcepaths[contents['extraction_element_path']].iter(Q('item'))))==7,'Original seven-item source contents')
 header=tree.find(Q('teiHeader'));check(header is not None,'Source credit/header provided')
 headerhashes={e.get('type').removeprefix('sha256-'):e.text for e in header.iter(Q('idno')) if e.get('type','').startswith('sha256-')}
 check(headerhashes=={k:h for k,h in HASH.items() if k!='scholarly_zip'},'Exact authority hashes in production header')
 check(any(e.get('target')=='https://creativecommons.org/publicdomain/zero/1.0/' for e in header.iter(Q('licence'))),'Documented TCP licence URI')
 check(len(metadata['native_chapters'])==7 and [x['printed_chapter'] for x in metadata['native_chapters']]==list(range(1,8)),'Seven source-native chapter anchors')
 check(len(metadata['project_navigation_covers'])==95 and collections.Counter(c['scheme'] for c in metadata['project_navigation_covers'])=={'chapter':16,'subchapter':76,'bamberg':3},'Actual project context inventory distinct from seven Lodge chapters')
 for cover in metadata['project_navigation_covers']:check(1<=cover['start_niese']<cover['end_niese_exclusive']<=350 and cover['precision']=='CONTAINING_NIESE_CONTEXT_NOT_NATIVE_CHAPTER_EQUIVALENCE','Qualified context range '+cover['project_boundary_id'])
 qualified=metadata['II284_independent_Lodge_qualification'];check(qualified['source_coordinate']==sections[283]['source_coordinate'] and qualified['whole_section_absent'] is False,'II.284 Lodge cut independent of qualified traditional boundary')
 # Confirm protected comparison versions from the actual isolated reference files.
 for relative,h in metadata['reference_snapshot']['files'].items():check(sha((root/relative).read_bytes())==h,'Coherent current reference snapshot '+relative)
 identity_sets={}
 for lang in ['Greek','Latin','English']:
  ref=parse((root/('assets/xml/antiquities/'+lang+'/book-02.xml')).read_bytes());ids=[]
  for el in ref.iter():
   if el.tag==Q('milestone') and el.get('unit')=='niese':ids.append(int(el.get('n')))
   elif lang!='English' and el.tag==Q('num'):
    digits=re.findall(r'\d+',''.join(el.itertext()))
    if digits:ids.append(int(digits[-1]))
  check(ids==numbers,'Cross-language current Book II identity set '+lang);identity_sets[lang]=len(ids)
 restored=reverse_production(data,ledger,check)
 check(restored==master and sha(restored)==HASH['scholarly_master'],'Byte-for-byte production inverse restores frozen master')
 check(erase_source_apparatus(restored)==extraction,'Second independent exact source extraction reconstruction')
 check(sha(data)==metadata['production_xml']['sha256']==ledger['derivative_sha256'],'Production derivative SHA-256 binding')
 check(sha(metadata_bytes)==ledger['metadata_sha256'],'Sidecar SHA-256 binding')
 # Each production marker's declared byte position must identify its actual tag.
 for s in sections:
  pos=s['production_marker_byte'];check(data[pos:].startswith(b'<milestone ') and ('xml:id="'+s['marker_id']+'"').encode() in data[pos:data.index(b'>',pos)+1],'Actual production marker byte locator '+str(s['niese']))
 check(ledger['source_node_aliases']==metadata['source_node_aliases'],'Exact source alias/ledger consistency')
 check(metadata['book_end']==freeze['end_boundaries'],'Frozen Book II end certificate carried intact')
 check(sections[-1]['source_coordinate']['original_TCP_raw_byte_offset']=='459147' and sections[-1]['extraction_exclusive_end_byte']==191891,'II.349 reaches native Book II root end')
 check(extraction[108:191891].startswith(b'<div ') and extraction[191891:191907].strip().startswith(b'</body>'),'Correct source book root exclusion of following works')
 if a.original_source:
  original_bytes=a.original_source.read_bytes();check(sha(original_bytes)==HASH['original_TCP'],'Immutable original A04680 hash')
  check(original_bytes[268046:459829]==extraction[108:191891],'Original TCP exact Book II root region')
  check(original_bytes[459845:].startswith(b'<div ') and b'n="3"' in original_bytes[459845:459930],'Book III begins at 459845 and remains excluded')
 if a.authority_dir:
  for filename,kind in [('CERTIFIED_SOURCE_BOOK_II.xml','certified_extraction'),('Lodge1602_Antiquities_BookII_FINAL_FROZEN_SCHOLARLY_PACKET.zip','scholarly_zip')]:check(sha((a.authority_dir/filename).read_bytes())==HASH[kind],'External mandatory authority '+kind)
 if a.restore_dir:
  a.restore_dir.mkdir(parents=True,exist_ok=True);(a.restore_dir/'restored-frozen-master.xml').write_bytes(restored);(a.restore_dir/'restored-certified-extraction.xml').write_bytes(extraction)
 return {'status':'PASS','certification_scope':'DATA_LAYER_ONLY; browser/renderer NOT_RUN','assertions_passed':len(assertions),'identity_coverage':349,'identity_sets':identity_sets,'source_counts':counts,'opening_note_count':1,'notes_within_Niese_intervals':150,'literal_stream_sha256':sha(stream.encode()),'historical_confidence':metadata['historical_confidence_counts'],'all_sixteen_MEDIUM_human_approved':True,'deferred_queries':197,'exact_production_to_scholarly_master':{'sha256':sha(restored),'byte_identical':True},'exact_scholarly_master_to_extraction':{'sha256':sha(extraction),'byte_identical':True},'source_tree_markup_notes_and_order_independently_equal':True,'all349_source_coordinates_and_individual_partitions_valid':True,'derivative_sha256':sha(data),'metadata_sha256':sha(metadata_bytes),'native_TCP_milestones':149,'BookIII_excluded':True,'no_II350':True}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo-root',type=Path,required=True);ap.add_argument('--xml',type=Path);ap.add_argument('--metadata',type=Path);ap.add_argument('--ledger',type=Path);ap.add_argument('--original-source',type=Path);ap.add_argument('--authority-dir',type=Path);ap.add_argument('--restore-dir',type=Path);ap.add_argument('--report',type=Path);a=ap.parse_args()
 try:report=verify(a)
 except Exception as e:
  report={'status':'FAIL','reason':str(e),'certification_scope':'DATA_LAYER_ONLY; browser/renderer NOT_RUN'}
  if a.report:a.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
  print(json.dumps(report,ensure_ascii=False));return 1
 if a.report:a.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps(report,ensure_ascii=False));return 0
if __name__=='__main__':sys.exit(main())
