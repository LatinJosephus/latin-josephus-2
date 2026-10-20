"""Whiston source preservation, explicit boundaries and refusal tests."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET


SEARCH = Path(__file__).resolve().parents[1]
REPOSITORY = SEARCH.parents[1]
spec = importlib.util.spec_from_file_location("whiston_extract", SEARCH / "extract-whiston.py")
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)
NS = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def utf16_slice(text: str, start: int, end: int) -> str:
    return text.encode("utf-16-le")[start * 2:end * 2].decode("utf-16-le")


def fixture(contents: str) -> bytes:
    return (f'<TEI xmlns="{extract.TEI}"><teiHeader><p>Unindexed metadata.</p></teiHeader>'
            '<text><body><note>William Whiston (1737)</note><div1><div2>'
            f'{contents}</div2></div1></body></text></TEI>').encode("utf-8")


def paragraph(contents: str, source_id: str = "english-book01-test") -> str:
    return f'<p xml:id="{source_id}">{contents}</p>'


def small(contents: str, expected: list[int] | None = None):
    return extract.extract_document(fixture(contents), verify_source=False,
                                    expected_sections=[27] if expected is None else expected)


class WhistonAcceptedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {name: (REPOSITORY / f"assets/xml/antiquities/English/{name}.xml").read_bytes()
                       for name in ["preface", "book-01", "book-09", "book-11"]}
        cls.documents = {name: extract.extract_document(data, book_number=1 if name == "preface" else int(name[-2:]),
                                                       preface=name == "preface", order_offset=26 if name == "book-01" else 0)
                         for name, data in cls.sources.items()}
        cls.pilot = cls.documents["preface"][0] + cls.documents["book-01"][0]

    def test_reviewed_pilot_has_346_intervals_and_21994_tokens(self):
        self.assertEqual([r["section"] for r in self.pilot], list(range(1, 347)))
        self.assertEqual([r["order"] for r in self.pilot], list(range(346)))
        self.assertEqual(len({r["id"] for r in self.pilot}), 346)
        self.assertEqual(sum(len(extract.words(r["text"])) for r in self.pilot), 21994)
        for name, expected in {"preface": (26, 1646), "book-01": (320, 20348),
                               "book-09": (291, 19074), "book-11": (347, 20213)}.items():
            records, report = self.documents[name]
            self.assertEqual((len(records), report["counts"]["runningWordTokens"]), expected)
            self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.sources[name]).hexdigest())

    def test_proem_reader_edition_and_narrative_boundary(self):
        self.assertEqual([r["section"] for r in self.pilot if r.get("breakBefore")], [27])
        for record in self.pilot:
            proem = record["section"] <= 26
            book = "preface" if proem else 1
            self.assertEqual(record["language"], "English")
            self.assertEqual(record["edition"], "Whiston")
            self.assertEqual(record["readerLink"], {"path": "antiquities/", "params":
                             {"book": book, "niese": record["section"], "english": "whiston"}})
            self.assertEqual(record["url"], f"/antiquities/?book={book}&niese={record['section']}&english=whiston")
            self.assertEqual(record.get("sourceDivision"), "proem" if proem else None)
            self.assertEqual(record.get("division"), "proem" if proem else None)
            self.assertEqual(record["citation"].get("proem", False), proem)
        self.assertTrue(self.pilot[26]["text"].startswith("In the beginning God created the heaven and the earth."))

    def test_every_record_and_exclusion_restores_actual_xml_paragraphs(self):
        for name, (records, report) in self.documents.items():
            by_id = {r["id"]: r for r in records}
            root = ET.fromstring(self.sources[name])
            originals = {p.get(XML_ID): "".join(p.itertext()) for p in root.findall(f".//{NS}body//{NS}p")
                         if p.findall(f".//{NS}milestone[@unit='niese']")}
            self.assertEqual(len(originals), len(report["paragraphs"]))
            for paragraph in report["paragraphs"]:
                original = originals[paragraph["sourceId"]]
                cursor, restored = 0, ""
                for piece in paragraph["sourcePieces"]:
                    self.assertEqual(piece["sourceStart"], cursor)
                    part = (utf16_slice(by_id[piece["recordId"]]["text"], piece["recordStart"], piece["recordEnd"])
                            if piece["kind"] == "record" else piece["text"])
                    self.assertEqual(part, utf16_slice(original, piece["sourceStart"], piece["sourceEnd"]))
                    self.assertEqual(hashlib.sha256(part.encode()).hexdigest(), piece["textSHA256"])
                    restored += part
                    cursor = piece["sourceEnd"]
                self.assertEqual(restored, original)
                self.assertEqual(cursor, len(original.encode("utf-16-le")) // 2)

    def test_only_punctuation_before_accepted_first_marker_is_excluded(self):
        records, report = self.documents["preface"]
        paragraph = next(p for p in report["paragraphs"] if p["sourceId"] == "english-preface-num5")
        prefix = [p for p in paragraph["sourcePieces"] if p.get("reason") == "pre-marker-label-punctuation"]
        self.assertEqual([(p["text"], p["sourceStart"], p["sourceEnd"]) for p in prefix], [(" . ", 6, 9)])
        self.assertTrue(records[4]["text"].startswith("Now I have undertaken the present work"))
        punctuated, _ = small('<p xml:id="test"><num>[1.1.]</num> . '
                             '<milestone unit="niese" n="27"/>. First; second—third! </p>')
        self.assertEqual(punctuated[0]["text"], ". First; second—third!")

    def test_ix_footnotes_are_excluded_and_narrative_adjacency_survives(self):
        records, report = self.documents["book-09"]
        text = " ".join(r["text"] for r in records)
        notes = [p for paragraph in report["paragraphs"] for p in paragraph["sourcePieces"]
                 if p.get("reason") == "whiston-footnote"]
        self.assertEqual(len(notes), 7)
        self.assertNotIn("Dr. Hudson", text)
        self.assertNotIn("What M. Le Clerc pretends", text)
        self.assertNotIn("CONCERNING THE WICKEDNESS", text)
        self.assertIn("Elisha also sent a hasty message to Joram, and exhorted him", text)
        self.assertIn("Joram, who was the son of a murderer, had sent one", text)
        self.assertIn("an epistle from Elijah the prophet, which declared", text)
        self.assertEqual([r["section"] for r in records if 51 <= r["section"] <= 109], list(range(51, 110)))
        self.assertTrue(all(not r.get("breakBefore") and not r["phraseBreaks"] for r in records))

    def test_xi_records_preserve_physical_order_at_three_non_numeric_seams(self):
        records, report = self.documents["book-11"]
        expected = list(range(1, 312)) + list(range(326, 343)) + list(range(312, 326)) + list(range(343, 348))
        self.assertEqual([r["section"] for r in records], expected)
        self.assertEqual([r["order"] for r in records], list(range(347)))
        self.assertEqual(records[310]["section"], 311)
        self.assertTrue(records[311]["text"].startswith("and Jaddua the high priest"))
        self.assertEqual(records[327]["section"], 342)
        self.assertTrue(records[328]["text"].startswith("But there was now a great disturbance"))
        self.assertEqual(records[341]["section"], 325)
        self.assertTrue(records[342]["text"].startswith("to whom he promised"))
        self.assertEqual(report["coverage"]["sourceWordSequenceSha256"], report["coverage"]["indexedWordSequenceSha256"])

    def test_source_changes_fail_but_crlf_only_representation_is_accepted(self):
        original = self.sources["book-01"]
        with self.assertRaisesRegex(extract.ExtractionError, "accepted source"):
            extract.extract_document(original.replace(b"In the beginning", b"At the beginning", 1))
        crlf_records, _ = extract.extract_document(original.replace(b"\n", b"\r\n"), order_offset=26)
        self.assertEqual(crlf_records, self.documents["book-01"][0])

    def test_build_is_reproducible_and_publishes_only_the_two_pilot_sources(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            report = extract.build_corpus(REPOSITORY, Path(first))
            extract.build_corpus(REPOSITORY, Path(second))
            self.assertEqual(report["scope"]["books"], [1])
            self.assertEqual(report["counts"]["sourceDocuments"], 2)
            self.assertEqual(report["counts"]["runningWordTokens"], 21994)
            self.assertEqual({s["path"] for s in report["books"][0]["sources"]},
                             {f"assets/xml/antiquities/English/{name}.xml" for name in ["preface", "book-01"]})
            self.assertEqual(sorted(p.name for p in Path(first).iterdir()),
                             ["book-01.corpus.json", "book-01.extraction-report.json", "corpus.json", "extraction-report.json"])
            for file in Path(first).iterdir():
                self.assertEqual(file.read_bytes(), (Path(second) / file.name).read_bytes())
            self.assertEqual(json.loads((Path(first) / "corpus.json").read_text()), self.pilot)


class WhistonBoundaryAndRefusalTests(unittest.TestCase):
    def test_inline_content_and_utf16_source_offsets_preserve_original_characters(self):
        records, report = small(paragraph('<num>[I.i.27]</num> <milestone unit="niese" n="27"/>'
                                         '😀 A<hi>br</hi>aham <note type="whiston-footnote">excluded π</note>'
                                         'and <emph>Isaac</emph><lb/>.'))
        self.assertEqual(records[0]["text"], "😀 Abraham and Isaac.")
        pieces = report["paragraphs"][0]["sourcePieces"]
        selected = [p for p in pieces if p["kind"] == "record"]
        self.assertEqual(selected[0]["recordStart"], 0)
        self.assertEqual(selected[0]["recordEnd"], 4)
        self.assertEqual("".join(utf16_slice(records[0]["text"], p["recordStart"], p["recordEnd"]) for p in selected),
                         "😀 Abraham and Isaac.")

    def test_unknown_or_unclassified_structure_is_refused(self):
        samples = [
            paragraph('<milestone unit="niese" n="27"/>Known <unclear>word</unclear>.'),
            paragraph('Unassigned words <milestone unit="niese" n="27"/>Known.'),
            paragraph('<milestone unit="niese" n="27"/>Known <lb>hidden words</lb>.'),
            paragraph('<milestone unit="niese" n="27"/>Known <note>unreviewed note</note>.'),
            '<head>Unclassified hidden words</head>' + paragraph('<milestone unit="niese" n="27"/>Known.'),
            '<milestone unit="niese" n="1"/>' + paragraph('<milestone unit="niese" n="27"/>Known.'),
            '<p>Unmarked narrative.</p>' + paragraph('<milestone unit="niese" n="27"/>Known.'),
            paragraph('<milestone unit="niese" n="27"/>Known.') + '<p xml:id="unassigned">More narrative.</p>',
        ]
        for source in samples:
            with self.subTest(source=source), self.assertRaises(extract.ExtractionError):
                small(source)

    def test_empty_duplicate_reordered_and_mid_word_boundaries_are_refused(self):
        samples = [
            '<milestone unit="niese" n="27"/><milestone unit="niese" n="28"/>Second.',
            '<milestone unit="niese" n="27"/>First. <milestone unit="niese" n="27"/>Second.',
            '<milestone unit="niese" n="28"/>First. <milestone unit="niese" n="27"/>Second.',
            '<milestone unit="niese" n="27"/>Abra<milestone unit="niese" n="28"/>ham.',
        ]
        for source in samples:
            with self.subTest(source=source), self.assertRaises(extract.ExtractionError):
                small(paragraph(source), [27, 28])

    def test_duplicate_source_ids_are_refused(self):
        with self.assertRaisesRegex(extract.ExtractionError, "Duplicate.*source ID"):
            small(paragraph('<milestone unit="niese" n="27"/>First.') +
                  paragraph('<milestone unit="niese" n="28"/>Second.'), [27, 28])


if __name__ == "__main__":
    unittest.main()
