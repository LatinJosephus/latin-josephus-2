const {fs,path,chromium,runtime,load,save,norm,hash,serve,listen,narrative}=require('./qa-common18.cjs');
async function main(){
 const build=load(path.join(__dirname,'BUILD_CONTEXT.json')),expected=load(path.join(__dirname,'XI_WITNESS_EXPECTATION.json')),logical=load(path.join(__dirname,'EXPECTED_SELECTIONS.json')),report={scope:'Independent original XI physical witness stream versus logical assembly',alignment:[],errors:[]};
 const server=serve(build.site),origin=await listen(server),context=await chromium.launchPersistentContext(path.join(runtime,'browser-xi-witness-order'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
 try{
  await page.goto(origin+'/antiquities/?book=11');await page.waitForFunction(()=>window.__qaReady);
  const actual=await page.evaluate(code=>{const q=window.__qa,text=eval('('+code+')'),d=q.getData(),physical=text(q.view().Latin),units=[...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value),alignment=units.map(u=>{q.assign({viewingLevel:'section-level',sectionNum:u});return {unit:u,id:'latin-book11-num'+u,text:text(q.selectView('Latin',d.Latin,q.currentIdBase()))}});return {physical,alignment,logical:text(q.antiquitiesNieseFragmentView('Latin',d.Latin,Array.from({length:347},(_,i)=>i+1)))}} ,narrative.toString());
  if(actual.physical!==norm(expected.physical_narrative))throw Error('Book physical stream/order');
  for(const unit of actual.alignment){if(unit.text!==norm(expected.units[unit.id]))throw Error('Alignment physical order '+unit.unit);report.alignment.push({unit:unit.unit,status:'ORIGINAL_PHYSICAL_WITNESS_TEXT_EXACT',sha256:hash(unit.text)});}
  if(actual.logical!==norm(Array.from({length:347},(_,i)=>logical[i+1].Latin).join(''))||actual.logical===actual.physical)throw Error('Canonical assembly versus physical order');
  if(report.errors.length)throw Error('Witness reader errors');report.result='PASS';report.Book='EXACT_ORIGINAL_PHYSICAL_WITNESS_ORDER';report.canonical='EXACT_CONTINUATION_ORDER_WITH_TWO_INTERPOLATIONS_ONCE';report.physical_occurrences=expected.physical_occurrences;report.physical_sha256=hash(actual.physical);report.canonical_sha256=hash(actual.logical);
 }catch(e){report.result='FAIL';report.failure=String(e)}finally{save(path.join(__dirname,'XI_WITNESS_ORDER_RESULTS.json'),report);await context.close();await new Promise(r=>server.close(r));}
 console.log(JSON.stringify({result:report.result,failure:report.failure,alignment:report.alignment.length,physical:report.physical_occurrences?.length}));if(report.result!=='PASS')process.exitCode=1;
}
main().catch(e=>{console.error(e);process.exitCode=1;});
