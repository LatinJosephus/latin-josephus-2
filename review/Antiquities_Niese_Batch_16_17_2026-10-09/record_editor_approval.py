"""Record the direct user's explicit all-B adjudication; retain rejected alternatives."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
TEXT='''I have now reviewed the full EDITORIAL_HOLD.txt summary.
I confirm approval of all four B recommendations. These four editorial decisions are closed.
1. XVI.294–295 — B: Assign each identity its two corresponding Latin fragments, ordered by their physical occurrence in the witness. Preserve and document the incomplete relative construction and the repeated Obadas death statement. Do not infer the cause of the displacement.
2. XVI.351/355/356 — B: Display both surviving 351 fragments: the earlier material beginning perissent and the displaced continuation beginning hac oratione ... quanti arabum. End 355 before that later prefix. Begin 356 at the existing chapter anchor before XVIIII Herodi (recorded Latin offset 95). Preserve the traditional/Bamberg boundary unchanged. Record the displaced correspondence explicitly.
3. XVII.24–25 — B: Begin 25 at Euocabat ergo eum. Retain the complete grant/name clause, including cui balatha nomen erat and its caedere compromisit continuation, in 24. Include reciprocal notices explaining that the name corresponding to Greek 25 already survives in Latin 24. Do not describe it as missing.
4. XVII.75–76 — B: Retain the entire shared burning imperative, including epistolamque antipatri and its governing conbure, in 75. Begin 76 at Ego autem plurimum. Include reciprocal notices explaining the earlier-surviving correspondence. Preserve the transmitted punctuation and attribution despite differences between Niese and Loeb.
These approvals concern the precise boundaries and representation policies described in the decision packets. Preserve the complete source text, physical order, IDs, existing divisions and rejected alternatives in the scholarly record.
Proceed with implementation and complete independent certification of both books under the governing prompt. All 759 Niese identities must pass the new-selection tests, alongside required protected regressions and byte-exact recovery.
No further approval is required for these four questions. Do not merge, push or publish; return the clean, locally certified XVI–XVII branch and final handoff.
'''
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    record=dict(status='ALL_FOUR_EDITORIAL_DECISIONS_CLOSED_APPROVED_B',authority='DIRECT_HUMAN_USER_MESSAGE',
        user_message_date='2026-10-10',transcription_note='Formatting normalized; substantive wording retained.',
        approval_text=TEXT,approval_sha256=hashlib.sha256(TEXT.encode()).hexdigest(),
        approvals={'XVI.294–295':'B','XVI.351/355/356':'B','XVII.24–25':'B','XVII.75–76':'B'},
        no_further_approval_required=True,no_merge_push_publish=True)
    save(BATCH/'EDITOR_ADJUDICATION_ALL_B.json',record)
    for roman,files in [('XVI',['DECISION_XVI_294_295.json','DECISION_XVI_351_355_356.json']),
                        ('XVII',['DECISION_XVII_024_025.json','DECISION_XVII_075_076.json'])]:
        p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
        history=read(p/'DECISION_HISTORY.json')
        for filename in files:
            decision=read(p/filename)
            decision.setdefault('historical_pre_adjudication_status',decision['status'])
            decision.update(status='CLOSED_EDITOR_APPROVED_B_NOT_YET_CERTIFIED',implementation_approved=True,
                editor_adjudication=dict(alternative='B',authority='DIRECT_HUMAN_USER_MESSAGE',date='2026-10-10',
                    approval_record='../Antiquities_Niese_Batch_16_17_2026-10-09/EDITOR_ADJUDICATION_ALL_B.json',
                    approval_sha256=record['approval_sha256']),certified=False)
            save(p/filename,decision)
            if not any(x.get('kind')=='EDITOR_ADJUDICATION' and x.get('packet')==filename for x in history):
                history.append(dict(kind='EDITOR_ADJUDICATION',packet=filename,selected='B',rejected_alternatives_retained=True,
                    authority='DIRECT_HUMAN_USER_MESSAGE',date='2026-10-10',implemented=False,reader_certified=False))
        save(p/'DECISION_HISTORY.json',history)
    print('Recorded four direct user B approvals; all rejected alternatives retained; implementation/certification still separate.')
if __name__=='__main__':main()
