const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium,serve,narrative}=require('./qa-common.cjs');
const runtime='C:/workspace/Antiquities-Niese-14-15-integration-runtime-20261009';
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
async function main(){
 const servers=[serve(path.join(runtime,'baseline-site'),false),serve(path.join(runtime,'site'),false)];
 for(const s of servers)await new Promise(r=>s.listen(0,'127.0.0.1',r));
 const context=await chromium.launchPersistentContext(path.join(runtime,'profile-display-advance'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const report={build_record:JSON.parse(fs.readFileSync(path.join(__dirname,'BUILD_RECORD.json'))),scope:'UNINSTRUMENTED_FINAL_BUILD_AGAINST_INCORPORATED_CANONICAL_ADVANCE',result:'PENDING',cases:[],errors:[],failedRequests:[],HTTPfailures:[]};
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));page.on('requestfailed',r=>report.failedRequests.push(r.url()));page.on('response',r=>{if(r.status()>=400)report.HTTPfailures.push({url:r.url(),status:r.status()});});
 const forbidden=new Map([['6.268','[XII.viii]'],['6.270','[XIII.i]'],['10.107','[VII.iii.108]'],['10.149','[VIII.vi.151]'],['13.212','[VI.vii.213]']]);
 try{
 for(const [book,n] of [[10,106],[10,107],[10,108],[10,109],[10,148],[10,149],[10,150],[10,151],[6,267],[6,268],[6,269],[6,270],[6,271],[6,272],[13,212],[13,213],[13,214]]){
  const captures=[];for(let i=0;i<2;i++){
   const origin=`http://127.0.0.1:${servers[i].address().port}`;
   await page.goto(origin+`/antiquities/?book=${book}&niese=${n}`);
   await page.waitForFunction(n=>document.querySelector('#niese-selector')?.value===String(n)&&document.querySelector('#latin tei-p,#latin .structural-unavailable')&&document.querySelector('#greek tei-p')&&document.querySelector('#english tei-p'),n);
   captures.push(await page.evaluate(code=>{const narrative=eval('('+code+')'),ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return {duplicateIDs:ids.filter((x,i)=>ids.indexOf(x)!==i),panes:Object.fromEntries(['Latin','Greek','English'].map(l=>{const p=document.getElementById(l.toLowerCase());return [l,{html:p.innerHTML.replaceAll(location.origin,'LOCAL_ORIGIN'),text:narrative(p),labels:[...p.querySelectorAll('tei-num')].map(x=>x.textContent.trim()),unavailable:!!p.querySelector('.structural-unavailable')}];}))};},narrative.toString()));
  }
  if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Canonical display advance changed '+book+'.'+n);
  const c=captures[1],bad=forbidden.get(book+'.'+n);
  if(c.duplicateIDs.length||(bad&&c.panes.Latin.labels.includes(bad)))throw Error('Leaked citation tail '+book+'.'+n);
  if(book===10&&n===107&&!c.panes.Latin.text.endsWith('quae tamen oportunius declarauimus.'))throw Error('X107 ending');
  if(book===10&&n===108&&(!c.panes.Latin.unavailable||c.panes.Latin.text||!c.panes.Greek.text||!c.panes.English.text))throw Error('X108 independent witnesses');
  if(book===10&&n===109&&!c.panes.Latin.text.startsWith('Interea dum hoc cognouisset'))throw Error('X109 opening');
  report.cases.push({book,niese:n,result:'PASS',all_three_panes_exact_canonical: true,no_label_only_tail:!!bad,digest:hash(JSON.stringify(c))});
 }
 if(report.errors.length||report.failedRequests.length||report.HTTPfailures.length)throw Error('Browser/network error');
 report.result='PASS';
 }catch(e){report.result='FAIL';report.failure=String(e);throw e;}
 finally{fs.writeFileSync(path.join(__dirname,'CANONICAL_ADVANCE_READER_QA.json'),JSON.stringify(report,null,2)+'\n');await context.close();for(const s of servers)await new Promise(r=>s.close(r));}
 console.log('PASS canonical display advance,17 uninstrumented final-build selections');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
