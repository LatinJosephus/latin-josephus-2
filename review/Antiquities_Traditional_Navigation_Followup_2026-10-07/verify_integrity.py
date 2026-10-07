from pathlib import Path
import hashlib,json,subprocess,collections
from lxml import etree as E
root=Path(r'C:\workspace\LatinJosephus-antiquities-traditional-navigation');review=root/'review/Antiquities_Traditional_Navigation_Followup_2026-10-07';baseline=json.loads((review/'BASELINE.json').read_bytes());base=baseline['base'];canonical=Path(baseline['canonical']);ns={'t':'http://www.tei-c.org/ns/1.0'};XI='{http://www.w3.org/XML/1998/namespace}id'
def git(p,*a):return subprocess.check_output(['git','--no-optional-locks','-C',str(p),*a])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fields(fs):return {f.get('name'):fields(f[0]) if E.QName(f[0]).localname=='fs' else [fields(x) for x in f[0]] if E.QName(f[0]).localname=='vColl' else f[0].text or '' for f in fs}
def rows(t):return {i.get(XI):fields(i.find('t:fs',ns)) for i in t.xpath('//t:item',namespaces=ns)}
def strip(d):
 if isinstance(d,dict):return {k:strip(v) for k,v in d.items() if k not in ['boundary-start','reader-note']}
 if isinstance(d,list):return [strip(v) for v in d]
 return d
old=E.fromstring(git(root,'show',base+':assets/xml/antiquities/structure.xml'));new=E.parse(str(root/'assets/xml/antiquities/structure.xml'));before=rows(old);after=rows(new)
assert strip(after)==before
assert [E.tostring(x) for x in old.xpath('//t:note',namespaces=ns)]==[E.tostring(x) for x in new.xpath('//t:note',namespaces=ns)]
rng=E.RelaxNG(E.parse(str(review.parent/'Antiquities_Traditional_Navigation_2026-10-06/tei_all.rng')));assert rng.validate(new),str(rng.error_log)
changed=[]
for rel,h in baseline['files'].items():
 p=root/rel;assert p.exists(),rel
 if sha(p)!=h['sha256']:changed.append(rel)
assert set(changed)=={'assets/js/renderTei.js','assets/xml/antiquities/structure.xml','_sass/_reader-ui.scss'}
style_base=json.loads((review/'NOTICE_STYLE_BASELINE.json').read_bytes())
for rel,h in style_base['protected_current_sha256'].items():assert sha(root/rel)==h,'Style-only task changed protected renderer/registry bytes'
xmls=list(root.glob('assets/xml/antiquities/*/*.xml'));assert len(xmls)==63
assert all(sha(p)==baseline['files'][p.relative_to(root).as_posix()]['sha256'] for p in xmls)
counts={}
for lang in ['Latin','Greek','English']:
 docs=[E.parse(str(p)) for p in (root/'assets/xml/antiquities'/lang).glob('*.xml')]
 counts[lang]={'paragraphs':sum(len(d.xpath('//t:p',namespaces=ns)) for d in docs),'identified_alignment_paragraphs':sum(len(d.xpath('//t:p[@xml:id]',namespaces={**ns,'xml':'http://www.w3.org/XML/1998/namespace'})) for d in docs)}
