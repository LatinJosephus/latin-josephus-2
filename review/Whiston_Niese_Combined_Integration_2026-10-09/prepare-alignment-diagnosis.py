from pathlib import Path
P=Path(__file__).resolve().parent
s=(P/'established-regressions.test.cjs').read_text();s=s.replace("if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1]))throw Error('Alignment-unit/witness Book regression '+book);", "if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1])){fs.writeFileSync(path.join(__dirname,'diagnostics/ALIGNMENT_PRE_VIII_X_DIFFERENCE.json'),JSON.stringify({book,snapshots},null,2));throw Error('Alignment-unit/witness Book regression '+book);}")
(P/'alignment-diagnosis.test.cjs').write_text(s,encoding='utf-8')
