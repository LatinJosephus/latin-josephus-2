const {fs,path,chromium,runtime,load,save,hash,serve,listen,narrative}=require('./qa-common18.cjs');
async function main(){
 const build=load(path.join(__dirname,'BUILD_CONTEXT.json')),servers=[serve(build.baseline_site,false),serve(build.site,false)],origins=[];
 for(const s of servers)origins.push(await listen(s));
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-interface-controls'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await context.newPage();
 const r={status:'RUNNING',build,scope:'Plain built reader labels, keyboard operation, contents, hidden encoded standOff isolation and UI identifiers',contents:[],keyboard:[],standOff:[],errors:[]};
 page.on('pageerror',e=>r.errors.push(String(e)));page.on('requestfailed',e=>r.errors.push(e.url()+':'+e.failure()?.errorText));page.on('console',e=>{if(e.type()==='error')r.errors.push(e.text())});page.on('response',e=>{if(e.status()>=400)r.errors.push(e.url()+':'+e.status())});
 try{
  for(const book of ['preface',1,11,15,16,17,18,19,20]){
   const captures=[];
   for(let side=0;side<2;side++){
    await page.goto(origins[side]+`/antiquities/?book=${book}&view=contents`,{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>document.querySelector('#latin .source-contents, #latin tei-div1'));
    captures.push(await page.evaluate(book=>Object.fromEntries(['latin','greek','english'].map(l=>{const c=document.querySelector('#'+l)?.cloneNode(true);if(book==='preface')c?.querySelectorAll('tei-milestone[unit="niese"],tei-milestone[unit="niese-end"],.niese-related-passage').forEach(n=>n.remove());return [l,c?.innerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')]})),book));
   }
   if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Plain contents changed '+book);
   r.contents.push({book,status:'PASS',digest:hash(captures[1]),approved_Proem_projection:book==='preface'?'Remove only approved 22 starts, exclusive end and tested related-passage UI; unchanged original source remains exact':null});
  }
  for(let side=0;side<2;side++){
   await page.goto(origins[side]+'/antiquities/?book=20',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>document.querySelector('#latin tei-div1'));
   const observed=await page.evaluate(()=>{
    const nodes=[...document.querySelectorAll('[id]')],duplicates=[...new Set(nodes.map(n=>n.id).filter((id,i,a)=>a.indexOf(id)!==i))];
    const standOff=[...document.querySelectorAll('tei-standoff')].map(n=>({id:n.id,display:getComputedStyle(n).display,visible:n.getClientRects().length>0,containsExecutable:n.querySelectorAll('a,button,input,select,script').length}));
    const active=[...document.querySelectorAll('a,button,input,select,[role="button"]')].filter(n=>n.id).map(n=>n.id);
    return {duplicates,standOff,activeDuplicateIDs:active.filter((id,i)=>active.indexOf(id)!==i),annotationPanel:document.querySelector('div#annotations')?.tagName,visibleStandOff:standOff.filter(n=>n.visible).length};
   });
   r.standOff.push({side,observed});
   if(observed.activeDuplicateIDs.length||observed.visibleStandOff||observed.standOff.some(x=>x.display!=='none'||x.containsExecutable))throw Error('Source-only standOff exposed/executable');
   if(JSON.stringify(observed.duplicates)!==JSON.stringify(['annotations'])||observed.annotationPanel!=='DIV')throw Error('Unexpected containing-view identifiers');
  }
  if(JSON.stringify(r.standOff[0].observed)!==JSON.stringify(r.standOff[1].observed))throw Error('Encoded source ID treatment changed');
  r.source_metadata_ID_observation='The unchanged Book XX standOff xml:id="annotations" is preserved as inert hidden encoded source; its duplicate with the visible UI div is present identically in the fresh baseline. No visible or executable duplicate ID, selected-view duplicate ID or annotation leakage is permitted.';
  await page.goto(origins[1]+'/antiquities/?book=preface&niese=25',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>['latin','greek','english'].every(l=>document.querySelector(`#${l} [type^="niese-"][n="25"]`)));
  await page.click('#display-settings-header button');
  const labels=await page.evaluate(()=>Object.fromEntries(['niese-selector','english-pane-select','greek-pane-select'].map(id=>[id,[...document.querySelector('#'+id).labels].map(l=>l.textContent.trim())])));
  if(Object.values(labels).some(x=>!x.length||!x.join('').trim()))throw Error('Accessible selector label absent');
  if(await page.locator('#niese-next').getAttribute('aria-label')!=='Next Niese section'||await page.locator('#niese-previous').getAttribute('aria-label')!=='Previous Niese section')throw Error('Accessible navigation names absent');
  await page.locator('#niese-selector').focus();await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');
  await page.waitForFunction(()=>['latin','greek','english'].every(l=>document.querySelector(`#${l} [type^="niese-"][n="26"]`)));
  r.keyboard.push({event:'Select next with ArrowDown and Enter',number:26,labels,status:'PASS'});
  await page.locator('#niese-previous').focus();await page.keyboard.press('Enter');await page.waitForFunction(()=>['latin','greek','english'].every(l=>document.querySelector(`#${l} [type^="niese-"][n="25"]`)));r.keyboard.push({event:'Activate Previous with Enter',number:25,status:'PASS'});
  for(const l of ['greek','english']){await page.uncheck('#'+l+'-pane-select');if(await page.locator('#'+l).isVisible())throw Error('Pane did not hide '+l);await page.check('#'+l+'-pane-select');if(!await page.locator('#'+l).isVisible())throw Error('Pane did not restore '+l);}
  r.pane_labels_and_keyboard='PASS';if(r.errors.length)throw Error(JSON.stringify(r.errors));r.status='PASS';
 }catch(e){r.status='FAIL';r.failure=String(e);throw e;}finally{save(path.join(__dirname,'INTERFACE_CONTROLS.json'),r);await context.close();for(const s of servers)await new Promise(resolve=>s.close(resolve));}
 console.log(JSON.stringify({status:r.status,plainContents:r.contents.length,keyboardEvents:r.keyboard.length,sourceMetadataIsolation:'PASS'}));
}
main().catch(e=>{console.error(e);process.exitCode=1});
