from prepare import *
import datetime,csv,io

SOURCE='07057a284e3eb4999bd875cd05eb970e30886452'
MERGE='a0245745c3fd3b3a04bfb5ed8acc192cd7f01b87'
events=[];started=datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt=RUNTIME/'PROMOTION_RECEIPT.json'
def run(args,cwd=ROOT):
    r=subprocess.run(['git',*args],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    events.append(dict(command=['git',*args],cwd=str(cwd),exit_code=r.returncode,output=r.stdout.decode('utf-8',errors='replace')))
    save(receipt,dict(status='PROMOTION_IN_PROGRESS',started=started,events=events))
    assert r.returncode==0,events[-1]
    return r.stdout.decode().strip()
def blob(rev,n,cwd=ROOT):return subprocess.check_output(['git','show',rev+':'+n],cwd=cwd)
def main():
    cert=json.loads((PACK/'CERTIFICATE.json').read_text());frozen=json.loads((PACK/'PROMOTION_STARTING_STATE.json').read_text())
    assert cert['status']=='PASS' and cert['gates']['complete_corpus']['total']==7376
    for row in json.loads((PACK/'CERTIFICATION_MANIFEST.json').read_text()):assert sha((PACK/row['path']).read_bytes())==row['sha256']
    assert run(['branch','--show-current'])=='antiquities-niese-proem-integration' and not run(['status','--porcelain'])
    target=run(['rev-parse','HEAD'])
    assert not run(['diff','--name-only',cert['tested_build']['commit'],target,'--','assets','_includes','_layouts','_pages','_sass','_data','bin','_config.yml','Gemfile'])
    for n,h in cert['production_sha256'].items():assert sha(blob(target,n))==h
    run(['fetch','origin','v2-development'],CANON)
    before=run(['ls-remote','--heads','origin','refs/heads/v2-development'],CANON).split()[0]
    assert before==BASE==run(['rev-parse','HEAD'],CANON)==run(['rev-parse','origin/v2-development'],CANON),'Canonical advanced; integrate and recertify its new lineage before promotion.'
    assert run(['branch','--show-current'],CANON)=='v2-development' and not run(['status','--porcelain'],CANON)
    for row in frozen['canonical_protected_checkout']:assert sha((CANON/row['relative_path']).read_bytes())==row['checkout']['sha256']
    for ref,oid in frozen['other_local_branch_refs'].items():assert run(['rev-parse',ref])==oid
    for p,state in frozen['preserved_worktrees'].items():assert run(['rev-parse','HEAD'],Path(p))==state['head'] and not run(['status','--porcelain'],Path(p))
    incoming=run(['rev-list',BASE+'..'+SOURCE]).splitlines()
    for ancestor in [BASE,SOURCE,MERGE,*incoming]:run(['merge-base','--is-ancestor',ancestor,target])
    run(['merge','--ff-only',target],CANON)
    assert run(['rev-parse','HEAD'],CANON)==target and not run(['status','--porcelain'],CANON)
    run(['push','origin','v2-development:v2-development'],CANON)
    run(['fetch','origin','v2-development'],CANON)
    direct=run(['ls-remote','--heads','origin','refs/heads/v2-development'],CANON).split()[0]
    assert direct==target==run(['rev-parse','HEAD'],CANON)==run(['rev-parse','origin/v2-development'],CANON)
    for ancestor in [BASE,SOURCE,MERGE,*incoming]:run(['merge-base','--is-ancestor',ancestor,'origin/v2-development'],CANON)
    production={}
    for n,h in cert['production_sha256'].items():
        fetched=blob('origin/v2-development',n,CANON);working=(CANON/n).read_bytes()
        assert sha(fetched)==h and (working==fetched or working.replace(b'\r\n',b'\n')==fetched)
        production[n]=dict(remote_fetched_blob_sha256=sha(fetched),canonical_working_sha256=sha(working),certified_sha256=h,checkout_line_endings_only=working!=fetched,bytes=len(fetched))
    for row in frozen['canonical_protected_checkout']:assert sha((CANON/row['relative_path']).read_bytes())==row['checkout']['sha256']
    states={str(p):dict(head=run(['rev-parse','HEAD'],p),status=run(['status','--porcelain'],p)) for p in [CANON,ROOT,*map(Path,frozen['preserved_worktrees'])]}
    assert all(not row['status'] for row in states.values())
    for p,state in frozen['preserved_worktrees'].items():assert states[p]['head']==state['head']
    for ref,oid in frozen['other_local_branch_refs'].items():assert run(['rev-parse',ref])==oid
    remote_refs={row.split()[1]:row.split()[0] for row in run(['ls-remote','--heads','origin'],CANON).splitlines()}
    preview={ref:dict(before=oid,after=remote_refs.get(ref),unchanged=remote_refs.get(ref)==oid) for ref,oid in frozen['preview_related_refs'].items()}
    assert all(r['unchanged'] for r in preview.values())
    rows=[]
    diff=subprocess.check_output(['git','diff','--name-status','-z',BASE,target],cwd=ROOT).split(b'\0');i=0
    while i<len(diff) and diff[i]:
        status=diff[i].decode();n=diff[i+1].decode('utf-8');i+=2
        assert not status.startswith(('R','C','D'))
        raw=blob(target,n);oid=run(['rev-parse',target+':'+n]);assert blob('origin/v2-development',n,CANON)==raw
        rows.append(dict(status=status,path=n,bytes=len(raw),git_blob=oid,sha256=sha(raw),remote_blob_verified=True,classification='production' if n in cert['production_sha256'] else 'approved source evidence' if n.startswith(('review/Antiquities_Niese_Proem_2026-10-10/','review/Antiquities_Niese_Proem_Recovery_2026-10-10/')) else 'integration QA'))
    assert {r['path'] for r in rows if r['classification']=='production'}==set(cert['production_sha256'])
    assert all(r['classification']!='integration QA' or r['path'].startswith(PACK.relative_to(ROOT).as_posix()+'/') for r in rows)
    manifest=RUNTIME/'FINAL_CHANGED_FILE_MANIFEST.json';save(manifest,dict(actual_start=BASE,final=target,remote=direct,total=len(rows),production_count=3,files=rows))
    output=io.StringIO(newline='');w=csv.DictWriter(output,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);(RUNTIME/'FINAL_CHANGED_FILE_MANIFEST.csv').write_text(output.getvalue(),encoding='utf-8',newline='')
    record=dict(status='PASS_CANONICAL_PROMOTED_PUSHED_AND_DIRECTLY_VERIFIED',started=started,finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_start=BASE,promotion_preflight_remote=before,final_canonical=target,final_remote=direct,final_tracking=run(['rev-parse','origin/v2-development'],CANON),certified_recovery_tip=SOURCE,merge_commit=MERGE,integration_QA_commits=run(['log','--first-parent','--format=%H %s',MERGE+'..'+target]).splitlines(),complete_source_history_remote_ancestors=incoming,production_hashes=production,canonical_protected_checkout_count=len(frozen['canonical_protected_checkout']),other_local_branches_preserved=True,clean_states=states,complete_corpus=7376,Proem=26,prior=7350,normal_push=True,force_push=False,preview_published=False,preview_branch_verification=preview,domains_changed=False,source_worktrees_and_checkpoints_preserved=True,certificate=info(PACK/'CERTIFICATE.json'),report=info(PACK/'REPORT.txt'),exact_changed_file_manifest=info(manifest),events=events)
    save(receipt,record)
    print('PASS canonical and directly verified remote '+target+'; exact '+str(len(rows))+'-file manifest; receipt '+str(receipt))
if __name__=='__main__':main()
