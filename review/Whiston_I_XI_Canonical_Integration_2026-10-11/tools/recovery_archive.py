"""Seal and independently restore the isolated candidate; no remote operation."""
from pathlib import Path
import datetime,hashlib,json,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[3];PACK=ROOT/'review/Whiston_I_XI_Canonical_Integration_2026-10-11'
PIN='663b8ce318f0aa247d304d8eeda5b8e76e7489c6'
CANON=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
SITE=Path('C:/workspace/Whiston-I-XI-Integration-runtime-20261011/standard-site')
OUT=Path('C:/workspace/Whiston-I-XI-Integration-Delivery-20261011');OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a,cwd=ROOT):return subprocess.check_output(['git',*a],cwd=cwd,stderr=subprocess.STDOUT)
assert not git('status','--porcelain').strip(),'Commit complete evidence before sealing'
assert json.loads((PACK/'INTEGRATION_CERTIFICATE.json').read_bytes())['status']=='CANONICAL-INTEGRATION-READY'
head=git('rev-parse','HEAD').decode().strip();branch=git('branch','--show-current').decode().strip()
assert git('rev-parse','HEAD',cwd=CANON).decode().strip()==PIN and not git('status','--porcelain',cwd=CANON).strip()
bundle=OUT/'integration.bundle';git('bundle','create',str(bundle),PIN+'..'+branch)
bundle_verification=git('bundle','verify',str(bundle)).decode()
patch=git('diff','--binary',PIN,head);(OUT/'IMPLEMENTATION.patch').write_bytes(patch)
scope=json.loads((PACK/'PRODUCTION_DIFF_SCOPE.json').read_bytes())['files']
focused=git('diff','--binary',PIN,head,'--',*scope);(OUT/'SOURCE_RENDERER_GUARDS.patch').write_bytes(focused)
receipt={'final_delivery_commit':head,'branch':branch,'pinned_canonical_commit':PIN,'original_prototype_commit':'0c1347a5a947ae5702cf60e4162d09d7510450e5',
 'commits':[dict(zip(['commit','subject'],line.split(' ',1))) for line in git('log','--reverse','--format=%H %s',PIN+'..'+head).decode().splitlines()],
 'bundle_prerequisite':PIN,'bundle_sha256':sha(bundle.read_bytes()),'patch_sha256':sha(patch),'focused_patch_sha256':sha(focused),
 'bundle_verification':bundle_verification,'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'no_merge_push_deployment':True}
(OUT/'DELIVERY_RECEIPT.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
items={}
changed=git('diff','--name-only',PIN,head).decode().splitlines()
for relative in changed:items['candidate/'+relative]=(ROOT/relative).read_bytes()
for name in ['integration.bundle','IMPLEMENTATION.patch','SOURCE_RENDERER_GUARDS.patch','DELIVERY_RECEIPT.json']:items[name]=(OUT/name).read_bytes()
items['RECOVERY.md']=(PACK/'RECOVERY.md').read_bytes()
items['tools/preview.cjs']=(ROOT/'review/Whiston_I_XI_Renderer_2026-10-11/tools/preview.cjs').read_bytes()
for folder in ['assets/js','assets/css','assets/xml','assets/data','assets/fonts','assets/img/brand']:
 for p in (SITE/folder).rglob('*'):
  if p.is_file():items['preview/'+p.relative_to(SITE).as_posix()]=p.read_bytes()
for route in ['antiquities','bellum-judaicum','contra-apionem','deh']:items['preview/'+route+'/index.html']=(SITE/route/'index.html').read_bytes()
manifest=[{'path':name,'bytes':len(body),'sha256':sha(body)} for name,body in sorted(items.items())]
manifest_bytes=(json.dumps(manifest,indent=2)+'\n').encode();items['CHECKSUMS.json']=manifest_bytes
(OUT/'CHECKSUMS.json').write_bytes(manifest_bytes)
archive=OUT/'Whiston-I-XI-Canonical-Integration-Ready.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,body in sorted(items.items()):z.writestr(name,body)
archive_hash=sha(archive.read_bytes());(OUT/(archive.name+'.sha256')).write_bytes((archive_hash+'  '+archive.name+'\n').encode())
for name in ['IMPLEMENTATION.patch','SOURCE_RENDERER_GUARDS.patch','integration.bundle']:(OUT/(name+'.sha256')).write_bytes((sha((OUT/name).read_bytes())+'  '+name+'\n').encode())
extraction=OUT/('verified-extraction-'+head[:7]);assert not extraction.exists(),'Use a fresh verification destination'
extraction.mkdir()
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name in z.namelist():
  target=(extraction/name).resolve();assert target.is_relative_to(extraction.resolve())
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(name))
 for row in json.loads(z.read('CHECKSUMS.json')):
  body=(extraction/row['path']).read_bytes();assert len(body)==row['bytes'] and sha(body)==row['sha256'],row['path']
for book in json.loads((PACK/'SOURCE_INVENTORY.json').read_bytes()):
 for source in book['outputs']:
  for prefix in ['candidate','preview']:assert sha((extraction/prefix/source['path']).read_bytes())==source['sha256']
clone=OUT/('verified-git-recovery-'+head[:7]);assert not clone.exists(),'Use a fresh Git recovery destination'
git('clone','--shared','--no-checkout','--config','core.autocrlf=false',str(CANON),str(clone))
git('fetch',str(extraction/'integration.bundle'),'refs/heads/'+branch+':refs/heads/recovered-integration',cwd=clone)
git('checkout','recovered-integration',cwd=clone)
assert git('rev-parse','HEAD',cwd=clone).decode().strip()==head and not git('status','--porcelain',cwd=clone).strip()
for relative in changed:assert (clone/relative).read_bytes()==(extraction/'candidate'/relative).read_bytes(),relative
original='review/Whiston_I_XI_Renderer_2026-10-11/CERTIFICATE.json'
assert (clone/original).read_bytes()==git('show','0c1347a5a947ae5702cf60e4162d09d7510450e5:'+original)
result={'status':'PASS','archive':str(archive),'archive_sha256':archive_hash,'archive_bytes':archive.stat().st_size,
 'archive_entries':len(items),'verified_manifest_entries':len(manifest),'CRC':'PASS','all_extracted_entry_hashes_verified':True,
 'all_12_candidate_and_preview_certified_sources_verified':True,'original_RENDERER_GO_certificate_preserved':True,
 'incremental_bundle_verified':True,'prerequisite':PIN,'actual_recovered_HEAD':head,'actual_recovered_git_clean':True,
 'all_changed_files_recovered_byte_identical':True,'verified_extraction':str(extraction),'verified_git_recovery':str(clone),
 'canonical_HEAD_after':git('rev-parse','HEAD',cwd=CANON).decode().strip(),'canonical_status_after':git('status','--porcelain',cwd=CANON).decode().strip()}
assert result['canonical_HEAD_after']==PIN and not result['canonical_status_after']
(OUT/'RECOVERY_VERIFICATION.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
print(json.dumps(result,indent=2))
