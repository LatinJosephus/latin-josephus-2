from reconnaissance import *
from mixed_mapper import Book
def main():
    records=json.loads((PACK/'STRUCTURAL_RECORDS.json').read_text(encoding='utf8'));byid={r['id']:r for r in records};result=[]
    for b in [18,19]:
        models={l:Book(raw=(packet(b)/'frozen-inputs'/f'{l}.xml').read_bytes()) for l in ['Latin','Greek','English']}
        for r in records:
            f=r['fields']
            if f['book']!=str(b):continue
            languages={}
            for lang,m in models.items():
                point=f[lang];u=next(u for u in m.units if u['id']==point['paragraph']);start=u['book_start']+int(point['offset']);assert re.sub(r'\s+',' ',u['text'][int(point['offset']):].strip()).startswith(re.sub(r'\s+',' ',point['anchor'].strip())),(r['id'],lang,point)
                endrow=byid.get(f['end'])
                if endrow:
                    endp=endrow['fields'][lang];v=next(u for u in m.units if u['id']==endp['paragraph']);end=v['book_start']+int(endp['offset'])
                else:end=len(m.stream)
                assert start<end,(r['id'],lang,start,end)
                languages[lang]=dict(start=start,end=end,text=m.stream[start:end],start_locator=m.locate(start),point=point)
            result.append(dict(id=r['id'],book=b,scheme=f['scheme'],chapter=f.get('chapter'),subchapter=f.get('subchapter'),niese=f.get('canonical-niese'),label=f.get('display'),languages=languages))
        print('validated current physical locators',b,len([r for r in result if r['book']==b])*3)
    save(PACK/'EXPECTED_STRUCTURAL_RANGES.json',result)
    pairchecks=[]
    for b,trad,bam in [(18,'LOEB-18-Chapter-8-0','B78-table1-row190'),(19,'LOEB-19-Chapter-6-0','B78-table1-row198')]:
        a=next(r for r in result if r['id']==trad);z=next(r for r in result if r['id']==bam)
        for lang in ['Greek','Latin','English']:
            x=a['languages'][lang];y=z['languages'][lang];assert x['start']<y['start']
            pairchecks.append(dict(book=b,language=lang,traditional=trad,bamberg=bam,literal_label=z['label'],shared_niese=a['niese'],traditional_coordinate=x['start_locator'],bamberg_coordinate=y['start_locator'],delta=y['start']-x['start'],result='DISTINCT_PHYSICAL_POINTS_CONFIRMED_FROM_CURRENT_BYTES'))
    save(PACK/'DISTINCT_PHYSICAL_POINT_PROOF.json',pairchecks)
if __name__=='__main__':main()
