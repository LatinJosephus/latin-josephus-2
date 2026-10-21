#!/usr/bin/env python3
"""Independent Whiston Bellum witness: minidom text streams, no extractor imports.

The seven accepted XML files already contain all 4,001 Niese intervals.
Their original sameAs paragraph anchors remain source identities. The supplied
passage in VII.208–209 includes a nested milestone and is retained as text and
editorial evidence. Ordinary chapter boundaries create no phrase barrier.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
from xml.dom import Node, minidom

TEI = 'http://www.tei-c.org/ns/1.0'
COLLECTION = 'bellum-english-whiston'
SOURCE_COMMIT = 'dc483d165f522aa848d36971c22386bcedbda511'
SPECS = [
    (1, 673, 234, '39713b6768eef8e7d6ac9640255eacd962ac9677175fbc05077aafe296a1b5ec'),
    (2, 654, 143, '52c0e14514dc6ba6942a2ff98e5a87c96122f117fe0122f112b697cbfc12f941'),
    (3, 542, 88, 'ced7460be53bc6f7f94e4a842f9a3c3f28624cdaaced38d433acf2f4dd3d0cd2'),
    (4, 663, 78, 'b5b299ee96671784527fc1edef4777e5a766e6f9496fcfb63470874c71824c96'),
    (5, 572, 65, '5a6647478976c860b7fb771b058b4af34181eff8201d502f037f0610ca536ee7'),
    (6, 442, 50, 'edf957eb0501feebbe595f44703c2caa185c9acb6d28efbe69875f3aaa8b2799'),
    (7, 455, 46, '2d2c308a500711fddad5cc7ba436f59c38890dd4988f6f5b505817e04e5b200b'),
]
SUPPLIED_ATTRIBUTES = {'reason': 'omitted', 'source': 'https://lexundria.com/j_bj/7.208-7.209/wst'}
SUPPLIED_TEXT = (' were slain, to the number of one thousand seven hundred, as were the women and the children made slaves; '
                 'but as Bassus thought he must perform the covenant, he had made with those that had surrendered the citadel, '
                 'he let them go, and restored Eleazar to them. ')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def all_text(node):
    if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
        return node.data
    return ''.join(all_text(child) for child in node.childNodes)


def u16(text):
    return len(text.encode('utf-16-le')) // 2


def slice16(text, start, end):
    return text.encode('utf-16-le')[2 * start:2 * end].decode('utf-16-le')


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


def extract_source(root, spec, order):
    book, expected_sections, expected_paragraphs, fingerprint = spec
    source_path = f'assets/xml/bellum/English/book-{book:02}.xml'
    raw = (root / source_path).read_bytes()
    lf = raw.replace(b'\r\n', b'\n')
    assert b'\r' not in lf and sha(lf) == fingerprint, ('Unaccepted Bellum Whiston source', source_path)
    assert b'<!DOCTYPE' not in raw.upper() and b'<!ENTITY' not in raw.upper()
    dom = minidom.parseString(raw)
    assert dom.documentElement.namespaceURI == TEI
    elements = list(dom.getElementsByTagName('*'))
    assert all(element.namespaceURI == TEI for element in elements)
    ids = [element.getAttribute('xml:id') for element in elements if element.hasAttribute('xml:id')]
    assert len(ids) == len(set(ids))
    bodies = dom.getElementsByTagName('body')
    assert len(bodies) == 1
    body = bodies[0]
    counts = Counter([body.localName, *(node.localName for node in body.getElementsByTagName('*'))])
    assert set(counts) <= {'body', 'div1', 'div2', 'p', 'milestone', 'supplied'}, counts
    assert counts['supplied'] == (1 if book == 7 else 0)
    rows, paragraphs, supplied, chapters = [], [], [], []
    for chapter in body.getElementsByTagName('div2'):
        number = int(chapter.getAttribute('n'))
        if chapter.getAttribute('type') != 'chapter':
            assert book == 5 and number == 13 and dict(chapter.attributes.items()) == {
                'n': '13', 'sameAs': '#latin-bellum5-chapter13'}
        markers = [int(e.getAttribute('n')) for e in chapter.getElementsByTagName('milestone')]
        chapters.append({'chapter': number, 'attributes': dict(chapter.attributes.items()), 'sections': markers})
        assert not any(child.nodeType == Node.TEXT_NODE and child.data.strip() for child in chapter.childNodes)
    for paragraph in body.getElementsByTagName('p'):
        source_id = paragraph.getAttribute('sameAs')
        assert set(dict(paragraph.attributes.items())) == {'sameAs'}
        assert re.fullmatch(fr'#latin-bellum{book}-num\d+', source_id)
        chapter = int(paragraph.parentNode.getAttribute('n'))
        raw_offset, active = 0, None
        paragraph_rows, markers, prefix, raw_marks = [], [], [], []

        def finish():
            nonlocal active
            if active is None:
                return
            events = active.pop('events')
            text = ''.join(event['text'] for event in events)
            leading = u16(text) - u16(text.lstrip())
            end = u16(text.rstrip())
            trimmed = text.strip()
            segments, cursor = [], 0
            for event in events:
                a, b = max(cursor, leading), min(cursor + u16(event['text']), end)
                if a < b:
                    piece = slice16(event['text'], a - cursor, b - cursor)
                    segments.append({'sourceId': source_id, 'rawStart': event['rawStart'] + a - cursor,
                                     'rawEnd': event['rawStart'] + b - cursor,
                                     'start': a - leading, 'end': b - leading, 'text': piece})
                cursor += u16(event['text'])
            assert ''.join(segment['text'] for segment in segments) == trimmed
            assert segments and scan_words(trimmed), ('Empty interval', book, active['section'])
            active.update(text=trimmed, tokens=scan_words(trimmed), sourceSegments=segments,
                          paragraphStart=segments[0]['rawStart'], paragraphEnd=segments[-1]['rawEnd'])
            rows.append(active)
            paragraph_rows.append(active['section'])
            active = None

        def walk(node):
            nonlocal raw_offset, active
            if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                event = {'text': node.data, 'rawStart': raw_offset}
                (prefix if active is None else active['events']).append(event)
                raw_offset += u16(node.data)
                return
            assert node.nodeType == Node.ELEMENT_NODE
            if node.localName == 'milestone':
                assert dict(node.attributes.items()) == {'unit': 'niese', 'n': node.getAttribute('n')}
                assert not node.childNodes and node.getAttribute('n').isdecimal()
                finish()
                section = int(node.getAttribute('n'))
                markers.append({'section': section, 'rawOffset': raw_offset,
                                'insideSupplied': node.parentNode.localName == 'supplied'})
                active = {'id': f'{COLLECTION}-{book}-{section}', 'book': book, 'section': section,
                          'order': order + len(rows), 'chapter': chapter, 'sourcePath': source_path,
                          'sourceId': source_id, 'sourceIds': [source_id], 'readerBook': book,
                          'rawStart': raw_offset, 'events': []}
                return
            assert node.localName == 'supplied' and book == 7
            assert dict(node.attributes.items()) == SUPPLIED_ATTRIBUTES
            assert source_id == '#latin-bellum7-num190' and all_text(node) == SUPPLIED_TEXT
            start = raw_offset
            for child in node.childNodes:
                walk(child)
            raw_marks.append({'kind': 'supplied', 'sourceId': source_id, 'rawStart': start, 'rawEnd': raw_offset,
                              'text': all_text(node), 'attributes': dict(node.attributes.items())})

        for child in paragraph.childNodes:
            walk(child)
        finish()
        assert not ''.join(event['text'] for event in prefix).strip(), ('Unexpected prefix', source_id)
        assert raw_offset == u16(all_text(paragraph))
        for row in rows:
            if row['sourceId'] != source_id:
                continue
            row['editorial'] = []
            for mark in raw_marks:
                a, b = max(row['paragraphStart'], mark['rawStart']), min(row['paragraphEnd'], mark['rawEnd'])
                if a < b:
                    row['editorial'].append({'kind': 'supplied', 'start': a - row['paragraphStart'], 'end': b - row['paragraphStart'],
                        'text': slice16(row['text'], a - row['paragraphStart'], b - row['paragraphStart']),
                        'sourceAttributes': mark['attributes'], 'rawStart': a, 'rawEnd': b})
        paragraphs.append({'sourceId': source_id, 'chapter': chapter, 'rawText': all_text(paragraph),
                           'rawLength': raw_offset, 'sections': paragraph_rows,
                           'nieseMarkers': markers, 'sourceAttributes': dict(paragraph.attributes.items())})
        supplied.extend(raw_marks)
    assert [row['section'] for row in rows] == list(range(1, expected_sections + 1))
    assert len(paragraphs) == expected_paragraphs
    assert len({p['sourceId'] for p in paragraphs}) == len(paragraphs)
    assert [item['chapter'] for item in chapters] == list(range(0 if book == 1 else 1, len(chapters) + (0 if book == 1 else 1)))
    if book == 1:
        assert chapters[0]['sections'] == list(range(1, 31))
        assert chapters[1]['sections'][0] == 31
    return {'evidence': {'path': source_path, 'book': book, 'indexed': True, 'sha256': sha(raw), 'lfSHA256': sha(lf),
                        'bytes': len(raw), 'bodyTags': dict(counts), 'paragraphs': len(paragraphs), 'sections': len(rows),
                        'tokens': sum(len(row['tokens']) for row in rows), 'chapters': len(chapters),
                        'suppliedElements': len(supplied)},
            'rows': rows, 'paragraphs': paragraphs, 'supplied': supplied, 'chapters': chapters,
            'exclusions': [], 'structural': [], 'formatting': []}


def main():
    assert len(sys.argv) in {1, 2}, 'Usage: whiston-bellum-source-witness.py [repository]'
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[3]
    files, order = [], 0
    for spec in SPECS:
        item = extract_source(root, spec, order)
        files.append(item)
        order += len(item['rows'])
    rows = [row for item in files for row in item['rows']]
    assert len(rows) == 4001 and [row['order'] for row in rows] == list(range(4001))
    assert sum(len(row['tokens']) for row in rows) == 215072
    marked = [row for row in rows if row['editorial']]
    assert [(row['book'], row['section']) for row in marked] == [(7, 208), (7, 209)]
    assert len([marker for item in files for p in item['paragraphs'] for marker in p['nieseMarkers'] if marker['insideSupplied']]) == 1
    result = {'sourceCommit': SOURCE_COMMIT, 'collectionId': COLLECTION,
              'runtime': {'python': sys.version.split()[0], 'unicode': unicodedata.unidata_version, 'xmlParser': 'xml.dom.minidom'},
              'rows': rows, 'sources': [item['evidence'] for item in files], 'indexedFiles': files, 'testSources': [],
              'bookTotals': [{'book': item['evidence']['book'], 'sections': item['evidence']['sections'], 'tokens': item['evidence']['tokens']}
                             for item in files],
              'totals': {'books': 7, 'sections': len(rows), 'tokens': sum(len(row['tokens']) for row in rows)}}
    print(json.dumps(result, ensure_ascii=False, separators=(',', ':')))


if __name__ == '__main__':
    main()
