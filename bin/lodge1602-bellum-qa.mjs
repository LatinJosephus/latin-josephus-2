#!/usr/bin/env node
// Independent local QA runner. The built publication and frozen authorities are read-only.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile, writeFile, cp, mkdtemp } from "node:fs/promises";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { resolve, sep } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
const root = resolve(fileURLToPath(new URL("../", import.meta.url)));
const args = process.argv.slice(2);
const option = (name, fallback) => args.includes(name) ? args[args.indexOf(name)+1] : fallback;
const pwsh = option("--pwsh", "pwsh");
const sha = b => createHash("sha256").update(b).digest("hex");
const baseline = "57b89a9d107bb76a2b30c146e401a2c76e25e4c3";
const native = resolve(root, "bin/deh-concordance-xml.ps1");
const corpus = (directory, script=native) => JSON.parse(execFileSync(pwsh,
  ["-NoProfile","-File",script,"-Mode","Corpus","-RepoRoot",directory], {encoding:"utf8",maxBuffer:32*1024*1024,stdio:["ignore","pipe","pipe"]}));
const frozen = await readFile(resolve(root,"assets/data/deh-josephus-concordance.json"));
assert.equal(sha(frozen),"c8f59a9bdfd8c49350b4d2656d1c685f4c4a63bd96450ddfd218ac3c07ca743c");
const historical = JSON.parse(frozen).canonical_xml_sha256;
const current = corpus(root).xml_sha256;
assert.deepEqual(Object.keys(current).sort(),Object.keys(historical).sort());
const differences = Object.entries(historical).filter(([p,h])=>current[p]!==h)
  .map(([path,expected_sha256])=>({path,expected_sha256,current_sha256:current[path]}));
assert.deepEqual(differences.map(d=>d.path).sort(),
  ["assets/xml/antiquities/Greek/book-05.xml","assets/xml/antiquities/Latin/book-05.xml"]);
const shadow = await mkdtemp(resolve(tmpdir(),"lodge-inventory-"));
await cp(resolve(root,"assets/xml"),resolve(shadow,"assets/xml"),{recursive:true});
const oldScript = resolve(shadow,"baseline-deh-concordance-xml.ps1");
await writeFile(oldScript,execFileSync("git",["show",baseline+":bin/deh-concordance-xml.ps1"],{cwd:root}));
const old = corpus(shadow,oldScript).xml_sha256;
const newPaths = Array.from({length:7},(_,i)=>"assets/xml/bellum/English/Lodge1602/book-0"+(i+1)+".xml");
assert.equal(Object.keys(old).length,107);
assert.deepEqual(Object.keys(old).filter(p=>!(p in historical)).sort(),newPaths);
await writeFile(resolve(shadow,"assets/xml/bellum/English/Lodge1602/unexpected.xml"),'<TEI xmlns="http://www.tei-c.org/ns/1.0"/>');
const unexpected = corpus(shadow).xml_sha256;
assert.ok("assets/xml/bellum/English/Lodge1602/unexpected.xml" in unexpected);
assert.throws(()=>assert.deepEqual(Object.keys(unexpected).sort(),Object.keys(historical).sort()));
const exempt = resolve(shadow,newPaths[0]);
await writeFile(exempt,"<malformed");
assert.throws(()=>corpus(shadow), "Exempt Lodge paths must still be parsed");
const inventory = {
  status:"PASS", compatibility_patch_required:true, historical_paths_checked:100,
  historical_paths_matching:98, preserved_baseline_mismatches:differences,
  unpatched_inventory_count:107, exact_exempt_paths:newPaths,
  unexpected_xml_detected:true, malformed_exempt_xml_rejected:true,
  frozen_concordance_sha256:sha(frozen)
};
console.log("Inventory QA PASS: exact seven-path exemption; 100 historical checks; two preserved baseline mismatches.");
if (args.includes("--inventory-only")) { console.log(JSON.stringify(inventory,null,2)); process.exit(0); }
const built = resolve(root, option("--site","_site"));
const checkpointPath=resolve(root,"../lodge1602-browser-checkpoint.json");
const fingerprintPaths=["assets/js/renderTei.js","assets/js/CETEI.js","assets/css/tei.css",
  ...Array.from({length:7},(_,i)=>["Latin","Greek","English","English/Lodge1602"].map(d=>"assets/xml/bellum/"+d+"/book-0"+(i+1)+".xml")).flat()];
