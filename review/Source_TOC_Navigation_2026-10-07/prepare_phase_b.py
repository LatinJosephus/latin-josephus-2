from pathlib import Path
from lxml import etree as E
from zipfile import ZipFile
import json,hashlib,re,copy,csv
ROOT=Path(r'C:\workspace\LatinJosephus-source-toc-navigation')
REV=ROOT/'review/Source_TOC_Navigation_2026-10-07'
DOC=Path(r'C:\workspace\Bamberg TOC books 2-5\Bamberg Msc. Class. 78 - TOC - bks. 2, 3, 4, 5.docx')
T='http://www.tei-c.org/ns/1.0'; W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; X='{http://www.w3.org/XML/1998/namespace}'; ns={'w':W,'t':T}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
def node(parent,tag,text=None,**attrs):
 q=E.SubElement(parent,'{'+T+'}'+tag,**attrs);q.text=text;return q
def tei(title):
 r=E.Element('{'+T+'}TEI',nsmap={None:T});h=node(r,'teiHeader');fd=node(h,'fileDesc');ts=node(fd,'titleStmt');node(ts,'title',title);node(ts,'respStmt');rs=ts[-1];node(rs,'resp','Transcription and import authority');node(rs,'name','Richard M. Pollard; source import documented in the review packet')
 ps=node(fd,'publicationStmt');node(ps,'p','LatinJosephus source paratext; working integration, 2026-10-08.');sd=node(fd,'sourceDesc');node(sd,'p','Source-specific contents; no navigation correspondence is asserted.');text=node(r,'text');body=node(text,'body');return r,body,sd
def xmlout(p,r):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(E.tostring(r,encoding='UTF-8',xml_declaration=True,pretty_print=True))
if not (REV/'PHASE_B_BASELINE_2026-10-08.json').exists():
 files={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts}
 save(REV/'PHASE_B_BASELINE_2026-10-08.json',files)
 archive=REV/'phase-a-accepted-2026-10-07';archive.mkdir(exist_ok=False)
 for name in ['REPORT.md','QA.json','FILE_MANIFEST.json','SOURCE_AUTHORITY.md']:(archive/name).write_bytes((REV/name).read_bytes())
with ZipFile(DOC) as z:
 d=E.fromstring(z.read('word/document.xml'));styles=E.fromstring(z.read('word/styles.xml'))
 assert not d.xpath('//w:del|//w:ins',namespaces=ns),'Tracked changes need separate inspection'
 sm={q.get('{'+W+'}styleId'):q for q in styles.findall('w:style',ns)}
 default=styles.find('w:docDefaults/w:rPrDefault/w:rPr/w:i',ns)
 def on(q):return q is not None and q.get('{'+W+'}val','true') not in ['false','0','off']
 def chain(id,seen=()):
  if not id or id in seen or id not in sm:return []
  q=sm[id];b=q.find('w:basedOn',ns);return chain(b.get('{'+W+'}val') if b is not None else None,seen+(id,))+[q]
 def italic(p,r):
  value=on(default);ps=p.find('w:pPr/w:pStyle',ns);cs=r.find('w:rPr/w:rStyle',ns)
  ids=[ps.get('{'+W+'}val') if ps is not None else 'Normal',cs.get('{'+W+'}val') if cs is not None else None]
  for id in ids:
   for st in chain(id):
    it=st.find('w:rPr/w:i',ns)
    if on(it):value=not value # OOXML style toggle property
  direct=r.find('w:rPr/w:i',ns)
  if direct is not None:value=on(direct)
  return value
 pars=[]
 for i,p in enumerate(d.xpath('//w:body//w:p',namespaces=ns)):
  text='';spans=[];runs=[]
  for j,r in enumerate(p.xpath('.//w:r',namespaces=ns)):
   v=''.join(''.join(c.itertext()) if E.QName(c).localname=='t' else '\t' if E.QName(c).localname=='tab' else '\n' if E.QName(c).localname in ['br','cr'] else '' for c in r if E.QName(c).localname in ['t','tab','br','cr'])
   if not v:continue
   start=len(text);text+=v;it=italic(p,r);runs.append({'run':j,'start':start,'end':len(text),'text':v,'italic':it})
   if it:
    if spans and spans[-1]['end']==start:spans[-1]['end']=len(text);spans[-1]['text']+=v;spans[-1]['runs'].append(j)
    else:spans.append({'start':start,'end':len(text),'text':v,'runs':[j]})
  pars.append({'paragraph':i,'text':text,'runs':runs,'italic_spans':spans})
