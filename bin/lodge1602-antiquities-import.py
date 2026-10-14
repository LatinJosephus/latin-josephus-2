#!/usr/bin/env python3
"""Deterministic frozen Lodge Antiquities production adapter. No source serialization.

Requires the complete verified scholarly packet and original TCP input. Writes only
generated data/evidence paths under --output-root. The verifier is independent.
"""
import argparse,base64,csv,hashlib,json,re,zipfile,collections
from pathlib import Path
from xml.parsers import expat
from xml.sax.saxutils import escape,quoteattr
import xml.etree.ElementTree as ET

VERSION='lodge1602-antiquities-adapter-v1'
PREFIX='english-lodge1602-antiquities-book02'
NS='http://www.tei-c.org/ns/1.0'
XMLID='{http://www.w3.org/XML/1998/namespace}id'
AUTH={
 'original_TCP':'3ca2646644d8c91cf35e8575a6ffbdeb5ecbd378c502f53fd9445d7da7431de6',
 'scholarly_master':'ba43e5c5937a1c8a82a0575886d9747121600b30a6430e50f90fcf1c16772e8b',
 'final_register':'a5b667891b6c5ae35b44b9c7b3923bcc5f886c7ae217493f4a4b0e5af2418863',
 'freeze_manifest':'403fc33a3ac9afab206869066ffc2e07a4f7ead6c18d3dcf134c19569dbf9b7f',
 'certified_extraction':'1d4b522760cd23d58b8bf8ff0475cb6511f57458d5f75fd1d4b0d2294c4afbaa',
 'scholarly_zip':'65a80755ef3095ef9cbfba5482b9869fed5c29b86d6ae785cf6b2fddd6eeb1e7'}
FILES={'scholarly_master':'Lodge1602_Antiquities_BookII_FINAL_FROZEN.xml','final_register':'Lodge1602_Antiquities_BookII_NIESE_349_FINAL.tsv','freeze_manifest':'Lodge1602_Antiquities_BookII_FINAL_FREEZE_MANIFEST.json','certified_extraction':'CERTIFIED_SOURCE_BOOK_II.xml','scholarly_zip':'Lodge1602_Antiquities_BookII_FINAL_FROZEN_SCHOLARLY_PACKET.zip'}
TARGETS={'xml':'assets/xml/antiquities/English/Lodge1602/book-02.xml','metadata':'assets/data/lodge1602-antiquities/book-02.json','master':'_docs/lodge1602-antiquities-source/book-02-frozen.xml','register':'_docs/lodge1602-antiquities-source/book-02-final.tsv','freeze':'_docs/lodge1602-antiquities-source/book-02-freeze-manifest.json','ledger':'_docs/lodge1602-antiquities-book02-integration.json'}
COUNTS={'literal_character_data_units':132602,'printed_chapters':7,'TCP_paragraphs':33,'marginal_notes':151,'TCP_gaps':132,'page_breaks':25,'native_TCP_milestones':149}
LO,HI,BOOKKEY=1,349,'2'
BATCH=False
WORK='antiquities'
BATCH_SCOPE={'proem':(1,26,'preface'),'book-01':(27,346,'1'),'book-03':(1,322,'3'),'book-04':(1,331,'4'),'book-05':(1,362,'5'),'book-06':(1,378,'6'),'book-07':(1,394,'7'),'book-08':(1,420,'8'),'book-09':(1,291,'9'),'book-10':(1,281,'10'),'book-11':(1,347,'11'),'book-12':(1,434,'12'),'book-13':(1,433,'13'),'book-14':(1,491,'14'),'book-15':(1,425,'15'),'book-16':(1,404,'16'),'book-17':(1,355,'17'),'book-18':(1,379,'18'),'book-19':(1,366,'19'),'book-20':(1,268,'20')}
BATCH_ZIP_SHA='21ee32b9f6d5e375ced2839e9cacc9b2e77619a93ddd105fb83280c22282c783'
EXCLUDED={'note','head','argument','trailer','byline','opener','closer','signed','label'}
def sha(b):return hashlib.sha256(b).hexdigest()
def jsonbytes(d):return (json.dumps(d,indent=2,ensure_ascii=False,sort_keys=True)+'\n').encode('utf-8')
def require(ok,msg):
 if not ok:raise ValueError(msg)
