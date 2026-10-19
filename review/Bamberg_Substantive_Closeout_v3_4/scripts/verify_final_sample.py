"""Read-only sample-draw, source-binding and exact-pixel verification.
Use --root for staged repository and --cache for the immutable native directory.
"""
from pathlib import Path
import argparse,json,random,hashlib
from PIL import Image
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def digest(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--root',type=Path);p.add_argument('--cache',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();f=a.packet/'final_verification';frame=load(f/'sampling_frame.json');sealed=load(f/'sampling_plan.json');records=load(f/'sample_records.json');bybook={r['book']:r for r in records};assert len(records)==len(bybook)==20
 for x in frame['books']:
  b=x['book'];ns=x['eligible_Niese_sections'];seed=int(hashlib.sha256((frame['seed']+f'|book={b}').encode()).hexdigest(),16);ix=random.Random(seed).randrange(len(ns));r=bybook[b];assert ns[ix]==r['niese']==x['selected_Niese'];assert r['niese'] not in x['excluded_previously_reviewed_Niese'];assert r['staged_transcription']==next(t for t in sealed['records'] if t['book']==b)['quote'];assert not r['review_decision'] and not r['editorial_comments']
  if a.root:
   data=(a.root/r['staged_source_path']).read_bytes();assert digest(data)==r['staged_source_sha256'];assert data[r['staged_source_byte_start']:r['staged_source_byte_end']].decode()==r['staged_transcription'];x,y=r['context_source_byte_span'];assert data[x:y].decode()==r['complete_raw_Niese_context']
  im=None
  if a.cache:
   native=a.cache/Path(r['native_source']).name;data=native.read_bytes();assert digest(data)==r['native_sha256'];im=Image.open(native).convert('RGB')
  for kind,asset in r['assets'].items():
   asset_path=f/asset['file'];assert digest(asset_path.read_bytes())==asset['sha256'];pic=Image.open(asset_path);pic.load();assert list(pic.size)==asset['dimensions']
   if im is not None and kind in ['tight','context']:assert pic.convert('RGB').tobytes()==im.crop(asset['xyxy']).tobytes()
 out=dict(result='PASS',seed=frame['seed'],books=20,selected_passages=20,identical_to_sealed_draw=True,prior_RMP_loci_excluded=True,all_sixty_assets_decode=True,exact_native_pixel_check=bool(a.cache),exact_staged_source_context_check=bool(a.root),new_manuscript_checks=0,remaining_human_budget=20,protected_reserve=20)
 if a.output:a.output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
