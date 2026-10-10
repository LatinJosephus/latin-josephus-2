"""Read-only source freeze and candidate census; no editorial certification."""
from pathlib import Path
import json, hashlib, subprocess, re, shutil, sys
from lxml import etree
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
PACK = Path(__file__).resolve().parent
RUNTIME = Path(r'C:\workspace\Antiquities-Niese-18-19-runtime-20261009')
CANON = Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
RECOVERY = Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review')
BASE = '9527578f361d48adb3094110254e627292bca2c5'
NS = {'t':'http://www.tei-c.org/ns/1.0'}
ID = '{http://www.w3.org/XML/1998/namespace}id'
PYTHON = sys.executable
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def git(*args,cwd=ROOT):
    return subprocess.check_output(['git',*args],cwd=cwd)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def info(p):
    raw=p.read_bytes()
    return {'path':str(p.resolve()),'bytes':len(raw),'sha256':sha(raw),'CRLF':raw.count(b'\r\n'),'LF_without_CR':raw.count(b'\n')-raw.count(b'\r\n'),'BOM':raw.startswith(b'\xef\xbb\xbf')}
def packet(b):return ROOT/f'review/Antiquities_Niese_Book{ {18:"XVIII",19:"XIX"}[b]}_2026-10-09'
def project(el):
    return ''.join(el.xpath('.//text()[not(ancestor::t:num) and not(ancestor::t:note) and not(ancestor::t:app) and not(ancestor::t:rdg)]',namespaces=NS))
