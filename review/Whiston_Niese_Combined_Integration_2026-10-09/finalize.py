from pathlib import Path
import json,hashlib,subprocess,datetime
from lxml import etree as E
P=Path(__file__).resolve().parent;R=P.parents[1];C=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development');W=R/'review/Whiston_Antiquities_Compiled_Index_2026-10-09'
def h(raw):return hashlib.sha256(raw).hexdigest()
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args])
def read(name):return json.loads((P/name).read_text(encoding='utf-8-sig'))
def save(name,data):(P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def record(root,rows):
 out=[]
 for name,before in rows.items():
  f=root/name;after={'bytes':f.stat().st_size,'sha256':h(f.read_bytes())};assert before==after,name
  out.append({'path':name,'before':before,'after':after,'result':'PASS'})
 return out
b=read('BASELINE.json');work=record(R,b['integration_files']);canonical=record(C,b['canonical_files'])
for root,key in [(R,'integration'),(C,'canonical')]:
 assert git(root,'rev-parse','HEAD').decode().strip()==b[key]['HEAD']
 index=Path(git(root,'rev-parse','--path-format=absolute','--git-path','index').decode().strip());assert h(index.read_bytes())==b[key+'_index']
assert not git(C,'status','--short').decode().strip();assert not git(R,'diff','--cached','--name-only').decode().strip()
status=git(R,'status','--short').decode().strip();assert status=='?? review/Whiston_Niese_Combined_Integration_2026-10-09/',status
cp=read('CHERRY_PICK_INTEGRITY.json');production=[x for x in cp['rows'] if not x['path'].startswith('review/')]
for x in production:assert h(git(R,'show','3553a74:'+x['path']))==x['sha256'],x['path']
# Verify final historic manifests in place, never update them.
historical=[]
for folder in ['Whiston_Antiquities_Compiled_Index_2026-10-09','Antiquities_Niese_Implementation_08_10_2026-10-09','Antiquities_Niese_Integration_08_10_2026-10-09']:
 base=R/'review'/folder;mp=base/'FILE_MANIFEST.json';m=json.loads(mp.read_text());entries=m.get('entries',m.get('files',[]))
 for x in entries:
  f=base/x['path'] if (base/x['path']).exists() else R/x['path'];assert h(f.read_bytes())==x['sha256'],str(f)
  if 'bytes' in x:assert f.stat().st_size==x['bytes'],str(f)
 historical.append({'packet':folder,'manifest_sha256':h(mp.read_bytes()),'verified_entries':len(entries),'result':'PASS'})
save('SOURCE_PRESERVATION_QA.json',{'result':'PASS','integration_files_verified':len(work),'canonical_files_verified':len(canonical),'production_changes':0,'original_Whiston_production_22_identical':True,'all_historical_certification_unchanged':historical,'original_and_final_Git_indices_identical':True,'integration_index_sha256':b['integration_index'],'canonical_index_sha256':b['canonical_index'],'canonical_status':'clean','integration_status':status,'integration_files':work,'canonical_files':canonical})
data=read('DATA_QA.json');layout=read('LAYOUT_QA.json');contents=read('CONTENTS_REGRESSION_QA.json');interaction=read('INTERACTION_QA.json');new=read('NEW_BOOK_BROWSER_QA.json');ui=read('UI_SUPPLEMENT_QA.json');reg=read('ESTABLISHED_RANGE_QA.json') if (P/'ESTABLISHED_RANGE_QA.json').exists() else read('BROWSER_QA.json');bamberg=read('BAMBERG_BROWSER_QA.json');align=read('ALIGNMENT_ALL_QA.json');follow=read('FOLLOWUP_GATE_QA.json');multi=read('XI_MULTISPAN_GATE_QA.json');protected=read('PROTECTED_SOURCE_GATE_QA.json');pi=read('PROTECTED_INTERACTION_QA.json')
for name,d in [('data',data),('layout',layout),('contents',contents),('interaction',interaction),('new',new),('ui',ui),('bamberg',bamberg),('alignment',align),('followup',follow),('Bellum',protected),('protected interactions',pi)]:assert d['result']=='PASS',name
assert not reg['errors'] and reg['traditional']['executable']==5034 and reg['traditional']['unavailable']==33
assert sum(x['selections'] for x in reg['niese'].values())==2456
assert sum(x['alignment_units'] for x in align['checks'])==1441
assert bamberg['division_identities']==198 and bamberg['language_displays']==594
assert multi['canonical_membership_no_duplication']==multi['interpolations_retained']=='PASS'
assert interaction['verifiedSelections']==3157 and len(interaction['checks'])==10
N={'t':'http://www.tei-c.org/ns/1.0'};greek=[]
for book in [8,10]:
 f=R/f'assets/xml/antiquities/paratext/niese/book-{book:02}-contents.xml';e=E.parse(str(f));n=len(e.xpath('//t:div[@type="contents"]/t:list/t:item',namespaces=N));assert n==12
 greek.append({'book':book,'Greek_source_entries':n,'Whiston_headings':15 if book==8 else 11,'Latin_source_contents':'neutral unavailable','physical_contents_sha256':h(f.read_bytes()),'browser_exact_source_projection':'PASS'})
# The fresh interaction capture has exactly twelve Greek item nodes in each target list.
for e in contents['checks']:
 if e['book'] in [8,10]:assert e['greek']=='own contents' and e['entries']==(15 if e['book']==8 else 11)
save('CONTENTS_QA.json',{'result':'PASS','records':59,'previous_records_exact':39,'Whiston_books':20,'headings':256,'interval_summaries':40,'source_schema_checks':data['executed_checks'],'audit_packets_verified':data['packets'],'display_themes':2,'display_widths':[1690,1200],'full_Whiston_layout_displays':len(layout['checks']),'entry_geometry_checks':layout['entryChecks'],'continuation_line_checks':layout['wrappedLineChecks'],'single_provenance':True,'originals_and_regularized_readings_exact':True,'existing39_exact_browser_checks':contents['existing'],'critical_book_contents_counts':greek,'URL_history_pane_roundtrips':len(contents['interactions']),'book_switches':contents['bookSwitches'],'keyboard':contents['keyboard'],'source_edition':'Auburn and Rochester: Alden & Beardsley, 1856; editorial compiled index','III8':'OF THE PRIESTHOOD OF AARON (no terminal full stop)','III15':'full approved source wording preserved','V3':'THEM preserved','deferred_Greek_V_stigma':'unchanged; not adjudicated'})
save('NIESE_QA.json',{'result':'PASS','verified_selection_total':interaction['verifiedSelections'],'coverage':'I-VIII and X; IX and XI-XX unavailable','prior_I_VII':2456,'new_selection_events':701,'Greek_exact_displays':701,'Latin_available_intervals':700,'Latin_explicit_unavailable':['X.108'],'English':'Broader aligned context explicitly labelled for all701; not exact independent segmentation','per_book_menu_identity_inventory':interaction['availability'],'VIII_X_fresh_browser':new,'focused_URL_history_endpoints_themes':ui})
save('ESTABLISHED_RANGE_QA.json',reg)
save('REGRESSION_QA.json',{'result':'PASS','traditional':reg['traditional'],'I_VII_Niese':reg['niese'],'Bamberg':{'identities':198,'language_displays':594,'same_Niese_different_physical_pairs':6,'URLs':'compact row identity round trips'},'Alignment_units':1441,'Alignment_language_comparisons':4323,'Book_and_Alignment_DOM':'exact vs canonical ad3158b (current pre-combination baseline)','chapter_availability_checks':len(follow['availability']),'zero_Subchapter_chapters':follow['zero_subchapter_chapters'],'prefix_clipping_checks':len(follow['prefixChecks']),'VI':follow['VI'],'XI_multispan_checks':len(multi['checks']),'XI_internal_citation_checks':len(multi['citationChecks']),'cross_work_book_configurations':reg['crossWork'],'Bellum_Niese_citations_per_English_witness':sum(x['niese'] for x in protected['checks'] if x['source']=='whiston'),'Bellum_source_book_configurations':len(protected['checks']),'protected_interaction_configurations':len(pi['checks']),'protected_interactions':pi,'production_corrections_required':False})
save('BROWSER_QA.json',{'result':'PASS','actual_fresh_Jekyll_build':read('ENVIRONMENT.json'),'combined_contents_Niese_interactions':interaction['checks'],'Whiston_20_books_2_themes_2_widths':len(layout['checks']),'all_59_contents_records':'PASS','new_Niese_selector_events':701,'critical_uninstrumented_URL_checks':len(new['uninstrumented']),'critical_new_Niese_URL_history_pane_checks':len(new['navigation']),'keyboard_history_themes_other_works':'PASS','screenshots':sorted(str(x.relative_to(P)).replace('\\','/') for x in (P/'screenshots').glob('*.png')),'visually_inspected':['screenshots/Antiquities-8-contents-light.png','screenshots/Antiquities-10-niese-108-dark.png','screenshots/Antiquities-10-contents-dark.png','screenshots/Contents-20-light.png','screenshots/Contents-14-light.png','screenshots/Antiquities-9-unsupported-Niese-dark.png'],'browser_exceptions':0,'console_errors_in_new_and_interaction_suites':0,'failed_requests':0,'clipping_overflow_or_duplicate_ids':'NONE'})
# Reference policies and initial harness evidence; no historical report is rewritten.
(P/'SOURCE_AUTHORITY.md').write_text('''# Combined certification authorities — 9 October 2026

This verification accepts the completed Whiston and Antiquities VIII/X scholarly decisions. No PDF or manuscript was reopened and no accepted source reading was revised.

Whiston governing edition: William Whiston, trans., The Works of Flavius Josephus, Auburn and Rochester: Alden & Beardsley, 1856. The per-book index arrangement and sentence case are editorial. Historical uppercase readings remain exact in orig, visible case-only readings in reg. III.8 has no terminal point; III.15 is the complete approved clause; V.3 retains THEM.

Original source audit manifest: 6c74c1e98987483b4193a34f457f2671429ef93e5050b1e114ddd83a86b7aa08 (342 entries verified afresh by validate-contents.py). Book III supplement: 356f8dbaece44e1c686a98f6e4c5b59dbc2c4818341e4aa9fd4986f350175591 (106 entries verified). Curated original/derived sources, collation, TEI All schema, editorial capitalization concordance and historic browser evidence remain unchanged in review/Whiston_Antiquities_Compiled_Index_2026-10-09. The question of the 1737 advertised Contents remains separate; this certificate makes no absence claim.

VIII/X authorities remain in the three original accepted packets: review/Antiquities_Niese_Batch_08_10_2026-10-08, review/Antiquities_Niese_Implementation_08_10_2026-10-09, review/Antiquities_Niese_Integration_08_10_2026-10-09. EXPECTED_INTERVALS.json is copied exactly as a test input; adopted registry and corpus bytes are canonical-identical. X.108's Latin absence, partial/qualified correspondences and broader English contexts are preserved. Greek Book V's deferred stigma issue is untouched.

All complete historical packet hashes and committed file comparisons are in SOURCE_PRESERVATION_QA.json and CHERRY_PICK_INTEGRITY.json. This new additive packet records current combined execution, not a revision of their historical findings.
''',encoding='utf-8')
(P/'diagnostics/HARNESS_NOTES.md').write_text('''# Initial harness findings

1. The initial clean assertion saw the new untracked verification script itself. Initial Git status was verified clean before any writes. The corrected baseline excludes only this additive packet; all tracked hashes and both indices are compared independently.
2. Default system Python lacks lxml. Validation was rerun successfully with the bundled dependency Python; no installation or source change was made.
3. Initial Back/Forward checks waited only for viewing level, so two Niese states could be confused while rendering. INTERACTION_INITIAL_TIMING_QA.json/log preserve that attempt. Final checks require a new render revision and exact identity before comparing complete pane text.
4. The built DEH reader correctly retained the test-only baseline=1 parameter in generated comparison links. PROTECTED_TEST_QUERY_DIFFERENCE.json records the entire difference. Final differential checks compare the old/current renderer and normalize only that injected parameter in comparison links; all source state and other URL parameters remain checked.
5. The historical Alignment gate used pre-VIII/X a480215. In VIII its empty milestones differ from the approved canonical renderer's displayed Niese numerals. ALIGNMENT_PRE_VIII_X_DIFFERENCE.json and logs preserve evidence. Final complete Book/Alignment DOM checks use canonical ad3158b, the correct pre-combination authority, and pass without stripping numerals or changing production.

All final accepted results are at the packet root. Initial INTERACTION_FAILURE/DIFFERENCE artifacts at the root are test-attempt diagnostics; the final PROTECTED_INTERACTION_QA.json and INTERACTION_QA.json supersede them. No failed attempt is represented as a successful run.
''',encoding='utf-8')
text=f'''# Combined Whiston + Antiquities VIII/X certification — 9 October 2026

**GO — Combined Whiston + Niese VIII/X integration certified.** Production remained unchanged. Only this additive certification packet was created; it remains unstaged and uncommitted.

Integration branch: codex/whiston-niese-combined-integration. HEAD: 6ef5cf7d6c19528ef26cdee855aabd57735f1877. Canonical v2-development HEAD/origin: ad3158b7a86dea6997510b3de17f2e510c23367c, clean and unchanged. Ancestry divergence is 0 2. Original 3553a746d1c45e68f78df0d59ed5a2d6a1c8c628 / e373ee190a153e717ccad20de969033c5510bfd4 map to a858356526ccd084ef8f734865b487af5d7981df / 6ef5cf7d6c19528ef26cdee855aabd57735f1877. All501 changed files (22 production and479 historical Whiston certification) match the original committed bytes. All22 production files also match original production3553a74. No unexpected cherry-pick change exists. All eight VIII/X production files and original Niese certifications match canonical.

59 source-contents records pass: 39 existing source records exact and20 Whiston indexes, with256 original headings,40 interval summaries and unchanged Roman labels. Fresh data/source/schema validation:1052 checks. All342 source-audit and106 BookIII supplement entries verify. III.8, III.15 and V.3 remain approved. One1856 attribution, hidden exact orig, visible sentence-case reg, Coelacanth, left alignment and inline numeral/hanging indentation pass all20books ×2themes ×2widths:80 displays,1024 entry checks,2822 continuation checks. No speculative links or structural equivalences are introduced.

Actual Niese menus independently yield3157 identities:2456 inI–VII,420 inVIII,281 inX. All701 new identities are driven through actual selector events and compared with accepted Greek/Latin interval texts;700 Latin intervals and the explicit X.108 absence remain distinct. English displays labelled broader aligned context, not falsely exact segmentation. IX andXI–XX stay unavailable.

VIII/X contents counts are independent: Greek12/12, Whiston15/11; Latin retains neutral source-contents unavailability. Both Contents→Niese→Contents and Niese→Contents→Niese pass at1690/1200px in light/dark themes. Ten focused combined cases cover complete source reloading, copied/direct URLs, Back/Forward, pane toggles, reload, Chapter/Subchapter/Alignment state andVIII→IX→X switching. No stale contents/identity/parameter or contradictory control remains. Twelve critical uninstrumented production URLs additionally verify the new Niese reader. All59 source records, including Bamberg XIV supplied numerals and seven Lodge lists, pass current browser projection comparisons. The deferred GreekV issue remains unchanged.

Fresh regression results:257 Chapters,1432 Subchapters,5034 executable traditional language ranges and33 expected unavailable states;198 Bamberg identities/594 language displays and all six different-position pairs;1441 Alignment units/4323 language comparisons and full Book order;2456 priorNiese identities/7368 language comparisons;257 chapter availability checks,227 structural-prefix checks;18XI multi-span and2 internal citation checks;14other-work book configurations;4001 Bellum citations in both Whiston and Lodge across14source-book configurations;5protected interaction configurations including keyboard, history, panes, themes and Lodge notes. BookVI/XI, Greek range repair, DEH and Apion remain intact.

The site was built afresh from this worktree into {read('ENVIRONMENT.json')['build']}. Actual Chrome/Playwright tests used the built HTML, CSS, CETEI, renderer and XML. Test-only hooks expose state/settled rendering for exhaustive assertions; uninstrumented URLs are recorded separately. Both themes and narrow panes were inspected, with screenshots forVIII/X contents/Niese, IX unsupported, WhistonIII/XX and BambergXIV. No browser exceptions, failed requests, unintended duplicate DOM IDs, clipping or overflow occurred in the final executed suites. Existing local build qualification: responsive-image plugin omitted only from temporary build options because unavailable locally, as in the established local Whiston build; production config/font loading is untouched.

Integrity: all{len(work)} original integration tracked files and{len(canonical)} canonical tracked files match their full initial SHA-256 inventories. All narrative XML, corpus metadata, CSS, renderer, registries, IDs/sameAs and historic certifications are byte-identical. Both raw Git indices and HEADs are unchanged. Canonical remains clean. No stage, commit, merge, rebase, push, reset, checkout or configuration operation occurred.

Initial test-attempt diagnostics are retained separately and explained in diagnostics/HARNESS_NOTES.md. They reflect harness timing/query/baseline choices, not production corrections. No new product defect or unresolved combined blocker remains. No implementation change was necessary.

Reproduce: build_disposable.rb with combined worktree and a separate disposable destination; validate-contents.py (bundled Python/lxml); layout-qa.test.cjs; layout-contents-regression.test.cjs; niese-browser.test.cjs and --ui-supplement; combined-interaction.test.cjs; established-regressions.test.cjs and --followup-gate/--alignment-all-gate/--multispan-gate/--protected-source-gate; bamberg-regression.test.cjs; protected-interaction.test.cjs. ENVIRONMENT.json fixes the build path used by these retained scripts. preflight.py documents the one-time initial baseline; do not replace BASELINE.json during a verification rerun. finalize.py verifies existing source baselines and assembles this final packet. FILE_MANIFEST.json records all packet-relative hashes, excluding only itself.

Final status: {status}. Stop for human review. Canonical and public preview were not advanced.
'''
for a,z in [('All501','All 501'),('and479','and 479'),('All22','All 22'),('production3553a74','production 3553a74'),('and20','and 20'),('with256','with 256'),('headings,40','headings, 40'),('validation:1052','validation: 1052'),('All342','All 342'),('and106','and 106'),('BookIII','Book III'),('One1856','One 1856'),('all20books ×2themes ×2widths:80','all 20 books × 2 themes × 2 widths: 80'),('displays,1024','displays, 1024'),('checks,2822','checks, 2822'),('yield3157','yield 3,157'),('identities:2456 inI–VII,420 inVIII,281 inX','identities: 2,456 in I–VII, 420 in VIII, 281 in X'),('All701','All 701'),('texts;700','texts; 700'),('IX andXI–XX','IX and XI–XX'),('Greek12/12, Whiston15/11','Greek 12/12, Whiston 15/11'),('at1690/1200px','at 1690/1200 px'),('andVIII→IX→X','and VIII→IX→X'),('All59','All 59'),('GreekV','Greek V'),('results:257','results: 257'),('Chapters,1432','Chapters, 1,432'),('Subchapters,5034','Subchapters, 5,034'),('and33','and 33'),('states;198','states; 198'),('identities/594','identities / 594'),('pairs;1441','pairs; 1,441'),('units/4323','units / 4,323'),('order;2456','order; 2,456'),('priorNiese','prior Niese'),('identities/7368','identities / 7,368'),('comparisons;257','comparisons; 257'),('checks,227','checks, 227'),('checks;18XI','checks; 18 XI'),('and2','and 2'),('checks;14other-work','checks; 14 other-work'),('configurations;4001','configurations; 4,001'),('across14source-book','across 14 source-book'),('configurations;5protected','configurations; 5 protected'),('BookVI/XI','Book VI/XI'),('forVIII/X','for VIII/X')]:text=text.replace(a,z)
(P/'REPORT.md').write_text(text,encoding='utf-8')
entries=[{'path':str(f.relative_to(P)).replace('\\','/'),'bytes':f.stat().st_size,'sha256':h(f.read_bytes())} for f in sorted(P.rglob('*')) if f.is_file() and f.name!='FILE_MANIFEST.json']
save('FILE_MANIFEST.json',{'date':'2026-10-09','scope':'Combined integration additive certification','excluded':['FILE_MANIFEST.json'],'entry_count':len(entries),'entries':entries})
for e in entries:assert h((P/e['path']).read_bytes())==e['sha256']
print(json.dumps({'result':'GO','manifest_entries':len(entries),'manifest_sha256':h((P/'FILE_MANIFEST.json').read_bytes()),'report_sha256':h((P/'REPORT.md').read_bytes()),'integration_tracked_files_preserved':len(work),'canonical_tracked_files_preserved':len(canonical),'status':status},indent=2))
