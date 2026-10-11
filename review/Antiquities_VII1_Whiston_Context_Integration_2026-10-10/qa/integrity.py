from pathlib import Path
import json,hashlib,subprocess
I=Path(r'C:/workspace/LatinJosephus-antiquities-vii1-whiston-context-integration');R=Path(r'C:/Users/Pollard_R/Git/LatinJosephus-v2-development');S=Path(r'C:/workspace/LatinJosephus-antiquities-vii1-whiston-context-repair');T=Path(r'C:/workspace/Antiquities-VII1-Whiston-Integration-runtime-20261010')
start=json.loads((T/'INTEGRATION_START.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git','--no-optional-locks','-C',str(I),*a])
C=start['canonical']['HEAD'];B=start['certified_source']['HEAD'];changed=git('diff','--name-only',C,'HEAD').decode().splitlines();prod=[p for p in changed if not p.startswith('review/')];assert prod==['assets/js/renderTei.js'];assert not git('diff',B,start['integration_merge']);assert not git('diff',start['integration_merge'],'HEAD','--','assets')
assert all(sha((R/p).read_bytes())==h for p,h in start['baseline_files'].items()),'canonical modified during testing'
assert all(sha((S/p).read_bytes())==h for p,h in start['certified_files'].items()),'certified source modified'
assert all(sha((I/p).read_bytes())==h for p,h in start['certified_files'].items()),'integration differs from certified checkout'
protected={p:h for p,h in start['baseline_files'].items() if p not in prod};eol=[]
for p,h in protected.items():
 rb=(R/p).read_bytes();ib=(I/p).read_bytes()
 if sha(ib)!=h:
  assert rb.replace(b'\r\n',b'\n')==ib.replace(b'\r\n',b'\n'),p
  eol.append(p)
paths=[p for p in protected if p.startswith('assets/xml/') and p.endswith('.xml')];regs=[p for p in protected if p.startswith('assets/') and 'niese' in p.lower() and p.endswith('.json')]
blobs={}
for p in paths+regs:
 b=git('show',C+':'+p);assert b==(I/p).read_bytes(),p;blobs[p]=sha(b)
expected=json.loads((I/'review/Antiquities_VII1_Whiston_Context_Repair_2026-10-10/CHANGED_FILES.json').read_text());assert all(sha((I/p).read_bytes())==h for p,h in expected['SHA256'].items())
assert (T/'candidate-final-site/assets/js/renderTei.js').read_bytes()==(I/'assets/js/renderTei.js').read_bytes()
r={'result':'PASS','baseline_commit':C,'merge_commit':start['integration_merge'],'merge_parents':start['merge_parents'],'certified_commit':B,'merge_tree_equals_certified_tree':True,'production_changed_files':prod,'production_SHA256':{p:sha((I/p).read_bytes()) for p in prod},'protected_original_tracked_files':len(protected),'XML_files_unchanged_Git_blobs_and_certified_checkout_bytes':len(paths),'Niese_registries_unchanged_Git_blobs_and_certified_checkout_bytes':len(regs),'protected_blob_SHA256':blobs,'canonical_checkout_original_bytes_unchanged_during_QA':True,'certified_source_files_unchanged':len(start['certified_files']),'legacy_canonical_CRLF_vs_new_checkout_LF':eol,'line_ending_explanation':'95 unchanged tracked inputs, including 53 XML files, have legacy CRLF in canonical and LF in fresh certified/integration checkouts. All XML and Niese registry integration bytes equal pinned Git blobs; no XML edits or normalization were performed. Canonical originals were independently hashed and remain unchanged during QA.','superseded_check':'Initial raw cross-checkout equality assertion failed because it did not account for legacy checkout line endings; CHECKOUT_EOL_DIAGNOSTIC.json retains all differences. No production defect.'}
(T/'SOURCE_INTEGRITY.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print({k:r[k] for k in ['result','XML_files_unchanged_Git_blobs_and_certified_checkout_bytes','Niese_registries_unchanged_Git_blobs_and_certified_checkout_bytes','production_SHA256']})