bookpars={2:(2,[3,4,5],[]),3:(9,list(range(10,21)),[]),4:([24,25],list(range(26,31)),[31]),5:(34,list(range(35,48)),[])}
inventory=[];italic_inventory=[];concordance=[]
for book,(heads,entries,closing) in bookpars.items():
 r,body,sd=tei(f'Bamberg Msc.Class.78 Antiquities {book}: source capitula')
 sd.remove(sd[0]);lb=node(sd,'listBibl');b=node(lb,'bibl','Bamberg, Staatsbibliothek, Msc.Class.78');b.set(X+'id','bamberg78');meta=pars[{2:0,3:7,4:22,5:33}[book]]['text'];node(b,'ref',meta,target=re.search(r'https://[^\s\]]+',meta).group(0));b=node(lb,'bibl',DOC.name+'; human-edited working transcription supplied 8 October 2026. SHA-256 '+sha(DOC));b.set(X+'id','word-transcription');b=node(lb,'bibl',"Franz Blatt, ed., The Latin Josephus (Aarhus, 1958), Antiquities I–V. Citation as recorded in the project’s _pages/about.md. Identified by the human editor as the source of italicized supplements; precise supplement page references were not supplied.");b.set(X+'id','blatt')
 resp=r.find('.//{'+T+'}respStmt');resp.set(X+'id','human-editor')
 div=node(body,'div',type='contents',subtype='marginal-capitula' if book<5 else 'main-text-capitula',source='#bamberg78 #word-transcription');div.set(X+'id',f'bamberg78-ant-{book:02}-contents')
 def mixed(q,par):
  text=par['text'];last=0
  for k,span in enumerate(par['italic_spans']):
   # Whitespace-only italics carry formatting, not a supplied manuscript letter.
   kind='supplied' if span['text'].strip() else 'hi'
   if len(q):q[-1].tail=(q[-1].tail or '')+text[last:span['start']]
   else:q.text=(q.text or '')+text[last:span['start']]
   e=node(q,kind,span['text'],**({'reason':'lost','source':'#blatt','resp':'#human-editor','rend':'italic'} if kind=='supplied' else {'rend':'italic'}));e.set(X+'id',f'bamberg78-ant-{book:02}-p{par["paragraph"]}-i{k+1}')
   rec={'book':book,'paragraph':par['paragraph'],**span,'classification':'BLATT_SUPPLEMENT' if kind=='supplied' else 'WHITESPACE_FORMATTING','tei_id':e.get(X+'id'),'tei_element':kind}
   italic_inventory.append(rec);concordance.append(rec);last=span['end']
  if len(q):q[-1].tail=(q[-1].tail or '')+text[last:]
  else:q.text=(q.text or '')+text[last:]
 for i in heads if isinstance(heads,list) else [heads]:mixed(node(div,'head'),pars[i])
 lst=node(div,'list',type='capitula')
 for i in entries:
  p=pars[i];label=re.match(r'^(?:\s*)([IVXLCDM]+)\b',p['text']).group(1);item=node(lst,'item',n=label);mixed(item,p)
  assert ''.join(item.itertext())==p['text'];inventory.append({'book':book,'entry_order':len(lst),'label':label,'paragraph':i,'text':p['text']})
 for i in closing:mixed(node(div,'trailer'),pars[i])
 if book<5:node(div,'note','Italicized text has been supplied from Blatt’s edition where trimming of the manuscript margins has removed words.',type='editorial',resp='#human-editor')
 file=f'assets/xml/antiquities/paratext/bamberg78/book-{book:02}-contents.xml';xmlout(ROOT/file,r)
 for rec in concordance:
  if rec['book']==book:rec['file']=file
