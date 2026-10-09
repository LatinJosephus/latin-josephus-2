const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const task=__dirname,canonical='C:/Users/Pollard_R/Git/LatinJosephus-v2-development';
const packet=path.join(canonical,'review/Antiquities_Niese_Implementation_08_10_2026-10-09');
const expected=JSON.parse(fs.readFileSync(path.join(packet,'EXPECTED_INTERVALS.json'),'utf8'));
const certificate=JSON.parse(fs.readFileSync(path.join(packet,'CERTIFICATION.json'),'utf8'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const site=path.join(task,'build/canonical-site'),certified='C:/workspace/Antiquities-Niese-Implementation-08-10-2026-10-09/build/site';
const norm=s=>String(s||'').replace(/\s+/g,' ').trim();
function narrative(node){
 const c=node.cloneNode(true);c.querySelectorAll('tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable').forEach(n=>n.remove());
 return [...(c.matches?.('tei-p')?[c]:[]),...c.querySelectorAll('tei-p')].filter(p=>!p.closest('tei-div2[n="0"]')).map(p=>p.textContent).join('').replace(/\s+/g,' ').trim();
}
function instrument(s){
 s=s.replace('  bookTitle.innerText = activeWork.title;',`  window.__qa={getState:()=>({...state}),getData:()=>fullData,view:()=>viewData,antiquitiesNieseStartEntries,traditionalRangeView,traditionalRows,bambergRows};\n  bookTitle.innerText = activeWork.title;`);
 s=s.replace('    syncNavigationControls();','    syncNavigationControls(); window.__qaRenderedState={...state};');
 return s.replace('  reload().then(() => {','  reload().then(() => { window.__qaReady=true; document.querySelector("#collapse-settings")?.classList.add("show");');
}
function serve(root,qa=false){return http.createServer((req,res)=>{
 const url=new URL(req.url,'http://localhost');let f=path.resolve(root,'.'+decodeURIComponent(url.pathname));
 if(!f.startsWith(path.resolve(root)+path.sep)){res.statusCode=403;return res.end();}
 if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');
 if(!fs.existsSync(f)){res.statusCode=404;return res.end();}
 let raw=fs.readFileSync(f);if(qa&&f.endsWith('renderTei.js'))raw=Buffer.from(instrument(raw.toString()));
 res.setHeader('Content-Type',f.endsWith('.xml')?'application/xml':f.endsWith('.json')?'application/json':f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':f.endsWith('.html')?'text/html':f.endsWith('.png')?'image/png':'application/octet-stream');res.end(raw);
});}
async function main(){
 const result={scope:'FOCUSED_SMOKE_ON_FRESH_CANONICAL_BUILD',started:new Date().toISOString(),result:'PENDING',browserExceptions:[],consoleErrors:[],failedRequests:[],books:{},criticalURLs:[],protectedURLs:[]};
 for(const r of certificate.built_production_files){const raw=fs.readFileSync(path.join(site,r.path));if(sha(raw)!==r.sha256)throw Error('Canonical build hash '+r.path);}
 result.certified_production_build_hashes='IDENTICAL';
 const servers=[serve(site,true),serve(site),serve(certified)];await Promise.all(servers.map(s=>new Promise(r=>s.listen(0,'127.0.0.1',r))));
 const origins=servers.map(s=>`http://127.0.0.1:${s.address().port}`),browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),context=await browser.newContext(),page=await context.newPage();
 page.on('pageerror',e=>result.browserExceptions.push(String(e)));page.on('console',m=>{if(m.type()==='error')result.consoleErrors.push(m.text());});page.on('requestfailed',r=>result.failedRequests.push({url:r.url(),error:r.failure()?.errorText}));
 async function open(route,which=0){await page.goto(origins[which]+route,{waitUntil:'domcontentloaded'});if(which===0)await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});else await page.waitForFunction(()=>document.querySelector('#book-selector')?.options.length>1&&document.querySelector('#latin tei-p,#latin .structural-unavailable,#latin .source-contents'),{},{timeout:60000});}
 try{
 for(const book of [8,10]){
  await open(`/antiquities/?book=${book}&niese=1`);
  const q=await page.evaluate(book=>{
   const q=window.__qa,d=q.getData(),entries=Object.fromEntries(['Greek','Latin'].map(l=>[l,q.antiquitiesNieseStartEntries(l,d[l]).map(e=>e.number)]));
   const menu=[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>Number(o.value));
   const newMarkers=[...d.Latin.querySelectorAll('tei-milestone[unit="niese"]')].map(m=>Number(m.getAttribute('n'))),broader={},chapterOwner=new Map();
   for(const scheme of ['chapter','subchapter']){
    const counts=new Map(),rows=q.traditionalRows(scheme);
    for(const row of rows){const v=q.traditionalRangeView('Latin',d.Latin,row);for(const m of v.querySelectorAll('tei-milestone[unit="niese"]')){const n=Number(m.getAttribute('n'));counts.set(n,(counts.get(n)||0)+1);if(scheme==='chapter')chapterOwner.set(n,row);}}
    // Certified chapters with no printed lower divisions have no Subchapter
    // view. Their internal citations remain covered by the Chapter view.
    const noSubchapter=scheme==='subchapter'?newMarkers.filter(n=>chapterOwner.has(n)&&q.traditionalRows('subchapter',chapterOwner.get(n).chapter).length===0):[];
    const missingOrRepeated=newMarkers.filter(n=>!noSubchapter.includes(n)&&counts.get(n)!==1);broader[scheme]={rows:rows.length,internal_sections_present_once:counts.size,chapters_without_subdivisions:noSubchapter.map(n=>({niese:n,chapter:chapterOwner.get(n).id})),missingOrRepeated};
   }
   return {menu,entries,broader,bamberg:q.bambergRows()[0]?.id};
  },book);
  const total=book===8?420:281,wanted=Array.from({length:total},(_,i)=>i+1),latinWanted=wanted.filter(n=>!(book===10&&n===108));
  if(JSON.stringify(q.menu)!==JSON.stringify(wanted)||JSON.stringify(q.entries.Greek)!==JSON.stringify(wanted)||JSON.stringify(q.entries.Latin)!==JSON.stringify(latinWanted))throw Error('Citation census '+book);
  if(Object.values(q.broader).some(v=>v.missingOrRepeated.length))throw Error('Broader internal sections '+JSON.stringify(q.broader));
  result.books[book]={selections:total,representedLatin:q.entries.Latin.length,unavailable:book===10?[108]:[],unique_executable_identities:'PASS',all_internal_markers_in_broader_views:q.broader,bamberg:q.bamberg};
 }
 const cases=[[8,1],[8,186],[8,187],[8,254],[8,255],[8,256],[8,367],[8,368],[8,369],[8,420],[10,1],[10,18],[10,33],[10,101],[10,102],[10,107],[10,108],[10,109],[10,149],[10,150],[10,151],[10,213],[10,248],[10,276],[10,277],[10,281]];
 for(const [b,n] of cases){
  const route=`/antiquities/?book=${b}&niese=${n}`;await open(route,1);
  const actual=await page.evaluate(code=>{
   const text=eval('('+code+')'),ids=[...document.querySelectorAll('[id]')].map(n=>n.id);
   return {Latin:text(document.querySelector('#latin')),Greek:text(document.querySelector('#greek')),English:text(document.querySelector('#english')),absence:document.querySelector('#latin .structural-unavailable')?.textContent||null,note:document.querySelector('#latin .niese-correspondence-note')?.textContent||null,context:!!document.querySelector('#english .niese-context-note'),duplicates:ids.filter((id,i)=>ids.indexOf(id)!==i),menu:document.querySelector('#niese-selector').value};
  },narrative.toString());
  if(actual.menu!==String(n)||actual.Latin!==norm(expected[b].Latin[n])||actual.Greek!==norm(expected[b].Greek[n])||!actual.English||!actual.context||actual.duplicates.length)throw Error('Actual canonical URL '+b+'.'+n);
  if(b===10&&n===108&&(!actual.absence||actual.Latin||!actual.Greek||!actual.English))throw Error('108 language independence');
  if([[8,367],[10,102],[10,276]].some(([x,y])=>x===b&&y===n)&&!actual.note)throw Error('Correspondence qualification '+b+'.'+n);
  result.criticalURLs.push({book:b,niese:n,exact_rendered_intervals:'PASS',LatinAbsence:!!actual.absence,qualified:!!actual.note,English_broader_context:true,duplicateIDs:0});
 }
 for(const [b,n] of [[8,367],[8,369],[10,102],[10,108],[10,150],[10,151],[10,276]]){
  await open(`/antiquities/?book=${b}&niese=${n}`);await page.reload();await page.waitForFunction(()=>window.__qaReady);
  for(const [button,next] of [['#niese-next',n+1],['#niese-previous',n]]){await page.click(button);await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),next);const actual=await page.locator('#latin').evaluate((node,code)=>eval('('+code+')')(node),narrative.toString());if(actual!==norm(expected[b].Latin[next]))throw Error('Previous/next rendered text');}
  await page.goBack();await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n+1);await page.goForward();await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n);
  await page.uncheck('#english-pane-select');await page.check('#english-pane-select');await page.uncheck('#greek-pane-select');await page.check('#greek-pane-select');
  for(const theme of ['light','dark']){await page.evaluate(t=>setTheme(t),theme);await page.waitForTimeout(550);}
 }
 result.reload_history_navigation_panes_themes='PASS';
 await open('/antiquities/?book=8&niese=367');await page.selectOption('#book-selector','09');await page.waitForFunction(()=>window.__qaRenderedState?.bookNum==='09');if(!await page.locator('#niese-level').isDisabled()||new URL(page.url()).searchParams.has('niese'))throw Error('IX unavailable fallback');
 await page.selectOption('#book-selector','10');await page.waitForFunction(()=>window.__qaRenderedState?.bookNum==='10');await page.check('#niese-level');await page.waitForFunction(()=>window.__qaRenderedState?.viewingLevel==='niese-level');await page.selectOption('#niese-selector','108');await page.waitForFunction(()=>window.__qaRenderedState?.nieseNum==='108');if(!await page.locator('#latin .structural-unavailable').count())throw Error('Return X.108');result.non_contiguous_availability='PASS';
 const protectedRoutes=['/antiquities/?book=1&niese=27','/antiquities/?book=7&niese=394','/antiquities/?book=6&chapter=12&subchapter=8','/antiquities/?book=11&chapter=8&subchapter=4','/antiquities/?book=8&unit=251','/antiquities/?book=8&view=contents','/antiquities/?book=10&view=contents','/antiquities/?book=14&view=contents','/antiquities/?book=1&bamberg=B78-table1-row005','/bellum-judaicum/?book=1&chapter=1','/bellum-judaicum/?book=4&chapter=1','/bellum-judaicum/?book=1&niese=1&english=whiston','/bellum-judaicum/?book=1&niese=1&english=lodge1602','/deh/?book=1&chapter=1&unit=1','/contra-apionem/?book=2&unit=1'];
 for(const route of protectedRoutes){
  const snapshots=[];for(const which of [2,1]){await open(route,which);snapshots.push(await page.evaluate(()=>Object.fromEntries(['latin','greek','english'].map(l=>[l,document.getElementById(l)?.innerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]))));}
  if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1]))throw Error('Protected canonical/certified difference '+route);result.protectedURLs.push({route,canonical_vs_certified_three_language_DOM:'PASS',sha256:sha(JSON.stringify(snapshots[1]))});
 }
 await open('/bellum-judaicum/?book=1&niese=1&english=lodge1602');await page.uncheck('#lodge-notes-visible');if(!await page.locator('#english').evaluate(n=>n.classList.contains('lodge-notes-hidden')))throw Error('Lodge notes hide');await page.check('#lodge-notes-visible');if(await page.locator('#english').evaluate(n=>n.classList.contains('lodge-notes-hidden')))throw Error('Lodge notes restore');result.Lodge_marginal_note_toggle='PASS';
 if(result.browserExceptions.length||result.consoleErrors.length||result.failedRequests.length)throw Error('Browser errors '+JSON.stringify({exceptions:result.browserExceptions,console:result.consoleErrors,requests:result.failedRequests}));
 result.total_Antiquities_selections=3157;result.finished=new Date().toISOString();result.result='PASS';
 fs.writeFileSync(path.join(task,'CANONICAL_SMOKE_QA.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({result:result.result,books:result.books,criticalURLs:result.criticalURLs.length,protectedURLs:result.protectedURLs.length,browserExceptions:0,consoleErrors:0,failedRequests:0},null,2));
 }catch(e){result.result='FAIL';result.failure=String(e);fs.writeFileSync(path.join(task,'CANONICAL_SMOKE_FAILURE.json'),JSON.stringify(result,null,2)+'\n');throw e;}
 finally{await browser.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
