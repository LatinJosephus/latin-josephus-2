const {fs,path,chromium,packet,root,build,expected,digest,serve,normalize,narrative,canonicalHTML}=require('./qa-common.cjs');
const pending=JSON.parse(fs.readFileSync(path.join(packet,'EXECUTABLE_IDENTITIES.json'),'utf8')).pending;
const controls=JSON.parse(fs.readFileSync(path.join(root,'review/Antiquities_Niese_Implementation_08_10_2026-10-09/EXPECTED_INTERVALS.json'),'utf8'));
async function listen(server,preferred=0){
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(preferred,'127.0.0.1',resolve);}).catch(async e=>{if(e.code!=='EADDRINUSE')throw e;await new Promise(r=>server.listen(0,'127.0.0.1',r));});
 return `http://127.0.0.1:${server.address().port}`;
}
async function main(){
 const report={scope:'ACTUAL_LOCAL_IX_BUILD',started:new Date().toISOString(),editorial_pending:pending,errors:[],consoleErrors:[],networkFailures:[]};
 const servers=[serve(path.join(build,'site')),serve(path.join(build,'baseline-site')),serve(path.join(build,'site'),false)];
 const origins=[await listen(servers[0],8909),await listen(servers[1]),await listen(servers[2])];report.origins=origins;
 const context=await chromium.launchPersistentContext('C:/workspace/Antiquities-Niese-09-runtime-20261009/profile-ix',{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1500,height:1000}});
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push(m.text());});page.on('requestfailed',r=>report.networkFailures.push({url:r.url(),reason:r.failure()?.errorText}));
 async function open(route,which=0){await page.goto(origins[which]+route,{waitUntil:'domcontentloaded'});if(which<2)await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});else await page.waitForFunction(()=>document.querySelector('#book-selector')?.options.length>1&&document.querySelector('#latin tei-p,#latin .structural-unavailable'),{},{timeout:60000});}
 async function change(selector,value){await page.selectOption(selector,value);await page.evaluate(()=>window.__qaPending);}
 async function capture(){return await page.evaluate(code=>{const text=eval('('+code+')');return Object.fromEntries(['Latin','Greek','English'].map(l=>[l,{text:text(document.querySelector('#'+l.toLowerCase())),unavailable:!!document.querySelector('#'+l.toLowerCase()+' .structural-unavailable'),partial:!!document.querySelector('#'+l.toLowerCase()+' .niese-correspondence-note'),context:!!document.querySelector('#'+l.toLowerCase()+' .niese-context-note')}]));},narrative.toString());}
 function verify(n,actual,book=9){
  for(const lang of ['Latin','Greek','English']){
   const wanted=book===9?(lang==='English'?expected[9].EnglishContext[n]:expected[9][lang][n]):lang==='English'?undefined:controls[book][lang][n];
   const held=book===9&&lang==='Latin'&&pending.length&&[239,240].includes(n);
   if(held){if(!actual[lang].unavailable||actual[lang].text)throw Error('Pending boundary notice '+n);continue;}
   if(wanted===null){if(!actual[lang].unavailable||actual[lang].text)throw Error(`${lang} unavailable ${book}.${n}`);}
   else if(wanted!==undefined&&actual[lang].text!==normalize(wanted))throw Error(`${lang} interval ${book}.${n}: ${actual[lang].text.slice(0,140)} != ${normalize(wanted).slice(0,140)}`);
   if(book===9&&lang==='English'&&wanted!==null&&!actual[lang].context)throw Error('Missing Whiston broader-context qualification '+n);
  }
  if(book===9&&n===110&&!actual.Latin.partial)throw Error('Missing partial survival notice IX.110');
 }
 try{
  await open('/antiquities/?book=9&niese=1');
  const menu=await page.locator('#niese-selector').evaluate(el=>[...el.options].filter(o=>o.value).map(o=>Number(o.value)));
  if(JSON.stringify(menu)!==JSON.stringify(Array.from({length:291},(_,i)=>i+1)))throw Error('IX menu coverage');
  const starts=await page.evaluate(()=>Object.fromEntries(['Latin','Greek'].map(l=>[l,window.__qa.antiquitiesNieseStartEntries(l,window.__qa.getData()[l]).map(e=>e.number)])));
  for(const l of ['Latin','Greek'])if(new Set(starts[l]).size!==starts[l].length)throw Error('Duplicate executable '+l+' claim');
  report.actual_selector_events=[];
  for(let n=1;n<=291;n++){
   await change('#niese-selector',String(n));const actual=await capture();verify(n,actual);
   const duplicate=await page.evaluate(()=>{const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);return ids.filter((id,i)=>ids.indexOf(id)!==i);});if(duplicate.length)throw Error('Duplicate DOM IDs '+n+': '+duplicate.join(','));
   const links=await page.locator('#latin a,#english a,#greek a').evaluateAll(nodes=>nodes.map(a=>({href:a.getAttribute('href'),brokenFragment:a.getAttribute('href')?.startsWith('#')&&!document.getElementById(a.getAttribute('href').slice(1))})));
   if(links.some(a=>a.href?.includes('undefined')||a.brokenFragment))throw Error('Unresolved IX reader link '+n+': '+JSON.stringify(links));
   report.actual_selector_events.push({n,result:'PASS',Latin:actual.Latin.unavailable?'PENDING_OR_UNAVAILABLE':'REPRESENTED',Greek:actual.Greek.unavailable?'UNAVAILABLE':'REPRESENTED',English:actual.English.unavailable?'UNAVAILABLE':'BROADER_CONTEXT',digest:digest(actual)});
  }
  report.identity_counts={selected:menu.length,Greek_starts:starts.Greek.length,Latin_starts:starts.Latin.length,expected_Latin_intervals:232,unavailable:59,pending_boundary:pending};
  console.log('IX actual selector events passed',menu.length);
  // Drive every existing Chapter/Subchapter range and compare its actual rendered extent
  // to the frozen baseline, stripping only the expressly authorized marker differences.
  await open('/antiquities/?book=9',1);
  const baseline=await page.evaluate(htmlCode=>{
   const html=eval('('+htmlCode+')'),q=window.__qa,data=q.getData();const result={chapters:{},subchapters:{}};
   for(const kind of ['chapter','subchapter'])for(const row of q.traditionalRegistry().filter(r=>Number(r.book)===9&&r.scheme===kind)){
    result[kind==='chapter'?'chapters':'subchapters'][row.id]={row,views:Object.fromEntries(Object.entries(data).map(([l,d])=>[l,html(q.traditionalRangeView(l,d,row),9,l)]))};
   }
   return result;
  },canonicalHTML.toString());
  // Registry uses level rather than kind in some frozen versions; fail on empty coverage.
  if(!Object.keys(baseline.chapters).length)throw Error('No actual IX chapter registry rows captured');
  await open('/antiquities/?book=9');report.traditional_ranges=[];
  for(const [kind,records] of Object.entries(baseline))for(const {row,views} of Object.values(records)){
   await page.check('#chapter-level');await page.evaluate(()=>window.__qaPending);await change('#chapter-selector',String(row.chapter));
   if(kind==='subchapters'){await page.check('#subchapter-level');await page.evaluate(()=>window.__qaPending);await change('#subchapter-selector',String(row.subchapter));}
   const actual=await page.evaluate(htmlCode=>{const html=eval('('+htmlCode+')');return Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>[l,html(v,9,l)]));},canonicalHTML.toString());
   if(JSON.stringify(actual)!==JSON.stringify(views))throw Error('Actual traditional extent '+row.id);
   report.traditional_ranges.push({id:row.id,kind,chapter:row.chapter,subchapter:row.subchapter,unavailable:Object.fromEntries(Object.entries(views).map(([l,v])=>[l,v?.includes('structural-unavailable')||false])),result:'PASS'});
  }
  console.log('IX actual traditional range events passed',report.traditional_ranges.length);
  report.navigation=[];
  for(const n of [1,49,50,51,52,108,109,110,111,180,181,182,215,216,217,238,239,240,241,290,291]){
   await open(`/antiquities/?book=9&niese=${n}`);verify(n,await capture());await page.reload();await page.waitForFunction(()=>window.__qaReady);verify(n,await capture());
   async function rendered(wanted){await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),wanted);verify(wanted,await capture());}
   if(n<291){await page.click('#niese-next');await rendered(n+1);await page.click('#niese-previous');await rendered(n);await page.goBack();await rendered(n+1);await page.goForward();await rendered(n);}else if(!await page.locator('#niese-next').isDisabled())throw Error('Final endpoint');
   if(n===1&&!await page.locator('#niese-previous').isDisabled())throw Error('Opening endpoint');
   for(const lang of ['english','greek']){await page.uncheck('#'+lang+'-pane-select');await page.check('#'+lang+'-pane-select');}
   if(!await page.locator('#latin-pane-select').isChecked()||!await page.locator('#latin-pane-select').isDisabled())throw Error('Established required Latin pane behavior');verify(n,await capture());
   report.navigation.push({n,deep_link_reload:'PASS',previous_next_history:'PASS',pane_switches:'PASS'});
  }
  await open('/antiquities/?book=9&niese=110');report.themes=[];
  for(const theme of ['light','dark']){await page.evaluate(t=>setTheme(t),theme);await page.waitForTimeout(550);await page.waitForFunction(()=>[...document.querySelectorAll('.lj-brand img')].every(im=>im.complete&&im.naturalWidth>0));const styles=await page.evaluate(()=>({theme:document.documentElement.dataset.theme,stored:localStorage.getItem('theme'),background:getComputedStyle(document.body).backgroundColor,noticeColor:getComputedStyle(document.querySelector('.niese-correspondence-note')).color,brandImagesLoaded:true}));if(styles.theme!==theme||styles.stored!==theme)throw Error('Theme application');report.themes.push(styles);await page.screenshot({path:path.join(packet,`IX110-${theme}.png`),fullPage:true});}
  if(report.themes[0].background===report.themes[1].background)throw Error('Theme did not change background');
  report.uninstrumented=[];
  for(const n of [1,50,51,80,109,110,111,181,216,239,240,291]){await open(`/antiquities/?book=9&niese=${n}`,2);verify(n,await capture());report.uninstrumented.push({book:9,n,result:'PASS'});}
  // Accepted exceptions and difficult neighbouring extents use unmodified production code.
  report.accepted_controls=[];
  for(const [b,n] of [[8,186],[8,187],[8,255],[8,367],[8,368],[8,369],[10,101],[10,102],[10,108],[10,109],[10,150],[10,151],[10,276],[10,277]]){await open(`/antiquities/?book=${b}&niese=${n}`,2);const actual=await capture();verify(n,actual,b);if(b===10&&n===108&&(!actual.Greek.text||!actual.English.text))throw Error('Independent X.108 Greek/English accessibility');report.accepted_controls.push({book:b,n,result:'PASS'});}
  await open('/bellum-judaicum/?book=1&niese=1&english=lodge1602');const before=await page.locator('#english').innerHTML();await page.uncheck('#lodge-notes-visible');if(!await page.locator('#english').evaluate(n=>n.classList.contains('lodge-notes-hidden')))throw Error('Lodge notes');await page.reload();await page.waitForFunction(()=>window.__qaReady);if(await page.locator('#lodge-notes-visible').isChecked())throw Error('Lodge reload');await page.check('#lodge-notes-visible');if(before!==await page.locator('#english').innerHTML())throw Error('Lodge restore');await change('#english-source-selector','whiston');if(await page.locator('#lodge-notes-select').isVisible())throw Error('Whiston source control');report.Lodge_notes_source_reload='PASS';
  if(report.errors.length||report.networkFailures.length||report.consoleErrors.length)throw Error('Unexpected diagnostics '+JSON.stringify({errors:report.errors,console:report.consoleErrors,network:report.networkFailures}));
  report.finished=new Date().toISOString();report.result=pending.length?'PASS_INDEPENDENT_WORK_PROVISIONAL':'PASS_CERTIFIED';fs.writeFileSync(path.join(packet,'NEW_BOOK_BROWSER_QA.json'),JSON.stringify(report,null,2));console.log(report.result);
 }catch(e){report.result='FAIL';report.failure=String(e);fs.writeFileSync(path.join(packet,'NEW_BOOK_BROWSER_FAILURE.json'),JSON.stringify(report,null,2));throw e;}
 finally{await context.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
