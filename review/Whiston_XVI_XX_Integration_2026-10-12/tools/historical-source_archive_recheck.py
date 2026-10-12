import pathlib,json,zipfile,hashlib,shutil
BASE=pathlib.Path(__file__).parent;PACK=BASE/'candidate/review/Whiston_XVI_XX_Integration_2026-10-12';OUT=BASE/'source-recovery';OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest();records=[]
for r in json.loads((PACK/'SOURCE_INVENTORY.json').read_text(encoding='utf-8')):
 p=pathlib.Path(r['archive']);assert sha(p.read_bytes())==r['archive_sha256'];checked=[]
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None;names=z.namelist();assert len(names)==len(set(names))
  for m in names:
   if not m.endswith('CHECKSUMS.json'):continue
   data=json.loads(z.read(m));entries=data if isinstance(data,list) else data.get('files',[]);prefix=m[:-len('CHECKSUMS.json')]
   for e in entries:
    member=prefix+e['path'].replace('\\','/');assert member in names,(p.name,member)
    assert sha(z.read(member))==e['sha256'],(p.name,member)
    checked.append(member)
  assert len(set(checked))==len(names)-1,(p.name,len(set(checked)),len(names))
  assert z.read(r['archive_member'])==(PACK/'certified'/f'book-{r["book"]:02}.xml').read_bytes()
 shutil.copy2(p,OUT/p.name)
 records.append(dict(book=r['book'],archive=p.name,sha256=r['archive_sha256'],CRC='PASS',all_manifest_members_verified=len(set(checked)),certified_output_byte_identical=True))
master=pathlib.Path('C:/Users/Pollard_R/Downloads/Lodge1602_Bellum_FINAL_ADJUDICATED_20261003.zip');assert sha(master.read_bytes())=='18a34bdbbfd199ab482b73ad442c19cd0fb5e70794e9d77aa0a74a1c7ad26fc0';shutil.copy2(master,OUT/master.name)
(PACK/'SOURCE_ARCHIVE_VERIFICATION.json').write_text(json.dumps(dict(status='PASS',archives=records,Lodge_master_sha256=sha(master.read_bytes())),indent=2)+'\n',encoding='utf-8')
print('Five source archive CRCs, complete manifests, certified output members and Lodge master hash PASS')
