"""Read-only Unicode / XML-byte mapping. Narrative = body chapter p mixed text,
excluding num, note, and apparatus descendants; paragraph whitespace is preserved.
Offsets are zero-based Python Unicode code points; XML byte ranges are half-open.
"""
import hashlib,re
from xml.parsers import expat
from lxml import etree
NS={'t':'http://www.tei-c.org/ns/1.0'}
XMLID='{http://www.w3.org/XML/1998/namespace}id'
def digest(b):return hashlib.sha256(b).hexdigest()
def raw_char_positions(raw,start,text):
 positions=[];i=start;decoded=''
 while len(decoded)<len(text):
  pos=i
  if raw[i:i+1]==b'&':
   end=raw.index(b';',i)+1;token=raw[i:end].decode()
   if token.startswith('&#x'):c=chr(int(token[3:-1],16))
   elif token.startswith('&#'):c=chr(int(token[2:-1]))
   else:c={'&amp;':'&','&lt;':'<','&gt;':'>','&quot;':'"','&apos;':"'"}[token]
   i=end
  elif raw[i:i+2]==b'\r\n':c='\n';i+=2
  elif raw[i:i+1]==b'\r':c='\n';i+=1
  else:
   j=i+1
   while j<len(raw) and raw[j]&0xc0==0x80:j+=1
   c=raw[i:j].decode('utf-8');i=j
  decoded+=c;positions.append(pos)
 assert decoded==text,(decoded,text,start)
 return positions
class Book:
 def __init__(self,path=None,raw=None):
  self.raw=raw if raw is not None else path.read_bytes()
  self.tree=etree.fromstring(self.raw);self.units=[];self.nodes=[];self.labels=[];self.stream='';self.excluded=[]
  pnodes=self.tree.xpath('//t:body//t:div2/t:p',namespaces=NS)
  stack=[];counts=[{}];cur=None;last_closed=None;parser=expat.ParserCreate()
  def start(name,attrs):
   nonlocal cur,last_closed
   tag=name.split(':')[-1];counts[-1][tag]=counts[-1].get(tag,0)+1
   path=(stack[-1]['path'] if stack else '')+'/'+tag+'['+str(counts[-1][tag])+']'
   node=dict(tag=tag,path=path,attrs=attrs,start=parser.CurrentByteIndex,child=False)
   if stack:stack[-1]['child']=True
   stack.append(node);counts.append({});last_closed=None
   if tag=='p' and any(s['tag']=='body' for s in stack) and any(s['tag']=='div2' for s in stack):
    el=pnodes[len(self.units)];reason='chapter-0 paratext' if any(s['tag']=='div2' and s['attrs'].get('n')=='0' for s in stack) else ('English editorial omission placeholder' if 'Omitted in Bamberg MS' in ''.join(el.itertext()) else '')
    cur=dict(index=len(self.units)+1,id=attrs.get('xml:id',''),xpath=self.tree.getroottree().getpath(el),raw_start=parser.CurrentByteIndex,text='',nodes=[],element=el,book_start=len(self.stream),excluded_reason=reason);self.units.append(cur)
    if reason:self.excluded.append(dict(id=cur['id'],reason=reason,text=''.join(el.itertext())))
   if tag=='num' and cur:
    self.labels.append(dict(unit=cur['index'],id=cur['id'],book_offset=len(self.stream),unit_offset=len(cur['text']),raw_start=parser.CurrentByteIndex,text='',path=path))
  def end(name):
   nonlocal cur,last_closed
   node=stack.pop();counts.pop();node['end']=parser.CurrentByteIndex
   if node['tag']=='p' and cur:
    endpos=parser.CurrentByteIndex
    cur['raw_end']=endpos if self.raw[endpos:endpos+2]!=b'</' else self.raw.index(b'>',endpos)+1
    cur['raw_hash']=digest(self.raw[cur['raw_start']:cur['raw_end']]);cur['parsed_hash']=digest(etree.tostring(cur['element'],encoding='utf-8',with_tail=False));cur=None
   last_closed=node
  def data(t):
   if not cur:return
   if any(s['tag']=='num' for s in stack):self.labels[-1]['text']+=t;return
   if cur['excluded_reason'] or any(s['tag'] in {'note','app','rdg'} for s in stack):return
   parent=stack[-1]
   if last_closed is not None and last_closed['path'].startswith(parent['path']+'/'):
    path=last_closed['path']+'/tail()'
   else:path=parent['path']+'/text()'
   pos=raw_char_positions(self.raw,parser.CurrentByteIndex,t)
   if cur['nodes'] and cur['nodes'][-1]['path']==path:
    n=cur['nodes'][-1];n['text']+=t;n['raw_positions']+=pos
   else:
    n=dict(path=path,text=t,raw_positions=pos,unit_start=len(cur['text']),book_start=len(self.stream),unit=cur['index']);cur['nodes'].append(n);self.nodes.append(n)
   cur['text']+=t;self.stream+=t
  parser.StartElementHandler=start;parser.EndElementHandler=end;parser.CharacterDataHandler=data
  def comment(t):
   nonlocal last_closed
   if not stack:return
   counts[-1]['comment()']=counts[-1].get('comment()',0)+1
   stack[-1]['child']=True
   last_closed=dict(path=stack[-1]['path']+'/comment()['+str(counts[-1]['comment()'])+']')
  parser.CommentHandler=comment
  parser.Parse(self.raw,True)
  for u in self.units:
   lxmltext=''.join(u['element'].xpath('.//text()[not(ancestor::t:num) and not(ancestor::t:note) and not(ancestor::t:app) and not(ancestor::t:rdg)]',namespaces=NS))
   assert u['text']==('' if u['excluded_reason'] else lxmltext),(u['id'],u['text'],lxmltext)
 def locate(self,offset):
  n=next(n for n in self.nodes if n['book_start']<=offset<n['book_start']+len(n['text']))
  u=self.units[n['unit']-1];k=offset-n['book_start']
  return dict(stable_id=u['id'],paragraph=u['index'],xpath=u['xpath'],text_node_path=n['path'],node_offset=k,unit_offset=n['unit_start']+k,book_offset=offset,raw_byte=n['raw_positions'][k],left=self.stream[max(0,offset-130):offset],right=self.stream[offset:offset+240],parsed_unit_sha256=u['parsed_hash'],raw_unit_sha256=u['raw_hash'])
 def first_content(self,offset):
  while offset<len(self.stream) and self.stream[offset].isspace():offset+=1
  return offset
