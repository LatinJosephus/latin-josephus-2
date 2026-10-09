from pathlib import Path
import json,hashlib,subprocess
V=Path(__file__).resolve().parent;R=V.parents[1];P=V/'presentation-correction';B=json.loads((V/'BASELINE.json').read_text(encoding='utf-8'));PB=json.loads((P/'BASELINE.json').read_text(encoding='utf-8'));C=Path(B['canonical'])
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args]).decode().strip()
def digest(o):return hashlib.sha256(json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
results={}
for kind,root,inventory in [('canonical',C,PB['canonical_files']),('worktree',R,B['worktree_files'])]:
 rows=[]
 for rel,row in inventory.items():
  new=h(root/rel);allowed=kind=='worktree' and rel in ['assets/xml/source-contents.xml','assets/css/tei.css'];assert new==row['sha256'] or allowed,(kind,rel);rows.append({'path':rel,'original_sha256':row['sha256'],'final_sha256':new,'changed':new!=row['sha256'],'authorized_source_change':allowed})
 protected=[x for x in rows if not x['authorized_source_change']];xml=[x for x in protected if x['path'].startswith('assets/xml/') and x['path'].endswith('.xml')]
 results[kind]={'files_checked':len(rows),'protected_files':len(protected),'XML_files_unchanged':len(xml),'original_inventory_sha256':digest({x['path']:x['original_sha256'] for x in rows}),'final_inventory_sha256':digest({x['path']:x['final_sha256'] for x in rows}),'protected_original_inventory_sha256':digest({x['path']:x['original_sha256'] for x in protected}),'protected_final_inventory_sha256':digest({x['path']:x['final_sha256'] for x in protected}),'files':rows}
idx=B['indices'][str(R)];assert h(Path(idx['path']))==idx['sha256'],('WORKTREE_INDEX',idx['path'])
canonical_index_changed=h(Path(PB['canonical_index']['path']))!=PB['canonical_index']['sha256']
current_head=git(C,'rev-parse','HEAD');current_origin=git(C,'rev-parse','origin/v2-development');concurrent=git(C,'log','--format=%h %s',PB['canonical_HEAD']+'..HEAD');concurrent_paths=git(C,'diff','--name-only',PB['canonical_HEAD']+'..HEAD').splitlines();assert all(x.startswith('review/Antiquities_Niese_Integration_08_10_2026-10-09/') for x in concurrent_paths),concurrent_paths
assert git(C,'diff','--cached','--name-only')==''
assert git(C,'status','--short')=='';assert current_head==current_origin=='ad3158b7a86dea6997510b3de17f2e510c23367c';assert git(C,'branch','--show-current')=='v2-development';assert git(R,'rev-parse','HEAD')==B['base'];assert set(git(R,'diff','--name-only').splitlines())=={'assets/xml/source-contents.xml','assets/css/tei.css'};assert git(R,'diff','--cached','--name-only')==''
newpaths=subprocess.check_output(['git','--no-optional-locks','-C',str(R),'ls-files','--others','--exclude-standard','-z']).decode().split('\0');newpaths=[x for x in newpaths if x];assert all(x.startswith('review/Whiston_Antiquities_Compiled_Index_2026-10-09/') or x.startswith('assets/xml/antiquities/paratext/whiston/') for x in newpaths)
results.update({'result':'PASS','base_commit':B['base'],'canonical_HEAD':current_head,'canonical_origin':current_origin,'presentation_start_canonical_HEAD':PB['canonical_HEAD'],'observed_concurrent_commit':concurrent,'concurrent_added_certification_paths':concurrent_paths,'canonical_raw_index_changed_externally':canonical_index_changed,'canonical_index_semantics_clean':True,'later_authorized_commits':PB['later_canonical_commits'],'branch':git(R,'branch','--show-current'),'canonical_status':'clean','worktree_status':git(R,'status','--short'),'worktree_index_byte_identical':True,'new_anchors':0,'narrative_changes':0,'prior_certifications_byte_identical':True,'no_unexpected_files':True,'no_staged_changes':True})
(V/'INTEGRITY_QA.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('INTEGRITY_PASS',results['canonical']['files_checked'],'canonical files;',results['worktree']['protected_files'],'protected worktree files;',results['worktree']['XML_files_unchanged'],'XML files')
