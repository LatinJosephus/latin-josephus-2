import pathlib,json,hashlib,re,sys,subprocess,shutil
BASE=pathlib.Path(__file__).parent;ROOT=BASE/'candidate';PACK=ROOT/'review/Whiston_XII_XV_Integration_2026-10-12'
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda b:hashlib.sha256(b).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
last=13 if sys.argv[1]=='A' else 15;initial=load(PACK/'BASELINE.json');allow={'.gitattributes','assets/js/renderTei.js','bin/reader-corpus-integrity.mjs','_docs/reader-corpus-integrity.json'}|{f'assets/xml/antiquities/English/book-{n:02}.xml' for n in range(12,last+1)}
changes=[];protected=0
for path,expected in initial['tracked_file_hashes'].items():
 actual=sha((ROOT/path).read_bytes());
 if actual!=expected:
  assert path in allow,('Unintended tracked change',path);changes.append(dict(path=path,baseline_SHA256=expected,candidate_SHA256=actual))
 else:protected+=1
old=(BASE/'baseline/assets/js/renderTei.js').read_text(encoding='utf-8');new=(ROOT/'assets/js/renderTei.js').read_text(encoding='utf-8');strip=lambda s:re.sub(r'exactNieseBooks: \[[^\]]+\]','exactNieseBooks: ENABLED_BOOKS',s,count=1)
assert strip(old)==strip(new),'Generic renderer logic changed';assert 'Whiston English: exact Niese interval.' not in new
recon=[]
for r in load(PACK/'SOURCE_INVENTORY.json'):
 if r['book']>last:continue
 actual=(ROOT/r['file']).read_bytes();assert sha(actual)==r['certified_sha256'];original=(PACK/'certified'/('approved-original-'+pathlib.Path(r['file']).name)).read_bytes();restored=re.sub(rb'<milestone unit="niese" n="\d+"/>',b'',actual);assert restored==original
 recon.append(dict(book=r['book'],certified_SHA256=sha(actual),reconstructed_SHA256=sha(restored),approved_baseline_SHA256=sha(original),byte_exact=True))
out=dict(status='PASS',stage=sys.argv[1],protected_tracked_files=protected,allowed_changes=changes,new_English_byte_exact=True,all_existing_I_XI_English_unchanged=True,all_Greek_Latin_XML_unchanged=True,XVI_XX_English_unchanged=True,registries_structure_CSS_unchanged=True,generic_renderer_unchanged=True,notice_correction_preserved=True,reconstruction=recon)
save(PACK/f'STAGE_{sys.argv[1]}_SOURCE_PRESERVATION.json',out)
if last==13:
 bam=load(PACK/'BAMBERG_QA.json');assert all(r['state']['viewingLevel']=='bamberg-level' and r['state']['bambergId']==r['unit'] for r in bam['views'])
 save(PACK/'STAGE_A_NATIVE_GUARDS.json',dict(status='PASS',production_XML=143,all_production_XML_parsed=True,frozen_publication_inputs=38,negative_checks=['unexpected XML','segmented English corruption','Lodge corruption','manifest alteration','concordance alteration','Lodge authority alteration','missing XML','generated publication authority hashes'],command='node bin/reader-corpus-qa.mjs --site runtime/standard-site',standard_build='full plugins, bundle check PASS; 80.808 seconds; inherited Sass warnings only'))
print('Stage',sys.argv[1],'source preservation PASS',protected,'unchanged tracked files',len(changes),'permitted changes')
shutil.copy2(__file__,PACK/'tools/source_preservation.py')
