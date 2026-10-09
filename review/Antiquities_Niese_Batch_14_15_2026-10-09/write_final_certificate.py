"""Finalize one independently completed book without advancing another book."""
from pathlib import Path
import json,sys,subprocess,csv,datetime
from source_scope import digest
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
PIN='ad3158b7a86dea6997510b3de17f2e510c23367c';b=int(sys.argv[1]);build=sys.argv[2];roman={14:'XIV',15:'XV'}[b]
P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09';site=Path(r'C:\workspace\Antiquities-Niese-14-15-runtime-20261009')/build/'site'
def load(name):return json.loads((P/name).read_text())
def save(path,x):path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd).decode().strip()
partition=load('COMPLETE_PARTITION_QA.json');reader=load('FULL_READER_QA.json');english=load('ENGLISH_CONTEXT_READER_QA.json')
protected=json.loads((BATCH/f'PROTECTED_COMPLETE_EXISTING_BOOKS_BROWSER_QA_{build}.json').read_text())
assert all(q['status' if 'status' in q else 'result']=='PASS' for q in [partition,reader,english,protected])
assert len(reader['selections'])==len(english['selections'])==partition['expected_sections']
assert Path(reader['local_build']).resolve()==Path(english['local_build']).resolve()==site.resolve()
assert not reader['registry_injected'] and not reader['browserErrors'] and not english['browserErrors']
rows=load('BOUNDARIES.json');assert not any(r['editorial_status']=='PENDING_USER_DECISION' for r in rows)
for r in rows:r['reader_certified']=True
save(P/'BOUNDARIES.json',rows)
plan=load('APPROVED_MARKER_PLAN_PARTIAL.json');plan.update(full_book_complete=True,reader_certified=True);save(P/'APPROVED_MARKER_PLAN.json',plan)
impl=load('LATIN_PARTIAL_IMPLEMENTATION.json');impl.update(status='COMPLETE_LOCAL_CORPUS_AND_READER_CERTIFIED',reader_availability_changed=True,reader_certified=True,registry_needed_before_enablement=False);save(P/'LATIN_IMPLEMENTATION.json',impl)
terminal=load('TERMINAL_EXTENT.json');terminal['full_book_partition_certified']=True;save(P/'TERMINAL_EXTENT.json',terminal)
opening=load('GREEK_OPENING_IMPLEMENTATION.json');opening.update(status='GREEK_OPENING_APPLIED_BOOK_LOCALLY_CERTIFIED',reader_certified=True);save(P/'GREEK_OPENING_IMPLEMENTATION.json',opening)
sources=load('PRINTED_SOURCES.json');sources['current_visual_inspection_complete']=True;sources['inspection_scope']='All relevant printed Niese narrative starts, opening, ending and listed independent control pages. This does not claim every page of the control PDF was inspected.';save(P/'PRINTED_SOURCES.json',sources)
registry=load('IDENTITY_REGISTRY.json');save(P/'EXECUTABLE_IDENTITIES.json',dict(book=b,status='COMPLETE_LOCAL_READER_CERTIFIED',expected_range=registry['range'],full_book_enabled=True,sections=registry['sections'],suppressedLatinLabels=registry['suppressedLatinLabels'],pending_editorial=[],unreviewed=[]))
snapshot=P/f'reader-certified-{build}';snapshot.mkdir(exist_ok=True)
for record in reader['built_files']:
 raw=(site/record['path']).read_bytes();assert digest(raw)==record['sha256']==digest((ROOT/record['path']).read_bytes())
 target=snapshot/('renderTei.js' if record['path'].endswith('renderTei.js') else 'IDENTITY_REGISTRY.json' if record['path'].endswith('.json') else record['path'].split('/')[-2]+'.xml')
 target.write_bytes(raw)
