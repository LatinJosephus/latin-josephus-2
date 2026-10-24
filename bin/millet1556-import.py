"""Deterministic, source-preserving site adapter for the frozen Millet master.

No scholarly source is rewritten. --check compares all derivatives without writes.
"""
from pathlib import Path
import argparse,hashlib,json,re
ROOT=Path(__file__).resolve().parent.parent
def rawsha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def packed(v):return (json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf8')
def derive(master):
 receipt=json.loads((master/'FREEZE_RECEIPT.json').read_text(encoding='utf8'));assert receipt['status']=='INTEGRATION_READY'
 for name,key in [('MILLET_ALIGNMENT_DATA.json','machine_data_sha256'),('MILLET_USSANI_MASTER.xml','master_XML_sha256'),('SOURCE_AND_VERSION_MANIFEST.json','source_manifest_sha256')]:assert rawsha(master/name)==receipt[key]
 data=json.loads((master/'MILLET_ALIGNMENT_DATA.json').read_text(encoding='utf8'));assert data['schema']=='millet-ussani-alignment/1.0'
 lines=[l|{'source_index':i} for i,l in enumerate(data['lines'])];byid={l['TEI_line_id']:l for l in lines};assert len(byid)==19104
 def frag(f):
  l=byid[f['source_TEI_line_id']];s=l['text_exact'];a,b=f['start_cp'],f['end_cp'];assert s[a:b]==f['text_exact'];assert len(s[:a].encode('utf-16-le'))//2==f['start_utf16'];assert len(s[:b].encode('utf-16-le'))//2==f['end_utf16']
  return {'line':l['TEI_line_id'],'start_cp':a,'end_cp':b,'start_utf16':f['start_utf16'],'end_utf16':f['end_utf16'],'fragment_sha256':f['fragment_SHA256']}
 def canonical(c):return c|{'ordinal':int(re.search(r'num(\d+)$',c['xml_id'])[1]),'unit':int(re.search(r'\.(\d+)$',c['citation'])[1])}
 files={};bookfiles=[];allprimary=set()
 for book in data['books']:
  n=book['book'];a,b=book['source_image_range'];mm=[];primary=set()
  for m in book['mappings']:
   ff=[frag(f) for f in m['source_fragments']];primary.update(f['line'] for f in ff)
   mm.append({k:m[k] for k in ['id','book','relation','relation_basis','certainty','editorial_attention','evidence_reason','annotation_ids','primary_coverage']}|{'canonical':canonical(m['canonical']),'fragments':ff,'source_passage_sha256':m['source_passage_sha256'],'provenance':m['provenance']})
  ll=[l|{'primary':l['TEI_line_id'] in primary} for l in lines if a<=l['image_number']<=b];allprimary.update(primary)
  ids={l['TEI_line_id'] for l in ll};nn=[d for d in data['native_divisions'] if d['book']==n];aa=[x for x in data['secondary_annotations'] if any(m['id']==x['mapping_id'] for m in mm)]
  for x in aa:x['fragments']=[frag(f) for f in x['source_fragments']];x.pop('source_fragments')
  obj={'schema':'millet1556-reader-book/1','version':data['version'],'book':n,'native':{k:v for k,v in book.items() if k!='mappings'},'pages':[p for p in data['pages'] if a<=p['image_number']<=b],'lines':ll,'divisions':nn,'mappings':mm,'annotations':aa}
  assert all(f['line'] in ids for m in mm for f in m['fragments']);name=f'book-{n:02d}.json';files[name]=packed(obj);bookfiles.append({'book':n,'path':name,'units':len(mm),'lines':len(ll),'sha256':hashlib.sha256(files[name]).hexdigest(),'bytes':len(files[name])})
 preliminary={'schema':'millet1556-reader-preliminary/1','version':data['version'],'book':0,'pages':[p for p in data['pages'] if p['image_number']<31],'lines':[l|{'primary':False} for l in lines if l['image_number']<31],'divisions':[d for d in data['native_divisions'] if d['book'] is None],'mappings':[],'annotations':[]}
 files['preliminary.json']=packed(preliminary);files['editorial.json']=packed(data['editorial_exceptions'])
 assert len(allprimary)==16236 and sum(b['units'] for b in bookfiles)==558
 manifest={'schema':'millet1556-reader/1','version':data['version'],'source_key':'millet1556','label':'Millet 1556 — French','language':'fr','bibliography':{'author':'Jean Millet, de Sainct Amour','title':"Les cinq livres de l’histoire d’Egesippe, contenans plusieurs guerres des Iuifs, & la ruine de Hierusalem",'imprint':'Paris: Guillaume Cavellat, 1556. Printed by Benoist Prévost; colophon dated 17 January 1556.','basis':'French translation of the Latin De excidio Hierosolymitano, historically attributed to Hegesippus. Ussani (1932) supplies the modern correspondence framework; it is not claimed as Millet’s sixteenth-century exemplar.'},'books':bookfiles,'preliminary':{'path':'preliminary.json','sha256':hashlib.sha256(files['preliminary.json']).hexdigest()},'editorial':{'path':'editorial.json','sha256':hashlib.sha256(files['editorial.json']).hexdigest()},'authority':{'status':'INTEGRATION_READY','master_xml_sha256':receipt['master_XML_sha256'],'machine_data_sha256':receipt['machine_data_sha256'],'source_manifest_sha256':receipt['source_manifest_sha256'],'freeze_receipt_sha256':rawsha(master/'FREEZE_RECEIPT.json')},'offset_contract':data['offset_contract'],'relation_contract':data['relation_contract'],'unavailable_outer_scans':data['unavailable_outer_scans'],'counts':{'canonical_units':558,'all_source_lines':19104,'primary_lines':16236,'primary_codepoints':934885,'annotations':162},'editorial_status':'Provisional scholarly transcription and passage alignment. Four inherited attention flags, 24 ancillary questions, B001-B009 and two source-layer notices remain unresolved. Translation differences are not established Latin variants.','source_display':'Exact Unicode, whitespace, physical lines and ¬ retained in data and source-coordinate DOM spans. Reading display reflows lines, hides division markers and inserts separately tagged spaces between complete words. Folio display is opt-in. No Unicode normalization or source editing.'}
 files['manifest.json']=packed(manifest)
 provenance={'schema':'millet1556-site-provenance/1','master_version':data['version'],'freeze_receipt':receipt,'source_and_version_manifest_sha256':receipt['source_manifest_sha256'],'derivation':'bin/millet1556-import.py; deterministic lossless source-line and stand-off offset adapter. No transcription editing. Full source hashes and identifiers remain in page/line records.','assets':{name:{'sha256':hashlib.sha256(bb).hexdigest(),'bytes':len(bb)} for name,bb in files.items()}}
 files['provenance.json']=packed(provenance)
 return files
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--master',type=Path,required=True);p.add_argument('--check',action='store_true');args=p.parse_args();files=derive(args.master);out=ROOT/'assets/data/deh-millet1556'
 for name,bb in files.items():
  dest=out/name
  if args.check:assert dest.read_bytes()==bb,('Derivative differs',name)
  else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(bb)
 print(json.dumps({'result':'PASS','mode':'check' if args.check else 'derive','assets':len(files),'canonical_units':558,'source_lines':19104,'total_bytes':sum(len(b) for b in files.values())}))
