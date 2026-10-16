"""Read-only source-bound verification. Run from any checkout containing source Git objects.

Usage: python review/Bamberg_Editorial_Integration_v1_8/verify_staging.py --root .
No historical signed form is rewritten. Original bytes are read directly from Git.
"""
from pathlib import Path
import argparse,collections,copy,csv,hashlib,io,json,re,subprocess,xml.etree.ElementTree as ET
SOURCE='ef55e7ebd6e86d886341e8fbca8403d32dfc00ac'
BASE='f13613e2e5cfc857a15b61201711211be6506279'
ORIGINAL='review/Bamberg_Editorial_Integration_v1_7/'
PACKET='review/Bamberg_Editorial_Integration_v1_8/'
PROTECTED={'add','del','gap','unclear','supplied','abbr','expan','sic','orig','reg','choice','app','lem','rdg','corr','note'}
def sha(data):return hashlib.sha256(data).hexdigest()
def structure(data):
 root=ET.fromstring(data);nodes=[];protected=[];ids=[]
 def visit(e,path):
  nodes.append((path,e.tag,tuple(e.attrib.items())))
  if e.tag.split('}')[-1] in PROTECTED:protected.append((path,''.join(e.itertext())))
  if e.get('{http://www.w3.org/XML/1998/namespace}id'):ids.append(e.get('{http://www.w3.org/XML/1998/namespace}id'))
  for i,c in enumerate(e):visit(c,path+(i,))
 visit(root,());assert len(ids)==len(set(ids))
 return nodes,protected,re.findall(rb'<[^>]+>',data)
def check_edits(data,patches):
 last=0;pieces=[];undo=[];delta=0
 for p in sorted(patches,key=lambda p:(p['byte_start'],p['byte_end'])):
  a,b=p['byte_start'],p['byte_end'];old,new=bytes.fromhex(p['old_bytes_hex']),bytes.fromhex(p['new_bytes_hex'])
  assert sha(data)==p['baseline_sha256'] and a>=last and data[a:b]==old==p['old'].encode()
  assert new==p['new'].encode() and re.findall(rb'<[^>]+>',old)==re.findall(rb'<[^>]+>',new)
  assert not re.search(rb'<(?:num\b|milestone\s+unit="niese")',old)
  pieces.extend([data[last:a],new]);last=b;undo.append((a+delta,a+delta+len(new),old));delta+=len(new)-len(old)
 result=b''.join(pieces+[data[last:]]);assert structure(data)==structure(result)
 recovered=result
 for a,b,old in reversed(undo):recovered=recovered[:a]+old+recovered[b:]
 assert recovered==data
 return result
