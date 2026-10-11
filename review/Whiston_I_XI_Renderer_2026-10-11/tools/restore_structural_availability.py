"""Bind inherited IX English restrictions to certified starts; preserve all other XML."""
from pathlib import Path
import json,re,subprocess,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11'
p=ROOT/'assets/xml/antiquities/structure.xml'
raw=subprocess.check_output(['git','show','663b8ce318f0aa247d304d8eeda5b8e76e7489c6:assets/xml/antiquities/structure.xml'],cwd=ROOT).decode()
NS='{http://www.tei-c.org/ns/1.0}'
XMLID='{http://www.w3.org/XML/1998/namespace}id'
source=ET.parse(ROOT/'assets/xml/antiquities/English/book-09.xml')
parents={int(m.get('n')):el.get(XMLID) for el in source.iter(NS+'p') for m in el.iter(NS+'milestone') if m.get('unit')=='niese'}
def locator(n,indent=''):
    fields={'available':'true','file':'English/book-09.xml','paragraph':parents[n],
            'kind':'niese-milestone','target':parents[n],'n':str(n)}
    return '<fs type="text-locator">'+''.join(f'<f name="{k}"><string>{v}</string></f>' for k,v in fields.items())+'</fs>'
changed=[]
def replace_item(match):
    item=match.group()
    if not re.search(r'<f name="book">\s*<string>9</string>',item):return item
    m=re.search(r'<f name="canonical-niese">\s*<string>(\d+)</string>',item)
    if not m or not 51<=int(m[1])<=109:return item
    n=int(m[1]);changed.append({'id':re.search(r'xml:id="([^"]+)"',item)[1],'niese':n,'paragraph':parents[n]})
    return re.sub(r'(<f name="English">)\s*<fs type="text-locator">.*?</fs>\s*(</f>)',
        lambda m:m[1]+locator(n)+m[2],item,count=1,flags=re.S)
modified=re.sub(r'<item\b[^>]*>.*?</item>',replace_item,raw,flags=re.S)
assert len(changed)==10,changed
alignment='<item xml:id="ALIGN-09-51-English-restored" corresp="Latin/book-09.xml#latin-book09-num51"><label>Restored Whiston English IX.51–109 for omission alignment unit 51</label><fs type="alignment-range">'
for k,v in {'canonical-target':'latin-book09-num51','language':'English','source':'Certified restored Whiston IX.51–109','base-commit':'2ce18b40ea8652e5e0d5046f10b1c39935fcdc54','availability':'true'}.items():
    alignment+=f'<f name="{k}"><string>{v}</string></f>'
alignment+=f'<f name="start">{locator(51)}</f><f name="end">{locator(110)}</f></fs><note type="alignment-adjudication"><p>The complete restored English interval corresponds to the inherited IX.51–109 omission placeholder. This binding supplies no Greek or Latin text and retains the restored source footnotes and qualifications.</p></note></item>'
modified=re.sub(r'(<list type="alignment-ranges">.*?)(</list>)',lambda m:m[1]+alignment+'\n'+m[2],modified,count=1,flags=re.S)
old=ET.fromstring(raw);new=ET.fromstring(modified)
olditems={e.get(XMLID):e for e in old.iter(NS+'item')}
newitems={e.get(XMLID):e for e in new.iter(NS+'item')}
for id,el in olditems.items():
    if id in [x['id'] for x in changed]:
        for item in (el,newitems[id]):
            fs=item.find(NS+'fs');english=next(f for f in fs if f.get('name')=='English');fs.remove(english)
    assert ET.tostring(el)==ET.tostring(newitems[id]),id
assert set(newitems)-set(olditems)=={'ALIGN-09-51-English-restored'}
p.write_bytes(modified.encode())
(PACK/'STRUCTURAL_REGISTRY_CHANGE.json').write_bytes((json.dumps({'rows':changed,'new_alignment':'ALIGN-09-51-English-restored','all_other_fields_and_Greek_Latin_locators_unchanged':True},indent=2)+'\n').encode())
print('Updated ten English structural locators and one restored English alignment range.')
