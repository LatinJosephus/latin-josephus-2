"""Seal only complete fresh combined-reader and independent source proofs."""
from integration_common import *

def main():
    names=['COMBINED_SOURCE_PROOF.json','XI_SOURCE_PROOF.json','BUILD_RECEIPT.json','BASELINE_CONTAINING_BROWSER.json','FINAL_BROWSER.json','PROTECTED_FINAL_BROWSER.json','READER_XI_RESULTS.json','READER_CONTAINING_RESULTS.json','READER_EXTRA_RESULTS.json','READER_STRUCTURE_CROSSWORK_RESULTS.json','COMBINED_EXTRA_RESULTS.json','XI_WITNESS_ORDER_RESULTS.json','LEGACY_DISTINCT_FINAL_BROWSER.json','SOURCE_CONTROLS_FINAL_BROWSER.json','TRANSITION_FINAL_BROWSER.json']
    results={name:read(D/name) for name in names}
    for name,r in results.items():
        assert r.get('status',r.get('result'))=='PASS',(name,r.get('failure'))
        assert not r.get('errors',[]),(name,r.get('errors'))
    source=results[names[0]];old=results['PROTECTED_FINAL_BROWSER.json'];new=results['FINAL_BROWSER.json'];xi=results['READER_XI_RESULTS.json'];extra=results['COMBINED_EXTRA_RESULTS.json'];base=results['BASELINE_CONTAINING_BROWSER.json'];cross=results['READER_STRUCTURE_CROSSWORK_RESULTS.json']
    assert len(old['selections'])==5231 and len(new['selections'])==745 and len(xi['selectors'])==347
    actual=set(extra['identity_set']);reviewed={f"{r['book']}.{r['number']}" for r in old['selections']+new['selections']}|{f"11.{r['n']}" for r in xi['selectors']}
    assert len(actual)==len(reviewed)==6323 and actual==reviewed
    assert len(new['views'])==len(base['views'])==267
    for row in new['views']:
        prior=next(r for r in base['views'] if r['id']==row['id'])
        assert row['hashes']==prior['hashes'] and row['existingDuplicateIDs']==prior['existingDuplicateIDs']
    for b in ['18','19']:assert new['books'][b]['legacyRanges']==base['books'][b]['legacyRanges']
    assert len(new['interactions'])==43 and len(xi['navigation'])==22 and len(xi['ranges'])==9 and len(xi['containing'])==120
    assert len(results['READER_CONTAINING_RESULTS.json']['rows'])==61
    assert len(results['READER_EXTRA_RESULTS.json']['rank_challenges'])==4 and len(results['READER_EXTRA_RESULTS.json']['uninstrumented'])==6
    assert len(extra['uninstrumented'])==19 and len(extra['physical_navigation'])==2
    assert len(results['XI_WITNESS_ORDER_RESULTS.json']['alignment'])==57
    assert len(results['LEGACY_DISTINCT_FINAL_BROWSER.json']['legacyRoutes'])==29 and len(results['LEGACY_DISTINCT_FINAL_BROWSER.json']['physicalPoints'])==6
    assert len(results['SOURCE_CONTROLS_FINAL_BROWSER.json']['events'])==3 and len(results['TRANSITION_FINAL_BROWSER.json']['transitions'])==3
    assert len(old['knownBaselineIssues'])==2 and len(old['protectedRoutes'])==13
    assert len(cross['books'])==21 and len(cross['cross_works'])==21
    # Confirm no production bytes changed after the actual tested Git archive.
    build=read(D/'BUILD_CONTEXT.json');built_tree=tree(build['source_commit'])
    for relative,f in built_tree.items():
        if not relative.startswith('review/'):assert_blob((ROOT/relative).read_bytes(),f['oid'])
    shutil.copyfile(ROOT/'review/Antiquities_Niese_Batch_18_19_2026-10-09/BASELINE_CONTAINING_BROWSER.json',D/'CERTIFIED_SOURCE_CONTAINING_AUTHORITY.json')
    certified=read(D/'CERTIFIED_SOURCE_CONTAINING_AUTHORITY.json')
    assert [(r['id'],r['hashes']) for r in certified['views']]==[(r['id'],r['hashes']) for r in base['views']]
    save('QA_REPAIRS.json',dict(production_regressions=0,unresolved_failures=0,harness_repairs=[dict(script='verify_build.py',initial_failure="KeyError: 'production_files'",cause='The integration scope schema calls its exact five-file list production.',repair='Use the recorded production field; rerun the entire build-input/output audit.',fresh_rerun='PASS, 640 Git-tree inputs and 488 static checks')],fresh_canonical_containing_replay='267 views match both final output and certified source authority',subsequent_QA_changes=['Separate baseline port 8919 from final port 8918','Add independent uninstrumented case and witness-order tests'],no_new_failure_reclassified_as_inherited=True))
    count=dict(selectable_identities=6323,prior_actual_selections=5231,XI_actual_selections=347,XVIII_XIX_actual_selections=745,XVIII_XIX_independent_Latin_intervals=743,XVIII_XIX_unavailable=2,XVIII_XIX_containing_routes=267,XVIII_XIX_direct_navigation_cases=43,XI_containing_routes=120,XI_independent_traditional_ranges=61,XI_assembled_ranges=9,XI_navigation_cases=22,XI_reversed_rank_challenges=4,XI_uninstrumented_selections=6,approved_case_uninstrumented_selections=19,XI_physical_Alignment_units=57,XI_physical_occurrences=354,legacy_chapter_routes=29,distinct_physical_language_points=6,actual_distinct_navigation_groups=2,book_transitions=3,protected_direct_routes=len(old['protectedRoutes']),protected_source_events=3,Antiquities_book_contexts=21,Antiquities_traditional_ranges=sum(r['traditional'] for r in cross['books']),Antiquities_Bamberg_ranges=sum(r['bamberg'] for r in cross['books']),Antiquities_Alignment_units=sum(r['alignment'] for r in cross['books']),cross_work_source_configurations=21,cross_work_citations=sum(r['niese'] for r in cross['cross_works']),cross_work_ranges=sum(r['ranges'] for r in cross['cross_works']),protected_focused_routes=len(cross['focused']),new_reader_failures=0,independently_reproduced_inherited_exceptions=2)
    production=read(D/'INCOMING_SCOPE.json')['production']
    production_manifest=[info(ROOT/p)|dict(relative=p) for p in production]
    save('CERTIFICATION.json',dict(status='PASS_READY_FOR_SAFE_CANONICAL_PROMOTION',canonical_start=START,direct_remote_start=START,certified_source=SOURCE,source_baseline=BASE,tested_merge=build['source_commit'],source_commits=source['source_commits'],all_sixteen_source_commits_preserved=True,counts=count,book_counts=[{k:v for k,v in b.items() if k in ['book','identities','independent_Latin_intervals','reused_physical_starts','added_Latin_milestones','retained_numeric_starts','unavailable','inverse_original_sha256','candidate_sha256']} for b in source['books']],decisions=[dict(case='XVIII.7',option='A',status='CLOSED_APPROVED',start='et supra quam dici potest'),dict(case='XVIII.94',option='B',status='CLOSED_APPROVED',start='Transacta uero festiuitate'),dict(case='XVIII.216–217',option='A',status='CLOSED_APPROVED',representation='No independent Latin interval in the present transcription; selectable Greek/English and cause-neutral specific notices'),dict(case='XIX.188',option='A',status='CLOSED_APPROVED',start='Erant enim cohortes')],source_integrity=dict(unchanged_canonical_files=3285,authorized_modified_existing_files=3,added_registry_files=2,exact_incoming_review_files=445,verbatim_HOLD_archive_files=104,XVIII_XIX_inverse_original_bytes=True,Greek_English_preserved=True,XI_original_production_data_CSS_preserved=True),production_files=production_manifest,test_results=[dict(file=name,sha256=sha((D/name).read_bytes()),status='PASS') for name in names],formal_merge_conflicts=0,manual_production_resolutions=0,new_scholarly_decisions=0,public_preview_updated=False,other_workbots_written=False))
    report=f'''# Antiquities XVIII–XIX — combined canonical integration certification

The isolated integration branch is fully certified and ready for safe promotion to canonical `v2-development` and a normal push. Every actual selectable identity is covered, with no new reader regression or unresolved scholarly decision. Public-preview publication is excluded. The final promoted commit and direct remote verification are recorded after promotion in `{R / 'PROMOTION_RECEIPT.json'}`.

Canonical and directly verified remote start: `{START}`. Certified source: `{SOURCE}`, based on `{BASE}`. Integration baseline record: `23f535de91ad4875bb947790bcdd4ab1308fa5cc`; reviewed normal merge and actual tested production tree: `{build['source_commit']}`. Both merge parents and all sixteen incoming commits remain ancestors. Their complete ordered hashes are in `BASELINE.json`, `INCOMING_SCOPE.json` and `CERTIFICATION.json`. The source branch was not rebased, reset or rewritten.

The merge had no formal conflicts. The shared renderer was examined against both parents: XI fragment assembly, continuation/attachment ranks, paragraph-end handling, context targets and disclosure remain; XVIII/XIX declared physical starts, inherited-label suppression, range endpoints and synthetic citation labels remain. The catalogue includes XI, XVIII and XIX. No entire-side renderer replacement or manual production resolution occurred. `MERGE_RECONCILIATION.json` records the review.

| Invariant | XVIII | XIX |
|---|---:|---:|
| Niese identities | 379 | 366 |
| Independent Latin intervals | 377 | 366 |
| Reused physical starts | 61 | 46 |
| Added Latin milestones | 316 | 320 |
| No independent Latin interval | 2 | 0 |
| Retained numeric Latin starts | 0 | 0 |

No new numeric Latin starts, Greek markers, end markers or other structural anchors were added. There are 636 added Latin milestones and 107 reused physical starts in total.

All four approved decisions remain closed: XVIII.7 A at `et supra quam dici potest`; XVIII.94 B at `Transacta uero festiuitate`; XVIII.216–217 A with no independent Latin interval in the present transcription; XIX.188 A at `Erant enim cohortes`. The exact alternatives, source evidence, coordinates, earlier HOLD state, reciprocal qualifications and indirect correspondence references survive byte-identically. For 216–217 the Greek and English contexts are independently selectable, with specific cause-neutral Latin notices, no substituted neighbouring text, conjectural text, original-translation-absence inference or physical-gap claim. The certified distinct traditional/Bamberg starts at XVIII.257 and XIX.292 remain physically separate in all three languages.

The actual combined identity catalogue contains **6,323** distinct identities: 5,231 earlier supported, 347 XI and 745 XVIII–XIX. `COMBINED_EXTRA_RESULTS.json` records all 21 actual book menus and canonical entries; their exact set equals the union of the three fresh exhaustive reader result sets. XVI, XVII and XX retain their prior availability. The number was not certified merely by addition.

| Fresh verification | Passed |
|---|---:|
| Every earlier supported selection, baseline versus merged live DOM | 5,231 |
| XI complete selections, full three-pane content/endpoints/occurrences | 347 |
| XVIII–XIX complete selections, full three-pane content/endpoints/qualifications | 745 |
| XVIII–XIX containing routes, fresh canonical baseline and merged build | 267 |
| XI containing routes | 120 |
| XI independent traditional ranges | 61 |
| XI assembled ranges, including entire 1–347 | 9 |
| Direct reload/previous/next/history cases, XVIII–XIX / XI | 43 / 22 |
| XI reversed-rank challenges / uninstrumented selections | 4 / 6 |
| Uninstrumented approved cases and immediate neighbours | 19 |
| XI original physical witness Alignment units / Latin occurrences | 57 / 354 |
| Legacy chapter direct routes / distinct physical language points | 29 / 6 |
| Actual independent Traditional/Bamberg navigation groups | 2 |
| Book transitions XVII–XVIII, XVIII–XIX, XIX–XX | 3 |
| Protected direct routes / source-selector events | 13 / 3 |
| Antiquities book contexts | 21 |
| Antiquities traditional / Bamberg / Alignment ranges | {count['Antiquities_traditional_ranges']} / {count['Antiquities_Bamberg_ranges']} / {count['Antiquities_Alignment_units']} |
| Cross-work/source configurations / citations / ranges | 21 / {count['cross_work_citations']} / {count['cross_work_ranges']} |
| Focused protected routes | {count['protected_focused_routes']} |

XI.312 retains both Bellum IV.105 insertions immediately before their corresponding portions; 311 and 342 exclude them. XI.326/342 canonical continuation order and duplicate suppression pass. An independent original-stream check confirms Book and all 57 Alignment units retain physical witness order, while logical assembly follows canonical Niese order. Traditional populations retain their independently certified span assembly. Whiston, Alignment, traditional/Bamberg controls, Bellum/Cardwell/Lodge, DEH, Contra Apionem, TOC, source switching, Lodge notes/reload, panes, both themes, history and accessibility pass. Settled light/dark screenshots were visually inspected.

Only the independently reproduced Book-I apparatus exception (three links and two distinct 404 targets) and unsupported I.1 exact TypeError/first-supported-27 signature remain. No new failure was labelled inherited. There are zero unresolved failures. One build-verification harness field-name error was corrected and the complete audit rerun; no product change was involved. `QA_REPAIRS.json` records this separately.

Fresh full Jekyll builds used separate Git archives of canonical start and merge `{build['source_commit']}` in `{R}`. The 640 non-review Git-tree input checks and 488 static source/output checks pass. There was no post-build asset replacement or registry injection. Browser profiles and servers were separate from all original WorkBot runtimes; all test servers and contexts closed.

Independent Latin reversal recovers the exact original XVIII bytes (SHA-256 `349ccf8751a0279c0a1f9836dd482a39698f7e3970d7018627c0d227c27dc8e3`) and XIX bytes (`ab1c28f03e1a5893057262edfc117b63a1d46ce0b20bb803fb4e1903db439e80`). Marker Unicode byte coordinates and complete Latin interval partitions pass independently. Greek/English bytes match the proper source-baseline blobs. Existing IDs, sameAs, numerical citations, punctuation, whitespace, paragraph order and traditional/Bamberg structures pass. All 462 structural language locators and 104 verbatim HOLD archive files survive. XI separately passes exact original Latin inverse recovery, Greek/English preservation and all 354/347 Latin/Greek physical occurrence locators.

Exactly **five production paths** differ from the canonical integration-start tree: `assets/js/renderTei.js`, `assets/xml/antiquities/Latin/book-18.xml`, `assets/xml/antiquities/Latin/book-19.xml`, `assets/xml/antiquities/niese/book-18.json`, and `assets/xml/antiquities/niese/book-19.json`. The first three modify existing files; the last two are new registries. All 3,285 other canonical-start files are byte-identical, including XI Latin/identity data, its CSS, all Greek/English, structure data and unrelated production files. All four incoming data files and 445 incoming review files match the certified source exactly. The only necessary shared-code change is the reviewed renderer merge. The integration adds its own review directory; `FILE_MANIFEST.json` enumerates every changed path, byte count and SHA-256. A mistakenly tracked integration Python cache was removed in the merge and is excluded from further evidence.

Promotion requires a fresh clean-state and direct remote-tip check. Any concurrent canonical advance must be integrated and affected checks repeated before promotion. Normal fast-forward canonical promotion and push are authorized; force push and public-preview publication are excluded. The runtime promotion receipt records final canonical/remote commits, full source ancestry, changed production hashes, clean states and the exact promotion result. Other WorkBots and original runtimes were not written to.
'''
    (D/'REPORT.md').write_text(report,encoding='utf8',newline='\n')
    changed_paths=set(git('diff','--name-only',START,'HEAD').decode().splitlines())
    changed_paths.update(str(p.relative_to(ROOT)).replace('\\','/') for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    changed_paths.discard(str((D/'FILE_MANIFEST.json').relative_to(ROOT)).replace('\\','/'))
    files=[dict(relative=p,bytes=(ROOT/p).stat().st_size,sha256=sha((ROOT/p).read_bytes())) for p in sorted(changed_paths)]
    assert all(p['relative'] in production or p['relative'].startswith(('review/Antiquities_Niese_BookXVIII_2026-10-09/','review/Antiquities_Niese_BookXIX_2026-10-09/','review/Antiquities_Niese_Batch_18_19_2026-10-09/','review/Antiquities_Niese_Integration_18_19_2026-10-10/')) for p in files)
    save('FILE_MANIFEST.json',dict(canonical_start=START,tested_production=build['source_commit'],production=production_manifest,files=files,self_excluded=True,changed_paths_including_manifest=len(files)+1,incoming_review_files=445,integration_review_files=sum(p['relative'].startswith(str(D.relative_to(ROOT)).replace('\\','/')+'/') for p in files)+1))
    print(json.dumps(dict(status='PASS',counts=count,changed_paths_including_manifest=len(files)+1,integration_review_files=sum(p['relative'].startswith(str(D.relative_to(ROOT)).replace('\\','/')+'/') for p in files)+1)))
if __name__=='__main__':main()
