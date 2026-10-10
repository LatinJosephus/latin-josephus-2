const {fs,path,chromium,runtime,load,save,norm,hash,serve,listen,narrative}=require('./qa-common.cjs');
async function main(){
 const build=load(path.join(__dirname,'BUILD_CONTEXT.json')),expected=load(path.join(__dirname,'EXPECTED_SELECTIONS.json')),report={started:new Date().toISOString(),scope:'Continuation-rank challenge, uninstrumented built-reader smoke, exact baseline exceptions',rank_challenges:[],uninstrumented:[],baseline_exceptions:[]};
 const servers=[serve(build.site),serve(build.site,false),serve(build.baseline_site)],origins=[];for(const s of servers)origins.push(await listen(s));
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-profile-extra-final'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1600,height:1000}}),page=await context.newPage();let errors=[];page.on('pageerror',e=>errors.push(String(e)));
 try{
 await page.goto(origins[0]+'/antiquities/?book=11&niese=326');await page.waitForFunction(()=>window.__qaReady);
 for(const n of [72,312,326,342]){
  const actual=await page.evaluate(({n,code})=>{const q=window.__qa,r=q.identityRegistry().sections.find(x=>x.number===n),saved=r.Latin.spans;r.Latin.spans=[...saved].reverse();try{const v=q.antiquitiesNieseFragmentView('Latin',q.getData().Latin,[n,n]);return{narrative:eval('('+code+')')(v),occurrences:[...v.querySelectorAll('[data-source-occurrence]')].map(x=>x.dataset.sourceOccurrence)}}finally{r.Latin.spans=saved}},{n,code:narrative.toString()});
  if(actual.narrative!==norm(expected[n].Latin)||JSON.stringify(actual.occurrences)!==JSON.stringify(expected[n].occurrences))throw Error('Rank/attachment sorting '+n);report.rank_challenges.push({n,reversed_declaration_and_duplicate_identity_requests:'PASS',digest:hash(actual)});
 }
 if(errors.length)throw Error('Rank reader error');
 for(const n of [1,72,312,326,342,347]){
  await page.goto(origins[1]+'/antiquities/?book=11&niese='+n);await page.waitForFunction(n=>document.querySelector('#latin [type="niese-section"]')?.getAttribute('n')===String(n),n);
  const actual=await page.evaluate(code=>Object.fromEntries(['Latin','Greek','English'].map(l=>[l,eval('('+code+')')(document.getElementById(l.toLowerCase()))])),narrative.toString());
  for(const l of ['Latin','Greek','English'])if(actual[l]!==norm(expected[n][l]))throw Error('Uninstrumented '+n+' '+l);if(await page.evaluate(()=>Boolean(window.__qa)))throw Error('Uninstrumented helper present');report.uninstrumented.push({n,result:'PASS',digest:hash(actual)});
 }
 await page.goto(origins[1]+'/antiquities/?book=11&niese=312');await page.waitForSelector('#latin [data-source-role="interpolation"]');
 report.visuals=[];
 for(const theme of ['light','dark']){await page.evaluate(t=>setTheme(t),theme);await page.waitForTimeout(550);const styles=await page.locator('#latin .niese-correspondence-note').first().evaluate(n=>({text:getComputedStyle(n).color,background:getComputedStyle(n).backgroundColor,link:getComputedStyle(n.querySelector('a')).color}));const file=path.join(runtime,'FINAL-XI-312-'+theme+'.png');await page.screenshot({path:file,fullPage:true});report.visuals.push({theme,file,styles});}
 await page.goto(origins[1]+'/antiquities/?book=11&chapter=8&subchapter=2');await page.waitForSelector('#traditional-reader-notice strong');if(!await page.locator('#traditional-reader-notice').textContent().then(t=>t.includes('Canonical order from separate witness fragments')&&t.includes('Jewish War 4.105')))throw Error('Accepted uninstrumented traditional notice');report.accepted_traditional_notice='PASS';
 if(errors.length)throw Error('Uninstrumented reader errors');
 const signatures=[];
 for(const i of [2,0]){
  errors=[];await page.goto(origins[i]+'/antiquities/?book=1&bamberg=B78-table1-row005');await page.waitForFunction(()=>window.__qaReady);
  const hrefs=await page.locator('a[href^="undefined"]').evaluateAll(ns=>ns.map(n=>n.getAttribute('href')));if(hrefs.length!==3)throw Error('Apparatus exception extent');
  const targets=[];for(const href of new Set(hrefs)){const r=await page.request.get(origins[i]+'/antiquities/'+href);if(r.status()!==404)throw Error('Apparatus exception target');targets.push({href,status:r.status()})}
  if(errors.length)throw Error('Supported apparatus route error');await page.goto(origins[i]+'/antiquities/?book=1&niese=1');await page.waitForFunction(()=>document.querySelector('#niese-selector')?.options.length>1);await page.waitForTimeout(550);
  if(errors.length!==1||errors[0]!=="TypeError: Cannot read properties of null (reading 'querySelector')")throw Error('Unsupported I1 exact error '+JSON.stringify(errors));
  const inventory=await page.locator('#niese-selector').evaluate(n=>({value:n.value,firstSupported:[...n.options].find(o=>o.value)?.value}));if(inventory.value!==''||inventory.firstSupported!=='27')throw Error('Unsupported I1 inventory');signatures.push({hrefs,targets,unsupported_error:errors[0],inventory});
  errors=[];await page.goto(origins[i]+'/antiquities/?book=1&niese=27');await page.waitForFunction(()=>window.__qaReady);if(errors.length)throw Error('Supported I27');report.baseline_exceptions.push({build:i===2?'frozen baseline':'final candidate',apparatus_route:'/antiquities/?book=1&bamberg=B78-table1-row005',unsupported_route:'/antiquities/?book=1&niese=1',...signatures.at(-1),supported_I27:'PASS'});
 }
 if(JSON.stringify(signatures[0])!==JSON.stringify(signatures[1]))throw Error('Baseline exception changed');report.result='PASS';
 }catch(e){report.result='FAIL';report.failure=String(e)}finally{report.finished=new Date().toISOString();report.origins=origins;save(path.join(__dirname,'READER_EXTRA_RESULTS.json'),report);await context.close();for(const s of servers)await new Promise(r=>s.close(r))}
 console.log(JSON.stringify({result:report.result,failure:report.failure,rank_challenges:report.rank_challenges.length,uninstrumented:report.uninstrumented.length,exceptions:report.baseline_exceptions.length}));if(report.result!=='PASS')process.exitCode=1;
}
main().catch(e=>{console.error(e);process.exitCode=1});
