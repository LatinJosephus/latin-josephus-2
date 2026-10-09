"""Assemble verified combined-integration evidence; never rewrite the certified source."""
from pathlib import Path
import json,hashlib,subprocess,shutil,sys,datetime
P=Path(__file__).resolve().parent;W=P.parents[1];R=Path('C:/workspace/Antiquities-Niese-09-integration-runtime-20261009')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(v):return hashlib.sha256(v).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def git(*a,where=W):return subprocess.check_output(['git','--no-optional-locks',*a],cwd=where).decode().strip()
b=read(P/'BASELINE.json');scope=read(P/'INCOMING_SCOPE.json');plan=read(P/'BUILD_PLAN.json');qa=read(P/'BROWSER_QA.json');integrity=read(P/'INTEGRITY_QA.json')
navigation=read(P/'NAVIGATION_CONTROLS_QA.json');assert navigation['result']=='PASS' and len(navigation['checks'])==4
assert qa['result']==integrity['result']=='PASS'
assert not qa['errors'] and not qa['consoleErrors'] and not qa['networkFailures']
assert qa['total_selectable']==3448 and len(qa['IX'])==15 and len(qa['production'])==11
assert len(qa['containing_views'])==2 and all(r['complete_239_241'] for r in qa['containing_views'])
assert plan['implementation_HEAD']==integrity['tested_implementation_HEAD']
head=git('rev-parse','HEAD');assert head==plan['implementation_HEAD']
source=Path(b['certified_source_worktree']);canonical=Path(b['canonical_worktree'])
assert git('rev-parse','HEAD',where=source)==b['certified_source_HEAD'] and not git('status','--porcelain',where=source)
assert git('rev-parse','HEAD',where=canonical)==b['canonical_initial_HEAD'] and not git('status','--porcelain',where=canonical)
current_tree={line.split('\t',1)[1]:line.split()[2] for line in git('ls-tree','-r','HEAD').splitlines()}
for r in scope['files']:
    assert current_tree[r['path']]==r['incoming_Git_blob_id']
    assert sha((W/r['path']).read_bytes())==r['certified_source_worktree_sha256']
    assert sha((source/r['path']).read_bytes())==r['certified_source_worktree_sha256']
for rel,rec in b['canonical_initial_tracked_files'].items():
    if rel in {r['path'] for r in scope['files'] if r['category']=='production'}:continue
    assert current_tree[rel]==rec['Git_blob_id'] and sha((W/rel).read_bytes())==rec['worktree_sha256']
logs=P/'build-logs';logs.mkdir(exist_ok=True)
for name in ['jekyll.log','baseline-jekyll.log']:shutil.copyfile(R/'build'/name,logs/name)
for f in logs.iterdir():assert 'done in' in f.read_text(encoding='utf8')
tools={'Python':{'path':sys.executable,'version':sys.version,'sha256':sha(Path(sys.executable).read_bytes())},
 'Node':{'path':shutil.which('node'),'version':subprocess.check_output(['node','--version']).decode().strip()},
 'Git':{'path':shutil.which('git'),'version':git('--version')},
 'Docker':{'version':subprocess.check_output(['docker','--version']).decode().strip(),'image':plan['image']},
 'Chrome':{'path':'C:/Program Files/Google/Chrome/Application/chrome.exe','sha256':sha(Path('C:/Program Files/Google/Chrome/Application/chrome.exe').read_bytes())},
 'Playwright':{'path':'C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright','version':read(Path('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json'))['version']},
 'Bundler':{'version':'4.0.22','source':'build.sh and runtime dependency log'}}
write(P/'EXECUTABLE_TOOLS.json',tools)
write(P/'BUILD_RECORD.json',{**plan,'result':'PASS','actual_two_source_build_exit_code':0,'no_static_refresh':True,
 'logs':{f.name:sha(f.read_bytes()) for f in logs.iterdir()},'built_assets':integrity['built_assets'],
 'QA_origins':qa['origins'],'isolated_browser_profile':str(R/'profile-integration'),'tool_identities':'EXECUTABLE_TOOLS.json'})
