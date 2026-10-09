from pathlib import Path
import json,sys
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=Path('C:/workspace/Antiquities-Niese-09-runtime-20261009')
if len(sys.argv)>1:
 lo,hi=map(int,sys.argv[1:3]);rows=json.loads((P/'INITIAL_GREEK_CENSUS.json').read_text(encoding='utf8'));last=None
 for r in rows:
  n=r['niese']
  if not lo<=n<=hi:continue
  if r['latin_target']!=last:
   print('\nLATIN',r['latin_target'],r['latin_target_text']);last=r['latin_target']
  print('G',n,r['greek'])
else:
 for first in range(277,336,2):
  ims=[]
  for page in range(first,min(first+2,336)):
   im=Image.open(P/'evidence'/f'Niese-pdf-{page:03}.png').convert('RGB');w,h=im.size
   im=im.crop((int(w*.17),int(h*.085),int(w*.92),int(h*.61)));ims.append((page,im))
  width=sum(im.width for _,im in ims);height=max(im.height for _,im in ims)+30
  sheet=Image.new('RGB',(width,height),'white');d=ImageDraw.Draw(sheet);x=0
  for page,im in ims:sheet.paste(im,(x,30));d.text((x+15,5),f'Niese II printed {page-8}, PDF {page}',fill='black');x+=im.width
  sheet.save(R/f'print-{first:03}.png')
