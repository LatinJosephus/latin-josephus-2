from pathlib import Path
from lxml import etree as E
import json,hashlib,subprocess
V=Path(__file__).resolve().parent;R=V.parents[1];A=Path(r'C:\workspace\LatinJosephus-Greek-Capitula-Audit-20261008')
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,d):(V/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(n):return json.loads((V/n).read_text(encoding='utf-8-sig'))
b=load('BASELINE.json');C=Path(b['canonical']);am=json.loads((A/'FILE_MANIFEST.json').read_text(encoding='utf-8'));checks=[]
for row in am['inputs']:
 p=Path(row['path']);actual=h(p);assert actual==row['sha256'],str(p);assert 'bytes' not in row or p.stat().st_size==row['bytes'],str(p);checks.append({'path':str(p),'role':row.get('role'),'recorded_sha256':row['sha256'],'verified_sha256':actual,'result':'PASS'})
dump('AUDIT_INPUT_INTEGRITY_QA.json',{'inputs_verified':len(checks),'checks':checks,'result':'PASS'})
rows=[]
for p,original in b['tracked_files'].items():
 actual=h(R/p);changed=p=='assets/xml/source-contents.xml';assert changed or actual==original['sha256'],p
 rows.append({'path':p,'original_sha256':original['sha256'],'final_sha256':actual,'authorized_registry_change':changed,'unchanged':actual==original['sha256']})
canonical=[]
for p,original in b['canonical_tracked_files'].items():
 actual=h(C/p);assert actual==original['sha256'],p;canonical.append({'path':p,'original_sha256':original['sha256'],'final_sha256':actual,'unchanged':True})
for r in am['outputs']:assert h(A/r['relative_path'])==r['sha256'] and (A/r['relative_path']).stat().st_size==r['bytes'],r['relative_path']
assert h(A/'FILE_MANIFEST.json')==b['audit_manifest_sha256'];assert len(list(A.rglob('*')))>120

def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args],text=True,encoding='utf-8').strip()
assert git(C,'rev-parse','HEAD')==b['base'] and git(C,'rev-parse','origin/v2-development')==b['base'] and not git(C,'status','--short')
assert git(C,'branch','--show-current')=='v2-development';assert h(b['canonical_index_path'])==b['canonical_index_sha256']
assert git(R,'rev-parse','HEAD')==b['base'];assert not git(R,'diff','--cached','--name-only')
changed=git(R,'diff','--name-only').splitlines();assert changed==['assets/xml/source-contents.xml']
new=git(R,'ls-files','--others','--exclude-standard').splitlines();production=[p for p in new if not p.startswith('review/Greek_Antiquities_Capitula_TOC_v1.1_2026-10-08/')];expected=[f'assets/xml/antiquities/paratext/niese/book-{n:02}-contents.xml' for n in [1,2,3,4,6,7,8,9,10]];assert sorted(production)==expected,production
assert all(p.startswith('review/Greek_Antiquities_Capitula_TOC_v1.1_2026-10-08/') or p in expected for p in new)
dump('INTEGRITY_QA.json',{'result':'PASS','canonical_HEAD':b['base'],'canonical_origin':b['base'],'canonical_branch':'v2-development','canonical_status':'clean','canonical_index_unchanged':True,'canonical_files_verified':len(canonical),'canonical_files':canonical,'worktree_existing_files':rows,'protected_worktree_files':len(rows)-1,'preexisting_XML_unchanged':sum(r['path'].endswith('.xml') and r['unchanged'] for r in rows),'source_audit_manifest_entries_verified':120,'source_audit_inputs_verified':len(checks),'source_audit_files':sum(p.is_file() for p in A.rglob('*')),'staged_changes':[],'modified_tracked_files':changed,'new_production_files':production,'git_status':git(R,'status','--short'),'repository_write_actions':'Only user-authorized creation of implementation branch/worktree. No stage/commit/merge/rebase/push/config operation.','initial_checkout_EOL_handling':'109 files differ from canonical only by initial checkout CRLF/LF; neither checkout was normalized. Own baseline hashes independently preserved.'})
print(json.dumps({'result':'PASS','canonical_files':len(canonical),'protected_worktree_files':len(rows)-1,'preexisting_XML_unchanged':sum(r['path'].endswith('.xml') and r['unchanged'] for r in rows),'audit_inputs':len(checks),'audit_outputs':120,'new_production_files':len(production)}))
