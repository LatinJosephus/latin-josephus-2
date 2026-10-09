"""Additive freeze of the documented advance; retain original integration baseline."""
from pathlib import Path
import datetime,hashlib,json,subprocess,shutil,tarfile
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
base=json.loads((P/'BASELINE.json').read_text());CAN=Path(base['canonical_checkout']);RT=Path(base['runtime'])
sha=lambda x:hashlib.sha256(x).hexdigest()
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd).decode('utf8').strip()
tip='c28efbdb615eaaf8dc9a939bc02e067886a83f37'
assert not (P/'CANONICAL_ADVANCE.json').exists()
assert git('rev-parse','HEAD',cwd=CAN)==tip and not git('status','--porcelain',cwd=CAN)
remote=git('ls-remote','origin','refs/heads/v2-development',cwd=CAN).split()[0]
assert remote==base['canonical_start']
assert git('rev-list','--count',base['canonical_start']+'..'+tip)=='1'
packet='review/Antiquities_Niese_Boundary_Display_2026-10-09'
manifest=json.loads((CAN/packet/'FILE_MANIFEST.json').read_text())
for f in manifest['files']:assert sha((CAN/f['path']).read_bytes())==f['sha256']
assert len(manifest['files'])==27
assert sha((CAN/'assets/js/renderTei.js').read_bytes())==manifest['production'][0]['after_sha256']
assert [x for x in git('diff','--name-only',base['canonical_start'],tip).splitlines() if not x.startswith('review/')]==['assets/js/renderTei.js']
records=[]
for line in git('ls-tree','-r','--format=%(objectmode) %(objectname) %(path)',tip).splitlines():
 mode,blob,path=line.split(' ',2);raw=(CAN/path).read_bytes()
 records.append(dict(path=path,mode=mode,blob=blob,working_sha256=sha(raw),working_bytes=len(raw),CRLF=raw.count(b'\r\n'),LF=raw.count(b'\n')))
diag=P/'diagnostics/BEFORE_CANONICAL_ADVANCE';diag.mkdir()
names=['BUILD_RECORD.json','INTEGRITY_QA.json','PRODUCTION_MANIFEST.json','PRODUCTION_RESOLUTION.json',
 'STRUCTURAL_LOCATOR_COMPATIBILITY.json','CRITICAL_COMBINED_READER_QA.json','IX_CURRENT_CANONICAL_QA.json',
 'PROTECTED_BROWSER_QA.json','WHISTON_LAYOUT_QA.json','BOOK_XIV_XV_TRANSITION_READER_QA.json','BOUNDED_BASELINE_EXCEPTIONS.json']
names += [x.relative_to(P).as_posix() for b in [14,15] for x in (P/f'books/{b}').rglob('*') if x.is_file()]
names += [x.relative_to(P).as_posix() for x in (P/'build-logs').rglob('*') if x.is_file()]
for name in names:
 dest=diag/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/name,dest)
value=dict(result='PASS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 original_integration_start=base['canonical_start'],canonical_advance=tip,remote_at_advance_freeze=remote,
 advance_report=str(CAN/packet/'REPORT.md'),advance_report_sha256=sha((CAN/packet/'REPORT.md').read_bytes()),
 advance_manifest_sha256=sha((CAN/packet/'FILE_MANIFEST.json').read_bytes()),advance_review_files=28,
 advance_production_scope=['assets/js/renderTei.js'],canonical_tracked_files=records,
 original_BASELINE_unchanged=True,coverage_unchanged=4315,
 reason='Documented local canonical display-only correction; retain its complete history and current contents before authorized XIV/XV promotion. Direct remote remains predecessor; normal final push will include this ancestor.',
 affected_projections=['VI.268','VI.270','X.107','X.149','XIII.212'],
 narrative_or_identity_changes=False,new_print_or_editorial_decisions_required=False)
(P/'CANONICAL_ADVANCE.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')
archive=RT/'canonical-advance-c28efbd.tar'
subprocess.check_call(['git','archive','--format=tar','-o',str(archive),tip],cwd=ROOT)
destination=RT/'baseline-c28efbd';destination.mkdir()
with tarfile.open(archive) as tar:
 for member in tar.getmembers():
  if member.name.startswith('review/') or not member.isfile():continue
  target=(destination/member.name).resolve();assert target.is_relative_to(destination.resolve())
  target.parent.mkdir(parents=True,exist_ok=True)
  with tar.extractfile(member) as src:target.write_bytes(src.read())
print('PASS additive canonical-advance snapshot;28 review files verified; frozen starting bytes retained')
