from pathlib import Path
from lxml import etree as E
import json,csv,collections,hashlib,re
R=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;B=json.loads((D/'BASELINE.json').read_bytes());T='{http://www.tei-c.org/ns/1.0}';NS={'t':T[1:-1]};XI='{http://www.w3.org/XML/1998/namespace}id'
load=lambda n:json.loads((D/n).read_bytes());write=lambda n,s:(D/n).write_bytes(s.encode());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
required=['BAMBERG_COMPACT_URL_QA.json','BAMBERG_BROWSER_QA.json','BAMBERG_RANGE_QA.json','BAMBERG_URL_QA.json','SAME_NIESE_DIFFERENT_POSITION_QA.json','FOLLOWUP_GATE_QA.json','ALIGNMENT_ALL_QA.json','PROTECTED_SOURCE_GATE_QA.json','XI_MULTISPAN_GATE_QA.json','RENDERED_GATE_QA.json','NOTICE_THEME_QA.json','INTERACTION_QA.json']
for name in required:
 v=load(name);assert v.get('result','PASS')=='PASS',(name,v.get('result'));assert not v.get('errors'),name
browser=load('BROWSER_QA.json');assert not browser['errors'];assert browser['traditional']['executable']==5034 and browser['traditional']['unavailable']==33
integrity=load('INTEGRITY_QA.json');assert integrity['result'] in ['PASS','PASS_SCHOLARLY_INPUTS_WITH_FILESYSTEM_METADATA_DRIFT']
registry=E.parse(str(R/'assets/xml/antiquities/structure.xml'))
def fields(fs):return {f.get('name'):fields(f[0]) if E.QName(f[0]).localname=='fs' else [fields(x) for x in f[0]] if E.QName(f[0]).localname=='vColl' else f[0].text or '' for f in fs}
records=[{'id':i.get(XI),**fields(i.find(T+'fs'))} for i in registry.xpath('//t:list[@type="bamberg-boundaries"]/t:item',namespaces=NS)]
columns=['id','book','source-order','manuscript-label-as-recorded','display','label-status','canonical-niese','niese-relationship','confidence','verification-status','certified-latin-incipit','image','manuscript-image-column-line','visible-numeral-or-initial','traditional-relationship','traditional-exact-identities','traditional-different-position-identities','end']+[f'{l}_{k}' for l in ['Latin','Greek','English'] for k in ['file','paragraph','offset','kind','target','edge','anchor']]
with (D/'BAMBERG_RECORD_INVENTORY.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
 for row in records:
  out={k:row.get(k,'') for k in columns if '_' not in k};out.update({f'{l}_{k}':row[l].get(k,'') for l in ['Latin','Greek','English'] for k in ['file','paragraph','offset','kind','target','edge','anchor']});w.writerow(out)
countbooks=[sum(int(r['book'])==b for r in records) for b in range(1,21)];assert sum(countbooks)==198
statuses=dict(collections.Counter(registry.xpath('//t:list[@type="traditional-boundaries"]/t:item/t:fs/t:f[@name="verification-status"]/t:string/text()',namespaces=NS)));assert statuses=={'CONFIRMED_NIESE_START':1672,'CONFIRMED_WITHIN_NIESE':3,'LOEB_NIESE_NUMBER_DISAGREEMENT':3,'NIESE_SOURCE_AMBIGUOUS':11}
comparison={work:sum(c['ranges'] for c in browser['crossWork'] if c['work']==work) for work in ['deh','bellum-judaicum','contra-apionem']};assert comparison=={'deh':1239,'bellum-judaicum':1441,'contra-apionem':693}
special_source_rows=['B78-table1-row008','B78-table1-row010','B78-table1-row012','B78-table1-row013'];checks=load('BAMBERG_RANGE_QA.json')['ranges'];assert all(sum(c['id']==s for c in checks)==3 for s in special_source_rows)
qa={'result':'PASS_WITH_DOCUMENTED_FILESYSTEM_METADATA_DRIFT' if integrity['filesystem_metadata_drift'] else 'PASS','implementation_recommendation':'GO_FOR_HUMAN_BROWSER_REVIEW_AND_COMMIT','date':'2026-10-07','worktree':str(R),'branch':'antiquities-bamberg-navigation','base_commit':B['base_commit'],'source_commit':'41e817680549767d36e3f80dbc825682908ea5e6','source_tag':'antiquities-structure-reconciliation-v1.1','bamberg':{'identities':198,'per_book':countbooks,'Niese_start':172,'internal':26,'unresolved':0,'language_displays':594,'unavailable_counterparts':0,'range_checks':594,'URL_round_trips':198,'source_order_previous_next_checks':198,'same_Niese_different_positions':{'pairs':6,'language_checks':18,'result':'PASS'},'four_Book_I_straddling_decisions':{'records':special_source_rows,'language_checks':12,'result':'PASS'},'final_division_book_end_checks':42,'negative_evidence_books':[6,7,8,9,10,11],'malformed_URL_cases':4,'duplicate_label_source_IDs':['B78-table1-row069','B78-table1-row070'],'physical_position_availability':'594/594 available'},'new_empty_anchors':{'Latin':15,'Greek':10,'English':28,'total':53,'XML_files':22},'traditional':browser['traditional'],'traditional_verification_status_rows':{**statuses,'UNRESOLVED':0},'Niese':{'books':[1,2,3,4,5,6,7],'selections':sum(v['selections'] for v in browser['niese'].values()),'three_pane_comparisons':sum(v['language_comparisons'] for v in browser['niese'].values()),'public_VIII_XX_expansion':False,'result':'PASS'},'alignment':{'selectable_unit_identities':sum(x['alignment_units'] for x in load('ALIGNMENT_ALL_QA.json')['checks']),'Book_witness_order_views':21,'VI_explicit_Greek_bindings':3,'result':'PASS'},'cross_work':{'differential_ranges':comparison,'Bellum_Whiston_Lodge_full_ranges':sum(c['ranges'] for c in load('PROTECTED_SOURCE_GATE_QA.json')['checks']),'Bellum_Whiston_Lodge_Niese_ranges':sum(c['niese'] for c in load('PROTECTED_SOURCE_GATE_QA.json')['checks']),'interactive_configurations':4,'semantic_changes':0,'result':'PASS'},'UI':{'all_257_chapter_availability':'PASS','nine_no_subchapter_chapters_preserved':9,'structural_prefix_checks':227,'VI_xii8_end_and_XIII_start':'PASS','XI_multispan_ranges':18,'XI_notice_unchanged':'PASS','reload_history_keyboard_panes':'PASS','rendered_ID_checks':'PASS','dark_light_controls_AA':'PASS','minimum_new_control_contrast':5.33},'integrity':integrity,'source_label_prompt_difference':{'source_record':'B78-table1-row079','Niese':230,'prompt':'XIIII','frozen_authority':'XIII','implemented':'XIII','new_source_judgment':False},'test_environment':'Installed Chrome, actual renderer/CETEI and XML; controlled reader fixture with real template conditionals and unchanged source CSS. No Jekyll build. Existing HTMLCollection.forEach compatibility adapter is supplied identically to baseline and implementation. Differential snapshots exclude only new empty Bamberg anchors; text/IDs/order are checked independently.','gates':required+['BROWSER_QA.json','INTEGRITY_QA.json','CURRENT_LOCATOR_GATE_QA.json','BAMBERG_BOUNDARY_QA.json'],'superseded_test_harness_diagnostics':'TEST_DEVELOPMENT_LOG.json','Git':'Authorized isolated worktree/branch creation only; all changes unstaged/uncommitted; no push, merge, rebase or configuration change.'}
assert qa['Niese']['selections']==2456 and qa['Niese']['three_pane_comparisons']==7368
qa['bamberg']['compact_URL']={'identities':198,'public_form':'?book=13&bamberg=76','state_identity':'B78-table1-row076','verbose_input_alias':True,'padded_numeric_input_alias':True,'real_browser_reload':198,'copy_load':198,'back_forward':198,'result':load('BAMBERG_COMPACT_URL_QA.json')['result']}
write('QA.json',json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
# Evidence is cited from the accepted packet; manuscript/source decisions are not reopened.
source_text=f'''# Source authority

Implementation base: `{B['base_commit']}` on `antiquities-bamberg-navigation`.

Scholarly authority: recovery commit `41e817680549767d36e3f80dbc825682908ea5e6`, tag `antiquities-structure-reconciliation-v1.1` (tag resolves to that commit). Packet: `{B['frozen_authority_path']}`.

The eight entries in the frozen v1.1 manifest were verified before implementation. All nine scholarly files, including the manifest itself, retain their recorded hashes. The independent verification checkpoint `19308a8ed937525c540827205b0c763768f5ce44` remains provenance of the unchanged traditional registry.

No PDF, manuscript image, original human checklist or Word audit was reopened. The frozen JSON supplies all 198 decisions and all 594 independent current-text locators. Literal labels and completed human-check fields are reproduced as recorded; every frozen Bamberg row is retained verbatim as JSON evidence in its registry item. Presentational locators were compiled against actual base XML; no numeric suffix, sameAs link or shared Niese number was used to adjudicate equality.

| Scholarly file | SHA-256 |
|---|---|
'''
for name,v in sorted(B['frozen_authority'].items()):
 if name!='desktop.ini':source_text+=f"| {name} | `{v['sha256']}` |\n"
source_text+='''
The existing registry's reconciliation-v1.1 bibliographical identity is reused. Bamberg record identity, label, source order, incipit, citation relationship, confidence, traditional relationship and independent language start/end coordinates remain separate fields. The new audited-coverage list explicitly records no chapter marks in VI–XI.

At Niese 230 the prompt's example says XIIIΙ/XIIII; the authoritative record B78-table1-row079 says XIII. XIII is retained without a new scholarly judgment.

A non-scholarly Windows desktop.ini changed after the initial snapshot. Its before/after hashes are recorded in INTEGRITY_QA.json. It is outside the frozen scholarly manifest and was neither written nor reverted by this task. This qualification prevents a claim that every filesystem entry in the recovery directory remained identical.
'''
write('SOURCE_AUTHORITY.md',source_text)
report=f'''# Bamberg navigation implementation review — 2026-10-07

GO for human browser review and a follow-up commit. Changes are unstaged and uncommitted in `{R}` on `antiquities-bamberg-navigation`, based on `{B['base_commit']}`. The canonical v2-development source checkout, HEAD and origin reference remain unchanged and its Git status is clean. No push, merge, rebase, staging, commit or Git-configuration change occurred.

## Architecture and reader behavior

Bamberg division is an independent Antiquities viewing level, backed by a new TEI-P5-valid list in the existing structure.xml registry. Its unique option values and application-state identities remain exact frozen source-record identities. Public URLs serialize their numeric source rows, for example `?book=13&bamberg=76` resolves to `B78-table1-row076`. The parser also accepts the old verbose form and zero-padded numeric inputs; the writer always emits the compact numeric form. They do not derive from manuscript numerals, Niese numbers, XPath or offsets. Previous/Next follows the registered physical source order. The existing generic per-language range/multi-span resolver is reused; only its endpoint lookup now includes both independent registries. No source-specific book/label conditional or exception table was added.

The template emits Bamberg controls only on Antiquities. Books with records enable the selector and viewing level; VI–XI disable them, with ordinary book changes falling back to Book view. Returning to a book with records restores availability. Invalid, empty or cross-book manual identities yield an explicit unavailable state and no substitute passage. Changing navigation scheme removes stale owned parameters while retaining unrelated query parameters and fragments.

All manuscript labels remain as recorded. Book I lacks II; XIII contains two literal III records (row069 and row070), distinguished by short incipits but different persistent option values. XII is labelled unnumbered, with enlarged-H evidence retained and no supplied numeral. XIV [XXVIII?], XIII XXIII and historical IIII/VIIII/XVIIII forms remain unchanged. XVIII VI → VIIII contains no synthetic VII/VIII. XV.[XII] is at certified 323 and XVI.XX at internal 368 in the num367 environment. Full evidence and confidence remain in data.

| Book | Bamberg options |
|---|---:|
'''
for i,n in enumerate(countbooks,1):report+=f'| {i} | {n} |\n'
report+='''
Total: 198 physical identities; 172 citation-start and 26 internal-to-Niese boundaries; zero unresolved and zero unavailable language counterparts. Relationships to traditional Chapter starts remain 75 exact, 117 Bamberg-only and six shared-Niese/different-position pairs. The Niese-230 pair's frozen label is XIII, whereas the task example called it XIIII; the source reading is retained.

## Exact locators and authorized empty anchors

All 594 frozen locators passed exact projected-offset and literal-anchor checks against the actual base XML. Existing certified traditional points, paragraph/inline edges and identified anchors were reused. Fifty-three empty TEI anchors were necessary: 15 Latin, 10 Greek, 28 English, in 22 files. Stable b78-language-source-record IDs and corresp links identify their registry records. MARKERS.json records exact insertion bytes, original byte positions and per-file counts.

Removing only those documented empty anchors reproduces every prior XML byte and hash exactly. There is no paragraph splitting, text/numeral/apparatus rewrite, ID or sameAs change, node reordering, or replacement of existing markers. Paragraph counts remain Latin 1,622; Greek 1,681; English 1,600. Book XI order and Book IX/VII inputs remain byte-identical. The complete prior registry bytes are retained; Bamberg and audited-coverage lists are appended. No Bamberg counterpart required multiple spans in this batch: source order is strictly increasing for each available language, and the existing multi-span capability remains intact for the traditional system.

## Exhaustive results

| Gate | Result |
|---|---|
| Bamberg physical starts and exact complete ranges | 594/594 PASS |
| Bamberg identities / URL round-trip / source-order controls / pane switching | 198/198 PASS |
| Compact URLs: actual copy/load, browser reload, exact frozen identity and back/forward | 198/198 PASS; verbose and padded aliases normalize |
| Final division to same-book end | 14 books × 3 languages = 42 PASS |
| Shared-Niese/different-physical-position pairs | 6 pairs / 18 language checks PASS |
| Book I straddling decisions | row008, row010, row012, row013; 12 language checks PASS |
| VI–XI audited absence and ordinary fallback | All six books PASS |
| Malformed Bamberg URLs | 4/4 explicit unavailable PASS |
| Duplicate III identity / reload / history / keyboard | PASS |
| Traditional registry | 257 Chapters; 1,432 Subchapters; 1,689 rows; 1,441 positions |
| Traditional executable ranges | 5,034 PASS |
| Book IX expected unavailable states | 33 PASS |
| Traditional Chapter availability / no fabricated lower 1 | 257 PASS; nine empty-subchapter Chapters retained |
| Heading/prefix ownership | 227 PASS; VI.xii.8 and VI.xiii/1 retained |
| Book XI canonical multi-span selections | 18 language ranges PASS; interpolation and witness views retained |
| Enabled Niese I–VII | 2,456 selections / 7,368 three-pane comparisons PASS |
| Alignment units and Book witness order | 1,441 unit identities and 21 Book/Proem views unchanged |
| Book VI explicit Greek alignment bindings | Three retained; adjacent-unit and Niese 269/271 checks PASS |
| DEH | 1,239 differential ranges PASS |
| Bellum Judaicum default navigation | 1,441 differential ranges PASS |
| Contra Apionem | 693 differential ranges PASS |
| Bellum Whiston/Lodge broad range suite | 10,340 ranges including 7,444 Niese ranges PASS |
| Protected-work pane/URL/history/keyboard/theme behavior | Four configurations PASS |
| Rendered identities, unique DOM IDs, URLs | PASS |
| Bamberg controls in light/dark themes | PASS; minimum measured contrast 5.33:1 |
| Existing shared Book XI notice | Unchanged; both themes and Book-view route PASS |
| Registry TEI P5, XML and topology integrity | PASS |

Traditional independent-verification populations remain 1,672 confirmed-start, three confirmed-internal, three number-disagreement and 11 ambiguous rows; zero unresolved. No source anomaly or ambiguity was normalized. Public Niese coverage remains I–VII. Book VII's separate alignment-target defect and Book IX's lacuna policy remain untouched.

## Verification limits and provenance

Tests use installed Chrome, the actual renderer/CETEI, actual XML and the real selector template in a controlled reader fixture. CSS tests use the canonical compiled stylesheet with unchanged source palette/reader partials. No Jekyll build or generated-site write occurred. The same existing HTMLCollection.forEach compatibility adapter is supplied in baseline and current fixtures; new empty anchors are excluded only from differential markup snapshots. Exact bytes, text, IDs, sameAs and order are independently verified. Human review should exercise the complete local/public-preview build before commit.

Initial failures during test adaptation involved browser instrumentation scope, simple Liquid preprocessing, unavailable DEH Greek controls, asynchronous render timing and a newly added null state field. They are explicitly marked superseded diagnostics in TEST_DEVELOPMENT_LOG.json; final PASS records govern QA. No scholarly boundary was changed to make a test pass.

All 560 snapshotted canonical files, all nine scholarly frozen-packet files, and both historical review directories (34 and 26 files) retain their recorded hashes. A final repeat observed desktop.ini drift in the recovery packet. This non-scholarly metadata file was not written to or reverted by this task; INTEGRITY_QA.json records the exact before/after values. Thus scholarly integrity passes with that separately documented filesystem qualification.

## Modified source files

'''
for rel in sorted(integrity['modified_existing_files']):report+='- '+rel+'\n'
report+='''
The human-review URL refinement changes only renderTei.js in application source: generic compact serialization/parsing, with no registry, XML, label or provenance change. COMPACT_URL_CHANGE.json records this refinement's before/after hash. No stylesheet change was needed. All additional files are in this new review directory. FILE_MANIFEST.json records before/after source hashes and new review-file hashes. Both prior certification directories and recovery scholarly authorities are protected and unedited.

## Reproduction

From the implementation worktree, use the available Python runtime with lxml for verify_integrity.py and the Node runtime with installed Playwright/Chrome for these commands (prefix each script with the new review-directory path):

- `node compact-url.test.cjs`
- `node bamberg.test.cjs`
- `node navigation.test.cjs`
- `node navigation.test.cjs --followup-gate`
- `node navigation.test.cjs --alignment-all-gate`
- `node navigation.test.cjs --alignment-gate`
- `node navigation.test.cjs --multispan-gate`
- `node navigation.test.cjs --protected-source-gate`
- `node navigation.test.cjs --rendered-gate`
- `node interaction.test.cjs`
- `node notice-theme.test.cjs`
- `python -B verify_integrity.py`

prepare_registry.py and patch_renderer.py document compilation/application from the exact clean base; they are not rerunnable against an already-patched registry. BASELINE.json is the initial byte inventory. CURRENT_LOCATOR_GATE_QA.json and BAMBERG_BOUNDARY_QA.json preserve the mapping gate. QA.json is the complete final result index.
'''
write('REPORT.md',report)
# Manifest excludes only its own self-referential hash; lists that reason explicitly.
files=[]
for rel in sorted(integrity['modified_existing_files']):
 p=R/rel;files.append({'path':rel,'status':'modified','before':B['worktree'][rel],'after':{'bytes':p.stat().st_size,'sha256':sha(p)},'new_empty_anchors':sum(m['file']==rel for m in load('MARKERS.json'))})
for p in sorted(D.iterdir()):
 if p.is_file() and p.name!='FILE_MANIFEST.json':files.append({'path':p.relative_to(R).as_posix(),'status':'new','before':None,'after':{'bytes':p.stat().st_size,'sha256':sha(p)}})
manifest={'base_commit':B['base_commit'],'modified_source_count':len(integrity['modified_existing_files']),'files':files,'manifest_self_hash':None,'self_hash_note':'FILE_MANIFEST.json cannot contain its own final hash; every other changed/new file is listed.','unstaged_uncommitted':True}
write('FILE_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'result':qa['result'],'source_files_modified':len(integrity['modified_existing_files']),'manifest_entries':len(files),'review_files':len(list(D.iterdir())),'Bamberg_identities':198,'language_ranges':594}))
