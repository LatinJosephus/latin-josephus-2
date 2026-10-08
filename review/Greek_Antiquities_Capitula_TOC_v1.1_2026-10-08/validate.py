from pathlib import Path
from lxml import etree as E
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[2]; V=Path(__file__).resolve().parent; A=Path(r'C:\workspace\LatinJosephus-Greek-Capitula-Audit-20261008')
ns={'t':'http://www.tei-c.org/ns/1.0'}
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,d):(V/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(R),*args],text=True,encoding='utf-8').strip()
checks=[]
def check(name,condition,details=None):
 checks.append({'test':name,'result':'PASS' if condition else 'FAIL','details':details});assert condition,(name,details)
master=json.loads((A/'GREEK_CAPITULA_MASTER.json').read_text(encoding='utf-8')); baseline=json.loads((V/'BASELINE.json').read_text(encoding='utf-8'))
schema=E.RelaxNG(E.parse(str(R/'review/Antiquities_Traditional_Navigation_2026-10-06/tei_all.rng')))
counts={1:19,2:8,3:10,4:5,6:15,7:12,8:12,9:16,10:12};concordance=[]
for b in master['books']:
 number=b['book']; p=R/f'assets/xml/antiquities/paratext/niese/book-{number:02}-contents.xml';doc=E.parse(str(p));items=doc.xpath('//t:div[@type="contents"]/t:list/t:item',namespaces=ns)
 check(f'Book {number} byte-identical audit proposal',h(p)==h(A/'proposed-tei'/p.name))
 check(f'Book {number} TEI schema',schema.validate(doc),str(schema.error_log))
 check(f'Book {number} entry count',len(items)==counts[number],len(items))
 for index,(item,entry) in enumerate(zip(items,b['entries']),1):
  label=item.find('t:label',ns);text=''.join(item.itertext());labeltext=''.join(label.itertext())
  check(f'Book {number} entry {index} elected print text and label',text==entry['printed_display'] and labeltext==entry['printed_label'] and item.get('n')==entry['printed_label'] and item.get('{http://www.w3.org/XML/1998/namespace}id')==entry['identity'])
  concordance.append({'book':number,'entry':index,'label':labeltext,'TEI_text':text,'audit_entry':entry,'companion_path':p.relative_to(R).as_posix()})
 check(f'Book {number} non-clickable paratext',not doc.xpath('//t:div[@type="contents"]//t:ref|//t:div[@type="contents"]//t:ptr|//t:div[@type="contents"]//t:milestone',namespaces=ns))
check('Nine companions and 109 entries',len(master['books'])==9 and len(concordance)==109)
registry=E.parse(str(R/'assets/xml/source-contents.xml'));check('Registry TEI schema',schema.validate(registry),str(schema.error_log));items=registry.xpath('//t:list[@type="source-contents"]/t:item',namespaces=ns)
check('Registry 30 existing plus 9 new',len(items)==39,len(items));identities=[i.get('{http://www.w3.org/XML/1998/namespace}id') for i in items];check('Unique registry identities',len(set(identities))==39)
base=E.fromstring(subprocess.check_output(['git','--no-optional-locks','-C',str(R),'show','HEAD:assets/xml/source-contents.xml']))
original=base.xpath('//t:list[@type="source-contents"]/t:item',namespaces=ns)
check('All existing registry records/attributes/text unchanged',all(E.tostring(i,method='c14n')==E.tostring(items[n],method='c14n') for n,i in enumerate(original)))
rows=[]
for item in items:
 fields={f.get('name'):''.join(f.itertext()).strip() for f in item.findall('t:fs/t:f',ns)};fields['id']=item.get('{http://www.w3.org/XML/1998/namespace}id');rows.append(fields)
check('Greek coverage exactly I-XX',sorted(int(r['book']) for r in rows if r['work']=='antiquities' and r['language']=='Greek')==list(range(1,21)))
check('All companion paths resolve',all((R/r['path']).is_file() for r in rows))
check('Only registry modified among existing tracked files',git('diff','--name-only')=='assets/xml/source-contents.xml')
protected=[p for p,v in baseline['tracked_files'].items() if p!='assets/xml/source-contents.xml'];check('All pre-existing protected worktree bytes unchanged',all(h(R/p)==baseline['tracked_files'][p]['sha256'] for p in protected),{'files':len(protected),'XML':sum(p.endswith('.xml') for p in protected)})
C=Path(baseline['canonical']);check('Canonical tracked bytes unchanged',all(h(C/p)==v['sha256'] for p,v in baseline['canonical_tracked_files'].items()))
check('Canonical index unchanged',h(baseline['canonical_index_path'])==baseline['canonical_index_sha256'])
check('Audit manifest and 120 files unchanged',h(A/'FILE_MANIFEST.json')==baseline['audit_manifest_sha256'] and all(h(A/r['relative_path'])==r['sha256'] for r in json.loads((A/'FILE_MANIFEST.json').read_text(encoding='utf-8'))['outputs']))
dump('SOURCE_ENTRY_CONCORDANCE.json',concordance);dump('REGISTRY_INVENTORY.json',rows);dump('DATA_QA.json',{'result':'PASS','checks':checks,'checks_passed':len(checks),'checks_failed':0,'entries':len(concordance),'per_book':counts,'protected_files':len(protected)})
print(json.dumps({'result':'PASS','checks':len(checks),'entries':len(concordance),'registry':len(items),'protected':len(protected)}))
