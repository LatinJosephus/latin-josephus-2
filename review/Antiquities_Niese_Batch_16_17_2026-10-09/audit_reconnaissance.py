"""Independent reconnaissance integrity and frozen-structural-evidence checks.

No segmentation, source review or reader certification is inferred from these
checks. The generated status distinguishes pending editorial work explicitly.
"""
from pathlib import Path
import json,hashlib,subprocess,csv,re
from collections import Counter
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent
FROZEN=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review\Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    base=json.loads((P/'BASELINE.json').read_text());inventory=json.loads((P/'ALL_BASE_FILES.json').read_text())
    drift=[x['relative'] for x in inventory if sha((ROOT/x['relative']).read_bytes())!=x['sha256']]
    assert not drift,drift
    authority=[]
    manifest=FROZEN/'Antiquities_Structure_Reconciliation_v1.1_SHA256SUMS.txt'
    for line in manifest.read_text().splitlines():
        digest,name=line.split(None,1);path=FROZEN/name.strip();actual=sha(path.read_bytes());assert digest==actual,name
        authority.append(dict(file=name.strip(),sha256=actual,manifest_verified=True))
    assert len(authority)==8
    source_rows={}
    for f in FROZEN.glob('*.csv'):
        rows=list(csv.DictReader(f.open(encoding='utf-8-sig',newline='')))
        source_rows[f.name]=[x for x in rows if x['book'] in ['16','17']]
    save(P/'FROZEN_STRUCTURAL_ROWS.json',dict(source=str(FROZEN),authority_files=authority,rows=source_rows,
        note='Source-qualified structural records and per-language offsets; not automatic Niese start locators.'))
    books={}
    for b,roman in [(16,'XVI'),(17,'XVII')]:
        packet=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09';frozen=json.loads((packet/'BASELINE.json').read_text());checks=[]
        for lang,input in frozen['inputs'].items():
            raw=(packet/f'frozen-inputs/{lang}.xml').read_bytes();actual=(ROOT/input['relative']).read_bytes()
            blob=subprocess.check_output(['git','show',f"{base['base_commit']}:{input['relative']}"],cwd=ROOT)
            assert sha(raw)==input['sha256'] and raw==actual
            assert sha(blob)==input['git_blob_sha256']
            checks.append(dict(language=lang,working_tree_sha256=sha(actual),frozen_sha256=sha(raw),git_blob_sha256=sha(blob),
                exact_working_tree_preservation=True,working_tree_equals_git_blob=actual==blob,CRLF_to_LF_equals_git_blob=actual.replace(b'\r\n',b'\n')==blob))
        structural=json.loads((packet/'INHERITED_STRUCTURAL_RECORDS.json').read_text());c=Counter(x['values'].get('scheme','alignment-registry') for x in structural)
        rows=json.loads((packet/'BOUNDARIES.json').read_text());reviewed=[x['number'] for x in rows if x['Latin_review_status'].startswith('INDIVIDUALLY_REVIEWED')]
        routine=[x['number'] for x in rows if x['Latin_review_status']=='INDIVIDUALLY_REVIEWED']
        pending=[x['number'] for x in rows if x['editorial_status']=='PENDING_EDITOR_ADJUDICATION']
        unavailable=[x['number'] for x in rows if x['correspondence_status']=='ABSENT_IN_TRANSCRIPTION']
        special=[x for x in structural if x['values'].get('verification-status') not in ['CONFIRMED_NIESE_START',None] or x['values'].get('traditional-relationship')=='SAME_NIESE_DIFFERENT_POSITION']
        save(packet/'INHERITED_ANOMALY_INVENTORY.json',dict(structural_counts=dict(c),entries=special,
            note='All original statuses, raw associations, literal labels and independent locators are frozen unchanged. No Niese identity is certified by this inventory.'))
        books[str(b)]=dict(candidate_identities=len(rows),expected=frozen['machine_census']['expected'],inputs=checks,
            inherited_structural_counts=dict(c),individual_Latin_reviews_completed=reviewed,individual_Latin_reviews_remaining=len(rows)-len(reviewed),
            routine_present_starts=routine,pending_editorial_identities=pending,unavailable_identities=unavailable,
            production_implementation=False,source_byte_recovery_after_implementation='NOT_APPLICABLE_NO_SOURCE_EDITS',reader_certification=False)
    sources=json.loads((P/'PRINTED_SOURCES.json').read_text())
    for source in ['Niese','Loeb']:
        assert sha(Path(sources[source]['path']).read_bytes())==sources[source]['sha256']
    save(P/'RECONNAISSANCE_INTEGRITY.json',dict(status='PASS_RECONNAISSANCE_ONLY',base_commit=base['base_commit'],
        tracked_pinned_files_verified=len(inventory),production_drift=drift,frozen_structural_manifest_verified=authority,
        immutable_PDF_hashes_verified=True,books=books,prior_selectable_count=2456+sum(x['sections'] for x in base['prior_identity_registries'].values()),
        proposed_additions=759,proposed_total=5990,implemented_additions=0,full_book_certification=False))
    print('PASS: pinned tracked files',len(inventory),'frozen structural hashes 8; six XML inputs unchanged; no implementation or certification claim.')
if __name__=='__main__':main()
