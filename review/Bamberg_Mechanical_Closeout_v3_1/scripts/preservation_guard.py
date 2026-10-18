"""Read-only verification of the separately authorized mechanical tranche."""
from pathlib import Path
import argparse,collections,copy,csv,hashlib,html,json,re,subprocess,unicodedata,xml.etree.ElementTree as ET
BASE='8f841d527780a3d23c73f7aa220f718c57239dda'
PACKET='review/Bamberg_Editorial_Integration_v1_9/'
PROTECTED={'add','del','gap','unclear','supplied','abbr','expan','sic','orig','reg','choice','app','lem','rdg','corr','note'}
def sha(data):return hashlib.sha256(data).hexdigest()
def structure(data):
 root=ET.fromstring(data);nodes=[];protected=[];ids=[]
 def visit(e,path):
  nodes.append((path,e.tag,tuple(e.attrib.items())))
  if e.tag.split('}')[-1] in PROTECTED:protected.append((path,''.join(e.itertext())))
  ident=e.get('{http://www.w3.org/XML/1998/namespace}id')
  if ident:ids.append(ident)
  for i,c in enumerate(e):visit(c,path+(i,))
 visit(root,());assert len(ids)==len(set(ids))
 return nodes,protected,re.findall(rb'<[^>]+>',data)
def protected_guard(data,a,b):
 """Expand source span to complete adjacent projected tokens without Unicode normalization."""
 text=data.decode('utf-8');charbytes=[0]
 for c in text:charbytes.append(charbytes[-1]+len(c.encode()))
 projection=[];ranges=[];protected=[];stack=[]
 for m in re.finditer(r'<[^>]*>|[^<]+',text):
  value=m.group()
  if value.startswith('<'):
   nm=re.match(r'</?([\w:.-]+)',value)
   if not nm:continue
   name=nm[1].split(':')[-1]
   if value.startswith('</'):
    assert stack and stack[-1][0]==name
    n,start=stack.pop()
    if n in PROTECTED:protected.append((charbytes[start],charbytes[m.end()],n))
   elif value.endswith('/>'):
    if name in PROTECTED:protected.append((charbytes[m.start()],charbytes[m.end()],name))
   else:stack.append((name,m.start()))
  else:
   for entity in re.finditer(r'&[^;]+;|[^&]',value):
    start=m.start()+entity.start();end=m.start()+entity.end()
    for c in html.unescape(entity.group()):projection.append(c);ranges.append((charbytes[start],charbytes[end]))
 indices=[i for i,(x,y) in enumerate(ranges) if x<b and y>a]
 before=[i for i,(x,y) in enumerate(ranges) if y<=a];after=[i for i,(x,y) in enumerate(ranges) if x>=b]
 if indices:lo,hi=min(indices),max(indices)
 else:
  assert before and after
  lo,hi=before[-1],after[0]
 def word(c):return c.isalnum() or unicodedata.category(c).startswith('M')
 while lo>0 and word(projection[lo-1]):lo-=1
 while hi+1<len(projection) and word(projection[hi+1]):hi+=1
 ra,rb=ranges[lo][0],ranges[hi][1];hits=[{'start':x,'end':y,'tag':n} for x,y,n in protected if x<rb and y>ra]
 return {'blocked':bool(hits),'whole_token_source_byte_span':[ra,rb],'protected_hits':hits,'Unicode_normalization_applied':False}
