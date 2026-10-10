"""Create unreviewed identity windows from frozen bytes, physical endpoints explicit."""
from pathlib import Path
import json,re,sys
sys.dont_write_bytecode=True
from mixed_mapper import Book,digest
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
def save(name,x):(D/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def models():return {lang:Book(D/'inputs'/f'{lang}.xml') for lang in ['Greek','Latin','English']}
def prepare():
    assert not (D/'CANDIDATE_REGISTER.json').exists()
    bs=models();g=bs['Greek'];labels=[x for x in g.labels if re.fullmatch(r'\[\d+\]',x['text'])]
    nums=[int(x['text'][1:-1]) for x in labels];assert sorted(nums)==list(range(2,348))
    physical=[dict(number=1,book_offset=0,implicit=True)]+[dict(number=int(x['text'][1:-1]),book_offset=x['book_offset'],label=x) for x in labels]
    rows=[]
    for i,x in enumerate(physical):
        start=x['book_offset'];end=physical[i+1]['book_offset'] if i+1<len(physical) else len(g.stream)
        at=g.first_content(start);loc=g.locate(at);u=g.units[loc['paragraph']-1];target=u['element'].get('sameAs','').lstrip('#')
        lu=next((z for z in bs['Latin'].units if z['id']==target),None)
        rows.append(dict(number=x['number'],Greek=dict(start=loc,end=g.locate(end) if end<len(g.stream) else dict(book_offset=end,kind='book-end'),
            raw_label=x.get('label'),text=g.stream[start:end],print_status='UNREVIEWED',word_interpretation='INHERITED_CANDIDATE'),
            Latin=dict(alignment_window=target,window_hash=lu['raw_hash'] if lu else None,review_status='UNREVIEWED',fragments=[]),
            physical_locator_status='MACHINE_VALIDATED_ONLY',editorial_status='UNREVIEWED',implementation_approved=False))
    rows.sort(key=lambda x:x['number']);save('CANDIDATE_REGISTER.json',rows)
    save('PHYSICAL_ORDER.json',{lang:dict(paragraphs=[u['id'] for u in b.units],labels=[dict(label=x['text'],paragraph=x['id'],offset=x['book_offset']) for x in b.labels]) for lang,b in bs.items()})
    print('347 candidate identities; physical Greek order explicitly retained; no review promoted.')
def show(a,z):
    rows=json.loads((D/'CANDIDATE_REGISTER.json').read_text(encoding='utf8'));bs=models();seen=set()
    for r in rows[a-1:z]:
        print(f'GREEK XI.{r["number"]}: {r["Greek"]["text"].strip()}')
        t=r['Latin']['alignment_window']
        if t not in seen:
            seen.add(t);u=next((u for u in bs['Latin'].units if u['id']==t),None)
            print(f'LATIN {t}: {u["text"] if u else "NO TARGET"}')
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    else:show(int(sys.argv[2]),int(sys.argv[3]))
