"""Read-only source-bound verification for the exclusive fifteen-case integration."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,re,subprocess
BASE='865bc6e228c27ba9859d030e50d50f79eb6f222a'
V18='8f841d527780a3d23c73f7aa220f718c57239dda'
DEVELOPMENT_BASE='f13613e2e5cfc857a15b61201711211be6506279'
PACKET='review/Bamberg_Editorial_Integration_v2_0/'
XML='assets/xml/antiquities/Latin/book-13.xml'
AUTHORIZED={'M14-B13-48004f243c':120,'M14-B13-477cdb858d':154,'M14-B13-c028dee2a1':225,'M14-B13-7899741b9f':232,'M14-B13-d5f6ea1941':247,'M14-B13-e406f2ca6b':263,'M14-B13-c0abf9e4f3':271,'M14-B13-30b81dc20e':293,'M14-B13-204148f34e':327,'M14-B13-a7f1a6a8f5':341,'M14-B13-f5fa29f54e':358,'M14-B13-db4aa6b6c3':394,'M14-B13-5487ad9420':408,'M14-B13-b4dbbb3471':414,'M14-B13-429234a8fe':430}
spec=importlib.util.spec_from_file_location('preserved_mechanical_guard',Path(__file__).resolve().parents[1]/'Bamberg_Editorial_Integration_v1_9/verify_mechanical.py');guardlib=importlib.util.module_from_spec(spec);spec.loader.exec_module(guardlib)
def sha(x):return hashlib.sha256(x).hexdigest()
def section_at(data,offset):
 section=0
 for m in re.finditer(rb'<milestone\b[^>]*unit="niese"[^>]*/>|<num\b[^>]*>.*?</num>',data[:offset],re.S):
  if m.group().startswith(b'<num'):section=int(re.findall(rb'\d+',m.group())[-1])
  else:section=int(re.search(rb'\bn="(\d+)"',m.group())[1])
 return section
def apply_fifteen(data,patches):
 assert len(patches)==15 and {p['candidate_id']:p['niese'] for p in patches}==AUTHORIZED
 assert len({p['byte_start'] for p in patches})==15
 for p in patches:
  a=p['byte_start'];assert p['book']==13 and p['baseline_sha256']==sha(data)
  assert p['byte_end']==a and p['old']=='' and p['new']==' ' and p['old_bytes_hex']=='' and p['new_bytes_hex']=='20'
  assert data[a:a+len(p['marker'].encode())]==p['marker'].encode()
  assert re.fullmatch(r'<(?:pb|cb)\b[^>]*/>',p['marker']) and section_at(data,a)==p['niese']
  left=re.sub(rb'<[^>]+>',b'',data[:a]).decode();right=re.sub(rb'<[^>]+>',b'',data[a:]).decode()
  assert left.endswith(p['left_word']) and right.startswith(p['right_word'])
  assert not guardlib.protected_guard(data,a,a)['blocked']
 result=guardlib.check_edits(data,patches)
 assert len(result)==len(data)+15 and guardlib.structure(data)==guardlib.structure(result)
 assert re.sub(rb'\s+',b'',result)==re.sub(rb'\s+',b'',data)
 return result
def prior_spans(git):
 m=json.loads(git('show',BASE+':review/Bamberg_Editorial_Integration_v1_9/mechanical_integration_manifest.json'));out=[]
 for p in m['prior_human_approved_protected_spans']:
  ps=[q for q in m['applied_patches'] if q['book']==p['book']];delta=sum(len(q['new'].encode())-len(q['old'].encode()) for q in ps if q['byte_end']<=p['base_byte_start'])
  out.append({'book':p['book'],'path':p['path'],'start':p['base_byte_start']+delta,'end':p['base_byte_end']+delta,'reading':p['approved_reading'],'candidate_ids':p['candidate_ids'],'class':'HUMAN_APPROVED'})
 for book in sorted({p['book'] for p in m['applied_patches']}):
  delta=0
  for p in sorted([q for q in m['applied_patches'] if q['book']==book],key=lambda q:q['byte_start']):
   a=p['byte_start']+delta;out.append({'book':book,'path':f'assets/xml/antiquities/Latin/book-{book:02}.xml','start':a,'end':a+len(p['new'].encode()),'reading':p['new'],'candidate_ids':[p['candidate_id']],'class':'MECHANICAL_V1_9'});delta+=len(p['new'].encode())-len(p['old'].encode())
 assert sum(len(p['candidate_ids']) for p in out)==76
 return out
def verify(root):
 def git(*a):return subprocess.check_output(['git','-c','core.longpaths=true','--no-optional-locks',*a],cwd=root)
 def load(n):return json.loads((root/PACKET/n).read_text(encoding='utf-8'))
 m=load('fifteen_applied_manifest.json');ps=m['patches'];original=json.loads(git('show',BASE+':review/Bamberg_Editorial_Integration_v1_9/outstanding_fifteen_investigation.json'))
 assert {p['candidate_id']:p['niese'] for p in original['records']}==AUTHORIZED
 before=git('show',BASE+':'+XML);after=(root/XML).read_bytes();assert after==apply_fifteen(before,ps)
 previous=json.loads(git('show',BASE+':review/Bamberg_Editorial_Integration_v1_9/mechanical_integration_manifest.json'))
 for p in ps:
  src=next(r for r in original['records'] if r['candidate_id']==p['candidate_id']);assert p['selected_TPEN_pair'] in src['fresh_TPEN_search']['exact_pairs']
  old=src['patch'];expected_a=old['byte_start']+sum(len(q['new'].encode())-len(q['old'].encode()) for q in previous['applied_patches'] if q['book']==13 and q['byte_end']<=old['byte_start'])
  assert p['byte_start']==expected_a and p['marker']==old['old'] and p['left_word']==src['left_fragment'] and p['right_word']==src['right_fragment']
  assert p['source_candidate_record_sha256']==sha(json.dumps(src,ensure_ascii=False,sort_keys=True).encode())
  assert p['source_image_and_TPEN_checks']=='PASS' and p['v2_visual_confirmation'] is True
  single=guardlib.check_edits(before,[p]);assert len(single)==len(before)+1
 prior_effects=0
 for p in prior_spans(git):
  data=git('show',BASE+':'+p['path']);assert data[p['start']:p['end']]==p['reading'].encode()
  insertions=ps if p['book']==13 else [];assert not any(p['start']<=q['byte_start']<p['end'] for q in insertions)
  shift=sum(q['byte_start']<=p['start'] for q in insertions);current=(root/p['path']).read_bytes();assert current[p['start']+shift:p['end']+shift]==p['reading'].encode();prior_effects+=len(p['candidate_ids'])
 assert prior_effects==76
 reg='_docs/reader-corpus-integrity.json';old=git('show',BASE+':'+reg);new=(root/reg).read_bytes();expected=json.loads(old);expected['files'][XML]['allowed_worktree_sha256'].append(sha(after));assert json.loads(new)==expected
 guard='bin/reader-corpus-integrity.mjs';g0=git('show',BASE+':'+guard);g1=(root/guard).read_bytes();assert g0.count(sha(old).encode())==1 and g1==g0.replace(sha(old).encode(),sha(new).encode())
 allowed={XML,reg,guard};changed=set(git('diff','--name-only',BASE,'--').decode().splitlines());assert {p for p in changed if not p.startswith(PACKET)}==allowed
 n=0
 for entry in git('ls-tree','-r','-z',BASE).split(b'\0'):
  if not entry:continue
  meta,name=entry.split(b'\t',1);rel=name.decode()
  if rel in allowed:continue
  data=(root/rel).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==meta.decode().split()[-1],rel;n+=1
 for f in load('exact_reversible_changes.json')['files']:
  baseline=git('show',BASE+':'+f['path']);current=(root/f['path']).read_bytes();assert sha(baseline)==f['before_sha256'] and sha(current)==f['after_sha256'];recovered=current
  for op in reversed(f['operations']):
   a,b=op['after_start'],op['after_end'];assert current[a:b]==bytes.fromhex(op['new_hex']);recovered=recovered[:a]+bytes.fromhex(op['old_hex'])+recovered[b:]
  assert recovered==baseline
 cumulative=load('cumulative_91_action_manifest.json');assert len(cumulative['actions'])==len({r['candidate_id'] for r in cumulative['actions']})==91
 assert cumulative['counts']=={'human_approved_v1_8':19,'mechanical_v1_9':57,'mechanical_v2_0':15}
 human=json.loads(git('show',BASE+':review/Bamberg_Editorial_Integration_v1_8/approved_correction_manifest.json'));by={p['candidate_id']:p for p in cumulative['actions']}
 for src in human['effects']+previous['applied_patches']:
  for key,value in src.items():assert by[src['candidate_id']][key]==value
 for src in ps:
  for key in ['candidate_id','book','niese','baseline_sha256','byte_start','byte_end','old','new','old_bytes_hex','new_bytes_hex']:assert by[src['candidate_id']][key]==src[key]
 for p in cumulative['actions']:
  data=(root/f'assets/xml/antiquities/Latin/book-{p["book"]:02}.xml').read_bytes()
  assert p['applied_locally'] is True and sha(data)==p['current_source_sha256']
  assert data[p['current_application_byte_start']:p['current_application_byte_end']]==bytes.fromhex(p['current_application_bytes_hex'])
 withheld=load('withheld_substantive_register.json');assert len(withheld['proposals'])==17
 for p in withheld['proposals']:
  current=(root/p['path']).read_bytes();assert sha(current)==p['current_source_sha256'] and current[p['current_byte_start']:p['current_byte_end']]==p['existing_reading'].encode()
  assert p['applied'] is False and p['integration_authorized'] is False
 if (root/PACKET/'FILE_MANIFEST.json').exists():
  for f in load('FILE_MANIFEST.json')['files']:assert sha((root/f['path']).read_bytes())==f['sha256']
 return {'result':'PASS','immediate_reversal_baseline':BASE,'original_development_baseline':DEVELOPMENT_BASE,'new_separator_actions':15,'prior_actions_preserved':prior_effects,'cumulative_actions':91,'Book_XIII_before_sha256':sha(before),'Book_XIII_after_sha256':sha(after),'inserted_bytes':15,'XML_Niese_IDs_divisions_foliation_layout_protected_markup':'PASS','individual_and_combined_inverse':'PASS','all_three_production_files_exact_inverse':'PASS','integrity_manifest_sha256':sha(new),'guard_logic_coverage_and_all_other_XML_hashes_unchanged':True,'unchanged_original_tracked_files':n,'withheld_substantive_proposals_preserved':17,'new_human_checks':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));a=p.parse_args();print(json.dumps(verify(a.root.resolve()),indent=2))
