from pathlib import Path
import json
P=Path(__file__).resolve().parent;W=P.parent/'Whiston_Antiquities_Compiled_Index_2026-10-09';site=json.loads((P/'ENVIRONMENT.json').read_text())['build'].replace('\\','/')
s=(W/'interaction-regression.test.cjs').read_text();s=s.replace('C:/Users/Pollard_R/AppData/Local/Temp/LatinJosephus-Whiston-Index-disposable-20261009',site).replace('layout-correction','screenshots').replace("'INTERACTION_QA.json'","'PROTECTED_INTERACTION_QA.json'")
a=s.index('const server=http.createServer');b=s.index('\n(async()=>{',a)
server='''const site=SITE;
const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://local');let f=path.resolve(site,'.'+decodeURIComponent(u.pathname));if(!f.startsWith(path.resolve(site)+path.sep)){res.statusCode=403;return res.end();}if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');if(!fs.existsSync(f)){res.statusCode=404;return res.end();}let raw=fs.readFileSync(f);if(f.endsWith('renderTei.js'))raw=Buffer.from(instrument(updated));res.setHeader('Content-Type',({'.xml':'application/xml','.json':'application/json','.html':'text/html','.js':'text/javascript','.css':'text/css','.otf':'font/otf','.svg':'image/svg+xml'})[path.extname(f)]||'application/octet-stream');res.end(raw);});'''.replace('SITE',json.dumps(site))
s=s[:a]+server+s[b:];s=s.replace('Actual renderer, CETEI, source XML and selectors; canonical compiled CSS plus current source palette/reader partials; no site build','Actual fresh combined Jekyll site, renderer, CETEI, source XML and selectors; no historical build reuse')
(P/'protected-interaction.test.cjs').write_text(s,encoding='utf-8')
