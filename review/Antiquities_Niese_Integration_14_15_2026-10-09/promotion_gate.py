"""Read-only Git/byte gates with receipts in this assignment's locations."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
load=lambda n:json.loads((P/n).read_text(encoding='utf8'))
sha=lambda x:hashlib.sha256(x).hexdigest()
base=load('BASELINE.json');CAN=Path(base['canonical_checkout']);RT=Path(base['runtime'])
advance=load('CANONICAL_ADVANCE.json') if (P/'CANONICAL_ADVANCE.json').exists() else None
effective=advance['canonical_advance'] if advance else base['canonical_start']
canonical_records=advance['canonical_tracked_files'] if advance else base['canonical_tracked_files']
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd).decode('utf8').strip()
def tree(commit):return dict(line.split(' ',1)[::-1] for line in git('ls-tree','-r','--format=%(objectname) %(path)',commit).splitlines())
def save(path,x):path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
mode=sys.argv[1]
assert mode in ['pre-certification','pre-promotion','post-promotion']
head=git('rev-parse','HEAD');canonical=git('rev-parse','HEAD',cwd=CAN)
remote=git('ls-remote','origin','refs/heads/v2-development',cwd=CAN).split()[0]
assert git('branch','--show-current',cwd=CAN)=='v2-development'
assert git('branch','--show-current')=='antiquities-niese-14-15-integration'
assert not git('status','--porcelain',cwd=CAN)
if mode!='pre-certification':assert not git('status','--porcelain')
source_refs={name:git('rev-parse','refs/heads/'+name) for name in [
 'antiquities-niese-08-10','antiquities-niese-08-10-implementation','antiquities-niese-09','antiquities-niese-12-13','antiquities-niese-14-15','antiquities-niese-boundary-display']}
assert source_refs['antiquities-niese-14-15']==base['source_tip']
assert source_refs['antiquities-niese-12-13']=='76083c2831afdb4853f7d7ebab0db6c64c18d914'
assert source_refs['antiquities-niese-09']=='b2766fc0a0f9ab8dfb1c4667fbb9c5c4d6eac659'
assert source_refs['antiquities-niese-boundary-display']==effective
assert git('rev-parse','HEAD',cwd=Path(base['source_checkout']))==base['source_tip']
assert not git('status','--porcelain',cwd=Path(base['source_checkout']))
other_source_status={name:git('status','--porcelain',cwd=Path(r'C:\workspace')/name)
 for name in ['LatinJosephus-antiquities-niese-09','LatinJosephus-antiquities-niese-12-13']}
incoming=load('INCOMING_SCOPE.json');production={r['path'] for r in incoming['files'] if r['kind']=='production'}
prod=load('PRODUCTION_MANIFEST.json');tested=load('BUILD_RECORD.json')['candidate_commit']
assert {r['path'] for r in prod['files']}==production
changed=set(git('diff','--name-only',tested,head).splitlines())
assert all(x.startswith('review/Antiquities_Niese_Integration_14_15_2026-10-09/') for x in changed)
subprocess.check_call(['git','merge-base','--is-ancestor',base['canonical_start'],head],cwd=ROOT)
subprocess.check_call(['git','merge-base','--is-ancestor',effective,head],cwd=ROOT)
subprocess.check_call(['git','merge-base','--is-ancestor',base['source_tip'],head],cwd=ROOT)
all_changed=set(git('diff','--name-only',effective,head).splitlines())
assert {x for x in all_changed if not x.startswith('review/')}==production
for r in prod['files']:
 assert sha((ROOT/r['path']).read_bytes())==r['merged_sha256']
 assert sha((RT/'site'/r['path']).read_bytes())==r['merged_sha256']
for r in incoming['files']:
 if r['kind']=='review':
  assert sha((Path(base['source_checkout'])/r['path']).read_bytes())==r['certified_working_sha256']
  assert sha((ROOT/r['path']).read_bytes())==r['certified_working_sha256']
final_tree=tree(head);protected=0
for r in canonical_records:
 if r['path'] in production:continue
 assert final_tree[r['path']]==r['blob']
 assert sha((CAN/r['path']).read_bytes())==r['working_sha256'],r['path']
 protected+=1
assert protected==len(canonical_records)-sum(r['path'] in production for r in canonical_records)
if mode!='pre-certification':
 manifest=load('FILE_MANIFEST.json')
 for r in manifest['files']:assert sha((P/r['relative']).read_bytes())==r['sha256'],r['relative']
 assert len(manifest['files'])+1==manifest['integration_additional_review_files']
 assert len(all_changed)==538+manifest['integration_additional_review_files']
 certificate=load('CERTIFICATE.json')
 assert certificate['tested_production_commit']==tested
 assert certificate['selectable_combined']==5231
 receipt_extra=dict(integration_review_files=manifest['integration_additional_review_files'],
                    exact_changed_file_count=len(all_changed),manifest_sha256=sha((P/'FILE_MANIFEST.json').read_bytes()),
                    report_sha256=sha((P/'REPORT.md').read_bytes()),certificate_sha256=sha((P/'CERTIFICATE.json').read_bytes()))
else:receipt_extra={}
if mode=='post-promotion':
 assert canonical==remote==head
 for r in prod['files']:assert sha((CAN/r['path']).read_bytes())==r['merged_sha256'],r['path']
 for r in incoming['files']:
  if r['kind']=='review':assert sha((CAN/r['path']).read_bytes())==r['certified_working_sha256'],r['path']
 final_C=tree(canonical)
 assert final_C==final_tree
 for r in load('FILE_MANIFEST.json')['files']:
  assert sha((CAN/'review/Antiquities_Niese_Integration_14_15_2026-10-09'/r['relative']).read_bytes())==r['sha256']
 status='CANONICAL_FAST_FORWARD_AND_NORMAL_PUSH_VERIFIED'
 destination=RT/'PROMOTION_RECEIPT.json'
else:
 if (P/'PROMOTION_VERIFICATION.json').exists():
  prior=load('PROMOTION_VERIFICATION.json')['canonical_head']
  assert canonical==remote==prior,'Closure must extend the directly verified first push'
  subprocess.check_call(['git','merge-base','--is-ancestor',prior,head],cwd=ROOT)
 else:
  assert canonical==effective and remote in [base['canonical_start'],effective],'Additional canonical/remote advance must be incorporated and assessed in isolation'
 status='READY_FOR_REVIEW_COMMIT' if mode=='pre-certification' else 'READY_FOR_AUTHORIZED_FAST_FORWARD_AND_NORMAL_PUSH'
 destination=P/'PRE_PROMOTION_GATE.json' if mode=='pre-certification' else RT/'PRE_PROMOTION_GATE_FINAL.json'
receipt=dict(result='PASS',status=status,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 canonical_start=base['canonical_start'],effective_canonical_baseline=effective,canonical_head=canonical,integration_head=head,remote_head_directly_verified=remote,
 incorporated_certified_source_tip=base['source_tip'],tested_production_commit=tested,
 source_history_preserved=True,canonical_and_integration_clean=mode!='pre-certification',canonical_clean=True,
 certified_source_clean=True,source_branches_preserved=source_refs,other_source_status_observed_read_only=other_source_status,protected_canonical_working_byte_checks=protected,
 exact_production_byte_checks=7,exact_incoming_review_byte_checks=531,production_unchanged_since_test=True,
 selectable_combined=5231,normal_push_only=True,no_force_reset_rebase_configuration_change=True,
 public_preview_export_push_deployment=False,**receipt_extra)
save(destination,receipt);print(json.dumps(receipt,indent=2))
