"""Independent XML text/coordinate audit for the 2026-10-25 AJ Latin repair.

No browser/runtime extraction functions are used. Offsets are half-open positions
in XML-parser-normalized body text, including whitespace and annotation text.
They are evidence coordinates, not replacements for the stored DOM boundaries.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
CERT = '_docs/aj-latin-reconciliation/certified-boundaries.json'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
BOOKS = [3, 9, 14, 15, 16, 17, 18, 20]

def sha(b):
    return hashlib.sha256(b).hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def norm(s):
    return re.sub(r'\s+', ' ', re.sub(r'\[\s*\d+\s*\]', '', s)).strip()

def records_sha(layer):
    return sha(json.dumps(layer['records'], sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())

class Source:
    def __init__(self, path):
        self.bytes = Path(path).read_bytes()
        self.root = ET.fromstring(self.bytes)
        self.body = self.root.find('.//{*}body')
        self.positions, self.parents, self.paths, self.chunks = {}, {}, {}, []
        self.length = 0
        def append(text):
            self.chunks.append(text or '')
            self.length += len(text or '')
        def walk(e, p):
            begin = self.length
            self.paths[id(e)] = p
            append(e.text)
            for i, c in enumerate(e):
                self.parents[id(c)] = e
                walk(c, p + [i])
                append(c.tail)
            self.positions[id(e)] = (begin, self.length)
        walk(self.body, [])
        self.text = ''.join(self.chunks)

    def locate(self, point):
        e = self.body
        for i in point['path']:
            e = list(e)[i]
        return e

    def point(self, point):
        e = self.locate(point)
        offset = self.positions[id(e)][point['side'] in ('after', 'end')]
        parent = e
        while parent is not None and not parent.get(XMLID):
            parent = self.parents.get(id(parent))
        return {'path': point['path'], 'side': point['side'],
                'tag': e.tag.split('}')[-1], 'attributes': dict(e.attrib),
                'nearest_xml_id': parent.get(XMLID) if parent is not None else None,
                'body_codepoint_offset': offset,
                'body_utf16_offset': len(self.text[:offset].encode('utf-16-le')) // 2,
                'before': self.text[max(0, offset-70):offset],
                'after': self.text[offset:offset+70]}

    def section(self, section):
        if not section['available']:
            assert not section['spans'] and section['note']
            return {'available': False, 'spans': [], 'text': '', 'text_sha256': sha(b'')}
        spans, pieces = [], []
        for span in section['spans']:
            start, end = self.point(span['start']), self.point(span['end'])
            # Same label exclusion performed by the runtime, independently
            # resolved in XML rather than through the runtime's DOM helpers.
            end_e = self.locate(span['end'])
            effective_end = end['body_codepoint_offset']
            if span['end']['side'] == 'before' and end_e.tag.endswith('}milestone') and end_e.get('unit') == 'niese':
                parent = self.parents[id(end_e)]
                siblings = list(parent)
                i = siblings.index(end_e)
                if i > 0:
                    prev = siblings[i-1]
                    numbers = re.findall(r'\d+', ''.join(prev.itertext()))
                    if prev.tag.endswith('}num') and not (prev.tail or '').strip() and numbers and int(numbers[-1]) == int(end_e.get('n')):
                        effective_end = self.positions[id(prev)][0]
            a, b = start['body_codepoint_offset'], effective_end
            assert a < b, (section['number'], a, b)
            excluded = []
            for e in self.body.iter():
                if e.get(XMLID) in section.get('excludedParagraphs', []):
                    x, y = self.positions[id(e)]
                    if x < b and y > a:
                        excluded.append((max(a, x), min(b, y)))
            text, cursor = '', a
            for x, y in sorted(excluded):
                text += self.text[cursor:x]
                cursor = y
            text += self.text[cursor:b]
            pieces.append(text)
            spans.append({'start': start, 'end': end,
                          'effective_end_codepoint_offset': b,
                          'effective_end_utf16_offset': len(self.text[:b].encode('utf-16-le')) // 2,
                          'excluded_body_intervals': excluded,
                          'raw_text': text, 'text': norm(text),
                          'text_sha256': sha(norm(text).encode())})
        text = norm(''.join(pieces))
        return {'available': True, 'spans': spans, 'text': text, 'text_sha256': sha(text.encode())}

def current_components(root, layer):
    sources = {b: Source(root / f'assets/xml/antiquities/Latin/book-{b:02}.xml') for b in BOOKS}
    result = []
    for r in layer['records']:
        for c in r['components']:
            result.append({'id': c['component_id'], 'deh_id': r['id'],
                           'book': c['frozen_target']['book'],
                           'sections': [{'number': s['number'], **sources[c['frozen_target']['book']].section(s)} for s in c['sections']['Latin']]})
    return result

def capture(args):
    root = Path(args.root).resolve()
    layer = read(root / 'assets/data/deh-aj-display.v1.json')
    frozen = read(root / 'assets/data/deh-josephus-concordance.json')
    oracle = read(args.prior_oracle)
    old = {b: Source(Path(args.historical_root) / f'book-{b:02}.xml') for b in BOOKS}
    current = {b: Source(root / f'assets/xml/antiquities/Latin/book-{b:02}.xml') for b in BOOKS}
    topology = {}
    for b in BOOKS:
        signature = lambda src: [(e.tag, dict(e.attrib)) for e in src.body.iter()]
        assert signature(old[b]) == signature(current[b]), ('Source topology changed', b)
        expected = layer['source_sha256'][f'assets/xml/antiquities/Latin/book-{b:02}.xml']
        assert sha(old[b].bytes) == expected
        topology[str(b)] = {'same_body_elements_attributes_and_order': True,
                            'old_sha256': expected, 'current_sha256': sha(current[b].bytes)}
    components = []
    for r in layer['records']:
        f = next(f for f in frozen['records'] if f['id'] == r['id'])
        deh = Source(root / f"assets/xml/deh/Latin/book-{f['deh']['book']:02}.xml")
        deh_element = next(e for e in deh.body.iter() if e.get(XMLID) == r['deh_xml_id'])
        for c in r['components']:
            b = c['frozen_target']['book']
            selections = []
            for s in c['sections']['Latin']:
                a, z = old[b].section(s), current[b].section(s)
                prior = oracle[f"Latin:{b}:{s['number']}"]
                assert a['text'] == prior['text'] and a['available'] == prior['available'], ('Historical independent oracle disagreement', b, s['number'])
                selections.append({'number': s['number'], 'boundary': s,
                                   'old': a, 'current': z,
                                   'selected_text_changed': a['text'] != z['text'],
                                   'raw_selected_text_changed': [x['raw_text'] for x in a['spans']] != [x['raw_text'] for x in z['spans']]})
            components.append({'id': c['component_id'], 'deh_id': r['id'],
                               'deh_citation': f['deh']['citation'], 'deh_xml_id': r['deh_xml_id'],
                               'deh_latin_text': norm(''.join(deh_element.itertext())),
                               'target': c['frozen_target'], 'raw_segment': c['raw_segment'],
                               'display_note': c.get('display_note'), 'annotations': c['annotations'],
                               'classification': 'BOUNDARIES_RETAINED_TEXT_REVERIFIED',
                               'sections': selections})
    result = {'schema': 1, 'base_commit': '5bb301c1b41d63c89c33a79826fc62892ac3890f',
              'historical_baseline': layer['baseline_commit'],
              'historical_layer_sha256': sha((root / 'assets/data/deh-aj-display.v1.json').read_bytes()),
              'unchanged_records_sha256': records_sha(layer),
              'prior_oracle_sha256': sha(Path(args.prior_oracle).read_bytes()),
              'coordinate_policy': 'half-open XML-parser-normalized body text; Unicode codepoints and UTF-16 code units; includes whitespace and annotation text',
              'source_topology': topology, 'components': components,
              'editorial_questions': [],
              'current_components': current_components(root, layer)}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'components':len(components),'section_occurrences':sum(len(c['sections']) for c in components),
                      'selected_text_changes':sum(s['selected_text_changed'] for c in components for s in c['sections']),
                      'raw_selected_text_changes':sum(s['raw_selected_text_changed'] for c in components for s in c['sections'])},indent=2))

def verify(root):
    root = Path(root).resolve()
    cert = read(root / CERT)
    layer = read(root / 'assets/data/deh-aj-display.v1.json')
    assert len(cert['components']) == 44 and len({c['deh_id'] for c in cert['components']}) == 31
    assert not cert['editorial_questions']
    assert records_sha(layer) == cert['unchanged_records_sha256'], 'Frozen targets, witness notes, exclusions or section boundaries changed'
    assert current_components(root, layer) == cert['current_components'], 'Certified Latin boundaries, selected passages or coordinates changed'
    for book, record in cert['source_topology'].items():
        assert sha((root / f'assets/xml/antiquities/Latin/book-{int(book):02}.xml').read_bytes()) == record['current_sha256']
    print(json.dumps({'status': 'PASS', 'DEH_records': 31, 'AJ_components': 44,
                      'Latin_section_occurrences': sum(len(c['sections']) for c in cert['components']),
                      'method': 'Independent ElementTree walk; exact text, path, side, boundary identity and codepoint/UTF16 coordinate match',
                      'new_editorial_adjudication': False}, indent=2))

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default=str(ROOT))
    p.add_argument('--capture', action='store_true')
    p.add_argument('--historical-root')
    p.add_argument('--prior-oracle')
    p.add_argument('--output')
    args = p.parse_args()
    if args.capture:
        assert args.historical_root and args.prior_oracle and args.output
        capture(args)
    else:
        verify(args.root)
