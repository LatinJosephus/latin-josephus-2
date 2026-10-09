const fs = require('fs');
const path = require('path');
const http = require('http');
const cp = require('child_process');
const crypto = require('crypto');
const {chromium} = require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../..');
const base = 'a48021588e0840330388a6055a97bd0f7c2cf827';
const head = cp.execFileSync('git',['--no-optional-locks','show',`${base}:assets/js/renderTei.js`], {cwd:root, encoding:'utf8'});
const updated = fs.readFileSync(path.join(root,'assets/js/renderTei.js'),'utf8');
const include = fs.readFileSync(path.join(root,'_includes/display-settings.html'),'utf8');
const compiledCSS=fs.readFileSync('C:/Users/POLLAR~1/AppData/Local/Temp/LatinJosephus-Whiston-Niese-Combined-disposable-20261009/assets/css/main.css','utf8');
const palette=fs.readFileSync(path.join(root,'_sass/_branding.scss'),'utf8');
const readerCSS=fs.readFileSync(path.join(root,'_sass/_reader-ui.scss'),'utf8');
const annotations = fs.readFileSync(path.join(root,'_includes/annotations-bar.html'),'utf8');
const report = {traditional:{}, niese:{}, crossWork:[], ui:[], errors:[]};
function cleanHTML(node){if(!node)return null;node=node.cloneNode(true);node.querySelectorAll('tei-anchor[type="bamberg-boundary"]').forEach(a=>a.remove());return node.outerHTML;}
function instrument(source) {
 source=source.replace('    syncNavigationControls();','    syncNavigationControls(); window.__qaRenderedState = {...state};');
 const extra = source.includes('const loadTraditionalRegistry') ? ',traditionalRegistry:()=>traditionalRegistry, alignmentRegistry:()=>alignmentRangeRegistry, traditionalRangeView,traditionalPoint,traditionalRows' : '';
 const supplemental = (source.includes('const traditionalRangePoint') ? ',traditionalRangePoint' : '') + (source.includes('let bambergRegistry') ? ',bambergRows,bambergSelection,bambergRegistry:()=>bambergRegistry,boundaryRegistry:()=>boundaryRegistry' : '');
 source = source.replace('  bookTitle.innerText = activeWork.title;', `  ${cleanHTML.toString()}
  window.__qa = {cleanHTML, getState:()=>({...state}), getData:()=>fullData, view:()=>viewData, reload, setState, setChapterSelectOptions, setSectionSelectOptions, setNieseSelectOptions, currentIdBase, applyNavigationFromUrl, syncUrlFromState, selectView${extra}${supplemental}, assign:patch=>Object.assign(state,patch)};\n  bookTitle.innerText = activeWork.title;`);
 source = source.replaceAll('setState(() => {', 'window.__qaPending = setState(() => {');
 return source.replace('  reload().then(() => {','  reload().then(() => {\n    window.__qaReady = true;');
}
const site="C:/Users/POLLAR~1/AppData/Local/Temp/LatinJosephus-Whiston-Niese-Combined-disposable-20261009";
const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://local');let f=path.resolve(site,'.'+decodeURIComponent(u.pathname));if(!f.startsWith(path.resolve(site)+path.sep)){res.statusCode=403;return res.end();}if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');if(!fs.existsSync(f)){res.statusCode=404;return res.end();}let raw=fs.readFileSync(f);if(f.endsWith('renderTei.js'))raw=Buffer.from(instrument(new URL(req.headers.referer||'http://local').searchParams.has('baseline')?head:updated));res.setHeader('Content-Type',({'.xml':'application/xml','.json':'application/json','.html':'text/html','.js':'text/javascript','.css':'text/css','.otf':'font/otf','.svg':'image/svg+xml'})[path.extname(f)]||'application/octet-stream');res.end(raw);});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const origin=`http://127.0.0.1:${server.address().port}`;
 const browser=await chromium.launch({headless:true, executablePath:"C:/Program Files/Google/Chrome/Application/chrome.exe"});
 const context=await browser.newContext(); const page=await context.newPage();
 page.on('pageerror',e=>(report.errors.push(String(e)),console.error('PAGEERROR',String(e))));
 async function open(route){await page.goto(origin+route);await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});await page.evaluate(()=>document.querySelector('#collapse-settings').classList.add('show'));}
 const checks=[],themes=[];
 async function settled(){await page.evaluate(()=>window.__qaPending);}
 function contrast(a,b){function lum(s){return s.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0)}const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
 for(const work of ['deh','bellum-judaicum','contra-apionem']){
  for(const source of (work==='bellum-judaicum'?['whiston','lodge1602']:[''])){
   const snapshots=[];for(const base of [true,false]){
    await open(`/${work}/?book=1&chapter=1${source?'&english='+source:''}${base?'&baseline=1':''}`);
    if(await page.locator('#bamberg-level,#bamberg-selector').count())throw Error('Bamberg UI leaks to another work');
    const chapters=await page.locator('#chapter-selector').evaluate(m=>[...m.options].filter(o=>o.value && o.value!=="contents").map(o=>o.value));if(chapters.length<2)throw Error('Missing protected Chapter controls');
    await page.selectOption('#chapter-selector',chapters[1]);await settled();
    const destination=await page.evaluate(()=>{const u=new URL(location.href);u.searchParams.delete('baseline');return {chapter:window.__qa.getState().chapterNum,url:u.search}});
    await page.reload();await page.waitForFunction(()=>window.__qaReady);await page.evaluate(()=>document.querySelector('#collapse-settings').classList.add('show'));if(await page.evaluate(()=>window.__qa.getState().chapterNum)!==chapters[1])throw Error('Protected reload identity');
    await page.selectOption('#chapter-selector',chapters[0]);await settled();await page.goBack();await page.waitForFunction(c=>window.__qaRenderedState?.chapterNum===c,chapters[1]);await page.goForward();await page.waitForFunction(c=>window.__qaRenderedState?.chapterNum===c,chapters[0]);
    await page.locator('#chapter-selector').focus();await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');await page.waitForTimeout(100);await settled();
    const keyboard=await page.evaluate(()=>({selected:document.querySelector('#chapter-selector').value,state:window.__qa.getState().chapterNum}));if(keyboard.selected!==String(keyboard.state??''))throw Error('Protected keyboard navigation '+work+' '+JSON.stringify(keyboard));
    await page.locator('#english-pane-select').uncheck({force:true});await page.locator('#english-pane-select').check({force:true});
    const capture=await page.evaluate(()=>({state:((s)=>{delete s.bambergId;return s})(window.__qa.getState()),views:Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>[l,v?.outerHTML.replaceAll('&amp;baseline=1','')])),label:document.querySelector('label[for="section-level"]').textContent}));
    for(const theme of ['light','dark']){await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);if(await page.locator('#chapter-selector').isDisabled())throw Error('Protected theme disables control');}
    snapshots.push({destination,keyboard,capture});
   }
   if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1])){fs.writeFileSync(path.join(__dirname,'INTERACTION_DIFFERENCE.json'),JSON.stringify({work,source,snapshots},null,2));throw Error('Protected interaction/DOM semantic regression '+work+' '+source);}
   checks.push({work,source:source||'default',URL_reload:'PASS',back_forward:'PASS',keyboard:'PASS',pane_switch:'PASS',light_dark_controls:'PASS',differential_DOM:'PASS',result:'PASS'});
  }
 }
 await open('/antiquities/?book=13&bamberg=B78-table1-row069&extra=keep#retained');
 for(const theme of ['light','dark']){
  await page.evaluate(t=>{document.documentElement.dataset.theme=t;document.querySelector('#collapse-settings').classList.add('show');},theme);
  const styles=await page.evaluate(()=>{const objects={};for(const id of ['bamberg-selector','bamberg-previous','bamberg-next']){const n=document.getElementById(id),s=getComputedStyle(n);objects[id]={color:s.color,background:s.backgroundColor,visible:n.getBoundingClientRect().height>0}}return objects;});
  for(const [id,s]of Object.entries(styles)){if(!s.visible)throw Error('Invisible Bamberg theme control '+id);const ratio=contrast(s.color,s.background);if(ratio<4.5)throw Error('Low contrast '+theme+' '+id+' '+ratio);s.contrast=Number(ratio.toFixed(2));}
  await page.locator('#display-settings').screenshot({path:path.join(__dirname,`screenshots/BAMBERG_CONTROLS_${theme}.png`)});themes.push({theme,styles,result:'PASS'});
 }
 await open('/bellum-judaicum/?book=1&english=lodge1602&lodgeNotes=0');
 if(!await page.locator('#english tei-note[place="margin"]').count())throw Error('Missing Lodge margin notes test data');
 if(!await page.locator('#english').evaluate(n=>n.classList.contains('lodge-notes-hidden')))throw Error('Lodge notes URL');
 await page.check('#lodge-notes-visible');if(new URL(page.url()).searchParams.has('lodgeNotes'))throw Error('Lodge notes restore URL');
 await page.selectOption('#chapter-selector','contents');await settled();await page.uncheck('#lodge-notes-visible');
 if(new URL(page.url()).searchParams.get('lodgeNotes')!=='0')throw Error('Contents notes preference');
 await page.reload();await page.waitForFunction(()=>window.__qaReady);await page.evaluate(()=>document.querySelector('#collapse-settings').classList.add('show'));
 if(await page.locator('#lodge-notes-visible').isChecked())throw Error('Contents notes reload preference');
 await page.check('#lodge-notes-visible');if(new URL(page.url()).searchParams.has('lodgeNotes'))throw Error('Contents restored notes URL');
 await page.selectOption('#english-source-selector','whiston');await settled();await page.selectOption('#english-source-selector','lodge1602');await settled();
 if(await page.locator('#chapter-selector').inputValue()!=='contents')throw Error('Source switch lost contents view');
 await page.selectOption('#chapter-selector','1');await settled();if(new URL(page.url()).searchParams.has('view'))throw Error('Lodge contents exit');
 checks.push({work:'bellum-judaicum',source:'lodge1602',notes_toggle_and_contents_preference:'PASS',source_switch:'PASS',result:'PASS'});
 if(report.errors.length)throw Error(JSON.stringify(report.errors));
 fs.writeFileSync(path.join(__dirname,'PROTECTED_INTERACTION_QA.json'),JSON.stringify({checks,themes,result:'PASS',test_environment:'Actual fresh combined Jekyll site, renderer, CETEI, source XML and selectors; no historical build reuse'},null,2));
 await browser.close();server.close();console.log('INTERACTION_QA_PASS',checks.length,'protected configurations and two themes');
})().catch(e=>{console.error(e);fs.writeFileSync(path.join(__dirname,'INTERACTION_FAILURE.json'),JSON.stringify({error:String(e)},null,2));server.close();process.exit(1)});
