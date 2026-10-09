"""Hash-pinned, byte-preserving approved VIII/X marker implementation.
Never reads old byte offsets as target offsets; maps the accepted narrative position
through the target's exact mixed text nodes after comparing Git blob and text stream.
"""
import pathlib,json,hashlib,subprocess,sys,re,collections
P=pathlib.Path(__file__).resolve().parent;W=P.parents[1];BASE='a48021588e0840330388a6055a97bd0f7c2cf827'
sys.path.insert(0,str(W/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,fixtures
def sha(x):return hashlib.sha256(x).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def git(*a):return subprocess.check_output(['git','--no-optional-locks',*a],cwd=W)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def patch(raw,ops):
 out=raw
 for op in sorted(ops,key=lambda x:(x['at'],x['delete']),reverse=True):
  at=op['at'];old=bytes.fromhex(op['before_hex']);new=bytes.fromhex(op['after_hex']);assert out[at:at+len(old)]==old
  out=out[:at]+new+out[at+len(old):]
 return out
assert git('branch','--show-current').decode().strip()=='antiquities-niese-08-10-implementation'
sources=[];results={};expectations={}
for b,roman,count,mcount,inh in [(8,'VIII',420,337,83),(10,'X',281,230,50)]:
 d=W/f'review/Antiquities_Niese_Book{roman}_2026-10-08';rows=read(d/'BOUNDARIES.json');baseline=read(d/'BASELINE.json');assert all(r['implementation_approved'] and not r['outstanding_editorial_decision'] for r in rows)
 books={};ops_by_lang={}
 for lang in ['Greek','Latin']:
  rel=f'assets/xml/antiquities/{lang}/book-{b:02}.xml';target=W/rel;snap=P/'inputs'/f'{lang}-book-{b:02}.xml'
  if not snap.exists():snap.parent.mkdir(parents=True,exist_ok=True);snap.write_bytes(target.read_bytes())
  original=snap.read_bytes();blob=git('show',BASE+':'+rel);assert sha(blob)==baseline['inputs'][lang]['worktree_before_sha256'],'Actual base blob differs from approved audit input'
  assert original.replace(b'\r\n',b'\n')==blob and original.count(b'\r')==original.count(b'\r\n'),'Unsupported newline or target source change'
  book=Book(raw=original);books[lang]=book;ops=[]
  # Audit and target narrative use parser-normalized Unicode, not raw byte equality.
  for r in rows:
   key='greek_locator' if lang=='Greek' else 'latin_locator'
   if loc:=r[key]:
    actual=book.locate(loc['book_offset']);assert actual['stable_id']==loc['stable_id'] and actual['text_node_path']==loc['text_node_path'] and actual['node_offset']==loc['node_offset'] and actual['right']==loc['right']
  if lang=='Latin':
   for r in rows:
    if r['latin_locator'] and not r['inherited_start_retained']:
     loc=book.locate(r['latin_locator']['book_offset']);tag=f'<milestone unit="niese" n="{r["niese"]}"/>'.encode();ops.append({'niese':r['niese'],'kind':'INSERT_LATIN_MILESTONE','at':loc['raw_byte'],'delete':0,'before_hex':'','after_hex':tag.hex(),'target_locator':loc})
   assert len(ops)==mcount
  else:
   for p in read(d/'ADJUDICATED_GREEK_PROPOSALS.json')['proposals']:
    n=p['niese'];loc=book.locate(p['chosen_locator']['book_offset']);tag=f'<num>[{n}]</num>'.encode()
    if n==1:ops.append({'niese':1,'kind':'ADD_EXPLICIT_OPENING_NUM','at':loc['raw_byte'],'delete':0,'before_hex':'','after_hex':tag.hex(),'target_locator':loc});continue
    if p['kind']=='RETAIN_EXISTING_WORD_LOCATOR':continue
    label=next(x for x in book.labels if x['text'].strip()==f'[{n}]');at=label['raw_start'];end=original.index(b'</num>',at)+len(b'</num>');assert original[at:end]==tag
    ops += [{'niese':n,'kind':'REMOVE_OLD_GREEK_NUM_ONLY','at':at,'delete':end-at,'before_hex':tag.hex(),'after_hex':''},{'niese':n,'kind':'INSERT_ADJUDICATED_GREEK_NUM','at':loc['raw_byte'],'delete':0,'before_hex':'','after_hex':tag.hex(),'target_locator':loc}]
  output=patch(original,ops)
  assert target.read_bytes() in [original,output],'Refuse application over unexpected bytes'
  parsed=Book(raw=output);assert parsed.stream==book.stream
  # Construct inverse edits in resulting byte coordinates, proving exact reversal.
  shift=0;inverse=[]
  for op in sorted(ops,key=lambda x:(x['at'],x['delete'])):
   old=bytes.fromhex(op['before_hex']);new=bytes.fromhex(op['after_hex']);inverse.append({'at':op['at']+shift,'delete':len(new),'before_hex':new.hex(),'after_hex':old.hex()});shift+=len(new)-len(old)
  assert patch(output,inverse)==original
  for query in ['//@xml:id','//@sameAs']:
   assert parsed.tree.xpath(query,namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})==book.tree.xpath(query,namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})
  target.write_bytes(output);ops_by_lang[lang]=ops
  sources.append({'book':b,'language':lang,'path':rel,'base_Git_blob_sha256':sha(blob),'audit_blob_sha256':baseline['inputs'][lang]['worktree_before_sha256'],'target_before_sha256':sha(original),'target_after_sha256':sha(output),'newline':'CRLF' if b'\r\n' in original else 'LF','BOM':original.startswith(b'\xef\xbb\xbf'),'authorized_operations':ops,'reverse_operations':inverse,'reverse_sha256':sha(patch(output,inverse)),'narrative_unchanged':True,'ids_sameAs_unchanged':True})
 # Registry exceptions suppress labels only as executable identities; visible labels stay.
 ids=read(d/'EXECUTABLE_IDENTITIES.json');suppressed=[{'paragraph':x['paragraph'],'label':x['visible_text'],'visibleClaim':x['visible_claim'],'actualSection':x['actual_candidate_section_at_label']} for x in ids['displaced_inherited_claims']]
 sections=[]
 for r in rows:
  n=r['niese'];note=None
  if (b,n)==(8,367):note='Only the closing words of this section survive in this Latin transcription. The main embassy narrative has no identifiable counterpart here. The cause is unknown.'
  if (b,n)==(10,102):note='The Latin begins with the first identifiable surviving counterpart: the appointment of Zedekiah. The opening details in the Greek are not explicitly expressed here.'
  if (b,n)==(10,276):note='The Latin preserves the Antiochus passage. The closing Greek notice of Roman rule and devastation has no identifiable counterpart in this transcription. The cause is unknown.'
  if (b,n)==(10,108):note='Text corresponding to this Niese section is unavailable in this Latin transcription. The eight-year Babylonian alliance, its repudiation and the turn towards Egypt have no identifiable counterpart here. The cause is unknown. Later Egyptian narrative survives.'
  sections.append({'number':n,'Latin':{'available':bool(r['latin_locator']),'correspondence':r['availability'],'note':note},'contextTarget':r['latin_paragraph_id'] if r['latin_locator'] else r['existing_label_paragraph']})
 registry={'schema':1,'book':b,'range':[1,count],'status':'EDITORIALLY_APPROVED_LOCAL_IMPLEMENTATION','suppressedLatinLabels':suppressed,'sections':sections}
 write(W/f'assets/xml/antiquities/niese/book-{b:02}.json',registry)
 q={'book':b,'expected_sections':count,'represented_Latin_intervals':count-(b==10),'inherited_starts':inh,'applied_Latin_milestones':mcount,'Greek_opening_nums_added':1,'Greek_num_relocations':sum(o['kind']=='INSERT_ADJUDICATED_GREEK_NUM' for o in ops_by_lang['Greek']),'Greek_retained_word_choices':[172,256,314,376,377] if b==8 else [],'all_source_narrative_preserved':True,'exact_byte_reversal':True,'IDs_sameAs_unchanged':True,'unavailable':[108] if b==10 else [],'editorial_decisions_pending':[],'source_records':[s for s in sources if s['book']==b]}
 write(d/'IMPLEMENTATION_PRESERVATION.json',q);results[str(b)]=q
 expectations[str(b)]={'Greek':{str(r['niese']):r['greek_section'] for r in rows},'Latin':{str(r['niese']):r.get('candidate_latin_section') if r['latin_locator'] else None for r in rows},'LatinFull':books['Latin'].stream,'GreekFull':books['Greek'].stream,'inherited':inh,'milestones':mcount}
write(P/'TARGET_BASELINE.json',{'base':BASE,'audit_review_commit':git('rev-parse','antiquities-niese-08-10').decode().strip(),'files':sources,'expected_Latin_milestones':567,'expected_represented_Latin_intervals':700,'expected_Niese_selection_total':3157,'mixed_content_fixtures':fixtures()})
write(P/'EXPECTED_INTERVALS.json',expectations)
print(json.dumps({b:{k:q[k] for k in ['applied_Latin_milestones','Greek_opening_nums_added','Greek_num_relocations','exact_byte_reversal']} for b,q in results.items()},indent=2))
