// Acceptance against an actual Jekyll build served by a normal localhost server.
// NODE_PATH may name an installed Playwright package directory.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const args=process.argv.slice(2),option=(key,fallback)=>args.includes(key)?args[args.indexOf(key)+1]:fallback;
const base=option('--base-url','http://127.0.0.1:4018'),out=path.resolve(option('--output',''));
assert(args.includes('--output'),'Supply an external --output directory.');fs.mkdirSync(out,{recursive:true});
const root=fileURLToPath(new URL('../',import.meta.url));
const data=n=>JSON.parse(fs.readFileSync(path.join(root,'assets/data/deh-millet1556',n?'book-0'+n+'.json':'preliminary.json')));
const result={status:'RUNNING',base,books:[],checks:[],errors:[],localHTTPFailures:[],externalFailures:[]};
const save=()=>fs.writeFileSync(path.join(out,'MILLET_BROWSER_QA.json'),JSON.stringify(result,null,2)+'\n');
const executablePath=option('--browser-executable',null);
const browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
result.browserVersion=browser.version();
const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage();
page.setDefaultTimeout(45000);
page.on('pageerror',e=>result.errors.push(e.message));
page.on('response',r=>{if(r.status()>=400&&r.url().startsWith(base))result.localHTTPFailures.push({url:r.url(),status:r.status()});});
page.on('requestfailed',r=>{if(!r.url().startsWith(base)&&!r.failure()?.errorText.includes('ERR_ABORTED'))result.externalFailures.push({url:r.url(),error:r.failure()?.errorText});});
const go=async url=>{await page.goto(base+url,{waitUntil:'domcontentloaded'});await page.waitForSelector('#latin tei-p[id^="latin-deh"]');const button=page.locator('#display-settings-header button');if(await button.getAttribute('aria-expanded')!=='true')await button.click();};
const ready=async n=>page.waitForFunction(n=>document.querySelector('#french')?.dataset.milletReady===String(n)&&!!document.querySelector('#millet-source'),n);
const select=async(selector,value)=>{await page.locator(selector).selectOption(String(value));};
const note=(name,detail={})=>{result.checks.push({name,...detail});save();console.log('PASS '+name);};
try {
 let milletRequests=[];page.on('request',r=>{if(r.url().includes('/deh-millet1556/'))milletRequests.push(r.url());});
 await go('/deh/?book=1');
 assert.equal(await page.locator('#french-pane-select').isChecked(),false);assert.equal(milletRequests.length,0);
 const snapshot=()=>Object.fromEntries(['latin','english'].map(k=>[k,[...document.querySelectorAll('#'+k+' tei-p[id]')].map(p=>[p.id,p.textContent])]));
 const baseline=await page.evaluate(snapshot);
 await page.evaluate(()=>document.getElementById('french-pane-select').click());await ready(1);
 assert.deepEqual(await page.evaluate(snapshot),baseline);
 note('Default panes preserved; French opt-in; lazy book assets');
 assert.equal(await page.locator('#french select,#french input').count(),0);
 assert.equal(await page.locator('#millet-general-controls #millet-view').count(),1);
 assert.equal(await page.locator('#millet-folios').isChecked(),false);
 assert.equal(await page.locator('#millet-source .millet-folio-marker').count(),0);
 assert(!(await page.locator('#millet-source').innerText()).includes('¬'));
 assert.equal(await page.locator('#millet-source .millet-line').first().evaluate(e=>getComputedStyle(e).display),'inline');
 await page.locator('#millet-folios').check();assert(await page.locator('.millet-folio-marker').count());await page.locator('#millet-folios').uncheck();
 note('Flowing paragraphs; division markers hidden without source edits; folios opt-in; controls in general panel');
 for(let b=1;b<=5;b++){
  if(b!==1)await go(`/deh/?book=${b}&french=millet1556`);await ready(b);
  await select('#millet-view','source');await ready(b);
  const expected=data(b);
  assert(!(await page.locator('#millet-page option').allTextContents()).join(' ').includes('Image '));
  const checked=await page.evaluate(d=>{
   const check=(v,m)=>{if(!v)throw Error(m);};
   const lines=new Map([...document.querySelectorAll('#millet-source [data-source-line]')].map(e=>[e.id,e]));
   check(lines.size===d.lines.length,'Source line count');
   for(const l of d.lines){const e=lines.get(l.TEI_line_id);check(e?.textContent===l.text_exact,'Literal DOM '+l.TEI_line_id);
    for(const atom of e.children){const a=Number(atom.dataset.startCp),z=Number(atom.dataset.endCp);check(atom.textContent===Array.from(l.text_exact).slice(a,z).join(''),'Codepoint DOM');check(atom.textContent===l.text_exact.slice(Number(atom.dataset.startUtf16),Number(atom.dataset.endUtf16)),'UTF16 DOM');}}
   let selections=0,multiple=0,crossPage=0;
   for(const m of d.mappings){
    const p=document.getElementById(m.canonical.xml_id);check(p,'Full Latin unit '+m.canonical.xml_id);
    const literal=p.cloneNode(true);literal.querySelectorAll('tei-num,[data-original]').forEach(e=>e.remove());literal.querySelectorAll('tei-unclear[data-empty]').forEach(e=>e.textContent='');
    check(literal.textContent===m.canonical.text_exact,'Canonical source identity '+m.canonical.xml_id);
    p.dispatchEvent(new MouseEvent('click',{bubbles:true}));
    const selected=[...document.querySelectorAll('#millet-source .millet-selected')];
    check(selected.length>0,'No selected French source '+m.id);
    const actual=new Map();
    for(const e of selected){check(e.dataset.mappings.split(' ').includes(m.id),'Unrelated French highlight '+m.id);const id=e.closest('[data-source-line]').id;if(!actual.has(id))actual.set(id,[]);actual.get(id).push([Number(e.dataset.startCp),Number(e.dataset.endCp)]);}
    for(const f of m.fragments){const atoms=actual.get(f.line)||[];const relevant=atoms.filter(([a,z])=>a>=f.start_cp&&z<=f.end_cp).sort((a,b)=>a[0]-b[0]);let end=f.start_cp;for(const[a,z]of relevant){check(a===end,'Gap or duplicate highlight');end=z;}check(end===f.end_cp,'Exact fragment endpoint');}
    check([...actual.keys()].every(id=>m.fragments.some(f=>f.line===id)),'Chapter-wide false highlight');
    check(document.getElementById(m.canonical.xml_id).classList.contains('millet-latin-target'),'Reverse Latin selection');
    if(new Set(m.fragments.map(f=>lines.get(f.line).dataset.sourceImage)).size>1)crossPage++;
    if(m.fragments.length>1)multiple++;selections++;
   }
   return {book:d.book,sourceLines:lines.size,selections,multiple,crossPage};
  },expected);
  result.books.push(checked);save();console.log('PASS all units book '+b+' '+JSON.stringify(checked));
 }
 assert.equal(result.books.reduce((n,b)=>n+b.selections,0),558);note('All 558 selections have exact source-to-DOM highlights in the real reader');
 await go('/deh/?book=1&chapter=1&unit=1&french=millet1556');await ready(1);
 assert(!(await page.locator('#millet-source').innerText()).includes("I'AY autrefois"));
 assert(await page.locator('#millet-source').evaluate(source=>[...source.querySelectorAll('[data-mappings]')].filter(e=>getComputedStyle(e).display!=='none').every(e=>e.classList.contains('millet-selected'))));
 await select('#millet-view','book');await ready(1);assert((await page.locator('#millet-source').innerText()).includes("I'AY autrefois"));
 note('Text follows the current unit like Lodge; Complete text retains the native book');
 await go('/deh/?book=1&chapter=2&unit=1&french=millet1556');await ready(1);
 assert.match(await page.locator('#millet-status').textContent(),/many-to-one/);note('I.2.1 many-to-one deep link');
 await go('/deh/?book=1&chapter=8&unit=1&french=millet1556');await ready(1);
 assert(await page.locator('.millet-attention').count());note('I.8.1 inherited attention flag preserved');
 await select('#millet-view','page');await ready(1);await select('#millet-page',31);
 const share=await page.locator('#millet-share').getAttribute('href');await go(new URL(share).pathname+new URL(share).search);await ready(1);
 assert.equal(await page.locator('#millet-page').inputValue(),'31');assert.equal(await page.locator('#millet-view').inputValue(),'page');
 await page.locator('#millet-alignment').uncheck();assert.equal(await page.locator('.millet-selected').count(),0);await page.locator('#millet-alignment').check();
 await select('#millet-view','chapter');await ready(1);const chapter=await page.locator('#millet-chapter').inputValue();assert(chapter);
 await select('#millet-view','running');await ready(1);await page.goBack();await ready(1);assert.equal(await page.locator('#millet-view').inputValue(),'chapter');
 note('Page/chapter deep links, alignment switch, back navigation');
 await select('#millet-view','preliminary');await ready(0);
 assert.equal(await page.locator('#millet-source [data-source-line]').count(),data(0).lines.length);
 assert.equal(await page.locator('#millet-source .millet-linked').count(),0);note('Complete unmapped preliminary matter');
 await go('/deh/?book=2&french=millet1556&millet-view=page&millet-page=280');await ready(2);assert(await page.locator('.millet-empty').count());note('Blank page 280 retained');
 await go('/deh/?book=5&french=millet1556&millet-view=page&millet-page=588');await ready(5);assert(await page.locator('#millet-source [data-source-line]').count());note('Colophon page 588 retained');
 await go('/deh/?book=1&french=millet1556');await ready(1);
 const french=page.locator('#millet-source [data-mappings]').first();await french.click();assert(await page.locator('#latin .millet-latin-target').count());note('French passage click locates Latin');
 await page.locator('#millet-ussani').selectOption('latin-deh1-num1');assert.match(await page.locator('#millet-status').textContent(),/Prol\.1/);note('Prologue selectable through accessible Ussani control');
 await page.locator('#millet-ussani').selectOption('latin-deh1-num4');
 await page.locator('#millet-status > summary').click();
 const parallel=page.getByRole('link',{name:'Open existing DEH ↔ Josephus parallels'});await parallel.waitFor();await parallel.click();
 await page.waitForSelector('#parallel-bj-text tei-p');assert(await page.locator('#parallel-deh-text tei-p').count());
 await page.screenshot({path:path.join(out,'DEH_JOSEPHUS_PARALLEL.png'),fullPage:true});
 await page.locator('#parallel-close').click();await ready(1);assert(await page.locator('#french-pane-select').isChecked());note('Existing Josephus parallel round trip retains French state');
 await page.screenshot({path:path.join(out,'MILLET_DESKTOP.png'),fullPage:false});
 await page.setViewportSize({width:390,height:844});
 const overflow=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,boxes:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1&&getComputedStyle(e).display!=='none').slice(0,12).map(e=>({tag:e.tagName,id:e.id,class:e.className,right:e.getBoundingClientRect().right}))}));result.mobile=overflow;assert(overflow.scroll<=overflow.width+1,'Mobile horizontal overflow: '+JSON.stringify(overflow));
 await page.screenshot({path:path.join(out,'MILLET_MOBILE.png'),fullPage:false});note('Responsive 390px layout');
 assert.equal(result.errors.filter(e=>!/\$ is not defined|jQuery is not defined/.test(e)).length,0,JSON.stringify(result.errors));
 assert.equal(result.localHTTPFailures.length,0,JSON.stringify(result.localHTTPFailures));
 result.status='PASS';save();
} catch(e){result.status='FAIL';result.failure=e.stack;await page.screenshot({path:path.join(out,'FAILURE.png'),fullPage:false}).catch(()=>{});save();throw e;}
finally{await browser.close();}
