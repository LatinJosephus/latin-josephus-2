"""Read-only authorization, exact-patch, structural and provenance verification.
Run from any checkout: python -B verify_integration.py --root CHECKOUT --packet PACKET.
The immediate reversal baseline is the accepted 91-action commit, not pre-v1.7 text.
"""
import argparse,hashlib,json,re,subprocess,sys,collections,csv
from pathlib import Path
sys.dont_write_bytecode=True
from preservation_guard import structure,protected_guard
BASE='bf91e314e9f9999df42b793de40bbe28c549e3c1'
def sha(x):return hashlib.sha256(x).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def apply(data,ps):
 out=[];end=0
 for p in sorted(ps,key=lambda p:(p['byte_start'],p['byte_end'])):
  a,b=p['byte_start'],p['byte_end'];assert a>=end and data[a:b]==bytes.fromhex(p['old_bytes_hex']);out +=[data[end:a],bytes.fromhex(p['new_bytes_hex'])];end=b
 return b''.join(out+[data[end:]])
def verify(root,packet):
 def git(*args):return subprocess.check_output(['git','-c','core.longpaths=true','--no-optional-locks','-C',str(root),*args])
 m=load(packet/'staging_correction_manifest.json');auth=load(packet/'registers/imported_editorial_decisions.json');ad={r['candidate_id']:r for r in auth};ps=m['effects'];assert len(ps)==13 and len({p['candidate_id'] for p in ps})==13 and set(ad)=={p['candidate_id'] for p in ps}
 exported=packet/'inputs/editorial/Bamberg_Visual_Review_Decisions_2026-10-17.csv';assert sha(exported.read_bytes())=='dac0cedf66937b9022df8bb7265d4d3e572969f6d3fec4bf8668970b4061b11b'
 csvrows=list(csv.DictReader(exported.open(encoding='utf-8-sig',newline='')));assert len(csvrows)==13
 historical={r['candidate_id']:r for r in load(packet/'registers/reconciled_master_correction_register.json')}
 for p in ps:
  d=ad[p['candidate_id']];assert d['valid'] and d['normalized_editorial_decision']==p['editorial_decision']=='ACCEPT CORRECTION';assert p['question_id']==d['question_id'] and p['decision_CSV_sha256']==sha(exported.read_bytes());assert next(r for r in csvrows if r['question_id']==p['question_id'])==d['original_CSV_fields']
  h=historical[p['candidate_id']]['historical_record'];assert p['registered_original']==h['old'] and p['registered_replacement']==h['new'];old,new=h['old'].encode(),h['new'].encode();left=0
  while left<min(len(old),len(new)) and old[left]==new[left]:left+=1
  end=0
  while end<min(len(old)-left,len(new)-left) and old[-end-1]==new[-end-1]:end+=1
  assert bytes.fromhex(p['old_bytes_hex'])==old[left:len(old)-end if end else len(old)] and bytes.fromhex(p['new_bytes_hex'])==new[left:len(new)-end if end else len(new)]
 inv=load(packet/'patches/exact_reversible_changes.json');changed={r['path'] for r in inv['files']};assert len(changed)==11;files=[];base={};post={}
 for book in m['affected_books']:
  rel=f'assets/xml/antiquities/Latin/book-{book:02}.xml';before=git('show',BASE+':'+rel);actual=(root/rel).read_bytes();pp=[p for p in ps if p['book']==book]
  for p in pp:
   assert sha(before)==p['baseline_sha256'] and not protected_guard(before,p['byte_start'],p['byte_end'])['blocked'];one=apply(before,[p]);assert structure(before)==structure(one)
  assert actual==apply(before,pp);assert structure(before)==structure(actual);base[book]=before;post[book]=actual
  files.append(dict(path=rel,before_sha256=sha(before),after_sha256=sha(actual),authorized_actions=len(pp),structure_Niese_ids_crossrefs_layout_protected='PASS'))
 for r in inv['files']:
  before=git('show',BASE+':'+r['path']);after=(root/r['path']).read_bytes();assert sha(before)==r['before_sha256'] and sha(after)==r['after_sha256'];recovered=after
  for op in reversed(r['exact_operations']):
   a,b=op['after_start'],op['after_end'];assert recovered[a:b]==bytes.fromhex(op['new_hex']);assert before[op['before_start']:op['before_end']]==bytes.fromhex(op['old_hex']);recovered=recovered[:a]+bytes.fromhex(op['old_hex'])+recovered[b:]
  assert recovered==before
 reg='_docs/reader-corpus-integrity.json';old=git('show',BASE+':'+reg);new=(root/reg).read_bytes();expected=json.loads(old);adds=load(packet/'qa/applied_source_certificate.json')['registration_additions']
 for r in adds:
  expected['files'][r['path']]['allowed_worktree_sha256'].append(r['sha256'])
 assert json.loads(new)==expected
 guard='bin/reader-corpus-integrity.mjs';before=git('show',BASE+':'+guard);after=(root/guard).read_bytes();assert before.count(sha(old).encode())==1 and after==before.replace(sha(old).encode(),sha(new).encode())
 prior=load(packet/'inputs/baselines/Bamberg_Editorial_Promotion_v2_1__cumulative_correction_inventory.json')['actions'];assert len(prior)==91;kept=[]
 for p in prior:
  b=p['book'];before=base.get(b) or git('show',BASE+f':assets/xml/antiquities/Latin/book-{b:02}.xml');after=post.get(b) or (root/f'assets/xml/antiquities/Latin/book-{b:02}.xml').read_bytes();a,z=p['current_application_byte_start'],p['current_application_byte_end'];pp=[x for x in ps if x['book']==b];assert before[a:z]==bytes.fromhex(p['current_application_bytes_hex']);assert not any(a<x['byte_end'] and z>x['byte_start'] for x in pp);delta=sum(len(bytes.fromhex(x['new_bytes_hex']))-len(bytes.fromhex(x['old_bytes_hex'])) for x in pp if x['byte_end']<=a);assert after[a+delta:z+delta]==before[a:z];kept.append(p['candidate_id'])
 remaining=[p for p in load(packet/'registers/all_unapplied_source_bindings.json') if p['candidate_id'] not in ad];assert len(remaining)==109
 for p in remaining:
  b=p['book'];before=base.get(b) or git('show',BASE+f':assets/xml/antiquities/Latin/book-{b:02}.xml');after=post.get(b) or (root/f'assets/xml/antiquities/Latin/book-{b:02}.xml').read_bytes();a,z=p['byte_start'],p['byte_end']
  if b==2:
   canonical=before.replace(b'\n',b'\r\n');assert sha(canonical)==p['baseline_sha256'];a-=canonical[:a].count(b'\r\n');z-=canonical[:z].count(b'\r\n')
  pp=[x for x in ps if x['book']==b];assert not any(a<x['byte_end'] and z>x['byte_start'] for x in pp);delta=sum(len(bytes.fromhex(x['new_bytes_hex']))-len(bytes.fromhex(x['old_bytes_hex'])) for x in pp if x['byte_end']<=a);assert after[a+delta:z+delta]==bytes.fromhex(p['old_bytes_hex'])
 unchanged=0
 for row in git('ls-tree','-r','-z',BASE).split(b'\0'):
  if not row:continue
  meta,n=row.split(b'\t',1);rel=n.decode()
  if rel in changed:continue
  data=(root/rel).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==meta.decode().split()[-1],rel;unchanged+=1
 actual_changes=set(git('diff','--name-only',BASE,'--').decode().splitlines());assert {p for p in actual_changes if not p.startswith('review/Bamberg_Editorial_Reconciliation_v3_0/')}==changed
 if (packet/'FILE_MANIFEST.json').is_file():
  prefix='review/Bamberg_Editorial_Reconciliation_v3_0/'
  for r in load(packet/'FILE_MANIFEST.json')['files']:
   assert r['path'].startswith(prefix);assert sha((packet/r['path'][len(prefix):]).read_bytes())==r['sha256']
 return dict(result='PASS',immediate_baseline=BASE,new_approved_actions=13,XML_files=9,prior_91_preserved=91,cumulative_staged_actions=104,cumulative_application_units=103,remaining_109_unapproved_actions_not_applied=True,unchanged_original_tracked_files=unchanged,exact_individual_combined_inverse='PASS',XML_Niese_IDs_crossrefs_physical_order_protected_markup='PASS',guard_logic_and_coverage_unchanged=True,files=files)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--packet',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path);a=p.parse_args();r=verify(a.root.resolve(),a.packet.resolve());s=json.dumps(r,indent=2)+'\n';print(s)
 if a.output:a.output.write_text(s,encoding='utf-8')