SP=W/'review/Antiquities_Niese_BookIX_2026-10-09';cert=read(SP/'CERTIFICATION.json')
verification={'result':'PASS_READY_FOR_CANONICAL_FAST_FORWARD_AND_NORMAL_PUSH','tested_merge_HEAD':head,
 'merge_parents':git('show','-s','--format=%P',head).split(),'actual_canonical_preparation_HEAD':b['canonical_initial_HEAD'],
 'certified_source_HEAD':b['certified_source_HEAD'],'certified_source_branch_unchanged':True,
 'incoming_production_count':scope['production_count'],'incoming_review_count':scope['review_count'],'incoming_total':scope['total'],
 'production_resolution_count':0,'incoming_all_exact':True,'canonical_advance_preserved':True,
 'IX_exhaustive_certification_retained':True,'focused_combined_build_QA':'PASS','source_byte_recovery':'PASS',
 'represented_Latin_intervals':232,'retained_Latin_starts':46,'added_Latin_milestones':186,'unavailable_IX_identities':59,
 'IX_selectable_identities':291,'previous_selectable_baseline':3157,'resulting_selectable_total':3448,
 'editorial_decisions_pending':[],'Greek_opening_added':1,'Greek_relocations':[181,216,240],
 'actual_IX_focus_selections':[x['n'] for x in qa['IX']],'actual_unmodified_production_selections':[x['n'] for x in qa['production']],
 'covered_containing_views':qa['containing_views'],'protected_checks':qa['protected'],'Whiston_contents_checks':qa['contents'],
 'actual_protected_navigation_events':'NAVIGATION_CONTROLS_QA.json',
 'source_certification_sha256':sha((SP/'CERTIFICATION.json').read_bytes()),
 'no_preview_or_deployment':True,'recorded_UTC':datetime.datetime.now(datetime.UTC).isoformat()}
