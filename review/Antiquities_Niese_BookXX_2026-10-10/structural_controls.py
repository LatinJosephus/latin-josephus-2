from prepare import *
from mixed_mapper import Book
from PIL import Image, ImageDraw
from collections import Counter
def fields(fs):
    return {f.get('name'):fields(f.find('t:fs',NS)) if f.find('t:fs',NS) is not None else ''.join(f.itertext()).strip() for f in fs.findall('t:f',NS)}
tree=etree.fromstring((PACK/'frozen-inputs/structure.xml').read_bytes())
records=[];controls=[]
models={l:Book(PACK/'frozen-inputs'/f'{l}.xml') for l in ['Latin','Greek','English']}
for item in tree.xpath('//t:item',namespaces=NS):
    fs=item.find('t:fs',NS)
    if fs is None:continue
    f=fields(fs)
    if f.get('book')!='20':continue
    r=dict(id=item.get(ID),**f)
    evidence=item.find('t:note[@type="source-evidence"]/t:p',NS)
    if evidence is not None:r['evidence']=json.loads(evidence.text)
    records.append(r)
    if r.get('scheme')=='subchapter':controls.append(dict(id=r['id'],**r['evidence']['frozen_loeb']))
save(PACK/'STRUCTURAL_CONTROLS.json',records)
print('Actual frozenXX source systems:',dict(Counter(r.get('scheme','coverage') for r in records)))
save(PACK/'LOEB_BOOKXX_CONTROLS.json',controls)
pdf=Path(json.loads((PACK/'BASELINE.json').read_text())['PDFs'][1]['path'])
for page in sorted({c['source_evidence']['english_pdf_page'] for c in controls}):render(pdf,page,PACK/f'evidence/Loeb-IX-PDF{page:03}.jpg')
for a in range(0,len(controls),6):
    panel=Image.new('RGB',(1300,1050),'white');draw=ImageDraw.Draw(panel)
    for i,c in enumerate(controls[a:a+6]):
        se=c['source_evidence'];im=Image.open(PACK/f"evidence/Loeb-IX-PDF{se['english_pdf_page']:03}.jpg")
        y=round(se['english_label_position_pt']['y']*145/72)
        crop=im.crop((0,max(0,y-40),im.width,min(im.height,y+200)))
        crop.thumbnail((640,310))
        x=(i%2)*650;z=(i//2)*350
        draw.text((x+5,z+4),f"{c['id']} {c['printed_label']} Niese association {c['niese_section']} | p{c['printed_page']} / PDF{se['english_pdf_page']}",fill='black')
        panel.paste(crop,(x,z+25))
    path=PACK/f'evidence/Loeb-controls-{a+1:02}-{min(a+6,len(controls)):02}.jpg';panel.save(path,quality=93)
save(PACK/'LOEB_CONTROL_EVIDENCE.json',dict(status='RENDERED_NOT_YET_REVIEWED',controls=controls,images=[info(p) for p in sorted((PACK/'evidence').glob('Loeb*.jpg'))]))
