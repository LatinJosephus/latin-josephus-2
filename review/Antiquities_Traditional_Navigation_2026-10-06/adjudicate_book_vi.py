from pathlib import Path
from lxml import etree as E
import subprocess,hashlib,json
ROOT=Path(__file__).resolve().parents[2];REVIEW=Path(__file__).resolve().parent
BASE='f7d9142cad998e8a005adea1a22532b9a78592db';NS='http://www.tei-c.org/ns/1.0';T='{'+NS+'}';XI='{http://www.w3.org/XML/1998/namespace}id';ns={'t':NS}
registry=E.parse(str(ROOT/'assets/xml/antiquities/structure.xml'))
evidence={};replacement={}
def projection(e):
 if E.QName(e).localname in ['num','milestone','pb','lb','note','anchor']:return ''
 return (e.text or '')+''.join(projection(ch)+(ch.tail or '') for ch in e)
for language in ['Latin','English','Greek']:
 file=f'assets/xml/antiquities/{language}/book-06.xml';raw=subprocess.check_output(['git','--no-optional-locks','show',BASE+':'+file],cwd=ROOT);xml=E.fromstring(raw)
 ps={e.get(XI):e for e in xml.xpath('//t:p[@xml:id]',namespaces=ns)}
 assert len(ps)==len(xml.xpath('//t:p[@xml:id]',namespaces=ns))
 evidence[language]={'file':file,'base_blob_sha256':hashlib.sha256(raw).hexdigest(),'paragraphs':{}}
 for pid in [language.lower()+'-book06-num271',language.lower()+'-book06-num272']:
  p=ps[pid];evidence[language]['paragraphs'][pid]={'sameAs':p.get('sameAs'),'inherited_num':p.find('t:num',ns).text,'text_anchor':' '.join(projection(p).split())[:160]}
 if language=='Greek':continue
 first=ps[language.lower()+'-book06-num271'];second=ps[language.lower()+'-book06-num272'];assert first.sourceline<second.sourceline
 if language=='Latin':
  for p,n,anchor in [(first,'269','Abiathar itaque abimelech'),(second,'271','Eo siquidem tempore')]:
   ms=p.xpath('./t:milestone[@unit="niese" and @n=$n]',namespaces=ns,n=n);assert len(ms)==1 and ms[0].tail.startswith(anchor)
   assert p.findall(T+'milestone').index(ms[0])==0
  evidence[language]['milestones']=[{'n':'269','paragraph':first.get(XI),'edge':'milestone[1]','offset':1},{'n':'271','paragraph':second.get(XI),'edge':'milestone[1]','offset':1}]
 else:
  assert ' '.join(projection(first).split()).startswith('But Abiathar, the son of Ahimelech')
  assert ' '.join(projection(second).split()).startswith('About this time it was that David heard')
  assert first.get('sameAs')=='#latin-book06-num271' and second.get('sameAs')=='#latin-book06-num272'
 replacement[language]={'available':'true','file':f'{language}/book-06.xml','paragraph':second.get(XI),'offset':'1' if language=='Latin' else '0','anchor':' '.join(projection(second).split())[:120],'kind':'element-edge' if language=='Latin' else 'paragraph','target':second.get(XI)}
 if language=='Latin':replacement[language]['edge']='milestone[1]'
corrections=[]
for ident in ['LOEB-06-Chapter-13-0','LOEB-06-Subchapter-13-1']:
 item=registry.xpath('//t:item[@xml:id=$i]',namespaces=ns,i=ident)[0]
 for language in ['Latin','English']:
  fs=item.xpath('./t:fs/t:f[@name=$n]/t:fs',namespaces=ns,n=language)[0];old={f.get('name'):f[0].text for f in fs}
  assert old['paragraph']==language.lower()+'-book06-num271',old
  record={'identity':ident,'language':language,'frozen_v1_1_locator':old,'verified_current_locator':replacement[language],'base_commit':BASE,'base_blob_sha256':evidence[language]['base_blob_sha256'],'authority':'CURRENT_BASE_XML_ADJUDICATION','source_primary_status_changed':False}
  corrections.append(record)
  for child in list(fs):fs.remove(child)
  for key,val in replacement[language].items():E.SubElement(E.SubElement(fs,T+'f',name=key),T+'string').text=val
  note=E.SubElement(item,T+'note',type='current-locator-adjudication');E.SubElement(note,T+'p').text=json.dumps(record,ensure_ascii=False,separators=(',',':'))
rng=E.RelaxNG(E.parse(str(REVIEW/'tei_all.rng')));assert rng.validate(registry),str(rng.error_log)
(ROOT/'assets/xml/antiquities/structure.xml').write_bytes(E.tostring(registry,encoding='UTF-8',xml_declaration=True,pretty_print=True))
(REVIEW/'VI_locator_corrections.json').write_text(json.dumps({'evidence':evidence,'corrections':corrections,'primary_statuses_unchanged':True,'alignment_repair_applied':False},ensure_ascii=False,indent=2),encoding='utf-8')
print('Four implementation locator fields corrected; TEI validation PASS; source judgments and XML unchanged.')
