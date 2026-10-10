from prepare import *
import zipfile,datetime
def main():
    p=PACK/'FINAL_PROTECTED_BROWSER.full.json';raw=p.read_bytes();r=json.loads(raw);count=len(r['selections'])
    assert count>0 and not r['errors'] and r['status'] in ['RUNNING','PASS']
    base=json.loads((PACK/'BASELINE_PROTECTED_BROWSER.json').read_text());assert r['selections']==base['selections'][:count]
    name='fresh-replay-'+str(count);target=RUNTIME/'checkpoints'/(name+'.zip');assert not target.exists()
    m=dict(source_build=r['sourceBuild'],selections=count,target=7350,status=r['status'],exact_rows_verified=True,raw_sha256=sha(raw),bytes=len(raw),created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as z:z.writestr('FINAL_PROTECTED_BROWSER.progress.json',raw);z.writestr('MANIFEST.json',json.dumps(m,indent=2))
    with zipfile.ZipFile(target) as z:assert z.testzip() is None and sha(z.read('FINAL_PROTECTED_BROWSER.progress.json'))==sha(raw)
    save(RUNTIME/'checkpoints'/(name+'.json'),dict(status='PASS_DURABLE_REPLAY_PROGRESS',archive=info(target),replay=m,CRC='PASS'))
    print('PASS archived '+str(count)+' exact fresh replay rows; '+str(target))
if __name__=='__main__':main()
