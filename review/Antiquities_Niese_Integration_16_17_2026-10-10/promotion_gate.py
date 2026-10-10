from integration_common import *
tip=git('rev-parse','HEAD').decode().strip();cert=read(D/'CERTIFICATION.json')
assert cert['status']=='PASS_READY_FOR_SAFE_CANONICAL_PROMOTION'
assert not git('status','--porcelain').strip()
assert not git('status','--porcelain',cwd=CAN).strip()
assert git('branch','--show-current',cwd=CAN).decode().strip()=='v2-development'
subprocess.run(['git','fetch','origin','v2-development'],cwd=CAN,check=True)
live=git('ls-remote','origin','refs/heads/v2-development',cwd=CAN).decode().split()[0]
canonical=git('rev-parse','HEAD',cwd=CAN).decode().strip();tracking=git('rev-parse','origin/v2-development').decode().strip()
assert canonical==START and live==START and tracking==START,('Canonical advanced; incorporate and recertify before promotion',canonical,live,tracking)
assert git('rev-parse','HEAD',cwd=SOURCE_ROOT).decode().strip()==SOURCE
assert not git('status','--porcelain',cwd=SOURCE_ROOT).strip()
for x in read(D/'CANONICAL_START_FILES.json'):assert sha((CAN/x['path']).read_bytes())==x['sha256'],x['path']
for x in read(D/'FILE_MANIFEST.json')['files']:assert sha((ROOT/x['path']).read_bytes())==x['sha256'],x['path']
for commit in [START,SOURCE,*cert['incoming_complete_history']]:assert ancestor(commit,tip)
save(R/'PRE_PROMOTION_WORKTREE_INVENTORY.json',dict(time_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),inventory=git('worktree','list','--porcelain').decode(),only_owned_integration_and_authorized_canonical_may_be_modified=True))
save(R/'PRE_PROMOTION_GATE.json',dict(status='PASS',time_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),final_integration_tip=tip,canonical=canonical,direct_remote=live,fetched_remote=tracking,canonical_clean=True,integration_clean=True,source_clean=True,source_tip=SOURCE,all_3799_canonical_working_files_untouched_before_promotion=True,certification_sha256=sha((D/'CERTIFICATION.json').read_bytes()),manifest_sha256=sha((D/'FILE_MANIFEST.json').read_bytes()),normal_fast_forward_and_push_authorized=True,public_preview_publication=False))
print('PASS promotion gate',tip,canonical,live)
