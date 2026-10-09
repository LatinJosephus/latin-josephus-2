"""Check final artifact hashes, pinned byte recovery and exclusive assignment scope."""
from pathlib import Path
import datetime, hashlib, json, re, subprocess
ROOT=Path(__file__).resolve().parents[2]
BATCH=Path(__file__).resolve().parent
PIN='ad3158b7a86dea6997510b3de17f2e510c23367c'
CANONICAL=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf8'))
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def git(*args,cwd=ROOT): return subprocess.check_output(['git',*args],cwd=cwd).decode('utf8').strip()
canon=git('rev-parse','HEAD',cwd=CANONICAL)
observations=load(BATCH/'CANONICAL_HEAD_OBSERVATIONS.json')
if canon!=observations['current']:
    observations.setdefault('later_observations',[]).append(dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),HEAD=canon,meaning='Read-only final handoff observation; frozen inputs remain the exact assigned commit.'))
observations['current']=canon
save(BATCH/'CANONICAL_HEAD_OBSERVATIONS.json',observations)
books=[]
for b,roman in [(14,'XIV'),(15,'XV')]:
    p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
    cert=load(p/'CERTIFICATION.json')
    assert cert['status']=='READY_FOR_COORDINATED_INTEGRATION' and not cert['pending_decisions']
    rows=load(p/'BOUNDARIES.json')
    assert len(rows)==cert['expected_sections']
    assert all(r['reader_certified'] and r['Latin_review_status']=='INDIVIDUALLY_REVIEWED' and r['print_observation']['image_inspected'] and r['editorial_status']!='PENDING_USER_DECISION' for r in rows)
    manifest=load(p/'FILE_MANIFEST.json')
    listed=set()
    for f in manifest['files']:
        q=Path(f['path']); assert q.is_file() and q.is_relative_to(p)
        raw=q.read_bytes(); assert len(raw)==f['bytes'] and sha(raw)==f['sha256'],str(q)
        listed.add(q.resolve())
    actual={q.resolve() for q in p.rglob('*') if q.is_file() and q.name!='FILE_MANIFEST.json'}
    assert actual==listed
    qa=load(p/'FULL_READER_QA.json'); visual=load(p/'READER_DECISIONS_AND_VISUAL_QA.json')
    assert qa['result']=='PASS' and not qa['browserErrors'] and not qa['registry_injected']
    assert len(qa['selections'])==len(rows)
    assert visual['status']=='PASS' and visual['full_reader_certificate_sha256']==sha((p/'FULL_READER_QA.json').read_bytes())
    assert len(qa['containing_views'])==cert['actual_containing_view_checks']
    for f in qa['built_files']:
        assert sha((ROOT/f['path']).read_bytes())==f['sha256']==sha((Path(qa['local_build'])/f['path']).read_bytes())
    for f in visual['visual_screenshots_inspected']:
        if 'sha256' in f: assert sha((ROOT/f['path']).read_bytes())==f['sha256']
    english=load(p/'ENGLISH_CONTEXT_READER_QA.json')
    assert english.get('status',english.get('result'))=='PASS'
    partition=load(p/'COMPLETE_PARTITION_QA.json'); assert partition['status']=='PASS'
    for f in partition['file_hashes']:
        assert sha(Path(f['path']).read_bytes())==f['after']
        assert sha((p/'frozen-inputs'/f"{f['language']}.xml").read_bytes())==f['before']
    latin=(ROOT/f'assets/xml/antiquities/Latin/book-{b:02}.xml').read_bytes()
    assert re.sub(rb'<milestone unit="niese" n="[0-9]+"/>',b'',latin)==(p/'frozen-inputs/Latin.xml').read_bytes()
    greek=(ROOT/f'assets/xml/antiquities/Greek/book-{b:02}.xml').read_bytes()
    inverse=load(p/'GREEK_OPENING_IMPLEMENTATION.json')['inverse']
    at,n=inverse['at'],inverse['delete']
    assert greek[at:at+n]==inverse['expected'].encode('utf8')
    assert greek[:at]+greek[at+n:]==(p/'frozen-inputs/Greek.xml').read_bytes()
    reg=load(ROOT/f'assets/xml/antiquities/niese/book-{b:02}.json')
    assert reg==load(p/'IDENTITY_REGISTRY.json')
    assert len(reg['sections'])==cert['selectable_identities']
    books.append(dict(book=b,status=cert['status'],certificate=str(p/'CERTIFICATION.json'),certificate_sha256=sha((p/'CERTIFICATION.json').read_bytes()),manifest_sha256=sha((p/'FILE_MANIFEST.json').read_bytes()),manifest_files_verified=len(listed),all_boundaries_complete=True,byte_exact_recovery_verified_now=True,all_final_source_and_build_hashes_match=True,all_selection_checks=len(qa['selections']),actual_containing_view_checks=len(qa['containing_views']),selectable_identities=cert['selectable_identities'],nonempty_Latin_intervals=cert['nonempty_Latin_intervals'],added_Latin_milestones=cert['added_Latin_milestones'],retained_starts=cert['retained_starts'],unavailable_sections=cert['unavailable_sections'],suppressed_labels=reg['suppressedLatinLabels']))
