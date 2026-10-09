"""Freeze the actual integration starting state and verify the complete certified incoming delta."""
from pathlib import Path
import subprocess, json, hashlib
ROOT = Path(__file__).resolve().parents[2]
PACK = Path(__file__).resolve().parent
CANONICAL = Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
SOURCE = Path('C:/workspace/LatinJosephus-antiquities-niese-12-13')
RUNTIME = Path('C:/workspace/Antiquities-Niese-12-13-integration-runtime-20261009')
BASE = 'ad3158b7a86dea6997510b3de17f2e510c23367c'
TIP = '76083c2831afdb4853f7d7ebab0db6c64c18d914'
START = 'cea765de5d990646b4d4dc079bac1c0da46ca107'
sha = lambda data: hashlib.sha256(data).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf8'))
def git(root, *args): return subprocess.check_output(['git','-C',str(root),*args])
def textgit(root,*args): return git(root,*args).decode('utf8').strip()
def save(name,data): (PACK/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def tracked(root,commit):
    result=[]
    for entry in git(root,'ls-tree','-rz','--full-tree',commit).split(b'\0'):
        if not entry: continue
        metadata,rawpath=entry.split(b'\t',1);mode,kind,blob=metadata.decode().split()
        path=rawpath.decode('utf8');p=root/path
        result.append({'path':path,'mode':mode,'blob':blob,'blob_sha256':sha(git(root,'show',f'{commit}:{path}')),
                       'working_sha256':sha(p.read_bytes()) if p.is_file() else None})
    return result
if __name__ == '__main__':
    assert not (PACK/'BASELINE.json').exists(), 'Do not overwrite the integration freeze'
    assert textgit(SOURCE,'rev-parse','HEAD') == TIP
    assert textgit(SOURCE,'branch','--show-current') == 'antiquities-niese-12-13'
    assert not textgit(SOURCE,'status','--porcelain')
    assert textgit(CANONICAL,'rev-parse','HEAD') == START
    assert textgit(CANONICAL,'branch','--show-current') == 'v2-development'
    assert not textgit(CANONICAL,'status','--porcelain')
    assert textgit(ROOT,'rev-parse','HEAD') == START
    assert textgit(ROOT,'merge-base',START,TIP) == BASE
    assert textgit(ROOT,'branch','--show-current') == 'antiquities-niese-12-13-integration'
    handoff = read(SOURCE/'review/Antiquities_Niese_Batch_12_13_2026-10-09/HANDOFF.json')
    certifications=[]
    for b in [12,13]:
        d=SOURCE/f'review/Antiquities_Niese_Book{"XII" if b==12 else "XIII"}_2026-10-09'
        cert=read(d/'CERTIFICATE.json');manifest=read(d/'FILE_MANIFEST.json')
        assert cert['status']=='LOCAL_CERTIFIED_READY_FOR_COORDINATED_INTEGRATION' and not cert['pending_editorial_decisions']
        assert sha((d/'FILE_MANIFEST.json').read_bytes()) == handoff['packets'][str(b)]['manifest_sha256']
        for item in manifest['files']:
            assert sha((SOURCE/item['path']).read_bytes()) == item['sha256'],item['path']
        for name,h in cert['evidence_sha256'].items():
            p=d/name if (d/name).exists() else SOURCE/'review/Antiquities_Niese_Batch_12_13_2026-10-09'/name
            assert sha(p.read_bytes())==h,p
        for name in ['EDITORIAL_DECISIONS.json','QUALIFIED_CORRESPONDENCE.json','BOUNDARIES.json','APPROVED_MARKER_PLAN.json','FINAL_SOURCE_QA.json','EXPECTED_INTERVALS.json']:
            read(d/name)
        certifications.append({'book':b,'certificate_path':str(d/'CERTIFICATE.json'),'certificate_sha256':sha((d/'CERTIFICATE.json').read_bytes()),
                               'manifest_sha256':sha((d/'FILE_MANIFEST.json').read_bytes()),'status':cert['status'],'bound_evidence_verified':list(cert['evidence_sha256'])})
    for item in handoff['changed_files']: assert sha((SOURCE/item['path']).read_bytes())==item['sha256'],item['path']
    delta=[]
    for line in textgit(ROOT,'diff','--name-status',BASE,TIP).splitlines():
        status,path=line.split('\t');raw=git(ROOT,'show',f'{TIP}:{path}')
        delta.append({'path':path,'status':status,'source_blob':textgit(ROOT,'rev-parse',f'{TIP}:{path}'),
                      'source_blob_sha256':sha(raw),'certified_working_sha256':sha((SOURCE/path).read_bytes()),'bytes':len(raw)})
    production=[i for i in delta if not i['path'].startswith('review/')];review=[i for i in delta if i['path'].startswith('review/')]
    assert len(production)==7 and all(i['path']=='assets/js/renderTei.js' or any(i['path']==f'assets/xml/antiquities/{lang}/book-{b:02}.{ext}' for b in [12,13] for lang,ext in [('Greek','xml'),('Latin','xml'),('niese','json')]) for i in production)
    assert all(any(i['path'].startswith(f'review/{r}/') for r in ['Antiquities_Niese_BookXII_2026-10-09','Antiquities_Niese_BookXIII_2026-10-09','Antiquities_Niese_Batch_12_13_2026-10-09']) for i in review)
    save('INCOMING_SCOPE.json',{'frozen_base':BASE,'source_tip':TIP,'production_count':len(production),'review_count':len(review),'total_count':len(delta),'production':production,'review':review,'certifications':certifications,'complete_source_history':textgit(ROOT,'log','--reverse','--format=%H %s',BASE+'..'+TIP).splitlines(),'result':'PASS'})
    if RUNTIME.exists(): assert not any(RUNTIME.iterdir()), 'Runtime is not empty; inspect ownership before reusing'
    RUNTIME.mkdir(parents=True,exist_ok=True)
    baseline={'canonical_checkout':str(CANONICAL),'canonical_branch':'v2-development','canonical_start':START,'remote_start_directly_verified':START,
              'source_checkout':str(SOURCE),'source_branch':'antiquities-niese-12-13','certified_tip':TIP,'frozen_base':BASE,
              'integration_worktree':str(ROOT),'integration_branch':'antiquities-niese-12-13-integration','runtime':str(RUNTIME),
              'preferred_QA_port':8913,'canonical_tracked_files':tracked(CANONICAL,START),'source_handoff_sha256':sha((SOURCE/'review/Antiquities_Niese_Batch_12_13_2026-10-09/REPORT.md').read_bytes()),
              'repository_instructions':'No AGENTS.md found in checked ancestors or repository inventory','actual_original_locations_were_unused':True,
              'published_preview_scope':'Excluded: no export, repository edit, deployment or domain action','result':'PASS'}
    save('BASELINE.json',baseline)
    print(f'PASS complete certified delta: {len(production)} production + {len(review)} review = {len(delta)} files; manifests and certificate evidence verified')
