from pathlib import Path
from lxml import etree as E,html
import json,hashlib,re,difflib,csv,subprocess
R=Path(r'C:\workspace\LatinJosephus-source-toc-navigation');V=R/'review/Source_TOC_Navigation_2026-10-07';N={'t':'http://www.tei-c.org/ns/1.0','w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def dump(name,v):(V/name).write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
extract=json.loads((V/'BAMBERG_WORD_EXTRACTION_2026-10-08.json').read_text());conc=json.loads((V/'BLATT_TEI_CONCORDANCE_2026-10-08.json').read_text());old=json.loads((V/'SOURCE_TOC_CENSUS.json').read_text(encoding='utf-8-sig'));records=json.loads((V/'VERIFIED_CONTENTS_REGISTRY_2026-10-08.json').read_text());base=json.loads((V/'PHASE_B_BASELINE_2026-10-08.json').read_text())
rng=E.RelaxNG(E.parse(str(R/'review/Antiquities_Traditional_Navigation_2026-10-06/tei_all.rng')));schema=[];entries=[];supp=[]
for b in range(2,6):
 p=R/f'assets/xml/antiquities/paratext/bamberg78/book-{b:02}-contents.xml';d=E.parse(str(p));assert rng.validate(d),str(rng.error_log)
 items=d.xpath('//t:list[@type="capitula"]/t:item',namespaces=N);expected=[r for r in extract['entries'] if r['book']==b]
 assert [''.join(i.itertext()) for i in items]==[r['text'] for r in expected]
 assert [i.get('n') for i in items]==[r['label'] for r in expected]
 for c in [c for c in conc if c['book']==b]:
  node=d.xpath('//*[@xml:id=$id]',namespaces=N,id=c['tei_id']);assert len(node)==1;assert ''.join(node[0].itertext())==c['text'];assert E.QName(node[0]).localname==c['tei_element']
  if c['tei_element']=='supplied':assert node[0].get('reason')=='lost' and node[0].get('source')=='#blatt' and node[0].get('resp')=='#human-editor'
 allsup=d.xpath('//t:supplied',namespaces=N);assert len(allsup)==len([c for c in conc if c['book']==b and c['tei_element']=='supplied'])
 schema.append({'file':str(p.relative_to(R)),'sha256':sha(p),'schema':'official project-retained TEI P5 tei_all.rng','result':'PASS'})
 entries.append({'book':b,'entries':len(items),'supplements':len(allsup),'entry_text_number_order':'PASS','surrounding_Latin':'PASS','italic_concordance':'PASS'})
p=R/'assets/xml/source-contents.xml';assert rng.validate(E.parse(str(p))),str(rng.error_log);schema.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'result':'PASS'})
assert len(conc)==64 and sum(c['tei_element']=='supplied' for c in conc)==63
assert sha(Path(extract['source']))==extract['sha256']
dump('BAMBERG_TRANSCRIPTION_QA_2026-10-08.json',{'books':entries,'schema':schema,'word_italic_spans':64,'lexical_Blatt_supplements':63,'whitespace_only_italic_spans':1,'invented_or_omitted_supplements':0,'DOCX_unchanged':True,'result':'PASS'})
# Compare the earlier Word paragraphs and archived Google Sites HTML with the governing new Word text.
new=[r for r in extract['entries'] if r['book']==5];previous=old['prior_word_transcription_observations']['5']['capitula_paragraphs'];previous=[t for t in previous if t.strip()]
h=old['archived_polyglot_observations']['5']['capitula_cell_text'];matches=list(re.finditer(r'(?m)^([IVXLCDM]+)\s',h));htmlentries=[' '.join(h[m.start():matches[i+1].start() if i+1<len(matches) else len(h)].split()) for i,m in enumerate(matches)]
assert len(new)==len(previous)==len(htmlentries)==13
variants=[]
for source,arr in [('earlier Word',previous),('archived Google Sites HTML',htmlentries)]:
 for n,prior in zip(new,arr):
  if n['text']==prior:continue
  diffs=[{'operation':op,'earlier':prior[a:b],'governing':n['text'][c:d]} for op,a,b,c,d in difflib.SequenceMatcher(None,prior,n['text'],autojunk=False).get_opcodes() if op!='equal']
  compact=lambda t:re.sub(r'\s+','',t)
  cats=[]
  if compact(prior)==compact(n['text']):cats=['SPELLING_PUNCTUATION_SPACING_DIFFERENCE']
  else:
   cats=['SPELLING_PUNCTUATION_SPACING_DIFFERENCE']
   if source=='archived Google Sites HTML' and n['label'] in ['I','II','IIII','VII','VIIII']:cats.append('EARLIER_TRANSCRIPTION_ERROR_CORRECTED_IN_NEW_DOCUMENT')
  variants.append({'entry':n['label'],'comparison_source':source,'earlier_text':prior,'governing_text':n['text'],'categories':cats,'differences':diffs,'decision':'Import governing 8 October Word text exactly; no replacement from earlier evidence.','material_uncertainty':False})
