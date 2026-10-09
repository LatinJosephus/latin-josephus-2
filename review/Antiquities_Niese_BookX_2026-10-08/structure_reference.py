"""Inventory canonical book-specific structural locators, never derive Niese starts."""
import argparse,json,hashlib,collections
from pathlib import Path
from lxml import etree
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--packet',type=Path,required=True);a=ap.parse_args();p=a.packet;d=json.loads((p/'BASELINE.json').read_text(encoding='utf-8'));b=d['book'];assert b in [8,10]
source=a.repo/'assets/xml/antiquities/structure.xml';raw=source.read_bytes();ns={'t':'http://www.tei-c.org/ns/1.0'};root=etree.fromstring(raw)
def features(fs):
 out={}
 for f in fs.findall('t:f',ns):
  nested=f.find('t:fs',ns)
  if nested is not None:value=dict(type=nested.get('type'),features=features(nested))
  else:value=''.join(f.itertext()).strip()
  key=f.get('name')
  if key in out:
   if not isinstance(out[key],list):out[key]=[out[key]]
   out[key].append(value)
  else:out[key]=value
 return out
rows=[]
for fs in root.xpath('//t:fs[t:f[@name="book"]/t:string=$book]',namespaces=ns,book=str(b)):
 el=fs.getparent();rows.append(dict(id=fs.get('{http://www.w3.org/XML/1998/namespace}id') or el.get('{http://www.w3.org/XML/1998/namespace}id'),type=fs.get('type'),features=features(fs)))
out=dict(book=b,source='assets/xml/antiquities/structure.xml',source_sha256=hashlib.sha256(raw).hexdigest(),role='Independent canonical structural inventory only; not an input to audit_book.py and not authority to manufacture a Niese start.',counts=dict(collections.Counter(r['type'] for r in rows)),rows=rows)
(p/'STRUCTURE_REFERENCE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Canonical structural reference',b,out['counts'])
