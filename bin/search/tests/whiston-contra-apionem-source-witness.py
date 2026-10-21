#!/usr/bin/env python3
"""Independent Whiston Contra Apionem witness; no extractor imports.

The two accepted XML files encode every Niese unit as a paragraph with its own
number and xml:id. Chapter and Whiston-section milestones preserve separate
division systems. In II.109 and II.112, a Whiston milestone occurs inside the
Niese paragraph; its following text belongs to that same paragraph.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import unicodedata
from xml.dom import Node, minidom

TEI = 'http://www.tei-c.org/ns/1.0'
COLLECTION = 'contra-apionem-english-whiston'
SOURCE_COMMIT = 'd626d119aa0eaf3e2dc9d8e50b232e7163a8f8bc'
SPECS = [
    (1, 320, 18497, 35, 35, '2c7731cf1eb2f4b70ff2177ef192b7b0452bf2871de023ab405ec83b60f6125a'),
    (2, 296, 18356, 41, 42, '12d006e8e0b296f84f5ef50ae7aa50c781ffe1b8821def5840e82cd317a7b467'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def all_text(node):
    if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
        return node.data
    return ''.join(all_text(child) for child in node.childNodes)


def u16(text):
    return len(text.encode('utf-16-le')) // 2


def scan_words(text):
    """Unicode category scan independent of the engine's regular expression."""
    result, start, start_offset, offset = [], None, None, 0
    for index in range(len(text) + 1):
        char = text[index] if index < len(text) else ' '
        category = unicodedata.category(char)[0]
        if start is not None and category not in 'LMN':
            term = unicodedata.normalize('NFC', text[start:index]).lower().replace('ς', 'σ')
            result.append({'term': unicodedata.normalize('NFC', term), 'start': start_offset, 'end': offset})
            start = start_offset = None
        if start is None and category in 'LN':
            start, start_offset = index, offset
        offset += u16(char)
    return result


def attributes(element):
    return dict(element.attributes.items())


def children(element):
    elements = []
    for child in element.childNodes:
        if child.nodeType == Node.ELEMENT_NODE:
            elements.append(child)
        else:
            assert child.nodeType == Node.TEXT_NODE and not child.data.strip(), ('Unexpected structural text', child)
    return elements


def marker_attributes(node):
    attrs = attributes(node)
    unit = attrs.get('unit')
    assert node.localName == 'milestone' and not node.childNodes
    assert unit in {'chapter', 'whiston-section'}
    assert attrs.get('n', '').isdecimal() and int(attrs['n']) > 0
    expected = {'unit': unit, 'n': attrs['n']}
    if unit == 'chapter':
        expected['subtype'] = 'niese'
    assert attrs == expected
    return attrs


