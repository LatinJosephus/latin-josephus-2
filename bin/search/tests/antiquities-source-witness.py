#!/usr/bin/env python3
"""Independent source witness for Antiquities Proem and Books I–XX.

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
SOURCE_COMMIT = "55bf610245860eab91166fdb7e4fba891f2c335b"
SPECS = [
    ("preface", 1, 1, 26, "e0588da38fe3d3e9f69735a79b204556906b1377cf8e4cf8b7ec3ce396789015"),
    ("book-01", 1, 27, 346, "5d05cb131cfdfeb1612993f034a3264406486ac4f082f5176b63bddd84dca02b"),
    ("book-02", 2, 1, 349, "b85c7973ff8183857f87d55a46c6db8b22c5ec078b8d7d5421f300acaa80c5f1"),
    ("book-03", 3, 1, 322, "4e2f268e05cd88a5cedccab1b0c9e8fd3315f013d89516eb17ca7c4c49ce6e59"),
    ("book-04", 4, 1, 331, "9f7075672bab18c816d17f05d249ecbb2abd20945b385398659752c29adb90b1"),
    ("book-05", 5, 1, 362, "9cc8e8d13ae376d16bcdab313d0e037aaf9d059dffc34abb0d21d9fd63420554"),
    ("book-06", 6, 1, 378, "98d31d890b841cafb6a50ecd213e479ea6d1c619d1fd8d19fd7ad030cfba894f"),
    ("book-07", 7, 1, 394, "0614d4b2180702b0286e74c7971c35ce386a015a397decf2d4b118877df507dd"),
    ("book-08", 8, 1, 420, "511b92a43ae07a0897cb8dfc5f0ec790e9c5d0bc8195b85e59bbe1096755c4af"),
    ("book-09", 9, 1, 291, "a018cf1fce87300451a6988c002e3a95be991ea6a685b443cceb27e387084640"),
    ("book-10", 10, 1, 281, "a842b24648312e74e886fa91ddfc016724cd949b20b4e475c5de696645632863"),
]
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII", 13: "XIII", 14: "XIV", 15: "XV", 16: "XVI", 17: "XVII", 18: "XVIII", 19: "XIX", 20: "XX"}
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
                              "milestone", "add", "del", "s", "ref", "anchor", "gap", "trailer",
                              "cb", "corr", "unclear", "expan", "head"}
    rows = []
    paragraph_rows = []
    excluded = []
    active = None
    current_p = None
    raw_offset = 0
    editorial = []
    niese_evidence = []

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
        if active is not None and number == active["section"]:
            assert (book, number) == (8, 255) and kind == "num", ("Unexpected repeated label", source, number)
            return
        expected = rows[-1]["section"] + 1 if rows else first
        if book == 9 and expected == 51:
            expected = 110
        assert number == expected, ("Niese sequence", source, number, expected)
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
            if book == 7 and current_p in {f"latin-book07-num{n}" for n in (69, 71, 78, 87, 90, 96)}:
                assert node.data == " Omitted in Bamberg MS", ("Unexpected omission notice", current_p, node.data)
                excluded.append({"kind": "omission-notice", "sourceId": current_p,
                                 "rawStart": raw_offset, "rawEnd": raw_offset + len(node.data),
                                 "text": node.data, "attributes": {}})
                raw_offset += len(node.data)
                return
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
                    # These accepted coarse printed labels are displaced from
                    # the explicit Niese milestones. Preserve the label as
                    # source evidence and let the actual milestone start the
                    # section; VIII.186 retains the preceding Latin words.
                    displaced = {(8, "latin-book08-num187"), (10, "latin-book10-num151")}
                    if (book, current_p) not in displaced:
                        start(int(match[1]), "num")
            excluded.append({"kind": tag, "sourceId": current_p, "rawStart": raw_offset,
                             "rawEnd": raw_offset + len(content), "text": content,
                             "attributes": attrs(node)})
            raw_offset += len(content)
            return
        if tag == "milestone":
            assert not all_text(node) and not children(node)
            if node.getAttribute("unit") == "niese":
                niese_evidence.append({"sourceId": current_p, "rawOffset": raw_offset, "attributes": attrs(node)})
                start(int(node.getAttribute("n")), "milestone")
            elif node.getAttribute("unit") == "niese-end":
                assert name == "preface" and active["section"] == 26
                active = None
            else:
                assert book in (9, 10) and set(attrs(node)) == {"n"} and re.fullmatch(r"sbb00000114_\d+\.jpg", node.getAttribute("n")), ("Unaccepted milestone", source, attrs(node))
                if active is not None:
                    touch()
                    active["events"].append({"kind": "milestone", "sourceId": current_p,
                                             "rawOffset": raw_offset, "attributes": attrs(node)})
            return
        if tag in ("pb", "lb", "anchor", "gap", "cb"):
            assert not all_text(node) and not children(node)
            if active is not None:
                touch()
                active["events"].append({"kind": tag, "sourceId": current_p,
                                         "rawOffset": raw_offset, "attributes": attrs(node)})
            return
        assert tag in ("add", "del", "s", "ref", "corr", "unclear", "expan"), ("Unknown inline element", source, tag)
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
        if book == 9 and source_id == "latin-book09-num51":
            notice = all_text(p)
            assert notice == "[Lacuna 51–109; cf. Blatt, p. 67]" and not children(p)
            excluded.append({"kind": "lacuna-notice", "sourceId": source_id,
                             "rawStart": 0, "rawEnd": len(notice), "text": notice,
                             "attributes": attrs(p)})
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
    if book >= 6:
        for head in body.getElementsByTagName("head"):
            excluded.append({"kind": "head", "text": all_text(head), "attributes": attrs(head)})
        for note in children(body, "note"):
            excluded.append({"kind": "body-note", "text": all_text(note), "attributes": attrs(note)})
    assert len(rows) == last - first + 1 - (59 if book == 9 else 0)

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
                    "trailingWhitespace": "" if book >= 6 and not text else raw_display[right:], "rawDisplaySha256": sha(raw_display),
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
        if book >= 6:
            row["literalGaps"].extend({"kind": "literal-ellipsis", "start": u16(text[:m.start()]),
                                       "end": u16(text[:m.end()]), "text": m.group()}
                                      for m in re.finditer("…", text))
            # Scraped punctuation is explicitly source-marked erasure. The two
            # uncertainty-marked sentence periods at X.65/75 remain ordinary
            # punctuation and do not become phrase interruptions.
            for mark in row["inlineMarks"]:
                if mark["kind"] == "del" and mark["attributes"].get("rend") == "scraping" and re.fullmatch(r"\.+", mark["text"]):
                    if not any(gap["start"] <= mark["start"] and gap["end"] >= mark["end"] for gap in row["literalGaps"]):
                        row["literalGaps"].append({"kind": "source-marked-dots", "start": mark["start"],
                                                  "end": mark["end"], "text": mark["text"],
                                                  "sourceTag": "del", "sourceAttributes": mark["attributes"]})
            row["literalGaps"].sort(key=lambda gap: (gap["start"], gap["end"], gap["kind"]))
        row["teiGaps"] = [m for m in row["structuralMarkers"] if m["kind"] == "gap"]
        row["phraseBreaks"] = sorted(set([gap["start"] for gap in row["literalGaps"]]
                                          + [gap["offset"] for gap in row["teiGaps"]]))
        row["breakBefore"] = book == 1 and row["section"] == 27 or book == 3 and row["section"] in (240, 241) or book == 7 and 69 <= row["section"] <= 100 or book == 9 and row["section"] == 110 or book == 10 and row["section"] in (108, 109)
        row["citationLabel"] = f"{ROMAN[book]}.{row['section']}"
        row["url"] = f"/antiquities/?book={row['readerBook']}&niese={row['section']}"
        row.pop("events")
        row.pop("lastParagraph")
    if book == 10:
        row = next(row for row in rows if row["section"] == 108)
        source_id = "latin-book10-num108"
        label = next(item for item in excluded if item.get("sourceId") == source_id and item["kind"] == "num")
        marker = next(item for item in niese_evidence if item["sourceId"] == source_id and item["attributes"] == {"unit": "niese", "n": "109"})
        paragraph = next(item for item in paragraph_rows if item["sourceId"] == source_id)
        between = paragraph["rawText"][label["rawEnd"]:marker["rawOffset"]]
        assert row["text"] == "" and between == " " and not row["teiGaps"] and not row["literalGaps"]
        row["emptySource"] = {
            "kind": "empty-source-interval", "sourcePath": source, "sourceId": source_id,
            "label": {"sourceTag": "num", "sourceAttributes": label["attributes"], "text": label["text"],
                      "sourceTextStart": label["rawStart"], "sourceTextEnd": label["rawEnd"]},
            "nextBoundary": {"sourceTag": "milestone", "sourceAttributes": marker["attributes"],
                             "sourceTextOffset": marker["rawOffset"]},
            "interveningText": between,
        }
    file = {"sourceFile": source, "book": book, "readerBook": "preface" if name == "preface" else book,
                  "sha256": sha(raw), "acceptedLF_sha256": accepted_hash,
                  "nieseRange": [first, last], "sections": len(rows),
                  "wordTokens": sum(len(row["tokens"]) for row in rows),
                  "stableIds": len(ids), "bodyTags": dict(body_tags),
                  "paragraphs": paragraph_rows, "excluded": excluded}
    if book >= 6:
        file["missingNieseRanges"] = [[51, 109]] if book == 9 else []
    return rows, file


# Independent XI–XX registry witness. This code uses minidom node identities
# and raw paragraph text offsets; it does not import the production extractor.
REGISTERED_SPECS = {
    11: (347, 347, 354, 58, '6c2624bbda467f64c1598530668eadbc727a4d410a549b92d65d98cc9235dbd0', 'b89420a9520192d592d9166eb5cc340b1d1dd13e68b7641514be6e9dd36fc309'),
    12: (434, 433, 433, 71, '63c1b84520577054e10faa059f53f4bffb71714cf724008f7f9d511f85d4568f', '6a181082bdebef79324aed4023ce532fc3086abbf1196a9a73a539ccb5a6d02a'),
    13: (433, 431, 431, 88, 'bad4303a38804f5c6bc0c274573eb81c78ba478d807008fd3fa4f633681fc95b', '00601dd32d0cc836beb45129cdc507608ced05de305b6e4d46899571b515ead1'),
    14: (491, 489, 489, 115, '211f49930eef6fa3a93836b8d18e32a3afa05656307e75d91e3d59d428485a76', '99361742e1e0aa7fe77ee61b879b283a6ec30692fb006d953ee5700050ab06f9'),
    15: (425, 423, 423, 66, '6b563b6bfa0ddd96c52030377043440e88aa90dd83913c67b5c940f4fcb02485', 'b2c39132e1e6d24ee94eb23fcee549ab104e4f92b3f89e7aa972b22a3f453f35'),
    16: (404, 380, 383, 61, '25151895a46d2c8d9d6fba53bdcf92afadc689ab834a7fd4d152f1df6acc12fa', '4255de34279ae13ff2da174421db8f98a9fbac37e66cf53bd4728cf46ae6fbfb'),
    17: (355, 355, 355, 61, 'efdcd622593626a3b9740745c1b1e23755b07d59c3423a02e76c453ed7df8c2b', '0613bbbd33166e805ca4f412f182b1ee9a5a166e1a302b3a9d011b44331a7a5f'),
    18: (379, 377, 377, 57, 'dec6665c846a7f90227502fffbc949bd0c571ed0e958ed0be1b95047a0b3be50', 'fdc0324aed5d8309cae28178c945ec0b1ea406a54f8a4625355ac6c69ef1e501'),
    19: (366, 366, 366, 52, '01e991bf1ef3a479b31c86255fafea36529ddededbb8b39ba79130c0c3c889c4', '7404cee1c29f29f991da2d30553a5259a446d9f576286b69365a717fac32dcc9'),
    20: (268, 257, 257, 51, '84308f674a71fdb50a44f17097d48a1d57a79ae8b260cb69fa0afad0c187caa7', '3542ef335653869483d9f62c41ce14687ab0845b47f5045eb428aef7b65094c3'),
}


def node_path(node):
    if node.parentNode.nodeType == Node.DOCUMENT_NODE:
        return '/' + node.localName + '[1]'
    peers = children(node.parentNode, node.localName)
    return node_path(node.parentNode) + '/' + node.localName + '[' + str(peers.index(node) + 1) + ']'


def tokens_with_tei_breaks(text, offsets):
    """Split only explicitly declared zero-width TEI seams before tokenizing."""
    wanted = set(offsets)
    points, position = [0], 0
    for index, character in enumerate(text):
        if position in wanted and index:
            points.append(index)
        position += u16(character)
    assert wanted <= {u16(text[:index]) for index in range(len(text) + 1)}
    points.append(len(text))
    result = []
    for first, last in zip(points, points[1:]):
        shift = u16(text[:first])
        result.extend({**token, 'start': token['start'] + shift, 'end': token['end'] + shift}
                      for token in tokens(text[first:last]))
    return result


def extract_registered_file(root, book, order):
    last, count, record_count, paragraph_count, xml_hash, registry_hash = REGISTERED_SPECS[book]
    source = f'assets/xml/antiquities/Latin/book-{book:02}.xml'
    registry_source = f'assets/xml/antiquities/niese/book-{book:02}.json'
    raw, registry_raw = (root / source).read_bytes(), (root / registry_source).read_bytes()
    for value, expected, path in [(raw, xml_hash, source), (registry_raw, registry_hash, registry_source)]:
        normalized = value.replace(b'\r\n', b'\n')
        assert b'\r' not in normalized and sha(normalized) == expected, ('Unaccepted source', path)
    assert b'<!DOCTYPE' not in raw.upper() and b'<!ENTITY' not in raw.upper()
    registry = json.loads(registry_raw)
    assert registry['book'] == book and registry['range'] == [1, last]
    dom = minidom.parseString(raw)
    assert dom.documentElement.namespaceURI == TEI
    body = dom.getElementsByTagName('body')[0]
    elements = [body] + list(body.getElementsByTagName('*'))
    with_ids = [e for e in dom.getElementsByTagName('*') if e.hasAttribute('xml:id')]
    idmap = {e.getAttribute('xml:id'): e for e in with_ids}
    assert len(idmap) == len(with_ids)
    all_paragraphs = list(body.getElementsByTagName('p'))
    first = next(i for i, p in enumerate(all_paragraphs)
                 if p.getAttribute('xml:id').startswith(f'latin-book{book:02}-num'))
    narrative = all_paragraphs[first:]
    assert len(narrative) == paragraph_count
    excluded = [{'kind': 'front-matter-paragraph', 'sourceXPath': node_path(p), 'text': all_text(p)}
                for p in all_paragraphs[:first]]
    narrative_elements = {node for p in narrative for node in [p] + list(p.getElementsByTagName('*'))}
    for node in elements:
        if node.localName in ('head', 'trailer') or node.localName == 'note' and node not in narrative_elements:
            excluded.append({'kind': node.localName, 'sourceXPath': node_path(node),
                             'text': all_text(node), 'attributes': attrs(node)})

    stream = ''
    narrative_ended, end_control = False, None
    positions, paragraph_of = {}, {}
    paragraphs, chunks, marks, markers = [], [], [], []
    structural = {'milestone', 'pb', 'cb', 'lb', 'anchor', 'gap'}
    inline = {'add', 'del', 'unclear', 'corr', 'expan', 's', 'ref'}
    for pindex, paragraph in enumerate(narrative):
        if pindex:
            stream += '\n\n'
        paragraph_start = len(stream)
        raw_offset = 0
        source_id = paragraph.getAttribute('xml:id') or 'xpath:' + node_path(paragraph)

        def walk(node):
            nonlocal stream, raw_offset, narrative_ended, end_control
            if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                # The accepted ranges deliberately stop before these exact
                # source notations. Preserve their raw positions separately;
                # they are neither Latin tokens nor new canonical sections.
                gap_notation = (book == 16 and source_id in {
                    'latin-book16-num188', 'latin-book16-num194', 'latin-book16-num395'
                } and node.data == '[...]')
                lacuna_notice = (book == 20 and source_id == 'latin-book20-num34'
                    and node.data == '[Niese sections 26–37 largely missing; cf. Blatt, p. 68]')
                if gap_notation or lacuna_notice:
                    expected_control = {
                        'latin-book16-num188': 'niese-latin-book16-end188',
                        'latin-book16-num395': 'niese-latin-book16-end394',
                        'latin-book20-num34': 'niese-latin-book20-end26',
                    }.get(source_id)
                    control = node.previousSibling if expected_control else node.parentNode
                    assert control.nodeType == Node.ELEMENT_NODE
                    assert control.getAttribute('xml:id') == (expected_control or source_id)
                    assert control is (idmap[expected_control] if expected_control else paragraph)
                    excluded.append({'kind': 'source-gap-notation' if gap_notation else 'lacuna-notice',
                                     'sourceId': source_id, 'rawStart': raw_offset,
                                     'rawEnd': raw_offset + len(node.data), 'text': node.data,
                                     'attributes': attrs(control), 'sourceXPath': node_path(control),
                                     'sourceTag': control.localName,
                                     'globalOffset': len(stream)})
                    raw_offset += len(node.data)
                    return
                if narrative_ended:
                    assert book == 12 and source_id == 'latin-book12-num426'
                    assert node.data == 'Flauii iosepp FLAUII IOSEPPI IUDAEICAE ANTIQUITATIS LIBER DUODECIMUS EXPLICIT'
                    excluded.append({'kind': 'book-subscription', 'sourceId': source_id,
                                     'rawStart': raw_offset, 'rawEnd': raw_offset + len(node.data),
                                     'text': node.data, 'attributes': attrs(end_control),
                                     'sourceXPath': node_path(end_control), 'sourceTag': 'milestone'})
                    raw_offset += len(node.data)
                    return
                begin = len(stream)
                stream += node.data
                if node.data:
                    chunks.append({'start': begin, 'end': len(stream), 'sourceId': source_id,
                                   'rawStart': raw_offset, 'rawEnd': raw_offset + len(node.data),
                                   'text': node.data})
                raw_offset += len(node.data)
                return
            assert node.nodeType == Node.ELEMENT_NODE and node.namespaceURI == TEI
            tag = node.localName
            assert tag in structural | inline | {'p', 'num', 'note'}
            paragraph_of[node] = pindex
            positions[node] = {'before': len(stream)}
            opening_numeral = (book == 15 and pindex == 0 and tag == 'add'
                               and node is children(paragraph, 'add')[0]
                               and attrs(node) == {'hand': 'post', 'place': 'marginleft'}
                               and all_text(node) == 'I')
            if tag in {'num', 'note'} or opening_numeral:
                value = all_text(node)
                excluded.append({'kind': 'chapter-annotation-before-first-registered-interval' if opening_numeral else tag,
                                 'sourceId': source_id, 'rawStart': raw_offset,
                                 'rawEnd': raw_offset + len(value), 'text': value,
                                 'attributes': attrs(node), 'sourceXPath': node_path(node)})
                raw_offset += len(value)
            else:
                begin, raw_begin = len(stream), raw_offset
                if tag in structural:
                    assert not children(node) and not all_text(node)
                    markers.append({'kind': tag, 'sourceId': source_id, 'rawOffset': raw_offset,
                                    'globalOffset': len(stream), 'attributes': attrs(node), 'sourceXPath': node_path(node)})
                for child in node.childNodes:
                    walk(child)
                if tag == 'milestone' and node.getAttribute('unit') == 'niese-end':
                    assert book == 12 and not narrative_ended
                    narrative_ended, end_control = True, node
                if tag in inline:
                    marks.append({'kind': tag, 'sourceId': source_id,
                                  'start': begin, 'end': len(stream),
                                  'rawStart': raw_begin, 'rawEnd': raw_offset, 'attributes': attrs(node)})
            positions[node]['after'] = len(stream)

        walk(paragraph)
        value = all_text(paragraph)
        assert raw_offset == len(value)
        parent = paragraph.parentNode
        chapter = parent.getAttribute('n') if parent.localName == 'div2' else ''
        paragraphs.append({'sourceId': source_id, 'sourceXPath': node_path(paragraph),
                           'rawText': value, 'rawTextSha256': sha(value), 'chapter': chapter,
                           'start': paragraph_start, 'end': len(stream)})

    def locate(point):
        kind = point['kind']
        if kind == 'book-end':
            return len(stream)
        element = idmap[point['target']]
        if kind == 'element-edge':
            for step in point['edge'].split('/'):
                match = re.fullmatch(r'([\w-]+)\[(\d+)\]', step)
                assert match, point
                choices = children(element, match[1])
                if match[1] == 'milestone' and registry.get('structuralMilestoneUnits'):
                    choices = [e for e in choices if (e.getAttribute('unit') if e.hasAttribute('unit')
                               or book <= 15 else None) in registry['structuralMilestoneUnits']]
                element = choices[int(match[2]) - 1]
        elif kind == 'niese-milestone':
            element = next(e for e in element.getElementsByTagName('milestone')
                           if e.getAttribute('unit') == 'niese' and e.getAttribute('n') == str(point['n']))
        assert kind in {'paragraph', 'paragraph-end', 'element', 'element-edge', 'niese-milestone', 'anchor'}
        return positions[element]['before' if kind == 'paragraph' else 'after']

    intervals = []
    if book in (11, 16, 17):
        for section in registry['sections']:
            for rank, span in enumerate(section['Latin'].get('spans', []), 1):
                intervals.append({'section': section['number'], 'start': locate(span['start']),
                                  'end': locate(span['end']), 'role': span.get('role', 'primary'),
                                  'occurrence': span.get('occurrence', span['start']['target']),
                                  'rank': span.get('continuationRank', rank),
                                  'startKind': 'registered-span', 'registeredSpan': span})
        intervals.sort(key=lambda interval: (interval['start'], interval['end']))
    elif book >= 18:
        for section in registry['sections']:
            latin = section['Latin']
            if not latin['available']:
                continue
            number = section['number']
            if latin.get('start'):
                start = locate(latin['start'])
                start_kind = 'registered-start'
            else:
                starts = [element for element in elements if element in positions
                          and element.localName == 'milestone'
                          and element.getAttribute('unit') == 'niese'
                          and element.getAttribute('n') == str(number)]
                assert len(starts) == 1, ('Missing or ambiguous accepted start', book, number)
                start = positions[starts[0]]['after']
                start_kind = 'milestone'
            intervals.append({'section': number, 'start': start, 'role': 'primary',
                              'occurrence': f'Latin-{book}-{number}-1', 'rank': 1,
                              'startKind': start_kind, 'endTarget': latin.get('endTarget')})
        intervals.sort(key=lambda interval: interval['start'])
        for index, interval in enumerate(intervals):
            interval['end'] = (locate({'kind': 'anchor', 'target': interval['endTarget']})
                               if interval['endTarget'] else intervals[index + 1]['start']
                               if index + 1 < len(intervals) else len(stream))
    else:
        suppressed = {(entry['paragraph'], entry['label']) for entry in registry.get('suppressedLatinLabels', [])}
        for element in elements:
            if element not in paragraph_of:
                continue
            tag = element.localName
            if tag == 'num':
                label = all_text(element).strip()
                source_id = paragraphs[paragraph_of[element]]['sourceId']
                if (source_id, label) in suppressed:
                    continue
                match = LABEL.fullmatch(label)
                assert match, ('Unreviewed numeric label', source, label)
                number = int(match[1])
            elif tag == 'milestone' and element.getAttribute('unit') == 'niese':
                number = int(element.getAttribute('n'))
            else:
                continue
            intervals.append({'section': number, 'start': positions[element]['after'], 'role': 'primary',
                              'occurrence': f'Latin-{book}-{number}-1', 'rank': 1, 'startKind': tag})
        intervals.sort(key=lambda interval: interval['start'])
        for index, interval in enumerate(intervals):
            interval['end'] = intervals[index + 1]['start'] if index + 1 < len(intervals) else len(stream)
    available = {entry['number'] for entry in registry['sections'] if entry['Latin']['available']}
    primary = [interval for interval in intervals if interval['role'] == 'primary']
    assert len(available) == count and {interval['section'] for interval in primary} == available
    assert len(intervals) == record_count
    assert len({interval['occurrence'] for interval in intervals}) == record_count
    assert not stream[:intervals[0]['start']].strip() and not stream[intervals[-1]['end']:].strip()
    for left, right in zip(intervals, intervals[1:]):
        assert left['end'] <= right['start'] and not stream[left['end']:right['start']].strip()
    counts = Counter(interval['section'] for interval in primary)
    passages = {passage['occurrence']: passage for passage in registry.get('sourcePassages', [])}
    rows = []
    for interval in intervals:
        section = interval['section']
        canonical = f'antiquities-latin-bamberg78-{book}-{section}'
        identifier = canonical
        citation = f'{ROMAN[book]}.{section}'
        extra = {'citationUnitId': canonical, 'citationUnitCitation': citation}
        if interval['role'] == 'interpolation':
            passage = passages[interval['occurrence']]
            assert passage['AntiquitiesIdentity'] is False and passage['primaryAntiquitiesFragment'] is False
            section = passage['identity']
            identifier = f'antiquities-latin-bamberg78-{book}-{section}'
            suffix = section.split('.')[-1]
            citation = f'XI, interpolated Bellum IV.{suffix}'
            extra = {'sourcePassage': passage, 'sourceOccurrence': interval['occurrence'],
                     'citationUnitId': identifier, 'citationUnitCitation': citation}
        elif counts[section] > 1:
            identifier += '-' + interval['occurrence']
            extra.update({'sourceOccurrence': interval['occurrence'], 'continuationRank': interval['rank'],
                          'fragmentCount': counts[section]})
            citation += f" (portion {interval['rank']} of {counts[section]})"
        row = {'id': identifier, 'book': book, 'section': section, 'sourceFile': source,
               'readerBook': book, 'readerNiese': interval['section'], 'sourceIds': [],
               'startKind': interval['startKind'], 'order': order + len(rows),
               'sourceSpans': [], 'inlineMarks': [], 'structuralMarkers': [],
               'boundaryWhitespace': [], 'text': '', 'breakBefore': (book, section) in {(16, 200), (20, 37)},
               'citationLabel': citation, 'url': f"/antiquities/?book={book}&niese={interval['section']}",
               'identityEvidence': {key: interval[key] for key in ('section', 'role', 'occurrence', 'rank')}, **extra}
        maps = []
        for paragraph in paragraphs:
            begin, end = max(interval['start'], paragraph['start']), min(interval['end'], paragraph['end'])
            if begin >= end:
                continue
            raw_piece = stream[begin:end]
            content = raw_piece.strip()
            first_content = begin + (len(raw_piece) - len(raw_piece.lstrip()) if content else len(raw_piece))
            last_content = end - len(raw_piece) + len(raw_piece.rstrip()) if content else first_content
            if content and row['text']:
                offset = u16(row['text'])
                row['text'] += '\n\n'
                row['sourceSpans'].append({'kind': 'separator', 'start': offset, 'end': offset + 2, 'text': '\n\n'})
            display_start = len(row['text'])
            row['text'] += content
            maps.append({'sourceId': paragraph['sourceId'], 'start': first_content, 'end': last_content,
                         'displayStart': display_start})
            for chunk in chunks:
                if chunk['sourceId'] != paragraph['sourceId']:
                    continue
                lo, hi = max(first_content, chunk['start']), min(last_content, chunk['end'])
                if lo < hi:
                    first16 = u16(row['text'][:display_start + lo - first_content])
                    last16 = u16(row['text'][:display_start + hi - first_content])
                    row['sourceSpans'].append({'kind': 'text', 'start': first16, 'end': last16,
                        'text': stream[lo:hi], 'sourceId': chunk['sourceId'],
                        'rawStart': chunk['rawStart'] + lo - chunk['start'],
                        'rawEnd': chunk['rawStart'] + hi - chunk['start']})
                for trim_first, trim_last in [(begin, first_content), (last_content, end)]:
                    lo, hi = max(trim_first, chunk['start']), min(trim_last, chunk['end'])
                    if lo < hi:
                        row['boundaryWhitespace'].append({'sourceId': chunk['sourceId'],
                            'rawStart': chunk['rawStart'] + lo - chunk['start'],
                            'rawEnd': chunk['rawStart'] + hi - chunk['start'], 'text': stream[lo:hi]})
        text = row['text']
        assert text and ''.join(span['text'] for span in row['sourceSpans']) == text
        row['sourceIds'] = list(dict.fromkeys(span['sourceId'] for span in row['sourceSpans'] if span['kind'] == 'text'))
        row['sourceId'] = row['sourceIds'][0]
        row['rawStart'] = next(span['rawStart'] for span in row['sourceSpans'] if span['kind'] == 'text')
        row['textSha256'] = sha(text)
        raw_display = stream[interval['start']:interval['end']]
        row['untrimmedDisplaySha256'] = sha(raw_display)
        row['rawDisplaySha256'] = sha(raw_display)
        row['leadingWhitespace'] = raw_display[:len(raw_display) - len(raw_display.lstrip())]
        row['trailingWhitespace'] = raw_display[len(raw_display.rstrip()):]
        for mark in marks:
            for mapping in maps:
                if mark['sourceId'] != mapping['sourceId']:
                    continue
                lo, hi = max(mapping['start'], mark['start']), min(mapping['end'], mark['end'])
                if lo < hi:
                    a, z = mapping['displayStart'] + lo - mapping['start'], mapping['displayStart'] + hi - mapping['start']
                    row['inlineMarks'].append({'kind': mark['kind'], 'start': u16(text[:a]), 'end': u16(text[:z]),
                                               'text': text[a:z], 'attributes': mark['attributes']})
        for marker in markers:
            point = marker['globalOffset']
            terminal = (interval is intervals[-1] and point == interval['end']
                        and marker['kind'] == 'milestone' and marker['attributes'].get('unit') == 'niese-end')
            range_closure = (point == interval['end'] and (
                book == 16 and marker['kind'] == 'milestone'
                and marker['attributes'].get('unit') == 'niese-range-end'
                and marker['attributes'].get('n') == str(section)
                or book == 20 and section == 26 and marker['kind'] == 'anchor'
                and marker['attributes'].get('xml:id') == 'niese-latin-book20-end26'))
            if not interval['start'] <= point < interval['end'] and not terminal and not range_closure:
                continue
            mapping = next((value for value in maps if value['sourceId'] == marker['sourceId']), None)
            if mapping is None:
                assert marker['kind'] != 'gap'
                if not range_closure:
                    continue
                offset = len(text)
            else:
                offset = mapping['displayStart'] + max(0, min(mapping['end'], point) - mapping['start'])
            row['structuralMarkers'].append({key: marker[key] for key in ('kind', 'sourceId', 'rawOffset', 'attributes')}
                                           | {'offset': u16(text[:offset])})
        row['literalGaps'] = [{'kind': 'literal-ellipsis' if match.group() == '…' else 'literal-dots',
                               'start': u16(text[:match.start()]), 'end': u16(text[:match.end()]), 'text': match.group()}
                              for match in re.finditer(r'\.{2,}|…|(?<=<)\.(?=>)', text)]
        for mark in row['inlineMarks']:
            if (mark['kind'] == 'del' and mark['attributes'].get('rend') in {'scraping', 'fading'}
                    and re.fullmatch(r'\.+', mark['text'])
                    and not any(gap['start'] == mark['start'] and gap['end'] == mark['end'] for gap in row['literalGaps'])):
                row['literalGaps'].append({'kind': 'source-marked-dots', 'start': mark['start'], 'end': mark['end'],
                                           'text': mark['text'], 'sourceAttributes': mark['attributes']})
        row['literalGaps'].sort(key=lambda gap: (gap['start'], gap['end'], gap['kind']))
        row['teiGaps'] = [marker for marker in row['structuralMarkers'] if marker['kind'] == 'gap']
        row['phraseBreaks'] = sorted({gap['start'] for gap in row['literalGaps']} | {gap['offset'] for gap in row['teiGaps']})
        row['tokens'] = tokens_with_tei_breaks(text, [gap['offset'] for gap in row['teiGaps']])
        rows.append(row)
    if book >= 16:
        def xml_attributes(values):
            return {('{http://www.w3.org/XML/1998/namespace}id' if name == 'xml:id' else name): value
                    for name, value in values.items()}

        def source_marker(node):
            paragraph = paragraphs[paragraph_of[node]]
            candidates = [marker for marker in markers if marker['sourceId'] == paragraph['sourceId']
                          and marker['kind'] == node.localName and marker['attributes'] == attrs(node)
                          and marker['globalOffset'] == positions[node]['before']]
            assert len(candidates) == 1
            return {'sourceId': paragraph['sourceId'], 'sourceXPath': node_path(node),
                    'sourceTag': node.localName, 'sourceAttributes': xml_attributes(attrs(node)),
                    'sourceTextOffset': candidates[0]['rawOffset']}

        source_gap_exclusions = [
            {'kind': 'excluded-' + item['kind'], 'sourceId': item['sourceId'],
             'sourceXPath': item['sourceXPath'], 'sourceTag': item['sourceTag'],
             'sourceAttributes': xml_attributes(item['attributes']),
             'sourceTextStart': item['rawStart'], 'sourceTextEnd': item['rawEnd'],
             'text': item['text'], 'textSha256': sha(item['text'])}
            for item in excluded if item['kind'] in {'source-gap-notation', 'lacuna-notice'}]
        expected_exclusions = {16: [('latin-book16-num188', 59, 64), ('latin-book16-num194', 0, 5),
                                    ('latin-book16-num395', 0, 5)],
                               20: [('latin-book20-num34', 0, 56)]}.get(book, [])
        assert [(item['sourceId'], item['sourceTextStart'], item['sourceTextEnd'])
                for item in source_gap_exclusions] == expected_exclusions
        explicit_boundaries = []
        if book in (16, 20):
            preceding, following = (188, 200) if book == 16 else (26, 37)
            end_node = idmap[f'niese-latin-book{book}-end{preceding}']
            start_nodes = [element for element in elements if element in positions
                           and element.localName == 'milestone' and element.getAttribute('unit') == 'niese'
                           and element.getAttribute('n') == str(following)]
            assert len(start_nodes) == 1
            start_node = start_nodes[0]
            relevant_ids = {'latin-book16-num188', 'latin-book16-num194'} if book == 16 else {'latin-book20-num34'}
            evidence = {'kind': 'registered-source-discontinuity', 'sourcePath': source,
                        'precedingSection': preceding, 'followingSection': following,
                        'precedingEnd': source_marker(end_node), 'followingStart': source_marker(start_node),
                        'excludedSourceSpans': [entry for entry in source_gap_exclusions if entry['sourceId'] in relevant_ids],
                        'qualification': 'This explicit source boundary blocks phrase adjacency; the cause and extent of absent Latin are not inferred.'}
            previous, next_row = [next(row for row in rows if row['section'] == number) for number in (preceding, following)]
            assert rows.index(next_row) == rows.index(previous) + 1
            assert next_row['breakBefore'] and len(evidence['excludedSourceSpans']) == (2 if book == 16 else 1)
            next_row['sourceBoundaryEvidence'] = evidence
            explicit_boundaries.append(evidence)
        # A Niese marker may divide two letter runs with no intervening space.
        # Such a canonical boundary separates the indexed tokens but remains
        # joinable in whole-book phrase scope. Audit every new physical seam.
        token_boundaries = []
        for previous, next_row in zip(rows, rows[1:]):
            last_span = next(span for span in reversed(previous['sourceSpans']) if span['kind'] == 'text')
            first_span = next(span for span in next_row['sourceSpans'] if span['kind'] == 'text')
            if (last_span['sourceId'] == first_span['sourceId'] and last_span['rawEnd'] == first_span['rawStart']
                    and unicodedata.category(previous['text'][-1])[0] in 'LMN'
                    and unicodedata.category(next_row['text'][0])[0] in 'LN'):
                token_boundaries.append({'sourceId': first_span['sourceId'], 'sourceTextOffset': first_span['rawStart'],
                                         'precedingSection': previous['section'], 'followingSection': next_row['section'],
                                         'leftToken': previous['tokens'][-1]['term'], 'rightToken': next_row['tokens'][0]['term']})
        assert token_boundaries == ([{'sourceId': 'latin-book17-num32', 'sourceTextOffset': 3308,
                                     'precedingSection': 41, 'followingSection': 42,
                                     'leftToken': 'eleuati', 'rightToken': 'cum'}] if book == 17 else [])
        token_boundary_evidence = []
        for boundary in token_boundaries:
            previous, next_row = [next(row for row in rows if row['section'] == boundary[name])
                                  for name in ('precedingSection', 'followingSection')]
            node = idmap[f"niese-latin-book{book}-{boundary['followingSection']}"]
            paragraph = paragraphs[paragraph_of[node]]
            marker_evidence = source_marker(node)
            assert marker_evidence['sourceTextOffset'] == boundary['sourceTextOffset']
            at = boundary['sourceTextOffset']
            left = previous['text'][previous['tokens'][-1]['start']:]
            right = next_row['text'][:next_row['tokens'][0]['end']]
            assert paragraph['rawText'][at - len(left):at + len(right)] == left + right
            token_boundary_evidence.append({'kind': 'registered-section-token-boundary', 'sourcePath': source,
                                            **marker_evidence,
                                            'flatTextOffset': positions[node]['before'] - paragraph['start'],
                                            'precedingRecordId': previous['id'], 'followingRecordId': next_row['id'],
                                            'sourceText': left + right, 'precedingText': left, 'followingText': right,
                                            'qualification': 'The adopted Niese boundary separates two search tokens without inserting or changing a source character. Whole-book phrase adjacency remains available.'})
        def marker_identity(marker):
            return (marker['kind'], marker['sourceId'], marker['rawOffset'], json.dumps(marker['attributes'], sort_keys=True))

        owned_markers = Counter(marker_identity(marker) for row in rows for marker in row['structuralMarkers'])
        unassigned_markers = []
        for marker in markers:
            key = marker_identity(marker)
            if owned_markers[key]:
                owned_markers[key] -= 1
            else:
                unassigned_markers.append({key: marker[key] for key in ('kind', 'sourceId', 'rawOffset', 'attributes', 'sourceXPath')})
        assert not any(owned_markers.values())
        assert [(marker['kind'], marker['sourceId'], marker['rawOffset'], marker['attributes']) for marker in unassigned_markers] == (
            [('lb', 'latin-book16-num194', 5, {})] if book == 16 else
            [('lb', 'latin-book20-num34', 56, {})] if book == 20 else [])
    unavailable = [entry for entry in registry['sections'] if not entry['Latin']['available']]
    missing_ranges = []
    for entry in unavailable:
        number = entry['number']
        if missing_ranges and missing_ranges[-1][1] == number - 1:
            missing_ranges[-1][1] = number
        else:
            missing_ranges.append([number, number])
    file = {'sourceFile': source, 'book': book, 'readerBook': book, 'sha256': sha(raw),
            'acceptedLF_sha256': xml_hash, 'nieseRange': [1, last], 'sections': len(rows),
            'canonicalSections': len(available), 'wordTokens': sum(len(row['tokens']) for row in rows),
            'stableIds': len(idmap), 'bodyTags': dict(Counter(e.localName for e in elements)),
            'paragraphs': [{key: value for key, value in paragraph.items() if key not in ('start', 'end')}
                           for paragraph in paragraphs], 'excluded': excluded,
            'missingNieseRanges': missing_ranges, 'unavailableLatinIdentities': unavailable,
            'identityRegistry': {'path': registry_source, 'sha256': sha(registry_raw), 'acceptedLF_sha256': registry_hash},
            'suppressedLatinLabels': registry.get('suppressedLatinLabels', []),
            'sourceOrder': [row['section'] for row in rows]}
    if book >= 16:
        file.update({'sourceGapExclusions': source_gap_exclusions,
                     'explicitSourceBoundaries': explicit_boundaries,
                     'registeredTokenBoundaries': token_boundaries,
                     'registeredTokenBoundaryEvidence': token_boundary_evidence,
                     'unassignedStructuralMarkers': unassigned_markers})
    return rows, file


def build(root):
    rows, files = [], []
    for spec in SPECS:
        new_rows, file = extract_file(root, spec, len(rows))
        rows.extend(new_rows)
        files.append(file)
    assert len(rows) == 3415
    assert sum(len(row["literalGaps"]) for row in rows if row["book"] <= 5) == 6
    assert [(row["book"], row["section"]) for row in rows if not row["text"]] == [(3, 240)] + [(7, n) for n in range(69, 100)] + [(10, 108)]
    assert sum(len(row["teiGaps"]) for row in rows) == 32
    assert sum(mark["kind"] == "add" for row in rows for mark in row["inlineMarks"]) == 45
    assert sum(mark["kind"] == "del" for row in rows for mark in row["inlineMarks"]) == 30
    assert sum(x["kind"] == "omission-notice" for f in files for x in f["excluded"]) == 6
    assert sum(x["kind"] == "lacuna-notice" for f in files for x in f["excluded"]) == 1
    for book in range(11, 21):
        new_rows, file = extract_registered_file(root, book, len(rows))
        rows.extend(new_rows)
        files.append(file)
    assert len(rows) == 7283
    assert sum(len(row["tokens"]) for row in rows) == 265023
    return {"sourceCommit": SOURCE_COMMIT, "files": files, "rows": rows,
            "totals": {"books": 20, "sourceFiles": 21, "sections": len(rows),
                       "wordTokens": sum(len(row["tokens"]) for row in rows)},
            "runtime": {"python": sys.version.split()[0], "unicode": unicodedata.unidata_version,
                        "xmlParser": "xml.dom.minidom"}}


if __name__ == "__main__":
    assert len(sys.argv) == 2, "Usage: antiquities-source-witness.py <source repository>"
    print(json.dumps(build(Path(sys.argv[1])), ensure_ascii=False, separators=(",", ":")))
