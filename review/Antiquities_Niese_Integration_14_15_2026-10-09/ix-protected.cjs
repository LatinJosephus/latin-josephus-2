const {fs,path,chromium,packet,root,build,expected,digest,serve,normalize,narrative,canonicalHTML}=require('./qa-common.cjs');
const controls=JSON.parse(fs.readFileSync(path.join(root,'review/Antiquities_Niese_Implementation_08_10_2026-10-09/EXPECTED_INTERVALS.json'),'utf8'));
const runtime='C:/workspace/Antiquities-Niese-14-15-integration-runtime-20261009';
async function listen(s,port=0){await new Promise((ok,no)=>{s.once('error',no);s.listen(port,'127.0.0.1',ok);}).catch(async e=>{if(e.code!=='EADDRINUSE')throw e;await new Promise(ok=>s.listen(0,'127.0.0.1',ok));});return `http://127.0.0.1:${s.address().port}`;}
async function main(){
 const report={build_record:JSON.parse(fs.readFileSync(path.join(packet,'BUILD_RECORD.json'),'utf8')),scope:'MERGED_XIV_XV_WITH_CURRENT_IX_XII_XIII_AND_WHISTON',started:new Date().toISOString(),IX:[],protected:[],coverage:[],contents:[],errors:[],consoleErrors:[],networkFailures:[]};
 const servers=[serve(path.join(build,'site')),serve(path.join(build,'baseline-site')),serve(path.join(build,'site'),false)];
 const origins=[await listen(servers[0],8915),await listen(servers[1]),await listen(servers[2])];report.origins=origins;
 const context=await chromium.launchPersistentContext(path.join(runtime,'profile-ix-protected'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1500,height:1000}});
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push(m.text());});page.on('requestfailed',r=>report.networkFailures.push({url:r.url(),reason:r.failure()?.errorText}));
 const save=name=>fs.writeFileSync(path.join(packet,name),JSON.stringify(report,null,2)+'\n');
 async function open(route,which=0){await page.goto(origins[which]+route,{waitUntil:'domcontentloaded'});if(which<2)await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});else await page.waitForFunction(()=>document.querySelector('#book-selector')?.options.length>1&&document.querySelector('#latin tei-p,#latin .structural-unavailable'),{},{timeout:60000});}
 async function change(selector,value){await page.selectOption(selector,value);await page.evaluate(()=>window.__qaPending);}
 async function capture(){return page.evaluate(code=>{const text=eval('('+code+')');return Object.fromEntries(['Latin','Greek','English'].map(l=>[l,{text:text(document.querySelector('#'+l.toLowerCase())),unavailable:!!document.querySelector('#'+l.toLowerCase()+' .structural-unavailable'),partial:!!document.querySelector('#'+l.toLowerCase()+' .niese-correspondence-note'),context:!!document.querySelector('#'+l.toLowerCase()+' .niese-context-note')}]));},narrative.toString());}
 function verify(book,n,a){for(const l of ['Greek','Latin','English']){const wanted=book===9?(l==='English'?expected[9].EnglishContext[n]:expected[9][l][n]):l==='English'?undefined:controls[book][l][n];if(wanted===null){if(!a[l].unavailable||a[l].text)throw Error(`Unavailable ${book}.${n} ${l}`);}else if(wanted!==undefined&&a[l].text!==normalize(wanted))throw Error(`Extent ${book}.${n} ${l}`);if(book===9&&l==='English'&&wanted!==null&&!a[l].context)throw Error('Whiston context qualification '+n);}if(book===9&&n===110&&!a.Latin.partial)throw Error('Partial110 notice');}
 async function rendered(n){await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n);verify(9,n,await capture());}
 async function noDuplicates(){const ids=await page.locator('[id]').evaluateAll(es=>es.map(e=>e.id));if(new Set(ids).size!==ids.length)throw Error('Duplicate IDs');}
 async function snapshot(){return page.evaluate(()=>Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>[l,v?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null])));}
 try{
  report.baseline_coverage=[];
  for(const which of [1,0])for(let book=1;book<=20;book++){
   await open(`/antiquities/?book=${book}`,which);const menu=await page.evaluate(()=>({disabled:document.querySelector('#niese-level').disabled,identities:[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>Number(o.value))}));
   const supported=book<=10||[12,13].includes(book)||(which===0&&[14,15].includes(book));if(menu.disabled===supported||new Set(menu.identities).size!==menu.identities.length)throw Error('Coverage '+book);if(!supported&&menu.identities.length)throw Error('Unexpected support '+book);
   if(book===9&&JSON.stringify(menu.identities)!==JSON.stringify(Array.from({length:291},(_,i)=>i+1)))throw Error('IX291 identities');
   (which===1?report.baseline_coverage:report.coverage).push({book,...menu,result:'PASS'});
  }
  report.total_selectable=report.coverage.reduce((n,x)=>n+x.identities.length,0);if(report.total_selectable!==5231)throw Error('Coverage total '+report.total_selectable);
  report.baseline_total_selectable=report.baseline_coverage.reduce((n,x)=>n+x.identities.length,0);
  if(report.baseline_total_selectable!==4315)throw Error('Actual starting canonical coverage');
  for(const record of report.coverage){const prior=report.baseline_coverage.find(x=>x.book===record.book);if(![14,15].includes(record.book)&&JSON.stringify(prior)!==JSON.stringify(record))throw Error('Protected availability set '+record.book);}
  if(report.total_selectable-report.baseline_total_selectable!==916)throw Error('Added coverage');
  for(const n of [1,50,51,109,110,180,181,182,215,216,217,239,240,241,291]){
   await open(`/antiquities/?book=9&niese=${n}`);const a=await capture();verify(9,n,a);await noDuplicates();
   await page.reload();await page.waitForFunction(()=>window.__qaReady);verify(9,n,await capture());
   if(n<291){await page.click('#niese-next');await rendered(n+1);await page.click('#niese-previous');await rendered(n);await page.goBack();await rendered(n+1);await page.goForward();await rendered(n);}else if(!await page.locator('#niese-next').isDisabled())throw Error('Ending navigation');
   if(n===1&&!await page.locator('#niese-previous').isDisabled())throw Error('Opening navigation');
   for(const l of ['english','greek']){await page.uncheck('#'+l+'-pane-select');await page.check('#'+l+'-pane-select');verify(9,n,await capture());}
   report.IX.push({n,result:'PASS',digest:digest(a),deep_link_reload:'PASS',previous_next_history:'PASS',independent_panes:'PASS'});
  }
  report.containing_views=[];
  for(const [level,subchapter] of [['chapter',''],['subchapter','3']]){
   await open('/antiquities/?book=9');await page.check('#chapter-level');await page.evaluate(()=>window.__qaPending);await change('#chapter-selector','11');
   if(subchapter){await page.check('#subchapter-level');await page.evaluate(()=>window.__qaPending);await change('#subchapter-selector',subchapter);}
   const a=await capture();for(const l of ['Greek','Latin'])for(const n of [239,240,241])if(!a[l].text.includes(normalize(expected[9][l][n])))throw Error('Containing view '+level+' '+l+' '+n);
   const integrated=await page.evaluate(code=>{const f=eval('('+code+')');return Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>[l,f(v,9,l)]));},canonicalHTML.toString());
   await open('/antiquities/?book=9',1);await page.check('#chapter-level');await page.evaluate(()=>window.__qaPending);await change('#chapter-selector','11');if(subchapter){await page.check('#subchapter-level');await page.evaluate(()=>window.__qaPending);await change('#subchapter-selector','3');}
   const before=await page.evaluate(code=>{const f=eval('('+code+')');return Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>[l,f(v,9,l)]));},canonicalHTML.toString());
   if(JSON.stringify(integrated)!==JSON.stringify(before))throw Error('Containing full baseline projection '+level);
   report.containing_views.push({chapter:11,subchapter:subchapter||null,level,complete_239_241:true,full_baseline_projection:'PASS',result:'PASS'});
  }
  for(const [book,n] of [[8,367],[8,369],[10,108]]){
   await open(`/antiquities/?book=${book}&niese=${n}`);const a=await capture();verify(book,n,a);if(book===10&&n===108&&(!a.Greek.text||!a.English.text||!a.Latin.unavailable))throw Error('Independent X108 display');report.protected.push({book,n,result:'PASS',digest:digest(a)});
  }
  // Actual controls are compared with current canonical, including complete pane markup.
  for(const route of ['/antiquities/?book=1&chapter=1&subchapter=1','/antiquities/?book=1&bamberg=B78-table1-row002','/antiquities/?book=8&unit=1','/bellum-judaicum/?book=1&niese=1','/bellum-judaicum/?book=1&niese=1&english=lodge1602']){
   const pair=[];for(const which of [1,0]){await open(route,which);pair.push(await snapshot());}if(JSON.stringify(pair[0])!==JSON.stringify(pair[1]))throw Error('Protected route '+route);report.protected.push({route,result:'PASS',current_canonical_projection:digest(pair[1])});
  }
  // Retain the intervening Whiston source index and its independent entry counts.
  for(const book of [8,9,10]){
   const pair=[];for(const which of [1,0]){await open(`/antiquities/?book=${book}&view=contents`,which);pair.push(await snapshot());}
   if(JSON.stringify(pair[0])!==JSON.stringify(pair[1]))throw Error('Intervening contents '+book);
   const counts=await page.evaluate(()=>({English:document.querySelectorAll('#english .source-contents tei-item tei-reg').length,Greek:document.querySelectorAll('#greek .source-contents tei-item,#greek .source-contents tei-p').length}));
   if(counts.English!==({8:15,9:14,10:11})[book])throw Error('Whiston contents count '+book);report.contents.push({book,...counts,current_canonical_projection:'PASS',result:'PASS'});
  }
  await open('/antiquities/?book=9&view=contents');await page.check('#niese-level');await page.evaluate(()=>window.__qaPending);await change('#niese-selector','240');verify(9,240,await capture());await change('#chapter-selector','contents');if(!await page.locator('#english .source-contents').count())throw Error('IX contents roundtrip');report.contents_roundtrip='PASS';
  report.new_book_contents_roundtrip=[];
  for(const [book,n] of [[12,248],[13,214],[14,388],[15,40]]){
   const pair=[];for(const which of [1,0]){await open(`/antiquities/?book=${book}&view=contents`,which);pair.push(await snapshot());}
   if(JSON.stringify(pair[0])!==JSON.stringify(pair[1]))throw Error('New-book current Whiston contents '+book);
   await page.check('#niese-level');await page.evaluate(()=>window.__qaPending);await change('#niese-selector',String(n));
   if(!await page.locator('#greek tei-p').count()||!await page.locator('#english tei-p').count())throw Error('New-book contents to Niese witnesses');
   if(book===12&&!await page.locator('#latin .structural-unavailable').count())throw Error('XII248 contents route qualification');
   if(book===13&&!await page.locator('#latin').textContent().then(t=>t.includes('Itaque iudaei feliciter')))throw Error('XIII214 contents route');
   await change('#chapter-selector','contents');
   if(JSON.stringify(await snapshot())!==JSON.stringify(pair[1]))throw Error('New-book Niese to contents projection '+book);
   const count=await page.locator('#english .source-contents tei-item tei-reg').count();if(count!==({12:11,13:16,14:16,15:11})[book])throw Error('New-book Whiston index count');
   report.new_book_contents_roundtrip.push({book,n,English_entries:count,result:'PASS'});
  }
  report.production=[];for(const n of [1,50,51,109,110,181,216,239,240,241,291]){await open(`/antiquities/?book=9&niese=${n}`,2);verify(9,n,await capture());await noDuplicates();report.production.push({n,result:'PASS'});}
  report.themes=[];for(const theme of ['light','dark']){await open('/antiquities/?book=9&niese=240',2);await page.evaluate(t=>setTheme(t),theme);await page.waitForTimeout(550);verify(9,240,await capture());await page.screenshot({path:path.join(packet,`IX240-integration-${theme}.png`),fullPage:true});report.themes.push({theme,result:'PASS'});}
  if(report.errors.length||report.consoleErrors.length||report.networkFailures.length)throw Error('Unexpected diagnostics '+JSON.stringify({errors:report.errors,console:report.consoleErrors,network:report.networkFailures}));
  report.finished=new Date().toISOString();report.result='PASS';save('IX_CURRENT_CANONICAL_QA.json');console.log('PASS: focused integration reader, current-canonical protected routes, contents and5231 selections');
 }catch(e){report.result='FAIL';report.failure=String(e);save('IX_CURRENT_CANONICAL_FAILURE.json');throw e;}
 finally{await context.close();await Promise.all(servers.map(s=>new Promise(ok=>s.close(ok))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
