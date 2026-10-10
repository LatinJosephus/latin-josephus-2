const {fs,path,chromium,packet,root,runtime,candidate,baseline,sha,serve,listen,open,builtHashes}=require('./qa-common.cjs');
async function main(){
 const report={status:'RUNNING',purpose:'ACTUAL_BUILT_OTHER_WORKS_ALL_CHAPTERS_UNITS_AND_BELLUM_WITNESSES',started:new Date().toISOString(),checks:[],errors:[],built_source_hashes:builtHashes()};
 const servers=[serve(baseline),serve(candidate)],origins=[];for(const s of servers)origins.push(await listen(s));
 const profile=path.join(runtime,'browser-source-gates'),owner=path.join(profile,'TASK_OWNER.json');
 if(fs.existsSync(profile)){if(!fs.existsSync(owner)||JSON.parse(fs.readFileSync(owner,'utf8')).root!==root)throw Error('Profile ownership');}
 else{fs.mkdirSync(profile);fs.writeFileSync(owner,JSON.stringify({root,purpose:report.purpose}));}
 const context=await chromium.launchPersistentContext(profile,{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
 try{
  const cases=[];
  for(let b=1;b<=7;b++)for(const source of ['whiston','lodge1602'])cases.push(['bellum-judaicum',b,source]);
  for(const [work,count] of [['contra-apionem',2],['deh',5]])for(let b=1;b<=count;b++)cases.push([work,b,null]);
  for(const [work,book,source] of cases){
   const captures=[];
   for(const origin of origins){
    await open(page,origin,`book=${book}${source?'&english='+source:''}`,work);
    captures.push(await page.evaluate(()=>{
     const q=window.__qa,data=q.getData(),rows=[];
     const render=()=>Object.fromEntries(Object.entries(data).map(([l,d])=>[l,q.selectView(l,d,q.currentIdBase())?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]));
     rows.push(['whole',render()]);
     const niese=q.canonicalNieseStartEntries().map(x=>x.number);
     for(const n of niese){q.assign({viewingLevel:'niese-level',nieseNum:String(n),chapterNum:null,sectionNum:null});rows.push(['niese:'+n,render()]);}
     const chapters=[...document.querySelector('#chapter-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value);
     for(const chapter of chapters){
      q.assign({viewingLevel:'chapter-level',chapterNum:chapter,sectionNum:null,nieseNum:null});rows.push(['chapter:'+chapter,render()]);
      q.assign({viewingLevel:'section-level'});q.setSectionSelectOptions();
      for(const unit of [...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value)){
       q.assign({sectionNum:unit});rows.push(['unit:'+chapter+':'+unit,render()]);
      }
     }
     return {english_source:q.getState().sources.English,Latin_source:q.getState().sources.Latin,Niese:niese.length,chapters:chapters.length,rows};
    }));
   }
   if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error(`Source gate ${work} ${book} ${source}`);
   report.checks.push({work,book,source,Latin_source:captures[1].Latin_source,english_source:captures[1].english_source,
    Niese:captures[1].Niese,chapters:captures[1].chapters,alignment_units:captures[1].rows.filter(x=>x[0].startsWith('unit:')).length,
    total_three_language_views:captures[1].rows.length,result:'PASS_EXACT_BASELINE_DOM',digest:sha(captures[1])});
   console.log('protected source gate',work,book,source||'',captures[1].rows.length);
  }
  if(report.errors.length)throw Error('Source gate browser diagnostics');
  report.status='PASS_OTHER_WORKS_ALL_CHAPTERS_UNITS_AND_BELLUM_WITNESSES';report.finished=new Date().toISOString();
  fs.writeFileSync(path.join(packet,'PROTECTED_SOURCE_GATE_QA.json'),JSON.stringify(report,null,2)+'\n');console.log(report.status);
 }catch(e){report.status='FAIL';report.failure=String(e);fs.writeFileSync(path.join(packet,'PROTECTED_SOURCE_GATE_FAILURE.json'),JSON.stringify(report,null,2)+'\n');throw e;}
 finally{await context.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
