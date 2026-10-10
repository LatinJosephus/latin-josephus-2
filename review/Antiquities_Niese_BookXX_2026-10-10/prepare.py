"""Freeze source, raw-byte mapping and review inputs. No certification by census."""
from pathlib import Path
import json, hashlib, subprocess, re, shutil, sys, concurrent.futures
from lxml import etree
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
PACK=Path(__file__).resolve().parent
CANON=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
RUNTIME=Path(r'C:\workspace\Antiquities-Niese-20-runtime-20261010')
BASE='65b3256fe202a06e33a59aa2d1dcbd7107358271'
RECOVERY=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review')
NS={'t':'http://www.tei-c.org/ns/1.0'}
ID='{http://www.w3.org/XML/1998/namespace}id'
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def info(path):
    raw=path.read_bytes()
    return dict(path=str(path.resolve()),bytes=len(raw),sha256=sha(raw),CRLF=raw.count(b'\r\n'),LF_without_CR=raw.count(b'\n')-raw.count(b'\r\n'),BOM=raw.startswith(b'\xef\xbb\xbf'))
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd)
def render(source,n,path,dpi=145):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-singlefile','-jpeg','-r',str(dpi),str(source),str(path.with_suffix(''))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    return dict(PDF_image_page=n,**info(path))
def main():
    assert not (PACK/'BASELINE.json').exists(),'Do not overwrite immutable baseline'
    assert git('rev-parse','HEAD').decode().strip()==BASE
    RUNTIME.mkdir(exist_ok=False)
    (PACK/'frozen-inputs').mkdir()
    governing=Path(r'C:\Users\Pollard_R\Mon disque\Downloads from Chrome (11-08-2026 onward)\WORKBOT_Antiquities_XX_Niese_2026-10-10.txt')
    shutil.copyfile(governing,PACK/governing.name)
    tracked=[line.split('\t',1) for line in git('ls-files','--stage').decode().splitlines()]
    production=[(meta.split()[1],rel) for meta,rel in tracked if rel.startswith(('assets/','_includes/','_layouts/','_pages/','_sass/','_data/','bin/')) or rel in ['_config.yml','Gemfile','.gitattributes','.gitignore','404.html','robots.txt','CNAME']]
    proc=subprocess.run(['git','cat-file','--batch'],input=''.join(oid+'\n' for oid,rel in production).encode(),stdout=subprocess.PIPE,check=True,cwd=ROOT)
    blobdata=proc.stdout;cursor=0;protected={}
    for oid,rel in production:
        stop=blobdata.index(b'\n',cursor);header=blobdata[cursor:stop].decode().split();size=int(header[-1]);blob=blobdata[stop+1:stop+1+size];cursor=stop+size+2
        protected[rel]=dict(**info(ROOT/rel),git_blob_oid=oid,git_blob_sha256=sha(blob),git_blob_bytes=size)
    save(PACK/'PROTECTED_INPUTS.json',protected)
    sources=[Path(r'C:\workspace\Niese Antiquities\batch-02\operajosephus04joseuoft.pdf'),next(Path(r'C:\workspace\Loeb Josephus Volumes').glob('*XVIII-XX*'))]
    pdfs=[]
    for p in sources:
        doc=PdfReader(p);pdfs.append(dict(**info(p),pages=len(doc.pages),metadata={str(k):str(v) for k,v in doc.metadata.items()}))
    baseline=dict(base=BASE,branch='antiquities-niese-20',worktree=str(ROOT),runtime=str(RUNTIME),preferred_port=8920,port_ownership_at_entry='No listener',canonical_HEAD=git('rev-parse','HEAD',cwd=CANON).decode().strip(),canonical_origin_tracking=git('rev-parse','origin/v2-development',cwd=CANON).decode().strip(),canonical_status=git('status','--porcelain',cwd=CANON).decode(),canonical_intervening_delta=git('diff','--name-status','9527578f361d48adb3094110254e627292bca2c5',BASE,cwd=CANON).decode(),direct_remote_observation=None,remote_observation_limitation='git ls-remote failed: could not resolve github.com; tracking ref is local cached state, not fresh remote verification.',governing_instructions=info(governing),PDFs=pdfs,applicable_AGENTS_files=[],review_status='PREPARATORY_CENSUS_ONLY',certified=False)
    save(PACK/'BASELINE.json',baseline)
    mapper=ROOT/'review/Antiquities_Niese_Batch_12_13_2026-10-09/mixed_mapper_batch.py'
    shutil.copyfile(mapper,PACK/'mixed_mapper.py')
    from mixed_mapper import Book,fixtures
    save(PACK/'MAPPER_PROVENANCE.json',dict(original=info(mapper),copy=info(PACK/'mixed_mapper.py'),fixtures=fixtures(),note='Existing XII/XIII-specific projections do not fire for Book XX. Source-only duration and final subscription must be reviewed separately.'))
    books={};models={}
    for lang in ['Greek','Latin','English']:
        rel=f'assets/xml/antiquities/{lang}/book-20.xml';p=ROOT/rel;raw=p.read_bytes();(PACK/'frozen-inputs'/f'{lang}.xml').write_bytes(raw)
        m=Book(p);models[lang]=m
        books[lang]=dict(**protected[rel],canonical=info(CANON/rel),ids=m.tree.xpath('//@xml:id'),sameAs=m.tree.xpath('//@sameAs'),paragraphs=len(m.units),paragraph_order=[u['id'] for u in m.units],div2=[dict(e.attrib) for e in m.tree.xpath('//t:div2',namespaces=NS)],labels=m.labels,milestones=[dict(e.attrib) for e in m.tree.xpath('//t:milestone',namespaces=NS)],all_topology=[dict(tag=etree.QName(e).localname,xpath=m.tree.getroottree().getpath(e),attributes=dict(e.attrib),text=e.text,tail=e.tail) for e in m.tree.iter() if isinstance(e.tag,str)],narrative_chars=len(m.stream),narrative_sha256=sha(m.stream.encode()))
        save(PACK/f'{lang.upper()}_UNITS.json',[{k:v for k,v in u.items() if k not in ['element','nodes']} for u in m.units])
        save(PACK/f'{lang.upper()}_PROJECTION.json',dict(stream=m.stream,nodes=m.nodes,excluded=m.excluded,inline_excluded=m.inline_excluded))
    save(PACK/'SOURCE_TOPOLOGY.json',books)
    g=models['Greek'];labels=[x for x in g.labels if re.fullmatch(r'\[\d+\]',x['text'])];nums={int(x['text'][1:-1]):x for x in labels}
    assert sorted(nums)==list(range(2,269)) and len(labels)==267
    start1=g.stream.index('Τελευτήσαντος δὲ τοῦ βασιλέως Ἀγρίππα')
    rows=[]
    for n in range(1,269):
        start=nums[n]['book_offset'] if n>1 else start1;end=nums[n+1]['book_offset'] if n<268 else len(g.stream)
        loc=g.locate(g.first_content(start));unit=g.units[loc['paragraph']-1];latin=next((u for u in models['Latin'].units if u['id']==unit['element'].get('sameAs','').lstrip('#')),None)
        rows.append(dict(book=20,number=n,Greek_label=nums.get(n),Greek_locator=loc,Greek_start=start,Greek_end=end,Greek_text=g.stream[start:end],Greek_paragraph=unit['id'],Latin_alignment_paragraph=latin['id'] if latin else None,print_review_status='PENDING',Latin_review_status='PENDING',candidate=None))
    save(PACK/'IDENTITIES.json',rows)
    save(PACK/'SOURCE_ONLY_RECONNAISSANCE.json',dict(Greek_duration=dict(start=0,end=start1,text=g.stream[:start1]),warning='Census and proposed opening only; final source extent review pending.'))
    structure=(ROOT/'assets/xml/antiquities/structure.xml').read_bytes();(PACK/'frozen-inputs/structure.xml').write_bytes(structure)
    tree=etree.fromstring(structure);records=[]
    for item in tree.xpath('//t:item',namespaces=NS):
        fields={f.get('name'):''.join(f.itertext()).strip() for f in item.xpath('./t:fs/t:f',namespaces=NS)}
        if fields.get('book')=='20':records.append(dict(id=item.get(ID),fields=fields,xml=etree.tostring(item,encoding='unicode')))
    save(PACK/'STRUCTURAL_RECORDS.json',records)
    authorities={}
    for name in ['Antiquities_Loeb_Structure_2026-10-04','Antiquities_Loeb_Niese_Verification_2026-10-05','Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06']:
        directory=RECOVERY/name;authorities[name]=[info(p) for p in directory.rglob('*') if p.is_file() and p.suffix.lower() in {'.json','.csv','.md','.txt','.docx'}]
    save(PACK/'FROZEN_STRUCTURAL_AUTHORITIES.json',authorities)
    print(json.dumps(dict(identities=len(rows),Greek_explicit=len(labels),units={l:len(m.units) for l,m in models.items()},characters={l:len(m.stream) for l,m in models.items()},structural_records=len(records),sources=pdfs),ensure_ascii=False))
    for kind,p in zip(['NIESE','LOEB'],sources):
        doc=PdfReader(p)
        save(PACK/f'{kind}_PAGE_TEXT.json',[dict(PDF_page=i+1,OCR=page.extract_text()) for i,page in enumerate(doc.pages)])
    print('Frozen inputs and locating OCR prepared; all scholarly statuses remain pending.')
if __name__=='__main__':main()
