from pathlib import Path
P=Path(__file__).resolve().parent
s=(P/'protected-interaction.test.cjs').read_text();s=s.replace('raw=Buffer.from(instrument(updated))',"raw=Buffer.from(instrument(new URL(req.headers.referer||'http://local').searchParams.has('baseline')?head:updated))")
s=s.replace('v?.outerHTML]',"v?.outerHTML.replaceAll('&amp;baseline=1','')]")
(P/'protected-interaction.test.cjs').write_text(s,encoding='utf-8')
