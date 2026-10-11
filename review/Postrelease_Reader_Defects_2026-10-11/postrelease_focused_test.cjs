const c=require('C:/workspace/LatinJosephus-postrelease-reader-repairs-runtime-20261011/qa/common.cjs');
(async()=>{const stage=process.argv[2],s=c.serve(c.path.join(c.runtime,stage+'-site')),o=await c.listen(s),ctx=await c.browser('package-'+stage),p=await ctx.newPage(),r={stage,origin:o,instrumentation:false,checks:[],errors:[],assets:[]};p.on('pageerror',e=>r.errors.push({url:p.url(),error:String(e)}));p.on('requestfailed',q=>r.errors.push({url:q.url(),error:q.failure()?.errorText}));p.on('response',q=>{if(q.status()>=400)r.errors.push({url:q.url(),status:q.status()})});
const open=async route=>{await p.goto(o+route);await p.waitForLoadState('networkidle');if(route.startsWith('/antiquities/')||route.startsWith('/bellum-')||route.startsWith('/deh/'))await p.waitForFunction(()=>document.querySelector('#latin')?.children.length>1||document.getElementById('unsupported-niese-notice'));};
const duplicateIds=()=>{const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);return ids.filter((x,i)=>ids.indexOf(x)!==i)};
try{
if(stage==='B'||stage==='final'){
 const bs=c.serve(c.path.join(c.runtime,'baseline-site')),bo=await c.listen(bs),bp=await ctx.newPage();try{
 for(const route of ['/antiquities/?book=1','/antiquities/?book=11','/antiquities/?book=20','/antiquities/?book=11&chapter=8','/antiquities/?book=11&niese=312','/antiquities/?book=20&niese=268','/bellum-judaicum/?book=1','/deh/?book=1']){
 await bp.goto(bo+route);await bp.waitForLoadState('networkidle');await bp.waitForFunction(()=>document.querySelector('#latin')?.children.length>1);const before=await bp.evaluate(()=>({panes:Object.fromEntries(['latin','greek','english'].map(l=>[l,document.getElementById(l)?.innerHTML.replaceAll(location.origin,'ORIGIN')])),notes:document.getElementById('annotations-list').innerHTML}));const beforeIDs=await bp.evaluate(duplicateIds);await open(route);
 const afterIDs=await p.evaluate(duplicateIds);if(route==='/bellum-judaicum/?book=1'){c.assert.deepEqual(beforeIDs,['header','annotations']);c.assert.deepEqual(afterIDs,['header']);r.checks.push({route,test:'independently reproduced pre-existing source-source header collision, outside annotations repair',beforeIDs,afterIDs,headerElements:await p.locator('[id="header"]').evaluateAll(ns=>ns.map(n=>({tag:n.tagName,pane:n.closest('#latin,#english')?.id,markup:n.outerHTML.slice(0,600)}))),result:'BASELINE LIMITATION'})}else c.assert.deepEqual(afterIDs,[],route+' duplicate IDs');c.assert.equal(await p.locator('#reader-annotations').count(),1);c.assert.equal(await p.locator('#collapse-annotations').getAttribute('data-mdb-parent'),'#reader-annotations');
 const after=await p.evaluate(()=>({panes:Object.fromEntries(['latin','greek','english'].map(l=>[l,document.getElementById(l)?.innerHTML.replaceAll(location.origin,'ORIGIN')])),notes:document.getElementById('annotations-list').innerHTML}));c.assert.deepEqual(after,before,'Source and generated annotation content must be unchanged '+route);
 const panel=p.locator('#reader-annotations');if(await panel.isVisible()){
 const b=p.locator('#annotations-header button'),collapse=p.locator('#collapse-annotations');await b.click();await p.waitForFunction(()=>document.getElementById('collapse-annotations').classList.contains('show'));c.assert.equal(await b.getAttribute('aria-expanded'),'true');await b.click();await p.waitForFunction(()=>!document.getElementById('collapse-annotations').classList.contains('show'));
 await p.locator('[data-mdb-target="#collapse-settings"]').click();const high=p.locator('#highlight-annotations');if(await high.isVisible()){await high.check();const highlighted=await p.locator('#latin .highlight').count();await high.uncheck();c.assert.equal(await p.locator('#latin .highlight').count(),0);r.checks.push({route,test:'annotation highlight',highlighted,result:'PASS'})}
 }else c.assert.equal(route,'/deh/?book=1');
 const sourceIDs=await p.locator('#latin [id="annotations"]').count();r.checks.push({route,test:'unique IDs, original TEI identity, unchanged note content and working disclosure',sourceAnnotationsIDs:sourceIDs,paneHashes:Object.fromEntries(Object.entries(after.panes).map(([l,v])=>[l,c.hash(v||'')])),notesSHA256:c.hash(after.notes),result:'PASS'});
 }
 }finally{await bp.close();await new Promise(r=>bs.close(r))}
}
if(stage==='D'||stage==='final'){
 for(const route of ['/','/about/','/background/']){
 await p.setViewportSize({width:1440,height:900});await open(route);
 c.assert.equal(await p.locator('#book-selector').count(),0);
 const content=await p.locator('body').innerText();c.assert(content.trim().length>200);
 c.assert.equal((await p.locator('html').getAttribute('data-theme'))==='dark',await p.locator('#light-toggle').getAttribute('aria-pressed')==='true');
 await p.getByRole('button',{name:'Dark mode',exact:true}).press('Space');
 await p.setViewportSize({width:390,height:844});await p.locator('.navbar-toggler').click();
 await p.waitForFunction(()=>document.getElementById('navbarNav').classList.contains('show'));c.assert(await p.locator('.navbar-collapse').isVisible());
 await p.locator('.navbar-toggler').click();await p.locator('.navbar-collapse').waitFor({state:'hidden'});
 await p.reload();await p.waitForLoadState('networkidle');
 r.checks.push({route,test:'general page startup, content, responsive navigation, theme and reload',bodyTextSHA256:c.hash(content),result:'PASS'})}
 await p.setViewportSize({width:1440,height:900});for(const route of ['/antiquities/?book=preface&niese=25','/antiquities/?book=1&niese=27','/antiquities/?book=7&niese=1','/bellum-judaicum/?book=1&niese=1','/deh/?book=1','/contra-apionem/?book=1']){await open(route);c.assert((await p.locator('#latin').innerText()).length>100);r.checks.push({route,test:'reader initialization preserved',result:'PASS'})}
}
c.assert.equal(r.errors.length,0,JSON.stringify(r.errors));r.result='PASS';
}catch(e){r.result='FAIL';r.failure=String(e);console.error(e);process.exitCode=1}finally{c.save('PACKAGE_'+stage+'_'+stage+'.json',r);await ctx.close();await new Promise(r=>s.close(r))}console.log('Package',stage,r.result,r.checks.length)})();
