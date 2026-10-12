"""Seal a fully verified stage, then independently restore it before further work."""
import pathlib,json,subprocess,zipfile,hashlib,shutil,sys
BASE=pathlib.Path(__file__).parent;ROOT=BASE/'candidate';PACK=ROOT/'review/Whiston_XVI_XX_Integration_2026-10-12';OUT=BASE/'exports';OUT.mkdir(exist_ok=True)
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda b:hashlib.sha256(b).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
git=lambda *args:subprocess.check_output(['git','-C',str(ROOT),*args])
stage=sys.argv[1];last={'A':17,'B':19,'C':20}[stage];new_count={'A':759,'B':1504,'C':1772}[stage]
assert load(PACK/'QA_RECEIPT.json')['last_book']==last
verification=json.loads(subprocess.check_output([sys.executable,str(PACK/'tools/verify_candidate.py')]))
assert verification['status']=='PASS';save(PACK/f'STAGE_{stage}_SOURCE_PRESERVATION.json',verification)
for name in ['bundle-check.log','standard-build.log','generated-source-verification.json','reader-corpus-guard.json']:
 target=PACK/'execution-logs'/f'Stage-{stage}-{name}';target.parent.mkdir(exist_ok=True);shutil.copy2(BASE/'runtime'/name,target)
guard=load(BASE/'runtime/reader-corpus-guard.json');assert guard['status']=='PASS' and guard['all_production_XML_parsed'] and len(guard['negative_tests'])==8
(PACK/'RECOVERY.md').write_text(f'''# Isolated Whiston XVI–XX recovery

Stage {stage} is certified through Book {last}, adding {new_count} English intervals to the pinned I–XV baseline. Overall status is {"COMPLETE CANDIDATE; FINAL RECONCILIATION PENDING" if stage=="C" else "PARTIAL — NOT CERTIFIED FOR ALL XVI–XX"}.

Canonical baseline: f6fa17f7616bf9ce046c28086b1a1448a9f8d049. No merge, push, preview modification or deployment is authorized. Do not use a shared checkout for recovery.

Verify the ZIP SHA-256, ZIP CRC and every CHECKSUMS.json member, then extract into a fresh owned directory. Initialize a private candidate with core.autocrlf=false, fetch the complete candidate-full.bundle, and check out the full identity in DELIVERY.json. All source-delivery identities are named recovery refs. No canonical repository, network or publication is needed. Run review/Whiston_XVI_XX_Integration_2026-10-12/tools/verify_candidate.py in the restored candidate. It independently walks all enabled frozen XML, checks exact source bytes and reconstruction, preserves all prior tracked sources, and reconciles the actual rendered records.

Preview reader HTML and assets are supplied for local inspection. Browser reproduction needs Node, Playwright and Chrome; create a private baseline by restoring the pinned commit from the bundle into another new checkout, and set WHISTON_SITE to the extracted preview. Browser hooks expose settled state only; source text and selection functions are unaltered. Use tools/browser_qa.cjs with QA_BOOKS and QA_REPORT_FILE, tools/structural_qa.cjs and the saved independent oracles. Stage QA reports and oracle populations are specified in QA_RECEIPT.json. A fresh standard build uses all configured plugins and the ordinary bundle check and bundle exec jekyll build --destination commands; retain all approved corpus/native guards.

Rollback is to discard this isolated candidate or create a fresh private checkout at the pinned baseline. Never reset, clean, stash, switch branches or overwrite canonical development. Stage A and B archives stay immutable after sealing. Stop at isolated inspection or certification.
''',encoding='utf-8')
shutil.copy2(__file__,PACK/'tools/stage_packaging_historical.py')
paths=['.gitattributes','assets/js/renderTei.js','_docs/reader-corpus-integrity.json','bin/reader-corpus-integrity.mjs','review/Whiston_XVI_XX_Integration_2026-10-12']+[f'assets/xml/antiquities/English/book-{n:02}.xml' for n in range(16,last+1)]
git('add',*paths);git('commit','-m',f'Certify isolated Whiston stage {stage} through book {last}: {new_count} new exact English intervals')
commit=git('rev-parse','HEAD').decode().strip()
for r in load(PACK/'SOURCE_INVENTORY.json'):git('update-ref',f'refs/recovery/source-book-{r["book"]}',r['delivery_commit'])
bundle=OUT/f'Stage-{stage}-full.bundle';git('bundle','create',str(bundle),'--all','HEAD');git('bundle','verify',str(bundle))
patch=OUT/f'Stage-{stage}.patch';patch.write_bytes(git('diff','--binary',load(PACK/'BASELINE.json')['commit'],commit))
delivery=dict(stage=stage,candidate_commit=commit,baseline_commit=load(PACK/'BASELINE.json')['commit'],enabled_through=last,new_intervals=new_count,full_bundle_SHA256=sha(bundle.read_bytes()),independent_verification=verification)
files={'candidate-full.bundle':bundle,'candidate.patch':patch};site=BASE/'runtime/standard-site'
for p in PACK.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:files['review/'+p.relative_to(PACK).as_posix()]=p
for folder in ['assets/xml','assets/js','assets/css','assets/data','assets/fonts','assets/img','antiquities','bellum-judaicum','contra-apionem','deh']:
 for p in (site/folder).rglob('*'):
  if p.is_file():files['preview/'+p.relative_to(site).as_posix()]=p
