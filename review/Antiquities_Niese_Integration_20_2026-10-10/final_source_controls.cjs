// Exercise visible protected source controls, comparing with independently loaded routes.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright');
const {serve,narrative}=require('./qa-common18.cjs');
const P=__dirname,runtime='C:/workspace/Antiquities-Niese-20-integration-runtime-20261010',sha=x=>crypto.createHash('sha256').update(x).digest('hex');
async function main(){
 const result={scope:'PROTECTED_BELLUM_SOURCE_SELECTOR_EVENTS',status:'RUNNING',events:[],errors:[]};
 const servers=['baseline-site','final-site'].map(s=>serve(path.join(runtime,s)));await Promise.all(servers.map(s=>new Promise((r,j)=>{s.once('error',j);s.listen(0,'127.0.0.1',r);})));const origins=servers.map(s=>'http://127.0.0.1:'+s.address().port);
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-final-source-controls'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),pages=await Promise.all([context.newPage(),context.newPage()]);
 pages.forEach((p,i)=>{p.on('pageerror',e=>result.errors.push({side:i,error:String(e)}));p.on('requestfailed',r=>result.errors.push({side:i,url:r.url(),error:r.failure()?.errorText}));});
 async function snapshot(p){return p.evaluate(code=>{const text=eval('('+code+')');return Object.fromEntries(['latin','greek','english'].map(l=>[l,text(document.querySelector('#'+l)).replace(/\s+/g,' ').trim()]));},narrative.toString());}
 async function open(source){await Promise.all(pages.map(async(p,i)=>{await p.goto(origins[i]+`/bellum-judaicum/?book=1&niese=1&latin=cardwell&english=${source}`,{waitUntil:'domcontentloaded'});await p.waitForFunction(()=>window.__qaReady);for(const l of ['greek','english'])await p.check('#'+l+'-pane-select');}));}
 try{
  const expected={};for(const source of ['whiston','lodge1602']){await open(source);const a=await Promise.all(pages.map(snapshot));if(JSON.stringify(a[0])!==JSON.stringify(a[1]))throw Error('Independent source route differs '+source);expected[source]=a[0];}
  if(expected.whiston.english===expected.lodge1602.english)throw Error('Source switch did not distinguish witness');
  for(const source of ['whiston','lodge1602','whiston']){
   await Promise.all(pages.map(async p=>{await p.selectOption('#english-source-selector',source);await p.waitForFunction(({source,expected,code})=>{const text=eval('('+code+')');return window.__qa.getState().sources.English===source&&['latin','greek','english'].every(l=>text(document.querySelector('#'+l)).replace(/\s+/g,' ').trim()===expected[l]);},{source,expected:expected[source],code:narrative.toString()});}));
   const actual=await Promise.all(pages.map(snapshot));if(JSON.stringify(actual[0])!==JSON.stringify(actual[1]))throw Error('Protected source selector changed');
   const states=await Promise.all(pages.map(p=>p.evaluate(()=>({sources:window.__qa.getState().sources,url:location.search,englishSelector:document.querySelector('#english-source-selector').value}))));if(JSON.stringify(states[0])!==JSON.stringify(states[1])||states[0].sources.Latin!=='cardwell')throw Error('Protected source state differs');result.events.push({source,state:states[0],status:'BASELINE_FINAL_SELECTOR_EVENT_IDENTICAL_TO_INDEPENDENT_ROUTE',sha256:sha(JSON.stringify(actual[0]))});
  }
  if(result.errors.length)throw Error('Source-control browser errors');result.status='PASS';
 }catch(e){result.status='FAIL';result.failure=String(e);throw e;}finally{fs.writeFileSync(path.join(P,'SOURCE_CONTROLS_FINAL_BROWSER.json'),JSON.stringify(result,null,2)+'\n');await context.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
 console.log(JSON.stringify({status:result.status,sourceControlEvents:result.events.length}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
