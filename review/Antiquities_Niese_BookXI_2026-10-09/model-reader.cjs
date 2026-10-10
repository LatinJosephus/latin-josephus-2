const {fs,path,chromium,runtime,load,save,norm,hash,serve,listen,narrative}=require('./qa-common.cjs');
async function main(){
 const report={scope:'302–347 transposition model rehearsal; remainder unreviewed',started:new Date().toISOString(),errors:[],selectors:[],ranges:[]};
 const s=serve(path.join(runtime,'model-build/site')),origin=await listen(s,8911),bs=serve(path.join(runtime,'model-build/baseline-site')),baseline=await listen(bs);
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-profile-model'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1500,height:1000}}),page=await context.newPage();
 page.on('pageerror',e=>report.errors.push(String(e)));const expected=load(path.join(__dirname,'MODEL_EXPECTED_INTERVALS.json'));
 try{
 await page.goto(origin+'/antiquities/?book=11&niese=302');await page.waitForFunction(()=>window.__qaReady);
 for(let n=302;n<=347;n++){
  await page.selectOption('#niese-selector',String(n));await page.evaluate(()=>window.__qaPending);
  const actual=await page.evaluate(code=>{const text=eval('('+code+')'),q=window.__qa,v=q.view();return {n:q.getState().nieseNum,text:Object.fromEntries(['Latin','Greek','English'].map(l=>[l,text(v[l])])),occurrences:[...v.Latin.querySelectorAll('[data-source-occurrence]')].map(x=>x.dataset.sourceOccurrence),ids:[...document.querySelectorAll('[id]')].map(x=>x.id)};},narrative.toString());
  for(const l of ['Latin','Greek','English'])if(actual.text[l]!==norm(expected[n][l]))throw Error(`${n} ${l} endpoint/content mismatch`);
  if(actual.n!==String(n)||new Set(actual.ids).size!==actual.ids.length)throw Error('State/duplicate IDs '+n);
  report.selectors.push({n,result:'PASS',content_sha256:hash(actual.text),occurrences:actual.occurrences});
 }
 for(const [a,b] of [[311,313],[325,327],[341,343],[310,314],[325,329],[340,347],[302,347]]){
  const ns=Array.from({length:b-a+1},(_,i)=>a+i),want=ns.map(n=>expected[n].Latin).join('');
  const actual=await page.evaluate(({ns,code})=>{const q=window.__qa,v=q.antiquitiesNieseFragmentView('Latin',q.getData().Latin,ns);return {text:eval('('+code+')')(v),occurrences:[...v.querySelectorAll('[data-source-occurrence]')].map(x=>x.dataset.sourceOccurrence),ids:[...v.querySelectorAll('[id]')].map(x=>x.id),labels:[...v.querySelectorAll('tei-num')].map(x=>x.textContent)};},{ns,code:narrative.toString()});
  if(actual.text!==norm(want)||new Set(actual.occurrences).size!==actual.occurrences.length||new Set(actual.ids).size!==actual.ids.length)throw Error('Range content/duplication '+a+'–'+b);
  if(ns.includes(312)&&(!actual.labels.includes('[BJ 4.105a]')||!actual.labels.includes('[BJ 4.105b]')))throw Error('Interpolation labels');
  report.ranges.push({a,b,result:'PASS',occurrences:actual.occurrences,text_sha256:hash(actual.text)});
 }
 report.preserved_views=[];
 for(const route of ['/antiquities/?book=11','/antiquities/?book=11&unit=306','/antiquities/?book=11&unit=312','/antiquities/?book=11&unit=321','/antiquities/?book=11&unit=326','/antiquities/?book=11&unit=340','/antiquities/?book=11&chapter=8','/antiquities/?book=11&chapter=8&subchapter=2','/antiquities/?book=11&chapter=8&subchapter=4','/antiquities/?book=11&chapter=8&subchapter=6']){
  const captures=[];for(const o of [baseline,origin]){await page.goto(o+route);await page.waitForFunction(()=>window.__qaReady);captures.push(await page.evaluate(()=>Object.fromEntries(['Latin','Greek','English'].map(l=>{const c=document.getElementById(l.toLowerCase()).cloneNode(true);c.querySelectorAll('tei-milestone[unit="niese"]').forEach(x=>x.remove());return[l,c.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')]}))));}
  if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Preserved view differs '+route);report.preserved_views.push({route,result:'PASS',digest:hash(captures[1])});
 }
 report.result=report.errors.length?'FAIL':'PASS';
 }catch(e){report.result='FAIL';report.failure=String(e);}finally{report.origin=origin;report.finished=new Date().toISOString();save(path.join(__dirname,'MODEL_READER_RESULTS.json'),report);await context.close();await new Promise(r=>s.close(r));await new Promise(r=>bs.close(r));}
 console.log(JSON.stringify({result:report.result,failure:report.failure,selectors:report.selectors.length,ranges:report.ranges.length,errors:report.errors}));if(report.result!=='PASS')process.exitCode=1;
}main().catch(e=>{console.error(e);process.exitCode=1;});
