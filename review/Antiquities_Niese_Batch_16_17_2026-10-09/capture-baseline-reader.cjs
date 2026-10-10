/* Read-only executable-view baseline, not new Niese certification. */
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),packet=__dirname,runtime='C:/workspace/Antiquities-Niese-16-17-runtime-20261009',site=path.join(runtime,'baseline-build/site');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
function instrument(s){
  s=s.replace('  bookTitle.innerText = activeWork.title;',`  window.__qa={getState:()=>({...state}),getData:()=>fullData,traditionalRows,bambergRows,traditionalRangeView,milestoneChapterView};\n  bookTitle.innerText = activeWork.title;`);
  return s.replace('  reload().then(() => {','  reload().then(() => { window.__qaReady=true;');
}
function serve(){return http.createServer((req,res)=>{
  const url=new URL(req.url,'http://localhost');let f=path.resolve(site,'.'+decodeURIComponent(url.pathname));
  if(!f.startsWith(path.resolve(site)+path.sep)){res.statusCode=403;return res.end();}
  if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');
  if(!fs.existsSync(f)){res.statusCode=404;return res.end();}
  let raw=fs.readFileSync(f);if(f.endsWith('renderTei.js'))raw=Buffer.from(instrument(raw.toString()));
  res.setHeader('Content-Type',f.endsWith('.xml')?'application/xml':f.endsWith('.json')?'application/json':f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':f.endsWith('.html')?'text/html':f.endsWith('.svg')?'image/svg+xml':f.endsWith('.png')?'image/png':f.endsWith('.jpg')?'image/jpeg':'application/octet-stream');res.end(raw);
});}
async function main(){
  const report={status:'PENDING',purpose:'PINNED_BASELINE_ONLY_NO_NEW_NIESE_CERTIFICATION',base:'65b3256fe202a06e33a59aa2d1dcbd7107358271',started:new Date().toISOString(),books:{},browserErrors:[]};
  const server=serve();await new Promise((r,j)=>{server.once('error',j);server.listen(8916,'127.0.0.1',r);});
  const origin='http://127.0.0.1:8916';report.origin=origin;
  const context=await chromium.launchPersistentContext(path.join(runtime,'browser-baseline-16-17'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const page=await context.newPage();page.on('pageerror',e=>report.browserErrors.push(String(e)));
  async function open(query){await page.goto(`${origin}/antiquities/?${query}`,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});}
  try{
    for(const b of [16,17]){
      await open(`book=${b}`);
      for(const language of ['english','greek'])await page.check(`#${language}-pane-select`);
      const inventory=await page.evaluate(()=>{
        const q=window.__qa,d=q.getData(),t=q.traditionalRows('chapter'),s=q.traditionalRows('subchapter'),m=q.bambergRows();
        const legacy=[...d.Latin.querySelectorAll('tei-milestone[unit="chapter"][n]')].map(x=>Number(x.getAttribute('n'))).filter(n=>n>0);
        return {chapters:t.map(x=>({id:x.id,chapter:x.chapter})),subchapters:s.map(x=>({id:x.id,chapter:x.chapter,subchapter:x.subchapter})),bamberg:m.map(x=>({id:x.id,label:x.display})),units:[...document.querySelector('#section-selector').options].filter(o=>o.value).map(o=>o.value),legacy:[...new Set(legacy)],NieseDisabled:document.querySelector('#niese-level').disabled};
      });
      if(!inventory.NieseDisabled)throw Error('Baseline unexpectedly has new Niese registration '+b);
      const queries=[{scheme:'book',query:`book=${b}`},...inventory.chapters.map(x=>({...x,scheme:'chapter',query:`book=${b}&chapter=${x.chapter}`})),...inventory.subchapters.map(x=>({...x,scheme:'subchapter',query:`book=${b}&chapter=${x.chapter}&subchapter=${x.subchapter}`})),...inventory.bamberg.map(x=>({...x,scheme:'bamberg',query:`book=${b}&bamberg=${x.id}`})),...inventory.units.map(x=>({scheme:'alignment-unit',unit:x,query:`book=${b}&unit=${x}`})),{scheme:'contents',query:`book=${b}&view=contents`}];
      const views=[];
      for(const item of queries){
        await open(item.query);
        const out=await page.evaluate(()=>{
          const q=window.__qa,panes={};
          for(const language of ['latin','greek','english']){
            const pane=document.querySelector('#'+language);const copy=pane.cloneNode(true);copy.querySelectorAll('h3,.niese-context-note,.niese-correspondence-note').forEach(x=>x.remove());
            const text=copy.textContent.replace(/\s+/g,' ').trim();
            panes[language]={html:copy.innerHTML,text,characters:text.length,ids:[...copy.querySelectorAll('[id]')].map(n=>n.id)};
          }
          const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);
          return {state:q.getState(),panes,duplicateIDs:ids.filter((id,i)=>ids.indexOf(id)!==i)};
        });
        const expectedLevel={'book':'book-level','chapter':'chapter-level','subchapter':'subchapter-level','bamberg':'bamberg-level','alignment-unit':'section-level'}[item.scheme];
        if(expectedLevel&&out.state.viewingLevel!==expectedLevel)throw Error('Wrong baseline level '+JSON.stringify({item,state:out.state}));
        if(item.scheme==='chapter'&&Number(out.state.chapterNum)!==Number(item.chapter))throw Error('Wrong chapter');
        if(item.scheme==='subchapter'&&(Number(out.state.chapterNum)!==Number(item.chapter)||Number(out.state.subchapterNum)!==Number(item.subchapter)))throw Error('Wrong subchapter');
        if(item.scheme==='bamberg'&&out.state.bambergId!==item.id)throw Error('Wrong Bamberg identity');
        if(item.scheme==='alignment-unit'&&String(out.state.sectionNum)!==String(item.unit))throw Error('Wrong alignment identity');
        if(!Object.values(out.panes).some(x=>x.characters>0))throw Error('Empty baseline selection '+JSON.stringify(item));
        for(const value of Object.values(out.panes)){value.html_sha256=sha(value.html);value.text_sha256=sha(value.text);}
        views.push({...item,...out});
      }
      await open(`book=${b}`);
      const legacy=await page.evaluate(numbers=>{
        const q=window.__qa,d=q.getData();return numbers.map(n=>({number:n,languages:Object.fromEntries(['Latin','Greek','English'].map(lang=>{const v=q.milestoneChapterView(lang,d[lang],n,false);return [lang,v?{html:v.outerHTML,text:v.textContent}:null];}))}));
      },inventory.legacy);
      if(legacy.some(x=>Object.values(x.languages).some(v=>!v||!v.text.trim())))throw Error('Empty legacy chapter '+b);
      await page.screenshot({path:path.join(packet,'evidence',`baseline-Book${b}.png`),fullPage:true});
      report.books[b]={inventory,views,legacy_chapter_ranges:legacy,all_view_count:views.length,status:'BASELINE_CAPTURE_PASS'};
      fs.writeFileSync(path.join(packet,'BASELINE_READER_PROGRESS.json'),JSON.stringify({book:b,views:views.length,inventory:{chapters:inventory.chapters.length,subchapters:inventory.subchapters.length,bamberg:inventory.bamberg.length,legacy:inventory.legacy.length,alignment:inventory.units.length}},null,2)+'\n');
      console.log('Baseline',b,views.length,'views; legacy',legacy.length);
    }
    if(report.browserErrors.length)throw Error('Baseline script errors');
    report.built_source_checks=['assets/js/renderTei.js','assets/css/tei.css','assets/xml/antiquities/structure.xml',...['Latin','Greek','English'].flatMap(l=>[16,17].map(b=>`assets/xml/antiquities/${l}/book-${b}.xml`))].map(f=>{const raw=fs.readFileSync(path.join(site,f));if(sha(raw)!==sha(fs.readFileSync(path.join(root,f))))throw Error('Built source differs '+f);return {path:f,sha256:sha(raw)};});
    report.status='PASS_BASELINE_ONLY';
  }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
  finally{report.finished=new Date().toISOString();fs.writeFileSync(path.join(packet,'BASELINE_READER_CAPTURE.json'),JSON.stringify(report,null,2)+'\n');await context.close();await new Promise(r=>server.close(r));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
