"""Correct only the XIII review stream; preserve initial freeze/provenance."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'Antiquities_Niese_Batch_12_13_2026-10-09'))
from record_review import *
g=books(13)['Greek'];rows=json.loads((P/'CANDIDATE_REGISTER.json').read_text(encoding='utf8'))
assert all(r['Latin']['review_status']=='NOT_REVIEWED' for r in rows)
starts={int(re.findall(r'\d+',x['text'])[-1]):g.first_content(x['book_offset']) for x in g.labels};starts[1]=g.first_content(0)
for r in rows:
 n=r['niese'];at=starts[n];loc=g.locate(at);u=g.units[loc['paragraph']-1];r['Greek']['locator']=loc;r['Greek']['section']=g.stream[at:starts.get(n+1,len(g.stream))];r['Latin']['alignment_window_paragraph']=u['element'].get('sameAs','').lstrip('#')
save(P/'CANDIDATE_REGISTER.json',rows)
save(P/'NARRATIVE_EXCLUSION_REVISION.json',{'reason':'Printed contents duration line lies above narrative I.1 on Niese III p151/PDF223 although XML places it inside chapter1. Exclude it without editing source. Initial frozen census remains historical.', 'source_XML_sha256':digest(g.raw),'excluded':g.excluded,'revised_narrative_codepoints':len(g.stream),'revised_narrative_sha256':digest(g.stream.encode()),'opening_locator':g.locate(starts[1]),'validation':independent_node(g,g.locate(starts[1])),'inherited_mapper_sha256':digest((ROOT/'review/Antiquities_Niese_BookX_2026-10-08/mixed_mapper.py').read_bytes()),'batch_mapper_sha256':digest((PACK/'mixed_mapper_batch.py').read_bytes()),'fixtures':fixtures()})
