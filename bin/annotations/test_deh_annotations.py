"""Independent checks against the original CSV and canonical DEH chapter XML."""
import csv
import hashlib
import json
import pathlib
import subprocess
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).parents[2]
NS = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'


class DEHAnnotations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'assets/data/deh-annotations/annotations.json').read_text(encoding='utf-8'))
        cls.citations = json.loads((ROOT / 'assets/data/alignment-citations.json').read_text(encoding='utf-8'))

    def test_original_csv_is_byte_exact_and_all_first_five_fields_survive(self):
        file = ROOT / '_docs/deh-annotations/source.csv'
        self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(), self.data['source']['sha256'])
        with file.open(encoding='utf-8-sig', newline='') as stream:
            original = list(csv.DictReader(stream))
        self.assertEqual(len(original), 1917)
        self.assertEqual(len(original), len(self.data['records']))
        for number, (source, record) in enumerate(zip(original, self.data['records']), 2):
            self.assertEqual(record['sourceRow'], number)
            self.assertEqual(record['original'], {key: source[key] for key in self.data['source']['usedColumns']})

    def test_all_chapter_boundaries_match_the_canonical_xml(self):
        seen = 0
        for file in (ROOT / 'assets/xml/deh/Latin').glob('book-*.xml'):
            for chapter in ET.parse(file).iter(NS + 'div2'):
                identifier = chapter.get(XID, '')
                if not identifier.startswith('latin-deh'):
                    continue
                expected = [p.get(XID) for p in chapter.iter(NS + 'p') if p.get(XID)]
                citation = self.citations['works']['deh'][identifier]
                self.assertEqual(citation['alignmentUnitIds'], expected)
                self.assertEqual(citation['status'], 'verified')
                for key, paragraph in [('startCitation', list(chapter.iter(NS + 'p'))[0]), ('endCitation', list(chapter.iter(NS + 'p'))[-1])]:
                    self.assertEqual(citation[key], ''.join(paragraph.find(NS + 'num').itertext()).strip('[] \n'))
                seen += 1
        self.assertEqual(seen, 177)

    def test_existing_josephus_citations_and_annotation_inventory_are_unchanged(self):
        old = json.loads(subprocess.check_output(['git', 'show', '0042341:assets/data/alignment-citations.json'], cwd=ROOT))
        for work in ['antiquities', 'bellum']:
            self.assertEqual(self.citations['works'][work], old['works'][work])
        for key, value in old['works']['deh'].items():
            self.assertEqual(self.citations['works']['deh'][key], value)
        file = '_docs/annotation-source-inventory.json'
        self.assertEqual((ROOT / file).read_bytes(), subprocess.check_output(['git', 'show', '0042341:' + file], cwd=ROOT))

    def test_every_csv_location_has_complete_chapter_coverage(self):
        for row in self.data['records']:
            citation = self.citations['works']['deh'][row['locationTargetId']]
            self.assertEqual(citation['granularity'], 'chapter')
            self.assertEqual(row['coveredAlignmentUnitIds'], citation['alignmentUnitIds'])
            self.assertTrue(row['coveredAlignmentUnitIds'])
            self.assertEqual(row['book'], citation['book'])
            self.assertEqual(row['chapter'], citation['chapter'])


if __name__ == '__main__':
    unittest.main()
