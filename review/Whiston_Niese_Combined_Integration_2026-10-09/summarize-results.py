from pathlib import Path
import json
P=Path(__file__).resolve().parent
for f in ['BAMBERG_BROWSER_QA.json','NEW_BOOK_BROWSER_QA.json','UI_SUPPLEMENT_QA.json','ALIGNMENT_ALL_QA.json','XI_MULTISPAN_GATE_QA.json','PROTECTED_SOURCE_GATE_QA.json','LAYOUT_QA.json','BAMBERG_RANGE_QA.json']:
 d=json.loads((P/f).read_text());print(f,{k:v for k,v in d.items() if not isinstance(v,(list,dict))});
 if f=='NEW_BOOK_BROWSER_QA.json':print('books',d['books'])
 if f=='PROTECTED_SOURCE_GATE_QA.json':print('citation counts',[(x['book'],x['source'],x['niese']) for x in d['checks']])
print('Greek displayed counts',[(x['book'],x['width'],x['theme']) for x in json.loads((P/'INTERACTION_QA.json').read_text())['checks'][:8]])
for folder in ['Whiston_Antiquities_Compiled_Index_2026-10-09','Antiquities_Niese_Implementation_08_10_2026-10-09','Antiquities_Niese_Integration_08_10_2026-10-09']:
 d=json.loads((P.parent/folder/'FILE_MANIFEST.json').read_text());print(folder,list(d),next(iter(d.get('entries',d.get('files',[]))),None))
