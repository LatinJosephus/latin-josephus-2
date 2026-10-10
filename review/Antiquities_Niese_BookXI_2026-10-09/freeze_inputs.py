"""One-time source freeze. No corpus or canonical writes."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys
from datetime import datetime, timezone
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]; D=Path(__file__).resolve().parent
RUNTIME=Path('C:/workspace/Antiquities-Niese-11-runtime-20261009')
CANON=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
BASE='65b3256fe202a06e33a59aa2d1dcbd7107358271'
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def save(name,value):
    (D/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def fileinfo(p):
    raw=p.read_bytes();return dict(path=str(p),bytes=len(raw),sha256=digest(raw))
def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    assert not (D/'BASELINE.json').exists(),'Frozen inputs already exist'
    mapper=ROOT/'review/Antiquities_Niese_BookXIV_2026-10-09/mixed_mapper.py'
    shutil.copyfile(mapper,D/'mixed_mapper.py')
    sys.path.insert(0,str(D));from mixed_mapper import Book,fixtures
    frozen=D/'inputs';frozen.mkdir()
    paths=git('ls-files','-z').decode().split('\0')[:-1]
    tree={line.split('\t',1)[1]:line.split()[2] for line in git('ls-tree','-r',BASE).decode().splitlines()}
    save('ALL_BASE_FILES.json',[dict(relative=p,git_blob_oid=tree[p],**fileinfo(ROOT/p)) for p in paths])
    inputs={}
    for lang in ['Greek','Latin','English']:
        rel=f'assets/xml/antiquities/{lang}/book-11.xml';p=ROOT/rel;raw=p.read_bytes();blob=git('show',f'{BASE}:{rel}')
        (frozen/f'{lang}.xml').write_bytes(raw);b=Book(p)
        inputs[lang]=dict(relative=rel,**fileinfo(p),git_blob_oid=tree[rel],git_blob_sha256=digest(blob),working_bytes_equal_blob=raw==blob,
            canonical_working_sha256=digest((CANON/rel).read_bytes()),last_source_commit=git('log','-1','--format=%H','--',rel).decode().strip(),
            encoding='UTF-8',BOM=raw.startswith(b'\xef\xbb\xbf'),CRLF=raw.count(b'\r\n'),LF=raw.count(b'\n'),
            ids=b.tree.xpath('//@xml:id'),sameAs=b.tree.xpath('//@sameAs'),labels=b.labels,
            existing_milestones=[dict(x.attrib) for x in b.tree.xpath('//t:milestone',namespaces={'t':'http://www.tei-c.org/ns/1.0'})],
            paragraph_order=[u['id'] for u in b.units],narrative_codepoints=len(b.stream),narrative_sha256=digest(b.stream.encode()),excluded=b.excluded)
        save(f'{lang.upper()}_TEXT_NODE_LEDGER.json',[dict(id=u['id'],xpath=u['xpath'],raw_unit_sha256=u['raw_hash'],book_start=u['book_start'],text=u['text'],nodes=u['nodes'],excluded_reason=u['excluded_reason']) for u in b.units])
        save(f'{lang.upper()}_CENSUS.json',dict(labels=b.labels,paragraph_order=[u['id'] for u in b.units],role='Physical XML census only, no boundary judgment'))
    shared=['assets/js/renderTei.js','_includes/display-settings.html','assets/xml/antiquities/structure.xml','assets/css/tei.css','_sass/_reader-ui.scss','_config.yml','Gemfile','Gemfile.lock']
    for rel in shared:
        if (ROOT/rel).exists():shutil.copyfile(ROOT/rel,frozen/Path(rel).name)
    sources={}
    pdfs=dict(Niese=Path('C:/workspace/Niese Antiquities/batch-02/operajosephus03joseuoft.pdf'),
        Loeb=Path('C:/workspace/Loeb Josephus Volumes/Josephus Jewish Antiquities (Books 9-11) (Ralph Marcus) (z-library.sk, 1lib.sk, z-lib.sk).pdf'),
        LevensonMartin=Path('C:/Users/Pollard_R/Zotero/storage/FS4X8IY4/Levenson and Martin - 2016 - The Ancient Latin Translations of Josephus.pdf'))
    for name,p in pdfs.items():
        pdf=PdfReader(p);sources[name]=dict(**fileinfo(p),PDF_pages=len(pdf.pages),metadata={str(k):str(v) for k,v in (pdf.metadata or {}).items()},inspection_status='NOT_YET_VISUALLY_REVIEWED')
        (RUNTIME/f'{name}-OCR.json').write_text(json.dumps([dict(pdf_page=i+1,text=x.extract_text()) for i,x in enumerate(pdf.pages)],ensure_ascii=False),encoding='utf8')
    save('PRINTED_SOURCES.json',sources)
    save('BASELINE.json',dict(baseline_commit=BASE,canonical_observed_head=git('rev-parse','HEAD',cwd=CANON).decode().strip(),
        remote_directly_verified=BASE,branch='antiquities-niese-11',worktree=str(ROOT),runtime=str(RUNTIME),scope_books=[11],
        frozen_at=datetime.now(timezone.utc).isoformat(),paths_unused_before_creation=True,AGENTS_found=[],
        intervening_commits=[dict(commit=BASE,change='assets/css/tei.css: Whiston compiled-index provenance font-style italic')],
        canonical_status=git('status','--porcelain',cwd=CANON).decode(),inputs=inputs,shared=[dict(relative=p,**fileinfo(ROOT/p)) for p in shared if (ROOT/p).exists()],
        mapper_source=fileinfo(mapper),fixtures=fixtures(),prior_selectable_baseline=5231,
        publication_receipt=fileinfo(Path('C:/workspace/Antiquities-Niese-Preview-09-12-13-14-15-2026-10-09/PUBLICATION_SUMMARY.json'))))
    save('DECISION_HISTORY.json',[])
    print('Frozen actual XI bytes and all baseline hashes. No corpus edits or certifications.')
if __name__=='__main__':main()
