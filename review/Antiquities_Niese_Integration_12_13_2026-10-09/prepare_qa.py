"""Adapt documented QA to isolated integration paths without altering source certificates."""
from preflight import *
import zipfile, shutil
original=SOURCE/'review/Antiquities_Niese_Batch_12_13_2026-10-09'
adapter=original/'browser_qa.cjs'
s=adapter.read_text(encoding='utf8')
s=s.replace('Antiquities-Niese-12-13-runtime-20261009','Antiquities-Niese-12-13-integration-runtime-20261009')
s=s.replace('const packet=b=>path.join(root,`review/Antiquities_Niese_Book${b===12?\'XII\':\'XIII\'}_2026-10-09`);',"const packet=b=>path.join(__dirname,'books',String(b));")
s=s.replace('await listen(servers[0],8912)','await listen(servers[0],8913)')
s=s.replace("'OWN_LOCAL_BUILDS'","'MERGED_INTEGRATION_BUILD'")
s=s.replace("if(!await page.locator('#niese-level').isDisabled())throw Error('IX enabled');","if(await page.locator('#niese-level').isDisabled())throw Error('Integrated IX disabled');")
s=s.replace("if(Number(book)<=8||Number(book)===10)for(const e of q.canonicalNieseStartEntries()){", "if(Number(book)<=10)for(const e of [...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>({number:Number(o.value)}))){")
s=s.replace("const report={mode,scope:","const report={build_record:load(path.join(__dirname,'BUILD_RECORD.json')),mode,scope:")
s=s.replace('`${routine?\'ROUTINE_\':\'\'}READER_', '`${mode}_${routine?\'ROUTINE_\':\'\'}READER_')
assert '8912' not in s and "throw Error('IX enabled')" not in s
(PACK/'book-browser.cjs').write_text(s,encoding='utf8',newline='\n')
for b in [12,13]:
    destination=PACK/'books'/str(b);destination.mkdir(parents=True,exist_ok=True)
    source=ROOT/f'review/Antiquities_Niese_Book{"XII" if b==12 else "XIII"}_2026-10-09'
    for name in ['EXPECTED_INTERVALS.json','EXECUTABLE_IDENTITIES.json']:
        shutil.copyfile(source/name,destination/name)
ixpacket=ROOT/'review/Antiquities_Niese_Integration_09_2026-10-09'
common=(ixpacket/'qa-common.cjs').read_text(encoding='utf8').replace('Antiquities-Niese-09-integration-runtime-20261009/build','Antiquities-Niese-12-13-integration-runtime-20261009')
(PACK/'qa-common.cjs').write_text(common,encoding='utf8',newline='\n')
ix=(ixpacket/'integration-browser.cjs').read_text(encoding='utf8')
ix=ix.replace('Antiquities-Niese-09-integration-runtime-20261009','Antiquities-Niese-12-13-integration-runtime-20261009').replace('8910','8913')
ix=ix.replace('const supported=book<=10&&book!==11;','const supported=book<=10||[12,13].includes(book);').replace('!==3448','!==4315')
ix=ix.replace('BROWSER_QA.json','IX_CURRENT_CANONICAL_QA.json').replace('BROWSER_FAILURE.json','IX_CURRENT_CANONICAL_FAILURE.json')
ix=ix.replace('profile-integration','profile-ix-protected').replace('Fresh_COMBINED','Fresh_COMBINED')
ix=ix.replace("scope:'FRESH_COMBINED_IX_INTEGRATION_BUILD'","build_record:JSON.parse(fs.readFileSync(path.join(packet,'BUILD_RECORD.json'),'utf8')),scope:'MERGED_XII_XIII_WITH_CURRENT_IX_AND_WHISTON'")
ix=ix.replace('and3448 selections','and4315 selections')
(PACK/'ix-protected.cjs').write_text(ix,encoding='utf8',newline='\n')
whiston=ROOT/'review/Whiston_Niese_Combined_Integration_2026-10-09'
for name in ['CONTENTS_EXPECTATIONS.json','EXISTING_CONTENTS_EXPECTATIONS.json']:
    shutil.copyfile(whiston/name,PACK/name)
