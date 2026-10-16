"""Reproduce the eight registered files in memory or a separate disposable output directory."""
from pathlib import Path
import argparse,json,subprocess
from verify_mechanical import BASE,PACKET,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--output-dir',type=Path);a=p.parse_args();root=a.root.resolve()
 records=json.loads((root/PACKET/'exact_reversible_changes.json').read_text())['files'];generated=[]
 if a.output_dir:
  output=a.output_dir.resolve();assert output!=root and not root.is_relative_to(output),'Output must be a separate disposable directory'
 for r in records:
  before=subprocess.check_output(['git','-c','core.longpaths=true','--no-optional-locks','show',BASE+':'+r['path']],cwd=root);assert sha(before)==r['before_sha256'];after=before
  for op in reversed(r['exact_operations']):
   lo,hi=op['before_start'],op['before_end'];assert before[lo:hi]==bytes.fromhex(op['old_hex']);after=after[:lo]+bytes.fromhex(op['new_hex'])+after[hi:]
  assert sha(after)==r['after_sha256']
  if a.output_dir:
   target=(output/r['path']).resolve();assert target.is_relative_to(output) and not target.exists(),'Do not overwrite existing outputs';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
  generated.append({'file':r['path'],'sha256':sha(after)})
 print(json.dumps({'result':'PASS','files':generated,'source_checkout_modified':False,'writes_to_separate_output_only':bool(a.output_dir)},indent=2))
if __name__=='__main__':main()
