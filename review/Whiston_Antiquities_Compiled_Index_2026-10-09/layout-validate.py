from pathlib import Path
from lxml import etree as E
import json,hashlib,subprocess
V=Path(__file__).resolve().parent;R=V.parents[1];L=V/'layout-correction';C=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development');B=json.loads((L/'BASELINE.json').read_text(encoding='utf-8'));N={'t':'http://www.tei-c.org/ns/1.0'}
def read(n):return json.loads((L/n).read_text(encoding='utf-8'))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(p,*a):return subprocess.check_output(['git','--no-optional-locks','-C',str(p),*a]).decode().strip()
def digest(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
checks=[]
def check(n,ok,detail=None):checks.append({'name':n,'result':'PASS' if ok else 'FAIL','detail':detail});assert ok,(n,detail)
wt={p:h(R/p) for p in B['worktree_files']};changed=[p for p in wt if wt[p]!=B['worktree_files'][p]['sha256']];check('only_stylesheet_changed',changed==['assets/css/tei.css'],changed)
protected={p:v for p,v in wt.items() if p!='assets/css/tei.css'};xml={p:v for p,v in protected.items() if p.startswith('assets/xml/') and p.endswith('.xml')};check('all_baseline_XML_bytes_preserved',len(xml)==len([p for p in B['worktree_files'] if p.startswith('assets/xml/') and p.endswith('.xml')]),len(xml))
can={p:h(C/p) for p in B['canonical_files']};check('canonical_all_files_identical',all(v==B['canonical_files'][p]['sha256'] for p,v in can.items()),len(can))
for root,idx in B['indices'].items():check('index_'+root,h(Path(idx['path']))==idx['sha256'])
check('canonical_state',git(C,'rev-parse','HEAD')==B['canonical_HEAD'] and git(C,'rev-parse','origin/v2-development')==B['canonical_origin'] and git(C,'status','--short')==B['canonical_status'])
check('implementation_state',git(R,'rev-parse','HEAD')==B['worktree_HEAD'] and git(R,'branch','--show-current')==B['branch'] and git(R,'diff','--cached','--name-only')=='')
check('prior_presentation_evidence_unchanged',all(h(V/p)==s for p,s in B['prior_presentation_review_files'].items()),len(B['prior_presentation_review_files']))
check('CSS_only_appended', (R/'assets/css/tei.css').read_bytes().startswith((L/'before-source/assets/css/tei.css').read_bytes()))
expected=[22,16,15,8,11,14,15,15,14,11,8,11,16,16,11,11,13,9,9,11];headings=[]
for b,c in enumerate(expected,1):
 p=R/f'assets/xml/antiquities/paratext/whiston/book-{b:02}-contents.xml';d=E.parse(str(p));items=d.xpath('//t:div[@type="contents"]/t:list/t:item',namespaces=N);check(f'book_{b}_paired_source_counts',len(items)==c and len(d.xpath('//t:div[@type="contents"]/t:list/t:label',namespaces=N))==c);headings+=items
check('256_original_and_display_pairs',len(headings)==256 and all(x.find('t:choice/t:orig',N) is not None and x.find('t:choice/t:reg',N) is not None for x in headings));check('registry_59_unchanged',len(E.parse(str(R/'assets/xml/source-contents.xml')).xpath('//t:list[@type="source-contents"]/t:item',namespaces=N))==59)
a=read('LAYOUT_QA.json');before=read('BEFORE_QA.json');check('all_1024_entry_geometries_PASS',a['result']=='PASS' and len(a['checks'])==80 and a['entryChecks']==1024);check('narrow_and_wide_both_themes',{x['width'] for x in a['checks']}=={1200,1690} and {x['theme'] for x in a['checks']}=={'light','dark'})
for x in before['checks']:
 y=next(v for v in a['checks'] if (v['width'],v['theme'],v['book'])==(x['width'],x['theme'],x['book']));check('book_material_unchanged_%s_%s_%s' % (x['book'],x['width'],x['theme']),len(x['above'])==len(y['above']) and all({k:v for k,v in p.items() if k!='top'}=={k:v for k,v in q.items() if k!='top'} and abs(p['top']-q['top'])<1 for p,q in zip(x['above'],y['above'])))
scope=read('CSS_SCOPE_QA.json');browser=read('CONTENTS_REGRESSION_QA.json');check('16_foreign_and_narrative_typography_checks',scope['result']=='PASS' and len(scope['checks'])==16);check('40_displays_59_records_20_URL_history_panes',browser['result']=='PASS' and browser['themeDisplays']==40 and len(browser['existing'])==39 and len(browser['interactions'])==20)
q={'result':'PASS','checks':checks,'executed_checks':len(checks),'protected_worktree_files':len(protected),'protected_XML_files':len(xml),'canonical_files':len(can),'canonical_HEAD':B['canonical_HEAD'],'worktree_HEAD':B['worktree_HEAD'],'branch':B['branch'],'original_protected_inventory_sha256':digest({p:B['worktree_files'][p]['sha256'] for p in protected}),'final_protected_inventory_sha256':digest(protected),'XML_before_inventory_sha256':digest({p:B['worktree_files'][p]['sha256'] for p in xml}),'XML_after_inventory_sha256':digest(xml),'CSS':read('FILE_CHANGES.json'),'original_headings_preserved':256,'regularized_headings_preserved':256,'registry_records_preserved':59,'source_changes_other_than_CSS':0,'indices_byte_identical':True,'staged_changes':0,'prior_evidence_preserved':True,'worktree_status':git(R,'status','--short')}
(L/'INTEGRITY_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('LAYOUT_INTEGRITY_PASS',len(checks),len(xml),'unchanged XML files;',len(protected),'protected source files')
