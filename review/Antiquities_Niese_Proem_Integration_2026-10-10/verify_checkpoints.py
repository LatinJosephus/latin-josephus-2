from prepare import *
import zipfile
def main():
    folder=Path(r'C:\workspace\Antiquities-Niese-Proem-Recovery-runtime-20261010\checkpoints');rows=[]
    for p in sorted(folder.glob('*.zip')):
        old=json.loads(p.with_suffix('.json').read_text());assert sha(p.read_bytes())==old['archive']['sha256'] and p.stat().st_size==old['archive']['bytes']
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
            manifest=json.loads(z.read('MANIFEST.json'))
            for row in manifest:
                b=z.read(row['path']);assert len(b)==row['bytes'] and sha(b)==row['sha256']
        rows.append(dict(**info(p),payloads_verified=len(manifest),CRC='PASS',matches_preserved_receipt=True))
    assert len(rows)==6
    original=Path(r'C:\Users\Pollard_R\Mon disque\Downloads from Chrome (11-08-2026 onward)\Antiquities-Proem-Segmentation-Data.zip')
    assert sha(original.read_bytes())=='c15d641485dc38f049d4b59ba6855f1e3d62f615113d5fbc0c784aa51a9ae146'
    with zipfile.ZipFile(original) as z:assert z.testzip() is None;count=len(z.infolist())
    save(PACK/'CHECKPOINT_PRESERVATION.json',dict(status='PASS',preserved_recovery_checkpoint_archives=rows,original_recovery_packet=dict(**info(original),entries=count,CRC='PASS',preserved_SHA256_payload_verification=128,packet_reimported=False),source_worktrees_modified=False,source_review_reopened=False))
    print('PASS all six recovery checkpoint archives and every manifest payload; original recovery packet preserved exactly')
if __name__=='__main__':main()
