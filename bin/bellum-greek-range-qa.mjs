#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createServer} from 'node:http';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(fileURLToPath(new URL('../',import.meta.url)));
const args=process.argv.slice(2),option=(n,f)=>args.includes(n)?args[args.indexOf(n)+1]:f;
const site=path.resolve(option('--site',path.join(root,'_site'))),out=path.resolve(option('--out',path.join(root,'../bellum-greek-range-qa')));
fs.mkdirSync(out,{recursive:true});
const git=(...a)=>execFileSync('git',a,{cwd:root,maxBuffer:32*1024*1024});
const baseline=option('--baseline','b11075ac14272f0cda568f3bd8859cb0ba405aed'),preLodge='57b89a9d107bb76a2b30c146e401a2c76e25e4c3';
const oldRenderer=git('show',baseline+':assets/js/renderTei.js'),preRenderer=git('show',preLodge+':assets/js/renderTei.js');
const sha=b=>createHash('sha256').update(b).digest('hex');
const xml=git('ls-files','*.xml').toString().trim().split(/\r?\n/);assert.equal(xml.length,107);
const xmlHashes=Object.fromEntries(xml.map(p=>[p,sha(fs.readFileSync(path.join(root,p)))]));
fs.writeFileSync(path.join(out,'xml-before.json'),JSON.stringify(xmlHashes,null,2)+'\n');
const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.xml':'application/xml','.json':'application/json'};
async function host(renderer){
 const server=createServer((req,res)=>{try{
  let p=decodeURIComponent(new URL(req.url,'http://localhost').pathname);if(p.endsWith('/'))p+='index.html';
  let body;if(p==='/assets/js/renderTei.js'&&renderer)body=renderer;
  else{const directory=p.startsWith('/assets/')||p.startsWith('/bin/')?root:site;let file=path.resolve(directory,'.'+p);assert(file.startsWith(directory+path.sep));if(!fs.existsSync(file)&&directory===root){file=path.resolve(site,'.'+p);assert(file.startsWith(site+path.sep));}body=fs.readFileSync(file);}
  res.setHeader('Content-Type',(types[path.extname(p)]||'application/octet-stream')+'; charset=utf-8');res.end(body);
 }catch{res.writeHead(404);res.end('Missing QA resource');}});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));return server;
}
const servers=await Promise.all([host(null),host(oldRenderer),host(preRenderer)]),bases=servers.map(s=>'http://127.0.0.1:'+s.address().port);
const require=createRequire(import.meta.url),{chromium}=require(require.resolve('playwright',{paths:[option('--module-root',root)]}));
const browser=await chromium.launch({headless:true,executablePath:option('--browser',undefined)}),errors=[],external=[];
const context=await browser.newContext({viewport:{width:1280,height:900}});
await context.addInitScript(()=>{if(!HTMLCollection.prototype.forEach)HTMLCollection.prototype.forEach=Array.prototype.forEach;});
await context.route('https://**/*',route=>route.abort());
context.on('requestfailed',r=>(bases.some(b=>r.url().startsWith(b))?errors:external).push({url:r.url(),error:r.failure()?.errorText}));
async function pageAt(index,query=''){
 const page=await context.newPage();page.on('pageerror',e=>errors.push({type:'pageerror',message:e.message}));
 page.on('response',r=>{if(r.status()>=400&&bases.some(b=>r.url().startsWith(b)))errors.push({url:r.url(),status:r.status()});});
 page.on('console',m=>{if(m.text().startsWith('Greek range QA'))console.log(m.text());});
 await page.goto(bases[index]+'/bellum-judaicum/'+query,{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>document.querySelector('#greek tei-div1'));
 await page.addScriptTag({url:bases[index]+'/bin/bellum-greek-range-browser-qa.js'});return page;
}
try{
 if(args.includes('--focused-only')) {
const checks=[];
 const page=await pageAt(0);
 const old=await pageAt(1);
 const ready=async p=>p.waitForFunction(()=>document.querySelector('#greek tei-p,#greek tei-div1,#greek tei-div2'));
 async function goto(p,index,q){
  await p.goto(bases[index]+'/bellum-judaicum/'+q,{waitUntil:'domcontentloaded'});await ready(p);
  await p.evaluate(()=>document.querySelector('#collapse-settings')?.classList.add('show'));
 }
 await goto(page,0,'?book=1&niese=1&english=lodge1602');
 const noteSnapshot=()=>page.evaluate(()=>({html:document.querySelector('#english').innerHTML,
  notes:[...document.querySelectorAll('#english tei-note')].filter(n=>!n.closest('[data-original]')).map(n=>({text:n.textContent,display:getComputedStyle(n).display})),
  hidden:document.querySelector('#english').classList.contains('lodge-notes-hidden'),checked:document.querySelector('#lodge-notes-visible').checked}));
 const initial=await noteSnapshot();assert(initial.notes.length);assert(initial.checked&&!initial.hidden);
 await page.uncheck('#lodge-notes-visible');
 let hidden=await noteSnapshot();assert.equal(hidden.html,initial.html);assert(hidden.hidden&&!hidden.checked);assert(hidden.notes.every(n=>n.display==='none'));
 assert.equal(new URL(page.url()).searchParams.get('lodgeNotes'),'0');checks.push('note toggle: DOM unchanged, notes hidden, lodgeNotes=0');
 await page.reload({waitUntil:'domcontentloaded'});await ready(page);hidden=await noteSnapshot();assert(hidden.hidden&&!hidden.checked);checks.push('lodgeNotes=0 survives reload');
 await page.addScriptTag({url:bases[0]+'/bin/bellum-greek-range-browser-qa.js'});
 await page.evaluate(async()=>{await window.bellumGreekRangeQA.change('#niese-selector',2);});
 assert.equal(new URL(page.url()).searchParams.get('lodgeNotes'),'0');assert((await noteSnapshot()).hidden);checks.push('lodgeNotes=0 survives Niese navigation');
 await page.evaluate(async()=>{const q=window.bellumGreekRangeQA;await q.level('chapter');await q.change('#chapter-selector',4);});
 assert.equal(new URL(page.url()).searchParams.get('lodgeNotes'),'0');assert((await noteSnapshot()).hidden);
 await page.evaluate(async()=>{const q=window.bellumGreekRangeQA;await q.level('section');await q.change('#section-selector',86);});
 assert.equal(new URL(page.url()).searchParams.get('lodgeNotes'),'0');assert((await noteSnapshot()).hidden);checks.push('lodgeNotes=0 survives Chapter/Sub-chapter navigation');
 await page.evaluate(async()=>{await window.bellumGreekRangeQA.change('#english-source-selector','whiston');await window.bellumGreekRangeQA.change('#english-source-selector','lodge1602');});
 assert((await noteSnapshot()).hidden);checks.push('lodgeNotes=0 survives witness switching');
 await page.check('#lodge-notes-visible');assert(!(await noteSnapshot()).hidden);assert.equal(new URL(page.url()).searchParams.get('lodgeNotes'),null);checks.push('notes restored with default URL');
 for(const q of ['?book=1&niese=33&english=lodge1602','?book=6&niese=3&english=lodge1602&lodgeNotes=0']){
  await goto(page,0,q);await goto(old,1,q);
  assert.equal(await page.locator('#english').innerHTML(),await old.locator('#english').innerHTML(),'Special Lodge DOM '+q);
  if(q.includes('niese=33')){
   const pos=await page.evaluate(()=>{
    const p=document.querySelector('#english tei-p'),num=p.querySelector('tei-num.niese-generated');
    const walker=document.createTreeWalker(p,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.data.trim()&&!n.parentElement.closest('tei-num.niese-generated,[data-original],tei-note')?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_SKIP});
    const t=walker.nextNode(),r=document.createRange();r.setStart(t,0);r.setEnd(t,Math.min(t.length,20));
    return {label:num.getBoundingClientRect().y,text:r.getBoundingClientRect().y};
   });assert(Math.abs(pos.label-pos.text)<5);checks.push('I.33 citation shares the prose line');
  }else{
   const omission=await page.locator('#english tei-gap[reason="omitted"][unit="niese-section"]').evaluate(g=>({display:getComputedStyle(g).display,notice:getComputedStyle(g,'::before').content}));
   assert.notEqual(omission.display,'none');assert.equal(omission.notice,'"'+ '[Omitted in Lodge]' +'"');checks.push('VI.3 omission visible with notes hidden');
  }
 }
 await page.close();await old.close();
 const existing=await pageAt(0);
 await existing.addScriptTag({url:bases[0]+'/bin/lodge1602-bellum-browser-qa.js'});
 const state=await existing.evaluate(async()=>{await window.lodgeSourceStateQA();return window.lodgeSourceStateResult;});
 assert.equal(state.status,'PASS');checks.push('existing lodgeSourceStateQA: all seven books/four levels, sources/history');
 await existing.reload({waitUntil:'domcontentloaded'});await ready(existing);
 assert((await existing.locator('#english h3').innerText()).includes('Lodge'));checks.push('existing history-selected Lodge state survives reload');
 await existing.close();
 const shell=errors.filter(e=>e.type==='pageerror'&&/\$ is not defined|mediumZoom is not defined|Masonry is not defined|imagesLoaded is not defined/.test(e.message));
 assert.deepEqual(errors.filter(e=>!shell.includes(e)),[]);
 fs.writeFileSync(path.join(out,'focused-qa.json'),JSON.stringify({status:'PASS',checks,state},null,2)+'\n');
 console.log(JSON.stringify({status:'PASS',checks},null,2));
 } else if(args.includes('--existing-static-only')) {
  let script=fs.readFileSync(path.join(root,'bin/lodge1602-bellum-qa.ps1'),'utf8');
  const first=script.indexOf('  foreach ($p in $manifest.original_xml_sha256.PSObject.Properties) {');
  const last=script.indexOf('  foreach ($book in $results)',first);
  assert(first>=0 && last>first,'Existing legacy inventory gate block');
  script=script.slice(0,first)+'  # Bellum-only invocation; later Antiquities VI release supersedes the historical 100-file gate.\n'+script.slice(last);
  script=script.replace('original_bellum_xml_byte_identical=21; all_original_xml_byte_identical=100',
    'original_bellum_xml_byte_identical=21; historical_non_bellum_gate="excluded: superseded by later Antiquities VI release"');
  const file=path.join(out,'lodge-bellum-static-scoped.ps1');fs.writeFileSync(file,script);
  const result=JSON.parse(execFileSync(option('--pwsh','pwsh'),['-NoProfile','-File',file,'-MasterZip',
    option('--master-zip',''),'-RepoRoot',root,'-SelfTest','-NoWrite'],{encoding:'utf8',maxBuffer:8*1024*1024}));
  for(const p of xml)assert.equal(sha(fs.readFileSync(path.join(root,p))),xmlHashes[p],'Static QA XML unchanged '+p);
  assert.equal(result.status,'PASS');
  fs.writeFileSync(path.join(out,'lodge-bellum-static.json'),JSON.stringify(result,null,2)+'\n');
  console.log('Existing Bellum static/frozen-master/self-test PASS; current 107 XML unchanged.');
 } else if(args.includes('--existing-lodge-only')) {
  const page=await pageAt(0);
  await page.addScriptTag({url:bases[0]+'/bin/lodge1602-bellum-browser-qa.js'});
  page.on('console',m=>{if(m.text().startsWith('Lodge QA progress'))console.log(m.text());});
  const result=await page.evaluate(()=>window.lodgeReaderQA('lodge1602'));
  const expected=JSON.parse(fs.readFileSync(path.join(root,'_docs/lodge1602-bellum-browser-qa.json'),'utf8')).lodge;
  assert.equal(result.digest,expected.digest,'Existing Lodge rendered text/IDs digest');
  await page.close();
  const shell=errors.filter(e=>e.type==='pageerror'&&/\$ is not defined|mediumZoom is not defined|Masonry is not defined|imagesLoaded is not defined/.test(e.message));
  assert.deepEqual(errors.filter(e=>!shell.includes(e)),[]);
  fs.writeFileSync(path.join(out,'existing-lodge-browser-qa.json'),JSON.stringify({status:'PASS',...result,frozen_digest_match:true},null,2)+'\n');
  console.log(JSON.stringify(result,null,2));
 } else {
 const reproductions=[];
 for(const index of [1,2]){
  const page=await pageAt(index);
  for(const book of [1,3,6,7])reproductions.push({revision:index===1?baseline:preLodge,...await page.evaluate(b=>window.bellumGreekRangeQA.reproduce(b),book)});
  await page.close();
 }
 fs.writeFileSync(path.join(out,'reproduction.json'),JSON.stringify(reproductions,null,2)+'\n');
 console.log(JSON.stringify(reproductions.map(r=>({revision:r.revision,book:r.book,chapter:r.chapter,missing:r.missing,unit:r.unit,direct:r.direct})),null,2));
 for(const revision of [baseline,preLodge]){const r=reproductions.find(r=>r.revision===revision&&r.book===1);assert(r.missing.includes(87));assert.deepEqual(r.direct,[87]);}
 if(args.includes('--reproduce-only'))console.log('PRE-EXISTING: I.87 omission reproduced at current and pre-Lodge revisions.');
 else {
  const fingerprint=sha(Buffer.concat([fs.readFileSync(path.join(root,'assets/js/renderTei.js')),oldRenderer,
    fs.readFileSync(path.join(root,'bin/bellum-greek-range-browser-qa.js')),
    fs.readFileSync(path.join(root,'assets/js/CETEI.js')),fs.readFileSync(path.join(root,'assets/css/tei.css')),
    fs.readFileSync(path.join(site,'bellum-judaicum/index.html')),fs.readFileSync(path.join(site,'assets/css/main.css')),
    Buffer.from(JSON.stringify(xmlHashes))]));
  const checkpointPath=path.join(out,'checkpoint.json');
  let checkpoint={fingerprint,results:{}};
  if(args.includes('--resume')&&fs.existsSync(checkpointPath)){const saved=JSON.parse(fs.readFileSync(checkpointPath));if(saved.fingerprint===fingerprint)checkpoint=saved;}
  const save=()=>fs.writeFileSync(checkpointPath,JSON.stringify(checkpoint,null,2)+'\n');
  const tasks=[];
  for(const source of ['whiston','lodge1602']) for(let b=1;b<=7;b++) tasks.push({source,book:b});
  const results=[];let cursor=0;
  async function worker(){
   while(cursor<tasks.length){
    const task=tasks[cursor++],key=task.source+':'+task.book;
    if(checkpoint.results[key]){results.push(checkpoint.results[key]);continue;}
    const current=await pageAt(0),previous=await pageAt(1);
    try{
     const [after,before]=await Promise.all([
      current.evaluate(({book,source})=>window.bellumGreekRangeQA.book(book,source,true),task),
      previous.evaluate(({book,source})=>window.bellumGreekRangeQA.book(book,source,false),task)
     ]);
     assert.deepEqual(after.digests,before.digests,'Cardwell/English/direct Greek DOM and text changed '+key);
     const result={...after,baseline_exact_match:true};results.push(result);checkpoint.results[key]=result;save();
     console.log('PASS '+key+' '+JSON.stringify(after.counts));
    }finally{await current.close();await previous.close();}
   }
  }
  await Promise.all([worker(),worker()]);
  const whiston=results.filter(r=>r.source==='whiston').sort((a,b)=>a.book-b.book);
  const lodge=results.filter(r=>r.source==='lodge1602').sort((a,b)=>a.book-b.book);
  const totals=rows=>rows.reduce((s,r)=>({chapters:s.chapters+r.counts.chapters,subchapters:s.subchapters+r.counts.subchapters,niese:s.niese+r.counts.niese}),{chapters:0,subchapters:0,niese:0});
  assert.deepEqual(totals(whiston),{chapters:111,subchapters:704,niese:4001});
  assert.deepEqual(totals(lodge),totals(whiston));
  assert(whiston.some(r=>r.split.length),'Corpus must exercise sections shared by adjacent coarse units');
  for(const p of xml)assert.equal(sha(fs.readFileSync(path.join(root,p))),xmlHashes[p],'Final XML hash '+p);
  const shell=errors.filter(e=>e.type==='pageerror'&&/\$ is not defined|mediumZoom is not defined|Masonry is not defined|imagesLoaded is not defined/.test(e.message));
  assert.deepEqual(errors.filter(e=>!shell.includes(e)),[],'Relevant browser/local HTTP errors');
  const report={status:'PASS',baseline,pre_lodge:'PRE-EXISTING',browser:await browser.version(),
   environment:'Actual built page shell and compiled main CSS; renderer/CETEI/TEI CSS/XML from current checkout. Offline HTMLCollection.forEach adapter; CDN shell failures classified separately.',
   greek:totals(whiston),whiston:totals(whiston),lodge:totals(lodge),xml_count:xml.length,xml_sha256:xmlHashes,
   split_boundaries:whiston.flatMap(r=>r.split),safeguards:whiston.flatMap(r=>r.safeguards),
   reproductions,results,relevant_errors:[],offline_shell_error_count:shell.length};
  fs.writeFileSync(path.join(out,'corpus-qa.json'),JSON.stringify(report,null,2)+'\n');
  console.log('CORPUS PASS '+JSON.stringify(report.greek));
 }
 }
}finally{await browser.close();for(const s of servers)s.close();}
