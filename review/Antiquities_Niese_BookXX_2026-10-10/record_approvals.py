"""Record the editor's actual attached decisions and preserve the preceding hold."""
from prepare import *

def main():
    attachment=Path(r'C:\Users\Pollard_R\.codex\attachments\c187293b-5a71-4166-a294-a8e43918cecb\Pasted text.txt')
    response=attachment.read_bytes().decode('utf-8')
    assert '**Approve A for all four cases.**' in response
    history=json.loads((PACK/'ADJUDICATION_HISTORY.json').read_text(encoding='utf-8'))
    assert len(history)==4 and all(h['status']=='PENDING' for h in history)
    archive=PACK/'history'/'EDITORIAL_HOLD_402ddb34b141'
    archive.mkdir(parents=True,exist_ok=False)
    names=['ADJUDICATION_HISTORY.json','CERTIFICATE.json','REPORT.md','LOCAL_HANDOFF.json','COVERAGE_GATE.json','BYTE_CERTIFICATION.json','CANDIDATE_BUILD.json','PRODUCTION_MANIFEST.json','BOOKXX_BROWSER.json','FINAL_PROTECTED_BROWSER.json','FINAL_OTHER_CONTROLS.json','VISIBLE_QUALIFICATIONS_BROWSER.json','BOOK_CLOSURE_BROWSER.json','GENERIC_END_CANDIDATE_PROOF.json']
    archived={}
    for name in names:
        shutil.copyfile(PACK/name,archive/name)
        archived[name]=info(archive/name)
    copy=PACK/'EDITORIAL_ADJUDICATION_2026-10-10.txt'
    shutil.copyfile(attachment,copy)
    for h in history:
        prior=dict(h)
        h.update(status='APPROVED',choice='A',user_response=response,
                 response_source=info(copy),original_attachment=info(attachment),
                 prior_status='PENDING / EDITORIAL_HOLD',previous_record=prior,
                 previous_hold_commit='402ddb34b141bc33bffb8e0e0c570b6f48dc0174',
                 evidence_packet=f"CASE_{h['case']}.json",
                 rejected_alternatives_retained_in=f"CASE_{h['case']}.md",
                 cause_of_absence='Undetermined; no physical-loss or translation-omission inference.',
                 approval_scope='Final editorial choice A; final implementation and independent certification authorized.')
    save(PACK/'ADJUDICATION_HISTORY.json',history)
    save(archive/'ARCHIVE_MANIFEST.json',dict(previous_commit='402ddb34b141bc33bffb8e0e0c570b6f48dc0174',files=archived,immutable_previous_status='EDITORIAL_HOLD',original_candidate_coordinates_and_rejected_alternatives='Retained unchanged in CASE_*.json/md and in the Git history.'))
    print('All four actual editorial decisions recorded; original response bytes and previous HOLD evidence retained.')

if __name__=='__main__':main()
