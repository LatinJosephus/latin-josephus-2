from integration_common import *
def main():
    assert git('rev-parse','HEAD').decode().strip()==START
    assert not RUNTIME.exists();RUNTIME.mkdir()
    assert git('status','--porcelain',cwd=CANON)==b'' and git('rev-parse','HEAD',cwd=CANON).decode().strip()==START
    assert git('rev-parse','origin/v2-development').decode().strip()==START
    assert git('rev-parse','HEAD',cwd=SOURCE).decode().strip()==SOURCE_TIP and git('status','--porcelain',cwd=SOURCE)==b''
    certificate=read(SOURCE_PACK/'CERTIFICATE.json');assert certificate['certified'] and certificate['ready_for_coordinated_integration']
    history=read(SOURCE_PACK/'ADJUDICATION_HISTORY.json');assert len(history)==4 and all(h['choice']=='A' and h['status']=='APPROVED' for h in history)
    assert len({h['user_response'] for h in history})==1
    for name,record in certificate['executed_gates'].items():assert info(SOURCE_PACK/name)['sha256']==record['sha256']
    files={}
    tree=git('ls-tree','-r',START).decode().splitlines()
    for line in tree:
        meta,rel=line.split('\t',1);mode,kind,oid=meta.split();files[rel]=dict(mode=mode,git_blob_oid=oid)
        if rel.startswith(('assets/','_includes/','_layouts/','_pages/','_sass/','_data/','bin/')) or rel in ['_config.yml','Gemfile','.gitattributes','.gitignore','CNAME']:
            blob=git('show',START+':'+rel)
            files[rel].update(git_sha256=sha(blob),git_bytes=len(blob),integration_checkout=info(ROOT/rel),canonical_checkout=info(CANON/rel))
    source_files={rel:dict(git_blob_oid=meta.split()[2]) for meta,rel in (line.split('\t',1) for line in git('ls-tree','-r',SOURCE_TIP).decode().splitlines()) if rel.startswith('review/Antiquities_Niese_BookXX_2026-10-10/')}
    refs=git('for-each-ref','--format=%(refname) %(objectname)','refs/heads').decode()
    other_refs={r:oid for r,oid in (line.split() for line in refs.splitlines()) if r not in ['refs/heads/v2-development','refs/heads/antiquities-niese-20-integration']}
    remote=git('ls-remote','origin','refs/heads/v2-development','refs/heads/main').decode()
    assert remote.split()[0]==START
    baseline=dict(status='FROZEN',canonical_start=START,direct_remote_start=remote,certified_source_tip=SOURCE_TIP,frozen_source_baseline=FROZEN,branch='antiquities-niese-20-integration',worktree=str(ROOT),runtime=str(RUNTIME),port=PORT,coordination='XI, XVI–XVII and XVIII–XIX already integrated; other integration workers observed idle. Later tips must be rechecked immediately before promotion.',required_ancestors=['c825afcaccd195ee3574d001b408c3cd71e0984c','d3b8bf9f8b10aca6748d40c37fd40e582afdcba5','5aa64ebc1d3281287e247f359b5718918ffb9de6'],source_certificate=info(SOURCE_PACK/'CERTIFICATE.json'),source_production_manifest=read(SOURCE_PACK/'PRODUCTION_MANIFEST.json'),source_approval=info(SOURCE_PACK/'ADJUDICATION_HISTORY.json'),other_local_branch_refs=other_refs,applicable_AGENTS_files=[],publication_authorized=False)
    for commit in baseline['required_ancestors']:subprocess.run(['git','merge-base','--is-ancestor',commit,START],cwd=ROOT,check=True)
    save(PACK/'BASELINE.json',baseline);save(PACK/'STARTING_FILES.json',files);save(PACK/'CERTIFIED_SOURCE_REVIEW_FILES.json',source_files)
    (PACK/'renderer-comparison').mkdir();(PACK/'renderer-comparison/canonical.js').write_bytes(git('show',START+':assets/js/renderTei.js'));(PACK/'renderer-comparison/incoming.js').write_bytes(git('show',SOURCE_TIP+':assets/js/renderTei.js'));(PACK/'renderer-comparison/base.js').write_bytes(git('show',FROZEN+':assets/js/renderTei.js'))
    print('Frozen canonical and directly verified remote',START,';',len(files),'protected Git files;',len(source_files),'incoming source-review files.')
if __name__=='__main__':main()
