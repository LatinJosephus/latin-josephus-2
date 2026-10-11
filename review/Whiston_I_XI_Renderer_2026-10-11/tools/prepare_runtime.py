"""Preserve hash-bound publication XML byte representations in the generated preview."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11'
CANON=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
SITE=Path('C:/workspace/Whiston-I-XI-Renderer-runtime-20261011/site')
sha=lambda b:hashlib.sha256(b).hexdigest()
rows=[]
paths=subprocess.check_output(['git','ls-tree','-r','--name-only','663b8ce318f0aa247d304d8eeda5b8e76e7489c6','assets/xml/bellum','assets/xml/deh','assets/xml/contra-apionem'],cwd=ROOT).decode().splitlines()
for path in paths:
    if not path.endswith('.xml'):continue
    blob=subprocess.check_output(['git','show','663b8ce318f0aa247d304d8eeda5b8e76e7489c6:'+path],cwd=ROOT)
    source=(CANON/path).read_bytes()
    assert blob.replace(b'\r\n',b'\n')==source.replace(b'\r\n',b'\n'),path
    assert (ROOT/path).read_bytes().replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n'),path
    (SITE/path).write_bytes(source)
    rows.append({'path':path,'git_sha256':sha(blob),'publication_sha256':sha(source),'EOL_only':blob!=source})
frozen=json.loads((ROOT/'assets/data/deh-josephus-concordance.json').read_bytes())
for path,h in frozen['canonical_xml_sha256'].items():
    if '/deh/' in path or '/bellum/' in path:assert sha((SITE/path).read_bytes())==h,path
(PACK/'PUBLICATION_BYTE_REPRESENTATION.json').write_bytes((json.dumps({'status':'PASS','repo_witness_sources_modified':False,'files':rows,'explanation':'Existing reviewed DEH/Bellum authority hashes bind CRLF publication bytes. Fresh Git worktrees contain LF. Only generated preview assets preserve the reviewed representation; repository witnesses and frozen hashes are unchanged.'},indent=2)+'\n').encode())
print('Preserved reviewed byte representations in generated preview:',len(rows),'XML files.')
