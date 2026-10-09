"""Record source-supported correspondence limits without changing physical cuts."""
from prepare_review import *
from record_review import apply
b=int(sys.argv[1]);d=packet(b);choices=json.loads((d/'LATIN_REVIEW_CHOICES.json').read_text(encoding='utf8'))
qualifications=json.loads((d/'QUALIFIED_CORRESPONDENCE.json').read_text(encoding='utf8'))
for n,q in qualifications.items():
 assert n in choices and choices[n]['phrase']
 choices[n]['notice']=q['note'];choices[n]['correspondence']=q['correspondence']
if b==12:choices['250']['limits']='Visible inherited label248 is retained, with its executable claim suppressed. Executable identity250 starts at the retained [250] marker and Post quam autem expoliauit templum. Adjoining 246–249 extents follow the closed user adjudication.'
save(d/'LATIN_REVIEW_CHOICES.json',choices);apply(b)
