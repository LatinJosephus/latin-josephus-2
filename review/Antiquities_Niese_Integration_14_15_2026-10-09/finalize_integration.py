"""Certify the final merged production bytes; never replace a frozen baseline."""
from pathlib import Path
import datetime, hashlib, json, subprocess

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
SHA = lambda b: hashlib.sha256(b).hexdigest()

def load(name):
    return json.loads((P / name).read_text(encoding='utf8'))

def save(name, obj):
    (P / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')

def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd).decode('utf8').strip()

base = load('BASELINE.json')
incoming = load('INCOMING_SCOPE.json')
build = load('BUILD_RECORD.json')
integrity = load('INTEGRITY_QA.json')
prod = load('PRODUCTION_MANIFEST.json')
tested = 'f483aabae6265478a98ad0e455d7d844fd733a71'
advance = load('CANONICAL_ADVANCE.json')
effective = advance['canonical_advance']
assert git('rev-parse', 'HEAD') == tested == build['candidate_commit'] == integrity['tested_production_commit']
assert all(x['result'] == 'PASS' for x in [build, integrity, prod])
assert len(incoming['source_history']) == 32
assert (incoming['production_count'], incoming['review_count'], incoming['total_files']) == (7, 531, 538)
assert git('status', '--porcelain', cwd=Path(base['canonical_checkout'])) == ''
assert git('rev-parse', 'HEAD', cwd=Path(base['canonical_checkout'])) == effective
assert git('status', '--porcelain', cwd=Path(base['source_checkout'])) == ''
assert git('rev-parse', 'HEAD', cwd=Path(base['source_checkout'])) == base['source_tip']

files = ['books/14/FULL_READER_QA.json', 'books/15/FULL_READER_QA.json',
         'CRITICAL_COMBINED_READER_QA.json', 'IX_CURRENT_CANONICAL_QA.json',
         'PROTECTED_BROWSER_QA.json', 'WHISTON_LAYOUT_QA.json',
         'BOOK_XIV_XV_TRANSITION_READER_QA.json', 'BOUNDED_BASELINE_EXCEPTIONS.json', 'CANONICAL_ADVANCE_READER_QA.json']
qa = {name: load(name) for name in files}
for name, record in qa.items():
    assert record.get('result', record.get('status')) == 'PASS', name
    if 'build_record' in record:
        assert record['build_record']['candidate_commit'] == tested, name
        assert record['build_record']['code_data_sha256'] == build['code_data_sha256'], name

book_qa = []
for book, total, represented, views, critical, absent in [
    (14, 491, 489, 127, [161,162,163,357,358,359,387,388,389,237,238,239,240], [238,239]),
    (15, 425, 423, 78, [39,40,41,337,338,339,346,347,348], [338,347])]:
    record = qa[f'books/{book}/FULL_READER_QA.json']
    assert record['registry_injected'] is False and not record['browserErrors']
    assert len(record['selections']) == total and len(record['containing_views']) == views
    assert record['census']['menu'] == list(range(1, total+1))
    assert len(record['census']['Latin']) == represented and len(record['census']['Greek']) == total
    for entry in record['built_files']:
        assert SHA((Path(base['runtime'])/'site'/entry['path']).read_bytes()) == entry['sha256'], entry['path']
    for n in critical:
        row = next(r for r in record['selections'] if r['number'] == n)
        assert row['duplicateIDs'] == 0 and row['Greek'] == 'EXACT_INTERVAL_PASS'
        assert row['English'] == 'PRESERVED_BROADER_CONTEXT_PASS'
    notes = {}
    for n in ([161,162,357,358,387,388] if book == 14 else [39,40]):
        containing = [v['id'] for v in record['containing_views'] if any(a['number'] == n and a['exact'] for a in v['notes'])]
        assert containing, f'{book}.{n} reciprocal containing notice missing'
        assert next(r for r in record['selections'] if r['number'] == n)['qualified']
        notes[str(n)] = containing
    book_qa.append(dict(book=book, selectable=total, nonempty_Latin_intervals=represented,
                        containing_views=views, critical_selections=critical,
                        exact_reciprocal_notices_in_containing_views=notes, unavailable=absent,
                        all_expected_selection_intervals_and_complete_views_verified=True))

