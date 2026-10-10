const {fs,path,chromium,runtime,load,save,norm,hash,serve,listen,narrative}=require('./qa-common18.cjs');
async function main(){
 const P=__dirname,build=load(path.join(P,'BUILD_CONTEXT.json')),expected=load(path.join(P,'FINAL_EXPECTED_INTERVALS.json')),controls=load(path.join(P,'STRUCTURAL_CONTROLS.json'));
 const servers=[serve(build.site),serve(build.site,false)],origins=[];for(const s of servers)origins.push(await listen(s));
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-XX-structural-controls'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await context.newPage();
 const r={status:'RUNNING',scope:'XX real structural selector events, Bamberg next/previous, visible source-only annotation and uninstrumented editorial controls',controls:[],plain:[],source_only:[],errors:[]};
 page.on('pageerror',e=>r.errors.push(String(e)));page.on('requestfailed',e=>r.errors.push(e.url()+':'+e.failure()?.errorText));
 async function open(q,plain=false){await page.goto(origins[plain?1:0]+'/antiquities/?'+q);if(!plain)await page.waitForFunction(()=>window.__qaReady);else await page.waitForFunction(()=>document.querySelector('#latin [type^="niese-"]'));}
 async function change(selector,value){await page.selectOption(selector,String(value));await page.evaluate(()=>window.__qaPending);}
 async function snapshot(){return page.evaluate(code=>{const text=eval('('+code+')'),ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return{text:Object.fromEntries(['Latin','Greek','English'].map(l=>[l,text(document.querySelector('#'+l.toLowerCase()))])),state:window.__qa?.getState(),duplicates:ids.filter((id,i)=>ids.indexOf(id)!==i),unavailable:document.querySelector('#latin .structural-unavailable')?.textContent||null,note:document.querySelector('#latin .niese-correspondence-note')?.textContent||null,EnglishContext:!!document.querySelector('#english .niese-context-note'),helper:!!window.__qa};},narrative.toString());}
 try{
  // Every structural selector row is exercised as a user event and checked
  // against the independent, freshly captured pre-integration containing view.
  await open('book=20');const baseline=load(path.join(P,'BASELINE_PROTECTED_BROWSER.json'));
  for(const scheme of ['chapter','subchapter','bamberg']){
   for(const c of controls.filter(c=>c.scheme===scheme)){
    await open('book=20');await page.check('#'+scheme+'-level');await page.evaluate(()=>window.__qaPending);
    if(scheme==='bamberg')await change('#bamberg-selector',c.id);else{await change('#chapter-selector',c.chapter);if(scheme==='subchapter')await change('#subchapter-selector',c.subchapter);}
    const a=await snapshot(),wanted=baseline.views.find(v=>v.id===c.id);
    for(const l of ['Latin','Greek','English'])if(hash(norm(a.text[l]))!==wanted.languages[l])throw Error('Structural selector physical range '+c.id+' '+l);
    if(JSON.stringify(a.duplicates)!==JSON.stringify(wanted.duplicates))throw Error('Structural duplicate IDs '+c.id);
    if(scheme==='bamberg'){
     const ordered=await page.locator('#bamberg-selector').evaluate(m=>[...m.options].filter(o=>o.value).map(o=>o.value)),i=ordered.indexOf(c.id);
     if(await page.locator('#bamberg-previous').isDisabled()!==(i===0)||await page.locator('#bamberg-next').isDisabled()!==(i===ordered.length-1))throw Error('Bamberg endpoints '+c.id);
     if(i<ordered.length-1){await page.click('#bamberg-next');await page.evaluate(()=>window.__qaPending);if(await page.locator('#bamberg-selector').inputValue()!==ordered[i+1])throw Error('Bamberg next');await page.click('#bamberg-previous');await page.evaluate(()=>window.__qaPending);if(await page.locator('#bamberg-selector').inputValue()!==c.id)throw Error('Bamberg previous');}
    }
    r.controls.push({id:c.id,scheme,range:'EXACT_FROZEN_BASELINE',selector_event:'PASS',next_previous:scheme==='bamberg'?'PASS':null});
   }
  }
  await open('book=20&unit=1');const units=baseline.XXcensus.alignment;
  for(const unit of units){await change('#section-selector',unit);const a=await snapshot(),wanted=baseline.views.find(v=>v.id==='XX-alignment-'+unit);for(const l of ['Latin','Greek','English'])if(hash(norm(a.text[l]))!==wanted.languages[l])throw Error('Alignment selector '+unit+' '+l);r.controls.push({id:'XX-alignment-'+unit,scheme:'alignment',selector_event:'PASS',range:'EXACT_FROZEN_BASELINE'});}
  for(const q of ['book=20','book=20&unit=34']){await open(q);const annotation=page.locator('#latin tei-p[id="latin-book20-num34"]');if(!await annotation.isVisible()||!(await annotation.textContent()).includes('[Niese sections 26–37 largely missing; cf. Blatt, p. 68]'))throw Error('Source-only annotation hidden/moved');r.source_only.push({query:q,id:'latin-book20-num34',visible:true,annotation:'EXACT_PRESERVED_SOURCE_TEXT'});}
  for(const n of [1,26,27,36,37,58,59,238,239,240,241,266,267,268]){await open('book=20&niese='+n,true);const a=await snapshot(),e=expected[n-1];if(a.helper||a.duplicates.length||!a.EnglishContext)throw Error('Plain-reader integrity '+n);for(const l of ['Latin','Greek','English'])if(a.text[l]!==norm(e[l]))throw Error('Plain exact full interval '+n+' '+l);if(e.unavailable?!a.unavailable?.includes(e.qualification):a.note!==e.qualification)throw Error('Plain notice '+n);r.plain.push({number:n,Greek:'EXACT',Latin:e.unavailable?'ACCURATE_UNAVAILABLE':'EXACT',English:'EXACT_CONTEXT',helper:false});}
  if(!await page.locator('#latin tei-trailer').isVisible())throw Error('AMEN trailer hidden');
  if(r.controls.length!==133||r.errors.length)throw Error('Incomplete controls/errors '+JSON.stringify(r.errors));r.status='PASS';
 }catch(e){r.status='FAIL';r.failure=String(e);throw e;}finally{save(path.join(P,'XX_STRUCTURAL_CONTROLS.json'),r);await context.close();for(const s of servers)await new Promise(r=>s.close(r));}
 console.log(JSON.stringify({status:r.status,controls:r.controls.length,plain:r.plain.length,source_only:r.source_only.length}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
