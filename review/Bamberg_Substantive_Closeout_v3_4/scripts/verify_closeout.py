"""Read-only v3.4 authorization, immutable structure and exact inverse QA.
Usage: python -B verify_closeout.py --root WORKTREE --packet PACKET
"""
from pathlib import Path
import argparse,json,csv,hashlib,subprocess,re,sys,xml.etree.ElementTree as ET
from preservation_guard import structure,protected_guard
BASE='f874b6a60f16c96f356abcbe070854611c49f2a3';CERT='35a474a5d8dcca627db6fb697c215decd0676cd6';PACK='review/Bamberg_Substantive_Closeout_v3_4/'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def append_hash_bytes(data,path,value):
 pattern=rb'("'+re.escape(path.encode())+rb'"\s*:\s*\{.*?"allowed_worktree_sha256"\s*:\s*\[)([^\]]*)(\])'
 matches=list(re.finditer(pattern,data,re.S));assert len(matches)==1
 m=matches[0];values=m[2];at=values.rfind(b'"')+1;assert at>0
 indent=re.search(rb'(?:\r?\n)([ \t]*)"[^"\r\n]+"\s*$',values).group(1)
 eol=re.search(rb'\r?\n',values).group();insert=b','+eol+indent+b'"'+value.encode()+b'"'
 pos=m.start(2)+at;return data[:pos]+insert+data[pos:]
