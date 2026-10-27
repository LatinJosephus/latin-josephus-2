"""Generate presentation citations from frozen TEI and certified identity registries.

No XML is written. Numeric alignment-ID suffixes are navigation keys only.
Run from any directory; --check rejects stale generated files.
"""
import argparse
import collections
import hashlib
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
NS = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def intervals(numbers):
    result = []
    for n in sorted(set(numbers)):
        if result and n == result[-1][1] + 1:
            result[-1][1] = n
        else:
            result.append([n, n])
    return result


def citation_map(tree, registry, work):
    """Intersect actual narrative characters with observed/certified section spans.

    Character positions exclude apparatus, notes and citation labels. This avoids
    attributing a preceding section merely because whitespace precedes a label.
    Explicit certified spans take precedence over inherited printed labels.
    """
    starts, ends, chunks, ids = {}, {}, [], {}
    clock = 0
    paragraphs = []

    def visit(node, paragraph=None, excluded=False):
        nonlocal clock
        starts[node] = clock
        clock += 1
        tag = node.tag.removeprefix(NS)
        excluded = excluded or tag in ('teiHeader', 'note', 'app', 'rdg', 'num', 'gap')
        if node.get(XMLID):
            ids[node.get(XMLID)] = node
        if tag == 'p' and (node.get(XMLID) or '').startswith('latin-'):
            paragraph = node
            paragraphs.append(node)
        if node.text and not excluded and paragraph is not None:
            if node.text.strip():
                chunks.append((clock, clock + len(node.text), paragraph))
            clock += len(node.text)
        for child in node:
            visit(child, paragraph, excluded)
            if child.tail and not excluded and paragraph is not None:
                if child.tail.strip():
                    chunks.append((clock, clock + len(child.tail), paragraph))
                clock += len(child.tail)
        ends[node] = clock
        clock += 1

    visit(tree.getroot())
    body = tree.find('.//' + NS + 'body')
    body_nodes = set(body.iter())
    paragraphs = [p for p in paragraphs if p in body_nodes]
    sections = {s['number']: s.get('Latin', {}) for s in registry.get('sections', [])}

    def point(locator):
        if locator.get('kind') == 'book-end':
            return ends[body]
        node = ids.get(locator.get('target'))
        if node is None:
            raise ValueError('Unresolved certified locator: ' + repr(locator))
        if locator.get('kind') == 'element-edge':
            for step in locator['edge'].split('/'):
                tag, ordinal = re.fullmatch(r'([\w-]+)\[(\d+)\]', step).groups()
                candidates = [c for c in node if c.tag == NS + tag and
                              (tag != 'milestone' or not registry.get('structuralMilestoneUnits') or
                               c.get('unit') in registry['structuralMilestoneUnits'])]
                node = candidates[int(ordinal) - 1]
        return ends[node] if locator.get('kind') == 'paragraph-end' else starts[node]

    spans = []
    explicit = any('spans' in s for s in sections.values())
    if explicit:
        # Mixing guessed starts with certified fragments would bridge lacunae or
        # give interpolations the identity of a neighbouring section.
        for number, section in sections.items():
            for span in section.get('spans', []):
                if span.get('role') == 'interpolation' or not section.get('available'):
                    continue
                spans.append((point(span['start']), point(span['end']), number))
    else:
        boundaries = []
        suppressed = {(s['paragraph'], s['label']) for s in registry.get('suppressedLatinLabels', [])}
        declared = {n for n, s in sections.items() if s.get('start')}
        for paragraph in paragraphs:
            apparatus_nodes = {child for note in paragraph.iter() if note.tag in (NS + 'note', NS + 'app', NS + 'rdg') for child in note.iter()}
            if work == 'bellum':
                match = re.match(r'\s*\[(\d+)\]', paragraph.text or '')
            else:
                label = next((c for c in paragraph if c.tag == NS + 'num'), None)
                label_text = ''.join(label.itertext()).strip() if label is not None else ''
                match = re.search(r'(\d+)\]$', label_text)
                if (paragraph.get(XMLID), label_text) in suppressed:
                    match = None
            if match:
                number = int(match[1])
                if number not in declared and (not sections or number in sections and sections[number].get('available')):
                    boundaries.append((starts[paragraph], number))
            for marker in paragraph.iter(NS + 'milestone'):
                if marker.get('unit') == 'niese' and marker not in apparatus_nodes:
                    number = int(marker.get('n'))
                    if not sections or number in sections and sections[number].get('available'):
                        boundaries.append((starts[marker], number))
        boundaries.extend((point(s['start']), n) for n, s in sections.items() if s.get('start') and s.get('available'))
        boundaries = sorted(set(boundaries))
        for i, (start, number) in enumerate(boundaries):
            end = boundaries[i + 1][0] if i + 1 < len(boundaries) else ends[body]
            spans.append((start, end, number))

    coverage = collections.defaultdict(set)
    paragraph_set = set(paragraphs)
    for start, end, number in spans:
        for left, right, paragraph in chunks:
            if left < end and right > start and paragraph in paragraph_set:
                coverage[paragraph.get(XMLID)].add(number)
    return paragraphs, coverage


