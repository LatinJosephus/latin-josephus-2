from integration_common import *
def main():
    assert git('rev-parse','HEAD').decode().strip()==START
    assert git('branch','--show-current').decode().strip()==BRANCH
    assert git('rev-parse','HEAD',cwd=SOURCE_ROOT).decode().strip()==SOURCE
    assert not git('status','--porcelain',cwd=SOURCE_ROOT).decode()
    assert not git('status','--porcelain',cwd=CANON).decode()
    assert not R.exists();R.mkdir()
    baseline=[]
    for rel,entry in tree(START).items():
        raw=(ROOT/rel).read_bytes();assert_blob(raw,entry['oid'])
        baseline.append(dict(relative=rel,**entry,bytes=len(raw),sha256=sha(raw)))
    source_tree=tree(SOURCE);incoming=[]
    paths=git('diff','--name-only',BASE,SOURCE).decode().splitlines()
    for rel in paths:
        raw=(SOURCE_ROOT/rel).read_bytes();assert_blob(raw,source_tree[rel]['oid'])
        incoming.append(dict(relative=rel,**source_tree[rel],bytes=len(raw),sha256=sha(raw)))
    receipt=read(Path(r'C:\workspace\Antiquities-Niese-18-19-runtime-20261009\FINAL_HANDOFF_RECEIPT.json'))
    commits=git('rev-list','--reverse',BASE+'..'+SOURCE).decode().splitlines()
    assert commits==[x['commit'] for x in receipt['local_commits']] and len(commits)==16
    assert len(incoming)==450 and len([x for x in incoming if not x['relative'].startswith('review/')])==5
    save('BASELINE.json',dict(canonical=START,direct_remote=START,source=SOURCE,source_baseline=BASE,branch=BRANCH,worktree=str(ROOT),runtime=str(R),files=baseline,source_commits=commits,canonical_initial_clean=True,source_initial_clean=True,preview_publication_authorized=False))
    save('INCOMING_SCOPE.json',dict(source=SOURCE,files=incoming,source_commits=commits,production=[x['relative'] for x in incoming if not x['relative'].startswith('review/')],review=[x['relative'] for x in incoming if x['relative'].startswith('review/')]))
    for name,commit in [('base',BASE),('canonical',START),('incoming',SOURCE)]:
        p=D/'renderer-comparison'/f'{name}.js';p.parent.mkdir(exist_ok=True);p.write_bytes(git('show',commit+':assets/js/renderTei.js'))
    save('SOURCE_PROVENANCE.json',dict(certified_source=SOURCE,receipt=info(Path(r'C:\workspace\Antiquities-Niese-18-19-runtime-20261009\FINAL_HANDOFF_RECEIPT.json')),source_report=info(SOURCE_ROOT/'review/Antiquities_Niese_Batch_18_19_2026-10-09/REPORT.md'),original_runtime_read_only=True,complete_16_commit_history_required=True))
    print('Frozen canonical',START,'files',len(baseline),'incoming',len(incoming),'commits',len(commits))
if __name__=='__main__':main()
