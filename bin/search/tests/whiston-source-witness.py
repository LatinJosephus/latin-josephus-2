#!/usr/bin/env python3
"""Independent source witness for Whiston Antiquities Proem and Books I-V.

This verifier imports no search or production-extractor code. It uses minidom,
an explicit text-node stream, and Unicode character categories. Books IX and
XI are deliberately test-only: their notes and source order are future guards,
not additional published coverage. Only CRLF-to-LF changes are accepted when
checking the eight reviewed XML fingerprints.
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
SOURCE_COMMIT = "7befd862818b4b52699cdb2fbd76c4846a0c13cf"
COLLECTION = "antiquities-english-whiston"
SPECS = [
    ("preface", 1, True, "d04712a2db72f2d2c39e175591b866308f93cb15d10f4ee3be70401f7dd614eb"),
    ("book-01", 1, True, "9cd8daf04bddfd94cd96f077c0b9336135c35d017fad029a56fd08e1fc2363f3"),
    ("book-02", 2, True, "70da231aafb85aecfec0510bc7489441ca8263b45e31dd33f3ed2f20237aa584"),
    ("book-03", 3, True, "0c663f9776a1249d85ceab2ad0bfa47dc3b537864598f4855a668e23e642df44"),
    ("book-04", 4, True, "6d58dfa865b47e1a1f347f8f322f578381e6f8a407c597e2f36ae3bd120c6554"),
    ("book-05", 5, True, "a8ab9d6b66e6d4a768f3fc247240d6423d5d9687a3f1026f327f9ea387560722"),
    ("book-09", 9, False, "d973618661bacf96f0a7ea81f1d7e44147f7826ff1d247908467b238263edc36"),
    ("book-11", 11, False, "0bdcc522c1f227dab7a61b19a4bef09a590af2bf25cbdce581277469c082acb2"),
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
    assert set(counts) <= {"TEI", "text", "body", "note", "div1", "div2", "p", "num", "milestone", "anchor", "lb"}, (path, counts)
    rows, exclusions, paragraphs, structural = [], [], [], []

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
        continuation = (stem, source_id) == ("book-04", "english-book04-num276b")
        if continuation:
            assert not markers and rows and rows[-1]["section"] == 276
            assert rows[-1]["sourceId"] == "english-book04-num276"
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
            active = {"section": 276, "events": []}
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
            if continuation:
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
            if tag in {"num", "note"}:
                text = all_text(node)
                exclusions.append({"kind": tag, "sourceId": source_id, "text": text,
                                   "rawStart": raw_offset, "rawEnd": raw_offset + u16(text),
                                   "section": None if active is None else active["section"],
                                   "attributes": dict(node.attributes.items())})
                raw_offset += u16(text)
                return
            if tag == "milestone":
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
                           "sections": paragraph_rows, "rawLength": raw_offset})

    expected = (list(range(1, 27)) if stem == "preface" else list(range(27, 347)) if book == 1
                else list(range(1, {2: 349, 3: 322, 4: 331, 5: 362}[book] + 1)) if book in {2, 3, 4, 5}
                else list(range(1, 292)) if book == 9
                else list(range(1, 312)) + list(range(326, 343)) + list(range(312, 326)) + list(range(343, 348)))
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
            "paragraphs": paragraphs, "structural": structural}


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
    assert len(rows) == 1710
    assert len({row["id"] for row in rows}) == len(rows)
    assert [row["order"] for row in rows] == list(range(1710))
    book_one = [row for row in rows if row["book"] == 1]
    assert [row["section"] for row in book_one] == list(range(1, 347))
    assert sum(len(row["tokens"]) for row in book_one) == 21994
    assert len([item for item in test_files[0]["exclusions"] if item["kind"] == "note" and item["sourceId"]]) == 7
    headings_with_ids = [item["sourceId"] for item in test_files[0]["exclusions"] if item["kind"] == "heading" and item["sourceId"]]
    assert headings_with_ids == ["english-book09-restored-heading-05", "english-book09-restored-heading-06"]
    result = {"sourceCommit": SOURCE_COMMIT,
              "runtime": {"python": sys.version.split()[0], "unicode": unicodedata.unidata_version,
                          "xmlParser": "xml.dom.minidom"},
              "rows": rows, "sources": [item["evidence"] for item in indexed_files],
              "indexedFiles": indexed_files, "testSources": test_files,
              "bookTotals": [{"book": book, "sections": sum(row["book"] == book for row in rows),
                              "tokens": sum(len(row["tokens"]) for row in rows if row["book"] == book)}
                             for book in range(1, 6)],
              "totals": {"books": 5, "sections": len(rows), "tokens": sum(len(row["tokens"]) for row in rows)}}
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
