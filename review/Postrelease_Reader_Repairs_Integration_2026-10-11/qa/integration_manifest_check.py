import reader_integration as a
import json,zipfile
a.saved()
start=a.u.load(a.T/'START.json');rows=[];changed=[];absent=[]
for r in start['baseline_manifest']:
 p=a.W/r['path']
 if not p.is_file():absent.append(r['path']);continue
 h=a.u.sha(p.read_bytes());same=h==r['SHA256']
 rows.append({**r,'integrated_SHA256':h,'unchanged':same})
 if not same:changed.append(r['path'])
assert not absent and sorted(changed)==a.PRODUCTION,(absent,changed)
result={'UTC':a.u.now(),'status':'PASS','baseline_commit':start['baseline'],'merged_commit':a.u.gt('rev-parse','HEAD',repo=a.W),'baseline_file_count':len(rows),'unchanged_count':len(rows)-len(changed),'changed_production_count':len(changed),'changed_production':changed,'absent':absent,'files':rows}
a.u.save(a.T/'SOURCE_MANIFEST_VERIFICATION.json',result)
snapshot={'UTC':a.u.now(),'status':'QA IN PROGRESS','merge':a.u.load(a.T/'MERGE.json'),'manifest_summary':{k:result[k] for k in ['status','baseline_file_count','unchanged_count','changed_production_count']},'jobs':{p.name:a.u.load(p) for p in a.T.glob('QA_JOB_*.json')}}
a.u.save(a.T/'checkpoints/MID_QA.json',snapshot)
with zipfile.ZipFile(a.T/'checkpoints/MID_QA.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['START.json','MERGE.json','SOURCE_MANIFEST_VERIFICATION.json','BUILD_VERSION_COMPARISON.json','PROTECTED_INPUTS.json','checkpoints/MID_QA.json']:
  z.write(a.T/name,name)
 for p in a.T.glob('QA_JOB_*.json'):z.write(p,p.name)
print(json.dumps({k:result[k] for k in ['status','baseline_file_count','unchanged_count','changed_production_count']}),flush=True)
