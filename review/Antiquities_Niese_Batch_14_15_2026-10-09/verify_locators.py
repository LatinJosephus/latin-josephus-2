"""Independent lxml-node and raw UTF-8 locator verification."""
import re
from source_scope import Book
from mixed_mapper import NS,raw_char_positions
def validate(book,loc):
    path=loc['text_node_path']; tail=path.endswith('/tail()')
    base=path.rsplit('/',1)[0]
    expression=re.sub(r'(?<=/)([A-Za-z][A-Za-z0-9]*)(?=\[)',r't:\1',base)
    found=book.tree.xpath(expression,namespaces=NS)
    assert len(found)==1,(path,len(found))
    text=found[0].tail if tail else found[0].text
    char=text[loc['node_offset']]
    assert char==book.stream[loc['book_offset']],(path,char,book.stream[loc['book_offset']])
    assert raw_char_positions(book.raw,loc['raw_byte'],char)==[loc['raw_byte']]
    return True
def validate_all_nodes(book):
    for n in book.nodes:
        if n['text']:validate(book,book.locate(n['book_start']))
    return dict(nodes_verified=len(book.nodes), method='Independent lxml .text/.tail lookup, Unicode code point comparison, and raw UTF-8/entity decoder roundtrip')
