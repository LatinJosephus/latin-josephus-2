"""Coverage and corruption checks for the deliberately narrow TEI pilot."""

import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET


PILOT = Path(__file__).resolve().parents[1]
REPOSITORY = PILOT.parents[1]
spec = importlib.util.spec_from_file_location("pilot_extract", PILOT / "extract.py")
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)


def fixture(contents: str) -> bytes:
    return (f'<TEI xmlns="{extract.TEI}"><text><body>'
            '<div1 n="1" type="book" subtype="Latin">'
            '<div2 n="0" type="chapter" xml:id="latin-bellum1-chapter0">'
            f'<p>{extract.BOOK_TITLE}</p>{contents}'
            '</div2></div1></body></text></TEI>').encode()


class ExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xml_bytes = (REPOSITORY / extract.SOURCE).read_bytes()
        cls.records, cls.report = extract.extract_document(
            cls.xml_bytes, expected_paragraphs=234, expected_milestones=439)
        cls.by_section = {record["section"]: record for record in cls.records}

    def test_complete_real_source_and_exact_restoration(self):
        self.assertEqual(len(self.records), 673)
        self.assertEqual([r["section"] for r in self.records], list(range(1, 674)))
        self.assertEqual([r["order"] for r in self.records], list(range(673)))
        self.assertTrue(all(r["language"] == "Latin" and r["edition"] == "Cardwell (1837)"
                            for r in self.records))
        counts = self.report["counts"]
        self.assertEqual(counts["citationParagraphs"] + counts["internalMilestones"], 673)
        self.assertEqual(counts["prefixRemovals"],
                         {"niese-label": 234, "chapter-label": 33, "subchapter-label": 200})
        coverage = self.report["coverage"]
        for first, second in (("rawParagraphSequenceSha256", "restoredParagraphSequenceSha256"),
                              ("sourceWordSequenceSha256", "indexedWordSequenceSha256"),
                              ("sourceNonWhitespaceContentSha256", "indexedNonWhitespaceContentSha256")):
            self.assertEqual(coverage[first], coverage[second])

    def test_known_internal_section_has_its_own_text_and_link(self):
        record = self.by_section[87]
        self.assertEqual(record["sourceId"], "latin-bellum1-num86")
        self.assertEqual(record["chapter"], 4)
        self.assertEqual(record["url"], "/bellum-judaicum/?book=1&niese=87")
        self.assertTrue(record["text"].startswith("At Theodorus repente superveniens"))
        self.assertNotIn("At Theodorus repente superveniens", self.by_section[86]["text"])

    def test_editorial_oddities_and_punctuation_are_preserved(self):
        self.assertIn("nortem", self.by_section[23]["text"])
        self.assertTrue(self.by_section[218]["text"].startswith("- EODEM"))
        self.assertTrue(self.by_section[303]["text"].startswith("' ET"))
        self.assertTrue(self.by_section[633]["text"].startswith("6 me miserum"))
        all_text = " ".join(record["text"] for record in self.records)
        self.assertNotIn(extract.BOOK_TITLE, all_text)
        self.assertEqual({entry["kind"] for entry in self.report["excluded"]},
                         {"teiHeader", "standOff", "book-title"})

    def test_source_order_is_preserved_without_numeric_sorting(self):
        source = fixture('<p xml:id="latin-bellum1-num1">[1] primus. '
                         '<milestone unit="niese" n="3"/>tertius. '
                         '<milestone unit="niese" n="2"/>secundus.</p>')
        records, report = extract.extract_document(source, expected_sections=3)
        self.assertEqual([r["section"] for r in records], [1, 3, 2])
        self.assertFalse(report["coverage"]["sourceOrderIsConsecutive"])

    def test_duplicate_missing_and_mismatched_section_ids_are_rejected(self):
        samples = [
            ('<p xml:id="latin-bellum1-num1">[1] prima. '
             '<milestone unit="niese" n="1"/>altera.</p>', "Duplicate Niese"),
            ('<p xml:id="latin-bellum1-num1">[1] prima.</p>', "missing=\\[2\\]"),
            ('<p xml:id="latin-bellum1-num1">[2] prima. '
             '<milestone unit="niese" n="2"/>altera.</p>', "xml:id disagree"),
        ]
        for contents, message in samples:
            with self.subTest(message=message), self.assertRaisesRegex(extract.ExtractionError, message):
                extract.extract_document(fixture(contents), expected_sections=2)

    def test_unknown_content_and_empty_intervals_are_rejected(self):
        samples = [
            ('<p xml:id="latin-bellum1-num1">[1] prima <hi>altera</hi>.</p>', "Unexpected substantive tag"),
            ('<p xml:id="latin-bellum1-num1">[1] prima.</p><p>Do not lose these words.</p>', "Unrecognised unnumbered"),
            ('<p xml:id="latin-bellum1-num1">[1] prima.'
             '<milestone unit="niese" n="2"/></p>', "Empty Niese"),
        ]
        for contents, message in samples:
            with self.subTest(message=message), self.assertRaisesRegex(extract.ExtractionError, message):
                extract.extract_document(fixture(contents), expected_sections=2)

    def test_word_split_at_milestone_is_rejected_for_this_source(self):
        source = fixture('<p xml:id="latin-bellum1-num1">[1] prin'
                         '<milestone unit="niese" n="2"/>cipium.</p>')
        with self.assertRaisesRegex(extract.ExtractionError, "splits or changes a word"):
            extract.extract_document(source, expected_sections=2)

    def test_punctuation_and_internal_whitespace_round_trip(self):
        source = fixture('<p xml:id="latin-bellum1-num1">[1] Quid?  vere: ita! \n'
                         '<milestone unit="niese" n="2"/>  Alterum—nunc. </p>')
        records, report = extract.extract_document(source, expected_sections=2)
        self.assertEqual([r["text"] for r in records], ["Quid?  vere: ita!", "Alterum—nunc."])
        spans = report["paragraphs"][0]["sections"]
        self.assertEqual(spans[0]["trailingWhitespace"], " \n")
        self.assertEqual(spans[1]["leadingWhitespace"], "  ")


class AllBooksExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.extracted = {}
        cls.xml = {}
        for book, expected in extract.BOOK_SPECS.items():
            cls.xml[book] = (REPOSITORY / f"assets/xml/bellum/Latin/book-{book:02}.xml").read_bytes()
            cls.extracted[book] = extract.extract_document(
                cls.xml[book], book_number=book, expected_sections=expected["sections"],
                expected_paragraphs=expected["numberedParagraphs"],
                expected_citation_paragraphs=expected["citationParagraphs"],
                expected_milestones=expected["milestones"])

    def test_all_seven_ranges_are_complete_and_global_order_continues(self):
        combined = []
        for book, (records, report) in self.extracted.items():
            expected = extract.BOOK_SPECS[book]
            with self.subTest(book=book):
                self.assertEqual([r["section"] for r in records], list(range(1, expected["sections"] + 1)))
                self.assertEqual(report["counts"]["numberedParagraphs"], expected["numberedParagraphs"])
                self.assertEqual(report["counts"]["citationParagraphs"] + report["counts"]["internalMilestones"], len(records))
                self.assertTrue(all(r["book"] == book and r["language"] == "Latin"
                                    and r["edition"] == "Cardwell (1837)" for r in records))
                self.assertTrue(all(r["id"] == f"bellum-latin-cardwell-{book}-{r['section']}"
                                    and r["url"] == f"/bellum-judaicum/?book={book}&niese={r['section']}"
                                    for r in records))
            combined.extend(records)
        self.assertEqual(len(combined), 4001)
        self.assertEqual(len({r["id"] for r in combined}), 4001)
        self.assertEqual([r["order"] for r in combined], list(range(4001)))

    def test_every_source_paragraph_recovers_from_final_record_slices(self):
        restored_count = 0
        for book, (records, report) in self.extracted.items():
            source = ET.fromstring(self.xml[book])
            originals = {p.get(extract.XML_ID): "".join(p.itertext())
                         for p in source.findall(f".//{{{extract.TEI}}}body//{{{extract.TEI}}}p")
                         if p.get(extract.XML_ID)}
            by_section = {r["section"]: r for r in records}
            for paragraph in report["paragraphs"]:
                pieces = [paragraph["removedPrefix"]]
                for span in paragraph["sections"]:
                    text = by_section[span["section"]]["text"]
                    part = text[span["recordTextStart"]:span["recordTextEnd"]]
                    pieces.extend([span["leadingWhitespace"], part, span["trailingWhitespace"]])
                self.assertEqual("".join(pieces), originals[paragraph["sourceId"]], paragraph["sourceId"])
                restored_count += 1
        self.assertEqual(restored_count, 704)

    def test_certified_continuations_do_not_create_duplicate_niese_sections(self):
        book3, report3 = self.extracted[3]
        by3 = {r["section"]: r for r in book3}
        self.assertEqual(by3[3]["sourceId"], "latin-bellum3-num1")
        self.assertEqual(by3[4]["sourceId"], "latin-bellum3-num3")
        self.assertTrue(by3[4]["text"].startswith("Invenit igitur solum Vespasianum"))
        self.assertNotIn("Invenit igitur", by3[3]["text"])
        continuation3 = next(p for p in report3["paragraphs"] if p["sourceId"] == "latin-bellum3-num3")
        self.assertFalse(continuation3["establishesNieseStart"])
        self.assertFalse(continuation3["sections"][0]["contributesText"])
        self.assertEqual(continuation3["removedPrefix"], "2. ")

        book6, report6 = self.extracted[6]
        by6 = {r["section"]: r for r in book6}
        self.assertEqual(by6[427]["sourceId"], "latin-bellum6-num420")
        self.assertEqual(by6[427]["text"],
                         "sed nec alienigenis quidem, nisi qui religionis causa venissent.\n\n"
                         "Magna vero haec multitudo ab extraneis congregabatur.")
        continuation6 = next(p for p in report6["paragraphs"] if p["sourceId"] == "latin-bellum6-num427")
        self.assertFalse(continuation6["establishesNieseStart"])
        self.assertEqual(continuation6["sections"][0]["separatorBefore"], "\n\n")
        self.assertEqual(continuation6["removedPrefix"], "4. ")
        self.assertEqual(sum(len(report["paragraphSeparators"]) for _, report in self.extracted.values()), 1)

    def test_continuation_requires_its_existing_prior_anchor(self):
        for book, number in ((3, 3), (6, 427)):
            marker = f'<milestone unit="niese" n="{number}"/>'.encode()
            corrupted = self.xml[book].replace(marker, b"", 1)
            with self.subTest(book=book), self.assertRaisesRegex(extract.ExtractionError, "continuation does not follow"):
                extract.extract_document(corrupted, book_number=book)
        duplicated = self.xml[6].replace(b'>4. Magna vero haec', b'>[427] 4. Magna vero haec', 1)
        with self.assertRaisesRegex(extract.ExtractionError, "Duplicate Niese section 427"):
            extract.extract_document(duplicated, book_number=6)

    def test_wrong_book_identity_is_rejected(self):
        with self.assertRaisesRegex(extract.ExtractionError, "Book division does not match"):
            extract.extract_document(self.xml[2], book_number=1)

    def test_combined_report_hashes_and_book_one_pilot_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            report = extract.build_corpus(REPOSITORY, out)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["counts"]["sections"], 4001)
            self.assertEqual(report["counts"]["numberedParagraphs"], 704)
            self.assertEqual(report["counts"]["citationParagraphs"], 702)
            self.assertEqual(report["counts"]["continuationParagraphs"], 2)
            self.assertEqual(report["counts"]["internalMilestones"], 3299)
            self.assertEqual(report["coverage"]["paragraphsExactlyRestored"], 704)
            combined = []
            for book in report["books"]:
                for field in ("corpus", "extractionReport"):
                    data = (out / book[field]["path"]).read_bytes()
                    self.assertEqual(len(data), book[field]["bytes"])
                    self.assertEqual(hashlib.sha256(data).hexdigest(), book[field]["sha256"])
                combined.extend(json.loads((out / book["corpus"]["path"]).read_bytes()))
            self.assertEqual(combined, json.loads((out / "corpus.json").read_bytes()))
            self.assertEqual(hashlib.sha256((out / "corpus.json").read_bytes()).hexdigest(), report["corpus"]["sha256"])
            self.assertEqual(hashlib.sha256((out / "data/book-01.corpus.json").read_bytes()).hexdigest(),
                             "9a3619160ec2fdd70b910065f190a30553e436a3069045e0cb51e7aae56d1e4c")


if __name__ == "__main__":
    unittest.main()
