from reconnaissance import *
from mixed_mapper import Book

def main():
    d=packet(18); rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'))
    l=Book(raw=(d/'frozen-inputs/Latin.xml').read_bytes())
    u=next(u for u in l.units if u['id']=='latin-book18-num90')
    choices=[dict(choice=k,phrase=p,locator=l.locate(u['book_start']+u['text'].index(p))) for k,p in [('A','quod tantum per dies festos'),('B','Transacta uero festiuitate')]]
    result=dict(book=18,number=94,status='HUMAN_EDITORIAL_CHOICE_PENDING',recommendation='B',Greek=[dict(number=r['number'],text=r['Greek_text'],locator=r['Greek_locator']) for r in rows[92:95]],Latin_full_paragraph=u['text'],choices=choices,Niese=dict(printed_page=157,PDF_page=171,image='evidence/Niese-IV-PDF171.jpg',examined=True),Loeb=dict(volume='IX',edition='1965',printed_pages=[66,67],PDF_pages=[82,83],images=['evidence/Loeb-IX-PDF082.jpg','evidence/Loeb-IX-PDF083.jpg'],examined=True),reason='The Latin relative quod grammatically refers to candelabrum. Greek 93 ends with the keeper lighting a lamp daily; Greek 94 begins with the garment delivered seven days before the feast. The Latin feast-only delivery statement is attached to its candlestick account. Its following return and three-feasts-and-fast statements survive as correspondence to 94, without the Greek timing and purification particulars.',proposed_notes={'93':'The Latin expands the stored temple objects and candlestick account. Its feast-only delivery relative clause remains attached to the candlestick; the Greek distinguishes daily lamp tending at 93 from the priestly garment account at 94.','94':'The Latin interval preserves the return after the feast and the three annual festivals and fast. The preceding feast-only delivery clause is retained with the Latin candlestick account at 93. The Greek seven-day timing and purification particulars have no separate expression here; no cause of this difference is inferred.'},Greek_edit='NONE',production_applied=False)
    save(d/'CASE_094.json',result)
    out='# XVIII.94: candlestick relative clause and garment narrative\n\nStatus: pending focused editorial choice. Recommendation: **B**, before `Transacta uero festiuitate`. No production edit has been applied.\n\nNiese IV (1890), printed p.157 / PDF image171, and Loeb IX (1965), printed pp.66–67 / PDF images82–83, were visually examined. The Greek93 lamp tending is distinct from the Greek94 priestly garment delivered seven days before the feast. Loeb preserves that distinction; it does not determine the medieval Latin cut.\n\n'
    for r in result['Greek']: out+=f"Greek {r['number']}:\n\n> {r['text'].strip()}\n\n"
    begin=u['text'].index('Similiter etiam'); end=u['text'].index('Uitellius autem tunc')
    out+='Latin on both sides:\n\n> '+u['text'][begin:end]+'\n\n'
    for c in choices:
        p=c['locator']; out+=f"{c['choice']}: before `{c['phrase']}`, paragraph `{p['stable_id']}`, Unicode paragraph coordinate {p['unit_offset']}, UTF-8 file byte {p['raw_byte']}, node `{p['text_node_path']}`, node coordinate {p['node_offset']}.\n\n"
    out+='A assigns the feast-only delivery relative clause to94, but that clause refers grammatically to the candlestick in the transmitted Latin and would need an explicit cross-identity qualification. B keeps the relative clause with its antecedent in93 and begins the qualified Latin interval for94 with the surviving return-after-feast statement. B is recommended because it preserves the Latin construction and reports the limited surviving correspondence. Neither choice licenses alteration of the source or an unqualified garment/candlestick equivalence. Reciprocal notes for93 and94 are recorded in CASE_094.json.\n\nFrozen source hashes and exact locations remain in the per-book baseline and case JSON; the independent structural registry puts these sections within traditional IV.3 and provides no separate lower physical boundary at94.\n'
    (d/'CASE_094.md').write_text(out,encoding='utf8',newline='\n')
    print(json.dumps({c['choice']:{'byte':c['locator']['raw_byte'],'paragraph_coordinate':c['locator']['unit_offset']} for c in choices}))

if __name__=='__main__': main()
