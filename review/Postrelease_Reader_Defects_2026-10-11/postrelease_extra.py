import postrelease_reader as a
import subprocess,os,sys
def run():
    p=a.Path('postrelease_general_navigation.cjs');s=p.read_text();old="await c.ready(p,1).catch(async()=>{await p.locator('#latin tei-p').first().waitFor({state:'attached'})});";assert old in s;s=s.replace(old,"await p.locator('#latin tei-p').first().waitFor({state:'attached'});await p.waitForLoadState('networkidle');");p.write_text(s,encoding='utf8',newline='\n')
    env={**os.environ,'PLAYWRIGHT_MODULE':a.PW,'REPAIR_RUNTIME':str(a.T)}
    r=subprocess.run([a.NODE,str(p.resolve())],env=env)
    if r.returncode:sys.exit(r.returncode)
    # Actual structural UI checks must verify document IDs as well as extents.
    src=(a.T/'qa/containing-real.cjs').read_text()
    old='const a=await p.evaluate(c.capture);'
    new="const ids=await p.locator('[id]').evaluateAll(ns=>ns.map(n=>n.id));c.assert.equal(new Set(ids).size,ids.length,'Selected structural view has unique DOM IDs');const a=await p.evaluate(c.capture);"
    assert old in src;src=src.replace(old,new).replace("c.save('CONTAINING_REAL_UI.json',r)","c.save('CONTAINING_IDS_REAL_UI.json',r)").replace("c.browser('candidate-containing-real')","c.browser('candidate-containing-ids-real')")
    out=a.T/'qa/containing-ids-real.cjs';out.write_text(src,encoding='utf8',newline='\n')
    if not (a.T/'READER_FINAL_PRIOR_RESULTS.json').exists():
        print('General navigation complete; structural ID check awaits structural census')
        return
    r=subprocess.run([a.NODE,str(out)],env=env)
    sys.exit(r.returncode)
if __name__=='__main__':run()
