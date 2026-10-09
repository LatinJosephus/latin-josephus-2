"""Read-only source freeze for this exact XII/XIII assignment; no corpus edits."""
from pathlib import Path
import sys,json,hashlib,subprocess,re
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
PACK=Path(__file__).resolve().parent
RUNTIME=Path('C:/workspace/Antiquities-Niese-12-13-runtime-20261009')
BASE='ad3158b7a86dea6997510b3de17f2e510c23367c'
CANON=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookX_2026-10-08'))
from mixed_mapper import Book,fixtures,digest,NS

def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def git(*args,cwd=ROOT):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=cwd)
def file_record(p):
 raw=p.read_bytes()
 return dict(path=str(p.resolve()),sha256=digest(raw),bytes=len(raw))
assert git('rev-parse','HEAD').decode().strip()==BASE
shared={'assignment':'XII and XIII only','base':BASE,'branch':git('branch','--show-current').decode().strip(),'worktree':str(ROOT),'canonical_HEAD_at_freeze':git('rev-parse','HEAD',cwd=CANON).decode().strip(),'runtime':str(RUNTIME),'preferred_QA_origin':'http://127.0.0.1:8912/','ownership_check':'Branch and proposed worktree/runtime absent before creation; new branch created from exact authorized base; no reset/switch of canonical','repository_instructions':'No AGENTS.md in worktree or checked applicable ancestor locations','mixed_mapper_fixtures':fixtures(),'publication_record':file_record(Path('C:/workspace/Antiquities-Niese-Preview-08-10-2026-10-09/PUBLICATION_SUMMARY.json'))}
sources=[Path('C:/workspace/Niese Antiquities/batch-02/operajosephus03joseuoft.pdf'),Path('C:/workspace/Antiquities-Niese-Batch-08-10/Niese-PDFs/Niese (1892) - Antiquities XI-XV.pdf'),Path('C:/workspace/Loeb Josephus Volumes/josephus jewish antiquities books XII-XIV VII (Unknown) (z-library.sk, 1lib.sk, z-lib.sk).pdf')]
shared['PDF_inventory']=[]
for i,p in enumerate(sources):
 r=file_record(p);reader=PdfReader(p);r.update(pages=len(reader.pages),metadata={str(k):str(v) for k,v in (reader.metadata or {}).items()},printed_title_and_coverage_status='NOT_YET_VISUALLY_INSPECTED')
 shared['PDF_inventory'].append(r)
 textfile=RUNTIME/f'pdf-{i}-text.json'
 if not textfile.exists():save(textfile,[page.extract_text() for page in reader.pages])
 print('PDF',i,p.name,r['sha256'],r['pages'])
method=[]
for folder in ['Antiquities_Niese_BookVIII_2026-10-08','Antiquities_Niese_BookX_2026-10-08','Antiquities_Niese_Batch_08_10_2026-10-08','Antiquities_Niese_Implementation_08_10_2026-10-09','Antiquities_Niese_Integration_08_10_2026-10-09']:
 for name in ['SOURCE_AUTHORITY.md','BASELINE.json','REPORT.md','FILE_MANIFEST.json','mixed_mapper.py','IMPLEMENTATION_SOURCE_AUTHORITY.md','IMPLEMENTATION_PRESERVATION.json','implement.py','CERTIFICATION.json','INTEGRATION_QA.json']:
  p=ROOT/'review'/folder/name
  if p.exists():method.append(file_record(p))
shared['accepted_method_records']=method
shared['pinned_reader_and_support']=[file_record(ROOT/p) for p in ['assets/js/renderTei.js','_includes/display-settings.html','assets/xml/antiquities/structure.xml','assets/xml/antiquities/niese/book-08.json','assets/xml/antiquities/niese/book-10.json']]
save(PACK/'BASELINE.json',shared)
for b,roman in [(12,'XII'),(13,'XIII')]:
 d=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
 baseline={'book':b,'base_commit':BASE,'branch':shared['branch'],'inputs':{},'printed_sources':[shared['PDF_inventory'][0],shared['PDF_inventory'][2]],'status':'SOURCE_FREEZE_ONLY; NO BOUNDARY OR IMPLEMENTATION CERTIFICATION'}
 books={}
 for lang in ['Greek','Latin','English']:
  rel=f'assets/xml/antiquities/{lang}/book-{b:02}.xml';p=ROOT/rel;raw=p.read_bytes();blob=git('show',BASE+':'+rel);canonical=(CANON/rel).read_bytes();book=Book(raw=raw);books[lang]=book
  frozen=d/'inputs'/f'{lang}-book-{b:02}.xml';frozen.parent.mkdir(exist_ok=True)
  if frozen.exists():assert frozen.read_bytes()==raw
  else:frozen.write_bytes(raw)
  baseline['inputs'][lang]={**file_record(p),'frozen_path':str(frozen),'git_blob_sha256':digest(blob),'git_blob_id':git('rev-parse',BASE+':'+rel).decode().strip(),'last_source_commit':git('log','-1','--format=%H',BASE,'--',rel).decode().strip(),'canonical_sha256_at_freeze':digest(canonical),'canonical_CRLF_to_LF_equals_worktree':canonical.replace(b'\r\n',b'\n')==raw,'worktree_CRLF_to_LF_equals_git_blob':raw.replace(b'\r\n',b'\n')==blob,'encoding':'UTF-8','BOM':raw.startswith(b'\xef\xbb\xbf'),'line_endings':{'CRLF':raw.count(b'\r\n'),'bare_LF':raw.count(b'\n')-raw.count(b'\r\n'),'bare_CR':raw.count(b'\r')-raw.count(b'\r\n')},'paragraphs':len(book.units),'excluded_units':book.excluded,'labels':book.labels,'narrative_codepoints':len(book.stream),'narrative_sha256':digest(book.stream.encode()),'IDs':book.tree.xpath('//@xml:id',namespaces={'xml':'http://www.w3.org/XML/1998/namespace'}),'sameAs':book.tree.xpath('//@sameAs')}
  print(b,lang,'units',len(book.units),'labels',len(book.labels),'narrative',len(book.stream))
 g=books['Greek'];labels=[]
 for x in g.labels:
  nums=re.findall(r'\d+',x['text']);labels.append(dict(number=int(nums[-1]) if nums else None,**x))
 save(d/'GREEK_CENSUS.json',{'book':b,'explicit_labels':labels,'implicit_opening_candidate':g.locate(g.first_content(0)),'expected_span_status':'Await independent visual opening/end verification; label arithmetic is not authority','last_XML_label':labels[-1] if labels else None,'final_narrative':g.stream[-1500:]})
 save(d/'BASELINE.json',baseline)
 save(d/'EDITORIAL_DECISIONS.json',{'book':b,'decisions':[],'pending':[],'review_incomplete':True})
 save(d/'BOUNDARIES.json',[])
 save(d/'QA.json',{'book':b,'freeze_and_mapper':'PASS','Greek_print_review':'NOT_STARTED','Latin_individual_review':'NOT_STARTED','implementation':'NOT_STARTED','reader_certification':'NOT_STARTED'})
 print('CENSUS',b,'explicit',len(labels),'range',labels[0]['number'],labels[-1]['number'],'duplicates',[n for n in set(x['number'] for x in labels) if sum(y['number']==n for y in labels)>1])
