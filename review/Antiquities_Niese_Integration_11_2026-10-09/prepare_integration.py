"""Freeze integration provenance without changing either source checkout."""
from pathlib import Path
import hashlib,json,subprocess,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent; ROOT=D.parents[1]
C=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
S=Path('C:/workspace/LatinJosephus-antiquities-niese-11')
R=Path('C:/workspace/Antiquities-Niese-11-integration-runtime-20261009')
BASE='65b3256fe202a06e33a59aa2d1dcbd7107358271'
TIP='c825afcaccd195ee3574d001b408c3cd71e0984c'
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd).decode().strip()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(name,data):(D/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
 assert git('rev-parse','HEAD')==BASE and git('rev-parse','HEAD',cwd=C)==BASE
 assert git('rev-parse','HEAD',cwd=S)==TIP and not git('status','--porcelain=v1',cwd=S)
 assert not git('status','--porcelain=v1',cwd=C)
 if R.exists():assert not list(R.iterdir()),'Only the empty directory created by this interrupted freeze may be resumed'
 else:R.mkdir()
 source_packet=S/'review/Antiquities_Niese_BookXI_2026-10-09'
 manifest=json.loads((source_packet/'FILE_MANIFEST.json').read_text())
 for f in manifest['files']:assert sha((S/f['relative']).read_bytes())==f['sha256'],f['relative']
 files=[]; lines=git('ls-tree','-r',BASE).splitlines()
 oids=[line.split('\t',1)[0].split()[2] for line in lines]
 batch=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(oids)+'\n').encode(),cwd=ROOT)
 at=0
 for line in lines:
  metadata,relative=line.split('\t',1);mode,kind,oid=metadata.split();assert kind=='blob'
  end=batch.index(b'\n',at);head=batch[at:end].decode().split();assert head[:2]==[oid,'blob']
  size=int(head[2]);blob=batch[end+1:end+1+size];at=end+size+2
  a=(C/relative).read_bytes();b=(ROOT/relative).read_bytes()
  files.append(dict(relative=relative,git_blob_oid=oid,git_blob_sha256=sha(blob),canonical_working_sha256=sha(a),working_sha256=sha(b),bytes=len(b),canonical_working_bytes=len(a)))
 scope=git('diff','--name-only',BASE,TIP).splitlines()
 production=[p for p in scope if not p.startswith('review/')]
 assert production==['assets/css/tei.css','assets/js/renderTei.js','assets/xml/antiquities/Latin/book-11.xml','assets/xml/antiquities/niese/book-11.json']
 save('BASELINE.json',dict(canonical=BASE,direct_remote=BASE,source_tip=TIP,source_baseline=BASE,canonical_clean=True,source_clean=True,worktree=str(ROOT),runtime=str(R),applicable_AGENTS=[],files=files))
 save('INCOMING_SCOPE.json',dict(source_tip=TIP,baseline=BASE,complete_source_commits=git('rev-list','--reverse',BASE+'..'+TIP).splitlines(),production=production,review=[p for p in scope if p.startswith('review/')],source_manifest_verified=len(manifest['files']),source_manifest_sha256=sha((source_packet/'FILE_MANIFEST.json').read_bytes()),conflicts=[],editorial_decisions='ALL CLOSED; preserved without change'))
 receipt=Path('C:/workspace/Antiquities-Niese-Preview-09-12-13-14-15-2026-10-09/PUBLICATION_SUMMARY.json')
 save('PREVIEW_REFERENCE.json',dict(path=str(receipt),sha256=sha(receipt.read_bytes()),publication_authorized=False))
 print(json.dumps(dict(baseline_files=len(files),incoming_files=len(scope),production=len(production),review=len(scope)-len(production),source_manifest_verified=len(manifest['files']))))
if __name__=='__main__':main()
