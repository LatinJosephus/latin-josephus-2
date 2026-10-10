from integration_common import *
context=read(D/'BUILD_CONTEXT.json');inputs=[];outputs=[]
for label,commit in [('baseline',START),('final',context['source_commit'])]:
    source=R/(label+'-source');site=R/(label+'-site')
    assert (site/'antiquities/index.html').is_file() and not (site/'review').exists()
    for entry in git('ls-tree','-rz','--full-tree',commit).split(b'\0'):
        if not entry:continue
        meta,path=entry.split(b'\t');relative=path.decode();oid=meta.decode().split()[2]
        if relative.startswith('review/'):continue
        raw=(source/relative).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==oid
        if label=='final':assert raw==(ROOT/relative).read_bytes(),relative
        inputs.append(dict(build=label,path=relative,git_blob=oid,sha256=sha(raw)))
        if relative.startswith('assets/') and not raw.startswith(b'---') and (site/relative).is_file():
            assert raw==(site/relative).read_bytes(),(label,relative)
            outputs.append(dict(build=label,path=relative,sha256=sha(raw)))
assert all(any(x['build']=='final' and x['path']==p for x in outputs) for p in PRODUCTION)
save('BUILD_RECEIPT.json',dict(status='PASS',**context,fresh_full_Jekyll_builds=2,build_exit_codes=dict(baseline=0,final=0),recipe=str(D/'build.sh'),image='ruby@sha256:dba270af6994f64e45ee3dd2b85225a2a0d01f29c04508c7a3c7c8dbf59d2a85',inputs=inputs,static_output_checks=outputs,postbuild_asset_replacement=False,registry_injection=False,public_preview_publication=False))
print('PASS',len(inputs),'Git-tree inputs;',len(outputs),'byte-identical static output checks')
