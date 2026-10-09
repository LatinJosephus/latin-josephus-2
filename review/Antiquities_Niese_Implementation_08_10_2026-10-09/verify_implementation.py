"""Read-only certification of the actual bytes, identities, partitions and build.
Run after implement.py and the browser suites. No source application or staging.
"""
import pathlib, json, hashlib, subprocess, sys, re, bisect, collections
from lxml import etree
P=pathlib.Path(__file__).resolve().parent; W=P.parents[1]
BUILD=pathlib.Path('C:/workspace/Antiquities-Niese-Implementation-08-10-2026-10-09/build/site')
sys.path.insert(0,str(W/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book, NS, fixtures
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(x):return hashlib.sha256(x).hexdigest()
def git(*args):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=W)
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def reverse(raw,ops):
 for op in sorted(ops,key=lambda o:(o['at'],o['delete']),reverse=True):
  a=op['at'];old=bytes.fromhex(op['before_hex']);new=bytes.fromhex(op['after_hex'])
  assert raw[a:a+len(old)]==old
  raw=raw[:a]+new+raw[a+len(old):]
 return raw
def norm(s):return re.sub(r'\s+',' ',s or '').strip()
target=read(P/'TARGET_BASELINE.json');base=target['base'];expected=read(P/'EXPECTED_INTERVALS.json')
assert git('branch','--show-current').decode().strip()=='antiquities-niese-08-10-implementation'
assert not git('merge-base','--is-ancestor',base,'HEAD')
report={'base':base,'audit_checkpoint':target['audit_review_commit'],'result':'PASS','books':{},'preservation':[],'mixed_content_fixtures':fixtures()}
for s in target['files']:
 raw=(W/s['path']).read_bytes();original=(P/'inputs'/f'{s["language"]}-book-{s["book"]:02}.xml').read_bytes()
 assert sha(raw)==s['target_after_sha256'] and sha(original)==s['target_before_sha256']
 assert reverse(raw,s['reverse_operations'])==original
 assert git('show',base+':'+s['path'])==original
 old,new=Book(raw=original),Book(raw=raw);assert old.stream==new.stream
 for q in ['//@xml:id','//@sameAs','//t:div1/@n','//t:div2/@n','//t:div2/@type']:
  assert old.tree.xpath(q,namespaces={**NS,'xml':'http://www.w3.org/XML/1998/namespace'})==new.tree.xpath(q,namespaces={**NS,'xml':'http://www.w3.org/XML/1998/namespace'})
 assert len(old.units)==len(new.units)
 if s['language']=='Latin':
  additions=[o for o in s['authorized_operations'] if o['kind']=='INSERT_LATIN_MILESTONE'];stripped=raw
  for op in additions:
   marker=bytes.fromhex(op['after_hex']);assert marker not in original and stripped.count(marker)==1
   stripped=stripped.replace(marker,b'',1)
  assert stripped==original
 assert raw.count(b'\r\n')==original.count(b'\r\n') and raw.count(b'\r')==original.count(b'\r')
 report['preservation'].append({k:s[k] for k in ['book','language','path','base_Git_blob_sha256','target_before_sha256','target_after_sha256','newline','BOM']}|{'exact_inverse_byte_recovery':True,'narrative_ID_sameAs_paragraph_divisions_unchanged':True})
for b,roman,total,inherited,added in [(8,'VIII',420,83,337),(10,'X',281,50,230)]:
 d=W/f'review/Antiquities_Niese_Book{roman}_2026-10-08';rows=read(d/'BOUNDARIES.json');registry=read(W/f'assets/xml/antiquities/niese/book-{b:02}.json')
 assert len(rows)==total and all(r['implementation_approved'] and not r['outstanding_editorial_decision'] and not r['Greek_start_awaiting_print_verification'] for r in rows)
 assert sum(r['inherited_start_retained'] for r in rows)==inherited
 assert [r['niese'] for r in rows if not r['latin_locator']]==([108] if b==10 else [])
 assert [s['number'] for s in registry['sections']]==list(range(1,total+1))
 partitions={};identity_records={}
 for language in ['Greek','Latin']:
  book=Book(path=W/f'assets/xml/antiquities/{language}/book-{b:02}.xml');starts=[]
  for label in book.labels:
   match=re.search(r'(\d+)\]$',label['text'].strip())
   if not match:continue
   n=int(match[1]);assert 1<=n<=total
   if language=='Latin' and any(rule['paragraph']==label['id'] and rule['label']==label['text'].strip() for rule in registry['suppressedLatinLabels']):continue
   starts.append((label['raw_start'],label['book_offset'],n,'inherited' if language=='Latin' else 'Greek-num'))
  if language=='Latin':
   positions=[a for node in book.nodes for a in node['raw_positions']]
   assert positions==sorted(positions)
   for m in re.finditer(rb'<milestone unit="niese" n="(\d+)"/>',book.raw):
    starts.append((m.start(),bisect.bisect_left(positions,m.start()),int(m[1]),'milestone'))
   assert len([x for x in starts if x[3]=='milestone'])==added
   assert len([x for x in starts if x[3]=='inherited'])==inherited
  starts.sort();numbers=[x[2] for x in starts];wanted=[n for n in range(1,total+1) if not(language=='Latin' and b==10 and n==108)]
  assert numbers==wanted and len(set(numbers))==len(numbers)
  assert starts[0][1]==0
  extents=[];parts=[]
  for i,(_,a,n,kind) in enumerate(starts):
   z=starts[i+1][1] if i+1<len(starts) else len(book.stream);text=book.stream[a:z]
   assert z>a and norm(text)==norm(expected[str(b)][language][str(n)])
   assert not any(p==a for p in [e['start'] for e in extents])
   extents.append({'niese':n,'start':a,'end':z,'kind':kind,'narrative_sha256':sha(text.encode())});parts.append(text)
  assert ''.join(parts)==book.stream
  partitions[language]={'intervals':len(parts),'complete_byte_independent_Unicode_narrative_partition':True,'characters':len(book.stream),'sha256':sha(book.stream.encode()),'adjacent_no_overlap_no_loss':True}
  identity_records[language]=extents
 write(d/'IMPLEMENTED_EXTENTS.json',{'book':b,'coordinate_system':'Unicode narrative code points; num/note/app/rdg excluded; all narrative whitespace included','languages':identity_records,'unavailable_Latin':[108] if b==10 else []})
 q={'book':b,'result':'PASS','expected_sections':total,'retained_inherited_starts':inherited,'new_Latin_milestones':added,'represented_Latin_intervals':total-(b==10),'unavailable':[108] if b==10 else [],'confidence_counts':dict(collections.Counter(r['classification'] for r in rows)),'remaining_routine_review':0,'remaining_editorial_decisions':0,'partitions':partitions,'inherited_label_exceptions':registry['suppressedLatinLabels'],'source_preservation':'BYTE_EXACT','all_print_and_editorial_qualifications_retained':True}
 report['books'][str(b)]=q;write(d/'IMPLEMENTATION_QA.json',q)
# Every previously tracked production file outside the six authorized edits is
# unchanged as a Git blob, accepting checkout CRLF without normalizing any file.
allowed={'assets/js/renderTei.js','_includes/display-settings.html'}|{s['path'] for s in target['files']}
unchanged=[]
for rel in git('ls-tree','-r','--name-only',base).decode().splitlines():
 if rel in allowed:continue
 blob=git('show',base+':'+rel);raw=(W/rel).read_bytes()
 assert raw==blob or raw.replace(b'\r\n',b'\n')==blob,rel
 unchanged.append({'path':rel,'Git_blob_sha256':sha(blob),'working_bytes_sha256':sha(raw)})
report['unchanged_base_files']=len(unchanged);write(P/'UNCHANGED_BASE_FILES.json',unchanged)
# Confirm that all eight changed/new production files were actually built.
built=[]
for rel in sorted(allowed-{'_includes/display-settings.html'}|{'assets/xml/antiquities/niese/book-08.json','assets/xml/antiquities/niese/book-10.json'}):
 raw=(W/rel).read_bytes();assert (BUILD/rel).read_bytes()==raw,rel
 built.append({'path':rel,'sha256':sha(raw)})
assert 'id="niese-previous"' in (BUILD/'antiquities/index.html').read_text(encoding='utf8')
report['built_production_files']=built
for name in ['NEW_BOOK_BROWSER_QA.json','PROTECTED_BROWSER_QA.json','UI_SUPPLEMENT_QA.json']:
 q=read(P/name);assert q['result']=='PASS' and not q['errors'] and not q['consoleErrors'] and not q['networkFailures'],name
report['actual_browser_QA']='PASS'
q=read(P/'BROWSER_QA.json');assert q['traditional']['executable']==5034 and q['traditional']['unavailable']==33 and q['traditional']['menusChapters']==257 and q['traditional']['menusSubchapters']==1432 and q['traditional']['physical']==1441 and not q['errors']
assert sum(x['selections'] for x in q['niese'].values())==2456
protected=read(P/'PROTECTED_BROWSER_QA.json')['antiquities']
assert sum(x['identities'] for x in protected['bamberg'])==198 and sum(x['identities'] for x in protected['alignment'])==1441
source=read(P/'PROTECTED_SOURCE_GATE_QA.json');assert source['result']=='PASS'
for source_name in ['whiston','lodge1602']:assert sum(x['niese'] for x in source['checks'] if x['source']==source_name)==4001
report['coverage']={'existing_Antiquities_Niese_selections':2456,'new_selections':701,'total':3157,'new_Latin_intervals':700,'Latin_absence_states':1,'traditional_chapters':257,'traditional_subchapters':1432,'traditional_executable_three_language_ranges':5034,'traditional_unavailable_states':33,'Bamberg_identities':198,'Bamberg_three_language_displays':594,'Alignment_units':1441,'Bellum_Niese_per_English_source':4001}
# Printed PDFs and prior evidence remain read-only. Recheck their frozen hashes;
# this is preservation verification, not a repeated visual collation.
audit=W/'review/Antiquities_Niese_Batch_08_10_2026-10-08'
printed=read(audit/'PRINT_EVIDENCE_MANIFEST.json');source_checks=[]
for item in printed['sources']+printed['images']:
 p=pathlib.Path(item['path']);p=p if p.is_absolute() else W/p
 actual=sha(p.read_bytes());assert actual==item['sha256'],str(p)
 source_checks.append({'path':item['path'],'sha256':actual,'unchanged':True})
frozen=read(audit/'FROZEN_SOURCE_VERIFICATION.json');frozen_count=0
for packet in frozen:
 for item in packet['files']:
  p=pathlib.Path(packet['root'])/item['path'];assert sha(p.read_bytes())==item['expected'];frozen_count+=1
write(P/'PRINT_INPUTS_UNCHANGED.json',{'sources_and_images':source_checks,'frozen_research_files_rechecked':frozen_count,'result':'PASS'})
report['printed_PDFs_and_frozen_evidence_unchanged']=True
write(P/'CERTIFICATION.json',report)
print(json.dumps({'result':report['result'],'unchanged_base_files':len(unchanged),'coverage':report['coverage']},indent=2))
