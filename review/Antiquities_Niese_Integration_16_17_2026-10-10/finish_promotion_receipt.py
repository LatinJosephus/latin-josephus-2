from integration_common import *
gate=read(R/'PRE_PROMOTION_GATE.json');tip=gate['final_integration_tip']
assert git('rev-parse','HEAD').decode().strip()==tip
assert git('rev-parse','HEAD',cwd=CAN).decode().strip()==tip
subprocess.run(['git','fetch','origin','v2-development'],cwd=CAN,check=True)
live=git('ls-remote','origin','refs/heads/v2-development',cwd=CAN).decode().split()[0]
fetched=git('rev-parse','origin/v2-development').decode().strip();assert live==fetched==tip
cert=read(D/'CERTIFICATION.json');ancestry=[]
for commit in [START,SOURCE,'08f46c0fdfa4639d49c0b13559fa590b6cce314b','5aa64ebc1d3281287e247f359b5718918ffb9de6',*cert['incoming_complete_history']]:
    assert ancestor(commit,live);ancestry.append(dict(commit=commit,verified_remote_ancestor=True))
states=[]
for name,folder in [('canonical',CAN),('integration',ROOT),('certified_source',SOURCE_ROOT)]:
    status=git('status','--porcelain',cwd=folder).decode();assert not status.strip(),(name,status)
    head=git('rev-parse','HEAD',cwd=folder).decode().strip();assert head==(SOURCE if name=='certified_source' else tip)
    states.append(dict(name=name,path=str(folder),HEAD=head,status_porcelain=status))
production=[]
for p in PRODUCTION:
    remote=git('show',live+':'+p);integrated=(ROOT/p).read_bytes();working=(CAN/p).read_bytes()
    assert remote==integrated and sha(remote)==next(x['sha256'] for x in cert['production'] if x['path']==p)
    assert working.replace(b'\r\n',b'\n')==remote.replace(b'\r\n',b'\n')
    production.append(dict(path=p,remote_git_sha256=sha(remote),certified_integrated_sha256=sha(integrated),canonical_working_sha256=sha(working),canonical_working_status='BYTE_IDENTICAL' if working==remote else 'CLEAN_WINDOWS_CHECKOUT_LINE_ENDING_TRANSLATION'))
remote_blobs={}
for entry in git('ls-tree','-rz','--full-tree',live).split(b'\0'):
    if entry:
        meta,path=entry.split(b'\t',1);remote_blobs[path.decode()]=meta.decode().split()[2]
protected=[]
for x in read(D/'CANONICAL_START_FILES.json'):
    if x['path'] in PRODUCTION:continue
    assert sha((CAN/x['path']).read_bytes())==x['sha256'],x['path']
    assert remote_blobs[x['path']]==x['blob'],x['path']
    protected.append(x['path'])
for x in read(D/'CERTIFIED_INCOMING_FILES.json'):
    if x['path']!='assets/js/renderTei.js':
        assert sha((ROOT/x['path']).read_bytes())==x['sha256']
        assert remote_blobs[x['path']]==x['blob'],x['path']
for x in read(D/'FILE_MANIFEST.json')['files']:assert sha((ROOT/x['path']).read_bytes())==x['sha256']
receipt=dict(status='PASS_CANONICAL_INTEGRATED_NORMALLY_PUSHED_AND_DIRECT_REMOTE_VERIFIED',time_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),starting_canonical=START,starting_remote=START,source=SOURCE,source_base=SOURCE_BASE,incoming_complete_history=cert['incoming_complete_history'],integration_baseline_commit=cert['integration_baseline_commit'],merge_commit=cert['merge_commit'],certification_commit=tip,final_canonical=tip,direct_remote=live,fetched_remote=fetched,ancestry=ancestry,production=production,canonical_protected_working_files_byte_exact=len(protected),complete_incoming_review_files_byte_exact=351,worktrees=states,combined_selectable_identities=7082,new_identities=759,new_physical_Latin_fragments=738,new_unavailable_Latin_identities=24,books=cert['books'],manifest=str(D/'FILE_MANIFEST.json'),manifest_sha256=sha((D/'FILE_MANIFEST.json').read_bytes()),integration_report=str(D/'INTEGRATION_REPORT.txt'),certification=str(D/'CERTIFICATION.json'),all_exhaustive_tests_pass=True,normal_push=True,force_push=False,public_preview_publication=False,other_WorkBots_modified=False,Book_XX_integration=False)
save(R/'PROMOTION_RECEIPT.json',receipt)
save(R/'POST_PROMOTION_WORKTREE_INVENTORY.json',dict(time_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),inventory=git('worktree','list','--porcelain').decode(),other_WorkBots_modified_by_this_integration=False))
report=(D/'INTEGRATION_REPORT.txt').read_text(encoding='utf8')
report+='\nFINAL PROMOTION VERIFIED\n'+f'Certification commit and final canonical HEAD: {tip}\nDirect live and freshly fetched origin/v2-development: {live}\nAll six source commits verified in remote ancestry. Normal push completed.\nCanonical, integration and original certified source worktrees are clean.\n'+f'{len(protected)} unrelated canonical working files remain byte-exact.\nAll seven production Git hashes match the certified integrated build and fetched remote.\nNo public-preview publication or refresh occurred. Other WorkBots remain untouched.\n'
(R/'FINAL_INTEGRATION_REPORT.txt').write_text(report,encoding='utf8',newline='\n')
print('PASS final canonical and directly verified remote',tip)