manifest=[dict(path=k,sha256=sha(p.read_bytes()),bytes=p.stat().st_size) for k,p in sorted(files.items())]
delivery_bytes=(json.dumps(delivery,indent=2)+'\n').encode();manifest.append(dict(path='DELIVERY.json',sha256=sha(delivery_bytes),bytes=len(delivery_bytes)))
archive=OUT/f'Stage-{stage}-RECOVERABLE.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for k,p in files.items():z.write(p,k)
 z.writestr('DELIVERY.json',delivery_bytes);z.writestr('CHECKSUMS.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for r in manifest:assert sha(z.read(r['path']))==r['sha256']
record=dict(status='PASS',stage=stage,candidate_commit=commit,archive=str(archive),SHA256=sha(archive.read_bytes()),verified_members=len(manifest),CRC='PASS',full_bundle_verified=True,new_intervals=new_count)
save(OUT/f'Stage-{stage}.verification.json',record);(OUT/f'Stage-{stage}-RECOVERABLE.zip.sha256').write_text(record['SHA256']+'  '+archive.name+'\n',encoding='utf-8')
# Fresh recovery uses only archive bytes. It does not read the live candidate or canonical.
recover=BASE/f'stage-{stage}-offline-recovery';assert not recover.exists();recover.mkdir()
with zipfile.ZipFile(archive) as z:
 for name in z.namelist():assert (recover/name).resolve().is_relative_to(recover.resolve())
 z.extractall(recover)
for r in manifest:assert sha((recover/r['path']).read_bytes())==r['sha256']
repo=recover/'candidate';subprocess.check_call(['git','init','--separate-git-dir',str(recover/'repository.git'),str(repo)])
g=lambda *a:subprocess.check_output(['git','-C',str(repo),*a])
g('config','core.autocrlf','false');g('fetch',str(recover/'candidate-full.bundle'),'HEAD');g('checkout','--detach',commit)
restored=json.loads(subprocess.check_output([sys.executable,str(repo/'review/Whiston_XVI_XX_Integration_2026-10-12/tools/verify_candidate.py')]))
assert restored==verification;assert not g('status','--porcelain=v1')
save(OUT/f'Stage-{stage}.offline-recovery.json',dict(status='PASS',stage=stage,archive_SHA256=record['SHA256'],candidate_commit=commit,manifest_verified=len(manifest),ZIP_CRC='PASS',fresh_private_checkout=True,no_canonical_or_network_dependency=True,source_and_display_reconciliation=restored))
print(json.dumps(record));print('Fresh offline recovery PASS; safe to continue after this stage')
