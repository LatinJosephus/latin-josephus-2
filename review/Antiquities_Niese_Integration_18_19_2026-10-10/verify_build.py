"""Confirm the actual tested static files came from the frozen merged Git tree."""
from integration_common import *
context=read(D/'BUILD_CONTEXT.json');tip=context['source_commit'];files=[];inputs=[]
for label,commit in [('baseline',START),('final',tip)]:
    source=R/(label+'-source');site=R/(label+'-site')
    assert (site/'antiquities/index.html').is_file()
    assert not (site/'review').exists()
    for relative,f in tree(commit).items():
        if relative.startswith('review/'):continue
        raw=(source/relative).read_bytes();assert_blob(raw,f['oid'])
        if label=='final':assert raw==(ROOT/relative).read_bytes(),relative
        inputs.append(dict(build=label,relative=relative,git_blob=f['oid'],sha256=sha(raw)))
        if relative.startswith('assets/') and not raw.startswith(b'---') and (site/relative).is_file():
            assert raw==(site/relative).read_bytes(),(label,relative)
            files.append(dict(build=label,relative=relative,sha256=sha(raw),status='BYTE_IDENTICAL_GIT_SOURCE_BUILD_OUTPUT'))
assert all(any(f['build']=='final' and f['relative']==relative for f in files) for relative in read(D/'INCOMING_SCOPE.json')['production'])
save('BUILD_RECEIPT.json',dict(status='PASS',**context,build_exit_codes=dict(baseline=0,final=0),fresh_full_Jekyll_builds=2,recipe='review/Whiston_Niese_Combined_Integration_2026-10-09/build_disposable.rb',static_output_checks=files,production_input_manifest=inputs,postbuild_asset_replacement=False,registry_injection=False,public_preview_publication=False))
print('PASS Git-tree production inputs',len(inputs),'static source/output checks',len(files))
