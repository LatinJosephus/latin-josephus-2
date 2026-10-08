const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),canonical='C:/Users/Pollard_R/Git/LatinJosephus-v2-development';
const include=fs.readFileSync(path.join(root,'_includes/display-settings.html'),'utf8'),annotations=fs.readFileSync(path.join(root,'_includes/annotations-bar.html'),'utf8');
const renderer=fs.readFileSync(path.join(root,'assets/js/renderTei.js'),'utf8').replace('  bookTitle.innerText = activeWork.title;','  window.__typographyState=()=>({...state});\n  bookTitle.innerText = activeWork.title;').replace('  reload().then(() => {','  reload().then(() => {\n    window.__typographyReady=true;');
const mainCSS=fs.readFileSync(path.join(canonical,'_site/assets/css/main.css'),'utf8');
const snapshots=[],ordinary=[],errors=[],network=[],failures=[];const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const server=http.createServer((req,res)=>{
 const u=new URL(req.url,'http://localhost');
 if(['/antiquities/','/bellum-judaicum/'].includes(u.pathname)){
  const ant=u.pathname==='/antiquities/';const ui=include.replace(/{% if page.permalink == "\/antiquities\/" %}([\s\S]*?){% endif %}/g,(_,b)=>{const[a,c='']=b.split('{% else %}');return ant?a:c;});
  const html=`<!doctype html><html data-theme="${u.searchParams.get('theme')||'light'}"><head><meta charset="utf-8"><style>.hidden,[hidden]{display:none!important}</style><link rel="stylesheet" href="/assets/css/main.css"><link rel="stylesheet" href="/assets/css/tei.css${u.searchParams.get('css')==='before'?'?baseline=1':''}"><link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/3.6.0/mdb.min.css"></head><body><main>${ui}<div id="pane-container">${['Latin','English','Greek','French','Italian'].map(l=>`<div id="${l.toLowerCase()}" class="pane"><h3>${l}</h3></div>`).join('')}${annotations}</div></main><script>HTMLCollection.prototype.forEach=Array.prototype.forEach;</script><script src="/assets/js/CETEI.js"></script><script src="/__renderer.js"></script></body></html>`;
  res.setHeader('Content-Type','text/html');res.end(html);return;
 }
 if(u.pathname==='/__renderer.js'){res.setHeader('Content-Type','text/javascript');res.end(renderer);return;}
 if(u.pathname==='/assets/css/main.css'){res.setHeader('Content-Type','text/css');res.end(mainCSS);return;}
 if(u.pathname==='/assets/css/tei.css'&&u.searchParams.has('baseline')){res.setHeader('Content-Type','text/css');res.end(fs.readFileSync(path.join(__dirname,'BEFORE_tei.css')));return;}
 const file=path.resolve(root,'.'+u.pathname);if(!file.startsWith(root+path.sep)||!fs.existsSync(file)){res.statusCode=404;res.end();return;}
 const ext=path.extname(file);res.setHeader('Content-Type',ext==='.xml'?'application/xml':ext==='.js'?'text/javascript':ext==='.css'?'text/css':ext==='.otf'?'font/otf':ext==='.woff2'?'font/woff2':'application/octet-stream');res.end(fs.readFileSync(file));
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin=`http://127.0.0.1:${server.address().port}`;
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1600,height:1050},deviceScaleFactor:1});
 page.on('pageerror',e=>errors.push(String(e)));page.on('requestfailed',r=>failures.push({url:r.url(),failure:r.failure()}));
 page.on('response',r=>{if(/fonts|mdb\.min\.css/.test(r.url()))network.push({url:r.url().replace(origin,''),status:r.status()});});
 const session=await page.context().newCDPSession(page);await session.send('DOM.enable');await session.send('CSS.enable');
 async function open(route){await page.goto(origin+route,{waitUntil:'load',timeout:60000});await page.waitForFunction(()=>window.__typographyReady,{},{timeout:60000});await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(150);}
 async function platform(selector){const doc=await session.send('DOM.getDocument');const {nodeId}=await session.send('DOM.querySelector',{nodeId:doc.root.nodeId,selector});return nodeId?(await session.send('CSS.getPlatformFontsForNode',{nodeId})).fonts:[];}
 const cases=[{key:'antiquities-III',route:'/antiquities/?book=3',languages:['Latin']},{key:'antiquities-V',route:'/antiquities/?book=5',languages:['Latin','Greek']},{key:'antiquities-XIV',route:'/antiquities/?book=14',languages:['Latin','Greek']},{key:'bellum-Lodge-I',route:'/bellum-judaicum/?book=1&english=lodge1602',languages:['English']}];
 const keys=['fontFamily','fontStyle','fontWeight','fontSize','lineHeight','letterSpacing','wordSpacing','textIndent','textAlign','marginTop','marginBottom','marginLeft','paddingLeft','color','backgroundColor'];
 for(const theme of ['light','dark'])for(const version of ['before','after'])for(const c of cases){
  await open(c.route+`&view=contents&theme=${theme}&css=${version}`);
  const result=await page.evaluate(({languages,keys})=>{
   const out={};for(const language of languages){
    const wrapper=document.querySelector('#'+language.toLowerCase()+' .source-contents');if(!wrapper)throw Error('No contents wrapper');
    const heading=wrapper.querySelector('tei-head,tei-seg[type="tcp-head"]')||wrapper.querySelector('tei-p')||wrapper.querySelector('tei-div2,tei-div');const entry=wrapper.querySelector('tei-item,tei-seg[type="tcp-item"]')||[...wrapper.querySelectorAll('tei-p')].find(n=>n!==heading)||heading;
    if(!entry||!heading)throw Error('Missing representative entry/heading '+language);
    const samples={heading,entry,numeral:wrapper.querySelector('tei-label,tei-num')||entry,italic:wrapper.querySelector('tei-supplied,tei-hi[rend="italic"]')};
    const data={};for(const [role,n]of Object.entries(samples))if(n){data[role]={tag:n.localName,text:n.textContent.slice(0,160),styles:Object.fromEntries(keys.map(k=>[k,getComputedStyle(n)[k]])),rect:{width:n.getBoundingClientRect().width,height:n.getBoundingClientRect().height},pseudoBefore:getComputedStyle(n,'::before').content,pseudoAfter:getComputedStyle(n,'::after').content};n.setAttribute('data-typography-'+role,'true');}else data[role]=null;
    const italics=[...wrapper.querySelectorAll('tei-supplied,tei-hi[rend="italic"],i,em')].map(n=>({text:n.textContent,fontFamily:getComputedStyle(n).fontFamily,fontStyle:getComputedStyle(n).fontStyle,source:n.getAttribute('source'),reason:n.getAttribute('reason')}));
    if(italics.some(n=>n.fontStyle!=='italic'))throw Error('Lost genuine italic');
    let surface=wrapper;while(surface.parentElement&&getComputedStyle(surface).backgroundColor==='rgba(0, 0, 0, 0)')surface=surface.parentElement;
    out[language]={samples:data,italicSpans:italics,background:getComputedStyle(surface).backgroundColor,headingAndEntriesText:wrapper.textContent,overflow:wrapper.scrollWidth>wrapper.clientWidth+1};
   }
   return {languages:out,bodyFont:getComputedStyle(document.body).fontFamily,readerVariable:getComputedStyle(document.documentElement).getPropertyValue('--lj-font-text').trim(),controlsFont:getComputedStyle(document.querySelector('#chapter-selector')).fontFamily,documentOverflow:document.documentElement.scrollWidth>innerWidth+1,fontLoaded:document.fonts.check('18px "LJ Coelacanth"')};
  },{languages:c.languages,keys});
  if(result.documentOverflow||Object.values(result.languages).some(l=>l.overflow))throw Error('Contents layout overflow '+c.key);
  if(!result.fontLoaded)throw Error('Coelacanth did not load');
  for(const language of c.languages)for(const role of ['heading','entry','numeral','italic']){const sample=result.languages[language].samples[role];if(sample)sample.platformFonts=await platform(`#${language.toLowerCase()} [data-typography-${role}]`);}
  if(version==='after')for(const l of Object.values(result.languages))for(const sample of Object.values(l.samples))if(sample&&!sample.styles.fontFamily.includes('LJ Coelacanth'))throw Error('Not established reading family');
  // Show actual pane content, including the III Blatt supplements / XIV supplied labels.
  const focus=c.key==='antiquities-XIV'?'#latin .source-contents tei-item:nth-of-type(5)':`#${c.languages[0].toLowerCase()} .source-contents`;
  await page.evaluate(()=>window.scrollTo(0,0));
  const screenshot=`${c.key}_${theme}_${version}.png`;await page.screenshot({path:path.join(__dirname,screenshot)});
  snapshots.push({case:c.key,route:c.route,theme,version,screenshot,...result});console.log(c.key,theme,version,result.bodyFont);
 }
 for(const theme of ['light','dark'])for(const c of cases)for(const view of ['book','chapter']){
  const compare=[];
  for(const version of ['before','after']){
   await open(c.route+`&${view==='chapter'?'chapter=1':'level=book'}&theme=${theme}&css=${version}`);
   const s=await page.evaluate(({languages,keys})=>({languages:Object.fromEntries(languages.map(l=>{const n=document.querySelector('#'+l.toLowerCase()+' tei-p');if(!n)throw Error('Missing ordinary reading paragraph');return[l,{text:n.textContent,styles:Object.fromEntries(keys.map(k=>[k,getComputedStyle(n)[k]])),html:document.querySelector('#'+l.toLowerCase()).innerHTML}]})),controlsFont:getComputedStyle(document.querySelector('#chapter-selector')).fontFamily,contents:document.querySelectorAll('.source-contents').length}),{languages:c.languages,keys});
   if(s.contents)throw Error('Unexpected contents in ordinary view');
   for(const language of c.languages)s.languages[language].platformFonts=await platform('#'+language.toLowerCase()+' tei-p');
   s.panesScreenshotSHA256=hash(await page.screenshot({clip:{x:0,y:Math.ceil((await page.locator('#pane-container').boundingBox()).y),width:1600,height:700}}));compare.push(s);
  }
  const semantic=x=>{const{panesScreenshotSHA256,...stable}=x;return stable;};if(JSON.stringify(semantic(compare[0]))!==JSON.stringify(semantic(compare[1]))){fs.writeFileSync(path.join(__dirname,'development-diagnostics','ORDINARY_DIFFERENCE.json'),JSON.stringify({case:c.key,view,theme,compare},null,2));throw Error('Ordinary narrative or navigation changed '+c.key+' '+view+' '+theme);}
  ordinary.push({case:c.key,theme,view,computed:compare[1],screenshotHashes:compare.map(x=>x.panesScreenshotSHA256),screenshotHashEqual:compare[0].panesScreenshotSHA256===compare[1].panesScreenshotSHA256,result:'PASS'});
 }
 // Compare all preserved presentation properties, allowing only the font family/metrics to change in TOC fragments.
 for(const after of snapshots.filter(x=>x.version==='after')){
  const before=snapshots.find(x=>x.case===after.case&&x.theme===after.theme&&x.version==='before');
  if(before.controlsFont!==after.controlsFont)throw Error('Navigation font changed');
  for(const [language,a]of Object.entries(after.languages)){
   const b=before.languages[language];if(a.headingAndEntriesText!==b.headingAndEntriesText)throw Error('Source text changed');
   for(const [role,s]of Object.entries(a.samples))if(s){const old=b.samples[role];for(const k of keys.filter(k=>k!=='fontFamily'))if(old.styles[k]!==s.styles[k])throw Error('Non-font property changed '+k);}
   const normal=ordinary.find(x=>x.case===after.case&&x.theme===after.theme&&x.view==='chapter').computed.languages[language];
   if(a.samples.entry.styles.fontFamily!==normal.styles.fontFamily)throw Error('TOC stack differs from narrative '+language);
   if(JSON.stringify(a.italicSpans.map(x=>x.fontStyle))!==JSON.stringify(b.italicSpans.map(x=>x.fontStyle)))throw Error('Italic state changed');
  }
 }
 if(errors.length)throw Error(errors.join('\n'));
 if(!network.some(x=>x.url.includes('mdb-ui-kit/3.6.0/mdb.min.css')&&x.status===200))throw Error('Actual existing MDB CSS not loaded; baseline would be invalid');
 const sourceBodies=snapshots.filter(x=>x.version==='before').map(x=>x.languages[Object.keys(x.languages)[0]].samples.entry.styles.fontFamily);if(!sourceBodies.some(s=>!s.includes('LJ Coelacanth')))throw Error('Reported sans-serif defect was not reproduced');
 fs.writeFileSync(path.join(__dirname,'BROWSER_QA.json'),JSON.stringify({result:'PASS',contents_scenarios:snapshots.length,ordinary_unchanged_comparisons:ordinary.length,snapshots,ordinary,network,requestFailures:failures,pageErrors:errors,test_environment:'Actual renderer, source XML, existing canonical compiled main CSS, existing book-layout MDB/Roboto URLs, and unchanged local font files. Only tei.css differs.'},null,2));
 await browser.close();server.close();console.log('TYPOGRAPHY_QA_PASS',snapshots.length,'TOC scenarios,',ordinary.length,'ordinary-view comparisons');
})().catch(e=>{console.error(e);fs.writeFileSync(path.join(__dirname,'BROWSER_FAILURE.json'),JSON.stringify({error:String(e),snapshots,ordinary,errors,network,failures},null,2));server.close();process.exit(1);});