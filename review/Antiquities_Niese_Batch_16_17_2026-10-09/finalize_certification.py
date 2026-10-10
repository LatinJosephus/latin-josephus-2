"""Issue separate local book certificates only after independent proofs and reader QA pass."""
from pathlib import Path
import json,hashlib,subprocess,datetime
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
FOLDERS=[ROOT/'review'/f'Antiquities_Niese_{n}_2026-10-09' for n in ['BookXVI','BookXVII','Batch_16_17']]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def write(p,s):p.write_text(s,encoding='utf8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args,cwd=ROOT):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=cwd,text=True).strip()
def reference(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
def historical(p):
    target=p.with_name(p.stem+'_HISTORICAL_PRE_IMPLEMENTATION'+p.suffix)
    assert not target.exists();target.write_bytes(p.read_bytes());return reference(target)
def manifest(production):
    path=BATCH/'REVIEW_FILE_MANIFEST.json'
    files=[dict(**reference(p),bytes=p.stat().st_size) for folder in FOLDERS for p in sorted(folder.rglob('*')) if p.is_file() and p!=path]
    save(path,dict(status='LOCALLY_CERTIFIED_XVI_AND_XVII_REVIEW_MANIFEST',base_commit=read(BATCH/'BASELINE.json')['base_commit'],
        folders=[p.relative_to(ROOT).as_posix() for p in FOLDERS],files=files,manifest_excludes_itself=True,
        production_changed_paths=production,implemented_new_identities=759))
    assert all(sha(ROOT/x['path'])==x['sha256'] for x in files)
def main():
    base=read(BATCH/'BASELINE.json');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    assert git('branch','--show-current')==base['branch']
    reports={name:read(BATCH/name) for name in ['NEW_BOOK_BROWSER_QA.json','CONTAINING_VIEWS_BROWSER_QA.json','PROTECTED_BROWSER_QA.json','PROTECTED_SOURCE_GATE_QA.json']}
    assert all(v['status'].startswith('PASS_') for v in reports.values())
    new=reports['NEW_BOOK_BROWSER_QA.json'];containing=reports['CONTAINING_VIEWS_BROWSER_QA.json'];protected=reports['PROTECTED_BROWSER_QA.json']
    assert protected['prior_Niese_selection_count']==5231 and sum(x['identities'] for x in protected['books'])==5231
    assert sum(x['identity_count'] for x in new['books'].values())==759
    assert sum(x['containing_view_count'] for x in containing['books'].values())==311
    assert sum(len(x['legacy_chapters']) for x in containing['books'].values())==35
    assert len(new['book_transitions'])==3 and len(new['themes'])==2
    for report in reports.values():
        assert not report.get('errors') and not report.get('consoleErrors') and not report.get('requestFailures')
        for item in report['built_source_hashes']:assert sha(ROOT/item['file'])==item['sha256']
    assert read(BATCH/'INDEPENDENT_IMPLEMENTATION_SOURCE_PROOF.json')['all_non_scope_pinned_files_unchanged']
    for packet in read(BATCH/'EXTERNAL_STRUCTURAL_PROVENANCE.json'):
        for item in packet['files']:assert sha(Path(item['path']))==item['sha256']
    print_sources=read(BATCH/'PRINTED_SOURCES.json')
    for name in ['Niese','Loeb']:assert sha(Path(print_sources[name]['path']))==print_sources[name]['sha256']
    canonical=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
    external_status=dict(path=str(canonical),HEAD=git('rev-parse','HEAD',cwd=canonical),status_porcelain=git('status','--porcelain',cwd=canonical),read_only_inspection=True)
    production=['assets/js/renderTei.js',*[f'assets/xml/antiquities/{l}/book-{b}.xml' for b in [16,17] for l in ['Latin','Greek']],*[f'assets/xml/antiquities/niese/book-{b}.json' for b in [16,17]]]
    certificates={};previous_source_checkpoints=git('log','--format=%H %s',base['base_commit']+'..HEAD').splitlines()
    for b,roman,expected in [(16,'XVI',404),(17,'XVII',355)]:
        p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
        proof=read(p/'INDEPENDENT_IMPLEMENTATION_SOURCE_PROOF.json');ledger=read(p/'APPLIED_RAW_BYTE_PATCH.json');rows=read(p/'BOUNDARIES.json')
        audit=read(p/'COMPLETE_PRIMARY_SOURCE_AUDIT.json');a=new['books'][str(b)];c=containing['books'][str(b)]
        assert proof['status'].startswith('PASS_') and proof['logical_identities']==a['identity_count']==len(rows)==expected
        assert [x['number'] for x in a['selections']]==list(range(1,expected+1))
        assert all(x['actual_selector']==x['next_previous']=='PASS' for x in a['selections'])
        assert sha(ROOT/ledger['registry']['relative'])==ledger['registry']['sha256']
        for row in rows:
            assert row['applied'] and row['implementation_approved'] and row['print_observation']['image_inspected'] and row['complete_interval_and_neighbours_read']
            row['reader_certified']=True;row['implementation_state']='APPLIED_AND_INDEPENDENTLY_LOCALLY_CERTIFIED'
            row['certification_state']='PASS_SOURCE_RECOVERY_ACTUAL_REGISTRY_AND_BUILT_READER'
            row['Greek_reviewed_interval']['status']='APPROVED_PRINT_SUPPORTED_INTERVAL_APPLIED_AND_READER_VERIFIED'
            row['certification_evidence']=dict(source='INDEPENDENT_IMPLEMENTATION_SOURCE_PROOF.json',reader='../Antiquities_Niese_Batch_16_17_2026-10-09/NEW_BOOK_BROWSER_QA.json',number=row['number'])
        save(p/'BOUNDARIES.json',rows)
        decisions=['DECISION_XVI_294_295','DECISION_XVI_351_355_356'] if b==16 else ['DECISION_XVII_024_025','DECISION_XVII_075_076']
        for name in decisions:
            decision=read(p/(name+'.json'));assert decision['editor_adjudication']['alternative']=='B'
            decision['status']='CLOSED_EDITOR_APPROVED_B_APPLIED_AND_LOCALLY_CERTIFIED';decision['applied']=decision['certified']=True
            decision['certification_evidence']='CERTIFICATION.json';save(p/(name+'.json'),decision)
            packet=p/(name+'.txt');historical(packet)
            write(packet,'CLOSED: editor approved B on 2026-10-10; applied and independently locally certified.\nRejected alternatives and the original complete packet follow as historical evidence.\n\n'+packet.read_text(encoding='utf8'))
        if b==17:
            packet=p/'DECISION_XVII_030_031.json';decision=read(packet)
            decision['historical_pre_application_status']=decision['status'];decision['status']='ROUTINE_PRINT_SUPPORTED_GREEK_CLAUSE_START_APPLIED_AND_LOCALLY_CERTIFIED'
            decision['applied']=decision['certified']=True;decision['certification_evidence']='CERTIFICATION.json';save(packet,decision)
        history=read(p/'DECISION_HISTORY.json');history.append(dict(kind='INDEPENDENT_LOCAL_BOOK_CERTIFICATION',date_UTC=now,
            identities=expected,all_individual_new_selections_and_next_previous='PASS',all_containing_and_legacy_views='PASS',byte_exact_recovery='PASS',all_5231_prior_selections='PASS',closed_editor_decisions=decisions,
            implemented=True,reader_certified=True,certificate='CERTIFICATION.json'))
        save(p/'DECISION_HISTORY.json',history)
        ledger['status']='APPLIED_AND_INDEPENDENTLY_LOCALLY_CERTIFIED';save(p/'APPLIED_RAW_BYTE_PATCH.json',ledger)
        original_audit=historical(p/'COMPLETE_PRIMARY_SOURCE_AUDIT.json')
        registry=read(ROOT/ledger['registry']['relative'])
        qualified_present=[s['number'] for s in registry['sections'] if s['Latin']['available'] and s['Latin'].get('note')]
        audit.update(status='COMPLETE_PRIMARY_REVIEW_EDITOR_ADJUDICATION_IMPLEMENTATION_AND_LOCAL_CERTIFICATION',historical_source_audit=original_audit,
            pending_editorial_identities=[],qualified_present_identities=qualified_present,source_edits=True,new_start_milestones=proof['added_markers']['START_MILESTONE'],
            new_end_or_other_anchors=sum(v for k,v in proof['added_markers'].items() if k!='START_MILESTONE'),
            implemented_selectable_identities=expected,source_byte_recovery='PASS_TWO_INDEPENDENT_BYTE_REVERSALS',
            new_Niese_reader_selections_tested=expected,independent_book_certification=True)
        save(p/'COMPLETE_PRIMARY_SOURCE_AUDIT.json',audit)
        certificate=dict(status='INDEPENDENTLY_LOCALLY_CERTIFIED',book=b,date_UTC=now,base_commit=base['base_commit'],branch=base['branch'],worktree=base['worktree'],runtime=base['runtime'],
            pinned_remote_context={k:base[k] for k in ['canonical_HEAD','origin_tracking_tip','live_origin_tip','baseline_selection_reason']},
            canonical_finish_read_only_inspection=external_status,independence='Independent raw-byte reversal, token removal, lxml actual-locator coverage and actual built-browser comparison against immutable baseline. No automatic alignment alone or syntax-only certification.',
            identities=expected,present_Latin_identities=proof['present_Latin_identities'],physical_Latin_fragments=proof['physical_Latin_fragments'],unavailable_Latin_identities=proof['unavailable_identities'],
            retained_Niese_starts=len(proof['retained_source_anchors']),retained_source_anchors=proof['retained_source_anchors'],new_start_milestones=proof['added_markers']['START_MILESTONE'],extra_anchors={k:v for k,v in proof['added_markers'].items() if k!='START_MILESTONE'},
            qualified_runtime_notices=proof['qualified_runtime_notices'],qualified_present_correspondences=qualified_present,
            present_runtime_correspondence_notices=len(qualified_present),source_unavailable_runtime_notices=len(proof['unavailable_identities']),
            Greek_retained_existing_citation_labels=expected-1,Greek_added_first_citation_labels=1,Greek_explicit_first_citation=True,Greek_other_marker_edits=[31] if b==17 else [],
            Greek_extent_notice_retained=True,printed_Niese_pages=audit['printed_Niese_pages'],all_individual_Latin_intervals_and_neighbours_reviewed=True,
            source_byte_proofs=proof['source_byte_proofs'],byte_exact_recovery=True,all_included_Latin_characters_covered_exactly_once=True,physical_order_preserved=True,no_philological_text_changes=True,
            reader=dict(all_new_individual_selections=expected,next_previous='PASS',independent_Whiston_context='PASS_UNCHANGED_BASELINE_ALIGNMENT',
                containing_views=c['containing_view_count'],legacy_chapters=len(c['legacy_chapters']),all_containing_endpoints='PASS_EXACT_BASELINE_DOM',
                direct_reload_history_fragment_and_uninstrumented_controls='PASS',themes='PASS',pane_switches='PASS',book_transitions='PASS',console_and_network='NO_ERRORS',
                XML_ID_uniqueness='PASS',DOM_ID_integrity='No new duplicates; unchanged BookXVII baseline English annotation repetitions explicitly recorded'),
            protected_prior_Niese=5231,all_non_scope_pinned_files_unchanged=True,source_English_structure_TOC_apparatus_material_and_existing_ID_preservation='PASS',
            editorial_decisions_closed=decisions,rejected_alternatives_retained=True,editor_approval_record=reference(BATCH/'EDITOR_ADJUDICATION_ALL_B.json'),
            source_proof=reference(p/'INDEPENDENT_IMPLEMENTATION_SOURCE_PROOF.json'),QA_reports=[reference(BATCH/name) for name in reports],
            preserved_source_qualified_coordinates=reference(p/'PROTECTED_STRUCTURAL_COORDINATES.json'),
            mandatory_regression_clusters=['234-236','355-357','367-369','traditional viii.2','traditional xi.1','Bamberg XX'] if b==16 else ['105-107','145-147','298-300','Greek traditional v.5 at epi toutois','Bamberg X versus traditional vi','Bamberg XVIIII versus traditional xi'],
            production_changed_paths=[x for x in production if x=='assets/js/renderTei.js' or f'book-{b}.' in x],local_checkpoints_before_certificate=previous_source_checkpoints,
            executable_verification_scripts=['verify_implemented_sources.py','new-books-browser.cjs','containing-views-browser.cjs','protected-browser.cjs','protected-source-gates.cjs'],
            ready_for_coordinated_canonical_integration=True,merged=False,pushed=False,published=False,deployed=False)
        save(p/'CERTIFICATION.json',certificate);certificates[str(b)]=reference(p/'CERTIFICATION.json')
        lines=[f'ANTIQUITIES {roman} — INDEPENDENTLY LOCALLY CERTIFIED',f"Pinned canonical/origin baseline: {base['base_commit']}.",f"Branch/worktree: {base['branch']} / {base['worktree']}.",f"Runtime: {base['runtime']}.",'',
            f"Niese identities {expected}; Latin present {proof['present_Latin_identities']}; physical fragments {proof['physical_Latin_fragments']}; unavailable {len(proof['unavailable_identities'])}.",
            f"Retained executable starts {len(proof['retained_source_anchors'])}; new Latin starts {proof['added_markers']['START_MILESTONE']}; extra anchors {sum(v for k,v in proof['added_markers'].items() if k!='START_MILESTONE')}; qualified runtime notices {proof['qualified_runtime_notices']}.",
            f"All Niese IV printed pages {audit['printed_Niese_pages']['printed'][0]}–{audit['printed_Niese_pages']['printed'][-1]} (PDF {audit['printed_Niese_pages']['pdf'][0]}–{audit['printed_Niese_pages']['pdf'][-1]}) visually checked; each Greek interval and Latin correspondence with neighbours reviewed.",
            'All disputed B choices approved by the editor, implemented and closed. Original alternatives remain in the packets. Causes of omissions/displacement remain undetermined.',
            'Segmentation only; complete witness text, punctuation, physical order, existing IDs/divisions, apparatus and material marking preserved.','',
            'Two independent raw-byte reversals recover the exact pinned sources:']
        for item in proof['source_byte_proofs']:lines.append(f"  {item['language']}: original/recovery SHA256 {item['original_sha256']}; implemented SHA256 {item['implemented_sha256']}.")
        lines.extend(['',f"All {expected} actual selector selections and next/previous controls PASS. Greek exact display and original Whiston aligned context independently checked.",
            f"All {c['containing_view_count']} containing/whole/contents selections and {len(c['legacy_chapters'])} inherited legacy endpoints PASS against immutable actual build.",
            'Direct URLs, reload, history, query plus fragment, uninstrumented controls, themes and panes PASS. No new console/network or ID errors.',
            'All 5,231 prior Niese views PASS exact baseline comparison; all20 Antiquities structural/TOC controls and Bellum/Cardwell/Whiston/Lodge, Contra Apionem and DEH remain protected.',
            'Certificate: CERTIFICATION.json. Exact boundaries/history: BOUNDARIES.json and DECISION_HISTORY.json.',
            'Source reversal ledger/proof: APPLIED_RAW_BYTE_PATCH.json and INDEPENDENT_IMPLEMENTATION_SOURCE_PROOF.json.',
            'Actual QA reports and complete hashed evidence manifest: ../Antiquities_Niese_Batch_16_17_2026-10-09/.',
            'Earlier source-audit handoff and preliminary proposal filenames are historical records; this certificate supersedes their pending state.',
            'Final local Git hashes and clean status are recorded after the final commit in the owned runtime FINAL_GIT_HANDOFF.json and the final response.',
            'Ready for coordinated canonical integration. No merge, push, publication or deployment.',''])
        write(p/'BOOK_HANDOFF.txt','\n'.join(lines))
        old_handoff=p/'SOURCE_AUDIT_HANDOFF.txt';historical(old_handoff)
        write(old_handoff,'HISTORICAL SOURCE-AUDIT CHECKPOINT; superseded by BOOK_HANDOFF.txt and CERTIFICATION.json.\n\n'+old_handoff.read_text(encoding='utf8'))
        print(roman,'CERTIFIED',expected,'new selections;',c['containing_view_count'],'containing views;',len(c['legacy_chapters']),'legacy endpoints')
    hold=BATCH/'EDITORIAL_HOLD.txt';historical(hold)
    write(hold,'ALL FOUR EDITORIAL DECISIONS CLOSED — B APPROVED 2026-10-10, IMPLEMENTED AND LOCALLY CERTIFIED.\nNo outstanding approval or scholarly hold. Full direct-user approval: EDITOR_ADJUDICATION_ALL_B.json.\nThe original summary and rejected alternatives follow as historical evidence.\n\n'+hold.read_text(encoding='utf8'))
    for name in ['BATCH_HANDOFF.txt','CHECKPOINT_STATUS.txt','RENDERER_APPLICATION_PLAN_PENDING_EDITOR.txt']:historical(BATCH/name)
    write(BATCH/'RENDERER_APPLICATION_PLAN_PENDING_EDITOR.txt','HISTORICAL PRE-ADJUDICATION PLAN; implemented and superseded by CERTIFICATION.json.\n\n'+(BATCH/'RENDERER_APPLICATION_PLAN_PENDING_EDITOR.txt').read_text(encoding='utf8'))
    counts=read(BATCH/'APPLIED_BATCH_COUNTS.json');counts['status']='INDEPENDENTLY_LOCALLY_CERTIFIED';save(BATCH/'APPLIED_BATCH_COUNTS.json',counts)
    original_batch_audit=historical(BATCH/'COMPLETE_PRIMARY_SOURCE_AUDIT.json')
    save(BATCH/'COMPLETE_PRIMARY_SOURCE_AUDIT.json',dict(status='BOTH_BOOKS_REVIEWED_EDITORIALLY_CLOSED_IMPLEMENTED_AND_INDEPENDENTLY_LOCALLY_CERTIFIED',
        historical_source_audit=original_batch_audit,books={str(b):read(ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09/COMPLETE_PRIMARY_SOURCE_AUDIT.json') for b,roman in [(16,'XVI'),(17,'XVII')]},
        independent_batch_certification=True,total_new_identities=759,prior_count=5231,local_selectable_total=5990))
    failure_history=dict(status='ALL_RECORDED_FAILURES_RESOLVED_AND_SUPERSEDED_BY_FINAL_PASS_REPORTS',
        failures=[dict(issue='Hash-only selection syntax was unsupported at baseline; test now uses established query with an anchor fragment.',kind='TEST_HARNESS',pass_report='NEW_BOOK_BROWSER_QA.json'),
        dict(issue='Theme color was sampled before its existing transition completed, then compared with an assumed light color. Actual baseline computed colors are now the independent oracle.',kind='TEST_HARNESS',pass_report='NEW_BOOK_BROWSER_QA.json'),
        dict(issue='Unitless original image milestones were excluded from frozen structural ordinal endpoints; new registries now retain every original milestone unit.',kind='IMPLEMENTATION_METADATA_REGRESSION_FIXED',pass_reports=['CONTAINING_VIEWS_BROWSER_QA.json','PROTECTED_BROWSER_QA.json']),
        dict(issue='Frozen and concurrent language objects had different key order with identical DOM values; legacy test now compares each language value.',kind='TEST_HARNESS',pass_report='CONTAINING_VIEWS_BROWSER_QA.json'),
        dict(issue='Book changes restore the whole-book viewing level. The transition test now chooses the Niese radio before its selector. Completed all759 selection evidence was retained only after verifying identical final build hashes.',kind='TEST_HARNESS',pass_report='NEW_BOOK_BROWSER_QA.json')],
        retained_failure_artifacts=[reference(p) for p in BATCH.glob('*FAILURE.json')]+[reference(p) for p in BATCH.glob('*MISMATCH*.json')])
    save(BATCH/'QA_FAILURE_HISTORY_AND_RESOLUTION.json',failure_history)
    save(BATCH/'VISUAL_READER_QA.json',dict(status='PASS_VISUALLY_INSPECTED_ACTUAL_READER_SCREENSHOTS',date_UTC=now,
        screenshots=[reference(p) for p in sorted((BATCH/'evidence').glob('candidate-*.png'))],
        inspected_all_listed_images=True,findings=['All three witness panes and contextual Whiston notice are readable.',
            'Approved physical fragments and reciprocal partial correspondence notices are visible; retained source spelling and punctuation remain visible.',
            'Unavailable XVI Latin selection shows a source-specific notice while Greek and English survive independently.',
            'Bamberg internal chapter numerals survive inside the exact Niese selections; XVII355 preserves the explicit book tail.',
            'Light and dark theme final colors match the unchanged actual baseline; correspondence notice contrast is readable.',
            'The existing XVII annotations bar is retained; no new structural or layout regression observed.']))
    batch_certificate=dict(status='BOTH_BOOKS_INDEPENDENTLY_LOCALLY_CERTIFIED',date_UTC=now,base=base,books=certificates,
        local_selectable_count=5990,prior_count=5231,new_count=759,actual_all_new_selections_and_next_previous='PASS',actual_containing_views=311,actual_legacy_endpoints=35,
        protected_prior_5231='PASS',other_works_and_source_witness_gates='PASS',production_paths=[reference(ROOT/x) for x in production],
        protected_input_manifest=reference(BATCH/'ALL_BASE_FILES.json'),source_proof=reference(BATCH/'INDEPENDENT_IMPLEMENTATION_SOURCE_PROOF.json'),
        QA_reports=[reference(BATCH/name) for name in reports],resolved_failure_history=reference(BATCH/'QA_FAILURE_HISTORY_AND_RESOLUTION.json'),
        canonical_finish_read_only_inspection=external_status,ready_for_coordinated_canonical_integration=True,
        Git_final_state_record=str(Path(base['runtime'])/'FINAL_GIT_HANDOFF.json'),
        merged=False,pushed=False,published=False,deployed=False,other_workbots_untouched=True)
    save(BATCH/'CERTIFICATION.json',batch_certificate)
    write(BATCH/'BATCH_HANDOFF.txt','\n'.join([
        'ANTIQUITIES XVI–XVII — BOTH BOOKS INDEPENDENTLY LOCALLY CERTIFIED',
        f"Immutable canonical/live-origin source at isolation: {base['base_commit']}.",f"Branch/worktree: {base['branch']} / {base['worktree']}.",f"Runtime: {base['runtime']}.",
        'XVI: 404 identities; Latin 380 present / 383 physical fragments / 24 unavailable; 378 new starts, 2 reused starts, 3 extra fragment and 2 explicit end anchors; 54 qualified notices.',
        'XVII: 355 identities; Latin 355 present / 355 physical fragments / 0 unavailable; 355 new starts; 29 qualified notices.',
        'All132 Niese narrative pages and all759 Greek intervals/individual Latin correspondences reviewed. Greek extent notices preserved; explicit section1 added to each book; only XVII31 existing citation marker relocated.',
        'Four direct-user B adjudications implemented and closed; rejected alternatives, complete source and physical order retained. No outstanding scholarly question.',
        'Both books have separate CERTIFICATION.json and BOOK_HANDOFF.txt. Exact source recovery by two independent methods; actual registry covers each included Latin character once.',
        'Actual local build: all759 individual selector and next/previous tests PASS; all311 containing views and35 legacy endpoints PASS; all5231 prior Niese selections PASS.',
        'All20 Antiquities structural/TOC controls, mandatory exceptional clusters, URL/reload/history/fragment, panes, themes, Whiston context and IDs PASS. No new console/network errors.',
        'Bellum/Cardwell/Whiston/Lodge all-book Niese/chapter/unit source gates, Contra Apionem and DEH protections PASS. English source and all non-scope pinned files bitwise preserved.',
        'Seven production paths changed: generic renderer, XVI/XVII Latin and Greek XML, two new Niese registries. Exact paths/hashes and executed verification scripts are in CERTIFICATION.json and REVIEW_FILE_MANIFEST.json.',
        'Retained failure files are superseded historical evidence; QA_FAILURE_HISTORY_AND_RESOLUTION.json records the repairs and final PASS reports.',
        'Prior audit checkpoints: c963c94 and 302e4d5. Final scoped local hashes and independently checked clean status: the owned runtime FINAL_GIT_HANDOFF.json and the final response.',
        'Local selectable total5990 = frozen5231 +759. This count describes the isolated local reader.',
        'Ready for coordinated canonical integration. Canonical and other workers were inspected read-only. No merge, push, publication, preview refresh or deployment.','']))
    write(BATCH/'CHECKPOINT_STATUS.txt','BOTH BOOKS INDEPENDENTLY LOCALLY CERTIFIED.\nAll four B decisions closed; all 759 new and 5231 protected selections PASS.\nSee CERTIFICATION.json, BATCH_HANDOFF.txt, REVIEW_FILE_MANIFEST.json and the owned runtime post-commit FINAL_GIT_HANDOFF.json.\nNo merge, push or publication.\n')
    write(BATCH/'REVIEW_EVIDENCE_INDEX.txt','\n'.join([
        'CURRENT CERTIFIED RECORDS',
        'Per-book CERTIFICATION.json, BOOK_HANDOFF.txt, BOUNDARIES.json, DECISION_HISTORY.json and APPLIED_RAW_BYTE_PATCH.json describe the implemented and verified state.',
        'Batch CERTIFICATION.json, BATCH_HANDOFF.txt and the four final *_QA.json reader reports close the full assignment.',
        'The independent implementation source proofs certify source recovery and actual locator coverage separately from reader testing; their reader_certified:false is a deliberate source-only distinction.',
        'EDITOR_ADJUDICATION_ALL_B.json records the direct human approval. Four decision JSONs and TXTs now identify approved B as applied and certified; alternatives remain explicit.',
        '',
        'HISTORICAL RESEARCH AND SUPERSEDED STATES',
        '*_HISTORICAL_PRE_IMPLEMENTATION files preserve earlier audit/decision/hold/handoff bytes. The complete earlier checkpoint is also Git302e4d5.',
        '*UNREVIEWED*, *PARTIAL* and *PENDING_EDITOR* filenames retain preliminary OCR/proposals and physical partition models as research history. They are not executable authority or current holds.',
        'Original candidate coordinates/intervals in BOUNDARIES.json remain separately named from the reviewed and applied coordinates; only reviewed values feed the implementation.',
        'The earlier INDEPENDENT_SOURCE_AUDIT_CHECK and INDEPENDENT_RECOMMENDED_PARTITION_CHECK reports are frozen pre-application research checks. Current implementation proof and certificates supersede their unimplemented state.',
        '*FAILURE.json and *MISMATCH*.json retain test history. QA_FAILURE_HISTORY_AND_RESOLUTION.json attributes each cause and its final PASS report.',
        '',
        'REPRODUCTION AND PROVENANCE',
        'Pinned inputs, source PDF hashes, the132 reviewed Niese body page images, Loeb controls, exact mixed-content locators and original source-qualified structural coordinates are retained in these three review folders.',
        'Completed source audit scripts: audit_reconnaissance.py, audit_completed_review.py, audit_recommended_partition.py and mapper fixtures. They describe their original pre-application state; do not rerun them to overwrite current records.',
        'Applied once: record_editor_approval.py, implement_approved_books.py, repair_structural_endpoint_metadata.py. Raw-byte patch ledgers contain every exact edit; do not apply the insertion script twice.',
        'Independent current source proof: verify_implemented_sources.py. Candidate actual build: build-candidate.sh using the pinned Ruby image recorded in prior build evidence.',
        'Actual reader checks: new-books-browser.cjs, containing-views-browser.cjs, protected-browser.cjs and protected-source-gates.cjs; immutable baseline is in the owned runtime baseline-build/site.',
        'Theme diagnostic records actual baseline colors; inspect_theme.cjs is diagnostic only. No production styling changed.',
        'Finalization: finalize_certification.py (one-time status/history/certificate update); verify_final_handoff.py (read-only committed bytes/manifest/clean status verification, with final Git record written in the owned runtime).',
        'All exact review paths and SHA256 values are in REVIEW_FILE_MANIFEST.json. All seven production paths and SHA256 values are in the batch certificate.','']))
    manifest(production)
    print('BATCH CERTIFIED: 759 + 5,231 = 5,990 local identities. Exact manifest prepared.')
if __name__=='__main__':main()
