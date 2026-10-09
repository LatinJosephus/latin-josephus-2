from pathlib import Path
import json, hashlib, re, csv, subprocess, sys, logging
logging.getLogger('pypdf').setLevel(logging.CRITICAL)
from lxml import etree as E
from pypdf import PdfReader

WORK = Path(r'C:\workspace\LatinJosephus-antiquities-niese-08-10')
CANON = Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
OUT = Path(__file__).parent
REC = Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review')
NS = {'t':'http://www.tei-c.org/ns/1.0'}
ID = '{http://www.w3.org/XML/1998/namespace}id'
sha = lambda b: hashlib.sha256(b).hexdigest()
def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

inventory = {}
for book in [8,10]:
    entry = {}
    for lang in ['Greek','Latin','English']:
        rel = f'assets/xml/antiquities/{lang}/book-{book:02}.xml'
        raw = (WORK/rel).read_bytes()
        root = E.fromstring(raw)
        paras = root.xpath('//t:body//t:div2[not(@n="0")]/t:p',namespaces=NS)
        nums = root.xpath('//t:body//t:num',namespaces=NS)
        entry[lang] = dict(path=rel, worktree_sha256=sha(raw),canonical_sha256=sha((CANON/rel).read_bytes()),
            paragraphs=[dict(id=p.get(ID),sameAs=p.get('sameAs'), text=''.join(p.itertext()),
            children=[dict(tag=E.QName(x).localname,attributes=dict(x.attrib)) for x in p if isinstance(x.tag,str)]) for p in paras],
            labels=[dict(text=''.join(n.itertext()),path=root.getroottree().getpath(n),parent=n.getparent().get(ID)) for n in nums],
            milestones=[dict(attributes=dict(m.attrib),path=root.getroottree().getpath(m)) for m in root.xpath('//t:milestone',namespaces=NS)],
            chapter_divisions=[dict(x.attrib) for x in root.xpath('//t:div2',namespaces=NS)],
            ids=root.xpath('//@xml:id',namespaces={'xml':'http://www.w3.org/XML/1998/namespace'}),sameAs=root.xpath('//@sameAs'))
        print(book,lang,'paras',len(paras),'labels',len(nums),'first',[x['text'] for x in entry[lang]['labels'][:3]],'last',[x['text'] for x in entry[lang]['labels'][-3:]])
    inventory[str(book)] = entry
save(OUT/'inventory.json',inventory)

pdfs = [next(Path(r'C:\workspace\Antiquities-Niese-Batch-08-10\Niese-PDFs').glob('*VI-X.pdf')),
        next(Path(r'C:\workspace\Loeb Josephus Volumes').glob('*Books V-VIII*')),
        next(Path(r'C:\workspace\Loeb Josephus Volumes').glob('*Books 9-11*'))]
metadata=[]
for index,p in enumerate(pdfs):
    r=PdfReader(p)
    tag=['niese-II','loeb-V','loeb-VI'][index]
    target=OUT/(tag+'-pages.json')
    if target.exists(): pages=json.loads(target.read_text('utf-8'))
    else:
        pages=[dict(pdf_page=i+1,text=page.extract_text() or '') for i,page in enumerate(r.pages)]
        save(target,pages)
    metadata.append(dict(path=str(p),sha256=sha(p.read_bytes()),size=p.stat().st_size,pages=len(r.pages),metadata=dict(r.metadata or {})))
    print(tag,metadata[-1],flush=True)
    print('OPENINGS',[(x['pdf_page'],x['text'][:160]) for x in pages[:7]],flush=True)
save(OUT/'pdf-metadata.json',metadata)

frozen=REC/'Antiquities_Loeb_Niese_Verification_2026-10-05'
for name in ['Loeb_Niese_Boundary_Audit.csv','Loeb_Niese_Exceptions.csv','Niese_Structural_Signals.csv']:
    rows=list(csv.DictReader((frozen/'batch-01'/name).open(encoding='utf-8-sig',newline='')))
    selected=[r for r in rows if r.get('antiquities_book',r.get('book')) in ['8','10']]
    save(OUT/(name.replace('.csv','')+'.json'),selected)
    print(name,len(selected),'keys',list(rows[0]) if rows else [],flush=True)
root=E.parse(str(WORK/'assets/xml/antiquities/structure.xml'))
print('STRUCTURE FS',root.xpath('//t:fs/@type',namespaces=NS)[:12],flush=True)
for fs in root.xpath('//t:fs',namespaces=NS)[:2]:
    print(E.tostring(fs,encoding='unicode')[:4500],flush=True)
