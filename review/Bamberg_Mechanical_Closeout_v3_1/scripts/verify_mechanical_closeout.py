"""Read-only v3.1 authorization, structural, preservation and inverse-chain QA."""
from pathlib import Path
import argparse,json,hashlib,subprocess,re,sys
sys.dont_write_bytecode=True
from preservation_guard import structure,protected_guard,check_edits
BASE='3e432065ae14db26749ad41a02ee359d724f63d3';CANON='bf91e314e9f9999df42b793de40bbe28c549e3c1';OLDPACK='review/Bamberg_Editorial_Reconciliation_v3_0/';PACK='review/Bamberg_Mechanical_Closeout_v3_1/'
def sha(data):return hashlib.sha256(data).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def undo(data,record):
 assert sha(data)==record['after_sha256'];out=data
 for op in reversed(record['exact_operations']):
  a,b=op['after_start'],op['after_end'];assert out[a:b]==bytes.fromhex(op['new_hex']);out=out[:a]+bytes.fromhex(op['old_hex'])+out[b:]
 assert sha(out)==record['before_sha256'];return out
def verify(root,packet,evidence_root=None):
 cache={}
 def git(*a):return subprocess.check_output(['git','-c','core.longpaths=true','--no-optional-locks','-C',str(root),*a])
 def original(rel,commit=BASE):
  key=(commit,rel)
  if key not in cache:cache[key]=git('show',commit+':'+rel)
  return cache[key]
 prior_manifest=json.loads(original(OLDPACK+'registers/mechanical_v3_1_readiness_manifest.json'));allowed={r['candidate_id']:r for r in prior_manifest['records'] if r['status']=='READY_FOR_SEPARATELY_AUTHORIZED_V3_1'};assert len(allowed)==53
 manifest=load(packet/'mechanical_integration_manifest.json');ps=manifest['effects'];assert len(ps)==len({p['candidate_id'] for p in ps})<=53;assert set(p['candidate_id'] for p in ps)<=set(allowed);ev={p['candidate_id']:p for p in load(packet/'evidence/visual_revalidation.json')}
 for p in ps:
  assert p==allowed[p['candidate_id']]['source_bound_staging_patch'];r=ev[p['candidate_id']];assert r['mechanical_error_confirmed'] and r['original_TPEN_rows_verified'] and r['source_and_crop_hashes_verified'] and not r['whole_token_protected_guard']['blocked'];assert r['disposition']=='VERIFIED_FOR_LOCAL_MECHANICAL_INTEGRATION'
 inverse=load(packet/'patches/exact_reversible_changes.json');changed={r['path'] for r in inverse['files']};xml=[];after_by_book={};before_by_book={};recovered={}
 for b in sorted({p['book'] for p in ps}):
  rel=f'assets/xml/antiquities/Latin/book-{b:02}.xml';before=original(rel);actual=(root/rel).read_bytes();pp=[p for p in ps if p['book']==b];expected=check_edits(before,pp);assert actual==expected and structure(before)==structure(actual)
  for p in pp:check_edits(before,[p])
  before_by_book[b]=before;after_by_book[b]=actual;xml.append(dict(path=rel,before_sha256=sha(before),after_sha256=sha(actual),actions=len(pp),XML_Niese_ids_links_divisions_layout_protected_order='PASS',individual_combined_inverse='PASS'))
 for r in inverse['files']:
  before=original(r['path']);actual=(root/r['path']).read_bytes();assert sha(before)==r['before_sha256'];recovered[r['path']]=undo(actual,r);assert recovered[r['path']]==before
 # All 104 prior actions survive at exact translated source spans.
 old=json.loads(original(OLDPACK+'registers/cumulative_104_action_inventory.json'))['actions'];assert len(old)==104
 for p in old:
  b=p['book'];rel=f'assets/xml/antiquities/Latin/book-{b:02}.xml';before=original(rel);after=(root/rel).read_bytes();a,z=p['v3_0_current_byte_start'],p['v3_0_current_byte_end'];expected=bytes.fromhex(p.get('current_application_bytes_hex',p.get('new_bytes_hex','')));assert before[a:z]==expected
  pp=[x for x in ps if x['book']==b];assert not any(a<x['byte_end'] and z>x['byte_start'] for x in pp);delta=sum(len(bytes.fromhex(x['new_bytes_hex']))-len(bytes.fromhex(x['old_bytes_hex'])) for x in pp if x['byte_end']<=a);assert after[a+delta:z+delta]==expected
 # Existing substantive decisions, including all 56 unapproved spans, remain immutable.
 withheld=json.loads(original(OLDPACK+'registers/withheld_substantive_register.json'));assert len(withheld)==56
 for p in withheld:
  q=p['source_bound_staging_patch'];b=p['book'];a,z=q['byte_start'],q['byte_end'];rel=f'assets/xml/antiquities/Latin/book-{b:02}.xml';before=original(rel);assert sha(before)==q['baseline_sha256'] and before[a:z]==bytes.fromhex(q['old_bytes_hex']);pp=[x for x in ps if x['book']==b];assert not any(a<x['byte_end'] and z>x['byte_start'] for x in pp);delta=sum(len(bytes.fromhex(x['new_bytes_hex']))-len(bytes.fromhex(x['old_bytes_hex'])) for x in pp if x['byte_end']<=a);assert (root/rel).read_bytes()[a+delta:z+delta]==before[a:z]
 assert b'a suo feruore pro peregrina recederent' in (root/'assets/xml/antiquities/Latin/book-05.xml').read_bytes();assert b'necessitatis causa, non uoluntatis causa et non uoluntatis efficerit' in (root/'assets/xml/antiquities/Latin/book-06.xml').read_bytes()
 # Reverse v3.1 to v3.0, then the unchanged historical v3.0 inverse to canonical.
 previous_inverse=json.loads(original(OLDPACK+'patches/exact_reversible_changes.json'))
 for r in previous_inverse['files']:
  immediate=recovered.get(r['path'],(root/r['path']).read_bytes());assert immediate==original(r['path']);assert undo(immediate,r)==original(r['path'],CANON)
 reg='_docs/reader-corpus-integrity.json';old_reg=original(reg);new_reg=(root/reg).read_bytes();expected=json.loads(old_reg)
 for r in xml:expected['files'][r['path']]['allowed_worktree_sha256'].append(r['after_sha256'])
 assert json.loads(new_reg)==expected
 guard='bin/reader-corpus-integrity.mjs';before=original(guard);after=(root/guard).read_bytes();assert before.count(sha(old_reg).encode())==1 and after==before.replace(sha(old_reg).encode(),sha(new_reg).encode())
 unchanged=0
 for row in git('ls-tree','-r','-z',BASE).split(b'\0'):
  if not row:continue
  meta,name=row.split(b'\t',1);rel=name.decode()
  if rel in changed:continue
  data=(root/rel).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==meta.decode().split()[-1],rel;unchanged+=1
 actual=set(git('diff','--name-only',BASE,'--').decode().splitlines());assert {n for n in actual if not n.startswith(PACK)}==changed
 # The old v3.0 verifier is intentionally not pointed at the new corrected live XML.
 # Its manifest/files remain frozen above; the new inverse chain tests its exact sources.
 if evidence_root:
  for rel,r in load(packet/'evidence/source_file_hashes.json').items():assert sha((evidence_root/rel).read_bytes())==r['sha256']
 if (packet/'FILE_MANIFEST.json').is_file():
  for r in load(packet/'FILE_MANIFEST.json')['files']:assert sha((packet/r['file']).read_bytes())==r['sha256']
 return dict(result='PASS',immediate_baseline=BASE,canonical_baseline=CANON,new_mechanical_actions=len(ps),previous_104_actions_preserved=True,cumulative_actions=104+len(ps),cumulative_application_units=103+len(ps),withheld_substantive_unchanged=56,unchanged_original_tracked_files=unchanged,XML_files=xml,all_structural_Niese_order_ids_links_protected_checks='PASS',individual_combined_exact_inverse='PASS',two_tranche_inverse_to_canonical='PASS',integrity_guard_logic_and_coverage_unchanged=True,Book_XI_physical_order_and_Bellum_fragments='UNCHANGED',original_decision_files='UNCHANGED',pro_peregrina_and_VI219='PRESERVED')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--packet',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--evidence-root',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();r=verify(a.root.resolve(),a.packet.resolve(),a.evidence_root);text=json.dumps(r,indent=2)+'\n';print(text)
 if a.output:a.output.write_text(text,encoding='utf-8')
