from pathlib import Path
from lxml import etree as E
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
NS='http://www.tei-c.org/ns/1.0';N={'t':NS};XI='{http://www.w3.org/XML/1998/namespace}id'
def tag(x):return '{'+NS+'}'+x
def fs(parent,values,typ):
 e=E.SubElement(parent,tag('fs'),type=typ)
 for k,v in values.items():
  f=E.SubElement(e,tag('f'),name=k)
  if isinstance(v,dict):fs(f,v,'text-locator')
  else:E.SubElement(f,tag('string')).text=str(v)
 return e
registry=E.parse(str(ROOT/'assets/xml/antiquities/structure.xml'))
rows={i.get(XI):i for i in registry.xpath('//t:list[@type="traditional-boundaries"]/t:item',namespaces=N)}
record={'interpretation':'Authentic non-monotonic Bamberg-derived witness order; earlier proposed reordering withdrawn','scholarly_status_change':False,'XML_changes':False,'source_scholarship':'User-supplied Levenson and Martin (2016), p.330; publisher identifies chapter at https://onlinelibrary.wiley.com/doi/10.1002/9781118325162.ch21. Page 330 was not independently re-read.','languages':{},'affected_selections':{}}
for lang in ['Greek','Latin','English']:
 path=ROOT/f'assets/xml/antiquities/{lang}/book-11.xml';doc=E.parse(str(path))
 def loc(number,edge=None):
  pid=f'{lang.lower()}-book11-num{number}';p=doc.xpath(f'//t:p[@xml:id="{pid}"]',namespaces=N)[0]
  v={'available':'true','file':f'{lang}/book-11.xml','paragraph':pid,'target':pid,'kind':'element-edge' if edge else 'paragraph'}
  if edge:v['edge']=edge
  return v
 def span(a,b,label):return {'start':a,'end':b,'label':label}
 end={'available':'true','kind':'book-end'}
 split=loc(321,'num[7]') if lang=='Latin' else None
 if split:
  p=doc.xpath('//t:p[@xml:id="latin-book11-num321"]/t:num',namespaces=N)
  assert ''.join(p[6].itertext())=='[342b]'
 maps={
  'LOEB-11-Chapter-8-0':[
   span(loc(304),loc(326),'Antiquities 304–311 and Latin 312a, with Latin Bellum 4.105a'),
   span(loc(312),split or loc(343),'Antiquities 312(b)–326(a), with Latin Bellum 4.105b'),
   span(loc(326),loc(312),'Antiquities 326(b)–342(a)'),
   span(split or loc(343),end,'Antiquities 342b–347 (Latin) / 343–347 (Greek/English)')],
  'LOEB-11-Subchapter-8-2':[
   span(loc(306),loc(326),'Antiquities 306–311 and Latin 312a, with Latin Bellum 4.105a'),
   span(loc(312),loc(313),'Antiquities 312(b), with Latin Bellum 4.105b')],
  'LOEB-11-Subchapter-8-3':[span(loc(313),loc(321),'Antiquities 313–320')],
  'LOEB-11-Subchapter-8-4':[
   span(loc(321),split or loc(343),'Antiquities 321–326(a)'),
   span(loc(326),loc(329),'Antiquities 326(b)–328')],
  'LOEB-11-Subchapter-8-5':[span(loc(329),loc(340),'Antiquities 329–339')],
  'LOEB-11-Subchapter-8-6':[
   span(loc(340),loc(312),'Antiquities 340–342(a)'),
   span(split or loc(343),end,'Antiquities 342b–347 (Latin) / 343–347 (Greek/English)')]
 }
 if lang!='Latin':
  labels={
   'LOEB-11-Chapter-8-0':['Antiquities 304–311','Antiquities 312–325','Antiquities 326–342','Antiquities 343–347'],
   'LOEB-11-Subchapter-8-2':['Antiquities 306–311','Antiquities 312'],
   'LOEB-11-Subchapter-8-3':['Antiquities 313–320'],
   'LOEB-11-Subchapter-8-4':['Antiquities 321–325','Antiquities 326–328'],
   'LOEB-11-Subchapter-8-5':['Antiquities 329–339'],
   'LOEB-11-Subchapter-8-6':['Antiquities 340–342','Antiquities 343–347']}
  for rid,values in labels.items():
   for spanValue,label in zip(maps[rid],values):spanValue['label']=label
 record['languages'][lang]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'paragraph_order':[p.get(XI) for p in doc.xpath('//t:p[@xml:id]',namespaces=N)],'current_section_membership':[]}
 for p in doc.xpath('//t:p[@xml:id]',namespaces=N):
  nums=[''.join(n.itertext()) for n in p.findall('t:num',N)]
  if p.get(XI).split('num')[-1] in ['306','326','329','340','312','313','321','343','346']:
   record['languages'][lang]['current_section_membership'].append({'paragraph':p.get(XI),'literal_nums':nums})
 for rid,spans in maps.items():
  item=rows[rid];langfs=item.find(f't:fs/t:f[@name="{lang}"]/t:fs',N)
  for old in langfs.xpath('t:f[@name="spans" or @name="presentation-note"]',namespaces=N):langfs.remove(old)
  f=E.SubElement(langfs,tag('f'),name='spans');coll=E.SubElement(f,tag('vColl'),org='list')
  for v in spans:fs(coll,v,'physical-span')
  if len(spans)>1:
   f=E.SubElement(langfs,tag('f'),name='presentation-note');E.SubElement(f,tag('string')).text='This selection is assembled in canonical structural order from separated witness fragments. Book and Alignment unit views preserve the XML witness order. Latin Bellum 4.105 interpolations, where present, remain with their labelled source fragments; no witness text has been moved or omitted.'
  record['affected_selections'].setdefault(rid,{})[lang]=spans
 for rid in maps:
  for note in rows[rid].xpath('t:note[@type="witness-order-adjudication"]',namespaces=N):rows[rid].remove(note)
  note=E.SubElement(rows[rid],tag('note'),type='witness-order-adjudication')
  E.SubElement(note,tag('p')).text='The current-text overlay uses ordered physical spans. The canonical traditional identity and independent source judgment are unchanged. Bamberg-derived non-monotonic order is authentic witness evidence, not a corpus ordering defect. Split Arabic citation labels and Bellum 4.105 interpolations are retained literally in the current XML.'
rng=E.RelaxNG(E.parse(str(D/'tei_all.rng')));assert rng.validate(registry),str(rng.error_log)
registry.write(str(ROOT/'assets/xml/antiquities/structure.xml'),encoding='UTF-8',xml_declaration=True,pretty_print=True)
(D/'XI_MULTISPAN_MEMBERSHIP.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('TEI_VALID_MULTI_SPAN_DATA',len(record['affected_selections']),'identities / 18 language mappings; no corpus XML writes')
