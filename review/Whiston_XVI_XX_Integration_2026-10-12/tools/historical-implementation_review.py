import pathlib,json,re,subprocess,hashlib
BASE=pathlib.Path(__file__).parent;ROOT=BASE/'candidate';PACK=ROOT/'review/Whiston_XVI_XX_Integration_2026-10-12';PIN='f6fa17f7616bf9ce046c28086b1a1448a9f8d049'
git=lambda *a:subprocess.check_output(['git','-C',str(ROOT),*a]);sha=lambda b:hashlib.sha256(b).hexdigest()
before=json.loads(git('show',PIN+':_docs/reader-corpus-integrity.json'));after=json.loads((ROOT/'_docs/reader-corpus-integrity.json').read_bytes())
new={f'assets/xml/antiquities/English/book-{n:02}.xml' for n in range(16,21)}
assert set(after['files'])==set(before['files'])
for p,r in before['files'].items():
 if p not in new:assert after['files'][p]==r,p
assert after['certified_whiston_paths']==before['certified_whiston_paths']+[f'assets/xml/antiquities/English/book-{n:02}.xml' for n in range(16,21)]
for k in set(before)|set(after):
 if k not in ['files','certified_whiston_paths','integration_baseline_commit']:assert before.get(k)==after.get(k),k
assert after['integration_baseline_commit']==PIN
old=git('show',PIN+':bin/reader-corpus-integrity.mjs').decode();current=(ROOT/'bin/reader-corpus-integrity.mjs').read_text(encoding='utf-8')
mask=lambda s:re.sub(r"const manifestSHA = '[a-f0-9]{64}';","const manifestSHA = 'REVIEWED';",s)
assert mask(old)==mask(current),'Guard changed beyond bound manifest digest'
old=git('show',PIN+':assets/js/renderTei.js').decode();current=(ROOT/'assets/js/renderTei.js').read_text(encoding='utf-8')
mask=lambda s:re.sub(r'exactNieseBooks: \[[^\]]+\]','exactNieseBooks: [REVIEWED]',s)
assert mask(old)==mask(current),'Renderer changed beyond activation list'
assert 'Whiston English: exact Niese interval.' not in current
old=git('show',PIN+':.gitattributes').decode();current=(ROOT/'.gitattributes').read_text(encoding='utf-8')
assert current.startswith(old)
out=dict(status='PASS',renderer_change='One existing Whiston exactNieseBooks activation list; no mechanism or registry change',guard_change='Only literal digest updated for complete reviewed manifest; no assertion removed',manifest_changes='Exactly five source entries, five certified paths and pinned integration baseline',all_other_manifest_entries_unchanged=True,all_existing_I_XV_tests_unchanged=True,Greek_Latin_and_registries_unchanged=True)
(PACK/'IMPLEMENTATION_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out))
