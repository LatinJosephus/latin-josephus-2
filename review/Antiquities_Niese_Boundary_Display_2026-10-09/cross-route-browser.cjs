const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium,serve}=require('../Antiquities_Niese_Integration_12_13_2026-10-09/qa-common.cjs');
const packet=__dirname,baseline=JSON.parse(fs.readFileSync(path.join(packet,'BASELINE.json'),'utf8'));
async function main(){
 const servers=[serve(baseline.baseline_site,false),serve(path.join(baseline.runtime,'site'),false)];await Promise.all(servers.map(s=>new Promise(r=>s.listen(0,'127.0.0.1',r))));
 const origins=servers.map(s=>`http://127.0.0.1:${s.address().port}`),browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),context=await browser.newContext(),page=await context.newPage(),report={routes:[],browserExceptions:[],consoleErrors:[],failedRequests:[],HTTPfailures:[]};
 page.on('pageerror',e=>report.browserExceptions.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push(m.text());});page.on('requestfailed',r=>report.failedRequests.push({url:r.url(),error:r.failure()?.errorText}));page.on('response',r=>{if(r.status()>=400)report.HTTPfailures.push({url:r.url(),status:r.status()});});
 try{
 for(const route of ['/deh/?book=1&chapter=1&unit=1','/deh/?book=5&chapter=1','/contra-apionem/?book=1&unit=1','/contra-apionem/?book=2&unit=1','/antiquities/?book=11&chapter=8&subchapter=4','/antiquities/?book=3&view=contents','/antiquities/?book=5&view=contents','/antiquities/?book=12&view=contents','/antiquities/?book=13&view=contents','/antiquities/?book=20&view=contents','/bellum-judaicum/?book=1&chapter=1','/bellum-judaicum/?book=4&chapter=1']){
  const snapshots=[];
  for(const which of [0,1]){
   await page.goto(origins[which]+route,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>document.querySelector('#book-selector')?.options.length>1&&document.querySelector('#latin tei-p,#latin .structural-unavailable,#latin .source-contents'));
   snapshots.push(await page.evaluate(()=>Object.fromEntries(['Latin','Greek','English'].map(l=>[l,document.getElementById(l.toLowerCase()).innerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')]))));
  }
  if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1]))throw Error('Protected actual route '+route);
  const before=snapshots[1];await page.reload();await page.waitForFunction(()=>document.querySelector('#book-selector')?.options.length>1&&document.querySelector('#latin tei-p,#latin .structural-unavailable,#latin .source-contents'));const after=await page.evaluate(()=>Object.fromEntries(['Latin','Greek','English'].map(l=>[l,document.getElementById(l.toLowerCase()).innerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')])));if(JSON.stringify(before)!==JSON.stringify(after))throw Error('Deep-link reload '+route);
  report.routes.push({route,baseline_candidate_three_language_DOM:'PASS',reload:'PASS',sha256:crypto.createHash('sha256').update(JSON.stringify(after)).digest('hex')});
 }
 if(report.browserExceptions.length||report.consoleErrors.length||report.failedRequests.length||report.HTTPfailures.length)throw Error('Protected route browser/asset errors');report.result='PASS';fs.writeFileSync(path.join(packet,'CROSS_ROUTE_QA.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({result:'PASS',routes:report.routes.length,browserErrors:0,failedAssets:0}));
 }finally{await browser.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
