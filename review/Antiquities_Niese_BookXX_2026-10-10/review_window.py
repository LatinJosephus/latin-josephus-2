from prepare import *
from mixed_mapper import Book
def main():
    a,z=map(int,sys.argv[1:3]);rows=json.loads((PACK/'IDENTITIES.json').read_text(encoding='utf-8'));l=Book(PACK/'frozen-inputs/Latin.xml')
    seen=[]
    for r in rows[a-1:z]:
        if r['Latin_alignment_paragraph'] not in seen:seen.append(r['Latin_alignment_paragraph'])
    for name in seen:
        u=next((u for u in l.units if u['id']==name),None)
        if u:print('\nLATIN '+name+' @'+str(u['book_start'])+'\n'+u['text'])
    for r in rows[a-1:z]:print('\nGREEK '+str(r['number'])+' '+r['Greek_paragraph']+'\n'+r['Greek_text'])
if __name__=='__main__':main()
