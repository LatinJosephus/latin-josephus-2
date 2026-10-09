"""Save individually authored boundary assessments; no automatic confidence inference."""
import argparse,json,pathlib
P=pathlib.Path(__file__).resolve().parent;W=P.parents[1]
a=argparse.ArgumentParser();a.add_argument('--book',type=int,choices=[8,10],required=True);args=a.parse_args()
d=W/f'review/Antiquities_Niese_Book{"VIII" if args.book==8 else "X"}_2026-10-08';f=d/'LATIN_INDIVIDUAL_REVIEWS.json'
notes=json.loads(f.read_text(encoding='utf8')) if f.exists() else {}
import sys
for line in sys.stdin.read().splitlines():
 if not line.strip():continue
 bits=line.split('|');n,status,assessment=bits[:3];assert status in ['SECURE','OPEN'];assert int(n)>0 and assessment.strip()
 value={'status':status,'assessment':assessment.strip(),'method':'Individual comparison of Greek incipit, Latin cut and adjoining Latin context; not inferred from Greek verification or section arithmetic.','scope':'CANDIDATE_BOUNDARY_ONLY_NOT_IMPLEMENTATION_CERTIFICATION'}
 if len(bits)>3 and bits[3].strip():value['proposed_anchor']=bits[3].strip()
 assert n not in notes or notes[n]==value,('Refusing to overwrite an earlier individual review',n)
 notes[n]=value
f.write_text(json.dumps(dict(sorted(notes.items(),key=lambda x:int(x[0]))),ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(args.book,'individual assessments recorded',len(notes))
