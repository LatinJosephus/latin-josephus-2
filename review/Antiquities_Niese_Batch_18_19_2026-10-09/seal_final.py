"""Seal independent book certificates only after all actual-reader proofs pass."""
from reconnaissance import *
from collections import Counter
from datetime import datetime,timezone
import ast

PRODUCTION = ['assets/js/renderTei.js','assets/xml/antiquities/Latin/book-18.xml','assets/xml/antiquities/Latin/book-19.xml','assets/xml/antiquities/niese/book-18.json','assets/xml/antiquities/niese/book-19.json']
DIRECTORIES = [str(packet(b).relative_to(ROOT)).replace('\\','/') for b in [18,19]]+[str(PACK.relative_to(ROOT)).replace('\\','/')]

def read(p):return json.loads(p.read_text(encoding='utf8'))

def supporting():
    checks=[]
    for p in sorted(PACK.glob('*.py')):
        ast.parse(p.read_text(encoding='utf8'),filename=str(p));checks.append(dict(path=str(p.relative_to(ROOT)),check='Python syntax',status='PASS'))
    for p in sorted(list(PACK.glob('*.cjs'))+[ROOT/'assets/js/renderTei.js']):
        r=subprocess.run([r'C:\Program Files\nodejs\node.exe','--check',str(p)],capture_output=True)
        assert r.returncode==0,r.stderr.decode();checks.append(dict(path=str(p.relative_to(ROOT)),check='JavaScript syntax',status='PASS'))
    commands=[['git','diff','--check',BASE,'--','assets','_includes'],['git','diff','--check','1938fa015ec9273ed396754a362f25f14ae6c6f8','--','.',':(exclude)*.patch',':(exclude)**/history/pre-adjudication-1938fa0/CASE_*.md'],['git','apply','--reverse','--check','--whitespace=nowarn',str(PACK/'REVIEW_RENDERER.patch')]]
    for cmd in commands:
        r=subprocess.run(cmd,cwd=ROOT,capture_output=True);assert r.returncode==0,r.stdout.decode()+r.stderr.decode()
    save(PACK/'FINAL_SYNTAX_QA.json',dict(status='PASS',files=checks,commands=commands,verbatim_whitespace_policy='Earlier source quotations and their exact archived copies retain original terminal spaces. Archived CASE Markdown is excluded from new-edit whitespace lint, with its byte-exact archival hash separately verified. Required single-space unified-diff context lines are also excluded. All production files pass normal whitespace lint; the generic patch reverses cleanly.'))

def validate_all():
    browser=read(PACK/'FINAL_BROWSER.json');prior=read(PACK/'PROTECTED_FINAL_BROWSER.json');transition=read(PACK/'TRANSITION_FINAL_BROWSER.json');legacy=read(PACK/'LEGACY_DISTINCT_FINAL_BROWSER.json');protection=read(PACK/'FINAL_PRODUCTION_PROTECTION_QA.json');build=read(PACK/'FINAL_BUILD.json');visual=read(PACK/'FINAL_VISUAL_REVIEW.json')
    for record in [browser,prior,transition,legacy,protection,visual]:assert record['status']=='PASS'
    assert len(browser['selections'])==745 and len(prior['selections'])==5231
    assert sum(s['Latin']=='EXACT_INTERVAL_PASS' for s in browser['selections'])==743
    assert [(s['book'],s['number']) for s in browser['selections'] if s['Latin']=='APPROVED_UNAVAILABLE_PASS']==[(18,216),(18,217)]
    assert not prior.get('reusedCompletedReplay') and not browser['errors'] and not prior['errors'] and not transition['errors'] and not legacy['errors']
    assert len(browser['views'])==267 and len(browser['interactions'])==43
    assert len(prior['protectedRoutes'])==13 and len(prior['knownBaselineIssues'])==2
    assert len(legacy['legacyRoutes'])==29 and len(legacy['physicalPoints'])==6
    source_controls=read(PACK/'SOURCE_CONTROLS_FINAL_BROWSER.json')
    assert source_controls['status']=='PASS' and len(source_controls['events'])==3 and not source_controls['errors']
    assert build['exit_code']==0 and build['all_changed_production_build_bytes_equal']
    for rel in PRODUCTION:
        raw=(ROOT/rel).read_bytes();assert raw==(Path(build['source'])/rel).read_bytes()==(Path(build['site'])/rel).read_bytes()
    scopes=git('diff','--name-only',BASE).decode().splitlines()
    assert sorted(p for p in scopes if not p.startswith('review/'))==PRODUCTION
    assert all(p in PRODUCTION or any(p.startswith(d+'/') for d in DIRECTORIES) for p in scopes)
    assert read(PACK/'ADJUDICATION_APPROVAL.json')['status']=='ALL_FOUR_HOLDS_CLOSED'
    for b in [18,19]:
        expected=read(packet(b)/'FINAL_EXPECTED_INTERVALS.json');census=browser['books'][str(b)]['reviewCensus']
        assert census['Latin']==[e['number'] for e in expected if e['safe_Latin_interval']]
        assert census['Greek']==census['menu']==list(range(1,len(expected)+1))
        assert read(packet(b)/'INDEPENDENT_FINAL_LOGICAL_QA.json')['status']=='PASS'
        assert read(packet(b)/'INDEPENDENT_FINAL_PRESERVATION_QA.json')['independent_exact_byte_reversal']
    return browser,prior,transition,legacy,protection,build,scopes

