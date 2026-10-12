"""Package and freshly restore the final isolated integration; no canonical writes."""
import pathlib,json,subprocess,zipfile,hashlib,shutil,datetime
BASE=pathlib.Path(__file__).parent;ROOT=BASE/'candidate';PACK=ROOT/'review/Whiston_XVI_XX_Integration_2026-10-12';OUT=BASE/'exports';PIN='f6fa17f7616bf9ce046c28086b1a1448a9f8d049';CANON=pathlib.Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def file_sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
git=lambda *a:subprocess.check_output(['git','-C',str(ROOT),*a])
assert load(PACK/'INTEGRATION_CERTIFICATE.json')['verdict']=='WHISTON XVI–XX CANONICAL-INTEGRATION-READY'
recovery=(PACK/'RECOVERY.md').read_text(encoding='utf-8')
recovery=recovery.replace('Stage C is certified through Book 20, adding 1772 English intervals to the pinned I–XV baseline. Overall status is COMPLETE CANDIDATE; FINAL RECONCILIATION PENDING.','Final candidate certification is complete: all 7376 exact English intervals, the new 1772 XVI–XX intervals, containing views, mandatory regressions, source preservation and canonical compatibility pass. See RECOVERY_FINAL.md for complete final delivery recovery. Stage A/B/C archive copies of this file retain their original checkpoint scope.')
(PACK/'RECOVERY.md').write_text(recovery,encoding='utf-8')
(PACK/'RECOVERY_FINAL.md').write_text('''# Final isolated candidate recovery and rollback

Verify FINAL.verification.json and the companion ZIP SHA-256, then extract into an empty owned directory. CHECKSUMS.json seals every delivered member; require every SHA-256 and ZIP CRC to pass. Stage A, B and C archives and receipts remain independent and immutable. The full bundle has no prerequisites and includes all source-delivery refs and historical regression baselines.

Create a private checkout with `git init --separate-git-dir repository.git candidate`, set local `core.autocrlf=false`, fetch `candidate-full.bundle` HEAD, and check out the exact full candidate commit in DELIVERY.json. Use only this owned checkout. The -text attributes preserve all newly integrated physical source bytes. Do not refer to the shared canonical repository. Run `python candidate/review/Whiston_XVI_XX_Integration_2026-10-12/tools/verify_candidate.py`. It creates no files unless --report is supplied. This independently walks all 7,376 frozen XML intervals, checks all approved byte streams and unchanged prior files, and reconciles saved actual browser evidence. This check is independent source/evidence reproduction; it does not masquerade as a new browser execution.

For fresh live-browser reproduction, run tools/prepare_reproduction.py from the recovered candidate. It refuses an existing baseline, creates a private baseline at f6fa17f7616bf9ce046c28086b1a1448a9f8d049 from the recovered bundle, and copies the archived preview into an owned runtime/standard-site. Run tools/run_browser_reproduction.ps1 -PlaywrightModule <absolute Playwright module path>. This freshly executes all 7,376 actual English displays, containing views and the structural/navigation/availability/DEH/Lodge controls. The archive's original evidence remains immutable; new reports are only in the recovered checkout. Chrome at C:/Program Files/Google/Chrome/Application/chrome.exe and Node/Python are the recorded local runtime; native legacy tests report their unchanged HTMLCollection iteration adapter and external shell/CDN errors separately.

For a fresh standard build, copy the recovered review/Whiston_XVI_XX_Integration_2026-10-12/build/Gemfile.lock to the recovered candidate root, configure the recorded Ruby/plugin dependencies, and run ordinary bundle check and bundle exec jekyll build --destination ../runtime/standard-site --disable-disk-cache. Keep every configured plugin. Run bin/prepare-reader-publication.mjs and bin/reader-corpus-qa.mjs --site ../runtime/standard-site. They validate exact hash-bound production authorities; they do not authorize deployment. The already-built preview supports independent offline source inspection without a Ruby install.

Run native full Bellum with bin/bellum-greek-range-qa.mjs --site ../runtime/standard-site --out ../runtime/native-bellum --module-root <node-modules> --browser <chrome>. Run tools/native_lodge_qa.mjs with the same site/module/browser flags. Both historical baseline objects are in the complete bundle. Set TEMP and TMP to an owned runtime/tmp directory for all negative-test copies. The five original delivery archives and the immutable Lodge master are supplied in source-recovery. Run bin/lodge1602-bellum-qa.ps1 -MasterZip <recovered source-recovery/Lodge1602_Bellum_FINAL_ADJUDICATED_20261003.zip> -RepoRoot <owned candidate> -SelfTest -NoWrite to repeat the master and nine deliberate-corruption controls.

Review candidate.patch, production-only.patch, SOURCE_INVENTORY.json and IMPLEMENTATION_REVIEW.json before any later separately authorized integration. Read GLOBAL_INTEGRATION_REPORT.txt for scope and retained qualifications. Stage-specific RECOVERY.md records inside the sealed archives describe their partial checkpoint scope. Final commit and ZIP identity are external to the committed dossier to avoid self-reference.

Rollback is to abandon the isolated candidate or restore the pinned baseline in a new private checkout. Never reset, clean, stash, switch branches, overwrite source or move files in canonical development or another worker's checkout. If canonical later advances, prepare a fresh isolated reconciliation and rerun affected tests; do not automatically rebase this certified candidate.

STOP after recovery, review or isolated certification. No canonical merge, push, public-preview modification, deployment or scholarly segmentation change is authorized.
''',encoding='utf-8')
shutil.copy2(__file__,PACK/'tools/final_packaging_historical.py')
for name in ['run-build.ps1','run-final-qa.ps1','run-native-qa.ps1','implementation_review.py','source_archive_recheck.py','enhance_final.py']:
 shutil.copy2(BASE/name,PACK/'tools'/('historical-'+name))
