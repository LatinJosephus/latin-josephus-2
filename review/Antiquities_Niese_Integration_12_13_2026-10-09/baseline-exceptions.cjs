const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {serve}=require('./book-browser.cjs');
const runtime='C:/workspace/Antiquities-Niese-12-13-integration-runtime-20261009',published='C:/workspace/Antiquities-Niese-Preview-08-10-2026-10-09';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const records=['PUBLICATION_SUMMARY.json','APPARATUS_LINK_DIAGNOSTIC.json','LINK_SCAN_INHERITED_ISSUE_QA.json'];
const report={source_records:records.map(n=>({path:path.join(published,n),sha256:sha(fs.readFileSync(path.join(published,n)))})),checks:[],result:'PENDING'};
(async()=>{
 const servers=[serve(path.join(runtime,'baseline-site')),serve(path.join(runtime,'site'))];
 for(const s of servers)await new Promise(r=>s.listen(0,'127.0.0.1',r));
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-profile-baseline-exceptions'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
 const expected=JSON.parse(fs.readFileSync(path.join(published,'APPARATUS_LINK_DIAGNOSTIC.json'),'utf8'))[0].refs.map(x=>x.html.match(/href="([^"]+)"/)[1]);
 for(let i=0;i<2;i++){
  const origin=`http://127.0.0.1:${servers[i].address().port}`,page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(origin+'/antiquities/?book=1&bamberg=B78-table1-row005');await page.waitForFunction(()=>window.__qaReady);
  const hrefs=await page.locator('a[href^="undefined"]').evaluateAll(a=>a.map(n=>n.getAttribute('href')));
  if(JSON.stringify(hrefs)!==JSON.stringify(expected))throw Error('Unbounded apparatus-link difference');
  const targets=[];for(const href of new Set(hrefs)){const response=await page.request.get(origin+'/antiquities/'+href);if(response.status()!==404)throw Error('Baseline broken target changed');targets.push({href,status:response.status()});}
  if(errors.length)throw Error('Unexpected supported Bamberg route exception');
  await page.goto(origin+'/antiquities/?book=1&niese=1');
  await page.waitForFunction(()=>document.querySelector('#niese-selector')?.options.length>1);
  await page.waitForTimeout(500);
  if(errors.length!==1||!errors[0].includes("Cannot read properties of null (reading 'querySelector')"))throw Error('Unsupported I.1 does not match bounded baseline error');
  const inventory=await page.locator('#niese-selector').evaluate(n=>({value:n.value,firstSupported:[...n.options].find(o=>o.value)?.value}));
  if(inventory.value!==''||inventory.firstSupported!=='27')throw Error('I.1 inventory classification');
  errors.length=0;await page.goto(origin+'/antiquities/?book=1&niese=27');await page.waitForFunction(()=>window.__qaReady);if(errors.length)throw Error('Supported I.27 error');
  report.checks.push({build:i?'candidate':'frozen_baseline',apparatus_route:'/antiquities/?book=1&bamberg=B78-table1-row005',hyperlinks:hrefs,broken_hyperlinks:3,distinct_broken_targets:targets,unsupported_route:'/antiquities/?book=1&niese=1',unsupported_error:"TypeError: Cannot read properties of null (reading 'querySelector')",inventory,supported_I_27:'PASS'});await page.close();
 }
 report.result='PASS';fs.writeFileSync(path.join(__dirname,'BOUNDED_BASELINE_EXCEPTIONS.json'),JSON.stringify(report,null,2)+'\n');console.log('PASS exact inherited exceptions');
 }finally{await context.close();for(const s of servers)await new Promise(r=>s.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
