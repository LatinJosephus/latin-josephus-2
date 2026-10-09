const fs=require('fs'),path=require('path'),http=require('http');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),site='C:/workspace/Antiquities-Niese-14-15-runtime-20261009/build2/site';
const P=b=>path.join(root,`review/Antiquities_Niese_Book${b===14?'XIV':'XV'}_2026-10-09`);
const norm=s=>s.replace(/\s+/g,' ').trim();
function narrative(node){
 const c=node.cloneNode(true);c.querySelectorAll('tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable').forEach(n=>n.remove());
 c.querySelectorAll('tei-add[place^="margin"]').forEach(n=>{if(/^(?:[IVXLCDM]+|[.·]+|nota|ss?)$/.test(n.textContent.trim()))n.remove();});
 return [...(c.matches?.('tei-p')?[c]:[]),...c.querySelectorAll('tei-p')].filter(p=>!p.closest('tei-div2[n="0"]')).map(p=>p.textContent.replace(/^\s*(?:X|II)\. /,'')).join('').replace(/\s+/g,' ').trim();
}
function instrument(s){
 s=s.replace('10: "assets/xml/antiquities/niese/book-10.json"','10: "assets/xml/antiquities/niese/book-10.json",14:"__review-registry/14.json",15:"__review-registry/15.json"');
 s=s.replace('  bookTitle.innerText = activeWork.title;','  window.__qa={getState:()=>({...state}),getData:()=>fullData,view:()=>viewData,antiquitiesNieseStartEntries,antiquitiesNieseExactView,traditionalRangeView,traditionalRows};\n  bookTitle.innerText = activeWork.title;');
 s=s.replace('    syncNavigationControls();','    syncNavigationControls(); window.__qaRenderedState={...state};');
 return s.replace('  reload().then(() => {','  reload().then(() => { window.__qaReady=true; document.querySelector("#collapse-settings")?.classList.add("show");');
}
async function main(){
 const server=http.createServer((req,res)=>{
  const url=new URL(req.url,'http://localhost');let f;
  if(/^\/__review-registry\/(14|15)\.json$/.test(url.pathname))f=path.join(P(Number(url.pathname.match(/(14|15)/)[0])),'IDENTITY_REGISTRY_PARTIAL.json');
  else{f=path.resolve(site,'.'+decodeURIComponent(url.pathname));if(!f.startsWith(path.resolve(site)+path.sep)){res.statusCode=403;return res.end();}if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');}
  if(!fs.existsSync(f)){res.statusCode=404;return res.end();}let raw=fs.readFileSync(f);if(f.endsWith('renderTei.js'))raw=Buffer.from(instrument(raw.toString()));
  res.setHeader('Content-Type',f.endsWith('.xml')?'application/xml':f.endsWith('.json')?'application/json':f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':f.endsWith('.html')?'text/html':'application/octet-stream');res.end(raw);
 });
 await new Promise(r=>server.listen(8914,'127.0.0.1',r));
 const origin='http://127.0.0.1:8914',context=await chromium.launchPersistentContext('C:/workspace/Antiquities-Niese-14-15-runtime-20261009/browser-reviewed-ranges',{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await context.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('requestfailed',r=>errors.push(r.url()+': '+r.failure()?.errorText));
 async function open(b,n){await page.goto(`${origin}/antiquities/?book=${b}&niese=${n}`,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});}
 try{
  for(const b of [14,15]){
   const registry=JSON.parse(fs.readFileSync(path.join(P(b),'IDENTITY_REGISTRY_PARTIAL.json'))),expected=JSON.parse(fs.readFileSync(path.join(P(b),'EXPECTED_REVIEWED_INTERVALS.json'))),rows=JSON.parse(fs.readFileSync(path.join(P(b),'BOUNDARIES.json')));
   const result={book:b,scope:'PARTIAL_REVIEWED_INTERVALS_ONLY_FULL_BOOK_NOT_CERTIFIED',origin,local_build:site,reader_registry_injected_only_in_test_server:true,full_book_enabled:false,started:new Date().toISOString(),result:'PENDING'};
   try{
    await open(b,1);
    result.census=await page.evaluate(()=>{const q=window.__qa,d=q.getData();return {menu:[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>Number(o.value)),Greek:q.antiquitiesNieseStartEntries('Greek',d.Greek).map(e=>e.number),Latin:q.antiquitiesNieseStartEntries('Latin',d.Latin).map(e=>e.number)};});
    if(JSON.stringify(result.census.menu)!==JSON.stringify(registry.sections.map(s=>s.number)))throw Error('Partial registry menu');
    for(const s of registry.sections){if(result.census.Latin.filter(n=>n===s.number).length!==1)throw Error('Duplicate/missing reviewed Latin identity '+s.number);}
    result.intervals=[];
    for(const e of expected){
     await page.selectOption('#niese-selector',String(e.number));await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),e.number);
     const v=await page.evaluate(code=>{const text=eval('('+code+')'),ids=[...document.querySelectorAll('[id]')].map(n=>n.id);return {Latin:text(document.querySelector('#latin')),Greek:text(document.querySelector('#greek')),English:text(document.querySelector('#english')),note:document.querySelector('#latin .niese-correspondence-note')?.textContent||null,context:!!document.querySelector('#english .niese-context-note'),duplicates:ids.filter((id,i)=>ids.indexOf(id)!==i)};},narrative.toString());
     if(v.Latin!==norm(e.text)||v.Greek!==norm(rows[e.number-1].Greek)||!v.English||!v.context||v.duplicates.length)throw Error('Rendered interval '+b+'.'+e.number+' '+JSON.stringify({actual:v,expectedLatin:norm(e.text),expectedGreek:norm(rows[e.number-1].Greek)}));
     if(rows[e.number-1].reader_note&&v.note!==rows[e.number-1].reader_note)throw Error('Reader qualification '+b+'.'+e.number);
     result.intervals.push({niese:e.number,Latin:'PASS',Greek:'PASS',English_broader_context:'PASS',duplicateIDs:0,qualified:!!v.note});
    }
    result.broader=await page.evaluate(()=>{const q=window.__qa,d=q.getData(),markers=[...d.Latin.querySelectorAll('tei-milestone[unit="niese"]')].map(n=>Number(n.getAttribute('n'))),res={};for(const scheme of ['chapter','subchapter']){const counts=new Map();for(const row of q.traditionalRows(scheme)){const v=q.traditionalRangeView('Latin',d.Latin,row);for(const m of v.querySelectorAll('tei-milestone[unit="niese"]')){const n=Number(m.getAttribute('n'));counts.set(n,(counts.get(n)||0)+1);}}res[scheme]={markers:markers.length,missingOrRepeated:markers.filter(n=>counts.get(n)!==1)};}return res;});
    if(Object.values(result.broader).some(v=>v.missingOrRepeated.length))throw Error('Chapter/subchapter marker coverage '+JSON.stringify(result.broader));
    const cases=b===14?[25,26,47,72,73,74,75,76,90,132,133]:[15,39,40,41,61,62];result.deepLinks=[];
    for(const n of cases){await open(b,n);await page.reload();await page.waitForFunction(()=>window.__qaReady);for(const [button,want] of [['#niese-next',n+1],['#niese-previous',n]]){await page.click(button);await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),want);}await page.goBack();await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n+1);await page.goForward();await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n);result.deepLinks.push({niese:n,reload_previous_next_history:'PASS'});}
    await page.uncheck('#english-pane-select');await page.check('#english-pane-select');await page.uncheck('#greek-pane-select');await page.check('#greek-pane-select');for(const theme of ['light','dark']){await page.evaluate(t=>setTheme(t),theme);await page.waitForTimeout(550);}
    await page.screenshot({path:path.join(P(b),'evidence',`local-reader-${b===15?'40':'133'}-checkpoint.png`),fullPage:true});
    result.panes_themes='PASS';result.browserErrors=errors;if(errors.length)throw Error('Browser errors');result.finished=new Date().toISOString();result.result='PASS';
   }catch(e){result.result='FAIL';result.failure=String(e);throw e;}finally{fs.writeFileSync(path.join(P(b),'PARTIAL_READER_QA.json'),JSON.stringify(result,null,2)+'\n');console.log(b,result.result,result.intervals?.length||0,result.failure||'');}
  }
 }finally{await context.close();await new Promise(r=>server.close(r));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
