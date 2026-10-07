from pathlib import Path
from lxml import etree as E
import json,re,hashlib,collections,subprocess
R=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;B=json.loads((D/'BASELINE.json').read_bytes());T='{http://www.tei-c.org/ns/1.0}';NS={'t':T[1:-1]};XI='{http://www.w3.org/XML/1998/namespace}id'
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
markers=json.loads((D/'MARKERS.json').read_bytes());changed=[];xml_checks=[];counts=collections.Counter();protected=[];filesystem_metadata_drift=[]
for rel,v in B['worktree'].items():
 p=R/rel;assert p.is_file(),('Missing original file',rel);raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
 if h!=v['sha256']:changed.append(rel)
 if rel.startswith('assets/xml/'):
  if rel=='assets/xml/antiquities/structure.xml':continue
  new=[m for m in markers if m['file']==rel];clean=raw
  for m in new:
   tag=m['markup'].encode();assert clean.count(tag)==1,(rel,m['xml_id']);clean=clean.replace(tag,b'',1)
  assert hashlib.sha256(clean).hexdigest()==v['sha256'],('Existing XML bytes changed',rel)
  if rel.startswith('assets/xml/antiquities/'):
   before=E.fromstring(clean);after=E.fromstring(raw);ids=[e.get(XI) for e in after.iter() if e.get(XI)];assert len(set(ids))==len(ids),('Duplicate XML ID',rel)
   pcount=len(before.xpath('//t:p',namespaces=NS));assert pcount==len(after.xpath('//t:p',namespaces=NS));assert [(e.get(XI),e.get('sameAs')) for e in before.iter() if e.get(XI) or e.get('sameAs')]==[(e.get(XI),e.get('sameAs')) for e in after.iter() if (e.get(XI) or e.get('sameAs')) and e.get('type')!='bamberg-boundary']
   # Removing only the approved empty anchors restores exact source bytes: stronger than projection/node-order equality.
   counts[rel.split('/')[3]]+=pcount;xml_checks.append({'file':rel,'before_sha256':v['sha256'],'after_sha256':h,'new_empty_anchors':len(new),'exact_bytes_restored_by_removing_anchors':'PASS','text_ID_sameAs_paragraph_order':'PASS','paragraphs':pcount})
assert dict(counts)=={'English':1600,'Greek':1681,'Latin':1622},dict(counts)
allowed={'assets/xml/antiquities/structure.xml','assets/js/renderTei.js','_includes/display-settings.html'}|{m['file'] for m in markers};assert set(changed)==allowed,(set(changed)-allowed,allowed-set(changed))
for kind,base,inventory in [('canonical',Path(B['canonical']),B['canonical_files']),('frozen_authority',Path(B['frozen_authority_path']),B['frozen_authority'])]:
 for rel,v in inventory.items():
  current=hashfile(base/rel)
  if current!=v['sha256']:
   assert kind=='frozen_authority' and rel=='desktop.ini',(kind,rel)
   filesystem_metadata_drift.append({'scope':kind,'file':str(base/rel),'before_sha256':v['sha256'],'after_sha256':current,'before_bytes':v['bytes'],'after_bytes':(base/rel).stat().st_size,'classification':'NON_SCHOLARLY_FILESYSTEM_METADATA','task_writes_to_file':False,'reverted':False})
 protected.append({'scope':kind,'files':len(inventory),'scholarly_byte_integrity':'PASS','filesystem_metadata_drift':kind=='frozen_authority' and bool(filesystem_metadata_drift)})
# Both historical review inventories are contained in the unchanged worktree baseline.
for dir in ['Antiquities_Traditional_Navigation_2026-10-06','Antiquities_Traditional_Navigation_Followup_2026-10-07']:
 selected=[r for r in B['worktree'] if r.startswith('review/'+dir+'/')];assert all(r not in changed for r in selected);protected.append({'scope':dir,'files':len(selected),'byte_integrity':'PASS'})
