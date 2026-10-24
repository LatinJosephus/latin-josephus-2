// Focused actual-browser acceptance for the compact DEH/French controls.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const args=process.argv.slice(2),opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
assert(args.includes('--output'),'Provide an external evidence directory.');
const out=path.resolve(opt('--output','')),base=opt('--base-url','http://127.0.0.1:4019');
fs.mkdirSync(path.join(out,'screenshots'),{recursive:true});fs.mkdirSync(path.join(out,'records'),{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:opt('--browser-executable','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')});
const page=await browser.newPage({viewport:{width:1440,height:900}});page.setDefaultTimeout(45000);
const result={status:'RUNNING',browser:browser.version(),checks:[],sizes:[],errors:[]};
page.on('pageerror',e=>result.errors.push(e.message));
const save=()=>fs.writeFileSync(path.join(out,'records/COMPACT_BROWSER_QA.json'),JSON.stringify(result,null,2)+'\n');
const pass=(name,detail={})=>{result.checks.push({name,...detail});save();console.log('PASS '+name);};
const url='/deh/?book=1&chapter=43&unit=3&french=millet1556&millet-unit=latin-deh1-num188&millet-align=0';
const ready=async(book=1)=>page.waitForFunction(b=>document.querySelector('#french')?.dataset.milletReady===String(b)&&!!document.querySelector('#millet-source'),book);
const openGlobal=async()=>{const b=page.locator('#display-settings-header button');if(await b.getAttribute('aria-expanded')!=='true')await b.click();await page.waitForFunction(()=>document.querySelector('#collapse-settings').classList.contains('show')&&!document.querySelector('#collapse-settings').classList.contains('collapsing'));};
const go=async(u=url)=>{await page.goto(base+u,{waitUntil:'domcontentloaded'});await ready(Number(new URL(base+u).searchParams.get('book'))||1);await openGlobal();};
const settings=async()=>{if(!await page.locator('#millet-view').isVisible())await page.locator('#millet-settings > summary').click();};
const select=async(id,value)=>{await settings();await page.locator(id).selectOption(String(value));};
const snapshot=()=>({source:[...document.querySelectorAll('#millet-source [data-source-line]')].map(e=>[e.id,e.textContent]),atoms:[...document.querySelectorAll('#millet-source [data-mappings]')].map(e=>[e.closest('[data-source-line]').id,e.dataset.startCp,e.dataset.endCp,e.dataset.startUtf16,e.dataset.endUtf16,e.dataset.mappings,e.textContent])});
const selected=()=>[...document.querySelectorAll('#millet-source .millet-selected')].map(e=>[e.closest('[data-source-line]').id,e.dataset.startCp,e.dataset.endCp,e.textContent]);
const measure=()=>({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,paneTop:document.querySelector('#pane-container').getBoundingClientRect().top+scrollY,controlsHeight:document.querySelector('#display-settings').getBoundingClientRect().height,textTops:['#latin tei-p','#english tei-p','#french .millet-paragraph'].map(s=>document.querySelector(s)?.getBoundingClientRect().top+scrollY)});
try{
 // Reproduce the old issued interface against exactly the same current site.
 if(fs.existsSync(path.join(out,'records/BEFORE_DEH.html'))){
  const git=opt('--git','C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe');
  for(const file of ['assets/js/milletReader.js','assets/css/millet.css']){
   const body=execFileSync(git,['show','8fd9a486f61935d4f9177653e89fad948eeb4a40:'+file],{cwd:process.cwd()});
   await page.route('**/'+file,route=>route.fulfill({body,contentType:file.endsWith('.js')?'text/javascript':'text/css'}));
  }
  await page.route('**/deh/?*',route=>route.fulfill({body:fs.readFileSync(path.join(out,'records/BEFORE_DEH.html')),contentType:'text/html'}));
  for(const size of [{width:1440,height:900},{width:1366,height:768},{width:390,height:844}]){
   await page.setViewportSize(size);await go();
   await page.evaluate(()=>window.scrollTo({top:0,left:0,behavior:'instant'}));await page.waitForFunction(()=>scrollY===0);
   await page.screenshot({path:path.join(out,'screenshots/BEFORE_'+size.width+'.png')});
   const metrics=await page.evaluate(measure);result.sizes.push({stage:'before',...metrics});
   if(size.width===1440){await page.locator('#millet-alignment').check();fs.writeFileSync(path.join(out,'records/BEFORE_SELECTED.json'),JSON.stringify(await page.evaluate(selected)));}
  }
  await page.unrouteAll();pass('Before screenshots reproduced from the exact previous Git revision');
 }
 for(const size of [{width:1440,height:900},{width:1366,height:768},{width:390,height:844}]){
  await page.setViewportSize(size);await go();
  assert.equal(await page.locator('#millet-controls').count(),1);
  assert.equal(await page.locator('#collapse-settings #millet-controls').count(),0);
  assert.equal(await page.locator('#millet-settings').getAttribute('open'),null);
  assert.equal(await page.locator('.millet-passage-label').textContent(),'[I.43.3]');
  assert.equal(await page.locator('.millet-passage-label').evaluate(e=>getComputedStyle(e).fontStyle),'normal');
  const actual=await page.evaluate(snapshot),baseline=JSON.parse(fs.readFileSync(path.join(out,'records/BASELINE_I43_3.json')));
  assert.deepEqual(actual.source,baseline.source);assert.deepEqual(actual.atoms,baseline.atoms);
  const latinEnglish=await page.locator('#latin,#english').allTextContents();
  await page.locator('#millet-alignment').check();assert(await page.locator('.millet-selected').count());
  assert.deepEqual(await page.evaluate(selected),JSON.parse(fs.readFileSync(path.join(out,'records/BEFORE_SELECTED.json'))));
  await page.locator('#millet-alignment').uncheck();assert.equal(await page.locator('.millet-selected').count(),0);
  assert.deepEqual(await page.locator('#latin,#english').allTextContents(),latinEnglish);
  const metrics=await page.evaluate(measure);assert(metrics.scrollWidth<=size.width,'Horizontal overflow: '+JSON.stringify(metrics));
  result.sizes.push({stage:'after',...metrics});
  await page.evaluate(()=>window.scrollTo({top:0,left:0,behavior:'instant'}));await page.waitForFunction(()=>scrollY===0);
  await page.screenshot({path:path.join(out,'screenshots/AFTER_'+size.width+'.png')});
  if(size.width===390){await page.locator('#french > h3').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'screenshots/FRENCH_390.png')});}
  await settings();await page.locator('#millet-folios').check();assert(await page.locator('.millet-folio-marker').count());
  assert.equal(await page.evaluate(()=>document.activeElement.id),'millet-folios');
  await page.locator('#millet-folios').uncheck();
  await page.locator('#millet-status > summary').click();assert(await page.getByRole('link',{name:'Read Ussani I.43.3',exact:true}).isVisible());
  await page.screenshot({path:path.join(out,'screenshots/SETTINGS_'+size.width+'.png')});
  await page.locator('#millet-status > summary').click();await page.locator('#millet-settings > summary').click();
  // Keyboard reopening and toggling do not strand focus in a removed element.
  await page.locator('#millet-settings > summary').press('Enter');assert(await page.locator('#millet-view').isVisible());
  await page.locator('#millet-folios').press('Space');assert.equal(await page.evaluate(()=>document.activeElement.id),'millet-folios');
  await page.locator('#millet-folios').press('Space');
  await page.locator('#english-pane-select').uncheck();assert(!await page.locator('#english').isVisible());
  assert(await page.locator('#french').isVisible());
  await page.locator('#french-pane-select').uncheck();assert(!await page.locator('#millet-controls').isVisible());assert(await page.locator('#latin').isVisible());
  await page.screenshot({path:path.join(out,'screenshots/SINGLE_'+size.width+'.png')});
  await page.locator('#french-pane-select').check();await ready();assert(await page.locator('#millet-controls').isVisible());
  await page.locator('#english-pane-select').check();
  pass('Responsive panes, settings, keyboard, exact source/offsets and highlights at '+size.width+'×'+size.height,metrics);
 }
 await page.setViewportSize({width:1440,height:900});await go();
 await settings();await page.locator('#millet-folios').check();await page.locator('#millet-alignment').check();
 await page.locator('#chapter-selector').selectOption('42');await ready();
 // Choosing a chapter clears the global sub-chapter. The independent aligned
 // passage remains selected until an actual new global unit is selected.
 await page.waitForFunction(()=>document.querySelector('#chapter-selector').value==='42'&&document.querySelector('#latin tei-p tei-num')?.textContent.trim()==='[I.42.1]');
 assert.equal(await page.locator('#millet-ussani').inputValue(),'latin-deh1-num188');
 await page.locator('#section-selector').selectOption({label:'[I.42.1]'});await ready();
 await page.waitForFunction(()=>document.querySelector('.millet-passage-label')?.textContent==='[I.42.1]');
 assert(await page.locator('#millet-folios').isChecked());assert(await page.locator('#millet-alignment').isChecked());assert(await page.locator('#millet-view').isVisible());
 await page.locator('#chapter-level').check();await ready();await page.waitForFunction(()=>!new URL(location).searchParams.has('unit'));
 await page.locator('#book-level').check();await ready();await page.waitForFunction(()=>!new URL(location).searchParams.has('chapter'));
 await page.locator('#section-level').check();await ready();
 await page.locator('#chapter-selector').selectOption('42');
 await page.locator('#section-selector').selectOption({label:'[I.42.1]'});await ready();
 await select('#millet-view','book');await ready();
 await page.locator('#millet-ussani').selectOption('latin-deh1-num188');
 await page.waitForFunction(()=>new URL(location).searchParams.get('chapter')==='43'&&new URL(location).searchParams.get('unit')==='3');await ready();
 // The ordinary source→Latin path, using a source atom for another unit.
 await page.locator('#millet-source [data-mappings]').first().click();
 await page.waitForFunction(()=>new URL(location).searchParams.get('chapter')==='0');await ready();
 assert(await page.locator('#latin .millet-latin-target').count());
 pass('Global book/chapter/sub-chapter and independent aligned passage navigation; preferences persist');
 for(const mode of ['source','chapter','page','preliminary','running']){
  await select('#millet-view',mode);await ready(mode==='preliminary'?0:1);
  if(mode==='page'){await page.locator('#millet-page').selectOption('31');const link=await page.locator('#millet-share').getAttribute('href');await page.goto(link);await ready();await settings();assert.equal(await page.locator('#millet-page').inputValue(),'31');}
 }
 await go();await settings();await page.locator('#millet-folios').check();await page.locator('#millet-folios').uncheck();
 await page.goBack();await ready();assert(await page.locator('#millet-folios').isChecked());
 await page.goForward();await ready();assert(!await page.locator('#millet-folios').isChecked());
 pass('All six French modes, share-link reload and browser back/forward');
 await go('/deh/?book=1&chapter=16&unit=3&french=millet1556');assert.match(await page.locator('#millet-status').textContent(),/displaced/);
 await go('/deh/?book=1&chapter=8&unit=1&french=millet1556');assert(await page.locator('.millet-attention').count());
 pass('Displacement and pending editorial metadata retained in contextual disclosure');
 await go();await page.getByRole('link',{name:'About this edition: Millet 1556',exact:true}).click();
 await page.getByRole('heading',{name:'Millet 1556 — French',exact:true}).waitFor();
 assert((await page.locator('article').innerText()).includes('independent Aligned passage selector'));
 await page.goBack();await ready();pass('About this edition opens updated control directions and returns to the same French view');
 assert.equal(result.errors.length,0,JSON.stringify(result.errors));result.status='PASS';save();
}catch(e){result.status='FAIL';result.failure=e.stack;save();await page.screenshot({path:path.join(out,'screenshots/FAILURE.png')});throw e;}
finally{await browser.close();}
