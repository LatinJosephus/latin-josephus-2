from pathlib import Path
import json,re,hashlib,sys
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
build=sys.argv[1] if len(sys.argv)>1 else 'build2'
assert build in ['build2','build3']
SITE=Path(r'C:\workspace\Antiquities-Niese-14-15-runtime-20261009')/build/'site'
sha=lambda b:hashlib.sha256(b).hexdigest()
for b,roman in [(14,'XIV'),(15,'XV')]:
 P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09';q=json.loads((P/'PARTIAL_READER_QA.json').read_text());assert q['result']=='PASS'
 Q=P/('reader-tested-checkpoint' if build=='build2' else 'reader-tested-checkpoint3');Q.mkdir(exist_ok=True);files=[]
 for lang in ['Greek','Latin','English']:
  src=SITE/f'assets/xml/antiquities/{lang}/book-{b:02}.xml';raw=src.read_bytes();(Q/f'{lang}.xml').write_bytes(raw)
  original=(P/f'frozen-inputs/{lang}.xml').read_bytes()
  if lang=='Latin':recovered=re.sub(rb'<milestone unit="niese" n="[0-9]+"/>',b'',raw)
  elif lang=='Greek':
   marker=b'<num>[1]</num>';assert raw.count(marker)==1;recovered=raw.replace(marker,b'',1)
  else:recovered=raw
  assert recovered==original,(b,lang)
  files.append(dict(language=lang,built_path=str(src),saved_path=str(Q/f'{lang}.xml'),sha256=sha(raw),frozen_sha256=sha(original),exact_byte_recovery=True))
 for name in ['IDENTITY_REGISTRY_PARTIAL.json','EXPECTED_REVIEWED_INTERVALS.json']:
  raw=(P/name).read_bytes();(Q/name).write_bytes(raw);files.append(dict(saved_path=str(Q/name),sha256=sha(raw)))
 raw=(SITE/'assets/js/renderTei.js').read_bytes();(Q/'renderTei.js').write_bytes(raw)
 files.append(dict(saved_path=str(Q/'renderTei.js'),sha256=sha(raw)))
 q['tested_input_manifest']=files;q['tested_executable_reader_is_local_build']=True
 q['full_book_certified']=False;q['later_reviewed_boundaries_require_fresh_build_and_QA']=True
 if b==15:
  image=P/'evidence/local-reader-40-checkpoint.png'
  target=P/('evidence/local-reader-62-checkpoint.png' if build=='build2' else 'evidence/local-reader-62-checkpoint3.png')
  if image.exists():image.replace(target)
  q['screenshot_section']=62
  q['screenshot_path']=str(target)
 else:
  q['screenshot_section']=133
  if build=='build3':
   image=P/'evidence/local-reader-133-checkpoint.png';target=P/'evidence/local-reader-133-checkpoint3.png'
   if image.exists():image.replace(target)
   q['screenshot_path']=str(target)
 (P/'PARTIAL_READER_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 (Q/'PARTIAL_READER_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print('Saved byte-exact actual local reader checkpoint inputs and build hashes for both partial QA records.')
source=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review\Antiquities_Loeb_Niese_Verification_2026-10-05')
manifest=source/'Antiquities_Loeb_Niese_Verification_SHA256SUMS.txt';results=[]
for line in manifest.read_text().splitlines():
 expected,relative=line.split('  ',1)
 if not (relative.startswith(('batch-02/','consolidated/')) or relative=='FREEZE.md'):continue
 file=source/relative
 if not file.exists():results.append(dict(path=str(file),status='MISSING_FILE',expected=expected));continue
 actual=sha(file.read_bytes());results.append(dict(path=str(file),status='PASS' if actual==expected else 'HASH_MISMATCH',expected=expected,actual=actual))
result=dict(manifest_path=str(manifest),manifest_sha256=sha(manifest.read_bytes()),scope='Shared structural controls covering XI–XV and consolidated source records; read-only verification, not current visual certification.',files=results,status='PASS' if all(x['status']=='PASS' for x in results) else 'FAIL')
(BATCH/'FROZEN_STRUCTURAL_SOURCE_QA.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
print('Frozen structural source records:',result['status'],len(results))
