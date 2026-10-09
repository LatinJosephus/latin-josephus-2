"""Merge explicitly authored individual reviews and observed print positions."""
from record_review import *
b=int(sys.argv[1]);p=Path(sys.argv[2]);data=json.loads(p.read_text(encoding='utf8'));d=packet(b)
c=json.loads((d/'LATIN_REVIEW_CHOICES.json').read_text(encoding='utf8')) if (d/'LATIN_REVIEW_CHOICES.json').exists() else {}
o=json.loads((d/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'))
for n,r in data.items():
 c[n]={k:v for k,v in r.items() if k not in ['page','position']}
 o[n]={'edition':'Niese III, 1892','printed_page':r['page']-72,'PDF_page':r['page'],'image':f'evidence/Niese/page-{r["page"]}.png','observed_numeral_position':r['position'],'word_boundary_status':'XML_WORD_START_CONFIRMED_FROM_PRINT','editorial_word_choice':'Keep XML start following visual examination of numeral placement, printed clauses and adjoining context.'}
save(d/'LATIN_REVIEW_CHOICES.json',c);save(d/'PRINT_OBSERVATIONS.json',o);apply(b)
