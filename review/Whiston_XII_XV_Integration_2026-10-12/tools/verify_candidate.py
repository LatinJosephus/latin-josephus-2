"""Read-only independent source/oracle/display-evidence verification.

Run with Python 3 from any recovered candidate; no canonical checkout is needed.
This script creates no files unless --report names an owned output file.
"""
import argparse, hashlib, json, pathlib, re, xml.etree.ElementTree as ET

PACK = pathlib.Path(__file__).resolve().parent.parent
ROOT = PACK.parents[1]
NS = '{http://www.tei-c.org/ns/1.0}'
sha = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
norm = lambda s: re.sub(r'\s+', ' ', s).strip()

def extract(data):
    """Walk the XML in document order; do not use the reader's DOM Range code."""
    div = ET.fromstring(data).find('.//' + NS + 'body/' + NS + 'div1')
    parts, marks = [], []
    position = 0
    def emit(s):
        nonlocal position
        if s:
            parts.append(s)
            position += len(s)
    def walk(e):
        tag = e.tag.removeprefix(NS)
        if tag == 'milestone' and e.get('unit') == 'niese':
            marks.append((int(e.get('n')), position))
            return
        if tag in ('num', 'note'):
            return
        emit(e.text)
        for child in e:
            walk(child)
            emit(child.tail)
    walk(div)
    text = ''.join(parts)
    return [(n, norm(text[start:marks[i+1][1] if i+1 < len(marks) else len(text)]))
            for i, (n, start) in enumerate(marks)]

def verify():
    initial = load(PACK / 'BASELINE.json')['tracked_file_hashes']
    allowed = {'.gitattributes', 'assets/js/renderTei.js',
               'bin/reader-corpus-integrity.mjs', '_docs/reader-corpus-integrity.json'}
    allowed |= {f'assets/xml/antiquities/English/book-{n:02}.xml' for n in range(12,16)}
    changed = []
    for path, expected in initial.items():
        if sha((ROOT / path).read_bytes()) != expected:
            assert path in allowed, ('Unexpected source change', path)
            changed.append(path)
    assert set(changed) == allowed
    renderer = (ROOT / 'assets/js/renderTei.js').read_text(encoding='utf-8')
    assert 'Whiston English: exact Niese interval.' not in renderer
    enabled = re.search(r'exactNieseBooks: \[([^\]]+)\]', renderer).group(1)
    assert json.loads('['+enabled+']') == ['preface'] + list(range(1,16))
    reconstructed = []
    for r in load(PACK / 'SOURCE_INVENTORY.json'):
        data = (ROOT / r['file']).read_bytes()
        frozen = (PACK / 'certified' / f'book-{r["book"]:02}.xml').read_bytes()
        original = (PACK / 'certified' / f'approved-original-book-{r["book"]:02}.xml').read_bytes()
        assert data == frozen and sha(data) == r['certified_sha256']
        restored = re.sub(rb'<milestone unit="niese" n="\d+"/>', b'', data)
        assert restored == original and sha(original) == r['baseline_sha256']
        reconstructed.append({'book':r['book'], 'certified_SHA256':sha(data),
                              'approved_reconstructed_SHA256':sha(restored), 'byte_exact':True})
    oracle = load(PACK / 'INTERVAL_ORACLE.json')
    expected = {(r['book'],r['number']):r for r in oracle}
    assert len(expected) == len(oracle) == 5604
    for book in ['preface'] + [str(n) for n in range(1,16)]:
        filename = 'preface.xml' if book == 'preface' else f'book-{int(book):02}.xml'
        rows = extract((ROOT / 'assets/xml/antiquities/English' / filename).read_bytes())
        saved = [r for r in oracle if r['book'] == book]
        assert [n for n,_ in rows] == [r['number'] for r in saved]
        for n,text in rows:
            e = expected[(book,n)]
            assert text == e['text'] and sha(text.encode()) == e['sha256'], (book,n)
    all_actual = []
    for file, count in [('CUMULATIVE_A_ENGLISH_QA.json',1710),
                        ('CUMULATIVE_B_ENGLISH_QA.json',2111),
                        ('NEW_XII_XV_ENGLISH_QA.json',1783)]:
        report = load(PACK / file)
        assert report['status'] == 'SECTIONS-PASS' and len(report['sections']) == count
        assert not report['errors'] and not report['requests']
        assert report['rendererSHA256'] == sha((ROOT/'assets/js/renderTei.js').read_bytes())
        all_actual += report['sections']
    keys = [(r['book'],r['number']) for r in all_actual]
    assert len(set(keys)) == len(keys) == 5604 and set(keys) == set(expected)
    for r in all_actual:
        e = expected[(r['book'],r['number'])]
        assert r['passed'] and r['allNarrativeVisible'] and r['GreekLatinPresentationUnchanged']
        assert r['expectedSHA256'] == r['renderedSHA256'] == e['sha256']
        assert r['opening'] == e['opening'] and r['closing'] == e['closing']
        assert r['notes'] == len(e['notes'])
    # These are preserved executed browser observations, not fresh browser runs.
    for file in ['REGRESSION_QA.json','BAMBERG_QA.json','UI_QA.json',
                 'BOOK_NAVIGATION_QA.json','AUXILIARY_QA.json','NATIVE_LODGE_BROWSER_QA.json']:
        assert load(PACK / file)['status'] == 'PASS', file
    return {'status':'PASS', 'source_changes':sorted(changed), 'unchanged_tracked_files':len(initial)-len(changed),
            'fresh_independent_XML_intervals':5604,'executed_display_records_reconciled':5604,
            'new_intervals':1783,'reconstruction':reconstructed,
            'qualification':'Browser evidence inspected and reconciled; use browser tools to reproduce live display checks.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=pathlib.Path)
    args = parser.parse_args()
    result = verify()
    if args.report:
        args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
