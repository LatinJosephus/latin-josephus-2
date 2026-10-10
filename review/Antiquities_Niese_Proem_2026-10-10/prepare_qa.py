from prepare import *
def main():
    old=ROOT/'review/Antiquities_Niese_Integration_20_2026-10-10'
    provenance=[]
    for name in ['browser_common.cjs','protected_browser.cjs','qa-common18.cjs','reader-structure-crosswork.cjs','reader-xi.cjs']:
        src=old/name;s=src.read_text(encoding='utf-8')
        s=s.replace('Antiquities-Niese-20-integration-runtime-20261010','Antiquities-Niese-Proem-runtime-20261010')
        s=s.replace('8921','8920').replace('003ac796021890dde4b3d8ff152100f386280b3c',BASE)
        if name=='browser_common.cjs':
            s=s.replace("server.listen(8920,'127.0.0.1',r)","server.listen(mode==='baseline'?8922:8920,'127.0.0.1',r)")
            s=s.replace("'http://127.0.0.1:8920/'+work","'http://127.0.0.1:'+server.address().port+'/'+work")
        if name=='protected_browser.cjs':s=s.replace('7082','7350')
        if name=='reader-structure-crosswork.cjs':
            start=s.index('if(Number(book)===20){');end=s.index('return c.outerHTML',start)
            s=s[:start]+'''if(book==='preface'){c.querySelectorAll('tei-milestone[unit="niese"],tei-milestone[unit="niese-end"]').forEach(m=>m.remove())}'''+s[end:]
            s=s.replace('7082','7350').replace('combined_identity_target=7350','combined_identity_target=7376')
        (PACK/name).write_text(s,encoding='utf-8',newline='\n')
        provenance.append(dict(source=info(src),adapter=info(PACK/name),changes='Local runtime/port/base; prior population 7350; Proem containing views reverse only inserted segmentation markers'))
    shutil.copyfile(old/'STRUCTURAL_CONTROLS.json',PACK/'STRUCTURAL_CONTROLS.json')
    save(PACK/'QA_HARNESS_PROVENANCE.json',provenance)
    b=json.loads((PACK/'BASELINE_BUILD.json').read_text());c=json.loads((PACK/'CANDIDATE_BUILD.json').read_text())
    save(PACK/'BUILD_CONTEXT.json',dict(baseline_commit=BASE,commit=c['source_commit'],baseline_site=b['site'],site=c['site'],root=str(ROOT)))
    print('Prepared protected 7350-selector suite and existing exhaustive structure/cross-work suite')
if __name__=='__main__':main()
