from reconnaissance import *
from mixed_mapper import Book
def main():
    d=packet(18);rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'));l=Book(raw=(d/'frozen-inputs/Latin.xml').read_bytes());u=next(u for u in l.units if u['id']=='latin-book18-num1')
    choices=[]
    for key,phrase in [('A','et supra quam dici potest'),('B','illa gens continuationibus')]:
        loc=l.locate(u['book_start']+u['text'].index(phrase));choices.append(dict(choice=key,phrase=phrase,locator=loc))
    result=dict(book=18,number=7,status='HUMAN_EDITORIAL_CHOICE_PENDING',recommendation='A',Greek=[dict(number=r['number'],text=r['Greek_text'],locator=r['Greek_locator']) for r in rows[5:8]],Latin_full_paragraph=u['text'],choices=choices,Niese=dict(printed_page=141,PDF_page=155,image='evidence/Niese-IV-PDF155.jpg',examined=True),reason='The Latin fuses the end of Greek 6 (unbounded evils filling the nation) with the war list opening 7. A retains the complete Latin introductory clause with 7; B preserves the adverbial phrase under 6 but separates it from its Latin subject and predicate. Neither yields unqualified exact correspondence.',proposed_notes={'6':'The Latin summarizes the developing calamities; the shared nation-and-war clause continues in the Latin interval for 7.','7':'This Latin interval begins with a shared introductory summary corresponding partly to the end of Greek 6, then presents the wars and plundering corresponding to 7.'},Greek_edit='NONE',production_applied=False)
    save(d/'CASE_007.json',result)
    text='# XVIII.7: shared Latin summary clause\n\nStatus: pending focused editorial choice. Recommendation: **A**, before `et supra quam dici potest`. No production edit has been applied.\n\nNiese IV (1890), printed p.141 / PDF image155, was visually examined. The print distinguishes 6 and7; the Greek end of6 describes evils beyond telling filling the nation, while7 continues with wars, deprivation, plunder and murder. The print does not adjudicate the different Latin construction.\n\n'
    for r in result['Greek']:text+=f"Greek {r['number']}:\n\n> {r['text'].strip()}\n\n"
    begin=u['text'].index('Nihilque');end=u['text'].index('Multae itaque')
    text+='Latin on both sides:\n\n> '+u['text'][begin:end]+'\n\n'
    for c in choices:
        p=c['locator'];text+=f"{c['choice']}: before `{c['phrase']}`, paragraph `{p['stable_id']}`, Unicode paragraph coordinate {p['unit_offset']}, UTF-8 file byte {p['raw_byte']}, node `{p['text_node_path']}`, node coordinate {p['node_offset']}.\n\n"
    text+='A keeps the Latin clause together and represents its shared correspondence explicitly with reciprocal notes at6 and7. B leaves `et supra quam dici potest` at the end of6 and begins7 with the nation-and-wars predicate. Both preserve every source character. A is recommended because it provides a coherent Latin opening and describes the overlapping correspondence rather than implying word-for-word equivalence. No omission or cause of loss is inferred.\n\nThe independent Loeb structural records put both citations within traditional I.1; they supply no separate physical lower division at7 and cannot resolve this Latin cut. Frozen Greek/Latin hashes, all coordinates and both proposals remain in CASE_007.json.\n'
    (d/'CASE_007.md').write_text(text,encoding='utf8',newline='\n')
    print(json.dumps({c['choice']:{'byte':c['locator']['raw_byte'],'paragraph_coordinate':c['locator']['unit_offset']} for c in choices}))
if __name__=='__main__':main()
