from pathlib import Path
import json
from datetime import datetime,timezone
D=Path(__file__).resolve().parent
def save(name,x):(D/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
p=json.loads((D/'INTERPOLATION_DECISION.json').read_text(encoding='utf8'))
assert p['status']=='PENDING'
p.update(status='CLOSED_USER_APPROVED',selected='Beside each312 portion',rejected='Both after assembledXI312 narrative',
    reason_rejected='Obscures the distinct positions in the transmitted sequence.',
    closed_at=datetime.now(timezone.utc).isoformat(),authority='Direct user reply in this assignment',
    requirements=['Canonical312a then312b','105a immediately before312a and105b immediately before312b','Separate visual and structural identification as interpolated Latin Bellum Judaicum','Concise transposition explanation','311 and342 exclude both','Each physical occurrence once per combined selection','Interpolations are not new identities or primary Antiquities fragments','Book/Alignment XML order unchanged','Accepted traditional fragments unchanged','No transmitted text or relationships changed'])
for s in p['sources']:s['association_status']='CLOSED_USER_APPROVED'
save('INTERPOLATION_DECISION.json',p)
h=json.loads((D/'DECISION_HISTORY.json').read_text(encoding='utf8'));h.append(dict(id='XI312-interpolation-presentation',status=p['status'],selected=p['selected'],rejected=p['rejected'],reason=p['reason_rejected'],authority=p['authority'],closed_at=p['closed_at']))
save('DECISION_HISTORY.json',h)
text=(D/'INTERPOLATION_DECISION.md').read_text(encoding='utf8').replace('Decision pending.','Decision CLOSED: direct user approval of the recommended presentation.').replace('Concrete alternative:','Rejected alternative:')
text+='\nUser additionally requires separate visual and structural identification as interpolated Latin Bellum Judaicum material. The trailing attachment alternative is rejected because it obscures the distinct transmitted positions.\n'
(D/'INTERPOLATION_DECISION.md').write_text(text,encoding='utf8',newline='\n')
print('Direct user decision recorded; no remaining interpolation affiliation question.')
