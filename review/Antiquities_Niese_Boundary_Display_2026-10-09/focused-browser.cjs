const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium,serve,narrative}=require('../Antiquities_Niese_Integration_12_13_2026-10-09/qa-common.cjs');
const packet=__dirname,baseline=JSON.parse(fs.readFileSync(path.join(packet,'BASELINE.json'),'utf8')),runtime=baseline.runtime;
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
async function main(){
 const servers=[serve(baseline.baseline_site,false),serve(path.join(runtime,'site'),false)];await Promise.all(servers.map(s=>new Promise(r=>s.listen(0,'127.0.0.1',r))));
 const origins=servers.map(s=>`http://127.0.0.1:${s.address().port}`),browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),context=await browser.newContext({viewport:{width:1600,height:1050}}),page=await context.newPage(),report={scope:'UNINSTRUMENTED_BUILT_READER',Niese:[],broader:[],browserExceptions:[],consoleErrors:[],failedRequests:[],HTTPfailures:[]};
 page.on('pageerror',e=>report.browserExceptions.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push(m.text());});page.on('requestfailed',r=>report.failedRequests.push({url:r.url(),error:r.failure()?.errorText}));page.on('response',r=>{if(r.status()>=400)report.HTTPfailures.push({url:r.url(),status:r.status()});});
 async function open(route,which){await page.goto(origins[which]+route,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>document.querySelector('#book-selector')?.options.length>1&&document.querySelector('#latin tei-p,#latin .structural-unavailable'));
 }
 async function snapshot(){return page.evaluate(code=>{
  const text=eval('('+code+')'),ids=[...document.querySelectorAll('[id]')].map(n=>n.id),panes={};
  for(const l of ['Latin','Greek','English']){const p=document.getElementById(l.toLowerCase());panes[l]={HTML:p.innerHTML.replaceAll(location.origin,'LOCAL_ORIGIN'),narrative:text(p),labels:[...p.querySelectorAll('tei-num')].map(n=>n.textContent.trim()),absence:!!p.querySelector('.structural-unavailable')};}
  return {panes,duplicates:ids.filter((id,i)=>ids.indexOf(id)!==i),number:document.querySelector('#niese-selector').value};
 },narrative.toString());}
 try{
 const cases=[[10,106],[10,107],[10,108],[10,109],[10,148],[10,149],[10,150],[10,151],[6,267],[6,268],[6,269],[6,270],[6,271],[6,272],[13,212],[13,213],[13,214]];
 const expected=JSON.parse(fs.readFileSync(path.join(packet,'../Antiquities_Niese_Implementation_08_10_2026-10-09/EXPECTED_INTERVALS.json'),'utf8'));
 for(const [book,n] of cases){
  const route=`/antiquities/?book=${book}&niese=${n}`,snapshots=[];
  for(const which of [0,1]){await open(route,which);snapshots.push(await snapshot());if(book===10&&[107,108,109].includes(n))await page.screenshot({path:path.join(packet,`${which?'AFTER':'BEFORE'}_X_${n}.png`),fullPage:true});}
  const before=snapshots[0],after=snapshots[1];
  for(const l of ['Latin','Greek','English']){
   if(before.panes[l].narrative!==after.panes[l].narrative||before.panes[l].absence!==after.panes[l].absence)throw Error('Rendered narrative/absence changed '+route+' '+l);
   if(l!=='Latin'&&before.panes[l].HTML!==after.panes[l].HTML)throw Error('Other witness changed '+route);
  }
  if(after.number!==String(n)||after.duplicates.length)throw Error('URL identity/DOM ID regression '+route);
  if(book===10&&after.panes.Latin.narrative!==String(expected[10].Latin[n]||'').replace(/\s+/g,' ').trim())throw Error('Accepted Latin interval '+route);
  if(book===10&&n===107&&(after.panes.Latin.labels.includes('[VII.iii.108]')||!after.panes.Latin.narrative.endsWith('quae tamen oportunius declarauimus.')))throw Error('107 endpoint display');
  if(book===10&&n===108&&(!after.panes.Latin.absence||after.panes.Latin.narrative||!after.panes.Greek.narrative||!after.panes.English.narrative))throw Error('108 independent absence state');
  if(book===10&&n===109&&(!after.panes.Latin.narrative.startsWith('Interea dum hoc cognouisset')||after.panes.Latin.labels.includes('[VII.iii.108]')))throw Error('Do not relocate inherited108 into109');
  report.Niese.push({book,niese:n,route,narrative_and_availability_preserved:true,labels_before:before.panes.Latin.labels,labels_after:after.panes.Latin.labels,duplicate_DOM_IDs:0});
 }
 const broader=[['/antiquities/?book=10&chapter=7','[VII.iii.108]'],['/antiquities/?book=10&chapter=7&subchapter=3','[VII.iii.108]'],['/antiquities/?book=10&unit=108','[VII.iii.108]'],['/antiquities/?book=10&chapter=8&subchapter=6','[VIII.vi.151]'],['/antiquities/?book=6&chapter=12&subchapter=8','[XII.viii]'],['/antiquities/?book=6&chapter=13','[XIII.i]'],['/antiquities/?book=13&chapter=6','[VI.vii.213]']];
 for(const [route,label] of broader){
  const snapshots=[];for(const which of [0,1]){await open(route,which);snapshots.push(await snapshot());}
  if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1])||!snapshots[1].panes.Latin.labels.includes(label))throw Error('Legitimate broader label display '+route);
  report.broader.push({route,retained_label:label,all_three_panes_DOM_identical_to_baseline:true,sha256:hash(JSON.stringify(snapshots[1]))});
 }
 await open('/antiquities/?book=10&niese=106',1);await page.locator('#display-settings .accordion-button').click();
 for(const n of [107,108,109]){await page.click('#niese-next');await page.waitForFunction(n=>document.querySelector('#niese-selector').value===String(n),n);const text=await page.locator('#latin').evaluate((node,code)=>eval('('+code+')')(node),narrative.toString());if(text!==String(expected[10].Latin[n]||'').replace(/\s+/g,' ').trim())throw Error('Next navigation rendered interval '+n);}
 await page.click('#niese-previous');await page.waitForFunction(()=>document.querySelector('#latin .structural-unavailable'));
 await page.goBack();await page.waitForFunction(()=>document.querySelector('#niese-selector').value==='109');await page.goForward();await page.waitForFunction(()=>document.querySelector('#latin .structural-unavailable'));
 await page.reload();await page.waitForFunction(()=>document.querySelector('#latin .structural-unavailable'));if(new URL(page.url()).searchParams.get('niese')!=='108')throw Error('Reload identity');
 await page.locator('#display-settings .accordion-button').click();for(const l of ['english','greek']){await page.uncheck(`#${l}-pane-select`);await page.check(`#${l}-pane-select`);}report.navigation='106→107→108→109; previous, Back/Forward, reload and panes PASS';
 await open('/antiquities/?book=10&niese=107',1);const themes=[];
 for(const theme of ['light','dark']){await page.evaluate(t=>setTheme(t),theme);await page.waitForTimeout(550);themes.push(await page.evaluate(()=>({theme:document.documentElement.dataset.theme,background:getComputedStyle(document.body).backgroundColor})));await page.screenshot({path:path.join(packet,`AFTER_X_107_${theme}.png`),fullPage:true});}
 if(themes[0].background===themes[1].background)throw Error('Theme switching');report.themes=themes;
 if(report.browserExceptions.length||report.consoleErrors.length||report.failedRequests.length||report.HTTPfailures.length)throw Error('Unexpected browser/asset diagnostics');
 report.result='PASS';fs.writeFileSync(path.join(packet,'FOCUSED_BROWSER_QA.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({result:'PASS',Niese:report.Niese.length,broader:report.broader.length,navigation:report.navigation,browserErrors:0,failedAssets:0}));
 }catch(e){report.result='FAIL';report.failure=String(e);fs.writeFileSync(path.join(packet,'FAILED_FOCUSED_BROWSER_QA.json'),JSON.stringify(report,null,2)+'\n');throw e;}
 finally{await browser.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
