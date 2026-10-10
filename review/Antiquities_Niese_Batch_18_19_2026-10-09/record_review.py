"""Persist explicitly supplied human-readable source observations; never infer approval."""
from reconnaissance import *
sys.path.insert(0,str(PACK))
from mixed_mapper import Book
def record(b,name):
    d=packet(b);rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'))
    source=Book(raw=(d/'frozen-inputs/Latin.xml').read_bytes())
    entries=json.loads((d/name).read_text(encoding='utf8'))
    history=[]
    for n,para,phrase,page,status,reason,note in entries:
        r=rows[n-1];u=next(u for u in source.units if u['id']==para)
        assert u['text'].count(phrase)==1,(n,para,phrase)
        k=u['book_start']+u['text'].index(phrase);loc=source.locate(k)
        label=next((l for l in source.labels if l['unit']==u['index'] and int(re.findall(r'\d+',l['text'])[-1])==n),None)
        candidate=dict(locator=loc,incipit=phrase,correspondence=status,reason=reason,note=note,retained_label=label,approved=status!='EDITORIAL_DECISION_PENDING')
        r.update(candidate=candidate,Latin_review_status='INDIVIDUALLY_REVIEWED_CANDIDATE',print_review_status='VISUALLY_REVIEWED',print_evidence=dict(edition='Niese IV, 1890',printed_page=page-14,PDF_page=page,image=f'evidence/Niese-IV-PDF{page:03}.jpg',visible_numeral= str(n) if n!=1 else 'Implicit first section at printed I.1 narrative opening',observation='Marginal identity and neighbouring printed Greek examined; printed line distinguished from exact XML word coordinate. Existing Greek text retained.'))
        history.append(dict(number=n,candidate=candidate,print_evidence=r['print_evidence'],reader_certified=False))
    save(d/'IDENTITIES.json',rows)
    prior=json.loads((d/'DECISION_HISTORY.json').read_text(encoding='utf8')) if (d/'DECISION_HISTORY.json').exists() else []
    prior.append(dict(kind='INDIVIDUAL_REVIEW_BATCH',input=name,observations=history));save(d/'DECISION_HISTORY.json',prior)
    print(b,'individually examined candidates',sum(r['candidate'] is not None for r in rows),'/',len(rows))
if __name__=='__main__':record(int(sys.argv[1]),sys.argv[2])
