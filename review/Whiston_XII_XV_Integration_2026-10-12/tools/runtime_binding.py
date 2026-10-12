"""Bind prior browser fixtures to the completed standard build; read-only inputs."""
import pathlib,json,re,hashlib
BASE=pathlib.Path(__file__).resolve().parents[4]
ROOT=BASE/'candidate'; PACK=ROOT/'review/Whiston_XII_XV_Integration_2026-10-12'
old=pathlib.Path('C:/workspace/Whiston-I-XI-Renderer-runtime-20261011/site')
new=BASE/'runtime/standard-site'
sha=lambda b:hashlib.sha256(b).hexdigest()
rows=[]
for f in ['antiquities/index.html','bellum-judaicum/index.html','contra-apionem/index.html','deh/index.html','assets/css/main.css','assets/css/deh-parallels.css']:
 a=(old/f).read_bytes();b=(new/f).read_bytes()
 clean=lambda x:re.sub(rb'(deh(?:Parallels\.js|-parallels\.css)\?v=)\d+',rb'\1BUILD_TIMESTAMP',x)
 assert a==b or f=='deh/index.html' and clean(a)==clean(b),f
 rows.append(dict(path=f,fixture_SHA256=sha(a),standard_build_SHA256=sha(b),byte_exact=a==b,only_cache_timestamp_difference=a!=b))
for f in (ROOT/'assets/js').rglob('*'):
 if f.is_file():
  assert f.read_bytes()==(new/f.relative_to(ROOT)).read_bytes(),str(f)
  rows.append(dict(path=f.relative_to(ROOT).as_posix(),standard_build_equals_candidate=True,SHA256=sha(f.read_bytes())))
for f in (old/'assets/xml').rglob('*'):
 if f.is_file() and f.relative_to(old/'assets/xml').parts[0] in ['bellum','deh','contra-apionem']:
  rel=f.relative_to(old);a=f.read_bytes();b=(new/rel).read_bytes()
  assert a==b or rel.parts[2]=='contra-apionem' and a.replace(b'\r\n',b'\n')==b.replace(b'\r\n',b'\n'),str(rel)
  rows.append(dict(path=rel.as_posix(),cross_work_publication_fixture_equals_standard_build=a==b,only_XML_EOL_representation_difference=a!=b,fixture_SHA256=sha(a),standard_build_SHA256=sha(b)))
for f in (ROOT/'assets/xml/antiquities').rglob('*'):
 if f.is_file():
  assert f.read_bytes()==(new/f.relative_to(ROOT)).read_bytes(),str(f)
  rows.append(dict(path=f.relative_to(ROOT).as_posix(),standard_build_equals_candidate=True,SHA256=sha(f.read_bytes())))
result=dict(status='PASS',original_fixture_location=str(old),fresh_standard_build=str(new),records=rows,
 qualification='Original helper retained a historical site path because its adaptation matched a different runtime name. Antiquities source and renderer requests were already candidate overlays. Reader HTML/CSS and Antiquities build inputs match exactly. DEH cache timestamps and six Apion XML CRLF/LF representations differ only as recorded; cross-work display checks are rerun against the fresh build. The owned helper now defaults to the task standard-site.',
 fixture_correction_changes_no_production_code=True)
(PACK/'STANDARD_BUILD_RUNTIME_BINDING.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Standard build runtime binding PASS',len(rows))
