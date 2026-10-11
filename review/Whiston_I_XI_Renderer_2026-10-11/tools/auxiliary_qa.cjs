const q=require('./browser_qa.cjs'),fs=require('fs'),path=require('path');
const {root,site,pack,chromium,serve,listen,open,assert,hash,oracle,snapshot,checkInterval}=q;
async function main(){
 const report={status:'RUNNING',errors:[]},srv=serve(),origin=await listen(srv);
 const html='<!doctype html><meta charset="utf-8"><title>DEH concordance regression</title><button id="run">Run</button><p id="qa-status"></p><pre id="qa-result"></pre><script src="/assets/js/CETEI.js"></script><script type="module" src="/bin/deh-parallels-browser-qa.js"></script>';
 fs.writeFileSync(path.join(site,'qa-deh.html'),html);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const ctx=await browser.newContext();
 const page=await ctx.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
 try{
  await page.goto(origin+'/qa-deh.html');await page.locator('#run').click();
  await page.waitForFunction(()=>document.querySelector('#qa-result').dataset.complete==='true',null,{timeout:60000});
  report.DEHConcordance=JSON.parse(await page.locator('#qa-result').textContent());
  assert(report.DEHConcordance.passed,'DEH concordance regression failed',report.DEHConcordance);
  console.log('DEH concordance checks passed',report.DEHConcordance.componentChecks.length);
  await open(page,origin,'bellum-judaicum','book=1&english=lodge1602');
  await page.addScriptTag({url:origin+'/bin/lodge1602-bellum-browser-qa.js'});
  await page.evaluate(()=>window.lodgeSourceStateQA());
  report.LodgeSourceState=await page.evaluate(()=>window.lodgeSourceStateResult);
  assert(report.LodgeSourceState.status==='PASS','Lodge source/history regression failed');
  await open(page,origin,'bellum-judaicum','book=1&niese=33&english=lodge1602');
  const before=await page.locator('#english').innerHTML();await page.locator('#lodge-notes-visible').uncheck({force:true});
  assert(await page.locator('#english').innerHTML()===before,'Lodge note toggle changed source DOM');
  const hidden=await page.locator('#english tei-note').evaluateAll(es=>es.filter(e=>!e.closest('[data-original]')).every(e=>getComputedStyle(e).display==='none'));
  assert(hidden,'Lodge notes did not hide');assert(new URL(page.url()).searchParams.get('lodgeNotes')==='0','Lodge URL preference missing');
  report.LodgeNoteToggle={passed:true,DOMUnchanged:true,notesHidden:true,sourceHash:hash(before)};
  await open(page,origin,'bellum-judaicum','book=6&niese=3&english=lodge1602&lodgeNotes=0');
  const omission=await page.locator('#english tei-gap[reason="omitted"]').evaluate(e=>({display:getComputedStyle(e).display,notice:getComputedStyle(e,'::before').content}));
  assert(omission.display!=='none'&&omission.notice.includes('Omitted in Lodge'),'Lodge omission notice disappeared');report.LodgeOmission={passed:true,...omission};
  report.markup=[];
  for(const expected of JSON.parse(fs.readFileSync(path.join(pack,'MARKUP_ORACLE.json')))){
   await open(page,origin,'antiquities',`book=${expected.book}&niese=${expected.number}`);
   checkInterval(await snapshot(page),oracle.find(e=>e.book===expected.book&&e.number===expected.number));
   const elements=await page.locator('#english').evaluate(pane=>{
    const clone=pane.cloneNode(true);clone.querySelectorAll('[data-original]').forEach(e=>e.remove());
    return [...clone.querySelectorAll('tei-anchor,tei-lb,tei-hi')].map(e=>({tag:e.localName.slice(4),attrs:Object.fromEntries([...e.attributes].filter(a=>!a.name.startsWith('data-')&&a.name!=='hidden'&&a.name!=='id').map(a=>[a.name.replace('xml:',''),a.value])),text:e.textContent.replace(/\s+/g,' ').trim()}));
   });
   assert(JSON.stringify(elements)===JSON.stringify(expected.elements),'Inline markup changed in displayed interval', {expected,actual:elements});
   report.markup.push({book:expected.book,number:expected.number,elements:elements.length,passed:true});
  }
  assert(report.errors.length===0,'Auxiliary browser errors',report.errors);report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{fs.writeFileSync(path.join(pack,'AUXILIARY_QA.json'),JSON.stringify(report,null,2)+'\n');await browser.close();srv.close();}
 console.log('Auxiliary QA',report.status);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
