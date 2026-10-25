#!/usr/bin/env python3
"""Independent Pollard English De excidio witness; no extractor imports.

The accepted five books have 558 complete chapter/paragraph units. A leading
num element carries each citation, and 217 paragraphs also have indentation
before that element. The witness walks DOM children and excludes that element
explicitly; it never treats the label's length as the paragraph prefix length.
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
COLLECTION = 'deh-english-pollard'
SOURCE_COMMIT = '21f9fbcef3b5a5dc9499756495d47b2e498d87f2'
ROMANS = [None, 'I', 'II', 'III', 'IV', 'V']
TRANSLATION_NOTES = {1: {31, 36, 70, 141}, 2: {73}, 3: {36, 47}, 4: set(), 5: {72}}
SPECS = [
    (1, 215, 40804, 47, 126, '1f8a50242272c8cbb2fe2054c10e318cf00d0aab91b508eb1ca9e7a9e6a60b47'),
    (2, 73, 17142, 18, 73, 'b87360225888e3e66950905eb047bded590302bb28b2b0f4c43fdbf8b089db2c'),
    (3, 70, 18640, 26, 18, 'f6c0c7ea4140e40bbe72d6a9293e5cbe6df73d15271d41d88d72a5eefd14e08c'),
    (4, 79, 17259, 33, 0, '1e5bf28ece4f00954924fe5aa9a704e647289a0c83e7e08ca99944b8412c0370'),
    (5, 121, 42207, 53, 0, '4df33b9d0409644e5f9f2bcacb87ca507e5ff2272d72d1a0b1c73e14f2484c91'),
]
LATIN_SHA = [
    '690da8720b61514199f898909c06661fddc9f3c79a06eea3b392325de7924aa7',
    'cc2ac0d622d56b0ef0e9a74bfdbcb2836c8cd89defbc0a70c11f9cb6274ef25a',
    'aeb861000317b2bbeada0a0d8918499f516f1dc524257ec90d140a5e9bf066c5',
    '150fb0857b07eaa47ca0de119558ed76368d6a452c06784475b97eb15a0e10fa',
    'f97fbd0992e8a540d250963109610060a8f417cb7cd18f93d5279c82cf2fcd97',
]


def sha(data):
    return hashlib.sha256(data.encode('utf-8') if isinstance(data, str) else data).hexdigest()


def all_text(node):
    if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
        return node.data
    return ''.join(all_text(child) for child in node.childNodes)


def u16(text):
    return len(text.encode('utf-16-le')) // 2


def scan_words(text):
    """Independent Unicode-category scanner, with original UTF-16 offsets."""
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


def elements(element):
    result = []
    for child in element.childNodes:
        if child.nodeType == Node.ELEMENT_NODE:
            result.append(child)
        else:
            assert child.nodeType == Node.TEXT_NODE and not child.data.strip(), ('Unexpected structural text', child)
    return result


def accepted_xml(root, path, fingerprint):
    raw = (root / path).read_bytes()
    lf = raw.replace(b'\r\n', b'\n')
    assert b'\r' not in lf and sha(lf) == fingerprint, ('Unaccepted source', path)
    assert b'<!DOCTYPE' not in raw.upper() and b'<!ENTITY' not in raw.upper()
    dom = minidom.parseString(raw)
    assert dom.documentElement.namespaceURI == TEI
    all_elements = list(dom.getElementsByTagName('*'))
    assert all(node.namespaceURI == TEI for node in all_elements)
    ids = [node.getAttribute('xml:id') for node in all_elements if node.hasAttribute('xml:id')]
    assert len(ids) == len(set(ids)), path
    return dom, {'path': path, 'sha256': sha(raw), 'lfSHA256': sha(lf), 'bytes': len(raw)}


def extract_source(root, spec, order):
    book, units, expected_tokens, chapter_count, indented_count, fingerprint = spec
    source_path = f'assets/xml/deh/English/book-{book:02}.xml'
    dom, source = accepted_xml(root, source_path, fingerprint)
    latin_path = f'assets/xml/deh/Latin/book-{book:02}.xml'
    latin_dom, latin_source = accepted_xml(root, latin_path, LATIN_SHA[book - 1])
    latin_ids = {node.getAttribute('xml:id'): node for node in latin_dom.getElementsByTagName('*') if node.hasAttribute('xml:id')}
    bodies = dom.getElementsByTagName('body')
    assert len(bodies) == 1 and attributes(bodies[0]) == {}
    body = bodies[0]
    body_tags = Counter([body.localName, *(node.localName for node in body.getElementsByTagName('*'))])
    assert body_tags == {'body': 1, 'note': 1 + len(TRANSLATION_NOTES[book]), 'div1': 1, 'div2': chapter_count,
                        'head': 2 if book == 1 else 1, 'p': units, 'num': units}
    body_children = elements(body)
    assert [node.localName for node in body_children] == ['note', 'div1']
    note, division = body_children
    assert attributes(note) == {} and not note.getElementsByTagName('*')
    assert attributes(division) == {'n': ROMANS[book], 'type': 'book', 'subtype': 'English',
                                    'xml:id': f'english-deh{book}', 'sameAs': f'#latin-deh{book}'}
    links = []
    for node in [division, *division.getElementsByTagName('*')]:
        if node.hasAttribute('xml:id'):
            english_id, target = node.getAttribute('xml:id'), node.getAttribute('sameAs')
            assert target == '#' + english_id.replace('english-', 'latin-', 1)
            assert target[1:] in latin_ids and latin_ids[target[1:]].localName == node.localName
            if node.localName in {'div1', 'div2'}:
                assert node.getAttribute('n') == latin_ids[target[1:]].getAttribute('n')
            links.append({'sourceId': english_id, 'sameAs': target, 'latinSourcePath': latin_path})
    header = dom.getElementsByTagName('teiHeader')[0]
    excluded = [{'kind': 'teiHeader', 'text': all_text(header), 'textSHA256': sha(all_text(header))},
                {'kind': 'body-note', 'text': all_text(note), 'textSHA256': sha(all_text(note))}]
    rows, paragraphs, chapters = [], [], []
    indented = 0
    for chapter_index, chapter_node in enumerate(elements(division)):
        chapter = chapter_index + (0 if book == 1 else 1)
        assert chapter_node.localName == 'div2'
        chapter_attributes = {'n': str(chapter), 'type': 'chapter',
                              'xml:id': f'english-deh{book}-chapter{chapter}',
                              'sameAs': f'#latin-deh{book}-chapter{chapter}'}
        assert attributes(chapter_node) == chapter_attributes
        chapter_rows, local_paragraph = [], 0
        for element_index, node in enumerate(elements(chapter_node)):
            if node.localName == 'head':
                assert element_index == 0 and attributes(node) == {} and not node.getElementsByTagName('*')
                expected = 'Prologue' if chapter == 0 else ('Book ' if book < 3 else 'BOOK ') + ROMANS[book]
                assert chapter in ({0, 1} if book == 1 else {1}) and all_text(node) == expected
                excluded.append({'kind': 'heading', 'chapter': chapter, 'text': expected, 'textSHA256': sha(expected)})
                continue
            assert node.localName == 'p'
            local_paragraph += 1
            section = len(rows) + 1
            source_id = f'english-deh{book}-num{section}'
            same_as = f'#latin-deh{book}-num{section}'
            assert attributes(node) == {'xml:id': source_id, 'sameAs': same_as}
            label = f'Prol.{local_paragraph}' if chapter == 0 else f'{ROMANS[book]}.{chapter}.{local_paragraph}'
            prefix_parts, running_parts, seen_label, annotation = [], [], False, ''
            for child in node.childNodes:
                if child.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                    if seen_label:
                        assert not annotation, 'Unreviewed text after a translation note'
                        running_parts.append(child.data)
                    else:
                        assert not child.data.strip()
                        prefix_parts.append(child.data)
                else:
                    if child.nodeType == Node.ELEMENT_NODE and child.localName == 'note':
                        assert seen_label and not annotation and section in TRANSLATION_NOTES[book]
                        assert attributes(child) == {'type': 'uncertainty', 'source': same_as}
                        assert not child.getElementsByTagName('*')
                        annotation = all_text(child)
                        assert annotation.startswith('Translation comparison: ')
                        continue
                    assert child.nodeType == Node.ELEMENT_NODE and child.localName == 'num' and not seen_label
                    assert attributes(child) == {} and not child.getElementsByTagName('*')
                    assert all_text(child) == f'[{label}]'
                    latin_labels = latin_ids[same_as[1:]].getElementsByTagName('num')
                    assert len(latin_labels) == 1 and all_text(latin_labels[0]) == all_text(child)
                    indented += int(bool(prefix_parts))
                    prefix_parts.append(all_text(child))
                    seen_label = True
            assert seen_label
            prefix, running = ''.join(prefix_parts), ''.join(running_parts)
            raw = all_text(node)
            assert prefix + running + annotation == raw
            text = running.strip()
            leading = running[:len(running) - len(running.lstrip())]
            trailing = running[len(running.rstrip()):]
            assert prefix + leading + text + trailing + annotation == raw and text
            tokens = scan_words(text)
            assert tokens
            start, end = u16(prefix + leading), u16(prefix + leading + text)
            assert end - start == u16(text)
            row = {'id': f'{COLLECTION}-{book}-{section}', 'book': book, 'section': section,
                   'order': order + len(rows), 'text': text, 'tokens': tokens,
                   'sourcePath': source_path, 'sourceId': source_id, 'sourceIds': [source_id],
                   'sourceSameAs': same_as, 'readerBook': book, 'chapter': chapter,
                   'paragraph': local_paragraph, 'citationLabel': label, 'prologue': chapter == 0,
                   'breakBefore': book == 1 and chapter == 1 and local_paragraph == 1,
                   'paragraphStart': start, 'paragraphEnd': end,
                   'sourceSegments': [{'sourceId': source_id, 'rawStart': start, 'rawEnd': end,
                                       'start': 0, 'end': u16(text), 'text': text}], 'editorial': []}
            rows.append(row)
            paragraphs.append({'sourceId': source_id, 'sourceIdentityKind': 'xml:id',
                               'sourcePath': source_path, 'sourceAttributes': attributes(node),
                               'bookAttributes': attributes(division), 'chapterAttributes': chapter_attributes,
                               'paragraphOrdinal': section - 1, 'chapter': chapter, 'paragraph': local_paragraph,
                               'citationLabel': label, 'rawText': raw, 'rawLength': u16(raw),
                               'runningText': running, 'removedPrefix': prefix,
                               'leadingWhitespace': leading, 'trailingWhitespace': trailing,
                               'annotationText': annotation, 'sections': [section]})
            chapter_rows.append(section)
        assert local_paragraph > 0
        chapters.append({'chapter': chapter, 'attributes': chapter_attributes, 'sections': chapter_rows})
    assert len(rows) == units and [row['section'] for row in rows] == list(range(1, units + 1))
    assert sum(len(row['tokens']) for row in rows) == expected_tokens
    assert len(chapters) == chapter_count and indented == indented_count
    assert len(links) == 1 + chapter_count + units
    assert sum(row['prologue'] for row in rows) == (3 if book == 1 else 0)
    assert sum(row['breakBefore'] for row in rows) == (1 if book == 1 else 0)
    assert not any(any(c in row['text'] for c in '[]†*') for row in rows)
    evidence = {**source, 'book': book, 'indexed': True, 'bodyTags': dict(body_tags),
                'paragraphs': units, 'sections': units, 'tokens': expected_tokens, 'chapters': chapter_count,
                'prologueUnits': sum(row['prologue'] for row in rows),
                'indentedBeforeCitationLabel': indented, 'sameAsLinks': len(links),
                'excludedBodyNotes': 1, 'excludedHeadings': 2 if book == 1 else 1,
                'editorialElements': len(TRANSLATION_NOTES[book]),
                'excludedTranslationNotes': len(TRANSLATION_NOTES[book]), 'literalBracketParagraphs': 0}
    return {'evidence': evidence, 'rows': rows, 'paragraphs': paragraphs, 'chapters': chapters,
            'sameAsLinks': links, 'exclusions': excluded,
            'latinEvidence': {**latin_source, 'book': book, 'indexed': False, 'purpose': 'Existing sameAs targets and exact citation-label alignment'}}


def main():
    assert len(sys.argv) in {1, 2}, 'Usage: deh-english-source-witness.py [repository]'
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[3]
    files, order = [], 0
    for spec in SPECS:
        item = extract_source(root, spec, order)
        files.append(item)
        order += len(item['rows'])
    rows = [row for item in files for row in item['rows']]
    assert len(rows) == 558 and [row['order'] for row in rows] == list(range(558))
    assert sum(len(row['tokens']) for row in rows) == 136052
    assert sum(source['evidence']['sameAsLinks'] for source in files) == 740
    assert sum(source['evidence']['indentedBeforeCitationLabel'] for source in files) == 217
    result = {'sourceCommit': SOURCE_COMMIT, 'collectionId': COLLECTION,
              'runtime': {'python': sys.version.split()[0], 'unicode': unicodedata.unidata_version, 'xmlParser': 'xml.dom.minidom'},
              'rows': rows, 'sources': [item['evidence'] for item in files], 'indexedFiles': files,
              'testSources': [item['latinEvidence'] for item in files],
              'bookTotals': [{'book': item['evidence']['book'], 'sections': item['evidence']['sections'], 'tokens': item['evidence']['tokens']}
                             for item in files],
              'totals': {'books': 5, 'sections': len(rows), 'tokens': sum(len(row['tokens']) for row in rows)}}
    print(json.dumps(result, ensure_ascii=False, separators=(',', ':')))


if __name__ == '__main__':
    main()