def build():
    result = {'schema': 1, 'provenance': {}, 'works': {}}
    inventory = {'schema': 1, 'works': {}, 'records': []}
    exceptions = []
    for work in ('antiquities', 'bellum', 'deh'):
        mappings = {}
        counts = collections.Counter()
        for path in sorted((ROOT / 'assets/xml' / work / 'Latin').glob('*.xml')):
            relative = path.relative_to(ROOT).as_posix()
            result['provenance'][relative] = digest(path)
            tree = ET.parse(path)
            registry_path = ROOT / 'assets/xml' / work / 'niese' / (path.stem + '.json')
            registry = {}
            provenance = [relative]
            if registry_path.exists():
                registry = json.loads(registry_path.read_text(encoding='utf-8'))
                key = registry_path.relative_to(ROOT).as_posix()
                result['provenance'][key] = digest(registry_path)
                provenance.append(key)
            if work == 'deh':
                paragraphs = [p for p in tree.iter(NS + 'p') if (p.get(XMLID) or '').startswith('latin-deh')]
                coverage = {}
            else:
                paragraphs, coverage = citation_map(tree, registry, work)
            book_match = re.search(r'book-(\d+)', path.name)
            book = int(book_match[1]) if book_match else 'preface'
            for p in paragraphs:
                unit_id = p.get(XMLID)
                entry = {'book': book, 'intervals': intervals(coverage.get(unit_id, [])),
                         'citationSystem': 'deh' if work == 'deh' else 'niese', 'provenance': provenance}
                if work == 'deh':
                    label = p.find(NS + 'num')
                    entry['citation'] = ''.join(label.itertext()).strip('[] \n') if label is not None else None
                    match = re.fullmatch(r'([IVX]+)\.(\d+)\.(\d+)', entry['citation'] or '')
                    if match:
                        entry['chapter'], entry['unit'] = int(match[2]), int(match[3])
                entry['status'] = 'verified' if entry['intervals'] or entry.get('citation') else 'unresolved'
                mappings[unit_id] = entry
            if work != 'deh':
                for chapter in tree.iter(NS + 'div2'):
                    if not (chapter.get(XMLID) or '').startswith('latin-'):
                        continue
                    numbers = set().union(*(coverage.get(p.get(XMLID), set()) for p in chapter.iter(NS + 'p')))
                    mappings[chapter.get(XMLID)] = {'book': book, 'intervals': intervals(numbers),
                        'citationSystem': 'niese', 'status': 'verified' if numbers else 'unresolved', 'provenance': provenance}
            if work == 'deh':
                # Chapter-level annotation locations have their own verified targets.
                # They must not be assigned to a chapter's first alignment unit.
                for chapter in tree.iter(NS + 'div2'):
                    chapter_id = chapter.get(XMLID) or ''
                    if not chapter_id.startswith('latin-deh'):
                        continue
                    unit_ids = [p.get(XMLID) for p in chapter.iter(NS + 'p')
                                if p.get(XMLID) in mappings]
                    chapter_number = int(chapter.get('n'))
                    labels = [mappings[unit]['citation'] for unit in unit_ids]
                    citation = 'Prologue' if chapter_number == 0 else None
                    if chapter_number and labels:
                        prefixes = {label.rsplit('.', 1)[0] for label in labels}
                        if len(prefixes) == 1:
                            citation = prefixes.pop()
                    mappings[chapter_id] = {'book': book, 'chapter': chapter_number,
                        'citationSystem': 'deh', 'granularity': 'chapter',
                        'citation': citation, 'alignmentUnitIds': unit_ids,
                        'startCitation': labels[0] if labels else None,
                        'endCitation': labels[-1] if labels else None,
                        'intervals': [], 'provenance': provenance,
                        'status': 'verified' if citation and unit_ids else 'unresolved'}
                result['works'][work] = mappings
                continue
            witnesses = {w.get(XMLID): ''.join(w.itertext()) for w in tree.iter(NS + 'witness')}
            occurrences = collections.Counter()
            for app in tree.iter(NS + 'app'):
                counts['sourceGroups'] += 1
                children = list(app)
                target = children[0].get('source', '').removeprefix('#') if children else ''
                # The first reading is the passage incipit, even where its source
                # is missing or mis-tagged. Preserve malformed references; do not
                # infer repairs from incipit labels or neighbouring manuscripts.
                for rdg in children[1:]:
                    source = rdg.get('source', '')
                    siglum = source.removeprefix('#')
                    occurrences[(target, siglum)] += 1
                    raw = ''.join(rdg.itertext())
                    record = {'work': work, 'alignmentUnitId': target, 'siglum': siglum,
                              'sourceBook': book,
                              'originalId': rdg.get(XMLID) or app.get(XMLID), 'notation': raw,
                              'occurrence': occurrences[(target, siglum)], 'sourceFile': relative,
                              'witnessLabel': witnesses.get(siglum), 'originalAlignmentReference': children[0].get('source'),
                              'originalManuscriptReference': rdg.get('source')}
                    inventory['records'].append(record)
                    counts['manuscriptReadings'] += 1
                    counts['sourceIds'] += bool(record['originalId'])
                    for symbol in ('¤', '@', '£', '¢', '#', '§', '...', '…', '¬', '¦'):
                        counts[symbol] += raw.count(symbol)
                    if target not in mappings or mappings[target]['status'] != 'verified':
                        exceptions.append({'work': work, 'unit': target, 'reason': 'No verified narrative coverage'})
                    if siglum not in witnesses:
                        exceptions.append({'work': work, 'siglum': siglum, 'reason': 'Witness missing from listWit'})
        result['works'][work] = mappings
        inventory['works'][work] = dict(counts)
    inventory['citationExceptions'] = list({json.dumps(e, sort_keys=True): e for e in exceptions}.values())
    return {'assets/data/alignment-citations.json': result,
            '_docs/annotation-source-inventory.json': inventory}


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--check', action='store_true')
    options = args.parse_args()
    for relative, data in build().items():
        output = ROOT / relative
        content = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
        if options.check:
            assert output.read_bytes() == content.encode('utf-8'), 'Stale generated data: ' + relative
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content.encode('utf-8'))
        print(relative)
