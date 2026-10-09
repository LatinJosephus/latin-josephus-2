from pathlib import Path
from lxml import etree as E
import json,hashlib,subprocess
V=Path(__file__).resolve().parent;R=V.parents[1];N={'t':'http://www.tei-c.org/ns/1.0'}
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((V/n).read_text(encoding='utf-8'))
def save(n,d):(V/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks=[]
def check(n,ok,detail=None):
 checks.append({'name':n,'result':'PASS' if ok else 'FAIL','detail':detail});assert ok,(n,detail)
def proj(e):return (e.text or '')+''.join(('' if E.QName(c).localname=='note' else proj(c))+(c.tail or '') for c in e)
A=Path(r'C:\workspace\LatinJosephus-Whiston-Contents-Audit-20261008');S=Path(r'C:\workspace\LatinJosephus-Whiston-BookIII-Adjudication-20261009')
packetresults=[]
for root,wanted in [(A,'6c74c1e98987483b4193a34f457f2671429ef93e5050b1e114ddd83a86b7aa08'),(S,'356f8dbaece44e1c686a98f6e4c5b59dbc2c4818341e4aa9fd4986f350175591')]:
 m=json.loads((root/'FILE_MANIFEST.json').read_text(encoding='utf-8'));check(root.name+'_manifest_hash',h(root/'FILE_MANIFEST.json')==wanted,wanted)
 bad=[x['path'] for x in m['entries'] if h(root/x['path'])!=x['sha256'] or (root/x['path']).stat().st_size!=x['bytes']];check(root.name+'_all_entries',not bad,len(m['entries']));check(root.name+'_self_exclusion_and_inventory',len([p for p in root.rglob('*') if p.is_file()])==len(m['entries'])+1 and 'FILE_MANIFEST.json' not in [x['path'] for x in m['entries']])
 q=json.loads((root/'QA.json').read_text(encoding='utf-8'));check(root.name+'_recorded_QA_all_pass',all(x['result']=='PASS' for x in q['checks']),len(q['checks']));packetresults.append({'root':str(root),'manifest_sha256':wanted,'entries_verified':len(m['entries']),'recorded_checks_passed':len(q['checks'])})
for x in read('ARCHIVAL_PROVENANCE.json')['copies']:check('archive_'+x['archive_path'],h(V/x['archive_path'])==x['sha256']==h(Path(x['original_path'])))
master=read('authority/BookIII-final/derived/WHISTON_HEADINGS_MASTER.json');expected=[22,16,15,8,11,14,15,15,14,11,8,11,16,16,11,11,13,9,9,11];schema=E.RelaxNG(E.parse(str(V/'authority/original-audit/sources/tei_all.rng')));check('master_ready_256',len(master['entries'])==256 and all(x['integration_ready'] and x['status'] in ['PRINT_VERIFIED','PRINT_VERIFIED_WITH_VARIANT'] for x in master['entries']))
changes=read('IMPLEMENTATION_MANIFEST.json')['production_changes'];results=[];browse=[]
for b,count in enumerate(expected,1):
 p=R/f'assets/xml/antiquities/paratext/whiston/book-{b:02}-contents.xml';d=E.parse(str(p));source=[e for e in master['entries'] if e['book']==b];items=d.xpath('//t:div[@type="contents"]/t:list/t:item',namespaces=N);labels=d.xpath('//t:div[@type="contents"]/t:list/t:label/text()',namespaces=N)
 check(f'book_{b}_schema',schema.validate(d),str(schema.error_log));check(f'book_{b}_heading_sequence',len(items)==count and [proj(x) for x in items]==[e['printed_heading'] for e in source]);check(f'book_{b}_labels_ids',labels==[e['printed_label'] for e in source] and [i.get('{http://www.w3.org/XML/1998/namespace}id') for i in items]==[e['id'] for e in source] and [int(i.get('n')) for i in items]==list(range(1,count+1)))
 check(f'book_{b}_identity_edition',d.xpath('string(//t:div[@type="contents"]/@n)',namespaces=N)==str(b) and d.xpath('string(//t:bibl/t:date/@when)',namespaces=N)=='1856' and d.xpath('string(//t:bibl/t:publisher)',namespaces=N)=='Alden & Beardsley')
 check(f'book_{b}_no_narrative_links',not d.xpath('//t:ref[not(ancestor::t:teiHeader)]',namespaces=N))
 row=next(x for x in changes if x['path']==p.relative_to(R).as_posix());raw=Path(row['authority_path']).read_bytes()
 for x in row['metadata_updates']:raw=raw.replace(x['before'].encode(),x['after'].encode())
 check(f'book_{b}_only_documented_metadata_updates',p.read_bytes()==raw)
 root=d.xpath('//t:div[@type="contents"]',namespaces=N)[0];browse.append({'book':b,'entries':count,'headings':[e['printed_heading'] for e in source],'labels':labels,'texts':[''.join(root.itertext())],'first':source[0]['printed_heading'],'last':source[-1]['printed_heading']});results.append({'book':b,'entries':count,'sha256':h(p),'schema':'PASS','heading_match':'PASS','label_match':'PASS'})
check('III8_no_terminal_point',browse[2]['headings'][7]=='OF THE PRIESTHOOD OF AARON');check('III15_final_certified_clause',browse[2]['headings'][14]=='HOW MOSES WAS DISPLEASED AT THIS, AND FORETOLD THAT GOD WAS ANGRY, AND THAT THEY SHOULD CONTINUE IN THE WILDERNESS FOR FORTY YEARS, AND NOT, DURING THAT TIME, EITHER RETURN INTO EGYPT, OR TAKE POSSESSION OF CANAAN.')
check('V3_THEM',browse[4]['headings'][2]=='HOW THE ISRAELITES AFTER THIS MISFORTUNE GREW WICKED, AND SERVED THE ASSYRIANS; AND HOW GOD DELIVERED THEM BY OTHNIEL, WHO RULED OVER THEM FORTY YEARS.')
reg=E.parse(str(R/'assets/xml/source-contents.xml'));old=E.parse(str(V/'registry-before.xml'));rows=reg.xpath('//t:list[@type="source-contents"]/t:item',namespaces=N);oldrows=old.xpath('//t:list[@type="source-contents"]/t:item',namespaces=N);check('registry_schema',schema.validate(reg),str(schema.error_log));check('registry_39plus20',len(rows)==59 and len(oldrows)==39);check('all39records_exact',all(E.tostring(a,method='c14n')==E.tostring(b,method='c14n') for a,b in zip(rows[:39],oldrows)));check('registry_all_original_bytes', (R/'assets/xml/source-contents.xml').read_bytes().split(b'        <item xml:id="contents-antiquities-whiston-01">')[0]==(V/'registry-before.xml').read_bytes().split(b'      </list>')[0])
raw=(R/'assets/xml/source-contents.xml').read_bytes();before=(V/'registry-before.xml').read_bytes();start=raw.index(b'        <item xml:id="contents-antiquities-whiston-01">');end=raw.index(b'      </list>',start);check('registry_exactly_inserted_block',raw[:start]+raw[end:]==before)
for b,row in enumerate(rows[39:],1):
 f={x.get('name'):''.join(x.itertext()).strip() for x in row.findall('t:fs/t:f',N)};check(f'registry_book{b}',f['book']==str(b) and f['witness']=='whiston' and f['language']=='English' and f['status']=='VERIFIED' and f['selectors']=='tei-div[type="contents"]' and (R/f['path']).exists())
save('CONTENTS_EXPECTATIONS.json',browse);save('DATA_QA.json',{'result':'PASS','executed_checks':len(checks),'checks':checks,'packets':packetresults,'companions':results,'headings':256,'registry':59,'existing_records':39,'production_text_changes':0});print('DATA_QA_PASS',len(checks),len(results),'companions',sum(x['entries'] for x in results),'headings')
