/* Isolated synthetic UI tests. Never reads a real editorial decision file. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const folder=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);fs.mkdirSync(out,{recursive:true});
const report={result:'RUNNING',real_editorial_decisions_accessed:false,checks_performed:0,remote_requests:[],errors:[]};
async function main(){
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_EXECUTABLE}),ctx=await browser.newContext({acceptDownloads:true,viewport:{width:1450,height:1050}}),page=await ctx.newPage();page.on('pageerror',e=>report.errors.push(String(e)));await ctx.route(/^https?:/,r=>{report.remote_requests.push(r.request().url());r.abort()});
 const url=pathToFileURL(path.join(folder,'Bamberg_Final_Independent_Verification.html')).href;
 const download=async(p,name)=>{const waiting=p.waitForEvent('download');await p.click('#download');const d=await waiting;const file=path.join(out,name);await d.saveAs(file);return file};
 try{
  await page.goto(url);await page.waitForFunction(()=>[...document.querySelectorAll('img[src]')].every(i=>i.complete&&i.naturalWidth>0));assert.equal(await page.locator('.card').count(),20);assert.equal(await page.locator('img').count(),61);assert.equal(await page.locator('#progress').textContent(),'0 / 20 answered');
  // The unused zoom image has no source until opened; all sixty actual assets decode.
  report.decoded_assets=await page.locator('img[src]').count();assert.equal(report.decoded_assets,60);
  await page.locator('[data-nav="FINAL34-B06"]').click();await page.waitForFunction(()=>!document.getElementById('FINAL34-B06').hidden);assert.match(await page.locator('#FINAL34-B06').textContent(),/Column B \(right\)/);
  await page.locator('#FINAL34-B06 .tight').click();assert(await page.locator('#zoom').isVisible());await page.click('#plus');assert.equal(await page.locator('#zoom-image').evaluate(e=>e.style.width),'150%');await page.click('#close');
  await page.locator('#FINAL34-B06 input[value="UNRESOLVED"]').check();const note='Synthetic QA only, "quoted"; first line\nSecond line: ā ē.';await page.locator('#FINAL34-B06 textarea').fill(note);await page.reload();assert.equal(await page.locator('#progress').textContent(),'1 / 20 answered');
  const file=await download(page,'synthetic_export.csv');const bytes=fs.readFileSync(file);assert(bytes.toString('utf8').includes('Synthetic QA only'));await page.screenshot({path:path.join(out,'sample_VI.png'),fullPage:false});
  const ctx2=await browser.newContext({acceptDownloads:true,viewport:{width:1450,height:1050}}),p2=await ctx2.newPage();await p2.goto(url);assert.equal(await p2.locator('#progress').textContent(),'0 / 20 answered');await p2.locator('#import').setInputFiles(file);await p2.waitForFunction(()=>document.getElementById('message').textContent.startsWith('Loaded twenty'));assert.equal(await p2.locator('#progress').textContent(),'1 / 20 answered');assert.equal(await p2.locator('#FINAL34-B06 textarea').inputValue(),note);const roundtrip=await download(p2,'synthetic_roundtrip.csv');assert.deepEqual(fs.readFileSync(roundtrip),bytes);
  const bad=path.join(out,'synthetic_invalid_identity.csv');fs.writeFileSync(bad,bytes.toString('utf8').replace('FINAL34-B01','FINAL34-INVALID'));await p2.locator('#import').setInputFiles(bad);await p2.waitForFunction(()=>document.getElementById('message').textContent.startsWith('Import rejected:'));assert.equal(await p2.locator('#progress').textContent(),'1 / 20 answered');
  await page.emulateMedia({media:'print'});assert.equal(await page.locator('.card:visible').count(),20);await page.emulateMedia({media:'screen'});
  const printable=await ctx2.newPage();await printable.goto(pathToFileURL(path.join(folder,'Printable_Final_Verification.html')).href);assert.equal(await printable.locator('.card:visible').count(),20);
  const fresh=await browser.newContext();const p3=await fresh.newPage();await p3.goto(url);assert.equal(await p3.locator('#progress').textContent(),'0 / 20 answered');await p3.screenshot({path:path.join(out,'first_passage.png'),fullPage:false});
  assert.equal(report.errors.length,0);assert.equal(report.remote_requests.length,0);Object.assign(report,{result:'PASS',cards:20,decoded_assets:60,file_URL_rendering:true,network_dependencies:0,CSV_export_import_exact_roundtrip:true,quotes_commas_newlines_Unicode_preserved:true,invalid_identity_rejected:true,isolated_local_draft_reload:true,zoom_controls:true,all_twenty_printable:true,synthetic_choices_not_human_decisions:true});
 }finally{fs.writeFileSync(path.join(out,'viewer_QA.json'),JSON.stringify(report,null,2)+'\n');await browser.close()}
}
main().catch(e=>{console.error(e);process.exitCode=1});
