import pathlib,json,hashlib
BASE=pathlib.Path(__file__).parent;ROOT=BASE/'candidate';SITE=BASE/'runtime/standard-site';PACK=ROOT/'review/Whiston_XVI_XX_Integration_2026-10-12'
sha=lambda b:hashlib.sha256(b).hexdigest();rows=[]
for f in ['preface.xml']+[f'book-{n:02}.xml' for n in range(1,21)]:
 p='assets/xml/antiquities/English/'+f;a=(ROOT/p).read_bytes();b=(SITE/p).read_bytes();assert a==b,(p,'Actual built English differs')
 rows.append(dict(path=p,sha256=sha(a),actual_build_byte_identical=True))
for p in ['assets/js/renderTei.js','assets/js/CETEI.js','assets/js/common.js','assets/js/dehParallels.js','assets/js/dehParallelsCore.js','assets/css/tei.css']:
 a=(ROOT/p).read_bytes();b=(SITE/p).read_bytes();assert a==b,(p,'Actual built renderer/module differs');rows.append(dict(path=p,sha256=sha(a),actual_build_byte_identical=True))
result=dict(status='PASS',actual_standard_build=str(SITE),all_21_Whiston_XML_and_reader_modules_byte_identical=True,records=rows,generated_all_production_sources_report='execution-logs/Stage-C-generated-source-verification.json')
(PACK/'STANDARD_BUILD_RUNTIME_BINDING.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Literal actual standard build binding PASS: 21 Whiston XML and all reader modules')
