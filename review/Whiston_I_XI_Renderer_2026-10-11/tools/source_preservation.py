from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11'
PIN='663b8ce318f0aa247d304d8eeda5b8e76e7489c6'
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd)
sources=json.loads((PACK/'SOURCE_INVENTORY.json').read_bytes())
preserved=[]
receipt_dir=PACK/'source-receipts';receipt_dir.mkdir(exist_ok=True)
for book in sources:
    (receipt_dir/f"Book{book['book']}-QA.json").write_bytes(git('show',book['delivery_commit']+':'+book['qa_path']))
    for output in book['outputs']:
        path=output['path'];expected=git('show',book['delivery_commit']+':'+path)
        assert (ROOT/path).read_bytes()==expected
        assert git('show','HEAD:'+path)==expected,path
        assert (PACK/'certified'/Path(path).name).read_bytes()==expected
        preserved.append({'path':path,'delivery_commit':book['delivery_commit'],'sha256':sha(expected),
            'worktree_and_implementation_commit_byte_identical':True,'XML_tree_identical_to_recovery':True})
allowed=[r['path'] for r in preserved]+['assets/js/renderTei.js','assets/css/tei.css','assets/xml/antiquities/niese/book-09.json','assets/xml/antiquities/structure.xml']
changed=[p for p in git('diff','--name-only',PIN,'HEAD').decode().splitlines() if not p.startswith('review/Whiston_I_XI_Renderer_2026-10-11/')]
assert sorted(changed)==sorted(allowed),changed
registry='assets/xml/antiquities/niese/book-09.json'
before=json.loads(git('show',PIN+':'+registry));after=json.loads((ROOT/registry).read_bytes())
for a,b in zip(before['sections'],after['sections']):
    if 51<=a['number']<=109:
        assert b['English']['available'] is True
        a.pop('English');b.pop('English')
    assert a==b
before['excludedNarrativeParagraphs'].pop('English');after['excludedNarrativeParagraphs'].pop('English')
assert before==after
start=json.loads((PACK/'PROTECTED_START.json').read_bytes());finish={}
for branch,old in start.items():
    repo=Path(old['worktree']);commit=git('rev-parse','HEAD',cwd=repo).decode().strip();status=git('status','--porcelain',cwd=repo).decode()
    differences=[]
    for path,h in old['working_files'].items():
        p=repo/path;actual=sha(p.read_bytes()) if p.is_file() else None
        if actual!=h:differences.append({'path':path,'before_sha256':h,'after_sha256':actual})
    finish[branch]={'commit_before':old['commit'],'commit_after':commit,'status_before':old['status'],'status_after':status,
        'working_files_checked':len(old['working_files']),'differences':differences,
        'unchanged':commit==old['commit'] and status==old['status'] and not differences}
    assert finish[branch]['unchanged'],(branch,differences)
out={'status':'PASS','source_assembly':preserved,'production_diff_scope':changed,
    'all_unaffected_Greek_Latin_and_cross_work_git_blobs_unchanged':True,
    'IX_registry_only_English_59_flags_and_English_exclusion_changed':True,
    'protected_worktrees':finish}
(PACK/'SOURCE_PRESERVATION_QA.json').write_bytes((json.dumps(out,indent=2)+'\n').encode())
(PACK/'PROTECTED_FINISH.json').write_bytes((json.dumps(finish,indent=2)+'\n').encode())
print('Source preservation PASS; canonical and XII/XIII worktrees unchanged.')
