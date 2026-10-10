from prepare import *
import sys
def main():
    history=PACK/'history/first-browser-attempt';history.mkdir(parents=True,exist_ok=True)
    for name in ['PROEM_BROWSER_QA.json','PROEM_DIFFERENCE.json','CANDIDATE_BUILD.json','BUILD_CONTEXT.json']:
        shutil.copyfile(PACK/name,history/name)
    changes=json.loads((PACK/'READER_PATCH.json').read_text())
    changes.append(dict(old='      pane.childNodes.forEach(node => {',new='      [...pane.childNodes].forEach(node => {'))
    save(PACK/'READER_PATCH.json',changes)
    save(PACK/'QA_REPAIR_HISTORY.json',dict(cause='The existing live NodeList clearing loop skips a following node when it removes its predecessor. The added terminal transition paragraph exposed this during 25/26 navigation.',observed='The first complete 26-menu replay passed; direct/reload/history failed after §26→25→26 because the previous Latin view remained, causing duplicate paragraph IDs and incorrect extent.',repair='Snapshot pane children before removal; one generic line. No source or boundary changes.',initial_evidence='history/first-browser-attempt',resolution='Full Proem and complete protected identity/range suite must be rerun on the corrected committed build.'))
    print('Retained failed attempt and one-line reader repair evidence')
if __name__=='__main__':main()
