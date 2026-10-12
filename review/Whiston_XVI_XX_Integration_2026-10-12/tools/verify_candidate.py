"""Portable, read-only source and independent XML/display evidence verification."""
import argparse,hashlib,json,pathlib,re,xml.etree.ElementTree as ET
PACK=pathlib.Path(__file__).resolve().parent.parent;ROOT=PACK.parents[1]
NS='{http://www.tei-c.org/ns/1.0}';sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));norm=lambda s:re.sub(r'\s+',' ',s).strip()
def extract(data):
 div=ET.fromstring(data).find('.//'+NS+'body/'+NS+'div1');parts=[];marks=[];pos=0
 def emit(s):
  nonlocal pos
  if s:parts.append(s);pos+=len(s)
 def walk(e):
  tag=e.tag.removeprefix(NS)
  if tag=='milestone' and e.get('unit')=='niese':marks.append((int(e.get('n')),pos));return
  if tag in ['num','note']:return
  emit(e.text)
  for c in e:walk(c);emit(c.tail)
 walk(div);text=''.join(parts)
 return [(n,norm(text[a:marks[i+1][1] if i+1<len(marks) else len(text)])) for i,(n,a) in enumerate(marks)]
def verify():
 receipt=load(PACK/'QA_RECEIPT.json');last=receipt['last_book'];initial=load(PACK/'BASELINE.json')['tracked_file_hashes']
 allowed={'.gitattributes','assets/js/renderTei.js','bin/reader-corpus-integrity.mjs','_docs/reader-corpus-integrity.json'}|{f'assets/xml/antiquities/English/book-{n:02}.xml' for n in range(16,last+1)}
 changed=[]
 for p,h in initial.items():
  assert (ROOT/p).is_file(),('Removed tracked file',p)
  if sha((ROOT/p).read_bytes())!=h:assert p in allowed,('Unexpected tracked change',p);changed.append(p)
 assert set(changed)==allowed,(set(changed),allowed)
 renderer=(ROOT/'assets/js/renderTei.js').read_text(encoding='utf-8');assert 'Whiston English: exact Niese interval.' not in renderer
 assert json.loads('['+re.search(r'exactNieseBooks: \[([^\]]+)\]',renderer).group(1)+']')==['preface']+list(range(1,last+1))
 sources=[]
 for r in load(PACK/'SOURCE_INVENTORY.json'):
  data=(PACK/'certified'/f'book-{r["book"]:02}.xml').read_bytes();assert sha(data)==r['certified_sha256']
  original=(PACK/'certified'/f'approved-original-book-{r["book"]:02}.xml').read_bytes()
  reconstructed=re.sub(rb'<milestone unit="niese" n="\d+"/>',b'',data)
  assert reconstructed==original and sha(original)==r['baseline_sha256']
  if r['book']<=last:assert (ROOT/r['file']).read_bytes()==data
  sources.append(dict(book=r['book'],sha256=sha(data),byte_exact=True,approved_original_reconstructed=True,enabled=r['book']<=last))
 for r in load(PACK/'I_XV_FROZEN_SOURCE_VERIFICATION.json')['files']:assert sha((ROOT/r['path']).read_bytes())==r['sha256']
 oracle=load(PACK/'INTERVAL_ORACLE.json');expected={(r['book'],r['number']):r for r in oracle};assert len(expected)==len(oracle)
 physical={}
 for b in ['preface']+[str(n) for n in range(1,last+1)]:
  filename='preface.xml' if b=='preface' else f'book-{int(b):02}.xml';data=(PACK/'certified'/filename).read_bytes()
  assert (ROOT/'assets/xml/antiquities/English'/filename).read_bytes()==data
  rows=extract(data);saved=[r for r in oracle if r['book']==b];assert [n for n,_ in rows]==[r['number'] for r in saved]
  assert len(rows)==len(set(n for n,_ in rows))
  for n,text in rows:assert text==expected[b,n]['text'] and sha(text.encode())==expected[b,n]['sha256'],(b,n)
  physical[b]=[n for n,_ in rows]
 assert physical['preface']==list(range(1,27)) and physical['1']==list(range(27,347))
 assert physical['11']==list(range(1,312))+list(range(326,343))+list(range(312,326))+list(range(343,348))
 actual=[]
 for name in receipt['section_reports']:
  r=load(PACK/name);assert r['status']=='SECTIONS-PASS' and not r['errors'] and not r['requests'];assert r['rendererSHA256']==sha((ROOT/'assets/js/renderTei.js').read_bytes());actual+=r['sections']
 keys=[(r['book'],r['number']) for r in actual];required={k for k in expected if receipt['complete_cumulative'] or (k[0]!='preface' and int(k[0])>=16)}
 assert len(keys)==len(set(keys)) and set(keys)==required,(len(keys),len(required))
 for r in actual:
  e=expected[r['book'],r['number']];assert r['passed'] and r['allNarrativeVisible'] and r['GreekLatinPresentationUnchanged']
  if receipt['complete_cumulative']:assert r['settledStateAndURLVerified'] and r['navigationLimitsVerified']
  assert r['expectedSHA256']==r['renderedSHA256']==e['sha256'] and r['notes']==len(e['notes'])
  assert r['opening']==e['opening'] and r['closing']==e['closing']
 for file in receipt['required_reports']:assert load(PACK/file)['status']=='PASS',file
 structural=load(PACK/receipt['structural_report']);soracle=load(PACK/'STRUCTURAL_ORACLE.json')
 expected_views={r['id']+':'+r['scheme']:r for r in soracle['rows'] if receipt['complete_cumulative'] or (r['book']!='preface' and int(r['book'])>=16)}
 assert structural['status']=='PASS' and not structural['errors'] and not structural['requests']
 assert len(structural['views'])==len(expected_views)
 for r in structural['views']:
  e=expected_views[r['id']+':'+r['scheme']];assert r['passed'] and r['available']==e['available']
  if e['available']:assert r['EnglishSHA256']==sha(e['text'].encode())
 return dict(status='PASS',last_book=last,independent_XML_intervals=len(expected),actual_display_intervals_reconciled=len(keys),complete_cumulative=receipt['complete_cumulative'],sources=sources,unchanged_tracked_files=len(initial)-len(changed),approved_changes=sorted(changed),containing_counts=structural['counts'],physical_XI_order_verified=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--report',type=pathlib.Path);args=p.parse_args();result=verify()
 if args.report:args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result))
