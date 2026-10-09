"""Record inspected narrative endings against frozen DOM and raw UTF-8 bytes."""
from pathlib import Path
import json
from source_scope import Book,digest
from verify_locators import validate
ROOT=Path(__file__).resolve().parents[2]
for b,roman,n,page,last in [(14,'XIV',491,402,'Nos igitur hunc terminum cognationis a samoneorum accepimus.'),(15,'XV',425,481,'Templum quidem huiusmodi constitutione finitum est.')]:
 p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
 l=Book(raw=(p/'frozen-inputs/Latin.xml').read_bytes());g=Book(raw=(p/'frozen-inputs/Greek.xml').read_bytes())
 assert l.stream.endswith(last)
 loc=l.locate(len(l.stream)-1);validate(l,loc)
 assert l.raw[loc['raw_byte']:loc['raw_byte']+1]==b'.'
 data=dict(book=b,number=n,status='INDEPENDENTLY_REVIEWED_NARRATIVE_END',last_narrative_character_locator=loc,
  exclusive_Unicode_end=len(l.stream),exclusive_raw_UTF8_end=loc['raw_byte']+1,
  terminal_sentence=last,Latin_source_sha256=digest(l.raw),Greek_source_sha256=digest(g.raw),
  edition='Niese III (1892)',printed_page=page-72,pdf_page=page,image=f'evidence/Niese-III-PDF{page}.jpg',image_inspected=True,
  finding='The complete final Greek section and Latin concluding sentence have been individually compared. Closing XML containers and any source subscriptions or apparatus are outside this narrative coordinate stream.',
  narrative_words_changed=False,following_book_outside_extent=True,full_book_partition_certified=False)
 (p/'TERMINAL_EXTENT.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 print(b,'terminal Unicode extent',len(l.stream),'raw exclusive end',loc['raw_byte']+1)
