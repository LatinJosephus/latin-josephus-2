from pathlib import Path
import json, hashlib, collections, re, urllib.request, subprocess
from lxml import etree as E
from xml.parsers import expat
ROOT=Path(__file__).resolve().parents[2]
REVIEW=Path(__file__).resolve().parent
AUTH=Path(r"C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review")
REC=AUTH/'Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06'
VER=AUTH/'Antiquities_Loeb_Niese_Verification_2026-10-05'
NS='http://www.tei-c.org/ns/1.0'; XI='{http://www.w3.org/XML/1998/namespace}id'; T='{'+NS+'}'
def sha(b):return hashlib.sha256(b).hexdigest()
def inventory(root):
 return {str(p.relative_to(root)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}
def projection(e):
 if E.QName(e).localname in {'num','milestone','pb','lb','note','anchor'}:return ''
 return (e.text or '')+''.join(projection(c)+(c.tail or '') for c in e if isinstance(c.tag,str))
def primitive(parent,name,value):
 f=E.SubElement(parent,T+'f',name=name)
 E.SubElement(f,T+'string').text='' if value is None else str(value)
 return f
assert not (ROOT/'assets/xml/antiquities/structure.xml').exists(),'Registry must not already exist.'
a=json.loads((REC/'Antiquities_Structure_Reconciliation.json').read_text(encoding='utf-8-sig'))
v=json.loads((VER/'consolidated/Antiquities_Loeb_Niese_I-XX.json').read_text(encoding='utf-8-sig'))
rows=a['loeb_boundaries']; audits={r['loeb_boundary_id']:r for r in v['audited_boundaries']}
assert len(rows)==1689 and sum(r['source']['division_level']=='Chapter' for r in rows)==257
assert len({r['independent_niese_verification']['physical_boundary_id'] for r in rows})==1441
assert collections.Counter(r['independent_niese_verification']['verification_status'] for r in rows)=={'CONFIRMED_NIESE_START':1672,'CONFIRMED_WITHIN_NIESE':3,'LOEB_NIESE_NUMBER_DISAGREEMENT':3,'NIESE_SOURCE_AMBIGUOUS':11}
for r in a['current_xml_structures']:assert sha((Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')/r['file']).read_bytes())==r['sha256'],r['file']
for folder,manifest in [(REC,'Antiquities_Structure_Reconciliation_v1.1_SHA256SUMS.txt'),(VER,'Antiquities_Loeb_Niese_Verification_SHA256SUMS.txt')]:
 for line in (folder/manifest).read_text(encoding='utf-8-sig').splitlines():
  digest,name=line.split('  ',1);assert sha((folder/name).read_bytes())==digest,name
baseline={'base_commit':'f7d9142cad998e8a005adea1a22532b9a78592db','worktree':inventory(ROOT),'production':inventory(Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')),'authorities':{'reconciliation':inventory(REC),'verification':inventory(VER)}}
if not (REVIEW/'BASELINE.json').exists(): (REVIEW/'BASELINE.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding='utf-8')
schema=urllib.request.urlopen('https://tei-c.org/Vault/P5/4.12.0/xml/tei/custom/schema/relaxng/tei_all.rng').read()
(REVIEW/'tei_all.rng').write_bytes(schema)
rng=E.RelaxNG(E.fromstring(schema))
# Deduplicate only points independently certified to coincide, within each language.
points={}; mutations={}; parsed={}; locators={}; marker_log=[]
for r in rows:
 context='preface' if r['source']['chapter'] is None else str(r['source']['book']).zfill(2)
 for language in ['Greek','Latin','English']:
  key=language.lower(); loc=r[key+'_location']; out={'available':'false'}
  if loc:
   file=f'assets/xml/antiquities/{language}/'+('preface.xml' if context=='preface' else f'book-{context}.xml')
   if file not in parsed:parsed[file]=E.fromstring((ROOT/file).read_bytes())
   found=parsed[file].xpath('//*[@xml:id=$i]',i=loc['paragraph_id']);assert len(found)==1,(r['id'],language)
   p=found[0]; txt=projection(p);off=loc['offset']
   assert re.sub(r'\s+',' ',txt[off:].strip()).startswith(re.sub(r'\s+',' ',loc['anchor'].strip())),(r['id'],language,off,txt[off:off+140],loc['anchor'])
   out={'available':'true','file':file.removeprefix('assets/xml/antiquities/'),'paragraph':loc['paragraph_id'],'offset':str(off),'anchor':loc['anchor'],'kind':'paragraph','target':loc['paragraph_id']}
   if off:
    category=r[key+'_feasibility']['category']
    if category=='EXISTING_ELEMENT_BOUNDARY':
     # The frozen path identifies an existing child edge. Select its edge, not a guessed word.
     suffix=loc['path'].split('/p[')[-1].split(']',1)[1]
     if not suffix:
      cursor=[0];edges=[]
      def edge_walk(e,path):
       local=E.QName(e).localname
       if path and cursor[0]==off:edges.append(path)
       if local in {'num','milestone','pb','lb','note','anchor'}:return
       cursor[0]+=len(e.text or '')
       counts={}
       for child in e:
        name=E.QName(child).localname;counts[name]=counts.get(name,0)+1
        edge_walk(child,path+'/'+name+'['+str(counts[name])+']');cursor[0]+=len(child.tail or '')
      edge_walk(p,'');assert len(edges)==1,(r['id'],language,edges)
      suffix=edges[0]
     out.update(kind='element-edge',edge=suffix.lstrip('/'))
    else:
     pk=(file,loc['paragraph_id'],off)
     if pk not in points:
      marker_id='trad-'+key+'-'+r['id'];points[pk]=marker_id
      mutations.setdefault(file,[]).append((loc['paragraph_id'],off,marker_id))
     out.update(kind='anchor',target=points[pk])
  locators[(r['id'],language)]=out
# Insert bytes only; no XML reserialization, whitespace normalization, or entity rewriting.
for file,insertions in mutations.items():
 raw=(ROOT/file).read_bytes(); parser=expat.ParserCreate(namespace_separator='}'); stack=[]; current=None; segments={}; count={}
 def start(name,attrs):
  global current
  local=name.split('}')[-1];stack.append(local)
  if local=='p' and attrs.get('http://www.w3.org/XML/1998/namespace}id'):
   current=attrs['http://www.w3.org/XML/1998/namespace}id'];segments.setdefault(current,[]);count[current]=0
 def end(name):
  global current
  if stack[-1]=='p':current=None
  stack.pop()
 def text(value):
  if current and not any(s in {'num','milestone','pb','lb','note','anchor'} for s in stack):
   segments[current].append((count[current],parser.CurrentByteIndex,value));count[current]+=len(value)
 parser.StartElementHandler=start;parser.EndElementHandler=end;parser.CharacterDataHandler=text;parser.Parse(raw,True)
 edits=[]
 for pid,off,mid in insertions:
  candidates=[s for s in segments[pid] if s[0]<=off<s[0]+len(s[2])]
  assert len(candidates)==1,(file,pid,off)
  begin,byte,value=candidates[0];delta=off-begin
  # Expat separates entity expansions; an offset inside one escaped character cannot arise.
  actual=byte+len(value[:delta].encode('utf-8'))
  assert raw[actual:].startswith(value[delta:delta+1].encode('utf-8')),(file,pid,off,'entity edge')
  tag=f'<anchor xml:id="{mid}" type="traditional-boundary" corresp="../structure.xml#{mid.split("-",2)[2]}"/>'.encode('utf-8')
  if tag not in raw: edits.append((actual,tag))
  marker_log.append({'file':file,'paragraph':pid,'offset':off,'xml_id':mid,'type':'anchor'})
 for pos,tag in sorted(edits,reverse=True):raw=raw[:pos]+tag+raw[pos:]
 E.fromstring(raw)
 (ROOT/file).write_bytes(raw)
# Ordinary TEI feature structures encode typed scholarly fields; no private XML elements.
root=E.Element(T+'TEI',nsmap={None:NS});h=E.SubElement(root,T+'teiHeader');fd=E.SubElement(h,T+'fileDesc')
ts=E.SubElement(fd,T+'titleStmt');E.SubElement(ts,T+'title').text='Josephus, Antiquities: certified traditional Chapter/Subchapter registry'
ps=E.SubElement(fd,T+'publicationStmt');E.SubElement(ps,T+'p').text='Pre-publication structural navigation data, 2026-10-06.'
sd=E.SubElement(E.SubElement(fd,T+'sourceDesc'),T+'listBibl');E.SubElement(sd,T+'bibl').text='Traditional Hudson–Havercamp hierarchy retained by Niese and substantially reproduced by Loeb; independent citation and current physical-copy evidence remain distinct.'
for ident,commit,tag in [('reconciliation-v1.1','41e817680549767d36e3f80dbc825682908ea5e6','antiquities-structure-reconciliation-v1.1'),('verification-v1.0','19308a8ed937525c540827205b0c763768f5ce44','antiquities-loeb-niese-verification-v1.0')]:
 b=E.SubElement(sd,T+'bibl',{XI:ident});b.text=f'{tag}; recovery commit {commit}.'
body=E.SubElement(E.SubElement(root,T+'text'),T+'body');lst=E.SubElement(body,T+'list',type='traditional-boundaries')
# Range endpoints are compiled from certified source order, independently of current paragraph arithmetic.
chapter_rows=[r for r in rows if r['source']['division_level']=='Chapter']
for index,r in enumerate(rows):
 s=r['source'];verification=r['independent_niese_verification'];audit=audits[verification['loeb_boundary_id']]
 chapter=s['chapter'];book=s['book'];level=s['division_level'];context='Proem' if chapter is None else str(book)
 parent='ANT-Proem' if chapter is None else (f'ANT-Book-{book:02}' if level=='Chapter' else f'LOEB-{book:02}-Chapter-{chapter}-0')
 if level=='Chapter':
  following=next((n for n in rows[index+1:] if n['source']['division_level']=='Chapter' and n['source']['book']==book),None)
 else:
  following=next((n for n in rows[index+1:] if n['source']['division_level']=='Subchapter' and n['source']['book']==book and n['source']['chapter']==chapter),None)
  if not following and chapter is not None:following=next((n for n in rows[index+1:] if n['source']['division_level']=='Chapter' and n['source']['book']==book),None)
 item=E.SubElement(lst,T+'item',{XI:r['id'],'n':str(chapter if level=='Chapter' else s['subchapter']),'corresp':'#reconciliation-v1.1 #verification-v1.0'})
 E.SubElement(item,T+'label').text=level+' '+str(chapter if level=='Chapter' else s['subchapter'])
 fs=E.SubElement(item,T+'fs',type='traditional-boundary')
 fields={'scheme':level.lower(),'book':book,'context':context,'chapter':chapter,'subchapter':s['subchapter'] if level=='Subchapter' else None,'parent':parent,'display':chapter if level=='Chapter' else s['subchapter'],'literal-label':s['printed_label'],'raw-loeb-associated-niese':s['niese_section'],'canonical-niese':verification['recommended_niese_association'],'niese-original':verification['niese_original_printed_section'],'verification-status':verification['verification_status'],'confidence':s['confidence'],'physical-point':verification['physical_boundary_id'],'end':following['id'] if following else 'BOOK_END','lower1-status':audit['chapter_opening_lower1_status']}
 for k,val in fields.items():primitive(fs,k,val)
 for language in ['Greek','Latin','English']:
  f=E.SubElement(fs,T+'f',name=language);lfs=E.SubElement(f,T+'fs',type='text-locator')
  for k,val in locators[(r['id'],language)].items():primitive(lfs,k,val)
 note=E.SubElement(item,T+'note',type='source-evidence');E.SubElement(note,T+'p').text=json.dumps({'frozen_loeb':s,'independent_verification':audit,'human_physical_copy_checks':[c for c in v['human_physical_copy_checks'] if c['case']==verification['loeb_boundary_id']]},ensure_ascii=False,separators=(',',':'))
assert rng.validate(root),str(rng.error_log)
(ROOT/'assets/xml/antiquities/structure.xml').write_bytes(E.tostring(root,encoding='UTF-8',xml_declaration=True,pretty_print=True))
(REVIEW/'MARKERS.json').write_text(json.dumps(marker_log,indent=2),encoding='utf-8')
print(json.dumps({'registry_rows':len(rows),'markers':collections.Counter(m['file'].split('/')[3] for m in marker_log),'modified_xml':list(mutations),'tei_validation':'PASS'},indent=2))
