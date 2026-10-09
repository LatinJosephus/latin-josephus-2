"""Prepare evidence/coordinate registers. No inferred Latin correspondence is approved."""
from pathlib import Path
import sys,json,re,shutil,argparse
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];PACK=Path(__file__).resolve().parent
RUNTIME=Path('C:/workspace/Antiquities-Niese-12-13-runtime-20261009')
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookX_2026-10-08'))
from mixed_mapper_batch import Book,digest,fixtures
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def packet(b):return ROOT/f'review/Antiquities_Niese_Book{"XII" if b==12 else "XIII"}_2026-10-09'
def books(b):return {lang:Book(packet(b)/'inputs'/f'{lang}-book-{b:02}.xml') for lang in ['Greek','Latin','English']}
def prepare():
 frozen=Path('C:/Users/Pollard_R/Mon disque/Latin Josephus Project/LatinJosephus-Recovery/latinjosephus-next/review/Antiquities_Loeb_Niese_Verification_2026-10-05')
 record=frozen/'batch-02/Loeb_Niese_Batch02.json';source=json.loads(record.read_text(encoding='utf8'))
 manifest=frozen/'Antiquities_Loeb_Niese_Verification_SHA256SUMS.txt'
 checks=[]
 for line in manifest.read_text(encoding='utf-8-sig').splitlines():
  if not line.strip():continue
  match=re.match(r'([a-fA-F0-9]{64})\s+\*?(.+)',line)
  if not match:continue
  h,rel=match.groups();p=frozen/rel
  checks.append({'path':str(p),'expected':h,'actual':digest(p.read_bytes()) if p.exists() else None})
 assert all(x['actual']==x['expected'] for x in checks)
 save(PACK/'FROZEN_REFERENCE_VERIFICATION.json',{'root':str(frozen),'manifest':str(manifest),'manifest_sha256':digest(manifest.read_bytes()),'checks':checks,'record':str(record),'record_sha256':digest(record.read_bytes()),'role':'Traditional physical starts/print windows only; no internal Latin correspondence authority'})
 for b in [12,13]:
  d=packet(b);bs=books(b);g,l=bs['Greek'],bs['Latin'];census=json.loads((d/'GREEK_CENSUS.json').read_text(encoding='utf8'));labels=census['explicit_labels'];starts={x['number']:g.first_content(x['book_offset']) for x in labels};starts[1]=g.first_content(0)
  count=max(starts);assert sorted(starts)==list(range(1,count+1))
  rows=[]
  for n in range(1,count+1):
   at=starts[n];loc=g.locate(at);unit=g.units[loc['paragraph']-1];target=unit['element'].get('sameAs','').lstrip('#');lu=next((u for u in l.units if u['id']==target),None)
   rows.append({'book':b,'niese':n,'Greek':{'locator':loc,'section':g.stream[at:starts.get(n+1,len(g.stream))],'print_status':'NOT_REVIEWED','word_boundary_status':'XML_CANDIDATE_ONLY'},'Latin':{'alignment_window_paragraph':target,'alignment_window_unit_sha256':lu['raw_hash'] if lu else None,'locator':None,'review_status':'NOT_REVIEWED','physical_placement_status':'UNASSIGNED','correspondence_limits':'NOT_REVIEWED'},'editorial_status':'NOT_REVIEWED','implementation_approved':False})
  if not (d/'CANDIDATE_REGISTER.json').exists():save(d/'CANDIDATE_REGISTER.json',rows)
  save(d/'FROZEN_PRINT_STARTS.json',[x for x in source['audited_boundaries'] if int(x['antiquities_book'])==b])
  save(d/'PRINTED_COVERAGE_REFERENCE.json',[x for x in source['exact_book_coverage'] if x['book']==b])
  baseline=json.loads((d/'BASELINE.json').read_text(encoding='utf8'));baseline['niese']={'first':1,'last':count,'expected_count':count,'Greek_explicit_nums':len(labels),'opening_implicit':True,'count_authority':'Independently inspected Niese III opening/end images and complete Greek census','printed_span':([73,148] if b==12 else [151,233]),'PDF_span':([145,220] if b==12 else [223,305])};save(d/'BASELINE.json',baseline)
  nodes=[{'paragraph':u['id'],'raw_unit_sha256':u['raw_hash'],**{k:v for k,v in node.items() if k!='unit'}} for u in l.units for node in u['nodes']];save(d/'LATIN_TEXT_NODE_LEDGER.json',nodes)
  (d/'evidence').mkdir(exist_ok=True)
  for n in ([145,220] if b==12 else [223,305]):shutil.copyfile(RUNTIME/f'niese-{n}.png',d/'evidence'/f'niese-{n:03}.png')
 print('Both complete Greek coordinate registers prepared; no Latin placement or approval inferred.')
def show(b,a,z):
 rows=json.loads((packet(b)/'CANDIDATE_REGISTER.json').read_text(encoding='utf8'));bs=books(b);printed=set()
 for r in rows[a-1:z]:
  print(f'\nGREEK {b}.{r["niese"]}: {r["Greek"]["section"].strip()}')
  target=r['Latin']['alignment_window_paragraph']
  if target not in printed:
   printed.add(target);u=next((u for u in bs['Latin'].units if u['id']==target),None)
   print(f'LATIN WINDOW {target}: {u["text"] if u else "MISSING TARGET"}')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','show']);ap.add_argument('--book',type=int,choices=[12,13]);ap.add_argument('--first',type=int,default=1);ap.add_argument('--last',type=int,default=10);args=ap.parse_args()
 if args.mode=='prepare':prepare()
 else:show(args.book,args.first,args.last)