def seal_book(b,data):
    browser,prior,transition,legacy,protection,build,scopes=data;d=packet(b);rows=read(d/'IDENTITIES.json');plan=read(d/'FINAL_MARKER_PLAN.json');proof=read(d/'INDEPENDENT_FINAL_PRESERVATION_QA.json');frozen=read(d/'BASELINE.json')
    selections=[s for s in browser['selections'] if s['book']==b];views=[v for v in browser['views'] if v['book']==b]
    cases=['CASE_007','CASE_094','CASE_216_217'] if b==18 else ['CASE_188']
    for r in rows:r['reader_certified']=True;r['final_reader_status']='APPROVED_UNAVAILABLE_WITH_INDEPENDENT_GREEK_ENGLISH' if not r['candidate'].get('locator') else 'EXACT_LATIN_GREEK_AND_PRESERVED_ENGLISH_CONTEXT_PASS'
    save(d/'IDENTITIES.json',rows)
    qa=dict(book=b,status='PASS',scope='ACTUAL_FINAL_PRODUCTION_READER',build_commit=build['source_commit'],selections=selections,containing_views=views,legacy_ranges=browser['books'][str(b)]['legacyRanges'],legacy_URLs=[r for r in legacy['legacyRoutes'] if r['book']==b],distinct_physical_points=[r for r in legacy['physicalPoints'] if r['book']==b],interactions=[r for r in browser['interactions'] if r['book']==b],themes=[r for r in transition['themes'] if r['book']==b],sources=transition['sources'],all_5231_baseline_selections_replayed_afresh=True,protected_controls=prior['protectedRoutes'],errors=[])
    save(d/'FINAL_BROWSER.json',qa)
    cert=dict(book=b,status='LOCAL_CERTIFIED_READY_FOR_COORDINATED_INTEGRATION',certified=True,ready_for_integration=True,utc=datetime.now(timezone.utc).isoformat(),baseline=BASE,worktree=str(ROOT),branch='antiquities-niese-18-19',runtime=str(RUNTIME),actual_production_build_commit=build['source_commit'],complete_primary_source_review=True,primary_review_accepted_by_human=True,Greek_identities=len(rows),Greek_explicit_starts=len(frozen['explicit_Greek_numbers']),Greek_implicit_opening_reused_anchor=rows[0]['Greek_physical_start'],Latin_identities_individually_reviewed=len(rows),Latin_counts=dict(independent_intervals=len(rows)-len(plan['approved_unavailable_sections']),unavailable_identities=plan['approved_unavailable_sections'],retained_numeric_starts=len(plan['retained_starts']),retained_existing_physical_starts=len(plan['reused_physical_starts']),new_niese_milestones=len(plan['markers']),new_end_anchors=0,new_other_anchors=0,qualified_available_intervals=sum(bool(r['candidate'].get('locator') and r['candidate'].get('note')) for r in rows),correspondence_counts=dict(Counter(r['candidate']['correspondence'] for r in rows))),all_holds_closed=True,case_decisions={name:read(d/(name+'.json'))['adjudication']['approved_choice'] for name in cases},previous_HOLD_commit='1938fa015ec9273ed396754a362f25f14ae6c6f8',preserved_history='history/pre-adjudication-1938fa0',byte_recovery=dict(independent_exact_reversal=True,coordinate_inverse=True,baseline_Latin_sha256=proof['source_sha256'],production_Latin_sha256=proof['candidate_sha256'],recovered_Latin_sha256=proof['source_sha256'],Greek_byte_identical=True,English_byte_identical=True,IDs_sameAs_Unicode_punctuation_whitespace_inline_markup_chapter_TOC_order_preserved=True),physical_locator_checks=len(proof['structural_locators']),browser=dict(all_Niese_selections=len(selections),exact_Latin_intervals=sum(s['Latin']=='EXACT_INTERVAL_PASS' for s in selections),approved_unavailable_with_independent_Greek_and_English=sum(s['Latin']=='APPROVED_UNAVAILABLE_PASS' for s in selections),containing_views=len(views),legacy_chapter_ranges=len(qa['legacy_ranges']),legacy_URLs=len(qa['legacy_URLs']),distinct_point_checks=len(qa['distinct_physical_points']),deep_navigation_interactions=len(qa['interactions']),all_prior_selections=5231,known_baseline_defects_only=True),protected_baseline_files=protection['protected_baseline_files'],protected_unchanged_files=protection['unchanged_files'],production_scope=[info(ROOT/rel) for rel in PRODUCTION if rel.endswith(f'book-{b:02}.xml') or rel.endswith(f'book-{b:02}.json')],no_merge_push_publication_preview_or_canonical_change=True)
    save(d/'CERTIFICATE.json',cert)
    save(d/'FILE_MANIFEST.json',dict(scope=str(d.relative_to(ROOT)),self_hash_excluded=True,files=[info(p) for p in sorted(d.rglob('*')) if p.is_file() and p!=d/'FILE_MANIFEST.json' and '__pycache__' not in p.parts]))
    print('Book',b,'independently LOCAL CERTIFIED')

