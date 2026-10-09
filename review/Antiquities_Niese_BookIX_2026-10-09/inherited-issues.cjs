const {fs,path,crypto,chromium,packet,build,serve}=require('./qa-common.cjs');
const publicationPath='C:/workspace/Antiquities-Niese-Preview-08-10-2026-10-09/PUBLICATION_SUMMARY.json';
const publication=JSON.parse(fs.readFileSync(publicationPath,'utf8'));
async function main(){
 const servers=[serve(path.join(build,'baseline-site')),serve(path.join(build,'site'))];await Promise.all(servers.map(s=>new Promise(r=>s.listen(0,'127.0.0.1',r))));const origins=servers.map(s=>`http://127.0.0.1:${s.address().port}`);
 const context=await chromium.launchPersistentContext('C:/workspace/Antiquities-Niese-09-runtime-20261009/profile-inherited-issues',{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});const page=await context.newPage();const report={publicationPath,publicationSHA256:crypto.createHash('sha256').update(fs.readFileSync(publicationPath)).digest('hex'),baseline:'ad3158b7a86dea6997510b3de17f2e510c23367c',origins,checks:[]};
 try{
  const known=publication.inherited_issues[0];
  for(const origin of origins){
   await page.goto(origin+known.route);await page.waitForFunction(()=>window.__qaReady);
   const hrefs=await page.locator('a[href^="undefined"]').evaluateAll(nodes=>nodes.map(a=>a.getAttribute('href')));
   if(JSON.stringify(hrefs)!==JSON.stringify(known.identical_public_and_baseline_hrefs))throw Error('Inherited apparatus target changed');
   const status=[];for(const href of new Set(hrefs)){const response=await page.request.get(new URL(href,origin+'/antiquities/').href);if(response.status()!==404)throw Error('Unexpected target status');status.push({href,status:response.status()});}
   report.checks.push({origin,route:known.route,hrefs,brokenLinks:hrefs.length,distinctTargets:status.length,status,result:'MATCHES_PRECISE_INHERITED_EXCEPTION'});
   const error=page.waitForEvent('pageerror');await page.goto(origin+'/antiquities/?book=1&niese=1');const e=String(await error);
   if(!e.includes("Cannot read properties of null (reading 'querySelector')"))throw Error('Additional unsupported-route error '+e);
   const unsupported=await page.locator('#niese-selector').evaluate(el=>({selectorValue:el.value,firstSupported:[...el.options].find(o=>o.value)?.value}));if(unsupported.selectorValue!==''||unsupported.firstSupported!=='27')throw Error('Unsupported I.1 inventory changed');
   await page.goto(origin+'/antiquities/?book=1&niese=27');await page.waitForFunction(()=>window.__qaReady);if(await page.locator('#niese-selector').inputValue()!=='27')throw Error('Supported I.27');
   report.checks.push({origin,unsupported_I_1:unsupported,error:e,supported_I_27:'PASS',result:'MATCHES_PRECISE_INHERITED_EXCEPTION'});
  }
  report.result='PASS';fs.writeFileSync(path.join(packet,'INHERITED_ISSUES_QA.json'),JSON.stringify(report,null,2));console.log('PASS precisely bounded inherited exceptions');
 }catch(e){report.failure=String(e);report.result='FAIL';fs.writeFileSync(path.join(packet,'INHERITED_ISSUES_FAILURE.json'),JSON.stringify(report,null,2));throw e;}
 finally{await context.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
