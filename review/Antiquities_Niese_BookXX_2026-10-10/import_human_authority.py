from prepare import *
import zipfile
tree=etree.fromstring((PACK/'frozen-inputs/structure.xml').read_bytes());records=[]
for item in tree.xpath('//t:item',namespaces=NS):
    node=item.find('t:note[@type="frozen-bamberg-evidence"]/t:p',NS)
    if node is None:continue
    r=json.loads(node.text)
    if r.get('book')==20:records.append(r)
assert len(records)==20
source=Path(records[0]['source_audit_file']);assert all(r['source_audit_file']==str(source) for r in records)
source_info=info(source);matches=all(r['source_audit_sha256']==source_info['sha256'] for r in records)
with zipfile.ZipFile(source) as z:doc=etree.fromstring(z.read('word/document.xml'))
w={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};table=doc.findall('.//w:tbl',w)[0];wordrows=table.findall('w:tr',w)
for r in records:
    row=wordrows[r['source_audit_row']-1]
    r['later_Word_row_cells_observation']=[''.join(c.itertext()) for c in row.findall('w:tc',w)]
save(PACK/'HUMAN_BAMBERG_AUTHORITY_BOOKXX.json',dict(current_external_source=source_info,current_docx_hash_matches_frozen_records=matches,frozen_hashes=sorted({r['source_audit_sha256'] for r in records}),records=records,precedence='FROZEN v1.1 records retain authority. The current external Word file differs from the frozen hash and is a later observation only, not a replacement authority. Existing human checks and current-text offsets remain protected; no fresh facsimile inspection is claimed.'))
print('Current Word hash matches frozen:',matches,source_info['sha256'])
print([(r['row'],r['numeral'],r['later_Word_row_cells_observation'][:3]) for r in records])