# Standard whitespace guard, retaining default blank/indent checks and Windows CR representation.
product=['.gitattributes','_docs/reader-corpus-integrity.json','bin/reader-corpus-integrity.mjs','assets/js/renderTei.js']+[f'assets/xml/antiquities/English/book-{n:02}.xml' for n in range(16,21)]
check=subprocess.run(['git','-C',str(ROOT),'-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--check',PIN,'--',*product],capture_output=True)
(PACK/'PRODUCTION_DIFF_WHITESPACE_CHECK.log').write_bytes(check.stdout+check.stderr);assert check.returncode==0,'Production whitespace guard failed'
head=subprocess.check_output(['git','--no-optional-locks','-C',str(CANON),'rev-parse','HEAD']).decode().strip();assert head==PIN
assert not subprocess.check_output(['git','--no-optional-locks','-C',str(CANON),'status','--porcelain=v1'])
git('add',*product,'review/Whiston_XVI_XX_Integration_2026-10-12');git('commit','-m','Certify all 7376 exact Whiston Antiquities intervals in isolated XVI-XX integration candidate')
commit=git('rev-parse','HEAD').decode().strip();assert not git('status','--porcelain=v1')
bundle=OUT/'candidate-full.bundle';git('bundle','create',str(bundle),'--all','HEAD');git('bundle','verify',str(bundle))
patch=OUT/'candidate.patch';patch.write_bytes(git('diff','--binary',PIN,commit));production=OUT/'production-only.patch';production.write_bytes(git('diff','--binary',PIN,commit,'--',*product))
inventory=git('diff','--name-status',PIN,commit).decode();(OUT/'CHANGE_INVENTORY.txt').write_text(inventory,encoding='utf-8')
delivery=dict(verdict='WHISTON XVI–XX CANONICAL-INTEGRATION-READY',candidate_commit=commit,canonical_baseline=PIN,candidate_branch=git('branch','--show-current').decode().strip(),new_intervals=1772,cumulative_intervals=7376,stage_commits={s:load(OUT/f'Stage-{s}.verification.json')['candidate_commit'] for s in ['A','B','C']},full_bundle_SHA256=file_sha(bundle),production_diff_SHA256=file_sha(production),canonical_clean_and_compatible=True,authorization='Isolated candidate only; STOP before merge, push or publication')
save(OUT/'DELIVERY.json',delivery)
files={'candidate-full.bundle':bundle,'candidate.patch':patch,'production-only.patch':production,'CHANGE_INVENTORY.txt':OUT/'CHANGE_INVENTORY.txt','DELIVERY.json':OUT/'DELIVERY.json'}
for p in PACK.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:files['review/'+p.relative_to(PACK).as_posix()]=p
for stage in ['A','B','C']:
 for suffix in ['-RECOVERABLE.zip','-RECOVERABLE.zip.sha256','.verification.json','.offline-recovery.json']:
  p=OUT/f'Stage-{stage}{suffix}';files['stages/'+p.name]=p
