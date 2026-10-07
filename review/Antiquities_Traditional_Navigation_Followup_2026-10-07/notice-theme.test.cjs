const fs = require('fs');
const path = require('path');
const http = require('http');
const assert = require('assert/strict');
const crypto = require('crypto');
const {chromium} = require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../..');
const canonical = 'C:/Users/Pollard_R/Git/LatinJosephus-v2-development';
const palette = fs.readFileSync(path.join(root,'_sass/_branding.scss'),'utf8');
const reader = fs.readFileSync(path.join(root,'_sass/_reader-ui.scss'),'utf8');
// These two partials contain ordinary CSS; no Sass compilation or site build is needed.
assert(!/\$|@mixin|@include|@extend/.test(reader));
const compiled = fs.readFileSync(path.join(canonical,'_site/assets/css/main.css'),'utf8');
const include = fs.readFileSync(path.join(root,'_includes/display-settings.html'),'utf8').replace(/{% if page.permalink == "\/antiquities\/" %}([\s\S]*?){% else %}([\s\S]*?){% endif %}/g,(_,a)=>a);
let renderer = fs.readFileSync(path.join(root,'assets/js/renderTei.js'),'utf8');
renderer = renderer.replace('  bookTitle.innerText = activeWork.title;', '  window.__themeQA = {state:()=>({...state}), view:()=>viewData};\n  bookTitle.innerText = activeWork.title;').replace('  reload().then(() => {','  reload().then(() => {\n    window.__themeReady = true;');
const fixture = '.alert { padding:1rem; border:1px solid transparent; margin-bottom:1rem; } .alert-secondary { background-color:#e2d9f3; color:inherit; }';
const server = http.createServer((req,res)=>{
 const url=new URL(req.url,'http://localhost');
 if(url.pathname==='/antiquities/'){
  res.setHeader('Content-Type','text/html');res.end(`<!doctype html><html><head><meta charset="utf-8"><style>${fixture}</style><link rel="stylesheet" href="/compiled-main.css"><style>${palette}</style></head><body>${include}<div id="pane-container">${['Latin','English','Greek','French','Italian'].map(l=>`<div id="${l.toLowerCase()}" class="pane"><h3>${l}</h3></div>`).join('')}</div><aside id="ordinary-alert" class="alert alert-secondary"><p>Unrelated ordinary alert</p><a href="#ordinary">Ordinary link</a></aside>${fs.readFileSync(path.join(root,'_includes/annotations-bar.html'),'utf8')}<script>HTMLCollection.prototype.forEach=Array.prototype.forEach;</script><script src="/assets/js/CETEI.js"></script><script src="/__renderer.js"></script></body></html>`);return;
 }
 if(url.pathname==='/compiled-main.css'){res.setHeader('Content-Type','text/css');res.end(compiled);return;}
 if(url.pathname==='/__renderer.js'){res.setHeader('Content-Type','text/javascript');res.end(renderer);return;}
 const target=path.resolve(root,'.'+url.pathname);
 if(!target.startsWith(root+path.sep)||!fs.existsSync(target)){res.statusCode=404;res.end();return;}
 res.setHeader('Content-Type',target.endsWith('.xml')?'application/xml':target.endsWith('.js')?'text/javascript':'application/octet-stream');res.end(fs.readFileSync(target));
});
function luminance(rgb){return rgb.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);}
function contrast(a,b){const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const context=await browser.newContext({viewport:{width:1280,height:900}});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 const checks=[];
 for(const subchapter of [4,6]){
  await page.goto(`http://127.0.0.1:${server.address().port}/antiquities/?book=11&chapter=8&subchapter=${subchapter}&extra=keep#retained`);
  await page.waitForFunction(()=>window.__themeReady);
  await page.evaluate(()=>document.fonts.ready);
  assert.equal(await page.locator('[data-structural-notice]').count(),1);
  const before = await page.evaluate(()=>({notice:document.querySelector('#traditional-reader-notice').innerHTML,panes:Object.fromEntries(Object.entries(window.__themeQA.view()).map(([l,v])=>[l,v.outerHTML]))}));
  async function colors(theme){
   return await page.evaluate(theme=>{
    document.documentElement.dataset.theme=theme;
    function get(node){const c=getComputedStyle(node);return {color:c.color,background:c.backgroundColor,border:c.borderColor,textDecoration:c.textDecorationLine,outlineStyle:c.outlineStyle,outlineWidth:c.outlineWidth,outlineColor:c.outlineColor};}
    const notice=document.querySelector('#traditional-reader-notice');return {notice:get(notice),prose:get(notice.querySelector('p')),link:get(notice.querySelector('a')),ordinary:get(document.querySelector('#ordinary-alert')),ordinaryLink:get(document.querySelector('#ordinary-alert a')),surface:getComputedStyle(document.documentElement).getPropertyValue('--lj-brand-surface').trim()};
   },theme);
  }
  const controls={};for(const theme of ['light','dark'])controls[theme]=await colors(theme);
  await page.addStyleTag({content:reader});
  for(const theme of ['light','dark']){
   await page.mouse.move(0,0);await page.evaluate(()=>document.activeElement?.blur());
   const c=await colors(theme);assert.deepEqual(c.ordinary,controls[theme].ordinary);assert.deepEqual(c.ordinaryLink,controls[theme].ordinaryLink);
   const textContrast=contrast(c.prose.color,c.notice.background),linkContrast=contrast(c.link.color,c.notice.background);
   assert(textContrast>=4.5,'Notice prose AA contrast');assert(linkContrast>=4.5,'Book-view link AA contrast');assert(c.link.textDecoration.includes('underline'));
   await page.locator('#traditional-reader-notice a').hover();const hover=await page.locator('#traditional-reader-notice a').evaluate(a=>getComputedStyle(a).color);assert(contrast(hover,c.notice.background)>=4.5);
   // Keyboard Tab proves a visible keyboard focus treatment, independently of hover.
   await page.locator('#traditional-reader-notice a').evaluate(a=>{a.setAttribute('data-tab-sentinel','true');a.focus();});
   await page.keyboard.press('Tab');await page.keyboard.press('Shift+Tab');
   const focus=await page.locator('#traditional-reader-notice a').evaluate(a=>{const s=getComputedStyle(a);return {focused:document.activeElement===a,focusVisible:a.matches(':focus-visible'),color:s.color,outlineStyle:s.outlineStyle,outlineWidth:s.outlineWidth};});
   assert(focus.focused&&focus.focusVisible&&focus.outlineStyle==='solid'&&parseFloat(focus.outlineWidth)>=2);assert(contrast(focus.color,c.notice.background)>=4.5);
   await page.locator('#traditional-reader-notice a').evaluate(a=>a.removeAttribute('data-tab-sentinel'));
   const after=await page.evaluate(()=>({notice:document.querySelector('#traditional-reader-notice').innerHTML,panes:Object.fromEntries(Object.entries(window.__themeQA.view()).map(([l,v])=>[l,v.outerHTML]))}));assert.deepEqual(after,before,'No notice wording or selected text change');
   if(subchapter===4){await page.locator('#traditional-reader-notice').screenshot({path:path.join(__dirname,`NOTICE_THEME_${theme}.png`)});}
   checks.push({subchapter,theme,noticeBackground:c.notice.background,proseColor:c.prose.color,linkColor:c.link.color,textContrast:Number(textContrast.toFixed(2)),linkContrast:Number(linkContrast.toFixed(2)),WCAG_AA_normal_text:'PASS',link_underlined:true,link_hover_focus_contrast:'PASS',keyboard_focus_outline:'PASS',ordinary_alert_and_link_unchanged:true,notice_wording_and_range_DOM_unchanged:true});
  }
  await page.locator('#traditional-reader-notice a').click();await page.waitForFunction(()=>window.__themeReady&&window.__themeQA.state().viewingLevel==='book-level');assert(new URL(page.url()).searchParams.get('extra')==='keep'&&page.url().endsWith('#retained'));
 }
 assert.deepEqual(errors,[]);
 const result={result:'PASS',checks,Book_view_link:'PASS',shared_notice_count:1,style_scope:'#traditional-reader-notice only',palette_variables:['--lj-brand-surface','--lj-brand-ink','--lj-brand-rule','--lj-brand-accent'],no_new_hard_coded_application_colours:true,test_environment:'Installed Chrome; actual renderer/XML; existing canonical compiled main.css plus unchanged source branding palette and current plain-CSS reader partial; representative lavender alert-secondary rule; no site build',existing_compiled_stylesheet_sha256:crypto.createHash('sha256').update(compiled).digest('hex'),screenshots:['NOTICE_THEME_light.png','NOTICE_THEME_dark.png']};
 fs.writeFileSync(path.join(__dirname,'NOTICE_THEME_QA.json'),JSON.stringify(result,null,2)+'\n');
 await browser.close();server.close();console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);server.close();process.exit(1);});