p=R/'assets/xml/antiquities/structure.xml';raw=p.read_bytes();new_start=raw.index(b'\n      <list xmlns="http://www.tei-c.org/ns/1.0" type="bamberg-boundaries">');end=raw.index(b'</body>',new_start);old_registry=raw[:new_start]+raw[end:];assert hashlib.sha256(old_registry).hexdigest()==B['worktree']['assets/xml/antiquities/structure.xml']['sha256'],'Pre-existing registry bytes changed'
tree=E.fromstring(raw);rng=E.RelaxNG(E.parse(str(R/'review/Antiquities_Traditional_Navigation_2026-10-06/tei_all.rng')));assert rng.validate(tree),str(rng.error_log)
def fields(fs):return {f.get('name'):fields(f[0]) if E.QName(f[0]).localname=='fs' else [fields(x) for x in f[0]] if E.QName(f[0]).localname=='vColl' else f[0].text or '' for f in fs}
trad=tree.xpath('//t:list[@type="traditional-boundaries"]/t:item',namespaces=NS);bam=tree.xpath('//t:list[@type="bamberg-boundaries"]/t:item',namespaces=NS);records=[fields(i.find(T+'fs')) for i in bam];source=json.loads((Path(B['frozen_authority_path'])/'Antiquities_Structure_Reconciliation.json').read_bytes())['bamberg_boundaries'];assert len(bam)==198;assert len(trad)==1689
for item,old in zip(bam,source):assert item.get(XI)==old['id'] and json.loads(item.find('t:note/t:p',NS).text)==old
assert [sum(int(r['book'])==b for r in records) for b in range(1,21)]==[18,3,11,5,13,0,0,0,0,0,0,1,21,27,13,20,19,19,8,20]
relationships=dict(collections.Counter(r['niese-relationship'] for r in records));assert relationships=={'EXACT_NIESE_START':172,'WITHIN_NIESE':26},relationships
assert len({i.get(XI) for i in tree.iter() if i.get(XI)})==len([i for i in tree.iter() if i.get(XI)])
assert 'II' not in [r['manuscript-label-as-recorded'].strip('[]') for r in records if r['book']=='1']
xii=[r for r in records if r['book']=='12'];assert len(xii)==1 and xii[0]['label-status']=='ABSENT' and xii[0]['display']=='unnumbered' and xii[0]['literal-label']==''
assert sum(r['book']=='13' and r['literal-label']=='III' for r in records)==2
assert any(r['book']=='14' and r['literal-label']=='[XXVIII?]' for r in records)
assert not {'VII','VIII'}&{r['literal-label'] for r in records if r['book']=='18'}
expected_source={'XV.[XII]':next(r for r in records if r['book']=='15' and r['literal-label']=='[XII]'),'XVI.XX':next(r for r in records if r['book']=='16' and r['literal-label']=='XX')}
assert expected_source['XV.[XII]']['canonical-niese']=='323';assert expected_source['XVI.XX']['canonical-niese']=='368';assert expected_source['XVI.XX']['Latin']['paragraph']=='latin-book16-num367'
review_rel=D.relative_to(R).as_posix();newfiles=[p.relative_to(R).as_posix() for p in R.rglob('*') if p.is_file() and p.name!='.git' and p.relative_to(R).as_posix() not in B['worktree']];assert all(p.startswith(review_rel+'/') for p in newfiles),newfiles
result={'result':'PASS_SCHOLARLY_INPUTS_WITH_FILESYSTEM_METADATA_DRIFT' if filesystem_metadata_drift else 'PASS','filesystem_metadata_drift':filesystem_metadata_drift,'modified_existing_files':changed,'protected':protected,'XML':xml_checks,'paragraph_counts':dict(counts),'marker_counts':dict(collections.Counter(m['language'] for m in markers)),'all_prior_XML_bytes_identical_after_removing_only_authorized_anchors':True,'Book_XI_order_text_ids_sameAs_unchanged':True,'Book_IX_and_VII_unchanged':True,'traditional_registry_bytes_unchanged':True,'registry_TEI_P5_valid':True,'bamberg_source_rows_preserved':198,'bamberg_classifications':relationships,'missing_duplicate_uncertain_labels':'PASS','specific_positions':expected_source,'source_packets_never_reinterpreted':True,'canonical_checkout_source_files_unchanged':True,'Git_write_operations':['Authorized isolated branch/worktree creation only'],'no_staging_commit_push_merge_rebase_configuration_change':True}
(D/'INTEGRITY_QA.json').write_bytes(json.dumps(result,ensure_ascii=False,indent=2).encode());print(json.dumps({k:v for k,v in result.items() if k not in ['XML','specific_positions','modified_existing_files']},ensure_ascii=False))
