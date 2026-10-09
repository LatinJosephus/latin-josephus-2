"""Read-only final repository/source gate; writes only this batch's new QA file."""
from pathlib import Path
import subprocess,json,hashlib,re
W=Path(r'C:\workspace\LatinJosephus-antiquities-niese-08-10');C=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development');P=W/'review/Antiquities_Niese_Batch_08_10_2026-10-08';H='1cf003beeb03f7b0acf2c42057ace062cdb7ebff'
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=root).decode('utf-8').strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
advance=json.loads((P/'CANONICAL_ADVANCE.json').read_text());CH=advance['current_canonical_HEAD']
files=[];totals={}
for tag,root,ref in [('worktree',W,H),('canonical',C,CH)]:
 entries=subprocess.check_output(['git','--no-optional-locks','ls-tree','-r','-z',ref],cwd=root).split(b'\0');count=0
 for entry in entries:
  if not entry:continue
  meta,name=entry.split(b'\t',1);mode,kind,expected=meta.decode().split();name=name.decode();assert kind=='blob',(name,kind)
  raw=(root/name).read_bytes();direct=blob(raw)==expected;lf=blob(raw.replace(b'\r\n',b'\n'))==expected
  assert direct or lf,('Tracked source differs from its pinned HEAD',tag,name)
  files.append(dict(checkout=tag,path=name,HEAD_blob_sha1=expected,sha256=hashlib.sha256(raw).hexdigest(),matches_HEAD_blob=direct,matches_HEAD_after_CRLF_checkout_normalization=lf));count+=1
 totals[tag]=count
assert git(W,'branch','--show-current')=='antiquities-niese-08-10';assert git(C,'branch','--show-current')=='v2-development'
assert git(W,'rev-parse','HEAD')==H;assert git(C,'rev-parse','HEAD')==git(C,'rev-parse','origin/v2-development')==CH
assert git(C,'status','--porcelain')=='';assert git(W,'diff','--name-only')=='';assert git(W,'diff','--cached','--name-only')==''
freeze=json.loads((P/'FROZEN_SOURCE_VERIFICATION.json').read_text())
for f in freeze:
 assert sha(Path(f['manifest']))==f['manifest_sha256']
 for r in f['files']:assert sha(Path(f['root'])/r['path'])==r['actual']==r['expected']
pdfs=json.loads((P/'pdf-metadata.json').read_text())
for x in pdfs:assert sha(Path(x['path']))==x['sha256']
for x in json.loads((P/'METHOD_SOURCE_MANIFEST.json').read_text(encoding='utf-8')):assert sha(Path(x['path']))==x['sha256']
for x in json.loads((P/'SOURCE_SEARCH.json').read_text(encoding='utf-8'))['selected_related_resources']:assert sha(Path(x['path']))==x['sha256']
out=dict(result='PASS',canonical_branch=git(C,'branch','--show-current'),canonical_HEAD=CH,origin_tracking_ref_HEAD=CH,canonical_advance='CANONICAL_ADVANCE.json',remote_scope='Local origin/v2-development tracking reference; no fetch/push/configuration change performed.',canonical_status='CLEAN',worktree_branch=git(W,'branch','--show-current'),worktree_HEAD=H,worktree_status=git(W,'status','--porcelain'),staged_files=[],tracked_modified_files=[],tracked_files_verified=totals,all_tracked_blobs_unchanged=True,frozen_manifest_and_file_hashes_rechecked=True,printed_PDF_hashes_rechecked=True,files=files)
(P/'REPOSITORY_INTEGRITY_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Repository/source gate PASS',len(files),'tracked files unchanged; canonical clean; no staged changes.')
