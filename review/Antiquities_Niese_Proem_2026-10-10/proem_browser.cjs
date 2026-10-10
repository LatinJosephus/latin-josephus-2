const {fs,path,P,runtime,norm,sha,narrative,session}=require('./browser_common.cjs');
async function main(){
 const s=await session('final'),r={status:'RUNNING',scope:'26 approved Proem extents, existing route, actual UI events, plain reader checks separately',selections:[],routes:[],errors:s.errors};
 const expected=JSON.parse(fs.readFileSync(path.join(P,'EXPECTED_INTERVALS.json')));
 const check=async n=>{const a=await s.snapshot(),e=expected[n-1];for(const l of ['Latin','Greek','English'])if(norm(a.languages[l])!==norm(e[l])){fs.writeFileSync(path.join(P,'PROEM_DIFFERENCE.json'),JSON.stringify({n,language:l,actual:a,expected:e},null,2));throw Error('Full extent '+n+' '+l)}if(a.duplicates.length||!a.EnglishContext||a.unavailable)throw Error('Availability/context/IDs '+n);if(n===26&&a.languages.Latin.includes('EXPLICIT'))throw Error('Trailer entered §26');const next=await s.page.locator('#niese-next').isDisabled(),prev=await s.page.locator('#niese-previous').isDisabled();if(next!==(n===26)||prev!==(n===1))throw Error('Previous/next terminal '+n);return a;};
 try{
  await s.open('book=preface&niese=1');for(const l of ['greek','english'])await s.page.check('#'+l+'-pane-select');
  const menu=await s.page.locator('#niese-selector').evaluate(n=>[...n.options].filter(o=>o.value).map(o=>Number(o.value)));
  if(JSON.stringify(menu)!==JSON.stringify(Array.from({length:26},(_,i)=>i+1)))throw Error('26 exact menu entries');
  const books=await s.page.locator('#book-selector').evaluate(n=>[...n.options].map(o=>o.value));if(books.filter(x=>/^\d+$/.test(x)).length!==20||books[0]!=='preface')throw Error('20 books plus existing Proem');r.bookMenu=books;
  for(let n=1;n<=26;n++){await s.select(n);const a=await check(n);r.selections.push({number:n,status:'PASS',fullTexts:Object.fromEntries(Object.entries(a.languages).map(([l,t])=>[l,sha(norm(t))])),LatinIDs:a.sourceIDs[0],EnglishContext:expected[n-1].English_context_target});}
  for(let n=1;n<=26;n++){
   await s.open('book=preface&niese='+n);await check(n);await s.page.reload();await s.page.waitForFunction(()=>window.__qaReady);await check(n);
   if(n<26){await s.page.click('#niese-next');await s.page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n+1);await check(n+1);await s.page.click('#niese-previous');await s.page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n);await check(n);await s.page.goBack();await s.page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n+1);await check(n+1);await s.page.goForward();await s.page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n);await check(n);}
   r.routes.push({number:n,directReloadPreviousNextHistory:'PASS'});
  }
  await s.open('book=preface');const whole=await s.snapshot();if(!whole.languages.Latin.includes('EXPLICIT')||whole.languages.Latin.includes('Omitted'))throw Error('Whole Proem/trailer');for(const l of ['Greek','Latin']){const all=norm(expected.map(e=>e[l]).join(''));if(!norm(whole.languages[l]).includes(all))throw Error('Whole Proem reconstruction '+l)}
  const targets=await s.page.locator('.niese-related-passage a').count();if(targets!==1)throw Error('Single Book I transition '+targets);
  await s.page.click('.niese-related-passage a');await s.page.waitForFunction(()=>window.__qaReady&&window.__qa.getState().bookNum==='01');if(await s.page.locator('#niese-selector').evaluate(n=>n.value)!=='27')throw Error('Transition target I.27');if(await s.page.locator('#niese-selector').evaluate(n=>[...n.options].filter(o=>o.value).length)!==320)throw Error('Book I narrative menu');r.wholeProemAndTransition='PASS';
  await s.page.goBack();await s.page.waitForFunction(()=>window.__qaReady&&window.__qa.getState().bookNum==='preface');await s.page.selectOption('#niese-selector','26');await s.page.waitForFunction(()=>window.__qaRenderedState?.nieseNum==='26');await check(26);if(await s.page.locator('.niese-related-passage a').count()!==1)throw Error('Repeated transition link');
  await s.page.selectOption('#niese-selector','25');await s.page.waitForFunction(()=>window.__qaRenderedState?.nieseNum==='25');if(await s.page.locator('.niese-related-passage').count())throw Error('Stale transition link');await check(25);
  for(const n of [1,2,25,26]){await s.open('book=preface&niese='+n);await s.page.screenshot({path:path.join(P,'evidence','Proem-reader-'+n+'.png'),fullPage:true});}
  if(r.errors.length)throw Error('Browser errors '+JSON.stringify(r.errors));r.status='PASS';
 }catch(e){r.status='FAIL';r.failure=String(e);throw e;}finally{fs.writeFileSync(path.join(P,'PROEM_BROWSER_QA.json'),JSON.stringify(r,null,2)+'\n');await s.close();}
 console.log(JSON.stringify({status:r.status,selections:r.selections.length,routes:r.routes.length,whole:r.wholeProemAndTransition}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