save(REV/'BAMBERG_WORD_EXTRACTION_2026-10-08.json',{'source':str(DOC),'sha256':sha(DOC),'paragraphs':pars,'entries':inventory,'counts':{b:len([q for q in inventory if q['book']==b]) for b in bookpars},'formatting_policy':'Resolved document defaults, paragraph and character style inheritance with OOXML italic toggles, then direct run formatting. Adjacent italic runs coalesced, character offsets preserved. Whitespace-only italics retained as hi, not supplied text.'})
save(REV/'WORD_ITALIC_SPANS_2026-10-08.json',italic_inventory);save(REV/'BLATT_TEI_CONCORDANCE_2026-10-08.json',concordance)
# A generic TEI feature-structure index registers only publication-eligible source paratext.
reg,body,sd=tei('LatinJosephus verified source contents index');lst=node(body,'list',type='source-contents');records=[]
def register(work,book,language,witness,path,selectors,note,authority):
 id=f'contents-{work}-{witness}-{book:02}';row={'id':id,'work':work,'book':str(book),'language':language,'witness':witness,'status':'VERIFIED','path':path,'selectors':selectors,'note':note,'authority':authority};records.append(row)
 item=node(lst,'item');item.set(X+'id',id);fs=node(item,'fs',type='source-contents')
 for k,v in row.items():
  if k=='id':continue
  f=node(fs,'f',name=k)
  if isinstance(v,list):
   coll=node(f,'vColl',org='list')
   for s in v:node(coll,'string',s)
  else:node(f,'string',v)
for b in [5,*range(11,21)]:register('antiquities',b,'Greek','niese',f'assets/xml/antiquities/Greek/book-{b:02}.xml',['tei-div2[n="0"]'],'','Production source contents formula and capitula; accepted Phase-A census. Existing transcription retained without source revision.')
for b in [13,*range(15,21)]:register('antiquities',b,'Latin','bamberg78',f'assets/xml/antiquities/Latin/book-{b:02}.xml',['tei-div2[n="0"]'],'','Production manuscript capitula and source transcription; accepted Phase-A census. Existing source readings retained.')
for b in bookpars:register('antiquities',b,'Latin','bamberg78',f'assets/xml/antiquities/paratext/bamberg78/book-{b:02}-contents.xml',['tei-div[type="contents"]'],'','Human-edited Word transcription supplied 2026-10-08. II–IV double-checked; V governing working transcription.')
for b in range(1,8):
 filebook={5:5,6:6,7:6}.get(b,b);printed={4:[4,5],5:[6],6:[7],7:[7]}.get(b,[b]);selectors=[f'tei-seg[type="tcp-list"][corresp$="/div[{n}]/list[1]"]' for n in printed]
 note='' if b<4 else 'These source contents follow Lodge’s printed book divisions. '+('This book contains the contents of printed Books IV and V.' if b==4 else f'The complete contents of printed Book {printed[0]} are displayed; its scope differs from the current reader book divisions.')
 register('bellum',b,'English','lodge1602',f'assets/xml/bellum/English/Lodge1602/book-{filebook:02}.xml',selectors,note,'Frozen final adjudicated Lodge master; seven source lists, 136 entries, exact textual equality certified by accepted census.')
xmlout(ROOT/'assets/xml/source-contents.xml',reg);save(REV/'VERIFIED_CONTENTS_REGISTRY_2026-10-08.json',records)
print(json.dumps({'entries':{b:len([q for q in inventory if q['book']==b]) for b in bookpars},'supplements':{b:len([q for q in concordance if q['book']==b and q['tei_element']=='supplied']) for b in bookpars},'italic_whitespace':len([q for q in concordance if q['tei_element']=='hi']),'registered_book_sources':len(records)}))