from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=Path('C:/workspace/Antiquities-Niese-09-runtime-20261009')
for first in range(277,336,4):
    ims=[]
    for page in range(first,min(first+4,336)):
        im=Image.open(P/'evidence'/f'Niese-pdf-{page:03}.png').convert('RGB');w,h=im.size
        im=im.crop((int(w*.17),int(h*.51),int(w*.94),int(h*.72)))
        ims.append((page,im))
    cellw=max(im.width for _,im in ims);cellh=max(im.height for _,im in ims)+28
    out=Image.new('RGB',(cellw*2,cellh*2),'white');d=ImageDraw.Draw(out)
    for i,(page,im) in enumerate(ims):
        x=(i%2)*cellw;y=(i//2)*cellh;out.paste(im,(x,y+28));d.text((x+10,y+5),f'Niese printed {page-8}; PDF {page}',fill='black')
    out.save(R/f'bottom-{first:03}.png')
