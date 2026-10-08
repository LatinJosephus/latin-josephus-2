from pathlib import Path
from lxml import etree as E
from collections import Counter
import json,csv,hashlib,copy,subprocess,sys
W=Path(r'C:\workspace\LatinJosephus-source-toc-navigation');V=W/'review/Source_TOC_Navigation_2026-10-07';D=Path(__file__).resolve().parent;A=D/'prior-effective-metadata';N={'t':'http://www.tei-c.org/ns/1.0'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(p,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(p),*args],text=True).strip()
if '--verify' in sys.argv:
 m=read(V/'FILE_MANIFEST.json');fail=[p for p,x in m['files'].items() if not (W/p).exists() or sha(W/p)!=x['after_sha256']];assert not fail,fail
 print('MANIFEST_PASS',len(m['files']),'entries; root manifest sha256',sha(V/'FILE_MANIFEST.json'));sys.exit()
before=read(D/'BEFORE.json');trans=read(D/'TRANSCRIPTION_QA.json');browser=read(D/'XIV_BROWSER_QA.json');contents=read(V/'CONTENTS_BROWSER_QA_2026-10-08.json');traditional=read(V/'BROWSER_QA.json');bamberg=read(V/'BAMBERG_BROWSER_QA.json');burl=read(V/'BAMBERG_URL_QA.json');pairs=read(V/'SAME_NIESE_DIFFERENT_POSITION_QA.json');interaction=read(V/'INTERACTION_QA.json');integrity=read(V/'INTEGRITY_QA_2026-10-08.json')
for x in [trans,browser,contents,bamberg,burl,pairs,interaction,integrity]:assert x['result']=='PASS'
assert traditional['traditional']['executable']==5034 and traditional['traditional']['unavailable']==33 and not traditional['errors']
assert contents['source_combinations']==104 and len(contents['interactions'])==30 and not contents['errors']
source=W/'assets/xml/antiquities/Latin/book-14.xml';companion=W/'assets/xml/antiquities/paratext/bamberg78/book-14-contents.xml';index=W/'assets/xml/source-contents.xml'
src=E.parse(str(source));comp=E.parse(str(companion));c0=src.xpath('//t:div2[@n="0"]',namespaces=N)[0];items=comp.xpath('//t:list[@type="capitula"]/t:item',namespaces=N)
assert len(items)==27
clean=[]
for item in items:
 q=copy.deepcopy(item);lab=q.find('t:label',N)
 if lab is not None:q.text=lab.tail[1:];q.remove(lab)
 clean.append(q)
def event_inventory(nodes):
 offset=0;events=[]
 def walk(node,is_root=False):
  nonlocal offset
  if not is_root:
   attrs=dict(node.attrib)
   if E.QName(node).localname=='milestone' and attrs.get('unit')=='image':attrs.pop('unit')
   events.append({'tag':E.QName(node).localname,'attributes':attrs,'source_projection_offset':offset,'text':node.text})
  offset+=len(node.text or '')
  for child in node:
   walk(child);offset+=len(child.tail or '')
 for node in nodes:walk(node,True)
 return events,offset