def check_edits(data,patches):
 last=0;pieces=[];undo=[];delta=0
 for p in sorted(patches,key=lambda p:(p['byte_start'],p['byte_end'])):
  a,b=p['byte_start'],p['byte_end'];old,new=bytes.fromhex(p['old_bytes_hex']),bytes.fromhex(p['new_bytes_hex'])
  assert sha(data)==p['baseline_sha256'] and a>=last and data[a:b]==old==p['old'].encode()
  assert new==p['new'].encode() and old!=new
  assert re.findall(rb'<[^>]+>',old)==re.findall(rb'<[^>]+>',new)
  assert re.sub(rb'\s+',b'',old)==re.sub(rb'\s+',b'',new)
  assert not re.search(rb'<(?:num\b|milestone\s+unit="niese")',old)
  assert not protected_guard(data,a,b)['blocked']
  pieces.extend([data[last:a],new]);last=b;undo.append((a+delta,a+delta+len(new),old));delta+=len(new)-len(old)
 result=b''.join(pieces+[data[last:]]);assert structure(data)==structure(result)
 assert re.sub(rb'\s+',b'',data)==re.sub(rb'\s+',b'',result)
 recovered=result
 for a,b,old in reversed(undo):recovered=recovered[:a]+old+recovered[b:]
 assert recovered==data
 return result
