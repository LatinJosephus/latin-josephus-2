from integration_common import *
def main():
    names=['SOURCE_INTEGRITY.json','CONFLICT_RESOLUTIONS.json','BASELINE_BUILD.json','CANDIDATE_BUILD.json','BASELINE_PROTECTED_BROWSER.json','FINAL_PROTECTED_BROWSER.json','BOOKXX_BROWSER.json','ADJUDICATED_CASES_BROWSER.json','BASELINE_OTHER_CONTROLS.json','FINAL_OTHER_CONTROLS.json','VISIBLE_QUALIFICATIONS_BROWSER.json','BOOK_CLOSURE_BROWSER.json','GENERIC_END_BASELINE_REPRO.json','GENERIC_END_CANDIDATE_PROOF.json','READER_XI_RESULTS.json','XI_WITNESS_ORDER_RESULTS.json','NEW_BOOK_BROWSER_QA.json','READER_FINAL_PRIOR_RESULTS.json','FINAL_BROWSER.json','BASELINE_CONTAINING_BROWSER.json','LEGACY_DISTINCT_FINAL_BROWSER.json','COMBINED_EXTRA_RESULTS.json','SOURCE_CONTROLS_FINAL_BROWSER.json','SUITE_xx-final.json','SUITE_18-19.json','SUITE_xi-witness.json']
    names.extend(['XX_STRUCTURAL_CONTROLS.json','VISUAL_REVIEW.json'])
    gates={n:read(PACK/n) for n in names}
    for n,g in gates.items():
        if n.endswith('BUILD.json'):assert g['exit_code']==0,n
        else:assert (g.get('status') or g.get('result')).startswith('PASS'),(n,g.get('failure'))
    old=gates['FINAL_PROTECTED_BROWSER.json'];new=gates['BOOKXX_BROWSER.json'];census=gates['COMBINED_EXTRA_RESULTS.json']
    assert len(old['selections'])==7082 and len(old['views'])==135
    assert len(new['selections'])==268
    assert len([r for r in new['selections'] if r['Latin']=='EXACT_FULL_INTERVAL_PASS'])==257
    assert len([r for r in new['selections'] if r['Latin']=='APPROVED_UNAVAILABLE_PASS'])==11
    pop=[f"{r['book']}.{r['number']}" for r in old['selections']]+[f"20.{r['number']}" for r in new['selections']]
    assert len(pop)==len(set(pop))==7350 and set(pop)==set(census['identity_set'])
    assert all(not r['duplicates'] for r in old['selections'])
    xi=gates['READER_XI_RESULTS.json'];assert len(xi['selectors'])==347 and len(xi['ranges'])==9 and len(xi['containing'])==120 and len(xi['navigation'])==22
    xv=gates['NEW_BOOK_BROWSER_QA.json'];assert xv['books']['16']['identity_count']==404 and xv['books']['17']['identity_count']==355
    assert xv['books']['16']['Latin_unavailable']==24 and xv['books']['17']['Latin_unavailable']==0
    xix=gates['FINAL_BROWSER.json'];assert len(xix['selections'])==745 and len(xix['views'])==267
    cross=gates['READER_FINAL_PRIOR_RESULTS.json'];assert len(cross['books'])==21 and len(cross['cross_works'])==21
    cross_counts=dict(Antiquities_containing=sum(2+x['traditional']+x['bamberg']+x['alignment'] for x in cross['books']),cross_work_citations=sum(x['niese'] for x in cross['cross_works']),cross_work_ranges=sum(x['ranges'] for x in cross['cross_works']))
    assert cross_counts==dict(Antiquities_containing=3370,cross_work_citations=8002,cross_work_ranges=1630)
    assert len(gates['ADJUDICATED_CASES_BROWSER.json']['groups'])==4
    assert len(gates['XX_STRUCTURAL_CONTROLS.json']['controls'])==133 and len(gates['XX_STRUCTURAL_CONTROLS.json']['plain'])==14
    assert len(gates['LEGACY_DISTINCT_FINAL_BROWSER.json']['legacyRoutes'])==29 and len(gates['LEGACY_DISTINCT_FINAL_BROWSER.json']['physicalPoints'])==6
    build=gates['CANDIDATE_BUILD.json'];prod=gates['SOURCE_INTEGRITY.json']['production_files']
    for rel,p in prod.items():
        assert sha((ROOT/rel).read_bytes())==p['sha256']==sha((Path(build['site'])/rel).read_bytes())
        assert sha(git('show','HEAD:'+rel))==p['sha256']
    save(PACK/'CORPUS_POPULATION.json',dict(status='PASS',identity_count=7350,exact_actual_identity_set=pop,live_menu_registry_identity_set=census['identity_set'],structural_counts=cross_counts,XX_structural_events=133,XX_uninstrumented_controls=14))
    changes=git('diff','--name-status',START,'HEAD').decode().splitlines()
    reserved={ (PACK/n).relative_to(ROOT).as_posix() for n in ['CHANGE_MANIFEST.json','CERTIFICATE.json','REPORT.md'] }
    full=[{'change':line.split('\t')[0],'path':line.split('\t')[-1],'sha256':sha((ROOT/line.split('\t')[-1]).read_bytes())} for line in changes if line.split('\t')[-1] not in reserved]
    # Include all pending integration evidence; every entry is explicitly manifested.
    for p in sorted(PACK.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            rel=p.relative_to(ROOT).as_posix()
            if rel not in reserved and rel not in {r['path'] for r in full}:full.append(dict(change='A',path=rel,sha256=sha(p.read_bytes())))
    full.extend(dict(change='A',path=rel,sha256=None,hash_attested_in_external_promotion_receipt=True) for rel in sorted(reserved))
    save(PACK/'CHANGE_MANIFEST.json',dict(start=START,tested_production_commit=build['source_commit'],production=prod,source_review_prefix='review/Antiquities_Niese_BookXX_2026-10-10/',integration_review_prefix=PACK.relative_to(ROOT).as_posix(),files=full,manifest_excludes_self_and_final_certificate_and_report=True))
    save(PACK/'CERTIFICATE.json',dict(status='PASS',starting_canonical=START,starting_direct_remote=START,certified_source_tip=SOURCE_TIP,tested_production_commit=build['source_commit'],combined_identities=7350,prior_identities=7082,original_baseline=5231,XI=347,XVI_XVII=759,XVIII_XIX=745,BookXX=268,represented_XX_Latin=257,unavailable_XX_Latin=list(range(27,37))+[238],XX_containing_views=135,XX_legacy_URLs=20,source_byte_recovery='SOURCE_INTEGRITY.json',closed_A_decisions_preserved=True,no_new_regressions=True,known_baseline_defects=gates['FINAL_OTHER_CONTROLS.json']['knownExceptions'],complete_history_preserved=True,gates={n:info(PACK/n) for n in names},fresh_complete_corpus_tests=True,publication=False,promotion='Requires last-minute fetch, ancestry, clean-state and direct remote verification; see external promotion receipt.'))
    report=f'''# Antiquities XX: final corpus integration certification

The actual merged reader passed fresh exhaustive certification of all **7,350 selectable Antiquities identities**. The starting canonical and directly verified remote were `{START}`. The history-preserving source merge is `{build['source_commit']}`; the complete certified Book XX source tip `{SOURCE_TIP}` is an ancestor.

## Merge and production scope

The only conflict was adjacent identity-loader registrations in `assets/js/renderTei.js`. The resolution retains XVI–XIX and appends XX. An independently reconstructed renderer is byte-identical to canonical plus the two authorized source additions: XX registration and generic per-language exclusive end. XI's fragment engine and all XVI–XIX behavior survive unchanged. See `CONFLICT_RESOLUTIONS.json` and `renderer-comparison/resolved.patch`.

The production scope is exactly four files: `assets/js/renderTei.js`, `assets/xml/antiquities/Greek/book-20.xml`, `assets/xml/antiquities/Latin/book-20.xml`, and `assets/xml/antiquities/niese/book-20.json`. All previously tracked files outside those three existing production files retain their baseline Git objects. All 273 incoming source-evidence files retain their certified objects. English, structural registries, CSS, display controls and other works are unchanged. `CHANGE_MANIFEST.json` lists production and review scope; the certificate and this report complete the review packet.

## Exhaustive content and availability

Fresh baseline/merged actual-reader comparisons replayed **7,082 prior selectors**, checking complete Latin, Greek and English narrative, full pane DOM hashes, source paragraph IDs and sameAs, qualification/unavailable notices, and duplicate IDs. This includes 5,231 original identities, 347 XI, 759 XVI–XVII and 745 XVIII–XIX. The new **268 XX selectors** were checked independently against the frozen full-interval Greek, Latin and Whiston-context oracles, rather than counts alone. The independently discovered live menu/registry set is exactly the same 7,350 distinct identities.

XX has **257 represented Latin intervals**, 257 new starts, one exclusive anchor, one Greek opening label and 267 inherited labels. **XX.27–36 and XX.238** have independent Greek and English context plus the precise unavailable-Latin notices. This asserts only absence of independently identifiable intervals in the present transcription. All four approved A decisions and all rejected alternatives remain intact; four groups with neighbours and physical/canonical ranges passed. The inherited bracketed annotation remains source-only at `latin-book20-num34`, visible in containing views.

## Structure, ranges and navigation

All **135 XX containing views**, all **20 legacy URLs** and complete physical extents passed. Traditional 12 chapters/50 lower divisions, Bamberg 20 divisions/legacy locations and 51 Alignment units remain independent. Opening narrative excludes the inherited duration notice; all final narrative and punctuation through XX.268 survive, XX.266 remains qualified, the full Latin trailer through AMEN is separate visible paratext, and Vita/XX.269 are excluded.

Fresh independent XI checks passed all **347 exact selectors**, **9 combined ranges**, **120 containing views**, **22 navigation cases**, both Bellum IV.105 interpolations, XI.312/326/342, and all **57 physical Alignment units**. Fresh XVI–XVII checks passed all **759 independently expected selectors**, next/previous at every selection, **50 direct/reload/history/plain-reader routes**, the four approved B decisions/displaced fragments and all 24 XVI unavailable-Latin notices. Fresh XVIII–XIX checks passed **745 independently expected selectors**, **267 containing views**, terminal cases, all unavailable/qualified intervals, 29 legacy URLs and six distinct physical points at XVIII.257/XIX.292. Uninstrumented approved cases and physical control switching also passed.

The structural/cross-work suite compared **3,370 Antiquities containing views**, **8,002 cross-work citation views** and **1,630 cross-work ranges**, across the Antiquities preface/all 20 books and complete Bellum/Contra Apionem/DEH structural populations using both Whiston and Lodge where applicable. Whiston/Cardwell/Lodge controls, Lodge notes, direct links, browser history, book transitions, themes, pane visibility, accessible notices and duplicate prevention passed. XX supplies 24 focused navigation cases, **133 actual structural selector events**, **14 plain-reader editorial cases**, direct annotation visibility in Book and Alignment, and the XIX-to-XX transition. Only the two independently reproduced inherited Book-I defects remain: unsupported I.1 outside the selectable population, and three inherited apparatus links with the unchanged 404 signature. No new regression passed.

One copied QA adapter initially imported the normalized-text helper into a test that measures original character offsets. Restoring its original raw-text helper corrected the test; all 29 legacy routes and six certified physical points were freshly rerun. The failed harness attempt and reason remain in `QA_HARNESS_REPAIR.json` and `HARNESS_OFFSET_INITIAL_ATTEMPT.json`. No production change was required; the successful exhaustive source/selection results remained valid.

## Byte preservation and evidence

Reversing only the authorized XX additions restores exact original bytes: Greek `042b24f1d6c50ef029cd8c6c49c24d76348778cd7ebd74cd8fc23906b6f81d19`; Latin `683ee52477cc21c6c9b68ef939696c4fb54b900e80f3774a3481f4e73837e282`. Unchanged English is `7d0813df000bab366ee8d785cdd154fd509db7428b7774739185cd83194cec34`. Original wording, punctuation, Unicode, whitespace, IDs, sameAs, annotations, apparatus, physical order and manuscript/chapter markup are thereby recovered in full. Previously integrated production files are compared with the actual starting canonical Git objects. Windows checkout differences are recorded separately in `WINDOWS_CHECKOUT_DIFFERENCES.json`; unrelated files were not normalized.

Builds are fresh archived Git sources in the isolated integration runtime. Browser hooks only observe the real reader; plain uninstrumented checks corroborate approved cases. All gate hashes appear in `CERTIFICATE.json`. Other source branches/worktrees/review packets/runtimes were untouched. No public-preview publication or refresh was performed. Canonical promotion and direct remote verification are recorded in the separate promotion receipt linked in the final handoff.
'''
    (PACK/'REPORT.md').write_text(report,encoding='utf-8',newline='\n')
    print('PASS complete 7350 corpus certificate and review handoff generated')
if __name__=='__main__':main()
