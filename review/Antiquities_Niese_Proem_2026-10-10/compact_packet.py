from prepare import *
def main():
    # Keep only pages used for this Proem audit. Earlier checkpoint retains the locating attempt.
    keep={'NIESE':[7,*range(94,100)],'LOEB':[7,*range(26,39,2)]}
    for label,pages in keep.items():
        p=PACK/(label+'_PAGE_TEXT.json');rows=json.loads(p.read_text(encoding='utf-8'));save(p,[r for r in rows if r['PDF_page'] in pages])
    used={f'{label.title()}-PDF{n:03}.jpg' for label,pages in keep.items() for n in pages}
    removed=[]
    for p in (PACK/'evidence').glob('*.jpg'):
        assert p.resolve().is_relative_to((PACK/'evidence').resolve())
        if p.name not in used:removed.append(info(p));p.unlink()
    save(PACK/'PRINT_IMAGES.json',[dict(PDF_page=int(p.stem[-3:]),**info(p)) for p in sorted((PACK/'evidence').glob('*.jpg'))])
    save(PACK/'PACKET_SCOPE_CLEANUP.json',dict(reason='Remove unused locating-page renders and OCR beyond the scoped Proem; original source-review checkpoint 3c4fe98 retains the search history',removed=removed))
    # Failed harness runs are retained separately, and final results are at the packet root.
    save(PACK/'HARNESS_NOTES.json',dict(status='RESOLVED',attempts=[dict(file='BASELINE_BUILD_SANDBOX_ATTEMPT.json',cause='Sandbox denied the installed Ruby runtime (0xC0000022); authorized disposable build retried outside sandbox, success.'),dict(file='CANDIDATE_BUILD_SANDBOX_ATTEMPT.json',cause='Same runtime restriction; successful local retry.'),dict(file='history/first-browser-attempt/STRUCTURAL_HARNESS_INITIAL_RESULT.json',cause='Contents-fallback comparison did not remove newly authorized Proem markers; added the same explicit marker reversal already used for whole/structural views. No production change.'),dict(file='history/first-browser-attempt/PROEM_HARNESS_CONTROL_MODE_RESULT.json',cause='After returning to whole Proem, test tried the hidden Niese selector without first choosing Niese mode; corrected to use actual visible control. No production change.')],production_repair='QA_REPAIR_HISTORY.json; one-line pane child snapshot; corrected committed build rerun in full'))
    rows=json.loads((PACK/'DECISION_REGISTER.json').read_text(encoding='utf-8'))
    import csv
    with (PACK/'BOUNDARIES.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['Niese','Greek printed start','Niese printed p','Niese PDF p','Loeb printed p','Loeb PDF p','Latin start','Latin enclosing id','Latin confidence','English context','Editorial status'])
        for r in rows:w.writerow([r['number'],r['Greek_start_phrase'],r['Niese']['printed_page'],r['Niese']['PDF_page'],r['Loeb']['printed_page'],r['Loeb']['PDF_page'],r['Latin_start']['right'][:110],r['Latin_start']['xml_id'],r['Latin_cut_confidence'],r['English_context_target'],r['editorial_status']])
    print('Scoped packet compacted; 26-row summary and full evidence retained')
if __name__=='__main__':main()
