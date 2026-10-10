from pathlib import Path
import json,hashlib,subprocess,sys,zipfile,datetime
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
RUNTIME=Path(r'C:\workspace\Antiquities-Niese-Proem-Integration-runtime-20261010')
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    name=sys.argv[1];target=RUNTIME/'checkpoints'/(name+'.zip');assert not target.exists()
    rev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    files=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['BASELINE_PROTECTED_BROWSER.json','PROTECTED_GIT_OBJECTS.json','STRUCTURAL_CONTROLS.json','FINAL_PROTECTED_BROWSER.full.json'] and p.suffix not in ['.png','.jpg']]
    manifest=[]
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as z:
        for p in files:
            raw=p.read_bytes();n=p.relative_to(P).as_posix();z.writestr(n,raw);manifest.append({'path':n,'bytes':len(raw),'sha256':sha(raw)})
        z.writestr('CHECKPOINT_MANIFEST.json',json.dumps({'head':rev,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':manifest},indent=2))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for row in manifest:assert sha(z.read(row['path']))==row['sha256']
    receipt={'head':rev,'archive':str(target),'bytes':target.stat().st_size,'sha256':sha(target.read_bytes()),'verified_payloads':len(manifest),'CRC':'PASS','immutable_once_written':True}
    (RUNTIME/'checkpoints'/(name+'.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
if __name__=='__main__':main()
