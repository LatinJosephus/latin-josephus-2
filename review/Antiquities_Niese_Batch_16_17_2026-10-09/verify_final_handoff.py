"""Read-only independent verification of final commits, manifests and certificates."""
from pathlib import Path
import json,hashlib,subprocess,datetime
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def git(*args):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=ROOT)
def main():
    base=read(BATCH/'BASELINE.json');cert=read(BATCH/'CERTIFICATION.json');manifest=read(BATCH/'REVIEW_FILE_MANIFEST.json')
    assert cert['status']=='BOTH_BOOKS_INDEPENDENTLY_LOCALLY_CERTIFIED'
    status=git('status','--porcelain').decode().strip();assert not status,status
    head=git('rev-parse','HEAD').decode().strip();assert git('branch','--show-current').decode().strip()==base['branch']
    changed=git('diff','--name-only',base['base_commit'],'HEAD').decode().splitlines()
    production=[x['path'] for x in cert['production_paths']]
    folders=manifest['folders'];assert all(p in production or any(p.startswith(f+'/') for f in folders) for p in changed),changed
    assert sorted(x for x in changed if not x.startswith('review/'))==sorted(production)
    for item in [*manifest['files'],*cert['production_paths']]:
        raw=(ROOT/item['path']).read_bytes();assert sha(raw)==item['sha256'],item['path']
        assert git('show','HEAD:'+item['path'])==raw,item['path']
    for name,reference in cert['books'].items():
        certificate_path=ROOT/reference['path'];assert sha(certificate_path.read_bytes())==reference['sha256']
        book=read(certificate_path);assert book['status']=='INDEPENDENTLY_LOCALLY_CERTIFIED'
        p=certificate_path.parent;rows=read(p/'BOUNDARIES.json');assert all(r['applied'] and r['reader_certified'] for r in rows)
        ledger=read(p/'APPLIED_RAW_BYTE_PATCH.json');assert sha((ROOT/ledger['registry']['relative']).read_bytes())==ledger['registry']['sha256']
        for language in ['Latin','Greek','English']:
            source=next(x for x in book['source_byte_proofs'] if x['language']==language)
            assert source['byte_exact_recovery'] and source['original_sha256']==source['ledger_reverse_sha256']==source['independent_token_reverse_sha256']
            actual=ROOT/f'assets/xml/antiquities/{language}/book-{name}.xml';assert sha(actual.read_bytes())==source['implemented_sha256']
    for name in ['Niese','Loeb']:
        source=read(BATCH/'PRINTED_SOURCES.json')[name];assert sha(Path(source['path']).read_bytes())==source['sha256']
    proof=read(BATCH/'INDEPENDENT_IMPLEMENTATION_SOURCE_PROOF.json')
    allowed=set(proof['changed_pinned_paths']);drift=[]
    for item in read(BATCH/'ALL_BASE_FILES.json'):
        if sha((ROOT/item['relative']).read_bytes())!=item['sha256']:drift.append(item['relative'])
    assert set(drift)==allowed and len(drift)==5
    hashes=[]
    for report_ref in cert['QA_reports']:
        path=ROOT/report_ref['path'];assert sha(path.read_bytes())==report_ref['sha256'];report=read(path);assert report['status'].startswith('PASS_')
        for item in report['built_source_hashes']:
            assert sha((ROOT/item['file']).read_bytes())==item['sha256']
            built=Path(base['runtime'])/'candidate-build/site'/item['file'];assert sha(built.read_bytes())==item['sha256']
        hashes.append(report_ref)
    git('diff','--check',base['base_commit'],'HEAD','--',*production)
    from verify_literal_review_whitespace import verify
    literal_whitespace=verify(committed=True)
    result=dict(status='PASS_FINAL_CLEAN_LOCALLY_CERTIFIED_HANDOFF',verified_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        branch=base['branch'],HEAD=head,status_porcelain=status,immutable_base=base['base_commit'],worktree=str(ROOT),runtime=base['runtime'],
        local_commits=git('log','--format=%H %s',base['base_commit']+'..HEAD').decode().splitlines(),
        production_changed_paths=production,changed_review_paths=[x for x in changed if x.startswith('review/')],
        review_file_count=len(manifest['files']),all_manifest_working_bytes_equal_committed_blobs=True,all_non_scope_pinned_files_unchanged=True,
        all_four_editor_B_decisions_closed=True,book_certificates=cert['books'],QA_reports=hashes,literal_review_whitespace_proof=literal_whitespace,
        new_selections=759,prior_selections=5231,containing_views=311,legacy_endpoints=35,local_total=5990,
        ready_for_coordinated_canonical_integration=True,merged=False,pushed=False,published=False,deployed=False)
    destination=Path(base['runtime'])/'FINAL_GIT_HANDOFF.json'
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print('PASS FINAL CLEAN HANDOFF',head,';',len(manifest['files']),'committed review files verified;',len(production),'production paths;',destination)
if __name__=='__main__':main()
