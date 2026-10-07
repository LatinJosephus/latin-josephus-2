from pathlib import Path
from lxml import etree as E
from xml.parsers import expat
import json,collections,hashlib,re
ROOT=Path(__file__).resolve().parents[2];REVIEW=Path(__file__).resolve().parent;AUTH=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review\Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06')
T='{http://www.tei-c.org/ns/1.0}';XI='{http://www.w3.org/XML/1998/namespace}id';NS={'t':T[1:-1]};OMIT={'num','milestone','pb','lb','note','anchor'}
source=json.loads((AUTH/'Antiquities_Structure_Reconciliation.json').read_bytes());rows=source['bamberg_boundaries'];baseline=json.loads((REVIEW/'BASELINE.json').read_bytes())
assert json.loads((REVIEW/'CURRENT_LOCATOR_GATE_QA.json').read_bytes())['result']=='PASS'
assert hashlib.sha256((ROOT/'assets/xml/antiquities/structure.xml').read_bytes()).hexdigest()==baseline['worktree']['assets/xml/antiquities/structure.xml']['sha256'],'Run only on clean base registry'
def project(e):
 if E.QName(e).localname in OMIT:return ''
 return (e.text or '')+''.join(project(c)+(c.tail or '') for c in e if isinstance(c.tag,str))
def fields(fs):return {f.get('name'):fields(f[0]) if E.QName(f[0]).localname=='fs' else [fields(x) for x in f[0]] if E.QName(f[0]).localname=='vColl' else f[0].text or '' for f in fs}
old_tree=E.parse(str(ROOT/'assets/xml/antiquities/structure.xml'))
trad={i.get(XI):fields(i.find('t:fs',NS)) for i in old_tree.xpath('//t:list[@type="traditional-boundaries"]/t:item',namespaces=NS)}
def primitive(p,k,v):
 f=E.SubElement(p,T+'f',name=k)
 if isinstance(v,dict):
  x=E.SubElement(f,T+'fs',type='text-locator')
  for key,value in v.items():primitive(x,key,value)
 else:E.SubElement(f,T+'string').text='' if v is None else str(v)
 return f
for rel,v in baseline['worktree'].items():
 if rel.startswith('assets/xml/antiquities/'):
  assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==v['sha256'],('Compiler requires exact baseline XML',rel)
parsed={};locators={};edits={};newpoints={};marker_log=[];mapping=[]
def stable_edge(node):
 steps=[];e=node
 while not e.get(XI):
  parent=e.getparent();assert parent is not None
  name=E.QName(e).localname;index=list(parent.findall(T+name)).index(e)+1;steps.insert(0,f'{name}[{index}]');e=parent
 return {'available':'true','kind':'element-edge','target':e.get(XI),'edge':'/'.join(steps)} if steps else {'available':'true','kind':'anchor' if E.QName(e).localname=='anchor' else 'element-edge','target':e.get(XI),'edge':''}
for r in rows:
 for lang in ['Greek','Latin','English']:
  frozen=r[lang.lower()+'_location'];file=f'assets/xml/antiquities/{lang}/book-{r["book"]:02}.xml'
  if file not in parsed:parsed[file]=E.parse(str(ROOT/file))
  doc=parsed[file];pid=frozen['paragraph_id'];off=frozen['offset']
  if pid.startswith('UNIDENTIFIED:'):
   path='/'+ '/'.join('t:'+step for step in frozen['path'].split('/')[1:]);p=doc.xpath(path,namespaces=NS)[0]
  else:p=doc.xpath('//*[@xml:id=$i]',i=pid)[0]
  text=project(p);assert re.sub(r'\s+',' ',text[off:].strip()).startswith(re.sub(r'\s+',' ',frozen['anchor'].strip()))
  out={'available':'true','file':file.removeprefix('assets/xml/antiquities/'),'paragraph':p.get(XI) or '', 'offset':str(off),'anchor':frozen['anchor']}
  matched=[(ident,v[lang]) for ident,v in trad.items() if v[lang].get('available')=='true' and v[lang].get('file')==out['file'] and v[lang].get('paragraph')==p.get(XI) and int(v[lang].get('offset',-1))==off]
  if matched and p.get(XI):
   # Reuse the existing certified location, preserving source-specific textual anchor separately.
   choices=[x for x in matched if x[0] in r.get('loeb_exact_ids',[])];chosen=(choices or matched)[0]
   oldloc=chosen[1];out.update({k:oldloc[k] for k in ['kind','target','edge','boundary-start'] if k in oldloc})
   action='REUSED_CERTIFIED_TRADITIONAL_POINT'
  elif off==0:
   if p.get(XI):out.update(kind='paragraph',target=p.get(XI))
   else:out.update(stable_edge(p))
   action='EXISTING_PARAGRAPH_EDGE'
  else:
   cursor=[0];candidates=[]
   def walk(e):
    if e is not p and cursor[0]==off:candidates.append(e)
    if E.QName(e).localname in OMIT:return
    cursor[0]+=len(e.text or '')
    for c in e:walk(c);cursor[0]+=len(c.tail or '')
   walk(p)
   # An already represented element edge is exact only if it has this certified text-projection coordinate.
   if candidates:
    exact=candidates[0]
    out.update(stable_edge(exact))
    if exact.get(XI) and E.QName(exact).localname not in ['anchor']:
     # Select before a directly identified inline element, using its containing stable edge.
     parent=exact.getparent();tag=E.QName(exact).localname;out.update(stable_edge(parent));out['kind']='element-edge';out['edge']=(out.get('edge','')+'/' if out.get('edge') else '')+f'{tag}[{list(parent.findall(T+tag)).index(exact)+1}]'
    action='EXISTING_INLINE_ELEMENT_EDGE'
   else:
    pk=(file,doc.getpath(p),off)
    if pk not in newpoints:
     marker='b78-'+lang.lower()+'-'+r['id'];newpoints[pk]=marker;edits.setdefault(file,[]).append({'path':doc.getpath(p),'pid':p.get(XI),'offset':off,'marker':marker,'record':r['id']})
    out.update(kind='anchor',target=newpoints[pk]);action='NEW_EMPTY_ANCHOR'
  locators[(r['id'],lang)]=out
  mapping.append({'id':r['id'],'book':r['book'],'language':lang,'frozen_location':frozen,'locator':out,'handling':action})
