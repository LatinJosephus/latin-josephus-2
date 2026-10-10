"""Route A recovery and read-only source verification. Never applies production edits."""
from pathlib import Path
import json, hashlib, subprocess, zipfile, shutil, csv, io, datetime

PACK = Path(__file__).resolve().parent
ROOT = PACK.parents[1]
OLD = ROOT/'review/Antiquities_Niese_Proem_2026-10-10'
RUNTIME = Path(r'C:\workspace\Antiquities-Niese-Proem-Recovery-runtime-20261010')
ZIP = Path(r'C:\Users\Pollard_R\Mon disque\Downloads from Chrome (11-08-2026 onward)\Antiquities-Proem-Segmentation-Data.zip')
BASE = '4f88fc1483ec14d418c678004e13bc2b6741a2b7'
PRODUCTION = '4afe79be6d4ba2f8fdcf5ca1a07fda878d7a56fb'
CHECKPOINT = '16f0f764a501825fef5ecb4ceba26f79f571c777'
EXPECTED_ZIP = 'c15d641485dc38f049d4b59ba6855f1e3d62f615113d5fbc0c784aa51a9ae146'
PRODUCTION_PATHS = ['assets/js/renderTei.js','assets/xml/antiquities/Latin/preface.xml','assets/xml/antiquities/niese/preface.json']
def sha(b): return hashlib.sha256(b).hexdigest()
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)
def save(name,data):
    p=PACK/name; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def record(p):
    b=p.read_bytes(); return {'path':str(p),'bytes':len(b),'sha256':sha(b)}
def main():
    assert not (PACK/'RECOVERY_BASELINE.json').exists()
    assert not RUNTIME.exists()
    assert git('rev-parse','HEAD').decode().strip()==CHECKPOINT
    for a,b in [(BASE,PRODUCTION),(PRODUCTION,CHECKPOINT)]: git('merge-base','--is-ancestor',a,b)
    raw=ZIP.read_bytes(); assert sha(raw)==EXPECTED_ZIP
    RUNTIME.mkdir()
    with zipfile.ZipFile(ZIP) as z:
        assert len(z.namelist())==129 and z.testzip() is None
        manifest=json.loads(z.read('MANIFEST.json')); assert len(manifest)==128
        assert set(z.namelist())=={r['path'] for r in manifest}|{'MANIFEST.json'}
        for r in manifest:
            b=z.read(r['path']); assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
        archive_dir=RUNTIME/'preserved-packet';archive_dir.mkdir()
        for n in z.namelist():
            p=Path(n);assert not p.is_absolute() and '..' not in p.parts
            target=archive_dir/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(n))
        for n in PRODUCTION_PATHS:
            assert (ROOT/n).read_bytes()==z.read('current-Proem-files/'+n)==git('show',PRODUCTION+':'+n)
        for language in ['Greek','English']:
            n=f'assets/xml/antiquities/{language}/preface.xml'
            assert (ROOT/n).read_bytes()==z.read('current-Proem-files/'+n)==git('show',BASE+':'+n)
        # Packet evidence agrees with surviving checkpoint except known status documentation.
        compare=[]
        for r in manifest:
            if r['path'].startswith('Proem-review/'):
                relative=r['path'].removeprefix('Proem-review/');p=OLD/relative
                assert p.exists() and p.read_bytes()==z.read(r['path']),relative
                compare.append(relative)
    scripts=['prepare.py','review_sources.py','verify_bytes.py','build.py','browser_common.cjs','qa-common18.cjs','proem_browser.cjs','plain_browser.cjs','protected_browser.cjs','reader-xi.cjs','reader-structure-crosswork.cjs']
    records=['DECISION_REGISTER.json','EXPECTED_INTERVALS.json','AUTHORIZED_ADDITIONS.json','READER_PATCH.json','PROTECTED_GIT_OBJECTS.json','STRUCTURAL_CONTROLS.json','BASELINE_PROTECTED_BROWSER.json']
    adapters=[]
    for n in scripts:
        b=(OLD/n).read_bytes();t=b.decode('utf-8')
        t=t.replace('Antiquities-Niese-Proem-runtime-20261010','Antiquities-Niese-Proem-Recovery-runtime-20261010')
        if n=='browser_common.cjs': t=t.replace("mode==='baseline'?8922:8920","mode==='baseline'?8927:8926")
        if n=='plain_browser.cjs': t=t.replace('listen(s,8923)','listen(s,8928)')
        (PACK/n).write_bytes(t.encode('utf-8'))
        adapters.append({'file':n,'original_sha256':sha(b),'adapter_sha256':sha(t.encode()),'changes':'isolated runtime; Proem ports 8926/8928; baseline port 8927'})
    for n in records:shutil.copyfile(OLD/n,PACK/n)
    shutil.copytree(OLD/'frozen-inputs',PACK/'frozen-inputs')
    (PACK/'evidence').mkdir()
    (PACK/'.gitignore').write_text('__pycache__/\nBASELINE_PROTECTED_BROWSER.json\nPROTECTED_GIT_OBJECTS.json\nSTRUCTURAL_CONTROLS.json\nFINAL_PROTECTED_BROWSER.full.json\n',encoding='utf-8')
    save('QA_HARNESS_PROVENANCE.json',{'original':str(OLD/'QA_HARNESS_PROVENANCE.json'),'adapters':adapters,'production_edits':False,'source_review_rerun':False})
    save('RECOVERY_BASELINE.json',{'status':'RECOVERED_NOT_YET_CERTIFIED','route':'A','branch':'antiquities-niese-proem-recovery','worktree':str(ROOT),'original_worktree':r'C:\workspace\LatinJosephus-antiquities-niese-proem','original_clean':not subprocess.check_output(['git','status','--porcelain'],cwd=r'C:\workspace\LatinJosephus-antiquities-niese-proem').strip(),'baseline_commit':BASE,'production_commit':PRODUCTION,'recovered_checkpoint':CHECKPOINT,'reconstructed_history':False,'ancestry_verified':True,'archive':record(ZIP),'archive_entries':129,'manifest_files_verified':128,'CRC':'PASS','packet_review_files_match_checkpoint':compare,'production_files':[record(ROOT/n) for n in PRODUCTION_PATHS],'runtime':str(RUNTIME),'preserved_packet':str(archive_dir),'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inherited_history':str(OLD/'history'),'stale_documentation':['packet README.md and EMERGENCY_STOP.md incorrectly abbreviate Latin 25 start as Quod; governing decisions and bytes start Volentius','old BOUNDARIES.csv and IMPLEMENTED_LOCATORS.json are historical; fresh records supersede them']})
    print('PASS Route A: ZIP, 128 manifest files, CRC, ancestry, production and inherited review bytes')
if __name__=='__main__':main()
