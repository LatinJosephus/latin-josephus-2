"""Certify the actual identity set, completed suites and exact integration scope."""
from pathlib import Path
import json,hashlib,subprocess,sys,datetime
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
A=ROOT/'review/Antiquities_Niese_BookXI_2026-10-09'
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT).decode().strip()
def main():
 names=['READER_XI_RESULTS.json','READER_FINAL_PRIOR_RESULTS.json','READER_CONTAINING_RESULTS.json','READER_EXTRA_RESULTS.json']
 reports=[load(D/n) for n in names]
 for r in reports:assert r['result']=='PASS' and not r.get('errors') and not r.get('failure')
 xi,prior,containing,extra=reports
 assert len(xi['selectors'])==347 and xi['menu']==list(range(1,348))
 assert len(xi['ranges'])==9 and len(xi['containing'])==120 and len(xi['navigation'])==22
 assert xi['view_switches']=='PASS' and xi['identity_order_and_false105']=='PASS'
 assert len(containing['rows'])==61 and len(extra['rank_challenges'])==4 and len(extra['uninstrumented'])==6 and len(extra['baseline_exceptions'])==2
 assert prior['prior_identity_count']==5231 and len(prior['selectors'])==5231 and len(prior['books'])==21
 assert len(prior['cross_works'])==21 and prior['Lodge_Whiston_switching']=='PASS'
 assert sum(r['niese'] for r in prior['cross_works'])==8002 and sum(r['ranges'] for r in prior['cross_works'])==1630
 totals={k:sum(r[k] for r in prior['books']) for k in ['traditional','bamberg','alignment']}
 assert totals==dict(traditional=1689,bamberg=198,alignment=1441),totals
 keys={(str(r['book']),r['n']) for r in prior['selectors']};assert len(keys)==5231 and not any(b=='11' for b,n in keys)
 new={('11',n) for n in xi['menu']};assert len(new)==347 and not keys.intersection(new)
 combined=keys|new;assert len(combined)==5578
 census=[]
 for book in ['preface',*[str(n) for n in range(1,21)]]:
  numbers=sorted(n for b,n in combined if b==book)
  census.append(dict(book=book,selectable_numbers=numbers,count=len(numbers),baseline_count=len([1 for b,n in keys if b==book])))
 save('IDENTITY_CENSUS.json',dict(result='PASS',baseline=5231,XI=347,combined=5578,actual_set_verified=True,books=census))
 registry=load(ROOT/'assets/xml/antiquities/niese/book-11.json')
 assert [r['number'] for r in registry['sections']]==list(range(1,348))
 spans=[s for r in registry['sections'] for s in r['Latin']['spans']]
 sources=[s for s in spans if s.get('role')=='interpolation'];primary=[s for s in spans if s.get('role')!='interpolation']
 assert len(primary)==352 and len(sources)==2 and len({s['occurrence'] for s in sources})==2
 assert len({s['occurrence'] for s in spans})==354
 for n in [312,326,342]:
  r=next(r for r in registry['sections'] if r['number']==n)
  assert sorted(s['continuationRank'] for s in r['Latin']['spans'] if s.get('role')!='interpolation')==[1,2]
 assert not any(s.get('role')=='interpolation' for n in [311,342] for s in next(r for r in registry['sections'] if r['number']==n)['Latin']['spans'])
 proof=load(D/'SOURCE_PROOF.json');preserved=load(D/'INTEGRATION_PRESERVATION.json');build=load(D/'BUILD_RECEIPT.json')
 assert proof['status']=='PASS' and preserved['result']=='PASS' and build['status']=='PASS'
 assert proof['Latin_inverse_byte_recovery'] and proof['Greek_inverse_byte_recovery'] and proof['English_byte_identical']
 assert len(load(A/'AUTHORIZED_ADDITIONS.json'))==270 and proof['counts']['added_end_markers']==0
 manifest=load(D/'BUILD_INPUT_MANIFEST.json')
 for f in manifest:assert sha((ROOT/f['relative']).read_bytes())==f['sha256'],f['relative']
 adaptations=load(D/'QA_ADAPTATIONS.json')
 for a in adaptations:
  a['integration_sha256']=sha((D/a['name']).read_bytes())
  if a['name']=='qa-common.cjs' and 'Fresh attempt-02' not in a['changes']:a['changes']+=' Fresh attempt-02 profiles after documented network suspension.'
 save('QA_ADAPTATIONS.json',adaptations)
 start=load(D/'BASELINE.json');scope=load(D/'INCOMING_SCOPE.json')
 certification=dict(result='PASS',certified_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),canonical_start=start['canonical'],direct_remote_start=start['direct_remote'],source_tip=start['source_tip'],tested_production_commit=build['production_commit'],source_commits=scope['complete_source_commits'],manual_conflict_resolutions=[],editorial_decisions='ALL CLOSED; source decisions and qualifications unchanged',counts=dict(logical_XI_identities=347,primary_Latin_fragments=352,interpolation_occurrences=2,added_Latin_start_markers=270,added_end_markers=0,prior_selectable=5231,combined_selectable=5578),reader_checks=dict(XI_selections=347,prior_selections=5231,XI_ranges=9,XI_containing_routes=120,independent_XI_traditional_populations=61,direct_reload_history_previous_next=22,Antiquities_containing=totals,cross_work_configurations=21,cross_work_citations=8002,cross_work_ranges=1630,rank_challenges=4,uninstrumented=6,protected_controls=len(prior['focused']),themes_and_panes='PASS',source_controls='PASS',Bellum_Whiston_Lodge_Apion_DEH='PASS',new_errors=0,allowed_baseline_exceptions=extra['baseline_exceptions']),source_preservation=dict(Latin_inverse_byte_recovery=True,Greek_English_unchanged=True,physical_occurrences=354,independent_locators=True,unrelated_baseline_files=3162,incoming_review_bytes_unchanged=88,production_bytes_match_certified_source=True),build=load(D/'BUILD_CONTEXT.json'),evidence=[dict(relative=str(p.relative_to(ROOT)).replace('\\','/'),sha256=sha(p.read_bytes())) for p in [*[D/n for n in names],D/'SOURCE_PROOF.json',D/'INTEGRATION_PRESERVATION.json',D/'PRODUCTION_MANIFEST.json',D/'BUILD_RECEIPT.json',D/'IDENTITY_CENSUS.json',D/'QA_ADAPTATIONS.json',D/'ATTEMPT_HISTORY.json']],public_preview_publication=False)
 certification['review_only_build_proof_commit']='ff1bdabab1213aaef0878f019340d1986978eb16'
 certification['inspected_theme_images']=[dict(theme=v['theme'],path=v['file'],sha256=sha(Path(v['file']).read_bytes()),inspection='Both interpolations remain separately labelled, beside their portions; notice, narrative and parallel panes are readable.') for v in extra['visuals']]
 save('CERTIFICATION.json',certification)
 report=f'''# Antiquities XI canonical integration

The complete certified XI source history is integrated and the fresh combined reader passes certification. Initial canonical and directly checked remote were `{start['canonical']}`. The certified source remains `{start['source_tip']}` on `antiquities-niese-11`, frozen from the same baseline. All nine source commits are ancestors of the isolated integration branch. The history includes provenance checkpoint `624ac80e5b7ed191d7a53ee5a0a6d706f9678fb9`, production merge `{build['production_commit']}` and review-only build/source proof `ff1bdabab1213aaef0878f019340d1986978eb16`. No conflict or manual production resolution was necessary; all accepted editorial decisions and qualifications remain exact.

Integration branch/worktree: `antiquities-niese-11-integration`, `C:\\workspace\\LatinJosephus-antiquities-niese-11-integration`. Disposable runtime: `C:\\workspace\\Antiquities-Niese-11-integration-runtime-20261009`. Full candidate and baseline builds are under `build`; final browsers use separate `attempt-02` profiles. Actual loopback origins appear in the result records. Test servers and browser contexts close normally.

Actual coverage is **5,578 selectable identities**, independently censused as 5,231 prior plus all 347 XI selections. XI has **352 primary Latin fragments**, **two separately identified Bellum IV.105 occurrences**, **270 added start markers**, **zero added end markers**, and zero Greek or English narrative edits. Fragment and marker counts are separate from logical identities. Removing only authorized Latin additions exactly recovers the pinned input bytes. All original and recomputed text/tail, Unicode and raw-byte locators pass independent checks. The physical narrative ledger reconstructs 354 occurrences, including both insertions and boundary whitespace, without loss or overlap. All 3,162 unrelated integration-start files and all 88 incoming source-review files remain exact.

XI.312 assembles 312a then 312b with BJ IV.105a immediately before 312a and BJ IV.105b immediately before 312b. Both remain visibly and structurally identified as interpolated Latin Bellum; neither creates an Antiquities identity. XI.311 and XI.342 exclude them independently. Combined selections include each physical occurrence once. XI.326 assembles 326a then 326b despite reversed physical placement; XI.342 assembles 342a then 342b without sweeping intervening text. XI.72's three reviewed portions also retain continuation order. Book and Alignment preserve Bamberg/XML order; traditional VIII.2, .4, .6 and Chapter VIII retain their accepted two/two/two/four Latin spans and independent parallel-language cuts, explanation, canonical-order heading and Book link.

The actual built reader passes all **347 XI selections** and all **5,231 prior selections**, with complete pane content and exact endpoints, identity inventory, qualifications and duplicate-ID checks. XI passes nine ranges (68–74, 311–313, 325–327, 341–343, 310–314, 325–329, 340–347, 302–347 and 1–347), 120 containing routes, 61 independent traditional populations and 22 direct/reload/history/previous-next controls. Pane/source switches, structural/witness/Niese transitions and both themes pass. Four reversed-declaration/duplicate-request challenges prove continuation and attachment order; six uninstrumented selections confirm the actual reader without the test bridge.

Protected checks cover 21 Antiquities contexts: 1,689 traditional selections, 198 Bamberg selections, 1,441 Alignment units and contents. A further 21 cross-work/source configurations cover 8,002 citations and 1,630 ranges. IX/XII/XIII/XIV/XV qualifications, VIII.367/369, X.108, the canonical boundary-label correction, current Whiston provenance italics, XV inherited chapter endpoints, Bellum IV.105 in Whiston/Lodge, Lodge notes/reload/source switching, Apion and DEH remain protected. Only the precisely reproduced inherited Book-I apparatus links (three links, two 404 targets) and unsupported I.1 error remain; supported I.27 passes. There is no new reader failure. Attempt 01 was interrupted by overnight local network suspension and is retained in ATTEMPT_HISTORY.json; complete fresh-profile reruns establish certification.

Exact incoming scope is four production files and 88 source-review files. Production: `assets/css/tei.css`, `assets/js/renderTei.js`, `assets/xml/antiquities/Latin/book-11.xml`, and `assets/xml/antiquities/niese/book-11.json`. The integration review packet is separate. Production bytes and Git blobs match the certified source; no transcription was moved, reserialized or normalized. Build inputs were frozen before two full Jekyll builds using the pinned Ruby image; 243 static output checks pass with no post-build replacement or registry injection. Existing source-authority, printed-page evidence, decisions and full fragment registers are referenced in the unchanged incoming XI packet instead of duplicated.

Promotion uses a fresh clean canonical/local/direct-remote gate, then fast-forward and normal push only. Final integration/canonical/remote hashes, remote production-file hash verification, source preservation and clean states are recorded after promotion in `C:\\workspace\\Antiquities-Niese-11-integration-runtime-20261009\\PROMOTION_RECEIPT.json`. FILE_MANIFEST.json and PRODUCTION_MANIFEST.json identify the exact committed scope; CERTIFICATION.json binds the successful evidence. The original XI source worktree remains preserved at its certified tip. No XVI–XIX source branch/worktree/runtime is changed. No preview export, publication, preview push, deployment or domain change occurs.
'''
 (D/'REPORT.md').write_text(report,encoding='utf8',newline='\n')
 rows=[]
 for p in sorted(D.rglob('*')):
  if p.is_file() and p.name!='FILE_MANIFEST.json':rows.append(dict(relative=str(p.relative_to(ROOT)).replace('\\','/'),role='integration review',bytes=p.stat().st_size,sha256=sha(p.read_bytes())))
 for p in load(D/'PRODUCTION_MANIFEST.json'):rows.append(dict(relative=p['relative'],role='production',bytes=(ROOT/p['relative']).stat().st_size,sha256=p['working_sha256'],git_blob_oid=p['git_blob_oid']))
 save('FILE_MANIFEST.json',dict(canonical_start=start['canonical'],source_tip=start['source_tip'],tested_production_commit=build['production_commit'],self_hash_excluded=True,integration_review_files=len(rows)-4,incoming_review_files=88,files=rows))
 print(json.dumps(dict(result='PASS',combined=len(combined),XI=347,prior=5231,review_manifest=len(rows)-4)))
if __name__=='__main__':main()