# Confirm frozen physical source order independently of all label arithmetic.
ordering=[]
for book in range(1,21):
 bs=[r for r in rows if r['book']==book]
 for lang in ['Greek','Latin','English']:
  if not bs:continue
  file=f'assets/xml/antiquities/{lang}/book-{book:02}.xml';doc=parsed[file];p_order={doc.getpath(p):i for i,p in enumerate(doc.xpath('//t:p',namespaces=NS))};points=[]
  for r in bs:
   f=r[lang.lower()+'_location'];pid=f['paragraph_id'];p=doc.xpath('/'+'/'.join('t:'+s for s in f['path'].split('/')[1:]),namespaces=NS)[0] if pid.startswith('UNIDENTIFIED:') else doc.xpath('//*[@xml:id=$i]',i=pid)[0]
   points.append((p_order[doc.getpath(p)],f['offset']))
  assert all(a<b for a,b in zip(points,points[1:])),(book,lang,points)
  ordering.append({'book':book,'language':lang,'source_order':'STRICTLY_INCREASING','starts':len(bs)})
# Locate byte insertions for identified and unidentified paragraphs without reserialization.
for file,insertions in edits.items():
 raw=(ROOT/file).read_bytes();parser=expat.ParserCreate(namespace_separator='}');stack=[];counter=[];current=None;segments={};counts={}
 def start(name,attrs):
  global current
  local=name.split('}')[-1]
  if counter:counter[-1][local]=counter[-1].get(local,0)+1;idx=counter[-1][local]
  else:idx=1
  stack.append((local,idx));counter.append({})
  if local=='p':
   current='/'+ '/'.join(f'{{{T[1:-1]}}}{n}[{i}]' for n,i in stack);segments[current]=[];counts[current]=0
 def end(name):
  global current
  if stack[-1][0]=='p':current=None
  stack.pop();counter.pop()
 def text(value):
  if current and not any(n in OMIT for n,i in stack):segments[current].append((counts[current],parser.CurrentByteIndex,value));counts[current]+=len(value)
 parser.StartElementHandler=start;parser.EndElementHandler=end;parser.CharacterDataHandler=text;parser.Parse(raw,True)
 def key_path(xpath):
  # lxml uses default namespace wildcards in getpath; paragraph identity is resolved against the exact parsed element.
  doc=parsed[file];p=doc.xpath(xpath,namespaces=doc.getroot().nsmap if None not in doc.getroot().nsmap else {})[0]
  parts=[]
  for e in reversed([p,*p.iterancestors()]):
   tag=E.QName(e).localname;par=e.getparent();idx=list(par.findall(T+tag)).index(e)+1 if par is not None else 1;parts.append(f'{{{T[1:-1]}}}{tag}[{idx}]')
  return '/'+ '/'.join(parts)
 changes=[]
 for edit in insertions:
  ss=segments[key_path(edit['path'])];off=edit['offset'];poss=[x for x in ss if x[0]<=off<x[0]+len(x[2])];assert len(poss)==1,(file,edit,poss)
  begin,byte,value=poss[0];delta=off-begin;position=byte+len(value[:delta].encode());assert raw[position:].startswith(value[delta:delta+1].encode())
  tag=f'<anchor xml:id="{edit["marker"]}" type="bamberg-boundary" corresp="../structure.xml#{edit["record"]}"/>'.encode()
  changes.append((position,tag));marker_log.append({'file':file,'language':file.split('/')[3],'record':edit['record'],'xml_id':edit['marker'],'paragraph':edit['pid'],'offset':off,'byte_position_before':position,'markup':tag.decode()})
 for pos,tag in sorted(changes,reverse=True):raw=raw[:pos]+tag+raw[pos:]
 E.fromstring(raw);(ROOT/file).write_bytes(raw)
