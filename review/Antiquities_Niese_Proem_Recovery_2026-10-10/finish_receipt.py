"""External post-commit receipt records the exact final tip without dirtying its own checkout."""
from recover import *
def main():
    certificate=json.loads((PACK/'CERTIFICATE.json').read_text(encoding='utf-8'));assert certificate['status']=='PASS'
    status=git('status','--porcelain').decode();assert not status.strip(),status
    tip=git('rev-parse','HEAD').decode().strip()
    original=Path(r'C:\workspace\LatinJosephus-antiquities-niese-proem')
    original_tip=subprocess.check_output(['git','rev-parse','HEAD'],cwd=original).decode().strip()
    original_status=subprocess.check_output(['git','status','--porcelain'],cwd=original).decode()
    assert original_tip==CHECKPOINT and not original_status.strip()
    canonical=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
    canonical_tip=subprocess.check_output(['git','rev-parse','HEAD'],cwd=canonical).decode().strip()
    canonical_status=subprocess.check_output(['git','status','--porcelain'],cwd=canonical).decode()
    assert canonical_tip==BASE and not canonical_status.strip()
    changes=git('diff','--name-only',CHECKPOINT,'HEAD').decode().splitlines()
    assert all(n.startswith('review/Antiquities_Niese_Proem_Recovery_2026-10-10/') for n in changes)
    receipt={'status':'LOCALLY CERTIFIED / READY FOR COORDINATED INTEGRATION','final_branch':'antiquities-niese-proem-recovery','final_tip':tip,'clean':True,'baseline_commit':BASE,'production_commit':PRODUCTION,'build_source_commit':certificate['tested_build_source_commit'],'original_worktree':{'path':str(original),'tip':original_tip,'clean':True},'canonical':{'path':str(canonical),'tip':canonical_tip,'clean':True},'recovery_changed_files':changes,'production_changes_since_recovered_checkpoint':[],'certificate':record(PACK/'CERTIFICATE.json'),'handoff':record(PACK/'LOCAL_HANDOFF.json'),'manifest':record(PACK/'CERTIFICATION_MANIFEST.json'),'local_checkpoint_commits':git('log','--format=%H %s',CHECKPOINT+'..HEAD').decode().splitlines(),'no_merge_push_or_publication':True,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (RUNTIME/'FINAL_BRANCH_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    for name in ['CERTIFICATE.json','LOCAL_HANDOFF.json']:
        data=json.loads((PACK/name).read_text(encoding='utf-8'));data.update(final_branch_tip=tip,final_branch_clean=True,post_commit_receipt=record(RUNTIME/'FINAL_BRANCH_RECEIPT.json'))
        (RUNTIME/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'final_tip':tip,'clean':True,'original_tip_preserved':original_tip,'canonical_tip_preserved':canonical_tip,'post_commit_receipt':str(RUNTIME/'FINAL_BRANCH_RECEIPT.json')}))
if __name__=='__main__':main()
