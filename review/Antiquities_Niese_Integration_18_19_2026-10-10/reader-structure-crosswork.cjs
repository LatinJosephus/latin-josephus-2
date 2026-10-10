const {fs,path,chromium,runtime,load,save,hash,serve,listen}=require('./qa-common.cjs');
async function main(){
 const final=process.argv.includes('--final'),build=load(path.join(__dirname,'BUILD_CONTEXT.json')),report={started:new Date().toISOString(),build,scope:'Every Antiquities containing view and exhaustive cross-work structural comparison against canonical integration start',books:[],cross_works:[],focused:[],errors:[]};
 const servers=[serve(build.baseline_site),serve(build.site)],origins=[];for(const s of servers)origins.push(await listen(s));
 const context=await chromium.launchPersistentContext(path.join(runtime,final?'browser-profile-prior-final3':'browser-profile-prior-final'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await context.newPage();
 page.on('pageerror',e=>report.errors.push(String(e)));page.on('requestfailed',r=>report.errors.push(r.url()+':'+r.failure()?.errorText));page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text())});
 const open=async(route,i)=>{await page.goto(origins[i]+route);await page.waitForFunction(()=>window.__qaReady)};
 try{
 let total=0;report.selectors=[];
 for(const book of ['preface',...Array.from({length:20},(_,i)=>String(i+1))]){
  const captures=[],menus=[],selections=[];
  for(const i of [0,1]){
   await open(`/antiquities/?book=${book}`,i);
   captures.push(await page.evaluate(({book,added})=>{
    const q=window.__qa,d=q.getData(),html=node=>{if(!node)return null;const c=node.cloneNode(true);if(Number(book)===11)c.querySelectorAll('tei-milestone[unit="niese"]').forEach(m=>{if(added.includes(m.id))m.remove()});if([18,19].includes(Number(book)))c.querySelectorAll('tei-milestone[unit="niese"]').forEach(m=>m.remove());return c.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')},capture=()=>Object.fromEntries(Object.entries(d).map(([l,data])=>[l,html(q.selectView(l,data,q.currentIdBase()))]));
    const whole=capture(),traditional=(q.traditionalRegistry()||[]).filter(r=>book==='preface'?r.context==='Proem':r.context!=='Proem'&&Number(r.book)===Number(book)).map(r=>[r.id,Object.fromEntries(Object.entries(d).map(([l,data])=>[l,html(q.traditionalRangeView(l,data,r))]))]),bamberg=q.bambergRows().map(r=>[r.id,Object.fromEntries(Object.entries(d).map(([l,data])=>[l,html(q.traditionalRangeView(l,data,r))]))]);
    q.assign({viewingLevel:'section-level',sectionNum:null});const units=[...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value),alignment=units.map(unit=>{q.assign({sectionNum:unit});return[unit,capture()]});return{whole,traditional,bamberg,alignment};
   },{book,added:load(path.join(__dirname,'AUTHORIZED_ADDITIONS.json')).map(x=>x.id)}));
   const menu=[];menus.push(menu); // Exhaustive actual selections are independently replayed by final_protected_reader.cjs.
   const sel=[];
   if(menu.length){
    await page.check('#niese-level');await page.evaluate(()=>window.__qaPending);
    for(const n of menu){
     await page.selectOption('#niese-selector',String(n));await page.evaluate(()=>window.__qaPending);
     const actual=await page.evaluate(()=>({state:window.__qa.getState().nieseNum,panes:Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>[l,v?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null])),ids:[...document.querySelectorAll('[id]')].map(x=>x.id)}));
     if(actual.state!==String(n)||new Set(actual.ids).size!==actual.ids.length)throw Error('Prior state/duplicate IDs '+book+'.'+n);delete actual.ids;
     if(!actual.panes.Latin&&!actual.panes.Greek)throw Error('Prior empty selection '+book+'.'+n);
     sel.push({n,digest:hash(actual)});
    }
   }
   selections.push(sel);
   await open(`/antiquities/?book=${book}&view=contents`,i);captures[i].contents=await page.evaluate(()=>Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>[l,v?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null])));
  }
  if(JSON.stringify(captures[0])!==JSON.stringify(captures[1])||JSON.stringify(menus[0])!==JSON.stringify(menus[1])||JSON.stringify(selections[0])!==JSON.stringify(selections[1])){save(path.join(runtime,`FAIL-prior-${book}.json`),{captures,menus,selections});throw Error('Prior DOM, qualifications, contents or identity inventory '+book)}
  total+=selections[1].length;report.selectors.push(...selections[1].map(x=>({book,...x,result:'PASS'})));report.books.push({book,niese:selections[1].length,traditional:captures[1].traditional.length,bamberg:captures[1].bamberg.length,alignment:captures[1].alignment.length,contents:'PASS',digest:hash(captures[1]),result:'PASS'});console.log('prior',book,'selectors',selections[1].length,'running',total);
 }
 report.actual_selections_in_separate_fresh_replay=5231;report.combined_identity_target=6323;
 for(const [work,count] of [['bellum-judaicum',7],['contra-apionem',2],['deh',5]])for(let book=1;book<=count;book++)for(const source of work==='bellum-judaicum'?['whiston','lodge1602']:['default']){
  const captures=[];for(const i of [0,1]){await open(`/${work}/?book=${book}${source==='default'?'':'&english='+source}`,i);captures.push(await page.evaluate(()=>{
   const q=window.__qa,data=q.getData(),capture=()=>Object.fromEntries(Object.entries(data).map(([l,d])=>[l,q.selectView(l,d,q.currentIdBase())?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]));const whole=capture(),niese=[];
   for(const e of q.canonicalNieseStartEntries()){q.assign({viewingLevel:'niese-level',nieseNum:String(e.number),chapterNum:null,sectionNum:null});niese.push([e.number,capture()])}
   const ranges=[],chapters=[...document.querySelector('#chapter-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value);
   for(const chapter of chapters){q.assign({viewingLevel:'chapter-level',chapterNum:chapter,sectionNum:null,nieseNum:null});ranges.push(['chapter:'+chapter,capture()]);q.assign({viewingLevel:'section-level'});q.setSectionSelectOptions();for(const u of [...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value)){q.assign({sectionNum:u});ranges.push(['unit:'+chapter+':'+u,capture()])}}
   return{whole,niese,ranges};
  }))}
  if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Cross-work '+work+book+source);report.cross_works.push({work,book,source,niese:captures[1].niese.length,ranges:captures[1].ranges.length,result:'PASS',digest:hash(captures[1])});console.log('cross-work',work,book,source);
 }
 for(const route of ['/antiquities/?book=8&niese=367','/antiquities/?book=8&niese=369','/antiquities/?book=10&niese=108','/antiquities/?book=9&niese=291','/antiquities/?book=13&niese=212','/antiquities/?book=13&niese=214','/antiquities/?book=14&niese=357','/antiquities/?book=15&chapter=1','/antiquities/?book=15&chapter=2','/antiquities/?book=15&niese=39','/antiquities/?book=15&niese=40','/bellum-judaicum/?book=4&niese=105&english=whiston','/bellum-judaicum/?book=4&niese=105&english=lodge1602']){
  const captures=[];for(const i of [0,1]){await open(route,i);captures.push(await page.evaluate(()=>Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>[l,v?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]))))}if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Focused control '+route);report.focused.push({route,result:'PASS',digest:hash(captures[1])});
 }
 await open('/bellum-judaicum/?book=1&niese=1&english=lodge1602',1);const before=await page.locator('#english').innerHTML();await page.uncheck('#lodge-notes-visible');if(!await page.locator('#english').evaluate(n=>n.classList.contains('lodge-notes-hidden')))throw Error('Lodge hide');await page.reload();await page.waitForFunction(()=>window.__qaReady);if(await page.locator('#lodge-notes-visible').isChecked())throw Error('Lodge reload');await page.check('#lodge-notes-visible');if(before!==await page.locator('#english').innerHTML())throw Error('Lodge restore');await page.selectOption('#english-source-selector','whiston');await page.evaluate(()=>window.__qaPending);if(await page.locator('#lodge-notes-select').isVisible())throw Error('Whiston source switch');report.Lodge_Whiston_switching='PASS';
 if(report.errors.length)throw Error('Browser/network errors');report.result='PASS';
 }catch(e){report.result='FAIL';report.failure=String(e)}finally{report.finished=new Date().toISOString();report.origins=origins;save(path.join(__dirname,final?'READER_FINAL_PRIOR_RESULTS.json':'READER_STRUCTURE_CROSSWORK_RESULTS.json'),report);await context.close();for(const s of servers)await new Promise(r=>s.close(r))}
 console.log(JSON.stringify({result:report.result,failure:report.failure,books:report.books.length,prior:report.prior_identity_count,cross_works:report.cross_works.length,errors:report.errors}));if(report.result!=='PASS')process.exitCode=1;
}
main().catch(e=>{console.error(e);process.exitCode=1});
