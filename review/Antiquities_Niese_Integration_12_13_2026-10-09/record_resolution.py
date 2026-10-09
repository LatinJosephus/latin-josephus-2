"""Verify the merged renderer equals current canonical plus precisely certified reader additions."""
from preflight import *
canonical=git(ROOT,'show',f'{START}:assets/js/renderTei.js')
expected=canonical
changes=[
    (b'        10: "assets/xml/antiquities/niese/book-10.json"',b'        10: "assets/xml/antiquities/niese/book-10.json",\n        12: "assets/xml/antiquities/niese/book-12.json",\n        13: "assets/xml/antiquities/niese/book-13.json"'),
    (b'        if (!marker.closest("tei-body") || !marker.closest("tei-p[id]")',b'        // Certified milestones can locate an anonymous transmitted paragraph.\n        if (!marker.closest("tei-body") || !marker.closest("tei-p")'),
    (b'    const end = entries[index + 1] || null;\n    const book = start.node.closest("tei-div1")',b'    // An explicit narrative end can precede a preserved book subscription.\n    const terminal = language === "Latin"\n      ? data.querySelector(\'tei-milestone[unit="niese-end"]\') : null;\n    const end = entries[index + 1] || (terminal ? {node: terminal, kind: "end"} : null);\n    const book = start.node.closest("tei-div1")')]
for index,(old,new) in enumerate(changes):
    if index==2:
        at=expected.index(b'  const antiquitiesNieseExactView =')
        before,scoped=expected[:at],expected[at:]
        assert scoped.count(old)==1,old
        expected=before+scoped.replace(old,new,1)
    else:
        assert expected.count(old)==1,old
        expected=expected.replace(old,new,1)
actual=(ROOT/'assets/js/renderTei.js').read_bytes()
assert actual==expected
for item in read(PACK/'INCOMING_SCOPE.json')['production']:
    if item['path']=='assets/js/renderTei.js': continue
    assert (ROOT/item['path']).read_bytes()==git(ROOT,'show',f'{TIP}:{item["path"]}')
save('PRODUCTION_RESOLUTION.json',{'starting_canonical':START,'certified_tip':TIP,'manual_conflicts':1,
    'conflict_path':'assets/js/renderTei.js','conflict_region':'Antiquities nieseIdentityBooks map',
    'resolution':'Keep canonical IX entry and certified XII/XIII entries alongside VIII/X',
    'automatically_combined_certified_changes':['Explicit Niese milestones can locate the existing anonymous XIII paragraph','Explicit niese-end bounds the final XII selection before the preserved subscription'],
    'canonical_reader_changes_preserved':['IX availability and identity registry','Registry-defined excluded narrative paragraphs','Unavailable language exact view before context fallback'],
    'validation':'Merged renderer byte-equals current canonical blob plus exactly the three recorded certified additions; all six incoming corpus/registry blobs equal the certified tip',
    'canonical_renderer_sha256':sha(canonical),'certified_renderer_sha256':sha(git(ROOT,'show',f'{TIP}:assets/js/renderTei.js')),
    'merged_renderer_sha256':sha(actual),'narrative_or_editorial_changes':False,'result':'PASS'})
print('PASS single identity-map conflict resolved; exact canonical-plus-certified renderer verified')
