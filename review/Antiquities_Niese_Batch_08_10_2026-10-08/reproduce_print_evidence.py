r"""Render the saved full-page evidence from unchanged supplied PDFs.
Requires Poppler pdftoppm. Source PDFs are read only. Output must be a new directory.
This reproduces images, not visual scholarly judgements.
Usage: python reproduce_print_evidence.py --out C:\workspace\new-disposable-evidence
"""
import argparse,pathlib,json,hashlib,subprocess,concurrent.futures
P=pathlib.Path(__file__).parent
a=argparse.ArgumentParser();a.add_argument('--out',required=True);args=a.parse_args()
out=pathlib.Path(args.out).resolve();assert not out.exists(),'Refusing to reuse or overwrite output directory'
m=json.loads((P/'PRINT_EVIDENCE_MANIFEST.json').read_text(encoding='utf8'))
for source in m['sources']:
 assert hashlib.sha256(pathlib.Path(source['path']).read_bytes()).hexdigest()==source['sha256'],'Source hash mismatch'
out.mkdir(parents=True)
def render(e):
 dest=out/e['path'];dest.parent.mkdir(parents=True,exist_ok=True)
 command=['pdftoppm','-f',str(e['pdf_page']),'-l',str(e['pdf_page']),'-singlefile','-jpeg' if e['format']=='jpeg' else '-png','-r',str(e['dpi']),e['source_path'],str(dest.with_suffix(''))]
 subprocess.run(command,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 return dict(path=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),matches_saved_bytes=hashlib.sha256(dest.read_bytes()).hexdigest()==e['sha256'])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:r=list(pool.map(render,m['images']))
(out/'RENDER_RESULT.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print('Rendered',len(r),'images. Pixel encoding may vary with Poppler version; compare pages visually if hashes differ.')
