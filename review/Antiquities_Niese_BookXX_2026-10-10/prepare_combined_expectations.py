"""Independent frozen-source expectations for the editor's four combined case groups."""
from prepare import *
from mixed_mapper import Book
rows=json.loads((PACK/'IDENTITIES.json').read_text(encoding='utf-8'))
expected=json.loads((PACK/'FINAL_EXPECTED_INTERVALS.json').read_text(encoding='utf-8'))
latin=Book(PACK/'frozen-inputs/Latin.xml');greek=Book(PACK/'frozen-inputs/Greek.xml')
groups=[]
for first,last in [(25,38),(57,60),(237,240),(239,242)]:
    members=expected[first-1:last];available=[e for e in members if not e['unavailable']]
    a=available[0]['start'];z=available[-1]['end'];source=latin.stream[a:z]
    annotation='[Niese sections 26–37 largely missing; cf. Blatt, p. 68] '
    assigned=''.join(e['Latin'] for e in available)
    assert source==(assigned if first!=25 else assigned[:expected[25]['end']-a]+annotation+assigned[expected[25]['end']-a:])
    g=greek.stream[rows[first-1]['Greek_start']:rows[last-1]['Greek_end']]
    assert g==''.join(e['Greek'] for e in members)
    groups.append(dict(first=first,last=last,members=[e['number'] for e in members],unavailable=[e['number'] for e in members if e['unavailable']],Greek=g,Latin_physical_source=source,Latin_independent_fragments=assigned,source_only_annotation=annotation if first==25 else '',Latin_original_extent=[a,z],Latin_original_start=latin.locate(a),Latin_original_end=latin.locate(z),English_context_by_identity={str(e['number']):e['English'] for e in members}))
save(PACK/'COMBINED_EXPECTED_INTERVALS.json',groups)
print('Independent frozen-source full text prepared for all four combined case groups.')
