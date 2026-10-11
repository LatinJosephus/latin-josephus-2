const fs=require('fs'),path=require('path'),http=require('http');
const site=path.resolve(process.env.WHISTON_SITE||'C:/workspace/Whiston-I-XI-Renderer-runtime-20261011/site');
const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.xml':'application/xml','.svg':'image/svg+xml','.otf':'font/otf','.woff2':'font/woff2'};
http.createServer((req,res)=>{
 const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname),file=path.resolve(site,'.'+pathname+(pathname.endsWith('/')?'index.html':''));
 if(!file.startsWith(site+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);return res.end();}
 res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');res.end(fs.readFileSync(file));
}).listen(Number(process.env.WHISTON_PORT||4173),'127.0.0.1',()=>console.log('Local prototype: http://127.0.0.1:'+(process.env.WHISTON_PORT||4173)+'/antiquities/?book=9&niese=51'));