ix = qa['IX_CURRENT_CANONICAL_QA.json']
assert (ix['baseline_total_selectable'], ix['total_selectable']) == (4315, 5231)
assert not ix['errors'] and not ix['consoleErrors'] and not ix['networkFailures']
critical = qa['CRITICAL_COMBINED_READER_QA.json']
assert len(critical['selections']) == 13 and len(critical['containing_views']) == 13
assert len(critical['new_book_original_views']) == 8
protected = qa['PROTECTED_BROWSER_QA.json']
assert protected['mode'] == 'protected' and len(protected['antiquities']) == 21
assert sum(r['niese'] for r in protected['antiquities']) == 4315
assert len(protected['cross_works']) == 21 and len(protected['focused_controls']) == 13
assert not protected['browserExceptions'] and not protected['consoleErrors'] and not protected['failedRequests']
whiston = qa['WHISTON_LAYOUT_QA.json']
assert (whiston['entryChecks'], whiston['wrappedLineChecks']) == (364,1160)
assert not whiston['pageErrors'] and not whiston['failedRequests']
assert len(qa['CANONICAL_ADVANCE_READER_QA.json']['cases']) == 17

images = [f'books/{b}/evidence/{n}' for b, names in [
    (14, ['local-reader-full-14-358-light.png','local-reader-full-14-358-dark.png','local-reader-full-14-availability.png']),
    (15, ['local-reader-full-15-40-light.png','local-reader-full-15-40-dark.png','local-reader-full-15-availability.png'])] for n in names]
save('VISUAL_REVIEW.json', dict(result='PASS', reviewed_by='Primary agent through view_image, final built-reader captures',
     tested_production_commit=tested, observations=[
         'XIV.358 and XV.40 qualifications readable in both themes with all three independent panes and no clipping.',
         'Transmitted interrupted XIV.358 Latin and partial XV.40 interval displayed as certified.',
         'XIV.238 and XV.338 unavailable descriptions display with no substituted Latin; Greek and labelled Whiston context remain readable.',
         'Brand images, navigation controls, text and note contrast visually verified.'],
     images=[dict(path=n, sha256=SHA((P/n).read_bytes()), actually_inspected=True) for n in images]))

compat = load('STRUCTURAL_LOCATOR_COMPATIBILITY.json')
compat.update(status='PASS', implemented_commit='cf082405078a849530b3c128c543e58304601e73',
    final_full_protected_QA='PROTECTED_BROWSER_QA.json', final_focused_containing_QA='CRITICAL_COMBINED_READER_QA.json',
    final_XV_full_reader_QA='books/15/FULL_READER_QA.json', final_candidate_code_data_sha256=build['code_data_sha256'],
    confirmed_all_registered_XV_Bamberg_and_Alignment_views_equal_preserved_current_canonical_source=True,
    final_QA_includes_all_legacy_milestone_locator_books=True)
save('STRUCTURAL_LOCATOR_COMPATIBILITY.json', compat)
resolution = load('PRODUCTION_RESOLUTION.json')
resolution['initial_merge_validation'] = resolution.pop('validation')
resolution['initial_merged_renderer_sha256'] = resolution.pop('merged_renderer_sha256')
resolution.update(final_result='PASS', complete_source_merge_commit='34435139bfabb4ef3d53187baa251f0165a92765',
    subsequent_production_resolution_commit='cf082405078a849530b3c128c543e58304601e73',
    subsequent_canonical_advance=effective,canonical_advance_merge=tested,
    canonical_advance_resolution='Clean automatic merge retains the later canonical label-only fragment correction. Full final build and all new/protected reader checks rerun against its actual baseline.',
    subsequent_resolution='Optional structuralMilestoneUnits support in traditionalPoint plus XV chapter-only registry metadata prevents new Niese markers shifting legacy structural milestone ordinals. No XML or section data changed.',
    final_validation='Full new-book and protected reader checks pass; exact Latin/Greek inverse and certified XV registry inverse pass; all current IX/XII/XIII/Whiston protected content and functions retained.',
    final_production_sha256={r['path']:r['merged_sha256'] for r in prod['files']},
    additional_production_paths=['assets/js/renderTei.js','assets/xml/antiquities/niese/book-15.json'],
    evidence='STRUCTURAL_LOCATOR_COMPATIBILITY.json')
