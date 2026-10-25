// Loopback-only local reader QA. No publication or external browser automation.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const args=process.argv.slice(2),opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
const site=path.resolve(opt('--site','')),out=path.resolve(opt('--out',''));
if(!args.includes('--site')||!args.includes('--out'))throw Error('Specify --site and --out');
const contentType={'.js':'text/javascript','.mjs':'text/javascript','.html':'text/html','.xml':'application/xml','.json':'application/json','.css':'text/css','.svg':'image/svg+xml','.woff2':'font/woff2'};
const serve=http.createServer(async(req,res)=>{
 try{
  const url=new URL(req.url,'http://127.0.0.1');let relative=decodeURIComponent(url.pathname).slice(1),corrupt=false;
  if(['__qa__/results','__qa__/bj-results','__qa__/ui-results'].includes(relative)&&req.method==='POST'){
   let text='';for await(const chunk of req){text+=chunk;if(text.length>1000000)throw Error('Oversized result');}
   const result=JSON.parse(req.headers['content-type']?.startsWith('application/x-www-form-urlencoded')?new URLSearchParams(text).get('result'):text);
   const name={'__qa__/results':'actual-browser-interval-qa.json','__qa__/bj-results':'actual-browser-bj-qa.json','__qa__/ui-results':'actual-browser-ui-qa.json'}[relative];
   fs.writeFileSync(path.join(out,name),JSON.stringify(result,null,2)+'\n');res.end('Local browser evidence saved');return;
  }
  if(relative.startsWith('__qa__/corrupt/')){relative=relative.slice('__qa__/corrupt/'.length);corrupt=true;}
  let file;
  if(relative==='__qa__/')file=path.join(root,'bin/aj-latin-browser-qa.html');
  else if(relative==='__qa__/aj-latin-browser-qa.mjs')file=path.join(root,'bin/aj-latin-browser-qa.mjs');
  else if(relative==='__qa__/certified-boundaries.json')file=path.join(root,'_docs/aj-latin-reconciliation/certified-boundaries.json');
  else if(relative==='__qa__/comparison-expectations.json')file=path.join(root,'_docs/aj-latin-reconciliation/comparison-expectations.json');
  else if(relative==='__qa__/bj/'){
   res.setHeader('Content-Type','text/html; charset=utf-8');res.end('<!doctype html><title>Existing DEH–Bellum browser QA</title><button id="run">Run existing DEH–Bellum checks</button><p id="qa-status">Ready</p><pre id="qa-result"></pre><script src="/assets/js/CETEI.js"></script><script type="module" src="/bin/deh-parallels-browser-qa.js"></script><script>new MutationObserver(()=>{const out=document.getElementById("qa-result");if(out.dataset.complete)fetch("/__qa__/bj-results",{method:"POST",headers:{"content-type":"application/json"},body:out.textContent});}).observe(document.getElementById("qa-result"),{attributes:true,attributeFilter:["data-complete"]});</script>');return;
  }else if(relative==='__qa__/record/'){
   res.setHeader('Content-Type','text/html; charset=utf-8');res.end('<!doctype html><title>Save observed local reader checks</title><h1>Local reader evidence</h1><form method="post" action="/__qa__/ui-results"><label for="result">Observed results</label><textarea id="result" name="result" rows="20" cols="100"></textarea><button>Save local evidence</button></form>');return;
  }else if(relative==='bin/deh-parallels-browser-qa.js')file=path.join(root,relative);
  else{file=path.resolve(site,relative);if(!file.startsWith(site+path.sep)&&file!==site)throw Error('Outside site');}
  if(fs.statSync(file).isDirectory())file=path.join(file,'index.html');
  let data=fs.readFileSync(file);if(corrupt)data=Buffer.concat([data,Buffer.from('UNAUTHORIZED CORRUPTION')]);
  res.setHeader('Content-Type',contentType[path.extname(file)]||'application/octet-stream');res.setHeader('Cache-Control','no-store');res.end(data);
 }catch(e){res.writeHead(e.code==='ENOENT'?404:400);res.end(String(e));}
});
serve.listen(+opt('--port',4025),'127.0.0.1',()=>console.log(`Local AJ reader and QA: http://127.0.0.1:${serve.address().port}/__qa__/`));
