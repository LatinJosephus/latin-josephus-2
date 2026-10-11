"""Create and verify a local recovery archive; never contact a remote or merge."""
from pathlib import Path
import hashlib,json,subprocess,zipfile,datetime
ROOT=Path(__file__).resolve().parents[3];PACK=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11'
PIN='663b8ce318f0aa247d304d8eeda5b8e76e7489c6'
CANON=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
SITE=Path('C:/workspace/Whiston-I-XI-Renderer-runtime-20261011/site')
OUT=Path('C:/workspace/Whiston-I-XI-Renderer-Delivery-20261011');OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd,stderr=subprocess.STDOUT)
assert not git('status','--porcelain').strip(),'Commit the QA/report before packaging'
head=git('rev-parse','HEAD').decode().strip();branch=git('branch','--show-current').decode().strip()
certificate=json.loads((PACK/'CERTIFICATE.json').read_bytes());assert certificate['status'].startswith('RENDERER-GO')
bundle=OUT/'prototype.bundle'
git('bundle','create',str(bundle),PIN+'..'+branch)
verification=git('bundle','verify',str(bundle)).decode()
patch=git('diff','--binary',PIN,head);(OUT/'IMPLEMENTATION.patch').write_bytes(patch)
commits=[dict(zip(['commit','subject'],line.split(' ',1))) for line in git('log','--reverse','--format=%H %s',PIN+'..'+head).decode().splitlines()]
receipt={'final_commit':head,'branch':branch,'pinned_canonical_commit':PIN,'commits':commits,'implementation_bundle_prerequisite':PIN,
    'bundle_sha256':sha(bundle.read_bytes()),'patch_sha256':sha(patch),'bundle_verification':verification,
    'no_merge_push_deployment':True,'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(OUT/'DELIVERY_RECEIPT.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
items={}
for rel in git('diff','--name-only',PIN,head).decode().splitlines():items['prototype/'+rel]=(ROOT/rel).read_bytes()
for name in ['prototype.bundle','IMPLEMENTATION.patch','DELIVERY_RECEIPT.json']:items[name]=(OUT/name).read_bytes()
items['RECOVERY.md']=(PACK/'RECOVERY.md').read_bytes()
items['tools/preview.cjs']=(PACK/'tools/preview.cjs').read_bytes()
for folder in ['assets/js','assets/css','assets/xml','assets/data','assets/fonts','assets/img/brand']:
    for p in (SITE/folder).rglob('*'):
        if p.is_file():items['preview/'+p.relative_to(SITE).as_posix()]=p.read_bytes()
for route in ['antiquities','bellum-judaicum','contra-apionem','deh']:
    p=SITE/route/'index.html';items['preview/'+route+'/index.html']=p.read_bytes()
manifest=[{'path':name,'bytes':len(data),'sha256':sha(data)} for name,data in sorted(items.items())]
items['CHECKSUMS.json']=(json.dumps(manifest,indent=2)+'\n').encode()
archive=OUT/'Whiston-I-XI-Renderer-Prototype-Certified.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted(items.items()):z.writestr(name,data)
archive_hash=sha(archive.read_bytes())
(OUT/(archive.name+'.sha256')).write_bytes((archive_hash+'  '+archive.name+'\n').encode())
recovery=OUT/'verified-extraction';recovery.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name in z.namelist():
        target=(recovery/name).resolve()
        assert target.is_relative_to(recovery.resolve()),name
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(name))
    recovered_manifest=json.loads(z.read('CHECKSUMS.json'))
    for row in recovered_manifest:
        data=(recovery/row['path']).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256'],row['path']
for book in json.loads((PACK/'SOURCE_INVENTORY.json').read_bytes()):
    for source in book['outputs']:
        assert sha((recovery/'prototype'/source['path']).read_bytes())==source['sha256']
        assert sha((recovery/'preview'/source['path']).read_bytes())==source['sha256']
clone=OUT/'verified-git-recovery'
assert not clone.exists(),'Choose a fresh recovery verification destination; never remove an existing checkout'
git('clone','--shared','--no-checkout',str(CANON),str(clone))
git('fetch',str(recovery/'prototype.bundle'),'refs/heads/'+branch+':refs/heads/recovered-prototype',cwd=clone)
git('checkout','recovered-prototype',cwd=clone)
assert git('rev-parse','HEAD',cwd=clone).decode().strip()==head
assert not git('status','--porcelain',cwd=clone).strip()
for rel in git('diff','--name-only',PIN,head).decode().splitlines():
    assert (clone/rel).read_bytes()==(recovery/'prototype'/rel).read_bytes(),rel
result={'status':'PASS','archive':str(archive),'archive_sha256':archive_hash,'archive_bytes':archive.stat().st_size,
    'archive_entries':len(items),'verified_manifest_files':len(manifest),'CRC':'PASS','all_extracted_entry_hashes_verified':True,
    'all_twelve_certified_XML_sources_verified':True,'incremental_bundle_verified':True,'pinned_prerequisite':PIN,
    'local_git_recovery_HEAD':head,'local_git_recovery_clean':True,'all_changed_files_byte_identical_in_recovery_checkout':True,
    'recovery_prerequisite_note':'Git recovery requires a repository containing the pinned canonical commit; the bundled static preview is independently runnable.',
    'verification_directory':str(recovery),'git_recovery_directory':str(clone)}
(OUT/'RECOVERY_VERIFICATION.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
print(json.dumps(result,indent=2))
