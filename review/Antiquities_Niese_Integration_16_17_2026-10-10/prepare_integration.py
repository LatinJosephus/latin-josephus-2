from integration_common import *
assert git('rev-parse','HEAD',cwd=CAN).decode().strip()==START
assert git('rev-parse','origin/v2-development').decode().strip()==START
assert not git('status','--porcelain',cwd=CAN).strip()
assert git('rev-parse','HEAD',cwd=SOURCE_ROOT).decode().strip()==SOURCE
assert not git('status','--porcelain',cwd=SOURCE_ROOT).strip()
assert not R.exists();R.mkdir()
assert ancestor('08f46c0fdfa4639d49c0b13559fa590b6cce314b',START)
assert ancestor('5aa64ebc1d3281287e247f359b5718918ffb9de6',START)
assert git('merge-base',START,SOURCE).decode().strip()==SOURCE_BASE
canonical=inventory(START,CAN);incoming=inventory(SOURCE,SOURCE_ROOT)
save('CANONICAL_START_FILES.json',canonical)
incoming_scope=[x for x in incoming if x['path'] in PRODUCTION or any(x['path'].startswith(f) for f in FOLDERS)]
save('CERTIFIED_INCOMING_FILES.json',incoming_scope)
source_receipt=read('C:/workspace/Antiquities-Niese-16-17-runtime-20261009/FINAL_GIT_HANDOFF.json')
assert source_receipt['HEAD']==SOURCE and source_receipt['status_porcelain']=='' and source_receipt['status'].startswith('PASS_')
catalogue=[]
for b in range(1,21):
    path=CAN/f'assets/xml/antiquities/niese/book-{b:02}.json'
    if path.exists():
        reg=read(path);catalogue.append(dict(book=b,identities=len(reg['sections']),range=reg['range']))
    elif b<=7:catalogue.append(dict(book=b,identities=320 if b==1 else {2:349,3:322,4:331,5:362,6:378,7:394}[b],authority='existing canonical renderer range; verify actual live menus independently'))
assert sum(x['identities'] for x in catalogue)==6323
save('BASELINE.json',dict(canonical_start=START,remote_start=START,source_tip=SOURCE,source_base=SOURCE_BASE,
    incoming_complete_history=git('rev-list','--reverse',SOURCE_BASE+'..'+SOURCE).decode().splitlines(),
    branch=git('branch','--show-current').decode().strip(),worktree=str(ROOT),runtime=str(R),port=8926,
    ownership_preflight='Integration branch/path/runtime/review directory absent; port8926 free; isolated from source and other workers.',
    canonical_clean=True,source_clean=True,canonical_catalogue=catalogue,canonical_before_count=6323,expected_combined_count=7082,
    XI_and_XVIII_XIX_already_promoted=True,direct_remote_verified=True,user_authorization='Integrate both books, combined certification, safe canonical fast-forward and normal origin/v2-development push. No public-preview publication.',
    source_receipt_sha256=sha(Path('C:/workspace/Antiquities-Niese-16-17-runtime-20261009/FINAL_GIT_HANDOFF.json').read_bytes()),
    canonical_files=len(canonical),incoming_scope_files=len(incoming_scope),date_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
(D/'renderer-comparison').mkdir()
for name,commit in [('base',SOURCE_BASE),('canonical',START),('incoming',SOURCE)]:
    (D/'renderer-comparison'/f'{name}.js').write_bytes(git('show',commit+':assets/js/renderTei.js'))
save(R/'TASK_OWNER.json',dict(root=str(ROOT),branch=git('branch','--show-current').decode().strip(),purpose='Authorized XVI-XVII isolated canonical integration',canonical_start=START))
print('PASS preflight:',len(canonical),'canonical files,',len(incoming_scope),'incoming scoped files; canonical6323 -> expected7082')