for name in ['FULL_READER_QA.json','ENGLISH_CONTEXT_READER_QA.json']: (snapshot/name).write_bytes((P/name).read_bytes())
(P/'LOCAL_BUILD_LOG.txt').write_bytes((site.parent/'jekyll.log').read_bytes())
canonical=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development');canon=git('rev-parse','HEAD',cwd=canonical)
certificate=dict(book=b,status='READY_FOR_COORDINATED_INTEGRATION',certified_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),pinned_commit=PIN,canonical_observed_HEAD=canon,frozen_inputs_advanced=False,branch=git('branch','--show-current'),implementation_parent_commit=git('rev-parse','HEAD'),worktree=str(ROOT),review_directory=str(P),runtime_directory=str(site.parents[1]),local_origin=reader['origin'],local_build=str(site),
 expected_sections=partition['expected_sections'],Greek_print_verified=partition['Greek_verified_starts'],Latin_individually_reviewed=partition['Latin_reviewed_candidates'],selectable_identities=partition['selectable_identities'],nonempty_Latin_intervals=partition['nonempty_Latin_intervals'],added_Latin_milestones=partition['added_milestones'],retained_starts=partition['retained_starts'],unavailable_sections=partition['unavailable_sections'],pending_decisions=[],
 Greek_marker_additions=[1],Greek_marker_corrections=[],Greek_marker_moves=[],exact_Latin_byte_recovery=True,exact_Greek_byte_recovery=True,English_unchanged=True,full_narrative_partition=True,complete_final_extent=True,all_locators_independently_verified=True,full_local_reader_certified=True,production_registry_tested=True,
 qualified_correspondence_sections=[r['number'] for r in rows if r.get('reader_note') and r['correspondence_status']!='UNAVAILABLE'],source_preservation='COMPLETE_PARTITION_QA.json',reader_certificate='FULL_READER_QA.json',independent_English_context_certificate='ENGLISH_CONTEXT_READER_QA.json',protected_certificate=str(BATCH/f'PROTECTED_COMPLETE_EXISTING_BOOKS_BROWSER_QA_{build}.json'),
 published_baseline_selectable=3157,added_local_selectable_coverage=partition['expected_sections'],published_coverage_added=0,local_total_with_this_book=3157+partition['expected_sections'],canonical_merged=False,branch_pushed=False,preview_updated=False,built_production_files=reader['built_files'])
save(P/'CERTIFICATION.json',certificate)
with (P/'BOUNDARIES_REVIEW.tsv').open('w',encoding='utf8',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['section','Greek print','Latin review','placement','correspondence','editorial','paragraph','text/tail path','Unicode node offset','raw UTF8 byte','Greek text','Latin left context','Latin right context','reason','image'])
 for r in rows:
  loc=r.get('Latin_locator',{});w.writerow([r['number'],r['Greek_print_status'],r['Latin_review_status'],r['physical_placement_status'],r['correspondence_status'],r['editorial_status'],r.get('Latin_paragraph_id',''),loc.get('text_node_path',''),loc.get('node_offset',''),loc.get('raw_byte',''),r['Greek'],loc.get('left',''),loc.get('right',''),r.get('review_reason',''),r.get('print_observation',{}).get('image','')])
