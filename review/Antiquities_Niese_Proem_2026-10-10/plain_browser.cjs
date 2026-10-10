const {fs,path,chromium,runtime,load,save,norm,hash,serve,listen}=require('./qa-common18.cjs');
const {narrative}=require('./browser_common.cjs');
async function main(){
 const build=load(path.join(__dirname,'BUILD_CONTEXT.json')),expected=load(path.join(__dirname,'EXPECTED_INTERVALS.json')),s=serve(build.site,false),origin=await listen(s,8923),context=await chromium.launchPersistentContext(path.join(runtime,'browser-plain-proem'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1600,height:1000}}),page=await context.newPage();
 const r={status:'RUNNING',source_build:build.commit,instrumentation:false,selectors:[],errors:[],assets:[]};
 page.on('pageerror',e=>r.errors.push({kind:'page',message:String(e)}));page.on('requestfailed',x=>r.errors.push({kind:'request',url:x.url(),message:x.failure()?.errorText}));page.on('console',m=>{if(m.type()==='error')r.errors.push({kind:'console',message:m.text()})});page.on('response',x=>{if(x.status()>=400)r.assets.push({url:x.url().replace(origin,'LOCAL_ORIGIN'),status:x.status()})});
 const ready=n=>page.waitForFunction(n=>['latin','greek','english'].every(l=>document.querySelector(`#${l} [type^="niese-"][n="${n}"]`)),n);
 const capture=()=>page.evaluate(code=>{const text=eval('('+code+')'),ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return {text:Object.fromEntries(['Latin','Greek','English'].map(l=>[l,text(document.querySelector('#'+l.toLowerCase()))])),duplicates:ids.filter((id,i)=>ids.indexOf(id)!==i),EnglishContext:!!document.querySelector('#english .niese-context-note'),LatinUnavailable:!!document.querySelector('#latin .structural-unavailable')};},narrative.toString());
 try{
  for(let n=1;n<=26;n++){
   await page.goto(origin+'/antiquities/?book=preface&niese='+n);await ready(n);const a=await capture();for(const l of ['Latin','Greek','English'])if(norm(a.text[l])!==norm(expected[n-1][l]))throw Error('Plain complete source extent '+n+' '+l);if(a.duplicates.length||!a.EnglishContext||a.LatinUnavailable)throw Error('Plain availability and IDs '+n);r.selectors.push({number:n,status:'PASS',text_hashes:Object.fromEntries(Object.entries(a.text).map(([l,t])=>[l,hash(norm(t))]))});
   if([1,2,25,26].includes(n)){
    await page.evaluate(()=>document.querySelector('#collapse-settings')?.classList.add('show'));for(const l of ['greek','english'])await page.check('#'+l+'-pane-select');await page.evaluate(()=>document.querySelector('#collapse-settings')?.classList.remove('show'));
    await page.screenshot({path:path.join(__dirname,'evidence','Proem-plain-'+n+'.png'),fullPage:true});
   }
  }
  await page.click('.niese-related-passage a');await ready(27);if(new URL(page.url()).searchParams.get('book')!=='1')throw Error('Book I transition URL');r.BookI27={status:'PASS',text_hashes:Object.fromEntries(Object.entries((await capture()).text).map(([l,t])=>[l,hash(norm(t))]))};await page.screenshot({path:path.join(__dirname,'evidence','BookI27-plain.png'),fullPage:true});
  await page.goto(origin+'/antiquities/?book=preface');await page.waitForFunction(()=>document.querySelector('#latin #latin-preface-num18'));await page.screenshot({path:path.join(__dirname,'evidence','Proem-whole-plain.png'),fullPage:true});
  if(r.errors.length||r.assets.length)throw Error('Plain browser/asset errors '+JSON.stringify({errors:r.errors,assets:r.assets}));r.status='PASS';
 }catch(e){r.status='FAIL';r.failure=String(e);throw e;}finally{save(path.join(__dirname,'PLAIN_READER_QA.json'),r);await context.close();await new Promise(resolve=>s.close(resolve));}
 console.log(JSON.stringify({status:r.status,plainSelectors:r.selectors.length,BookI27:r.BookI27?.status}));
}
main().catch(e=>{console.error(e);process.exitCode=1});
