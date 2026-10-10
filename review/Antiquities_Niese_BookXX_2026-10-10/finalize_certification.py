"""Issue final local certification only from the actual closed decisions and executed gates."""
from prepare import *
from datetime import datetime, timezone

def read(name):return json.loads((PACK/name).read_text(encoding='utf-8'))

def main():
    decisions=read('ADJUDICATION_HISTORY.json');identities=read('IDENTITIES.json')
    assert len(decisions)==4 and all(d['status']=='APPROVED' and d['choice']=='A' and d['user_response'] for d in decisions)
    assert len(identities)==268 and all(r['print_review_status']=='VISUALLY_REVIEWED' and r['individual_review_complete'] and r['editorial_closed'] and r['Latin_review_status']=='CLOSED_INDIVIDUAL_REVIEW' for r in identities)
    build=read('CANDIDATE_BUILD.json');production=build['source_commit'];qa_commit=git('rev-parse','HEAD').decode().strip()
    assert build['exit_code']==0 and git('merge-base',BASE,production).decode().strip()==BASE
    gates=['COMPLETE_PRINT_AUDIT.json','BASELINE_STRUCTURAL_BROWSER_COMPARISON.json','BASELINE_PROTECTED_BROWSER.json','FINAL_PROTECTED_BROWSER.json','BASELINE_OTHER_CONTROLS.json','FINAL_OTHER_CONTROLS.json','BOOKXX_BROWSER.json','ADJUDICATED_CASES_BROWSER.json','BOOK_CLOSURE_BROWSER.json','VISIBLE_QUALIFICATIONS_BROWSER.json','FINAL_VISUAL_INSPECTION.json','HOLD_ARCHIVE_VERIFICATION.json','BYTE_CERTIFICATION.json','COVERAGE_GATE.json','GENERIC_END_BASELINE_REPRO.json','GENERIC_END_CANDIDATE_PROOF.json']
    for name in gates:assert read(name)['status']=='PASS',(name,'Gate did not pass')
    c=read('COVERAGE_GATE.json');b=read('BYTE_CERTIFICATION.json');xx=read('BOOKXX_BROWSER.json');p=read('FINAL_PROTECTED_BROWSER.json');other=read('FINAL_OTHER_CONTROLS.json');cases=read('ADJUDICATED_CASES_BROWSER.json')
    for result in [xx,p,other,cases,read('VISIBLE_QUALIFICATIONS_BROWSER.json'),read('BOOK_CLOSURE_BROWSER.json')]:assert result['sourceBuild']==production,'Stale browser evidence'
    assert len(xx['selections'])==268 and sum(s['Latin']=='EXACT_FULL_INTERVAL_PASS' for s in xx['selections'])==257 and sum(s['Latin']=='APPROVED_UNAVAILABLE_PASS' for s in xx['selections'])==11
    assert len(p['selections'])==5231 and len(p['views'])==135 and len(p['XXlegacy'])==20
    assert len(other['routes'])==35 and len(cases['groups'])==4 and all(g['combinedDuplicateIDs']==0 for g in cases['groups'])
    assert not xx['errors'] and not p['errors'] and not other['errors'] and not cases['errors']
    assert (c['new_Latin_start_milestones'],c['primary_Latin_fragments'],c['new_exclusive_end_anchors'],c['retained_original_Latin_Niese_starts'],c['retained_original_Greek_labels'],c['new_Greek_opening_labels'])==(257,257,1,0,267,1)
    files=['assets/js/renderTei.js','assets/xml/antiquities/Greek/book-20.xml','assets/xml/antiquities/Latin/book-20.xml','assets/xml/antiquities/niese/book-20.json']
    changed=git('diff','--name-only',BASE,'--', 'assets','_includes','_layouts','_pages','_sass','_data','bin','_config.yml','Gemfile').decode().splitlines()
    assert sorted(changed)==sorted(files),'Production scope exceeded'
    source_hashes={}
    for rel in files:
        raw=(ROOT/rel).read_bytes();assert git('show',f'{production}:{rel}')==raw
        assert (Path(build['source'])/rel).read_bytes()==raw and (Path(build['site'])/rel).read_bytes()==raw
        source_hashes[rel]=info(ROOT/rel)
    save(PACK/'PRODUCTION_MANIFEST.json',dict(base=BASE,verified_production_commit=production,files=source_hashes,protected_scope='PROTECTED_INPUTS.json',untouched_English_and_other_work_content=True,only_new_reader_capability='Generic per-language endTarget plus narrow declaration of the Book XX registry.',exact_source_commit_build_and_working_bytes_match=True))
    canonical_status=git('status','--porcelain',cwd=CANON).decode();canonical_head=git('rev-parse','HEAD',cwd=CANON).decode().strip()
    # Observation only: another authorized task may advance canonical; source stays frozen.
    observation=dict(observed_at=datetime.now(timezone.utc).isoformat(),canonical_HEAD=canonical_head,canonical_status=canonical_status,our_assignment_modified_canonical=False,source_baseline_unchanged=BASE)
    save(PACK/'FINAL_CANONICAL_OBSERVATION.json',observation)
    counts={k:v for k,v in c.items() if k not in ['physical_intervals','count_method']}
    test_counts=dict(BookXX_individual_selections=268,exact_nonempty_Latin_selections=257,approved_unavailable_Latin_selections=11,adjudicated_combined_groups=4,individual_case_group_checks=sum(len(g['individual']) for g in cases['groups']),BookXX_containing_views=135,independently_resolved_structural_ranges=82,independent_three_language_structural_comparisons=246,legacy_physical_extents=20,legacy_chapter_URLs=20,prior_Niese_selections=5231,other_work_and_source_control_routes=35,critical_navigation_cases=len(xx['interactions']),new_reader_errors=0,duplicate_DOM_IDs=0)
    certificate=dict(status='LOCALLY_CERTIFIED',certified=True,ready_for_coordinated_integration=True,issued_at=datetime.now(timezone.utc).isoformat(),base=BASE,branch='antiquities-niese-20',branch_ref='refs/heads/antiquities-niese-20',worktree=str(ROOT),runtime=str(RUNTIME),port=8920,verified_production_commit=production,QA_evidence_commit=qa_commit,final_certificate_commit='Resolve refs/heads/antiquities-niese-20 after the final certificate commit; its own hash cannot be embedded in itself.',Greek_printed_identity_review='268/268 COMPLETE',individual_Latin_comparison='268/268 COMPLETE',editorial_cases_closed='4/4; all A explicitly approved by the editor',pending_cases=[],editorial_history=info(PACK/'ADJUDICATION_HISTORY.json'),original_approval=info(PACK/'EDITORIAL_ADJUDICATION_2026-10-10.txt'),previous_hold_preserved='history/EDITORIAL_HOLD_402ddb34b141 plus immutable earlier commits and unchanged CASE packets',counts=counts,test_counts=test_counts,byte_recovery=b['BookXX'],unchanged_English_BookXX_sha256=sha((ROOT/'assets/xml/antiquities/English/book-20.xml').read_bytes()),protected_production_inputs=b['protected_files'],executed_gates={name:info(PACK/name) for name in gates},production_manifest=info(PACK/'PRODUCTION_MANIFEST.json'),previous_selectable_identities=len(p['selections']),local_selectable_identities=len(p['selections'])+len(xx['selections']),known_baseline_exceptions=other['knownExceptions'],combined_test_method=cases['method'],canonical_observation=observation,source_preservation='Exact full-file recovery by reversing only authorized empty-tag insertions; original source text, order, whitespace, punctuation, IDs, sameAs, markup, paratext, English and all unrelated production content preserved.',no_merge_push_or_publication=True,new_public_release=False,integration_limit='Certified against frozen pre-XI65b source only. Coordinator must reconcile minimal shared-reader hunks with then-current canonical and rerun combined suites including any newly integrated books.')
    save(PACK/'CERTIFICATE.json',certificate)
    handoff=dict(status='LOCALLY CERTIFIED / READY FOR COORDINATED INTEGRATION',branch='antiquities-niese-20',branch_ref='refs/heads/antiquities-niese-20',base=BASE,verified_production_commit=production,QA_evidence_commit=qa_commit,worktree=str(ROOT),runtime=str(RUNTIME),review=str(PACK),certificate=str(PACK/'CERTIFICATE.json'),report=str(PACK/'REPORT.md'),approved_cases={d['case']:dict(choice=d['choice'],status=d['status'],packet=str(PACK/f"CASE_{d['case']}.json")) for d in decisions},counts={k:c[k] for k in ['logical_selectable_identities','nonempty_Latin_identities','primary_Latin_fragments','new_Latin_start_milestones','retained_original_Latin_Niese_starts','new_exclusive_end_anchors','new_Greek_opening_labels','retained_original_Greek_labels','unavailable_identities','partial_identities']},test_counts=test_counts,production_files=files,coordinator_reconciliation=['Retain frozen65b source certification and original approval/history evidence; do not rebase or overwrite another WorkBot’s worktree.','Integrate the approved Book XX XML insertions and book-specific JSON registry through a separate authorized task.','Reconcile only the narrow Book XX registry registration and generic endTarget renderer hunks with then-current v2-development; do not replace its renderer with this branch snapshot.','Preserve later XI and XVI–XIX work and rerun the actual combined identity population, containing navigation, source/byte and Whiston controls after reconciliation.','No additional editorial approval is needed for these four A decisions. Publication and canonical integration remain outside this assignment.'],publication_authorized=False,merge_push_publish_performed=False,remaining_BookXX_source_certification_work=[])
    save(PACK/'LOCAL_HANDOFF.json',handoff)
    report=f'''# Antiquities XX — final local certification

**LOCALLY CERTIFIED / READY FOR COORDINATED INTEGRATION.** All 268 printed Greek identities and all 268 individual Latin comparisons are complete. The editor explicitly approved A in all four cases, closing every editorial hold. The approved source and the real built reader have passed the final independent gates.

The immutable baseline is `{BASE}`. The isolated branch is `antiquities-niese-20`, in `{ROOT}`. The actual final build uses production commit `{production}`; the final QA evidence is committed at `{qa_commit}`. The dedicated runtime is `{RUNTIME}`. The branch tip adds this certificate and handoff; its exact final hash is resolved from the branch ref and reported on completion. No merge, push or publication occurred.

| Actual inventory | Count |
|---|---:|
| Independently selectable Greek Niese identities |268|
| Nonempty Latin identities / primary intervals / physical fragments |257 /257 /257|
| Unavailable independent Latin identities |11: XX.27–36 and XX.238|
| Newly inserted Latin start milestones |257|
| Retained original Latin Niese starts |0|
| New exclusive Latin end anchors |1, before the inherited annotation|
| Total Latin milestones (including preserved source markers) |294: 257 Niese,20 chapter,17 unqualified|
| Greek opening addition / retained original labels |1 /267|
| Traditional chapters / lower divisions |12 /50|
| Bamberg divisions / retained legacy positions |20 /20|
| Selectable Alignment units |51|
| Pending editorial holds |0|

These counts come from the actual parsed final XML and independently mapped raw byte positions, checked against the identity registry and individually reviewed extents. Each represented Latin identity has one physical interval. Their {c['assigned_Latin_characters']} projected characters plus the {c['source_only_characters']}-character annotation interval account for all {c['Latin_projection_characters']} original Latin projection characters, without overlap or unassigned narrative. The source-only interval retains `latin-book20-num34`, its exact original location, wording and line break. No annotation wording is allocated to a Niese narrative fragment.

XX.26 and XX.37 have explicitly qualified partial correspondence; XX.27–36 are independently unavailable in the present transcription. XX.59 begins at `habe inquit fiducia`, retaining the full expression once and recording its overlap with the Greek XX.58 imperative. XX.238 has no independent Latin appointment interval; XX.239 retains `quo per insidias moriente` and its missing-antecedent qualification. XX.241 starts at `Is namque primus`; `cum et pontificatum tenuisset et regnum` stays in XX.240. The compressed syntax and punctuation remain untouched. The cause of either absence is undetermined.

The exact user response, original attachment hashes, previous pending records and earlier HOLD certificate/QA are preserved in ADJUDICATION_HISTORY.json, EDITORIAL_ADJUDICATION_2026-10-10.txt and history/EDITORIAL_HOLD_402ddb34b141. All CASE packets retain their rejected alternatives and original text-node, code-point and raw-byte coordinates. Partial correspondence remains qualified for XX.26,37,218,240,241,266, with additional qualifications for XX.59 and239.

Niese IV (1890), title image5 and printed276–320/PDF290–334, was physically inspected for every identity. The complete register records each numeral's printed/PDF page, image hash, marginal line observation, original Greek XML marker, complete Greek extent and individual Latin comparison. OCR served only to locate images; it did not certify boundaries. Greek XX.1 begins at `Τελευτήσαντος δὲ τοῦ βασιλέως Ἀγρίππα`, after the unchanged41-character book-duration notice. Its sole Greek edit is `<num>[1]</num>`; no existing label moves.

Loeb IX (1965) title, all50 lower divisions, all12 chapter openings and the book ending were independently inspected. Greek ends at printed532/PDF548 and English at533/PDF549, before the separate additional note. The20 frozen Bamberg records preserve their complete physical locators, literal numerals, images and source relationships. The later external human Word audit has a different whole-file hash but its20 Book XX cells match; frozen v1.1 authority remains in force, with no new manuscript-facsimile claim.

All mandatory early and later structural windows are covered. Bamberg VI within51, XI within129, XVIIII at200 and XX at215 retain their actual points; traditional ix197, x224, xi252 and xii259 remain distinct. XX.199–201 received no textual or authenticity intervention. The complete current ending through XX.268 and its punctuation remain intact. XX.266's partial correspondence is recorded without supplying the living-witness wording. The original Latin trailer through AMEN is visible separately after268. Vita begins separately at Niese printed321/PDF335 and is excluded throughout; there is no269 identity.

| Executed final reader check | Result |
|---|---|
| All268 Book XX selections, three panes |268 exact full Greek intervals;257 exact full Latin intervals;11 explicit approved unavailable notices;268 preserved Whiston contexts; exact citation labels and no duplicate DOM IDs|
| Four adjudicated groups |25–38,57–60,237–240,239–242 individually and combined;26 member checks; source-only annotation and shared wording accounted exactly|
| All135 containing views |Book, source contents,51 Alignment units,12 traditional chapters,50 lower divisions and20 Bamberg divisions match immutable baseline|
| Independent structural spans |82 complete ranges ×3 languages =246 source-coordinate/full-text comparisons; candidate containing texts match these validated baseline extents|
| All20 legacy controls |Physical extents unchanged and all20 legacy chapter URL meanings replayed|
| Prior supported Niese population |All5,231 actual baseline selections replayed individually with matching full-text hashes, notes, availability, original paragraph IDs/sameAs and duplicate-ID state|
| Other works and source controls |35 routes passed, including XV endpoint/contents, XVI–XX Book controls, Bellum/Cardwell/Whiston/Lodge, DEH and Contra Apionem|
| Navigation and display |24 critical direct/reload/next/previous/history cases, pane/theme toggles, XIX→XX, visible qualifications and Whiston italic provenance passed|
| Generic exclusive end |Original built-reader reproduction and final generic-fix proof passed; no Book XX range conditional|
| Source fidelity |Exact Greek/Latin byte recovery; all299 protected production inputs checked; English and unrelated content unchanged|

The reader exposes individual Niese selection. Combined case QA uses its actual exact-view function for every member and native DOM ranges over the same loaded source, compared with separately prepared frozen-source projections. It does not claim an unsupported multi-Niese URL or introduce new navigation. English remains labelled aligned Whiston context, without invented exact cuts.

No new reader, console, network or asset errors were accepted. The precise inherited exceptions were reproduced against both builds: three Book-I apparatus links with404 targets and unsupported I.1's null-querySelector error (the actual supported population begins at I.27). The frozen prior population excludes later XI and XVI–XIX Niese integrations. The local total is5,499 selectable identities; this is not a public-release count. Actual Jekyll build exit0 includes inherited Sass deprecation warnings in its retained log.

| Witness | Original and independently restored SHA-256 |
|---|---|
| Greek |`{b['BookXX']['Greek']['original']}`|
| Latin |`{b['BookXX']['Latin']['original']}`|
| English, unchanged |`{certificate['unchanged_English_BookXX_sha256']}`|

Recovery reverses only the approved empty-tag additions, comparing the complete original files byte for byte. Source wording, spelling, punctuation, whitespace, line endings, Greek combining characters, old IDs/sameAs, paragraphs, order, notes, apparatus, manuscript breaks/images, chapter markers and paratext are preserved. Every English file, structure.xml, display controls, CSS and unrelated source remain unchanged. PRODUCTION_MANIFEST.json confirms the built source, built site, Git source commit and working files have the same bytes.

Exactly four production files differ from65b: assets/xml/antiquities/Greek/book-20.xml, assets/xml/antiquities/Latin/book-20.xml, assets/xml/antiquities/niese/book-20.json and assets/js/renderTei.js. The renderer adds only the Book XX registry declaration and generic per-language endTarget handling. The registry protects existing chapter-milestone ordinals through the established generic structural mechanism.

Canonical advanced independently during the audit. The source branch stays on the explicitly required pre-XI65b baseline; BASELINE.json's later canonical_HEAD observation is distinguished in CANONICAL_OBSERVATIONS.json. FINAL_CANONICAL_OBSERVATION.json records the latest read-only observation. The integration coordinator must reconcile the narrow shared-reader hunks with then-current v2-development, preserve subsequent book work and rerun the combined integrated suites. No source-certification work remains for Book XX.

The reproducible audit is in IDENTITIES.json/BOUNDARIES.csv, LATIN_PHYSICAL_SOURCE_LEDGER.json, LATIN_PHYSICAL_ORDER.json, APPROVED_INSERTIONS.json, COVERAGE_GATE.json and BYTE_CERTIFICATION.json. Executed browser scripts and full receipts accompany them. CERTIFICATE.json hashes every gate; LOCAL_HANDOFF.json records paths, commits and integration requirements. The earlier HOLD remains historical evidence only. This assignment stops at local certification and handoff.
'''
    (PACK/'REPORT.md').write_text(report,encoding='utf-8',newline='\n')
    print('LOCALLY CERTIFIED / READY FOR COORDINATED INTEGRATION; every actual gate passed, all four editorial decisions closed.')

if __name__=='__main__':main()
