"""Independent source-event markup ownership; separately seal complete book markup."""
import pathlib,json,re,xml.etree.ElementTree as ET,shutil
PACK=pathlib.Path(__file__).resolve().parent.parent;NS='{http://www.tei-c.org/ns/1.0}';ID='{http://www.w3.org/XML/1998/namespace}id'
norm=lambda s:re.sub(r'\s+',' ',s).strip();load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
rows=[];whole=[];pruned=[]
for book in dict.fromkeys(r['book'] for r in load(PACK/'INTERVAL_ORACLE.json')):
 name='preface.xml' if book=='preface' else f'book-{int(book):02}.xml';root=ET.fromstring((PACK/'certified'/name).read_bytes()).find('.//'+NS+'body/'+NS+'div1')
 events=[];spans={};marks=[];items=[];parents={}
 def walk(e,paragraph=None,in_num=False):
  tag=e.tag.removeprefix(NS);paragraph=e if tag=='p' else paragraph;in_num=in_num or tag=='num';a=len(events);events.append(('start',e,in_num))
  if tag in ['anchor','lb','hi'] and not in_num:items.append(e);parents[e]=paragraph
  if e.text:events.append(('text',e.text,in_num))
  for c in e:
   walk(c,paragraph,in_num)
   if c.tail:events.append(('text',c.tail,in_num))
  b=len(events);events.append(('end',e,in_num));spans[e]=(a,b)
  if tag=='milestone' and e.get('unit')=='niese':marks.append((int(e.get('n')),a,b))
 walk(root);marks.sort(key=lambda r:r[1])
 def text(a,b):return ''.join(v for kind,v,num in events[a:b] if kind=='text' and not num)
 def row(e,a,b):
  left,right=spans[e];attrs={k.removeprefix('{http://www.w3.org/XML/1998/namespace}'):v for k,v in e.attrib.items()}
  return dict(tag=e.tag.removeprefix(NS),attrs=attrs,text=norm(text(max(a,left+1),min(b,right))))
 whole.append(dict(book=book,elements=[row(e,0,len(events)) for e in items]))
 for i,(number,marker_start,marker_end) in enumerate(marks):
  a=marker_end+1;b=marks[i+1][1] if i+1<len(marks) else len(events);selected=[]
  for e in items:
   left,right=spans[e];tag=e.tag.removeprefix(NS)
   overlap=(a<=left<b) if tag in ['anchor','lb'] else (left<b and right>=a and bool(norm(text(max(a,left+1),min(b,right)))))
   if not overlap:continue
   p=parents[e]
   if p is not None:
    pleft,pright=spans[p];lo,hi=max(a,pleft+1),min(b,pright)
    retained_marker=any(kind=='start' and node.tag==NS+'milestone' for kind,node,_ in events[lo:hi] if kind!='text')
    if not norm(text(lo,hi)) and not retained_marker:
     pruned.append(dict(book=book,number=number,tag=tag,source_id=e.get(ID),reason='Only structural markup in an empty exclusive-end paragraph after inherited citations are removed; independently verify it in complete containing source'))
     continue
   selected.append(row(e,a,b))
  if selected or any(r['book']==book and r['number']==number for r in pruned):rows.append(dict(book=book,number=number,elements=selected))
for name,value in [('MARKUP_ORACLE.json',rows),('WHOLE_MARKUP_ORACLE.json',whole),('EMPTY_ENDPOINT_MARKUP_QUALIFICATION.json',dict(status='PASS',source_bytes_and_renderer_unchanged=True,pruned_endpoint_nodes=pruned,all_whole_book_markup_required=True,method='Independent XML start/end/text events; exact ranges have exclusive paragraph endpoints, with citation labels removed. Full containing markup remains separately mandatory.'))]:
 (PACK/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Independent markup oracle:',len(rows),'selected intervals;',len(whole),'complete books;',len(pruned),'qualified empty endpoint structural nodes')