source_events,source_length=event_inventory(c0.findall('t:p',N));copy_events,copy_length=event_inventory(clean)
assert source_events==copy_events and source_length==copy_length
assert [''.join(h.itertext()) for h in c0.findall('t:head',N)]==[''.join(h.itertext()) for h in comp.xpath('//t:div[@type="contents"]/t:head',namespaces=N)]
source_prefix=[(E.QName(e).localname,e.get('n')) for e in c0 if E.QName(e).localname in ['milestone','pb','cb']]
copy_prefix=[(E.QName(e).localname,e.get('n')) for e in comp.xpath('//t:div[@type="contents"]',namespaces=N)[0] if E.QName(e).localname in ['milestone','pb','cb']]
assert source_prefix==copy_prefix
assert len(comp.xpath('//t:supplied',namespaces=N))==8 and not comp.xpath('//t:supplied[@source="#blatt"]',namespaces=N)
ids=comp.xpath('//@xml:id');assert len(ids)==len(set(ids))
records=read(V/'VERIFIED_CONTENTS_REGISTRY_2026-10-08.json');assert records[:-1]==read(A/'VERIFIED_CONTENTS_REGISTRY_2026-10-08.json') and len(records)==30
expected=read(V/'CONTENTS_EXPECTATIONS_2026-10-08.json');assert expected[:-1]==read(A/'CONTENTS_EXPECTATIONS_2026-10-08.json')
elig=read(V/'SOURCE_TOC_ELIGIBILITY_2026-10-08.json');oldelig=read(A/'SOURCE_TOC_ELIGIBILITY_2026-10-08.json')
row=next(r for r in elig['rows'] if r['work']=='Antiquities' and int(r['book'])==14 and r['language']=='Latin')
for a,b in zip(elig['rows'],oldelig['rows']):
 if a is not row:assert a==b
oldrow=next(r for r in oldelig['rows'] if r['work']=='Antiquities' and int(r['book'])==14 and r['language']=='Latin')
row.update({'current_encoding':'SOURCE_COMPANION_WITH_APPROVED_EDITORIAL_SEGMENTATION; original chapter-zero encoding unchanged','contents_file':companion.relative_to(W).as_posix(),'available_elsewhere_in_production':True,'recommended_action':'Display the approved 27-entry companion contents with explicitly supplied [V]–[XII]; preserve original source XML and open transcription holds.','confidence':'HIGH_HUMAN_APPROVED_EDITORIAL_SEGMENTATION','prior_census_evidence_note':oldrow['evidence_note'],'evidence_note':'2026-10-08 human clarification confirms the Herodian material is genuinely transmitted here. All eight editorial contents boundaries approved. SR-061 contents segmentation resolved; original source encoding and historical extra-1 discrepancy unchanged.','browser_integration':'PASS','authority':oldrow['authority']+'; SR-061_Implementation_2026-10-08/DECISION.md'})
dump(V/'SOURCE_TOC_ELIGIBILITY_2026-10-08.json',elig)
with (V/'SOURCE_TOC_ELIGIBILITY_2026-10-08.csv').open('w',encoding='utf-8',newline='') as f:
 keys=list(dict.fromkeys(k for r in elig['rows'] for k in r));wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in elig['rows'])
