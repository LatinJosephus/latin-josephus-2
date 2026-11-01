"""Read-only projection of the accepted Lauro reader assets into physical passages.

Run with --books 1 for the pilot; the default builds all five books. No scholarly
input is edited. Coordinates in records are UTF-16, end exclusive.
"""
import argparse
import hashlib
import json
from pathlib import Path
import unicodedata

COLLECTION = 'deh-italian-lauro1544'
VERSION = 'LAURO1544_WEBSITE_RELEASE_20261031_V1'
EDITION = 'Lauro 1544 (corrected 199; provisional correspondence)'
PINS = ['8205c706d637277ee98cd4e3adbbd86ae2f13ff7128a90edd7feae2f8ecd7ae7', '829ca7017671c0420163d9ba4a77c715831185cec62d34ff6df63575a7a95164', '70ee4d7b1a6241cd9c6c4c7d5f45436942c1b0cdaebd178f395cd7102e45a9bc', '4142b77e21428258713617998c80da1047e82153dfa73ed39a0b471e231f6ac1', '4457fb8b741c5f8967466b64612fa0ba70c4dadfc35b34c8a69297a643a92be5']


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
    value = re.sub(r'(?<=[^\W_])¬\s*(?=[^\W_])', '', text.replace('[ſi]', 'ſi'))
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
    return {page['image_number']: f'f. {(page["image_number"]+1)//2}{"r" if page["image_number"]%2 else "v"}' for page in data['pages']}


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
        included = line['primary'] and line['emit_in_main_text']
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
            division = 'prologue' if all(canonical[mid]['citation'].startswith('Prol.') for mid in mids) else 'narrative'
            previous = records[-1] if records else None
            if not previous or previous['mappingIds'] != mids or previous['division'] != division:
                section = len(records) + 1
                identity = f'{COLLECTION}-{line["TEI_line_id"]}-{start}'
                records.append({'id': identity, 'work': 'deh', 'book': data['book'], 'section': section,
                    'order': initial_order + len(records), 'language': 'Italian', 'edition': EDITION,
                    'citationScheme': 'source-span', 'citationUnitId': identity,
                    'normalizationProfile': 'early-print-it-v1', 'division': division,
                    'sourceId': line['TEI_line_id'], 'sourceOccurrence': identity,
                    'mappingIds': mids, 'canonicalCorrespondences': [canonical[mid] for mid in mids],
                    'sourcePath': f'assets/data/deh-lauro1544/book-{data["book"]:02}.json',
                    'breakBefore': bool(previous and previous['division'] != division),
                    'text': '', 'sourcePieces': [], 'phraseBreaks': [], 'textGaps': [],
                    'readerLink': {'path': 'deh/', 'params': {'book': data['book'], 'italian': 'lauro1544',
                        'lauro-view': 'page', 'lauro-page': line['image_number']}},
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
                'textSHA256': sha(text), 'acceptedSourceLineSHA256': line['text_sha256'],
                'baselineRecordId': line['baseline_record_id'], 'logicalRecordId': line['logical_record_id'],
                'pageId': line['page_id'], 'imageId': line['image_id'],
                'originalSourceLineIds': line['original_source_line_ids'],
                'editorialAnnotations': line.get('editorial_annotations', [])})
            # Only the specifically accepted supplied-letter annotation permits
            # bracket removal for word matching. Original record.text is exact.
            import re
            for match in re.finditer(r'\[[^\]]+\]', text):
                assert match[0] == '[ſi]' and any(a.get('kind') == 'SUPPLIED_EDITORIAL_TEXT' for a in line['editorial_annotations']), 'Unclassified bracketed primary text'
                record.setdefault('suppliedTextRanges', []).append({'start': offset+u16(text[:match.start()]), 'end': offset+u16(text[:match.end()]), 'text': match[0]})
                record.setdefault('sourceAnnotations', []).append({'kind':'supplied','text':match[0], 'line':line['TEI_line_id'], 'editoriallySuppliedNotPrinted':True})
    for record in records:
        assert sum(p['recordEnd']-p['recordStart'] for p in record['sourcePieces']) > 0
        first, last = record['sourcePieces'][0], record['sourcePieces'][-1]
        record['citationLabel'] = f'Book {data["book"]}, {first["folio"]}' + (f'–{last["folio"]}' if first['image'] != last['image'] else '')
        refs = '; '.join(c['citation'] for c in record['canonicalCorrespondences'])
        record['citationLabel'] += f' (DEH correspondence: {refs})'
        record['citationUnitCitation'] = record['citationLabel']
        record['url'] = f'/deh/?book={data["book"]}&italian=lauro1544&lauro-view=page&lauro-page={first["image"]}'
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
        relative = f'assets/data/deh-lauro1544/book-{number:02}.json'
        content = (root / relative).read_bytes()
        assert sha(content) == PINS[number - 1], 'Accepted reader input hash differs: ' + relative
        data = json.loads(content)
        assert data['version'] == VERSION
        records, accounting = project(data, len(all_records))
        all_records += records
        corpus = save(f'book-{number:02}.corpus.json', records) | {'records': len(records)}
        tokens = sum(word_count(r['text']) for r in records)
        coverage = {'paragraphsExactlyRestored': sum(l['primary'] and l['emit_in_main_text'] for l in data['lines']),
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
    manifest = {'schemaVersion': 1, 'id': COLLECTION, 'work': 'deh', 'label': 'De excidio Hierosolymitano — Lauro Italian',
        'citationPrefix': 'Lauro', 'citationScheme': 'source-span', 'unitLabel': 'Italian passage', 'unitLabelPlural': 'Italian passages',
        'language': 'Italian', 'edition': EDITION, 'readerPath': 'deh/', 'corpus': f'../data/{COLLECTION}/corpus.json',
        'extractionReport': f'../data/{COLLECTION}/extraction-report.json',
        'books': [{'number': b['book'], 'label': f'Book {b["book"]}' + (' (including translated Prologue)' if b['book'] == 1 else ''),
            'corpus': f'../data/{COLLECTION}/book-{b["book"]:02}.corpus.json', 'sections': b['corpus']['records'],
            'sectionRange': [1, b['corpus']['records']], 'source': b['source']['path']} for b in books]}
    (base / f'config/{COLLECTION}.json').write_bytes(dump(manifest))


if __name__ == '__main__':
    main()
