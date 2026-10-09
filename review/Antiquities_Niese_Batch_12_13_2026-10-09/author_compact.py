"""Expand human-authored pipe records into explicit per-boundary review JSON."""
from prepare_review import *
import subprocess
b=int(sys.argv[1]);src=Path(sys.argv[2]);data={}
for line in src.read_text(encoding='utf8').splitlines():
 if not line.strip() or line.startswith('#'):continue
 fields=line.split('|');assert 5<=len(fields)<=7,line
 n,phrase,assessment,page,position=fields[:5]
 data[n]={'phrase':phrase,'assessment':assessment,'page':int(page),'position':position}
 if len(fields)>5 and fields[5]:data[n]['limits']=fields[5]
 if len(fields)>6 and fields[6]:data[n]['paragraph']=fields[6]
dest=src.with_suffix('.json');save(dest,data)
subprocess.run([sys.executable,'-B',str(PACK/'author_batch.py'),str(b),str(dest)],check=True)
