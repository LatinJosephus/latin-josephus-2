const {spawn}=require('child_process'),fs=require('fs'),path=require('path');
const q=require('./browser_qa.cjs');
async function main(){
 const child=spawn(process.execPath,['bin/deh-parallels-qa.mjs','0'],{cwd:q.root,stdio:['ignore','pipe','pipe']});
 let log='';child.stdout.on('data',b=>log+=b);child.stderr.on('data',b=>log+=b);
 const origin=await new Promise((resolve,reject)=>{
  const check=()=>{const match=log.match(/http:\/\/127\.0\.0\.1:\d+\//);if(match)resolve(match[0]);else if(child.exitCode!==null)reject(Error(log));else setTimeout(check,100);};check();
 });
 const browser=await q.chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 try{
  await page.goto(origin);await page.locator('#run').click();
  await page.waitForFunction(()=>document.querySelector('#qa-result').dataset.complete==='true',null,{timeout:120000});
  const result=JSON.parse(await page.locator('#qa-result').textContent());
  q.assert(result.passed&&result.componentChecks.length===2115&&result.sectionOccurrences===8193,'Native DEH extraction harness failed',result);
  q.assert(!errors.length,'Native DEH browser errors');
  fs.writeFileSync(path.join(q.pack,'DEH_LAUNCHER_QA.json'),JSON.stringify({status:'PASS',launcher:'bin/deh-parallels-qa.mjs',guard_log:log,errors,result},null,2)+'\n');
  console.log('Native DEH launcher and actual displayed extraction PASS, 2115 components, 8193 section occurrences');
 }finally{await browser.close();child.kill();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
