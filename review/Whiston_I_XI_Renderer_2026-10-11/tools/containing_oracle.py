from pathlib import Path
import json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11'
NS='{http://www.tei-c.org/ns/1.0}'
norm=lambda s:re.sub(r'\s+',' ',s).strip()
def text(el):
    if el.tag.removeprefix(NS) in ('num','note','milestone'):return ''
    return (el.text or '')+''.join(text(c)+(c.tail or '') for c in el)
whole={}
for book in ['preface']+list(range(1,12)):
    file='preface.xml' if book=='preface' else f'book-{book:02d}.xml'
    whole[str(book)]=norm(text(ET.parse(ROOT/'assets/xml/antiquities/English'/file).getroot()))
def value(el):
    if el.tag==NS+'fs':return {f.get('name'):value(f[0]) for f in el}
    if el.tag==NS+'vColl':return [value(e) for e in el]
    return el.text or ''
rows=[]
tree=ET.parse(ROOT/'assets/xml/antiquities/structure.xml')
for el in next(e for e in tree.iter(NS+'list') if e.get('type')=='traditional-boundaries'):
    if el.tag!=NS+'item':continue
    row={'id':el.get('{http://www.w3.org/XML/1998/namespace}id'),**value(el.find(NS+'fs'))}
    if int(row.get('book','0'))>11:continue
    rows.append(row)
(PACK/'CONTAINING_ORACLE.json').write_bytes((json.dumps({'whole':whole,'rows':rows},ensure_ascii=False,indent=2)+'\n').encode())
print('Containing oracles:',len(rows),'traditional rows; twelve complete English files.')