def verify(root):
 def git(*a):return subprocess.check_output(['git','-c','core.longpaths=true','--no-optional-locks',*a],cwd=root)
 def original(name):return git('show',SOURCE+':'+ORIGINAL+name)
 def packet(name):return json.loads((root/PACKET/name).read_text(encoding='utf-8'))
 manifest_bytes=original('approved_correction_manifest.json');m=json.loads(manifest_bytes);derived=packet('approved_correction_manifest.json')
 assert git('rev-parse',SOURCE+'^').decode().strip()==BASE==m['base_commit']==derived['development_baseline']
 assert sha(manifest_bytes)==derived['original_manifest_sha256']
 assert len(m['effects'])==19 and len(m['application_units'])==18
 assert len(derived['application_units'])==18
 by_unit={u['candidate_id']:u for u in m['application_units']}
 for unit in derived['application_units']:
  for key,value in unit.items():assert by_unit[unit['candidate_id']][key]==value
 assert len({p['candidate_id'] for p in m['effects']})==19
 assert {p['candidate_id'] for p in m['effects']}=={c for p in m['application_units'] for c in p['covered_candidate_ids']}
 ledger=list(csv.DictReader(io.StringIO(original('twenty_check_editorial_ledger.csv').decode('utf-8-sig'))));reviews={r['review_id']:r for r in ledger}
 assert len(ledger)==20 and all(r['completed_check'].lower()=='true' for r in ledger)
 derived_ledger=list(csv.DictReader((root/PACKET/'twenty_check_editorial_ledger.csv').open(encoding='utf-8-sig',newline='')))
 assert len(derived_ledger)==20
 for row in derived_ledger:
  for key,value in row.items():assert reviews[row['review_id']][key]==value
 for e in m['effects']:
  raw=original(e['signed_source_file']);assert sha(raw)==e['signed_source_sha256']
  row=next(r for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))) if r['review_id']==e['human_review_id'])
  assert row==e['signed_authorization'] and row['editor']=='RMP' and row['decision'].strip()
  assert e['human_confirmed'] and reviews[e['human_review_id']]['normalized_decision'].startswith('ACCEPT CORRECTION')
  d=next(p for p in derived['effects'] if p['candidate_id']==e['candidate_id'])
  for k in ['candidate_id','existing_reading','proposed_reading','human_review_id','signed_source_sha256','canonical_source_sha256','byte_start','byte_end']:assert d[k]==e[k]
  assert d['signed_row_sha256']==sha(json.dumps(row,sort_keys=True,ensure_ascii=False).encode())
 files=[];allowed=set()
 for book in sorted({p['book'] for p in m['application_units']}):
  rel=f'assets/xml/antiquities/Latin/book-{book:02}.xml';allowed.add(rel)
  before=git('show',BASE+':'+rel);actual=(root/rel).read_bytes();ps=[p for p in m['application_units'] if p['book']==book]
  assert actual==check_edits(before,ps)==git('show',SOURCE+':'+rel)
  for p in ps:check_edits(before,[p])
  files.append({'file':rel,'effects':sum(len(p['covered_candidate_ids']) for p in ps),'before_sha256':sha(before),'after_sha256':sha(actual),'XML_Niese_structure_ids_crossrefs_layout_and_protected_markup':'PASS','individual_and_combined_exact_inverse':'PASS'})
 assert b'quattuor <cb n="2/2"/>digitorum' in (root/'assets/xml/antiquities/Latin/book-12.xml').read_bytes()
 rel='_docs/reader-corpus-integrity.json';old=git('show',BASE+':'+rel);new=(root/rel).read_bytes();expected=json.loads(old)
 for f in files:expected['files'][f['file']]['allowed_worktree_sha256'].append(f['after_sha256'])
 assert json.loads(new)==expected and new==git('show',SOURCE+':'+rel)
 guard='bin/reader-corpus-integrity.mjs';old_guard=git('show',BASE+':'+guard);new_guard=(root/guard).read_bytes()
 assert old_guard.count(sha(old).encode())==1 and new_guard==old_guard.replace(sha(old).encode(),sha(new).encode())==git('show',SOURCE+':'+guard)
 allowed|={rel,guard}
 changed=set(git('diff','--name-only',BASE,'--').decode().splitlines())
 assert {p for p in changed if not p.startswith(PACKET)}==allowed
 # Every original tracked file outside the eleven-file authority whitelist is byte-identical.
 tree=git('ls-tree','-r','-z',BASE).split(b'\0');unchanged=0;total=0
 for entry in tree:
  if not entry:continue
  meta,name=entry.split(b'\t',1);rel=name.decode();mode,kind,oid=meta.decode().split();total+=1
  if rel in allowed:continue
  data=(root/rel).read_bytes();blob_oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  assert blob_oid==oid,rel;unchanged+=1
 # Read-only prospective patch checks. Nothing is written or promoted by a status.
 mech=packet('mechanical_compatibility.json');assert len(mech['proposals'])==72
 original_mech={r['candidate_id']:r for r in json.loads(original('mechanical_integration_readiness.json'))['proposals']}
 for p in mech['proposals']:
  assert p['patch']==original_mech[p['candidate_id']]['rebased_patch'] and p['status']==original_mech[p['candidate_id']]['status']
  data=(root/p['path']).read_bytes();check_edits(data,[p['patch']]);assert p['applied'] is False and p['integration_authorized'] is False
 for book in {p['book'] for p in mech['proposals']}:
  ps=[p for p in mech['proposals'] if p['book']==book];check_edits((root/ps[0]['path']).read_bytes(),[p['patch'] for p in ps])
 held=packet('withheld_substantive_compatibility.json');assert len(held['proposals'])==17
 original_held={r['candidate_id']:r for r in json.loads(original('withheld_substantive_register.json'))['proposals']}
 for p in held['proposals']:
  for key in ['candidate_id','book','niese','existing_reading','proposed_reading']:assert p[key]==original_held[p['candidate_id']][key]
  data=(root/p['path']).read_bytes();assert sha(data)==p['staging_source_sha256'] and data[p['staging_byte_start']:p['staging_byte_end']]==p['existing_reading'].encode()
  assert p['applied'] is False and p['integration_authorized'] is False
 hygiene=packet('source_commit_inventory_and_hygiene.json');assert len(hygiene['records'])==62
 for r in hygiene['records']:assert sha(git('show',SOURCE+':'+r['path']))==r['source_blob_sha256']
 # New promoted files must be text and portable; original signed evidence stays in source history.
 private=re.compile(r'(?i)(?<![a-z0-9])(?:[a-z]:[\\/]+|file:\/{3}|/'+r'home'+r'/[^/]+/|/'+r'Users'+r'/[^/]+/)')
 promoted=[]
 for p in sorted((root/PACKET).rglob('*')):
  if not p.is_file():continue
  assert p.suffix.lower() in {'.md','.json','.csv','.py','.diff','.txt','.mjs','.cjs'}
  raw=p.read_bytes();assert b'\0' not in raw and not private.search(raw.decode('utf-8-sig')),p.name
  promoted.append({'path':p.relative_to(root).as_posix(),'sha256':sha(raw),'bytes':len(raw)})
 frozen=root/PACKET/'FILE_MANIFEST.json'
 if frozen.exists():
  entries=json.loads(frozen.read_text(encoding='utf-8'))['files']
  assert {p['path'] for p in entries}=={p['path'] for p in promoted if not p['path'].endswith('/FILE_MANIFEST.json')}
  for entry in entries:assert sha((root/entry['path']).read_bytes())==entry['sha256']
 return {'result':'PASS','source_commit':SOURCE,'development_baseline':BASE,'baseline_drift':False,'signed_approved_effects':19,'application_units':18,'completed_human_checks':20,'production_files_exactly_equal_source_commit':11,'files':files,'integrity_manifest_sha256':sha(new),'integrity_guard_logic_and_coverage_unchanged':True,'unchanged_original_tracked_files':unchanged,'original_tracked_files':total,'Greek_translations_DEH_renderer_and_other_existing_files_unchanged':True,'mechanical_read_only_exact_reversible_checks':72,'mechanical_ready':57,'mechanical_requires_further_examination':15,'withheld_substantive_compatible':17,'unapproved_corrections_applied':0,'portable_review_inventory':promoted,'native_images_or_temporary_files_promoted':0}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('.'));a=parser.parse_args()
 print(json.dumps(verify(a.root.resolve()),ensure_ascii=False,indent=2))
