"""Reuse the established suites, referencing immutable incoming authority records."""
from pathlib import Path
import json,sys,hashlib,subprocess,tarfile,io
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
A=ROOT/'review/Antiquities_Niese_BookXI_2026-10-09'
R=Path('C:/workspace/Antiquities-Niese-11-integration-runtime-20261009')
def sha(x):return hashlib.sha256(x).hexdigest()
def save(n,x):(D/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
 baseline=json.loads((D/'BASELINE.json').read_text());incoming=json.loads((D/'INCOMING_SCOPE.json').read_text())
 scripts=['qa-common.cjs','reader-xi.cjs','reader-prior.cjs','reader-containing.cjs','reader-extra.cjs','build.sh','build_receipt.py']
 adaptations=[]
 for name in scripts:
  original=(A/name).read_text(encoding='utf8');s=original
  s=s.replace('C:/workspace/Antiquities-Niese-11-runtime-20261009',str(R).replace('\\','/'))
  if name=='qa-common.cjs':
   s=s.replace("const load=p=>JSON.parse(fs.readFileSync(p,'utf8')),save=", "const authority=path.join(root,'review/Antiquities_Niese_BookXI_2026-10-09');\nconst authorityNames=new Set(['EXPECTED_SELECTIONS.json','AUTHORIZED_ADDITIONS.json','TRADITIONAL_EXPECTATIONS.json']);\nconst load=p=>JSON.parse(fs.readFileSync(!fs.existsSync(p)&&authorityNames.has(path.basename(p))?path.join(authority,path.basename(p)):p,'utf8')),save=")
  if name=='reader-xi.cjs':s=s.replace('listen(s,8911)','listen(s,8912)')
  if name=='build_receipt.py':s=s.replace('from mixed_mapper import digest','import hashlib\ndef digest(raw):return hashlib.sha256(raw).hexdigest()')
  (D/name).write_text(s,encoding='utf8',newline='\n')
  adaptations.append(dict(name=name,authority_sha256=sha((A/name).read_bytes()),integration_sha256=sha((D/name).read_bytes()),changes='Runtime, preferred port, immutable evidence references; build receipt uses hashlib. No test algorithm or selection code change.'))
 original=(A/'verify_sources.py').read_text(encoding='utf8')
 original=original.replace('from mixed_mapper import Book,digest,NS,XMLID,fixtures',"A=Path(__file__).resolve().parents[1]/'Antiquities_Niese_BookXI_2026-10-09'\nsys.path.insert(0,str(A))\nfrom mixed_mapper import Book,digest,NS,XMLID,fixtures")
 original=original.replace('D=Path(__file__).resolve().parent;ROOT=D.parents[1]', 'OUT=Path(__file__).resolve().parent;D=A;ROOT=OUT.parents[1]')
 original=original.replace("def save(name,x):(D/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\\n',encoding='utf8',newline='\\n')", "def save(name,x):\n if name in ['LATIN_OUTPUT_LOCATORS.json','GREEK_OUTPUT_LOCATORS.json','IDENTITY_REGISTER.json']:\n  assert x==json.loads((D/name).read_text(encoding='utf8')),name\n else:(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\\n',encoding='utf8',newline='\\n')")
 (D/'verify_sources.py').write_text(original,encoding='utf8',newline='\n')
 adaptations.append(dict(name='verify_sources.py',authority_sha256=sha((A/'verify_sources.py').read_bytes()),integration_sha256=sha((D/'verify_sources.py').read_bytes()),changes='Read original authority in place; compare recomputed registers instead of rewriting incoming records; write only new integration proof.'))
 save('QA_ADAPTATIONS.json',adaptations)
 target=R/'source';base=R/'baseline-source';out=R/'build'
 assert not target.exists() and not base.exists() and not out.exists()
 target.mkdir();base.mkdir();out.mkdir()
 paths=[x['relative'] for x in baseline['files'] if not x['relative'].startswith('review/')]+[p for p in incoming['production'] if p not in {x['relative'] for x in baseline['files']}]
 manifest=[]
 for rel in paths:
  raw=(ROOT/rel).read_bytes();q=target/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
  manifest.append(dict(relative=rel,bytes=len(raw),sha256=sha(raw)))
 archive=subprocess.check_output(['git','archive',baseline['canonical']],cwd=ROOT)
 expected={x['relative']:x for x in baseline['files']}
 with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
  for member in tf.getmembers():
   rel=member.name
   if not member.isfile() or rel.startswith('review/'):continue
   assert rel in expected and not Path(rel).is_absolute() and '..' not in Path(rel).parts
   raw=tf.extractfile(member).read();assert sha(raw)==expected[rel]['working_sha256'],rel
   q=base/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
 save('BUILD_INPUT_MANIFEST.json',manifest)
 save('BUILD_CONTEXT.json',dict(source=str(target),baseline_source=str(base),site=str(out/'site'),baseline_site=str(out/'baseline-site'),build_directory=str(out),baseline=baseline['canonical'],image='ruby@sha256:dba270af6994f64e45ee3dd2b85225a2a0d01f29c04508c7a3c7c8dbf59d2a85',purpose='Fresh full integration/baseline Jekyll builds; no post-build replacement'))
 print('Prepared',len(manifest),'production files and immutable authority references')
if __name__=='__main__':main()
