from pathlib import Path
P=Path(__file__).resolve().parent;W=P.parents[1]
if (P/'protected-browser.cjs').exists():raise SystemExit('Initial adaptation is frozen. Run the reviewed IX browser harnesses directly; do not overwrite their dedicated profiles or final fixes.')
old=W/'review/Antiquities_Niese_Implementation_08_10_2026-10-09'
s=(old/'browser-certify.cjs').read_text(encoding='utf8')
s=s.replace("build='C:/workspace/Antiquities-Niese-Implementation-08-10-2026-10-09/build'","build='C:/workspace/Antiquities-Niese-09-runtime-20261009/build'")
s=s.replace('[8,10].includes(Number(book))','[8,9,10].includes(Number(book))')
s=s.replace("if(Number(book)<=7)","if(Number(book)<=10 && Number(book)!==9)")
start=s.index(" if(report.mode==='ui-supplement'){")
body=s.index("  report.antiquities={traditional:",start)
end=s.index(" if(report.errors.length)",body)
block=s[body:end].rstrip();assert block.endswith('}')
block=block[:-1] # remove original else branch's closing brace
s=s[:start]+block+'\n'+s[end:]
s=s.replace("mode:process.argv.includes('--ui-supplement')?'ui-supplement':process.argv.includes('--regressions')?'protected-regressions':'new-books'","mode:'protected-regressions'")
(P/'protected-browser.cjs').write_text(s,encoding='utf8',newline='\n')
# Dedicated Bellum witness-range gate uses the same locally built site and frozen renderer.
s=(old/'established-regressions.test.cjs').read_text(encoding='utf8')
s=s.replace("const base = 'a48021588e0840330388a6055a97bd0f7c2cf827';","const base = 'ad3158b7a86dea6997510b3de17f2e510c23367c';")
s=s.replace("C:/workspace/Antiquities-Niese-Implementation-08-10-2026-10-09/build/site","C:/workspace/Antiquities-Niese-09-runtime-20261009/build/site")
begin=s.index(" if(process.argv.includes('--protected-source-gate')){")
finish=s.index(" if(process.argv.includes('--rendered-gate')){",begin)
header=s[:s.index(" if(process.argv.includes('--alignment-all-gate')){")]
gate=s[begin:finish]
gate=gate.replace(" if(process.argv.includes('--protected-source-gate')){"," {")
tail="})().catch(e=>{console.error(e);fs.writeFileSync(path.join(__dirname,'BELLUM_SOURCE_FAILURE.json'),JSON.stringify({error:String(e),report},null,2));server.close();process.exit(1);});\n"
(P/'bellum-witness-gate.cjs').write_text(header+gate+tail,encoding='utf8',newline='\n')
print('Copied and scoped accepted browser comparison and Bellum witness gates to IX packet.')
