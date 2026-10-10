import sys
sys.dont_write_bytecode=True
from integration_common import *
authority=ROOT/'review/Antiquities_Niese_BookXI_2026-10-09'
sys.path.insert(0,str(authority))
from mixed_mapper import Book
b=Book(authority/'inputs/Latin.xml');ledger=read(authority/'LATIN_PHYSICAL_COVERAGE.json')
assert ''.join(f['text'] for f in ledger)==b.stream
save('XI_WITNESS_EXPECTATION.json',dict(source_sha256=sha(b.raw),physical_narrative=b.stream,physical_occurrences=[f['occurrence'] for f in ledger],units={u['id']:u['text'] for u in b.units}))