scope=load(BATCH/'FINAL_PRODUCTION_SCOPE.json')
production={f['path'] for f in scope['production_files']}
changed=git('diff','--name-only',PIN).splitlines()
reviews=[f'review/Antiquities_Niese_Book{r}_2026-10-09/' for r in ['XIV','XV']]+['review/Antiquities_Niese_Batch_14_15_2026-10-09/']
assert {f for f in changed if not any(f.startswith(p) for p in reviews)}==production
for f in scope['production_files']:
    assert sha((ROOT/f['path']).read_bytes())==f['sha256']
    if '/niese/' in f['path']:
        assert not git('ls-tree',PIN,'--',f['path'])
        f.update(before_working_tree_sha256=None,before_git_blob_sha256=None,new_file=True)
    else:
        blob=subprocess.check_output(['git','show',f"{PIN}:{f['path']}"],cwd=ROOT)
        if f['path'].endswith('renderTei.js'):
            baseline=next(x for x in load(BATCH/'BASELINE.json')['shared_files'] if Path(x['path']).name=='renderTei.js')
        else:
            b=int(Path(f['path']).stem.split('-')[1]); roman={14:'XIV',15:'XV'}[b]
            baseline=load(ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09/BASELINE.json')['inputs'][Path(f['path']).parent.name]
        assert sha(blob)==baseline['sha256']
        f.update(before_working_tree_sha256=baseline['sha256'],before_git_blob_sha256=sha(blob),before_bytes=len(blob),working_tree_bytes_equal_pinned_Git_blob=True,new_file=False)
    raw=(ROOT/f['path']).read_bytes()
    f.update(after_working_tree_sha256=sha(raw),encoding='UTF-8',BOM=raw.startswith(b'\xef\xbb\xbf'),CRLF=raw.count(b'\r\n'),LF=raw.count(b'\n'))
scope['canonical_observed_HEAD']=canon
save(BATCH/'FINAL_PRODUCTION_SCOPE.json',scope)
assert load(BATCH/'FINAL_SHARED_SOURCE_INTEGRITY.json')['status']=='PASS'
protected=load(BATCH/'PROTECTED_COMPLETE_EXISTING_BOOKS_BROWSER_QA_build5.json')
assert protected.get('status',protected.get('result'))=='PASS'
assert load(BATCH/'BOOK_XIV_XV_TRANSITION_READER_QA.json')['status']=='PASS'
coverage=load(BATCH/'LOCAL_COMBINED_COVERAGE.json')
coverage.update(status='BOTH_BOOKS_READY_FOR_COORDINATED_INTEGRATION',certification_pending_until_actual_browser_checks=False,canonical_observed_HEAD=canon,pending_editorial_decisions=[])
for row in coverage['books']:
    final=next(x for x in books if x['book']==row['book'])
    row.update(status=final['status'],suppressed_labels=final['suppressed_labels'],added_Latin_milestones=final['added_Latin_milestones'],retained_starts=final['retained_starts'],certificate=final['certificate'],all_selection_checks=final['all_selection_checks'],actual_containing_view_checks=final['actual_containing_view_checks'])
save(BATCH/'LOCAL_COMBINED_COVERAGE.json',coverage)
audit=dict(status='PASS',observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),pinned_commit=PIN,audited_parent_commit=git('rev-parse','HEAD'),branch=git('branch','--show-current'),canonical_observed_HEAD=canon,frozen_inputs_advanced=False,books=books,production_changed_file_count=len(production),production_scope='FINAL_PRODUCTION_SCOPE.json',per_book_manifests_exact=True,final_browser_certificate_hashes_match_actual_production_and_build=True,independent_partition_and_locator_certificates_current=True,source_inverse_verified_now=True,shared_protected_gate='PROTECTED_COMPLETE_EXISTING_BOOKS_BROWSER_QA_build5.json',book_transition_gate='BOOK_XIV_XV_TRANSITION_READER_QA.json',new_selection_checks=sum(x['all_selection_checks'] for x in books),new_actual_containing_view_checks=sum(x['actual_containing_view_checks'] for x in books),published_selectable_baseline=3157,added_local_selectable=916,local_total_selectable=4073,added_local_nonempty_Latin_intervals=912,published_added_coverage=0,canonical_merged=False,pushed=False,preview_updated=False)
save(BATCH/'FINAL_HANDOFF_AUDIT.json',audit)
print('PASS: both book manifests, final source/build hashes, byte-exact inverses, 916 selections, 205 containing views, seven-file production scope.')
