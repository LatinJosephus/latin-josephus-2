// No renderer instrumentation: verify containing paratext and the terminal replacement sequence.
const {fs,path,chromium,runtime,load,save,norm,hash,serve,listen}=require('./qa-common18.cjs');
const {narrative}=require('./browser_common.cjs');
async function main(){
 const build=load(path.join(__dirname,'BUILD_CONTEXT.json')),expected=load(path.join(__dirname,'EXPECTED_INTERVALS.json')),server=serve(build.site,false),origin=await listen(server,8930);
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-plain-final-controls'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1600,height:1000}}),page=await context.newPage();
 const r={status:'RUNNING',build,instrumentation:false,sequence:[],errors:[]};
 page.on('pageerror',e=>r.errors.push(String(e)));page.on('requestfailed',x=>r.errors.push(x.url()+':'+x.failure()?.errorText));
 try{
 await page.goto(origin+'/antiquities/?book=preface');await page.waitForFunction(()=>document.querySelector('#latin #latin-preface-num18'));
 const whole=await page.evaluate(()=>{const ids=[...document.querySelectorAll('[id]')].map(n=>n.id),pane=document.querySelector('#latin'),body=pane.querySelector('tei-div1');return{paratext:[...body.querySelectorAll('tei-p:not([id])')].map(p=>p.textContent),paragraphIDs:[...body.querySelectorAll('tei-p[id]')].map(p=>p.id),duplicates:ids.filter((id,i)=>ids.indexOf(id)!==i),links:pane.querySelectorAll('.niese-related-passage a').length}});
 if(whole.duplicates.length||JSON.stringify(whole.paratext)!==JSON.stringify(['[Proemium]','EXPLICITPRAEFATIOIOSEPPI;'])||whole.paragraphIDs.length!==4||whole.links!==1)throw Error('Separate whole-Proem paratext/IDs/transition '+JSON.stringify(whole));r.whole=whole;
 await page.goto(origin+'/antiquities/?book=preface&niese=25');await page.waitForFunction(()=>document.querySelector('#latin [type^="niese-"][n="25"]'));
 await page.evaluate(()=>document.querySelector('#collapse-settings').classList.add('show'));for(const l of ['greek','english'])await page.check('#'+l+'-pane-select');
 for(const n of [25,26,25,26]){
  await page.selectOption('#niese-selector',String(n));await page.waitForFunction(n=>['latin','greek','english'].every(l=>document.querySelector(`#${l} [type^="niese-"][n="${n}"]`)),n);
  const a=await page.evaluate(code=>{const text=eval('('+code+')'),ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return{text:Object.fromEntries(['Latin','Greek','English'].map(l=>[l,text(document.querySelector('#'+l.toLowerCase()))])),duplicates:ids.filter((id,i)=>ids.indexOf(id)!==i),links:document.querySelectorAll('.niese-related-passage a').length};},narrative.toString());
  for(const l of ['Latin','Greek','English'])if(norm(a.text[l])!==norm(expected[n-1][l]))throw Error('Plain final extent '+n+' '+l);
  if(a.duplicates.length||a.links!==(n===26?1:0))throw Error('Plain stale content/IDs/link '+n);
  r.sequence.push({n,status:'PASS',text_hashes:Object.fromEntries(Object.entries(a.text).map(([l,t])=>[l,hash(norm(t))])),duplicates:a.duplicates,related_links:a.links});
 }
 if(r.errors.length)throw Error('Plain browser errors');r.status='PASS';
 }catch(e){r.status='FAIL';r.failure=String(e)}finally{save(path.join(__dirname,'PLAIN_FINAL_CONTROLS.json'),r);await context.close();await new Promise(resolve=>server.close(resolve))}
 console.log(JSON.stringify({status:r.status,failure:r.failure,sequence:r.sequence.length}));if(r.status!=='PASS')process.exitCode=1;
}
main().catch(e=>{console.error(e);process.exitCode=1});
