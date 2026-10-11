import postrelease_reader as a
import postrelease_stage as s
import shutil,sys,subprocess,csv,gzip,json

PRODUCTION=['_includes/annotations-bar.html','_includes/header.html','_sass/_antiquities.scss','_sass/_branding.scss','_sass/_reader-ui.scss','assets/js/dark_mode.js','assets/js/renderTei.js','assets/js/theme.js']
RESULTS=['THEME_FINAL.json','PACKAGE_final_final.json','PACKAGE_E_final.json','candidate-VII1-7.json','candidate-VII1-REGRESSION.json','COMBINED_CONTEXT.json','CONTEXT_GUARDS.json','TARGETED_UI.json','VII2_6_NAVIGATION_PRESENTATION.json','KEYBOARD_FULL_SOURCE.json','PROTECTED_CONTROLS.json','GENERAL_NAVIGATION.json','CONTAINING_REAL_UI.json','CONTAINING_IDS_REAL_UI.json','COMPACT_EVIDENCE.json']
def manifest():
    frozen={x['path']:x for x in a.load(a.T/'START.json')['source_manifest']};prod=[]
    for path in PRODUCTION:
        b=(a.W/path).read_bytes();prod.append({'path':path,'baseline_SHA256':frozen[path]['SHA256'],'final_SHA256':a.sha(b),'bytes':len(b),'Git_blob':a.gt('hash-object',path,repo=a.W)})
    changed=sorted(a.gt('diff','--name-only',a.F,'HEAD','--',':(exclude)review/',repo=a.W).splitlines());assert changed==PRODUCTION
    build=a.load(a.T/'BUILD_candidate-final.json');built={r['path']:r for r in build['assets']}
    for path in ['assets/js/renderTei.js','assets/js/theme.js','assets/js/dark_mode.js']:
        assert built[path]['SHA256']==a.sha((a.W/path).read_bytes())==a.sha((a.T/'candidate-final-site'/path).read_bytes())
    evidence=[{'path':p.relative_to(a.W).as_posix(),'bytes':p.stat().st_size,'SHA256':a.sha(p.read_bytes())} for p in sorted(a.Q.rglob('*')) if p.is_file() and p.name!='CHANGED_FILES.json']
    a.save(a.Q/'CHANGED_FILES.json',{'baseline':a.F,'tested_implementation_commit':a.gt('rev-parse','HEAD',repo=a.W),'production':prod,'built_assets':build['assets'],'evidence':evidence,'self_excluded_to_avoid_recursive_hash':'CHANGED_FILES.json','full_frozen_source_manifest':'BASELINE.json','no_XML_registry_release_marker_domain_config_change':True})

