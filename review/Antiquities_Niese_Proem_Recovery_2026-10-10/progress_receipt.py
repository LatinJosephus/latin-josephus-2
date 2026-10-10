"""Compact progress receipts never promote incomplete runs to certification."""
from recover import *
from collections import Counter
def main():
    p=PACK/'FINAL_PROTECTED_BROWSER.full.json';full=json.loads(p.read_text()) if p.exists() else {'status':'NOT_STARTED','selections':[],'books':[],'views':[]}
    counts=Counter(r['book'] for r in full['selections'])
    books=[{'book':b['book'],'passed':counts[b['book']],'expected':len(b['menu']),'complete':counts[b['book']]==len(b['menu'])} for b in full['books']]
    reports={}
    for name,key in [('PROEM_BROWSER_QA.json','status'),('PLAIN_READER_QA.json','status'),('PLAIN_FINAL_CONTROLS.json','status'),('READER_XI_RESULTS.json','result'),('FRESH_FOCUSED_CONTROLS.json','status')]:
        if (PACK/name).exists():
            r=json.loads((PACK/name).read_text());reports[name]={'status':r.get(key),'report':record(PACK/name)}
        else:reports[name]={'status':'RUNNING_OR_PENDING'}
    receipt={'status':'NOT_CERTIFIED','build':json.loads((PACK/'BUILD_CONTEXT.json').read_text()),'full_replay_status':full['status'],'saved_selections':len(full['selections']),'target':7350,'XX_containing_views':len(full['views']),'books':books,'reports':reports,'source_checkpoint':git('rev-parse','HEAD').decode().strip(),'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    save('REPLAY_PROGRESS.json',receipt)
    print(json.dumps({k:receipt[k] for k in ['status','full_replay_status','saved_selections','target','XX_containing_views','books']}))
if __name__=='__main__':main()
