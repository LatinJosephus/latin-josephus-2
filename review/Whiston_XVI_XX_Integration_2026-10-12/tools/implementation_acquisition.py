import pathlib,json,hashlib,sys,re,xml.etree.ElementTree as ET,shutil
BASE=pathlib.Path(__file__).parent;ROOT=BASE/'candidate';PACK=ROOT/'review/Whiston_XVI_XX_Integration_2026-10-12'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
last={'A':17,'B':19,'C':20}[sys.argv[1]]
if last>17:assert (BASE/'exports/Stage-A.offline-recovery.json').exists(),'Restored Stage A required'
if last>19:assert (BASE/'exports/Stage-B.offline-recovery.json').exists(),'Restored Stage B required'
records=load(PACK/'SOURCE_INVENTORY.json');manifest=load(ROOT/'_docs/reader-corpus-integrity.json');base=load(PACK/'BASELINE.json')
for r in records:
 if r['book']>last:continue
 data=(PACK/'certified'/f'book-{r["book"]:02}.xml').read_bytes();assert sha(data)==r['certified_sha256'];(ROOT/r['file']).write_bytes(data)
 if r['file'] not in manifest['certified_whiston_paths']:manifest['certified_whiston_paths'].append(r['file'])
 previous=manifest['files'][r['file']]
 manifest['files'][r['file']]={**previous,'git_sha256':sha(data),'authority_commit':r['delivery_commit'],'allowed_worktree_sha256':[sha(data)],'certified_archive_sha256':r['archive_sha256'],'independent_corpus_certification':'WHISTON-ANTIQUITIES-CORPUS-CERTIFIED'}
manifest['integration_baseline_commit']=base['commit'];save(ROOT/'_docs/reader-corpus-integrity.json',manifest)
guard=ROOT/'bin/reader-corpus-integrity.mjs';text=guard.read_text(encoding='utf-8');text=re.sub(r"const manifestSHA = '[a-f0-9]{64}';",f"const manifestSHA = '{sha((ROOT/'_docs/reader-corpus-integrity.json').read_bytes())}';",text);guard.write_text(text,encoding='utf-8',newline='')
renderer=ROOT/'assets/js/renderTei.js';text=renderer.read_text(encoding='utf-8');enabled='["preface", '+', '.join(str(n) for n in range(1,last+1))+']';text,count=re.subn(r'exactNieseBooks: \[[^\]]+\]',f'exactNieseBooks: {enabled}',text,count=1);assert count==1 and 'Whiston English: exact Niese interval.' not in text;renderer.write_text(text,encoding='utf-8',newline='')
attrs=ROOT/'.gitattributes';text=attrs.read_text(encoding='utf-8');text=re.sub(r'\n# Preserve certified Whiston XVI.*', '',text,flags=re.S);text+='\n# Preserve certified Whiston XVI–XX XML bytes during Git checkout.\n'+''.join(f'/assets/xml/antiquities/English/book-{n:02}.xml -text whitespace=cr-at-eol,-blank-at-eol,-blank-at-eof\n' for n in range(16,last+1));attrs.write_text(text,encoding='utf-8',newline='')
availability=[]
for n in range(16,last+1):
 registry=load(ROOT/f'assets/xml/antiquities/niese/book-{n:02}.json');false=[r['number'] for r in registry['sections'] if r.get('English',{}).get('available') is False];assert not false,(n,false)
 availability.append(dict(book=n,identities=len(registry['sections']),English_false=false,registry_unchanged=True))
