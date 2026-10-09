from pathlib import Path
import json
from mixed_mapper import Book
P=Path(__file__).resolve().parent
decision_path=P/'EDITORIAL_DECISIONS.json'
if decision_path.exists():
    decision=json.loads(decision_path.read_text(encoding='utf8')).get('240',{})
    if decision.get('status')=='CLOSED_EXPLICIT_USER_EDITORIAL_RESOLUTION':
        packet=json.loads((P/'DECISION_240_ALTERNATIVES.json').read_text(encoding='utf8'))
        assert packet['adopted_alternative']==decision['choice']
        print('Closed adjudication and original alternatives retained; no pending packet regenerated.')
        raise SystemExit(0)
base=json.loads((P/'BASELINE.json').read_text(encoding='utf8'));rows=json.loads((P/'BOUNDARIES.json').read_text(encoding='utf8'))
books={lang:Book(raw=Path(base['inputs'][f'assets/xml/antiquities/{lang}/book-09.xml']['snapshot']).read_bytes()) for lang in ['Greek','Latin']}
alternatives={}
for name,ga,la in [('A','ἔσται δ᾽ οὐδεὶς','et nullus hanc uoluntatem'),('B','σώζειν γὰρ','dum animas suas')]:
    alternatives[name]={}
    for lang,anchor in [('Greek',ga),('Latin',la)]:
        b=books[lang];cut=b.stream.index(anchor);a=rows[238][lang+'_locator']['book_offset'];end=rows[240][lang+'_locator']['book_offset']
        alternatives[name][lang]={'chosen_cut':b.locate(cut),'section_239':b.stream[a:cut],'section_240':b.stream[cut:end],'section_239_extent':[a,cut],'section_240_extent':[cut,end]}
packet={'section':240,'status':'PENDING_USER_ADJUDICATION','recommendation':'A','printed_Niese':{'edition':'Opera II, Berlin 1885','printed_page':317,'PDF_page':325,'image':'evidence/Niese-pdf-325.png','observed_numeral':'right margin against line containing both ἔσται δ᾽ and σώζειν γὰρ; exact cut not typographically marked'},'control_Loeb':{'edition':'Marcus, Loeb VI, 1958','printed_page':126,'PDF_page':142,'image':'evidence/Loeb-control-142.png','observed_numeral':'left margin against line containing tail of ἁρπάσατε and both proposed clause starts'},'alternatives':alternatives,'unaffected_after':241,'words_punctuation_whitespace_changed':False}
(P/'DECISION_240_ALTERNATIVES.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
history={'authorization':'User assignment dated 2026-10-09: independently verified unambiguous Greek corrections and Latin milestones authorized in isolated IX worktree','routine_closed':[{'section':1,'decision':'Represent independently verified implicit Greek opening by accepted num mechanism','Niese_printed_page':269,'Niese_PDF_page':277,'Loeb_printed_page':2,'Loeb_PDF_page':18},{'section':181,'decision':'Move Greek marker before τρία βέλη; Latin counterpart Cumque tres sagittas','Niese_printed_page':305,'Niese_PDF_page':313,'Loeb_printed_page':96,'Loeb_PDF_page':112},{'section':216,'decision':'Move Greek marker before τὸν αὐτὸν δὲ τρόπον; Latin counterpart Eodem uero modo','Niese_printed_page':312,'Niese_PDF_page':320,'Loeb_printed_page':112,'Loeb_PDF_page':128}],'pending':[{'section':240,'packet':'DECISION_240.md','machine_packet':'DECISION_240_ALTERNATIVES.json','recommendation':'A','user_decision_received':False}],'availability_review':{'sections':'51–109','whole_section_unavailable_in_this_file':['Greek','Latin','English'],'physical_cause':'NOT_ESTABLISHED','tradition_wide_absence':'NOT_INFERRED','partial_surviving_section':110}}
(P/'EDITORIAL_HISTORY.json').write_text(json.dumps(history,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print('Recorded alternative Unicode/raw-byte cuts and recomputed adjoining extents.')
