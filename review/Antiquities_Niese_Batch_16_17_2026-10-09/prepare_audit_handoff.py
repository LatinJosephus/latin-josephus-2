"""Prepare a source-audit handoff and review-only file manifest, not certificates."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
FOLDERS=[ROOT/'review'/f'Antiquities_Niese_{name}_2026-10-09' for name in ['BookXVI','BookXVII','Batch_16_17']]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def write(p,s):p.write_text(s,encoding='utf8',newline='\n')

def main():
    base=read(BATCH/'BASELINE.json');integrity=read(BATCH/'RECONNAISSANCE_INTEGRITY.json')
    source=read(BATCH/'INDEPENDENT_SOURCE_AUDIT_CHECK.json');partition=read(BATCH/'INDEPENDENT_RECOMMENDED_PARTITION_CHECK.json')
    reader=read(BATCH/'BASELINE_READER_CAPTURE.json')
    assert not integrity['production_drift'] and reader['status']=='PASS_BASELINE_ONLY'
    assert not source['batch_certified'] and source['implemented_new_identities']==0
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()==base['branch']
    for b,roman in [(16,'XVI'),(17,'XVII')]:
        p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
        audit=read(p/'COMPLETE_PRIMARY_SOURCE_AUDIT.json');check=source['books'][str(b)]
        report=[f'ANTIQUITIES {roman} — COMPLETE SOURCE AUDIT; EDITORIAL HOLD',
            'This is not a production implementation or independent book certificate.','',
            f"Immutable canonical/origin source at isolation: {base['base_commit']}.",
            f"Branch: {base['branch']}; worktree: {base['worktree']}.",
            f"Runtime: {base['runtime']}; baseline reader port: {base['port']}.",
            'Earlier audit checkpoint: c963c94. Final audit commit is identified in the accompanying handoff.',
            'No merge, push, publication, deployment or other-worker modification.','',
            f"Printed Niese IV narrative pages {audit['printed_Niese_pages']['printed'][0]}–{audit['printed_Niese_pages']['printed'][-1]} / PDF{audit['printed_Niese_pages']['pdf'][0]}–{audit['printed_Niese_pages']['pdf'][-1]} all visually inspected.",
            f"All {audit['identity_count']} Greek intervals and individual Latin correspondences reviewed.",
            f"Complete Latin narrative paragraphs read: {audit['complete_narrative_Latin_paragraphs_read']}.",
            f"Routine present starts adopted, not applied: {audit['routine_present_starts']}.",
            f"Unavailable in this transcription: {audit['unavailable_identities']}.",
            f"Pending editorial starts: {audit['pending_editorial_identities']}.",
            f"Explicitly qualified present correspondences: {audit['qualified_present_identities']}.",
            'Causes of omission/displacement/variation remain undetermined; no philological corrections.','',
            f"Existing structural records preserved: {integrity['books'][str(b)]['inherited_structural_counts']}.",
            'New start milestones: 0; extra endpoint/other anchors: 0; new registered identities: 0.',
            f"Recommended B model only: {partition['books'][str(b)]['logical_present_identities']} logical Latin identities / {partition['books'][str(b)]['physical_fragments']} physical fragments.",
            'Recommended model physical coverage passed; it remains unapproved and unapplied.','',
            f"Independent Greek raw-byte/lxml coordinates checked: {check['Greek_raw_byte_and_independent_lxml_coordinates_checked']}.",
            f"Independent routine Latin raw-byte/lxml coordinates checked: {check['routine_Latin_raw_byte_and_independent_lxml_coordinates_checked']}.",
            f"Exceptional retained source coordinates checked: {check['retained_exceptional_coordinates_checked']}.",
            'Exact current source preservation:']
        for x in check['source_preservation']:
            report.append(f"  {x['language']}: SHA256 {x['sha256']}; {x['bytes']} bytes; {x['existing_xml_ids']} existing XML IDs; CRLF {x['CRLF']}, LF {x['LF']}.")
        r=reader['books'][str(b)]
        report.extend(['Source recovery after reversing edits: not applicable; sources have not been edited.',
            f"Actual baseline browser capture: {r['all_view_count']} containing/whole/contents views and {len(r['legacy_chapter_ranges'])} legacy chapter outputs.",
            'New Niese selection browser QA: 0; independent book certification: NOT ISSUED.','',
            'Executed source-audit checks: audit_reconnaissance.py; audit_completed_review.py;',
            'audit_recommended_partition.py; mixed_mapper.py fixture checks.',
            'Baseline build/capture: build-baseline.sh; capture-baseline-reader.cjs.',
            'Evidence and exact locators: BOUNDARIES.json; COMPLETE_PRIMARY_SOURCE_AUDIT.json;',
            'INDEPENDENT_SOURCE_AUDIT_CHECK.json; PROTECTED_STRUCTURAL_COORDINATES.json;',
            'RECOMMENDED_PHYSICAL_PARTITION_PENDING_EDITOR.json; per-book decision packets.',
            'Batch file paths and hashes: ../Antiquities_Niese_Batch_16_17_2026-10-09/REVIEW_FILE_MANIFEST.json.','',
            'After adjudication, implementation, actual registry/byte-recovery proof and required',
            'new/prior-reader suites remain necessary. Not ready for coordinated integration.',''])
        write(p/'SOURCE_AUDIT_HANDOFF.txt','\n'.join(report))
    write(BATCH/'BATCH_HANDOFF.txt','\n'.join([
        'ANTIQUITIES XVI–XVII — SOURCE AUDIT COMPLETE; BOTH BOOKS ON EDITORIAL HOLD',
        'No implementation or independent book/batch certification is claimed.','',
        f"Immutable base: {base['base_commit']} (canonical and live origin verified at isolation).",
        f"Owned branch/worktree: {base['branch']} / {base['worktree']}.",
        f"Owned runtime: {base['runtime']}.",
        'All 759 printed identities, Greek intervals and individual Latin correspondences reviewed.',
        'XVI: 376 routine starts; 24 unavailable; four starts await two representation decisions.',
        'XVII: 352 routine starts; none unavailable; three starts await two cut decisions.',
        'All four B recommendations are concrete in EDITORIAL_HOLD.txt and the four packets.',
        'The governing section5 expressly gates disputed implementation on adjudication.',
        'No editor answer received. Both books therefore have genuine outstanding gates.','',
        'Independent checks: 3,165 pinned files unchanged; eight frozen reconciliation hashes;',
        'six XML inputs unchanged; 759 Greek and 728 routine Latin coordinates; 36 exceptional',
        'structural source coordinates; proposed narrative coverage exactly once in witness order.',
        'Actual baseline browser: 311 containing/whole/contents views plus 35 legacy outputs.',
        'BookXVII inherited annotation DOM-ID repetitions are captured, not silently repaired.',
        'Candidate browser: not run; all 759 new selections and necessary regressions remain.','',
        'Production changes: NONE. All additions/modifications are in these three assigned',
        'review folders. REVIEW_FILE_MANIFEST.json lists exact evidence paths and SHA256.',
        'Earlier local checkpoint c963c94; final audit checkpoint is given in the response.',
        'Git cleanliness is checked after the local audit commit; no certificate inferred.',
        'Canonical, other workers, English/Whiston, prior Niese registries, traditional/Bamberg,',
        'other works and shared reader retain their pinned bytes. No merge/push/publish/deploy.',
        'Current selectable count 5,231; proposed eventual local total 5,990 after certification.',
        'Not ready for coordinated canonical integration.','',
        'Resume only after editorial answers, then follow RENDERER_APPLICATION_PLAN_PENDING_EDITOR.txt.',
        'Run minimal implementation, exact byte reversal, independent actual registry ranges,',
        'candidate build and all-759 browser suite. Generic range changes also require all',
        '5,231 protected selections. Issue separate book certificates only after checks pass.','']))
    entries=[]
    manifest=BATCH/'REVIEW_FILE_MANIFEST.json'
    for folder in FOLDERS:
        for file in sorted(folder.rglob('*')):
            if file.is_file() and file!=manifest:
                raw=file.read_bytes();entries.append(dict(path=file.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=sha(raw)))
    save(manifest,dict(status='SOURCE_AUDIT_EVIDENCE_ONLY_NO_IMPLEMENTATION_CERTIFICATE',
        base_commit=base['base_commit'],folders=[p.relative_to(ROOT).as_posix() for p in FOLDERS],
        files=entries,manifest_excludes_itself=True,production_changed_paths=[],implemented_new_identities=0))
    assert all(sha((ROOT/x['path']).read_bytes())==x['sha256'] for x in entries)
    print('Source-audit handoff and manifest:',len(entries),'review files; production changed paths 0; no certificates.')

if __name__=='__main__':main()
