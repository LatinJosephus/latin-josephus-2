"""Verify committed promotion, fetched remote bytes, ancestry and clean states."""
from integration_common import *
import datetime

def gate():
    assert git('rev-parse','HEAD',cwd=CANON).decode().strip()==START
    assert git('branch','--show-current',cwd=CANON).decode().strip()=='v2-development'
    assert git('branch','--show-current').decode().strip()==BRANCH
    assert git('rev-parse','HEAD',cwd=SOURCE_ROOT).decode().strip()==SOURCE
    for p in [ROOT,CANON,SOURCE_ROOT]:assert not git('status','--porcelain',cwd=p).decode()
    direct=git('ls-remote','origin','refs/heads/v2-development').decode().split()[0]
    assert direct==START,'Concurrent remote advance requires isolated reconciliation and affected tests.'
    git('fetch','origin','v2-development')
    assert git('rev-parse','origin/v2-development').decode().strip()==START
    cert=read(D/'CERTIFICATION.json');assert cert['status']=='PASS_READY_FOR_SAFE_CANONICAL_PROMOTION'
    manifest=read(D/'FILE_MANIFEST.json')
    for f in manifest['files']:assert sha((ROOT/f['relative']).read_bytes())==f['sha256']
    for relative,f in tree(cert['tested_merge']).items():
        if not relative.startswith('review/'):assert_blob((ROOT/relative).read_bytes(),f['oid'])
    refs=dict(line.split(' ',1) for line in git('for-each-ref','--format=%(refname) %(objectname)','refs/heads').decode().splitlines())
    save(R/'PRE_PROMOTION_GATE.json',dict(status='PASS_CLEAN_CURRENT_AND_REMOTE_CANONICAL_START',canonical=START,direct_remote=direct,integration=git('rev-parse','HEAD').decode().strip(),source=SOURCE,certification_sha256=sha((D/'CERTIFICATION.json').read_bytes()),branch_refs=refs,verified_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    print('PASS promotion gate: local and direct/fetched remote',START,'all three worktrees clean')

def main():
    tip=git('rev-parse','HEAD').decode().strip()
    canonical=git('rev-parse','HEAD',cwd=CANON).decode().strip()
    fetched=git('rev-parse','origin/v2-development').decode().strip()
    direct=git('ls-remote','origin','refs/heads/v2-development').decode().split()[0]
    assert tip==canonical==fetched==direct
    assert git('branch','--show-current',cwd=CANON).decode().strip()=='v2-development'
    assert git('branch','--show-current').decode().strip()==BRANCH
    states={str(p):git('status','--porcelain',cwd=p).decode() for p in [ROOT,CANON,SOURCE_ROOT]}
    assert not any(states.values()),states
    assert git('rev-parse','HEAD',cwd=SOURCE_ROOT).decode().strip()==SOURCE
    baseline=read(D/'BASELINE.json');cert=read(D/'CERTIFICATION.json');manifest=read(D/'FILE_MANIFEST.json')
    assert cert['counts']['selectable_identities']==6323
    for c in baseline['source_commits']+[START,SOURCE]:
        assert subprocess.run(['git','merge-base','--is-ancestor',c,tip],cwd=ROOT).returncode==0
    assert len(baseline['source_commits'])==16
    final_tree=tree(tip);remote_tree=tree(fetched);assert final_tree==remote_tree
    paths=git('diff','--name-only',START,tip).decode().splitlines()
    assert len(paths)==manifest['changed_paths_including_manifest']
    expected={f['relative']:f for f in manifest['files']}
    manifest_relative=str((D/'FILE_MANIFEST.json').relative_to(ROOT)).replace('\\','/')
    assert set(paths)==set(expected)|{manifest_relative}
    changes=[]
    for relative in paths:
        raw=(CANON/relative).read_bytes();assert_blob(raw,final_tree[relative]['oid'])
        assert raw==(ROOT/relative).read_bytes()
        if relative in expected:assert sha(raw)==expected[relative]['sha256']
        changes.append(dict(relative=relative,git_blob=final_tree[relative]['oid'],bytes=len(raw),sha256=sha(raw)))
    unchanged=0
    changed_existing={'assets/js/renderTei.js','assets/xml/antiquities/Latin/book-18.xml','assets/xml/antiquities/Latin/book-19.xml'}
    for f in baseline['files']:
        if f['relative'] in changed_existing:continue
        assert final_tree[f['relative']]['oid']==f['oid']
        assert sha((CANON/f['relative']).read_bytes())==f['sha256'];unchanged+=1
    assert unchanged==3285
    production=[]
    for f in manifest['production']:
        relative=f['relative'];raw=git('show',f'origin/v2-development:{relative}')
        assert raw==(CANON/relative).read_bytes() and sha(raw)==f['sha256']
        production.append(dict(relative=relative,sha256=sha(raw),bytes=len(raw),fetched_remote_git_blob=remote_tree[relative]['oid'],direct_remote_tip_verified=direct))
    gate=read(R/'PRE_PROMOTION_GATE.json')
    refs=dict(line.split(' ',1) for line in git('for-each-ref','--format=%(refname) %(objectname)','refs/heads').decode().splitlines())
    foreign_changes=[dict(branch=k,before=v,after=refs.get(k)) for k,v in gate['branch_refs'].items() if k not in ['refs/heads/v2-development','refs/heads/'+BRANCH] and refs.get(k)!=v]
    receipt=dict(status='PASS_CANONICAL_PROMOTED_AND_NORMAL_PUSH_VERIFIED',verified_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),starting_canonical=START,starting_direct_remote=START,final_canonical=canonical,final_fetched_remote=fetched,final_direct_remote=direct,certified_source=SOURCE,source_baseline=BASE,integration_baseline_commit='23f535de91ad4875bb947790bcdd4ab1308fa5cc',integration_merge_commit=cert['tested_merge'],integration_certification_commit=tip,all_sixteen_source_commits=baseline['source_commits'],all_sixteen_preserved_in_remote_ancestry=True,counts=cert['counts'],book_counts=cert['book_counts'],closed_decisions=cert['decisions'],safe_fast_forward_promotion=True,normal_push=True,force_push=False,source_history_rewritten=False,clean_states=states,source_tip_unchanged=True,production_remote_file_hashes=production,changed_files=changes,changed_path_count=len(paths),unchanged_canonical_start_files=unchanged,unchanged_incoming_review_files=445,integration_review_files=manifest['integration_review_files'],formal_merge_conflicts=0,manual_production_resolutions=0,canonical_report=str(CANON/str(D.relative_to(ROOT))/'REPORT.md'),isolated_report=str(D/'REPORT.md'),report_sha256=sha((D/'REPORT.md').read_bytes()),manifest_sha256=sha((D/'FILE_MANIFEST.json').read_bytes()),public_preview_refreshed=False,public_preview_published=False,other_workbots_written=False,other_workbot_runtimes_written=False,foreign_branch_advances_observed_since_gate=foreign_changes,worktree_inventory=git('worktree','list','--porcelain').decode())
    save(R/'PROMOTION_RECEIPT.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['changed_files','worktree_inventory','clean_states','counts','book_counts','closed_decisions','production_remote_file_hashes','all_sixteen_source_commits']}))
if __name__=='__main__':gate() if '--gate' in sys.argv else main()
