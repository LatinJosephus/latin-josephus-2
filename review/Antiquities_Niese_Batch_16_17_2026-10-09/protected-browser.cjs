const {fs,path,chromium,packet,runtime,candidate,baseline,sha,serve,listen,normalize,narrative,cleanContaining,open,change,capture,builtHashes}=require('./qa-common.cjs');
async function main(){
 const report={status:'RUNNING',purpose:'EXHAUSTIVE_5231_PRIOR_NIESE_AND_PROTECTED_STRUCTURAL_OTHER_WORKS',started:new Date().toISOString(),books:[],errors:[],consoleErrors:[],requestFailures:[],built_source_hashes:builtHashes()};
 const servers=[serve(baseline),serve(candidate),serve(candidate,false)];const origins=[];for(const server of servers)origins.push(await listen(server));report.origins=origins;
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-protected-regressions'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1500,height:1000}});
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push(m.text());});page.on('requestfailed',r=>report.requestFailures.push({url:r.url(),error:r.failure()?.errorText}));
 const prior=[1,2,3,4,5,6,7,8,9,10,12,13,14,15];let count=0;
 async function controls(book,which){
  await open(page,origins[which],`book=${book}`);
  return page.evaluate(({book,code})=>{
   const html=eval('('+code+')'),q=window.__qa,d=q.getData(),render=()=>Object.fromEntries(Object.entries(d).map(([l,data])=>[l,html(q.selectView(l,data,q.currentIdBase()),book,l)]));
   const chapters=(q.traditionalRegistry()||[]).filter(r=>book==='preface'?r.context==='Proem':r.context!=='Proem'&&Number(r.book)===Number(book)).map(r=>[r.id,Object.fromEntries(Object.entries(d).map(([l,data])=>[l,html(q.traditionalRangeView(l,data,r),book,l)]))]);
   const bamberg=q.bambergRows().map(r=>[r.id,Object.fromEntries(Object.entries(d).map(([l,data])=>[l,html(q.traditionalRangeView(l,data,r),book,l)]))]);
   q.assign({viewingLevel:'section-level',chapterNum:null,subchapterNum:null,bambergId:null,nieseNum:null,sectionNum:null});
   const units=[...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value);
   const alignment=units.map(n=>{q.assign({sectionNum:n});return [n,render()];});
   const legacy=[...new Set([...d.Latin.querySelectorAll('tei-milestone[unit="chapter"][n]')].map(m=>Number(m.getAttribute('n'))).filter(n=>n>0))]
    .map(n=>[n,Object.fromEntries(Object.entries(d).map(([l,data])=>[l,html(q.milestoneChapterView(l,data,n,false),book,l)]))]);
   return {chapters,bamberg,alignment,legacy};
  },{book,code:cleanContaining.toString()});
 }
 try{
  for(const book of prior){
   const captures=[];
   for(const which of [0,1]){
    await open(page,origins[which],`book=${book}`);
    captures.push(await page.evaluate(({book,textCode})=>{
     const text=eval('('+textCode+')'),q=window.__qa,data=q.getData();const entries=q.canonicalNieseStartEntries();
     return entries.map(e=>{
      q.assign({viewingLevel:'niese-level',nieseNum:String(e.number),chapterNum:null,subchapterNum:null,bambergId:null,sectionNum:null});
      const result={};for(const [language,d] of Object.entries(data)){
       const view=q.selectView(language,d,q.currentIdBase());result[language]={html:view?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null,text:text(view),unavailable:!!view?.querySelector('.structural-unavailable')};
      }return {number:e.number,result};
     });
    },{book,textCode:narrative.toString()}));
   }
   if(JSON.stringify(captures[0])!==JSON.stringify(captures[1])){fs.writeFileSync(path.join(packet,`PROTECTED_MISMATCH_BOOK${book}.json`),JSON.stringify(captures,null,2));throw Error('Protected prior Niese DOM/text/order '+book);}
   const identities=captures[1].map(x=>({number:x.number,languages:Object.fromEntries(Object.entries(x.result).map(([l,v])=>[l,{DOM_sha256:sha(v.html||''),text_sha256:sha(v.text||''),characters:(v.text||'').length,unavailable:v.unavailable}]))}));
   count+=identities.length;report.books.push({book,identities:identities.length,all_three_language_DOM_and_text:'PASS_EXACT_BASELINE_COMPARISON',selections:identities});
   // Actual selector events corroborate the exhaustive DOM suite at both ends
   // and a middle selection in every prior book.
   await page.check('#niese-level');await page.evaluate(()=>window.__qaPending);
   const events=[];for(const n of [...new Set([identities[0].number,identities[Math.floor(identities.length/2)].number,identities.at(-1).number])]){
    await change(page,'#niese-selector',n);const actual=await capture(page);
    if(actual.nieseValue!==String(n))throw Error('Protected selector '+book+'.'+n);
    for(const lang of ['Latin','Greek','English']){
     const expected=captures[1].find(x=>x.number===n).result[lang];
     if(actual.languages[lang].text!==expected.text||actual.languages[lang].unavailable!==expected.unavailable)throw Error('Protected actual pane '+book+'.'+n+' '+lang);
    }events.push({number:n,actual_selector:'PASS'});
   }report.books.at(-1).actual_selector_events=events;
   fs.writeFileSync(path.join(packet,'PROTECTED_BROWSER_PROGRESS.json'),JSON.stringify({book,prior_selections_checked:count,total:5231},null,2)+'\n');console.log('protected prior',book,identities.length,'cumulative',count);
  }
  if(count!==5231)throw Error('Protected census '+count);
  report.prior_Niese_selection_count=count;report.structural=[];report.contents=[];
  for(const book of ['preface',...Array.from({length:20},(_,i)=>i+1)]){
   const a=await controls(book,0),b=await controls(book,1);
   if(JSON.stringify(a)!==JSON.stringify(b)){fs.writeFileSync(path.join(packet,`PROTECTED_STRUCTURE_MISMATCH_${book}.json`),JSON.stringify({a,b},null,2));throw Error('Protected structures '+book);}
   report.structural.push({book,traditional:a.chapters.length,bamberg:a.bamberg.length,alignment:a.alignment.length,legacy:a.legacy.length,full_three_language_DOM_after_only_approved_marker_removal:'PASS',digest:sha(b)});
   const contents=[];for(const which of [0,1]){await open(page,origins[which],`book=${book}&view=contents`);contents.push(await page.evaluate(()=>Object.fromEntries(Object.entries(window.__qa.view()).map(([l,d])=>[l,d?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]))));}
   if(JSON.stringify(contents[0])!==JSON.stringify(contents[1]))throw Error('Source TOC '+book);report.contents.push({book,result:'PASS',digest:sha(contents[1])});console.log('protected structure/TOC',book);
  }
  report.other_works=[];
  for(const [work,books] of [['bellum-judaicum',7],['contra-apionem',2],['deh',5]])for(let book=1;book<=books;book++){
   const captures=[];
   for(const which of [0,1]){
    await open(page,origins[which],`book=${book}`,work);
    captures.push(await page.evaluate(()=>{
     const q=window.__qa,data=q.getData(),capture=()=>Object.fromEntries(Object.entries(data).map(([l,d])=>[l,q.selectView(l,d,q.currentIdBase())?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]));
     const whole=capture(),niese=[];for(const e of q.canonicalNieseStartEntries()){q.assign({viewingLevel:'niese-level',nieseNum:String(e.number)});niese.push([e.number,capture()]);}
     return {whole,niese};
    }));
   }
   if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Other work '+work+' '+book);
   report.other_works.push({work,book,whole_and_all_existing_Niese:'PASS',Niese_count:captures[1].niese.length,digest:sha(captures[1])});console.log('protected other work',work,book);
  }
  report.prior_exceptional_direct_URLs=[];
  const checks=[[8,186],[8,187],[8,255],[8,367],[8,368],[8,369],[9,239],[9,240],[9,241],[10,101],[10,108],[10,109],[10,150],[10,277],[12,248],[12,249],[13,213],[13,214],[13,215],[13,216],[14,162],[14,238],[14,239],[14,358],[14,388],[15,40],[15,338],[15,347],[15,425]];
  for(const [book,n] of checks){const values=[];for(const which of [0,2]){await open(page,origins[which],`book=${book}&niese=${n}`,'antiquities',which!==2);values.push((await capture(page)).languages);}
   if(JSON.stringify(values[0])!==JSON.stringify(values[1]))throw Error('Protected uninstrumented direct URL '+book+'.'+n);
   report.prior_exceptional_direct_URLs.push({book,n,result:'PASS'});
  }
  // Source-specific Bellum controls, including Cardwell, Whiston and Lodge.
  report.Bellum_witnesses=[];
  for(const english of ['whiston','lodge1602']){
   const a=[];for(const which of [0,1]){
    await open(page,origins[which],`book=1&niese=1&english=${english}`,'bellum-judaicum');
    a.push(await page.locator('#english').evaluate(el=>el.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')));
   }if(a[0]!==a[1])throw Error('Bellum witness '+english);report.Bellum_witnesses.push({english,result:'PASS'});
  }
  await open(page,origins[1],'book=1&niese=1&english=lodge1602','bellum-judaicum');const before=await page.locator('#english').innerHTML();
  await page.uncheck('#lodge-notes-visible');if(!await page.locator('#english').evaluate(el=>el.classList.contains('lodge-notes-hidden')))throw Error('Lodge note toggle');
  await page.reload();await page.waitForFunction(()=>window.__qaReady);if(await page.locator('#lodge-notes-visible').isChecked())throw Error('Lodge note reload');
  await page.check('#lodge-notes-visible');if(before!==await page.locator('#english').innerHTML())throw Error('Lodge note restoration');
  await change(page,'#english-source-selector','whiston');if(await page.locator('#lodge-notes-select').isVisible())throw Error('Whiston source switch');report.Lodge_note_source_reload='PASS';
  if(report.errors.length||report.consoleErrors.length||report.requestFailures.length)throw Error('Protected unexpected diagnostics '+JSON.stringify({errors:report.errors,console:report.consoleErrors,network:report.requestFailures}));
  report.status='PASS_ALL_5231_PRIOR_SELECTIONS_AND_PROTECTED_REGRESSIONS';report.finished=new Date().toISOString();
  fs.writeFileSync(path.join(packet,'PROTECTED_BROWSER_QA.json'),JSON.stringify(report,null,2)+'\n');console.log(report.status);
 }catch(e){report.status='FAIL';report.failure=String(e);fs.writeFileSync(path.join(packet,'PROTECTED_BROWSER_FAILURE.json'),JSON.stringify(report,null,2)+'\n');throw e;}
 finally{await context.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