# Add a TEI list without rewriting a byte of the pre-existing registry content.
newlist=E.Element(T+'list',type='bamberg-boundaries',nsmap={None:T[1:-1]});E.SubElement(newlist,T+'head').text='Bamberg, Staatsbibliothek, Msc.Class.78: independent manuscript divisions'
counts=collections.Counter((r['book'],r['bamberg_chapter']) for r in rows)
for r in rows:
 bs=[x for x in rows if x['book']==r['book']];index=bs.index(r);following=bs[index+1] if index+1<len(bs) else None;label=r['bamberg_chapter'];absent=label.startswith('None:');supplied=label.startswith('[');uncertain=r['audit_identifier_uncertain'] or '?' in label
 display='unnumbered' if absent else label
 if counts[(r['book'],label)]>1:
  incipit=r.get('certified_start') or r.get('snippet','');display+=' — '+' '.join(incipit.split()[:7]);assert incipit
 item=E.SubElement(newlist,T+'item',{XI:r['id'],'corresp':'#reconciliation-v1.1'});E.SubElement(item,T+'label').text='Bamberg division '+display;fs=E.SubElement(item,T+'fs',type='bamberg-boundary')
 values={'scheme':'bamberg','book':r['book'],'context':str(r['book']),'source-record':r['id'],'source-order':index+1,'display':display,'manuscript-label-as-recorded':label,'literal-label':'' if absent else label,'label-status':'ABSENT' if absent else 'SUPPLIED_UNCERTAIN' if supplied and uncertain else 'SUPPLIED' if supplied else 'UNCERTAIN' if uncertain else 'LITERAL','canonical-niese':r['niese_section'],'niese-relationship':r['niese_relationship'],'at-niese-start':str(r['boundary_at_niese_start']).lower(),'confidence':r['confidence'],'verification-status':r['physical_position_status'],'physical-point':r['id'],'image':r['image'],'manuscript-image-column-line':r.get('human_exact_position_check',{}).get('fields_verbatim',{}).get('Image/column/line'),'visible-numeral-or-initial':r.get('human_exact_position_check',{}).get('fields_verbatim',{}).get('Visible numeral/initial and its position'),'certified-latin-incipit':r.get('certified_start') or r['latin_location']['anchor'],'traditional-relationship':r['chapter_relationship'],'traditional-exact-identities':' '.join(r.get('loeb_exact_ids',[])),'traditional-different-position-identities':' '.join(r.get('loeb_different_position_ids',[])),'end':following['id'] if following else 'BOOK_END'}
 for k,v in values.items():primitive(fs,k,v)
 for lang in ['Greek','Latin','English']:primitive(fs,lang,locators[(r['id'],lang)])
 note=E.SubElement(item,T+'note',type='frozen-bamberg-evidence');E.SubElement(note,T+'p').text=json.dumps(r,ensure_ascii=False,separators=(',',':'))
coverage=E.Element(T+'list',type='bamberg-coverage',nsmap={None:T[1:-1]})
for book in range(1,21):
 count=sum(r['book']==book for r in rows);i=E.SubElement(coverage,T+'item',{XI:f'B78-coverage-book{book:02}'});fs=E.SubElement(i,T+'fs',type='audited-coverage')
 for k,v in {'book':book,'division-count':count,'evidence-status':'AUDITED_NO_CHAPTER_MARKS' if count==0 else 'AUDITED_DIVISIONS_PRESENT','source':'reconciliation-v1.1'}.items():primitive(fs,k,v)
raw=(ROOT/'assets/xml/antiquities/structure.xml').read_bytes();E.indent(newlist,space='  ',level=3);E.indent(coverage,space='  ',level=3);addition=b'      '+E.tostring(newlist,encoding='UTF-8')+b'\n      '+E.tostring(coverage,encoding='UTF-8')+b'\n';assert raw.count(b'</body>')==1;raw=raw.replace(b'</body>',b'\n'+addition+b'</body>',1);tree=E.fromstring(raw)
rng=E.RelaxNG(E.parse(str(ROOT/'review/Antiquities_Traditional_Navigation_2026-10-06/tei_all.rng')));assert rng.validate(tree),str(rng.error_log)
assert len(tree.xpath('//t:list[@type="bamberg-boundaries"]/t:item',namespaces=NS))==198
(ROOT/'assets/xml/antiquities/structure.xml').write_bytes(raw)
(REVIEW/'MARKERS.json').write_bytes(json.dumps(marker_log,ensure_ascii=False,indent=2).encode());(REVIEW/'BAMBERG_BOUNDARY_QA.json').write_bytes(json.dumps({'mappings':mapping,'source_order':ordering,'new_anchor_counts':dict(collections.Counter(m['language'] for m in marker_log)),'TEI_valid':'PASS','result':'PASS'},ensure_ascii=False,indent=2).encode())
print(json.dumps({'rows':len(rows),'anchor_counts':dict(collections.Counter(m['language'] for m in marker_log)),'modified_XML_files':list(edits),'source_order':'PASS','TEI_valid':'PASS'}))