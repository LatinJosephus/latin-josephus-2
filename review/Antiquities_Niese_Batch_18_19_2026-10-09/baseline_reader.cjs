const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright');
const packet=__dirname,runtime='C:/workspace/Antiquities-Niese-18-19-runtime-20261009',site=path.join(runtime,'baseline-site');
const expected=JSON.parse(fs.readFileSync(path.join(packet,'EXPECTED_STRUCTURAL_RANGES.json')));
const normalize=s=>s.replace(/\s+/g,' ').trim();
function narrative(node){const c=node.cloneNode(true);c.querySelectorAll('tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable').forEach(n=>n.remove());return [...(c.matches?.('tei-p')?[c]:[]),...c.querySelectorAll('tei-p')].filter(p=>!p.closest('tei-div2[n="0"]')).map(p=>p.textContent).join('');}
function instrument(s){
 s=s.replace('  bookTitle.innerText = activeWork.title;',`  window.__qa={getState:()=>({...state}),getData:()=>fullData,view:()=>viewData,traditionalRows,bambergRows,traditionalRangeView,traditionalPoint,milestoneChapterMarkers,milestoneChapterNumbers,milestoneChapterView};\n  bookTitle.innerText = activeWork.title;`);
 return s.replace('  reload().then(() => {','  reload().then(() => { window.__qaReady=true; document.querySelector("#collapse-settings")?.classList.add("show");');
}
const result={status:'RUNNING',scope:'BASELINE_STRUCTURAL_READER_ONLY_NOT_NEW_NIESE_CERTIFICATION',site,books:{},views:[],distinctPairs:[],errors:[],started:new Date().toISOString()};
const server=http.createServer((req,res)=>{let f=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!f.startsWith(path.resolve(site)+path.sep)){res.statusCode=403;return res.end();}if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');if(!fs.existsSync(f)){res.statusCode=404;return res.end();}let raw=fs.readFileSync(f);if(f.endsWith('renderTei.js'))raw=Buffer.from(instrument(raw.toString()));res.setHeader('Content-Type',f.endsWith('.xml')?'application/xml':f.endsWith('.json')?'application/json':f.endsWith('.js')?'text/javascript':f.endsWith('.html')?'text/html':f.endsWith('.css')?'text/css':f.endsWith('.png')?'image/png':f.endsWith('.jpg')?'image/jpeg':f.endsWith('.svg')?'image/svg+xml':'application/octet-stream');res.end(raw);});
async function main(){
 await new Promise((r,j)=>{server.once('error',j);server.listen(8918,'127.0.0.1',r);});result.origin='http://127.0.0.1:8918';
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-baseline-18-19'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await context.newPage();
 page.on('pageerror',e=>result.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')result.errors.push(m.text());});page.on('requestfailed',r=>result.errors.push(r.url()+': '+r.failure()?.errorText));
 async function open(query){await page.goto(`${result.origin}/antiquities/?${query}`,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});}
 try{
  for(const b of [18,19]){
   await open(`book=${b}`);for(const lang of ['latin','greek','english'])await page.check(`#${lang}-pane-select`);
   result.books[b]=await page.evaluate(()=>{const q=window.__qa;return {actualTraditionalChapterOptions:[...document.querySelector('#chapter-selector').options].filter(o=>/^\d+$/.test(o.value)&&Number(o.value)>0).map(o=>Number(o.value)),actualAlignmentOptions:[...document.querySelector('#section-selector').options].filter(o=>o.value).map(o=>o.value),traditionalSubchapters:q.traditionalRows('subchapter').length,bamberg:q.bambergRows().map(r=>({id:r.id,label:r.display})),legacyPositiveChapterNumbers:q.milestoneChapterNumbers().filter(n=>Number(n)>0),NieseEnabled:!document.querySelector('#niese-level').disabled};});
   for(const row of expected.filter(r=>r.book===b)){
    const query=`book=${b}&`+(row.scheme==='bamberg'?`bamberg=${Number(row.id.split('-row')[1])}`:`chapter=${row.chapter}`+(row.scheme==='subchapter'?`&subchapter=${row.subchapter}`:''));
    await open(query);
    const actual=await page.evaluate(code=>{const text=eval('('+code+')'),ids=[...document.querySelectorAll('[id]')].map(n=>n.id);return {languages:Object.fromEntries(['Latin','Greek','English'].map(l=>[l,text(document.querySelector('#'+l.toLowerCase()))])),duplicateIDs:ids.filter((id,i)=>ids.indexOf(id)!==i),state:window.__qa.getState()};},narrative.toString());
    for(const lang of ['Latin','Greek','English'])if(normalize(actual.languages[lang])!==normalize(row.languages[lang].text)){fs.writeFileSync(path.join(packet,'BASELINE_RANGE_DIFFERENCE.json'),JSON.stringify({row:row.id,language:lang,actual:actual.languages[lang],expected:row.languages[lang].text},null,2));throw Error('Full structural range '+row.id+' '+lang);}
    if(actual.duplicateIDs.length)throw Error('Duplicate IDs '+row.id);
    result.views.push({id:row.id,scheme:row.scheme,book:b,Latin:'PASS',Greek:'PASS',English:'PASS',duplicateIDs:0});
   }
   for(const id of result.books[b].actualAlignmentOptions){await open(`book=${b}&unit=${id}`);const actual=await page.evaluate(()=>({state:window.__qa.getState(),paragraphs:['latin','greek','english'].map(l=>({language:l,paragraphs:document.querySelectorAll('#'+l+' tei-p').length,text:document.querySelector('#'+l).textContent.trim().length}))}));if(actual.state.sectionNum!==id||actual.paragraphs.some(p=>!p.paragraphs||!p.text))throw Error('Alignment '+b+'.'+id);}
  }
  const pairProof=JSON.parse(fs.readFileSync(path.join(packet,'DISTINCT_PHYSICAL_POINT_PROOF.json')));
  for(const b of [18,19]){
   await open(`book=${b}`);const pair=await page.evaluate(b=>{const q=window.__qa,d=q.getData(),a=q.traditionalRows('chapter').find(r=>r['canonical-niese']===(b===18?'257':'292')),z=q.bambergRows().find(r=>r.id===(b===18?'B78-table1-row190':'B78-table1-row198'));return {traditional:a.id,bamberg:z.id,label:z.display,languages:Object.fromEntries(['Latin','Greek','English'].map(l=>[l,{traditionalTarget:q.traditionalPoint(d[l],a[l]).node.id,bambergTarget:q.traditionalPoint(d[l],z[l]).node.outerHTML,distinct:q.traditionalPoint(d[l],a[l]).node!==q.traditionalPoint(d[l],z[l]).node}]))};},b);if(Object.values(pair.languages).some(l=>!l.distinct))throw Error('Distinct structural points '+b);result.distinctPairs.push({book:b,...pair,independentByteProof:pairProof.filter(r=>r.book===b)});
  }
  if(result.errors.length)throw Error('Browser errors '+JSON.stringify(result.errors));result.status='PASS';
 }catch(e){result.status='FAIL';result.failure=String(e);throw e;}finally{result.completed=new Date().toISOString();fs.writeFileSync(path.join(packet,'BASELINE_STRUCTURAL_BROWSER.json'),JSON.stringify(result,null,2));await context.close();server.close();}
 console.log(JSON.stringify({status:result.status,structuralViews:result.views.length,books:result.books,distinctPairs:result.distinctPairs.length}));
}
main().catch(e=>{console.error(e);server.close();process.exit(1);});
