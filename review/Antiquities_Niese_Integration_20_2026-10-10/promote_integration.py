"""Authorized normal canonical promotion; receipts stay outside Git to preserve clean final checkouts."""
from integration_common import *
from datetime import datetime,timezone
def run(args,cwd=ROOT):
    r=subprocess.run(['git',*args],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    events.append(dict(command=['git',*args],cwd=str(cwd),exit_code=r.returncode,output=r.stdout.decode('utf-8',errors='replace')))
    save(receipt_path,dict(status='PROMOTION_IN_PROGRESS',events=events,started=started))
    assert r.returncode==0,events[-1]
    return r.stdout.decode().strip()
events=[];started=datetime.now(timezone.utc).isoformat();receipt_path=RUNTIME/'PROMOTION_RECEIPT.json'
def main():
    cert=read(PACK/'CERTIFICATE.json');assert cert['status']=='PASS' and cert['combined_identities']==7350
    target=run(['rev-parse','HEAD']);assert run(['status','--porcelain'])==''
    assert run(['branch','--show-current'])=='antiquities-niese-20-integration'
    production=read(PACK/'SOURCE_INTEGRITY.json')['production_files']
    for rel,p in production.items():assert sha(git('show','HEAD:'+rel))==p['sha256']
    run(['fetch','origin'],CANON)
    local_before=run(['rev-parse','HEAD'],CANON);remote_before=run(['ls-remote','origin','refs/heads/v2-development'],CANON).split()[0]
    assert local_before==remote_before==START,'Canonical advanced: reconcile and recertify in isolation before promotion.'
    assert run(['branch','--show-current'],CANON)=='v2-development' and run(['status','--porcelain'],CANON)==''
    startfiles=read(PACK/'STARTING_FILES.json')
    preserved=0
    for rel,details in startfiles.items():
        if rel not in production and 'canonical_checkout' in details:
            assert sha((CANON/rel).read_bytes())==details['canonical_checkout']['sha256'],rel
            preserved+=1
    for tip in [SOURCE_TIP,*read(PACK/'BASELINE.json')['required_ancestors']]:run(['merge-base','--is-ancestor',tip,target])
    run(['merge-base','--is-ancestor',START,target])
    run(['merge','--ff-only',target],CANON)
    assert run(['rev-parse','HEAD'],CANON)==target and run(['status','--porcelain'],CANON)==''
    run(['push','origin','v2-development'],CANON)
    run(['fetch','origin'],CANON)
    remote_after=run(['ls-remote','origin','refs/heads/v2-development'],CANON).split()[0]
    final=run(['rev-parse','HEAD'],CANON);tracking=run(['rev-parse','origin/v2-development'],CANON)
    assert final==tracking==remote_after==target
    incoming=run(['rev-list',START+'..'+SOURCE_TIP]).splitlines()
    for tip in incoming:run(['merge-base','--is-ancestor',tip,'origin/v2-development'],CANON)
    hashes={}
    for rel,p in production.items():
        working=sha((CANON/rel).read_bytes());remote=sha(git('show','origin/v2-development:'+rel,cwd=CANON));integration=sha((ROOT/rel).read_bytes())
        assert working==remote==integration==p['sha256']
        hashes[rel]=dict(canonical_working_sha256=working,fetched_directly_verified_remote_blob_sha256=remote,integration_sha256=integration,all_identical=True)
    for rel,details in startfiles.items():
        if rel not in production and 'canonical_checkout' in details:assert sha((CANON/rel).read_bytes())==details['canonical_checkout']['sha256'],rel
    refs=read(PACK/'BASELINE.json')['other_local_branch_refs']
    for ref,oid in refs.items():assert run(['rev-parse',ref])==oid,ref
    states={str(p):dict(head=run(['rev-parse','HEAD'],p),status=run(['status','--porcelain'],p)) for p in [CANON,ROOT,SOURCE]}
    assert all(not p['status'] for p in states.values()) and states[str(SOURCE)]['head']==SOURCE_TIP
    record=dict(status='PASS_CANONICAL_PROMOTED_PUSHED_AND_DIRECTLY_VERIFIED',started=started,finished=datetime.now(timezone.utc).isoformat(),starting_canonical=START,starting_remote=START,promotion_preflight_canonical=local_before,promotion_preflight_remote=remote_before,final_canonical=final,final_remote=remote_after,final_tracking=tracking,certified_source_tip=SOURCE_TIP,merge_commit=cert['tested_production_commit'],integration_history=run(['log','--first-parent','--format=%H %s',START+'..'+target]).splitlines(),all_eight_incoming_source_commits_remote_ancestors=incoming,production_hashes=hashes,preserved_canonical_working_files=preserved,other_local_branch_refs_unchanged=refs,clean_states=states,combined_identities=7350,BookXX_identities=268,BookXX_represented_Latin=257,BookXX_unavailable_Latin=11,certificate=info(PACK/'CERTIFICATE.json'),report=info(PACK/'REPORT.md'),changed_file_manifest=info(PACK/'CHANGE_MANIFEST.json'),normal_push=True,force_push=False,preview_published=False,source_worktree_untouched=True,events=events)
    save(receipt_path,record)
    print('PASS canonical and direct remote '+final+'; 7350 identities; receipt '+str(receipt_path))
if __name__=='__main__':main()
