const {chromium,path,runtime,packet,fs,candidate,baseline,serve,listen,open}=require('./qa-common.cjs');
(async()=>{
 const servers=[serve(baseline),serve(candidate)],origins=[];for(const s of servers)origins.push(await listen(s));
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-candidate-new-books'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const page=await context.newPage(),observations=[];
  for(let which=0;which<2;which++){
   await open(page,origins[which],`book=16${which?'&niese=351':''}`);
   for(const theme of ['light','dark']){
    await page.evaluate(t=>setTheme(t),theme);await page.waitForFunction(()=>!document.documentElement.classList.contains('transition'));
    await page.waitForTimeout(800);
    observations.push({which,theme,style:await page.evaluate(()=>({body:getComputedStyle(document.body).backgroundColor,foreground:getComputedStyle(document.body).color,
     root:getComputedStyle(document.documentElement).backgroundColor,global:getComputedStyle(document.documentElement).getPropertyValue('--global-bg-color'),
     paper:getComputedStyle(document.documentElement).getPropertyValue('--lj-brand-paper'),pane:getComputedStyle(document.querySelector('#latin')).backgroundColor,
     sheets:[...document.styleSheets].map(s=>s.href)}))});
   }
  }
  fs.writeFileSync(path.join(packet,'THEME_BASELINE_DIAGNOSTIC.json'),JSON.stringify(observations,null,2)+'\n');console.log(JSON.stringify(observations));
 }finally{await context.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
})().catch(e=>{console.error(e);process.exitCode=1;});
