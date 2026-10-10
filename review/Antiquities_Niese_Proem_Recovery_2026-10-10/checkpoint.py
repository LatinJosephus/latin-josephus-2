"""Compact durable archive; original packet, corpus and source images stay preserved separately."""
from recover import *
import sys
def main(stage):
    folder=RUNTIME/'checkpoints';folder.mkdir(exist_ok=True)
    target=folder/(stage+'.zip');assert not target.exists()
    payload={}
    for p in sorted(PACK.rglob('*')):
        if not p.is_file() or any(x in p.parts for x in ['__pycache__','frozen-inputs','evidence']):continue
        if p.name in ['PROTECTED_GIT_OBJECTS.json','BASELINE_PROTECTED_BROWSER.json','STRUCTURAL_CONTROLS.json','FINAL_PROTECTED_BROWSER.full.json']:continue
        payload['review/'+p.relative_to(PACK).as_posix()]=p.read_bytes()
    for n in PRODUCTION_PATHS:payload['production/'+n]=(ROOT/n).read_bytes()
    payload['production-only.patch']=git('diff','--binary',BASE,'HEAD','--',*PRODUCTION_PATHS)
    payload['git-receipt.json']=(json.dumps({'stage':stage,'branch':git('branch','--show-current').decode().strip(),'tip':git('rev-parse','HEAD').decode().strip(),'status':git('status','--short').decode(),'original_checkpoint':CHECKPOINT,'production_commit':PRODUCTION,'baseline':BASE,'history_source':'surviving original repository; ZIP is an additional compact checkpoint, not a Git-history substitute'},indent=2)+'\n').encode()
    manifest=[{'path':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(payload.items())]
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in payload.items():z.writestr(n,b)
        z.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(target) as z:assert z.testzip() is None
    receipt={'stage':stage,'archive':record(target),'files':len(manifest),'CRC':'PASS','branch_tip':git('rev-parse','HEAD').decode().strip(),'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (folder/(stage+'.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    save('LATEST_CHECKPOINT.json',receipt)
    print(json.dumps(receipt))
if __name__=='__main__':main(sys.argv[1])
