from pathlib import Path
import xml.etree.ElementTree as ET,json,hashlib
I=Path('C:/workspace/LatinJosephus-antiquities-vii1-whiston-context-integration');T=Path('C:/workspace/Antiquities-VII1-Whiston-Integration-runtime-20261010');ns={'t':'http://www.tei-c.org/ns/1.0'};X='{http://www.w3.org/XML/1998/namespace}id';facts={}
for l in ['Latin','Greek','English']:
 b=(I/f'assets/xml/antiquities/{l}/book-07.xml').read_bytes();root=ET.fromstring(b);pars=[p for p in root.findall('.//t:p',ns) if p.get(X)];facts[l]={'sha256':hashlib.sha256(b).hexdigest(),'paragraphs':[{'id':p.get(X),'sameAs':p.get('sameAs'),'label':p.find('t:num',ns).text if p.find('t:num',ns) is not None else None,'text':' '.join(''.join(p.itertext()).split()),'Niese_milestones':[m.attrib for m in p.findall('t:milestone',ns)]} for p in pars[:(6 if l=='Greek' else 1)]]}
root=ET.parse(I/'assets/xml/antiquities/structure.xml').getroot()
def val(e):
 if e.tag.endswith('fs'):return {f.get('name'):val(next(iter(f))) for f in e}
 if e.tag.endswith('vColl'):return [val(c) for c in e]
 return ''.join(e.itertext())
records=[]
for item in root.findall('.//t:item',ns):
 fs=item.find('t:fs',ns)
 if fs is not None:
  d={'id':item.get(X),**val(fs)}
  if d.get('book')=='7' and d.get('chapter')=='1' and (d.get('scheme')=='chapter' or d.get('subchapter')=='1'):records.append(d)
facts['containing_records']=records;(T/'VII_2_6_SOURCE_FACTS.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2));print({l:[{k:p[k] for k in ['id','sameAs','label']} for p in facts[l]['paragraphs']] for l in ['Latin','Greek','English']});print([{k:r.get(k) for k in ['id','scheme','chapter','subchapter','canonical-niese','end']} for r in records])