def seal_batch(data):
    browser,prior,transition,legacy,protection,build,scopes=data
    certs={b:read(packet(b)/'CERTIFICATE.json') for b in [18,19]};assert all(c['certified'] for c in certs.values())
    supporting()
    commits=[dict(commit=line.split('\t')[0],subject=line.split('\t')[1]) for line in git('log','--reverse','--format=%H%x09%s',BASE+'..HEAD').decode().splitlines()]
    save(PACK/'SCOPED_COMMITS.json',dict(baseline=BASE,local_commits_before_final_seal=commits,branch='antiquities-niese-18-19',final_seal_receipt='The final seal commit is reported by Git after this packet is committed; a commit cannot contain its own hash.',merge_push_publication=False))
    save(PACK/'FINAL_SCOPE_MANIFEST.json',dict(baseline=BASE,production_paths=PRODUCTION,production_files=[info(ROOT/p) for p in PRODUCTION],review_directories=DIRECTORIES,tracked_paths_against_baseline=scopes,baseline_protected_unchanged_files=protection['unchanged_files'],actual_build_commit=build['source_commit'],ready_for_coordinated_integration=True))
    hashes='\n'.join(f"| `{rel}` | `{sha((ROOT/rel).read_bytes())}` |" for rel in PRODUCTION)
    commits_text='\n'.join(f"- `{x['commit']}` — {x['subject']}" for x in commits)
    report=f'''# Antiquities XVIII–XIX: final local certification

**Both books are independently certified and ready for coordinated integration.** All four human adjudications are applied as A, B, A, A. There are no open editorial holds. The isolated local reader now supplies **5,976 selectable identities = 5,231 baseline + 379 XVIII + 366 XIX**.

Baseline: `{BASE}`. Branch: `antiquities-niese-18-19`.
Worktree: `{ROOT}`. Disposable runtime: `{RUNTIME}`.
Actual production build: `{build['source_commit']}`, served only locally from `final-site`. Subsequent certification commits change review records only; every changed production file is byte-identical in the worktree, committed build source and built site. The final seal commit and clean-state receipt are obtained from Git after committing this report. No merge, push, canonical write, preview change or publication occurred. XI and other workers' workspaces were not used or changed.

## Final counts, recomputed after adjudication

| Certified figure | XVIII | XIX | Total |
|---|---:|---:|---:|
| Independently reviewed/selectable Niese identities | 379 | 366 | 745 |
| Existing explicit Greek numbers retained | 378 | 365 | 743 |
| Existing Greek opening anchors reused | 1 | 1 | 2 |
| Independent Latin intervals | 377 | 366 | 743 |
| Latin identities without an independent interval | 2 | 0 | 2 |
| Existing numeric Latin starts retained | 0 | 0 | 0 |
| Existing source-qualified Latin starts reused | 61 | 46 | 107 |
| Added Latin Niese milestones | 316 | 320 | 636 |
| Added Greek markers / end anchors / other anchors | 0 | 0 | 0 |
| Qualified available Latin intervals | {certs[18]['Latin_counts']['qualified_available_intervals']} | {certs[19]['Latin_counts']['qualified_available_intervals']} | {sum(c['Latin_counts']['qualified_available_intervals'] for c in certs.values())} |

The final marker totals supersede preliminary314/319. All743 positive Latin intervals form an exact, positive-length, consecutive partition of the complete original narrative stream. There is no interval invented for216 or217, no borrowed neighbouring text and no inserted gap or conjecture. Existing Latin IDs, literal Roman labels and source chapter signs remain unchanged; zero numeric starts reflects the actual original Latin files.

## Closed decisions and preserved history

- XVIII.7 **A** begins `et supra quam dici potest`; the preceding material remains in6. Reciprocal6/7 notes retain the shared correspondence qualification.
- XVIII.94 **B** begins `Transacta uero festiuitate`; the preceding feast-only relative remains with its Latin candlestick antecedent in93. The approved93/94 notes report the limited correspondence and missing distinct timing/purification expression.
- XVIII.216–217 **A** supplies no independent Latin interval in the present Bamberg transcription. Each Greek identity and its Whiston context is independently selectable. Separate Latin notices identify the astrology/Galba account at216 and the general divination account at217, explain the direct215→218 transition, and retain cross-references to the succession-omen/foreknowledge wording at218. This representation establishes neither omission from the original Latin translation nor a scribal, exemplar or physical-loss mechanism.
- XIX.188 **A** begins `Erant enim cohortes`; the preceding `qui senatui consentiebant` remains in187. Reciprocal notes preserve the allegiance overlap and absence of an independently expressed sign-distribution statement.

Every case preserves its exact alternatives, primary source evidence, original mixed-content/Unicode/UTF-8 coordinates and earlier pending statement, then appends the human approval and applied adjacent extents. The complete prior HOLD records are preserved verbatim under `history/pre-adjudication-1938fa0` and at `{ '1938fa015ec9273ed396754a362f25f14ae6c6f8' }`. `ADJUDICATION_ARCHIVE.json` hashes every archived record; independent verification checks all of them. `DECISION_HISTORY.json` retains every prior proposal and appends dated human adjudication events. Historical review-only plans and outputs remain explicitly distinct from the final production plans and certificates.

Primary evidence remains the individually examined Niese IV (1890) print, all379/366 Greek identities, complete Latin witnesses and full book endings, with the frozen Loeb IX (1965) and October4–7 structural controls. The human accepted this completed review. Original printed-page images, all individual observations and their hashes are preserved. Greek duration notices, source-only contents, nested argument/floatingText, apparatus and XIX→XX separation remain literal.

## Independent source preservation

Coordinate-based inversion and a separate grammar-based inversion both recover the exact original Latin bytes. The latter independently checks the complete set/order of authorized markers without trusting shifted inverse coordinates. A further independent proof verifies every actual inserted UTF-8 point and the full interval partition.

| Book | Recovered original Latin SHA-256 | Actual production Latin SHA-256 |
|---|---|---|
| XVIII | `{certs[18]['byte_recovery']['baseline_Latin_sha256']}` | `{certs[18]['byte_recovery']['production_Latin_sha256']}` |
| XIX | `{certs[19]['byte_recovery']['baseline_Latin_sha256']}` | `{certs[19]['byte_recovery']['production_Latin_sha256']}` |

Greek and English bytes are unchanged. IDs, sameAs, Unicode, punctuation, whitespace, inline markup, paragraph/chapter order, all inherited labels, image/page/column milestones, TOCs and source header/trailer material are preserved. All462 current source-qualified structural locators pass. Of282 frozen protected production files,279 retain their hashes; the only three modified baseline files are the two assigned Latin files and generic renderer. Two new assigned registries complete the five-path production scope. All unrelated works, other books, Whiston source bytes, structure.xml, display controls and source navigation records are protected.

## Actual reader certification

| Live certification class | Final result |
|---|---|
| All745 new Niese selections, all three panes | PASS:745 exact Greek ranges,745 unchanged English contexts,743 exact Latin intervals,2 approved specific unavailability notices |
| All5,231 prior selections, freshly replayed baseline versus final build | PASS: identical live texts, paragraph IDs/sameAs, notes, context and absence states; no checkpoint reuse |
| All267 containing views | PASS:154 traditional/subchapter/Bamberg,109 Alignment,4 Book/contents; full endpoints in all three languages |
| All29 legacy chapter ranges /87 language ranges | PASS:21 XVIII and8 XIX; complete original endpoints retained |
| All29 inherited chapter URLs | PASS: actual baseline/final routes and DOM meanings identical |
| All6 mandatory distinct physical points | PASS in Latin, Greek and English |
| All43 deep interaction cases | PASS: direct/reloaded URLs, previous/next, terminal controls, back/forward; all approved cases and both neighbours included |
| XVII→XVIII→XIX→XX book transitions | PASS with frozen XVII/XX availability and ordinary Book-view fallback |
| Language panes, available source controls and accessibility | PASS; unique IDs in every new Niese selection, labelled navigation, qualified notices with accessible roles |
| Light/dark themes | PASS: all4 settled final screenshots visually inspected |
|13 protected control routes | PASS: XV endpoint/Bamberg/contents, XVII/XX, Bellum Cardwell/Whiston/Lodge, DEH and Contra Apionem |
|3 actual Whiston/Lodge selector changes | PASS: both baseline and final DOM equal their independently loaded source routes; Cardwell preserved |
| Syntax, production whitespace and generic patch reversal | PASS; verbatim archival source-quotation whitespace retained explicitly |

Traditional chapter counts remain9/9, subchapters57/52 and Bamberg divisions19/8. At XVIII.257, traditional VIII stays at paragraph start and Bamberg literal`XVIIII` remains later at Greek153/Latin156/English187. At XIX.292, traditional VI stays at paragraph start and literal Bamberg`V` remains later at Greek146/Latin133/English153. Complete containing ranges and direct runtime locator resolution independently confirm the distinctions. New Niese milestones are excluded from the original structural milestone ordinal vocabulary, which retains every original unit type, including unqualified image markers.

Named section regressions include XVIII1,6–8,63–64,93–95,116–119,215–218,256–258,378–379 and XIX1,187–189,291–293,353–366. Final tails are complete; no text is borrowed from XX. All prior VIII–X and XII–XV identities are included in the5,231 exhaustive replay. No provisional XI/XVI–XVII identities are added to the pinned baseline arithmetic.

The only reproduced reader failures are the two precisely known Book-I baseline defects: three inherited apparatus links/two distinct404 targets and the unsupportedI.1 null-querySelector exception. Both readers reproduce their exact signatures; I.1 is outside the selectable population. No other console, asset or page error is excused. The pre-existing full Book-view duplicate`annotations` ID remains identical to baseline; every new Niese selection has zero duplicate IDs.

## Exact scope and handoff

| Production path | Final SHA-256 |
|---|---|
{hashes}

Review scope is exclusively:

- `review/Antiquities_Niese_BookXVIII_2026-10-09`
- `review/Antiquities_Niese_BookXIX_2026-10-09`
- `review/Antiquities_Niese_Batch_18_19_2026-10-09`

`FINAL_SCOPE_MANIFEST.json` records every tracked path against baseline and production hashes. Each book's `FILE_MANIFEST.json` and `CERTIFICATE.json` provide separately sealed evidence, intervals, preservation proof and browser certification. The batch manifest lists all batch artifacts. Generic renderer changes reuse the current per-language declarative physical locator resolver and contain no book-specific boundary workaround. The implementation was developed by this WorkBot against the pinned baseline; no other WorkBot renderer was copied.

Local checkpoint commits before final seal:

{commits_text}

The final seal's own hash and clean state are reported after committing this packet. Both books are ready for a coordinator to review and integrate together with concurrent work. This task stops at the clean local branch.
'''
    for old,new in {'preliminary314/319':'preliminary 314/319','All743':'All 743','for216':'for 216','or217':'or 217','in6.':'in 6.','Reciprocal6/7':'Reciprocal 6/7','in93.':'in 93.','approved93/94':'approved 93/94','at216':'at 216','at217':'at 217','direct215':'direct 215','at218':'at 218','in187':'in 187','all379/366':'all 379/366','All462':'All 462','Of282':'Of 282','files,279':'files, 279','All745':'All 745','PASS:745':'PASS: 745',',745':', 745',',743':', 743',',2 approved':', 2 approved','All5,231':'All 5,231','All267':'All 267','PASS:154':'PASS: 154',',109':', 109',',4 Book':', 4 Book','All29':'All 29','/87 language':'/87 language','PASS:21':'PASS: 21','and8':'and 8','All6 mandatory':'All 6 mandatory','All43':'All 43','all4 settled':'all 4 settled','|13 protected':'| 13 protected','|3 actual':'| 3 actual','remain9/9':'remain 9/9','subchapters57/52':'subchapters 57/52','divisions19/8':'divisions 19/8','literal`':'literal `','Greek153/Latin156/English187':'Greek 153/Latin 156/English 187','Greek146/Latin133/English153':'Greek 146/Latin 133/English 153','XVIII1,':'XVIII.1,','XIX1,':'XIX.1,','the5,231':'the 5,231','distinct404':'distinct 404','unsupportedI.1':'unsupported I.1','duplicate`':'duplicate `'}.items():report=report.replace(old,new)
    (PACK/'REPORT.md').write_text(report,encoding='utf8',newline='\n')
    save(PACK/'CERTIFICATE.json',dict(status='LOCAL_CERTIFIED_READY_FOR_COORDINATED_INTEGRATION',certified=True,baseline=BASE,branch='antiquities-niese-18-19',selectable_total=5976,new_identities=745,prior_identities_freshly_replayed=5231,independent_Latin_intervals=743,unavailable_Latin_identities=['18.216','18.217'],new_Latin_milestones=636,reused_Latin_physical_starts=107,all_editorial_holds_closed=True,books=[certs[b] for b in [18,19]],production_files=[info(ROOT/p) for p in PRODUCTION],actual_build_commit=build['source_commit'],no_merge_push_publication=True))
    all_paths=sorted(set(git('diff','--name-only',BASE).decode().splitlines()+git('ls-files','--others','--exclude-standard').decode().splitlines()))
    assert all(p in PRODUCTION or any(p.startswith(d+'/') for d in DIRECTORIES) for p in all_paths)
    save(PACK/'FINAL_SCOPE_MANIFEST.json',dict(baseline=BASE,production_paths=PRODUCTION,production_files=[info(ROOT/p) for p in PRODUCTION],review_directories=DIRECTORIES,all_changed_or_added_paths_against_baseline=all_paths,baseline_protected_unchanged_files=protection['unchanged_files'],actual_build_commit=build['source_commit'],ready_for_coordinated_integration=True))
    save(PACK/'FILE_MANIFEST.json',dict(scope='BATCH_REVIEW_PACKET_ONLY',self_hash_excluded=True,files=[info(p) for p in sorted(PACK.rglob('*')) if p.is_file() and p!=PACK/'FILE_MANIFEST.json' and '__pycache__' not in p.parts]))
    print('Final batch LOCAL CERTIFIED; production scope five paths;5976 selectable identities.')

if __name__=='__main__':
    data=validate_all()
    if sys.argv[1] in ['18','19']:seal_book(int(sys.argv[1]),data)
    elif sys.argv[1]=='batch':seal_batch(data)
    else:raise ValueError('Use18,19 or batch')
