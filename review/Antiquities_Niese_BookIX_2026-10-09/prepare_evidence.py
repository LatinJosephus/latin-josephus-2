from pathlib import Path
import json,sys,re,pdfplumber
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent; W=P.parents[1];R=Path('C:/workspace/Antiquities-Niese-09-runtime-20261009')
if (P/'BOUNDARIES.json').exists():raise SystemExit('Initial evidence preparation is frozen. Use register_boundaries.py with the reviewed local mapper; do not overwrite final methodology.')
src=W/'review/Antiquities_Niese_BookX_2026-10-08/mixed_mapper.py'; dst=P/'mixed_mapper.py'
raw=src.read_bytes();raw=raw.replace(b"else ('English editorial omission placeholder'",b"else ('IX editorial omission placeholder' if attrs.get('xml:id') in {'latin-book09-num51','greek-book09-num51','english-book09-num51'} else ('English editorial omission placeholder'")
raw=raw.replace(b"else '')\r\n",b"else ''))\r\n").replace(b"else '')\n",b"else ''))\n")
dst.write_bytes(raw)
sys.path.insert(0,str(P));from mixed_mapper import Book,digest,fixtures
print(fixtures())
baseline=json.loads((P/'BASELINE.json').read_text(encoding='utf8'))
for name in ['Niese','Loeb']:
 doc=pdfplumber.open(baseline['controls'][name]['absolute_path'])
 if name=='Niese':pages=list(range(277,335)) # one-based 278..335 = printed 270..327
 else: pages=[4,5,6,7,8,9,10,11,18,19,20,21,22,23,168,169,170,171]
 for i in pages:
  f=P/'evidence'/f'{name}-pdf-{i+1:03}.png'
  if not f.exists():doc.pages[i].to_image(resolution=140).save(f)
  (R/f'{name}-{i+1:03}.txt').write_text(doc.pages[i].extract_text() or '',encoding='utf8')
 # Title inventory thumbnails: locating only; actual title is reviewed at full size.
 ims=[]
 for i in range(1,13):
  im=Image.open(P/'evidence'/f'{name}-pdf-{i:03}.png');im.thumbnail((220,300));ims.append((i,im))
 sheet=Image.new('RGB',(880,990),'white');d=ImageDraw.Draw(sheet)
 for j,(i,im) in enumerate(ims):x=(j%4)*220;y=(j//4)*330;sheet.paste(im,(x,y));d.text((x+10,y+302),f'{name} PDF {i}',fill='black')
 sheet.save(R/f'{name}-title-inventory.jpg')
g=Book(W/'assets/xml/antiquities/Greek/book-09.xml');l=Book(W/'assets/xml/antiquities/Latin/book-09.xml')
nums={int(re.findall(r'\d+',m['text'])[-1]):m for m in g.labels};starts={n:g.first_content(m['book_offset']) for n,m in nums.items()};starts[1]=g.first_content(0)
rows=[]
for n in range(1,292):
 k=starts.get(n);end=next((starts[a] for a in range(n+1,292) if a in starts),len(g.stream))
 loc=g.locate(k) if k is not None else None;u=g.units[loc['paragraph']-1] if loc else None;target=u['element'].get('sameAs','').lstrip('#') if u else 'latin-book09-num51';lu=next((x for x in l.units if x['id']==target),None)
 rows.append({'niese':n,'greek':g.stream[k:end] if k is not None else None,'greek_locator':loc,'latin_target':target,'latin_target_text':lu['text'] if lu else None,'greek_print_status':'NOT_REVIEWED','latin_status':'NOT_REVIEWED','editorial_status':'PENDING_REVIEW'})
(P/'INITIAL_GREEK_CENSUS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Prepared IX evidence; placeholders excluded by exact IDs. Narrative:',len(g.stream),len(l.stream))
