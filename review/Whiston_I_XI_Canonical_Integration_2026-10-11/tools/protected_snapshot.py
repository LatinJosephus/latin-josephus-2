from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'review/Whiston_I_XI_Canonical_Integration_2026-10-11'
repositories={'canonical':'C:/Users/Pollard_R/Git/LatinJosephus-v2-development',
 'prototype':'C:/workspace/LatinJosephus-Whiston-I-XI-Renderer-Prototype-20261011',
 'XII':'C:/workspace/LatinJosephus-BookXII-Pilot-20261011',
 'XIII':'C:/workspace/LatinJosephus-BookXIII-Pilot-20261011',
 'XIV':'C:/workspace/LatinJosephus-BookXIV-Pilot-20261011'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(repo,*a):return subprocess.check_output(['git',*a],cwd=repo).decode().strip()
rows={}
for key,relative in repositories.items():
 repo=Path(relative)
 rows[key]={'path':relative,'HEAD':git(repo,'rev-parse','HEAD'),'branch':git(repo,'branch','--show-current'),
   'status':git(repo,'status','--porcelain'),'files':{p:sha((repo/p).read_bytes()) for p in git(repo,'ls-files').splitlines() if (repo/p).is_file()}}
assert rows['canonical']['HEAD']=='663b8ce318f0aa247d304d8eeda5b8e76e7489c6' and not rows['canonical']['status']
assert rows['prototype']['HEAD']=='0c1347a5a947ae5702cf60e4162d09d7510450e5' and not rows['prototype']['status']
name='PROTECTED_START.json' if '--start' in sys.argv else 'PROTECTED_FINISH.json'
if name=='PROTECTED_FINISH.json':
 original=json.loads((PACK/'PROTECTED_START.json').read_bytes());assert original==rows,'Protected worktree state changed'
# Canonical and XII/XIII also match the previous mission's complete snapshot.
prior=json.loads((ROOT/'review/Whiston_I_XI_Renderer_2026-10-11/PROTECTED_START.json').read_bytes())
for key in ['canonical','XII','XIII']:
 old=next(v for v in prior.values() if Path(v['worktree'])==Path(rows[key]['path']))
 assert old['commit']==rows[key]['HEAD'] and old['status'].strip()==rows[key]['status']
 assert old['working_files']==rows[key]['files'],key
(PACK/name).write_bytes((json.dumps(rows,indent=2)+'\n').encode())
print('Protected states verified:',{k:dict(HEAD=v['HEAD'],status=v['status'],tracked_files=len(v['files'])) for k,v in rows.items()})
