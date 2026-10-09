from pathlib import Path
import json,re,pdfplumber
P=Path(__file__).resolve().parent;R=Path('C:/workspace/Antiquities-Niese-09-runtime-20261009');b=json.loads((P/'BASELINE.json').read_text(encoding='utf8'))
doc=pdfplumber.open(b['controls']['Loeb']['absolute_path'])
hits=[]
for page in doc.pages[18:168]:
 t=page.extract_text() or ''
 if any(re.search(r'(?m)^'+str(n)+r'\b',t) for n in [240]):
  pn=page.page_number;hits.append({'PDF':pn,'text':t});page.to_image(resolution=200).save(P/'evidence'/f'Loeb-control-{pn}.png');(R/f'Loeb-control-{pn}.txt').write_text(t,encoding='utf8')
(P/'CONTROL_SEARCH.json').write_text(json.dumps(hits,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print([(x['PDF'],x['text'][:90]) for x in hits])
