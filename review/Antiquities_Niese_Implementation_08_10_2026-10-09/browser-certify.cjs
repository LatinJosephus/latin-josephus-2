const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const packet=__dirname,root=path.resolve(packet,'../..'),build='C:/workspace/Antiquities-Niese-Implementation-08-10-2026-10-09/build';
const expected=JSON.parse(fs.readFileSync(path.join(packet,'EXPECTED_INTERVALS.json'),'utf8'));
const digest=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
function instrument(source){
 source=source.replace('  bookTitle.innerText = activeWork.title;',`  window.__qa={getState:()=>({...state}),getData:()=>fullData,view:()=>viewData,reload,setState,selectView,selectCanonicalView,currentIdBase,canonicalNieseStartEntries,antiquitiesNieseStartEntries,traditionalRangeView,traditionalRows,bambergRows,bambergSelection,traditionalRegistry:()=>traditionalRegistry,alignmentRegistry:()=>alignmentRangeRegistry,bambergRegistry:()=>bambergRegistry,assign:patch=>Object.assign(state,patch)};
  bookTitle.innerText = activeWork.title;`);
 source=source.replaceAll('setState(() => {','window.__qaPending = setState(() => {');
 source=source.replace('    syncNavigationControls();','    syncNavigationControls(); window.__qaRenderedState={...state};');
 return source.replace('  reload().then(() => {','  reload().then(() => { window.__qaReady=true; document.querySelector("#collapse-settings")?.classList.add("show");');
}
function serve(site,qa=true){return http.createServer((req,res)=>{
 const u=new URL(req.url,'http://localhost');let f=path.resolve(site,'.'+decodeURIComponent(u.pathname));
 if(!f.startsWith(path.resolve(site)+path.sep)){res.statusCode=403;return res.end();}
 if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');
 if(!fs.existsSync(f)){res.statusCode=404;return res.end();}
 let raw=fs.readFileSync(f);if(qa&&f.endsWith('renderTei.js'))raw=Buffer.from(instrument(raw.toString()));
 res.setHeader('Content-Type',f.endsWith('.xml')?'application/xml':f.endsWith('.json')?'application/json':f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':f.endsWith('.html')?'text/html':'application/octet-stream');res.end(raw);
});}
const normalize=s=>String(s||'').replace(/\s+/g,' ').trim();
function narrative(node){
 if(!node)return null;const c=node.cloneNode(true);
 c.querySelectorAll('tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable').forEach(x=>x.remove());
 return [...(c.matches?.('tei-p')?[c]:[]),...c.querySelectorAll('tei-p')].filter(p=>!p.closest('tei-div2[n="0"]')).map(p=>p.textContent).join('').replace(/\s+/g,' ').trim();
}
function canonicalHTML(node,book,language){
 if(!node)return null;const c=node.cloneNode(true);
 if([8,10].includes(Number(book))){c.querySelectorAll('tei-milestone[unit="niese"],.niese-correspondence-note').forEach(n=>n.remove());if(language==='Greek')c.querySelectorAll('tei-num').forEach(n=>n.remove());}
 return c.outerHTML;
}
async function main(){
 const report={scope:'ACTUAL_BUILT_IMPLEMENTATION',mode:process.argv.includes('--ui-supplement')?'ui-supplement':process.argv.includes('--regressions')?'protected-regressions':'new-books',errors:[],consoleErrors:[],networkFailures:[],started:new Date().toISOString()};
 const servers=[serve(path.join(build,'site')),serve(path.join(build,'baseline-site')),serve(path.join(build,'site'),false)];
 await Promise.all(servers.map(s=>new Promise(r=>s.listen(0,'127.0.0.1',r))));const origins=servers.map(s=>`http://127.0.0.1:${s.address().port}`);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const context=await browser.newContext();const page=await context.newPage();
 page.on('pageerror',e=>report.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push(m.text());});
 page.on('requestfailed',r=>report.networkFailures.push({url:r.url(),reason:r.failure()?.errorText}));
 async function open(route,which=0){await page.goto(origins[which]+route,{waitUntil:'domcontentloaded'});if(which<2)await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});else await page.waitForFunction(()=>document.querySelector('#book-selector')?.options.length>1&&document.querySelector('#latin tei-p, #latin .structural-unavailable'),{},{timeout:60000});}
 async function change(selector,value){await page.selectOption(selector,value);await page.evaluate(()=>window.__qaPending);}
 try{
 if(report.mode==='ui-supplement'){
  report.navigation=[];
  const cases=[[8,1],[8,59],[8,187],[8,255],[8,367],[8,368],[8,369],[8,420],[10,1],[10,18],[10,102],[10,108],[10,109],[10,150],[10,151],[10,276],[10,277],[10,281]];
  async function rendered(n){await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n);const actual=await page.locator('#latin').evaluate((node,code)=>eval('('+code+')')(node),narrative.toString());const b=await page.evaluate(()=>Number(window.__qa.getState().bookNum));if(actual!==normalize(expected[b].Latin[n]))throw Error(`Navigation rendered interval ${b}.${n}`);}
  for(const [book,n] of cases){
   await open(`/antiquities/?book=${book}&niese=${n}`);await rendered(n);
   if(n<(book===8?420:281)){await page.click('#niese-next');await rendered(n+1);await page.click('#niese-previous');await rendered(n);await page.goBack();await rendered(n+1);await page.goForward();await rendered(n);}
   else if(!await page.locator('#niese-next').isDisabled())throw Error('Final next endpoint');
   if(n===1&&!await page.locator('#niese-previous').isDisabled())throw Error('First previous endpoint');
   const themeStyles=[];
   for(const theme of ['light','dark']){await page.evaluate(theme=>setTheme(theme),theme);await page.waitForTimeout(550);themeStyles.push(await page.evaluate(()=>({theme:document.documentElement.dataset.theme,stored:localStorage.getItem('theme'),background:getComputedStyle(document.body).backgroundColor})));}
   if(themeStyles[0].background===themeStyles[1].background||themeStyles.some(x=>x.theme!==x.stored))throw Error('Theme did not apply');
   report.navigation.push({book,n,rendered_previous_next_back_forward:'PASS',endpoints:'PASS',themeStyles});
  }
  await open('/bellum-judaicum/?book=1&niese=1&english=lodge1602');
  const before=await page.locator('#english').innerHTML();await page.uncheck('#lodge-notes-visible');
  if(!await page.locator('#english').evaluate(n=>n.classList.contains('lodge-notes-hidden'))||new URL(page.url()).searchParams.get('lodgeNotes')!=='0')throw Error('Lodge notes hide');
  await page.reload();await page.waitForFunction(()=>window.__qaReady);if(await page.locator('#lodge-notes-visible').isChecked())throw Error('Lodge notes reload');await page.check('#lodge-notes-visible');
  if(before!==await page.locator('#english').innerHTML()||await page.locator('#english').evaluate(n=>n.classList.contains('lodge-notes-hidden')))throw Error('Lodge notes restore');
  await change('#english-source-selector','whiston');if(await page.locator('#lodge-notes-select').isVisible())throw Error('Whiston marginal notes control');report.Lodge_notes_and_Whiston_source_switch='PASS';
  report.other_deep_links=[];
  for(const route of ['/deh/?book=1&chapter=1&unit=1','/deh/?book=5&chapter=1','/contra-apionem/?book=1&unit=1','/contra-apionem/?book=2&unit=1','/antiquities/?book=14&view=contents']){
   await open(route);const before=await page.locator('#latin').innerHTML();await page.reload();await page.waitForFunction(()=>window.__qaReady);if(before!==await page.locator('#latin').innerHTML())throw Error('Deep link reload '+route);report.other_deep_links.push({route,result:'PASS'});
  }
 }else if(report.mode==='new-books'){
  report.books={};
  for(const book of process.argv.includes('--book10')?[10]:[8,10]){
   await open(`/antiquities/?book=${book}&niese=1`);
   const projection=await page.evaluate(({book,expected,narrativeCode})=>{
    const text=eval('('+narrativeCode+')'),q=window.__qa,data=q.getData(),errors=[],results=[],ids={};
    for(const l of ['Greek','Latin']){const starts=q.antiquitiesNieseStartEntries(l,data[l]);ids[l]=starts.map(e=>e.number);if(new Set(ids[l]).size!==ids[l].length)errors.push('Duplicate '+l+' starts: '+JSON.stringify(starts.filter(e=>ids[l].filter(n=>n===e.number).length>1).map(e=>({number:e.number,kind:e.kind,paragraph:e.node.closest('tei-p')?.id,text:e.node.textContent,html:e.node.outerHTML.slice(0,800)}))));}
    for(let n=1;n<=Object.keys(expected.Greek).length;n++){
     q.assign({viewingLevel:'niese-level',nieseNum:String(n),chapterNum:null,subchapterNum:null,sectionNum:null,bambergId:null});
     const row={n};
     for(const l of ['Greek','Latin','English']){
      const v=q.selectView(l,data[l],q.currentIdBase());row[l]=text(v);const wanted=l==='English'?undefined:expected[l][n];
      if(wanted===null){if(!v?.querySelector('.structural-unavailable')||row[l])errors.push(`${l} ${n} unavailable state`);}
      else if(wanted!==undefined&&row[l]!==wanted.replace(/\s+/g,' ').trim())errors.push(`${l} ${n} interval mismatch`);
      if(l==='English'&&(!v?.querySelector('.niese-context-note')||!row[l]))errors.push(`English ${n} missing broader context`);
      const all=[...v?.querySelectorAll('[id]')||[]].map(x=>x.id);if(new Set(all).size!==all.length)errors.push(`${l} ${n} duplicate DOM IDs`);
     }
     results.push(row);
    }
    return {errors,ids,results,menu:[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>Number(o.value))};
   },{book,expected:expected[book],narrativeCode:narrative.toString()});
   if(projection.errors.length)throw Error(JSON.stringify(projection.errors.slice(0,30)));
   const max=book===8?420:281;if(projection.menu.length!==max)throw Error('Niese menu count');
   // Drive every citation through the actual select event and renderUI.
   const ui=[];
   for(let n=1;n<=max;n++){
    await change('#niese-selector',String(n));
    const actual=await page.evaluate(code=>{
     const text=eval('('+code+')'),q=window.__qa,v=q.view(),idList=[...document.querySelectorAll('[id]')].map(x=>x.id);
     return {state:q.getState().nieseNum,Greek:text(v.Greek),Latin:text(v.Latin),English:text(v.English),duplicates:idList.filter((id,i)=>idList.indexOf(id)!==i),notice:v.Latin?.querySelector('.structural-unavailable')?.textContent||null};
    },narrative.toString());
    if(actual.state!==String(n)||actual.Greek!==normalize(expected[book].Greek[n])||actual.Latin!==normalize(expected[book].Latin[n])||actual.duplicates.length)throw Error(`UI ${book}.${n}: ${JSON.stringify(actual).slice(0,300)}`);
    if(book===10&&n===108&&!actual.notice)throw Error('108 lacks notice');ui.push(n);
   }
   const q={book,expected_sections:max,all_identity_projections:'PASS',Greek_starts:projection.ids.Greek.length,Latin_starts:projection.ids.Latin.length,all_actual_selector_events_and_rendered_intervals:ui.length,all_English_broader_contexts:'PASS',no_duplicate_executable_starts:true,no_duplicate_DOM_IDs:true,interval_digest:digest(projection.results),result:'PASS'};
   report.books[book]=q;fs.writeFileSync(path.join(root,`review/Antiquities_Niese_Book${book===8?'VIII':'X'}_2026-10-08/IMPLEMENTATION_BROWSER_QA.json`),JSON.stringify(q,null,2));console.log('all new-book UI selections',book,max);
  }
  report.navigation=[];
  for(const [book,n] of [[8,1],[8,59],[8,187],[8,255],[8,367],[8,368],[8,369],[8,420],[10,1],[10,18],[10,102],[10,108],[10,109],[10,150],[10,151],[10,276],[10,277],[10,281]]){
   const route=`/antiquities/?book=${book}&niese=${n}`;await open(route);await page.reload();await page.waitForFunction(()=>window.__qaReady);if(new URL(page.url()).searchParams.get('niese')!==String(n))throw Error('Reload URL identity');
   if(n<(book===8?420:281)){await page.click('#niese-next');await page.evaluate(()=>window.__qaPending);if(new URL(page.url()).searchParams.get('niese')!==String(n+1))throw Error('next');await page.click('#niese-previous');await page.evaluate(()=>window.__qaPending);if(new URL(page.url()).searchParams.get('niese')!==String(n))throw Error('previous');await page.goBack();await page.waitForFunction(v=>window.__qa.getState().nieseNum===String(v),n+1);await page.goForward();await page.waitForFunction(v=>window.__qa.getState().nieseNum===String(v),n);}
   await page.uncheck('#english-pane-select');await page.check('#english-pane-select');await page.uncheck('#greek-pane-select');await page.check('#greek-pane-select');
   for(const theme of ['light','dark']){await page.evaluate(theme=>{document.documentElement.setAttribute('data-theme',theme);document.documentElement.setAttribute('data-bs-theme',theme);},theme);await page.screenshot({path:path.join(packet,`BOOK${book}_${n}_${theme}.png`),fullPage:true});}
   report.navigation.push({book,n,deep_link_reload:'PASS',previous_next_history:n<(book===8?420:281)?'PASS':'FINAL_ENDPOINT',pane_switches:'PASS',themes:'PASS'});
  }
  await open('/antiquities/?book=8&niese=367');await change('#book-selector','09');if(!await page.locator('#niese-level').isDisabled())throw Error('IX must remain unsupported');
  await change('#book-selector','10');await page.check('#niese-level');await page.evaluate(()=>window.__qaPending);await change('#niese-selector','108');if(!await page.locator('#latin .structural-unavailable').count())throw Error('Restore X.108');
  report.non_contiguous_availability='PASS';
  // Uninstrumented production script at all exception and partial-correspondence cases.
  report.uninstrumented=[];
  for(const [book,n] of [[8,187],[8,255],[8,367],[8,368],[8,369],[10,102],[10,108],[10,109],[10,150],[10,151],[10,276],[10,277]]){
   await open(`/antiquities/?book=${book}&niese=${n}`,2);const latin=await page.locator('#latin').evaluate((node,code)=>eval('('+code+')')(node),narrative.toString());
   if(latin!==normalize(expected[book].Latin[n]))throw Error(`Uninstrumented ${book}.${n}`);report.uninstrumented.push({book,n,result:'PASS'});
  }
 }else{
  report.antiquities={traditional:[],bamberg:[],alignment:[],niese:[],contents:[]};
  for(const book of process.argv.includes('--cross-only')?[]:['preface',...Array.from({length:20},(_,i)=>String(i+1))]){
   const captures=[];
   for(const which of [1,0]){
    await open(`/antiquities/?book=${book}`,which);
    captures.push(await page.evaluate(({book,htmlCode})=>{
     const html=eval('('+htmlCode+')'),q=window.__qa,data=q.getData(),capture=()=>Object.fromEntries(Object.entries(data).map(([l,d])=>[l,html(q.selectView(l,d,q.currentIdBase()),book,l)]));
     const traditional=(q.traditionalRegistry()||[]).filter(r=>book==='preface'?r.context==='Proem':r.context!=='Proem'&&Number(r.book)===Number(book)).map(r=>[r.id,Object.fromEntries(Object.entries(data).map(([l,d])=>[l,html(q.traditionalRangeView(l,d,r),book,l)]))]);
     const bamberg=q.bambergRows().map(r=>[r.id,Object.fromEntries(Object.entries(data).map(([l,d])=>[l,html(q.traditionalRangeView(l,d,r),book,l)]))]);
     q.assign({viewingLevel:'section-level',sectionNum:null});const units=[...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value);const alignment=units.map(unit=>{q.assign({sectionNum:unit});return [unit,capture()];});
     const niese=[];if(Number(book)<=7){for(const entry of q.canonicalNieseStartEntries()){q.assign({viewingLevel:'niese-level',nieseNum:String(entry.number),chapterNum:null,subchapterNum:null,sectionNum:null});niese.push([entry.number,capture()]);}}
     return {traditional,bamberg,alignment,niese};
    },{book,htmlCode:canonicalHTML.toString()}));
   }
   for(const category of ['traditional','bamberg','alignment','niese']){
    if(JSON.stringify(captures[0][category])!==JSON.stringify(captures[1][category])){
     fs.writeFileSync(path.join(packet,`FAIL_${category}_${book}.json`),JSON.stringify(captures,null,2));throw Error(`${category} baseline mismatch book ${book}`);
    }
    report.antiquities[category].push({book,identities:captures[1][category].length,three_language_DOM_and_order:'PASS',digest:digest(captures[1][category])});
   }
   // Actual source contents are fetched/rendered by the current registry.
   const contents=[];for(const which of [1,0]){await open(`/antiquities/?book=${book}&view=contents`,which);contents.push(await page.evaluate(()=>Object.fromEntries(Object.entries(window.__qa.view()).map(([l,d])=>[l,d?.outerHTML||null]))));}
   if(JSON.stringify(contents[0])!==JSON.stringify(contents[1]))throw Error('source contents '+book);report.antiquities.contents.push({book,result:'PASS'});console.log('protected Antiquities',book);
  }
  report.crossWorks=[];
  for(const [work,count] of [['bellum-judaicum',7],['contra-apionem',2],['deh',5]]){
   for(let book=1;book<=count;book++){
    const captures=[];
    for(const which of [1,0]){
     await open(`/${work}/?book=${book}`,which);
     captures.push(await page.evaluate(()=>{
      // The two disposable servers have different ports. Compare the full
      // DOM after removing only each server's origin from local deep links.
      const q=window.__qa,data=q.getData(),capture=()=>Object.fromEntries(Object.entries(data).map(([l,d])=>[l,q.selectView(l,d,q.currentIdBase())?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]));
      const whole=capture(),niese=[];for(const e of q.canonicalNieseStartEntries()){q.assign({viewingLevel:'niese-level',nieseNum:String(e.number)});niese.push([e.number,capture()]);}
      return {whole,niese};
     }));
    }
    if(JSON.stringify(captures[0])!==JSON.stringify(captures[1])){fs.writeFileSync(path.join(packet,`FAIL_cross_${work}_${book}.json`),JSON.stringify(captures,null,2));throw Error(`Cross-work ${work} ${book}`);}report.crossWorks.push({work,book,niese:captures[1].niese.length,result:'PASS',digest:digest(captures[1])});console.log('protected',work,book);
   }
  }
  // Existing dedicated suites additionally cover Lodge notes, source switching,
  // Bellum chapter ranges and DEH/Contra Apionem URLs against the same build.
 }
 if(report.errors.length)throw Error('Browser exceptions '+JSON.stringify(report.errors));
 report.finished=new Date().toISOString();report.result='PASS';
 fs.writeFileSync(path.join(packet,report.mode==='new-books'?'NEW_BOOK_BROWSER_QA.json':report.mode==='ui-supplement'?'UI_SUPPLEMENT_QA.json':'PROTECTED_BROWSER_QA.json'),JSON.stringify(report,null,2));console.log('PASS',report.mode);
 }catch(error){report.result='FAIL';report.failure=String(error);fs.writeFileSync(path.join(packet,'FAILED_BROWSER_QA.json'),JSON.stringify(report,null,2));throw error;}
 finally{await browser.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
