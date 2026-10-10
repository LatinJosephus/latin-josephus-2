"""Use actual selector events and require all language panes to finish rendering."""
from reconnaissance import PACK
p=PACK/'review_reader.cjs'
s=p.read_text(encoding='utf8')
old="await page.selectOption('#niese-selector',String(e.number));await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n)&&document.querySelector(`#greek [type=\"niese-section\"][n=\"${n}\"]`),e.number);"
new="""await page.evaluate(async n=>{const menu=document.querySelector('#niese-selector');menu.value=String(n);menu.dispatchEvent(new Event('change',{bubbles:true}));const start=Date.now();await new Promise((resolve,reject)=>{const check=()=>{if(window.__qaRenderedState?.nieseNum===String(n)&&['latin','greek','english'].every(l=>document.querySelector(`#${l} [n="${n}"][type^="niese-"]`)))return resolve();if(Date.now()-start>30000)return reject(Error('All panes did not finish rendering '+n));setTimeout(check,5);};check();});},e.number);"""
assert s.count(old)==1
s=s.replace(old,new)
p.write_text(s,encoding='utf8',newline='\n')
