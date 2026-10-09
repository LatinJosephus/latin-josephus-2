"""Explicit-manifest local commits. No push, merge, rebase or config changes.
The final reader bytes are restored after staging each availability declaration.
"""
import pathlib,json,subprocess,hashlib,sys
P=pathlib.Path(__file__).resolve().parent;W=P.parents[1]
phase=sys.argv[1];scope=json.loads((P/'COMMIT_SCOPE.json').read_text())
assert phase in scope['groups'];paths=scope['groups'][phase]
def git(*args):return subprocess.check_output(['git',*args],cwd=W)
assert git('branch','--show-current').decode().strip()=='antiquities-niese-08-10-implementation'
assert not git('diff','--cached','--name-only')
manifest={x['path']:x for x in json.loads((P/'FILE_MANIFEST.json').read_text())['files']}
for rel in paths:
 assert (W/rel).is_file(),rel
 if rel in manifest:assert hashlib.sha256((W/rel).read_bytes()).hexdigest()==manifest[rel]['sha256'],rel
reader=W/'assets/js/renderTei.js';full=reader.read_bytes()
old=b'      nieseIdentityBooks: {\n        8: "assets/xml/antiquities/niese/book-08.json",\n        10: "assets/xml/antiquities/niese/book-10.json"\n      },'
assert full.count(old)==1
stage=full
if phase=='shared_reader':stage=full.replace(old,b'      nieseIdentityBooks: {},')
if phase=='VIII':stage=full.replace(old,b'      nieseIdentityBooks: {\n        8: "assets/xml/antiquities/niese/book-08.json"\n      },')
temp=pathlib.Path('C:/workspace/Antiquities-Niese-Implementation-08-10-2026-10-09/commit-inputs');temp.mkdir(parents=True,exist_ok=True)
spec=temp/(phase+'.nul');spec.write_bytes(b'\0'.join(p.encode() for p in paths)+b'\0')
messages={
 'shared_reader':'Support registry-driven Antiquities Niese identities\n\nAdd generic availability, inherited-label suppression, language absence and correspondence notes, plus Niese previous/next controls. Exclude header folio and apparatus numbers from narrative citation identities. No new book is declared in this shared machinery commit. VIII and X data and explicit availability keys follow separately.\n\nAuthorized isolated local work only; canonical integration, push and public deployment remain pending.\n',
 'VIII':'Implement and locally certify Antiquities VIII Niese segmentation\n\nRepresent all 420 sections with 83 retained inherited starts and 337 byte-preserving Latin milestones. Add Greek opening 1 and relocate the six adjudicated Greek starts, preserving printed marginal/Loeb/editorial distinctions. Retain VIII.367 surviving tail and both repetitions at 369. Preserve visible inherited 187/255 claims while suppressing their false executable starts through book data.\n\nEnable only VIII through the shared reader registry. Independent source, adjudication, preservation and actual built-site browser certificates accompany the book. Depends on the preceding generic reader commit. No textual emendations, paragraph splits, supplementation or gaps. Canonical integration, push and deployment remain unauthorized.\n',
 'X':'Implement and locally certify Antiquities X Niese segmentation\n\nRepresent 281 selectable sections with 50 retained inherited starts, 230 byte-preserving Latin milestones and an explicit Latin absence state for 108. Add Greek opening 1 and relocate 33. Start 102 at nomine sedechiam, preserving simulet ioachim with 101; qualify available 276 without supplying the absent Roman-rule notice. Preserve displaced visible 108/151 labels while resolving their executable identities through data.\n\nAdd explicit X availability; IX remains unavailable. Independent preservation and actual built-site browser certificates accompany the book. Depends on the shared reader machinery. No narrative or traditional structure changes. Canonical integration, push and deployment remain unauthorized.\n',
 'shared_certification':'Certify the isolated Antiquities VIII and X implementation batch\n\nPreserve accepted review records and audit history; record current-base byte reversals, complete partitions, all 701 actual new-book browser selections, 700 Latin intervals and X.108 absence. Document 3,157 cumulative Antiquities selections and protected traditional, Bamberg, Alignment, source-contents, Whiston/Lodge, Bellum, DEH and Contra Apionem regressions.\n\nExact path scope and SHA-256 manifest accompany reproducible application, build and verification scripts. All work remains local; canonical integration, push and public deployment are pending subsequent review.\n'}
body=temp/(phase+'.txt');body.write_text(messages[phase],encoding='utf8',newline='\n')
try:
 reader.write_bytes(stage)
 git('add','--pathspec-from-file='+str(spec),'--pathspec-file-nul')
 staged=git('diff','--cached','--name-only','-z').decode().split('\0');staged=[p for p in staged if p]
 assert sorted(staged)==sorted(paths),(staged,paths)
 result=git('commit','--file='+str(body)).decode();print(result.splitlines()[0])
 print(git('rev-parse','HEAD').decode().strip());print('Explicit staged files:',len(staged))
finally:reader.write_bytes(full)
