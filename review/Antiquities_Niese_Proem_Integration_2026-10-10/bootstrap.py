from pathlib import Path
import hashlib, json, shutil, subprocess, datetime

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
BASE='4f88fc1483ec14d418c678004e13bc2b6741a2b7'
TIP='07057a284e3eb4999bd875cd05eb970e30886452'
MERGE='a0245745c3fd3b3a04bfb5ed8acc192cd7f01b87'
R=ROOT/'review/Antiquities_Niese_Proem_Recovery_2026-10-10'
H=ROOT/'review/Antiquities_Niese_Proem_2026-10-10'
X=ROOT/'review/Antiquities_Niese_Integration_20_2026-10-10'
RUNTIME=Path(r'C:\workspace\Antiquities-Niese-Proem-Integration-runtime-20261010')
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def record(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}

def main():
    assert git('rev-parse','HEAD').decode().strip()==MERGE
    assert git('rev-parse','antiquities-niese-proem-recovery').decode().strip()==TIP
    assert git('rev-parse','v2-development').decode().strip()==BASE
    assert git('show','-s','--format=%P',MERGE).decode().strip().split()==[BASE,TIP]
    ancestors=[BASE,TIP,'16f0f764a501825fef5ecb4ceba26f79f571c777','4afe79be6d4ba2f8fdcf5ca1a07fda878d7a56fb','a3ca656151f1170a099f4f143f70feb1118dbfd1']
    for rev in ancestors:subprocess.run(['git','merge-base','--is-ancestor',rev,MERGE],cwd=ROOT,check=True)
    checked=[]
    for row in json.loads((R/'CERTIFICATION_MANIFEST.json').read_text()):
        p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p.read_bytes())==row['sha256'],str(p)
        checked.append(row)
    handoff=Path(r'C:\workspace\Antiquities-Niese-Proem-Recovery-runtime-20261010')
    full=handoff/'reports/FINAL_PROTECTED_BROWSER.full.json'
    assert sha(full.read_bytes())=='5ceebb39318f781a4c57e697baad56702f2d1ce3f4c2e2789a6fea14e7f0d605'
    old=json.loads(full.read_text());assert old['status']=='PASS' and len(old['selections'])==7350
    assert json.loads((R/'CERTIFICATE.json').read_text())['status']=='PASS'
    incoming=git('log','--reverse','--format=%H %P %s',BASE+'..'+TIP).decode().splitlines()
    production={'assets/js/renderTei.js':'665f31b0a5cfe668692490c1c1ffece09097ca4cfa69ff0e516e862e56ce2d72','assets/xml/antiquities/Latin/preface.xml':'e0588da38fe3d3e9f69735a79b204556906b1377cf8e4cf8b7ec3ce396789015','assets/xml/antiquities/niese/preface.json':'0a0e46771df523aad8a3dad9e696ec51bbe5cd9da084ec81eed0a20aeb6b2e18'}
    for n,h in production.items():assert sha((ROOT/n).read_bytes())==sha(git('show',TIP+':'+n))==h
    assert git('diff','--name-only',TIP,MERGE).strip()==b''
    if RUNTIME.exists():
        assert {p.name for p in RUNTIME.iterdir()}<={'reports','checkpoints','logs'}
        assert not any(p.is_file() for p in RUNTIME.rglob('*'))
    else:RUNTIME.mkdir()
    for d in ['reports','checkpoints','logs']:(RUNTIME/d).mkdir(exist_ok=True)
    provenance=[]
    def copy(source,name=None,edits=()):
        dest=P/(name or source.name);dest.parent.mkdir(parents=True,exist_ok=True)
        original=source.read_bytes();new=original
        if source.suffix in ['.py','.cjs']:
            s=original.decode('utf-8').replace('Antiquities-Niese-Proem-Recovery-runtime-20261010','Antiquities-Niese-Proem-Integration-runtime-20261010').replace('Antiquities-Niese-20-integration-runtime-20261010','Antiquities-Niese-Proem-Integration-runtime-20261010')
            for a,b in edits:
                assert a in s,(source,a);s=s.replace(a,b)
            new=s.encode('utf-8')
        dest.write_bytes(new)
        provenance.append({'source':record(source),'destination':record(dest),'adaptations':list(edits),'isolated_runtime':source.suffix in ['.py','.cjs']})
    for n in ['prepare.py','review_sources.py','verify_bytes.py','verify_recovery.py','build.py','qa-common18.cjs','proem_browser.cjs','plain_browser.cjs','plain_final_controls.cjs','protected_browser.cjs','reader-xi.cjs','reader-structure-crosswork.cjs','focused_controls.cjs','DECISION_REGISTER.json','EXPECTED_INTERVALS.json','AUTHORIZED_ADDITIONS.json','READER_PATCH.json']:copy(R/n)
    copy(R/'browser_common.cjs',edits=[("server.listen(mode==='baseline'?8927:8926", "server.listen(Number(process.env.NIESE_QA_PORT||(mode==='baseline'?8957:8956))"),("'browser-'+mode", "'browser-'+(process.env.NIESE_QA_PROFILE||mode)")])
    for p in (R/'frozen-inputs').iterdir():copy(p,'frozen-inputs/'+p.name)
    for n in ['BASELINE_PROTECTED_BROWSER.json','PROTECTED_GIT_OBJECTS.json','STRUCTURAL_CONTROLS.json']:copy(H/n)
    for n in ['xi-witness-order.cjs','XI_WITNESS_EXPECTATION.json','THEME_BASELINE_DIAGNOSTIC.json','DISTINCT_PHYSICAL_POINT_PROOF.json','FINAL_EXPECTED_INTERVALS.json','COMBINED_EXPECTED_INTERVALS.json','bookxx_browser.cjs','combined_cases_browser.cjs','xx_controls.cjs','prove_range_end.cjs']:copy(X/n)
    copy(ROOT/'review/Antiquities_Niese_Integration_16_17_2026-10-10/reader-extra.cjs')
    copy(X/'combined-extra.cjs',edits=[('!==7350','!==7376')])
    copy(X/'final_source_controls.cjs',edits=[("'final-site'","'candidate-site'")])
    copy(X/'qa-common16.cjs',edits=[("'final-site'","'candidate-site'")])
    copy(X/'new-books-browser.cjs')
    copy(X/'closure_browser.cjs',edits=[("'frozen-inputs','Latin.xml'","'XX-frozen-Latin.xml'")])
    copy(X/'frozen-inputs/Latin.xml','XX-frozen-Latin.xml')
    gov=Path(r'C:\Users\Pollard_R\Mon disque\Downloads from Chrome (11-08-2026 onward)\WORKBOT_Antiquities_Proem_Canonical_Integration_2026-10-10.txt');copy(gov)
    (P/'.gitignore').write_text('__pycache__/\nBASELINE_PROTECTED_BROWSER.json\nPROTECTED_GIT_OBJECTS.json\nSTRUCTURAL_CONTROLS.json\nFINAL_PROTECTED_BROWSER.full.json\n',encoding='utf-8')
    save(P/'QA_HARNESS_PROVENANCE.json',provenance)
    save(P/'MERGE_RECEIPT.json',{'status':'PASS','actual_start':BASE,'direct_remote_start':BASE,'remote_method':'Fresh fetch origin v2-development and direct git ls-remote --heads origin refs/heads/v2-development','certified_recovery_tip':TIP,'merge':MERGE,'parents':[BASE,TIP],'conflicts':[],'production_resolution':'None required; exact certified production bytes retained','ancestors_verified':ancestors,'incoming_commits':incoming,'incoming_changed_files':git('diff','--name-status',BASE,TIP).decode().splitlines(),'production_sha256':production,'source_manifest_verified':checked,'source_full_replay':record(full),'source_worktrees_and_checkpoints_preserved':True,'archive_reimported':False,'source_review_reopened':False,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    save(RUNTIME/'START_RECEIPT.json',{'merge':MERGE,'baseline':BASE,'source':TIP,'root':str(ROOT),'review':str(P),'governing':record(gov),'published':False})
    print('PASS verified certified evidence, complete ancestry, exact merge tree and isolated harness provenance')
if __name__=='__main__':main()
