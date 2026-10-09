const fs=require('fs'),path=require('path'),crypto=require('crypto');
const common=require('../Antiquities_Niese_Integration_12_13_2026-10-09/qa-common.cjs');
const {chromium,serve}=common,packet=__dirname,baseline=JSON.parse(fs.readFileSync(path.join(packet,'BASELINE.json'),'utf8')),runtime=baseline.runtime;
async function main(){
 const mode=process.argv.includes('--baseline')?'baseline':'candidate',site=mode==='baseline'?baseline.baseline_site:path.join(runtime,'site'),server=serve(site);
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin=`http://127.0.0.1:${server.address().port}`,browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),context=await browser.newContext(),page=await context.newPage(),report={mode,books:[],browserExceptions:[],consoleErrors:[],failedRequests:[]};
 page.on('pageerror',e=>report.browserExceptions.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push(m.text());});page.on('requestfailed',r=>report.failedRequests.push({url:r.url(),error:r.failure()?.errorText}));
 try{
 for(const book of [1,2,3,4,5,6,7,8,9,10,12,13]){
  await page.goto(origin+`/antiquities/?book=${book}&niese=${book===1?27:1}`,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});
  const capture=await page.evaluate(async book=>{
   const q=window.__qa,data=q.getData(),numbers=[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>Number(o.value)),rows=[];
   const sha=async s=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))].map(n=>n.toString(16).padStart(2,'0')).join('');
   const plain=node=>{if(!node)return '';const c=node.cloneNode(true);c.querySelectorAll('tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable').forEach(n=>n.remove());return c.textContent.replace(/\s+/g,' ').trim();};
   const starts=Object.fromEntries(['Latin','Greek'].map(l=>[l,q.antiquitiesNieseStartEntries(l,data[l]).map(e=>({number:e.number,kind:e.kind,paragraph:e.node.closest('tei-p')?.id||null}))]));
   for(const n of numbers){
    q.assign({viewingLevel:'niese-level',nieseNum:String(n),chapterNum:null,subchapterNum:null,sectionNum:null,bambergId:null});
    const row={number:n};
    for(const l of ['Latin','Greek','English']){
     const v=q.selectView(l,data[l],q.currentIdBase()),ids=[...v?.querySelectorAll('[id]')||[]].map(e=>e.id);
     if(ids.length!==new Set(ids).size)throw Error('Duplicate view IDs '+book+'.'+n+' '+l);
     row[l]={html:await sha(v?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||''),narrative:await sha(plain(v)),unavailable:!!v?.querySelector('.structural-unavailable'),note:v?.querySelector('.niese-correspondence-note')?.textContent||null};
     if(l==='Latin'){
      const last=[...v?.querySelectorAll('tei-p')||[]].at(-1),start=starts.Latin.find(e=>e.number===n);
      if(last&&last.id&&start&&last.id!==start.paragraph){const prefix=last.cloneNode(true),labels=[...prefix.querySelectorAll('tei-num')].map(e=>e.textContent.trim());prefix.querySelectorAll('tei-num').forEach(e=>e.remove());if(labels.length&&!prefix.textContent.trim()&&!prefix.querySelector('*'))row.leakedLabelPrefix={paragraph:last.id,labels,HTML:last.outerHTML};}
     }
    }
    rows.push(row);
   }
   return {book,selection_count:numbers.length,starts,rows};
  },book);
  report.books.push(capture);console.log(mode,'Antiquities',book,capture.selection_count);
 }
 if(report.browserExceptions.length||report.consoleErrors.length||report.failedRequests.length)throw Error('Browser diagnostics');
 report.total=report.books.reduce((s,b)=>s+b.selection_count,0);if(report.total!==4315)throw Error('Current supported inventory count');
 report.leaks=report.books.flatMap(b=>b.rows.filter(r=>r.leakedLabelPrefix).map(r=>({book:b.book,niese:r.number,...r.leakedLabelPrefix})));
 if(mode==='candidate'){
  const previous=JSON.parse(fs.readFileSync(path.join(packet,'BASELINE_NIESE_PROJECTIONS.json'),'utf8')),changes=[];
  for(let i=0;i<report.books.length;i++){
   const before=previous.books[i],after=report.books[i];
   if(JSON.stringify(before.starts)!==JSON.stringify(after.starts)||before.selection_count!==after.selection_count)throw Error('Executable identities changed '+before.book);
   for(let j=0;j<after.rows.length;j++){
    const a=before.rows[j],b=after.rows[j];
    for(const l of ['Latin','Greek','English']){
     if(a[l].narrative!==b[l].narrative||a[l].unavailable!==b[l].unavailable||a[l].note!==b[l].note)throw Error('Narrative/availability/qualification changed '+before.book+'.'+a.number+' '+l);
     if(a[l].html!==b[l].html){if(l!=='Latin'||!a.leakedLabelPrefix||b.leakedLabelPrefix)throw Error('Unexpected DOM change '+before.book+'.'+a.number+' '+l);changes.push({book:before.book,niese:a.number,removed_label_only_fragment:a.leakedLabelPrefix,narrative_preserved:true});}
    }
   }
  }
  if(report.leaks.length||changes.length!==previous.leaks.length)throw Error('Boundary-label leakage not fully reconciled');
  report.display_only_changes=changes;report.all_4315_Niese_selections_narrative_availability_notices_and_identity_starts_preserved=true;
 }
 report.result='PASS';fs.writeFileSync(path.join(packet,mode==='baseline'?'BASELINE_NIESE_PROJECTIONS.json':'EQUIVALENT_LEAKAGE_QA.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({mode,result:report.result,total:report.total,leaks:report.leaks,changes:report.display_only_changes},null,2));
 }catch(e){report.result='FAIL';report.error=String(e);fs.writeFileSync(path.join(packet,`FAILED_${mode}_LEAKAGE.json`),JSON.stringify(report,null,2)+'\n');throw e;}
 finally{await browser.close();await new Promise(r=>server.close(r));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
