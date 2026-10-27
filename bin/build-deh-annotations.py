"""Derive a chapter-level display adapter from the editor's unmodified DEH CSV.

Only columns A-E are interpreted. No XML, concordance or source CSV is written.
"""
import argparse
import collections
import csv
import hashlib
import html
import io
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_docs/deh-annotations/source.csv'
SOURCE_SHA256 = 'dfe4d299390481525c358b1baef864640ef700e7a94d941b91746feeed4a398d'
ALIASES = {
    'Cherbourg 51': 'M0133', 'Berne 180': 'M0081', 'Besancon 833': 'M0089',
    'Paris 1490': 'M0341', 'Paris 12512': 'M0355', 'Paris 12513': 'M0356',
    'Cambrai 678': 'M0113', 'Karlsruhe 82': 'M0212', 'Karlsruhe 101': 'M0211',
    'Leyde 21': 'M0221', 'Laon 403b': 'M0217', 'Saint Gall 626': 'M0508',
    'Paris 5061': 'M0367', 'Rome 170': 'M0472', 'Leyde 17': 'M0224',
    'Turin 7': 'M0535', 'Milan 105': 'M0279', 'Cassel 65': 'M0123',
    'Naples 34': 'M0314', 'Bruxelles 5540': 'M0100', 'Paris 13367': 'M0358'
}
COLUMNS = ['manuscrit', 'folio', 'section', 'main', 'contenu']


def build():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, 'Source CSV changed'
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''))
    assert reader.fieldnames[:5] == COLUMNS
    rows = list(reader)
    citations = json.loads((ROOT / 'assets/data/alignment-citations.json').read_text(encoding='utf-8'))
    catalogue_path = ROOT / '_pages/manuscripts.html'
    catalogue = catalogue_path.read_text(encoding='utf-8')
    registry = {}
    for alias, identifier in ALIASES.items():
        tag = re.search(r'<tr\b[^>]*id="ljm-' + identifier + r'"[^>]*>.*?</tr>', catalogue)[0]
        assert 'DEH' in re.search(r'data-work="([^"]+)"', tag)[1]
        name = html.unescape(re.search(r'class="ljm-name">(.*?)</span>', tag)[1])
        repository = html.unescape(re.search(r'class="ljm-repository">(.*?)</span>', tag)[1])
        city, shelfmark = name.split(', ', 1)
        registry[alias] = {'displayName': f'{city}, {repository}, {shelfmark}',
            'repository': repository, 'shelfmark': shelfmark, 'catalogueId': identifier,
            'pagination': 'page' if alias == 'Saint Gall 626' else 'folio',
            'provenance': '_pages/manuscripts.html#ljm-' + identifier}
    records, exceptions = [], []
    duplicates = collections.defaultdict(list)
    for row_number, row in enumerate(rows, 2):
        assert None not in row and len(row) == len(reader.fieldnames)
        original = {key: row[key] for key in COLUMNS}
        assert original['manuscrit'] in registry
        match = re.fullmatch(r'(\d+)\.(\d+)', original['section'])
        assert match, (row_number, original['section'])
        book, chapter = map(int, match.groups())
        # The editor explicitly assigned the sole source 0.1 note to the whole prologue.
        if (book, chapter) == (0, 1):
            book, chapter = 1, 0
        target = f'latin-deh{book}-chapter{chapter}'
        location = citations['works']['deh'].get(target)
        if not location or location['status'] != 'verified':
            target = None
            exceptions.append({'row': row_number, 'kind': 'unresolved-location', 'source': original['section']})
        hand = re.fullmatch(r'(\d+)-(\d+)', original['main'])
        issues = []
        expected_prefix = re.search(r'\d+', original['manuscrit'])[0]
        if hand and hand[1] != expected_prefix:
            issues.append('hand-code-prefix-differs-from-manuscript')
            exceptions.append({'row': row_number, 'kind': issues[-1], 'source': original['main']})
        record = {'presentationId': f'ms-annotation-deh-csv-20261027-row-{row_number}',
            'sourceRow': row_number, 'original': original, 'locationTargetId': target,
            'book': book if target else None, 'chapter': chapter if target else None,
            'coveredAlignmentUnitIds': location['alignmentUnitIds'] if target else [], 'issues': issues}
        records.append(record)
        duplicates[tuple(original.values())].append(row_number)
    duplicate_groups = [indices for indices in duplicates.values() if len(indices) > 1]
    dataset = {'schemaVersion': 1, 'convention': 'deh-csv-20261027',
        'source': {'file': '_docs/deh-annotations/source.csv', 'sha256': SOURCE_SHA256, 'recordCount': len(rows),
            'usedColumns': COLUMNS, 'ignoredColumns': reader.fieldnames[5:]},
        'manuscripts': registry, 'records': records}
    report = {'sourceRows': len(rows), 'locatedRows': sum(bool(r['locationTargetId']) for r in records),
        'manuscripts': len(registry), 'chapterLocations': len({r['locationTargetId'] for r in records if r['locationTargetId']}),
        'sourceSha256': SOURCE_SHA256, 'columnsUsed': COLUMNS, 'columnsIgnored': reader.fieldnames[5:],
        'approvedPrologueMapping': {'source': '0.1', 'target': 'latin-deh1-chapter0', 'granularity': 'whole-prologue'},
        'duplicateGroupsInIncludedColumns': duplicate_groups,
        'duplicateExtraRowsPreserved': sum(len(indices) - 1 for indices in duplicate_groups),
        'exceptions': exceptions, 'sourceFilesUnchanged': True,
        'ecaudataRows': sum(r['original']['contenu'].count('\\c{e}') > 0 for r in records),
        'untranscribedPlaceholderRows': sum('[*]' in r['original']['contenu'] for r in records)}
    return {'assets/data/deh-annotations/annotations.json': dataset,
            '_docs/deh-annotations/inventory.json': report}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    options = parser.parse_args()
    for name, data in build().items():
        content = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        target = ROOT / name
        if options.check:
            assert target.read_bytes() == content, 'Stale generated data: ' + name
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        print(name)
