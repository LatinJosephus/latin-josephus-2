"""Reconstruct the three registered outputs without modifying the source checkout."""
from pathlib import Path
import argparse,json,subprocess
from verify_v2 import BASE,PACKET,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--output-dir',type=Path);a=p.parse_args();root=a.root.resolve();rows=json.loads((root/PACKET/'exact_reversible_changes.json').read_text())['files'];out=[]
 if a.output_dir:
  targetbase=a.output_dir.resolve();assert targetbase!=root and not root.is_relative_to(targetbase)
 for r in rows:
  before=subprocess.check_output(['git','-c','core.longpaths=true','--no-optional-locks','show',BASE+':'+r['path']],cwd=root);assert sha(before)==r['before_sha256'];after=before
  for op in reversed(r['operations']):
   a0,b0=op['before_start'],op['before_end'];assert before[a0:b0]==bytes.fromhex(op['old_hex']);after=after[:a0]+bytes.fromhex(op['new_hex'])+after[b0:]
  assert sha(after)==r['after_sha256']
  if a.output_dir:
   path=(targetbase/r['path']).resolve();assert path.is_relative_to(targetbase) and not path.exists();path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
  out.append({'path':r['path'],'sha256':sha(after)})
 print(json.dumps({'result':'PASS','files':out,'source_checkout_modified':False},indent=2))
if __name__=='__main__':main()
