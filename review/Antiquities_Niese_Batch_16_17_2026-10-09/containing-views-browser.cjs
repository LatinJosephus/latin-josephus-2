const {fs,path,chromium,packet,runtime,candidate,sha,serve,listen,cleanContaining,open,builtHashes}=require('./qa-common.cjs');
const frozen=JSON.parse(fs.readFileSync(path.join(packet,'BASELINE_READER_CAPTURE.json'),'utf8'));
async function main(){
 const report={status:'RUNNING',purpose:'ACTUAL_ALL_311_CONTAINING_VIEWS_AND_35_LEGACY_ENDPOINTS',started:new Date().toISOString(),books:{},errors:[],built_source_hashes:builtHashes()};
 const server=serve(candidate);const origin=await listen(server);report.origin=origin;
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-containing-views'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
 try{
  for(const b of [16,17]){
   const checked=[];const old=frozen.books[b];
   for(const item of old.views){
    await open(page,origin,item.query);
    const comparison=await page.evaluate(({item,book})=>{
     function clean(node,language){
      const c=node.cloneNode(true);c.querySelectorAll('h3,.niese-context-note,.niese-correspondence-note,tei-milestone[unit^="niese"]').forEach(x=>x.remove());
      if(language==='greek')c.querySelectorAll('tei-num').forEach(x=>x.remove());
      return c.innerHTML.replaceAll(location.origin,'LOCAL_ORIGIN');
     }
     const result={};for(const lang of ['latin','greek','english']){
      const original=document.createElement('div');original.innerHTML=item.panes[lang].html;
      const actual=document.querySelector('#'+lang);const before=clean(original,lang),after=clean(actual,lang);
      result[lang]={before,after,match:before===after};
     }
     const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);
     return {languages:result,state:window.__qa.getState(),duplicates:ids.filter((id,i)=>ids.indexOf(id)!==i)};
    },{item,book:b});
    if(Object.values(comparison.languages).some(x=>!x.match)){
     fs.writeFileSync(path.join(packet,`CONTAINING_MISMATCH_${b}.json`),JSON.stringify({item,comparison},null,2));throw Error('Containing DOM/endpoint mismatch '+b+' '+item.query);
    }
    if(JSON.stringify(comparison.duplicates)!==JSON.stringify(item.duplicateIDs))throw Error('Containing new DOM ID regression '+item.query);
    for(const k of ['bookNum','chapterNum','subchapterNum','bambergId','sectionNum','viewingLevel'])if(comparison.state[k]!==item.state[k])throw Error('Containing state '+k+' '+item.query);
    checked.push({query:item.query,scheme:item.scheme,result:'PASS_EXACT_BASELINE_DOM_AFTER_APPROVED_MARKER_REMOVAL',digest:sha(Object.fromEntries(Object.entries(comparison.languages).map(([l,x])=>[l,x.after]))),baseline_duplicates:comparison.duplicates});
    if(checked.length%40===0)console.log('containing',b,checked.length,'/',old.views.length);
   }
   await open(page,origin,`book=${b}`);
   const legacy=await page.evaluate(({numbers,code})=>{
    const html=eval('('+code+')'),q=window.__qa,data=q.getData();return numbers.map(n=>({number:n,languages:Object.fromEntries(Object.entries(data).map(([l,d])=>[l,html(q.milestoneChapterView(l,d,n,false),window.__qa.getState().bookNum,l)]))}));
   },{numbers:old.legacy_chapter_ranges.map(x=>x.number),code:cleanContaining.toString()});
   const normalized=await page.evaluate(({rows,code,book})=>{
    const html=eval('('+code+')');return rows.map(r=>({number:r.number,languages:Object.fromEntries(Object.entries(r.languages).map(([l,v])=>{const holder=document.createElement('div');holder.innerHTML=v.html;return [l,html(holder.firstElementChild,book,l)];}))}));
   },{rows:old.legacy_chapter_ranges,code:cleanContaining.toString(),book:b});
   // Frozen captures use Latin/Greek/English key order; the loader resolves
   // independent language requests concurrently. Compare language values.
   if(legacy.length!==normalized.length||legacy.some((r,i)=>r.number!==normalized[i].number||['Latin','Greek','English'].some(l=>r.languages[l]!==normalized[i].languages[l]))){fs.writeFileSync(path.join(packet,`LEGACY_ENDPOINT_MISMATCH_${b}.json`),JSON.stringify({before:normalized,after:legacy},null,2));throw Error('Legacy chapter endpoints '+b);}
   report.books[b]={status:'PASS',views:checked,containing_view_count:checked.length,legacy_chapters:legacy.map(x=>({number:x.number,result:'PASS_EXACT_ENDPOINTS',digest:sha(x.languages)}))};
   console.log('containing complete',b,checked.length,'legacy',legacy.length);
  }
  if(report.errors.length)throw Error('Containing browser exceptions');
  report.status='PASS_ALL_311_CONTAINING_VIEWS_AND_35_LEGACY_ENDPOINTS';report.finished=new Date().toISOString();
  fs.writeFileSync(path.join(packet,'CONTAINING_VIEWS_BROWSER_QA.json'),JSON.stringify(report,null,2)+'\n');console.log(report.status);
 }catch(e){report.status='FAIL';report.failure=String(e);fs.writeFileSync(path.join(packet,'CONTAINING_VIEWS_BROWSER_FAILURE.json'),JSON.stringify(report,null,2)+'\n');throw e;}
 finally{await context.close();await new Promise(r=>server.close(r));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
