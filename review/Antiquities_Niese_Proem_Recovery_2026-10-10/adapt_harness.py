from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
f=P/'protected_browser.cjs';s=f.read_text(encoding='utf-8')
assert 'FINAL_PROTECTED_BROWSER.full.json' not in s
s=s.replace("'FINAL_PROTECTED_BROWSER.json'","'FINAL_PROTECTED_BROWSER.full.json'")
s=s.replace('r.selections.push(row);','r.selections.push(row);if(r.selections.length%100===0){console.log("Replay durable progress",r.selections.length);fs.writeFileSync(path.join(P,"FINAL_PROTECTED_BROWSER.full.json"),JSON.stringify(r,null,2));}')
f.write_text(s,encoding='utf-8',newline='\n')
f=P/'proem_browser.cjs';s=f.read_text(encoding='utf-8')
assert 'stalePaneSequence' not in s
s=s.replace('for(const n of [1,2,25,26]){','r.stalePaneSequence=[];for(const n of [25,26,25,26]){await s.select(n);const a=await check(n);r.stalePaneSequence.push({number:n,Latin_sha256:sha(norm(a.languages.Latin)),duplicates:a.duplicates,status:"PASS"});}\n  for(const n of [1,2,25,26]){')
f.write_text(s,encoding='utf-8',newline='\n')
prov=json.loads((P/'QA_HARNESS_PROVENANCE.json').read_text())
prov['recovery_changes']=['protected report uses ignored full evidence file, saves progress every 100 selections, all baseline comparisons unchanged','Proem adds explicit 25-26-25-26 sequence with full extent and duplicate-ID checks']
for a in prov['adapters']:a['adapter_sha256']=hashlib.sha256((P/a['file']).read_bytes()).hexdigest()
(P/'QA_HARNESS_PROVENANCE.json').write_text(json.dumps(prov,indent=2)+'\n',encoding='utf-8',newline='\n')
