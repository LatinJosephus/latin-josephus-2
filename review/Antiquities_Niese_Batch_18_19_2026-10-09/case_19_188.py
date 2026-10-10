from reconnaissance import *
from mixed_mapper import Book

def main():
    d=packet(19); rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'))
    l=Book(raw=(d/'frozen-inputs/Latin.xml').read_bytes())
    u=next(u for u in l.units if u['id']=='latin-book19-num185')
    choices=[dict(choice=k,phrase=p,locator=l.locate(u['book_start']+u['text'].index(p))) for k,p in [('A','Erant enim cohortes'),('B','qui senatui consentiebant')]]
    result=dict(book=19,number=188,status='HUMAN_EDITORIAL_CHOICE_PENDING',recommendation='A',Greek=[dict(number=r['number'],text=r['Greek_text'],locator=r['Greek_locator']) for r in rows[185:189]],Latin_full_paragraph=u['text'],choices=choices,Niese=dict(printed_pages=[242,243],PDF_pages=[256,257],images=['evidence/Niese-IV-PDF256.jpg','evidence/Niese-IV-PDF257.jpg'],examined=True),reason='Greek 187 describes the restored consular command. Greek 188 begins with Chaerea taking and distributing the sign to soldiers aligned with the Senate, then the four cohorts. Latin omits a distinct sign-distribution statement. Its qui senatui consentiebant relative has the consuls of the prior sentence as grammatical antecedent, but the allegiance theme corresponds to Greek 188.',proposed_notes={'187':'The Latin has no independent hundred-year dating and keeps its qui senatui consentiebant relative with the prior consuls. The allegiance theme overlaps the following Greek section 188.','188':'The Latin interval begins with the surviving four-cohort account. The earlier qui senatui consentiebant relative remains grammatically with the consuls in 187, although its allegiance theme corresponds to Greek 188. No distinct statement of Chaerea taking and distributing the sign is present at this join; no cause of the difference is inferred.'},Greek_edit='NONE',production_applied=False)
    save(d/'CASE_188.json',result)
    out='# XIX.188: Senate allegiance relative and four cohorts\n\nPending specific human editorial choice. Recommendation: **A**, before `Erant enim cohortes`. No production edit applied.\n\nNiese IV (1890), printed pp.242–243 / PDF images256–257, visually examined. The printed division at188 precedes Chaerea taking and distributing the sign; the Latin join has no distinct distribution statement. Both choices preserve every source character and the separate structural division records.\n\n'
    for r in result['Greek']:out+=f"Greek {r['number']}:\n\n> {r['text'].strip()}\n\n"
    out+='Full Latin alignment paragraph:\n\n> '+u['text']+'\n\n'
    for c in choices:
        p=c['locator'];out+=f"{c['choice']}: before `{c['phrase']}`, paragraph `{p['stable_id']}`, Unicode paragraph coordinate {p['unit_offset']}, UTF-8 byte {p['raw_byte']}, node `{p['text_node_path']}`, node coordinate {p['node_offset']}.\n\n"
    out+='A keeps the Latin relative with the consuls and begins188 at the independently surviving four-cohort account. Reciprocal notes report the allegiance-theme overlap and the missing distinct sign-distribution statement. B begins188 with the allegiance relative to reflect its Greek thematic counterpart, but separates the Latin relative from its consular antecedent. A is recommended because it preserves the transmitted syntax and limits the independent interval claim. Neither alternative licenses reconstruction or unqualified equivalence.\n\nAuthority and source hashes remain in the baseline ledger; exact candidate locators and the entire paragraph are in CASE_188.json.\n'
    (d/'CASE_188.md').write_text(out,encoding='utf8',newline='\n')
    print(json.dumps({c['choice']:{'byte':c['locator']['raw_byte'],'paragraph_coordinate':c['locator']['unit_offset']} for c in choices}))
if __name__=='__main__':main()
