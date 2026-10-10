"""Display frozen candidates and independently source-qualified structural records."""
from reconnaissance import *
def structural():
    doc=etree.parse(str(ROOT/'assets/xml/antiquities/structure.xml'))
    result=[]
    for item in doc.xpath('//t:list[@type="traditional-boundaries" or @type="bamberg-boundaries"]/t:item',namespaces=NS):
        fields={f.get('name'):''.join(f.itertext()).strip() for f in item.xpath('./t:fs/t:f',namespaces=NS)}
        if fields.get('book') not in ['18','19']:continue
        result.append(dict(id=item.get(ID),fields=fields,locators=[etree.tostring(e,encoding='unicode') for e in item.xpath('.//t:ptr|.//t:span',namespaces=NS)]))
    save(PACK/'STRUCTURAL_RECORDS.json',result)
    for r in result:
        if r['fields'].get('scheme')=='chapter' or r['id'].startswith('B78'):
            print(json.dumps(r,ensure_ascii=False))
def candidates(b,a,z):
    rows=json.loads((packet(b)/'IDENTITIES.json').read_text(encoding='utf8'))
    seen=set()
    for r in rows[a-1:z]:
        print(f"{b}.{r['number']} {r['Greek_paragraph']}\nG: {r['Greek_text']}")
        if r['Latin_alignment_paragraph'] not in seen:
            print(f"L [{r['Latin_alignment_paragraph']}]: {r['Latin_alignment_text']}")
            seen.add(r['Latin_alignment_paragraph'])
if __name__=='__main__':
    if sys.argv[1]=='structure':structural()
    else:candidates(*map(int,sys.argv[1:]))
