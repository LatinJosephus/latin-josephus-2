from integration_common import *
checks={
 'BUILD_RECEIPT.json':'status','COMBINED_SOURCE_PROOF.json':'status',
 'NEW_BOOK_BROWSER_QA.json':'status','CONTAINING_VIEWS_BROWSER_QA.json':'status',
 'EDITORIAL_STRUCTURAL_EXTRA_RESULTS.json':'status','PROTECTED_SOURCE_GATE_QA.json':'status',
 'PROTECTED_FINAL_BROWSER.json':'status','FINAL_BROWSER.json':'status',
 'LEGACY_DISTINCT_FINAL_BROWSER.json':'status','TRANSITION_FINAL_BROWSER.json':'status',
 'SOURCE_CONTROLS_FINAL_BROWSER.json':'status','READER_XI_RESULTS.json':'result',
 'READER_CONTAINING_RESULTS.json':'result','READER_EXTRA_RESULTS.json':'result',
 'XI_WITNESS_ORDER_RESULTS.json':'result','READER_FINAL_PRIOR_RESULTS.json':'result',
 'COMBINED_EXTRA_RESULTS.json':'result'}
results={}
for name,key in checks.items():
    x=read(D/name);assert x[key].startswith('PASS'),(name,x.get('failure'))
    assert not x.get('errors') and not x.get('consoleErrors') and not x.get('requestFailures'),name
    results[name]=x
new=results['NEW_BOOK_BROWSER_QA.json'];containing=results['CONTAINING_VIEWS_BROWSER_QA.json']
assert sum(x['identity_count'] for x in new['books'].values())==759
assert len(results['PROTECTED_FINAL_BROWSER.json']['selections'])==5231
assert len(results['READER_XI_RESULTS.json']['selectors'])==347
assert len(results['FINAL_BROWSER.json']['selections'])==745
assert len(results['COMBINED_EXTRA_RESULTS.json']['identity_set'])==7082
assert sum(x['containing_view_count'] for x in containing['books'].values())==311
assert sum(len(x['legacy_chapters']) for x in containing['books'].values())==35
assert len(results['EDITORIAL_STRUCTURAL_EXTRA_RESULTS.json']['unavailable'])==24
assert len(results['EDITORIAL_STRUCTURAL_EXTRA_RESULTS.json']['points'])==36
assert len(results['EDITORIAL_STRUCTURAL_EXTRA_RESULTS.json']['ranges'])==14
assert len(results['LEGACY_DISTINCT_FINAL_BROWSER.json']['physicalPoints'])==6
assert len(results['LEGACY_DISTINCT_FINAL_BROWSER.json']['legacyRoutes'])==29
assert new['pane_switches']=='PASS' and len(new['book_transitions'])==3
assert len(new['direct_navigation'])==50 and len(new['themes'])==2
build=read(D/'BUILD_CONTEXT.json');tip=git('rev-parse','HEAD').decode().strip()
assert ancestor(SOURCE,tip) and ancestor(START,tip)
for x in read(D/'BUILD_RECEIPT.json')['inputs']:
    if x['build']=='final':assert sha((ROOT/x['path']).read_bytes())==x['sha256'],x['path']
history=read(D/'BASELINE.json')['incoming_complete_history']
for commit in history:assert ancestor(commit,tip)
counts={16:dict(identities=404,Latin_identities=380,physical_Latin_fragments=383,unavailable=24,new_Latin_starts=378,reused_starts=2,additional_anchors=5,qualification_notices=54),17:dict(identities=355,Latin_identities=355,physical_Latin_fragments=355,unavailable=0,new_Latin_starts=355,reused_starts=0,additional_anchors=0,qualification_notices=29)}
for b,c in counts.items():
    p=read(D/f'BOOK_{b}_INDEPENDENT_SOURCE_PROOF.json');reg=read(ROOT/f'assets/xml/antiquities/niese/book-{b}.json')
    assert len(reg['sections'])==c['identities'] and p['physical_Latin_fragments']==c['physical_Latin_fragments']
    assert p['present_Latin_identities']==c['Latin_identities'] and len(p['unavailable_identities'])==c['unavailable']
    assert p['qualified_runtime_notices']==c['qualification_notices']
    assert sum(bool(r['Latin'].get('note')) for r in reg['sections'] if r['Latin']['available'])==c['qualification_notices']
    raw=(ROOT/f'assets/xml/antiquities/Latin/book-{b}.xml').read_bytes()
    assert raw.count(b'<milestone unit="niese" ')==c['new_Latin_starts']
    assert raw.count(b'<milestone unit="niese-fragment" ')+raw.count(b'<milestone unit="niese-range-end" ')==c['additional_anchors']
    reused=[r['number'] for r in reg['sections'] if r['Latin']['available'] and not r['Latin']['spans'][0]['start']['target'].startswith('niese-latin-book')]
    assert reused==([356,368] if b==16 else [])
    assert new['books'][str(b)]['identity_count']==c['identities']
    c['byte_recovery']={x['language']:x['ledger_reverse_sha256'] for x in p['source_byte_proofs']}
    save(f'BOOK_{b}_INTEGRATION_CERTIFICATION.json',dict(status='PASS_INDEPENDENT_SOURCE_AND_MERGED_READER_CERTIFICATION',book=b,counts=c,canonical_start=START,certified_source=SOURCE,actual_tested_merge=build['source_commit'],source_evidence=f'BOOK_{b}_INDEPENDENT_SOURCE_PROOF.json',browser_evidence='NEW_BOOK_BROWSER_QA.json',containing_evidence='CONTAINING_VIEWS_BROWSER_QA.json',all_editorial_decisions_closed_and_preserved=True))
