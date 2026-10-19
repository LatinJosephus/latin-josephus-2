"""Read-only final-sample authorization, immutable XML and inverse-chain checks."""
from pathlib import Path
import json,csv,hashlib,re,subprocess,argparse,xml.etree.ElementTree as ET
from preservation_guard import structure,protected_guard
BASE='123d82f631602ccad174daea38e99d6a64d3e69f';DEV='f874b6a60f16c96f356abcbe070854611c49f2a3';PACK='review/Bamberg_Final_Verification_v3_5/'
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def append_hash_bytes(data,path,value):
 m=list(re.finditer(rb'("'+re.escape(path.encode())+rb'"\s*:\s*\{.*?"allowed_worktree_sha256"\s*:\s*\[)([^\]]*)(\])',data,re.S));assert len(m)==1;m=m[0];v=m[2];at=v.rfind(b'"')+1;assert at>0;indent=re.search(rb'(?:\r?\n)([ \t]*)"[^"\r\n]+"\s*$',v).group(1);eol=re.search(rb'\r?\n',v).group();pos=m.start(2)+at;return data[:pos]+b','+eol+indent+b'"'+value.encode()+b'"'+data[pos:]
def undo(data,r):
 assert sha(data)==r['after_sha256'];out=data
 for op in reversed(r['exact_operations']):
  a,z=op['after_start'],op['after_end'];assert out[a:z]==bytes.fromhex(op['new_hex']);out=out[:a]+bytes.fromhex(op['old_hex'])+out[z:]
 assert sha(out)==r['before_sha256'];return out
