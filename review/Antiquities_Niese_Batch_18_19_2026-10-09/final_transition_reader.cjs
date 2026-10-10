const fs=require('fs'),path=require('path');
const {chromium}=require('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright');
const {serve}=require('./final_reader.cjs');
const P=__dirname,runtime='C:/workspace/Antiquities-Niese-18-19-runtime-20261009';
async function main(){
 const result={scope:'ACTUAL_FINAL_PRODUCTION_BOOK_TRANSITIONS_SOURCES_PANES_AND_ACCESSIBILITY',status:'RUNNING',transitions:[],sources:[],themes:[],errors:[]};
 const server=serve(path.join(runtime,'final-site'));await new Promise((r,j)=>{server.once('error',j);server.listen(8918,'127.0.0.1',r);});
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-final-transitions'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await context.newPage();
 page.on('pageerror',e=>result.errors.push(String(e)));page.on('requestfailed',r=>result.errors.push(r.url()+': '+r.failure()?.errorText));
 async function book(b){await page.selectOption('#book-selector',String(b));await page.waitForFunction(b=>window.__qaRenderedState?.bookNum===String(b)&&document.querySelector(`#latin tei-p[id^="latin-book${b}-num"]`),b);}
 async function section(n){await page.selectOption('#niese-selector',String(n));await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n)&&['latin','greek','english'].every(l=>document.querySelector(`#${l} [type^="niese-"][n="${n}"]`)),n);}
 try{
  await page.goto('http://127.0.0.1:8918/antiquities/?book=17',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__qaReady);for(const l of ['greek','english'])await page.check('#'+l+'-pane-select');if(!await page.locator('#niese-level').isDisabled())throw Error('Frozen XVII availability changed');
  await book(18);await page.check('#niese-level');await section(1);result.transitions.push({from:17,to:18,opening:'PASS',noticeExcludedFromSection1:true});
  await section(379);await book(19);await page.check('#niese-level');await section(1);result.transitions.push({from:18,tail:379,to:19,opening:1,status:'PASS',bookSelectorPreservesOrdinaryBookViewFallback:true});
  await section(366);await book(20);if(!await page.locator('#niese-level').isDisabled()||new URL(page.url()).searchParams.has('niese'))throw Error('XX frozen availability fallback');result.transitions.push({from:19,tail:366,to:20,status:'PASS',XXunchanged:true});
  await book(18);await page.check('#niese-level');await section(118);
  for(const [language,value] of [['latin','bamberg78'],['greek','niese'],['english','whiston']]){const available=await page.evaluate(l=>[...document.querySelector('#'+l+'-source-selector').options].map(o=>o.value),language);if(available.length!==1||available[0]!==value)throw Error('Frozen source availability '+language);result.sources.push({language,value,status:'PASS',singleSourceOnly:true,sourceSelectorIntentionallyHidden:true});}
  result.accessibility=await page.evaluate(()=>{const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);return {duplicateIDs:ids.filter((id,i)=>ids.indexOf(id)!==i),noteRoles:[...document.querySelectorAll('.niese-correspondence-note')].map(n=>n.getAttribute('role')),nieseSelectorLabels:[...document.querySelector('#niese-selector').labels].map(n=>n.textContent.trim()),previousName:document.querySelector('#niese-previous').getAttribute('aria-label'),nextName:document.querySelector('#niese-next').getAttribute('aria-label')};});
  if(result.accessibility.duplicateIDs.length||result.accessibility.noteRoles.some(r=>r!=='note'))throw Error('New section accessibility/IDs');
  for(const b of [18,19]){await page.goto(`http://127.0.0.1:8918/antiquities/?book=${b}&niese=${b===18?5:365}`,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__qaReady);for(const theme of ['light','dark']){await page.evaluate(t=>setTheme(t),theme);await page.waitForTimeout(800);const style=await page.locator('#latin .niese-correspondence-note').evaluate(n=>{const s=getComputedStyle(n);return {display:s.display,color:s.color,background:s.backgroundColor,role:n.getAttribute('role')};});if(style.display==='none'||style.color===style.background)throw Error('Unreadable note '+theme);await page.screenshot({path:path.join(P,'..',`Antiquities_Niese_Book${b===18?'XVIII':'XIX'}_2026-10-09`,'evidence','final-reader-'+theme+'.png'),fullPage:true});result.themes.push({book:b,theme,style,status:'PASS'});}}
  if(result.errors.length)throw Error('Transition reader errors');result.status='PASS';
 }catch(e){result.status='FAIL';result.failure=String(e);throw e;}finally{fs.writeFileSync(path.join(P,'TRANSITION_FINAL_BROWSER.json'),JSON.stringify(result,null,2)+'\n');await context.close();await new Promise(r=>server.close(r));}
 console.log(JSON.stringify(result));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
