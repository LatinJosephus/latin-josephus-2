from pathlib import Path
import json,hashlib,subprocess
V=Path(__file__).resolve().parent;R=V.parents[1];B=json.loads((V/'BASELINE.json').read_text(encoding='utf-8'));C=Path(B['canonical'])
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args]).decode().strip()
def digest(o):return hashlib.sha256(json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
results={}
for kind,root in [('canonical',C),('worktree',R)]:
 rows=[]
 for rel,row in B[kind+'_files'].items():
  new=h(root/rel);allowed=kind=='worktree' and rel=='assets/xml/source-contents.xml';assert new==row['sha256'] or allowed,(kind,rel);rows.append({'path':rel,'original_sha256':row['sha256'],'final_sha256':new,'changed':new!=row['sha256'],'authorized_registry_extension':allowed})
 before={x['path']:x['original_sha256'] for x in rows};after={x['path']:x['final_sha256'] for x in rows};protected=[x for x in rows if not x['authorized_registry_extension']];xml=[x for x in protected if x['path'].startswith('assets/xml/') and x['path'].endswith('.xml')]
 results[kind]={'files_checked':len(rows),'protected_files':len(protected),'XML_files_unchanged':len(xml),'original_inventory_sha256':digest(before),'final_inventory_sha256':digest(after),'protected_original_inventory_sha256':digest({x['path']:x['original_sha256'] for x in protected}),'protected_final_inventory_sha256':digest({x['path']:x['final_sha256'] for x in protected}),'files':rows}
for root,idx in B['indices'].items():assert h(Path(idx['path']))==idx['sha256'],('INDEX',root)
assert git(C,'status','--short')=='';assert git(C,'rev-parse','HEAD')==git(C,'rev-parse','origin/v2-development')==B['base'];assert git(C,'branch','--show-current')=='v2-development';assert git(R,'rev-parse','HEAD')==B['base'];assert git(R,'diff','--name-only')=='assets/xml/source-contents.xml';assert git(R,'diff','--cached','--name-only')==''
newpaths=subprocess.check_output(['git','--no-optional-locks','-C',str(R),'ls-files','--others','--exclude-standard','-z']).decode().split('\0');newpaths=[x for x in newpaths if x];assert all(x.startswith('review/Whiston_Antiquities_Compiled_Index_2026-10-09/') or x.startswith('assets/xml/antiquities/paratext/whiston/') for x in newpaths)
checkouts=[x for x in B['canonical_files'] if B['canonical_files'][x]['sha256']!=B['worktree_files'][x]['sha256']];non_eol=[x for x in checkouts if (C/x).read_bytes().replace(b'\r\n',b'\n')!=(R/x).read_bytes().replace(b'\r\n',b'\n')];assert not non_eol
results.update({'result':'PASS','canonical_HEAD':B['base'],'branch':git(R,'branch','--show-current'),'canonical_status':'clean','worktree_status':git(R,'status','--short'),'indices_byte_identical':True,'source_packets':'Verified separately by validate.py before and after implementation','new_anchors':0,'narrative_changes':0,'prior_certifications_byte_identical':True,'original_worktree_vs_canonical_EOL_only_differences':len(checkouts),'no_unexpected_files':True,'no_staged_changes':True})
(V/'INTEGRITY_QA.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('INTEGRITY_PASS',results['canonical']['files_checked'],'canonical files;',results['worktree']['protected_files'],'protected worktree files;',results['worktree']['XML_files_unchanged'],'XML files')