xmlpaths=[p for p in before if p.startswith('assets/xml/') and p.endswith('.xml')];unchangedxml=[p for p in xmlpaths if sha(W/p)==before[p]]
assert len(unchangedxml)==len(xmlpaths)-1 and index.relative_to(W).as_posix() not in unchangedxml
for p in ['assets/js/renderTei.js','assets/css/tei.css','assets/xml/antiquities/structure.xml']:assert sha(W/p)==before[p]
struct=E.parse(str(W/'assets/xml/antiquities/structure.xml'));assert len(struct.xpath('//t:list[@type="bamberg-boundaries"]/t:item',namespaces=N))==198
cross={w:sum(x['ranges'] for x in traditional['crossWork'] if x['work']==w) for w in ['deh','bellum-judaicum','contra-apionem']};niese=sum(x['selections'] for x in traditional['niese'].values());assert niese==2456
qa={'date':'2026-10-08','decision':'SR-061 TOC SEGMENTATION EDITORIALLY RESOLVED','verdict':'GO_FOR_HUMAN_BROWSER_REVIEW_AND_PUBLICATION_PREPARATION','entries':27,'literal_manuscript_numerals':19,'supplied_editorial_numerals':['[V]','[VI]','[VII]','[VIII]','[IX]','[X]','[XI]','[XII]'],'approved_exact_boundaries':8,'source_projection_characters':source_length,'source_projection_unchanged':True,'source_inline_events_identical':len(source_events),'heading_and_initial_page_markers_unchanged':True,'Herodian_material_retained_once_and_in_place':True,'XII_end':'mereretur.','IX_not_equated_to_narrative_VIIII':True,'historical_export_1_discrepancy':'OPEN_UNCHANGED','schema':trans['schema'],'brackets_visible_in_both_themes':True,'themes':browser['themes'],'visual_QA':'Light/dark screenshots inspected; bracketed labels and Latin/Greek prose legible, no overflow or overlap.','contents_source_combinations':104,'eligible_book_witnesses':30,'URL_reload_history_round_trips':30,'Greek_and_Latin_XIV_contents_side_by_side':'PASS','English_own_unavailable_state':'PASS','traditional':traditional['traditional'],'Niese':{'selections':2456,'three_pane_comparisons':7368},'Bamberg':{'identities':198,'language_displays':594,'compact_URL_round_trips':198,'same_Niese_distinct_position_pairs':6,'pair_language_checks':18},'cross_work_ranges':cross,'pane_source_keyboard_history_theme_interaction_configurations':len(interaction['checks']),'alignment_regression':'Existing 1,441-unit exhaustive QA retained; renderer, all alignment XML, source registry and bindings byte-identical. Ordinary unit links retested by current range/browser suite.','XML_integrity':{'all_original_production_XML':108,'all_existing_source_XML_including_companions_unchanged':len(unchangedxml),'contents_index_only_existing_XML_change':True,'no_new_narrative_anchor':True,'no_text_ID_sameAs_topology_milestone_change_to_existing_XML':True},'protected_external_authorities':48,'original_SR061_and_proposal_unchanged':True,'other_source_decisions_and_contents_records_unchanged':True,'renderer_and_CSS_unchanged_this_step':True,'canonical_checkout_clean':True,'staged_files':0,'Git_write_operations':0,'production_source_files_changed_this_step':[index.relative_to(W).as_posix(),companion.relative_to(W).as_posix()]}
dump(D/'QA.json',qa)
active=read(A/'QA.json');active['source_eligibility'].update({'eligible_book_witness_combinations':30,'unavailable_or_deferred':74,'Latin_XIV':'VERIFIED companion; SR-061 editorial segmentation approved and implemented. Historical source encoding unchanged; export extra 1 remains open.'})
active['contents_browser']['supported_URL_history_copy_reload_cases']=30;active['contents_browser']['source_combinations']=104
active['TEI_schema']=[{**x,**({'sha256':sha(index)} if x['file'].replace('\\','/')=='assets/xml/source-contents.xml' else {})} for x in active['TEI_schema']]
active['TEI_schema'].append({'file':companion.relative_to(W).as_posix(),'sha256':sha(companion),'schema':'official project-retained TEI P5 tei_all.rng','result':'PASS'})
active['SR061_editorial_resolution']=qa;active['supporting_evidence'].extend(['SR-061_Implementation_2026-10-08/QA.json','SR-061_Implementation_2026-10-08/TRANSCRIPTION_QA.json','SR-061_Implementation_2026-10-08/XIV_BROWSER_QA.json']);dump(V/'QA.json',active)
report=f'''# SR-061 approved Book XIV contents integration — amendment 2026-10-08

**GO for human browser review and publication preparation.** Book XIV now has **27 Latin contents entries: 19 literal manuscript numerals and eight editorially supplied numerals [V]–[XII]**. All eight starts and ends match the unchanged approved proposal. The complete Herodian passage remains within [VII], and [XII] ends at `mereretur.` [IX] remains independent of narrative VIIII. The historical export's unexplained `1` after `prelio in` remains open and was not imported or interpreted.

The new TEI companion is `{companion.relative_to(W).as_posix()}`. Its SHA-256 is `{sha(companion)}`. The generic index `assets/xml/source-contents.xml` registers it for `?book=14&view=contents`. Greek and Latin each show their own contents; English retains its neutral unavailable message. No renderer or CSS change was needed in this step.

Every source character in the 19 original contents paragraphs is preserved, apart from explicitly added editorial numbering and its separator spacing. Exact source fragments concatenate to the prior source paragraph content; source headings, additions/deletions/expansion apparatus and physical-position markers are retained. Eight `<supplied reason="not-transmitted" source="#sr061-editorial-approval">` numerals carry brackets literally and are separate from Blatt's lost-text supplements in II–IV. Three image milestones receive the schema-required unit attribute in this new companion only. No original XML, paragraph boundary, ID, sameAs, source numeral or navigation identity changed.

Fresh QA passes: 104 book/source combinations; 30 supported contents URL/history/reload cases; all 27 Latin XIV projections and eight approved boundaries; both themes (contrast 13.23:1 light, 11.85:1 dark); 5,034 executable traditional language ranges plus 33 expected unavailable states; 2,456 enabled Niese selections / 7,368 pane comparisons; 198 Bamberg identities / 594 displays / 198 compact URL round-trips; all six same-Niese/different-position pairs; DEH 1,239, Bellum 1,441 and Contra Apionem 693 cross-work range comparisons; pane/source/history/keyboard interaction regression. Existing 1,441-unit exhaustive alignment evidence remains applicable because its XML, renderer and registry are unchanged; current ordinary unit-link checks pass.

Integrity passes for all 108 original production XML files, the four earlier companion files, original Phase-A census, original SR-061 history and proposal, both frozen structural authorities, 48 inspected external sources and the governing II–V DOCX. The original Latin XIV file remains SHA-256 `{sha(source)}`. Canonical remains clean at the accepted HEAD. All changes remain unstaged and uncommitted; no push, merge or build was performed.

The dated decision, entry inventory, reproducible import/browser checks, screenshots and integrity/manifest records are in `SR-061_Implementation_2026-10-08/`. Previous effective metadata are retained there byte-for-byte in `prior-effective-metadata/`. The earlier Phase-B report below is historical; its Latin-XIV hold and 29-source total are superseded only by this amendment. Other accepted source decisions are unchanged.

---

'''
(V/'REPORT.md').write_text(report+(A/'REPORT.md').read_text(encoding='utf-8'),encoding='utf-8')
authority=f'''# SR-061 editorial authority amendment — 2026-10-08

Richard M. Pollard approved all eight boundaries in `SR-061_Proposal_2026-10-08/PROPOSAL.md` (SHA-256 `{sha(V/'SR-061_Proposal_2026-10-08/PROPOSAL.md')}`). The Herodian passage is genuine transmitted Book XIV content and remains in place. The supplied [V]–[XII] numerals are modern editorial reconstruction, not manuscript readings or Blatt-derived supplements. This resolves TOC segmentation only; the original mixed-paragraph XML and historical review remain unchanged, and the export's additional `1` remains an open transcription discrepancy.

Source XML: `assets/xml/antiquities/Latin/book-14.xml`, SHA-256 `{sha(source)}`. Held paragraph SHA-256 remains `0284126a6164f2e4fa20deafa45af2ac8b22a394dc8366600703c0836c882725`. New companion SHA-256 `{sha(companion)}`. Effective registration now contains 30 verified book/witness combinations. See the dated decision and exact entry inventory in `SR-061_Implementation_2026-10-08/`. No new source image/PDF adjudication occurred.

The earlier authority record below remains historical evidence; its unresolved Latin-XIV status is superseded by this explicit human decision. All other source decisions remain unchanged.

---

'''
(V/'SOURCE_AUTHORITY.md').write_text(authority+(A/'SOURCE_AUTHORITY.md').read_text(encoding='utf-8'),encoding='utf-8')
allowed_names={'REPORT.md','QA.json','FILE_MANIFEST.json','SOURCE_AUTHORITY.md','SOURCE_TOC_ELIGIBILITY_2026-10-08.json','SOURCE_TOC_ELIGIBILITY_2026-10-08.csv','VERIFIED_CONTENTS_REGISTRY_2026-10-08.json','CONTENTS_EXPECTATIONS_2026-10-08.json','CONTENTS_BROWSER_QA_2026-10-08.json','CONTENTS_light.png','CONTENTS_dark.png','BROWSER_QA.json','INTERACTION_QA.json','BAMBERG_BROWSER_QA.json','BAMBERG_RANGE_QA.json','BAMBERG_URL_QA.json','SAME_NIESE_DIFFERENT_POSITION_QA.json','INTEGRITY_QA_2026-10-08.json'}
allowed={'assets/xml/source-contents.xml'}|{(V/n).relative_to(W).as_posix() for n in allowed_names}
changes=[p for p,h in before.items() if not (W/p).exists() or sha(W/p)!=h];assert set(changes)<=allowed,changes
new=[p.relative_to(W).as_posix() for p in W.rglob('*') if p.is_file() and p.relative_to(W).as_posix() not in before and not p.is_relative_to(D)];assert new==[companion.relative_to(W).as_posix()],new
C=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development');assert git(C,'status','--short')=='' and git(C,'rev-parse','HEAD')=='087c0bf651037d83c5156495836510d250bdcf09';assert git(W,'diff','--cached','--name-only')==''
protected={p:h for p,h in before.items() if p not in allowed};assert all(sha(W/p)==h for p,h in protected.items())
dump(D/'INTEGRITY_QA.json',{'result':'PASS','protected_pre_existing_files_unchanged':len(protected),'all_pre_existing_files':len(before),'authorized_pre_existing_changes':changes,'new_source_file':new,'original_XML_unchanged':108,'existing_companions_unchanged':4,'structure_registry_unchanged':True,'Bamberg_identities_unchanged':198,'original_census_and_SR061_proposal_unchanged':True,'renderer_CSS_unchanged_this_step':True,'canonical_clean':True,'index_unstaged':True,'external_authorities_unchanged':48,'git_write_operations':0,'worktree_status':git(W,'status','--short')})
dump(D/'FILE_MANIFEST.json',{'date':'2026-10-08','scope':'Approved SR-061 companion integration','manifest_excludes_itself':True,'production_source_files':{p:{'before_sha256':before.get(p),'after_sha256':sha(W/p)} for p in [index.relative_to(W).as_posix(),companion.relative_to(W).as_posix()]},'protected_pre_existing_files_sha256':protected,'review_files_sha256':{p.relative_to(D).as_posix():sha(p) for p in sorted(D.rglob('*')) if p.is_file() and p!=D/'FILE_MANIFEST.json'}})
manifest=read(A/'FILE_MANIFEST.json');manifest['new_production_source_files'].append(companion.relative_to(W).as_posix());manifest['SR061_approved_amendment']={'decision':'SR-061_Implementation_2026-10-08/DECISION.md','entries':27,'supplied_numerals':qa['supplied_editorial_numerals'],'new_empty_narrative_anchors':0,'effective_eligible_sources':30,'changed_existing_files_this_step':changes}
files_to_hash=[W/p for p in manifest['modified_existing_production_files']+manifest['new_production_source_files']]+[p for p in V.rglob('*') if p.is_file() and p!=V/'FILE_MANIFEST.json']
oldfiles=manifest['files'];manifest['files']={p.relative_to(W).as_posix():{'before_sha256':oldfiles.get(p.relative_to(W).as_posix(),{}).get('before_sha256'),'after_sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(set(files_to_hash))};manifest['eligible_source_files']={r['path']:sha(W/r['path']) for r in records};manifest['manifest_self']={'excluded_from_hash_entries':True,'reason':'Self-hash is reported externally; no recursive manifest digest.'};dump(V/'FILE_MANIFEST.json',manifest)
print('FINAL_QA_PASS',json.dumps({'entries':27,'source_combinations':104,'URL_cases':30,'traditional_ranges':5034,'Niese_selections':2456,'Bamberg_displays':594,'protected_files':len(protected),'authorized_existing_changes':changes,'manifest_entries':len(manifest['files'])},indent=2))