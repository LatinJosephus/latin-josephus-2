"""Copy accepted QA machinery; write all fresh results only in integration packet."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
SRC=ROOT/'review/Antiquities_Niese_Batch_14_15_2026-10-09'
PRE=ROOT/'review/Antiquities_Niese_Integration_12_13_2026-10-09'
oldruntime='C:/workspace/Antiquities-Niese-12-13-integration-runtime-20261009'
runtime='C:/workspace/Antiquities-Niese-14-15-integration-runtime-20261009'
records=[]
def read(p):
 records.append(dict(source=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 return p.read_text(encoding='utf8')
def save(name,text):(P/name).write_text(text,encoding='utf8',newline='\n')
def replace(text,a,b):
 assert a in text,a
 return text.replace(a,b)
for b in [12,13,14,15]:(P/'books'/str(b)/'evidence').mkdir(parents=True,exist_ok=True)
(P/'screenshots').mkdir(exist_ok=True)
s=read(SRC/'full-reader-qa.cjs')
s=replace(s,"const P=path.join(root,`review/Antiquities_Niese_Book${roman}_2026-10-09`),runtime='C:/workspace/Antiquities-Niese-14-15-runtime-20261009',site=path.join(runtime,build,'site');","const sourceP=path.join(root,`review/Antiquities_Niese_Book${roman}_2026-10-09`),P=path.join(__dirname,'books',String(b)),runtime='"+runtime+"',site=path.join(runtime,build,'site');")
for name in ['IDENTITY_REGISTRY.json','BOUNDARIES.json','EXPECTED_REVIEWED_INTERVALS.json','EXPECTED_ENGLISH_CONTEXT.json']:s=replace(s,"path.join(P,'"+name+"')","path.join(sourceP,'"+name+"')")
s=replace(s,"server.listen(8914,'127.0.0.1',resolve)","server.listen(8915,'127.0.0.1',resolve)")
s=replace(s,"result.origin='http://127.0.0.1:8914'","result.origin=`http://127.0.0.1:${server.address().port}`")
s=replace(s,"scope:'COMPLETE_LOCAL_BOOK_READER_CERTIFICATION'","scope:'FRESH_MERGED_CANONICAL_INTEGRATION_BOOK_READER_CERTIFICATION'")
save('full-reader-integration.cjs',s)
s=read(SRC/'book-transition-qa.cjs');s=replace(s,'C:/workspace/Antiquities-Niese-14-15-runtime-20261009',runtime);s=replace(s,"'build5/site'","'site'");s=replace(s,"server.listen(8914,'127.0.0.1',resolve)","server.listen(8915,'127.0.0.1',resolve)");s=replace(s,'http://127.0.0.1:8914','http://127.0.0.1:8915');save('book-transition-qa.cjs',s)
s=read(PRE/'qa-common.cjs');save('qa-common.cjs',s.replace(oldruntime,runtime))
s=read(PRE/'ix-protected.cjs');s=s.replace(oldruntime,runtime).replace('await listen(servers[0],8913)','await listen(servers[0],8915)')
s=replace(s,"book<=10||(which===0&&[12,13].includes(book))","book<=10||[12,13].includes(book)||(which===0&&[14,15].includes(book))")
s=replace(s,'report.total_selectable!==4315','report.total_selectable!==5231');s=replace(s,'report.baseline_total_selectable!==3448','report.baseline_total_selectable!==4315')
s=replace(s,'![12,13].includes(record.book)','![14,15].includes(record.book)');s=replace(s,'report.baseline_total_selectable!==867','report.baseline_total_selectable!==916')
s=replace(s,'[[12,248],[13,214]]','[[12,248],[13,214],[14,388],[15,40]]');s=replace(s,'({12:11,13:16})[book]','({12:11,13:16,14:16,15:11})[book]')
s=s.replace('MERGED_XII_XIII_WITH_CURRENT_IX_AND_WHISTON','MERGED_XIV_XV_WITH_CURRENT_IX_XII_XIII_AND_WHISTON').replace('and4315 selections','and5231 selections')
save('ix-protected.cjs',s)
s=read(PRE/'book-browser.cjs');s=s.replace(oldruntime,runtime).replace('await listen(servers[0],8913)','await listen(servers[0],8915)')
s=replace(s,'[12,13].includes(Number(book))','[12,13,14,15].includes(Number(book))')
s=replace(s,'if(Number(book)<=10)for','if(Number(book)<=10||[12,13].includes(Number(book)))for')
save('book-browser.cjs',s)
for name in ['CONTENTS_EXPECTATIONS.json','EXISTING_CONTENTS_EXPECTATIONS.json']:(P/name).write_bytes((PRE/name).read_bytes())
s=read(PRE/'whiston-layout.cjs');s=s.replace(oldruntime,runtime);s=replace(s,'[3,5,12,13,20]','[3,5,12,13,14,15,20]');save('whiston-layout.cjs',s)
s=read(PRE/'baseline-exceptions.cjs');save('baseline-exceptions.cjs',s.replace(oldruntime,runtime))
for b in [12,13]:
 for name in ['EXPECTED_INTERVALS.json','EXECUTABLE_IDENTITIES.json']:(P/'books'/str(b)/name).write_bytes((PRE/'books'/str(b)/name).read_bytes())
(P/'QA_ADAPTATION.json').write_text(json.dumps(dict(source_scripts=records,inputs='Accepted source expected XIV/XV intervals, decisions and Greek register; current-canonical XII/XIII expected intervals and Whiston contents. No identity data injected.',changes=['Own integration paths, outputs and independent profiles; fresh candidate and starting-canonical builds','Merged availability includes IX XII/XIII XIV/XV; compare prior sets and require exactly916 additions','Preserve source certificates: fresh book QA and images written under integration books/','Protected DOM comparisons strip only incoming XIV/XV marker additions in broader original-source views; all current canonical logic retained','Explicit Whiston XIV/XV index and Contents/Niese roundtrip checks added'],current_English='Actual integration-start English hashes are frozen separately. XIV/XV English bytes currently equal source-frozen English; accepted source expected contexts remain applicable.'),indent=2)+'\n',encoding='utf8',newline='\n')
print('Prepared independent integration QA with preserved source packets.')
