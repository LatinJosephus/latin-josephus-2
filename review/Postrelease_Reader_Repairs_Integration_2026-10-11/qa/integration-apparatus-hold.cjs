const c=require('C:/workspace/Postrelease-Reader-Repairs-Integration-runtime-20261011/qa/common.cjs');
(async()=>{
 const s=c.serve(c.path.join(c.runtime,'baseline-site')),origin=await c.listen(s),ctx=await c.browser('integration-independent-C-hold'),p=await ctx.newPage();
 const r={started:new Date().toISOString(),baseline_origin:origin,route:'/antiquities/?book=1&bamberg=5',status:'RUNNING',baseline_errors:[],requests:[]};
 p.on('pageerror',e=>r.baseline_errors.push(String(e)));p.on('requestfailed',x=>r.baseline_errors.push(x.url()+': '+x.failure()?.errorText));
 try{
  await p.goto(origin+r.route,{waitUntil:'domcontentloaded'});await p.waitForSelector('#latin tei-p',{state:'attached'});await p.waitForLoadState('networkidle');
  r.links=await p.locator('#latin tei-ref a[href]').evaluateAll(ns=>ns.filter(n=>n.getAttribute('href').startsWith('undefinednote')).map(n=>({href:n.getAttribute('href'),source_target:n.closest('tei-ref').getAttribute('target'),paragraph:n.closest('tei-p').id,label:n.textContent})));
  const final=c.load?c.load('FIVE_DEFECTS_candidate-final.json'):JSON.parse(c.fs.readFileSync(c.path.join(c.runtime,'FIVE_DEFECTS_candidate-final.json'),'utf8'));
  const row=final.rows.find(x=>x.route===r.route);
  const after=row.state.links.filter(n=>n.href.startsWith('undefinednote')).map(n=>({href:n.href,source_target:n.source_target,paragraph:n.paragraph,label:n.label}));
  c.assert.equal(r.links.length,3);c.assert.deepEqual(after,r.links);c.assert.deepEqual(r.baseline_errors,[]);c.assert.deepEqual(row.errors,[]);c.assert.deepEqual(row.network,[]);
  for(const href of new Set(r.links.map(n=>n.href))){const response=await ctx.request.get(origin+'/antiquities/'+href);r.requests.push({href,URL:response.url(),status:response.status()});c.assert.equal(response.status(),404)}
  c.assert.equal(r.requests.length,2);c.assert.equal(final.linkRequests.length,2);c.assert(final.linkRequests.every(n=>n.status===404));
  r.original_identifiers_preserved=true;r.no_guessed_redirect=true;r.final_requests=final.linkRequests;r.status='KNOWN UNRESOLVED — EDITORIAL HOLD';
 }finally{r.finished=new Date().toISOString();c.save('APPARATUS_HOLD_COMPARISON.json',r);await ctx.close();await new Promise(r=>s.close(r))}
 console.log(r.status,'3 original links; 2 unchanged 404 targets independently reproduced');
})().catch(e=>{console.error(e);process.exitCode=1});
