// Real-reader chapter coverage: combine existing sub-chapter intervals exactly.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const {chromium}=createRequire(import.meta.url)('playwright');
const args=process.argv.slice(2),opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
assert(args.includes('--output'));const out=path.resolve(opt('--output','')),base=opt('--base-url','http://127.0.0.1:4019');
fs.mkdirSync(out,{recursive:true});
const folder=fileURLToPath(new URL('../assets/data/deh-millet1556/',import.meta.url));
const books=[1,2,3,4,5].map(n=>JSON.parse(fs.readFileSync(path.join(folder,`book-0${n}.json`))));
const browser=await chromium.launch({headless:true,executablePath:opt('--browser-executable','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')});
const page=await browser.newPage({viewport:{width:1440,height:900}});page.setDefaultTimeout(45000);
const result={status:'RUNNING',browser:browser.version(),chapters:[],checks:[],errors:[]};
page.on('pageerror',e=>result.errors.push(e.message));
const save=()=>fs.writeFileSync(path.join(out,'CHAPTER_BROWSER_QA.json'),JSON.stringify(result,null,2)+'\n');
const ready=async(chapter)=>page.waitForFunction(ch=>document.querySelector('#millet-status')?.textContent.includes(`Ussani ${ch}:`)&&!!document.querySelector('#millet-source'),chapter);
const global=async()=>{const b=page.locator('#display-settings-header button');if(await b.getAttribute('aria-expanded')!=='true')await b.click();await page.waitForFunction(()=>document.querySelector('#collapse-settings').classList.contains('show'));};
const settings=async()=>{if(!await page.locator('#millet-ussani').isVisible())await page.locator('#millet-settings > summary').click();};
const label=(book,chapter)=>String(chapter)==='0'?'Prologue':`${['','I','II','III','IV','V'][book]}.${chapter}`;
const checkChapter=async(b,ch)=>{
 const mappings=b.mappings.filter(m=>String(m.canonical.chapter)===String(ch));await ready(label(b.book,ch));
 const checked=await page.evaluate(({b,mappings,ch})=>{
  const check=(ok,msg)=>{if(!ok)throw Error(msg);};
  const wanted=new Set(mappings.map(m=>m.id)),ids=new Set(mappings.flatMap(m=>m.fragments.map(f=>f.line)));
  const lines=new Map([...document.querySelectorAll('#millet-source [data-source-line]')].map(e=>[e.id,e]));
  check(lines.size===ids.size,'Chapter line count');check([...lines.keys()].every(id=>ids.has(id)),'Unrelated source line');
  for(const l of b.lines.filter(l=>ids.has(l.TEI_line_id)))check(lines.get(l.TEI_line_id).textContent===l.text_exact,'Changed exact source payload');
  const merge=aa=>{const out=[];for(const[a,z]of aa.sort((a,b)=>a[0]-b[0])){if(out.length&&a<=out.at(-1)[1])out.at(-1)[1]=Math.max(out.at(-1)[1],z);else out.push([a,z]);}return out;};
  const actual=new Map();
  for(const span of document.querySelectorAll('#millet-source .millet-selected')){
   check(span.dataset.mappings.split(' ').some(id=>wanted.has(id)),'Unrelated highlight');
   const line=span.closest('[data-source-line]').id;if(!actual.has(line))actual.set(line,[]);actual.get(line).push([Number(span.dataset.startCp),Number(span.dataset.endCp)]);
   const source=b.lines.find(l=>l.TEI_line_id===line).text_exact;
   check(span.textContent===Array.from(source).slice(Number(span.dataset.startCp),Number(span.dataset.endCp)).join(''),'Changed selected codepoints');
   check(span.textContent===source.slice(Number(span.dataset.startUtf16),Number(span.dataset.endUtf16)),'Changed UTF16 offsets');
  }
  for(const id of ids){const expected=merge(mappings.flatMap(m=>m.fragments.filter(f=>f.line===id).map(f=>[f.start_cp,f.end_cp])));check(JSON.stringify(merge(actual.get(id)||[]))===JSON.stringify(expected),'Chapter interval union '+id);}
  const latin=[...document.querySelectorAll('#latin .millet-latin-target')].map(e=>e.id).sort();
  check(JSON.stringify(latin)===JSON.stringify(mappings.map(m=>m.canonical.xml_id).sort()),'Latin group selection');
  return {book:b.book,chapter:String(ch),units:mappings.length,sourceLines:lines.size,selectedAtoms:document.querySelectorAll('.millet-selected').length};
 },{b,mappings,ch});result.chapters.push(checked);save();
};
try{
 for(const b of books){
  const chapters=[...new Set(b.mappings.map(m=>m.canonical.chapter))];
  await page.goto(base+`/deh/?book=${b.book}&chapter=${chapters[0]}&french=millet1556`,{waitUntil:'domcontentloaded'});await ready(label(b.book,chapters[0]));await global();
  for(const ch of chapters){await page.locator('#chapter-selector').selectOption(String(ch));await checkChapter(b,ch);}
  console.log('PASS all chapters book '+b.book);
 }
 assert.equal(result.chapters.reduce((n,c)=>n+c.units,0),558);
 result.checks.push('Every chapter and Prologue: exact union, no missing/duplicate lines, original character offsets, all Latin units highlighted');
 // A legacy chapter URL may still carry a stale single-unit parameter.
 await page.goto(base+'/deh/?book=5&chapter=1&french=millet1556&millet-unit=latin-deh5-num1');await checkChapter(books[4],'1');await global();
 await page.locator('#millet-alignment').uncheck();assert.equal(await page.locator('.millet-selected').count(),0);
 await page.locator('#millet-alignment').check();await checkChapter(books[4],'1');
 await page.locator('#latin #latin-deh5-num2').click();
 await page.waitForFunction(()=>document.querySelector('#millet-status').textContent.includes('Ussani V.1.2:'));
 assert.equal(await page.locator('#latin .millet-latin-target').count(),1);assert.equal(new URL(page.url()).searchParams.get('millet-select'),'unit');
 await page.reload();await ready('V.1.2');assert.equal(await page.locator('#latin .millet-latin-target').count(),1);
 await settings();await page.locator('#millet-ussani').selectOption('');await checkChapter(books[4],'1');
 await page.goBack();await ready('V.1.2');await page.goForward();await checkChapter(books[4],'1');
 await page.locator('#millet-settings > summary').click();await page.evaluate(()=>scrollTo(0,0));
 await page.screenshot({path:path.join(out,'CHAPTER_V1.png')});
 await page.locator('#millet-status > summary').click();assert.equal(await page.locator('#millet-status > details').count(),5);
 await page.screenshot({path:path.join(out,'CHAPTER_V1_DETAILS.png')});
 result.checks.push('Legacy links, highlighting switch, individual selection, share/reload, Whole Ussani chapter option and history');
 await global();await page.locator('#section-level').check();await page.locator('#section-selector').selectOption({label:'[V.1.1]'});await ready('V.1.1');
 await page.locator('#chapter-selector').selectOption('2');await checkChapter(books[4],'2');
 result.checks.push('Changing the chapter before choosing a sub-chapter follows the whole chapter');
 assert.equal(result.errors.length,0,JSON.stringify(result.errors));result.status='PASS';save();
}catch(e){result.status='FAIL';result.failure=e.stack;save();await page.screenshot({path:path.join(out,'CHAPTER_FAILURE.png')});throw e;}
finally{await browser.close();}
