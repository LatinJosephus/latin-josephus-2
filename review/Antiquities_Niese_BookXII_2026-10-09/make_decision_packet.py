from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'Antiquities_Niese_Batch_12_13_2026-10-09'))
from record_review import *
bs=books(12);l=bs['Latin'];g=bs['Greek'];rows=json.loads((P/'CANDIDATE_REGISTER.json').read_text(encoding='utf8'))
locs={}
for n,para,phrase in [(246,'latin-book12-num246','Reuersus ergo'),(247,'latin-book12-num246','Ingres susque'),(249,'latin-book12-num246','nec non etiam eos'),(250,'latin-book12-num248','Post quam autem')]:
 u=next(u for u in l.units if u['id']==para);at=u['book_start']+u['text'].index(phrase);loc=l.locate(at);locs[str(n)]={'phrase':phrase,'locator':loc,'validation':independent_node(l,loc)}
save(P/'DECISION_XII_248_249.json',{'status':'PENDING_USER_DECISION','input_sha256':digest(l.raw),'Greek_input_sha256':digest(g.raw),'Greek':[{k:v for k,v in r.items() if k in ['book','niese','Greek']} for r in rows[241:256]],'Latin_context':[{'paragraph':u['id'],'text':u['text'],'raw_unit_sha256':u['raw_hash']} for u in l.units if u['id'] in ['latin-book12-num242','latin-book12-num246','latin-book12-num248']],'alternative_A_starts':locs,'recommendation':'A','alternative_B':'Retain all 247 text until250; no independent248/249 interval; retain partial correspondence notes.'})
