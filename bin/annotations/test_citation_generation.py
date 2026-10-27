"""Independent small XML fixtures exercise boundaries, gaps and registered spans."""
import importlib.util
import pathlib
import unittest
import subprocess
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('builder', pathlib.Path(__file__).parents[1] / 'build-annotation-citations.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def document(body):
    return ET.ElementTree(ET.fromstring('<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>' + body + '</body></text></TEI>'))


class CitationGeneration(unittest.TestCase):
    def test_protected_corpus_matches_development_git_bytes(self):
        root = pathlib.Path(__file__).parents[2]
        baseline = '519d607b890f76bf48e427529c4278151a124326'
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '-z', baseline, '--', 'assets/xml', 'assets/data',
            'assets/js/dehParallels.js', 'assets/js/dehParallelsCore.js', 'assets/js/dehAntiquitiesCore.js',
            'CNAME', '_config.yml'], cwd=root).decode().strip('\0').split('\0')
        raw = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=root,
            input=''.join(baseline + ':' + p + '\n' for p in paths).encode())
        pos = 0
        for relative in paths:
            end = raw.index(b'\n', pos)
            size = int(raw[pos:end].split()[-1])
            pos = end + 1
            actual, expected = (root / relative).read_bytes(), raw[pos:pos + size]
            if not relative.startswith(('assets/xml/', 'assets/data/')):
                # Unmodified non-corpus files may retain the original Windows
                # checkout's automatic line endings; do not rewrite hosting files.
                actual, expected = actual.replace(b'\r\n', b'\n'), expected.replace(b'\r\n', b'\n')
            self.assertEqual(actual, expected, relative)
            pos += size + 1

    def test_internal_and_final_units_never_use_id_suffix(self):
        tree = document('<p xml:id="latin-book01-num999"><num>[I.i.27]</num> a <milestone unit="niese" n="28"/>b</p><p xml:id="latin-book01-num1"><num>[I.ii.30]</num>last</p>')
        _, coverage = builder.citation_map(tree, {}, 'antiquities')
        self.assertEqual(coverage['latin-book01-num999'], {27, 28})
        self.assertEqual(coverage['latin-book01-num1'], {30})

    def test_lacuna_does_not_fill_missing_sections(self):
        tree = document('<p xml:id="latin-book01-num1"><num>[I.i.1]</num>a<milestone unit="niese" n="4"/>b</p>')
        _, coverage = builder.citation_map(tree, {}, 'antiquities')
        self.assertEqual(builder.intervals(coverage['latin-book01-num1']), [[1, 1], [4, 4]])

    def test_registered_fragments_override_misleading_labels_and_skip_interpolation(self):
        tree = document('<p xml:id="latin-book11-num1"><num>[I.i.999]</num><anchor xml:id="a"/>a<anchor xml:id="b"/>interpolation<anchor xml:id="c"/>c<anchor xml:id="d"/></p>')
        loc = lambda target: {'kind': 'element', 'target': target}
        registry = {'sections': [{'number': 1, 'Latin': {'available': True, 'spans': [
            {'start': loc('a'), 'end': loc('b')}, {'start': loc('b'), 'end': loc('c'), 'role': 'interpolation'}]}},
            {'number': 4, 'Latin': {'available': True, 'spans': [{'start': loc('c'), 'end': loc('d')}]}}]}
        _, coverage = builder.citation_map(tree, registry, 'antiquities')
        self.assertEqual(coverage['latin-book11-num1'], {1, 4})

    def test_apparatus_numbers_do_not_enter_narrative_coverage(self):
        tree = document('<p xml:id="latin-book01-num1"><note><milestone unit="niese" n="99"/></note><num>[I.i.1]</num>a</p>')
        _, coverage = builder.citation_map(tree, {}, 'antiquities')
        self.assertEqual(coverage['latin-book01-num1'], {1})


if __name__ == '__main__':
    unittest.main()
