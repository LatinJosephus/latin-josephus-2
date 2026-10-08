from pathlib import Path
from lxml import etree as E, html
from collections import Counter
import csv, io, json, hashlib, re, subprocess, zipfile
ROOT=Path(r'C:\workspace\LatinJosephus-source-toc-navigation')
CANON=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
PROJECT=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project')
RECOVERY=PROJECT/'LatinJosephus-Recovery/latinjosephus-next'
OUT=ROOT/'review/Source_TOC_Navigation_2026-10-07'
BASE='087c0bf651037d83c5156495836510d250bdcf09'
NS={'t':'http://www.tei-c.org/ns/1.0','w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
PRESENT='PRESENT_IN_PRODUCTION'
OMITTED='PRESENT_IN_AUTHORITY_OMITTED_FROM_PRODUCTION'
NONE='SOURCE_HAS_NO_TOC'
UNKNOWN='NOT_YET_VERIFIED'
def sha(data):return hashlib.sha256(data).hexdigest()
def git(root,*args):return subprocess.run(['git','-C',str(root),*args],capture_output=True,check=True).stdout.decode('utf-8').strip()
def write(name,s):
 p=(OUT/name).resolve();assert p.parent==OUT.resolve();p.write_bytes(s.encode('utf-8'))
def dump(name,d):write(name,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def norm(s):return ' '.join(s.split())
def text(e):return ''.join(e.itertext())
def inventory():return {p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts}
def node_record(t,e):return {'xpath':t.getpath(e),'attributes':dict(e.attrib),'text':text(e),'text_sha256':sha(text(e).encode()),'paragraphs':[text(p) for p in e.xpath('./t:p',namespaces=NS)]}
initial={'canonical':{'branch':git(CANON,'branch','--show-current'),'head':git(CANON,'rev-parse','HEAD'),'origin':git(CANON,'rev-parse','origin/v2-development'),'status':git(CANON,'status','--short')},'worktree':{'branch':git(ROOT,'branch','--show-current'),'head':git(ROOT,'rev-parse','HEAD'),'status_outside_review':git(ROOT,'status','--short','--','.',':(exclude)review/Source_TOC_Navigation_2026-10-07')}}
assert initial['canonical']=={'branch':'v2-development','head':BASE,'origin':BASE,'status':''}
assert initial['worktree']=={'branch':'source-toc-navigation','head':BASE,'status_outside_review':''}
before=inventory();authorities={};external_before={}
def authority(key,p,entry=None,expected=None,description=''):
 p=Path(p);d=p.read_bytes();digest=sha(d);external_before[str(p)]=digest
 if expected:assert digest==expected,(key,digest,expected)
 a={'path':str(p),'sha256':digest,'bytes':len(d),'description':description}
 if entry:
  with zipfile.ZipFile(p) as z:d=z.read(entry)
  a.update(entry=entry,entry_sha256=sha(d),entry_bytes=len(d))
 authorities[key]=a;return d
lodge=Path(r'C:\Users\Pollard_R\Downloads\Lodge1602_Bellum_FINAL_ADJUDICATED_20261003.zip')
d=authority('lodge-tcp',lodge,'work/inputs/A04680.xml','18a34bdbbfd199ab482b73ad442c19cd0fb5e70794e9d77aa0a74a1c7ad26fc0','Accepted frozen master, complete TCP source')
assert sha(d)=='3ca2646644d8c91cf35e8575a6ffbdeb5ecbd378c502f53fd9445d7da7431de6'
ltree=E.fromstring(d).getroottree();lodge_lists={};lodge_checks=[]
for printed in range(1,8):
 e=ltree.xpath(f'/t:TEI/t:text/t:group/t:text[2]/t:body/t:div[{printed}]/t:list',namespaces=NS)[0]
 rec=node_record(ltree,e);rec.update(printed_book=printed,source_xpath=f'/TEI[1]/text[1]/group[1]/text[2]/body[1]/div[{printed}]/list[1]',item_count=len(e.xpath('./t:item',namespaces=NS)),entries=[text(i) for i in e.xpath('./t:item',namespaces=NS)])
 found=[]
 for canonical in range(1,8):
  p=ROOT/f'assets/xml/bellum/English/Lodge1602/book-{canonical:02}.xml';tr=E.parse(str(p))
  for n in tr.xpath('//t:seg[@type="tcp-list"]',namespaces=NS):
   if n.get('corresp')==rec['source_xpath']:
    assert text(n)==rec['text'];found.append({'book':canonical,'file':p.relative_to(ROOT).as_posix(),'xpath':tr.getpath(n),'text_sha256':sha(text(n).encode())})
 assert len(found)==1
 rec['production_locations']=found;lodge_lists[printed]=rec
 lodge_checks.append({'printed_book':printed,'production_book':found[0]['book'],'items':rec['item_count'],'decoded_text_identical':True})
assert [r['items'] for r in lodge_checks]==[21,28,19,7,14,16,31]
volume_rec=node_record(ltree,ltree.xpath('/t:TEI/t:text/t:group/t:text[1]/t:front/t:div[@type="table_of_contents"]',namespaces=NS)[0])
bjzip=Path(r'C:\Users\Pollard_R\Downloads\Bellum_Whiston_I-VII_FINAL_REBASE_RC1.zip')
d=authority('bellum-whiston-control',bjzip,'evidence/perseus/tlg0526.tlg004.perseus-eng2.xml',description='Pinned external Perseus control; no printed contents provenance')
assert sha(d)=='bb948d1a1dff1cb4459fbaa5aeb99ef17d957ff111104fb862c0b6498a0fe780'
tr=E.fromstring(d);assert len(tr.xpath('//*[@subtype="book"]'))==7 and not tr.xpath('//t:front|//t:list',namespaces=NS)
authority('bellum-whiston-provenance',bjzip,'Bellum_Whiston_FROZEN_PROVENANCE.md',description='Supplied production XML is textual base; external controls are not preparation-master evidence')
p=PROJECT/'Antiquities Edition/Old Site/sites.google.com/files/2848/2848-h/2848-h.htm'
d=authority('antiquities-whiston-digital-candidate',p,description='Saved Gutenberg 2848 HTML; printed-edition origin of CONTENTS not established')
t=html.fromstring(d).getroottree();x=t.xpath('//h2[normalize-space()="CONTENTS"]')[0].getnext();pgbooks=[]
while x is not None and x.tag!='h2':
 s=norm(text(x))
 if x.tag=='h3' and s.startswith('BOOK '):pgbooks.append({'book':len(pgbooks)+1,'heading':text(x),'entries':[]})
 if x.tag=='p' and x.get('class')=='toc' and s.startswith('CHAPTER'):
  a=x.xpath('.//a')[0];ts=t.xpath('//*[@id=$n or @name=$n]',n=a.get('href').lstrip('#'));title=ts[0].getparent().xpath('following-sibling::h3[1]')[0] if ts else None
  pgbooks[-1]['entries'].append({'text':text(a),'target':a.get('href'),'linked_heading_text':text(title) if title is not None else None,'linked_heading_xpath':t.getpath(title) if title is not None else None,'matches_linked_heading_after_whitespace_collapse':title is not None and norm(text(title))==s})
 x=x.getnext()
assert len(pgbooks)==20
ca=RECOVERY/'_source/contra-apionem'
ca_paths={'Greek':ca/'Niese-1889-Greek/freeze/Contra_Apionem_Greek_Niese_1889_Perseus_grc2_SOURCE_FROZEN.xml','Latin':ca/'Boysen-1898-Latin/freeze/Contra_Apionem_Latin_Boysen_1898_SOURCE_FROZEN.xml','English':ca/'whiston-v0.1/Perseus_Whiston_Contra_Apionem_SOURCE_FROZEN.xml'}
for lang,p in ca_paths.items():
 d=authority('contra-'+lang.lower(),p,description='Complete frozen TEI has no front/list; underlying print absence not inferred');tr=E.fromstring(d)
 assert len(tr.xpath('//*[@subtype="book"]'))==2 and not tr.xpath('//*[local-name()="front" or local-name()="list"]')
authority('contra-whiston-ingest-policy',ca/'whiston-v0.1/Whiston_Ingest_QA_v0.1.md',description='Editor-note omission recorded; no TOC omission policy')
deh=PROJECT/'DEH Translation - ChatGPT Project'
authority('deh-ussani-digital',deh/'DLT000241.xml',expected='c21f51499e21550f0c3284fe6f6f756733c28086b469383d1b0eeecf42c70510',description='Named digilibLT upstream')
authority('deh-latin-freeze',deh/'DEH_Latin_Corpus_Final_Canonical_Package.zip',description='Frozen five-book digital corpus; no print-front-matter absence conclusion')
with zipfile.ZipFile(deh/'DEH_Latin_Corpus_Final_Canonical_Package.zip') as z:
 for n in z.namelist():
  if n.endswith('.xml'):assert not E.fromstring(z.read(n)).xpath('//*[local-name()="list" or local-name()="front"]')
d=authority('deh-english-consultation-export',deh/'DEH_Latin_English_Parallel_v1.0_2026-09-22.docx',description='Complete consultation export declares frozen TEI authoritative')
with zipfile.ZipFile(io.BytesIO(d)) as z:
 tr=E.fromstring(z.read('word/document.xml'));assert not any(re.search(r'(?i)table of contents|\bcontents\b|capitula',''.join(p.xpath('.//w:t/text()',namespaces=NS))) for p in tr.xpath('//w:p',namespaces=NS))
pretei=PROJECT/'Latin Josephus Project - For PSS/Edition Files - Part 1 (pre-TEI) - Ant. 1-8';word_records={}
for p in sorted(pretei.glob('*.docx')):
 b=int(re.search(r'Book (\d+)',p.name).group(1));d=authority(f'ant-latin-word-{b}',p,description='Earlier manuscript transcription; nested Word tables read without editing')
 with zipfile.ZipFile(io.BytesIO(d)) as z:
  tr=E.fromstring(z.read('word/document.xml'));tabs=[]
  for tab in tr.xpath('//w:tbl',namespaces=NS):
   rs=[r.xpath('./w:tc',namespaces=NS) for r in tab.xpath('./w:tr',namespaces=NS)]
   if sum(len(c)==3 for c in rs)>10:tabs.append(rs)
  word_records[b]={'first_rows':[[norm(''.join(c.xpath('.//w:t/text()',namespaces=NS)))[:350] for c in row] for rs in tabs for row in rs[:5]]}
  if b==5:
   assert len(tabs)==1;word_records[b]['capitula_paragraphs']=[''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in tabs[0][2][0].xpath('.//w:p',namespaces=NS)]
assert len(word_records[5]['capitula_paragraphs'])==14
rom=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII'];oldsite={}
for b,r in enumerate(rom,1):
 p=PROJECT/f'Antiquities Edition/Liber {r}/Book {b} - The Latin Josephus.html'
 if not p.exists():continue
 d=authority(f'ant-polyglot-html-{b}',p,description='Archived project source-labelled polyglot page');tr=html.fromstring(d);tabs=[]
 for tab in tr.xpath('//table'):
  rs=[r.xpath('./td|./th') for r in tab.xpath('./tr|./tbody/tr')]
  if sum(len(c)==3 for c in rs)>10:tabs.append(rs)
 oldsite[b]={'first_rows':[[norm(text(c))[:350] for c in row] for rs in tabs for row in rs[:5]]}
 if b==5:assert len(tabs)==1;oldsite[b]['capitula_cell_text']=text(tabs[0][2][0])
assert 'iehsus' in oldsite[5]['capitula_cell_text'] and 'ihesus' in word_records[5]['capitula_paragraphs'][0]
for p in sorted((PROJECT/'Latin Josephus Project - For PSS/Edition Files - Part 2 (TEI) - Ant. 9-20').glob('Edition - Bamberg*.txt')):
 b=int(re.search(r'Book (\d+)',p.name).group(1));d=authority(f'ant-latin-tpen-{b}',p,description='Local upstream T-PEN TEI-like export');authorities[f'ant-latin-tpen-{b}']['opening_excerpt']=d.decode('utf-8',errors='replace')[:650]
cw=PROJECT/'De Bello Judaico'
for k,n in [('ocr','Cardwell (1837) - De Bello Judaico - Merged copy.txt'),('corrected','Cardwell (1837) - De Bello Judaico - Merged and Corrected - For Comparison.txt')]:
 d=authority('cardwell-'+k,cw/n,description='Merged running-text transcription; full print-front-matter authority unestablished');authorities['cardwell-'+k]['explicit_contents_heading_hits']=len(re.findall(r'(?im)^\s*(index|argumenta|contents|capitula|conspectus)\b',d.decode('utf-8',errors='replace')))
for b in range(1,8):
 p=cw/f'Cardwell (1837) - De Bello Judaico - Book {b}.htm'
 if p.exists():authority(f'cardwell-html-{b}',p,description='Earlier per-book running-text transcription')
d=authority('latin-xiv-existing-hold',RECOVERY/'review/Antiquities_source_review_reconciliation_2026-09-28/SOURCE_REVIEW_PACKET.md',description='Existing SR-061 whole-paragraph source/structure hold')
assert b'Whole-paragraph source/structure hold' in d
history=[]
for c in ('a89405e','ac3e20f','d08d8b5',BASE):
 for w,l,b in [('antiquities','Latin',5),('antiquities','English',1),('antiquities','English',5),('bellum','English',1)]:
  path=f'assets/xml/{w}/{l}/book-{b:02}.xml';proc=subprocess.run(['git','-C',str(ROOT),'show',c+':'+path],capture_output=True)
  if proc.returncode:continue
  tr=E.fromstring(proc.stdout);ds=tr.xpath('//*[local-name()="div2" and @n="0"]');history.append({'commit':git(ROOT,'rev-parse',c),'path':path,'git_blob_bytes_sha256':sha(proc.stdout),'chapter_zero_paragraphs':[len(d.xpath('./*[local-name()="p"]')) for d in ds],'chapter_zero_incipit':[norm(text(d))[:180] for d in ds]})
rows=[];trees={};observations={}
specs=[('Antiquities','antiquities',20,[('Greek','Niese','Greek'),('Latin','Bamberg 78','Latin'),('English','Whiston','English')]),('Bellum Judaicum','bellum',7,[('Greek','Niese','Greek'),('Latin','Cardwell (1837)','Latin'),('English','Whiston','English'),('English','Lodge (1602)','English/Lodge1602')]),('Contra Apionem','contra-apionem',2,[('Greek','Niese (1889)','Greek'),('Latin','Boysen (1898)','Latin'),('English','Whiston','English')]),('DEH','deh',5,[('Latin','Ussani (1932)','Latin'),('English','Pollard v1.0','English')])]
for work,slug,books,sources in specs:
 for lang,source,directory in sources:
  for b in range(1,books+1):
   path=f'assets/xml/{slug}/{directory}/book-{b:02}.xml';p=ROOT/path;tr=E.parse(str(p));trees[path]=tr;d0=tr.xpath('//*[local-name()="div2" and @n="0"]');block=d0[0] if d0 else None
   observed=False;status=UNKNOWN;auth=[];locs=[];note='No source contents list found in current XML. Source-level absence has not been established.';action='Verify complete authoritative source paratext; do not synthesize a list.';confidence='UNCERTAIN_SOURCE_AVAILABILITY'
   if slug=='antiquities' and lang=='Greek' and (b==5 or b>=11):
    status=PRESENT;observed=True;locs=[node_record(tr,block)];note='Explicit contents formula followed by summary paragraphs in chapter-zero wrapper; preserve source wording and order.';auth=[path];action='Display existing contents as paratext after the global restoration gate clears.';confidence='HIGH_CURRENT_ENCODING'
   elif slug=='antiquities' and lang=='Latin' and b>=13:
    status=PRESENT;observed=True;locs=[node_record(tr,block)];auth=[path,f'ant-latin-tpen-{b}'];action='Display preserved capitula; keep transcription holds and source grouping.';confidence='HIGH_CURRENT_ENCODING';note='Explicit INCIPIUNT CAPITULA list in production. Paragraph grouping is not normalized into navigation entries.'
    if b==14:note+=' SR-061 holds paragraph 4, which mixes contents and Herodian narrative; do not adjudicate, move, delete or subdivide it.';auth+=['latin-xiv-existing-hold']
   elif slug=='antiquities' and lang=='Latin' and b==5:
    status=OMITTED;auth=['ant-latin-word-5','ant-polyglot-html-5'];note='Fourteen manuscript capitula paragraphs survive upstream; current chapter zero retains only the introductory formula. Word/HTML readings differ: ihesus / iehsus, chananeos / chananaeos, tribubus / tribubs.';action='HOLD restoration pending identification/adjudication of the governing transcription; do not choose variants silently.';confidence='HIGH_EXISTENCE_UNSETTLED_READING'
   elif slug=='antiquities' and lang=='English':
    auth=['antiquities-whiston-digital-candidate'];note='Gutenberg candidate has linked CONTENTS; print provenance and original preparation policy are unestablished. Production absence is not source absence.'
    if b==5:observed=True;locs=[node_record(tr,block)];note='Production has eleven CHAPTER-summary paragraphs before narrative. Source-print status remains unverified; archived project table and Gutenberg candidate also contain this list.';auth+=['ant-polyglot-html-5','ant-latin-word-5']
    action='HOLD: identify actual Whiston source edition / preparation master and establish whether the list is source paratext or added digital navigation.'
   elif slug=='bellum' and source=='Lodge (1602)':
    printed={1:[1],2:[2],3:[3],4:[4,5],5:[6],6:[7],7:[7]}[b];status=PRESENT;observed=b!=7;auth=['lodge-tcp'];locs=[lodge_lists[n] for n in printed];confidence='HIGH_FROZEN_SOURCE_TEXT';note='Exact source lists, not marginal notes or generated chapter menus. Lodge printed-book boundaries differ from canonical Niese books.'
    if b==7:note+=' Printed-book VII list is already preserved in production Book VI, not this Book VII slice; it covers canonical VI–VII. Do not manufacture a new Book-VII-specific list.'
    if b==4:note+=' Both printed IV and V lists survive here; IV preserves 1,2,3,5,5,6,7.'
    action='Reuse complete existing source list(s), identifying printed-book scope; no segmentation or source-text restoration.'
   elif slug=='bellum' and source=='Whiston':
    auth=['bellum-whiston-control','bellum-whiston-provenance'];note='Pinned Perseus control has book/chapter heads but no separate contents list. Frozen provenance makes supplied production XML the textual base and Perseus an external control. Complete print contents/preparation source not recovered.';action='HOLD restoration: supply actual English preparation source or complete identified Whiston contents pages. Do not collect in-text headings.'
   elif slug=='bellum' and lang=='Latin':
    auth=['cardwell-ocr','cardwell-corrected',f'cardwell-html-{b}'];note='Current and local merged running-text transcriptions have no verified separate contents list. These exports do not establish complete printed front matter.'
   elif slug=='contra-apionem':
    auth=['contra-'+lang.lower()];note='Complete frozen upstream digital TEI has two books, no front/list contents encoding. This establishes digital availability only, not absence from the complete printed edition.'
   elif slug=='deh' and lang=='English':
    status=NONE;auth=[path,'deh-english-consultation-export'];confidence='HIGH_BORN_DIGITAL_SOURCE';note='Registered born-digital Pollard v1.0 translation has no source contents list. Complete consultation export has none and expressly subordinates itself to frozen TEI; chapter/unit labels are not contents.';action='No source TOC to display for this registered translation; do not generate one.'
   elif slug=='deh' and lang=='Latin':
    auth=['deh-latin-freeze','deh-ussani-digital'];note='Frozen Ussani-based corpus and named digilibLT upstream have running text / Prologue, no separate contents list. This does not prove that complete Ussani print apparatus has no contents.'
   elif slug=='antiquities':
    auth=[k for k in (f'ant-latin-word-{b}',f'ant-latin-tpen-{b}',f'ant-polyglot-html-{b}') if k in authorities];note='Current and inspected earlier project material do not furnish an attested list here. Titles, duration summaries and HAEC SUNT formulas without entries are not reconstructed as TOCs. Complete source paratext remains to be verified.'
   rows.append({'work':work,'book':b,'source':source,'language':lang,'toc_status':status,'authority':'; '.join(auth),'current_encoding':'SOURCE_CONTENTS_BLOCK_PRESENT' if observed else 'NO_SOURCE_CONTENTS_BLOCK_IN_THIS_BOOK_XML','production_file':path,'production_sha256':sha(p.read_bytes()),'production_toc_present':observed,'available_elsewhere_in_production':slug=='bellum' and source=='Lodge (1602)' and b==7,'source_scope':'Born-digital translation v1.0' if status==NONE else 'Specified list/source evidence; no unsupported complete-edition absence claim','recommended_action':action,'confidence':confidence,'evidence_note':note,'contents_observations':locs})
   observations[path]={'chapter_zero':node_record(tr,block) if block is not None else None,'body_incipit':norm(text(tr.xpath('//*[local-name()="body"]')[0]))[:280],'front_list_contents_candidates':[node_record(tr,n) for n in tr.xpath('//*[local-name()="front" or local-name()="list" or @type="contents" or @type="toc" or @type="tcp-list"]')],'paragraph_count':len(tr.xpath('//*[local-name()="p"]'))}
assert len(rows)==104 and len({(r['work'],r['book'],r['source']) for r in rows})==104
assert Counter(r['toc_status'] for r in rows)=={PRESENT:26,OMITTED:1,NONE:5,UNKNOWN:72}
proem=[]
for lang in ('Greek','Latin','English'):
 p=ROOT/f'assets/xml/antiquities/{lang}/preface.xml';tr=E.parse(str(p));trees[p.relative_to(ROOT).as_posix()]=tr;proem.append({'work':'Antiquities','context':'Proem','language':lang,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes()),'toc_status':UNKNOWN,'observation':'No encoded source contents list; no generated Proem menu is substituted.'})
assert len(trees)==107
reg=E.parse(str(ROOT/'assets/xml/antiquities/structure.xml'));ts=reg.xpath('//t:fs[@type="traditional-boundary"]',namespaces=NS)
def field(e,k):return ''.join(e.xpath(f'./t:f[@name="{k}"]/t:string/text()',namespaces=NS))
reg_counts={'level_rows':len(ts),'chapters':sum(field(e,'scheme')=='chapter' for e in ts),'subchapters':sum(field(e,'scheme')=='subchapter' for e in ts),'physical_positions':len({field(e,'physical-point') for e in ts}),'bamberg':len(reg.xpath('//t:fs[@type="bamberg-boundary"]',namespaces=NS)),'primary_statuses':dict(Counter(field(e,'verification-status') for e in ts))}
assert [reg_counts[k] for k in ('level_rows','chapters','subchapters','physical_positions','bamberg')]==[1689,257,1432,1441,198]
summary={}
for work,slug,books,sources in specs:
 for lang,source,d in sources:
  selected=[r for r in rows if r['work']==work and r['source']==source];summary[work+' / '+source]={s:[r['book'] for r in selected if r['toc_status']==s] for s in (PRESENT,OMITTED,NONE,UNKNOWN)}
result={'audit_date':'2026-10-07','base_commit':BASE,'worktree':str(ROOT),'branch':'source-toc-navigation','verdict':'STOP_AFTER_CENSUS_NO_IMPLEMENTATION','phase_a_book_source_rows':104,'additional_proem_observations':proem,'status_totals':dict(Counter(r['toc_status'] for r in rows)),'totals_by_work_source':summary,'source_authorities':authorities,'census':rows,'all_production_observations':observations,'whiston_digital_candidate_contents':pgbooks,'whiston_git_lineage':history,'prior_word_transcription_observations':word_records,'archived_polyglot_observations':oldsite,'lodge_exact_source_contents_checks':lodge_checks,'lodge_volume_wide_list_of_works':volume_rec,'restoration_gate':{'pass':False,'blockers':['Whiston printed contents / preparation provenance is not established for Antiquities or Bellum.','Latin Antiquities V upstream contents readings differ; governing transcription not uniquely identified.'],'existing_hold':'Latin Antiquities XIV SR-061 remains untouched; no new source judgment.'},'source_omission_conclusion':'Systematic intentional Whiston contents exclusion has not been established. Antiquities V retains a list; other absence predates earliest inspected per-book Git blobs. Bellum frozen documentation identifies other editorial operations, not a TOC-exclusion rule.','source_text_restored':False,'reader_changed':False,'web_used':False,'registry_counts':reg_counts}
dump('SOURCE_TOC_CENSUS.json',result)
fields=[k for k in rows[0] if k!='contents_observations'];s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows({k:r[k] for k in fields} for r in rows);write('SOURCE_TOC_CENSUS.csv',s.getvalue())
authority_md='''# Source authority for the contents census

Audit date: 2026-10-07. No source text was restored and no structural adjudication was reopened.

The 104-row matrix covers every registered book/source combination. Three Antiquities Proem files were also inspected. PRESENT_IN_PRODUCTION records existing attested lists, including the Lodge VII list preserved elsewhere in production. NOT_YET_VERIFIED is retained where source-level existence, absence or provenance is unestablished. SOURCE_HAS_NO_TOC is used only for the registered born-digital Pollard English translation, not inferred for print editions from incomplete digital transcriptions.

## Whiston authority limit

The saved Gutenberg 2848 HTML has a CONTENTS block with book/chapter hyperlinks. Its particular printing and whether that list was added for electronic navigation are not established locally. The candidate has 256 chapter links: 243 match their linked heading after whitespace collapse; 13 do not, including wording, spelling, punctuation, footnote formatting and a split heading. Both exact texts are retained in the JSON. These comparisons do not adjudicate variants or establish print provenance. Matching in-text headings are observations, not a reconstruction method or proof of printed provenance. Earlier project tables label Whiston (1737), but do not identify a complete preparation source or a contents-transcription policy. Antiquities V already has eleven summary paragraphs. Certifying/restoring all twenty lists by copying that digital navigation would exceed the evidence.

Bellum's frozen package expressly makes supplied production XML its textual base. Pinned Perseus is an external control with no separate contents list. Retained printed evidence supports a Book-VII running-text recovery, not the complete contents apparatus. No located document establishes deliberate systematic TOC exclusion. The missing authority is the English preparation master or complete identified Whiston source, with its source contents pages and governing transcription policy. Existing editorial-note omission documentation is not a TOC-omission rule.

## Bamberg and Lodge

Latin Antiquities V has fourteen upstream capitula paragraphs. Word reads ihesus, chananeos, tribubus; archived HTML reads iehsus, chananaeos, tribubs. Both remain evidence. Identify the governing transcription before importing wording. Latin XIV SR-061 remains a whole-paragraph source/structure hold: contents mix with Herodian narrative, and its origin/placement is unestablished. Nothing is moved, split, deleted or adjudicated here.

Lodge's seven printed lists have 21,28,19,7,14,16,31 entries (136 total). All seven decoded source text streams match the accepted production derivatives exactly. Printed IV preserves 1,2,3,5,5,6,7. Canonical IV contains printed IV and V lists; canonical V contains printed VI; canonical VI contains printed VII. Canonical VII starts inside printed VII; its complete source contents list remains in canonical VI. A future view must disclose the printed-book scope without inventing a new list or a subset inferred from navigation. The volume-wide list of works in the first source front is separate paratext. Lodge's 4,001-section segmentation is unchanged.

## Method and limits

All 107 production book/Proem XMLs were parsed. Actual contents wording and wrappers, including unqualified chapter-zero paragraphs and TCP-list spans, were inspected. ZIP/source files were read without extraction or alteration. Word OOXML inspection included nested tables. Local Git blobs were read to trace Whiston history. No list was generated from IDs, Chapter menus, Niese coordinates, Bamberg divisions, Alignment units or marginal notes. No web search/fetch occurred. No source PDF or manuscript image was reopened to adjudicate structure.

Local searches covered canonical/worktree XML and local Git history, recovery _source/provenance/review metadata, Segmentation resources, relevant Downloads packages, earlier transcription/HTML folders, Lodge's frozen master, Cardwell running-text exports and DEH authorities. This is a bounded census of available evidence, not a claim that every historic print witness or every file on disk was examined. Niese Antiquities PDFs remain available locally for later paratext verification; implementation is blocked by the requested Whiston/source-wording gate first. Print-level absence is not concluded from a missing list in the current XML.

## Fingerprints

| Authority | File SHA-256 | ZIP entry SHA-256, if applicable |
|---|---|---|
'''
for k,a in authorities.items():authority_md+=f'| {k} | {a["sha256"]} | {a.get("entry_sha256", "")} |\n'
authority_md+='\nExact absolute paths, ZIP entry names, production hashes, source contents observations and historical Git-blob hashes are in SOURCE_TOC_CENSUS.json.\n';write('SOURCE_AUTHORITY.md',authority_md)
report='''# Source table of contents census

**NO-GO for reader integration: the requested source-restoration gate has not passed.** Every current book/source combination has a row, but source-level verification remains open in 72 of the 104 rows. Three additional Proem files were inspected. Only this supplemental review directory is written. No source text was imported and reader behaviour has not changed.

'''
report+='Base: '+BASE+'. Branch: source-toc-navigation. Worktree: '+str(ROOT)+'. Canonical was clean on v2-development; HEAD and origin/v2-development matched the required base.\n\n'
report+='| Work / source | Present in production | Upstream list omitted from book | Source has no TOC | Not yet verified |\n|---|---|---|---|---|\n'
for k,s in summary.items():report+='| '+k+' | '+' | '.join(', '.join(map(str,s[v])) or '—' for v in (PRESENT,OMITTED,NONE,UNKNOWN))+' |\n'
report+='''
Totals: **26 PRESENT_IN_PRODUCTION; 1 PRESENT_IN_AUTHORITY_OMITTED_FROM_PRODUCTION; 5 SOURCE_HAS_NO_TOC; 72 NOT_YET_VERIFIED.** The per-book evidence, production observations, authority references and actions are in SOURCE_TOC_CENSUS.csv/JSON. PRESENT does not assert list-to-navigation identity.

Already encoded source lists: Antiquities Greek V and XI–XX; Antiquities Latin XIII–XX; Lodge printed Bellum I–VII. Seven Lodge lists live in six canonical production files; the list relevant to canonical VII remains in canonical VI. Antiquities Whiston V has a list in production too, but stays NOT_YET_VERIFIED as source-print paratext. Existing encoding must not be confused with printed-source provenance.

Upstream Latin V capitula are missing from production, but the Word and HTML readings differ. Neither is silently selected. Existing Latin XIV hold SR-061 remains intact. A Whiston digital candidate is located, but source-authorized print contents/preparation provenance is not. The Gutenberg candidate contains 256 chapter links; 13 do not match their linked heading after whitespace-only comparison. Exact candidate list/heading texts are retained independently, without silent correction. Deliberate systematic omission cannot be concluded from the inspected evidence. SOURCE_AUTHORITY.md identifies the exact required source/adjudication.

The five books of the registered born-digital Pollard English translation have no source contents list. Cardwell, Niese, Boysen and Whiston rows without an attested list remain NOT_YET_VERIFIED for complete source paratext. Absence in current/frozen digital running text does not establish print-level SOURCE_HAS_NO_TOC.

## Deferred reader design

After source provenance clears, reuse existing contents/list XML where safe or use a TEI paratext companion with witness/book locators and source scope. Source text must not live in JavaScript, ordinary chapter paragraphs or a fake chapter wrapper. A generic availability index can add Table of contents first in the Chapter selector, preserve numbered options and select view=contents. Contents mode removes conflicting chapter/subchapter/bamberg/niese/unit parameters, preserves book, unrelated parameters and fragments, and follows existing history flow. Mixed panes show the selected witness's own source list or a neutral unavailability message. No entry links are inferred from navigation numbers. These are proposals only.

## QA and protected behaviour

All 107 current reader book/Proem XMLs parse. Registry populations remain 257 Chapters, 1,432 Subchapters, 1,689 level rows, 1,441 physical points and 198 Bamberg identities. Lodge source contents equality passes 7/7 lists, 136 entries.

All pre-existing worktree files remain byte-identical to the census baseline, including XML, structure.xml, renderer, templates, styles and historical review packets. Inspected external authorities also retain their exact hashes. Canonical checkout and Git index are unchanged. Source text, IDs, sameAs, milestones, segmentation and Book-XI witness order were not edited.

Browser/URL/history/theme and exhaustive navigation suites are NOT RUN because Phase B stopped before any reader change. No new browser certification or regression PASS is claimed. Antiquities traditional/Niese/Bamberg/alignment, Bellum Cardwell/Whiston/Lodge/Niese, DEH and Contra Apionem are preserved by byte identity, not re-certified through execution. Historical Bellum Greek 818 empty Whiston milestones are not treated as TOC text or activated.

Changed files: only this new census/report/QA/reproducibility packet. No source/application, recovery/frozen, existing certification or generated site file changed. Nothing staged, committed, pushed, merged or rebased. GO only for reviewing the census; NO-GO for reader integration until the source gate clears.
'''
write('REPORT.md',report)
assert inventory()==before, 'Pre-existing worktree file changed'
assert {p:sha(Path(p).read_bytes()) for p in external_before}==external_before
assert git(CANON,'branch','--show-current')=='v2-development'
assert git(CANON,'rev-parse','HEAD')==BASE and git(CANON,'rev-parse','origin/v2-development')==BASE
assert git(CANON,'status','--short')==''
assert git(ROOT,'diff','--name-only')=='' and git(ROOT,'diff','--cached','--name-only')==''
assert git(ROOT,'status','--short','--','.',':(exclude)review/Source_TOC_Navigation_2026-10-07')==''
qa={'verdict':'STOP_AFTER_CENSUS_NO_IMPLEMENTATION','initial_safety_gate':initial,'book_source_census_rows':104,'census_identities_unique':True,'complete_book_source_matrix':True,'proem_files':3,'well_formed_production_xml':107,'status_totals':result['status_totals'],'registry_invariants':reg_counts,'lodge_contents_source_equality':{'lists':7,'items':136,'pass':True,'checks':lodge_checks},'whiston_candidate':{'books':20,'chapter_links':sum(len(r['entries']) for r in pgbooks),'matching_linked_headings':sum(e['matches_linked_heading_after_whitespace_collapse'] for r in pgbooks for e in r['entries']),'printed_provenance_verified':False,'deliberate_omission_established':False},'latin_v_capitula':{'upstream_paragraphs':14,'production_absence_verified':True,'candidate_reading_variants_preserved':True,'unique_restoration_authority':False},'no_synthetic_contents':True,'no_source_restoration':True,'no_new_structural_source_judgment':True,'no_xml_application_change':True,'existing_worktree_files_byte_identical':True,'existing_worktree_file_count':len(before),'inspected_external_files_byte_identical':True,'inspected_external_file_count':len(external_before),'historical_certification_packets_unchanged':True,'canonical_checkout_clean_unchanged':True,'worktree_index_untouched':True,'web_used':False,'site_build_run':False,'browser_url_history_theme_qa':'NOT_RUN_PHASE_B_BLOCKED','antiquities_navigation_regression':'NOT_RUN; source and application byte identity verified','bellum_navigation_regression':'NOT_RUN; source and application byte identity verified','deh_contra_apionem_regression':'NOT_RUN; source and application byte identity verified','git_actions':'Read-only inspections and explicitly requested branch/worktree creation only; no stage, commit, push, merge, rebase, reset, stash, clean or configuration change','remaining_source_uncertainties':result['restoration_gate']}
dump('QA.json',qa)
manifest={'base_commit':BASE,'modified_existing_files':[],'no_existing_file_modified':True,'new_files':{},'preexisting_worktree_files':before,'inspected_external_file_hashes':external_before,'manifest_self_hash':'Omitted to avoid self-reference; FILE_MANIFEST.json is itself a new review deliverable.'}
for p in sorted(OUT.iterdir()):
 if p.is_file() and p.name!='FILE_MANIFEST.json':manifest['new_files'][p.relative_to(ROOT).as_posix()]={'before_sha256':None,'after_sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
dump('FILE_MANIFEST.json',manifest)
assert inventory()==before
print(json.dumps({'verdict':qa['verdict'],'rows':104,'statuses':qa['status_totals'],'existing_files_unchanged':len(before),'external_files_unchanged':len(external_before),'lodge_lists':7,'lodge_items':136,'whiston_candidate':qa['whiston_candidate'],'registry':reg_counts,'created_files':[p.name for p in OUT.iterdir()]},ensure_ascii=False,indent=2))
