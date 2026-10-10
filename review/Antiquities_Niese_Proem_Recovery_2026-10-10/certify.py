"""Strict final gates, concise Git evidence, full replay retained separately."""
from recover import *
from collections import Counter

def load(n):return json.loads((PACK/n).read_text(encoding='utf-8'))
def main():
    build=load('BUILD_CONTEXT.json');full=load('FINAL_PROTECTED_BROWSER.full.json');base=load('BASELINE_PROTECTED_BROWSER.json')
    proem=load('PROEM_BROWSER_QA.json');plain=load('PLAIN_READER_QA.json');plain_final=load('PLAIN_FINAL_CONTROLS.json');xi=load('READER_XI_RESULTS.json');focused=load('FRESH_FOCUSED_CONTROLS.json');equivalence=load('CONTAINING_CROSSWORK_EQUIVALENCE.json')
    assert full['status']=='PASS' and full['sourceBuild']==build['commit']
    assert len(full['selections'])==len(base['selections'])==7350 and len(full['views'])==135 and len(full['books'])==20
    assert full['selections']==base['selections'] and full['books']==base['books']
    assert all(not s['duplicates'] for s in full['selections']) and not full['errors']
    assert proem['status']==plain['status']==plain_final['status']=='PASS'
    assert proem['source_build']==plain['source_build']==build['commit']
    assert len(proem['selections'])==len(proem['routes'])==len(plain['selectors'])==26
    assert [r['number'] for r in proem['stalePaneSequence']]==[25,26,25,26]
    assert [r['n'] for r in plain_final['sequence']]==[25,26,25,26]
    assert proem['wholeProemAndTransition']==plain['BookI27']['status']=='PASS'
    assert xi['result']=='PASS' and xi['build']==build
    assert len(xi['selectors'])==347 and len(xi['ranges'])==9 and len(xi['containing'])==120 and len(xi['navigation'])==22
    assert xi['identity_order_and_false105']==xi['view_switches']=='PASS' and not xi['errors']
    assert focused['status']==equivalence['status']=='PASS' and not focused['errors'] and not equivalence['differences']
    assert load('VISUAL_QA.json')['status']=='PASS' and load('METADATA_RECONCILIATION.json')['status']=='PASS'
    assert not git('diff',build['commit'],'HEAD','--','assets','_includes','_layouts','_pages','_sass','_data','bin','_config.yml','Gemfile').strip()
    for n in PRODUCTION_PATHS:
        assert (ROOT/n).read_bytes()==(Path(build['site'])/n).read_bytes()==git('show',PRODUCTION+':'+n)
    for row in load('BUILD_ASSET_MANIFEST.json'):
        assert sha((Path(build['site'])/row['path']).read_bytes())==row['sha256']
    from verify_recovery import main as verify
    verify()
    reports=RUNTIME/'reports';reports.mkdir(exist_ok=True)
    full_copy=reports/'FINAL_PROTECTED_BROWSER.full.json';shutil.copyfile(PACK/'FINAL_PROTECTED_BROWSER.full.json',full_copy)
    raw_receipt=record(full_copy)
    def digest(x):return sha(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode())
    summaries=[]
    for b in full['books']:
        rows=[r for r in full['selections'] if r['book']==b['book']]
        assert [r['number'] for r in rows]==b['menu']
        summaries.append({'book':b['book'],'selections':len(rows),'first':b['menu'][0],'last':b['menu'][-1],'status':'PASS','sequence_sha256':digest(rows),'duplicate_selection_IDs':0})
    save('FINAL_PROTECTED_BROWSER.json',{'status':'PASS','source_build':build['commit'],'production_commit':PRODUCTION,'started':full['started'],'finished':full['finished'],'fresh_replay':True,'cached_selections_used':0,'selections':7350,'books':summaries,'XX_containing_views':135,'XX_containing_sha256':digest(full['views']),'XX_exclusive_end_and_trailer':'Preserved exact containing DOM/text endpoints and all 268 selections against immutable baseline','all_selection_content_notes_sourceIDs_endpoints_paneDOM_match':True,'duplicate_selection_IDs':0,'containing_baseline_ID_observations':[{'id':v['id'],'duplicates':v['duplicates'],'matches_baseline':v['duplicates']==next(x for x in base['views'] if x['id']==v['id'])['duplicates']} for v in full['views'] if v['duplicates']],'errors':[],'full_evidence':raw_receipt})
    save('FINAL_BYTE_HASHES.json',{'status':'PASS','production_commit':PRODUCTION,'production_files':[record(ROOT/n) for n in PRODUCTION_PATHS],'source_originals':load('BYTE_CERTIFICATION.json')['sources'],'expected_intervals':[{'number':r['number'],'Latin':sha(r['Latin'].encode()),'Greek':sha(r['Greek'].encode()),'English_context_target':r['English_context_target'],'English':sha(r['English'].encode())} for r in load('EXPECTED_INTERVALS.json')]})
    # Manifest intentionally omits the manifest/certificate/handoff themselves to avoid self-reference.
    manifest=[{'path':str(p.relative_to(PACK)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(PACK.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['CERTIFICATE.json','LOCAL_HANDOFF.json','CERTIFICATION_MANIFEST.json','LATEST_CHECKPOINT.json','REPLAY_PROGRESS.json','FINAL_PROTECTED_BROWSER.full.json','BASELINE_PROTECTED_BROWSER.json','PROTECTED_GIT_OBJECTS.json','STRUCTURAL_CONTROLS.json']]
    save('CERTIFICATION_MANIFEST.json',manifest)
    report_names=['RECOVERY_BASELINE.json','METADATA_RECONCILIATION.json','BYTE_CERTIFICATION.json','PRODUCTION_PRESERVATION.json','RECONSTRUCTION_QA.json','FINAL_BYTE_HASHES.json','PROEM_BROWSER_QA.json','PLAIN_READER_QA.json','PLAIN_FINAL_CONTROLS.json','READER_XI_RESULTS.json','FINAL_PROTECTED_BROWSER.json','CONTAINING_CROSSWORK_EQUIVALENCE.json','PRESERVED_CONTAINING_CROSSWORK_PASS.json','FRESH_FOCUSED_CONTROLS.json','VISUAL_QA.json','BUILD_CONTEXT.json','BUILD_ASSET_MANIFEST.json','CERTIFICATION_MANIFEST.json']
    certificate={'status':'PASS','designation':'LOCALLY CERTIFIED / READY FOR COORDINATED INTEGRATION','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'recovery_route':'A','baseline_commit':BASE,'recovered_checkpoint':CHECKPOINT,'production_commit':PRODUCTION,'build':build,'tested_build_source_commit':build['commit'],'certification_parent_commit':git('rev-parse','HEAD').decode().strip(),'final_branch_ref':'refs/heads/antiquities-niese-proem-recovery','final_branch_receipt':str(RUNTIME/'FINAL_BRANCH_RECEIPT.json'),'history_reconstructed':False,'production_files':[record(ROOT/n) for n in PRODUCTION_PATHS],'gates':{'Proem':{'full_selections':26,'plain_selections':26,'direct_reload_previous_next_history':26,'stale_pane_sequence':[25,26,25,26],'plain_stale_pane_sequence':[25,26,25,26],'Greek_Latin_present':26,'Latin_unavailable':0,'Latin_inherited_starts':4,'Latin_added_starts':22,'exclusive_Latin_end':1,'Greek_added_markers':0,'English_context_paragraphs':4,'whole_paratext_separate':True,'Book_I_transition':27,'Book_I_population':320},'prior_identity_replay':{'status':'PASS','fresh':True,'selections':7350,'books':20,'cached_rows':0,'content_notes_sourceIDs_endpoints_DOM':'exact immutable baseline match','zero_duplicate_selection_IDs':True,'XX_containing_views':135},'XI':{'status':'PASS','selections':347,'ranges':9,'containing_views':120,'navigation_cases':22,'assembly_312_326_342':'PASS','two_distinct_BJ_IV_105_attachments':'PASS','transposition_Book_Alignment_witness_order':'PASS'},'containing_crosswork':{'status':'PASS','preserved_final_production_PASS':str(PACK/'PRESERVED_CONTAINING_CROSSWORK_PASS.json'),'byte_equivalent_reader_inputs':256,'DEH_build_cache_timestamp_keys_normalized':2,'fresh_focused_controls':11,'Lodge_Whiston_switching':'PASS'},'preservation':{'Greek_English_unchanged':True,'Latin_exact_marker_reversal':True,'Latin_baseline_sha256':'0c4719d6e120ec414fa75076f471d86aa5af9a11bb810299399118992fa897e8','narrative_reconstruction':26,'unrelated_production_unchanged':True,'generic_pane_child_snapshot_fix_preserved':True}},'partial_correspondence_notes':{str(n):load('METADATA_RECONCILIATION.json')['Latin'+str(n)] for n in [25,26]},'local_identity_population':7376,'source_review_reopened':False,'reports':[record(PACK/n) for n in report_names],'new_blockers':[],'integration':{'canonical_merge':False,'push':False,'public_preview_publication':False,'domains_changed':False}}
    save('CERTIFICATE.json',certificate)
    save('LOCAL_HANDOFF.json',{'status':certificate['designation'],'branch':'antiquities-niese-proem-recovery','worktree':str(ROOT),'recovery_route':'A','baseline_commit':BASE,'recovered_checkpoint':CHECKPOINT,'production_commit':PRODUCTION,'tested_build_source_commit':build['commit'],'runtime':str(RUNTIME),'certificate':str(PACK/'CERTIFICATE.json'),'manifest':str(PACK/'CERTIFICATION_MANIFEST.json'),'final_tip_and_clean_status_receipt':str(RUNTIME/'FINAL_BRANCH_RECEIPT.json'),'final_tip_resolution':'Final certification commit is the branch ref resolved in the external post-commit receipt; avoids a self-referential commit hash.','historical_review_preserved':str(OLD),'original_worktree_preserved':r'C:\workspace\LatinJosephus-antiquities-niese-proem','compact_checkpoints':str(RUNTIME/'checkpoints'),'full_replay_evidence':raw_receipt,'changed_production_manifest':PRODUCTION_PATHS,'new_recovery_production_changes':[],'metadata_and_QA_only_since_checkpoint':True,'integration_authorized':False,'source_decisions_reopened':False,'new_blockers':[]})
    save('REPLAY_PROGRESS.json',{'status':'COMPLETE_CERTIFIED','supersedes':'Historical in-progress receipts preserved in Git checkpoints','build':build,'saved_selections':7350,'target':7350,'XX_containing_views':135,'books':summaries,'certificate':str(PACK/'CERTIFICATE.json')})
    print('PASS all final certification gates; certificate and handoff written')
if __name__=='__main__':main()