def extract_source(root, spec, order):
    book, expected_sections, expected_tokens, expected_chapters, expected_whiston, fingerprint = spec
    source_path = f'assets/xml/contra-apionem/English/book-{book:02}.xml'
    raw = (root / source_path).read_bytes()
    lf = raw.replace(b'\r\n', b'\n')
    assert b'\r' not in lf and sha(lf) == fingerprint, ('Unaccepted Contra Apionem Whiston source', source_path)
    assert b'<!DOCTYPE' not in raw.upper() and b'<!ENTITY' not in raw.upper()
    dom = minidom.parseString(raw)
    assert dom.documentElement.namespaceURI == TEI
    elements = list(dom.getElementsByTagName('*'))
    assert all(element.namespaceURI == TEI for element in elements)
    ids = [element.getAttribute('xml:id') for element in elements if element.hasAttribute('xml:id')]
    assert len(ids) == len(set(ids))
    texts = dom.getElementsByTagName('text')
    assert len(texts) == 1 and attributes(texts[0]) == {'xml:lang': 'eng'}
    bodies = dom.getElementsByTagName('body')
    assert len(bodies) == 1 and attributes(bodies[0]) == {}
    body = bodies[0]
    counts = Counter([body.localName, *(node.localName for node in body.getElementsByTagName('*'))])
    assert set(counts) == {'body', 'div1', 'p', 'milestone'}, counts
    book_divisions = children(body)
    assert len(book_divisions) == 1
    division = book_divisions[0]
    assert division.localName == 'div1' and attributes(division) == {
        'type': 'book', 'n': str(book), 'xml:id': f'english-apion{book}'}
    rows, paragraphs, chapters, direct_markers, all_markers = [], [], [], [], []
    current_chapter = current_whiston = previous_section = None
    for element_index, node in enumerate(children(division)):
        if node.localName == 'milestone':
            attrs = marker_attributes(node)
            unit, number = attrs['unit'], int(attrs['n'])
            marker = {'unit': unit, 'number': number, 'sourceAttributes': attrs,
                      'bookChildIndex': element_index, 'previousSection': previous_section,
                      'beforeSection': (previous_section or 0) + 1}
            direct_markers.append(marker)
            all_markers.append({**marker, 'location': 'between-paragraphs'})
            if unit == 'chapter':
                current_chapter = number
                chapters.append({'chapter': number, 'attributes': attrs, 'sections': []})
            else:
                current_whiston = number
            continue
        assert node.localName == 'p'
        section = int(node.getAttribute('n'))
        source_id = f'english-apion{book}-num{section}'
        assert attributes(node) == {'n': str(section), 'xml:id': source_id}
        assert section == (previous_section or 0) + 1
        assert current_chapter and current_whiston
        start_whiston = current_whiston
        offset, segments, inside_markers = 0, [], []
        for child in node.childNodes:
            if child.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                end = offset + u16(child.data)
                segments.append({'sourceId': source_id, 'rawStart': offset, 'rawEnd': end,
                                 'start': offset, 'end': end, 'text': child.data})
                offset = end
            else:
                assert child.nodeType == Node.ELEMENT_NODE
                attrs = marker_attributes(child)
                assert attrs['unit'] == 'whiston-section'
                marker = {'unit': attrs['unit'], 'number': int(attrs['n']),
                          'sourceTextOffset': offset, 'sourceAttributes': attrs}
                inside_markers.append(marker)
                all_markers.append({**marker, 'location': 'inside-paragraph',
                                    'sourceId': source_id, 'section': section})
                current_whiston = int(attrs['n'])
        text = all_text(node)
        assert text and text == text.strip()
        assert ''.join(segment['text'] for segment in segments) == text
        assert offset == u16(text)
        tokens = scan_words(text)
        assert tokens
        rows.append({'id': f'{COLLECTION}-{book}-{section}', 'book': book, 'section': section,
                     'order': order + len(rows), 'text': text, 'tokens': tokens,
                     'sourcePath': source_path, 'sourceId': source_id, 'sourceIds': [source_id],
                     'readerBook': book, 'chapter': current_chapter, 'sourceChapter': current_chapter,
                     'whistonSectionStart': start_whiston, 'whistonSectionEnd': current_whiston,
                     'sourceSegments': segments, 'paragraphStart': 0, 'paragraphEnd': offset,
                     'editorial': []})
        paragraphs.append({'sourceId': source_id, 'sourceIdentityKind': 'xml:id',
                           'sourceAttributes': attributes(node), 'rawText': text, 'rawLength': offset,
                           'sections': [section], 'sourceChapter': current_chapter,
                           'whistonSectionStart': start_whiston, 'whistonSectionEnd': current_whiston,
                           'nieseMarkers': [], 'structuralMarkers': inside_markers})
        chapters[-1]['sections'].append(section)
        previous_section = section
    assert [row['section'] for row in rows] == list(range(1, expected_sections + 1))
    assert sum(len(row['tokens']) for row in rows) == expected_tokens
    assert [chapter['chapter'] for chapter in chapters] == list(range(1, expected_chapters + 1))
    assert [marker['number'] for marker in all_markers if marker['unit'] == 'whiston-section'] == list(range(1, expected_whiston + 1))
    embedded = [marker for marker in all_markers if marker['location'] == 'inside-paragraph']
    assert [(m['section'], m['number'], m['sourceTextOffset']) for m in embedded] == ([] if book == 1 else [(109, 9, 106), (112, 10, 4)]), embedded
    return {'evidence': {'path': source_path, 'book': book, 'indexed': True,
                        'sha256': sha(raw), 'lfSHA256': sha(lf), 'bytes': len(raw), 'bodyTags': dict(counts),
                        'paragraphs': len(paragraphs), 'sections': len(rows), 'tokens': expected_tokens,
                        'chapters': len(chapters), 'whistonSections': expected_whiston,
                        'embeddedWhistonMilestones': len(embedded), 'editorialElements': 0,
                        'literalBracketParagraphs': sum('[' in row['text'] or ']' in row['text'] for row in rows)},
            'rows': rows, 'paragraphs': paragraphs, 'chapters': chapters,
            'structuralMarkers': direct_markers, 'allStructuralMarkers': all_markers,
            'supplied': [], 'exclusions': [], 'structural': [], 'formatting': []}


def main():
    assert len(sys.argv) in {1, 2}, 'Usage: whiston-contra-apionem-source-witness.py [repository]'
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[3]
    files, order = [], 0
    for spec in SPECS:
        item = extract_source(root, spec, order)
        files.append(item)
        order += len(item['rows'])
    rows = [row for item in files for row in item['rows']]
    assert len(rows) == 616 and [row['order'] for row in rows] == list(range(616))
    assert sum(len(row['tokens']) for row in rows) == 36853
    result = {'sourceCommit': SOURCE_COMMIT, 'collectionId': COLLECTION,
              'runtime': {'python': sys.version.split()[0], 'unicode': unicodedata.unidata_version, 'xmlParser': 'xml.dom.minidom'},
              'rows': rows, 'sources': [item['evidence'] for item in files], 'indexedFiles': files, 'testSources': [],
              'bookTotals': [{'book': item['evidence']['book'], 'sections': item['evidence']['sections'], 'tokens': item['evidence']['tokens']}
                             for item in files],
              'totals': {'books': 2, 'sections': len(rows), 'tokens': sum(len(row['tokens']) for row in rows)}}
    print(json.dumps(result, ensure_ascii=False, separators=(',', ':')))


if __name__ == '__main__':
    main()
