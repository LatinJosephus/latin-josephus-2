from pathlib import Path
import json,sys,subprocess,hashlib,re,pdfplumber
P=Path(__file__).resolve().parent; W=P.parents[1]
R=Path('C:/workspace/Antiquities-Niese-09-runtime-20261009')
sys.path.insert(0,str(W/'review/Antiquities_Niese_BookX_2026-10-08'))
from mixed_mapper import Book,fixtures,digest,NS
def save(name,obj): (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def git(*args,cwd=W):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=cwd)
R.mkdir(exist_ok=True);(P/'inputs').mkdir(exist_ok=True);(P/'evidence').mkdir(exist_ok=True)
baseline={'base':'ad3158b7a86dea6997510b3de17f2e510c23367c','canonical_initial_HEAD':git('rev-parse','HEAD',cwd='C:/Users/Pollard_R/Git/LatinJosephus-v2-development').decode().strip(),'branch':git('branch','--show-current').decode().strip(),'worktree':str(W),'review':str(P),'runtime':str(R),'repository_instructions_found':[],'inputs':{},'controls':{},'mapper_fixtures':fixtures()}
for rel in [f'assets/xml/antiquities/{lang}/book-09.xml' for lang in ['Greek','Latin','English']]+['assets/js/renderTei.js','_includes/display-settings.html','assets/xml/antiquities/structure.xml']:
 raw=(W/rel).read_bytes(); blob=git('show',baseline['base']+':'+rel)
 snap=P/'inputs'/rel.replace('/','__'); assert not snap.exists() or snap.read_bytes()==raw;snap.write_bytes(raw)
 baseline['inputs'][rel]={'absolute_path':str(W/rel),'snapshot':str(snap),'worktree_sha256':digest(raw),'git_blob_sha256':digest(blob),'git_blob_id':git('rev-parse',baseline['base']+':'+rel).decode().strip(),'worktree_bytes':len(raw),'git_blob_bytes':len(blob),'UTF8':True,'BOM':raw.startswith(b'\xef\xbb\xbf'),'CRLF':raw.count(b'\r\n'),'LF':raw.count(b'\n'),'working_bytes_equal_blob':raw==blob,'CRLF_to_LF_equals_blob':raw.replace(b'\r\n',b'\n')==blob,'last_source_commit':git('log','-1','--format=%H','--',rel).decode().strip()}
for name,path,expected in [('Niese','C:/workspace/Antiquities-Niese-Batch-08-10/Niese-PDFs/Niese (1885) - Antiquities VI-X.pdf','040c1570bc25730fa2c98b2f9ae847646af67919b6a634c2685628601de12b44'),('Loeb','C:/workspace/Loeb Josephus Volumes/Josephus Jewish Antiquities (Books 9-11) (Ralph Marcus) (z-library.sk, 1lib.sk, z-lib.sk).pdf','cda46526761f421ffe3f9c2eec79b1672d5c1160dd7f51f16166c48f09736226')]:
 q=Path(path);h=digest(q.read_bytes());assert h==expected;doc=pdfplumber.open(q)
 baseline['controls'][name]={'absolute_path':str(q),'sha256':h,'bytes':q.stat().st_size,'pages':len(doc.pages),'metadata':doc.metadata,'matches_accepted_control':True}
 for i in list(range(0,12)) + ([274,275,276,277,335,336,337] if name=='Niese' else [15,16,17,166,167,168,169,170,171]):
  page=doc.pages[i]; page.to_image(resolution=115).save(P/'evidence'/f'{name}-pdf-{i+1:03}.png')
  (R/f'{name}-{i+1:03}.txt').write_text(page.extract_text() or '',encoding='utf8')
save('BASELINE.json',baseline)
books={lang:Book(W/f'assets/xml/antiquities/{lang}/book-09.xml') for lang in ['Greek','Latin','English']}
inventory={}
for lang,b in books.items():
 inventory[lang]={'units':[{'id':u['id'],'text':u['text'],'start':u['book_start'],'raw_hash':u['raw_hash'],'sameAs':u['element'].get('sameAs'),'excluded_reason':u['excluded_reason']} for u in b.units],'labels':b.labels,'excluded':b.excluded,'narrative_length':len(b.stream)}
save('SOURCE_INVENTORY.json',inventory)
g=books['Greek'];nums={int(re.findall(r'\d+',m['text'])[-1]):m for m in g.labels};starts={n:g.first_content(m['book_offset']) for n,m in nums.items()};starts[1]=g.first_content(0)
rows=[]
for n,k in sorted(starts.items()):
 end=starts.get(n+1,len(g.stream));loc=g.locate(k);u=g.units[loc['paragraph']-1];target=u['element'].get('sameAs','').lstrip('#');lu=next((x for x in books['Latin'].units if x['id']==target),None)
 rows.append({'niese':n,'greek':g.stream[k:end],'greek_locator':loc,'latin_target':target,'latin_target_text':lu['text'] if lu else None,'greek_print_status':'NOT_REVIEWED','latin_status':'NOT_REVIEWED','editorial_status':'PENDING_REVIEW'})
save('INITIAL_GREEK_CENSUS.json',rows)
print(json.dumps({'baseline':baseline['base'],'canonical':baseline['canonical_initial_HEAD'],'explicit_Greek':len(g.labels),'Greek_numbers':[min(nums),max(nums)],'missing_in_1_to_terminal':sorted(set(range(1,max(nums)+1))-set(nums)),'Latin_labels':len(books['Latin'].labels),'Latin_excluded':books['Latin'].excluded,'fixtures':baseline['mapper_fixtures']},ensure_ascii=False,indent=2))
