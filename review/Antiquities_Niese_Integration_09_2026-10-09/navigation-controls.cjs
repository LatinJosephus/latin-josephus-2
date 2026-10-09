const {fs,path,chromium,packet,build,serve,digest}=require('./qa-common.cjs');
async function main(){
 const report={scope:'ACTUAL_PROTECTED_NAVIGATION_EVENTS',checks:[],errors:[]};
 const servers=[serve(path.join(build,'site')),serve(path.join(build,'baseline-site'))];
 await Promise.all(servers.map(s=>new Promise(ok=>s.listen(0,'127.0.0.1',ok))));
 const origins=servers.map(s=>`http://127.0.0.1:${s.address().port}`);report.origins=origins;
 const context=await chromium.launchPersistentContext('C:/workspace/Antiquities-Niese-09-integration-runtime-20261009/profile-controls',{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
 async function change(sel,v){await page.selectOption(sel,v);await page.evaluate(()=>window.__qaPending);}
 async function radio(sel){await page.check(sel);await page.evaluate(()=>window.__qaPending);}
 try{
  for(const kind of ['traditional','bamberg','alignment','Bellum']){
   const pair=[];
   for(const which of [1,0]){
    const route=kind==='Bellum'?'/bellum-judaicum/?book=1':'/antiquities/?book='+(kind==='alignment'?'8':'1');
    await page.goto(origins[which]+route);await page.waitForFunction(()=>window.__qaReady);
    if(kind==='traditional'){await radio('#chapter-level');await change('#chapter-selector','1');await radio('#subchapter-level');await change('#subchapter-selector','1');}
    if(kind==='bamberg'||kind==='alignment'){
     const prefix=kind==='bamberg'?'bamberg':'section';await radio('#'+prefix+'-level');
     const values=await page.locator('#'+prefix+'-selector').evaluate(el=>[...el.options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value));
     if(!values.length)throw Error('Missing executable menu '+kind);await change('#'+prefix+'-selector',values[Math.min(1,values.length-1)]);
    }
    if(kind==='Bellum'){await radio('#niese-level');await change('#niese-selector','1');await change('#english-source-selector','lodge1602');await page.uncheck('#lodge-notes-visible');await page.reload();await page.waitForFunction(()=>window.__qaReady);if(await page.locator('#lodge-notes-visible').isChecked())throw Error('Lodge note persistence');await page.check('#lodge-notes-visible');}
    const a=await page.evaluate(()=>({state:window.__qa.getState(),view:Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>[l,v?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]))}));
    const wanted={traditional:'subchapter-level',bamberg:'bamberg-level',alignment:'section-level',Bellum:'niese-level'}[kind];
    if(a.state.viewingLevel!==wanted)throw Error('Actual navigation state '+kind);pair.push(a);
   }
   if(JSON.stringify(pair[0])!==JSON.stringify(pair[1]))throw Error('Current canonical navigation projection '+kind);
   report.checks.push({kind,actual_state:pair[1].state,pane_projection_digest:digest(pair[1].view),current_canonical_comparison:'PASS',result:'PASS'});
  }
  if(report.errors.length)throw Error('Unexpected browser errors');report.result='PASS';fs.writeFileSync(path.join(packet,'NAVIGATION_CONTROLS_QA.json'),JSON.stringify(report,null,2)+'\n');console.log('PASS: actual traditional, Bamberg, Alignment and Bellum navigation states match current canonical');
 }catch(e){report.result='FAIL';report.failure=String(e);fs.writeFileSync(path.join(packet,'NAVIGATION_CONTROLS_FAILURE.json'),JSON.stringify(report,null,2)+'\n');throw e;}
 finally{await context.close();await Promise.all(servers.map(s=>new Promise(ok=>s.close(ok))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