save('PRODUCTION_RESOLUTION.json', resolution)

adaptation = load('QA_ADAPTATION.json')
adaptation['changes'] += [
    'Local servers fall back to an available port when preferred8915 is occupied; each suite has its own browser profile.',
    'XV built registry comparison removes exactly the new integration metadata line before checking the certified hash; actual built hashes still bind the full registry bytes.',
    'Predecessor XII/XIII fixtures contain Greek/Latin; English independently compared to actual current-canonical panes and hashes rather than an absent fixture field.',
    'Full protected run uses --protected; one accidental default-mode rerun additionally checked all XII selections but did not replace the protected result.',
    'Final protected rerun follows final BUILD_RECORD creation; a previous final-build run with stale provenance is retained only in diagnostics.']
helpers = ['full-reader-integration.cjs','book-browser.cjs','qa-common.cjs','ix-protected.cjs','critical-combined.cjs',
           'whiston-layout.cjs','book-transition-qa.cjs','baseline-exceptions.cjs','display-advance-critical.cjs']
adaptation['final_helpers'] = [dict(path=n,sha256=SHA((P/n).read_bytes())) for n in helpers]
save('QA_ADAPTATION.json', adaptation)

diag = P/'PREPARATION_DIAGNOSTICS.md'
with diag.open('a',encoding='utf8',newline='\n') as f:
    f.write('''

The first disposable Git-archive extraction using the filtered tar API failed under Windows filesystem restrictions. A premature build launch had also left an empty directory named build.sh where a recipe file was expected. Its resolved path was verified inside this assignment's runtime and it was empty before nonrecursive removal. Trusted archive members were then extracted with destination containment checks; the recipe was saved and subsequent complete builds succeeded. These preparation failures were not represented as completed builds.

The initial protected XV Bamberg comparison exposed a real truncation caused by new Niese milestones changing an inherited milestone ordinal. The exact failure and pre-fix results remain in diagnostics/. The separately committed reader compatibility fix is documented in STRUCTURAL_LOCATOR_COMPATIBILITY.json; the final full builds, all916 selections,205 containing views and full protected comparisons passed afterward. No editorial cut or narrative bytes changed.

An early concurrent XV browser attempt found preferred8915 occupied. The suite now selects a free fallback port without stopping any service. The predecessor fixture initially lacked the presumed English field; corrected checks use actual current-canonical English rather than manufacturing a fixture. The failed attempt is retained.

The first post-build protected pass read an older BUILD_RECORD while integrity finalization was finishing. It did exercise the final site, but its obsolete embedded provenance disqualifies it as final certification; it is retained as diagnostics/FINAL_BUILD_STALE_PROVENANCE_PROTECTED_BROWSER_QA.json. The protected suite was rerun after the final record. One invocation omitted --protected and performed an additional XII-only check; final certification uses the explicit protected mode. Local browser reruns initially hit ERR_NETWORK_ACCESS_DENIED under the sandbox. Authorized escalated localhost runs succeeded. No automatic approval-review rejection occurred.

The first promotion pre-gate correctly stopped when canonical had advanced to c28efbd while the remote remained81126ce. Its documented reader-only fix and all28 review files were frozen separately in CANONICAL_ADVANCE.json and merged cleanly in f483aab. The original BASELINE.json and81126ce archive were not replaced. The full builds and all executable gates were rerun using the actual c28efbd baseline. An app thread inventory request did not complete within the bounded preparation window and was terminated; no claim is made to have inspected another chat through that service. The filesystem report, manifests, code, actual clean checkout and direct remote evidence were inspected successfully instead.
''')