for p in (BASE/'source-recovery').glob('*.zip'):files['source-recovery/'+p.name]=p
site=BASE/'runtime/standard-site'
for folder in ['assets/xml','assets/js','assets/css','assets/data','assets/fonts','assets/img','antiquities','bellum-judaicum','contra-apionem','deh']:
 for p in (site/folder).rglob('*'):
  if p.is_file():files['preview/'+p.relative_to(site).as_posix()]=p
manifest=[dict(path=k,sha256=file_sha(p),bytes=p.stat().st_size) for k,p in sorted(files.items())]
save(OUT/'FINAL_MANIFEST.json',manifest);archive=OUT/'Whiston-XVI-XX-FINAL-RECOVERY.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for k,p in files.items():z.write(p,k)
 z.writestr('CHECKSUMS.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(set(z.namelist()))==len(manifest)+1
 for r in manifest:
  with z.open(r['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
record=dict(status='PASS',verdict=delivery['verdict'],candidate_commit=commit,baseline_commit=PIN,archive=str(archive),SHA256=file_sha(archive),manifest_SHA256=file_sha(OUT/'FINAL_MANIFEST.json'),bytes=archive.stat().st_size,manifest_verified_members=len(manifest),ZIP_CRC='PASS',full_bundle_no_prerequisites=True)
save(OUT/'FINAL.verification.json',record);(OUT/(archive.name+'.sha256')).write_text(record['SHA256']+'  '+archive.name+'\n',encoding='utf-8')
# Restore only archive bytes, no dependency on canonical or the live candidate.
recover=BASE/'final-offline-recovery';assert not recover.exists();recover.mkdir()
with zipfile.ZipFile(archive) as z:
 for name in z.namelist():assert (recover/name).resolve().is_relative_to(recover.resolve())
 z.extractall(recover)
for r in manifest:assert file_sha(recover/r['path'])==r['sha256']
repo=recover/'candidate';subprocess.check_call(['git','init','--separate-git-dir',str(recover/'repository.git'),str(repo)])
g=lambda *a:subprocess.check_output(['git','-C',str(repo),*a])
g('config','core.autocrlf','false');g('fetch',str(recover/'candidate-full.bundle'),'HEAD');g('checkout','--detach',commit)
verification=json.loads(subprocess.check_output(['python',str(repo/'review/Whiston_XVI_XX_Integration_2026-10-12/tools/verify_candidate.py')]))
assert verification==load(PACK/'FINAL_SOURCE_PRESERVATION.json') and not g('status','--porcelain=v1')
source_history=[]
for source in load(repo/'review/Whiston_XVI_XX_Integration_2026-10-12/SOURCE_INVENTORY.json'):
 assert g('rev-parse',source['delivery_commit']).decode().strip()==source['delivery_commit']
 assert g('cat-file','-t',source['delivery_commit']).decode().strip()=='commit'
 blob=g('show',source['delivery_commit']+':'+source['file'])
 assert hashlib.sha256(blob).hexdigest()==source['delivery_blob_sha256']
 source_history.append(dict(book=source['book'],delivery_commit=source['delivery_commit'],Git_blob_SHA256=hashlib.sha256(blob).hexdigest(),verified=True))
receipt=dict(status='PASS',archive_SHA256=record['SHA256'],candidate_commit=commit,verified_members=len(manifest),ZIP_CRC='PASS',fresh_private_checkout=True,canonical_or_network_dependency=False,new_source_bytes_preserved=True,independent_XML_intervals=7376,actual_display_records_reconciled=7376,three_stage_archives_preserved=True,five_original_delivery_commits_and_blobs=source_history,verification=verification)
save(OUT/'FINAL.offline-recovery.json',receipt)
assert subprocess.check_output(['git','--no-optional-locks','-C',str(CANON),'rev-parse','HEAD']).decode().strip()==PIN
assert not subprocess.check_output(['git','--no-optional-locks','-C',str(CANON),'status','--porcelain=v1'])
assert not git('status','--porcelain=v1')
print(json.dumps(record));print(json.dumps(delivery));print('Complete final archive and fresh offline recovery PASS; STOP at isolated certification')