authority=(P/'SOURCE_AUTHORITY.md').read_text().split('Current status:')[0].replace('Remaining rows are explicitly unreviewed.','All relevant Niese narrative starts are now visually reviewed; individual observations and independent controls are recorded in the per-section register.')
authority+=f'Current status: all {partition["expected_sections"]} Greek starts visually reviewed and Latin candidates individually reviewed; {partition["nonempty_Latin_intervals"]} represented Latin intervals and unavailabilities {partition["unavailable_sections"]}; no pending decisions. Exact source recovery, complete partition, final extent and full local reader checks pass. See CERTIFICATION.json. Local identity data: `{ROOT}/assets/xml/antiquities/niese/book-{b:02}.json`.\n';(P/'SOURCE_AUTHORITY.md').write_text(authority,encoding='utf8',newline='\n')
report=f'''# Book {roman}: complete local certification

**Ready for coordinated integration.** Baseline `{PIN}`; isolated branch `{certificate['branch']}`; implementation parent `{certificate['implementation_parent_commit']}`. Actual worktree: `{ROOT}`. Canonical observed HEAD: `{canon}`; frozen inputs were not advanced.

All **{partition['expected_sections']}** printed Greek identities and Latin candidates were individually reviewed. Latin has **{partition['nonempty_Latin_intervals']} nonempty intervals**, **{partition['added_milestones']} added milestones**, **{partition['retained_starts']} retained starts** and verified unavailabilities **{partition['unavailable_sections']}**. No editorial decision remains pending. Unavailability concerns this transcription; its cause is unknown and no physical-loss or whole-tradition claim is made. Partial correspondence stays separate from physical placement confidence.

The only Greek citation edit adds implicit opening 1; no existing Greek marker was corrected or moved. Removing Latin milestones and reversing that Greek addition recovers the same frozen UTF-8/LF bytes exactly. All words, spelling, punctuation, whitespace, labels, apparatus, IDs, sameAs, paragraphs and traditional divisions are preserved. English is byte-identical. Independent DOM/raw-UTF8 locators, opening whitespace, all adjoining extents and the final narrative extent pass the complete partition check.

The actual local build `{site}` passed every selection using the production book registry, with no injected identity data: exact Latin and Greek intervals, independent frozen English contexts, unavailable Latin with Greek/English access, all chapter/subchapter ranges, deep links, previous/next, reload/history, pane controls, unique IDs and light/dark notes. Full range reconstruction preserves the complete narrative. Protected checks passed I–VIII/X, all 26 accepted VIII/X critical URLs and 23 protected routes including contents, traditional/Bamberg, Alignment, Whiston, Bellum/Lodge and other affected works. Browser exceptions, console errors and failed requests: zero. Inherited Book-I exceptions remain precisely bounded in the baseline records.

XV.40 uses the user's approved B locator before `seditiones domesticas pacando`; the complete `praeter legem exuit` removal statement remains in XV.39. Reciprocal notes disclose displaced correspondence and partial compression/reordering. Alternatives A and C remain rejected in decision history. The intervals through XV.41 were recomputed and reader-verified.

Published baseline: **3,157 selectable identities**. This book adds **{partition['expected_sections']} local selections**, giving **{3157+partition['expected_sections']} locally**, with **{partition['nonempty_Latin_intervals']} new nonempty Latin intervals**. Published added coverage: **0**. No canonical merge, push, preview update or deployment occurred. Later coordinated integration must reconcile against then-current canonical code.

Evidence: [certificate](CERTIFICATION.json), [boundary register](BOUNDARIES.json), [human review](BOUNDARIES_REVIEW.tsv), [source/partition checks](COMPLETE_PARTITION_QA.json), [reader QA](FULL_READER_QA.json), [English context checks](ENGLISH_CONTEXT_READER_QA.json), [source authority](SOURCE_AUTHORITY.md), [decisions](DECISION_HISTORY.json), [implementation](LATIN_IMPLEMENTATION.json), [exact file manifest](FILE_MANIFEST.json). Historical partial checkpoints are retained as history and are superseded by this complete certificate.
'''
if b!=15:report=report.replace(report[report.index('XV.40 uses'):report.index('Published baseline:')],'')
(P/'REPORT.md').write_text(report,encoding='utf8',newline='\n')
files=[dict(path=str(f),relative_path=f.relative_to(ROOT).as_posix(),bytes=f.stat().st_size,sha256=digest(f.read_bytes())) for f in sorted(P.rglob('*')) if f.is_file() and f.name!='FILE_MANIFEST.json']
save(P/'FILE_MANIFEST.json',dict(book=b,pinned_commit=PIN,files=files,manifest_excludes_itself=True,note='Image presence alone does not imply inspection; per-row observations record actual inspection.'))
print(roman,'READY_FOR_COORDINATED_INTEGRATION',certificate['selectable_identities'],certificate['nonempty_Latin_intervals'])