dump('BOOK_V_VARIANCE_REGISTER_2026-10-08.json',{'governing_source':extract['source'],'sha256':extract['sha256'],'entries':13,'comparisons':26,'variants':variants,'chapter_number_or_entry_boundary_differences':0,'consequential_unresolved_encoding_problems':0,'classification_limit':'Error classifications describe correction relative to the human-authorized improved working transcription, not fresh manuscript adjudication. Literal insertion notation a\\b/ and Qui\\a/ is retained as supplied in the Word text.'})
# Keep the accepted census immutable. This is a separate dated status amendment.
key=lambda w,b,l,s:(w,int(b),l,s)
sourcekeys={'Niese':'niese','Bamberg Msc.Class.78':'bamberg78','Bamberg 78':'bamberg78','Whiston':'whiston','Lodge 1602':'lodge1602'}
matrix=[]
for row in old['census']:
 p=row['production_file'];parts=p.split('/');w=parts[2];b=int(row['book']);l=row['language'];witness=('lodge1602' if 'Lodge1602' in p else 'bamberg78' if w=='antiquities' and l=='Latin' else 'current' if w=='bellum' and l=='Greek' else 'niese' if l=='Greek' else 'whiston' if l=='English' and w!='deh' else 'pollard' if l=='English' else 'ussani' if w=='deh' else 'cardwell' if w=='bellum' else 'boysen')
 rec=next((r for r in records if (r['work'],int(r['book']),r['language'],r['witness'])==(w,b,l,witness)),None)
 amended={**row,'amendment_date':'2026-10-08','witness_key':witness,'source_existence':'VERIFIED_PRESENT' if rec else 'VERIFIED_NO_TOC' if row['toc_status']=='SOURCE_HAS_NO_TOC' else 'PRESENT_WITH_HOLD' if w=='antiquities' and b==14 and l=='Latin' else 'NOT_YET_VERIFIED','text_verification':'HUMAN_DOUBLE_CHECKED' if rec and w=='antiquities' and l=='Latin' and b in [2,3,4] else 'HUMAN_GOVERNING_TRANSCRIPTION' if rec and w=='antiquities' and l=='Latin' and b==5 else 'EXISTING_SOURCE_PARATEXT_VERIFIED' if rec else 'DEFERRED','encoded_availability':bool(rec),'publication_eligibility':'ELIGIBLE' if rec else 'DEFERRED','browser_integration':'COMPLETE' if rec else 'UNAVAILABLE','supplements_present':bool(rec and w=='antiquities' and l=='Latin' and b in [2,3,4]),'phase_b_recommendation':'Verified source contents display, no inferred navigation targets.' if rec else 'Preserve source evidence and defer; no generated substitute.'}
 if w=='antiquities' and l=='Latin' and b in [2,3,4,5]:amended['phase_b_recommendation']='Human-edited Word transcription imported; marginal II–IV / main-text V; controlling authority supersedes earlier comparative versions.'
 matrix.append(amended)
assert sum(x['encoded_availability'] for x in matrix)==29
assert len(matrix)==104
dump('SOURCE_TOC_ELIGIBILITY_2026-10-08.json',{'original_census':'SOURCE_TOC_CENSUS.json (unchanged)','per_source_policy':'Revised human authorization, 2026-10-08','rows':matrix,'eligible':29,'deferred':75})
cols=['work','book','source','language','witness_key','toc_status','source_existence','text_verification','encoded_availability','supplements_present','publication_eligibility','browser_integration','phase_b_recommendation']
with (V/'SOURCE_TOC_ELIGIBILITY_2026-10-08.csv').open('w',encoding='utf8',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');writer.writeheader();writer.writerows(matrix)
dump('EDITORIAL_DECISIONS_2026-10-08.json',{'blocking':[],'preserved_readings':[{'book':2,'entry':'III','reading':'factus factusque','decision':'Preserve exact governing transcription; no silent removal.'},{'book':4,'entry':'V','reading':'[...]si','decision':'Existing uncertainty retained literally; does not prevent faithful encoding.'},{'book':4,'entry':'I','reading':'\\m/','decision':'Retain human transcription notation literally; no inferred mapping.'},{'book':5,'entries':['VIII','VIIII'],'readings':['a\\b/','Qui\\a/'],'decision':'Retain human transcription insertion notation exactly.'}],'bibliography':{'Blatt':'Franz Blatt, ed., The Latin Josephus (Aarhus, 1958); local project _pages/about.md. Exact supplement page references not supplied.'},'deferred':[{'witness':'Latin Antiquities XIV','reason':'Existing SR-061 whole-paragraph contents/Herodian-narrative hold; no split, deletion or new judgment.'},{'witness':'Whiston/Cardwell/other unverified sources','reason':'Original census provenance limits remain; no generated reconstruction.'}]})
print('TEI and transcription PASS',entries,'matrix',len(matrix),'eligible',sum(x['encoded_availability'] for x in matrix),'Book V variants',len(variants))
# Reproducible expectations use exact source XML text, without converter decorations.
expect=[]
for row in records:
 d=E.parse(str(R/row['path']));roots=[]
 for selector in row['selectors']:
  if 'tei-div2' in selector:roots+=d.xpath('//*[local-name()="div2"][@n="0"]')
  elif 'tei-div[' in selector:roots+=d.xpath('//*[local-name()="div"][@type="contents"]')
  else:
   suffix=selector.split('corresp$="')[1].split('"')[0];roots += [q for q in d.xpath('//*[local-name()="seg"][@type="tcp-list"]') if q.get('corresp','').endswith(suffix)]
 assert len(roots)==len(row['selectors']),row
 expect.append({**row,'texts':[''.join(q.itertext()) for q in roots],'supplements':[q.text for z in roots for q in z.xpath('.//*[local-name()="supplied"]')]})
dump('CONTENTS_EXPECTATIONS_2026-10-08.json',expect)
