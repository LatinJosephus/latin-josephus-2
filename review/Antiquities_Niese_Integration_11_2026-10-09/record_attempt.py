"""Retain failed browser evidence; reruns must pass their entire suites."""
from pathlib import Path
import json,hashlib,sys
D=Path(__file__).resolve().parent
R=Path('C:/workspace/Antiquities-Niese-11-integration-runtime-20261009')
attempt=sys.argv[1];target=R/('attempt-'+attempt+'-results');assert not target.exists();target.mkdir()
history=[]
for name in ['READER_XI_RESULTS.json','READER_FINAL_PRIOR_RESULTS.json','READER_EXTRA_RESULTS.json','READER_CONTAINING_RESULTS.json']:
 p=D/name
 if not p.exists():continue
 raw=p.read_bytes();r=json.loads(raw);q=target/name;q.write_bytes(raw)
 history.append(dict(name=name,started=r.get('started'),finished=r.get('finished'),result=r.get('result'),failure=r.get('failure'),errors=r.get('errors',[]),completed={k:len(r.get(k,[])) for k in ['selectors','ranges','containing','navigation','rows','rank_challenges','uninstrumented','baseline_exceptions']},full_evidence=str(q),sha256=hashlib.sha256(raw).hexdigest()))
out=D/'ATTEMPT_HISTORY.json';prior=json.loads(out.read_text()) if out.exists() else []
prior.append(dict(attempt=attempt,disposition='Not certification: local network I/O suspension interrupted browser loads. No production change; entire suites rerun in fresh profiles.',suites=history))
out.write_text(json.dumps(prior,indent=2)+'\n',encoding='utf8',newline='\n')
print('Recorded',len(history),'suite attempts without suppressing failures')
