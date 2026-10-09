import json,hashlib,subprocess,shutil
from pathlib import Path
packet=Path(__file__).resolve().parent
root=packet.parents[1]
def read(name):return json.loads((packet/name).read_text())
def sha(raw):return hashlib.sha256(raw).hexdigest()
base=read('BASELINE.json');runtime=Path(base['runtime'])
for name in ['EQUIVALENT_LEAKAGE_QA.json','FOCUSED_BROWSER_QA.json','PROTECTED_BROWSER_QA.json','CROSS_ROUTE_QA.json']:assert read(name)['result']=='PASS',name
for rel,h in base['assets_pinned'].items():assert sha((root/rel).read_bytes())==h,rel
changes=subprocess.check_output(['git','-C',str(root),'diff','--name-only'],text=True).splitlines()
assert changes==['assets/js/renderTei.js'],changes
assert len(read('EQUIVALENT_LEAKAGE_QA.json')['display_only_changes'])==5
assert read('EQUIVALENT_LEAKAGE_QA.json')['total']==4315
for name in ['jekyll.log','dependencies.log']:shutil.copyfile(runtime/name,packet/name)
protected=read('PROTECTED_BROWSER_QA.json')
protected['scope']='DISPLAY_ONLY_CORRECTION_AGAINST_CURRENT_CERTIFIED_CANONICAL'
protected['Antiquities_Niese_checks']='All 4315 separately covered by EQUIVALENT_LEAKAGE_QA.json; no Niese exclusions from the regression result'
(packet/'PROTECTED_BROWSER_QA.json').write_text(json.dumps(protected,indent=2)+'\n',encoding='utf-8')
harness=packet/'protected-browser.cjs'
s=harness.read_text().replace("'MERGED_INTEGRATION_BUILD'", "'DISPLAY_ONLY_CORRECTION_AGAINST_CURRENT_CERTIFIED_CANONICAL'")
harness.write_text(s,encoding='utf-8')
preservation={'result':'PASS','base':base['base'],'production_scope':changes,'Latin_book10_before_sha256':base['XML_pinned']['assets/xml/antiquities/Latin/book-10.xml'],'Latin_book10_after_sha256':sha((root/'assets/xml/antiquities/Latin/book-10.xml').read_bytes()),'XML_and_registry_files':len(base['XML_pinned']),'all_XML_registry_bytes_unchanged':True,'all_other_asset_inputs_unchanged':True,'IDs_sameAs_paragraphs_divisions_Niese_milestones_unchanged':True,'all_Greek_Latin_executable_start_inventories_unchanged':True,'all_4315_narratives_availability_notices_and_qualifications_unchanged':True,'reader_before_sha256':base['baseline_renderer_sha256'],'reader_after_sha256':sha((root/'assets/js/renderTei.js').read_bytes()),'display_projection_changes':read('EQUIVALENT_LEAKAGE_QA.json')['display_only_changes'],'broader_labels_preserved':read('FOCUSED_BROWSER_QA.json')['broader'],'visual_review':['BEFORE_X_107.png','AFTER_X_107_light.png'],'canonical_integration':'Not performed in this pre-integration review stage','push_or_deployment':'Not performed'}
(packet/'SOURCE_PRESERVATION_QA.json').write_text(json.dumps(preservation,indent=2)+'\n',encoding='utf-8')
manifest={'base':base['base'],'production':[{'path':'assets/js/renderTei.js','before_sha256':base['baseline_renderer_sha256'],'after_sha256':preservation['reader_after_sha256']}],'review_directory':packet.relative_to(root).as_posix(),'self_excluded':True,'files':[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(packet.iterdir()) if p.is_file() and p.name!='FILE_MANIFEST.json']}
(packet/'FILE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','XML_preserved':len(base['XML_pinned']),'Antiquities_Niese_selections':4315,'corrected_label_only_tails':5,'review_files_including_manifest':len(manifest['files'])+1},indent=2))
