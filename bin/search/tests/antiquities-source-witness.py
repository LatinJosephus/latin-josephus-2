#!/usr/bin/env python3
"""Independent source witness for Antiquities Proem and Books I–V.

This verifier uses minidom and a text-node event stream, independently of the
production ElementTree extractor. It does not import any search code. Its XML
inputs are the exact accepted source commit, allowing CRLF to LF conversion.
The output preserves source-to-display spans and independently tokenizes every
unit by Unicode character category.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
from collections import Counter
from xml.dom import Node, minidom

TEI = "http://www.tei-c.org/ns/1.0"
SOURCE_COMMIT = "5d48b5285a5fa921ec5e666f60d04216e6e9270d"
SPECS = [
    ("preface", 1, 1, 26, "e0588da38fe3d3e9f69735a79b204556906b1377cf8e4cf8b7ec3ce396789015"),
    ("book-01", 1, 27, 346, "5d05cb131cfdfeb1612993f034a3264406486ac4f082f5176b63bddd84dca02b"),
    ("book-02", 2, 1, 349, "b85c7973ff8183857f87d55a46c6db8b22c5ec078b8d7d5421f300acaa80c5f1"),
    ("book-03", 3, 1, 322, "4e2f268e05cd88a5cedccab1b0c9e8fd3315f013d89516eb17ca7c4c49ce6e59"),
    ("book-04", 4, 1, 331, "9f7075672bab18c816d17f05d249ecbb2abd20945b385398659752c29adb90b1"),
    ("book-05", 5, 1, 362, "9cc8e8d13ae376d16bcdab313d0e037aaf9d059dffc34abb0d21d9fd63420554"),
]
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}
LABEL = re.compile(r"\[(?:[IVXLCDMivxlcdm]+\.)?(?:[IVXLCDMivxlcdm]+\.)?(\d+)\]\Z")
LITERAL_DOTS = re.compile(r"(?<=<)\.+(?=>)|\.{3,}")


def sha(data):
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


def all_text(node):
    if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
        return node.data
    return "".join(all_text(child) for child in node.childNodes)


def attrs(node):
    return dict(node.attributes.items())


def children(node, name=None):
    return [child for child in node.childNodes if child.nodeType == Node.ELEMENT_NODE
            and (name is None or child.localName == name)]


def u16(text):
    return len(text.encode("utf-16-le")) // 2


def tokens(text):
    result = []
    start = None
    for index in range(len(text) + 1):
        category = unicodedata.category(text[index])[0] if index < len(text) else "Z"
        if start is not None and category not in "LMN":
            raw = text[start:index]
            term = unicodedata.normalize("NFC", raw).lower().replace("ς", "σ")
            result.append({"term": unicodedata.normalize("NFC", term),
                           "start": u16(text[:start]), "end": u16(text[:index])})
            start = None
        if start is None and category in "LN":
            start = index
    return result


def extract_file(root, spec, order):
    name, book, first, last, accepted_hash = spec
    source = f"assets/xml/antiquities/Latin/{name}.xml"
    raw = (root / source).read_bytes()
    lf = raw.replace(b"\r\n", b"\n")
    assert b"\r" not in lf and sha(lf) == accepted_hash, ("Unaccepted XML", source)
    assert b"<!DOCTYPE" not in raw.upper() and b"<!ENTITY" not in raw.upper()
    dom = minidom.parseString(raw)
    assert dom.documentElement.namespaceURI == TEI
    body = dom.getElementsByTagName("body")[0]
    ids = [e.getAttribute("xml:id") for e in dom.getElementsByTagName("*") if e.hasAttribute("xml:id")]
    assert len(ids) == len(set(ids)), ("Duplicate source ID", source)
    body_tags = Counter(e.localName for e in [body] + list(body.getElementsByTagName("*")))
    assert set(body_tags) <= {"body", "note", "div1", "div2", "p", "num", "pb", "lb",
                              "milestone", "add", "del", "s", "ref", "anchor", "gap", "trailer"}
    rows = []
    paragraph_rows = []
    excluded = []
    active = None
    current_p = None
    raw_offset = 0
    editorial = []

    def touch():
        if active is None:
            return
        if current_p not in active["sourceIds"]:
            active["sourceIds"].append(current_p)
        if active["lastParagraph"] is not None and active["lastParagraph"] != current_p:
            active["events"].append({"kind": "separator", "text": "\n\n"})
        active["lastParagraph"] = current_p

    def start(number, kind):
        nonlocal active
        assert number == first + len(rows), ("Niese sequence", source, number, len(rows))
        active = {"book": book, "section": number, "sourceFile": source,
                  "readerBook": "preface" if name == "preface" else book,
                  "sourceIds": [], "events": [], "lastParagraph": None,
                  "startKind": kind, "sourceId": current_p,
                  "order": order + len(rows), "rawStart": raw_offset}
        rows.append(active)
        touch()

    def walk(node):
        nonlocal raw_offset, active
        if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
            if active is None:
                assert not node.data.strip(), ("Narrative without Niese identity", source, current_p, node.data)
            else:
                touch()
                active["events"].append({"kind": "text", "text": node.data,
                                         "sourceId": current_p, "rawStart": raw_offset,
                                         "rawEnd": raw_offset + len(node.data)})
            raw_offset += len(node.data)
            return
        assert node.nodeType == Node.ELEMENT_NODE and node.namespaceURI == TEI
        tag = node.localName
        if tag in ("num", "note"):
            content = all_text(node)
            if tag == "num":
                match = LABEL.fullmatch(content.strip())
                if match:
                    start(int(match[1]), "num")
            excluded.append({"kind": tag, "sourceId": current_p, "rawStart": raw_offset,
                             "rawEnd": raw_offset + len(content), "text": content,
                             "attributes": attrs(node)})
            raw_offset += len(content)
            return
        if tag == "milestone":
            assert not all_text(node) and not children(node)
            if node.getAttribute("unit") == "niese":
                start(int(node.getAttribute("n")), "milestone")
            elif node.getAttribute("unit") == "niese-end":
                assert name == "preface" and active["section"] == 26
                active = None
            else:
                raise AssertionError(("Unaccepted milestone", source, attrs(node)))
            return
        if tag in ("pb", "lb", "anchor", "gap"):
            assert not all_text(node) and not children(node)
            if active is not None:
                touch()
                active["events"].append({"kind": tag, "sourceId": current_p,
                                         "rawOffset": raw_offset, "attributes": attrs(node)})
            return
        assert tag in ("add", "del", "s", "ref"), ("Unknown inline element", source, tag)
        begin = raw_offset
        for child in node.childNodes:
            walk(child)
        editorial.append({"kind": tag, "sourceId": current_p, "rawStart": begin,
                          "rawEnd": raw_offset, "attributes": attrs(node)})

    for p in body.getElementsByTagName("p"):
        source_id = p.getAttribute("xml:id")
        if not source_id:
            excluded.append({"kind": "heading-or-subscription", "text": all_text(p)})
            continue
        current_p = source_id
        raw_offset = 0
        touch()
        for child in p.childNodes:
            walk(child)
        raw_text = all_text(p)
        assert raw_offset == len(raw_text)
        chapter = p.parentNode.getAttribute("n") if p.parentNode.localName == "div2" else "proem"
        paragraph_rows.append({"sourceId": source_id, "rawText": raw_text,
                               "rawTextSha256": sha(raw_text), "chapter": chapter})
    for trailer in body.getElementsByTagName("trailer"):
        excluded.append({"kind": "trailer", "text": all_text(trailer)})
    assert len(rows) == last - first + 1

    for row in rows:
        # The established search convention trims a paragraph fragment's edge
        # whitespace before adding its explicit two-newline separator. Retain
        # the removed source characters here so this normalization is audited.
        row["boundaryWhitespace"] = []
        row["untrimmedDisplaySha256"] = sha("".join(event.get("text", "") for event in row["events"]))
        for index, event in enumerate(row["events"]):
            if event["kind"] != "separator":
                continue
            for direction in (-1, 1):
                scan = index + direction
                while 0 <= scan < len(row["events"]):
                    part = row["events"][scan]
                    if part["kind"] == "separator":
                        break
                    if part["kind"] != "text":
                        scan += direction
                        continue
                    value = part["text"]
                    trimmed = value.rstrip() if direction == -1 else value.lstrip()
                    removed = value[len(trimmed):] if direction == -1 else value[:len(value) - len(trimmed)]
                    if removed:
                        raw_start = part["rawEnd"] - len(removed) if direction == -1 else part["rawStart"]
                        row["boundaryWhitespace"].append({"sourceId": part["sourceId"], "rawStart": raw_start,
                                                          "rawEnd": raw_start + len(removed), "text": removed})
                        if direction == -1:
                            part["rawEnd"] -= len(removed)
                        else:
                            part["rawStart"] += len(removed)
                        part["text"] = trimmed
                    if trimmed:
                        break
                    scan += direction
        raw_display = "".join(event.get("text", "") for event in row["events"])
        text = raw_display.strip()
        left = len(raw_display) - len(raw_display.lstrip())
        right = len(raw_display.rstrip())
        row.update({"text": text, "leadingWhitespace": raw_display[:left],
                    "trailingWhitespace": raw_display[right:], "rawDisplaySha256": sha(raw_display),
                    "textSha256": sha(text), "tokens": tokens(text), "sourceSpans": [],
                    "inlineMarks": [], "structuralMarkers": []})
        position = 0
        for event in row["events"]:
            value = event.get("text", "")
            lo, hi = max(left, position), min(right, position + len(value))
            if hi > lo:
                a, b = lo - left, hi - left
                span = {"kind": event["kind"], "start": u16(text[:a]), "end": u16(text[:b]),
                        "text": raw_display[lo:hi]}
                if event["kind"] == "text":
                    span.update({"sourceId": event["sourceId"],
                                 "rawStart": event["rawStart"] + lo - position,
                                 "rawEnd": event["rawStart"] + hi - position})
                row["sourceSpans"].append(span)
            if event["kind"] not in ("text", "separator"):
                offset = u16(text[:max(0, min(len(text), position - left))])
                row["structuralMarkers"].append({**event, "offset": offset})
            position += len(value)
        assert "".join(span["text"] for span in row["sourceSpans"]) == text
        for mark in editorial:
            fragments = [span for span in row["sourceSpans"] if span["kind"] == "text"
                         and span["sourceId"] == mark["sourceId"]
                         and span["rawStart"] < mark["rawEnd"] and span["rawEnd"] > mark["rawStart"]]
            if not fragments:
                continue
            first_span, last_span = fragments[0], fragments[-1]
            first_skip = max(0, mark["rawStart"] - first_span["rawStart"])
            last_keep = min(len(last_span["text"]), mark["rawEnd"] - last_span["rawStart"])
            start16 = first_span["start"] + u16(first_span["text"][:first_skip])
            end16 = last_span["start"] + u16(last_span["text"][:last_keep])
            encoded = text.encode("utf-16-le")
            row["inlineMarks"].append({"kind": mark["kind"], "start": start16, "end": end16,
                                        "text": encoded[start16*2:end16*2].decode("utf-16-le"),
                                        "attributes": mark["attributes"]})
        row["sourceIds"] = list(dict.fromkeys(span["sourceId"] for span in row["sourceSpans"] if span["kind"] == "text")) or [row["sourceId"]]
        row["inlineMarks"].sort(key=lambda mark: (mark["start"], -mark["end"], mark["kind"]))
        row["literalGaps"] = [{"kind": "literal-dots", "start": u16(text[:m.start()]),
                                "end": u16(text[:m.end()]), "text": m.group()}
                               for m in LITERAL_DOTS.finditer(text)]
        row["teiGaps"] = [m for m in row["structuralMarkers"] if m["kind"] == "gap"]
        row["phraseBreaks"] = sorted(set([gap["start"] for gap in row["literalGaps"]]
                                          + [gap["offset"] for gap in row["teiGaps"]]))
        row["breakBefore"] = book == 1 and row["section"] == 27 or book == 3 and row["section"] in (240, 241)
        row["citationLabel"] = f"{ROMAN[book]}.{row['section']}"
        row["url"] = f"/antiquities/?book={row['readerBook']}&niese={row['section']}"
        row.pop("events")
        row.pop("lastParagraph")
    return rows, {"sourceFile": source, "book": book, "readerBook": "preface" if name == "preface" else book,
                  "sha256": sha(raw), "acceptedLF_sha256": accepted_hash,
                  "nieseRange": [first, last], "sections": len(rows),
                  "wordTokens": sum(len(row["tokens"]) for row in rows),
                  "stableIds": len(ids), "bodyTags": dict(body_tags),
                  "paragraphs": paragraph_rows, "excluded": excluded}


def build(root):
    rows, files = [], []
    for spec in SPECS:
        new_rows, file = extract_file(root, spec, len(rows))
        rows.extend(new_rows)
        files.append(file)
    assert len(rows) == 1710
    assert sum(len(row["literalGaps"]) for row in rows) == 6
    assert [(row["book"], row["section"]) for row in rows if not row["text"]] == [(3, 240)]
    assert sum(len(row["teiGaps"]) for row in rows) == 1
    assert sum(mark["kind"] == "add" for row in rows for mark in row["inlineMarks"]) == 19
    assert sum(mark["kind"] == "del" for row in rows for mark in row["inlineMarks"]) == 23
    return {"sourceCommit": SOURCE_COMMIT, "files": files, "rows": rows,
            "totals": {"books": 5, "sourceFiles": 6, "sections": len(rows),
                       "wordTokens": sum(len(row["tokens"]) for row in rows)},
            "runtime": {"python": sys.version.split()[0], "unicode": unicodedata.unidata_version,
                        "xmlParser": "xml.dom.minidom"}}


if __name__ == "__main__":
    assert len(sys.argv) == 2, "Usage: antiquities-source-witness.py <source repository>"
    print(json.dumps(build(Path(sys.argv[1])), ensure_ascii=False, separators=(",", ":")))