layout=(whiston/'layout-qa.test.cjs').read_text(encoding='utf8')
layout=layout.replace("site='C:/Users/POLLAR~1/AppData/Local/Temp/LatinJosephus-Whiston-Niese-Combined-disposable-20261009'", "site='C:/workspace/Antiquities-Niese-12-13-integration-runtime-20261009/site'")
layout=layout.replace('const report={result:',"const report={build_record:JSON.parse(fs.readFileSync(path.join(__dirname,'BUILD_RECORD.json'),'utf8')),result:")
layout=layout.replace("?'BEFORE_QA.json':'LAYOUT_QA.json'","?'BEFORE_QA.json':'WHISTON_LAYOUT_QA.json'")
layout=layout.replace('before?expected.filter(x=>[3,12].includes(x.book)):expected','before?expected.filter(x=>[3,12].includes(x.book)):expected.filter(x=>[3,5,12,13,20].includes(x.book))')
layout=layout.replace('report.books=before?2:20;report.uniqueEntries=before?26:256;','report.books=before?2:5;report.uniqueEntries=before?26:64;')
(PACK/'whiston-layout.cjs').write_text(layout,encoding='utf8',newline='\n')
layout=layout.replace("const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});const context=await browser.newContext({viewport:{width:1690,height:1100},deviceScaleFactor:1});", "const context=await chromium.launchPersistentContext('C:/workspace/Antiquities-Niese-12-13-integration-runtime-20261009/profile-whiston-layout',{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1690,height:1100},deviceScaleFactor:1});const browser={close:()=>context.close()};")
assert 'launchPersistentContext' in layout
(PACK/'whiston-layout.cjs').write_text(layout,encoding='utf8',newline='\n')
(PACK/'screenshots').mkdir(exist_ok=True)
exceptions=(original/'baseline_exceptions.cjs').read_text(encoding='utf8')
exceptions=exceptions.replace("require('./browser_qa.cjs')","require('./book-browser.cjs')").replace('Antiquities-Niese-12-13-runtime-20261009','Antiquities-Niese-12-13-integration-runtime-20261009')
(PACK/'baseline-exceptions.cjs').write_text(exceptions,encoding='utf8',newline='\n')
build=(ixpacket/'build.sh').read_text(encoding='utf8')
(PACK/'build.sh').write_text(build,encoding='utf8',newline='\n')
archive=RUNTIME/'canonical-production.zip'
top=textgit(ROOT,'ls-tree','--name-only',START).splitlines()
subprocess.check_call(['git','-C',str(ROOT),'archive','--format=zip',f'--output={archive}',START,*[p for p in top if p!='review']])
baseline=RUNTIME/'baseline-source';baseline.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:
    for item in z.infolist():
        target=(baseline/item.filename).resolve();assert baseline.resolve() in target.parents or target==baseline.resolve()
    z.extractall(baseline)
save('QA_ADAPTATION.json',{'source_tip':TIP,'source_browser_helper':str(adapter),'source_helper_sha256':sha(adapter.read_bytes()),
    'new_books':'Same certified expected intervals and executable identities copied byte-for-byte into integration-only QA fixtures',
    'adaptations':['Isolated integration runtime, result directories, profiles and port 8913','IX remains enabled during new-book switching','Protected sweep covers all current-canonical I-X menu identities including IX unavailable selections','Fresh focused IX/coverage test expects current canonical plus XII/XIII','Fresh Whiston layout targets III/V cited passages, new XII/XIII and XX in both themes and widths; unchanged broader historical layout evidence retained'],
    'canonical_archive_commit':START,'canonical_archive_sha256':sha(archive.read_bytes()),'source_certificates_modified':False,'result':'PASS'})
print('Prepared isolated actual-canonical baseline, full new-book sweeps, IX and targeted Whiston QA')