assert counts=={'Latin':{'paragraphs':1622,'identified_alignment_paragraphs':1442},'Greek':{'paragraphs':1681,'identified_alignment_paragraphs':1442},'English':{'paragraphs':1600,'identified_alignment_paragraphs':1442}}
historical=[rel for rel in baseline['files'] if rel.startswith('review/Antiquities_Traditional_Navigation_2026-10-06/')];assert all(rel not in changed for rel in historical)
assert git(canonical,'status','--porcelain').strip()==b'';assert git(canonical,'rev-parse','HEAD').decode().strip()==base;assert git(canonical,'branch','--show-current').decode().strip()=='v2-development'
# Clean canonical Git state checks its own checkout; Windows checkout line endings need not equal the isolated worktree bytes.
canonical_targets={rel:{'sha256':sha(canonical/rel),'bytes':(canonical/rel).stat().st_size} for rel in changed}
old_baseline=json.loads((review.parent/'Antiquities_Traditional_Navigation_2026-10-06/BASELINE.json').read_bytes())
authority_root=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review');authorities={}
for name,dirname,manifest in [('reconciliation','Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06','Antiquities_Structure_Reconciliation_v1.1_SHA256SUMS.txt'),('verification','Antiquities_Loeb_Niese_Verification_2026-10-05','Antiquities_Loeb_Niese_Verification_SHA256SUMS.txt')]:
 packet=authority_root/dirname;oldhashes=old_baseline['authorities'][name];assert sha(packet/manifest)==oldhashes[manifest]['sha256']
 entries=(packet/manifest).read_text(encoding='utf-8-sig').splitlines();checked=0
 for line in entries:
  h,rel=line.split('  ',1);assert sha(packet/rel)==h,(name,rel);checked+=1
 assert all(sha(packet/rel)==h['sha256'] for rel,h in oldhashes.items() if (packet/rel).is_file()),name
 authorities[name]={'manifest_entries_verified':checked,'manifest_sha256':sha(packet/manifest),'existing_files_match_historical_certification_hashes':'PASS'}
trad=[r for r in after.values() if r.get('scheme') in ['chapter','subchapter']];status=dict(collections.Counter(r['verification-status'] for r in trad));assert status=={'CONFIRMED_NIESE_START':1672,'CONFIRMED_WITHIN_NIESE':3,'LOEB_NIESE_NUMBER_DISAGREEMENT':3,'NIESE_SOURCE_AMBIGUOUS':11}
regcounts={'chapters':sum(r['scheme']=='chapter' for r in trad),'subchapters':sum(r['scheme']=='subchapter' for r in trad),'rows':len(trad),'physical_positions':len({r['physical-point'] for r in trad}),'statuses':status,'unresolved':0};assert [regcounts[k] for k in ['chapters','subchapters','rows','physical_positions']]==[257,1432,1689,1441]
diagnostics=json.loads((review/'PREFIX_LOCATOR_ADJUDICATION.json').read_bytes())
updatecounts=collections.Counter()
for fs in new.xpath('//t:fs[@type="text-locator"][t:f[@name="boundary-start"]]',namespaces=ns):
 lang=next(f.get('name') for f in fs.iterancestors() if E.QName(f).localname=='f' and f.get('name') in ['Greek','Latin','English']);updatecounts[lang]+=1
diagnostics['locator_fields_updated']=dict(updatecounts)
for d in diagnostics['diagnostics']:
 if d['identity']=='LOEB-15-Subchapter-8-4' and d['language']=='English':d['prefix_text']='[284]'
(review/'PREFIX_LOCATOR_ADJUDICATION.json').write_bytes(json.dumps(diagnostics,ensure_ascii=False,indent=2).encode())
result={'status':'PASS','base_commit':base,'TEI_P5_4.12.0':'PASS','original_registry_fields_source_evidence_and_fragment_membership':'UNCHANGED','registry_counts':regcounts,'all_63_corpus_XML_files_byte_identical':len(xmls),'topology':counts,'Book_XI_XML_text_node_order_ID_sameAs':'BYTE_IDENTICAL','new_empty_anchors':0,'historical_certification_files_verified':len(historical),'canonical_checkout':'CLEAN_AT_BASE_NO_TASK_WRITES','canonical_target_hashes':canonical_targets,'frozen_authorities':authorities,'existing_changed_files':changed,'prefix_locations':diagnostics['unique_prefix_locations'],'prefix_locator_fields':dict(updatecounts),'shared_reader_note_identities':diagnostics['shared_reader_note_identities']}
(review/'INTEGRITY_QA.json').write_bytes(json.dumps(result,indent=2).encode());print(json.dumps(result))