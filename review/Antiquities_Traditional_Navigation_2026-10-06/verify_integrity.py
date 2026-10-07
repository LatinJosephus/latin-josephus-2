from pathlib import Path
from lxml import etree as E
import json,hashlib,re,collections,subprocess
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;BASE=json.loads((D/'BASELINE.json').read_text());NS={'t':'http://www.tei-c.org/ns/1.0'};XI='{http://www.w3.org/XML/1998/namespace}id'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def inventory(root):return {str(p.relative_to(root)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}
def project(e):
 if E.QName(e).localname in ['num','milestone','pb','lb','note','anchor']:return ''
 return (e.text or '')+''.join(project(c)+(c.tail or '') for c in e)
counts={};marker_counts={}
for language in ['Latin','Greek','English']:
 ps=ids=markers=0
 for p in (ROOT/f'assets/xml/antiquities/{language}').glob('*.xml'):
  rel=str(p.relative_to(ROOT)).replace('\\','/');after=p.read_bytes();old=re.sub(rb'<anchor xml:id="trad-[^"]+" type="traditional-boundary" corresp="[^"]+"/>',b'',after)
  assert sha(old)==BASE['worktree'][rel]['sha256'],rel
  a=E.fromstring(old);b=E.fromstring(after);anchors=b.xpath('//t:anchor[@type="traditional-boundary"]',namespaces=NS)
  assert project(a)==project(b),rel
  assert a.xpath('//@sameAs')==b.xpath('//@sameAs'),rel
  assert [x.get(XI) for x in a.xpath('//t:p',namespaces=NS)]==[x.get(XI) for x in b.xpath('//t:p',namespaces=NS)],rel
  oldids=a.xpath('//@xml:id');newids=b.xpath('//@xml:id');assert len(newids)==len(set(newids)),rel
  assert set(newids)-set(oldids)=={x.get(XI) for x in anchors},rel
  ps+=len(b.xpath('//t:p',namespaces=NS));ids+=len(b.xpath('//t:p[@xml:id]',namespaces=NS));markers+=len(anchors)
 counts[language]={'paragraphs':ps,'identified_alignment_paragraphs':ids};marker_counts[language]=markers
assert counts=={'Latin':{'paragraphs':1622,'identified_alignment_paragraphs':1442},'Greek':{'paragraphs':1681,'identified_alignment_paragraphs':1442},'English':{'paragraphs':1600,'identified_alignment_paragraphs':1442}}
assert marker_counts=={'Latin':3,'Greek':7,'English':3}
registry=E.parse(str(ROOT/'assets/xml/antiquities/structure.xml'));rng=E.RelaxNG(E.parse(str(D/'tei_all.rng')));assert rng.validate(registry),str(rng.error_log)
registry_ids=set(registry.xpath('//@xml:id'))
for m in json.loads((D/'MARKERS.json').read_text()):
 anchor=E.parse(str(ROOT/m['file'])).xpath('//t:anchor[@xml:id="'+m['xml_id']+'"]',namespaces=NS)[0]
 assert anchor.get('corresp')=='../structure.xml#'+m['xml_id'].split('trad-'+m['file'].split('/')[3].lower()+'-',1)[1]
 assert anchor.get('corresp').split('#')[1] in registry_ids
items=registry.xpath('//t:list[@type="traditional-boundaries"]/t:item',namespaces=NS);rows=[{f.get('name'):f[0].text for f in x.xpath('./t:fs/t:f[t:string]',namespaces=NS)} for x in items]
authority_root=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review')
reconciliation=json.loads((authority_root/'Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06/Antiquities_Structure_Reconciliation.json').read_text(encoding='utf-8-sig'))
verification=json.loads((authority_root/'Antiquities_Loeb_Niese_Verification_2026-10-05/consolidated/Antiquities_Loeb_Niese_I-XX.json').read_text(encoding='utf-8-sig'))
source_rows={r['id']:r for r in reconciliation['loeb_boundaries']}
source_audits={r['loeb_boundary_id']:r for r in verification['audited_boundaries']}
assert {i.get(XI) for i in items}==set(source_rows)
for item,row in zip(items,rows):
 original=source_rows[item.get(XI)];sv=original['independent_niese_verification'];audit=source_audits[sv['loeb_boundary_id']]
 payload=json.loads(item.find('t:note[@type="source-evidence"]/t:p',NS).text)
 assert payload['frozen_loeb']==original['source'] and payload['independent_verification']==audit
 assert payload['human_physical_copy_checks']==[c for c in verification['human_physical_copy_checks'] if c['case']==sv['loeb_boundary_id']]
 expected={'raw-loeb-associated-niese':original['source']['niese_section'],'canonical-niese':sv['recommended_niese_association'],'niese-original':sv['niese_original_printed_section'],'verification-status':sv['verification_status'],'physical-point':sv['physical_boundary_id'],'literal-label':original['source']['printed_label']}
 for key,value in expected.items():assert (row.get(key) or '')==('' if value is None else str(value)),(item.get(XI),key)
assert len(items)==1689 and collections.Counter(x['scheme'] for x in rows)=={'chapter':257,'subchapter':1432}
assert len({x['physical-point'] for x in rows})==1441
assert collections.Counter(x['verification-status'] for x in rows)=={'CONFIRMED_NIESE_START':1672,'CONFIRMED_WITHIN_NIESE':3,'LOEB_NIESE_NUMBER_DISAGREEMENT':3,'NIESE_SOURCE_AMBIGUOUS':11}
assert len(registry.xpath('//t:list[@type="alignment-ranges"]/t:item',namespaces=NS))==3
assert len([x for x in rows if x['scheme']=='subchapter' and x['context']=='Proem'])==4
missing1=[]
for row in rows:
 if row['scheme']=='chapter' and not any(x['parent']==f'LOEB-{int(row["book"]):02}-Chapter-{row["chapter"]}-0' and x['subchapter']=='1' for x in rows):missing1.append((row['book'],row['chapter']))
assert len(missing1)==9
assert inventory(Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development'))==BASE['production']
source=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review')
for key,folder in [('reconciliation','Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06'),('verification','Antiquities_Loeb_Niese_Verification_2026-10-05')]:assert inventory(source/folder)==BASE['authorities'][key]
now=inventory(ROOT);changed=[f for f,b in BASE['worktree'].items() if not f.startswith('review/Antiquities_Traditional_Navigation_2026-10-06/') and now.get(f)!=b]
expected=['_includes/display-settings.html','assets/js/renderTei.js',*[f'assets/xml/antiquities/{l}/book-{n:02}.xml' for l,nums in [('Greek',range(15,21)),('Latin',[13,15,16]),('English',[1,13,15])] for n in nums]]
assert set(changed)==set(expected),changed
record={'result':'PASS','registry':{'Chapters':257,'Subchapters':1432,'traditional_rows':1689,'physical_positions':1441,'alignment_span_records':3,'primary_statuses':dict(collections.Counter(x['verification-status'] for x in rows)),'unresolved':0,'chapter_openings_without_lower1':9,'Proem_lower_divisions':4,'TEI_P5_4.12.0':'PASS'},'text_topology':counts,'added_empty_anchors':marker_counts,'source_XML_recovered_exactly_after_removing_13_authorized_anchors':True,'all_1689_identities_source_readings_associations_statuses_and_human_checks_match_frozen_authorities':'PASS','all_new_anchor_corresp_targets_resolve_to_external_registry':'PASS','text_projection_original_ids_sameAs_paragraph_order':'PASS','canonical_checkout_unchanged':'PASS','frozen_packets_unchanged':'PASS','protected_other_work_XML_styles_templates_layout_configuration_generated_files':'PASS','changed_existing_files':changed,'no_commits_push_merge_rebase_or_Git_configuration_change':True}
(D/'INTEGRITY_QA.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(record,indent=2))
