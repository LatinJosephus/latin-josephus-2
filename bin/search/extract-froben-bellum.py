"""Read-only search projection of the released Froben 1524 Bellum reader.

Niese/reader books determine query scope. Native printed books and divisions
are independent provenance. Every accepted narrative character has one owner.
Coordinates in the accepted reader are code points; search geometry is UTF-16.
"""
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

COLLECTION = 'bellum-latin-froben1524'
SOURCE = 'assets/data/bellum-froben1524/reader.json'
SOURCE_SHA256 = '7817b7bc22def4486431a29aecef7565f0d3be87e941ca5dae29726737500e5e'
TEXT_SHA256 = '18d24f457f62f4a925073cd2fd5b02a106f2be48614e0dab64a08f0c4bd34a6d'
COUNTS = [673, 654, 542, 663, 572, 442, 455]
HERE = Path(__file__).resolve().parent

def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()

def dump(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()

def u16(text):
    return len(text.encode('utf-16-le')) // 2

def words(text):
    count, active = 0, False
    for char in text:
        kind = unicodedata.category(char)[0]
        if kind in 'LN':
            count += not active
            active = True
        elif kind != 'M':
            active = False
    return count

def source_index(data):
    rows, locations = [], {}
    for page in data['pages']:
        for row in page['rows']:
            key = (page['image'], row['id'])
            assert key not in locations
            prefix = [0]
            for char in row['text']:
                prefix.append(prefix[-1] + u16(char))
            locations[key] = len(rows)
            rows.append({'row': row, 'page': page, 'prefix': prefix})
    def point(location):
        index = locations[tuple(location[:2])]
        assert 0 <= location[2] <= len(rows[index]['row']['text'])
        return index, location[2]
    return rows, point

def fragments(rows, point, span, paragraph_only=True):
    (first, begin), (last, end) = point(span['start']), point(span['end'])
    assert (first, begin) < (last, end)
    result = []
    for index in range(first, last + bool(end)):
        item = rows[index]
        if paragraph_only and item['row']['role'] != 'paragraph':
            continue
        lo, hi = begin if index == first else 0, end if index == last else len(item['row']['text'])
        if hi > lo:
            result.append((item, lo, hi))
    return result

def project_text(parts):
    """Project explicit joins while retaining linear original-source pieces."""
    cells = [(char, item, cp) for item, lo, hi in parts
             for cp, char in enumerate(item['row']['text'][lo:hi], lo)]
    raw = ''.join(cell[0] for cell in cells)
    removed, joins = set(), []
    for match in re.finditer(r'¬+\s*', raw):
        assert match.start() and match.end() < len(raw), 'Unresolved continuation at a citation boundary'
        assert raw[match.start()-1].isalnum(), 'Unresolved explicit continuation'
        removed.update(range(match.start(), match.end()))
        joins.append((match.start(), match.end(), match.group()))
    kept = [(i, cell) for i, cell in enumerate(cells) if i not in removed]
    while kept and kept[0][1][0].isspace(): kept.pop(0)
    while kept and kept[-1][1][0].isspace(): kept.pop()
    text, pieces, offset, last = [], [], 0, None
    for _, (char, item, cp) in kept:
        value = ' ' if char in '\r\n\t' else char
        kind = 'whitespace' if value != char else 'literal'
        page, row, prefix = item['page'], item['row'], item['prefix']
        if last is not None and last[0] is item and last[1] + 1 == cp and last[2] == kind:
            piece = pieces[-1]
            piece['recordEnd'] = offset + u16(value)
            piece['sourceEnd'] = prefix[cp+1]
            last = (item, cp, kind, last[3])
        else:
            if last is not None:
                pieces[-1]['textSHA256'] = sha(last[0]['row']['text'][last[3]:last[1]+1])
            pieces.append({'image': page['image'], 'pageId': page['id'], 'pageLabel': page['display'],
                'facsimile': page['facsimile'], 'line': row['id'], 'sourceStart': prefix[cp], 'sourceEnd': prefix[cp+1],
                'recordStart': offset, 'recordEnd': offset + u16(value), 'projection': kind})
            last = (item, cp, kind, cp)
        text.append(value)
        offset += u16(value)
    assert last is not None, 'An accepted Niese section has no prose'
    pieces[-1]['textSHA256'] = sha(last[0]['row']['text'][last[3]:last[1]+1])
    join_evidence = []
    for begin, end, original in joins:
        _, left, cp = cells[begin]
        _, right, next_cp = cells[end]
        join_evidence.append({'marker': [left['page']['image'], left['row']['id'], cp],
            'following': [right['page']['image'], right['row']['id'], next_cp], 'sourceText': original,
            'wordContinuation': cells[end][0].isalnum() or unicodedata.category(cells[end][0])[0] == 'M'})
    value = ''.join(text)
    assert '¬' not in value
    return value, pieces, join_evidence, raw

def project(data, selected_books):
    rows, point = source_index(data)
    combined, reports = [], []
    for book in selected_books:
        units = [unit for unit in data['niese'] if unit['book'] == f'latin-bellum{book}']
        assert [unit['number'] for unit in units] == list(range(1, COUNTS[book-1]+1))
        records, owned, join_count = [], {}, 0
        for unit in units:
            assert len(unit['spans']) == 1
            span = unit['spans'][0]
            parts = fragments(rows, point, span)
            text, pieces, joins, raw = project_text(parts)
            start, end = point(span['start']), point(span['end'])
            def related(layer):
                return [{'id': item['id'], 'label': item['label'], **({'kind': item['kind']} if 'kind' in item else {})}
                        for item in data[layer] if any(point(s['start']) < end and point(s['end']) > start for s in item['spans'])]
            for item, lo, hi in parts:
                key = (item['page']['image'], item['row']['id'])
                owned.setdefault(key, []).append((lo, hi))
            record = {'id': f'{COLLECTION}-{book}-{unit["number"]}', 'collectionId': COLLECTION,
                'work': 'bellum', 'book': book, 'section': unit['number'], 'order': len(combined) + len(records),
                'language': 'Latin', 'edition': 'Froben 1524', 'citationScheme': 'niese',
                'sourcePath': SOURCE, 'sourceId': unit['id'], 'sourceIds': list(dict.fromkeys(piece['line'] for piece in pieces)),
                'sourceOccurrence': f'{COLLECTION}-{unit["id"]}', 'sourceVersion': SOURCE_SHA256,
                'readerLink': {'path': 'bellum-judaicum/', 'params': {'book': book, 'niese': unit['number'], 'froben': '1'}},
                'url': f'/bellum-judaicum/?book={book}&niese={unit["number"]}&froben=1',
                'text': text, 'sourcePieces': pieces,
                'frobenSource': {'nieseId': unit['id'], 'span': span, 'printedBooks': related('frobenBooks'),
                    'printedDivisions': related('divisions'), 'joins': joins, 'rawNarrativeSHA256': sha(raw)}}
            records.append(record)
            join_count += len(joins)
        canonical, = [item for item in data['books'] if item['id'] == f'latin-bellum{book}']
        accounting = []
        for item, lo, hi in fragments(rows, point, canonical['spans'][0], False):
            row, page = item['row'], item['page']
            ranges = sorted(owned.get((page['image'], row['id']), []))
            if row['role'] == 'paragraph':
                cursor = lo
                for begin, finish in ranges:
                    assert begin == cursor and finish > begin, f'Duplicated or uncovered source interval: {row["id"]}'
                    cursor = finish
                assert cursor == hi
            else:
                assert not ranges
            accounting.append({'image': page['image'], 'line': row['id'], 'role': row['role'],
                'startCP': lo, 'endCP': hi, 'textSHA256': sha(row['text'][lo:hi]),
                'classification': 'indexed-running-text' if row['role'] == 'paragraph' else 'excluded-printed-heading'})
        counts = {'sections': len(records), 'runningWordTokens': sum(words(record['text']) for record in records),
            'sourceRows': len(accounting), 'paragraphRows': sum(item['role'] == 'paragraph' for item in accounting),
            'explicitContinuations': join_count}
        reports.append({'status': 'PASS', 'book': book, 'counts': counts, 'sourceAccounting': accounting,
            'coverage': {'sectionsExactlyRestored': len(records), 'sourceIntervalsOwnedOnce': True,
                'completeRange': [1, COUNTS[book-1]], 'missingSections': [], 'unexpectedSections': [], 'duplicateSections': []}})
        combined.extend(records)
    return combined, reports

def build(root, output, books):
    raw = (root / SOURCE).read_bytes()
    assert sha(raw) == SOURCE_SHA256, 'The accepted Froben Bellum reader changed'
    data = json.loads(raw)
    assert data['textSha256'] == TEXT_SHA256 and len(data['pages']) == 260 and len(data['niese']) == 4001
    records, books_report = project(data, list(range(1, books+1)))
    output.mkdir(parents=True, exist_ok=True)
    def artifact(name, value):
        content = dump(value)
        (output / name).write_bytes(content)
        return {'path': f'data/{COLLECTION}/{name}', 'sha256': sha(content), 'bytes': len(content)}
    for report in books_report:
        selected = [record for record in records if record['book'] == report['book']]
        name = f'book-{report["book"]:02}'
        report['source'] = {'path': SOURCE, 'sha256': sha(raw), 'bytes': len(raw)}
        report['corpus'] = {**artifact(name+'.corpus.json', selected), 'records': len(selected)}
        report['extractionReport'] = artifact(name+'.extraction-report.json', report)
    combined = {'status': 'PASS', 'collection': COLLECTION,
        'corpus': {**artifact('corpus.json', records), 'records': len(records)},
        'counts': {'books': books, 'sections': len(records), 'runningWordTokens': sum(words(record['text']) for record in records)},
        'coverage': {'sectionsExactlyRestored': len(records), 'wordSequencePreserved': True,
            'nonWhitespaceContentPreserved': True, 'globalIdsUnique': len({record['id'] for record in records}) == len(records),
            'globalOrderIsConsecutive': all(record['order'] == index for index, record in enumerate(records)),
            'allSectionTextsNonempty': all(record['text'] for record in records), 'sourceIntervalsOwnedOnce': True},
        'books': books_report}
    artifact('extraction-report.json', combined)
    return combined['counts']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=HERE.parent.parent)
    parser.add_argument('--output-dir', type=Path, default=HERE/'data'/COLLECTION)
    parser.add_argument('--books', type=int, choices=range(1, 8), default=7)
    args = parser.parse_args()
    print(json.dumps(build(args.source_root, args.output_dir, args.books)))
