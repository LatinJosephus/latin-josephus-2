from prepare import *
def main():
    target=PACK/'PROMOTION_STARTING_STATE.json';assert not target.exists()
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=CANON).decode().strip()==BASE
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=CANON).strip()
    refs=dict(line.split(' ',1) for line in git('for-each-ref','--format=%(refname) %(objectname)','refs/heads').decode().splitlines())
    refs.pop('refs/heads/antiquities-niese-proem-integration');refs.pop('refs/heads/v2-development')
    allowed=set(json.loads((PACK/'MERGE_RECEIPT.json').read_text())['production_sha256'])
    protected=json.loads((PACK/'PRODUCTION_PRESERVATION.json').read_text())['protected']
    # info's absolute path is useful; separately keep the immutable repository-relative key.
    files=[dict(relative_path=row['path'],checkout=info(CANON/row['path'])) for row in protected]
    source_paths=[Path(r'C:\workspace\LatinJosephus-antiquities-niese-proem'),Path(r'C:\workspace\LatinJosephus-antiquities-niese-proem-recovery')]
    states={str(p):dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=p).decode().strip(),status=subprocess.check_output(['git','status','--porcelain'],cwd=p).decode()) for p in source_paths}
    assert all(not r['status'] for r in states.values())
    remote=subprocess.check_output(['git','ls-remote','--heads','origin'],cwd=CANON).decode().splitlines()
    remote_refs={row.split()[1]:row.split()[0] for row in remote}
    assert remote_refs['refs/heads/v2-development']==BASE
    save(target,dict(status='PASS',starting_canonical=BASE,other_local_branch_refs=refs,remote_branch_refs=remote_refs,canonical_protected_checkout=files,preserved_worktrees=states,preview_related_refs={k:v for k,v in remote_refs.items() if k in ['refs/heads/master','refs/heads/gh-pages']},preview_deployment_command_not_invoked=True))
    print('PASS frozen promotion safeguards, preserved worktrees, unrelated branch refs and checkout hashes')
if __name__=='__main__':main()
