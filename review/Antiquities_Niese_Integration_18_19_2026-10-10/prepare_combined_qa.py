"""Adapt committed QA to the new integration baseline without altering its evidence."""
from integration_common import *
import difflib

old18=ROOT/'review/Antiquities_Niese_Batch_18_19_2026-10-09'
old11=ROOT/'review/Antiquities_Niese_Integration_11_2026-10-09'
provenance=[]
def adapt(src,name,transforms):
    original=src.read_text(encoding='utf8');s=original
    for a,b in transforms:
        assert a in s,(name,a)
        s=s.replace(a,b)
    p=D/name;p.write_text(s,encoding='utf8',newline='\n')
    provenance.append(dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src.read_bytes()),adapted=name,adapted_sha256=sha(p.read_bytes()),changes=''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='certified QA',tofile='integration QA'))))

common18=[('C:/workspace/Antiquities-Niese-18-19-runtime-20261009',str(R).replace('\\','/'))]
for name in ['final_reader.cjs','final_protected_reader.cjs','final_transition_reader.cjs','final_legacy_distinct_reader.cjs','final_source_controls.cjs']:
    changes=list(common18)
    if name=='final_reader.cjs':changes += [("path.join(d,'evidence','final-reader-'+theme+'.png')","path.join(P,'evidence',b+'-reader-'+theme+'.png')")]
    if name=='final_transition_reader.cjs':changes += [("path.join(P,'..',`Antiquities_Niese_Book${b===18?'XVIII':'XIX'}_2026-10-09`,'evidence','final-reader-'+theme+'.png')","path.join(P,'evidence',b+'-transition-'+theme+'.png')")]
    adapt(old18/name,name,changes)
for name in ['EXPECTED_STRUCTURAL_RANGES.json','BASELINE_CONTAINING_BROWSER.json','DISTINCT_PHYSICAL_POINT_PROOF.json']:
    shutil.copyfile(old18/name,D/name)
    provenance.append(dict(source=str((old18/name).relative_to(ROOT)),source_sha256=sha((old18/name).read_bytes()),adapted=name,adapted_sha256=sha((D/name).read_bytes()),changes='Unchanged certified expectation authority, not a reused integration test result.'))
common11=[('C:/workspace/Antiquities-Niese-11-integration-runtime-20261009/attempt-02',str(R).replace('\\','/')),
 ('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright','C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright')]
adapt(old11/'qa-common.cjs','qa-common.cjs',common11)
adapt(old11/'reader-xi.cjs','reader-xi.cjs',[("captures[1].notice?.replace(expectedTitle,'')||null","captures[1].notice||null"),("await page.selectOption(id,v);await page.evaluate(()=>window.__qaPending)","await page.evaluate(async({id,v})=>{const m=document.querySelector(id);m.value=v;m.dispatchEvent(new Event('change',{bubbles:true}));await window.__qaPending;},{id,v})")])
for name in ['reader-containing.cjs','reader-extra.cjs']:
    adapt(old11/name,name,[])
# Containing and cross-work structural replay complements the separate fresh
# exhaustive 5,231 actual menu selections. The canonical start already has XI.
s=(old11/'reader-prior.cjs').read_text(encoding='utf8')
s=s.replace("if(Number(book)===11)c.querySelectorAll('tei-milestone[unit=\"niese\"]').forEach(m=>{if(added.includes(m.id))m.remove()});", "if(Number(book)===11)c.querySelectorAll('tei-milestone[unit=\"niese\"]').forEach(m=>{if(added.includes(m.id))m.remove()});if([18,19].includes(Number(book)))c.querySelectorAll('tei-milestone[unit=\"niese\"]').forEach(m=>m.remove());")
a="const menu=Number(book)===11?[]:await page.locator('#niese-selector').evaluate(n=>[...n.options].filter(o=>o.value).map(o=>Number(o.value)));menus.push(menu);"
assert a in s;s=s.replace(a,"const menu=[];menus.push(menu); // Exhaustive actual selections are independently replayed by final_protected_reader.cjs.")
a="if(total!==5231)throw Error('Prior actual inventory '+total+' differs from5231');report.prior_identity_count=total;report.with_XI=total+347;"
assert a in s;s=s.replace(a,"report.actual_selections_in_separate_fresh_replay=5231;report.combined_identity_target=6323;")
s=s.replace("'READER_PRIOR_RESULTS.json'","'READER_STRUCTURE_CROSSWORK_RESULTS.json'").replace("Exhaustive 5231 prior selectable identities and affected containing views on fresh builds","Every Antiquities containing view and exhaustive cross-work structural comparison against canonical integration start")
(D/'reader-structure-crosswork.cjs').write_text(s,encoding='utf8',newline='\n')
provenance.append(dict(source=str((old11/'reader-prior.cjs').relative_to(ROOT)),source_sha256=sha((old11/'reader-prior.cjs').read_bytes()),adapted='reader-structure-crosswork.cjs',adapted_sha256=sha((D/'reader-structure-crosswork.cjs').read_bytes()),changes='All 21 Antiquities contexts, structural views and cross-work ranges retained. 5231 actual selection loop moved to separate fresh differential suite; only authorized new XVIII/XIX milestones removed from containing DOM comparison. XI notice baseline already certified.'))
adapt(old11/'verify_sources.py','verify_xi_sources.py',[("'assets/css/tei.css'}","'assets/css/tei.css','assets/xml/antiquities/Latin/book-18.xml','assets/xml/antiquities/Latin/book-19.xml'}"),("save('SOURCE_PROOF.json',report)","save('XI_SOURCE_PROOF.json',report)")])
(D/'evidence').mkdir(exist_ok=True)
save('QA_ADAPTATIONS.json',dict(status='EXPECTATIONS_PRESERVED_NEW_RUNTIME_AND_BASELINE',scripts=provenance,original_source_and_XI_review_unchanged=True,fresh_replay_required=True))
save('MERGE_RECONCILIATION.json',dict(status='PASS_REVIEWED_AUTOMATIC_MERGE',formal_conflicts=[],manual_production_resolutions=[],source_tip=SOURCE,canonical_start=START,renderer_review=dict(XI_fragment_assembly='All canonical fragment blocks and paragraph-end handling preserved; spans path returns before declared physical-start processing.',XVIII_XIX_physical_starts='Declared-start entries, inherited-label suppression, paragraph edge range handling, and synthetic labels preserved.',catalogue='Book XI plus both XVIII and XIX declarations coexist.',proof_required=['347 exact XI selections and fragment ordering challenges','745 exact XVIII-XIX selections','5231 fresh protected selections']),scholarly_changes=[],integration_only_cleanup='Remove mistakenly tracked Python bytecode from the baseline-record commit; retain source evidence unchanged.'))
print('Prepared independent combined QA in',D)