historical = [
    ROOT/'review/Whiston_Niese_Combined_Integration_2026-10-09/REPORT.md',
    ROOT/'review/Whiston_Antiquities_Compiled_Index_2026-10-09/REPORT.md',
    ROOT/'review/Whiston_Antiquities_Compiled_Index_2026-10-09/presentation-correction/initial-integration/REPORT.md',
    Path(r'C:\workspace\LatinJosephus-antiquities-niese-09-integration\review\Antiquities_Niese_Integration_09_2026-10-09\REPORT.md'),
    ROOT/'review/Antiquities_Niese_Boundary_Display_2026-10-09/REPORT.md']
for roman in ['XIV','XV']:
    historical += [ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09/{n}' for n in ['SOURCE_AUTHORITY.md','CERTIFICATION.json','COMPLETE_PARTITION_QA.json','REPORT.md']]
save('REUSED_EVIDENCE_APPLICABILITY.json',dict(result='PASS', evidence=[dict(path=str(x),sha256=SHA(x.read_bytes())) for x in historical],
    philology='Accepted print observations, decisions and independently validated text/tail/raw-byte locators reused because every frozen input and implemented corpus byte matches its source certificate. No print collation repeated.',
    Whiston='Historical source-authority/schema/display evidence retained: 59 source records,20 compiled indexes,256 accepted original/display headings, III.8/III.15/V.3 decisions. Current canonical source-contents.xml, all English sources, relevant CSS and existing behavior preserved. Fresh final-build layout and interaction checks recorded separately.',
    bounded_exceptions='Only the original three Book-I Bamberg apparatus hyperlinks with two broken targets and unsupported I.1 querySelector TypeError are inherited. Fresh exact-bound checks compare candidate and current canonical. No new error waived.',
    no_pre_fix_reader_evidence_used_as_final=True))

branches = {name:git('rev-parse','refs/heads/'+name) for name in [
    'antiquities-niese-08-10','antiquities-niese-08-10-implementation','antiquities-niese-09',
    'antiquities-niese-12-13','antiquities-niese-14-15','antiquities-niese-boundary-display']}
assert branches['antiquities-niese-14-15'] == base['source_tip']
assert branches['antiquities-niese-12-13'] == '76083c2831afdb4853f7d7ebab0db6c64c18d914'
assert branches['antiquities-niese-09'] == 'b2766fc0a0f9ab8dfb1c4667fbb9c5c4d6eac659'
assert branches['antiquities-niese-boundary-display'] == effective

certificate = dict(status='READY_FOR_AUTHORIZED_CANONICAL_FAST_FORWARD_AND_NORMAL_PUSH',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    canonical_start=base['canonical_start'],effective_canonical_baseline=effective,canonical_advance_merge=tested,remote_start_directly_verified=base['remote_start_directly_verified'],
    source_frozen_base=base['frozen_source_base'],certified_source_tip=base['source_tip'],
    provenance_checkpoint='15ecf7dd96a4f7c5d3ad8805bc9e8c211362a442',
    complete_source_history_merge='34435139bfabb4ef3d53187baa251f0165a92765',source_history_commits=32,
    tested_production_commit=tested,tested_code_data_sha256=build['code_data_sha256'],
    incoming_scope=dict(production=7,review=531,total=538), production_resolution='PRODUCTION_RESOLUTION.json',
    books=book_qa,identities_added=916,nonempty_Latin_intervals=912,retained_starts=106,added_milestones=806,
    unavailable={'XIV':[238,239],'XV':[338,347]},only_Greek_marker_additions=['XIV.1','XV.1'],
    XV_representation='423 added milestones, zero retained starts; visible labels and certified identity suppression unchanged',
    selectable_baseline=4315,selectable_combined=5231,complete_prior_identity_sets_preserved=True,
    final_reader_QA=[dict(path=n,sha256=SHA((P/n).read_bytes()),result='PASS') for n in files],
    all_new_selections=916,all_new_containing_views=205,protected_prior_selections=4315,
    protected_traditional_rows=sum(x['traditional'] for x in protected['antiquities']),
    protected_Bamberg_rows=sum(x['bamberg'] for x in protected['antiquities']),
    protected_Alignment_units=sum(x['alignment'] for x in protected['antiquities']),
    protected_cross_work_configurations=21,protected_cross_work_citations=sum(x['niese'] for x in protected['cross_works']),
    protected_cross_work_ranges=sum(x['ranges'] for x in protected['cross_works']),
    source_byte_recovery='PASS exact pinned Latin milestone inverse and Greek opening inverse; no normalization/reserialization',
    current_English_and_other_witness_preservation='PASS against actual current-canonical baseline; historical source English separately recorded',
    protected_canonical_Git_blobs=integrity['canonical_protected_Git_blobs_unchanged'],protected_canonical_actual_working_bytes_preserved=True,
    integration_checkout_line_ending_only_variants=len(integrity['integration_checkout_working_variants']),incoming_review_bytes_exact=531,
    source_certificates_unchanged=True,source_branches_preserved=branches,
    narrative_changes_after_certified_source=False,outstanding_editorial_decisions=[],known_exceptions='BOUNDED_BASELINE_EXCEPTIONS.json',
    public_preview_export_push_deployment=False,post_promotion_receipt=str(Path(base['runtime'])/'PROMOTION_RECEIPT.json'))
save('CERTIFICATE.json', certificate)

# Include every new integration packet file, excluding only its self-referential manifest.
packet_paths = sorted(x for x in P.rglob('*') if x.is_file() and x.name != 'FILE_MANIFEST.json')
# REPORT.md is created below and counted before the manifest is generated.
new_review_count = len(packet_paths) + (0 if (P/'REPORT.md').exists() else 1) + 1
report = f'''# Antiquities XIV–XV canonical integration — 9 October 2026

XIV and XV are ready for the authorized canonical fast-forward and normal push. Both books' closed decisions, exact certified corpus bytes and independent unavailable states are preserved. Final combined coverage is **5,231 selectable identities = 4,315 + 916**. The final promotion and directly verified remote commit are recorded in `{base['runtime']}\\PROMOTION_RECEIPT.json` after the verification-only commit.

Integration worktree: `{ROOT}`. Branch: `antiquities-niese-14-15-integration`. Runtime: `{base['runtime']}`. The original source worktree and runtime are unchanged. Preferred localhost port8915 is used when free; actual suite origins and fallback ports are recorded in their QA. Separate headless browser profiles are under this integration runtime.

The completed XII–XIII handoff was verified against its report, all111 manifest entries plus manifest, certificate evidence hashes, seven production blobs, promotion receipt, source ancestry and current IX/Whiston lineage. Actual initial canonical and directly verified remote were `{base['canonical_start']}`; no assumed predecessor was used. The canonical checkout was clean. No applicable AGENTS file was present.

At the first promotion gate, local canonical had advanced to `{effective}` while the remote remained81126ce. This documented correction removes only label-only tails from VI268/270, X107/149 and XIII212 and leaves all corpus/registry bytes and identities unchanged. Its complete28-file review packet and one-file renderer change were verified and merged automatically in `{tested}`. CANONICAL_ADVANCE.json adds an actual current snapshot without replacing the original baseline. The fresh baseline build and all final gates use this later code;17 targeted uninstrumented selections explicitly protect its correction. Final coverage remains4,315 before XIV/XV. The normal final push includes this preserved canonical ancestor.

Complete source history from `{base['frozen_source_base']}` through `{base['source_tip']}` was merged, including all32 commits and **538 incoming files:7 production and531 review**. Incoming packets contain247 XIV files,225 XV files and59 batch files. Original review/certificate bytes remain exact. Production paths are listed with before/source/final hashes in INCOMING_SCOPE.json, BASELINE.json and PRODUCTION_MANIFEST.json:

- assets/js/renderTei.js
- assets/xml/antiquities/Greek/book-14.xml and book-15.xml
- assets/xml/antiquities/Latin/book-14.xml and book-15.xml
- assets/xml/antiquities/niese/book-14.json and book-15.json

History: provenance-only checkpoint15ecf7dd96a4f7c5d3ad8805bc9e8c211362a442; complete source merge34435139bfabb4ef3d53187baa251f0165a92765 (parents15ecf7d and48a5b5c); production compatibility resolution cf082405078a849530b3c128c543e58304601e73; clean merge of the later canonical display fix `{tested}`; subsequent certification commit adds this review packet only. This integration adds **{new_review_count} review files** including FILE_MANIFEST.json, separate from531 incoming reviews. No English, structure.xml, other-book narrative, configuration, CSS or font file was edited.

One merge-conflicted path, renderTei.js, had two regions. The merged registry keeps VIII/IX/X/XII/XIII and adds XIV/XV; the canonical anonymous-paragraph comment and already-compatible guard are retained. The initial renderer exactly matched canonical plus two registrations.

Fresh wider-view testing then found a real XV Bamberg truncation: Niese106 had displaced the chapter5 milestone[1] endpoint in latin-book15-num106. Inspection of all112 registered milestone-edge locators distinguished104 chapter targets from8 legitimate earlier Niese targets. All9 XV witness locators target original chapter milestones. A minimal optional per-book structuralMilestoneUnits filter plus one XV registry metadata line preserves those original chapter ordinals. Other books retain their old locator behavior. All XV Bamberg/Alignment original-source views, other works and the complete new reader passed after a full rebuild. This is an implementation compatibility repair; no accepted boundary changed. Removing exactly the one LF metadata line recovers the certified XV registry. The four corpus files and XIV registry remain byte-identical to the certified source. Full history/reasons/hashes are in PRODUCTION_RESOLUTION.json and STRUCTURAL_LOCATOR_COMPATIBILITY.json.

| Book | Selectable | Nonempty Latin intervals | Retained starts | Added milestones | Latin unavailable |
|---|---:|---:|---:|---:|---|
| XIV |491|489|106|383|238,239|
| XV |425|423|0|423|338,347|
| Batch |916|912|106|806|4 identities|

Only Greek XIV.1 and XV.1 opening identities were added. XV's zero-retained-start representation, inherited visible labels and identity handling remain intact. XIV162A,358A,388B and XV40B are closed and unchanged. Exact physical intervals and reciprocal notices passed at XIV161–163,357–359,387–389 and XV39–41 and in their containing views. Difficult syntax, affirmative hyrcani fidem transgressus est, interrupted peri … culis and displaced death/praeter legem correspondence remain qualified. The four unavailable Latin selections retain independent Greek and Whiston context; they consume no neighboring Latin and make no expanded absence claim or inference about cause.

The final full candidate and archived current-canonical builds include all Gemfile plugins, using the pinned Ruby image and Bundler4.0.22. Build exit0;240 built static source hashes match. BUILD_RECORD.json binds production `{tested}`, tree `{build['candidate_tree']}`, code/data SHA-256 `{build['code_data_sha256']}`. The final review-only commit changes no built production data; its promotion gate checks that equivalence.

Fresh final-build QA passed every491 XIV and425 XV selection, exact Greek/Latin intervals, labelled preserved broader English context, all127 XIV and78 XV chapter/subchapter containing views, full narrative partition, actual range completeness, final extents, qualification/availability notices, unique IDs, deep links, Previous/Next, Back/Forward/reload, pane switching, book transition/reset, themes and assets. The six final captures of XIV358/XV40 in both themes and unavailable XIV238/XV338 were visually inspected. QA uses actual local built reader/data with state hooks for exhaustive assertions; uninstrumented critical URLs are independently recorded. No registry is injected.

Protected checks passed all4,315 starting-canonical Niese selections, {certificate['protected_traditional_rows']} traditional rows, {certificate['protected_Bamberg_rows']} Bamberg rows, {certificate['protected_Alignment_units']} Alignment units and source contents across Antiquities preface/I–XX. Explicit IX50–51,109–110, Greek181/216,239–241 and containing views pass. XII246–250 and XIII212–217/269 pass with13 containing views, current English, distributed/resumed correspondence, suppressed inherited213, unavailable213/216 and anonymous-paragraph handling. Thirteen accepted VIII/X focused controls include VIII187/255/367–369 and X101–102,108–109,150–151,276–277; exact prior source DOM comparisons also protect the inherited-label exceptions. Bellum Whiston/Lodge, note visibility/reload/source switching, Apion and DEH pass across21 configurations, {certificate['protected_cross_work_citations']} citations and {certificate['protected_cross_work_ranges']} ranges. Current Whiston source-contents/compiled-index functions, specified source headings and interaction roundtrips are preserved; fresh layout checks for III,V,XII,XIII,XIV,XV,XX cover364 original/display pairs and1,160 continuation checks at both widths/themes.

Exact byte recovery passed: delete806 added Latin milestones and reverse only the2 approved Greek openings to recover the identical pinned source inputs. No XML reserialization, whitespace normalization, text movement or emendation is used. The independently validated raw/text/tail locators and partition certificates remain applicable through identical input/output hashes. All531 incoming review bytes and original certificates are unchanged. All{integrity['canonical_protected_Git_blobs_unchanged']:,} unrelated effective-canonical Git blobs and actual canonical working bytes remain unchanged at certification.{len(integrity['integration_checkout_working_variants'])} integration checkout LF/CRLF differences are explicitly recorded as read-only representation differences, while unchanged Git blobs and actual canonical bytes are separately protected. XIV/XV English current-canonical and historical frozen hashes are recorded independently; they currently agree. No historical English bytes were restored.

Only the precisely bounded original Book-I Bamberg three apparatus hyperlinks/two broken targets and unsupported I.1 TypeError are inherited. Fresh exact-bound candidate/current-baseline checks pass; supported I.27 is error-free. No additional browser exception, failed request or duplicate ID is waived. Earlier preparation/harness failures and the corrected XV defect are retained and distinguished from final PASS evidence in diagnostics/ and PREPARATION_DIAGNOSTICS.md. All final QA references carry final production hashes/provenance; obsolete pre-fix or stale-provenance runs are not final certification.

Source branches VIII/X, IX, XII/XIII, XIV/XV and the later citation-display correction are preserved, with exact tips in CERTIFICATE.json. There are no pending editorial decisions. Promotion is authorized and follows a fresh clean-checkout/local/direct-remote gate; fast-forward only and normal push, no force/reset/rebase/configuration change. The runtime receipt records actual final canonical/integration/remote HEADs and post-promotion byte checks. No public-preview export, preview repository push, deployment or CNAME/domain change occurred. Stop after canonical handoff.
'''
(P/'REPORT.md').write_text(report,encoding='utf8',newline='\n')
packet_paths = sorted(x for x in P.rglob('*') if x.is_file() and x.name != 'FILE_MANIFEST.json')
assert len(packet_paths) + 1 == new_review_count
save('FILE_MANIFEST.json', dict(schema='integration-review-manifest-v1',tested_production_commit=tested,
    incoming_production_files=7,incoming_review_files=531,integration_additional_review_files=new_review_count,
    excludes_only='FILE_MANIFEST.json',files=[dict(path=str(x),relative=x.relative_to(P).as_posix(),sha256=SHA(x.read_bytes()),bytes=x.stat().st_size) for x in packet_paths]))
print(json.dumps(dict(result='PASS',new_selections=916,containing_views=205,combined_coverage=5231,
                     incoming_production=7,incoming_review=531,integration_review=new_review_count,
                     certificate=str(P/'CERTIFICATE.json')),indent=2))
