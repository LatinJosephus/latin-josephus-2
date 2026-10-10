"""Verify frozen research and all independent current physical locators."""
from reconnaissance import *
from mixed_mapper import Book
def fs_record(fs):
    result={}
    for f in fs.findall('t:f',NS):
        nested=f.find('t:fs',NS)
        result[f.get('name')]=fs_record(nested) if nested is not None else ''.join(f.itertext()).strip()
    return result
def main():
    checks=[]
    for dirname,manifest in [('Antiquities_Loeb_Structure_2026-10-04','Antiquities_Loeb_Structure_SHA256SUMS.txt'),('Antiquities_Loeb_Niese_Verification_2026-10-05','Antiquities_Loeb_Niese_Verification_SHA256SUMS.txt'),('Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06','Antiquities_Structure_Reconciliation_v1.1_SHA256SUMS.txt')]:
        directory=RECOVERY/dirname;entries=[]
        for line in (directory/manifest).read_text(encoding='utf8').splitlines():
            m=re.match(r'^([0-9a-f]{64})\s+\*?(.+)$',line)
            if m:
                p=directory/m[2];actual=sha(p.read_bytes());entries.append(dict(relative=m[2],expected=m[1],actual=actual,match=actual==m[1]));assert actual==m[1],p
        checks.append(dict(authority=dirname,manifest=info(directory/manifest),entries=entries,status='PASS'))
    save(PACK/'AUTHORITY_INTEGRITY.json',checks)
    r=json.loads((RECOVERY/'Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06/Antiquities_Structure_Reconciliation.json').read_text(encoding='utf8'))
    v=json.loads((RECOVERY/'Antiquities_Loeb_Niese_Verification_2026-10-05/consolidated/Antiquities_Loeb_Niese_I-XX.json').read_text(encoding='utf8'))
    romans={18:'XVIII',19:'XIX'}
    def mentions(x,b):
        if isinstance(x,list):return any(mentions(z,b) for z in x)
        if not isinstance(x,dict):return False
        for k,z in x.items():
            if k in ['antiquities_books','books'] and isinstance(z,list) and any(str(n) in [str(b),romans[b]] for n in z):return True
            if k in ['book','book_number','antiquities_book'] and str(z) in [str(b),romans[b]]:return True
            if k in ['loeb_boundary_id','case','boundary_id','loeb_id'] and isinstance(z,str) and (z.startswith(romans[b]+'.') or z.startswith(f'LOEB-{b:02}-')):return True
            if k in ['book_or_range','book_or_books'] and str(z) in [str(b),romans[b],'XVI–XX','XVI-XX','XVI–XIX','XVIII–XX']:return True
            if isinstance(z,(dict,list)) and mentions(z,b):return True
        return False
    def scoped(x,b):
        if isinstance(x,list):return [z for z in x if mentions(z,b)]
        return dict(scope='SHARED_AUTHORITY_METADATA_NOT_BOOK_FILTERED',value=x)
    extracts=[]
    for b in [18,19]:
        er={k:scoped(x,b) for k,x in r.items() if isinstance(x,(dict,list))}
        er['loeb_book_headings']=[r['loeb_book_headings'][b-1]]
        ev={k:scoped(x,b) for k,x in v.items() if isinstance(x,(dict,list))}
        assert len(er['loeb_boundaries'])=={18:66,19:61}[b]
        assert len(ev['audited_boundaries'])=={18:66,19:61}[b]
        assert len(er['bamberg_boundaries'])=={18:19,19:8}[b]
        save(packet(b)/'FROZEN_RECONCILIATION_RECORDS.json',er)
        save(packet(b)/'FROZEN_VERIFICATION_RECORDS.json',ev)
        extracts.append(dict(book=b,reconciliation_counts={k:len(x) for k,x in er.items() if isinstance(x,list)},verification_counts={k:len(x) for k,x in ev.items() if isinstance(x,list)},extraction_policy='Nested source.book, antiquities_book, Roman boundary IDs and source-only book/range observations are inspected; complete matching records retained unchanged. Shared metadata explicitly labelled.',supersedes='Initial top-level-only extract omitted nested records and combined book18/19 rows. Frozen originals and hashes were unchanged.'))
    save(PACK/'AUTHORITY_EXTRACTION_QA.json',extracts)
    doc=etree.parse(str(ROOT/'assets/xml/antiquities/structure.xml'));records=[]
    for item in doc.xpath('//t:list[@type="traditional-boundaries" or @type="bamberg-boundaries"]/t:item',namespaces=NS):
        fs=item.find('t:fs',NS);f=fs_record(fs)
        if f.get('book') not in ['18','19']:continue
        records.append(dict(id=item.get(ID),fields=f))
    save(PACK/'STRUCTURAL_RECORDS.json',records)
    for b in [18,19]:
        local=[r for r in records if r['fields']['book']==str(b)]
        save(packet(b)/'STRUCTURAL_RECORDS.json',local)
        print(b,'registry rows',len(local),'schemes',{s:sum(r['fields']['scheme']==s for r in local) for s in ['chapter','subchapter','bamberg']})
        print('opening',json.dumps(next(r for r in local if r['fields'].get('scheme')=='chapter'),ensure_ascii=False))
    for b,n in [(18,'257'),(19,'292')]:
        for r in records:
            if r['fields']['book']==str(b) and r['fields'].get('canonical-niese')==n and r['fields'].get('scheme') in ['chapter','bamberg']:print(json.dumps(r,ensure_ascii=False))
    print('Frozen research hashes all verified; no current locator is yet claimed browser-certified.')
if __name__=='__main__':main()