save(PACK/'AVAILABILITY_QA.json',availability)
NS='{http://www.tei-c.org/ns/1.0}';norm=lambda s:re.sub(r'\s+',' ',s).strip();oracle=[];whole={};markup=[]
for b in ['preface']+list(range(1,last+1)):
 filename='preface.xml' if b=='preface' else f'book-{b:02}.xml';f=PACK/'certified'/filename
 if isinstance(b,int) and b>=16:assert sha(f.read_bytes())==next(r['certified_sha256'] for r in records if r['book']==b)
 else:f=BASE/'baseline/assets/xml/antiquities/English'/filename
 root=ET.fromstring(f.read_bytes());div=root.find('.//'+NS+'body/'+NS+'div1');parts=[];position=0;marks=[];notes=[];inline=[];current=None;element_rows={}
 def emit(s,stack):
  global position
  if not s:return
  start=position;parts.append(s);position+=len(s)
  for tag,attrs in stack:
   if tag in ['hi','q','foreign','emph','title','ref','name','seg']:inline.append(dict(start=start,end=position,tag=tag,attrs=attrs,text=s))
 def walk(e,stack=()):
  global current
  tag=e.tag.removeprefix(NS)
  if tag=='milestone' and e.get('unit')=='niese':marks.append((int(e.get('n')),position));current=int(e.get('n'));return
  if tag=='num':return
  if tag=='note':notes.append(dict(offset=position,text=norm(''.join(e.itertext())),attrs=dict(e.attrib)));return
  attrs={k.removeprefix('{http://www.w3.org/XML/1998/namespace}'):v for k,v in e.attrib.items()}
  if current is not None and tag in ['anchor','lb','hi']:element_rows.setdefault(current,[]).append(dict(tag=tag,attrs=attrs,text=norm(''.join(e.itertext()))))
  stack=stack+((tag,attrs),);emit(e.text,stack)
  for child in e:walk(child,stack);emit(child.tail,stack)
 walk(div);alltext=''.join(parts)
 for i,(number,start) in enumerate(marks):
  end=marks[i+1][1] if i+1<len(marks) else len(alltext);value=norm(alltext[start:end]);ips=[]
  for item in inline:
   l,r=max(start,item['start']),min(end,item['end'])
   if l<r and norm(alltext[l:r]):ips.append(dict(tag=item['tag'],attrs=item['attrs'],text=norm(alltext[l:r])))
  oracle.append(dict(book=str(b),number=number,nextPhysical=marks[i+1][0] if i+1<len(marks) else None,text=value,rawText=alltext[start:end],sha256=sha(value.encode()),opening=value[:100],closing=value[-100:],notes=[note for note in notes if start<=note['offset']<end],inline=ips))
 markup += [dict(book=str(b),number=n,elements=es) for n,es in element_rows.items()]
 def wholetext(e):return '' if e.tag.removeprefix(NS) in ['num','note','milestone'] else (e.text or '')+''.join(wholetext(c)+(c.tail or '') for c in e)
 whole[str(b)]=norm(wholetext(root))
prior={(r['book'],r['number']):r for r in load(PACK/'PRIOR_INTERVAL_ORACLE.json')}
for r in oracle:
 if (r['book'],r['number']) in prior:assert r['text']==prior[r['book'],r['number']]['text'],(r['book'],r['number'],'prior oracle changed')
save(PACK/'INTERVAL_ORACLE.json',oracle);save(PACK/'MARKUP_ORACLE.json',markup)
def value(e):
 if e.tag==NS+'fs':return {f.get('name'):value(f[0]) for f in e}
 if e.tag==NS+'vColl':return [value(c) for c in e]
 return e.text or ''
rows=[]
for e in next(e for e in ET.parse(ROOT/'assets/xml/antiquities/structure.xml').iter(NS+'list') if e.get('type')=='traditional-boundaries'):
 if e.tag==NS+'item':
  r={'id':e.get('{http://www.w3.org/XML/1998/namespace}id'),**value(e.find(NS+'fs'))}
  if int(r.get('book','0'))<=last:rows.append(r)
save(PACK/'CONTAINING_ORACLE.json',dict(whole=whole,rows=rows))
shutil.copy2(__file__,PACK/'tools/implementation_acquisition.py')
print('Stage',sys.argv[1],'enabled through',last,'independent oracle intervals',len(oracle),'traditional rows',len(rows),'no generic renderer/registry changes')
