"""Separate local review-implementation checkpoint for one assigned book."""
from reconnaissance import *
b=int(sys.argv[1]);assert b in [18,19]
d=packet(b)
names=['APPROVED_SECURE_MARKER_PLAN.json','INDEPENDENT_REVIEW_PRESERVATION_QA.json',
       'REVIEW_EXPECTED_INTERVALS.json','REVIEW_IDENTITY_REGISTRY.json','SECURE_REVIEW_IMPLEMENTATION.json',
       'review-output/Latin.xml','evidence/review-harness-light.png','evidence/review-harness-dark.png']
paths=[str((d/n).relative_to(ROOT)).replace('\\','/') for n in names]
assert not git('diff','--cached','--name-only').strip()
subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True)
assert set(git('diff','--cached','--name-only').decode().splitlines())<=set(paths)
subprocess.run(['git','commit','-m',f'Prepare reversible Antiquities { {18:"XVIII",19:"XIX"}[b]} secure review implementation'],cwd=ROOT,check=True)
print(git('rev-parse','HEAD').decode().strip())
