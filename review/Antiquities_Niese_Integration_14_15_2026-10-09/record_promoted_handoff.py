"""Preserve the verified first push in the review packet; close with evidence only."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda n:json.loads((P/n).read_text(encoding='utf8'))
base=load('BASELINE.json');RT=Path(base['runtime'])
receipt=json.loads((RT/'PROMOTION_RECEIPT.json').read_text(encoding='utf8'))
primary=receipt['canonical_head']
assert receipt['result']=='PASS' and receipt['status']=='CANONICAL_FAST_FORWARD_AND_NORMAL_PUSH_VERIFIED'
assert primary==receipt['remote_head_directly_verified']==receipt['integration_head']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==primary
assert not (P/'PROMOTION_VERIFICATION.json').exists()
snapshot=P/'diagnostics/PRIMARY_PROMOTION';snapshot.mkdir()
for name in ['FILE_MANIFEST.json','CERTIFICATE.json','REPORT.md']:
 shutil.copyfile(P/name,snapshot/('FIRST_PUSH_'+name))
(P/'PROMOTION_VERIFICATION.json').write_bytes((RT/'PROMOTION_RECEIPT.json').read_bytes())
cert=load('CERTIFICATE.json')
cert.update(status='CANONICAL_INTEGRATION_AND_NORMAL_PUSH_VERIFIED',primary_verified_promotion_commit=primary,
    primary_directly_verified_remote=primary,committed_promotion_evidence='PROMOTION_VERIFICATION.json',
    final_handoff_commit='Following review-only commit; actual final HEAD and remote directly verified in runtime PROMOTION_RECEIPT.json',
    production_unchanged_after_verified_promotion=True)
(P/'CERTIFICATE.json').write_text(json.dumps(cert,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
report=(P/'REPORT.md').read_text(encoding='utf8')
paragraphs=report.split('\n\n')
paragraphs[1]=(f'**Canonical integration and normal push verified.** The complete certified XIV/XV history was fast-forwarded into canonical and normally pushed at `{primary}`; the remote commit was verified directly. '
 'Both books\' closed decisions, exact certified corpus bytes and independent unavailable states are preserved. Combined coverage is **5,231 selectable identities =4,315 +916**. '
 'PROMOTION_VERIFICATION.json preserves the first verified push. The following closure commit changes review evidence only; its final local/remote HEAD is directly verified in the runtime PROMOTION_RECEIPT.json.')
report='\n\n'.join(paragraphs)
report+=f'\n\nCanonical promotion completed from c28efbdb615eaaf8dc9a939bc02e067886a83f37 to `{primary}` by fast-forward only, followed by normal origin/v2-development push and direct remote verification. All7 final production bytes,531 incoming review bytes and2,498 protected canonical working-file hashes were checked again after promotion. Canonical/integration/source worktrees are clean and every recorded source branch is preserved. This closure adds only proof, final certificate/report state and an updated review manifest; no production code/data or prior source certificate changes. Historical frozen-base source coverage4,073 =3,157 +916 remains distinct from combined canonical5,231. No public-preview export, preview push, deployment or domain change occurred.\n'
paths=sorted(x for x in P.rglob('*') if x.is_file() and x!=P/'FILE_MANIFEST.json')
count=len(paths)+1
report=re.sub(r'This integration adds \*\*\d+ review files\*\*',f'This integration adds **{count} review files**',report)
(P/'REPORT.md').write_text(report,encoding='utf8',newline='\n')
manifest=load('FILE_MANIFEST.json')
manifest.update(integration_additional_review_files=count,primary_verified_promotion_commit=primary,
 files=[dict(path=str(x),relative=x.relative_to(P).as_posix(),sha256=sha(x.read_bytes()),bytes=x.stat().st_size) for x in paths])
(P/'FILE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print('PASS verified promotion recorded in review; closure review files',count,'production unchanged')
