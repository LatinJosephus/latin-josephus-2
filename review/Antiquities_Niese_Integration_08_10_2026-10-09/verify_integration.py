"""Read-only committed-manifest, audit-provenance and source-count verification.
Outputs separate integration evidence; never alters prior certification or sources.
"""
import pathlib,subprocess,hashlib,json,threading,sys,re
from lxml import etree
TASK=pathlib.Path(__file__).resolve().parent
C=pathlib.Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
I=pathlib.Path('C:/workspace/LatinJosephus-antiquities-niese-08-10-implementation')
BASE='a48021588e0840330388a6055a97bd0f7c2cf827'
INCOMING='2b07ac23143d7fa551753aee1d7051da5a77b99a'
AUDIT='fb8a65e2a6c7d6e5426f3b4751d30e67528b1a28'
mode=sys.argv[1] if len(sys.argv)>1 else 'preflight'
def git(*a,root=C):return subprocess.check_output(['git','--no-optional-locks',*a],cwd=root)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def blobs(specs):
 p=subprocess.Popen(['git','--no-optional-locks','cat-file','--batch'],cwd=C,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 def send():p.stdin.write(('\n'.join(specs)+'\n').encode());p.stdin.close()
 sender=threading.Thread(target=send);sender.start()
 for spec in specs:
  header=p.stdout.readline().decode().split();assert len(header)==3 and header[1]=='blob',(spec,header)
  size=int(header[2]);raw=p.stdout.read(size);assert len(raw)==size and p.stdout.read(1)==b'\n'
  yield spec,raw
 sender.join();assert p.wait()==0
assert git('rev-parse','antiquities-niese-08-10-implementation').decode().strip()==INCOMING
assert git('rev-parse','antiquities-niese-08-10').decode().strip()==AUDIT
assert git('branch','--show-current').decode().strip()=='v2-development'
assert not git('status','--porcelain=v1')
assert not git('status','--porcelain=v1',root=I)
head=git('rev-parse','HEAD').decode().strip();remote=git('rev-parse','origin/v2-development').decode().strip()
if mode=='preflight':
 assert head==BASE and remote==BASE
else:assert not git('merge-base','--is-ancestor',INCOMING,'HEAD')
assert not git('merge-base','--is-ancestor',BASE,INCOMING)
packet=I/'review/Antiquities_Niese_Implementation_08_10_2026-10-09'
manifest=read(packet/'FILE_MANIFEST.json');scope=read(packet/'COMMIT_SCOPE.json');proof=read(packet/'AUDIT_RECORDS_PRESERVED.json');certificate=read(packet/'CERTIFICATION.json')
assert scope['base']==BASE and scope['audit_checkpoint']==AUDIT and proof['review_checkpoint']==AUDIT
incoming=set(git('diff','--name-only',BASE,INCOMING).decode().splitlines())
scoped={p for rows in scope['groups'].values() for p in rows};assert incoming==scoped and len(incoming)==477
production=sorted(p for p in incoming if not p.startswith('review/'));assert len(production)==8
expected={r['path']:r for r in manifest['files']};assert len(expected)==475
assert incoming-set(expected)=={'review/Antiquities_Niese_Implementation_08_10_2026-10-09/FILE_MANIFEST.json','review/Antiquities_Niese_Implementation_08_10_2026-10-09/COMMIT_SCOPE.json'}
committed=[]
for spec,raw in blobs([INCOMING+':'+p for p in sorted(incoming)]):
 rel=spec.split(':',1)[1];h=sha(raw)
 if rel in expected:assert h==expected[rel]['sha256'] and len(raw)==expected[rel]['bytes'],rel
 assert raw==(I/rel).read_bytes(),rel
 committed.append({'path':rel,'Git_blob_sha256':h,'bytes':len(raw)})
audit_hashes={r['path']:r['audit_Git_blob_sha256'] for r in proof['files']}
assert len(audit_hashes)==381
for spec,raw in blobs([AUDIT+':'+p for p in sorted(audit_hashes)]):
 rel=spec.split(':',1)[1];assert sha(raw)==audit_hashes[rel]
 assert next(r['Git_blob_sha256'] for r in committed if r['path']==rel)==audit_hashes[rel]
sequence=git('rev-list','--reverse',BASE+'..'+INCOMING).decode().splitlines()
assert len(sequence)==4 and AUDIT not in sequence
ns={'t':'http://www.tei-c.org/ns/1.0'};books={}
for b,total,retained,new in [(8,420,83,337),(10,281,50,230)]:
 g=etree.fromstring(git('show',INCOMING+f':assets/xml/antiquities/Greek/book-{b:02}.xml'))
 latin=etree.fromstring(git('show',INCOMING+f':assets/xml/antiquities/Latin/book-{b:02}.xml'))
 nums=[int(re.search(r'\[(\d+)\]',x.text).group(1)) for x in g.xpath('//t:body//t:p/t:num',namespaces=ns)]
 assert nums==list(range(1,total+1))
 milestones=latin.xpath('//t:body//t:milestone[@unit="niese"]',namespaces=ns)
 assert len(milestones)==new and len({m.get('n') for m in milestones})==new
 assert not latin.xpath('//t:note//t:milestone[@unit="niese"]|//t:app//t:milestone[@unit="niese"]',namespaces=ns)
 registry=json.loads(git('show',INCOMING+f':assets/xml/antiquities/niese/book-{b:02}.json'))
 assert len(registry['sections'])==total and registry['range']==[1,total]
 absent=[r['number'] for r in registry['sections'] if not r['Latin']['available']];assert absent==([108] if b==10 else [])
 assert len(registry['suppressedLatinLabels'])==2
 q=certificate['books'][str(b)];assert q['retained_inherited_starts']==retained and q['new_Latin_milestones']==new and q['represented_Latin_intervals']==total-len(absent)
 books[str(b)]={'sections':total,'retained_inherited_starts':retained,'Latin_milestones':new,'Latin_intervals':total-len(absent),'unavailable':absent,'inherited_exceptions':registry['suppressedLatinLabels']}
canonical=[]
if mode!='preflight':
 for spec,raw in blobs(['HEAD:'+p for p in sorted(incoming)]):
  rel=spec.split(':',1)[1];assert sha(raw)==next(r['Git_blob_sha256'] for r in committed if r['path']==rel),rel
  working=(C/rel).read_bytes();assert working==raw or working.replace(b'\r\n',b'\n')==raw,rel
  canonical.append({'path':rel,'committed_sha256':sha(raw),'checkout_sha256':sha(working),'checkout_CRLF_equivalent':working!=raw})
report={'mode':mode,'result':'PASS','canonical_HEAD':head,'refreshed_origin':remote,'implementation_HEAD':INCOMING,'recorded_base':BASE,'audit_checkpoint':AUDIT,'incoming_sequence':sequence,'incoming_files':committed,'incoming_count':len(incoming),'production_scope':production,'review_files':469,'approved_audit_files_byte_exact':381,'books':books,'total_Antiquities_selections':certificate['coverage']['total'],'canonical_checkouts':canonical,'certification_reused':'All certified production inputs and committed outputs unchanged'}
(TASK/('PREFLIGHT.json' if mode=='preflight' else 'CANONICAL_HASH_QA.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:report[k] for k in ['mode','result','canonical_HEAD','refreshed_origin','incoming_count','production_scope','approved_audit_files_byte_exact','total_Antiquities_selections']},indent=2))