def verify(root,packet):
 def git(*a):return subprocess.check_output(['git','-c','core.longpaths=true','--no-optional-locks','-C',str(root),*a])
 manifest=load(packet/'approved_correction_manifest.json');ps=manifest['actions'];rec=load(packet/'reconciliation_manifest.json')['records'];byid={p['candidate_id']:p for p in rec}
 sources=load(packet/'decision_import_certificate.json')['sources'];exports=[{r['candidate_id']:r for r in csv.DictReader((packet/s['file']).open(encoding='utf-8-sig',newline=''))} for s in sources]
 assert len(exports[0])==len(exports[1])==56
 for ident,r in exports[0].items():
  if r['decision']=='ACCEPT CORRECTION':
   assert all(exports[1][ident][f]==r[f] for f in ['decision','editorial_comments','editorial_amended_reading','response_recorded_utc'])
 for r in rec:
  signed=exports[1][r['candidate_id']];assert signed['question_id']==r['candidate_id']
  assert all(str(r[k])==signed[k] for k in ['book','niese','folio'])
  assert r['original_reading']==signed['current_reading'] and r['decision_verbatim']==signed['decision']
  assert r['editorial_comment_verbatim']==signed['editorial_comments'] and r['editorial_amended_reading_verbatim']==signed['editorial_amended_reading']
  if not r['withheld_reason']:
   assert r['approved_replacement']==signed['proposed_reading'] and not signed['editorial_amended_reading']
   assert r['source_bound_patch']['registered_original']==signed['current_reading'] and r['source_bound_patch']['registered_replacement']==signed['proposed_reading']
 assert len(ps)==len({p['candidate_id'] for p in ps})==46
 assert sum(p['decision_verbatim']=='ACCEPT CORRECTION' for p in rec)==47 and len(rec)==56
 inv=load(packet/'patches/exact_reversible_changes.json');changed={r['path'] for r in inv['files']};xml=[];old={};new={}
 for r in inv['files']:
  rel=r['path'];a=git('show',BASE+':'+rel);b=(root/rel).read_bytes();assert sha(a)==r['before_sha256'] and sha(b)==r['after_sha256'];old[rel]=a;new[rel]=b
  restored=b
  for op in reversed(r['exact_operations']):
   x,y=op['after_start'],op['after_end'];assert restored[x:y]==bytes.fromhex(op['new_hex']);assert a[op['before_start']:op['before_end']]==bytes.fromhex(op['old_hex']);restored=restored[:x]+bytes.fromhex(op['old_hex'])+restored[y:]
  assert restored==a
  if not rel.endswith('.xml'):continue
  assert a==git('show',CERT+':'+rel);assert structure(a)==structure(b);ET.fromstring(b)
  parts=[];last=0
  for p in sorted((p for p in ps if p['source_path']==rel),key=lambda p:p['byte_start']):
   x,y=p['byte_start'],p['byte_end'];assert x>=last and a[x:y]==bytes.fromhex(p['old_bytes_hex']);assert sha(a)==p['baseline_sha256'];assert not protected_guard(a,x,y)['blocked'];assert byid[p['candidate_id']]['decision_verbatim']=='ACCEPT CORRECTION';assert byid[p['candidate_id']]['implementation_status'] in ['APPROVED AND IMPLEMENTABLE','APPROVED WITH AMENDMENT']
   # Exact patch authority is source-bound, rather than a dictionary transformation.
   assert p==byid[p['candidate_id']]['source_bound_patch'];assert re.findall(rb'<[^>]+>',p['old'].encode())==re.findall(rb'<[^>]+>',p['new'].encode());parts.extend([a[last:x],bytes.fromhex(p['new_bytes_hex'])]);last=y
   individual=a[:x]+bytes.fromhex(p['new_bytes_hex'])+a[y:];assert structure(individual)==structure(a);assert individual[:x]+a[x:y]+individual[x+len(bytes.fromhex(p['new_bytes_hex'])):]==a
  assert b''.join(parts+[a[last:]])==b
  xml.append(dict(path=rel,before_sha256=sha(a),after_sha256=sha(b),structure_Niese_ids_refs_divisions_layout_protected='PASS'))
 # Every previous action survives at its translated exact current source span.
 cumulative=load(packet/'cumulative_correction_inventory.json');assert cumulative['actions_count']==203 and cumulative['application_units_count']==202
 assert len(cumulative['actions'])==len({p['candidate_id'] for p in cumulative['actions']})==203
 assert len({(p['book'],p['current_byte_start'],p['current_byte_end'],p['current_bytes_hex']) for p in cumulative['actions']})==202
 for p in cumulative['actions']:
  rel=f'assets/xml/antiquities/Latin/book-{p["book"]:02}.xml';data=(root/rel).read_bytes();assert sha(data)==p['current_source_sha256'];assert data[p['current_byte_start']:p['current_byte_end']]==bytes.fromhex(p['current_bytes_hex']),p['candidate_id']
 assert sum(p.get('v3_4_status')=='PREVIOUSLY_INTEGRATED_PRESERVED' for p in cumulative['actions'])==157
 for p in rec:
  if not p['withheld_reason']:continue
  q=p['source_bound_patch'];rel=p['source_path'];a=old.get(rel,git('show',BASE+':'+rel));x,y=q['byte_start'],q['byte_end'];assert a[x:y]==bytes.fromhex(q['old_bytes_hex']);pp=[r for r in ps if r['source_path']==rel];assert not any(x<r['byte_end'] and y>r['byte_start'] for r in pp);delta=sum(len(bytes.fromhex(r['new_bytes_hex']))-len(bytes.fromhex(r['old_bytes_hex'])) for r in pp if r['byte_end']<=x);assert (root/rel).read_bytes()[x+delta:y+delta]==a[x:y]
 assert b'a suo feruore pro peregrina recederent' in (root/'assets/xml/antiquities/Latin/book-05.xml').read_bytes()
 assert b'necessitatis causa, non uoluntatis causa et non uoluntatis efficerit' in (root/'assets/xml/antiquities/Latin/book-06.xml').read_bytes()
 reg='_docs/reader-corpus-integrity.json';expected=json.loads(old[reg]);expected_bytes=old[reg]
 for r in xml:
  expected['files'][r['path']]['allowed_worktree_sha256'].append(r['after_sha256']);expected_bytes=append_hash_bytes(expected_bytes,r['path'],r['after_sha256'])
 assert json.loads(new[reg])==expected
 assert new[reg]==expected_bytes,'Only fourteen hash registrations may change; retain all inherited mixed line endings.'
 guard='bin/reader-corpus-integrity.mjs';assert new[guard]==old[guard].replace(sha(old[reg]).encode(),sha(new[reg]).encode());assert old[guard].count(sha(old[reg]).encode())==1
 unchanged=0
 for rel,h in load(packet/'inputs/staging_original_tracked_hashes.json').items():
  if rel not in changed:assert sha((root/rel).read_bytes())==h,rel;unchanged+=1
 actual=set(git('diff','--name-only',BASE,'--').decode().splitlines());assert {p for p in actual if not p.startswith(PACK)}==changed
 # All 166 production XML files parse; unchanged witnesses retain exact bytes.
 xmlfiles=[]
 for p in sorted((root/'assets/xml').rglob('*.xml')):
  ET.parse(p);xmlfiles.append(dict(path=p.relative_to(root).as_posix(),sha256=sha(p.read_bytes())))
 assert len(xmlfiles)==166
 xi='assets/xml/antiquities/Latin/book-11.xml';assert structure(git('show',BASE+':'+xi))==structure((root/xi).read_bytes())
 for s in load(packet/'decision_import_certificate.json')['sources']:assert sha((packet/s['file']).read_bytes())==s['sha256']
 return dict(result='PASS',immediate_baseline=BASE,certified_XML_baseline=CERT,approved_decisions=47,new_staged_actions=46,withheld_conditional_XIII314=1,unreviewed_unchanged=9,previous_actions_preserved=157,cumulative_actions=203,application_units=202,modified_XML=xml,production_XML=xmlfiles,individual_combined_exact_inverse='PASS',Niese_ids_refs_divisions_layout_protected='PASS',Book_XI_physical_order_Bellum='PRESERVED',integrity_logic_seal_coverage='PASS',unrelated_tracked_files_unchanged=unchanged,pro_peregrina_and_VI219='PRESERVED',new_human_checks=0)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--packet',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path);a=p.parse_args();r=verify(a.root.resolve(),a.packet.resolve());s=json.dumps(r,indent=2)+'\n';print(s)
 if a.output:a.output.write_text(s,encoding='utf-8')
