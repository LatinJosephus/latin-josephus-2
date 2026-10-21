"""Regression tests for accepted Whiston Bellum source projection."""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

MODULE = Path(__file__).resolve().parents[1] / "extract-whiston-bellum.py"
SPEC = importlib.util.spec_from_file_location("extract_whiston_bellum", MODULE)
EXTRACTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXTRACTOR)
ROOT = MODULE.parents[2]


def source(number):
    return (ROOT / f"assets/xml/bellum/English/book-{number:02d}.xml").read_bytes()


def fixture(content, paragraph_attributes='sameAs="#latin-bellum1-num1"'):
    return (f'<TEI xmlns="{EXTRACTOR.TEI}"><text><body><div1 n="1" subtype="English" type="book">'
            '<div2 n="0" type="chapter" sameAs="#latin-bellum1-chapter0">'
            f'<p {paragraph_attributes}>{content}</p></div2></div1></body></text></TEI>').encode()


def small(content, expected=(1, 2), **kwargs):
    return EXTRACTOR.extract_document(fixture(content, **kwargs), book_number=1, verify_source=False,
                                       expected_sections=list(expected))


class WhistonBellumExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = {}
        offset = 0
        for book in range(1, 8):
            cls.books[book] = EXTRACTOR.extract_document(source(book), book_number=book, order_offset=offset)
            offset += len(cls.books[book][0])

    def test_all_seven_books_complete_and_all_704_paragraphs_restore_exactly(self):
        total = paragraphs = tokens = 0
        for book, (records, report) in self.books.items():
            contract = EXTRACTOR.CONTRACTS[book]
            self.assertEqual([r['section'] for r in records], list(range(1, contract['sections'] + 1)))
            self.assertEqual(report['counts']['runningWordTokens'], contract['tokens'])
            self.assertEqual(report['counts']['narrativeParagraphs'], contract['paragraphs'])
            self.assertEqual(report['coverage']['rawParagraphSequenceSha256'], report['coverage']['restoredParagraphSequenceSha256'])
            by_id = {r['id']: r for r in records}
            for paragraph in report['paragraphs']:
                restored = ''.join(EXTRACTOR.utf16_slice(by_id[p['recordId']]['text'], p['recordStart'], p['recordEnd'])
                                   if p['kind'] == 'record' else p['text'] for p in paragraph['sourcePieces'])
                self.assertEqual(restored, paragraph['rawText'])
            total += len(records)
            paragraphs += len(report['paragraphs'])
            tokens += report['counts']['runningWordTokens']
        self.assertEqual((total, paragraphs, tokens), (4001, 704, 215072))

    def test_source_contracts_accept_only_lf_crlf_equivalence(self):
        for book in range(1, 8):
            with self.subTest(book=book):
                raw = source(book)
                first, report = EXTRACTOR.extract_document(raw, book_number=book)
                crlf = raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
                windows, windows_report = EXTRACTOR.extract_document(crlf, book_number=book)
                self.assertEqual(first, windows)
                self.assertEqual(report['coverage'], windows_report['coverage'])
                self.assertEqual(windows_report['source']['sha256'], EXTRACTOR.sha(crlf))
                self.assertTrue(windows_report['sourceContract']['verified'])
                with self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'source differs'):
                    EXTRACTOR.extract_document(raw.replace(b'<text ', b'<text altered="yes" ', 1), book_number=book)

    def test_nested_supplied_209_milestone_and_both_annotations_are_preserved(self):
        records, report = self.books[7]
        first, second = records[207:209]
        self.assertEqual(first['section'], 208)
        self.assertEqual(second['section'], 209)
        self.assertEqual([(r['section'], m['start'], m['end']) for r in records for m in r['editorialMarks']],
                         [(208, 157, 262), (209, 0, 154)])
        for record in [first, second]:
            mark = record['editorialMarks'][0]
            self.assertEqual(mark['kind'], 'supplied')
            self.assertEqual(mark['sourceTag'], 'supplied')
            self.assertEqual(mark['sourceAttributes'], EXTRACTOR.SUPPLIED_ATTRIBUTES)
            self.assertEqual(record['text'][mark['start']:mark['end']], mark['text'])
            self.assertEqual(record['phraseBreaks'], [])
            self.assertNotIn('breakBefore', record)
        paragraph = next(p for p in report['paragraphs'] if p['editorialSpans'])
        self.assertEqual(paragraph['sourceId'], '#latin-bellum7-num190')
        self.assertEqual(paragraph['editorialSpans'][0]['text'], EXTRACTOR.SUPPLIED_TEXT)
        self.assertIn(209, [m['section'] for m in paragraph['nieseMarkers']])

    def test_supplied_origin_and_text_cannot_be_reinterpreted(self):
        raw = source(7)
        for old, new in [(b'reason="omitted"', b'reason="lost"'), (b'were slain,', b'were injured,'),
                         (b'https://lexundria.com/j_bj/7.208-7.209/wst', b'https://example.org/')]:
            with self.subTest(change=new), self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'supplied'):
                EXTRACTOR.extract_document(raw.replace(old, new, 1), book_number=7, verify_source=False)

    def test_book_i_preface_and_narrative_stay_adjacent(self):
        records, report = self.books[1]
        self.assertEqual([r['section'] for r in records[28:32]], [29, 30, 31, 32])
        self.assertTrue(all(not r.get('breakBefore') and not r['phraseBreaks'] for r in records))
        self.assertEqual(report['paragraphs'][0]['parentAttributes']['n'], '0')
        self.assertTrue(report['scope']['includesEmbeddedPreface'])
        self.assertEqual(records[0]['readerLink'], {'path': 'bellum-judaicum/', 'params': {'book': 1, 'niese': 1, 'english': 'whiston'}})

    def test_sameas_is_preserved_as_provenance_without_inventing_xml_ids(self):
        for book, (records, report) in self.books.items():
            self.assertTrue(all(r['sourceId'].startswith(f'#latin-bellum{book}-num') for r in records))
            self.assertTrue(all(r['sourceIdentityKind'] == 'sameAs' for r in records))
            self.assertTrue(all(p['sourceAttributes'] == {'sameAs': p['sourceId']} for p in report['paragraphs']))

    def test_book_v_chapter13_missing_type_attribute_is_preserved(self):
        paragraphs = [p for p in self.books[5][1]['paragraphs'] if p['parentAttributes']['n'] == '13']
        self.assertTrue(paragraphs)
        self.assertTrue(all(p['parentAttributes'] == {'n': '13', 'sameAs': '#latin-bellum5-chapter13'} for p in paragraphs))

    def test_original_unicode_offsets_and_xml_entities_restore(self):
        records, report = small('  <milestone unit="niese" n="1"/>𐐀lpha &amp; á, <milestone unit="niese" n="2"/> beta.  ')
        self.assertEqual([r['text'] for r in records], ['𐐀lpha & á,', 'beta.'])
        pieces = report['paragraphs'][0]['sourcePieces']
        first = next(p for p in pieces if p['kind'] == 'record')
        self.assertEqual(first['recordEnd'], len(records[0]['text']) + 1)
        self.assertEqual(EXTRACTOR.utf16_slice(records[0]['text'], 0, first['recordEnd']), records[0]['text'])
        self.assertEqual(report['coverage']['sourceWordSequenceSha256'], report['coverage']['indexedWordSequenceSha256'])

    def test_unmarked_words_or_punctuation_before_first_marker_are_refused(self):
        for prefix in ['Intro ', '.', '1. ']:
            with self.subTest(prefix=prefix), self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'precedes'):
                small(prefix + '<milestone unit="niese" n="1"/>alpha <milestone unit="niese" n="2"/> beta')

    def test_missing_duplicate_out_of_order_or_empty_sections_are_refused(self):
        cases = ['<milestone unit="niese" n="1"/>alpha',
                 '<milestone unit="niese" n="1"/>alpha <milestone unit="niese" n="1"/> beta',
                 '<milestone unit="niese" n="2"/>alpha <milestone unit="niese" n="1"/> beta',
                 '<milestone unit="niese" n="1"/> <milestone unit="niese" n="2"/> beta']
        for content in cases:
            with self.subTest(content=content), self.assertRaises(EXTRACTOR.ExtractionError):
                small(content)

    def test_marker_inside_word_is_refused(self):
        with self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'split or change source words'):
            small('<milestone unit="niese" n="1"/>alpha<mis/>beta'.replace('<mis/>', '<milestone unit="niese" n="2"/>'))

    def test_unknown_substantive_markup_and_milestone_attributes_are_refused(self):
        for inline in ['<note>annotation</note>', '<gap/>', '<del>word</del>', '<milestone unit="chapter" n="2"/>',
                       '<milestone unit="niese" n="3" cert="low"/>', '<milestone unit="niese" n="3">text</milestone>']:
            with self.subTest(inline=inline), self.assertRaises(EXTRACTOR.ExtractionError):
                small('<milestone unit="niese" n="1"/>alpha ' + inline + '<milestone unit="niese" n="2"/> beta')

    def test_original_paragraph_identity_and_source_path_are_required(self):
        for attrs in ['sameAs="#latin-bellum2-num1"', 'xml:id="english-bellum1-num1"', 'sameAs="#latin-bellum1-num1" n="1"']:
            with self.subTest(attrs=attrs), self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'sameAs identity'):
                small('<milestone unit="niese" n="1"/>alpha <milestone unit="niese" n="2"/> beta', paragraph_attributes=attrs)
        with self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'source path differs'):
            EXTRACTOR.extract_document(source(1), book_number=1, source_path='assets/xml/bellum/Latin/book-01.xml')


if __name__ == '__main__':
    unittest.main()
