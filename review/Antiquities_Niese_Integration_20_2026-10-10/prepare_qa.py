from integration_common import *
import difflib
def main():
    canonical=git('show',START+':assets/js/renderTei.js')
    incoming=git('show',SOURCE_TIP+':assets/js/renderTei.js')
    base=git('show',FROZEN+':assets/js/renderTei.js')
    old=b'    const end = entries[index + 1] || (terminal ? {node: terminal, kind: "end"} : null);'
    start=incoming.index(b'    // A source-qualified exclusive end')
    finish=incoming.index(b'    const book = start.node.closest',start)
    approved=incoming[start:finish].rstrip(b'\n')
    assert canonical.count(old)==1
    expected=canonical.replace(b'        19: "assets/xml/antiquities/niese/book-19.json"',b'        19: "assets/xml/antiquities/niese/book-19.json",\n        20: "assets/xml/antiquities/niese/book-20.json"').replace(old,approved)
    actual=(ROOT/'assets/js/renderTei.js').read_bytes()
    assert actual==expected,'Resolution differs from exact canonical plus the two authorized source changes'
    patch=''.join(difflib.unified_diff(canonical.decode().splitlines(True),actual.decode().splitlines(True),fromfile='canonical/renderTei.js',tofile='merged/renderTei.js'))
    (PACK/'renderer-comparison/resolved.patch').write_text(patch,encoding='utf-8',newline='\n')
    save(PACK/'CONFLICT_RESOLUTIONS.json',dict(status='PASS',conflicted_files=['assets/js/renderTei.js'],conflict='Adjacent identity-loader registrations 16–19 versus 20',resolution='Retain all canonical registrations 16–19 and append 20. The separate exclusive-end hunk merges after canonical fragment dispatch. No complete-file side selection.',canonical_sha256=sha(canonical),source_sha256=sha(incoming),resolved_sha256=sha(actual),exact_canonical_plus_two_source_hunks=True,XI_and_XVI_XIX_fragment_engine_byte_preserved=True))
    for name in ['browser_common.cjs','protected_browser.cjs','bookxx_browser.cjs','combined_cases_browser.cjs','protected_controls_browser.cjs','notice_visual_browser.cjs','closure_browser.cjs','prove_range_end.cjs']:
        raw=(SOURCE_PACK/name).read_text(encoding='utf-8').replace('Antiquities-Niese-20-runtime-20261010','Antiquities-Niese-20-integration-runtime-20261010').replace('8920','8921').replace(FROZEN,START)
        if name=='browser_common.cjs':
            raw=raw.replace("'tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable'","'tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable,.niese-source-passage-label'")
            raw=raw.replace("return {languages:","return {paneDOM:Object.fromEntries(['latin','greek','english'].map(l=>[l,document.querySelector('#'+l)?.innerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null])),languages:")
        if name=='protected_browser.cjs':
            raw=raw.replace('sourceIDs:a.sourceIDs};','sourceIDs:a.sourceIDs,paneDOM_sha256:sha(JSON.stringify(a.paneDOM))};')
            raw=raw.replace("if(r.errors.length)throw", "if(r.selections.length!==7082||r.views.length!==135)throw Error('Incomplete actual baseline population'); if(r.errors.length)throw")
        (PACK/name).write_text(raw,encoding='utf-8',newline='\n')
    for name in ['STRUCTURAL_CONTROLS.json','FINAL_EXPECTED_INTERVALS.json','COMBINED_EXPECTED_INTERVALS.json']:
        shutil.copyfile(SOURCE_PACK/name,PACK/name)
    shutil.copytree(SOURCE_PACK/'frozen-inputs',PACK/'frozen-inputs')
    (PACK/'evidence').mkdir(exist_ok=True)
    oldpack=ROOT/'review/Antiquities_Niese_Integration_16_17_2026-10-10'
    names=['qa-common18.cjs','qa-common16.cjs','reader-xi.cjs','xi-witness-order.cjs','reader-structure-crosswork.cjs','final_source_controls.cjs','final_legacy_distinct_reader.cjs','combined-extra.cjs','XI_WITNESS_EXPECTATION.json','DISTINCT_PHYSICAL_POINT_PROOF.json','BASELINE_CONTAINING_BROWSER.json']
    for name in names:
        raw=(oldpack/name).read_text(encoding='utf-8').replace('Antiquities-Niese-16-17-integration-runtime-20261010','Antiquities-Niese-20-integration-runtime-20261010')
        if name=='reader-structure-crosswork.cjs':
            a=raw.index('if(Number(book)===11)c.querySelectorAll');b=raw.index("return c.outerHTML",a)
            raw=raw[:a]+'''if(Number(book)===20){c.querySelectorAll('tei-milestone[unit="niese"],tei-anchor[id="niese-latin-book20-end26"]').forEach(m=>m.remove());c.querySelectorAll('tei-num').forEach(m=>{if(m.textContent==='[1]')m.remove()});}'''+raw[b:]
            raw=raw.replace('report.actual_selections_in_separate_fresh_replay=5231;report.combined_identity_target=7082;','report.actual_selections_in_separate_fresh_replay=7082;report.combined_identity_target=7350;')
        if name=='combined-extra.cjs':
            raw=raw.replace('7082','7350')
            raw=raw.replace("if(report.books.filter(b=>[20].includes(b.book)).some(b=>b.menu.length||!b.disabled))throw Error('Unintegrated book scope changed');","if(report.books.find(b=>b.book===20).menu.length!==268||report.books.find(b=>b.book===20).disabled)throw Error('Book XX combined support');")
        if name in ['final_source_controls.cjs','final_legacy_distinct_reader.cjs']:
            raw=raw.replace("require('./final_reader.cjs')","require('./qa-common18.cjs')")
        (PACK/name).write_text(raw,encoding='utf-8',newline='\n')
    save(PACK/'QA_HARNESS_PROVENANCE.json',dict(status='PREPARED',source_helpers='Copied from certified XX source packet and canonical XVI–XIX integration suites. Original packets untouched.',adaptations=['Isolated runtime and local port/profile','Current canonical baseline SHA','All 7082 prior live-DOM selections with complete pane DOM digest','All 7350 live menu/registry identity census','Containing-view comparison reverses only authorized XX presentation additions, leaving XI and XVI–XIX markup intact'],source_helpers_sha256={n:sha((SOURCE_PACK/n).read_bytes()) for n in ['browser_common.cjs','protected_browser.cjs','bookxx_browser.cjs']},original_integration_helpers_sha256={n:sha((oldpack/n).read_bytes()) for n in names}))
    print('PASS exact two-hunk renderer reconciliation; independent integration QA prepared')
if __name__=='__main__':main()