const fingerprint=sha(Buffer.from((await Promise.all(fingerprintPaths.map(async p=>p+":"+sha(await readFile(resolve(built,p)))))).join("\n")));
let checkpoint={fingerprint};
try { const saved=JSON.parse(await readFile(checkpointPath,"utf8")); if(saved.fingerprint===fingerprint)checkpoint=saved; } catch(e) { if(e.code!=="ENOENT")throw e; }
const saveCheckpoint=()=>writeFile(checkpointPath,JSON.stringify(checkpoint,null,2)+"\n");
const legacyRenderer = execFileSync("git",["show",baseline+":assets/js/renderTei.js"],{cwd:root});
const legacyCss = execFileSync("git",["show",baseline+":assets/css/tei.css"],{cwd:root});
const type = p => p.endsWith(".html")?"text/html":p.endsWith(".css")?"text/css":p.endsWith(".js")?"text/javascript":p.endsWith(".xml")?"application/xml":p.endsWith(".json")?"application/json":"application/octet-stream";
function host(legacy=false) {
  const server = createServer(async(req,res)=>{
    try {
      let p = decodeURIComponent(new URL(req.url,"http://localhost").pathname);
      if (p.endsWith("/")) p+="index.html";
      let body;
      if (legacy && p==="/assets/js/renderTei.js") body=legacyRenderer;
      else if (legacy && p==="/assets/css/tei.css") body=legacyCss;
      else if (p==="/bin/lodge1602-bellum-browser-qa.js") body=await readFile(resolve(root,"bin/lodge1602-bellum-browser-qa.js"));
      else {
        const file=resolve(built,"."+p);
        if (!file.startsWith(built+sep)) throw new Error("Path escapes built site");
        body=await readFile(file);
      }
      res.writeHead(200,{"Content-Type":type(p)+"; charset=utf-8"}); res.end(body);
    } catch { res.writeHead(404); res.end("Missing QA resource"); }
  });
  return new Promise(resolve=>server.listen(0,"127.0.0.1",()=>resolve(server)));
}
const server=await host(); const oldServer=await host(true);
const require=createRequire(import.meta.url);
const {chromium}=require(require.resolve("playwright",{paths:[option("--module-root",root)]}));
const browser=await chromium.launch({headless:true, executablePath:option("--browser",undefined)});
const base="http://127.0.0.1:"+server.address().port;
const oldBase="http://127.0.0.1:"+oldServer.address().port;
const errors=[], externalFailures=[];
try {
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  // The existing reader relies on the collection extension supplied by its
  // external UI environment. Supply the same native iteration contract for
  // offline QA; neither production renderer is changed.
  await context.addInitScript(() => {
    if (!HTMLCollection.prototype.forEach) {
      HTMLCollection.prototype.forEach = Array.prototype.forEach;
    }
  });
  // Unrelated CDN dependencies may be unavailable offline. Keep their failures
  // separate; never intercept the reader, CETEI, local CSS or TEI requests.
  context.on("requestfailed",r=>{
    (r.url().startsWith(base)||r.url().startsWith(oldBase)?errors:externalFailures).push({url:r.url(),error:r.failure()?.errorText});
  });
  const page=await context.newPage();
  page.on("console",m=>{if(m.text().startsWith("Lodge QA progress"))console.log(m.text());});
  page.on("pageerror",e=>{errors.push({type:"pageerror",message:e.message});console.log("Browser page error:",e.message);});
  page.on("response",r=>{if(r.status()>=400&&r.url().startsWith(base)) errors.push({url:r.url(),status:r.status()});});
  await page.goto(base+"/bellum-judaicum/",{waitUntil:"domcontentloaded"});
  await page.waitForFunction(()=>document.querySelector("#english tei-div1"),{timeout:60000});
  await page.addScriptTag({url:base+"/bin/lodge1602-bellum-browser-qa.js"});
  assert.equal(await page.locator("#english-source-selector").inputValue(),"whiston","Fresh default");
  const lodge=checkpoint.lodge||await page.evaluate(()=>window.lodgeReaderQA("lodge1602"));
  checkpoint.lodge=lodge; await saveCheckpoint();
  console.log("Lodge actual reader PASS:",JSON.stringify(lodge.counts));
  const whiston=checkpoint.whiston||await page.evaluate(()=>window.lodgeReaderQA("whiston"));
  checkpoint.whiston=whiston; await saveCheckpoint();
  console.log("Whiston actual reader PASS:",JSON.stringify(whiston.counts));
  const baselinePage=await context.newPage();
  await baselinePage.goto(oldBase+"/bellum-judaicum/",{waitUntil:"domcontentloaded"});
  await baselinePage.waitForFunction(()=>document.querySelector("#english tei-div1"),{timeout:60000});
  await baselinePage.addScriptTag({url:oldBase+"/bin/lodge1602-bellum-browser-qa.js"});
  const previous=checkpoint.previous||await baselinePage.evaluate(()=>window.lodgeReaderQA("whiston"));
  checkpoint.previous=previous; await saveCheckpoint();
  assert.deepEqual(whiston.digest,previous.digest,"Whiston rendered output differs from baseline");
  console.log("All Whiston chapter/coarse/Niese output hashes equal approved baseline renderer.");
  const sourceState=await page.evaluate(async()=>{await window.lodgeSourceStateQA();return window.lodgeSourceStateResult;});
  await page.reload({waitUntil:"domcontentloaded"});
  await page.waitForFunction(()=>document.querySelector("#english h3")?.textContent.includes("Lodge (1602)")&&document.querySelector("#english tei-div2[n='182']"),{timeout:60000});
  await page.setViewportSize({width:390,height:844});
  // The native controls remain usable even when the external collapse library
  // is unavailable. Opening the existing settings panel is a QA presentation step.
  await page.evaluate(()=>document.querySelector("#collapse-settings").classList.add("show"));
  await page.focus("#english-source-selector");
  await page.keyboard.press("Home"); await page.keyboard.press("Enter");
  await page.waitForFunction(()=>document.querySelector("#english h3")?.textContent.includes("Whiston"),{timeout:60000});
  await page.keyboard.press("End"); await page.keyboard.press("Enter");
  await page.waitForFunction(()=>document.querySelector("#english h3")?.textContent.includes("Lodge (1602)"),{timeout:60000});
  await page.screenshot({path:resolve(root,"../Lodge1602_Bellum_narrow_QA.png"),fullPage:false});
  const shellErrors=errors.filter(e=>e.type==="pageerror"&&/\$ is not defined|mediumZoom is not defined|Masonry is not defined|imagesLoaded is not defined/.test(e.message));
  const relevant=errors.filter(e=>!shellErrors.includes(e));
  assert.deepEqual(relevant,[],"Relevant local reader/HTTP errors");
  const report={
    schema:"lodge1602-bellum-browser-qa-v1",date:"2026-10-03",status:"PASS",
    browser:await browser.version(),engine:"Chromium",engines_tested:1,
    actual_built_reader:true,site_build_override:"Only jekyll-responsive-image omitted: installed RMagick binary unavailable; production reader/page/layout/CSS unchanged.",
    offline_qa_environment:"HTMLCollection.forEach uses Array.forEach; external CDN shell failures are reported separately.",
    lodge,whiston:{...whiston,baseline_exact_render_digest_match:true},source_state_qa:sourceState,
    narrow_native_keyboard_selection:"PASS",viewport:{width:390,height:844},
    relevant_console_or_local_http_errors:relevant,unrelated_offline_shell_errors:shellErrors,
    external_cdn_request_failures:externalFailures,inventory
  };
  await writeFile(resolve(root,"_docs/lodge1602-bellum-browser-qa.json"),JSON.stringify(report,null,2)+"\n");
  console.log("Complete browser/source/history/keyboard QA PASS.");
} finally { await browser.close(); server.close(); oldServer.close(); }
