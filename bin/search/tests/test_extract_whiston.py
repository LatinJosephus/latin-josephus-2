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
ORDER_STARTS = {"preface": 0, "book-01": 26, "book-02": 346, "book-03": 695,
                "book-04": 1017, "book-05": 1348, "book-06": 1710, "book-07": 2088,
                "book-08": 2482, "book-09": 2902, "book-10": 3193, "book-11": 3474,
                "book-12": 3821, "book-13": 4255, "book-14": 4688, "book-15": 5179, "book-16": 5604, "book-17": 6008,
                "book-18": 6363, "book-19": 6742, "book-20": 7108}
PRIOR_ARTIFACT_HASHES = {
    "book-01.corpus.json": "5d94451f1363230e0578d995ece458dd8a4b40e56064487f1362194de21404f0",
    "book-01.extraction-report.json": "5ff96ccfd1a08a6abdc3a37e6e832db53db7d9f9a7e12c6eb02bfee6130e53a9",
    "book-02.corpus.json": "7000e802415b3246a14e3fb9fc0c5e40490fb8fa31351c228aaf31353b7b663f",
    "book-02.extraction-report.json": "3eab5244d80df012cfc7c5dec46a78be90ba3b805c759c009954eed8cb18f6ab",
    "book-03.corpus.json": "26e09b435952e06b7911a4d985b44ede81bdc291ea10d18a8218f79f340fd36b",
    "book-03.extraction-report.json": "67acd98bdc96a4e357fdfac47276f375f021c5e917f2b42e5c08d151213afa6c",
    "book-04.corpus.json": "108edd83587cf34f2a901a74ba92bd7821f0b64a7555b505a9f7f855b42d1d78",
    "book-04.extraction-report.json": "e771f5e133a471447489a16f08b1d2fedab03356f6543143e9858ee637dae500",
    "book-05.corpus.json": "fb309ee22dc2f98b65d189679657219fc808b00e64fa5737ecb8e7044e876a80",
    "book-05.extraction-report.json": "d59fe5d530f2a5ea401957dc2d1bcdf542670711b98c9d2c2b19b20e670d7d6a",
    "book-06.corpus.json": "142daee893d0f76385ec4da56a3f02d0dbc62a0f2a1ba6d70937bc1840ed22aa",
    "book-06.extraction-report.json": "73f8bb987096e2fae58361f4fe682aba3601d95ad249aa6e7979063adb3906b2",
    "book-07.corpus.json": "e6c7f4848665e900ac0e1afe2cbb8fe4ed69aba048b6406dcf447b3300df4988",
    "book-07.extraction-report.json": "6a88571253d7b8e3730e5aa815d0fd13ec7ae44730424c6d544a85307c9beb81",
    "book-08.corpus.json": "0ecd93f5267d3d3897aa89ea81a13f8134145c1ceafd14987446d39a50bd37f4",
    "book-08.extraction-report.json": "ee24daad593d279c7b8e9dba27bfe0608ffe12c328214e91f5fcf242db0502b3",
    "book-09.corpus.json": "ca43d1c591ae901a2fa63e708b014cd07b840eb0c4b8ad0fd47ab6d3ee6a49da",
    "book-09.extraction-report.json": "3b560d3b506d3d868730d6baf461c086f12ca7bdedb16054d279645915444806",
    "book-10.corpus.json": "030de30df76282de086c78fbcfbafed69b2623fa5dad4d92e2b342e3ae038903",
    "book-10.extraction-report.json": "1adf83a25272f7cef6ac661b05c42ac1036369961774099741e1e741c3b55e27",
    "book-11.corpus.json": "abecea45451d3c3b16134b2baee8eb748cdf269b290c5d2b37b5ab6ee421debd",
    "book-11.extraction-report.json": "676227b0565269bfbb1571e9968441a7a71d5feb129895610410f7feae5346f5",
    "book-12.corpus.json": "383dc20706ae59faf9783d305c3308dca9d965c353173b9cb1f22bc3b82982c0",
    "book-12.extraction-report.json": "8f31bd84d74217aeb4ef3442061dea6abf97f143bd2762c52a51061f4871870e",
    "book-13.corpus.json": "58d4c4b9bc50f18553039d18ff426b357aa055fcb5fc5fe9e332d983f673f9e6",
    "book-13.extraction-report.json": "4f547d03aa6fc7a69d52787d3fafaa65a1246c5cbe5137c29dad7ecdfc9257a5",
    "book-14.corpus.json": "77faa2febc172b5268b92f3251eb81db97c28f995caec6b40eae3e44154eaad7",
    "book-14.extraction-report.json": "cf7b8f9d4d3fe089fcca7d482f1fd3b957e0e42e0c35e164073056166658f041",
    "book-15.corpus.json": "8a9f38dc0227e78c28ee380df4132cbb7ba3effd69ef784bbb8f34f4e6b42a01",
    "book-15.extraction-report.json": "9b3fa3b455af3df3141e6226c7da33a4a0b6dc903a40ce90678c74fb231211d3"
}


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
                       for name in ORDER_STARTS}
        cls.documents = {name: extract.extract_document(data, book_number=1 if name == "preface" else int(name[-2:]),
                                                       preface=name == "preface", order_offset=ORDER_STARTS[name])
                         for name, data in cls.sources.items()}
        cls.pilot = cls.documents["preface"][0] + cls.documents["book-01"][0]
        cls.collection = cls.pilot + [record for book in range(2, 21) for record in cls.documents[f"book-{book:02}"][0]]

    def test_reviewed_pilot_has_346_intervals_and_21994_tokens(self):
        self.assertEqual([r["section"] for r in self.pilot], list(range(1, 347)))
        self.assertEqual([r["order"] for r in self.pilot], list(range(346)))
        self.assertEqual(len({r["id"] for r in self.pilot}), 346)
        self.assertEqual(sum(len(extract.words(r["text"])) for r in self.pilot), 21994)
        for name, expected in {"preface": (26, 1646), "book-01": (320, 20348),
                               "book-02": (349, 23020), "book-03": (322, 20955),
                               "book-04": (331, 22900), "book-05": (362, 23396),
                               "book-06": (378, 28422), "book-07": (394, 28285),
                               "book-08": (420, 29968), "book-09": (291, 19074),
                               "book-10": (281, 18035), "book-11": (347, 20213),
                               "book-12": (434, 25083), "book-13": (433, 25616),
                               "book-14": (491, 29186), "book-15": (425, 26972),
                               "book-16": (404, 23831), "book-17": (355, 23725),
                               "book-18": (379, 24253), "book-19": (366, 21575),
                               "book-20": (268, 14435)}.items():
            records, report = self.documents[name]
            self.assertEqual((len(records), report["counts"]["runningWordTokens"]), expected)
            self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.sources[name]).hexdigest())

    def test_complete_collection_has_7376_intervals_and_470938_tokens(self):
        self.assertEqual(len(self.collection), 7376)
        self.assertEqual(len({r["id"] for r in self.collection}), 7376)
        self.assertEqual([r["order"] for r in self.collection], list(range(7376)))
        self.assertEqual(sum(len(extract.words(r["text"])) for r in self.collection), 470938)
        for book, last in [(2, 349), (3, 322), (4, 331), (5, 362), (6, 378), (7, 394), (8, 420), (9, 291), (10, 281),
                           (11, 347), (12, 434), (13, 433), (14, 491), (15, 425), (16, 404), (17, 355), (18, 379), (19, 366), (20, 268)]:
            records = self.documents[f"book-{book:02}"][0]
            self.assertEqual(sorted(r["section"] for r in records), list(range(1, last + 1)))
            self.assertEqual([r["section"] for r in records], extract.expected_sequence(book, False))
            for record in records:
                self.assertEqual(record["id"], f"antiquities-english-whiston-{book}-{record['section']}")
                self.assertEqual(record["readerLink"]["params"], {"book": book, "niese": record["section"], "english": "whiston"})
                self.assertNotIn("division", record)
                self.assertNotIn("breakBefore", record)
                self.assertTrue(record["text"])
                self.assertEqual(record["textGaps"], [])
                self.assertEqual(record["phraseBreaks"], [])

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
                         if p.findall(f".//{NS}milestone[@unit='niese']") or p.get(XML_ID) == "english-book04-num276b"}
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

    def test_iv_276_retains_its_markerless_paragraph_and_audited_separator(self):
        records, report = self.documents["book-04"]
        record = records[275]
        first = ("It is also a duty to show the roads to those who do not know them, and not to esteem it a matter "
                 "for sport, when we hinder others' advantages, by setting them in a wrong way.")
        second = "In like manner, let no one revile a person blind or dumb."
        self.assertEqual(record["text"], first + "\n\n" + second)
        self.assertEqual(record["sourceIds"], ["english-book04-num276", "english-book04-num276b"])
        self.assertEqual(record["sourceId"], "english-book04-num276")
        self.assertEqual(report["counts"]["continuationParagraphs"], 1)
        continuation = next(p for p in report["paragraphs"] if p["sourceId"] == "english-book04-num276b")
        self.assertEqual(continuation["nieseMarkers"], [])
        self.assertEqual(continuation["recordJoin"], {"kind": "paragraph-separator", "recordId": record["id"],
                         "start": len(first), "end": len(first) + 2, "text": "\n\n"})
        self.assertEqual(continuation["sections"][0]["recordOffset"], len(first) + 2)
        self.assertEqual("".join(utf16_slice(record["text"], p["recordStart"], p["recordEnd"])
                                 for p in continuation["sourcePieces"] if p["kind"] == "record"), second)
        self.assertNotIn("32.", record["text"])

    def test_v_contents_and_repeated_chapter_headings_are_both_excluded(self):
        records, report = self.documents["book-05"]
        headings = [block["text"] for block in report["excludedBlocks"] if block["kind"] == "heading"]
        self.assertEqual(len(headings), 23)
        self.assertEqual(headings[1:12], headings[12:23])
        self.assertEqual(report["counts"]["narrativeParagraphs"], 98)
        self.assertNotIn("Concerning The Fortitude Of Samson", " ".join(r["text"] for r in records))

    def test_viii_255_retains_all_42_prefix_words_with_exact_original_spans(self):
        records, report = self.documents["book-08"]
        record = records[254]
        first = ("Now therefore when he fell upon the country of the Hebrews, he took the strongest cities of Rehoboam's "
                 "kingdom without fighting; and when he had put garrisons in them, he came last of all to Jerusalem.")
        second = ("Now when Rehoboam, and the multitude with him, were shut up in Jerusalem by the means of the army "
                  "of Shishak, and when they besought God to give them victory and deliverance, they could not persuade "
                  "God to be on their side.")
        self.assertEqual(len(extract.words(second)), 42)
        self.assertEqual(record["text"], first + "\n\n" + second)
        self.assertEqual(record["sourceIds"], ["english-book08-num251", "english-book08-num255"])
        self.assertEqual(record["sourceId"], "english-book08-num251")
        self.assertEqual(report["counts"]["continuationParagraphs"], 1)
        continuation = next(p for p in report["paragraphs"] if p["sourceId"] == "english-book08-num255")
        self.assertEqual([m["section"] for m in continuation["nieseMarkers"]], list(range(256, 263)))
        self.assertEqual([s["section"] for s in continuation["sections"]], list(range(255, 263)))
        self.assertEqual(continuation["recordJoin"], {"kind": "paragraph-separator", "recordId": record["id"],
                         "start": 201, "end": 203, "text": "\n\n"})
        self.assertEqual(continuation["continuationOf"], {"recordId": record["id"], "section": 255,
                         "previousSourceId": "english-book08-num251", "nextSourceId": "english-book08-num263",
                         "firstMilestone": 256, "nextSection": 263})
        self.assertEqual(continuation["sections"][0]["recordOffset"], 203)
        self.assertTrue(all("recordOffset" not in section for section in continuation["sections"][1:]))
        pieces = [p for p in continuation["sourcePieces"] if p.get("recordId") == record["id"]]
        self.assertEqual([(p["sourceStart"], p["sourceEnd"], p["recordStart"], p["recordEnd"]) for p in pieces],
                         [(3, 226, 203, 426)])
        self.assertEqual(utf16_slice(record["text"], 203, 426), second)
        self.assertTrue(records[255]["text"].startswith("But Shemaiah the prophet told them"))

    def test_viii_letter_salutation_and_x_bold_words_remain_narrative(self):
        letter, report = self.documents["book-08"]
        self.assertIn("Hiram To King Solomon", letter[52]["text"])
        self.assertEqual(report["counts"]["structuralMarkers"], 2)
        records = self.documents["book-10"][0]
        for section, words in [(184, ["Samaritans"]), (243, ["Number"]), (244, ["weight", "fragment"])]:
            record = records[section - 1]
            for word in words:
                self.assertIn(word, record["text"])
            self.assertEqual(record["editorialMarks"], [])
            self.assertEqual(record["sourceMarkup"], [])
            self.assertEqual(record["phraseBreaks"], [])

    def test_english_iii_240_does_not_inherit_the_latin_omission(self):
        record = self.documents["book-03"][0][239]
        self.assertEqual(record["section"], 240)
        self.assertTrue(record["text"])
        self.assertEqual(record["textGaps"], [])
        self.assertEqual(record["phraseBreaks"], [])

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
        self.assertEqual([r["order"] for r in records], list(range(3474, 3821)))
        self.assertEqual(records[310]["section"], 311)
        self.assertTrue(records[311]["text"].startswith("and Jaddua the high priest"))
        self.assertEqual(records[327]["section"], 342)
        self.assertTrue(records[328]["text"].startswith("But there was now a great disturbance"))
        self.assertEqual(records[341]["section"], 325)
        self.assertTrue(records[342]["text"].startswith("to whom he promised"))
        self.assertEqual(report["coverage"]["sourceWordSequenceSha256"], report["coverage"]["indexedWordSequenceSha256"])

    def test_source_changes_fail_but_crlf_only_representation_is_accepted(self):
        for book in range(1, 21):
            name = f"book-{book:02}"
            original = self.sources[name]
            with self.subTest(book=book), self.assertRaisesRegex(extract.ExtractionError, "accepted source"):
                extract.extract_document(original + b"\n<!-- Unreviewed source change -->", book_number=book)
            crlf_records, _ = extract.extract_document(original.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"), book_number=book,
                                                       order_offset=ORDER_STARTS[name])
            self.assertEqual(crlf_records, self.documents[name][0])

    def test_native_crlf_sources_retain_raw_provenance_and_accept_lf_representations(self):
        cases = [
            (12, 158411, "e28ce3914fe0e764571e049b20b5ddabfc6d3080cf6dd4537522b083be7cc83c", "ba4808e3b5e234c2ec1bbffd3e4b662a78b2fe41c1643be3e4e7e6662d583286"),
            (17, 148192, "29a0a40375396016162920b32462f259cf3791fa6a12b4af1f6d2ed7bd41cca1", "d6056846f61ae43003989a2d799501d5e9edb7c3b407d9292b3c89064df6a0ac"),
            (18, 150720, "db6c960c3d27457e21b4f5cccdf5a389f6d9ecdfd927a53d1379484eeef3c67d", "ba1529509dddf72ec82a5eda63fb95f6d0f8d88dad87c69f5cf7a431536c63fa"),
            (19, 136009, "9ce4e6116a0cbd57823e07cff97559941e9015da79d02dd0ae6b2e9c0877e129", "e025279ffb304a08f2f960845c6dca1e09162188bffd44f541cd787ae0aaf094"),
            (20, 94225, "229c2c47f9c4f6ad19ae3b96aeb8c9fcdbe849bb4a733cf214ad0f133d28bc0e", "8f5437db04d4423b79db151603187f50400a9d41938f94394a8da744842af673"),
        ]
        for book, size, raw_hash, normalized_hash in cases:
            with self.subTest(book=book):
                name = f"book-{book:02}"
                original = self.sources[name]
                report = self.documents[name][1]
                self.assertEqual(len(original), size)
                self.assertEqual(report["source"]["sha256"], raw_hash)
                self.assertEqual(report["source"]["bytes"], size)
                self.assertEqual(report["sourceContract"]["normalizedSHA256"], normalized_hash)
                normalized = original.replace(b"\r\n", b"\n")
                self.assertNotEqual(original, normalized)
                records, lf_report = extract.extract_document(normalized, book_number=book, order_offset=ORDER_STARTS[name])
                self.assertEqual(records, self.documents[name][0])
                self.assertEqual(lf_report["source"]["sha256"], normalized_hash)
                self.assertEqual(lf_report["paragraphs"], report["paragraphs"])

    def test_xii_and_xiv_prefixes_keep_every_word_in_the_preceding_citation(self):
        cases = [
            (12, 147, "english-book12-num145", "english-book12-num148", "The epistle was this:", 4,
             (343, 345, 366, 6, 27)),
            (12, 226, "english-book12-num223", "english-book12-num225",
             "We have met with a certain writing, whereby we have discovered that both the Jews and the Lacedemonians "
             "are of one stock, and are derived from the kindred of Abraham It is but just therefore that you, who are "
             "our brethren, should send to us about any of your concerns as you please.", 53, (61, 63, 345, 6, 288)),
            (14, 237, "english-book14-num236", "english-book14-num237",
             '"In the month Quntius, when Lucius Lentulus and Caius Mercellus were consuls;', 12, (257, 259, 336, 0, 77)),
        ]
        for book, section, previous_id, source_id, prefix, tokens, offsets in cases:
            with self.subTest(book=book, section=section):
                records, report = self.documents[f"book-{book:02}"]
                record = next(item for item in records if item["section"] == section)
                continuation = next(item for item in report["paragraphs"] if item["sourceId"] == source_id)
                start, record_start, record_end, source_start, source_end = offsets
                self.assertEqual(len(extract.words(prefix)), tokens)
                self.assertEqual(record["text"].split("\n\n")[1], prefix)
                self.assertEqual(record["sourceId"], previous_id)
                self.assertEqual(record["sourceIds"], [previous_id, source_id])
                self.assertEqual(continuation["recordJoin"], {"kind": "paragraph-separator", "recordId": record["id"],
                                 "start": start, "end": record_start, "text": "\n\n"})
                pieces = [p for p in continuation["sourcePieces"] if p.get("recordId") == record["id"]]
                self.assertEqual([(p["recordStart"], p["recordEnd"], p["sourceStart"], p["sourceEnd"]) for p in pieces],
                                 [(record_start, record_end, source_start, source_end)])
                self.assertEqual(utf16_slice(record["text"], record_start, record_end), prefix)
                self.assertEqual(continuation["nieseMarkers"][0]["section"], section + 1)
                self.assertEqual(continuation["sections"][0]["section"], section)
                self.assertTrue(all("recordOffset" not in item for item in continuation["sections"][1:]))
                self.assertEqual(record["phraseBreaks"], [])

    def test_xii_bold_epithets_remain_ordinary_narrative(self):
        records = self.documents["book-12"][0]
        for section, text in [(125, "The God"), (157, "The Just")]:
            record = records[section - 1]
            self.assertIn(text, record["text"])
            self.assertEqual(record["editorialMarks"], [])
            self.assertEqual(record["sourceMarkup"], [])
            self.assertEqual(record["phraseBreaks"], [])

    def test_xv_chapter_milestones_are_structural_evidence_without_new_citations_or_gaps(self):
        records, report = self.documents["book-15"]
        markers = [(p["sourceId"], m) for p in report["paragraphs"] for m in p["structuralMarkers"]
                   if m["kind"] == "milestone"]
        expected = [(1, 1), (2, 11), (3, 39), (4, 88), (5, 106), (6, 121), (7, 121),
                    (8, 161), (9, 194), (10, 213), (11, 299), (12, 326), (13, 380)]
        self.assertEqual([(source_id, m["sourceAttributes"]) for source_id, m in markers],
                         [(f"english-book15-num{p}", {"unit": "chapter", "n": str(c)}) for c, p in expected])
        self.assertEqual(report["counts"]["nieseMilestones"], 425)
        self.assertEqual(report["counts"]["structuralMarkers"], 14)
        self.assertEqual(len(records), 425)
        self.assertTrue(all(not r.get("breakBefore") and not r["phraseBreaks"] for r in records))
        for mode in ["remove", "renumber", "change_unit", "move"]:
            root = ET.fromstring(self.sources["book-15"])
            marker = root.find(f".//{NS}milestone[@unit='chapter']")
            parent = next(p for p in root.iter() if marker in list(p))
            if mode == "remove":
                parent.remove(marker)
            elif mode == "renumber":
                marker.set("n", "99")
            elif mode == "change_unit":
                marker.set("unit", "niese")
            else:
                parent.remove(marker)
                root.find(f".//{NS}p[@xml:id='english-book15-num11']", {"xml": "http://www.w3.org/XML/1998/namespace"}).insert(0, marker)
            with self.subTest(mode=mode), self.assertRaises(extract.ExtractionError):
                extract.extract_document(ET.tostring(root), book_number=15, verify_source=False)

    def test_new_chapter_milestones_remain_structure_without_new_citations_or_phrase_gaps(self):
        for book, chapters, structures in [(16, 16, 20), (17, 19, 19), (18, 21, 21), (19, 8, 8), (20, 20, 20)]:
            with self.subTest(book=book):
                records, report = self.documents[f"book-{book:02}"]
                markers = [marker for paragraph in report["paragraphs"] for marker in paragraph["structuralMarkers"]]
                self.assertEqual(len(markers), structures)
                self.assertEqual(sum(marker["kind"] == "milestone" and marker["sourceAttributes"]["unit"] == "chapter"
                                     for marker in markers), chapters)
                self.assertTrue(all(not record["phraseBreaks"] and not record.get("breakBefore") for record in records))
                root = ET.fromstring(self.sources[f"book-{book:02}"])
                marker = root.find(f".//{NS}milestone[@unit='chapter']")
                marker.set("unit", "niese")
                with self.assertRaises(extract.ExtractionError):
                    extract.extract_document(ET.tostring(root), book_number=book, verify_source=False)

    def test_xx_structural_summary_heading_is_excluded_with_its_exact_parent_and_text(self):
        records, report = self.documents["book-20"]
        heading = next(item for item in report["excludedBlocks"] if item["kind"] == "structural-heading")
        self.assertEqual(heading, {"kind": "structural-heading", "element": "head",
            "text": "CONTAINING THE INTERVAL OF TWENTY-TWO YEARS. FROM FADUS THE PROCURATOR TO FLORUS.",
            "sourceAttributes": {"sameAs": "#latin-book20-chapter1-head"},
            "parentAttributes": {"n": "1", "sameAs": "#latin-book20-chapter1", "type": "chapter", XML_ID: "english-book20-chapter1"}})
        self.assertEqual(report["counts"]["excludedStructuralHeadings"], 1)
        self.assertNotIn(heading["text"], "\n".join(record["text"] for record in records))
        self.assertEqual(records[-1]["section"], 268)
        self.assertTrue(records[-1]["text"].endswith("and others are prohibited."))
        for mode in ["remove", "change-text", "change-identity", "move", "nested-markup"]:
            root = ET.fromstring(self.sources["book-20"])
            element = root.find(f".//{NS}head")
            parent = next(item for item in root.iter() if element in list(item))
            if mode == "remove":
                parent.remove(element)
            elif mode == "change-text":
                element.text += " Unreviewed words."
            elif mode == "change-identity":
                element.set("sameAs", "#different-heading")
            elif mode == "move":
                parent.remove(element)
                parent.append(element)
            else:
                ET.SubElement(element, f"{NS}hi").text = "Unreviewed words."
            with self.subTest(mode=mode), self.assertRaises(extract.ExtractionError):
                extract.extract_document(ET.tostring(root), book_number=20, verify_source=False)

    def test_xix_363_and_364_remain_separate_accepted_intervals(self):
        records = self.documents["book-19"][0]
        self.assertEqual([r["section"] for r in records], list(range(1, 367)))
        self.assertTrue(records[362]["text"].startswith("Accordingly he sent Cuspins Fadus"))
        self.assertTrue(records[363]["text"].startswith("But he determined, in the first place,"))
        self.assertEqual(records[362]["sourceId"], records[363]["sourceId"])
        self.assertNotEqual(records[362]["id"], records[363]["id"])
        self.assertEqual(records[363]["readerLink"]["params"], {"book": 19, "niese": 364, "english": "whiston"})

    def test_build_is_reproducible_preserves_books_i_xv_and_publishes_all_twenty_one_sources(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            report = extract.build_corpus(REPOSITORY, Path(first))
            extract.build_corpus(REPOSITORY, Path(second))
            self.assertEqual(report["scope"]["books"], list(range(1, 21)))
            self.assertNotIn("pilot", report["scope"])
            self.assertEqual(report["counts"]["sourceDocuments"], 21)
            self.assertEqual(report["counts"]["runningWordTokens"], 470938)
            self.assertEqual({s["path"] for book in report["books"] for s in book["sources"]},
                             {f"assets/xml/antiquities/English/{name}.xml" for name in ["preface"] + [f"book-{b:02}" for b in range(1, 21)]})
            self.assertEqual(sorted(p.name for p in Path(first).iterdir()),
                             [name for b in range(1, 21) for name in [f"book-{b:02}.corpus.json", f"book-{b:02}.extraction-report.json"]]
                             + ["corpus.json", "extraction-report.json"])
            for file in Path(first).iterdir():
                self.assertEqual(file.read_bytes(), (Path(second) / file.name).read_bytes())
            self.assertEqual(json.loads((Path(first) / "corpus.json").read_text()), self.collection)
            for name, expected in PRIOR_ARTIFACT_HASHES.items():
                self.assertEqual(hashlib.sha256((Path(first) / name).read_bytes()).hexdigest(), expected)

    def test_iv_continuation_cannot_be_removed_reassigned_or_given_a_fake_milestone(self):
        for mode in ["remove", "rename", "move", "milestone"]:
            root = ET.fromstring(self.sources["book-04"])
            continuation = root.find(f".//{NS}p[@xml:id='english-book04-num276b']", {"xml": "http://www.w3.org/XML/1998/namespace"})
            parent = next(p for p in root.iter() if continuation in list(p))
            if mode == "remove":
                parent.remove(continuation)
            elif mode == "rename":
                continuation.set(XML_ID, "english-book04-unreviewed")
            elif mode == "move":
                index = list(parent).index(continuation)
                parent.remove(continuation)
                parent.insert(index + 1, continuation)
            else:
                continuation.insert(0, ET.Element(NS + "milestone", {"unit": "niese", "n": "276"}))
            with self.subTest(mode=mode), self.assertRaises(extract.ExtractionError):
                extract.extract_document(ET.tostring(root), book_number=4, verify_source=False)

    def test_viii_prefix_continuation_cannot_be_removed_reassigned_or_given_a_fake_milestone(self):
        for mode in ["remove_prefix", "rename", "move", "milestone"]:
            root = ET.fromstring(self.sources["book-08"])
            continuation = root.find(f".//{NS}p[@xml:id='english-book08-num255']", {"xml": "http://www.w3.org/XML/1998/namespace"})
            parent = next(p for p in root.iter() if continuation in list(p))
            if mode == "remove_prefix":
                continuation.find(NS + "num").tail = ""
            elif mode == "rename":
                continuation.set(XML_ID, "english-book08-unreviewed")
            elif mode == "move":
                index = list(parent).index(continuation)
                parent.remove(continuation)
                parent.insert(index + 1, continuation)
            else:
                continuation.insert(0, ET.Element(NS + "milestone", {"unit": "niese", "n": "255"}))
            with self.subTest(mode=mode), self.assertRaises(extract.ExtractionError):
                extract.extract_document(ET.tostring(root), book_number=8, verify_source=False)

    def test_xii_xiv_prefixes_cannot_be_removed_reassigned_or_given_fake_milestones(self):
        for book, source_id, section in [(12, "english-book12-num148", 147),
                                         (12, "english-book12-num225", 226),
                                         (14, "english-book14-num237", 237)]:
            for mode in ["remove_prefix", "rename", "move", "milestone"]:
                root = ET.fromstring(self.sources[f"book-{book:02}"])
                continuation = root.find(f".//{NS}p[@xml:id='{source_id}']", {"xml": "http://www.w3.org/XML/1998/namespace"})
                parent = next(p for p in root.iter() if continuation in list(p))
                if mode == "remove_prefix":
                    continuation.text = ""
                    for child in continuation:
                        if child.tag == NS + "milestone":
                            break
                        child.tail = ""
                elif mode == "rename":
                    continuation.set(XML_ID, f"english-book{book:02}-unreviewed")
                elif mode == "move":
                    index = list(parent).index(continuation)
                    parent.remove(continuation)
                    parent.insert(index + 1, continuation)
                else:
                    continuation.insert(0, ET.Element(NS + "milestone", {"unit": "niese", "n": str(section)}))
                with self.subTest(book=book, section=section, mode=mode), self.assertRaises(extract.ExtractionError):
                    extract.extract_document(ET.tostring(root), book_number=book, verify_source=False)


class WhistonBoundaryAndRefusalTests(unittest.TestCase):
    def test_partial_paragraph_continuation_uses_utf16_and_resets_later_record_offsets(self):
        source = fixture(paragraph('<milestone unit="niese" n="255"/>😀 First.', "english-book08-num251") +
                         paragraph('<num>3.</num> 😀 Continued. <milestone unit="niese" n="256"/>Next section.',
                                   "english-book08-num255") +
                         paragraph('<milestone unit="niese" n="263"/>Third.', "english-book08-num263"))
        records, report = extract.extract_document(source, book_number=8, verify_source=False, expected_sections=[255, 256, 263])
        self.assertEqual(records[0]["text"], "😀 First.\n\n😀 Continued.")
        self.assertEqual(records[1]["text"], "Next section.")
        continuation = report["paragraphs"][1]
        self.assertEqual((continuation["recordJoin"]["start"], continuation["recordJoin"]["end"]), (9, 11))
        pieces = [piece for piece in continuation["sourcePieces"] if piece["kind"] == "record"]
        self.assertEqual([(p["recordStart"], p["recordEnd"]) for p in pieces], [(11, 24), (0, 13)])
        self.assertNotIn("recordOffset", continuation["sections"][1])
        self.assertEqual([m["section"] for m in continuation["nieseMarkers"]], [256])

    def test_continuation_record_offsets_count_utf16_code_units(self):
        source = fixture(paragraph('<milestone unit="niese" n="276"/>😀 First.', "english-book04-num276") +
                         paragraph('<num>32.</num> Second.', "english-book04-num276b") +
                         paragraph('<milestone unit="niese" n="277"/>Third.', "english-book04-num277"))
        records, report = extract.extract_document(source, book_number=4, verify_source=False, expected_sections=[276, 277])
        self.assertEqual(records[0]["text"], "😀 First.\n\nSecond.")
        continuation = report["paragraphs"][1]
        self.assertEqual((continuation["recordJoin"]["start"], continuation["recordJoin"]["end"]), (9, 11))
        piece = next(piece for piece in continuation["sourcePieces"] if piece["kind"] == "record")
        self.assertEqual((piece["recordStart"], piece["recordEnd"]), (11, 18))
        self.assertEqual(utf16_slice(records[0]["text"], piece["recordStart"], piece["recordEnd"]), "Second.")

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
            paragraph('<milestone unit="niese" n="27"/>Known <milestone unit="chapter" n="1"/>words.'),
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
