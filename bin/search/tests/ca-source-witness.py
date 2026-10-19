#!/usr/bin/env python3
"""Independent SHA-pinned Contra Apionem witness; no extractor imports.

The exact contents of this file are embedded in ca-corpus-qa.mjs. That verifier
checks the standalone copy against its embedded witness before executing it.
"""
import hashlib
import json
import pathlib
import re
import sys
import unicodedata
from collections import Counter
from xml.dom import minidom, Node

root = pathlib.Path(sys.argv[1])
TEI = "http://www.tei-c.org/ns/1.0"
expected = {
    1: {"sections": 320, "tokens": 10657, "chapters": 35,
        "hash": "9e72ddadf9a0d4cd0ce20ec190ed8420dd289a4704520f79c7fc2ca5b2d39a62"},
    2: {"sections": 296, "tokens": 10361, "chapters": 41,
        "hash": "5336ba55f50d21d1a453cc98ec946dd9404a161c38824b00f2496c37ce69bc8b"},
}


def sha(data):
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


def children(node, name=None):
    return [c for c in node.childNodes if c.nodeType == Node.ELEMENT_NODE
            and (name is None or c.localName == name)]


def attrs(node):
    return dict(node.attributes.items())


def all_text(node):
    return "".join(c.data if c.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE)
                   else all_text(c) for c in node.childNodes)


def utf16(text):
    return len(text.encode("utf-16-le")) // 2


def tokens(text):
    out = []
    i = 0
    while i < len(text):
        if unicodedata.category(text[i])[0] not in "LN":
            i += 1
            continue
        j = i + 1
        while j < len(text) and unicodedata.category(text[j])[0] in "LMN":
            j += 1
        term = unicodedata.normalize("NFC", text[i:j]).lower().replace("ς", "σ")
        out.append({"term": unicodedata.normalize("NFC", term),
                    "start": utf16(text[:i]), "end": utf16(text[:j])})
        i = j
    return out