def finish():
    assert not a.state(a.W)['status'],'Production branch must be clean before recording aggregate evidence'
    tip=a.gt('rev-parse','HEAD',repo=a.W);start=a.load(a.T/'START.json');x=a.load(a.T/'baseline-NIESE.json');y=a.load(a.T/'candidate-final-NIESE.json')
    assert x['result']==y['result']=='COMPLETE' and len(x['rows'])==len(y['rows'])==7376 and not x['errors'] and not y['errors'] and x['books']==y['books']
    assert all(b['languages']==d['languages'] and not d['duplicates'] for b,d in zip(x['rows'],y['rows']))
    st=a.load(a.T/'qa/READER_FINAL_PRIOR_RESULTS.json');assert st['result']=='PASS' and not st['errors'] and st['totals']=={'traditional':1689,'bamberg':198,'alignment':1441}
    assert sum(r['niese'] for r in st['cross_works'])==8002 and sum(r['ranges'] for r in st['cross_works'])==1630
    for n in RESULTS:
        d=a.load(a.T/n);assert d.get('result',d.get('status'))=='PASS',(n,d.get('failure'));shutil.copy2(a.T/n,a.Q/n)
    raw=a.load(a.T/'FIVE_DEFECTS_candidate-final.json');assert len(raw['rows'])==11 and all(not row['errors'] and not row['network'] for row in raw['rows']);assert len(raw['linkRequests'])==2 and all(r['status']==404 for r in raw['linkRequests'])
    for route in ['/antiquities/?book=11','/antiquities/?book=20']:
        assert not next(r for r in raw['rows'] if r['route']==route)['state']['duplicates']
    assert len([r for r in next(r for r in raw['rows'] if r['route'].endswith('bamberg=5'))['state']['links'] if r['href'].startswith('undefinednote')])==3
    # The after-capture records observations, not an inherited-error waiver.
    raw['result']='AFTER_CAPTURE_VERIFIED';a.save(a.Q/'FIVE_DEFECTS_after.json',raw)
    for n in ['BUILD_candidate-final.json','NIESE_EXACT_COMPARISON.json','SOURCE_MANIFEST_VERIFICATION.json','PROTECTED_SOURCE_INPUTS.json','READER_FINAL_PRIOR_RESULTS.json','MID_QA_CHECKPOINT.json','FINAL_JOB_niese.json','FINAL_JOB_structural.json','FINAL_JOB_focused.json']:
        shutil.copy2(a.T/n,a.Q/n)
    with (a.Q/'NIESE_MATRIX.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.writer(f);w.writerow(['actual_local_URL','work','book','Niese','view','source_commit','Latin_DOM_SHA256','Greek_DOM_SHA256','English_DOM_SHA256','Latin_text_SHA256','Greek_text_SHA256','English_text_SHA256','all_panes_equal_fresh_baseline','original_IDs_and_qualification_equal','duplicate_IDs','result'])
        for row in y['rows']:w.writerow([row['URL'],'Antiquities',row['book'],row['n'],'Niese',a.F,*[row['languages'][l]['DOM'] for l in ['Latin','Greek','English']],*[row['languages'][l]['text'] for l in ['Latin','Greek','English']],True,True,0,'PASS'])
    for mode in ['baseline','candidate-final']:
        with gzip.GzipFile(filename=str(a.Q/(mode+'-NIESE.json.gz')),mode='wb',mtime=0) as f:f.write((a.T/(mode+'-NIESE.json')).read_bytes())
    # Keep compact native screenshots in Git; full-book raw captures remain indexed in runtime.
    imageNames=['COMPACT-'+mode+'-'+label+'.png' for mode in ['baseline','candidate-final'] for label in ['Book-XI','Book-XX','Home','Unsupported-I1']]
    imageNames+=['THEME-final-1-1440-light.png','THEME-final-2-1440-dark.png','THEME-final-3-390-light.png','THEME-final-4-390-dark.png']
    (a.Q/'screenshots').mkdir(exist_ok=True)
    for n in imageNames:shutil.copy2(a.T/'screenshots'/n,a.Q/'screenshots'/n)
    for f in a.Path('.').glob('postrelease_*'):
        if f.suffix in ['.py','.cjs']:shutil.copy2(f,a.Q/f.name)
    (a.Q/'qa').mkdir(exist_ok=True)
    for f in (a.T/'qa').iterdir():
        if f.is_file() and f.suffix in ['.cjs','.rb','.yml','.json']:shutil.copy2(f,a.Q/'qa'/f.name)
    (a.Q/'logs').mkdir(exist_ok=True)
    for f in (a.T/'logs').iterdir():
        if f.is_file() and f.suffix=='.log':shutil.copy2(f,a.Q/'logs'/f.name)
    (a.Q/'failed-attempts').mkdir(exist_ok=True)
    for folder in (a.T/'attempts').iterdir():
        if folder.is_dir():
            for f in folder.iterdir():
                if f.is_file() and f.suffix in ['.json','.cjs']:shutil.copy2(f,a.Q/'failed-attempts'/(folder.name+'-'+f.name))
    protected=[]
    for row in a.load(a.T/'PROTECTED_SOURCE_INPUTS.json')['files']:
        before=row['SHA256'];current=a.sha((a.W/row['path']).read_bytes());built=a.sha((a.T/'candidate-final-site'/row['path']).read_bytes());assert current==built==before
        protected.append({**row,'final_SHA256':current,'built_SHA256':built,'result':'PASS'})
    preservation=a.load(a.T/'SOURCE_MANIFEST_VERIFICATION.json');assert sorted(preservation['changed_files'])==PRODUCTION
    a.save(a.Q/'SOURCE_PRESERVATION.json',{'result':'PASS','XML_count':143,'protected_input_count':159,'frozen_tracked_files':5166,'unchanged_original_tracked_files':5158,'protected_files':protected,'full_manifest_verified':preservation})
    packages={'A':{'status':'PASS','fix':'Native named theme button, keyboard focus and accurate pressed state'},'B':{'status':'PASS','fix':'UI annotation panel namespaced; every scholarly/source ID preserved'},'C':{'status':'EDITORIAL HOLD / NOT REPAIRED / NOT PASSED','fix':None,'decision':'Explicit human hold; original targets retained. Does not block A/B/D/E completion.'},'D':{'status':'PASS','fix':'Shared reader requires a work contract and real reader controls'},'E':{'status':'PASS','fix':'Validate explicit Antiquities Niese requests against actual supported identities; accurate notice and valid links; no false passage'}}
    counts={'Antiquities_actual_Niese':7376,'Proem':26,'Antiquities_I_XX':7350,'traditional':1689,'Bamberg':198,'Alignment':1441,'cross_work_Niese':8002,'cross_work_structural':1630}
    suites=[{'file':n,'status':'PASS','SHA256':a.sha((a.T/n).read_bytes()),'checks':len(a.load(a.T/n).get('checks',a.load(a.T/n).get('rows',a.load(a.T/n).get('ranges',[]))))} for n in RESULTS]
    a.save(a.Q/'TEST_RESULTS.json',{'UTC':a.now(),'result':'PASS FOR A/B/D/E; C EXPLICITLY UNRESOLVED','tested_commit':tip,'production_renderer_SHA256':a.sha((a.W/'assets/js/renderTei.js').read_bytes()),'counts':counts,'exact_comparison':a.load(a.T/'NIESE_EXACT_COMPARISON.json'),'structural_crosswork':st,'suites':suites,'C_remaining_404s':raw['linkRequests'],'baseline_limitations':[{'case':'Bellum Book I header ID','cause':'Latin and English TEI headers use the same original header ID','before_after':'Independently equal before/after; source-source collision outside the five requested defects','evidence':'PACKAGE_final_final.json, FIVE_DEFECTS_after.json and FIVE_DEFECTS_baseline.json'}],'harness_corrections':[{'failure':'Broad duplicate-ID check found inherited Bellum header','disposition':'Explicit independently measured baseline limitation; no source/header renaming'},{'failure':'D test started before build completed, assumed nonexistent main element, then clicked before navbar transition ended','disposition':'Attempts preserved; completed build, actual body template and completed collapse transitions verified; no production change added'},{'failure':'VII.1 positive test runner passed candidate as a directory path','disposition':'Original failed result and log preserved; corrected absolute tested-build path, fresh profile, positive source assertion PASS. Original job-level FAIL remains archived; effective suite gates use the corrected result.'}],'no_new_supported_route_console_network_ID_or_text_regression':True,'no_public_Niese_range_control_added':True})
    commits=a.gt('log','--reverse','--format=%H %s',a.F+'..HEAD',repo=a.W).splitlines()
    a.save(a.Q/'CERTIFICATE.json',{'UTC':a.now(),'overall':'PARTIAL CERTIFICATION — A/B/D/E PASS; C EDITORIAL HOLD','all_five_repaired':'NO-GO','independent_completed_packages':'PASS','packages':packages,'counts':counts,'zero_new_regressions':True,'source_preservation':'143 XML and all 159 protected inputs exact; 5,158 of 5,166 original tracked files unchanged','baseline':a.F,'public_preview_unchanged':a.V,'implementation_tip':tip,'commits':commits,'tested_renderer_SHA256':a.sha((a.W/'assets/js/renderTei.js').read_bytes()),'readiness':'Clean locally certified A/B/D/E branch for separate integration review; no promotion authorized','final_commit_and_clean_state':'Runtime HANDOFF_RECEIPT.json is created after the evidence-only certification commit'})
    receipt={'UTC':a.now(),'canonical':a.state(),'canonical_remote':a.gt('ls-remote','origin','refs/heads/v2-development').split()[0],'preview_remote':a.gt('ls-remote','https://github.com/LatinJosephus/LatinJosephus.github.io.git','refs/heads/main').split()[0],'preview_publication':a.state(a.Path('C:/workspace/LatinJosephus-Antiquities-VII1-6-Preview-Publication-20261011')),'preview_original':a.state(a.Path('C:/workspace/LatinJosephus-Antiquities-Final-Preview-Publication-20261010')),'canonical_renderer_SHA256':a.sha((a.R/'assets/js/renderTei.js').read_bytes()),'other_worktrees':a.protected(),'writes':'Only new isolated branch/worktree, task review/runtime and local project orchestration scripts; shared Git metadata only for the authorized new worktree, branch and local commits','merge_push_deploy_reset_domain_changes':False}
    assert receipt['canonical']['HEAD']==receipt['canonical_remote']==a.F and not receipt['canonical']['status'] and receipt['preview_remote']==a.V and not receipt['preview_publication']['status'] and not receipt['preview_original']['status']
    previous={r['worktree']:r for r in start['other_worktrees']};receipt['concurrent_worktree_drift']=[{'path':r['worktree'],'before_HEAD':previous[r['worktree']].get('HEAD'),'after_HEAD':r.get('HEAD'),'before_status':previous[r['worktree']]['status'],'after_status':r['status']} for r in receipt['other_worktrees'] if r['worktree'] in previous and (r.get('HEAD')!=previous[r['worktree']].get('HEAD') or r['status']!=previous[r['worktree']]['status'])]
    a.save(a.Q/'READ_ONLY_RECEIPT.json',receipt)
    report=f'''# Post-release reader repair certificate

**A/B/D/E: PASS, locally certified. C: EDITORIAL HOLD, not repaired and not passed.** The user's explicit hold preserves the three original apparatus references and permits independent completion of the other packages. This is not a five-defect completion certificate.

| Package | Outcome | Final action |
|---|---|---|
| A | PASS | Native `Dark mode` button; Enter/Space, keyboard focus, real role/name/pressed state and existing persistence. |
| B | PASS | UI panel `reader-annotations`; selectors and MDB parent updated; original TEI IDs, notes and source order unchanged. |
| C | EDITORIAL HOLD | Missing UUID targets retained without invented mapping; permanent unresolved-reference register. |
| D | PASS | Shared reader initializes only where its work data and reader controls exist; general-page content and navigation preserved. |
| E | PASS | Registry-derived invalid Niese validation before selection/annotations; typed URL retained, no text substituted, real Proem 1/I.27 links. |

## Baseline and isolated branch

Canonical and directly verified remote: `{a.F}`. Public preview: `{a.V}`. Canonical renderer was `c4741903c21c4cc0e4629cdca4d951a5c64ffcab6da5e44e40aaaebcc0e3cad3`.

Branch: `{a.BR}`. Worktree: `{a.W}`. Tested implementation tip: `{tip}`. An evidence-only certification commit follows; its exact final HEAD, clean status and report hashes are in `{a.T}/HANDOFF_RECEIPT.json`.

Actual Git ancestry retains the certified VII.1 (`b48e8778b6ece616775d59a8e8949199c3ee84ef`) and VII.2–6 (`0f006764c36b36bc0cf856f6c3b11f2e4a03660c`) repairs. A/B/D/E have separate code commits; C has a separate evidence-only hold commit. CERTIFICATE.json lists exact commit ancestry.

## Fresh actual-build certification

- **7,376/7,376 actual Niese selections:** 26 Proem and 7,350 Books I–XX. Exact pane DOM, meaningful text hashes, original IDs, type and qualification arrays match a newly captured unmodified canonical baseline for every selection. All menus and book endpoints match. Zero selected-view duplicate IDs and zero console/network failures.
- **1,689 traditional, 198 Bamberg, 1,441 Alignment views:** exhaustive production selector/extent comparisons using getter-only harness exports, all exact; plus unmodified actual Book/containing-view navigation, direct links and reloads. 21 Book/contents configurations also match. This is a complete equivalent structural harness, not a claim of thousands of UI clicks.
- **8,002 cross-work Niese and 1,630 structural ranges:** exact production-renderer output comparisons in 21 work/book/witness configurations. Bellum/Cardwell/Greek, Whiston/Lodge controls and notes, DEH and Contra Apionem remain protected.
- VII.1–7: existing full Whiston source paragraphs exactly once; original wording/paragraph IDs/sameAs and contextual qualification. Four internal composite tests include VII.1–6, VII.2–6, repeated/nonsequential identity inputs, and VII.6–7. Adjacent physical English paragraphs remain separate. No public range UI or URL was introduced; Whiston remains contextual, not precise Niese segmentation.
- Positive protected checks include Proem25/26/I.27 transitions, XI312/326/342 and their two Bellum IV.105 attachments, XVI–XVII fragment boundaries, XVIII216–217, XX27–36/238, the complete XX268 AMEN trailer and Vita exclusion. Themes, pane/witness switching, note controls, keyboard, previous/next, reload and history passed.
- A: three pages/works, desktop and 390px mobile in both themes; Chrome accessibility tree, actual Tab/Enter/Space, focus outline and cross-navigation/reload persistence. General pages retain their exact baseline visible text and actual navbar navigation into/from readers.
- E: I.1, XX269, unsupported Proem27, malformed/empty/zero/negative/oversized Niese requests and unknown books retain their invalid URLs, show an accurate alert and no fabricated passage. Supported links, menus, reload and history remain accurate.

No production code changed after the frozen tested build. The rendered JS SHA-256 is `{a.sha((a.W/'assets/js/renderTei.js').read_bytes())}`. CHANGED_FILES.json records all eight source production hashes and all 251 built-asset hashes.

## Preservation and remaining issues

All **143 scholarly XML files** and **159 protected XML/data/registry inputs** are byte-identical in source and tested build. The entire 5,166-file frozen tracked manifest was checked: 5,158 original files unchanged; exactly eight production source files changed. No translations, Niese/division boundaries, source identifiers, source order, release marker, CNAME or configuration changed.

Package C still reproduces at [Book I, Bamberg 5](https://latinjosephus.github.io/antiquities/?book=1&bamberg=5): three links and two distinct malformed 404 destinations. The three target UUIDs are absent from all current scholarly XML and the searched locally available Git history under assets/xml. Exact source line/column, original markup, surviving candidate notes, search scope and limits are in UNRESOLVED_REFERENCES.json/.md. No fresh facsimile inspection or secure note mapping is claimed. Authoritative mapping evidence must precede a focused editorial approval packet.

An additional inherited Bellum Book-I `header` collision was independently observed in both baseline and final: Latin and English TEI headers share the original ID. It is unchanged and outside this repair's five packages. Thus the certificate does not claim globally unique document IDs for every pre-existing cross-work Book view. The targeted `annotations` collision is removed and all tested Antiquities selected/containing views have unique IDs.

Harness failures are preserved with their original observations/logs. They involved the newly found Bellum baseline collision, early build readiness, an assumed nonexistent main element, navbar transition timing and one wrong positive-test directory argument. Corrected real-template/path/wait checks passed without broad error suppression or extra production edits. The original focused job FAIL is retained; the corrected VII.1 source-content result is a separately documented PASS.

## Scope, reproduction and handoff

Production changes: `_includes/header.html`, `_includes/annotations-bar.html`, `_sass/_branding.scss`, `_sass/_antiquities.scss`, `_sass/_reader-ui.scss`, `assets/js/theme.js`, `assets/js/dark_mode.js`, `assets/js/renderTei.js`. Review artifacts are separately listed and hashed.

Fresh isolated Chrome profiles, loopback ports and download directories were used. The established native Ruby/Jekyll builder excludes the research archive and uses the same certified plugin policy; the builder/config and logs are included. No dependency upgrade or unsupported public route was introduced. REPRODUCE.md describes the preserved scripts and exact runtime inputs.

Review: CERTIFICATE.json, TEST_RESULTS.json, NIESE_MATRIX.csv, compressed complete captures, CHANGED_FILES.json, SOURCE_PRESERVATION.json, EVIDENCE_INDEX.md and READ_ONLY_RECEIPT.json. Compact ZIP checkpoints are integrity-indexed under `{a.T}/checkpoints`.

**Recommendation:** review and integrate the independently certified A/B/D/E commits through a separate authorized task. Keep C on explicit editorial HOLD. Canonical and both preview checkouts/remotes are unchanged and clean; other-worker drift, if any, is recorded without touching their work. No merge, push, deployment, destructive reset or domain change was performed.
'''
    (a.Q/'REPORT.md').write_text(report,encoding='utf8',newline='\n')
    (a.Q/'REPRODUCE.md').write_text(f'''# Reproducing the local certification

Tested implementation: {tip}; canonical baseline: {a.F}. All native build and browser dependencies were discovered from the existing certified harness. Exact executable paths, builds, configs and command arguments are preserved in postrelease_reader.py, postrelease_runqa.py, BUILD_candidate-final.json and FINAL_JOB_*.json.

The baseline site was built before production edits and remains immutable under `{a.T}/baseline-site`. The final site is `{a.T}/candidate-final-site`. Reusing these roots with fresh profiles reproduces the exact comparison; a new build can instead be created from a separate checkout of the baseline and this repair branch. The source tree must not be silently reset to create that comparison.

Run postrelease_reader.py build candidate-final to create the final native build. Run postrelease_runqa.py prepare then its niese, structural and focused jobs with Python; they invoke the discovered Node/Playwright/Chrome runtime and allocate independent ports. Run postrelease_extra.py for general navigation and structural IDs, and postrelease_screens.cjs for compact native before/after evidence. The exact original positive-test failure is archived; the corrected invocation passes the absolute candidate-final-site directory, followed by candidate as the mode.

QA harnesses under qa/ export production selectors only when explicitly instrumented for exhaustive structural or internal composite tests. The 7,376 selection replay and focused UI/source checks run unmodified built production JS. No exported getter or public combined-range control is part of the production patch.

Full DOM/text/ID/type/qualification captures are preserved compressed in baseline-NIESE.json.gz and candidate-final-NIESE.json.gz; NIESE_MATRIX.csv lists every actual local URL and matched hashes. Baseline source hashes for all 5,166 original files are in BASELINE.json. Focused VII source evidence includes full surviving English and exact Greek comparisons; no English boundaries are manufactured.
''',encoding='utf8',newline='\n')
    idx=['# Evidence index','','A/B/D/E are locally certified; C remains an explicit scholarly hold. Full result paths are relative to this review directory unless stated otherwise.','','| Evidence | Contents |','|---|---|','| FIVE_DEFECTS_baseline.json / FIVE_DEFECTS_live.json | Independent canonical/public before captures, stacks, IDs and exact failing URLs |','| FIVE_DEFECTS_after.json | Eleven fresh after routes; A/B/D/E corrected; C still three malformed links/two404s |','| UNRESOLVED_REFERENCES.json / .md | C original IDs/locations, target/history searches, surviving candidates and source limits |','| NIESE_MATRIX.csv / *-NIESE.json.gz | Every actual route; complete raw captures and exact pane/hash/ID/qualification comparisons |','| READER_FINAL_PRIOR_RESULTS.json | Complete structural and cross-work production extent/DOM comparisons |','| candidate-VII1-7.json / candidate-VII1-REGRESSION.json | Exact source-derived full Whiston and Greek evidence; one contextual paragraph, retained qualification |','| COMBINED_CONTEXT.json / CONTEXT_GUARDS.json | Internal composites and in-memory generic guards; no public range control |','| THEME_FINAL.json / COMPACT_EVIDENCE.json | Accessibility tree, keyboard, before tab sequence and small before/after screenshots |','| GENERAL_NAVIGATION.json / PACKAGE_final_final.json | Static content preservation, real navigation and controls; baseline header collision |','| CONTAINING*_UI.json / TARGETED_UI.json / VII2_6_NAVIGATION_PRESENTATION.json / KEYBOARD_FULL_SOURCE.json | Real structural/direct/history/pane/keyboard transitions |','| PROTECTED_CONTROLS.json | 29 positive XI–XX controls, terminal trailer and witness/notes switching |','| failed-attempts/ / logs/ | Original failed observations and test logs; corrected-case provenance |','| CHANGED_FILES.json / SOURCE_PRESERVATION.json / READ_ONLY_RECEIPT.json | Exact source/build/evidence hashes and repository preservation |','', '## Compact screenshot collection','']
    for n in imageNames:idx.append(f'- [screenshots/{n}](screenshots/{n}) — SHA-256 `{a.sha((a.Q/"screenshots"/n).read_bytes())}`')
    idx+=['',f'Original full-page raw screenshots remain in `{a.T}/screenshots`; large whole-book captures are deliberately excluded from the compact review/ZIP copies. No unlicensed facsimile/source images were copied.','',f'Post-commit clean-state handoff receipt: `{a.T}/HANDOFF_RECEIPT.json`.','']
    (a.Q/'EVIDENCE_INDEX.md').write_text('\n'.join(idx),encoding='utf8',newline='\n')
    # Include durable checkpoint indexes; archived ZIPs stay under the dedicated runtime.
    (a.Q/'checkpoint-indexes').mkdir(exist_ok=True)
    for f in (a.T/'checkpoints').glob('*.json'):shutil.copy2(f,a.Q/'checkpoint-indexes'/f.name)
    manifest()
    s.commit('final-certification','Certify independent reader repairs and retain the apparatus editorial hold')
    handoff={'UTC':a.now(),'baseline_canonical':a.F,'baseline_preview':a.V,'tested_implementation_commit':tip,'final_branch':a.BR,'final_commit':a.gt('rev-parse','HEAD',repo=a.W),'repair_worktree':a.state(a.W),'canonical':a.state(),'canonical_remote':a.gt('ls-remote','origin','refs/heads/v2-development').split()[0],'preview_remote':a.gt('ls-remote','https://github.com/LatinJosephus/LatinJosephus.github.io.git','refs/heads/main').split()[0],'renderer_SHA256':a.sha((a.W/'assets/js/renderTei.js').read_bytes()),'production':a.load(a.Q/'CHANGED_FILES.json')['production'],'counts':counts,'package_status':packages,'report':str(a.Q/'REPORT.md'),'report_SHA256':a.sha((a.Q/'REPORT.md').read_bytes()),'certificate_SHA256':a.sha((a.Q/'CERTIFICATE.json').read_bytes()),'manifest_SHA256':a.sha((a.Q/'CHANGED_FILES.json').read_bytes()),'review_receipt':str(a.Q/'READ_ONLY_RECEIPT.json'),'final_checkpoint':str(a.T/'checkpoints/checkpoint-final-certification.json'),'no_merge_push_publish':True}
    assert not handoff['repair_worktree']['status'] and handoff['canonical_remote']==handoff['canonical']['HEAD']==a.F and not handoff['canonical']['status'] and handoff['preview_remote']==a.V
    a.save(a.T/'HANDOFF_RECEIPT.json',handoff)
    print('FINAL CERTIFIED LOCAL COMMIT',handoff['final_commit']);print('A/B/D/E PASS; C EDITORIAL HOLD. No merge/push/publication. Clean state verified.')

if __name__=='__main__':finish()