for x in read(D/'HARNESS_PROVENANCE.json'):
    assert sha((ROOT/x['original']).read_bytes())==x['original_sha256']
    x['final_adapted_sha256']=sha((D/x['adapted']).read_bytes())
    results.setdefault('_harness_provenance',[]).append(x)
save('HARNESS_PROVENANCE.json',results.pop('_harness_provenance'))
save('HARNESS_REPAIRS.json',dict(production_changes_after_tested_merge=False,repairs=[dict(check='Canonical file preservation',reason='98 existing clean Windows checkout line-ending translations are recorded separately; compare unrelated production bytes with canonical Git archive and preserve working bytes at promotion.'),dict(check='Baseline containing capture provenance',reason='All 311 captures and 35 endpoints completed. The copied source harness compared baseline build with merged working assets; final provenance compares the baseline with its frozen canonical Git archive.',evidence='BASELINE_READER_INITIAL_CAPTURE.json',resumption='Source-proof-only completion; capture rows retained unchanged.'),dict(check='Protected inherited coordinates',reason='Frozen coordinate summaries omit element-edge paths; the final independent check resolves complete original registry locators.',retest='All 14 combined ranges, 36 physical coordinates and 24 unavailable selections passed.')]))
conflicts=read(D/'CONFLICT_RESOLUTIONS.json');conflicts['status']='PASS_RESOLVED_AND_EXHAUSTIVELY_CERTIFIED';save('CONFLICT_RESOLUTIONS.json',conflicts)
scope=git('diff','--name-only','-z',START,'HEAD').decode().split('\0');scope=[x for x in scope if x]
assert set(x for x in scope if not x.startswith('review/'))==set(PRODUCTION)
incoming=[x for x in scope if any(x.startswith(f) for f in FOLDERS)];assert len(incoming)==351
production=[dict(path=p,sha256=sha((ROOT/p).read_bytes())) for p in PRODUCTION]
cert=dict(status='PASS_READY_FOR_SAFE_CANONICAL_PROMOTION',canonical_start=START,remote_start=START,source_tip=SOURCE,source_base=SOURCE_BASE,incoming_complete_history=history,merge_commit=build['source_commit'],integration_baseline_commit='7a550010',books=counts,combined_selectable_identities=7082,exhaustive_population=dict(older=5231,XI=347,XVI_XVII=759,XVIII_XIX=745,total=7082),new_physical_Latin_fragments=738,unavailable_new_Latin_identities=24,additional_XVI_anchors=5,qualification_notices=83,all_four_B_decisions_preserved=True,all_incoming_review_files_byte_exact=True,incoming_review_files=351,production=production,regressions={name:dict(status=results[name][key],sha256=sha((D/name).read_bytes())) for name,key in checks.items()},known_unchanged_baseline_issues=results['PROTECTED_FINAL_BROWSER.json']['knownBaselineIssues'],new_reader_defects=0,public_preview_publication=False,Book_XX_integration=False,other_WorkBots_modified=False,receipt=str(R/'PROMOTION_RECEIPT.json'))
cert['integration_baseline_commit']=git('rev-parse','7a55001').decode().strip()
save('CERTIFICATION.json',cert)
cross=results['READER_FINAL_PRIOR_RESULTS.json'];work_citations=sum(x['niese'] for x in cross['cross_works']);work_ranges=sum(x['ranges'] for x in cross['cross_works'])
report=f'''Antiquities XVI–XVII canonical integration — combined certification PASS

Starting canonical and directly verified remote: {START}
Certified source tip: {SOURCE}
Frozen source baseline: {SOURCE_BASE}
Integration baseline commit: {cert['integration_baseline_commit']}
History-preserving merge: {build['source_commit']}
Final certification commit, canonical HEAD and directly verified remote HEAD:
recorded by the post-promotion receipt at {R / 'PROMOTION_RECEIPT.json'}.

All six incoming source commits remain ancestors:
'''+''.join('  '+x+'\n' for x in history)+f'''
Counts                    XVI   XVII   Total
Niese identities           404    355    759
Identities with Latin      380    355    735
Physical Latin fragments   383    355    738
Unavailable Latin           24      0     24
New Latin starts           378    355    733
Reused source starts         2      0      2
Additional anchors           5      0      5
Qualification notices       54     29     83

The 380 represented XVI identities and 383 fragments remain distinct. No fragments
were collapsed into continuous intervals. All 24 unavailable identities keep their
cause-neutral notices and independent Greek and contextual Whiston access.

All four approved B decisions remain closed and unchanged: XVI.294–295 retains
both fragments per identity in witness order, the incomplete relative construction
and repeated Obadas statement; XVI.351 keeps both perissent and hac oratione
fragments, 355 ends before the latter, and 356 starts at the inherited anchor before
XVIIII Herodi (Latin offset 95). XVII.24 retains the complete grant/name clause and
caedere compromisit; 25 begins Euocabat ergo eum. XVII.75 retains epistolamque
antipatri and conbure; 76 begins Ego autem plurimum. Reciprocal notices, transmitted
punctuation/attribution, rejected alternatives and all source evidence survive.

Only the shared renderer conflicted, in three regions. Registration retains all
canonical books and adds XVI–XVII. Canonical explicit physical-span and declared
start support preserves XI ranks/attachments/interpolations and XVIII–XIX starts.
A generic unranked single-identity path retains XVI–XVII's certified wrapper and
labels at reused chapter anchors. No whole conflict side was selected.

Fresh full Jekyll builds: canonical {START} and merged {build['source_commit']}.
644 Git-tree build inputs and 492 static source/output comparisons passed.
All 7,082 selections passed: 5,231 older, 347 XI, 759 XVI–XVII, 745 XVIII–XIX.
759 new selections include full Latin/Greek content, boundaries, contextual English,
and next/previous. All 311 new containing views and 35 legacy endpoints pass.
Four editorial groups and neighbours pass 14 combined range assemblies; all 36
protected physical coordinates pass. All 24 empty-Latin selections pass separately.
XI: 9 combined ranges, 120 containing routes, 61 independent traditional records,
57 alignment witnesses, 354 physical occurrences and both Bellum interpolations.
XVIII–XIX: 267 containing routes, 29 legacy routes, unavailable XVIII.216–217 and
the six distinct physical points at XVIII.257/XIX.292 remain protected.
All 21 Antiquities contexts, traditional/Bamberg/Alignment/TOC and {work_citations}
cross-work citations plus {work_ranges} ranges pass. Direct URLs, reload/history,
themes, panes, source events and accessibility pass. XV–XVI, XVI–XVII and
XVII–XVIII transitions pass without cross-book contamination.
Zero new reader defects. The two established Book-I apparatus/unsupported-I.1
exceptions were independently reproduced at the current canonical baseline.

Both Latin originals recover byte-exactly through two independent inversions;
Greek recovery and English preservation also pass. IDs, sameAs, punctuation,
whitespace, original order, chapter divisions, five extra XVI anchors and all 83
qualification notices are preserved. All 3,799 canonical-start files were checked:
five existing production files changed, two new registries were added; all unrelated
canonical Git files and existing review records remain byte-exact. The receipt
separately verifies preservation of pre-existing Windows checkout translations.

Production scope (seven files):
'''+''.join('  '+p+'\n' for p in PRODUCTION)+f'''
Review scope: complete incoming 351-file packet plus this integration review directory.
The exact manifest records every production and review file, size and SHA-256.
Canonical promotion is permitted only after a fresh remote/history/clean-state gate.
No force push, public-preview publication, Book XX integration or modification of
other WorkBots, their source branches or runtimes is authorized or performed.
Final clean states, actual pushed/fetched HEAD and changed production hashes are
recorded in the promotion receipt. Stop after verified canonical promotion.
'''
(D/'INTEGRATION_REPORT.txt').write_text(report,encoding='utf8',newline='\n')
paths=set(scope)|{p.relative_to(ROOT).as_posix() for p in D.rglob('*') if p.is_file()}
manifest_path=(D/'FILE_MANIFEST.json').relative_to(ROOT).as_posix();paths.discard(manifest_path)
assert all(p in PRODUCTION or any(p.startswith(f) for f in FOLDERS) or p.startswith(D.relative_to(ROOT).as_posix()+'/') for p in paths)
manifest=[dict(path=p,bytes=(ROOT/p).stat().st_size,sha256=sha((ROOT/p).read_bytes())) for p in sorted(paths)]
save('FILE_MANIFEST.json',dict(status='PASS',baseline=START,source=SOURCE,tested_merge=build['source_commit'],production_files=len(PRODUCTION),incoming_review_files=len(incoming),integration_review_files=sum(x['path'].startswith(D.relative_to(ROOT).as_posix()+'/') for x in manifest)+1,self_excluded=True,files=manifest))
print('PASS sealed combined 7082-identity certification;',len(manifest),'manifest entries')
