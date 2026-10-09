"""Prove complete merge scope and exact IX preservation without modifying source records."""
from pathlib import Path
import json,hashlib,subprocess,datetime
P=Path(__file__).resolve().parent;W=P.parents[1];R=Path('C:/workspace/Antiquities-Niese-09-integration-runtime-20261009')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(v):return hashlib.sha256(v).hexdigest()
def git(*args):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=W).decode().strip()
b=read(P/'BASELINE.json');scope=read(P/'INCOMING_SCOPE.json');SP=W/'review/Antiquities_Niese_BookIX_2026-10-09'
source=Path(b['certified_source_worktree']);prod={r['path'] for r in scope['files'] if r['category']=='production'}
assert set(git('diff','--name-only',b['canonical_initial_HEAD'],'--','assets','_includes').splitlines())==prod
for r in scope['files']:
    assert git('rev-parse','HEAD:'+r['path'])==r['incoming_Git_blob_id']
    assert sha((W/r['path']).read_bytes())==r['certified_source_worktree_sha256'],r['path']
retained=0
for rel,rec in b['canonical_initial_tracked_files'].items():
    if rel in prod:continue
    assert sha((W/rel).read_bytes())==rec['worktree_sha256'],rel
    retained+=1
impl=read(SP/'IMPLEMENTATION_PRESERVATION.json');frozen=read(SP/'BASELINE.json');recovery={}
for lang in ['Greek','Latin','English']:
    rel=f'assets/xml/antiquities/{lang}/book-09.xml';actual=(W/rel).read_bytes();original=Path(frozen['inputs'][rel]['snapshot']).read_bytes()
    assert sha(original)==frozen['inputs'][rel]['worktree_sha256']
    recovered=actual
    if lang!='English':
        for op in sorted(impl['sources'][lang]['inverse_operations'],key=lambda o:(o['at'],o['delete']),reverse=True):
            old=bytes.fromhex(op['before_hex']);new=bytes.fromhex(op['after_hex']);at=op['at'];assert recovered[at:at+len(old)]==old
            recovered=recovered[:at]+new+recovered[at+len(old):]
    assert recovered==original
    recovery[lang]={'before_sha256':sha(original),'integrated_sha256':sha(actual),'recovered_sha256':sha(recovered),'byte_exact_recovery':True,'built_byte_equal':actual==(R/'build/site'/rel).read_bytes()}
    assert recovery[lang]['built_byte_equal']
assets={}
for rel in sorted(prod|{'assets/css/tei.css','assets/xml/source-contents.xml','assets/xml/antiquities/paratext/whiston/book-09-contents.xml'}):
    actual=(W/rel).read_bytes();built=(R/'build/site'/rel).read_bytes();assert actual==built
    assets[rel]={'worktree_sha256':sha(actual),'built_sha256':sha(built),'byte_equal':True,
      'certified_IX_file':rel in prod,'current_canonical_advance_file':rel not in prod}
head=git('rev-parse','HEAD');assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=source).decode().strip()==b['certified_source_HEAD']
assert not subprocess.check_output(['git','status','--porcelain'],cwd=source).decode().strip()
out={'result':'PASS','recorded_UTC':datetime.datetime.now(datetime.UTC).isoformat(),'tested_implementation_HEAD':head,
 'incoming_production_count':scope['production_count'],'incoming_review_count':scope['review_count'],
 'all_incoming_files_match_certified_source':True,'all_retained_canonical_files_byte_equal':retained,
 'canonical_advance_preserved':True,'reconciliation_required':False,'production_resolution_paths':[],
 'relevant_production_equals_certified_IX':True,'exhaustive_certification_retained':'review/Antiquities_Niese_BookIX_2026-10-09/CERTIFICATION.json',
 'source_recovery':recovery,'built_assets':assets,'certified_source_HEAD_unchanged':True,'certified_source_worktree_clean':True}
(P/'INTEGRITY_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(f'PASS: all {scope["total"]} incoming files exact; {retained} original canonical files retained; source-byte recovery and fresh build hashes exact')
