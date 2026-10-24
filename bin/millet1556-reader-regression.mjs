// Existing reader/search smoke checks against the real generated site.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const args=process.argv.slice(2),opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
const base=opt('--base-url','http://127.0.0.1:4019'),out=path.resolve(opt('--output',''));
assert(args.includes('--output'));fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({headless:true,...(opt('--browser-executable',null)?{executablePath:opt('--browser-executable')}:{})});
const page=await browser.newPage({viewport:{width:1440,height:1000}}),results={status:'RUNNING',checks:[],errors:[]};
results.browserVersion=browser.version();
page.on('pageerror',e=>results.errors.push(e.message));page.setDefaultTimeout(45000);
const save=()=>fs.writeFileSync(path.join(out,'EXISTING_READER_BROWSER_QA.json'),JSON.stringify(results,null,2)+'\n');
const check=(name,details={})=>{results.checks.push({name,...details});save();console.log('PASS '+name);};
try{
 for(const [work,book,n,source]of [['bellum',1,31,'whiston'],['bellum',2,1,'lodge1602'],['antiquities',2,1,'lodge1602'],['antiquities',14,308,'lodge1602'],['antiquities',20,268,'whiston'],['contra-apionem',1,1,'lodge1602']]){
  const url=`/${work==='bellum'?'bellum-judaicum':work}/?book=${book}&niese=${n}&english=${source}`;
  await page.goto(base+url,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>!!document.querySelector('#english tei-body, #english tei-div2'));
  const snapshot=await page.evaluate(()=>({heading:document.querySelector('#english h3').textContent,selected:document.querySelector('#english-source-selector').value,english:document.querySelector('#english').innerText.length,latin:document.querySelector('#latin').innerText.length,greek:document.querySelector('#greek').innerText.length,millet:!!document.querySelector('#french-pane-select')}));
  assert.equal(snapshot.selected,source);assert(!snapshot.millet);assert(snapshot.english>80);assert(snapshot.latin>40);assert(snapshot.greek>40);check(url,snapshot);
 }
 for(const source of ['aj_niese','aj_whiston']){
  await page.goto(base+`/deh/?book=1&chapter=15&unit=3&parallel=deh-1-15-3&parallel-work=AJ&aj-source=${source}`,{waitUntil:'domcontentloaded'});
  await page.waitForSelector('#parallel-bj-text tei-div2');assert(!/differs from|Could not load/.test(await page.locator('#parallel-status').textContent()));
  check('Existing AJ comparison '+source,{sections:await page.locator('#parallel-bj-text tei-div2').count()});
 }
 // This pre-existing rejection is retained, not hidden by changing a scholarly pin.
 await page.goto(base+'/deh/?book=1&chapter=15&unit=3&parallel=deh-1-15-3&parallel-work=AJ&aj-source=aj_latin',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>document.querySelector('#parallel-status')?.textContent.includes('differs from the AJ display authority'));
 check('Known baseline AJ Latin hash guard still rejects stale source pins',{classification:'pre-existing; XML and historical pins preserved'});
 await page.goto(base+'/search/',{waitUntil:'domcontentloaded'});await page.locator('#search-button').waitFor();
 await page.waitForFunction(()=>!document.getElementById('search-button').disabled);
 const options=await page.locator('#work option').allTextContents();assert(options.some(v=>v.includes('De excidio')));
 await page.locator('#query').fill('rex');await page.locator('#search-button').click();
 await page.waitForFunction(()=>document.querySelector('#results')?.children.length>0);
 check('Existing search produces results',{status:await page.locator('#status').textContent(),collections:options.length});
 await page.screenshot({path:path.join(out,'SEARCH_BROWSER.png'),fullPage:false});
 assert.equal(results.errors.length,0,JSON.stringify(results.errors));results.status='PASS';save();
}catch(e){results.status='FAIL';results.failure=e.stack;save();await page.screenshot({path:path.join(out,'REGRESSION_FAILURE.png'),fullPage:false});throw e;}
finally{await browser.close();}
