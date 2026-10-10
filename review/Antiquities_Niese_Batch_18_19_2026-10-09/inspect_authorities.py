from reconnaissance import *
for p in [RECOVERY/'Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06/Antiquities_Structure_Reconciliation.json',RECOVERY/'Antiquities_Loeb_Niese_Verification_2026-10-05/consolidated/Antiquities_Loeb_Niese_I-XX.json']:
    j=json.loads(p.read_text(encoding='utf8'))
    print(p,[(k,type(v).__name__,len(v) if isinstance(v,(dict,list)) else None) for k,v in j.items()])
    for k,v in j.items():
        if isinstance(v,list) and v:print('SAMPLE',k,json.dumps(v[0],ensure_ascii=False)[:2200])
        elif isinstance(v,dict):print('DICT KEYS',k,list(v.keys())[:30])
for lang in ['Greek','Latin','English']:
    doc=etree.parse(str(ROOT/f'assets/xml/antiquities/{lang}/book-19.xml'))
    print(lang)
    for e in doc.xpath('//t:div2',namespaces=NS):
        if e.get('n')=='0':print(etree.tostring(e,encoding='unicode'))
    print('NESTED',[(etree.QName(e).localname,doc.getpath(e),dict(e.attrib),''.join(e.itertext())) for e in doc.xpath('//t:argument|//t:floatingText|//t:note',namespaces=NS)])
