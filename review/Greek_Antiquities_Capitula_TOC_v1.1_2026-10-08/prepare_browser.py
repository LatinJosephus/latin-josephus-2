import json
from pathlib import Path
from lxml import etree as E
V=Path(__file__).resolve().parent;R=V.parents[1];ns={'t':'http://www.tei-c.org/ns/1.0'}
rows=json.loads((R/'review/Source_TOC_Navigation_2026-10-07/CONTENTS_EXPECTATIONS_2026-10-08.json').read_text(encoding='utf-8'))
for b in [1,2,3,4,6,7,8,9,10]:
 p=R/f'assets/xml/antiquities/paratext/niese/book-{b:02}-contents.xml';d=E.parse(str(p));root=d.xpath('//t:div[@type="contents"]',namespaces=ns)[0]
 rows.append({'id':f'contents-antiquities-niese-{b:02}','work':'antiquities','book':b,'language':'Greek','witness':'niese','texts':[''.join(root.itertext())],'supplements':[],'entries':[{'label':''.join(i.find('t:label',ns).itertext()),'text':''.join(i.itertext()),'n':i.get('n')} for i in root.findall('t:list/t:item',ns)],'headings':[''.join(i.itertext()) for i in root.findall('t:head',ns)],'trailer':[''.join(i.itertext()) for i in root.findall('t:trailer',ns)]})
(V/'CONTENTS_EXPECTATIONS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(len(rows))
