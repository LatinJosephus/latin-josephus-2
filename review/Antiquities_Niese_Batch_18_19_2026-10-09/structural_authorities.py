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
    def scoped(x):
        if isinstance(x,list):return [z for z in x if isinstance(z,dict) and str(z.get('book',z.get('book_number',''))) in ['18','19','XVIII','XIX']]
        return x
    for b in [18,19]:
        save(packet(b)/'FROZEN_RECONCILIATION_RECORDS.json',{k:scoped(r[k]) for k in ['bamberg_boundaries','loeb_boundaries','chapter_concordance','same_niese_different_position_pairs','current_xml_structures','bamberg_coverage']})
        save(packet(b)/'FROZEN_VERIFICATION_RECORDS.json',{k:scoped(v[k]) for k in ['audited_boundaries','exceptions','significant_and_typographical_variants','structural_observations','physical_inspection_register','frozen_records','human_physical_copy_checks']})
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
