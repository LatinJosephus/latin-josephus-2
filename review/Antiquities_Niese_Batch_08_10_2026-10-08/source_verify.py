from pathlib import Path
import json, hashlib, re, subprocess, zipfile
ROOT=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review')
OUT=Path(__file__).parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result=[]
for folder,name in [('Antiquities_Loeb_Niese_Verification_2026-10-05','Antiquities_Loeb_Niese_Verification_SHA256SUMS.txt'),('Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06','Antiquities_Structure_Reconciliation_v1.1_SHA256SUMS.txt')]:
 root=ROOT/folder; manifest=root/name; rows=[]
 for line in manifest.read_text(encoding='utf-8-sig').splitlines():
  m=re.match(r'^([0-9a-f]{64})\s+\*?(.+)$',line)
  if not m: continue
  p=root/m[2]; actual=sha(p) if p.is_file() else None
  rows.append(dict(path=m[2],expected=m[1],actual=actual,match=actual==m[1]))
 result.append(dict(root=str(root),manifest=str(manifest),manifest_sha256=sha(manifest),files=rows,pass_all=all(x['match'] for x in rows)))
write('FROZEN_SOURCE_VERIFICATION.json',result)
resources=Path(r'C:\Users\Pollard_R\Git\Segmentation resources')
files=subprocess.check_output(['rg','--files','--hidden','-g','!.git/**',str(resources)],text=True,encoding='utf-8').splitlines()
xmls=[p for p in files if p.lower().endswith('.xml')]
selected=[dict(path=p,sha256=sha(Path(p))) for p in xmls if re.search(r'(book[-_ ]?0?[68]|book[-_ ]?10|master|niese)',p,re.I) and not re.search(r'disposable_tool_tests',p,re.I)]
zip_hits=[]; zip_inventory=[]
for p in files:
 if p.lower().endswith('.zip'):
  try:
   with zipfile.ZipFile(p) as z:
    hits=[n for n in z.namelist() if re.search(r'(book[-_ ]?0?8|book[-_ ]?10|bookviii|bookx\b).*\.xml$',n,re.I)]
    zip_inventory.append(dict(path=p,entries=len(z.namelist()),VIII_X_xml_entries=hits))
    if hits:zip_hits.append(dict(path=p,entries=hits))
  except zipfile.BadZipFile: zip_inventory.append(dict(path=p,error='Not a readable ZIP'))
write('SOURCE_SEARCH.json',dict(root=str(resources),file_count=len(files),xml_count=len(xmls),xml_paths=xmls,selected_related_resources=selected,zip_inventory=zip_inventory,bookVIII_X_zip_hits=zip_hits,conclusion='No independently identified accepted Greek master for VIII/X among supplied resources; canonical Greek is the machine source and Niese print remains primary authority. Prior VI/VII files are method evidence only.'))
print('Frozen manifests',[(r['pass_all'],len(r['files'])) for r in result]);print('Resource files',len(files),'XML',len(xmls),'VIII/X ZIP hits',len(zip_hits))
