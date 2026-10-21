#!/usr/bin/env python3
"""Independent source witness for Whiston Antiquities Proem and Books I-XV.

This verifier imports no search or production-extractor code. It uses minidom,
an explicit text-node stream, and Unicode character categories. Book IX's
restored text is indexed but its footnotes and headings are excluded. Book XI
preserves its physical source order, including its displaced blocks. Only
CRLF-to-LF changes are accepted when checking the sixteen reviewed XML fingerprints.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
from xml.dom import Node, minidom

TEI = "http://www.tei-c.org/ns/1.0"
SOURCE_COMMIT = "4f5f648a8e423819afe143bb12a93772a42b4e43"
COLLECTION = "antiquities-english-whiston"
SPECS = [
    ("preface", 1, True, "d04712a2db72f2d2c39e175591b866308f93cb15d10f4ee3be70401f7dd614eb"),
    ("book-01", 1, True, "9cd8daf04bddfd94cd96f077c0b9336135c35d017fad029a56fd08e1fc2363f3"),
    ("book-02", 2, True, "70da231aafb85aecfec0510bc7489441ca8263b45e31dd33f3ed2f20237aa584"),
    ("book-03", 3, True, "0c663f9776a1249d85ceab2ad0bfa47dc3b537864598f4855a668e23e642df44"),
    ("book-04", 4, True, "6d58dfa865b47e1a1f347f8f322f578381e6f8a407c597e2f36ae3bd120c6554"),
    ("book-05", 5, True, "a8ab9d6b66e6d4a768f3fc247240d6423d5d9687a3f1026f327f9ea387560722"),
    ("book-06", 6, True, "116338d9f8a424bfb2ec63af5531b3c72941708ae00e7f327ba8909dc1e125eb"),
    ("book-07", 7, True, "d8109c20ceca61283dd5150bf2059f3cffda924f5f82625a4e6b1073b4c60eb3"),
    ("book-08", 8, True, "609cedd3dbab1f7af831877f2aea820781e2b34b6c998ab41b3ffa6cb0fb8289"),
    ("book-09", 9, True, "d973618661bacf96f0a7ea81f1d7e44147f7826ff1d247908467b238263edc36"),
    ("book-10", 10, True, "7f4fde2921f8c5fc670d688174f5c67f81eed7c264c63af89b6c7adb0725e7eb"),
    ("book-11", 11, True, "0bdcc522c1f227dab7a61b19a4bef09a590af2bf25cbdce581277469c082acb2"),
    ("book-12", 12, True, "ba4808e3b5e234c2ec1bbffd3e4b662a78b2fe41c1643be3e4e7e6662d583286"),
    ("book-13", 13, True, "01ff55a3e01bd82c6590ef8bbfa30c05a22a8ebc292086b10095011b552f91a9"),
    ("book-14", 14, True, "9f5ffef649c2922e54402ca7ab09795307fe0595c68d47754df8aefe47464ed1"),
    ("book-15", 15, True, "223b08bd399b58dd6da5929a5cbffacb31f461ee11d4d6dd4aa45b498283d579"),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def all_text(node):
    if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
        return node.data
    return "".join(all_text(child) for child in node.childNodes)


def u16(text):
    return len(text.encode("utf-16-le")) // 2


def scan_words(text):
    """Word boundaries by Unicode categories, independent of JS regexes."""
    result, start, start_offset, offset = [], None, None, 0
    for index in range(len(text) + 1):
        char = text[index] if index < len(text) else " "
        category = unicodedata.category(char)[0]
        if start is not None and category not in "LMN":
            raw = text[start:index]
            term = unicodedata.normalize("NFC", raw).lower().replace("ς", "σ")
            result.append({"term": unicodedata.normalize("NFC", term),
                           "start": start_offset, "end": offset})
            start = start_offset = None
        if start is None and category in "LN":
            start, start_offset = index, offset
        offset += u16(char)
    return result


def extract_source(root, spec, order=0):
    stem, book, indexed, accepted_sha = spec
    path = f"assets/xml/antiquities/English/{stem}.xml"
    raw = (root / path).read_bytes()
    lf = raw.replace(b"\r\n", b"\n")
    assert b"\r" not in lf and sha(lf) == accepted_sha, ("Unaccepted Whiston XML", path)
    assert b"<!DOCTYPE" not in raw.upper() and b"<!ENTITY" not in raw.upper(), path
    dom = minidom.parseString(raw)
    assert dom.documentElement.namespaceURI == TEI, path
    elements = list(dom.getElementsByTagName("*"))
    assert all(element.namespaceURI == TEI for element in elements), path
    ids = [element.getAttribute("xml:id") for element in elements if element.hasAttribute("xml:id")]
    assert len(ids) == len(set(ids)), ("Duplicate XML IDs", path)
    counts = Counter(element.localName for element in elements)
    assert set(counts) <= {"TEI", "text", "body", "note", "div1", "div2", "p", "num", "milestone", "anchor", "lb", "hi"}, (path, counts)
    rows, exclusions, paragraphs, structural, formatting = [], [], [], [], []

    # Source/editor notes outside a narrative paragraph are excluded as a
    # complete subtree, rather than allowing their words into the first unit.
    for note in dom.getElementsByTagName("note"):
        parent = note.parentNode
        while parent is not None and getattr(parent, "localName", None) != "p":
            parent = parent.parentNode
        if parent is None:
            exclusions.append({"kind": "note", "sourceId": None, "text": all_text(note),
                               "attributes": dict(note.attributes.items())})

    for paragraph in dom.getElementsByTagName("p"):
        source_id = paragraph.getAttribute("xml:id") or None
        markers = [marker for marker in paragraph.getElementsByTagName("milestone")
                   if marker.getAttribute("unit") == "niese"]
        continuation = {("book-04", "english-book04-num276b"): (276, "english-book04-num276", []),
                        ("book-08", "english-book08-num255"): (255, "english-book08-num251", list(range(256, 263))),
                        ("book-12", "english-book12-num148"): (147, "english-book12-num145", list(range(148, 154))),
                        ("book-12", "english-book12-num225"): (226, "english-book12-num223", [227]),
                        ("book-14", "english-book14-num237"): (237, "english-book14-num236", [238, 239, 240])}.get((stem, source_id))
        if continuation:
            section, previous_id, paragraph_markers = continuation
            assert rows and rows[-1]["section"] == section and rows[-1]["sourceId"] == previous_id
            assert [int(marker.getAttribute("n")) for marker in markers] == paragraph_markers
        if not markers and not continuation:
            assert re.match(r"(?:BOOK\b|CHAPTER\b|CONTAINING\b|Antiquities of the Jews -- Preface$)",
                            all_text(paragraph).strip(), re.I), ("Unclassified markerless paragraph", path, source_id)
            assert source_id is None or paragraph.getAttribute("rend") == "whiston-chapter-heading", (path, source_id)
            exclusions.append({"kind": "heading", "sourceId": source_id,
                               "text": all_text(paragraph), "attributes": dict(paragraph.attributes.items())})
            continue
        assert source_id, ("Narrative paragraph without a stable ID", path)
        raw_offset, active, prefix = 0, None, []
        if continuation:
            active = {"section": continuation[0], "events": [], "continuesPrevious": True}
        paragraph_rows = []

        def finish():
            nonlocal active
            if active is None:
                return
            event_list = active.pop("events")
            text = "".join(event["text"] for event in event_list)
            leading = u16(text) - u16(text.lstrip())
            end = u16(text.rstrip())
            trimmed = text.strip()
            output_offset, segments = 0, []
            for event in event_list:
                length = u16(event["text"])
                a, b = max(output_offset, leading), min(output_offset + length, end)
                if b > a:
                    encoded = event["text"].encode("utf-16-le")
                    piece = encoded[2 * (a - output_offset):2 * (b - output_offset)].decode("utf-16-le")
                    segments.append({"sourceId": source_id,
                                     "rawStart": event["rawStart"] + a - output_offset,
                                     "rawEnd": event["rawStart"] + b - output_offset,
                                     "start": a - leading, "end": b - leading, "text": piece})
                output_offset += length
            assert "".join(segment["text"] for segment in segments) == trimmed
            active.update(text=trimmed, tokens=scan_words(trimmed), sourceSegments=segments)
            assert active["tokens"], ("Empty Whiston interval", path, active["section"])
            if active.pop("continuesPrevious", False):
                previous = rows[-1]
                start = u16(previous["text"])
                join = "\n\n"
                previous.setdefault("paragraphJoins", []).append({"start": start, "end": start + u16(join),
                    "text": join, "beforeSourceId": previous["sourceIds"][-1], "afterSourceId": source_id})
                previous["text"] += join + trimmed
                previous["tokens"] = scan_words(previous["text"])
                previous["sourceIds"].append(source_id)
                previous["sourceSegments"].extend({**segment, "start": start + u16(join) + segment["start"],
                                                  "end": start + u16(join) + segment["end"]} for segment in segments)
            else:
                rows.append(active)
            paragraph_rows.append(active["section"])
            active = None

        def walk(node):
            nonlocal raw_offset, active
            if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                event = {"text": node.data, "rawStart": raw_offset}
                if active is None:
                    prefix.append(event)
                else:
                    active["events"].append(event)
                raw_offset += u16(node.data)
                return
            assert node.nodeType == Node.ELEMENT_NODE, ("Unexpected XML node", path, node.nodeType)
            tag = node.localName
            if tag == "hi":
                assert book in {10, 12} and dict(node.attributes.items()) == {"rend": "bold"}
                assert active is not None and all(child.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE) for child in node.childNodes)
                start = raw_offset
                for child in node.childNodes:
                    walk(child)
                formatting.append({"kind": tag, "sourceId": source_id, "section": active["section"],
                                   "rawStart": start, "rawEnd": raw_offset, "text": all_text(node),
                                   "attributes": dict(node.attributes.items())})
                return
            if tag in {"num", "note"}:
                text = all_text(node)
                exclusions.append({"kind": tag, "sourceId": source_id, "text": text,
                                   "rawStart": raw_offset, "rawEnd": raw_offset + u16(text),
                                   "section": None if active is None else active["section"],
                                   "attributes": dict(node.attributes.items())})
                raw_offset += u16(text)
                return
            if tag == "milestone":
                if node.getAttribute("unit") == "chapter":
                    assert book == 15 and not all_text(node) and not node.childNodes
                    assert node.getAttribute("n").isdecimal()
                    structural.append({"kind": "chapter-milestone", "sourceId": source_id, "rawOffset": raw_offset,
                                       "section": None if active is None else active["section"],
                                       "attributes": dict(node.attributes.items())})
                    return
                assert not all_text(node) and node.getAttribute("unit") == "niese", (path, source_id)
                finish()
                value = node.getAttribute("n")
                assert value.isdecimal() and int(value) > 0, (path, value)
                section = int(value)
                active = {"id": f"{COLLECTION}-{book}-{section}", "book": book, "section": section,
                          "order": order + len(rows), "sourcePath": path, "sourceId": source_id,
                          "sourceIds": [source_id], "readerBook": "preface" if stem == "preface" else book,
                          "proem": stem == "preface", "rawStart": raw_offset,
                          "events": []}
                return
            assert tag in {"anchor", "lb"} and not all_text(node) and not node.childNodes, (path, tag)
            structural.append({"kind": tag, "sourceId": source_id, "rawOffset": raw_offset,
                               "section": None if active is None else active["section"],
                               "attributes": dict(node.attributes.items())})

        for child in paragraph.childNodes:
            walk(child)
        finish()
        prefix_text = "".join(event["text"] for event in prefix)
        if prefix_text.strip():
            assert (stem, source_id, prefix_text.strip()) == ("preface", "english-preface-num5", "."), ("Unexpected pre-marker prose", path, source_id, prefix_text)
            exclusions.append({"kind": "pre-marker-prefix", "sourceId": source_id, "text": prefix_text,
                               "reason": "The reader begins the Niese interval immediately after its milestone."})
        assert raw_offset == u16(all_text(paragraph)), ("Unaccounted source text", path, source_id)
        paragraphs.append({"sourceId": source_id, "rawText": all_text(paragraph),
                           "sections": paragraph_rows, "nieseSections": [int(marker.getAttribute("n")) for marker in markers],
                           "rawLength": raw_offset})

    if stem == "preface":
        expected = list(range(1, 27))
    elif book == 1:
        expected = list(range(27, 347))
    elif book == 11:
        expected = list(range(1, 312)) + list(range(326, 343)) + list(range(312, 326)) + list(range(343, 348))
    else:
        expected = list(range(1, {2: 349, 3: 322, 4: 331, 5: 362, 6: 378, 7: 394, 8: 420,
                                 9: 291, 10: 281, 12: 434, 13: 433, 14: 491, 15: 425}[book] + 1))
    assert [row["section"] for row in rows] == expected, ("Niese physical sequence", path)
    assert len({row["id"] for row in rows}) == len(rows)
    evidence = {"path": path, "book": book, "proem": stem == "preface", "indexed": indexed,
                "sha256": sha(raw), "lfSHA256": sha(lf), "bytes": len(raw), "stableIds": len(ids),
                "bodyTags": dict(counts), "paragraphs": len(paragraphs), "sections": len(rows),
                "tokens": sum(len(row["tokens"]) for row in rows),
                "excludedHeadings": sum(item["kind"] == "heading" for item in exclusions),
                "excludedNotes": sum(item["kind"] == "note" for item in exclusions),
                "excludedLabels": sum(item["kind"] == "num" for item in exclusions)}
    return {"evidence": evidence, "rows": rows, "exclusions": exclusions,
            "paragraphs": paragraphs, "structural": structural, "formatting": formatting}


def main():
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[3]
    assert len(sys.argv) in {1, 2}, "Usage: whiston-source-witness.py [repository]"
    files, order = [], 0
    for spec in SPECS:
        file = extract_source(root, spec, order if spec[2] else 0)
        files.append(file)
        if spec[2]:
            order += len(file["rows"])
    indexed_files = [file for file in files if file["evidence"]["indexed"]]
    test_files = [file for file in files if not file["evidence"]["indexed"]]
    rows = [row for file in indexed_files for row in file["rows"]]
    assert len(rows) == 5604
    assert len({row["id"] for row in rows}) == len(rows)
    assert [row["order"] for row in rows] == list(range(5604))
    book_one = [row for row in rows if row["book"] == 1]
    assert [row["section"] for row in book_one] == list(range(1, 347))
    assert sum(len(row["tokens"]) for row in book_one) == 21994
    previous_batch = [row for row in rows if row["book"] <= 5]
    assert len(previous_batch) == 1710 and sum(len(row["tokens"]) for row in previous_batch) == 112265
    book_nine = next(file for file in indexed_files if file["evidence"]["book"] == 9)
    assert len([item for item in book_nine["exclusions"] if item["kind"] == "note" and item["sourceId"]]) == 7
    headings_with_ids = [item["sourceId"] for item in book_nine["exclusions"] if item["kind"] == "heading" and item["sourceId"]]
    assert headings_with_ids == ["english-book09-restored-heading-05", "english-book09-restored-heading-06"]
    assert [row["section"] for row in book_nine["rows"] if 51 <= row["section"] <= 109] == list(range(51, 110))
    assert [(item["section"], item["text"]) for item in next(file for file in indexed_files if file["evidence"]["book"] == 10)["formatting"]] == [(184, "Samaritans"), (243, "Number"), (244, "weight"), (244, "fragment")]
    assert not test_files
    previous_ten = [row for row in rows if row["book"] <= 10]
    assert len(previous_ten) == 3474 and sum(len(row["tokens"]) for row in previous_ten) == 236049
    result = {"sourceCommit": SOURCE_COMMIT,
              "runtime": {"python": sys.version.split()[0], "unicode": unicodedata.unidata_version,
                          "xmlParser": "xml.dom.minidom"},
              "rows": rows, "sources": [item["evidence"] for item in indexed_files],
              "indexedFiles": indexed_files, "testSources": test_files,
              "bookTotals": [{"book": book, "sections": sum(row["book"] == book for row in rows),
                              "tokens": sum(len(row["tokens"]) for row in rows if row["book"] == book)}
                             for book in range(1, 16)],
              "totals": {"books": 15, "sections": len(rows), "tokens": sum(len(row["tokens"]) for row in rows)}}
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