def rows(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def verified_inputs(authority,original):
 paths={k:authority/n for k,n in FILES.items()};paths['original_TCP']=original
 for k,p in paths.items():require(sha(p.read_bytes())==AUTH[k],'Mandatory scholarly authority mismatch: '+k)
 checked=[]
 for line in (authority/'SHA256SUMS.txt').read_text(encoding='utf-8-sig').splitlines():
  if not line.strip():continue
  h,n=line.split(maxsplit=1);n=n.lstrip('*');p=authority/n
  require(p.resolve().is_relative_to(authority.resolve()),'Unsafe packet member')
  require(sha(p.read_bytes())==h,'Frozen packet checksum mismatch: '+n);checked.append(n)
 return paths,checked

def tag_end(data,start):
 quote=None
 for i in range(start,len(data)):
  c=data[i]
  if quote is not None:
   if c==quote:quote=None
  elif c in (34,39):quote=c
  elif c==62:return i+1
 raise ValueError('Unclosed tag')

def index_xml(data):
 """Parser supplies byte coordinates; quote-aware scanner bounds individual tags."""
 parser=expat.ParserCreate();nodes=[];stack=[];pis=[]
 def start(name,attrs):
  pos=parser.CurrentByteIndex;end=tag_end(data,pos)
  parent=stack[-1] if stack else None
  counters=parent['counters'] if parent else {}
  number=counters.get(name,0)+1;counters[name]=number
  path=(parent['path'] if parent else '')+'/'+name+'['+str(number)+']'
  node={'tag':name,'attrs':attrs,'start':pos,'start_end':end,'path':path,'parent':parent,'counters':{},'children':[],'empty':data[pos:end].rstrip().endswith(b'/>')}
  if parent:parent['children'].append(node)
  nodes.append(node);stack.append(node)
 def end(name):
  node=stack.pop();node['end']=node['start_end'] if node['empty'] else tag_end(data,parser.CurrentByteIndex)
 def pi(target,value):
  pos=parser.CurrentByteIndex;end=data.index(b'?>',pos)+2;pis.append({'target':target,'start':pos,'end':end})
 parser.StartElementHandler=start;parser.EndElementHandler=end;parser.ProcessingInstructionHandler=pi
 parser.ExternalEntityRefHandler=lambda *a:0
 parser.StartDoctypeDeclHandler=lambda *a:(_ for _ in ()).throw(ValueError('DTD forbidden'))
 parser.Parse(data,True);return nodes,pis

def reference_snapshot(root,base):
 filename='preface.xml' if BOOKKEY=='preface' else 'book-'+BOOKKEY.zfill(2)+'.xml'
 if WORK=='contra-apionem':return {'base_commit':base,'files':{p:sha((root/p).read_bytes()) for p in ['assets/xml/contra-apionem/'+lang+'/'+filename for lang in ['Greek','Latin','English']]}}
 paths=['assets/xml/antiquities/'+lang+'/'+filename for lang in ['Greek','Latin','English']]+['assets/xml/antiquities/structure.xml','assets/js/renderTei.js']
 return {'base_commit':base,'files':{p:sha((root/p).read_bytes()) for p in paths}}
def registry_records(root):
 if WORK=='contra-apionem':
  # Existing Apion chapters are project divisions, independent of Lodge's p.
  data=(root/('assets/xml/contra-apionem/Latin/book-'+BOOKKEY.zfill(2)+'.xml')).read_bytes()
  nodes,_=index_xml(data);current=1;chapters=[]
  for n in nodes:
   identity=re.search(r'-num(\d+)$',n['attrs'].get('xml:id',''))
   if identity:current=int(identity[1])
   if n['tag']=='milestone' and n['attrs'].get('unit')=='chapter':
    paragraph=n['parent']
    while paragraph is not None and paragraph['tag']!='p':paragraph=paragraph['parent']
    before=data[paragraph['start_end']:n['start']] if paragraph else b''
    before=re.sub(rb'<num\b[^>]*>.*?</num>',b'',before,flags=re.S)
    mid=bool(re.sub(rb'<[^>]*>',b'',before).strip())
    chapters.append((int(n['attrs']['n']),current,mid))
  return [{'project_boundary_id':'apion'+BOOKKEY+'-chapter'+str(ch),'scheme':'chapter','chapter':ch,'start_niese':start,'end_niese_exclusive':chapters[i+1][1]+int(chapters[i+1][2]) if i+1<len(chapters) else HI+1,'precision':'CONTAINING_NIESE_CONTEXT_NOT_NATIVE_CHAPTER_EQUIVALENCE'} for i,(ch,start,mid) in enumerate(chapters)]
 tree=ET.fromstring((root/'assets/xml/antiquities/structure.xml').read_bytes())
 q=lambda s:'{'+NS+'}'+s
 def fields(el):
  d={}
  for f in el.findall(q('f')):
   child=next(iter(f),None)
   if child is not None:d[f.get('name')]=fields(child) if child.tag==q('fs') else ''.join(child.itertext()).strip()
  return d
 allrows={el.get(XMLID):fields(el.find(q('fs'))) for el in tree.iter(q('item')) if el.get(XMLID) and el.find(q('fs')) is not None}
 selected=[]
 target_book=BOOKKEY
 for key,d in allrows.items():
  if d.get('book')!=target_book or d.get('scheme') not in ['chapter','subchapter','bamberg']:continue
  if 'canonical-niese' not in d:continue
  start=int(d['canonical-niese']);ending=allrows.get(d.get('end'),{})
  if BATCH and not LO<=start<=HI:continue
  require(d.get('end')=='BOOK_END' or d.get('end') in allrows,'Unresolved structural endpoint: '+str(key))
  end=int(ending['canonical-niese']) if ending.get('book')==target_book and ending.get('canonical-niese') else HI+1
  if BATCH:end=min(end,HI+1)
  require(LO<=start<=end<=HI+1 and (BATCH or start<end),'Unsupported traditional boundary pair: '+str(key))
  # Mid-identity or qualified endpoints give containing context, never a word-level equality.
  end_exact=(ending.get('verification-status')=='CONFIRMED_NIESE_START' or end==HI+1) and end>start
  selected.append({'project_boundary_id':key,'scheme':d['scheme'],'start_niese':start,'end_niese_exclusive':end if end_exact else min(HI+1,end+1),'precision':'CONTAINING_NIESE_CONTEXT_NOT_NATIVE_CHAPTER_EQUIVALENCE','start_verification':d.get('verification-status'),'end_boundary_id':d.get('end'),'end_verification':ending.get('verification-status'),'source_qualified_locators':{lang:d.get(lang,{}) for lang in ['Greek','Latin','English']},'qualified':d.get('verification-status')!='CONFIRMED_NIESE_START' or not end_exact})
 if not BATCH:require(len(selected)==95,'Traditional Book II context inventory changed: expected 95 records')
 return selected

def configure_batch(a):
 global BATCH,LO,HI,BOOKKEY,PREFIX,AUTH,FILES,TARGETS,COUNTS
 BATCH=True;LO,HI,BOOKKEY=BATCH_SCOPE[a.unit]
 basename='preface' if BOOKKEY=='preface' else 'book-'+BOOKKEY.zfill(2)
 PREFIX='english-lodge1602-antiquities-'+('preface' if BOOKKEY=='preface' else 'book'+BOOKKEY.zfill(2))
 new_batch=int(BOOKKEY) >= 6 if BOOKKEY!='preface' else False
 zp=a.authority_dir/('Lodge1602_Antiquities_BATCH_VI_X_FINAL_FROZEN_SCHOLARLY_PACKET.zip' if new_batch else 'Lodge1602_Antiquities_BATCH_I_III_V_FINAL_FROZEN_SCHOLARLY_PACKET.zip')
 if BOOKKEY!='preface' and int(BOOKKEY)>=11:zp=a.authority_dir/'Lodge1602_Antiquities_BATCH_XI_XV_FINAL_FROZEN_SCHOLARLY_PACKET.zip'
 if BOOKKEY!='preface' and int(BOOKKEY)>=16:zp=a.authority_dir/'Lodge1602_Antiquities_BATCH_XVI_XX_FINAL_FROZEN_SCHOLARLY_PACKET.zip'
 require(sha(zp.read_bytes())==('27c84528e17c8eebf8e8a320ee147a9e2b1e9f438cbf65bfce061e299c596b29' if BOOKKEY!='preface' and int(BOOKKEY)>=16 else '8d48df45df82a91e1667fa72c60ac44174b53c0cb0b9182c92e65fadaa6315e1' if BOOKKEY!='preface' and int(BOOKKEY)>=11 else '804662293e12910f00e955835217ffd9d504eaef700dbf37a1795310dc91b146' if new_batch else BATCH_ZIP_SHA),'Frozen batch ZIP mismatch')
 with zipfile.ZipFile(zp) as z:
  for name in ['FINAL_FREEZE_MANIFEST.json',a.unit+'/SEGMENTED_FINAL.xml',a.unit+'/NIESE_BOUNDARY_REGISTER.tsv',a.unit+'/CERTIFIED_SOURCE.xml',a.unit+'/EXTRACTION_RECIPE.json',a.unit+'/SOURCE_TEXT_NODE_MAP.json',a.unit+'/BOUNDARIES.json',a.unit+'/INDEPENDENT_QA.json','HUMAN_ADJUDICATION_LOG.json']:
   require(z.read(name)==(a.authority_dir/name).read_bytes(),'Frozen ZIP/member mismatch: '+name)
 freeze=json.loads((a.authority_dir/'FINAL_FREEZE_MANIFEST.json').read_bytes());require(freeze['status']=='FINAL_SCHOLARLY_FREEZE_CERTIFIED' and freeze['outstanding_adjudications']==0,'Batch freeze not closed')
 qa=json.loads((a.authority_dir/a.unit/'INDEPENDENT_QA.json').read_bytes());require(qa['status']=='PASS' and qa['identity_count']==HI-LO+1,'Frozen unit QA')
 FILES={'scholarly_master':a.unit+'/SEGMENTED_FINAL.xml','final_register':a.unit+'/NIESE_BOUNDARY_REGISTER.tsv','freeze_manifest':'FINAL_FREEZE_MANIFEST.json','certified_extraction':a.unit+'/CERTIFIED_SOURCE.xml','scholarly_zip':zp.name}
 AUTH={k:sha((a.authority_dir/n).read_bytes()) for k,n in FILES.items()};AUTH['original_TCP']='3ca2646644d8c91cf35e8575a6ffbdeb5ecbd378c502f53fd9445d7da7431de6'
 TARGETS={'xml':'assets/xml/antiquities/English/Lodge1602/'+basename+'.xml','metadata':'assets/data/lodge1602-antiquities/'+basename+'.json','master':'_docs/lodge1602-antiquities-source/'+basename+'-frozen.xml','register':'_docs/lodge1602-antiquities-source/'+basename+'-final.tsv','freeze':'_docs/lodge1602-antiquities-source/'+basename+'-freeze-manifest.json','ledger':'_docs/lodge1602-antiquities-'+basename.replace('-','')+'-integration.json'}
 c=qa['source_counts'];COUNTS={'literal_character_data_units':qa['literal_characters'],'printed_chapters':sum(n['attrs'].get('type')=='chapter' for n in index_xml((a.authority_dir/a.unit/'CERTIFIED_SOURCE.xml').read_bytes())[0]),'TCP_paragraphs':c.get('p',0),'marginal_notes':c.get('note',0),'TCP_gaps':c.get('gap',0),'page_breaks':c.get('pb',0),'native_TCP_milestones':c.get('milestone',0)}
 return freeze

def batch_partition(a,register,source):
 node_map=json.loads((a.authority_dir/a.unit/'SOURCE_TEXT_NODE_MAP.json').read_bytes())
 lookup={(n['owner_extraction_xpath'],n['slot']):n for n in node_map['nodes']}
 result=[]
 for r in register:
  n=lookup[(r['extraction_element_path'],r['text_slot'])];x,y=n['extraction_raw_start'],n['extraction_raw_end']
  result.append({'literal_exclusive_end':r['literal_exclusive_end'],'source_parsed_text_node_sha256':sha(n['text'].encode()),'source_raw_text_node_sha256':sha(source[x:y]),'source_text_node_extraction_start':x,'source_text_node_extraction_end_exclusive':y,'narrative_fragment_sha256':r['narrative_fragment_sha256'],'extraction_exclusive_end_byte':r['extraction_exclusive_end_byte'],'raw_source_XML_fragment_sha256':r['raw_fragment_sha256'],'exact_Lodge_incipit':r['english_incipit'][:min(len(r['english_incipit']),int(r['literal_characters']))],'exact_Lodge_tail':r['exact_Lodge_tail'],'active_editorial_status':'HUMAN_APPROVED' if r['editorial_status']=='HUMAN_APPROVED' else 'FINAL_HIGH_ACCEPTED_UNDER_ESTABLISHED_WORKFLOW','correspondence_qualification':r['classification']})
 return result

def configure_apion(a):
 global BATCH,WORK,LO,HI,BOOKKEY,PREFIX,AUTH,FILES,TARGETS,COUNTS
 BATCH=True;WORK='contra-apionem';LO=1;BOOKKEY=str(int(a.unit[-2:]));HI=320 if BOOKKEY=='1' else 296
 PREFIX='english-lodge1602-apion'+BOOKKEY
 zp=a.authority_dir/'Lodge1602_ContraApionem_FINAL_FROZEN_SCHOLARLY_PACKET.zip'
 require(sha(zp.read_bytes())=='90aeaaa6b0cc9f6f3c1a5c3c92f167e729df91f04b33184b2d0fa21b7ec4247f','Frozen Apion ZIP mismatch')
 with zipfile.ZipFile(zp) as z:
  for name in ['FINAL_FREEZE_MANIFEST.json',a.unit+'/SEGMENTED_FINAL.xml',a.unit+'/NIESE_BOUNDARY_REGISTER.tsv',a.unit+'/CERTIFIED_SOURCE.xml',a.unit+'/EXTRACTION_RECIPE.json',a.unit+'/SOURCE_TEXT_NODE_MAP.json','HUMAN_ADJUDICATION_LOG.json']:
   require(z.read(name)==(a.authority_dir/name).read_bytes(),'Frozen ZIP/member mismatch: '+name)
 freeze=json.loads((a.authority_dir/'FINAL_FREEZE_MANIFEST.json').read_bytes());require(freeze['status']=='FINAL_SCHOLARLY_FREEZE_CERTIFIED' and freeze['outstanding_adjudications']==0,'Apion freeze not closed')
 qa=json.loads((a.authority_dir/a.unit/'INDEPENDENT_QA.json').read_bytes());require(qa['status']=='PASS' and qa['identity_count']==HI,'Frozen Apion QA')
 FILES={'scholarly_master':a.unit+'/SEGMENTED_FINAL.xml','final_register':a.unit+'/NIESE_BOUNDARY_REGISTER.tsv','freeze_manifest':'FINAL_FREEZE_MANIFEST.json','certified_extraction':a.unit+'/CERTIFIED_SOURCE.xml','scholarly_zip':zp.name}
 AUTH={k:sha((a.authority_dir/n).read_bytes()) for k,n in FILES.items()};AUTH['original_TCP']='3ca2646644d8c91cf35e8575a6ffbdeb5ecbd378c502f53fd9445d7da7431de6'
 TARGETS={'xml':'assets/xml/contra-apionem/English/Lodge1602/'+a.unit+'.xml','metadata':'assets/data/lodge1602-contra-apionem/'+a.unit+'.json','master':'_docs/lodge1602-contra-apionem-source/'+a.unit+'-frozen.xml','register':'_docs/lodge1602-contra-apionem-source/'+a.unit+'-final.tsv','freeze':'_docs/lodge1602-contra-apionem-source/'+a.unit+'-freeze-manifest.json','ledger':'_docs/lodge1602-contra-apionem-'+a.unit.replace('-','')+'-integration.json'}
 counts=qa['source_counts'];COUNTS={'literal_character_data_units':qa['literal_characters'],'printed_chapters':0,'TCP_paragraphs':counts['p'],'marginal_notes':counts['note'],'TCP_gaps':counts['gap'],'page_breaks':counts['pb'],'native_TCP_milestones':counts['milestone']}
 return freeze

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--authority-dir',type=Path,required=True);ap.add_argument('--original-source',type=Path,required=True);ap.add_argument('--reference-root',type=Path,required=True);ap.add_argument('--base-commit',required=True);ap.add_argument('--output-root',type=Path,required=True);ap.add_argument('--ledger-copy',type=Path)
 ap.add_argument('--work',choices=['antiquities','contra-apionem'],default='antiquities');ap.add_argument('--unit',choices=list(BATCH_SCOPE)+['book-02']);a=ap.parse_args();
 batchfreeze=configure_apion(a) if a.work=='contra-apionem' else configure_batch(a) if a.unit else None
 require(not a.output_root.resolve().is_relative_to(a.authority_dir.resolve()),'Never write into the frozen authority directory');paths,checked=verified_inputs(a.authority_dir,a.original_source)
 master=paths['scholarly_master'].read_bytes();source=paths['certified_extraction'].read_bytes();register=rows(paths['final_register']);partition=batch_partition(a,register,source) if BATCH else rows(a.authority_dir/'Lodge1602_Antiquities_BookII_SECTION_PARTITION.tsv')
 require([int(r['number']) for r in register]==list(range(LO,HI+1)),'Register identity set')
 freeze=json.loads(paths['freeze_manifest'].read_bytes());require(freeze.get('outstanding_adjudications' if BATCH else 'current_boundary_decisions_outstanding')==0,'Freeze not closed')
 if BATCH:
  freeze={**freeze,'historical_confidence_counts':{**{'LOW':0},**dict(collections.Counter(r['confidence'] for r in register))},'historical_classification_counts':dict(collections.Counter(r['classification'] for r in register)),'source_coordinate_convention':'Original UTF8 TCP and extraction bytes; exclusive endpoints. Unicode text/tail offsets are independent. Piecewise source-span mapping is retained.','end_boundaries':{'last_identity':HI,'source_book_root_exclusive_TCP_byte':int(register[-1]['original_TCP_exclusive_end_byte']),'extraction_exclusive_end_byte':int(register[-1]['extraction_exclusive_end_byte'])}}
 absences=[]
 if BATCH:
  human=json.loads((a.authority_dir/'HUMAN_ADJUDICATION_LOG.json').read_bytes())
  for r in register:
   if int(r['literal_characters'])!=0:
    require(int(r['literal_characters'])>0,'Invalid section extent');continue
   if a.unit=='book-14':
    n=int(r['number']);tcp=2738736 if 218<=n<=223 else 2741178 if 229<=n<=264 else None
    require(tcp is not None and r['classification']=='NO_SEPARATE_COUNTERPART' and r['confidence']=='LOW' and r['editorial_status']=='HUMAN_APPROVED','Unapproved empty Lodge interval')
    require(int(r['original_TCP_raw_byte_offset'])==int(r['original_TCP_exclusive_end_byte'])==tcp,'Approved Book XIV empty source coordinate')
    group=next(x for x in human['records'] if r['identity'] in x.get('affected_identities',[]))
    member=next(x for x in group['individual_records'] if x['identity']==r['identity'])
    require(group['status']==member['status']=='HUMAN_APPROVED' and group['TCP']==tcp and group['approved_zero_length'] and group['absence_treatment']=='DOCUMENTARY_COLLECTION_ABRIDGED' and sha((a.authority_dir/'HUMAN_ADJUDICATION_LOG.json').read_bytes())==freeze['human_log_sha256'],'Frozen explicit collective empty-interval authorization')
    require(member['approved_coordinate']['original_TCP_raw_byte_offset']==member['approved_coordinate']['original_TCP_exclusive_end_byte']==tcp,'Frozen individual empty-interval authorization')
    absences.append({'niese':n,'identity':r['identity'],'classification':'NO_SEPARATE_COUNTERPART','absence_treatment':'DOCUMENTARY_COLLECTION_ABRIDGED','group_adjudication_id':group['adjudication_id'],'group_start_niese':min(group['numbers']),'group_end_niese':max(group['numbers']),'editorial_status':'HUMAN_APPROVED','original_TCP_start_byte':tcp,'original_TCP_end_exclusive':tcp,'frozen_human_log_sha256':freeze['human_log_sha256'],'notice':'No separate corresponding passage in Lodge (1602); documentary collection abbreviated.'})
   else:
    require(a.unit=='book-10' and r['identity']=='X.238' and r['classification']=='NO_SEPARATE_COUNTERPART' and r['confidence']=='LOW' and r['editorial_status']=='HUMAN_APPROVED','Unapproved empty Lodge interval')
    require(int(r['original_TCP_raw_byte_offset'])==int(r['original_TCP_exclusive_end_byte'])==1970937 and int(register[238]['original_TCP_raw_byte_offset'])==1970937,'Approved coincident X.238/X.239 source cut')
    approved=next(x for x in human['records'] if x['identity']=='X.238')
    require(approved['status']=='HUMAN_APPROVED' and approved['approved_TCP_byte']==approved['approved_TCP_exclusive_endpoint']==1970937 and sha((a.authority_dir/'HUMAN_ADJUDICATION_LOG.json').read_bytes())==freeze['human_log_sha256'],'Frozen explicit zero-length authorization')
    absences.append({'niese':238,'identity':'X.238','classification':'NO_SEPARATE_COUNTERPART','editorial_status':'HUMAN_APPROVED','original_TCP_start_byte':1970937,'original_TCP_end_exclusive':1970937,'frozen_human_log_sha256':freeze['human_log_sha256'],'notice':'No separate corresponding passage in Lodge (1602)'})
 nodes,pis=index_xml(master);source_nodes,_=index_xml(source)
 niese=[n for n in nodes if n['tag']=='milestone' and n['attrs'].get('unit')=='niese']
 require([int(n['attrs']['n']) for n in niese]==list(range(LO,HI+1)),'Master milestone scope/order')
 native=[n for n in nodes if n not in niese];require(len(native)==len(source_nodes),'Source/master structural count mismatch')
 for n,s in zip(native,source_nodes):require(n['tag']==s['tag'] and n['attrs']==s['attrs'],'Source/master node mapping mismatch')
 source_of={id(n):s for n,s in zip(native,source_nodes)};edits=[];aliases=[]
 original_nodes,_=index_xml(a.original_source.read_bytes()) if BATCH else ([],[])
 original_paths={n['start']:n['path'] for n in original_nodes}
 recipe=json.loads((a.authority_dir/a.unit/'EXTRACTION_RECIPE.json').read_bytes()) if BATCH else None
 def tcpbyte(pos):
  if not BATCH:return pos+267938
  cursor=len(bytes.fromhex(recipe['prefix_hex']))
  for left,right in recipe['source_spans']:
   if cursor<=pos<cursor+right-left:return left+pos-cursor
   cursor+=right-left
  raise ValueError('Not an original source locus '+str(pos))
 def sourcepath(n):
  return original_paths[tcpbyte(n['start'])] if BATCH else n['path'].replace('/text[1]/body[1]/div[1]','/text[1]/group[1]/text[1]/body[1]/div[2]',1)
 def edit(start,end,new,reason,node=None):
  require(0<=start<=end<=len(master),'Invalid edit interval')
  d={'master_start':start,'master_end_exclusive':end,'original_b64':base64.b64encode(master[start:end]).decode(),'replacement_b64':base64.b64encode(new).decode(),'reason':reason}
  if node is not None:d['master_element_path']=node['path']
  edits.append(d)
 def add_id(n,identifier):
  require('xml:id' not in n['attrs'],'Refusing to overwrite original source ID')
  pos=n['start_end']-2 if n['empty'] else n['start_end']-1
  edit(pos,pos,(' xml:id='+quoteattr(identifier)).encode(),'ADD_REVERSIBLE_SOURCE_NODE_ID',n)
  s=source_of[id(n)];aliases.append({'production_id':identifier,'source_element_path':sourcepath(s),'extraction_element_path':s['path'],'extraction_start_byte':s['start'],'original_TCP_start_byte':tcpbyte(s['start']),'source_element_end_exclusive':s['end'],'source_element_sha256':sha(source[s['start']:s['end']]),'source_tag':s['tag']})
 for n in niese:
  num=int(n['attrs']['n']);attrs=dict(n['attrs']);attrs['xml:id']=PREFIX+'-niese'+str(num);attrs['type']='lodge-'+WORK+'-certified-niese'
  token=('<milestone'+''.join(' '+k+'='+quoteattr(v) for k,v in attrs.items())+'/>').encode()
  edit(n['start'],n['start_end'],token,'REPLACE_ONLY_PROJECT_MARKER_METADATA',n)
 for pi in pis:
  require(pi['target'] in ['lodge-pilot','lodge-continuation'],'Unsupported processing instruction')
  edit(pi['start'],pi['end'],b'','REMOVE_REVERSIBLE_HISTORICAL_PROJECT_PI')
 for tag,kind in [('p','p'),('note','note'),('pb','pb'),('list','list')]+([('item','item')] if BATCH else []):
  for i,n in enumerate([n for n in native if n['tag']==tag],1):add_id(n,PREFIX+'-tcp-'+kind+str(i).zfill(3))
 chapters=[n for n in native if n['tag']=='div' and n['attrs'].get('type')=='chapter']
 for i,n in enumerate(chapters,1):add_id(n,PREFIX+'-tcp-chapter'+str(i).zfill(2))
 book=next(n for n in native if n['tag']=='div' and n['attrs'].get('type')==('source-extraction' if BOOKKEY=='preface' else 'book'))
 if BOOKKEY!='preface':add_id(book,PREFIX+'-tcp-book')
 edit(book['start'],book['start'],('<div1 xml:id="'+PREFIX+'" type="'+('preface' if BOOKKEY=='preface' else 'book')+'" n="'+BOOKKEY+'">').encode(),'INSERT_READER_BOOK_WRAPPER')
 edit(book['end'],book['end'],b'</div1>','CLOSE_READER_BOOK_WRAPPER')
 bib=json.loads((a.reference_root/'assets/data/lodge1602-antiquities/book-02.json').read_bytes())['provenance']['bibliographical_metadata'] if BATCH else json.loads((a.authority_dir/'Lodge1602_Antiquities_BookII_SOURCE_MANIFEST.json').read_bytes())['source_bibliographical_metadata']
 require(any('Creative Commons 0 1.0 Universal' in x['text'] for x in bib['licensing']),'TCP licence not supported by frozen provenance')
 original_tree=ET.fromstring(a.original_source.read_bytes());q=lambda s:'{'+NS+'}'+s
 source_bibl=original_tree.find('.//'+q('sourceDesc'));require(source_bibl is not None,'TCP source bibliography missing')
 require('1602' in ''.join(source_bibl.itertext()),'Original edition identity mismatch')
 title=bib['titles'][0]['text'];credit='EEBO-TCP A04680; diplomatic transcription of the 1602 edition, translated by Thomas Lodge from Latin and French. Scholarly segmentation is the LatinJosephus frozen Book II edition; routine HIGH positions were accepted under the project workflow, sixteen MEDIUM positions explicitly human-approved.'
 if BATCH:credit='EEBO-TCP A04680; Thomas Lodge 1602 diplomatic transcription. Frozen Proem and Books I, III–V total 1361 Niese identities; eight historical MEDIUM boundaries explicitly human-approved. Native source order and character data unchanged.'
 if BATCH and BOOKKEY!='preface' and int(BOOKKEY)>=6:credit='EEBO-TCP A04680; Thomas Lodge 1602 diplomatic transcription. Frozen Books VI–X total 1764 Niese identities; four historical MEDIUM and one LOW treatment explicitly human-approved. X.238 has no separate counterpart; no source text is supplied or changed.'
 if BATCH and BOOKKEY!='preface' and int(BOOKKEY)>=11:credit='EEBO-TCP A04680; Thomas Lodge 1602 diplomatic transcription. Frozen Books XI–XV total 2130 Niese identities; eleven individual MEDIUM and two collective LOW decisions explicitly human-approved. Forty-two Book XIV identities have no separate counterpart because the documentary collection is abbreviated; no source text is supplied or changed.'
 if BATCH and BOOKKEY!='preface' and int(BOOKKEY)>=16:credit='EEBO-TCP A04680; Thomas Lodge 1602 diplomatic transcription. Frozen Books XVI–XX total 1772 Niese identities; seven historical MEDIUM boundaries explicitly human-approved. Independent LatinJosephus segmentation; no zero-length intervals. Native source order and character data unchanged.'
 if WORK=='contra-apionem':credit='EEBO-TCP A04680; Thomas Lodge 1602 diplomatic transcription, Contra Apionem Books I–II. Frozen 616 Niese identities; six historical MEDIUM boundaries HUMAN_APPROVED. No emendation, absent identity or relocated source node. Greek, Latin and Whiston divisions may differ.'
 header=('<teiHeader><fileDesc><titleStmt><title>'+escape(title)+' — '+('Contra Apionem' if WORK=='contra-apionem' else 'Antiquities')+' '+('Book II' if not BATCH else 'Proem' if BOOKKEY=='preface' else 'Book '+BOOKKEY)+'</title><author>Flavius Josephus</author><respStmt><resp>English translator</resp><name>Thomas Lodge</name></respStmt><respStmt><resp>Transcription</resp><name>EEBO Text Creation Partnership</name></respStmt><respStmt><resp>Frozen Niese segmentation and reversible production adapter</resp><name>LatinJosephus project</name></respStmt></titleStmt><publicationStmt><p>Data-layer derivative; reader/browser certification pending.</p><availability><licence target="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0 Universal applies to the TCP transcription. No additional licence for independent project annotations is asserted here.</licence></availability></publicationStmt><sourceDesc><bibl><title>'+escape(title)+'</title><pubPlace>London</pubPlace><publisher>Printed by Peter Short at the charges of G. Bishop, S. Waterson, P. Short, and Tho. Adams</publisher><date>1602</date><idno type="EEBO-TCP">A04680</idno></bibl><p>'+escape(credit)+'</p>'+''.join('<idno type="sha256-'+k+'">'+v+'</idno>' for k,v in sorted(AUTH.items()) if k!='scholarly_zip')+'</sourceDesc></fileDesc><encodingDesc><p>Deterministic '+VERSION+'. Source-native chapters, paragraphs, marginal notes, gaps, page breaks and typography retained. Added source IDs and reader wrapper are fully reversible. No paragraph sameAs assertions.</p></encodingDesc></teiHeader>')
 text=next(n for n in native if n['tag']=='text');edit(text['start'],text['start'],header.encode(),'INSERT_PROJECT_HEADER_OUTSIDE_SOURCE_BODY')
 edits.sort(key=lambda d:(d['master_start'],d['master_end_exclusive']))
 previous=0;out=[];cursor=0;outputpos=0
 for d in edits:
  start,end=d['master_start'],d['master_end_exclusive'];require(start>=cursor,'Overlapping transformations')
  unchanged=master[cursor:start];out.append(unchanged);outputpos+=len(unchanged)
  replacement=base64.b64decode(d['replacement_b64']);d['derivative_start']=outputpos;d['derivative_end_exclusive']=outputpos+len(replacement);out.append(replacement);outputpos+=len(replacement);cursor=end
 out.append(master[cursor:]);derivative=b''.join(out);ET.fromstring(derivative)
 require(b'\r' not in derivative and not derivative.startswith(b'\xef\xbb\xbf'),'Unexpected BOM/line endings')
 def transform_offset(pos):
  delta=0
  for d in edits:
   if d['master_start']<pos:delta+=len(base64.b64decode(d['replacement_b64']))-(d['master_end_exclusive']-d['master_start'])
  return pos+delta
 prodnodes,_=index_xml(derivative);byid={n['attrs'].get('xml:id'):n for n in prodnodes if n['attrs'].get('xml:id')}
 for alias in aliases:
  pn=byid[alias['production_id']];alias.update({'production_element_path':pn['path'],'production_start_byte':pn['start'],'production_end_exclusive':pn['end']})
 evidence=[]
 prodbook=byid[PREFIX] if BOOKKEY=='preface' else byid[PREFIX+'-tcp-book']
 oldinside=[n for n in native if book['start']<=n['start']<book['end']]
 newinside=[n for n in prodnodes if prodbook['start']<=n['start']<prodbook['end'] and not(n['tag']=='milestone' and n['attrs'].get('unit')=='niese')]
 if BOOKKEY=='preface':newinside=newinside[1:]
 require(len(oldinside)==len(newinside),'Native production-node correspondence')
 serials={'gap':0,'milestone':0}
 for old,new in zip(oldinside,newinside):
  require(old['tag']==new['tag'],'Native production-node ordering')
  if old['tag'] not in serials:continue
  serials[old['tag']]+=1;src=source_of[id(old)]
  evidence.append({'evidence_key':PREFIX+'-source-'+old['tag']+str(serials[old['tag']]).zfill(3),'source_tag':old['tag'],'source_attributes':src['attrs'],'extraction_element_path':src['path'],'source_element_path':sourcepath(src),'extraction_start_byte':src['start'],'original_TCP_start_byte':tcpbyte(src['start']),'extraction_end_exclusive':src['end'],'source_raw_element_sha256':sha(source[src['start']:src['end']]),'production_element_path':new['path'],'production_start_byte':new['start'],'production_end_exclusive':new['end'],'semantic_role':'TCP_TRANSCRIPTION_GAP_NOT_IDENTITY_OMISSION' if old['tag']=='gap' else 'ORIGINAL_TCP_MARKER_NOT_PROJECT_NIESE'})
 sections=[]
 for i,(r,p,n) in enumerate(zip(register,partition,niese)):
  num=int(r['number']);start=int(r['whole_book_literal_narrative_offset']);end=int(partition[i]['literal_exclusive_end'])
  sections.append({'identity':r['identity'],'niese':num,'marker_id':PREFIX+'-niese'+str(num),'frozen_marker_alias':n['attrs']['xml:id'],'production_marker_byte':byid[PREFIX+'-niese'+str(num)]['start'],'source_coordinate':{k:r[k] for k in ['source_element_path','extraction_element_path','text_node_xpath','text_slot','unicode_offset_in_text_node','unicode_offset_in_paragraph','extraction_raw_byte_offset','original_TCP_raw_byte_offset','whole_book_literal_narrative_offset']},'source_node_sha256':p['source_parsed_text_node_sha256'],'raw_source_text_node_sha256':p['source_raw_text_node_sha256'],'source_text_node_extraction_start':int(p['source_text_node_extraction_start']),'source_text_node_extraction_end_exclusive':int(p['source_text_node_extraction_end_exclusive']),'literal_exclusive_end':end,'literal_character_extent':end-start,'narrative_fragment_sha256':p['narrative_fragment_sha256'],'extraction_exclusive_end_byte':int(p['extraction_exclusive_end_byte']),'raw_source_fragment_sha256':p['raw_source_XML_fragment_sha256'],'incipit':p['exact_Lodge_incipit'],'tail':p['exact_Lodge_tail'],'historical_confidence':r.get('historical_confidence') or r['confidence'],'historical_classification':r['classification'],'active_editorial_status':p['active_editorial_status'],'current_boundary_review_required':False,'correspondence_qualification':p['correspondence_qualification'],'rationale':r['rationale']})
 chapterdata=[]
 parsed=ET.fromstring(source)
 chapterEls=parsed.findall('.//'+q('div')+'[@type="chapter"]')
 for i,ch in enumerate(chapterEls,1):
  head=ch.find(q('head'));chapterdata.append({'printed_chapter':int(ch.get('n')) if BATCH else i,'source_label':''.join(head.itertext()),'anchor_id':PREFIX+'-tcp-chapter'+str(i).zfill(2),'precision':'SOURCE_NATIVE_ONLY; independent of Bamberg/Whiston divisions'})
 notes=[x for x in aliases if x['source_tag']=='note'];firstcut=int(register[0]['extraction_raw_byte_offset'])
 for note in notes:
  byte=note['extraction_start_byte'];preceding=[s['niese'] for s in sections if int(s['source_coordinate']['extraction_raw_byte_offset'])<=byte]
  note['physical_niese_interval']=preceding[-1] if preceding else None
  note['context']='PRE_FIRST_IDENTITY_SOURCE_CONTEXT' if not preceding else 'ORIGINAL_PHYSICAL_SOURCE_LOCUS'
 if not BATCH:require(sum(n['physical_niese_interval'] is None for n in notes)==1,'Opening note distribution')
 qualified=sections[283] if not BATCH else None
 metadata={'schema':VERSION,'schema_version':1,'required_fields':['availability','production_xml','authorities','reference_snapshot','source_counts','native_chapters','source_node_aliases','marginal_notes','sections','project_navigation_covers'],'work':WORK,'source':'lodge1602','book_key':BOOKKEY,'availability':{'availableBookKeys':['preface','1','2','3','4','5'] if BATCH else ['2'],'exactNieseBooks':['preface','1','2','3','4','5'] if BATCH else ['2'],'proem_integrated':BATCH,'other_books_integrated':BATCH,'identity_range':[LO,HI],'whole_section_absences':absences,'inherits_other_witness_availability':False},'production_xml':{'path':TARGETS['xml'],'sha256':sha(derivative),'book_wrapper_id':PREFIX,'native_book_id':PREFIX+'-tcp-book'},'authorities':AUTH,'reference_snapshot':reference_snapshot(a.reference_root,a.base_commit),'source_counts':COUNTS,'historical_confidence_counts':freeze['historical_confidence_counts'],'historical_classification_counts':freeze['historical_classification_counts'],'all_MEDIUM_explicitly_human_approved':True,'scholarly_status':'FINAL_SCHOLARLY_FREEZE_CERTIFIED','reader_browser_status':'PENDING_BATCH_BROWSER_QA' if BATCH else 'PENDING_WORKBOT_7B; NOT_TESTED','deferred_observations':{'count':197,'sha256':sha((a.authority_dir/'Lodge1602_Antiquities_BookII_DEFERRED_QUERIES.tsv').read_bytes()),'disposition':'NONBLOCKING_SOURCE_PROOFREADING; no emendation'} if not BATCH else {'disposition':'Frozen witness qualifications retained in section rationales; no emendation'},'literal_count_convention':'Outermost narrative p; exclude note/head/argument/trailer/byline/opener/closer/signed/label subtrees but retain their following tails; retain other character data including gap descriptions and layout whitespace. Unicode code points, no normalization.','coordinate_convention':freeze['source_coordinate_convention'],'native_chapters':chapterdata,'source_contents':next((x for x in aliases if x['source_tag']=='list'),None),'source_node_aliases':aliases,'source_evidence_nodes':evidence,'marginal_notes':notes,'pre_first_identity_context':{'literal_units':int(register[0]['whole_book_literal_narrative_offset']),'notes':[n['production_id'] for n in notes if n['physical_niese_interval'] is None],'not_a_Niese_identity':True,'note_anchor_relocated':False},'sections':sections,'project_navigation_covers':registry_records(a.reference_root),'II284_independent_Lodge_qualification':({'lodge_identity':'2.284','incipit':qualified['incipit'],'source_coordinate':qualified['source_coordinate'],'Lodge_boundary_status':'CERTIFIED_HIGH_ACCEPTED_UNDER_PROJECT_WORKFLOW','whole_section_absent':False,'project_context_boundary':'LOEB-02-Subchapter-13-3','project_context_qualification':'NIESE_SOURCE_AMBIGUOUS; use containing context or unavailable structural view; does not qualify the frozen Lodge exact cut'} if not BATCH else None),'provenance':{'bibliographical_metadata':bib,'TCP_licence':'CC0 1.0 Universal','TCP_licence_uri':'https://creativecommons.org/publicdomain/zero/1.0/','project_annotations_licence':'Not independently specified by frozen authority; do not infer TCP CC0 applies to independent annotations','sameAs_claims':[],'scholarly_master_is_not_production_derivative':True},'book_end':freeze['end_boundaries']}
 if BATCH and BOOKKEY!='preface' and int(BOOKKEY)>=6:
  metadata['availability'].update({'availableBookKeys':['preface']+[str(i) for i in range(1,11)],'exactNieseBooks':['preface']+[str(i) for i in range(1,11)]})
 if BATCH and BOOKKEY!='preface' and int(BOOKKEY)>=11:
  metadata['availability'].update({'availableBookKeys':['preface']+[str(i) for i in range(1,16)],'exactNieseBooks':['preface']+[str(i) for i in range(1,16)]})
 if BATCH and BOOKKEY!='preface' and int(BOOKKEY)>=16:
  metadata['availability'].update({'availableBookKeys':['preface']+[str(i) for i in range(1,21)],'exactNieseBooks':['preface']+[str(i) for i in range(1,21)]})
 if BATCH:metadata.update({'authority_unit':a.unit,'literal_block_tags':['p','item'],'literal_count_convention':'Outermost narrative p and narrative chapter item blocks; exclude native note/head/argument and other paratext subtrees, retain following tails, gap descriptions and every Unicode character without normalization.'})
 if WORK=='contra-apionem':
  metadata['availability'].update({'availableBookKeys':['1','2'],'exactNieseBooks':['1','2'],'proem_integrated':False,'other_books_integrated':True})
  metadata['human_adjudications']=[r for r in json.loads((a.authority_dir/'HUMAN_ADJUDICATION_LOG.json').read_bytes())['records'] if r['identity'] in {s['identity'] for s in sections}]
  metadata['native_structure_qualification']='No native chapter divisions or book-local contents list. Lettered TCP milestones are not chapters. Project chapters display containing Niese context.'
 ledger={'schema':'lodge1602-antiquities-inverse-ledger-v1','converter_version':VERSION,'authorities':AUTH,'derivative_sha256':sha(derivative),'metadata_sha256':sha(jsonbytes(metadata)),'input_byte_length':len(master),'output_byte_length':len(derivative),'edits':edits,'source_node_aliases':aliases,'inverse_rule':'Assert each replacement byte interval, replace it by original_b64 in ascending derivative order, retaining every interstitial byte. Empty removals restored in ledger order. No XML serialization.','source_counts':COUNTS,'frozen_packet_checksum_members_verified':len(checked),'reader_browser_status':'PENDING_NOT_RUN'}
 outputs={TARGETS['xml']:derivative,TARGETS['metadata']:jsonbytes(metadata),TARGETS['master']:master,TARGETS['register']:paths['final_register'].read_bytes(),TARGETS['freeze']:paths['freeze_manifest'].read_bytes(),TARGETS['ledger']:jsonbytes(ledger)}
 for relative,b in outputs.items():
  target=a.output_root/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
 if a.ledger_copy:a.ledger_copy.write_bytes(jsonbytes(ledger))
 print(json.dumps({'status':'PASS','derivative_sha256':sha(derivative),'metadata_sha256':sha(jsonbytes(metadata)),'ledger_sha256':sha(jsonbytes(ledger)),'edits':len(edits),'sections':len(sections),'native_aliases':len(aliases),'navigation_covers':len(metadata['project_navigation_covers'])}))
if __name__=='__main__':main()
