// Read-only focused controls adapted from the preserved cross-work structural harness.
const {fs,path,chromium,runtime,load,save,hash,serve,listen}=require('./qa-common18.cjs');
async function main(){
 const build=load(path.join(__dirname,'BUILD_CONTEXT.json')),servers=[serve(build.baseline_site),serve(build.site)],origins=[];
 for(const s of servers)origins.push(await listen(s));
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-focused-recovery'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await context.newPage();
 const report={status:'RUNNING',build,started:new Date().toISOString(),scope:'Fresh full DEH structural inputs and Bellum I/IV Whiston/Lodge controls following build-time cache-key normalization',controls:[],errors:[]};
 page.on('pageerror',e=>report.errors.push(String(e)));page.on('requestfailed',r=>report.errors.push(r.url()+':'+r.failure()?.errorText));page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text())});
 const open=async(route,i)=>{await page.goto(origins[i]+route);await page.waitForFunction(()=>window.__qaReady)};
 try{
 const routes=[...Array.from({length:5},(_,i)=>({work:'deh',book:i+1,source:null})),...[1,4].flatMap(book=>['whiston','lodge1602'].map(source=>({work:'bellum-judaicum',book,source})))];
 for(const r of routes){
  const captures=[];
  for(const i of [0,1]){
   await open(`/${r.work}/?book=${r.book}${r.source?'&english='+r.source:''}`,i);
   captures.push(await page.evaluate(()=>{
    const q=window.__qa,data=q.getData(),capture=()=>Object.fromEntries(Object.entries(data).map(([l,d])=>[l,q.selectView(l,d,q.currentIdBase())?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]));const whole=capture(),niese=[];
    for(const e of q.canonicalNieseStartEntries()){q.assign({viewingLevel:'niese-level',nieseNum:String(e.number),chapterNum:null,sectionNum:null});niese.push([e.number,capture()])}
    const ranges=[],chapters=[...document.querySelector('#chapter-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value);
    for(const chapter of chapters){q.assign({viewingLevel:'chapter-level',chapterNum:chapter,sectionNum:null,nieseNum:null});ranges.push(['chapter:'+chapter,capture()]);q.assign({viewingLevel:'section-level'});q.setSectionSelectOptions();for(const u of [...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value)){q.assign({sectionNum:u});ranges.push(['unit:'+chapter+':'+u,capture()])}}
    return{whole,niese,ranges};
   }));
  }
  if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Focused structural difference '+JSON.stringify(r));
  report.controls.push({...r,niese:captures[1].niese.length,ranges:captures[1].ranges.length,status:'PASS',digest:hash(captures[1])});
 }
 for(const source of ['whiston','lodge1602']){
  const captures=[];for(const i of [0,1]){await open('/bellum-judaicum/?book=4&niese=105&english='+source,i);captures.push(await page.evaluate(()=>Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>[l,v?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]))))}
  if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Bellum IV.105 attachment control '+source);
  report.controls.push({route:'BJ IV.105',source,status:'PASS',digest:hash(captures[1])});
 }
 await open('/bellum-judaicum/?book=1&niese=1&english=lodge1602',1);const before=await page.locator('#english').innerHTML();
 await page.uncheck('#lodge-notes-visible');if(!await page.locator('#english').evaluate(n=>n.classList.contains('lodge-notes-hidden')))throw Error('Lodge hide');
 await page.reload();await page.waitForFunction(()=>window.__qaReady);if(await page.locator('#lodge-notes-visible').isChecked())throw Error('Lodge reload');
 await page.check('#lodge-notes-visible');if(before!==await page.locator('#english').innerHTML())throw Error('Lodge restore');
 await page.selectOption('#english-source-selector','whiston');await page.evaluate(()=>window.__qaPending);if(await page.locator('#lodge-notes-select').isVisible())throw Error('Whiston switch');report.Lodge_Whiston_switching='PASS';
 if(report.errors.length)throw Error('Focused browser errors');report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=String(e)}finally{report.finished=new Date().toISOString();save(path.join(__dirname,'FRESH_FOCUSED_CONTROLS.json'),report);await context.close();for(const s of servers)await new Promise(r=>s.close(r))}
 console.log(JSON.stringify({status:report.status,controls:report.controls.length,failure:report.failure}));if(report.status!=='PASS')process.exitCode=1;
}
main().catch(e=>{console.error(e);process.exitCode=1});
