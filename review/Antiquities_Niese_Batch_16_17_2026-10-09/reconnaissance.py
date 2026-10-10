"""Freeze assignment bytes and build explicitly UNREVIEWED candidate records.

This script never edits production. Census, OCR and inherited labels do not
constitute scholarly review or certification.
"""
from pathlib import Path
import sys, json, re, subprocess, hashlib, shutil
from collections import Counter
from datetime import datetime, timezone
from pypdf import PdfReader
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
BATCH = Path(__file__).resolve().parent
BASE = '65b3256fe202a06e33a59aa2d1dcbd7107358271'
CANON = Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
RUNTIME = Path(r'C:\workspace\Antiquities-Niese-16-17-runtime-20261009')
RECOVERY = Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next')
sys.path.insert(0, str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book, fixtures, digest, NS

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf8', newline='\n')

def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd)

def info(path):
    raw = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(raw), sha256=digest(raw))

def pdfinfo(path):
    d = PdfReader(path)
    return dict(**info(path), pages=len(d.pages), metadata={str(k):str(v) for k,v in (d.metadata or {}).items()})

def records(tree, b):
    output=[]
    for item in tree.xpath('//t:list/t:item', namespaces=NS):
        fs=item.find('t:fs', NS)
        if fs is None: continue
        values={f.get('name'):''.join(f.itertext()).strip() for f in fs.findall('t:f', NS) if f.find('t:string', NS) is not None}
        if values.get('book')!=str(b):continue
        locators={}
        for f in fs.findall('t:f', NS):
            inner=f.find('t:fs', NS)
            if inner is not None:
                locators[f.get('name')]={v.get('name'):''.join(v.itertext()).strip() for v in inner.findall('t:f', NS)}
        output.append(dict(id=item.get('{http://www.w3.org/XML/1998/namespace}id'),values=values,locators=locators,source_xml=etree.tostring(item,encoding='unicode')))
    return output

