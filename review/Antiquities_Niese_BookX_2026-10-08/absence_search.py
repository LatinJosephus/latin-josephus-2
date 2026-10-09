"""Reproduce missing-passage context and whole-book lexical searches, read-only.
Search results support review; absence is a reading judgment, not a regex theorem.
"""
from pathlib import Path
import argparse,json,re,hashlib
from mixed_mapper import Book
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--packet',type=Path,required=True);a=ap.parse_args();p=a.packet
d=json.loads((p/'BASELINE.json').read_text(encoding='utf-8'));b=d['book'];assert b in [8,10]
path=a.repo/d['inputs']['Latin']['path'];raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==d['inputs']['Latin']['worktree_before_sha256']
l=Book(path);rows=json.loads((p/'BOUNDARIES.json').read_text(encoding='utf-8'));n=367 if b==8 else 108
ids=['latin-book08-num363'] if b==8 else ['latin-book10-num103','latin-book10-num108']
pattern=r'legat|domos|domus|possessio|pulchr|optim' if b==8 else r'octo|aegypt|amicit|pact|foed|tribut'
hits=[]
for u in l.units:
 for m in re.finditer(pattern,u['text'],re.I):hits.append(dict(paragraph_id=u['id'],term=m.group(),locator=l.locate(u['book_start']+m.start()),context=u['text'][max(0,m.start()-100):m.end()+180]))
context=[dict(paragraph_id=u['id'],full_narrative=u['text'],raw_paragraph_sha256=u['raw_hash'],raw_start=u['raw_start'],raw_end=u['raw_end']) for u in l.units if u['id'] in ids]
out=dict(book=b,niese=n,source_sha256=hashlib.sha256(raw).hexdigest(),status='UNAVAILABLE_IN_CANONICAL_LATIN_TRANSCRIPTION',Greek_passage=rows[n-1]['greek_section'],reason=rows[n-1]['verification_reason'],Latin_surrounding_paragraphs=context,previous_correspondence=rows[n-2],next_correspondence=rows[n],whole_book_search=dict(pattern=pattern,hits=hits),method_limit='The complete candidate reading pass and immediate narrative transition establish the missing counterpart. Lexical search checks for displacement and preserves related hits; it does not alone prove absence. No later recap or other eight-year episode is reused as this citation.',new_text_supplied=False,new_gap_created=False)
(p/'ABSENCE_SEARCH.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Missing-passage context and search written',b,n,len(hits),'related hits')
