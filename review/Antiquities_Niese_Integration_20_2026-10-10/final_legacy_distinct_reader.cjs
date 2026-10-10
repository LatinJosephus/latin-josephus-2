// Direct legacy routes and physical-point resolution in the actual final reader.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright');
const {serve,narrative}=require('./qa-common18.cjs');
const P=__dirname,runtime='C:/workspace/Antiquities-Niese-20-integration-runtime-20261010';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
async function main(){
 const result={scope:'ACTUAL_FINAL_LEGACY_URLS_AND_DISTINCT_PHYSICAL_POINTS',status:'RUNNING',legacyRoutes:[],physicalPoints:[],errors:[]};
 const servers=['baseline-site','final-site'].map(s=>serve(path.join(runtime,s)));
 await Promise.all(servers.map(s=>new Promise((r,j)=>{s.once('error',j);s.listen(0,'127.0.0.1',r);})));const origins=servers.map(s=>'http://127.0.0.1:'+s.address().port);
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-final-legacy-distinct'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),pages=await Promise.all([context.newPage(),context.newPage()]);
 pages.forEach((p,i)=>{p.on('pageerror',e=>result.errors.push({side:i,error:String(e)}));p.on('requestfailed',r=>result.errors.push({side:i,url:r.url(),error:r.failure()?.errorText}));});
 async function open(query){await Promise.all(pages.map(async(p,i)=>{await p.goto(origins[i]+'/antiquities/?'+query,{waitUntil:'domcontentloaded'});await p.waitForFunction(()=>window.__qaReady);for(const l of ['greek','english'])await p.check('#'+l+'-pane-select');}));}
 try{
  const baseline=JSON.parse(fs.readFileSync(path.join(P,'BASELINE_CONTAINING_BROWSER.json'))),proof=JSON.parse(fs.readFileSync(path.join(P,'DISTINCT_PHYSICAL_POINT_PROOF.json')));
  for(const b of [18,19]){
   for(const n of baseline.books[b].legacy){await open(`book=${b}&chapter=${n}`);const a=await Promise.all(pages.map(p=>p.evaluate(code=>{const text=eval('('+code+')'),norm=s=>s.replace(/\s+/g,' ').trim();return {url:location.search,state:window.__qa.getState(),languages:Object.fromEntries(['latin','greek','english'].map(l=>[l,norm(text(document.querySelector('#'+l)))]))};},narrative.toString())));if(JSON.stringify(a[0])!==JSON.stringify(a[1]))throw Error('Legacy URL meaning changed '+b+'.'+n);result.legacyRoutes.push({book:b,chapter:n,resolvedQuery:a[0].url,state:a[0].state,status:'IDENTICAL_BASELINE_FINAL_LIVE_DOM',sha256:sha(JSON.stringify(a[0]))});}
   await open(`book=${b}`);
   for(const row of proof.filter(r=>r.book===b)){
    const actual=await pages[1].evaluate(({row,code})=>{const q=window.__qa,text=eval('('+code+')'),data=q.getData()[row.language];const records=[...q.traditionalRows('chapter'),...q.bambergRows()];return [row.traditional,row.bamberg].map(id=>{const record=records.find(r=>r.id===id),point=q.traditionalPoint(data,record[row.language]),p=point.node.closest('tei-p'),range=document.createRange();range.setStart(p,0);if(point.kind==='paragraph')range.setEnd(point.node,0);else range.setEndBefore(point.node);const wrapper=p.cloneNode(false);wrapper.appendChild(range.cloneContents());return {identity:id,paragraph:p.id,offset:Array.from(text(wrapper)).length,kind:point.kind,locator:record[row.language]};});},{row,code:narrative.toString()});
    const coords=[row.traditional_coordinate,row.bamberg_coordinate];for(let i=0;i<2;i++)if(actual[i].paragraph!==coords[i].stable_id||actual[i].offset!==coords[i].unit_offset)throw Error('Distinct physical point moved '+b+' '+row.language+' '+actual[i].identity);
    if(actual[1].offset-actual[0].offset!==row.delta||row.delta===0)throw Error('Physical points collapsed');result.physicalPoints.push({...row,actual,status:'DISTINCT_POINTS_IN_ACTUAL_FINAL_DOM'});
   }
  }
  if(result.legacyRoutes.length!==29||result.physicalPoints.length!==6||result.errors.length)throw Error('Incomplete legacy/physical proof');result.status='PASS';
 }catch(e){result.status='FAIL';result.failure=String(e);throw e;}finally{fs.writeFileSync(path.join(P,'LEGACY_DISTINCT_FINAL_BROWSER.json'),JSON.stringify(result,null,2)+'\n');await context.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
 console.log(JSON.stringify({status:result.status,legacyRoutes:result.legacyRoutes.length,physicalPoints:result.physicalPoints.length}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