def verify(root,packet):
 def git(*a):return subprocess.check_output(['git','-c','core.longpaths=true','--no-optional-locks','-C',str(root),*a])
 cert=load(packet/'decision_import_certificate.json');src=packet/cert['source_file'];assert sha(src.read_bytes())==cert['sha256'];csvrows=list(csv.DictReader(src.open(encoding='utf-8-sig',newline='')));byid={r['check_id']:r for r in csvrows};assert len(csvrows)==len(byid)==20 and set(byid)=={f'FINAL34-B{b:02}' for b in range(1,21)}
 results=load(packet/'final_check_results.json');assert results['completed']==20 and results['unanswered']==results['unresolved']==0
 for r in results['records']:
  original=byid[r['check_id']];assert r['original_export_record']==original;q=r['sample'];before=git('show',BASE+':'+q['staged_source_path']);assert sha(before)==original['source_sha256']==q['staged_source_sha256'];assert original['staging_commit']==BASE==q['staging_commit'];assert before[q['staged_source_byte_start']:q['staged_source_byte_end']].decode()==original['staged_transcription'];assert all(original[k]==str(q[k]) for k in ['book','niese','folio']);assert original['physical_location']==q['location'];assert r['completed_check'] is True
 assert sum(r['decision']=='CONFIRM EXISTING TRANSCRIPTION' for r in csvrows)==14 and sum(r['decision']=='DISCREPANCY FOUND' for r in csvrows)==6
 directives=load(packet/'final_sample_implementation_records.json');bycandidate={r['candidate_id']:r for r in directives};manifest=load(packet/'applied_correction_manifest.json');ps=manifest['actions'];assert len(ps)==len(bycandidate)==11 and len({p['candidate_id'] for p in ps})==11
 for p in ps:
  r=bycandidate[p['candidate_id']];assert r['minimal_patch']==p;rmp=byid[p['check_id']];assert rmp['decision']=='DISCREPANCY FOUND';assert rmp['editorial_comments']==r['editorial_comment_verbatim'];assert p['registered_original']+' > '+p['registered_replacement'] in rmp['editorial_comments'];assert p['authority_export_sha256']==cert['sha256'];assert r['implementation_status']=='APPROVED AND IMPLEMENTABLE'
 inverse=load(packet/'patches/exact_reversible_changes.json');changed={r['path'] for r in inverse['files']};assert len(changed)==8;recovered={};xml=[]
 for r in inverse['files']:
  rel=r['path'];before=git('show',BASE+':'+rel);actual=(root/rel).read_bytes();assert sha(before)==r['before_sha256'];recovered[rel]=undo(actual,r);assert recovered[rel]==before
  if not rel.endswith('.xml'):continue
  assert structure(before)==structure(actual);ET.fromstring(actual);parts=[];last=0;pps=sorted((p for p in ps if p['source_path']==rel),key=lambda p:p['byte_start'])
  for p in pps:
   a,z=p['byte_start'],p['byte_end'];old,new=bytes.fromhex(p['old_bytes_hex']),bytes.fromhex(p['new_bytes_hex']);assert sha(before)==p['baseline_sha256'];assert before[a:z]==old==p['old'].encode();assert new==p['new'].encode();assert a>=last and not protected_guard(before,a,z)['blocked'];assert re.findall(rb'<[^>]*>',old)==re.findall(rb'<[^>]*>',new)
   fa,fz=p['registered_byte_start'],p['registered_byte_end'];assert before[fa:fz].decode()==p['registered_original'];assert (before[fa:a]+new+before[z:fz]).decode()==p['registered_replacement'];assert not re.search(rb'<[^>]*>',before[fa:fz])
   single=before[:a]+new+before[z:];assert structure(single)==structure(before);assert single[:a]+old+single[a+len(new):]==before;parts.extend([before[last:a],new]);last=z
  assert b''.join(parts+[before[last:]])==actual;xml.append(dict(path=rel,before_sha256=sha(before),after_sha256=sha(actual),actions=len(pps),XML_Niese_IDs_refs_divisions_layout_protected='PASS'))
 assert len(xml)==6
 cumulative=load(packet/'cumulative_correction_inventory.json');actions=cumulative['actions'];assert len(actions)==len({r['candidate_id'] for r in actions})==214;assert len({(r['book'],r['current_byte_start'],r['current_byte_end'],r['current_bytes_hex']) for r in actions})==213
 for r in actions:
  data=(root/f'assets/xml/antiquities/Latin/book-{r["book"]:02}.xml').read_bytes();assert sha(data)==r['current_source_sha256'];assert data[r['current_byte_start']:r['current_byte_end']]==bytes.fromhex(r['current_bytes_hex']),r['candidate_id']
 assert sum(r['v3_5_status']=='PREVIOUS_203_PRESERVED' for r in actions)==203
 held=load(packet/'withheld_unresolved_register.json');assert len(held)==10;prior=load(packet/'inputs/prior_ten_withheld_records.json');assert {r['candidate_id'] for r in held}=={r['candidate_id'] for r in prior}
 for r in held:
  assert not r['applied'];assert r['original_record']==next(x for x in prior if x['candidate_id']==r['candidate_id']);data=(root/r['current_source_path']).read_bytes();assert sha(data)==r['current_source_sha256'] and data[r['current_byte_start']:r['current_byte_end']]==bytes.fromhex(r['current_bytes_hex'])
 assert sum(r['editorial_status']=='UNREVIEWED / UNAPPROVED' for r in held)==9
 assert next(r for r in held if r['candidate_id']=='M14-B13-5d140d1c1b')['original_reading']=='nec<cb n="2/2"/>et'
 assert b'a suo feruore pro peregrina recederent' in (root/'assets/xml/antiquities/Latin/book-05.xml').read_bytes();assert b'necessitatis causa, non uoluntatis causa et non uoluntatis efficerit' in (root/'assets/xml/antiquities/Latin/book-06.xml').read_bytes()
 # Reverse new edits to the unchanged v3.4 commit, then its original inverse to development.
 previous=json.loads(git('show',BASE+':review/Bamberg_Substantive_Closeout_v3_4/patches/exact_reversible_changes.json'))
 for r in previous['files']:
  middle=recovered.get(r['path'],(root/r['path']).read_bytes());assert middle==git('show',BASE+':'+r['path']);assert undo(middle,r)==git('show',DEV+':'+r['path'])
 reg='_docs/reader-corpus-integrity.json';old=git('show',BASE+':'+reg);want=old;expected=json.loads(old)
 for r in xml:want=append_hash_bytes(want,r['path'],r['after_sha256']);expected['files'][r['path']]['allowed_worktree_sha256'].append(r['after_sha256'])
 now=(root/reg).read_bytes();assert now==want and json.loads(now)==expected;guard='bin/reader-corpus-integrity.mjs';gold=git('show',BASE+':'+guard);assert (root/guard).read_bytes()==gold.replace(sha(old).encode(),sha(now).encode()) and gold.count(sha(old).encode())==1
 unchanged=0
 for rel,h in load(packet/'inputs/staging_original_tracked_hashes.json').items():
  if rel not in changed:assert sha((root/rel).read_bytes())==h,rel;unchanged+=1
 actual=set(git('diff','--name-only',BASE,'--').decode().splitlines());assert {p for p in actual if not p.startswith(PACK)}==changed
 xmls=[]
 for p in sorted((root/'assets/xml').rglob('*.xml')):ET.parse(p);xmls.append(dict(path=p.relative_to(root).as_posix(),sha256=sha(p.read_bytes())))
 assert len(xmls)==166
 for r in load(packet/'image_evidence_manifest.json'):
  for a in r['assets'].values():assert sha((packet/a['file']).read_bytes())==a['sha256']
 ledger=load(packet/'authoritative_human_review_ledger_100.json');assert ledger['completed_total']==100 and ledger['remaining_total']==0;assert len(ledger['checks'])==len({r['check_id'] for r in ledger['checks']})==100;assert ledger['checks'][:80]==load(packet/'inputs/prior_80_check_ledger.json')['checks']
 assert (root/'assets/xml/antiquities/Latin/book-11.xml').read_bytes()==git('show',BASE+':assets/xml/antiquities/Latin/book-11.xml')
 return dict(result='PASS',immediate_baseline=BASE,development_baseline=DEV,final_checks_imported=20,confirmations=14,discrepancy_checks=6,new_authorized_actions=11,new_XML_files=6,modified_XML=xml,previous_203_actions='EXACTLY_PRESERVED',cumulative_actions=214,application_units=213,individual_and_combined_inverse='PASS',complete_v3_4_v3_5_inverse_to_development='PASS',Niese_ids_refs_divisions_layout_protected='PASS',Book_XI_Bellum_physical_order='BYTE_IDENTICAL',withheld_unreviewed_unchanged=9,conditional_XIII314_unchanged=True,pro_peregrina_and_VI219='EXACT',registration_hashes_seal_logic_coverage='PASS',unchanged_original_tracked_files=unchanged,production_XML=xmls,completed_human_checks=100,remaining_human_checks=0,new_checks_requested=0)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);a.add_argument('--packet',type=Path,default=Path(__file__).resolve().parents[1]);a.add_argument('--output',type=Path);p=a.parse_args();r=verify(p.root,p.packet)
 if p.output:p.output.parent.mkdir(parents=True,exist_ok=True);p.output.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps({k:v for k,v in r.items() if k not in ['production_XML','modified_XML']},indent=2))
