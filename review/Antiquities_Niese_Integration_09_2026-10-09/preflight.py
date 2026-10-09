"""One-time frozen integration inventory; never replace an existing baseline."""
from pathlib import Path
import json,hashlib,subprocess,datetime
P=Path(__file__).resolve().parent;W=P.parents[1]
C=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
S=Path('C:/workspace/LatinJosephus-antiquities-niese-09')
R=Path('C:/workspace/Antiquities-Niese-09-integration-runtime-20261009')
B='ad3158b7a86dea6997510b3de17f2e510c23367c';T='b2766fc0a0f9ab8dfb1c4667fbb9c5c4d6eac659'
D='92f009a668507ece4b82bdc4040a2b40b1f2cae7'
def rawgit(*args,where=W):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=where)
def git(*args,where=W):return rawgit(*args,where=where).decode().strip()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
assert not (P/'BASELINE.json').exists(),'Existing frozen baseline must not be overwritten'
assert git('rev-parse','HEAD',where=S)==T and git('branch','--show-current',where=S)=='antiquities-niese-09'
assert not git('status','--porcelain',where=S)
assert git('rev-parse','HEAD',where=C)==git('rev-parse','HEAD')==D
assert git('branch','--show-current',where=C)=='v2-development' and not git('status','--porcelain',where=C)
assert git('rev-parse','origin/v2-development')==D
SP=S/'review/Antiquities_Niese_BookIX_2026-10-09';m=read(SP/'FILE_MANIFEST.json');cert=read(SP/'CERTIFICATION.json')
assert cert['ready_for_integration'] and cert['new_book_reader_QA']=='PASS_CERTIFIED' and not cert['pending_editorial_decisions']
assert cert['Greek_marker_moves']==[181,216,240]
assert cert['Latin_nonempty_reader_intervals']==cert['inherited_Latin_starts']+cert['applied_Latin_milestones']==232
assert cert['expected_identities']==232+59==291
review_files={Path(f['absolute_path']) for f in m['review_files']}
assert review_files=={f for f in SP.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f!=SP/'FILE_MANIFEST.json'}
for f in m['review_files']:
    assert sha(Path(f['absolute_path']).read_bytes())==f['sha256']
for rel,rec in m['production_changes'].items():assert sha((S/rel).read_bytes())==rec['source_sha256']
paths=git('diff','--name-only',B,T).splitlines();assert set(paths)==set(m['Git_changed_files'])
incoming=[]
for rel in paths:
    status=git('diff','--name-status',B,T,'--',rel).split('\t')[0]
    content=rawgit('show',T+':'+rel)
    incoming.append({'path':rel,'status':status,'category':'review' if rel.startswith('review/') else 'production',
      'incoming_Git_blob_id':git('rev-parse',T+':'+rel),'incoming_Git_blob_sha256':sha(content),
      'certified_source_worktree_sha256':sha((S/rel).read_bytes()),'bytes':len(content)})
production=[r for r in incoming if r['category']=='production'];reviews=[r for r in incoming if r['category']=='review']
assert {r['path'] for r in production}==set(m['production_changes'])
assert all(r['path'].startswith('review/Antiquities_Niese_BookIX_2026-10-09/') for r in reviews)
assert len(reviews)==len(review_files)+1
tracked={}
for rel in git('ls-tree','-r','--name-only',D).splitlines():
    tracked[rel]={'Git_blob_id':git('rev-parse',D+':'+rel),'worktree_sha256':sha((W/rel).read_bytes())}
advance=git('diff','--name-only',B,D).splitlines()
assert 'assets/js/renderTei.js' not in advance
assert not set(paths)&set(advance),'Unexpected overlapping canonical advance'
authority=Path('C:/Users/Pollard_R/.codex/attachments/3e48b3c3-11d5-41f6-9fa8-56bc30e6d50e/Pasted text.txt')
baseline={'recorded_UTC':datetime.datetime.now(datetime.UTC).isoformat(),'frozen_IX_base':B,'certified_source_HEAD':T,
 'certified_source_branch':'antiquities-niese-09','certified_source_worktree':str(S),'source_initial_status':'CLEAN',
 'canonical_initial_HEAD':D,'canonical_branch':'v2-development','canonical_initial_status':'CLEAN','canonical_worktree':str(C),
 'origin':'https://github.com/LatinJosephus/latin-josephus-2.git','directly_verified_origin_HEAD':D,
 'integration_branch':'antiquities-niese-09-integration','integration_worktree':str(W),'review':str(P),'runtime':str(R),
 'preferred_QA_origin':'http://127.0.0.1:8910','proposed_locations_were_absent':True,'applicable_AGENTS_found':[],
 'authority_attachment':str(authority),'authority_sha256':sha(authority.read_bytes()),
 'incoming_production_count':len(production),'incoming_review_count':len(reviews),'incoming_total':len(paths),
 'canonical_advance_paths':advance,'canonical_advance_commits':git('log','--reverse','--format=%H %s',B+'..'+D).splitlines(),
 'canonical_initial_tracked_files':tracked,'source_manifest_sha256':sha((SP/'FILE_MANIFEST.json').read_bytes()),
 'source_certification_sha256':sha((SP/'CERTIFICATION.json').read_bytes()),'source_decision_sha256':sha((SP/'DECISION_240.md').read_bytes()),
 'Git_version':git('--version'),'integration_method':'Merge complete certified source into actual canonical in isolation, then fast-forward canonical'}
write(P/'INCOMING_SCOPE.json',{'base':B,'source_HEAD':T,'production_count':len(production),'review_count':len(reviews),'total':len(incoming),'files':incoming})
write(P/'BASELINE.json',baseline)
write(R/'OWNERSHIP.json',{'assignment':'Antiquities IX canonical integration 2026-10-09','integration_worktree':str(W),'review':str(P),'source_HEAD':T})
print(f'PASS: complete incoming scope = {len(production)} production + {len(reviews)} review = {len(incoming)} files; certified hashes exact; canonical advance preserved')