def fixtures():
 raw=b'<?xml version="1.0"?><TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div2><p xml:id="x">A &amp; B &#x3b1; <add>C</add>D<!--comment-->K<pb/>E<del>F</del>G<num>[1]</num>H\r\nI</p><p>J</p></div2></body></text></TEI>'
 b=Book(raw=raw);assert b.stream=='A & B \u03b1 CDKEFGH\nIJ'
 for i,c in enumerate(b.stream):
  loc=b.locate(i);k=loc['raw_byte'];assert raw_char_positions(raw,k,c)==[k]
 assert '/add[1]/text()' in b.locate(b.stream.index('C'))['text_node_path']
 assert '/add[1]/tail()' in b.locate(b.stream.index('D'))['text_node_path']
 assert '/pb[1]/tail()' in b.locate(b.stream.index('E'))['text_node_path']
 assert '/comment()[1]/tail()' in b.locate(b.stream.index('K'))['text_node_path']
 b2=Book(raw=b'<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div2><p>A<note>not narrative</note>B<add><del>C</del>D</add>E<num>[2]</num>F&amp;G&#169;H</p></div2></body></text></TEI>')
 assert b2.stream=='ABCDEF&G\u00a9H'
 assert '/note[1]/tail()' in b2.locate(1)['text_node_path']
 assert '/add[1]/tail()' in b2.locate(4)['text_node_path']
 b3=Book(raw=b'<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div2 n="0"><p>Title</p></div2><div2 n="1"><p><num>[1]</num>A</p><p><num>[2]</num>Omitted in Bamberg MS</p><p>B</p></div2></body></text></TEI>')
 assert b3.stream=='AB' and len(b3.excluded)==2
 return dict(status='PASS',tests=['mixed .text/.tail','UTF-8','numeric and named entities','CRLF','comment exclusion and tail coordinates','empty element tails','nested add/del retained','num excluded with tail retained','two units','raw Unicode-byte roundtrip','note excluded with tail retained','nested-child tail ownership','chapter-0 paratext exclusion','omission-placeholder exclusion'])
if __name__=='__main__':print(fixtures())
