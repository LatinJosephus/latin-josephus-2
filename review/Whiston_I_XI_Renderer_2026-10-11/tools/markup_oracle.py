from pathlib import Path
import json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3];PACK=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11'
NS='{http://www.tei-c.org/ns/1.0}'
result=[]
for file in sorted((PACK/'certified').glob('*.xml')):
    book='preface' if file.stem=='preface' else str(int(file.stem[-2:]))
    current=[None];rows={}
    def walk(e):
        tag=e.tag.removeprefix(NS)
        if tag=='milestone' and e.get('unit')=='niese':current[0]=int(e.get('n'))
        if current[0] is not None and tag in ('anchor','lb','hi'):
            attrs={k.removeprefix('{http://www.w3.org/XML/1998/namespace}'):v for k,v in e.attrib.items()}
            rows.setdefault(current[0],[]).append({'tag':tag,'attrs':attrs,'text':' '.join(''.join(e.itertext()).split())})
        for c in e:walk(c)
    walk(ET.parse(file).getroot())
    result.extend({'book':book,'number':n,'elements':elements} for n,elements in rows.items())
(PACK/'MARKUP_ORACLE.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print('Inline markup fixtures:',len(result),'selections;',sum(len(r['elements']) for r in result),'elements.')