rows = []
books = []
all_ids = []
for book in (1, 2):
    path = f"assets/xml/contra-apionem/Latin/book-{book:02d}.xml"
    raw = (root / path).read_bytes()
    lf = raw.replace(b"\r\n", b"\n")
    assert b"\r" not in lf and sha(lf) == expected[book]["hash"], ("Unaccepted source", path)
    assert b"<!DOCTYPE" not in raw.upper() and b"<!ENTITY" not in raw.upper()
    dom = minidom.parseString(raw)
    assert dom.documentElement.namespaceURI == TEI
    body = dom.getElementsByTagName("body")[0]
    assert [e.localName for e in children(body)] == ["note", "pb", "div1"]
    bn = children(body, "div1")[0]
    roman = "I" if book == 1 else "II"
    assert attrs(bn) == {"n": roman, "subtype": "Latin", "type": "book", "xml:id": f"latin-apion{book}"}
    paragraphs = children(bn, "p")
    assert len(paragraphs) == expected[book]["sections"]
    assert all(e.localName == "p" for e in children(bn))
    ids = [e.getAttribute("xml:id") for e in dom.getElementsByTagName("*") if e.hasAttribute("xml:id")]
    assert len(ids) == len(set(ids)) == expected[book]["sections"] + 2
    all_ids.extend(ids)
    body_tags = Counter(e.localName for e in [body] + list(body.getElementsByTagName("*")))
    assert set(body_tags) <= {"body", "note", "pb", "div1", "p", "milestone", "q", "add", "foreign"}
    chapter = 0
    first_row_index = len(rows)
    for section, p in enumerate(paragraphs, 1):
        source_id = f"latin-apion{book}-num{section}"
        expected_attrs = {"n": str(section), "xml:id": source_id}
        if book == 1 and section in (119, 147):
            expected_attrs["ana"] = "#niese-boundary-within-preceding-lacuna"
        if book == 2 and section == 68:
            expected_attrs["ana"] = "#transcription-restoration-is"
        assert attrs(p) == expected_attrs
        parts = []
        marks = []
        markers = []
        first_text_chapter = None

        def walk(node):
            global chapter, first_text_chapter
            if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                if node.data.strip() and first_text_chapter is None:
                    first_text_chapter = chapter
                parts.append(node.data)
                return
            assert node.nodeType == Node.ELEMENT_NODE and node.namespaceURI == TEI
            kind = node.localName
            start = len("".join(parts))
            if kind in ("pb", "milestone"):
                assert not all_text(node) and not children(node)
                if kind == "milestone":
                    assert attrs(node) == {"n": str(chapter + 1), "unit": "chapter", "subtype": "boysen"}
                    chapter += 1
                else:
                    assert set(attrs(node)) == {"n"} and node.getAttribute("n").isdigit()
                markers.append({"kind": kind, "rawOffset": start, "attributes": attrs(node)})
                return
            assert kind in ("q", "add", "foreign")
            assert attrs(node) == ({"xml:lang": "grc"} if kind == "foreign" else {})
            for child in node.childNodes:
                walk(child)
            marks.append({"kind": kind, "rawStart": start, "rawEnd": len("".join(parts)), "attributes": attrs(node)})

        for child in p.childNodes:
            walk(child)
        raw_text = "".join(parts)
        assert raw_text == all_text(p)
        text = raw_text.strip()
        left = len(raw_text) - len(raw_text.lstrip())
        ts = tokens(text)
        assert ts
        inline_marks = []
        for mark in marks:
            start, end = mark["rawStart"] - left, mark["rawEnd"] - left
            assert 0 <= start < end <= len(text)
            inline_marks.append({"kind": mark["kind"], "start": utf16(text[:start]),
                                 "end": utf16(text[:end]), "text": text[start:end], "attributes": mark["attributes"]})
        asterisks = [{"start": utf16(text[:m.start()]), "end": utf16(text[:m.end()]), "text": m.group()}
                    for m in re.finditer(r"\*(?:\s*\*)*", text)]
        rows.append({"book": book, "section": section, "sourceId": source_id,
                     "text": text, "rawTextSha256": sha(raw_text),
                     "leadingWhitespace": raw_text[:left], "trailingWhitespace": raw_text[len(raw_text.rstrip()):],
                     "tokens": ts, "inlineMarks": inline_marks,
                     "editorialMarks": [{k: m[k] for k in ("kind", "start", "end", "text")}
                                        for m in inline_marks if m["kind"] == "add"],
                     "phraseBreaks": [m["start"] for m in asterisks], "asteriskMarkers": asterisks,
                     "attributes": attrs(p), "structuralMarkers": markers,
                     "chapterStart": first_text_chapter, "chapterEnd": chapter,
                     "breakBefore": book == 1 and section in (119, 147),
                     "citationLabel": f"{roman}.{section}",
                     "url": f"/contra-apionem/?book={book}&niese={section}"})
    assert chapter == expected[book]["chapters"]
    token_count = sum(len(row["tokens"]) for row in rows[first_row_index:])
    assert token_count == expected[book]["tokens"]
    books.append({"book": book, "path": path, "sha256": sha(raw), "acceptedLF_sha256": expected[book]["hash"],
                  "sections": len(paragraphs), "tokens": token_count, "stableIds": len(ids), "bodyTags": dict(body_tags)})

assert len(rows) == 616 and len(all_ids) == len(set(all_ids)) == 620
assert sum(len(row["phraseBreaks"]) for row in rows) == 25
assert sum(len(row["editorialMarks"]) for row in rows) == 1
assert sum(len(tokens(m["text"])) for row in rows for m in row["inlineMarks"] if m["kind"] == "foreign") == 7
print(json.dumps({"books": books, "rows": rows, "stableIds": len(all_ids),
                  "runtime": {"python": sys.version.split()[0], "unicode": unicodedata.unidata_version,
                              "xmlParser": "xml.dom.minidom"}}, ensure_ascii=False, separators=(",", ":")))
