from pathlib import Path
from lxml import etree as E
import json,hashlib,subprocess,shutil,textwrap
R=Path(__file__).resolve().parents[2];V=Path(__file__).resolve().parent
A=Path(r'C:\workspace\LatinJosephus-Greek-Capitula-Audit-20261008');C=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
BASE='f393fa1223b38d9ca114e583fcc57d5e34425815';AH='4d5bf373b7d9d5c0d656a04b567b591446bafca9b24d4969ec98f73956c75d1b'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args],text=True,encoding='utf-8').strip()
def dump(name,d):(V/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert git(C,'rev-parse','HEAD')==BASE and git(C,'rev-parse','origin/v2-development')==BASE and not git(C,'status','--short')
assert git(R,'rev-parse','HEAD')==BASE and git(R,'branch','--show-current')=='codex/antiquities-greek-capitula-toc-v1.1'
assert h(A/'FILE_MANIFEST.json')==AH
am=json.loads((A/'FILE_MANIFEST.json').read_text(encoding='utf-8'));assert len(am['outputs'])==120
for row in am['outputs']:assert h(A/row['relative_path'])==row['sha256'],row['relative_path']
tracked=git(R,'ls-files').splitlines();baseline={p:{'sha256':h(R/p),'bytes':(R/p).stat().st_size} for p in tracked}
canonical_baseline={p:{'sha256':h(C/p),'bytes':(C/p).stat().st_size} for p in tracked}
checkout_differences=[]
for p,v in baseline.items():
 if canonical_baseline[p]['sha256']!=v['sha256']:
  assert (C/p).read_bytes().replace(b'\r\n',b'\n')==(R/p).read_bytes().replace(b'\r\n',b'\n'),p
  checkout_differences.append({'path':p,'canonical':canonical_baseline[p],'worktree':v,'difference':'Initial Git checkout CRLF/LF serialization only; each baseline preserved separately'})
dump('CHECKOUT_EOL_DIAGNOSTIC.json',{'count':len(checkout_differences),'files':checkout_differences,'no_normalization_performed':True})
dump('BASELINE.json',{'base':BASE,'branch':git(R,'branch','--show-current'),'canonical':str(C),'worktree':str(R),'tracked_files':baseline,'canonical_tracked_files':canonical_baseline,'canonical_index_path':str(C/'.git/index'),'canonical_index_sha256':h(C/'.git/index'),'audit_manifest_sha256':AH})
archive=V/'audit-authority';archive.mkdir(exist_ok=False)
core=['FILE_MANIFEST.json','REPORT.md','SOURCE_AUTHORITY.md','GREEK_CAPITULA_MASTER.json','GREEK_CAPITULA_COLLATION.json','GREEK_CAPITULA_REVIEW.md','GREEK_CAPITULA_INTEGRATION_PLAN.md','QA.json']
for name in core:shutil.copyfile(A/name,archive/name);assert h(A/name)==h(archive/name)
dump('AUDIT_ARCHIVE_REFERENCE.json',{'arrangement':'Hash-verified archival arrangement: retain the complete accepted external audit packet at the path below, unchanged. The original manifest and core source/editorial documents are mirrored byte-for-byte here. Every external audit file, including raw digital witnesses and visual print evidence, is enumerated by that manifest. These documents record the audit stage and are not rewritten as implementation reports.','original_packet':str(A),'original_manifest_sha256':AH,'original_packet_files':121,'manifest_entries':120,'manifest_self_exclusion':'FILE_MANIFEST.json only','verified_before_implementation':120,'archived_core_copies':[{'path':'audit-authority/'+n,'sha256':h(archive/n)} for n in core]})
master=json.loads((A/'GREEK_CAPITULA_MASTER.json').read_text(encoding='utf-8'));rows=[]
for b in master['books']:
 rel=f'assets/xml/antiquities/paratext/niese/book-{b["book"]:02}-contents.xml';p=R/rel
 assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(A/'proposed-tei'/p.name,p)
 assert h(p)==h(A/'proposed-tei'/p.name)
 rows.append({'path':rel,'audit_source':str(A/'proposed-tei'/p.name),'before_sha256':None,'after_sha256':h(p),'book':b['book'],'entries':b['entry_count'],'copy_byte_identical':True})
registry=R/'assets/xml/source-contents.xml';raw=registry.read_bytes();marker=b'        </list>'
assert raw.count(marker)==1
proposal=E.parse(str(A/'PROPOSED_REGISTRY_ADDITIONS.xml'));ns={'t':'http://www.tei-c.org/ns/1.0'}
items=proposal.xpath('//t:list[@type="source-contents"]/t:item',namespaces=ns);assert len(items)==9
# Insert additions at one byte position; do not reserialize any installed registry record.
blocks=[]
for item in items:
 s=E.tostring(item,encoding='unicode',pretty_print=True,with_tail=False).replace(' xmlns="http://www.tei-c.org/ns/1.0"','')
 s=textwrap.indent(textwrap.dedent(s).rstrip(),'        ')
 blocks.append(s)
addition=('\n'.join(blocks)+'\n').encode('utf-8');index=raw.index(marker);updated=raw[:index]+addition+raw[index:]
registry.write_bytes(updated);assert updated[:index]+updated[index+len(addition):]==raw
rows.append({'path':'assets/xml/source-contents.xml','before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':h(registry),'inserted_records':9,'original_bytes_recoverable_by_removing_insertion':True,'insertion_byte_offset':index,'insertion_byte_length':len(addition)})
dump('IMPLEMENTATION_MANIFEST.json',{'base':BASE,'source_audit_manifest_sha256':AH,'production_changes':rows,'renderer_modified':False,'CSS_modified':False,'existing_narrative_XML_modified':False,'source_entries_added':109,'new_companions':9})
(V/'DEFERRED_BOOK_V.md').write_text('''# Deferred Book V control encoding issue\n\nThe accepted source audit identifies a stray literal [στιγμα]. after Greek Antiquities V contents entry5 and an irregular ς -- label for entry6. This integration does not change Book V, its existing registration or its display. The separate source/editorial decision remains deferred; see the byte-preserved audit-authority/GREEK_CAPITULA_REVIEW.md. It does not affect the nine newly added companions.\n''',encoding='utf-8')
print('Copied 9 byte-identical companions; inserted 9 registry items; total 109 entries. No renderer/CSS/narrative edit.')