def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    assert not (BATCH/'BASELINE.json').exists(), 'Frozen evidence already exists'
    tracked=git('ls-files','-z').decode().split('\0')[:-1]
    save(BATCH/'ALL_BASE_FILES.json',[dict(relative=p,**info(ROOT/p)) for p in tracked])
    niese=pdfinfo(Path(r'C:\workspace\Niese Antiquities\batch-02\operajosephus04joseuoft.pdf'))
    loeb=pdfinfo(next(Path(r'C:\workspace\Loeb Josephus Volumes').glob('*Xv-XVII*')))
    source=Path(r'C:\Users\Pollard_R\Mon disque\Downloads from Chrome (11-08-2026 onward)\WORKBOT_Antiquities_XVI_XVII_Niese_2026-10-09.txt')
    shutil.copyfile(source,BATCH/source.name)
    registry=etree.parse(str(ROOT/'assets/xml/antiquities/structure.xml'))
    reader=(ROOT/'assets/js/renderTei.js').read_text(encoding='utf8')
    paths=re.findall(r'"(assets/xml/antiquities/niese/book-\d+\.json)"',reader)
    prior={}
    for p in paths:
        data=json.loads((ROOT/p).read_text());prior[str(data['book'])]=dict(range=data['range'],sections=len(data['sections']),input=info(ROOT/p))
    # Legacy I-VII counts are taken from the current declared range data below;
    # this read-only census is kept separate from the workbot's frozen 5231 claim.
    sources=dict(Niese=niese,Loeb=loeb,authority_status='TITLE_AND_BODY_IMAGES_AWAITING_CURRENT_VISUAL_REVIEW')
    save(BATCH/'PRINTED_SOURCES.json',sources)
    n=PdfReader(niese['path']);l=PdfReader(loeb['path'])
    save(BATCH/'NIESE_ALL_OCR.json',[dict(pdf_page=i+1,text=p.extract_text()) for i,p in enumerate(n.pages)])
    save(BATCH/'LOEB_ALL_OCR.json',[dict(pdf_page=i+1,text=p.extract_text()) for i,p in enumerate(l.pages)])
    external=[]
    for packet in ['Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06','Antiquities_Loeb_Niese_Verification_2026-10-05']:
        folder=RECOVERY/'review'/packet
        if folder.exists():
            external.append(dict(packet=str(folder),files=[info(p) for p in folder.iterdir() if p.is_file()]))
    save(BATCH/'EXTERNAL_STRUCTURAL_PROVENANCE.json',external)
    for number,roman,expected in [(16,'XVI',404),(17,'XVII',355)]:
        folder=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09';folder.mkdir(exist_ok=False)
        frozen=folder/'frozen-inputs';frozen.mkdir()
        rows={};models={}
        for lang in ['Greek','Latin','English']:
            rel=f'assets/xml/antiquities/{lang}/book-{number:02}.xml';p=ROOT/rel
            raw=p.read_bytes();blob=git('show',f'{BASE}:{rel}');model=Book(p);models[lang]=model
            (frozen/f'{lang}.xml').write_bytes(raw)
            protected={tag:[etree.tostring(x,encoding='unicode') for x in model.tree.xpath(f'//t:{tag}',namespaces=NS)] for tag in ['milestone','head','argument','floatingText','pb','cb','note','gap','unclear','corr','div1','div2']}
            # Wrappers are separately inventoried by attributes; full source is frozen.
            for tag in ['div1','div2','argument','floatingText']:
                protected[tag]=[dict(path=model.tree.getroottree().getpath(x),attributes=dict(x.attrib)) for x in model.tree.xpath(f'//t:{tag}',namespaces=NS)]
            rows[lang]=dict(**info(p),relative=rel,git_blob_sha256=digest(blob),git_blob_oid=git('rev-parse',f'{BASE}:{rel}').decode().strip(),
                working_tree_equals_blob=raw==blob,encoding='UTF-8',BOM=raw.startswith(b'\xef\xbb\xbf'),CRLF=raw.count(b'\r\n'),LF=raw.count(b'\n'),
                xml_ids=model.tree.xpath('//@xml:id'),sameAs=model.tree.xpath('//@sameAs'),paragraph_count=len(model.units),
                narrative_sha256=digest(model.stream.encode()),labels=model.labels,excluded=model.excluded,protected=protected)
            save(folder/f'{lang.upper()}_TEXT_NODE_LEDGER.json',[{k:v for k,v in u.items() if k!='element'} for u in model.units])
        g=models['Greek'];labels=[x for x in g.labels if re.fullmatch(r'\[\d+\]',x['text'].strip()) and not g.units[x['unit']-1]['excluded_reason']]
        starts={int(x['text'][1:-1]):g.first_content(x['book_offset']) for x in labels}
        if 1 not in starts:starts[1]=g.first_content(0)
        ordered=sorted(starts);candidates=[]
        for i,num in enumerate(ordered):
            offset=starts[num];end=starts[ordered[i+1]] if i+1<len(ordered) else len(g.stream)
            candidates.append(dict(number=num,Greek_candidate_locator=g.locate(offset),Greek_candidate_interval=g.stream[offset:end],
                Greek_print_status='UNREVIEWED',Latin_review_status='UNREVIEWED',physical_placement_status='UNPLACED',correspondence_status='UNASSESSED',
                editorial_status='NO_CASE_YET',implementation_approved=False,reader_certified=False))
        census=dict(expected=expected,explicit_labels=[int(x['text'][1:-1]) for x in labels],implicit_opening=not any(x['text']=='[1]' for x in labels),
            duplicate_claims=[v for v,c in Counter(int(x['text'][1:-1]) for x in labels).items() if c>1],missing_claims=sorted(set(range(1,expected+1))-set(starts)),
            candidate_count=len(candidates),status='MACHINE_CENSUS_ONLY')
        save(folder/'BASELINE.json',dict(book=number,base_commit=BASE,inputs=rows,machine_census=census))
        save(folder/'BOUNDARIES.json',candidates)
        save(folder/'INHERITED_STRUCTURAL_RECORDS.json',records(registry,number))
        save(folder/'DECISION_HISTORY.json',[])
        print(roman,json.dumps(census),flush=True)
    save(BATCH/'BASELINE.json',dict(base_commit=BASE,canonical_HEAD=git('rev-parse','HEAD',cwd=CANON).decode().strip(),
        origin_tracking_tip=git('rev-parse','origin/v2-development',cwd=CANON).decode().strip(),live_origin_tip='65b3256fe202a06e33a59aa2d1dcbd7107358271',
        baseline_selection_reason='Canonical advanced only by Whiston provenance italic style; current immutable clean tip preserves that correction and all certified navigation.',
        branch=git('branch','--show-current').decode().strip(),worktree=str(ROOT),runtime=str(RUNTIME),port=8916,
        ownership_preflight='Branch/path/runtime absent and port free before creation; other worktrees inspected read-only.',
        workbot=info(source),timestamp_UTC=datetime.now(timezone.utc).isoformat(),prior_identity_registries=prior,
        declared_published_count=5231,expected_batch_identities=759,expected_local_total=5990,mapper_fixtures=fixtures(),
        protected_files=[info(ROOT/p) for p in ['assets/js/renderTei.js','assets/css/tei.css','assets/xml/antiquities/structure.xml','_includes/display-settings.html']],
        applicable_AGENTS_files_found=[],status='READ_ONLY_RECONNAISSANCE_NO_IMPLEMENTATION_OR_CERTIFICATION'))

if __name__=='__main__':main()