def main():
    assert not (PACK/'BASELINE.json').exists(),'Never overwrite frozen inputs'
    assert git('rev-parse','HEAD').decode().strip()==BASE
    RUNTIME.mkdir(exist_ok=False)
    protected={}
    for rel in git('ls-files').decode().splitlines():
        if rel.startswith(('assets/','_includes/','_layouts/','_pages/','_sass/','_data/')) or rel in ['_config.yml','Gemfile','Gemfile.lock']:
            p=ROOT/rel
            if p.is_file(): protected[rel]=dict(**info(p),git_blob_oid=git('rev-parse',f'{BASE}:{rel}').decode().strip(),git_blob_sha256=sha(git('show',f'{BASE}:{rel}')))
    save(PACK/'PROTECTED_INPUTS.json',protected)
    governing=Path(r'C:\Users\Pollard_R\Mon disque\Downloads from Chrome (11-08-2026 onward)\WORKBOT_Antiquities_XVIII_XIX_Niese_2026-10-09.txt')
    shutil.copyfile(governing,PACK/governing.name)
    sources=[Path(r'C:\workspace\Antiquities-Niese-Batch-08-10\Niese-PDFs\Niese (1890) - Antiquities XVI-XX.pdf'), next(Path(r'C:\workspace\Loeb Josephus Volumes').glob('*XVIII-XX*'))]
    pdfs=[]
    for p in sources:
        doc=PdfReader(p);pdfs.append(dict(**info(p),pages=len(doc.pages),metadata={str(k):str(v) for k,v in doc.metadata.items()}))
    baseline=dict(base=BASE,branch='antiquities-niese-18-19',worktree=str(ROOT),runtime=str(RUNTIME),canonical_HEAD=git('rev-parse','HEAD',cwd=CANON).decode().strip(),canonical_origin_tracking=git('rev-parse','origin/v2-development',cwd=CANON).decode().strip(),canonical_status=git('status','--porcelain',cwd=CANON).decode(),canonical_delta=git('diff','--name-status',BASE,'HEAD',cwd=CANON).decode(),direct_remote_observed='65b3256fe202a06e33a59aa2d1dcbd7107358271',baseline_choice='Source XML, registries, renderer and controls match current canonical; later delta only assets/css/tei.css. Use requested concurrent baseline.',governing_instructions=info(governing),PDFs=pdfs,applicable_AGENTS_files=[],review_status='MACHINE_CENSUS_ONLY')
    save(PACK/'BASELINE.json',baseline)
    authorities={}
    for name in ['Antiquities_Loeb_Structure_2026-10-04','Antiquities_Loeb_Niese_Verification_2026-10-05','Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06']:
        directory=RECOVERY/name
        authorities[name]=[info(p) for p in directory.rglob('*') if p.is_file() and p.suffix.lower() in {'.json','.csv','.md','.txt'}]
    save(PACK/'FROZEN_STRUCTURAL_AUTHORITIES.json',authorities)
    # Reuse the accepted raw-byte mapper, explicitly disable its unrelated XIII/XII projections.
    mapper=ROOT/'review/Antiquities_Niese_Batch_12_13_2026-10-09/mixed_mapper_batch.py'
    shutil.copyfile(mapper,PACK/'mixed_mapper.py')
    sys.path.insert(0,str(PACK));from mixed_mapper import Book,fixtures
    save(PACK/'MAPPER_PROVENANCE.json',dict(original=info(mapper),copy=info(PACK/'mixed_mapper.py'),fixtures=fixtures(),note='No XIII/XII-specific projection fires for XVIII/XIX. Nested paragraphs and floatingText checked against independent lxml census.'))
    structure=etree.parse(str(ROOT/'assets/xml/antiquities/structure.xml'))
    for b,last in [(18,379),(19,366)]:
        d=packet(b);(d/'frozen-inputs').mkdir(parents=True)
        models={};books={}
        for lang in ['Greek','Latin','English']:
            rel=f'assets/xml/antiquities/{lang}/book-{b:02}.xml';p=ROOT/rel;raw=p.read_bytes();(d/'frozen-inputs'/f'{lang}.xml').write_bytes(raw)
            model=Book(p);models[lang]=model
            books[lang]=dict(**protected[rel],canonical=info(CANON/rel),ids=model.tree.xpath('//@xml:id'),sameAs=model.tree.xpath('//@sameAs'),paragraphs=len(model.units),paragraph_order=[u['id'] for u in model.units],div2=[dict(e.attrib) for e in model.tree.xpath('//t:div2',namespaces=NS)],labels=model.labels,milestones=[dict(e.attrib) for e in model.tree.xpath('//t:milestone',namespaces=NS)],nested_topology=[dict(tag=etree.QName(e).localname,xpath=model.tree.getroottree().getpath(e),attributes=dict(e.attrib)) for e in model.tree.xpath('//t:argument|//t:floatingText|//t:note',namespaces=NS)],narrative_chars=len(model.stream),narrative_sha256=sha(model.stream.encode()))
            save(d/f'{lang.upper()}_UNITS.json',[{k:v for k,v in u.items() if k not in ['element','nodes']} for u in model.units])
        gre=models['Greek'];labels=[x for x in gre.labels if re.fullmatch(r'\[\d+\]',x['text'])]
        nums={int(x['text'][1:-1]):x for x in labels}
        identities=[]
        for n in range(1,last+1):
            label=nums.get(n);start=label['book_offset'] if label else (gre.units[next(i for i,u in enumerate(gre.units) if u['id'].endswith('num1'))]['book_start'] if n==1 else None)
            assert start is not None,(b,n)
            end=nums[n+1]['book_offset'] if n<last else len(gre.stream)
            unit=next(u for u in gre.units if u['book_start']<=start<u['book_start']+len(u['text']))
            latin=next((u for u in models['Latin'].units if u['id']==unit['element'].get('sameAs','').lstrip('#')),None)
            identities.append(dict(book=b,number=n,Greek_label=label,Greek_locator=gre.locate(gre.first_content(start)),Greek_start=start,Greek_end=end,Greek_text=gre.stream[start:end],Greek_paragraph=unit['id'],Latin_alignment_paragraph=latin['id'] if latin else None,Latin_alignment_text=latin['text'] if latin else None,print_review_status='PENDING',Latin_review_status='PENDING',candidate=None))
        save(d/'BASELINE.json',dict(book=b,expected_range=[1,last],explicit_Greek_numbers=sorted(nums),missing_explicit=sorted(set(range(1,last+1))-set(nums)),duplicate_numbers=[n for n in nums if sum(x['text']==f'[{n}]' for x in labels)>1],sources=books,identity_count=len(identities),certified=False))
        save(d/'IDENTITIES.json',identities)
        rows=[]
        for item in structure.xpath('//t:item',namespaces=NS):
            bibl=item.find('t:bibl',NS)
            if bibl is not None and any('book' in (e.get('unit','')) and (e.text or '').strip() in [str(b),{18:'XVIII',19:'XIX'}[b]] for e in bibl.iter()):rows.append(etree.tostring(item,encoding='unicode'))
        # Keep a complete immutable registry copy because its schema qualifies book via attributes.
        (d/'frozen-inputs/structure.xml').write_bytes((ROOT/'assets/xml/antiquities/structure.xml').read_bytes())
        save(d/'PRINTED_SOURCES.json',dict(Niese=pdfs[0],Loeb=pdfs[1],visual_review_complete=False))
        print(json.dumps({'book':b,'identities':len(identities),'Greek_explicit':len(labels),'missing_explicit':sorted(set(range(1,last+1))-set(nums)),'units':{l:len(m.units) for l,m in models.items()},'narrative_characters':{l:len(m.stream) for l,m in models.items()}}))
    # OCR is used only to locate pages to inspect visually.
    for kind,p in zip(['NIESE','LOEB'],sources):
        doc=PdfReader(p)
        save(PACK/f'{kind}_PAGE_TEXT.json',[dict(PDF_page=i+1,OCR=page.extract_text()) for i,page in enumerate(doc.pages)])
    print('Frozen source census; no starts promoted and no production edits.')
if __name__=='__main__':main()
