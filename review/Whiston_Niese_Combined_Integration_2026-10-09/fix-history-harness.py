from pathlib import Path
import json
P=Path(__file__).resolve().parent
s=(P/'combined-interaction.test.cjs').read_text(encoding='utf-8-sig')
s=s.replace('window.__combinedRendered={...state};','window.__combinedRendered={...state}; window.__combinedRevision=(window.__combinedRevision||0)+1;')
s=s.replace("async function waitView(view){await page.waitForFunction(v=>window.__combinedRendered?.viewingLevel===v,view);}","async function history(direction,view,n=null){const revision=await page.evaluate(()=>window.__combinedRevision);await page[direction]();await page.waitForFunction(({revision,view,n})=>window.__combinedRevision>revision&&window.__combinedRendered?.viewingLevel===view&&(n===null||Number(window.__combinedRendered.nieseNum)===n),{revision,view,n});}")
s=s.replace("await page.goBack();await waitView('niese-level');await niese(book,section);await page.goForward();await waitView('contents-level');", "await history('goBack','niese-level',section);await niese(book,section);await history('goForward','contents-level');")
s=s.replace("await page.goBack();await waitView('niese-level');await page.goForward();await waitView('niese-level');", "await history('goBack','niese-level',1);await history('goForward','niese-level',final);")
s=s.replace("throw Error(`${book}.${n} ${l} interval changed`)", "throw Error(`${book}.${n} ${l} interval changed: ${JSON.stringify({state:d.q,actual:d.text[l],expected:expected[book][l][n]})}`)")
(P/'combined-interaction.test.cjs').write_text(s,encoding='utf-8')
