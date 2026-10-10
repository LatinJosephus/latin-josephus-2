"""Make a scoped local scholarly-review checkpoint, excluding implementation QA."""
from reconnaissance import *
b=int(sys.argv[1]);assert b in [18,19]
d=packet(b)
names=['IDENTITIES.json','DECISION_HISTORY.json','PRINTED_SOURCES.json','FROZEN_RECONCILIATION_RECORDS.json',
       'FROZEN_VERIFICATION_RECORDS.json','PRIMARY_REVIEW_COMPLETE.json','OPENING_AND_PARATEXT_REVIEW.json']
files=[d/n for n in names]+list(d.glob('review-*.json'))+list(d.glob('CASE_*.json'))+list(d.glob('CASE_*.md'))
if b==18:files+=list((d/'evidence').glob('Loeb-IX-PDF*.jpg'))
paths=[str(p.relative_to(ROOT)).replace('\\','/') for p in files]
assert all(p.startswith(str(d.relative_to(ROOT)).replace('\\','/')+'/') for p in paths)
assert not git('diff','--cached','--name-only').strip(),'Refuse a mixed staged checkpoint'
subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True)
staged=git('diff','--cached','--name-only').decode().splitlines();assert set(staged)<=set(paths)
assert staged
title=f'Complete Antiquities { {18:"XVIII",19:"XIX"}[b]} primary review; retain pending editorial cases'
subprocess.run(['git','commit','-m',title],cwd=ROOT,check=True)
print(git('rev-parse','HEAD').decode().strip())