def verify(root):
 def git(*a):return subprocess.check_output(['git','-c','core.longpaths=true','--no-optional-locks',*a],cwd=root)
 def load(n):return json.loads((root/PACKET/n).read_text(encoding='utf-8'))
 manifest=load('mechanical_integration_manifest.json');evidence=load('evidence_inventory.json');sources={r['candidate_id']:r for r in evidence['records']}
 original=json.loads(git('show',BASE+':review/Bamberg_Editorial_Integration_v1_8/mechanical_compatibility.json'))
 allowed={r['candidate_id']:r for r in original['proposals'] if r['status'].startswith('READY')}
 assert len(allowed)==57 and set(p['candidate_id'] for p in manifest['applied_patches'])<=set(allowed)
 assert len({p['candidate_id'] for p in manifest['applied_patches']})==len(manifest['applied_patches'])
 for p in manifest['applied_patches']:
  assert p==allowed[p['candidate_id']]['patch']
  r=sources[p['candidate_id']];assert r['v1_9_visual_revalidation']['reviewed'] and r['crop_hashes_verified'] and r['native_sources_verified'] and r['TPEN_exact_pair_verified']
  assert r['v1_9_integration_authorized'] and r['source_status'].startswith('READY')
 files=[];changes=set()
 for book in sorted({p['book'] for p in manifest['applied_patches']}):
  rel=f'assets/xml/antiquities/Latin/book-{book:02}.xml';before=git('show',BASE+':'+rel);ps=[p for p in manifest['applied_patches'] if p['book']==book];actual=(root/rel).read_bytes()
  assert actual==check_edits(before,ps)
  for p in ps:check_edits(before,[p])
  changes.add(rel);files.append({'file':rel,'patches':len(ps),'before_sha256':sha(before),'after_sha256':sha(actual),'parse_Niese_ids_divisions_layout_crossrefs_protected_markup':'PASS','individual_and_combined_exact_inverse':'PASS','all_nonwhitespace_bytes_unchanged':True})
 reg='_docs/reader-corpus-integrity.json';before=git('show',BASE+':'+reg);actual=(root/reg).read_bytes();expected=json.loads(before)
 for f in files:
  entry=expected['files'][f['file']]['allowed_worktree_sha256'];assert f['after_sha256'] not in entry;entry.append(f['after_sha256'])
 assert json.loads(actual)==expected
 guard='bin/reader-corpus-integrity.mjs';old=git('show',BASE+':'+guard);new=(root/guard).read_bytes();assert old.count(sha(before).encode())==1
 assert new==old.replace(sha(before).encode(),sha(actual).encode())
 inverse=load('exact_reversible_changes.json');assert len(inverse['files'])==len(changes)+2
 for f in inverse['files']:
  baseline=git('show',BASE+':'+f['path']);current=(root/f['path']).read_bytes();assert sha(baseline)==f['before_sha256'] and sha(current)==f['after_sha256']
  recovered=current;last=len(current)+1
  for op in reversed(f['exact_operations']):
   a,b=op['after_start'],op['after_end'];assert b<last and current[a:b]==bytes.fromhex(op['new_hex']);assert baseline[op['before_start']:op['before_end']]==bytes.fromhex(op['old_hex'])
   recovered=recovered[:a]+bytes.fromhex(op['old_hex'])+recovered[b:];last=a
  assert recovered==baseline
 changes|={reg,guard};changed=set(git('diff','--name-only',BASE,'--').decode().splitlines());assert {p for p in changed if not p.startswith(PACKET)}==changes
 unchanged=0
 for entry in git('ls-tree','-r','-z',BASE).split(b'\0'):
  if not entry:continue
  meta,name=entry.split(b'\t',1);rel=name.decode()
  if rel in changes:continue
  data=(root/rel).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==meta.decode().split()[-1],rel;unchanged+=1
 # Preserve every old editorial and substantive register byte-for-byte; test new location bindings.
 held=load('outstanding_fifteen_investigation.json');assert len(held['records'])==15 and held['applied']==0
 assert not set(p['candidate_id'] for p in manifest['applied_patches']) & {p['candidate_id'] for p in held['records']}
 prior=json.loads(git('show',BASE+':review/Bamberg_Editorial_Integration_v1_8/withheld_substantive_compatibility.json'))
 held_compatible=0;substantive_compatible=0
 for p in held['records']:
  q=p['patch'];offset=sum(len(x['new'].encode())-len(x['old'].encode()) for x in manifest['applied_patches'] if x['book']==p['book'] and x['byte_end']<=q['byte_start'])
  assert not any(q['byte_start']<x['byte_end'] and q['byte_end']>x['byte_start'] for x in manifest['applied_patches'] if x['book']==p['book'])
  data=(root/f'assets/xml/antiquities/Latin/book-{p["book"]:02}.xml').read_bytes();assert data[q['byte_start']+offset:q['byte_end']+offset]==q['old'].encode();held_compatible+=1
 for p in prior['proposals']:
  a,b=p['staging_byte_start'],p['staging_byte_end'];ps=[x for x in manifest['applied_patches'] if x['book']==p['book']]
  assert not any(a<x['byte_end'] and b>x['byte_start'] for x in ps)
  delta=sum(len(x['new'].encode())-len(x['old'].encode()) for x in ps if x['byte_end']<=a)
  data=(root/p['path']).read_bytes();assert data[a+delta:b+delta]==p['existing_reading'].encode();substantive_compatible+=1
 assert substantive_compatible==17 and held_compatible==15
 prior_effects=0
 for p in manifest['prior_human_approved_protected_spans']:
  a,b=p['base_byte_start'],p['base_byte_end'];baseline=git('show',BASE+':'+p['path']);assert baseline[a:b]==p['approved_reading'].encode()
  ps=[x for x in manifest['applied_patches'] if x['book']==p['book']];assert not any(a<x['byte_end'] and b>x['byte_start'] for x in ps)
  shift=sum(len(x['new'].encode())-len(x['old'].encode()) for x in ps if x['byte_end']<=a)
  assert (root/p['path']).read_bytes()[a+shift:b+shift]==p['approved_reading'].encode();prior_effects+=len(p['candidate_ids'])
 assert prior_effects==19
 freeze=root/PACKET/'FILE_MANIFEST.json'
 if freeze.exists():
  for r in json.loads(freeze.read_text())['files']:assert sha((root/r['path']).read_bytes())==r['sha256']
 return {'result':'PASS','base_commit':BASE,'mechanical_corrections':len(manifest['applied_patches']),'XML_files':len(files),'files':files,'integrity_manifest_sha256':sha(actual),'validation_logic_and_corpus_coverage_unchanged':True,'unchanged_original_tracked_files':unchanged,'original_19_approved_effects_exactly_preserved':prior_effects,'complete_eight_file_exact_inverse':'PASS','held_fifteen_not_applied':held_compatible,'substantive_seventeen_not_applied':substantive_compatible,'new_human_checks':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));a=p.parse_args();print(json.dumps(verify(a.root.resolve()),indent=2))
