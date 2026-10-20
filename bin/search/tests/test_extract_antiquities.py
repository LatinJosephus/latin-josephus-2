"""Citation, source preservation and refusal tests for Antiquities I–XX."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET


SEARCH = Path(__file__).resolve().parents[1]
REPOSITORY = SEARCH.parents[1]
spec = importlib.util.spec_from_file_location("antiquities_extract", SEARCH / "extract-antiquities.py")
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)
NS = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def utf16_slice(text: str, start: int, end: int) -> str:
    return text.encode("utf-16-le")[start * 2:end * 2].decode("utf-16-le")


def paragraph(text: str, section: int = 27) -> str:
    return f'<p xml:id="latin-book01-num{section}"><num>[I.i.{section}]</num>{text}</p>'


def fixture(contents: str) -> bytes:
    return (f'<TEI xmlns="{extract.TEI}"><teiHeader><p>Metadata outside the Latin text.</p></teiHeader>'
            '<text xml:id="book-01-text"><body><note>Bamberg Msc. Class. 78</note>'
            '<div1 n="I" type="book" subtype="Latin" xml:id="latin-book01">'
            '<div2 n="1" type="chapter" xml:id="latin-book01-chapter1">'
            f'{contents}</div2></div1></body></text></TEI>').encode("utf-8")


def small(source: bytes, last: int = 27):
    return extract.extract_document(source, book_number=1, order_offset=0, expected_range=[27, last])


class AntiquitiesRealSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {key: (REPOSITORY / f"assets/xml/antiquities/Latin/{key}.xml").read_bytes()
                       for key in ["preface"] + [f"book-{n:02}" for n in range(1, 6)]}
        cls.documents = {key: extract.extract_document(data, book_number=1 if key == "preface" else int(key[-2:]),
                                                       preface=key == "preface",
                                                       expected_counts=extract.PREFACE_SPEC if key == "preface"
                                                       else extract.BOOK_SPECS[int(key[-2:])])
                         for key, data in cls.sources.items()}
        cls.records = [r for records, _ in cls.documents.values() for r in records]
        cls.by_citation = {r["citationLabel"]: r for r in cls.records}

    def test_full_tranche_has_1710_citations_and_67657_original_word_tokens(self):
        self.assertEqual(len(self.records), 1710)
        self.assertEqual(len({r["id"] for r in self.records}), 1710)
        self.assertEqual([r["order"] for r in self.records], list(range(1710)))
        self.assertEqual(sum(len(extract.words(r["text"])) for r in self.records), 67657)
        expected = {"preface": (26, 986), "book-01": (320, 13223), "book-02": (349, 13570),
                    "book-03": (322, 12793), "book-04": (331, 13180), "book-05": (362, 13905)}
        for key, (units, tokens) in expected.items():
            records, report = self.documents[key]
            self.assertEqual(len(records), units)
            self.assertEqual(report["counts"]["runningWordTokens"], tokens)
            self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.sources[key]).hexdigest())

    def test_proem_has_its_own_reader_route_and_a_boundary_before_the_narrative(self):
        proem, _ = self.documents["preface"]
        self.assertEqual([r["section"] for r in proem], list(range(1, 27)))
        for record in proem:
            self.assertEqual(record["book"], 1)
            self.assertEqual(record["division"], "proem")
            self.assertTrue(record["citation"]["proem"])
            self.assertEqual(record["readerLink"], {"path": "antiquities/", "params": {"book": "preface", "niese": record["section"]}})
            self.assertEqual(record["url"], f"/antiquities/?book=preface&niese={record['section']}")
            self.assertNotIn("chapter", record)
        narrative = self.by_citation["I.27"]
        self.assertTrue(narrative["breakBefore"])
        self.assertNotIn("division", narrative)
        self.assertEqual(narrative["url"], "/antiquities/?book=1&niese=27")
        self.assertTrue(narrative["text"].startswith("In principio creauit deus"))

    def test_all_finished_record_slices_restore_every_source_paragraph_exactly(self):
        for key, (records, report) in self.documents.items():
            by_section = {r["section"]: r for r in records}
            root = ET.fromstring(self.sources[key])
            originals = {p.get(XML_ID): "".join(p.itertext()) for p in root.findall(f".//{NS}body//{NS}p") if p.get(XML_ID)}
            self.assertEqual(len(originals), len(report["paragraphs"]))
            for paragraph in report["paragraphs"]:
                source = originals[paragraph["sourceId"]]
                cursor, restored = 0, ""
                for segment in paragraph["segments"]:
                    self.assertEqual(segment["sourceTextStart"], cursor)
                    if segment["kind"] == "source-text":
                        part = by_section[segment["section"]]["text"][segment["recordTextStart"]:segment["recordTextEnd"]]
                        self.assertEqual(hashlib.sha256(part.encode()).hexdigest(), segment["textSha256"])
                    else:
                        self.assertIn(segment["kind"], ("excluded-note", "excluded-label", "trimmed-edge-whitespace"))
                        part = segment["text"]
                    self.assertEqual(part, source[segment["sourceTextStart"]:segment["sourceTextEnd"]])
                    restored += part
                    cursor = segment["sourceTextEnd"]
                self.assertEqual(restored, source)
                self.assertEqual(cursor, len(source))
                self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), paragraph["rawTextSha256"])
            for first, second in (("rawParagraphSequenceSha256", "restoredParagraphSequenceSha256"),
                                  ("sourceWordSequenceSha256", "indexedWordSequenceSha256"),
                                  ("sourceNonWhitespaceContentSha256", "displayNonWhitespaceContentSha256")):
                self.assertEqual(report["coverage"][first], report["coverage"][second])

    def test_six_continuation_labels_do_not_create_false_niese_starts(self):
        expected = {"II.95": "latin-book02-num95", "III.178": "latin-book03-num179",
                    "IV.106": "latin-book04-num107", "IV.155": "latin-book04-num156",
                    "IV.276": "latin-book04-num276b", "V.32": "latin-book05-num33"}
        for citation, continuation_id in expected.items():
            record = self.by_citation[citation]
            self.assertIn(continuation_id, record["sourceIds"])
            self.assertNotEqual(record["sourceId"], continuation_id)
            self.assertEqual(record["text"].count("\n\n"), 1)
        self.assertTrue(self.by_citation["III.179"]["text"].startswith("mirari siquidem"))
        self.assertTrue(self.by_citation["IV.107"]["text"].startswith("Mazianitas"))
        self.assertEqual(self.by_citation["IV.276"]["text"].split("\n\n")[-1], "Nemo blasphemet absentem")
        self.assertEqual(sum(r["counts"]["continuationParagraphs"] for _, r in self.documents.values()), 6)

    def test_nested_sentence_markers_establish_sections_102_and_103(self):
        marked = {r["section"]: m for r in self.documents["book-01"][0]
                  for m in r["sourceMarkup"] if m["kind"] == "s"}
        self.assertEqual(set(marked), {101, 102, 103})
        for section, mark in marked.items():
            record = self.by_citation[f"I.{section}"]
            self.assertEqual(utf16_slice(record["text"], mark["start"], mark["end"]), mark["text"])
        self.assertTrue(self.by_citation["I.102"]["text"].startswith("Moneo tamen"))

    def test_all_19_additions_23_deletions_and_nested_refs_remain_searchable(self):
        marks = [m for r in self.records for m in r["editorialMarks"]]
        self.assertEqual(sum(m["kind"] == "add" for m in marks), 19)
        self.assertEqual(sum(m["kind"] == "del" for m in marks), 23)
        self.assertEqual(sum(m["kind"] == "ref" for r in self.records for m in r["sourceMarkup"]), 3)
        first = self.by_citation["I.34"]
        self.assertTrue(first["text"].startswith("Post septimam uero diem"))
        self.assertIn("quem<...>", first["text"])
        for record in self.records:
            for mark in record["editorialMarks"] + record["sourceMarkup"]:
                self.assertEqual(utf16_slice(record["text"], mark["start"], mark["end"]), mark["text"])
                self.assertEqual(mark["kind"], mark["sourceTag"])
                self.assertIsInstance(mark["sourceAttributes"], dict)
        self.assertTrue(any(m["sourceAttributes"] == {"hand": "post", "place": "interlinear"} for m in marks))
        self.assertTrue(any(m["sourceAttributes"] == {"hand": "orig", "rend": "strikethrough"} for m in marks))

    def test_six_literal_dot_gaps_are_conservative_boundaries_but_double_period_is_not(self):
        expected = {"I.34": [(257, 260)], "I.53": [(355, 358)], "II.80": [(360, 365)],
                    "II.93": [(95, 98)], "IV.84": [(245, 247), (251, 252)]}
        observed = {r["citationLabel"]: [(m["start"], m["end"]) for m in r["textGaps"] if m["kind"] == "literal-dots"]
                    for r in self.records if any(m["kind"] == "literal-dots" for m in r["textGaps"])}
        self.assertEqual(observed, expected)
        for citation, spans in observed.items():
            record = self.by_citation[citation]
            self.assertEqual(record["phraseBreaks"], [a for a, _ in spans])
            for gap in record["textGaps"]:
                self.assertEqual(utf16_slice(record["text"], gap["start"], gap["end"]), gap["text"])
        self.assertIn("triginta..", self.by_citation["I.149"]["text"])
        self.assertEqual(self.by_citation["I.149"]["phraseBreaks"], [])
        self.assertTrue(all(not r["textGaps"] for r in self.documents["preface"][0]))

    def test_only_iii_240_is_empty_and_its_omission_is_explicit(self):
        self.assertEqual([r["citationLabel"] for r in self.records if not r["text"]], ["III.240"])
        gap = self.by_citation["III.240"]
        self.assertEqual(gap["phraseBreaks"], [0])
        self.assertEqual(gap["textGaps"], [{"kind": "tei-gap", "start": 0, "end": 0, "text": "", "sourceAttributes": {"reason": "omitted"}}])
        self.assertEqual(gap["sourceId"], "latin-book03-num239")
        self.assertEqual([r["citationLabel"] for r in self.records if r.get("breakBefore")], ["I.27", "III.240", "III.241"])
        self.assertEqual(self.documents["book-03"][1]["coverage"]["allowedEmptySections"], [240])
        self.assertFalse(self.documents["book-03"][1]["coverage"]["allSectionTextsNonempty"])

    def test_notes_titles_and_reference_labels_are_excluded_with_provenance(self):
        latin = "\n".join(r["text"] for r in self.records)
        for excluded in ("annotation illisible", "arcam dicit", "EXPLICITPRAEFATIO", "INCIP. LIB.", "[I.i.27]"):
            self.assertNotIn(excluded, latin)
        self.assertEqual(sum(r["counts"]["excludedAnnotationNotes"] for _, r in self.documents.values()), 12)
        note_segments = [s for _, report in self.documents.values() for p in report["paragraphs"] for s in p["segments"] if s["kind"] == "excluded-note"]
        self.assertEqual(len(note_segments), 12)
        self.assertTrue(all(s["sourceAttributes"].get("source") in extract.NOTE_SOURCES for s in note_segments))

    def test_combined_build_is_deterministic_and_preserves_the_prepared_i_to_xv_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sentinel = root / "previous-work.json"
            sentinel.write_bytes(b"preserved earlier collection")
            output = root / "data" / extract.COLLECTION
            report = extract.build_corpus(REPOSITORY, output)
            original = {p.name: p.read_bytes() for p in output.iterdir()}
            extract.build_corpus(REPOSITORY, output)
            self.assertEqual(original, {p.name: p.read_bytes() for p in output.iterdir()})
            self.assertEqual(len(original), 42)
            self.assertEqual(report["counts"]["sections"], 7283)
            self.assertEqual(report["counts"]["sourceDocuments"], 21)
            self.assertEqual(report["counts"]["identityRegistries"], 10)
            self.assertEqual(report["counts"]["canonicalSections"], 7273)
            self.assertEqual(report["counts"]["citationUnits"], 7275)
            self.assertEqual(report["counts"]["runningWordTokens"], 265023)
            self.assertEqual([b["book"] for b in report["books"]], list(range(1, 21)))
            self.assertEqual(report["books"][0]["source"]["path"], "assets/xml/antiquities/Latin/book-01.xml")
            self.assertEqual([s["path"] for s in report["books"][0]["additionalSources"]], ["assets/xml/antiquities/Latin/preface.xml"])
            self.assertEqual(sentinel.read_bytes(), b"preserved earlier collection")
            for book in report["books"]:
                for kind in ("corpus", "extractionReport"):
                    data = (root / book[kind]["path"]).read_bytes()
                    self.assertEqual(hashlib.sha256(data).hexdigest(), book[kind]["sha256"])
                    self.assertEqual(len(data), book[kind]["bytes"])
            self.assertEqual(json.loads(original["corpus.json"]), sum([json.loads(original[f"book-{b:02}.corpus.json"]) for b in range(1, 21)], []))
            self.assertEqual(json.loads(original["corpus.json"])[:1710], self.records)
            for b in range(1, 16):
                for suffix in ("corpus.json", "extraction-report.json"):
                    name = f"book-{b:02}.{suffix}"
                    self.assertEqual(original[name], (SEARCH / extract.OUTPUT_PREFIX / name).read_bytes(), name)
            for b in report["books"][10:]:
                self.assertEqual(b["additionalSources"], [b["identityRegistry"]])
                self.assertEqual(b["identityRegistry"]["sha256"],
                                 hashlib.sha256((REPOSITORY / b["identityRegistry"]["path"]).read_bytes()).hexdigest())

    def test_invalid_final_source_cannot_partially_replace_existing_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_directory = root / "assets/xml/antiquities/Latin"
            source_directory.mkdir(parents=True)
            for key, source in self.sources.items():
                if key == "book-05":
                    source = source.replace(b'<milestone unit="niese" n="362"', b'<milestone unit="niese" n="999"', 1)
                (source_directory / f"{key}.xml").write_bytes(source)
            destination = root / "output"
            destination.mkdir()
            (destination / "corpus.json").write_bytes(b"previous complete tranche")
            with self.assertRaisesRegex(extract.ExtractionError, "consecutive Niese"):
                extract.build_corpus(root, destination)
            self.assertEqual({p.name: p.read_bytes() for p in destination.iterdir()}, {"corpus.json": b"previous complete tranche"})


class AntiquitiesSecondBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {b: (REPOSITORY / f"assets/xml/antiquities/Latin/book-{b:02}.xml").read_bytes()
                       for b in range(6, 11)}
        cls.documents = {b: extract.extract_document(data, book_number=b, expected_counts=extract.BOOK_SPECS[b])
                         for b, data in cls.sources.items()}
        cls.records = [r for rows, _ in cls.documents.values() for r in rows]
        cls.by_citation = {r["citationLabel"]: r for r in cls.records}

    def test_second_batch_exact_counts_order_and_accepted_source_bindings(self):
        expected = {6: (378, 16460), 7: (394, 15801), 8: (420, 17810), 9: (232, 9209), 10: (281, 10921)}
        self.assertEqual(len(self.records), 1705)
        self.assertEqual([r["order"] for r in self.records], list(range(1710, 3415)))
        self.assertEqual(sum(len(extract.words(r["text"])) for r in self.records), 70201)
        for b, (count, tokens) in expected.items():
            rows, report = self.documents[b]
            self.assertEqual((len(rows), report["counts"]["runningWordTokens"]), (count, tokens))
            self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.sources[b]).hexdigest())
            self.assertEqual(report["source"]["path"], f"assets/xml/antiquities/Latin/book-{b:02}.xml")

    def test_all_new_running_paragraphs_restore_exactly_with_excluded_notices(self):
        for b, (rows, report) in self.documents.items():
            by_section = {r["section"]: r for r in rows}
            root = ET.fromstring(self.sources[b])
            originals = {p.get(XML_ID): "".join(p.itertext()) for p in root.findall(f".//{NS}body//{NS}p")
                         if p.find(NS + "num") is not None}
            self.assertEqual(len(originals), len(report["paragraphs"]))
            for audit in report["paragraphs"]:
                raw = originals[audit["sourceId"]]
                cursor, restored = 0, ""
                for segment in audit["segments"]:
                    self.assertEqual(segment["sourceTextStart"], cursor)
                    part = (by_section[segment["section"]]["text"][segment["recordTextStart"]:segment["recordTextEnd"]]
                            if segment["kind"] == "source-text" else segment["text"])
                    self.assertEqual(part, raw[segment["sourceTextStart"]:segment["sourceTextEnd"]])
                    restored += part
                    cursor = segment["sourceTextEnd"]
                self.assertEqual(restored, raw)
                self.assertEqual(cursor, len(raw))
            self.assertEqual(report["coverage"]["sourceWordSequenceSha256"], report["coverage"]["indexedWordSequenceSha256"])
            self.assertEqual(report["coverage"]["sourceNonWhitespaceContentSha256"], report["coverage"]["indexedNonWhitespaceContentSha256"])

    def test_chapter_only_and_displaced_labels_use_explicit_milestones(self):
        for citation, source_id in (("VI.269", "latin-book06-num271"), ("VI.271", "latin-book06-num272"),
                                    ("X.150", "latin-book10-num151")):
            self.assertEqual(self.by_citation[citation]["sourceId"], source_id)
            report = self.documents[self.by_citation[citation]["book"]][1]
            audit = next(p for p in report["paragraphs"] if p["sourceId"] == source_id)
            self.assertTrue(audit["establishesNieseStart"])
            self.assertEqual(audit["sections"][0]["startKind"], "milestone")
        self.assertEqual(self.by_citation["VII.1"]["sourceId"], "latin-book07-num")

    def test_book_viii_continuations_do_not_move_latin_to_printed_next_label(self):
        first = self.by_citation["VIII.186"]
        self.assertTrue(first["text"].endswith("\n\nHuc ergo causa delectationis egrediebatur"))
        self.assertEqual(first["sourceIds"][-1], "latin-book08-num187")
        self.assertNotIn("Huc ergo", self.by_citation["VIII.187"]["text"])
        second = self.by_citation["VIII.255"]
        self.assertEqual(second["sourceIds"][-1], "latin-book08-num255")
        self.assertEqual(second["text"].count("\n\n"), 1)
        self.assertEqual(self.documents[8][1]["counts"]["continuationParagraphs"], 2)

    def test_vii_omitted_units_have_separate_gap_evidence_and_no_english_tokens(self):
        rows, report = self.documents[7]
        self.assertEqual([r["section"] for r in rows if not r["text"]], list(range(69, 100)))
        for n in range(69, 100):
            record = self.by_citation[f"VII.{n}"]
            self.assertTrue(record["breakBefore"])
            self.assertEqual(record["phraseBreaks"], [0])
            self.assertEqual(record["textGaps"], [{"kind": "tei-gap", "start": 0, "end": 0, "text": "", "sourceAttributes": {"reason": "omitted"}}])
        self.assertTrue(self.by_citation["VII.100"]["breakBefore"])
        notices = [s for p in report["paragraphs"] for s in p["segments"] if s["kind"] == "excluded-omission-notice"]
        self.assertEqual(len(notices), 6)
        self.assertTrue(all(s["text"] == " Omitted in Bamberg MS" and s["sourceTag"] == "#text" and s["sourceAttributes"] == {} for s in notices))
        self.assertNotIn("Omitted", " ".join(r["text"] for r in rows))

    def test_ix_missing_range_is_declared_without_synthetic_records(self):
        rows, report = self.documents[9]
        self.assertEqual([r["section"] for r in rows], list(range(1, 51)) + list(range(110, 292)))
        self.assertEqual(report["coverage"]["completeRange"], [1, 291])
        self.assertEqual(report["coverage"]["missingSections"], list(range(51, 110)))
        self.assertFalse(report["coverage"]["sourceOrderIsConsecutive"])
        notice = next(e for e in report["excluded"] if e["kind"] == "lacuna-notice")
        self.assertEqual(notice["text"], "[Lacuna 51–109; cf. Blatt, p. 67]")
        self.assertEqual(notice["sourceId"], "latin-book09-num51")
        self.assertEqual(notice["missingSections"], list(range(51, 110)))
        after = self.by_citation["IX.110"]
        self.assertTrue(after["breakBefore"])
        self.assertTrue(after["text"].startswith("[…] Nam uerba uesaniae locutus est"))
        self.assertEqual(after["textGaps"], [{"kind": "literal-ellipsis", "start": 1, "end": 2, "text": "…"}])
        self.assertNotIn("Blatt", " ".join(r["text"] for r in rows))

    def test_x108_is_an_empty_source_interval_without_a_fabricated_gap(self):
        record = self.by_citation["X.108"]
        self.assertEqual(record["text"], "")
        self.assertEqual(record["textGaps"], [])
        self.assertEqual(record["phraseBreaks"], [])
        self.assertTrue(record["breakBefore"])
        self.assertTrue(self.by_citation["X.109"]["breakBefore"])
        self.assertEqual(record["emptySource"], {
            "kind": "empty-source-interval", "sourcePath": "assets/xml/antiquities/Latin/book-10.xml",
            "sourceId": "latin-book10-num108", "label": {"sourceTag": "num", "sourceAttributes": {},
                "text": "[VII.iii.108]", "sourceTextStart": 0, "sourceTextEnd": 13},
            "nextBoundary": {"sourceTag": "milestone", "sourceAttributes": {"unit": "niese", "n": "109"}, "sourceTextOffset": 14},
            "interveningText": " ",
        })
        audit = next(p for p in self.documents[10][1]["paragraphs"] if p["sourceId"] == "latin-book10-num108")
        empty_fragment = audit["sections"][0]
        self.assertEqual((empty_fragment["leadingWhitespace"], empty_fragment["trailingWhitespace"]), (" ", ""))

    def test_every_new_editorial_span_and_expansion_preserves_source_letters_and_attributes(self):
        editorial = [m for r in self.records for m in r["editorialMarks"]]
        self.assertEqual({kind: sum(m["kind"] == kind for m in editorial) for kind in ("add", "del", "unclear")},
                         {"add": 26, "del": 7, "unclear": 63})
        self.assertEqual(sum(m["kind"] == "corr" for r in self.records for m in r["sourceMarkup"]), 48)
        self.assertEqual(sum(m["kind"] == "expan" for r in self.records for m in r["sourceMarkup"]), 6)
        for record in self.records:
            for mark in record["editorialMarks"] + record["sourceMarkup"]:
                self.assertEqual(utf16_slice(record["text"], mark["start"], mark["end"]), mark["text"])
                self.assertEqual(mark["sourceTag"], mark["kind"])
            self.assertFalse(any(m["kind"] == "unclear" for m in record["sourceMarkup"]))
        for citation in ("X.199", "X.200"):
            self.assertTrue(any(m["kind"] == "unclear" for m in self.by_citation[citation]["editorialMarks"]))
        self.assertTrue(any(m["kind"] == "expan" for m in self.by_citation["X.200"]["sourceMarkup"]))

    def test_all_eight_new_literal_gaps_match_independent_source_inventory(self):
        expected = {"VII.68": [("literal-ellipsis", 155, 156)], "VII.140": [("literal-ellipsis", 74, 75)],
                    "VII.141": [("literal-ellipsis", 1, 2)], "VII.378": [("literal-dots", 312, 315)],
                    "VIII.54": [("literal-ellipsis", 329, 330)], "IX.110": [("literal-ellipsis", 1, 2)],
                    "X.154": [("source-marked-dots", 95, 97), ("source-marked-dots", 107, 108)]}
        actual = {r["citationLabel"]: [(g["kind"], g["start"], g["end"]) for g in r["textGaps"]]
                  for r in self.records if r["textGaps"] and r["text"]}
        self.assertEqual(actual, expected)
        for mark in self.by_citation["X.154"]["textGaps"]:
            self.assertEqual(mark["sourceTag"], "del")
            self.assertEqual(mark["sourceAttributes"], {"hand": "?", "rend": "scraping"})

    def test_uncertain_sentence_periods_are_visible_without_phrase_barriers(self):
        for citation, offset in (("X.65", 273), ("X.75", 134)):
            record = self.by_citation[citation]
            self.assertIn({"kind": "unclear", "start": offset, "end": offset + 1, "text": ".", "sourceTag": "unclear", "sourceAttributes": {"reason": "uncertainty"}}, record["editorialMarks"])
            self.assertEqual(record["textGaps"], [])
            self.assertEqual(record["phraseBreaks"], [])

    def test_source_images_columns_and_intext_notes_do_not_add_words(self):
        for b, expected in ((9, (17, 33, 17)), (10, (22, 43, 22))):
            counts = self.documents[b][1]["counts"]
            self.assertEqual((counts["pageBreaks"], counts["columnBreaks"], counts["imageMilestones"]), expected)
        report = self.documents[10][1]
        self.assertEqual(report["counts"]["excludedAnnotationNotes"], 19)
        notes = [s for p in report["paragraphs"] for s in p["segments"] if s["kind"] == "excluded-note"]
        self.assertEqual(len(notes), 19)
        self.assertNotIn("chapter 2 starts here", " ".join(r["text"] for r in self.records))
        self.assertEqual(sum(e["kind"] == "book-title" for e in report["excluded"]), 2)

    def test_notice_changes_cannot_silently_enter_or_remove_latin(self):
        for b, before, after in ((7, b" Omitted in Bamberg MS", b"Omitted Latin might begin here"),
                                  (9, "[Lacuna 51–109; cf. Blatt, p. 67]".encode(), b"[Changed lacuna]")):
            with self.subTest(book=b), self.assertRaisesRegex(extract.ExtractionError, "notice"):
                extract.extract_document(self.sources[b].replace(before, after, 1), book_number=b)

    def test_empty_or_missing_source_boundaries_require_exact_evidence(self):
        changed = self.sources[10].replace(b'<num>[VII.iii.108]</num> <milestone', b'<num>[VII.iii.108]</num> latina <milestone', 1)
        with self.assertRaisesRegex(extract.ExtractionError, "empty source interval"):
            extract.extract_document(changed, book_number=10)
        changed = self.sources[9].replace(b'<num>[V.i.110]</num>', b'<num>[V.i.51]</num>', 1)
        if changed == self.sources[9]:
            root = ET.fromstring(self.sources[9])
            label = next(p.find(NS + "num") for p in root.findall(f".//{NS}p") if p.get(XML_ID) == "latin-book09-num110")
            label.text = label.text.replace("110", "51")
            changed = ET.tostring(root)
        with self.assertRaisesRegex(extract.ExtractionError, "consecutive Niese"):
            extract.extract_document(changed, book_number=9)

    def test_unreviewed_new_markup_and_annotation_changes_fail(self):
        for before, after in ((b"<corr>", b'<corr resp="unknown">'),
                              (b"chapter 2 starts here", b"uncatalogued running words")):
            with self.subTest(replacement=after), self.assertRaises(extract.ExtractionError):
                extract.extract_document(self.sources[10].replace(before, after, 1), book_number=10)

    def test_invalid_tenth_book_cannot_partially_replace_existing_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "assets/xml/antiquities/Latin"
            directory.mkdir(parents=True)
            for key in ["preface"] + [f"book-{b:02}" for b in range(1, 11)]:
                data = (REPOSITORY / f"assets/xml/antiquities/Latin/{key}.xml").read_bytes()
                if key == "book-10":
                    data = data.replace(b'<milestone unit="niese" n="281"', b'<milestone unit="niese" n="999"', 1)
                (directory / f"{key}.xml").write_bytes(data)
            output = root / "out"
            output.mkdir()
            (output / "corpus.json").write_bytes(b"previous complete search")
            with self.assertRaisesRegex(extract.ExtractionError, "consecutive Niese"):
                extract.build_corpus(root, output)
            self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, {"corpus.json": b"previous complete search"})


class AntiquitiesThirdBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {b: (REPOSITORY / f"assets/xml/antiquities/Latin/book-{b:02}.xml").read_bytes()
                       for b in range(11, 16)}
        cls.registries = {b: (REPOSITORY / f"assets/xml/antiquities/niese/book-{b:02}.json").read_bytes()
                          for b in range(11, 16)}
        cls.documents = {b: extract.extract_document(data, book_number=b, identity_registry=cls.registries[b])
                         for b, data in cls.sources.items()}
        cls.records = [r for rows, _ in cls.documents.values() for r in rows]

    def test_registered_physical_and_canonical_counts_and_source_bindings(self):
        expected = {11: (354, 347, 349, 11589), 12: (433, 433, 433, 13683),
                    13: (431, 431, 431, 13803), 14: (489, 489, 489, 15148), 15: (423, 423, 423, 12223)}
        self.assertEqual(len(self.records), 2130)
        self.assertEqual(len({r["id"] for r in self.records}), 2130)
        self.assertEqual([r["order"] for r in self.records], list(range(3415, 5545)))
        self.assertEqual(len({r["citationUnitId"] for r in self.records if "sourcePassage" not in r}), 2123)
        self.assertEqual(len({r["citationUnitId"] for r in self.records}), 2125)
        for b, (physical, canonical, units, token_count) in expected.items():
            rows, report = self.documents[b]
            self.assertEqual((len(rows), report["counts"]["canonicalSections"], report["counts"]["citationUnits"],
                              report["counts"]["runningWordTokens"]), (physical, canonical, units, token_count))
            self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.sources[b]).hexdigest())
            self.assertEqual(report["identityRegistry"]["sha256"], hashlib.sha256(self.registries[b]).hexdigest())
            self.assertTrue(all(row["text"] for row in rows))
            self.assertTrue(all(row.get("citationUnitId") for row in rows))

    def test_xi_reordered_and_split_portions_keep_physical_order_and_canonical_identity(self):
        rows, report = self.documents[11]
        start = next(i for i, r in enumerate(rows) if r["section"] == 67)
        self.assertEqual([r["section"] for r in rows[start:start + 9]], [67, 68, 72, 69, 70, 71, 72, 72, 73])
        portions = [r for r in rows if r["section"] == 72]
        self.assertEqual([r["continuationRank"] for r in portions], [2, 1, 3])
        self.assertEqual([r["text"].split()[0] for r in portions], ["Septem", "Mancipiorum", "Subiugalia"])
        self.assertEqual({r["citationUnitId"] for r in portions}, {extract.COLLECTION + "-11-72"})
        self.assertEqual({r["citationUnitCitation"] for r in portions}, {"XI.72"})
        self.assertEqual([r["sourceOccurrence"] for r in portions],
                         ["Latin-XI-72-2", "Latin-XI-72-1", "Latin-XI-72-3"])
        for number, count in ((72, 3), (312, 2), (326, 2), (342, 2)):
            selected = [r for r in rows if r["section"] == number]
            self.assertEqual(len(selected), count)
            self.assertEqual({r["fragmentCount"] for r in selected}, {count})
            self.assertEqual(len({r["id"] for r in selected}), count)
        self.assertEqual(report["coverage"]["fragmentedSections"], [72, 312, 326, 342])
        self.assertFalse(any(r.get("breakBefore") for r in rows))

    def test_registered_diagnostics_count_named_and_anonymous_paragraphs_and_all_structural_markers(self):
        # Independently counted from the accepted minidom source witness.
        expected = {11: (58, 57, 1, 3, 2, 0, 0, 0), 12: (71, 71, 0, 3, 2, 0, 0, 0),
                    13: (88, 87, 1, 3, 18, 0, 4, 1), 14: (115, 112, 3, 8, 2, 0, 4, 0),
                    15: (66, 66, 0, 8, 8, 13, 0, 1)}
        keys = ("narrativeParagraphs", "numberedParagraphs", "anonymousNarrativeParagraphs", "continuationParagraphs",
                "chapterDivisions", "chapterMilestones", "bambergAnchors", "traditionalBoundaryAnchors")
        for b, values in expected.items():
            report = self.documents[b][1]
            self.assertEqual(tuple(report["counts"][key] for key in keys), values)
            self.assertEqual(report["counts"]["citationParagraphs"] + report["counts"]["continuationParagraphs"], values[0])
            self.assertEqual(report["coverage"]["paragraphsExactlyRestored"], values[0])
            self.assertFalse(report["coverage"]["sourceOrderIsConsecutive"])
            self.assertTrue(report["coverage"]["physicalSourceOrderPreserved"])

    def test_bellum_interpolations_remain_distinct_from_antiquities_312(self):
        rows, report = self.documents[11]
        inserted = [r for r in rows if "sourcePassage" in r]
        accepted = {p["identity"]: p for p in json.loads(self.registries[11])["sourcePassages"]}
        self.assertEqual([r["section"] for r in inserted], ["BJ.IV.105a", "BJ.IV.105b"])
        for row in inserted:
            self.assertEqual(row["sourcePassage"], accepted[row["section"]])
            self.assertFalse(row["sourcePassage"]["AntiquitiesIdentity"])
            self.assertEqual(row["citationUnitId"], row["id"])
            self.assertNotEqual(row["citationUnitId"], extract.COLLECTION + "-11-312")
            self.assertEqual(row["readerLink"]["params"], {"book": 11, "niese": 312})
            self.assertEqual(row["url"], "/antiquities/?book=11&niese=312")
            self.assertIn("interpolated Bellum", row["citationLabel"])
        self.assertEqual(sum(len(extract.words(r["text"])) for r in inserted), 25)
        self.assertEqual(report["coverage"]["interpolatedSourcePassages"], 2)

    def test_registry_unavailable_identities_do_not_fabricate_text_or_a_lacuna(self):
        expected = {11: [], 12: [248], 13: [213, 216], 14: [238, 239], 15: [338, 347]}
        for b, unavailable in expected.items():
            rows, report = self.documents[b]
            self.assertEqual(report["coverage"]["unavailableSections"], unavailable)
            self.assertFalse(set(unavailable) & {r["section"] for r in rows})
            self.assertFalse(any(r.get("breakBefore") or r.get("emptySource") for r in rows))
            self.assertEqual([item["number"] for item in report["coverage"]["unavailableIdentities"]], unavailable)
            if b != 11:
                self.assertEqual([r["section"] for r in rows],
                                 [n for n in range(1, extract.BOOK_SPECS[b]["range"][1] + 1) if n not in unavailable])

    def test_every_original_paragraph_restores_from_finished_record_id_slices(self):
        for b, (rows, report) in self.documents.items():
            root = ET.fromstring(self.sources[b])
            by_id = {r["id"]: r for r in rows}
            for p in report["paragraphs"]:
                element = root.find("./" + "/".join(NS + step for step in p["sourceXPath"].split("/")[2:]))
                self.assertIsNotNone(element, p["sourceXPath"])
                source = "".join(element.itertext())
                restored, cursor = "", 0
                for segment in p["segments"]:
                    self.assertEqual(segment["sourceTextStart"], cursor)
                    text = (by_id[segment["recordId"]]["text"][segment["recordTextStart"]:segment["recordTextEnd"]]
                            if segment["kind"] == "source-text" else segment["text"])
                    self.assertEqual(text, source[segment["sourceTextStart"]:segment["sourceTextEnd"]])
                    restored += text
                    cursor = segment["sourceTextEnd"]
                self.assertEqual(restored, source)
                self.assertEqual(cursor, len(source))
                self.assertEqual(p["rawTextSha256"], hashlib.sha256(source.encode()).hexdigest())
                if element.get(XML_ID):
                    self.assertEqual(p["sourceId"], element.get(XML_ID))
                else:
                    self.assertEqual(p["sourceId"], "xpath:" + p["sourceXPath"])
            self.assertEqual(report["coverage"]["sourceNonWhitespaceContentSha256"],
                             report["coverage"]["displayNonWhitespaceContentSha256"])
            self.assertEqual(report["coverage"]["sourceWordSequenceSha256"],
                             report["coverage"]["indexedWordSequenceSha256"])

    def test_anonymous_narrative_paragraphs_and_actual_continuations_are_retained(self):
        self.assertEqual(sum(rep["counts"]["anonymousNarrativeParagraphs"] for _, rep in self.documents.values()), 5)
        xi345 = next(r for r in self.documents[11][0] if r["section"] == 345)
        self.assertIn("ad aegyptum", xi345["text"])
        self.assertTrue(any(s.startswith("xpath:") for s in xi345["sourceIds"]))
        xiii269 = next(r for r in self.documents[13][0] if r["section"] == 269)
        self.assertTrue(xiii269["sourceId"].startswith("xpath:"))
        self.assertTrue(xiii269["text"].startswith("Alexander autem regnum accipiens"))
        xiv47 = next(r for r in self.documents[14][0] if r["section"] == 47)
        self.assertIn("VI Aristobolus", xiv47["text"])
        self.assertTrue(any(s.startswith("xpath:") for s in xiv47["sourceIds"]))
        for section in (73, 485):
            row = next(r for r in self.documents[14][0] if r["section"] == section)
            self.assertTrue(row["sourceId"].startswith("xpath:"))

    def test_source_gaps_and_inline_offsets_preserve_text_and_interrupt_phrases(self):
        tei = [(r["book"], r["section"], g) for r in self.records for g in r["textGaps"] if g["kind"] == "tei-gap"]
        self.assertEqual([(b, s, g["sourceAttributes"]["reason"]) for b, s, g in tei],
                         [(12, 8, "hole"), (12, 35, "hole"), (13, 393, "fading")])
        for record in self.records:
            for mark in record["editorialMarks"] + record["sourceMarkup"] + record["textGaps"]:
                self.assertEqual(utf16_slice(record["text"], mark["start"], mark["end"]), mark["text"])
            self.assertEqual(record["phraseBreaks"], sorted({g["start"] for g in record["textGaps"]}))
        row = next(r for r in self.documents[13][0] if r["section"] == 393)
        gap = row["textGaps"][0]
        self.assertEqual(utf16_slice(row["text"], gap["start"] - 3, gap["start"] + 1), "ress")
        self.assertEqual(gap["start"], gap["end"])
        self.assertEqual(self.documents[13][1]["counts"]["runningWordTokens"],
                         1 + sum(len(extract.words(r["text"])) for r in self.documents[13][0]))
        dots = [(r["section"], g["text"]) for r in self.documents[14][0] for g in r["textGaps"]]
        self.assertEqual(dots, [(19, ".."), (28, ".."), (31, ".."), (35, ".."), (40, ".."), (45, ".."),
                                (65, ".."), (68, ".."), (76, ".."), (78, ".."), (221, "..."), (439, "..")])

    def test_only_the_unassigned_initial_xv_chapter_mark_is_excluded(self):
        rows, report = self.documents[15]
        self.assertTrue(rows[0]["text"].startswith("Sossius quidem et herodes"))
        excluded = [s for p in report["paragraphs"] for s in p["segments"] if s["kind"] == "excluded-chapter-annotation"]
        self.assertEqual(len(excluded), 1)
        self.assertEqual(excluded[0]["text"], "I")
        self.assertEqual(excluded[0]["sourceAttributes"], {"hand": "post", "place": "marginleft"})
        row = next(r for r in rows if r["section"] == 83)
        self.assertTrue(any(mark["kind"] == "add" and mark["text"] == "I"
                            and mark["sourceAttributes"].get("place") == "interlinear"
                            for mark in row["editorialMarks"]))

    def test_xii_explicit_niese_end_preserves_but_does_not_index_its_inline_subscription(self):
        rows, report = self.documents[12]
        final = rows[-1]
        subscription = "Flauii iosepp FLAUII IOSEPPI IUDAEICAE ANTIQUITATIS LIBER DUODECIMUS EXPLICIT"
        self.assertEqual(final["section"], 434)
        self.assertTrue(final["text"].endswith("defunctus est."))
        self.assertNotIn("FLAUII IOSEPPI", final["text"])
        paragraph = next(p for p in report["paragraphs"] if p["sourceId"] == "latin-book12-num426")
        excluded = [s for s in paragraph["segments"] if s["kind"] == "excluded-book-subscription"]
        self.assertEqual(len(excluded), 1)
        self.assertEqual(excluded[0]["text"], subscription)
        self.assertEqual(excluded[0]["sourceTag"], "milestone")
        self.assertEqual(excluded[0]["sourceAttributes"], {"unit": "niese-end"})
        marker = next(m for m in paragraph["structuralMarkers"] if m["sourceAttributes"].get("unit") == "niese-end")
        self.assertEqual(marker["recordId"], final["id"])
        self.assertEqual(marker["recordTextOffsetUTF16"], extract.utf16_length(final["text"]))
        self.assertEqual(len(extract.words(subscription)), 9)
        self.assertEqual(report["counts"]["nieseEndMilestones"], 1)
        self.assertEqual(report["counts"]["excludedInlineSubscriptions"], 1)
        self.assertTrue(paragraph["exactRestorationVerified"])

    def test_changed_registry_or_xml_requires_review_but_crlf_is_accepted(self):
        for b in (11, 15):
            with self.subTest(book=b), self.assertRaisesRegex(extract.ExtractionError, "identity registry differs"):
                extract.extract_document(self.sources[b], book_number=b, identity_registry=self.registries[b] + b" ")
            with self.subTest(book=b), self.assertRaisesRegex(extract.ExtractionError, "XML differs"):
                extract.extract_document(self.sources[b].replace(b"<p ", b"<p changed='yes' ", 1),
                                         book_number=b, identity_registry=self.registries[b])
            rows, _ = extract.extract_document(self.sources[b].replace(b"\n", b"\r\n"), book_number=b,
                                               identity_registry=self.registries[b].replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
            self.assertEqual(rows, self.documents[b][0])

    def test_final_registry_failure_does_not_replace_existing_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ["preface"] + [f"book-{b:02}" for b in range(1, 21)]:
                relative = f"assets/xml/antiquities/Latin/{name}.xml"
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((REPOSITORY / relative).read_bytes())
            for b in range(11, 21):
                relative = f"assets/xml/antiquities/niese/book-{b:02}.json"
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((REPOSITORY / relative).read_bytes() + (b" " if b == 20 else b""))
            output = root / "out"
            output.mkdir()
            (output / "corpus.json").write_bytes(b"previous complete search")
            with self.assertRaisesRegex(extract.ExtractionError, "identity registry differs"):
                extract.build_corpus(root, output)
            self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, {"corpus.json": b"previous complete search"})

    def test_registered_fixture_preserves_split_order_astral_markup_and_a_gap_inside_a_word(self):
        source = (f'<TEI xmlns="{extract.TEI}"><text><body><div1>'
                  '<p xml:id="latin-book11-num1"><num>[1]</num> 𐐀ve <add hand="post" place="interlinear">Áli</add>us '
                  '<milestone xml:id="second" unit="niese" n="2"/> res<gap reason="fading"/>s '
                  '<milestone xml:id="first-again" unit="niese" n="1"/> finis<note type="uncertainty">annotation</note> '
                  '</p></div1></body></text></TEI>').encode()
        def endpoint(target, kind="element"):
            return {"target": target, "kind": kind}
        registry = {"book": 11, "range": [1, 2], "sections": [
            {"number": 1, "Latin": {"available": True, "spans": [
                {"start": endpoint("latin-book11-num1", "paragraph"), "end": endpoint("second"),
                 "role": "primary", "occurrence": "Latin-XI-1-1", "continuationRank": 1},
                {"start": endpoint("first-again"), "end": endpoint("latin-book11-num1", "paragraph-end"),
                 "role": "primary", "occurrence": "Latin-XI-1-2", "continuationRank": 2}]}},
            {"number": 2, "Latin": {"available": True, "spans": [
                {"start": endpoint("second"), "end": endpoint("first-again"),
                 "role": "primary", "occurrence": "Latin-XI-2-1", "continuationRank": 1}]}}]}
        registry_bytes = json.dumps(registry).encode()
        # Patch only the test's accepted fixture contract, never production's
        # public API or its requirement to bind reviewed source bytes.
        with patch.dict(extract.BOOK_SPECS, {11: {"range": [1, 2], "paragraphs": 1, "records": 3, "canonicalSections": 2}}), \
                patch.dict(extract.REGISTERED_SOURCES, {11: (extract.sha(source), extract.sha(registry_bytes))}):
            rows, report = extract.extract_document(source, book_number=11, identity_registry=registry_bytes, order_offset=0)
        self.assertEqual([r["section"] for r in rows], [1, 2, 1])
        self.assertEqual([r["text"] for r in rows], ["𐐀ve Álius", "ress", "finis"])
        self.assertEqual(rows[0]["citationUnitId"], rows[2]["citationUnitId"])
        self.assertNotEqual(rows[0]["id"], rows[2]["id"])
        self.assertEqual(rows[0]["editorialMarks"][0]["start"], 5)
        self.assertEqual(rows[0]["editorialMarks"][0]["end"], 9)
        self.assertEqual(rows[1]["phraseBreaks"], [3])
        self.assertEqual(report["counts"]["runningWordTokens"], 5)
        self.assertTrue(report["coverage"]["sourceProjectionExactlyRestoresSource"])


class AntiquitiesFourthBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {b: (REPOSITORY / f"assets/xml/antiquities/Latin/book-{b:02}.xml").read_bytes()
                       for b in range(16, 21)}
        cls.registries = {b: (REPOSITORY / f"assets/xml/antiquities/niese/book-{b:02}.json").read_bytes()
                          for b in range(16, 21)}
        cls.documents = {b: extract.extract_document(data, book_number=b, identity_registry=cls.registries[b])
                         for b, data in cls.sources.items()}
        cls.records = [r for rows, _ in cls.documents.values() for r in rows]
        cls.by_citation = {r["citationLabel"]: r for r in cls.records}

    def test_all_five_books_have_the_independently_counted_physical_records_and_search_tokens(self):
        expected = {16: (383, 380, 10471, 61), 17: (355, 355, 15287, 61),
                    18: (377, 377, 15306, 57), 19: (366, 366, 11791, 52), 20: (257, 257, 7864, 51)}
        self.assertEqual(len(self.records), 1738)
        self.assertEqual(len({r["id"] for r in self.records}), 1738)
        self.assertEqual(len({r["citationUnitId"] for r in self.records}), 1735)
        self.assertEqual([r["order"] for r in self.records], list(range(5545, 7283)))
        self.assertEqual(sum(report["counts"]["runningWordTokens"] for _, report in self.documents.values()), 60719)
        for b, values in expected.items():
            rows, report = self.documents[b]
            self.assertEqual((len(rows), report["counts"]["canonicalSections"],
                              report["counts"]["runningWordTokens"], report["counts"]["narrativeParagraphs"]), values)
            self.assertEqual(report["counts"]["anonymousNarrativeParagraphs"], 0)
            self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.sources[b]).hexdigest())
            self.assertEqual(report["identityRegistry"]["sha256"], hashlib.sha256(self.registries[b]).hexdigest())
            self.assertTrue(all(r["text"] and r["sourceIds"] and "sourcePassage" not in r for r in rows))

    def test_xvi_split_sections_retain_the_accepted_fragment_order_and_start_anchor_identities(self):
        rows, report = self.documents[16]
        self.assertEqual([r["section"] for r in rows if 293 <= r["section"] <= 296],
                         [293, 294, 295, 294, 295, 296])
        self.assertEqual([r["section"] for r in rows if 350 <= r["section"] <= 356],
                         [350, 351, 352, 353, 354, 355, 351, 356])
        registry = json.loads(self.registries[16])
        for section in (294, 295, 351):
            portions = [r for r in rows if r["section"] == section]
            accepted = next(entry["Latin"]["spans"] for entry in registry["sections"] if entry["number"] == section)
            self.assertEqual([r["sourceOccurrence"] for r in portions], [span["start"]["target"] for span in accepted])
            self.assertEqual([r["continuationRank"] for r in portions], [1, 2])
            self.assertEqual({r["fragmentCount"] for r in portions}, {2})
            self.assertEqual({r["citationUnitId"] for r in portions}, {f"{extract.COLLECTION}-16-{section}"})
            self.assertEqual(len({r["id"] for r in portions}), 2)
            self.assertTrue(all(r["url"] == f"/antiquities/?book=16&niese={section}" for r in portions))
        self.assertEqual(report["coverage"]["fragmentedSections"], [294, 295, 351])
        self.assertTrue(self.by_citation["XVI.351 (portion 1 of 2)"]["text"].startswith("perissent qui"))
        self.assertTrue(self.by_citation["XVI.351 (portion 2 of 2)"]["text"].startswith("hac oratione"))
        self.assertEqual(self.by_citation["XVI.351 (portion 2 of 2)"]["sourceIds"], ["latin-book16-num356"])
        self.assertTrue(self.by_citation["XVI.356"]["text"].startswith("XVIIII Herodi"))

    def test_unavailable_registry_identities_do_not_invent_text_or_add_unattested_barriers(self):
        expected_breaks = {16: [200], 17: [], 18: [], 19: [], 20: [37]}
        for b, (rows, report) in self.documents.items():
            registry = json.loads(self.registries[b])
            unavailable = [entry for entry in registry["sections"] if not entry["Latin"]["available"]]
            self.assertEqual(report["coverage"]["unavailableIdentities"], unavailable)
            self.assertEqual(report["coverage"]["unavailableSections"], [entry["number"] for entry in unavailable])
            self.assertEqual({r["section"] for r in rows},
                             {entry["number"] for entry in registry["sections"] if entry["Latin"]["available"]})
            self.assertEqual([r["section"] for r in rows if r.get("breakBefore")], expected_breaks[b])
            self.assertFalse(any(r.get("emptySource") for r in rows))
        self.assertEqual(self.documents[20][1]["coverage"]["completeRange"], [1, 268])
        self.assertEqual(self.documents[20][0][-1]["section"], 268)
        self.assertTrue(self.documents[20][0][-1]["text"].endswith("aliud prohibemur."))

    def test_every_new_narrative_paragraph_is_exactly_restored_from_finished_record_slices(self):
        restored_paragraphs = 0
        for b, (rows, report) in self.documents.items():
            root = ET.fromstring(self.sources[b])
            originals = {p.get(XML_ID): p for p in root.findall(f".//{NS}body//{NS}p") if p.get(XML_ID)}
            by_id = {r["id"]: r for r in rows}
            for paragraph in report["paragraphs"]:
                source = "".join(originals[paragraph["sourceId"]].itertext())
                restored, cursor = "", 0
                for segment in paragraph["segments"]:
                    self.assertEqual(segment["sourceTextStart"], cursor)
                    text = (by_id[segment["recordId"]]["text"][segment["recordTextStart"]:segment["recordTextEnd"]]
                            if segment["kind"] == "source-text" else segment["text"])
                    self.assertEqual(text, source[segment["sourceTextStart"]:segment["sourceTextEnd"]])
                    restored += text
                    cursor = segment["sourceTextEnd"]
                self.assertEqual(restored, source)
                self.assertEqual(cursor, len(source))
                self.assertEqual(paragraph["rawTextSha256"], hashlib.sha256(source.encode()).hexdigest())
                self.assertTrue(paragraph["exactRestorationVerified"])
                restored_paragraphs += 1
            self.assertEqual(report["coverage"]["sourceNonWhitespaceContentSha256"],
                             report["coverage"]["displayNonWhitespaceContentSha256"])
            self.assertEqual(report["coverage"]["sourceWordSequenceSha256"],
                             report["coverage"]["indexedWordSequenceSha256"])
        self.assertEqual(restored_paragraphs, 282)

    def test_xvi_and_xx_boundary_notices_remain_exact_reversible_evidence_outside_search_text(self):
        for b, citation, kind, text, count in (
                (16, "XVI.200", "excluded-source-gap-notation", "[...]", 2),
                (20, "XX.37", "excluded-lacuna-notice", "[Niese sections 26–37 largely missing; cf. Blatt, p. 68]", 1)):
            rows, report = self.documents[b]
            row = self.by_citation[citation]
            evidence = row["sourceBoundaryEvidence"]
            self.assertEqual(evidence["kind"], "registered-source-discontinuity")
            self.assertTrue(row["breakBefore"])
            self.assertEqual(len(evidence["excludedSourceSpans"]), count)
            self.assertIn(evidence, report["coverage"]["explicitSourceBoundaries"])
            raw = {p.get(XML_ID): "".join(p.itertext()) for p in ET.fromstring(self.sources[b]).iter(NS + "p")}
            for excluded in evidence["excludedSourceSpans"]:
                self.assertEqual(excluded["kind"], kind)
                self.assertEqual(excluded["text"], text)
                self.assertEqual(raw[excluded["sourceId"]][excluded["sourceTextStart"]:excluded["sourceTextEnd"]], text)
                self.assertEqual(excluded["textSha256"], hashlib.sha256(text.encode()).hexdigest())
                self.assertIn(excluded, report["excluded"])
            self.assertNotIn(text, "".join(r["text"] for r in rows))
        notices = [item for item in self.documents[16][1]["excluded"] if item["kind"] == "excluded-source-gap-notation"]
        self.assertEqual([item["sourceId"] for item in notices],
                         ["latin-book16-num188", "latin-book16-num194", "latin-book16-num395"])
        self.assertEqual(self.by_citation["XX.26"]["text"], "Commorabatur itaque iazatis in hac regione.")

    def test_explicit_end_markers_attach_to_actual_preceding_text_without_inventing_source_paragraphs(self):
        for b, section, marker_id, expected_offset, marker_paragraph in (
                (16, 188, "niese-latin-book16-end188", 58, "latin-book16-num188"),
                (16, 394, "niese-latin-book16-end394", 236, "latin-book16-num395"),
                (20, 26, "niese-latin-book20-end26", 43, "latin-book20-num34")):
            rows, report = self.documents[b]
            row = next(r for r in rows if r["section"] == section)
            paragraph = next(p for p in report["paragraphs"] if p["sourceId"] == marker_paragraph)
            marker = next(m for m in paragraph["structuralMarkers"] if m["sourceAttributes"].get(XML_ID) == marker_id)
            self.assertEqual(marker["recordId"], row["id"])
            self.assertEqual(marker["recordTextOffset"], expected_offset)
            self.assertEqual(marker["recordTextOffsetUTF16"], extract.utf16_length(row["text"]))
            if section != 188:
                self.assertNotIn(marker_paragraph, row["sourceIds"])
        for _, report in self.documents.values():
            self.assertEqual(sum(item["kind"] == "trailer" for item in report["excluded"]), 1)

    def test_actual_gaps_and_all_literal_editorial_spans_survive_with_exact_utf16_offsets(self):
        gaps = [(r["book"], r["section"], g) for r in self.records for g in r["textGaps"]]
        self.assertEqual(gaps, [
            (16, 170, {"kind": "tei-gap", "start": 154, "end": 154, "text": "", "sourceAttributes": {}}),
            (20, 263, {"kind": "literal-dots", "start": 78, "end": 80, "text": ".."}),
        ])
        self.assertIn("nostrae pro .n..e, etiam graecas", self.by_citation["XX.263"]["text"])
        for row in self.records:
            for mark in row["editorialMarks"] + row["sourceMarkup"] + row["textGaps"]:
                self.assertEqual(utf16_slice(row["text"], mark["start"], mark["end"]), mark["text"])
            self.assertEqual(row["phraseBreaks"], sorted({gap["start"] for gap in row["textGaps"]}))

    def test_supplemental_xviii_xix_starts_cover_only_identities_without_actual_niese_markers(self):
        for b, expected_actual, expected_supplemental in ((18, 316, 61), (19, 320, 46)):
            registry = json.loads(self.registries[b])
            self.assertEqual(registry["structuralMilestoneUnits"], [None, "chapter"])
            actual = {int(node.get("n")) for node in ET.fromstring(self.sources[b]).iter(NS + "milestone")
                      if node.get("unit") == "niese"}
            supplemental = {entry["number"] for entry in registry["sections"] if "start" in entry["Latin"]}
            self.assertEqual(len(actual), expected_actual)
            self.assertEqual(len(supplemental), expected_supplemental)
            self.assertFalse(actual & supplemental)
            self.assertEqual(actual | supplemental, {r["section"] for r in self.documents[b][0]})
            self.assertEqual(self.documents[b][1]["counts"]["registeredSupplementalStarts"], expected_supplemental)
        self.assertTrue(self.by_citation["XVIII.2"]["text"].startswith("II Mittitur etiam cum eo copinius"))
        self.assertTrue(self.by_citation["XIX.1"]["text"].startswith("Gaius autem non in solos iudaeos"))

    def test_xvii_registered_token_seam_preserves_all_characters_and_remains_phrase_joinable(self):
        rows, report = self.documents[17]
        left, right = self.by_citation["XVII.41"], self.by_citation["XVII.42"]
        self.assertTrue(left["text"].endswith("inmaturius eleuati"))
        self.assertTrue(right["text"].startswith("cum igitur"))
        self.assertFalse(right.get("breakBefore"))
        evidence = report["coverage"]["registeredTokenBoundaryEvidence"]
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["sourceTextOffset"], 3308)
        self.assertEqual(evidence[0]["sourceAttributes"][XML_ID], "niese-latin-book17-42")
        self.assertEqual((evidence[0]["sourceText"], evidence[0]["precedingText"], evidence[0]["followingText"]),
                         ("eleuaticum", "eleuati", "cum"))
        self.assertEqual((evidence[0]["precedingRecordId"], evidence[0]["followingRecordId"]), (left["id"], right["id"]))
        self.assertNotEqual(report["coverage"]["rawParagraphWordSequenceSha256"], report["coverage"]["sourceWordSequenceSha256"])
        self.assertEqual(report["coverage"]["registeredBoundaryWordSequenceSha256"], report["coverage"]["indexedWordSequenceSha256"])
        self.assertEqual(sum(len(extract.words(r["text"])) for r in rows), 15287)

    def test_reviewed_word_seam_does_not_authorize_arbitrary_source_word_splitting(self):
        changed = self.sources[17].replace(b'eleuati<milestone unit="niese" n="42"',
                                            b'eleuatiX<milestone unit="niese" n="42"', 1)
        self.assertNotEqual(changed, self.sources[17])
        with patch.dict(extract.REGISTERED_SOURCES, {17: (hashlib.sha256(changed).hexdigest(), extract.REGISTERED_SOURCES[17][1])}):
            with self.assertRaisesRegex(extract.ExtractionError, "token boundary moved"):
                extract.extract_document(changed, book_number=17, identity_registry=self.registries[17])

    def test_changed_new_sources_or_registries_fail_while_windows_line_endings_preserve_records(self):
        for b in range(16, 21):
            with self.subTest(book=b), self.assertRaisesRegex(extract.ExtractionError, "identity registry differs"):
                extract.extract_document(self.sources[b], book_number=b, identity_registry=self.registries[b] + b" ")
            with self.subTest(book=b), self.assertRaisesRegex(extract.ExtractionError, "XML differs"):
                extract.extract_document(self.sources[b] + b" ", book_number=b, identity_registry=self.registries[b])
            crlf_xml = self.sources[b].replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            crlf_registry = self.registries[b].replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            rows, _ = extract.extract_document(crlf_xml, book_number=b, identity_registry=crlf_registry)
            self.assertEqual(rows, self.documents[b][0])


class AntiquitiesCorruptionTests(unittest.TestCase):
    def test_utf16_markup_offsets_preserve_astral_letters_and_word_internal_page_markers(self):
        target = "note_" + "a" * 32
        records, report = small(fixture(paragraph(
            f' 𐐀ve Á<add>li</add>us post<del><ref target="{target}">ra</ref></del> '
            'Ro<pb n="2v"/>manos <s>unus <milestone unit="niese" n="28"/>alter</s> ')), last=28)
        first, second = records
        self.assertEqual(first["text"], "𐐀ve Álius postra Romanos unus")
        self.assertEqual(second["text"], "alter")
        self.assertEqual(first["editorialMarks"][0]["start"], 7)
        self.assertEqual(first["editorialMarks"][0]["text"], "li")
        for record in records:
            for mark in record["editorialMarks"] + record["sourceMarkup"]:
                self.assertEqual(utf16_slice(record["text"], mark["start"], mark["end"]), mark["text"])
        self.assertTrue(report["coverage"]["sourceProjectionExactlyRestoresSource"])

    def test_conservative_dot_detection_does_not_reinterpret_letter_supplements(self):
        records, _ = small(fixture(paragraph(" &lt;similiter&gt; respo&lt;nderet&gt;ur nosc&lt;untur&gt; triginta.. con&lt;...&gt;perit [f...s] se&lt;.&gt;ba ")))
        self.assertEqual([g["text"] for g in records[0]["textGaps"]], ["...", "...", "."])
        self.assertEqual(records[0]["text"], "<similiter> respo<nderet>ur nosc<untur> triginta.. con<...>perit [f...s] se<.>ba")

    def test_unknown_substantive_tag_cannot_be_silently_dropped(self):
        for tag in ("choice", "app", "supplied", "foreign", "unclear"):
            with self.subTest(tag=tag), self.assertRaisesRegex(extract.ExtractionError, "unexpected running-text markup"):
                small(fixture(paragraph(f"ante <{tag}>uerbum</{tag}> post")))

    def test_unknown_editorial_attributes_require_review(self):
        with self.assertRaisesRegex(extract.ExtractionError, "addition attributes"):
            small(fixture(paragraph('ante <add resp="unknown">uerbum</add> post')))

    def test_unreviewed_note_or_a_note_inside_running_text_requires_review(self):
        for text in ('<note>possibly main text</note>ante', 'ante <note source="#BernBBMs50">new position</note>'):
            with self.subTest(text=text), self.assertRaisesRegex(extract.ExtractionError, "unreviewed running-text note"):
                small(fixture(paragraph(text)))

    def test_duplicate_missing_and_reordered_niese_markers_fail(self):
        for marker in (27, 29):
            with self.subTest(marker=marker), self.assertRaisesRegex(extract.ExtractionError, "consecutive Niese"):
                small(fixture(paragraph(f'prima <milestone unit="niese" n="{marker}"/>secunda')), last=28)
        with self.assertRaisesRegex(extract.ExtractionError, "citation coverage"):
            small(fixture(paragraph("prima")), last=28)

    def test_niese_marker_cannot_split_an_original_word(self):
        with self.assertRaisesRegex(extract.ExtractionError, "divides or changes an original word"):
            small(fixture(paragraph('di<milestone unit="niese" n="28"/>cit')), last=28)

    def test_unmarked_empty_sections_fail(self):
        with self.assertRaisesRegex(extract.ExtractionError, "unmarked empty Niese section"):
            small(fixture(paragraph('prima<milestone unit="niese" n="28"/>')), last=28)

    def test_gap_outside_the_reviewed_iii_240_omission_fails(self):
        with self.assertRaisesRegex(extract.ExtractionError, "reviewed explicit omissions"):
            small(fixture(paragraph('<gap reason="omitted"/>')))
        with self.assertRaisesRegex(extract.ExtractionError, "gap attributes"):
            small(fixture(paragraph('<gap reason="illegible"/>')))

    def test_deleted_gap_marker_cannot_turn_iii_240_into_an_unmarked_empty_record(self):
        source = (REPOSITORY / "assets/xml/antiquities/Latin/book-03.xml").read_bytes()
        source = source.replace(b'<gap reason="omitted"/>', b'', 1)
        with self.assertRaisesRegex(extract.ExtractionError, "unmarked empty Niese section"):
            extract.extract_document(source, book_number=3)

    def test_duplicate_paragraph_ids_fail(self):
        source = fixture(paragraph("prima") + paragraph("secunda", 28))
        source = source.replace(b'xml:id="latin-book01-num28"', b'xml:id="latin-book01-num27"', 1)
        with self.assertRaisesRegex(extract.ExtractionError, "Duplicate paragraph identity"):
            small(source, last=28)

    def test_unreviewed_unnumbered_paragraph_cannot_be_discarded(self):
        with self.assertRaisesRegex(extract.ExtractionError, "Unreviewed unnumbered paragraph"):
            small(fixture('<p>Substantive text without numbering</p>' + paragraph("prima")))

    def test_dtd_comments_and_processing_instructions_are_not_ignored(self):
        for source in (b'<!DOCTYPE TEI [<!ENTITY x "unsafe">]>' + fixture(paragraph("prima")),
                       fixture(paragraph("prima<!--additional material-->")),
                       fixture(paragraph("prima<?target processing?>"))):
            with self.subTest(source=source[:100]), self.assertRaises(extract.ExtractionError):
                small(source)

    def test_missing_or_nested_num_label_fails(self):
        with self.assertRaisesRegex(extract.ExtractionError, "missing citation num label"):
            small(fixture('<p xml:id="latin-book01-num27">No label</p>'))
        with self.assertRaisesRegex(extract.ExtractionError, "citation or note nested"):
            small(fixture(paragraph('ante <s><num>[I.ii.28]</num>post</s>')))

    def test_eleventh_book_requires_its_accepted_identity_registry(self):
        with self.assertRaisesRegex(extract.ExtractionError, "identity registry"):
            extract.extract_document(fixture(paragraph("prima")), book_number=11)


if __name__ == "__main__":
    unittest.main()