write(P/'VERIFICATION.json',verification)
prod='\n'.join('- `'+r['path']+'`' for r in scope['files'] if r['category']=='production')
report=f'''# Antiquities IX — verified canonical integration

The complete certified IX branch has been merged in isolation with current canonical and passes combined-build verification. It is ready for canonical fast-forward and the explicitly authorized normal push. Public-preview refresh and deployment are outside this assignment. The handoff response reports the final directly verified canonical and remote heads after execution.

Certified source: `{b['certified_source_HEAD']}` on `antiquities-niese-09`, at `{source}`. Source branch and working files remain unchanged and clean. Its frozen base is `{b['frozen_IX_base']}`. Actual canonical and origin before preparation were `{b['canonical_initial_HEAD']}` on `v2-development`, clean. That canonical advance contains the Whiston compiled-index work; every existing canonical file except the four accepted IX production paths is preserved byte-for-byte. No other worker's branch, worktree, runtime or browser session was modified.

Integration branch: `antiquities-niese-09-integration`, at `{W}`. Review: `{P}`. Dedicated runtime: `{R}`. Tested merge: `{head}`; parents: `{verification['merge_parents']}`. The full IX history is preserved as a merge parent, rather than integrating only the final §240 change. No conflict or production reconciliation was required. Canonical can advance to this tested result and its subsequent review-only certification commit by fast-forward.

## Exact scope

The incoming delta from `{b['frozen_IX_base']}` to `{b['certified_source_HEAD']}` is **{scope['production_count']} production files + {scope['review_count']} review files = {scope['total']} files**. INCOMING_SCOPE.json lists each path, status, Git blob identity and certified working-byte hash. All incoming files match the certified source exactly. The 200 review files are the complete accepted IX packet, including original frozen inputs, printed images, editorial history and prior/final QA.

The four incoming production paths are:

{prod}

Integration-specific additions are review-only under `review/Antiquities_Niese_Integration_09_2026-10-09`; FILE_MANIFEST.json records their exact final list, count and hashes. The checkpoint, merge and final verification commits keep review-only work distinct. Production resolutions: zero. Existing Whiston contents/CSS, English narrative sources and every other book remain as current canonical.

## Accepted boundaries and preservation

Greek opening identity1 is added, and markers181,216,240 are relocated. IX.240 begins before Greek `ἔσται δ᾽` and Latin `et nullus`. The incoming DECISION_240.md retains the shared printed line and both alternatives: A is an explicit editorial resolution of the word-level ambiguity; the inherited Greek `σώζειν γὰρ` paired with Latin `dum animas suas` remains rejected B. The printed numeral is not described as unambiguously fixing the word cut. Decisions are closed.

**232 represented Latin intervals = 46 retained starts + 186 milestones. 291 identities = 232 represented Latin intervals + 59 unavailable identities (§§51–109).** IX.110 retains its qualified surviving tail. All three supplied IX witnesses omit51–109; no physical cause or tradition-wide absence is inferred. Removing only the added Latin milestones and reversing the authorized Greek marker operations recovers the exact frozen source bytes. English source bytes are unchanged. INTEGRITY_QA.json independently repeats the inverse against the actual combined source files.

## Verification of the combined implementation

A fresh complete Jekyll build of the tested merge and a fresh archived build of actual pre-integration canonical both exited0. No repository plugin was omitted and no static refresh was used. Read-only mounts and a pinned Ruby image isolate build dependencies and output in the dedicated runtime. All incoming production output hashes equal the certified IX result. Current canonical CSS, source-contents index and Whiston IX contents output hashes also match their actual retained source bytes. BUILD_RECORD.json records build provenance, logs, executable identities and output hashes. Initial preparation failures are accurately retained in PREPARATION_DIAGNOSTICS.md and are not counted as successful certification.

Because the renderer, IX XML and identity data are identical to the certified result, its exhaustive 291-selection and 68-range certification remains applicable. Fresh focused integration QA used actual events at `{verification['actual_IX_focus_selections']}`, including opening,50/51,109/110,181,216,239–241 and ending. Deep links, previous/next, Back/Forward, reload, pane toggles, IDs and exact expected Greek/Latin/English-context extents pass. Eleven critical URLs additionally pass with unmodified production code. Screenshots at IX.240 in both themes were visually inspected.

Complete resulting239–241 Greek and Latin extents are present in ChapterXI and subchapterXI.3; each entire containing pane projection equals actual canonical with only the approved marker differences removed. Protected checks include VIII.367,VIII.369,X.108 with independently available Greek/English, actual traditional/Bamberg/Alignment routes and Bellum Whiston/Lodge views compared to the current canonical build. Current Whiston/Greek contents forVIII,IX,X match their canonical projections, with English15/14/11 entries and IX Contents→Niese→Contents roundtrip. Actual menus across all20 books confirm **3,157 +291 =3,448 selectable Antiquities Niese identities**, distinct from IX's232 represented Latin intervals and59 addressable absence states. No unexpected script, console or network diagnostics occurred in the passing final gate.

## Advance and push gate

Before advancing canonical, recheck its HEAD and clean state against the frozen actual canonical state and verify origin directly. Preserve and reconcile any intervening advance rather than resetting it. Advance with `--ff-only`, verify canonical production bytes against the tested build, push only `v2-development` normally to its existing origin, and read remote HEAD directly afterward. The certified IX source branch remains fixed at `{b['certified_source_HEAD']}`. No public-preview refresh or deployment is authorized or performed.
'''
(P/'REPORT.md').write_text(report,encoding='utf8',newline='\n')
files=[f for f in sorted(P.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f!=P/'FILE_MANIFEST.json']
write(P/'FILE_MANIFEST.json',{'tested_merge_HEAD':head,'canonical_preparation_HEAD':b['canonical_initial_HEAD'],
 'incoming_scope':'INCOMING_SCOPE.json','incoming_production_count':scope['production_count'],'incoming_review_count':scope['review_count'],
 'integration_specific_review_count_including_manifest':len(files)+1,
 'integration_specific_paths':[str(f.relative_to(W)).replace('\\','/') for f in files]+[str((P/'FILE_MANIFEST.json').relative_to(W)).replace('\\','/')],
 'review_files':[{'path':str(f.relative_to(W)).replace('\\','/'),'absolute_path':str(f),'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in files],
 'self_hash_exclusion':'FILE_MANIFEST.json','production_resolutions':[]})
print(f'PASS: integration evidence finalized; {len(files)+1} review-only additions; 3448 selections; canonical fast-forward/normal push gate ready')
