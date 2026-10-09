"""Freeze actual assignment inputs; never edits corpus or external evidence."""
from pathlib import Path
import sys, json, subprocess, hashlib, shutil, re
from datetime import datetime, timezone
from pypdf import PdfReader
ROOT = Path(__file__).resolve().parents[2]
BATCH = Path(__file__).resolve().parent
CANON = Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
BASE = 'ad3158b7a86dea6997510b3de17f2e510c23367c'
RUNTIME = Path(r'C:\workspace\Antiquities-Niese-14-15-runtime-20261009')
RESEARCH = Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review\Antiquities_Loeb_Niese_Verification_2026-10-05')
sys.path.insert(0, str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book, fixtures, digest
def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf8', newline='\n')
def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd)
def fileinfo(path):
    raw=path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(raw), sha256=digest(raw))
def freeze_pdf(path):
    info=fileinfo(path); doc=PdfReader(path)
    return dict(**info, pages=len(doc.pages), metadata={str(k):str(v) for k,v in (doc.metadata or {}).items()})
def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    assert not (BATCH/'BASELINE.json').exists(), 'Already frozen; do not overwrite'
    current=git('rev-parse','HEAD',cwd=CANON).decode().strip()
    tracked=git('ls-files','-z').decode().split('\0')[:-1]
    save(BATCH/'ALL_BASE_FILES.json', [dict(relative=p, **fileinfo(ROOT/p)) for p in tracked])
    shared=['assets/js/renderTei.js','_includes/display-settings.html','assets/xml/antiquities/structure.xml','_config.yml','Gemfile']
    info=dict(base_commit=BASE, canonical_observed_HEAD=current, branch=git('branch','--show-current').decode().strip(),
        worktree=str(ROOT), runtime=str(RUNTIME), canonical=str(CANON), timestamp=datetime.now(timezone.utc).isoformat(),
        proposed_paths_unused_before_creation=True, applicable_AGENTS_files_found=[],
        preferred_origin='http://127.0.0.1:8914/', scope_books=[14,15], shared_files=[fileinfo(ROOT/p) for p in shared],
        published_baseline_selections=3157, published_preview_commit='714159a395dd3a728e10de392c16cfaf5769e335',
        publication_record=fileinfo(Path(r'C:\workspace\Antiquities-Niese-Preview-08-10-2026-10-09\PUBLICATION_SUMMARY.json')),
        mixed_mapper_source=fileinfo(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08/mixed_mapper.py'), mixed_mapper_fixtures=fixtures())
    niese=freeze_pdf(Path(r'C:\workspace\Niese Antiquities\batch-02\operajosephus03joseuoft.pdf'))
    duplicate=freeze_pdf(Path(r'C:\workspace\Antiquities-Niese-Batch-08-10\Niese-PDFs\Niese (1892) - Antiquities XI-XV.pdf'))
    assert niese['sha256']==duplicate['sha256']=='676dcc1e9c66892d9a48177043a74fd4d63eca9932a405ba4db6d03f7cf313ab'
    save(BATCH/'NIESE_SOURCE.json', dict(primary=niese, read_only_duplicate=duplicate, coverage_status='HISTORICAL_RECORD_LOCATED_AWAITING_CURRENT_VISUAL_INSPECTION'))
    selected={14: next(Path(r'C:\workspace\Loeb Josephus Volumes').glob('*XII-XIV*')),15:next(Path(r'C:\workspace\Loeb Josephus Volumes').glob('*Xv-XVII*'))}
    for number,roman in [(14,'XIV'),(15,'XV')]:
        folder=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
        frozen=folder/'frozen-inputs'; frozen.mkdir()
        shutil.copyfile(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08/mixed_mapper.py', folder/'mixed_mapper.py')
        rows={}; census={}
        for lang in ['Greek','Latin','English']:
            relative=f'assets/xml/antiquities/{lang}/book-{number:02}.xml'; path=ROOT/relative
            raw=path.read_bytes(); blob=git('show',f'{BASE}:{relative}'); canonical=(CANON/relative).read_bytes()
            (frozen/f'{lang}.xml').write_bytes(raw)
            model=Book(path)
            rows[lang]=dict(**fileinfo(path), relative=relative, git_blob_sha256=digest(blob), git_blob_oid=git('rev-parse',f'{BASE}:{relative}').decode().strip(),
                last_path_commit=git('log','-1','--format=%H','--',relative).decode().strip(), canonical_sha256=digest(canonical),
                canonical_bytes=len(canonical), canonical_CRLF_to_LF_matches_worktree=canonical.replace(b'\r\n',b'\n')==raw,
                worktree_bytes_equal_git_blob=raw==blob, encoding='UTF-8', BOM=raw.startswith(b'\xef\xbb\xbf'), CRLF=raw.count(b'\r\n'), LF=raw.count(b'\n'),
                paragraphs=len(model.units), narrative_paragraphs=sum(not u['excluded_reason'] for u in model.units),
                narrative_codepoints=len(model.stream), narrative_sha256=digest(model.stream.encode()), excluded=model.excluded,
                labels=model.labels, ids=model.tree.xpath('//@xml:id'), sameAs=model.tree.xpath('//@sameAs'))
            if lang=='Greek':
                labels=[x for x in model.labels if re.fullmatch(r'\[\d+\]',x['text'].strip()) and not model.units[x['unit']-1]['excluded_reason']]
                nums=[int(x['text'].strip()[1:-1]) for x in labels]
                census=dict(explicit_sequence=nums, explicit_count=len(nums), implicit_opening_in_machine_source=1 not in nums,
                    label_sequence_contiguous=nums==list(range(min(nums),max(nums)+1)), count_status='MACHINE_CENSUS_ONLY_PRINT_ENDPOINTS_NOT_YET_VERIFIED')
                starts=[dict(number=int(x['text'].strip()[1:-1]),locator=model.locate(model.first_content(x['book_offset']))) for x in labels]
                starts.insert(0,dict(number=1,locator=model.locate(model.first_content(0)),implicit=True))
                for i,s in enumerate(starts):
                    s['Greek']=model.stream[s['locator']['book_offset']:starts[i+1]['locator']['book_offset'] if i+1<len(starts) else len(model.stream)]
                    s['Greek_print_status']='UNREVIEWED';s['Latin_review_status']='UNREVIEWED';s['physical_placement_status']='UNPLACED';s['correspondence_status']='UNASSESSED';s['editorial_status']='NO_CASE_YET'
                save(folder/'BOUNDARIES.json',starts)
            if lang=='Latin':
                save(folder/'LATIN_TEXT_NODE_LEDGER.json', [dict(paragraph=u['index'], id=u['id'], raw_sha256=u['raw_hash'], text=u['text'], excluded_reason=u['excluded_reason'],nodes=u['nodes']) for u in model.units])
        save(folder/'BASELINE.json',dict(book=number, roman=roman, base_commit=BASE, canonical_observed_HEAD=current, inputs=rows, machine_census=census))
        save(folder/'PRINTED_SOURCES.json',dict(Niese=niese, Loeb=freeze_pdf(selected[number]), current_visual_inspection_complete=False))
        save(folder/'DECISION_HISTORY.json',[])
        (folder/'SOURCE_AUTHORITY.md').write_text(f'# Book {roman}: source authority\n\nPinned source: `{BASE}`. Actual worktree: `{ROOT}`. Canonical observed HEAD: `{current}`. The original UTF-8 working-tree XML bytes are frozen in frozen-inputs; BASELINE.json distinguishes Git blobs, working-tree bytes and canonical CRLF bytes.\n\nGreek: `{ROOT}/assets/xml/antiquities/Greek/book-{number:02}.xml`. Latin: `{ROOT}/assets/xml/antiquities/Latin/book-{number:02}.xml`. English: `{ROOT}/assets/xml/antiquities/English/book-{number:02}.xml`. Renderer: `{ROOT}/assets/js/renderTei.js`. Controls: `{ROOT}/_includes/display-settings.html`. Existing identity data: `{ROOT}/assets/xml/antiquities/niese/book-08.json` and book-10.json.\n\nNiese primary: `{niese["path"]}`. Its hash matches the accepted external duplicate. Printed title, coverage and individual starts remain to be independently inspected in this assignment. Loeb: `{selected[number]}`. Full PDF hashes and metadata are in PRINTED_SOURCES.json.\n\nThe accepted VIII/X audit, implementation and integration packets at the pinned commit supply methodology and regression expectations. Their historical NO-GO states do not restrict this authorized local assignment. The mapper is copied byte-exactly and its 14 fixture groups pass. Narrative coordinates exclude chapter-0 contents, num labels, notes and apparatus. Whiston is contextual evidence and is preserved.\n\nFrozen structural research: `{RESEARCH}`. Structural rows locate windows and do not certify exact Niese starts. The transcription is the Latin textual base; no claim of physical loss or of the whole tradition follows from absent correspondence here.\n\nCurrent status: input freeze and machine census only. No scholarly or reader certification is claimed.\n',encoding='utf8',newline='\n')
    save(BATCH/'BASELINE.json',info)
    print(json.dumps(dict(worktree=str(ROOT),canonical_observed_HEAD=current,PDF=niese,mapper=fixtures()),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
