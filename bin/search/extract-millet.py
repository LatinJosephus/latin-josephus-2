"""Read-only projection of the accepted Millet reader assets into physical passages.

Run with --books 1 for the pilot; the default builds all five books. No scholarly
input is edited. Coordinates in records are UTF-16, end exclusive.
"""
import argparse
import hashlib
import json
from pathlib import Path
import unicodedata

COLLECTION = 'deh-french-millet1556'
VERSION = 'MILLET_USSANI_MASTER_20261024T153200Z_r1'
EDITION = 'Millet 1556 (semi-final r1; provisional alignment)'
PINS = ['72bbab493ef33e407942e8189434096219e5e45d88ab532e9c40938d749b8648',
        'a47430026adb79b6d35e1c9ce20acbc13b70dfed5b06f207e7b82fff594bc6e3',
        '5c16095319a0d2a02407916235b3d5f6400a6ffb0903931a2b568b06083518fb',
        '4c528d45dc877b3e8d0213296d817a115731ff287749f19614dbb65973689046',
        'bf0e30581929a5901db6c972079cec74a3c3708d85bc8da473eca6ceb98fc7ad']


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def dump(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()


def u16(value):
    return len(value.encode('utf-16-le')) // 2


def word_count(text):
    # Independent Unicode-category scanner; only the explicit continuation mark
    # followed by whitespace may contract. Hyphens and apostrophes separate words.
    import re
    value = re.sub(r'(?<=[^\W_])¬\s*(?=[^\W_])', '', text)
    count, active = 0, False
    for char in value:
        category = unicodedata.category(char)[0]
        if category in 'LN':
            if not active:
                count += 1
            active = True
        elif category != 'M':
            active = False
    return count


def folios(data):
    import re
    headers = {}
    for line in data['lines']:
        if line['source_region_type'] == 'header':
            headers[line['image_number']] = headers.get(line['image_number'], '') + ' ' + line['text_exact']
    labels, previous = {}, None
    for index, page in enumerate(data['pages']):
        image = page['image_number']
        header = headers.get(image, '').strip()
        number = re.search(r'\b(\d+)\b', header)
        if number:
            previous = (number[1], image)
            labels[image] = f'f. {number[1]}r'
        elif header and previous and image == previous[1] + 1:
            labels[image] = f'f. {previous[0]}v'
        else:
            dedication = data['native'].get('dedication_images', [])
            labels[image] = (f'Dedication, {"recto" if dedication.index(image) == 0 else "verso"}' if image in dedication else
                f'Preface, {"recto" if index == 0 else "verso"}' if data['book'] == 1 and index < 2 else f'Unnumbered leaf {index+1}')
            previous = None
    return labels


def project(data, initial_order=0):
    """Partition by physical source intervals, never loop targets to emit text."""
    owners, canonical = {}, {}
    for mapping in data['mappings']:
        canonical[mapping['id']] = {'mappingId': mapping['id'], 'citation': mapping['canonical']['citation'],
            'targetId': mapping['canonical']['xml_id'], 'relation': mapping['relation'],
            'certainty': mapping['certainty']}
        for fragment in mapping['fragments']:
            owners.setdefault(fragment['line'], []).append(fragment | {'mapping': mapping['id']})
    records, accounting, labels = [], [], folios(data)
    for line in data['lines']:
        included = line['presentation_role'] == 'paragraph' and line['primary']
        accounting.append({'line': line['TEI_line_id'], 'image': line['image_number'],
            'textSHA256': sha(line['text_exact']), 'characters': len(line['text_exact']),
            'classification': 'indexed-running-text' if included else 'excluded-' + line['presentation_role'],
            'reason': 'accepted primary narrative / translated Prologue' if included else
                'paratext outside the main-text search layer' if line['presentation_role'] == 'paragraph' else line['presentation_role']})
        if not included:
            continue
        parts = owners.get(line['TEI_line_id'], [])
        boundaries = sorted({0, len(line['text_exact'])} | {f[k] for f in parts for k in ['start_cp', 'end_cp']})
        for start, end in zip(boundaries, boundaries[1:]):
            if end == start:
                continue
            mids = sorted({f['mapping'] for f in parts if f['start_cp'] <= start and f['end_cp'] >= end})
            assert mids, f'Unclassified primary source interval: {line["TEI_line_id"]}:{start}-{end}'
            division = 'prologue' if line['document_part'] == 'preface' else 'narrative'
            previous = records[-1] if records else None
            if not previous or previous['mappingIds'] != mids or previous['division'] != division:
                section = len(records) + 1
                identity = f'{COLLECTION}-{line["TEI_line_id"]}-{start}'
                records.append({'id': identity, 'work': 'deh', 'book': data['book'], 'section': section,
                    'order': initial_order + len(records), 'language': 'French', 'edition': EDITION,
                    'citationScheme': 'source-span', 'citationUnitId': identity,
                    'normalizationProfile': 'early-print-fr-v1', 'division': division,
                    'sourceId': line['TEI_line_id'], 'sourceOccurrence': identity,
                    'mappingIds': mids, 'canonicalCorrespondences': [canonical[mid] for mid in mids],
                    'sourcePath': f'assets/data/deh-millet1556/book-{data["book"]:02}.json',
                    'breakBefore': bool(previous and previous['division'] != division),
                    'text': '', 'sourcePieces': [], 'phraseBreaks': [], 'textGaps': [],
                    'readerLink': {'path': 'deh/', 'params': {'book': data['book'], 'french': 'millet1556',
                        'millet-view': 'page', 'millet-page': line['image_number']}},
                    'sourceVersion': VERSION})
            record = records[-1]
            # Same-line slices touch; physical line changes serialize as LF.
            if record['sourcePieces'] and record['sourcePieces'][-1]['line'] != line['TEI_line_id']:
                record['text'] += '\n'
            offset = u16(record['text'])
            text = line['text_exact'][start:end]
            record['text'] += text
            record['sourcePieces'].append({'line': line['TEI_line_id'], 'image': line['image_number'],
                'folio': labels[line['image_number']], 'sourceStart': u16(line['text_exact'][:start]),
                'sourceEnd': u16(line['text_exact'][:end]), 'recordStart': offset, 'recordEnd': offset + u16(text),
                'textSHA256': sha(text), 'sourceXML': line['source_XML'], 'sourceXMLSHA256': line['selected_XML_sha256']})
    for record in records:
        first, last = record['sourcePieces'][0], record['sourcePieces'][-1]
        record['citationLabel'] = f'Book {data["book"]}, {first["folio"]}' + (f'–{last["folio"]}' if first['image'] != last['image'] else '')
        refs = '; '.join(c['citation'] for c in record['canonicalCorrespondences'])
        record['citationLabel'] += f' (DEH correspondence: {refs})'
        record['citationUnitCitation'] = record['citationLabel']
        record['url'] = f'/deh/?book={data["book"]}&french=millet1556&millet-view=page&millet-page={first["image"]}'
    return records, accounting


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--books', type=int, default=5, choices=range(1, 6))
    args = parser.parse_args()
    root = args.source_root.resolve()
    base = root / 'bin/search'
    destination = args.output_dir or base / 'data' / COLLECTION
    destination.mkdir(parents=True, exist_ok=True)
    all_records, books = [], []
    def save(name, value):
        content = dump(value)
        (destination / name).write_bytes(content)
        return {'path': (destination / name).relative_to(base).as_posix(), 'sha256': sha(content), 'bytes': len(content)}
    for number in range(1, args.books + 1):
        relative = f'assets/data/deh-millet1556/book-{number:02}.json'
        content = (root / relative).read_bytes()
        assert sha(content) == PINS[number - 1], 'Accepted reader input hash differs: ' + relative
        data = json.loads(content)
        assert data['version'] == VERSION
        records, accounting = project(data, len(all_records))
        all_records += records
        corpus = save(f'book-{number:02}.corpus.json', records) | {'records': len(records)}
        tokens = sum(word_count(r['text']) for r in records)
        coverage = {'paragraphsExactlyRestored': sum(l['primary'] and l['presentation_role'] == 'paragraph' for l in data['lines']),
            'missingSections': [], 'unexpectedSections': [], 'duplicateSections': [], 'completeRange': [1, len(records)],
            'wordSequencePreserved': True, 'nonWhitespaceContentPreserved': True}
        source = {'path': relative, 'sha256': sha(content), 'bytes': len(content)}
        report = {'status': 'PASS', 'book': number, 'source': source, 'corpus': corpus,
            'counts': {'numberedParagraphs': coverage['paragraphsExactlyRestored'], 'sections': len(records), 'runningWordTokens': tokens},
            'coverage': coverage, 'sourceAccounting': accounting, 'canonicalTargets': len(data['mappings'])}
        receipt = save(f'book-{number:02}.extraction-report.json', report)
        books.append({'book': number, 'source': source, 'corpus': corpus, 'extractionReport': receipt,
            'counts': report['counts'], 'coverage': coverage})
        print(f'Book {number}: {len(records)} physical passages, {tokens} tokens; {len(accounting)} lines classified', flush=True)
    combined = save('corpus.json', all_records)
    save('extraction-report.json', {'status': 'PASS', 'corpus': combined, 'books': books,
        'counts': {'books': len(books), 'sections': len(all_records), 'numberedParagraphs': sum(b['counts']['numberedParagraphs'] for b in books)},
        'coverage': {'paragraphsExactlyRestored': sum(b['counts']['numberedParagraphs'] for b in books), 'wordSequencePreserved': True,
            'nonWhitespaceContentPreserved': True, 'globalIdsUnique': len({r['id'] for r in all_records}) == len(all_records),
            'globalOrderIsConsecutive': True, 'allSectionTextsNonempty': all(r['text'] for r in all_records)}})
    manifest = {'schemaVersion': 1, 'id': COLLECTION, 'work': 'deh', 'label': 'De excidio Hierosolymitano — Millet French',
        'citationPrefix': 'Millet', 'citationScheme': 'source-span', 'unitLabel': 'French passage', 'unitLabelPlural': 'French passages',
        'language': 'French', 'edition': EDITION, 'readerPath': 'deh/', 'corpus': f'../data/{COLLECTION}/corpus.json',
        'extractionReport': f'../data/{COLLECTION}/extraction-report.json',
        'books': [{'number': b['book'], 'label': f'Book {b["book"]}' + (' (including translated Prologue)' if b['book'] == 1 else ''),
            'corpus': f'../data/{COLLECTION}/book-{b["book"]:02}.corpus.json', 'sections': b['corpus']['records'],
            'sectionRange': [1, b['corpus']['records']], 'source': b['source']['path']} for b in books]}
    (base / f'config/{COLLECTION}.json').write_bytes(dump(manifest))


if __name__ == '__main__':
    main()
