"""Summarize executed gates honestly; an editorial hold is never a certificate."""
from prepare import *
def read(name):return json.loads((PACK/name).read_text(encoding='utf-8'))
def main():
    assert read('ADJUDICATION_HISTORY.json')==[dict(case=c,status='PENDING',choice=None,user_response=None,question_presented=True) for c in ['059','026_037','238','241']]
    evidence_names=['COMPLETE_PRINT_AUDIT.json','BASELINE_STRUCTURAL_BROWSER_COMPARISON.json','BASELINE_PROTECTED_BROWSER.json','FINAL_PROTECTED_BROWSER.json','BASELINE_OTHER_CONTROLS.json','FINAL_OTHER_CONTROLS.json','BOOKXX_BROWSER.json','BOOK_CLOSURE_BROWSER.json','VISIBLE_QUALIFICATIONS_BROWSER.json','BYTE_CERTIFICATION.json','GENERIC_END_BASELINE_REPRO.json','GENERIC_END_CANDIDATE_PROOF.json']
    assert all(read(name)['status']=='PASS' for name in evidence_names)
    assert len(read('FINAL_PROTECTED_BROWSER.json')['selections'])==5231
    assert len(read('BOOKXX_BROWSER.json')['selections'])==268
    production_commit='3bc395ad2bb3594364633e76f4daabaa137e6480';qa_commit='be1dda266bcb869e83d039df52e3e1d7c506e05f'
    files=['assets/js/renderTei.js','assets/xml/antiquities/Greek/book-20.xml','assets/xml/antiquities/Latin/book-20.xml','assets/xml/antiquities/niese/book-20.json']
    manifest={rel:info(ROOT/rel) for rel in files}
    assert git('diff','--name-only',production_commit,'--','assets','_includes','_layouts','_sass','_data').decode()==''
    save(PACK/'PRODUCTION_MANIFEST.json',dict(base=BASE,verified_production_commit=production_commit,files=manifest,protected_scope='PROTECTED_INPUTS.json',untouched_English_and_other_work_content=True,only_new_reader_capability='Generic per-language endTarget; narrow declaration of Book20 identity registry.'))
    certificate=dict(status='EDITORIAL_HOLD',certified=False,ready_for_coordinated_integration=False,base=BASE,branch='antiquities-niese-20',worktree=str(ROOT),runtime=str(RUNTIME),port=8920,verified_production_commit=production_commit,QA_evidence_commit=qa_commit,Greek_printed_identity_review='268/268 COMPLETE',individual_Latin_comparison='268/268 COMPLETE',routine_closed_Latin=251,editorial_cases_closed='0/4',pending_cases=['026_037','059','238','241'],pending_identities=[26,*range(27,37),37,58,59,238,240,241],counts=read('COVERAGE_GATE.json'),byte_recovery=read('BYTE_CERTIFICATION.json')['BookXX'],unchanged_English_BookXX_sha256=sha((PACK/'frozen-inputs/English.xml').read_bytes()),executed_gates={name:info(PACK/name) for name in evidence_names},previous_selectable_identities=5231,local_selectable_identities_including_editorial_holds=5499,new_public_release=False,known_baseline_exceptions=read('FINAL_OTHER_CONTROLS.json')['knownExceptions'],untouched_canonical_check='git status --porcelain returned empty after QA; canonical was not edited.',no_merge_push_or_publication=True,limitation='Four editorial decisions remain pending. Actual browser PASS includes17 explicit editorial holds and251 accepted Latin intervals; it is not a final scholarly certification.')
    save(PACK/'CERTIFICATE.json',certificate)
    handoff=dict(status='EDITORIAL_HOLD; NOT READY FOR INTEGRATION',branch='antiquities-niese-20',branch_ref='refs/heads/antiquities-niese-20',worktree=str(ROOT),runtime=str(RUNTIME),review=str(PACK),base=BASE,verified_production_commit=production_commit,QA_evidence_commit=qa_commit,authority_commits=['46f65f4413d30de31715fac8c6d22969d35f0a3e','5c32167c04eb51026e989e52eeb2ba983c9ebcb4'],certificate=str(PACK/'CERTIFICATE.json'),report=str(PACK/'REPORT.md'),pending_cases={case:dict(packet=str(PACK/f'CASE_{case}.md'),recommended='A',status='PENDING') for case in ['026_037','059','238','241']},resume_steps=['Record exact human choices and responses in ADJUDICATION_HISTORY.json; do not infer approval from elapsed time.','For closed accepted choices, execute prepare_accepted_patch.py. It reverses only documented routine insertions against the frozen bytes and applies the accepted map. A B decision withholding unavailability leaves a scholarly hold.','Verify bytes and complete final physical membership, then make a scoped source commit and build_candidate.py into a unique commit-named runtime. Existing executed routine build/evidence remains available.','Run bookxx_browser.cjs against FINAL_EXPECTED_INTERVALS.json and all containing/protected browser checks; reverify source opening, end, notices, contents and source bytes. Preserve the routine-stage evidence under distinct names before updating final receipts.','Only after all final gates and four decisions close, issue LOCALLY CERTIFIED / READY FOR COORDINATED INTEGRATION, make final scoped commits and verify a clean worktree. Stop before merge/push/publication.'],coordinator_reconciliation='Canonical advanced to08f46c0 during this audit with XI integration. Keep immutable65b source. Reconcile the two narrow reader hunks with later canonical by normal integration review; never overwrite its renderer with this snapshot. No XI or other concurrent unintegrated work is included.',production_files=files,publication_authorized=False)
    save(PACK/'LOCAL_HANDOFF.json',handoff)
    hashes=read('BYTE_CERTIFICATION.json')['BookXX']
    report=f'''# Antiquities XX — local editorial hold

**EDITORIAL HOLD. Full scholarly certification and integration readiness are withheld.** The printed Greek audit and individual Latin comparison are complete for all268 identities. Four editor questions remain unanswered, affecting17 Latin identities. All independent technical checks have completed.

The immutable source is `{BASE}`, the clean canonical head observed at entry. It differs from the published9527578 source only by the inherited Whiston provenance italics. Canonical later advanced to08f46c0; the successful direct remote observation is in CANONICAL_OBSERVATIONS.json. This branch remains on the frozen pre-XI baseline. BASELINE.json was captured after the later advance; its canonical_HEAD field is that later observation, not the chosen source commit. No concurrent unintegrated changes were copied.

The isolated branch is `antiquities-niese-20`, at `{ROOT}`. Its dedicated runtime is `{RUNTIME}`. The actual Jekyll candidate build and browser tests were run against the production content of `{production_commit}`. The main QA evidence commit is `{qa_commit}`. The branch tip additionally stores this handoff and its report; obtain its exact final hash from the branch ref. No merge, push, export, deployment or publication occurred.

| Reviewed or measured item | Actual result |
|---|---:|
| Printed Niese Greek identities |268/268 individually reviewed|
| Individual complete Greek/Latin comparisons |268/268 completed|
| Logical Greek/menu identities |268, exactly1–268|
| Current nonempty accepted Latin intervals |251|
| Current new Latin start milestones |251|
| Retained original Latin Niese starts |0|
| Temporary exclusive end anchors protecting unresolved adjacent material |3|
| Current pending Latin identities |17|
| Adjudicated independent-unavailability decisions |0|
| New explicit Greek opening label |1; original267 labels retained|
| Traditional Chapters / Subchapters |12 /50|
| Bamberg divisions / retained legacy positions |20 /20|
| Alignment units selectable in actual reader |51|

The pending identities are26–37,58–59,238 and240–241. `available:false` at this stage means **EDITORIAL_HOLD**, not an approved absence. All held source material remains byte-for-byte in Book, Alignment and chapter views. Secure25,57 and239 end before their unresolved neighbors, so those neighbors are not swallowed by another Niese selection.

The four focused packets preserve complete Greek extents, Niese image/page evidence, exact Latin nodes and byte/code-point coordinates, neighboring effects, alternatives and recommendations. CASE_026_037 recommends partial26/37, unavailable27–36 and separate preservation of the inherited bracketed annotation. CASE_059 recommends beginning59 at `habe inquit fiducia`, retaining the phrase and qualifying the Greek58 imperative overlap; the alternative begins at `inquit fiducia`. CASE_238 recommends explicit unavailability for Jonathan's appointment, with239's relative opening qualified. CASE_241 recommends beginning241 at `Is namque primus`; its alternative begins at `cum et pontificatum tenuisset et regnum`. Both preserve the inherited compressed Latin syntax. ADJUDICATION_HISTORY.json still records four pending decisions. If all four recommended alternatives are accepted, the provisional plan has257 Latin intervals and11 unavailable identities; those are not current certified counts.

Niese IV1890 title and BookXX printed276–320/PDF290–334 were physically inspected. Each identity is tied to the actual page image, its hash, XML marker, complete Greek section and individual Latin analysis. OCR was only a locating aid. The original marginal numeral is a line observation, not a word tag. §1 begins at `Τελευτήσαντος δὲ τοῦ βασιλέως Ἀγρίππα`, after the preserved41-code-point duration notice; its only Greek edit is `<num>[1]</num>`. No existing Greek label was moved, including the267 label at the preceding paragraph's end.

Loeb IX1965 title, all50 traditional lower divisions, all12 chapter openings and the final268 wording were independently inspected. Loeb Greek ends at printed532/PDF548, English at533/PDF549 before the separate Additional Note on XVIII343. The frozen20 Bamberg records, literal/supplied labels, images, relationships and complete original-source locators remain unchanged. The current external Word file differs from the frozen audit hash, although all20 BookXX image/book/numeral cells still match. The frozen v1.1 records retain precedence; this is documented in HUMAN_BAMBERG_AUTHORITY_BOOKXX.json, with no new facsimile claim.

The dense opening divisions and every required critical window were covered by the exhaustive268-selection comparison. Traditional ix begins197, x224, xi252 and xii259. Bamberg VI begins inside51, XI inside129, XVIIII at200 and XX at215; their physical points were not substituted for Niese or traditional starts. §§199–201 were reviewed normally with no textual/authenticity intervention. §§259–268 preserve all current wording and final punctuation. Latin266 has a qualified partial correspondence; its missing living-witness clause was not supplemented. The complete original Latin `tei-trailer` through AMEN remains visible after268 as paratext. Vita starts separately at Niese printed321/PDF335 and is wholly excluded; no269 identity exists.

| Executed browser gate | Result |
|---|---|
| All268 XX selections |268 exact full Greek intervals and preserved Whiston context;251 exact full Latin intervals;17 explicit holds; no duplicate DOM IDs|
| XX containing views |135 unchanged views: Book, contents,51 Alignment units and82 traditional/Bamberg records|
| Independent structural spans |82 complete ranges ×3 languages, all source anchor/offset checks and full browser text matches|
| Legacy positions and URLs |All20 legacy range extents unchanged; all20 chapter URL behaviors replayed|
| Prior Niese population |All5,231 actual baseline identities replayed individually with identical text, notes, paragraph IDs/sameAs and duplicate-ID state|
| Other works and source controls |35 route comparisons passed, including XV endpoint, XVI–XX Book controls, Whiston/Cardwell/Lodge, DEH and Contra Apionem|
| Navigation and presentation |24 critical direct/reload/next/previous/history cases; panes/themes; XIX→XX; visible notices and Whiston italic provenance passed|
| Generic end capability |Actual baseline synthetic reproduction includes source-only annotation; candidate honors registered exclusive end without changing the source|

The two allowed baseline defects were precisely reproduced: three inherited Book-I apparatus links with404 targets, and unsupported I.1's exact null-querySelector error with27 as the first supported identity. No new console, network or asset error was accepted. XI and unintegrated XVI–XIX Niese work are outside the frozen population. The current local menu total is5,499, including17 BookXX Latin holds; this is no public-release count. The original reader exposes individual Niese selection and complete containing ranges; its source contents intentionally carry no inferred navigation targets.

All299 protected production inputs were hash-compared. Greek/Latin edits independently reverse to the exact frozen full-file bytes. All wording, spelling, punctuation, whitespace, original IDs/sameAs, paragraph/container topology, notes, mixed markup, manuscript breaks/images, chapter markers and source paratext are protected. Every English file, structure.xml, display controls, CSS, unrelated XML and other works remain unchanged.

| Witness | Original and independently restored SHA-256 |
|---|---|
| Greek |`{hashes['Greek']['reversed']}`|
| Latin |`{hashes['Latin']['reversed']}`|
| English, unchanged |`{certificate['unchanged_English_BookXX_sha256']}`|

Exactly four production files differ: assets/xml/antiquities/Greek/book-20.xml, assets/xml/antiquities/Latin/book-20.xml, assets/xml/antiquities/niese/book-20.json and assets/js/renderTei.js. The reader change is a narrow BookXX registration and generic per-language endTarget capability, with no XX-specific range conditional. The full evidence and code are under this review directory. BOUNDARIES.csv/IDENTITIES.json contain the exhaustive register; LATIN_PHYSICAL_SOURCE_LEDGER.json separates physical order and source-only material; SECURE_INSERTIONS.json, BYTE_CERTIFICATION.json and PRODUCTION_MANIFEST.json document exact mutations and fidelity. CERTIFICATE.json explicitly withholds certification. LOCAL_HANDOFF.json gives the gated continuation and later coordinator reconciliation instructions.
'''
    for a,b in [('all268','all 268'),('affecting17','affecting 17'),('published9527578','published 9527578'),('to08f46c0','to 08f46c0'),('exactly1','exactly 1'),('original267','original 267'),('BookXX','Book XX'),('Secure25,57 and239','Secure §§25, 57 and 239'),('partial26/37','partial §§26/37'),('unavailable27–36','unavailable §§27–36'),('beginning59','beginning §59'),('Greek58','Greek §58'),('239\'s','§239\'s'),('beginning241','beginning §241'),('has257','has 257'),('and11','and 11'),('IV1890','IV (1890)'),('IX1965','IX (1965)'),('all50','all 50'),('all12','all 12'),('final268','final §268'),('printed532','printed 532'),('at533','at 533'),('frozen20','frozen 20'),('all20','all 20'),('begins197, x224, xi252 and xii259','begins at §197, x at §224, xi at §252 and xii at §259'),('inside51','inside §51'),('inside129','inside §129'),('at200','at §200'),('at215','at §215'),('Latin266','Latin §266'),('after268','after §268'),('printed321','printed 321'),('no269','no §269'),('268-selection','268-selection'),('context;251','context; 251'),('intervals;17','intervals; 17'),('contents,51','contents, 51'),('and82','and 82'),('ranges ×3','ranges × 3'),('All20','All 20'),('All5,231','All 5,231'),('including17','including 17'),('total is5,499','total is 5,499'),('All299','All 299')]:report=report.replace(a,b)
    (PACK/'REPORT.md').write_text(report,encoding='utf-8',newline='\n')
    print('Wrote honest editorial-HOLD certificate, report, scoped manifest and continuation handoff.')
if __name__=='__main__':main()
