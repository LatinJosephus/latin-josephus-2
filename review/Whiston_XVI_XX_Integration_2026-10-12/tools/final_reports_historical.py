import pathlib,json,hashlib,subprocess,csv,shutil,datetime,re
BASE=pathlib.Path(__file__).parent;ROOT=BASE/'candidate';PACK=ROOT/'review/Whiston_XVI_XX_Integration_2026-10-12';PIN='f6fa17f7616bf9ce046c28086b1a1448a9f8d049';CANON=pathlib.Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda b:hashlib.sha256(b).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def file_sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
section_files=['CUMULATIVE_A_ENGLISH_QA.json','CUMULATIVE_B_ENGLISH_QA.json','CUMULATIVE_C_ENGLISH_QA.json','NEW_XVI_XX_ENGLISH_QA.json'];actual=[]
for name in section_files:
 report=load(PACK/name);assert report['status']=='SECTIONS-PASS' and not report['errors'] and not report['requests'];assert report['rendererSHA256']==sha((ROOT/'assets/js/renderTei.js').read_bytes())
 actual+=report['sections']
assert len(actual)==len(set((r['book'],r['number']) for r in actual))==7376
assert all(r['passed'] and r['settledStateAndURLVerified'] and r['navigationLimitsVerified'] and r['expectedSHA256']==r['renderedSHA256'] for r in actual)
required=['STRUCTURAL_QA.json','REGRESSION_QA.json','BAMBERG_QA.json','SPECIAL_QA.json','UI_QA.json','BOOK_NAVIGATION_QA.json','AUXILIARY_QA.json','NATIVE_LODGE_BROWSER_QA.json','IMPLEMENTATION_REVIEW.json','SOURCE_ARCHIVE_VERIFICATION.json','STANDARD_BUILD_RUNTIME_BINDING.json']
for name in required:assert load(PACK/name)['status']=='PASS',name
aux=load(PACK/'AUXILIARY_QA.json')
assert len(aux['wholeMarkup'])==21 and all(r['passed'] and r['allSourceAnchorsAndInlineMarkupPreserved'] for r in aux['wholeMarkup'])
assert len(aux['markup'])==41 and all(r['passed'] for r in aux['markup'])
assert any(r['book']=='16' and r['number']==355 and r['elements']==0 for r in aux['markup'])
save(PACK/'METHOD_CORRECTIONS.json',dict(status='PASS',initial_failure_preserved=['INITIAL_AUXILIARY_QA.json','INITIAL_AUXILIARY_MARKUP_FAILURE.json','INITIAL_MARKUP_ORACLE.json'],finding='The first markup fixture assigned the empty Bamberg anchor before XVI.356 to the preceding interval solely by physical milestone order. The existing renderer prunes its empty exclusive-end paragraph after removing inherited citation labels.',resolution='Independent XML start/end/text-event expectations qualify that one empty endpoint shell. All 21 whole-book source anchor/linebreak/emphasis populations and 41 meaningful or explicitly empty selected markup cases are now mandatory and pass.',qualification='EMPTY_ENDPOINT_MARKUP_QUALIFICATION.json',source_and_renderer_unchanged=True,guards_removed_or_disabled=False,retest='AUXILIARY_QA.json: PASS'))
save(PACK/'VISUAL_INSPECTION.json',dict(status='PASS',images=['evidence/book-20-1440-light.png','evidence/book-16-375-dark.png'],observations='Desktop three-witness layout and mobile stacked witness layout are legible; exact English is visible and no redundant exact-English notice appears.',scope='Supplementary visual inspection; exhaustive text and state evidence is in the browser reports.'))
structural=load(PACK/'STRUCTURAL_QA.json');assert structural['counts']==load(PACK/'STRUCTURAL_ORACLE.json')['counts']
assert len(structural['views'])==len(load(PACK/'STRUCTURAL_ORACLE.json')['rows']) and len(load(PACK/'BAMBERG_QA.json')['views'])==structural['counts']['bamberg']
native=load(BASE/'runtime/native-bellum/corpus-qa.json');assert native['status']=='PASS' and not native['relevant_errors']
shutil.copy2(BASE/'runtime/native-bellum/corpus-qa.json',PACK/'NATIVE_BELLUM_BROWSER_QA.json')
shutil.copy2(BASE/'runtime/native-bellum/reproduction.json',PACK/'NATIVE_BELLUM_HISTORICAL_REPRODUCTIONS.json')
masterlog=(PACK/'execution-logs/lodge-master-negative.log').read_text(encoding='utf-8-sig');assert 'FAIL' not in masterlog and 'PASS' in masterlog
guard=load(BASE/'runtime/reader-corpus-guard.json');assert guard['status']=='PASS' and len(guard['negative_tests'])==8
build=dict(status='PASS',full_configured_plugins=True,bundle_check='PASS',standard_build_seconds=float(re.search(r'done in ([\d.]+) seconds',(BASE/'runtime/standard-build.log').read_text(encoding='utf-8-sig')).group(1)),production_corpus_guard=guard,native_Bellum_counts={k:native[k] for k in ['greek','whiston','lodge']},native_Lodge='PASS; complete actual built-page, source/history/keyboard and accepted baseline digest',Lodge_master_and_corruption_guards='PASS; immutable master SHA and nine corruption tests',limitations='Chromium only; unchanged offline HTMLCollection iteration adapter and separately logged external CDN shell failures in native legacy tests')
save(PACK/'BUILD_AND_GUARDS.json',build)
keys=['book','number','nextPhysical','expectedSHA256','renderedSHA256','notes','inline','allNarrativeVisible','GreekLatinPresentationUnchanged','settledStateAndURLVerified','navigationLimitsVerified','URL']
with (PACK/'CUMULATIVE_ENGLISH_QA.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows([{k:r.get(k) for k in keys} for r in actual])
save(PACK/'CUMULATIVE_ENGLISH_QA.json',dict(status='PASS',intervals=7376,previous_I_XV=5604,new_XVI_XX=1772,missing=[],duplicate=[],source='Independent Python frozen-XML projection compared with actual live reader text; original Stage C 1772 observations retained at identical final source/renderer state',reports=section_files,notes=sum(r['notes'] for r in actual),inline_elements=sum(r['inline'] for r in actual),all_actual_URL_and_settled_states_verified=True,all_actual_navigation_limits_verified=True,all_Greek_Latin_section_presentations_unchanged=True))
save(PACK/'NEW_XVI_XX_SECTION_MATRIX.json',[r for r in actual if r['book']!='preface' and int(r['book'])>=16])
oracle=load(PACK/'INTERVAL_ORACLE.json');save(PACK/'ENGLISH_PHYSICAL_ORDER_QA.json',dict(status='PASS',books={b:[r['number'] for r in oracle if r['book']==b] for b in dict.fromkeys(r['book'] for r in oracle)},XI_order='1–311,326–342,312–325,343–347; independently verified in fresh XML traversal',Proem_26_and_narrative_320_distinct=True))
archives=[]
for stage in ['A','B','C']:
 r=load(BASE/f'exports/Stage-{stage}.verification.json');o=load(BASE/f'exports/Stage-{stage}.offline-recovery.json');assert o['status']=='PASS' and file_sha(pathlib.Path(r['archive']))==r['SHA256']
 books={'A':[16,17],'B':[18,19],'C':[20]}[stage];incremental=sum(x['expected_count'] for x in load(PACK/'SOURCE_INVENTORY.json') if x['book'] in books)
 archives.append(dict(**r,offline_recovery='PASS',books_added_this_stage=books,intervals_added_this_stage=incremental,cumulative_enabled_intervals=o['source_and_display_reconciliation']['independent_XML_intervals']))
save(PACK/'STAGE_RECOVERY_REGISTER.json',archives)
head=subprocess.check_output(['git','--no-optional-locks','-C',str(CANON),'rev-parse','HEAD']).decode().strip();dirty=subprocess.check_output(['git','--no-optional-locks','-C',str(CANON),'status','--porcelain=v1']).decode();assert head==PIN and not dirty,'Canonical changed; fresh isolated reconciliation required'
save(PACK/'CANONICAL_COMPATIBILITY.json',dict(status='PASS',initial_certified_HEAD=PIN,final_observed_HEAD=head,canonical_clean=True,canonical_advance=False,automatic_rebase=False,observed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),remote_preview_not_a_source_authority=True))
receipt=dict(last_book=20,complete_cumulative=True,section_reports=section_files,structural_report='STRUCTURAL_QA.json',required_reports=required+['BUILD_AND_GUARDS.json','CANONICAL_COMPATIBILITY.json']);save(PACK/'QA_RECEIPT.json',receipt)
verification=json.loads(subprocess.check_output(['python',str(PACK/'tools/verify_candidate.py')]));assert verification['status']=='PASS' and verification['actual_display_intervals_reconciled']==7376;save(PACK/'FINAL_SOURCE_PRESERVATION.json',verification)
certificate=dict(verdict='WHISTON XVI–XX CANONICAL-INTEGRATION-READY',canonical_baseline=PIN,new_exact_English_intervals=1772,cumulative_exact_English_intervals=7376,complete_Niese_identity_set=True,frozen_source_bytes_preserved=True,I_XV_unchanged=True,Greek_Latin_unchanged=True,containing_views=structural['counts'],mandatory_regressions='PASS',standard_build_and_approved_guards='PASS',three_independent_stage_recoveries='PASS',canonical_compatibility='PASS',merge_push_deployment_authorized=False,scope='Isolated integration candidate only; inherited scholarly qualifications retained without new segmentation decisions');save(PACK/'INTEGRATION_CERTIFICATE.json',certificate)
report=f'''WHISTON XVI–XX CANONICAL-INTEGRATION-READY
Isolated final integration candidate — 2026-10-12, America/Toronto

All 7,376 / 7,376 Whiston English Niese selections pass exact normalized displayed-text comparison with expectations independently extracted from the frozen certified XML. The new XVI–XX population is 1,772; previously integrated Proem/I–XV is 5,604. All selections have settled state, URL and navigation-limit checks. Complete identity sets and actual English physical order are verified, including the 26-section Proem, Book IX restoration and Book XI transposition.

Canonical baseline: {PIN}. Canonical still matches this identity and is clean; no fresh reconciliation or rebase was required. Candidate and stage commit identities are in the external DELIVERY.json and STAGE_RECOVERY_REGISTER.json. No canonical merge, push, public-preview change or deployment was performed.

Sources and implementation
SOURCE_INVENTORY.json records the five full delivery identities, certified physical SHA-256, immutable Git-object hashes, recovery ZIP hashes and qualifications. SOURCE_ARCHIVE_VERIFICATION.json verifies every checksum member and CRC of the five original ZIPs. All five production XML files equal their corpus-certified frozen bytes; all I–XV files remain byte-identical. Greek/Latin XML, Niese/structural registries, all existing tests and unrelated tracked files remain unchanged. Removing only introduced milestones reconstructs all five approved original byte streams exactly. Recorded Git LF versus physical CRLF differences are preserved as proven representation qualifications, never as text-normalization authority.

The renderer change is one existing exactNieseBooks activation list. Complete production manifest source entries and its literal guard digest are updated; no guard assertion, plugin or renderer mechanism is removed. IMPLEMENTATION_REVIEW.json records the narrow review. The full and production-only binary diffs are supplied beside the final bundle.

Containing views and navigation
Independent XML/registry expectations verify {structural['counts']['book']} whole-book, {structural['counts']['chapter']} traditional chapter, {structural['counts']['subchapter']} subchapter, {structural['counts']['bamberg']} Bamberg and {structural['counts']['alignment']} alignment views: {len(structural['views'])} actual settled views. Counts come from the current registries and actual canonical paragraph menus. The established containing, native book-change, history, direct-link, Previous/Next and light/dark/mobile regressions also pass. All source narrative is visible. English notes and all six inline emphasis runs are preserved; inherited quotations and callouts remain verbatim.

Special protections
The first auxiliary markup fixture failed at XVI.355 because it assigned an empty exclusive-end paragraph anchor to the visible interval. METHOD_CORRECTIONS.json and the preserved initial failure explain the XML ownership correction. A stronger independent event-based markup oracle now requires all 21 whole-book anchor/linebreak/emphasis populations and 41 selected cases, including the deliberately empty XVI.355 shell. All pass; source bytes and renderer behavior were unchanged, and no guard was removed or disabled.

All 24 XVI identities without Latin counterparts display exact English and preserve genuine witness notices. XVII.299 retains distinct traditional/Bamberg/Niese starts and corrected terminal numbering. XVIII.215–218 retain witness-specific Latin availability; XVIII.257 retains its distinct divisions. XIX.363 and XIX.364 display separate exact intervals; XIX.292's traditional/Bamberg divisions remain intact. XX.267 retains its additional wording and A.D. 03; XX.268 retains three books and the complete last sentence. XX.269 is rejected without substitute narrative. Separate Latin trailer, paratext and Vita/work boundaries are unchanged. SPECIAL_QA.json preserves actual notice/availability and boundary results. The redundant exact-English notice is absent throughout.

Cross-work and guards
The complete native Bellum Greek, Whiston and Lodge range populations pass: {json.dumps(native['greek'])} per recorded witness population. Native Lodge's complete rendered baseline digest, source/history/keyboard behavior, immutable master comparison and all nine corruption guards pass. Contra Apionem, DEH, full DEH concordance and all Antiquities Greek/Latin display comparisons pass. AUXILIARY_QA.json, REGRESSION_QA.json and native reports retain detailed results.

Standard full-plugin build passes in {build['standard_build_seconds']} seconds; bundle check and exact production corpus guard pass. All 143 production XML files parse; all 38 frozen publication authorities match literally; all eight approved negative tests pass. Existing native offline HTMLCollection iteration support and external CDN shell failures are separately recorded. Certification covers the tested Chromium reader and the isolated candidate, with all inherited scholarly qualifications; it does not certify hosted publication or additional browser engines.

Recovery
Stages A, B and C each have a full Git bundle, verified archive/member checksums, binary diff, QA, source inventory and successful fresh independent checkout/reconciliation. They remain unchanged. The final ZIP includes all three stage archives and receipts, all five original source recovery ZIPs, the Lodge master, complete candidate history, literal built preview, source/corpus evidence and portable verification/reproduction tools. Final ZIP SHA-256, manifest and fresh offline-recovery receipt are outside the committed dossier to avoid self-reference. Follow RECOVERY.md and RECOVERY_FINAL.md in an empty owned directory. Rollback is to abandon the isolated candidate or restore the pinned baseline into a new private checkout; never alter a shared checkout.

STOP. Separate authorization is required for canonical integration or publication.
'''
(PACK/'GLOBAL_INTEGRATION_REPORT.txt').write_text(report,encoding='utf-8')
shutil.copy2(__file__,PACK/'tools/final_reports_historical.py')
print(json.dumps(certificate));print('Final reports and independent 7,376-source/display reconciliation PASS')
