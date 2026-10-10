from prepare import *
import datetime

SOURCE='07057a284e3eb4999bd875cd05eb970e30886452'
MERGE='a0245745c3fd3b3a04bfb5ed8acc192cd7f01b87'
def load(n):return json.loads((PACK/n).read_text(encoding='utf-8'))
def digest(x):return sha(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode())
def main():
    build=load('BUILD_CONTEXT.json');full=load('FINAL_PROTECTED_BROWSER.full.json');base=load('BASELINE_PROTECTED_BROWSER.json')
    for group in ['corpus','xi','crosswork','special']:
        suite=load('SUITE_'+group+'.json');assert suite['status']=='PASS' and suite['build']['source_commit']==build['commit']
        for row in suite['scripts']:
            assert row['exit_code']==0 and sha((PACK/row['script'][0]).read_bytes())==row['script_sha256'] and sha(Path(row['log']).read_bytes())==row['log_sha256']
    assert full['status']=='PASS' and full['sourceBuild']==build['commit'] and not full['errors']
    assert len(full['selections'])==7350 and len(full['views'])==135 and len(full['books'])==20
    assert full['selections']==base['selections'] and full['books']==base['books'] and all(not row['duplicates'] for row in full['selections'])
    proem=load('PROEM_BROWSER_QA.json');plain=load('PLAIN_READER_QA.json');terminal=load('PLAIN_FINAL_CONTROLS.json')
    assert proem['status']==plain['status']==terminal['status']=='PASS'
    assert proem['source_build']==plain['source_build']==build['commit']
    assert len(proem['selections'])==len(proem['routes'])==len(plain['selectors'])==26
    assert [r['number'] for r in proem['stalePaneSequence']]==[25,26,25,26] and [r['n'] for r in terminal['sequence']]==[25,26,25,26]
    assert proem['wholeProemAndTransition']==plain['BookI27']['status']=='PASS'
    xi=load('READER_XI_RESULTS.json');witness=load('XI_WITNESS_ORDER_RESULTS.json');extra=load('READER_EXTRA_RESULTS.json')
    assert xi['result']==witness['result']==extra['result']=='PASS' and xi['build']==build
    assert len(xi['selectors'])==347 and len(xi['ranges'])==9 and len(xi['containing'])==120 and len(xi['navigation'])==22
    assert xi['identity_order_and_false105']==xi['view_switches']=='PASS' and len(witness['alignment'])==57 and not xi['errors'] and not witness['errors']
    assert len(extra['rank_challenges'])==4 and len(extra['uninstrumented'])==6 and len(extra['baseline_exceptions'])==2
    exceptions=extra['baseline_exceptions'];a,b=exceptions
    for key in ['hrefs','targets','unsupported_error','inventory']:assert a[key]==b[key]
    assert len(a['hrefs'])==3 and len(a['targets'])==2 and a['unsupported_error']=="TypeError: Cannot read properties of null (reading 'querySelector')"
    new=load('NEW_BOOK_BROWSER_QA.json');xx=load('BOOKXX_BROWSER.json');xxviews=load('XX_STRUCTURAL_CONTROLS.json');closure=load('BOOK_CLOSURE_BROWSER.json');groups=load('ADJUDICATED_CASES_BROWSER.json');end=load('GENERIC_END_CANDIDATE_PROOF.json')
    assert new['status']=='PASS_ALL_759_NEW_SELECTIONS_AND_NAVIGATION' and not new['errors'] and not new['consoleErrors'] and not new['requestFailures']
    assert len(new['books']['16']['selections'])==404 and new['books']['16']['Latin_unavailable']==24 and len(new['books']['17']['selections'])==355
    assert len(new['direct_navigation'])==50 and len(new['themes'])==2 and new['pane_switches']=='PASS' and len(new['book_transitions'])==3
    assert xx['status']==xxviews['status']==closure['status']==groups['status']==end['status']=='PASS'
    assert len(xx['selections'])==268 and len(xx['interactions'])==24 and not xx['errors']
    assert len(xxviews['controls'])==133 and len(xxviews['plain'])==14 and len(xxviews['source_only'])==2 and not xxviews['errors']
    assert len(groups['groups'])==4 and not groups['errors'] and not end['result']['annotationIncluded']
    assert 'AMEN' in closure['actualTrailer'] and closure['paratextOutsideNarrativeParagraphs'] and not closure['VitaIncluded'] and not closure['Niese269Created'] and closure['nextDisabled']
    cross=load('READER_FINAL_PRIOR_RESULTS.json');focused=load('FRESH_FOCUSED_CONTROLS.json');combined=load('COMBINED_EXTRA_RESULTS.json');source=load('SOURCE_CONTROLS_FINAL_BROWSER.json');ui=load('INTERFACE_CONTROLS.json')
    assert cross['result']==combined['result']=='PASS' and focused['status']==source['status']==ui['status']=='PASS'
    assert cross['build']==focused['build']==build and len(cross['books'])==21 and len(cross['cross_works'])==21 and len(cross['focused'])==13
    assert cross['Lodge_Whiston_switching']==focused['Lodge_Whiston_switching']=='PASS' and len(focused['controls'])==11 and len(source['events'])==3
    assert len(combined['identity_set'])==len(set(combined['identity_set']))==7376 and len(combined['uninstrumented'])==19 and len(combined['physical_navigation'])==2
    for r in [cross,focused,combined,source,ui]:assert not r['errors']
    assert len(ui['contents'])==9 and len(ui['keyboard'])==2
    assert load('READER_INPUT_EQUIVALENCE.json')['status']=='PASS' and load('READER_INPUT_EQUIVALENCE.json')['reader_inputs']==256
    assert load('VISUAL_QA.json')['status']=='PASS'
    assert load('CHECKPOINT_PRESERVATION.json')['status']=='PASS'
    decisions=[]
    for roman,name in [('XVI','DECISION_XVI_294_295.json'),('XVI','DECISION_XVI_351_355_356.json'),('XVII','DECISION_XVII_024_025.json'),('XVII','DECISION_XVII_075_076.json')]:
        n=f'review/Antiquities_Niese_Book{roman}_2026-10-09/{name}';assert (ROOT/n).read_bytes()==git('show',BASE+':'+n)
        decisions.append(dict(path=n,sha256=sha((ROOT/n).read_bytes()),status='Exact approved canonical decision retained'))
    save(PACK/'FOUR_B_DECISIONS_PRESERVATION.json',dict(status='PASS',review_reopened=False,decisions=decisions))
    from verify_recovery import main as verify
    verify()
    allowed=load('MERGE_RECEIPT.json')['production_sha256']
    for n,h in allowed.items():assert sha((ROOT/n).read_bytes())==sha((Path(build['site'])/n).read_bytes())==sha(git('show',SOURCE+':'+n))==h
    assert not git('diff',build['commit'],'HEAD','--','assets','_includes','_layouts','_pages','_sass','_data','bin','_config.yml','Gemfile').strip()
    prefix=PACK.relative_to(ROOT).as_posix()+'/'
    assert all(n.startswith(prefix) for n in git('diff','--name-only',SOURCE,'HEAD').decode().splitlines())
    for row in load('BUILD_ASSET_MANIFEST.json'):assert sha((Path(build['site'])/row['path']).read_bytes())==row['sha256']
    full_copy=RUNTIME/'reports/FINAL_PROTECTED_BROWSER.full.json';shutil.copyfile(PACK/'FINAL_PROTECTED_BROWSER.full.json',full_copy)
    summaries=[]
    for row in full['books']:
        rows=[s for s in full['selections'] if s['book']==row['book']];assert [s['number'] for s in rows]==row['menu']
        summaries.append(dict(book=row['book'],selections=len(rows),first=row['menu'][0],last=row['menu'][-1],status='PASS',sequence_sha256=digest(rows),duplicate_selection_IDs=0))
    save(PACK/'FINAL_PROTECTED_BROWSER.json',dict(status='PASS',fresh_replay=True,build=build,selections=7350,books=summaries,XX_containing_views=135,full_content_notes_availability_source_IDs_endpoints_and_pane_DOM_match=True,duplicates_in_all_selected_views=0,errors=[],full_evidence=info(full_copy)))
    save(PACK/'FINAL_BYTE_HASHES.json',dict(status='PASS',production=[dict(relative_path=n,**info(ROOT/n)) for n in allowed],source_restoration=load('BYTE_CERTIFICATION.json'),unrelated_production=load('PRODUCTION_PRESERVATION.json')['protected_existing_production_count']))
    gates={
      'actual_identity_menu_and_registry_population':7376,
      'complete_corpus':dict(status='PASS',Proem=26,existing_I_XX=7350,total=7376,cached_rows=0,zero_duplicate_selection_IDs=True),
      'Proem':dict(full=26,plain=26,all_direct_reload_previous_next_history=26,Latin_intervals=26,inherited_starts=4,added_starts=22,exclusive_end=1,unavailable=0,English_unchanged_context_paragraphs=4,stale_pane_sequence=[25,26,25,26],plain_stale_pane_sequence=[25,26,25,26],paratext_isolated=True,transition_to_I27='PASS',I_population=320),
      'XI':dict(selectors=347,ranges=9,containing=120,navigation=22,assembly_312_326_342='PASS',rank_declaration_order_challenges=4,original_physical_alignment_units=57,Book_and_Alignment_witness_order='PASS',two_distinct_BJ_IV105_attachments='PASS'),
      'XVI_XVII':dict(selectors=759,unavailable_XVI_Latin=24,navigation=50,all_four_B_decisions_preserved=True,critical_fragments='XVI294-295,351,355,356;XVII24-25,75-76',themes_and_panes='PASS'),
      'XVIII_XIX':dict(full_population_in_prior_replay=745,extra_plain_cases=19,unavailable_XVIII=[216,217],distinct_physical_starts=['XVIII257','XIX292'],qualified_independent_Greek_English='PASS'),
      'XX':dict(selectors=268,Latin_available=257,unavailable_Latin=list(range(27,37))+[238],containing=135,actual_structural_controls=133,plain=14,adjudicated_groups=4,source_only_annotation_isolation='PASS',exclusive_end='PASS',full_trailer_through_AMEN='PASS',Vita_excluded=True),
      'containing':dict(books=21,traditional=sum(r['traditional'] for r in cross['books']),Bamberg=sum(r['bamberg'] for r in cross['books']),Alignment=sum(r['alignment'] for r in cross['books']),contents='PASS',XV_endpoints_and_VII_XIV_qualifications='PASS'),
      'cross_work':dict(bindings=21,Niese_ranges=sum(r['niese'] for r in cross['cross_works']),structural_ranges=sum(r['ranges'] for r in cross['cross_works']),focused=13,fresh_focused=11,reader_input_equivalence=256,DEH_cache_keys_normalized=2,Bellum_Cardwell_Whiston_Lodge='PASS',Contra_Apionem='PASS',DEH='PASS',English_source_events=3),
      'interface':dict(plain_contents=9,keyboard_events=2,labels_themes_and_panes='PASS',no_new_console_network_asset_errors=True,source_only_standOff_hidden_inert_and_identical_to_fresh_baseline=True)
    }
    report='Antiquities Proem canonical integration — complete local certification\n\n'
    report+=f'Actual canonical/remote start: {BASE}\nCertified recovery source: {SOURCE}\nHistory-preserving merge: {MERGE}\nTested fresh build source: {build["commit"]}\n\n'
    report+='PASS: 7,376/7,376 complete selections (26 Proem plus all 7,350 prior identities). Each prior row matches the independent immutable baseline in full normalized Greek/Latin/English, pane DOM, source IDs, correspondence notes, availability and endpoints; none used a cached replay row. All selected views have zero duplicate IDs.\n\n'
    report+='Proem: 26/26 full and plain selections; all 26 direct/reload/history/previous/next routes; 25→26→25→26 stable in both modes; Proem→I.27 complete and separate. Four inherited Latin starts, 22 added starts, one exclusive end, zero unavailable sections. §25 retains Volentius through Quod ego nunc quidem; §26 begins literal adrerum narrationem. Both approved partial-correspondence notices retained. Four unchanged English contextual paragraphs; no invented exact English alignment. Proemium and EXPLICIT PRAEFATIO IOSEPPI remain containing-view paratext.\n\n'
    report+='Critical controls: XI 347 selections, nine assembly ranges, 120 containing views, 57 physical Alignment units and two distinct BJ IV.105 attachments. XVI/XVII all 759 independent selections and 50 navigation cases; four B decisions and 24 unavailable XVI Latin identities preserved. XVIII216–217 remain unavailable in Latin with independent Greek/English access; XVIII257 and XIX292 retain distinct physical traditional/Bamberg starts. XX all 268 selections, 135 containing views, 133 structural controls, 14 plain cases, four combined case groups, unavailable27–36/238, exclusive end and complete AMEN trailer, no Vita.\n\n'
    report+=f'All 21 Antiquities containing bindings: {gates["containing"]["traditional"]} traditional, {gates["containing"]["Bamberg"]} Bamberg and {gates["containing"]["Alignment"]} Alignment views; source contents preserved. All 21 cross-work bindings: {gates["cross_work"]["Niese_ranges"]} Niese and {gates["cross_work"]["structural_ranges"]} structural ranges, plus 13 and 11 focused controls and three real English source-selector events. All 256 reader inputs equal certified recovery after normalization of exactly two DEH build cache timestamps.\n\n'
    report+='Preservation: exact full-file Latin restoration after reversing only the 22 authorized starts and one end anchor; Greek/English byte-identical; all unrelated production Git objects unchanged. No merge conflict or renderer resolution was needed; final production hashes exactly equal the certified recovery. All original/recovery worktrees, decisions and checkpoints remain preserved.\n\n'
    report+='Only the two precisely reproduced Book-I defects remain: three inherited apparatus hrefs leading to two 404 targets, and unsupported I.1 with the exact inherited TypeError. I.27 remains supported. The unchanged hidden Book XX standOff source metadata carries xml:id=annotations alongside the UI div; the fresh baseline reproduces this encoded-source ID, with no visible/executable collision or source annotation leak. This is recorded transparently; all 7,376 selectable views have zero duplicate IDs. No new errors were accepted.\n\n'
    report+='Promotion and directly verified final commit are recorded after the normal push in the external PROMOTION_RECEIPT.json. The exact final Git changed-file manifest is written there alongside this certificate, avoiding a self-referential final commit hash. No preview export, deployment, publication or domain change is authorized or performed.\n'
    (PACK/'REPORT.txt').write_text(report,encoding='utf-8',newline='\n')
    excluded={'CERTIFICATE.json','CERTIFICATION_MANIFEST.json','FINAL_PROTECTED_BROWSER.full.json','BASELINE_PROTECTED_BROWSER.json','PROTECTED_GIT_OBJECTS.json','STRUCTURAL_CONTROLS.json'}
    manifest=[dict(path=p.relative_to(PACK).as_posix(),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in sorted(PACK.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in excluded]
    save(PACK/'CERTIFICATION_MANIFEST.json',manifest)
    save(PACK/'CERTIFICATE.json',dict(status='PASS',designation='COMPLETE MERGED READER CERTIFIED FOR SAFE CANONICAL PROMOTION',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_start=BASE,source_tip=SOURCE,merge_commit=MERGE,tested_build=build,certification_parent_commit=git('rev-parse','HEAD').decode().strip(),gates=gates,partial_correspondence_notes={str(n):load('METADATA_RECONCILIATION.json')['Latin'+str(n)] for n in [25,26]},known_baseline_defects=exceptions,preserved_source_metadata_observation=ui['source_metadata_ID_observation'],production_sha256=allowed,renderer_resolution='None: exact certified source retained',source_review_reopened=False,source_history_preserved=True,new_blockers=[],preview_published=False,final_promotion_receipt=str(RUNTIME/'PROMOTION_RECEIPT.json'),exact_final_changed_file_manifest=str(RUNTIME/'FINAL_CHANGED_FILE_MANIFEST.json'),evidence_manifest=info(PACK/'CERTIFICATION_MANIFEST.json'),full_replay_evidence=info(full_copy)))
    print('PASS all 7,376 selections and all combined integration certification gates')
if __name__=='__main__':main()
