from pathlib import Path
import hashlib,json,subprocess,shutil,tempfile
P=Path(__file__).resolve().parent; R=P.parents[1]; C=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
W=R/'review/Whiston_Antiquities_Compiled_Index_2026-10-09'; N=R/'review/Antiquities_Niese_Implementation_08_10_2026-10-09'
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args])
def h(raw):return hashlib.sha256(raw).hexdigest()
def save(name,obj):(P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def inv(root):
 paths=git(root,'ls-files','-z').decode().split('\0');return {p:{'sha256':h((root/p).read_bytes()),'bytes':(root/p).stat().st_size} for p in paths if p}
def state(root):return {k:git(root,*a).decode().strip() for k,a in {'HEAD':['rev-parse','HEAD'],'branch':['branch','--show-current'],'status':['status','--short'],'origin':['rev-parse','origin/v2-development']}.items()}
b={'integration':state(R),'canonical':state(C),'integration_files':inv(R),'canonical_files':inv(C),'integration_index':h(Path(git(R,'rev-parse','--path-format=absolute','--git-path','index').decode().strip()).read_bytes()),'canonical_index':h(Path(git(C,'rev-parse','--path-format=absolute','--git-path','index').decode().strip()).read_bytes())}
b['integration']['certification_untracked']=b['integration']['status']; assert all(P.name in line for line in b['integration']['status'].splitlines()); b['integration']['status']=''
assert b['integration']['HEAD']=='6ef5cf7d6c19528ef26cdee855aabd57735f1877' and b['integration']['branch']=='codex/whiston-niese-combined-integration' and not b['integration']['status']
assert b['canonical']['HEAD']==b['canonical']['origin']=='ad3158b7a86dea6997510b3de17f2e510c23367c' and b['canonical']['branch']=='v2-development' and not b['canonical']['status']
assert git(R,'rev-list','--left-right','--count',b['canonical']['HEAD']+'...HEAD').decode().strip()=='0\t2'
save('BASELINE.json',b)
paths=git(R,'diff','--name-only','ad3158b...HEAD').decode().splitlines(); original=git(R,'diff','--name-only','a480215...e373ee1').decode().splitlines()
assert paths==original and len(paths)==501
rows=[]
for p in paths:
 a=git(R,'show','e373ee1:'+p);z=(R/p).read_bytes();assert a==z,p
 rows.append({'path':p,'sha256':h(z),'bytes':len(z),'original_commit':'e373ee190a153e717ccad20de969033c5510bfd4','result':'PASS'})
assert sum(not p.startswith('review/') for p in paths)==22
save('CHERRY_PICK_INTEGRITY.json',{'result':'PASS','changed_files':501,'production_files':22,'historical_certification_files':479,'original_production_commit':git(R,'rev-parse','3553a74').decode().strip(),'original_certification_commit':git(R,'rev-parse','e373ee1').decode().strip(),'cherry_picked_production':git(R,'rev-parse','a858356').decode().strip(),'cherry_picked_certification':b['integration']['HEAD'],'rows':rows})
np=['_includes/display-settings.html','assets/js/renderTei.js']+[f'assets/xml/antiquities/{l}/book-{n:02}.xml' for l in ['Greek','Latin'] for n in [8,10]]+[f'assets/xml/antiquities/niese/book-{n:02}.json' for n in [8,10]]
assert all((R/p).read_bytes()==(C/p).read_bytes() for p in np)
save('SOURCE_PRESERVATION_PREFLIGHT.json',{'result':'PASS','canonical_Niese_files':[{'path':p,'sha256':h((R/p).read_bytes())} for p in np]})
site=Path(tempfile.gettempdir())/'LatinJosephus-Whiston-Niese-Combined-disposable-20261009';assert not site.exists(),str(site)
save('ENVIRONMENT.json',{'build':str(site),'build_policy':'separate disposable build; no source writes; review excluded; local installed Jekyll; responsive-image plugin unavailable locally and omitted only in build options'})
# Copy accepted verification programs; only their output/data/build paths change.
for name in ['CONTENTS_EXPECTATIONS.json','EXISTING_CONTENTS_EXPECTATIONS.json']:shutil.copyfile(W/name,P/name)
shutil.copyfile(N/'EXPECTED_INTERVALS.json',P/'EXPECTED_INTERVALS.json')
shutil.copyfile(W/'build_disposable.rb',P/'build_disposable.rb')
for name in ['layout-qa.test.cjs','layout-contents-regression.test.cjs']:
 s=(W/name).read_text();s=s.replace('C:/Users/Pollard_R/AppData/Local/Temp/LatinJosephus-Whiston-Index-disposable-20261009',site.as_posix()).replace("const capture=path.join(__dirname,'layout-correction');","const capture=path.join(__dirname,'screenshots');").replace('layout-correction/','')
 (P/name).write_text(s,encoding='utf-8')
# Exhaustive accepted range suite uses actual freshly built HTML.
s=(N/'established-regressions.test.cjs').read_text().replace('C:/workspace/Antiquities-Niese-Implementation-08-10-2026-10-09/build/site',site.as_posix())
(P/'established-regressions.test.cjs').write_text(s,encoding='utf-8')
# Bamberg suite evaluates actual current renderer; no fixture source edits.
s=(W/'bamberg-regression.test.cjs').read_text();(P/'bamberg-regression.test.cjs').write_text(s,encoding='utf-8')
# New-book suite compares all expected interval texts and drives all selector events.
s=(N/'browser-certify.cjs').read_text().replace("build='C:/workspace/Antiquities-Niese-Implementation-08-10-2026-10-09/build'","build="+json.dumps(str(site.parent))).replace("path.join(build,'site')",json.dumps(site.as_posix())).replace("path.join(build,'baseline-site')",json.dumps(site.as_posix()))
# output screenshots in new packet, not historical packet.
(P/'niese-browser.test.cjs').write_text(s,encoding='utf-8')
(P/'screenshots').mkdir();(P/'diagnostics').mkdir()
# Fresh source/schema validation reads prior authorities but writes only this packet.
s=(W/'validate.py').read_text();s=s.replace("V=Path(__file__).resolve().parent;R=V.parents[1];", "O=Path(__file__).resolve().parent;V=O.parent/'Whiston_Antiquities_Compiled_Index_2026-10-09';R=O.parents[1];").replace("(V/n).write_text", "(O/n).write_text")
(P/'validate-contents.py').write_text(s,encoding='utf-8')
print('BASELINE_PASS',len(b['integration_files']),len(b['canonical_files']),'CHERRY_PICK_501_PASS')
