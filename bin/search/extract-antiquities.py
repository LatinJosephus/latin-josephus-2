#!/usr/bin/env python3
"""Extract accepted Bamberg 78 Antiquities I–X and the separate Proem.

The source's Niese labels and milestones establish citations; physical paragraph
IDs remain provenance only. All running source characters, including add/del
content, are retained. Every paragraph can be restored from the finished search
records plus explicitly excluded labels, notes and trimmed edge whitespace.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET


TEI = "http://www.tei-c.org/ns/1.0"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
COLLECTION = "antiquities-latin-bamberg78"
EDITION = "Bamberg Msc. Class. 78"
OUTPUT_PREFIX = f"data/{COLLECTION}"
ROMANS = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X"}
PARAGRAPH_SEPARATOR = "\n\n"
BOOK_SPECS = {
    1: {"range": [27, 346], "paragraphs": 79, "milestones": 241, "chapters": 23,
        "pb": 23, "add": 19, "del": 22, "note": 12, "ref": 3, "s": 1, "anchor": 1,
        "gap": 0, "literalGaps": 2, "continuations": 0},
    2: {"range": [1, 349], "paragraphs": 76, "milestones": 274, "chapters": 17,
        "pb": 26, "add": 0, "del": 1, "note": 0, "ref": 0, "s": 0, "anchor": 0,
        "gap": 0, "literalGaps": 2, "continuations": 1},
    3: {"range": [1, 322], "paragraphs": 79, "milestones": 244, "chapters": 16,
        "pb": 24, "add": 0, "del": 0, "note": 0, "ref": 0, "s": 0, "anchor": 1,
        "gap": 1, "literalGaps": 0, "continuations": 1},
    4: {"range": [1, 331], "paragraphs": 88, "milestones": 246, "chapters": 9,
        "pb": 25, "add": 0, "del": 0, "note": 0, "ref": 0, "s": 0, "anchor": 1,
        "gap": 0, "literalGaps": 2, "continuations": 3},
    5: {"range": [1, 362], "paragraphs": 98, "milestones": 265, "chapters": 12,
        "pb": 24, "add": 0, "del": 0, "note": 0, "ref": 0, "s": 0, "anchor": 1,
        "gap": 0, "literalGaps": 0, "continuations": 1},
    6: {"range": [1, 378], "paragraphs": 83, "milestones": 297, "chapters": 15,
        "pb": 26, "add": 0, "del": 0, "note": 0, "ref": 0, "s": 0, "anchor": 0,
        "gap": 0, "literalGaps": 0, "continuations": 0},
    7: {"range": [1, 394], "paragraphs": 76, "milestones": 318, "chapters": 16,
        "pb": 28, "add": 0, "del": 0, "note": 0, "ref": 0, "s": 0, "anchor": 0,
        "gap": 31, "literalGaps": 4, "continuations": 0, "omissionNotices": 6},
    8: {"range": [1, 420], "paragraphs": 85, "milestones": 337, "chapters": 16,
        "pb": 30, "add": 0, "del": 0, "note": 0, "ref": 0, "s": 0, "anchor": 0,
        "gap": 0, "literalGaps": 1, "continuations": 2},
    9: {"range": [1, 291], "paragraphs": 46, "milestones": 186, "chapters": 4,
        "pb": 17, "cb": 33, "imageMilestones": 17, "add": 12, "del": 4, "note": 0,
        "ref": 0, "s": 0, "anchor": 0, "gap": 0, "literalGaps": 1, "continuations": 0, "corr": 11, "unclear": 1, "expan": 0},
    10: {"range": [1, 281], "paragraphs": 52, "milestones": 230, "chapters": 11,
         "pb": 22, "cb": 43, "imageMilestones": 22, "add": 14, "del": 3, "note": 19,
         "ref": 0, "s": 0, "anchor": 0, "gap": 0, "literalGaps": 2, "continuations": 0, "corr": 37, "unclear": 61, "expan": 6},
}
MISSING_SECTIONS = {9: list(range(51, 110))}
EMPTY_SECTIONS = {3: [240], 7: list(range(69, 100))}
EMPTY_SOURCE_SECTIONS = {10: [108]}
OMISSION_NOTICE_IDS = {f"latin-book07-num{n}" for n in (69, 71, 78, 87, 90, 96)}
LACUNA_NOTICE = "[Lacuna 51–109; cf. Blatt, p. 67]"
MILESTONE_STARTS = {
    "latin-book06-num271": (6, "[XII.viii]", 269),
    "latin-book06-num272": (6, "[XIII.i]", 271),
    "latin-book10-num151": (10, "[VIII.vi.151]", 150),
}
PREFACE_SPEC = {"range": [1, 26], "paragraphs": 4, "milestones": 22, "chapters": 0,
                "pb": 2, "add": 0, "del": 0, "note": 0, "ref": 0, "s": 0, "anchor": 0,
                "gap": 0, "literalGaps": 0, "continuations": 0}
CONTINUATIONS = {
    "latin-book02-num95": (2, "[VI.ii]", 95),
    "latin-book03-num179": (3, "[VII.vii]", 178),
    "latin-book04-num107": (4, "[VI.iii]", 106),
    "latin-book04-num156": (4, "[VI.xiii]", 155),
    "latin-book04-num276b": (4, "[VIII.xxxii]", 276),
    "latin-book05-num33": (5, "[I.x]", 32),
    "latin-book08-num187": (8, "[VII.iv.187]", 186),
    "latin-book08-num255": (8, "[X.iii.255]", 255),
}
HEADINGS = {
    1: " INCIP. LIB. ANTIQVITATIS IOSEPHI HISTOGRAFI",
    2: "HAEC SVNT IN SECUNDO LIBRO IOSEPHI HISTORIARUM ANTIQVITATIS IVDAEICAE",
    3: "INCIPIT LIBER TERTIUS HAEC IN SUNT IN LIBRO TERTIO IOSIPPI HISTORIARUM IUDAICAE ANTIQUITATIS",
    4: "INCIPIT LIBER QUARTUS HAEC SUNT HINC VARIO LIBRO IOSEPPI IUDAICAE ANTIQUITATIS",
    5: "HAEC INSUNT IN QUINTO LIBRO IOSEPPI HISTORIARUMIUDAICAE ANTIQUITATIS",
    6: "INCIPIT LIBER SEXTUS",
    7: " INCIPIT LIBER SEPTIMUS IOSEPPI IUDAICAE ANTIQUITATIS",
    8: " INCIPIT LIBER VIII IOSEPPI HISTORIARUM IUDAEICAE ANTIQUITATIS; CONTINET HIC LIBER TEMPUS ANNORUM CLX III",
    9: "Incipit liber nonus iosepphi historiarum iudaeicae antiquitatis continet hic liber tempus annorum CL et mensium VI",
}
BOOK_X_HEADINGS = [
    "INCIPIT LIBER DECIMUS IOSEPHI HISTORIARUM IUDAEICAE ANTIQUI TATIS.",
    "CONTINET HIC LIBER TEMPUS ANNORUM CLXXXII. MENSIUM VI DIERUM DECEM.",
]
TRAILERS = {
    1: "[FLAVII IOSEPPI ANTIQUITATIS IUDAICAE]EXPLICIT LIBER PRIMUS",
    2: "EXPLICIT FLAUII IOSEPPI IUDAICAE ANTIQUITATIS LIBER SECUNDUS",
    3: "FLAVII IOSEPPI IUDAICAE ANTIQUITATIS. EXPLICIT LIBER TERTIUS.",
    4: "FLAUII IOSEPPI IUDAICAE ANTIQUITATIS EXPLICIT LIBER QUARTUS",
    5: "EXPLICIT LIBER QUINTUS",
    6: "EXPLICIT LIBER SEXTUS",
    7: "FLAUII IOSEPPHI HISTORIAE ANTIQUITATIS LIBER SEPTIMUS EXPLICIT",
    8: "EXPLICIT LIBER OCTAUUS",
    10: "EXPLICIT LIBER DECIMUS",
}
NOTE_SOURCES = {"#BernBBMs50", "#LeidenUBVLF17", "#MonzaBCMsb20", "#BernBBMs118", "#RomeBAVPalLat814"}

# Exact accepted in-text annotations are excluded, never interpreted as Latin.
BOOK_X_NOTES = [('latin-book10-num15', {}, 'chapter 2 starts here'),
 ('latin-book10-num30', {'type': 'uncertainty'}, 'geniss'),
 ('latin-book10-num30', {'type': 'uncertainty'}, 'dimisit'),
 ('latin-book10-num30', {'type': 'uncertainty'}, 'berosus'),
 ('latin-book10-num40', {'type': 'uncertainty'}, 'quiescam'),
 ('latin-book10-num40', {'type': 'uncertainty'}, 'cogitauita or cogitaui uita'),
 ('latin-book10-num68', {}, 'chapter 6 starts here'),
 ('latin-book10-num81', {}, 'chapter 7 starts here'),
 ('latin-book10-num135', {'type': 'certainty'}, 'percuti'),
 ('latin-book10-num154', {'type': 'uncertainty'}, 'regaliter'),
 ('latin-book10-num155', {'type': 'uncertainty'}, 'suasit'),
 ('latin-book10-num168', {'type': 'uncertainty'}, 'erepti'),
 ('latin-book10-num219', {}, 'chapter 13 starts here'),
 ('latin-book10-num219', {'type': 'uncertainty'}, 'indicis'),
 ('latin-book10-num229', {'type': 'certainty'}, 'baldasar'),
 ('latin-book10-num263', {'type': 'uncertainty'}, 'habuit'),
 ('latin-book10-num263', {'type': 'certainty'}, 'fauo'),
 ('latin-book10-num263', {'type': 'uncertainty'}, 'predatus'),
 ('latin-book10-num263', {'type': 'uncertainty'}, 'relinquit')]
INLINE_TAGS = {"pb", "milestone", "add", "del", "s", "ref", "anchor", "gap", "note", "num", "cb", "corr", "unclear", "expan"}
# Retain dotted source notation verbatim. A single dotted lacuna in <.> is also
# present; ordinary periods and literal letter supplements in <...> are not gaps.
BRACKETED_EXPRESSION = re.compile(r"<[^<>\[\]]*>|\[[^<>\[\]]*\]")


def literal_dot_gaps(text: str) -> list[tuple[int, int]]:
    result = []
    for expression in BRACKETED_EXPRESSION.finditer(text):
        for dots in re.finditer(r"\.+", expression.group()):
            if len(dots.group()) > 1 or expression.group() == "<.>":
                result.append((expression.start() + dots.start(), expression.start() + dots.end()))
    return result


class ExtractionError(ValueError):
    """The source is outside the reviewed Antiquities I–X contract."""


def section_sequence(book: int, limits: list[int]) -> list[int]:
    return [n for n in range(limits[0], limits[1] + 1) if n not in MISSING_SECTIONS.get(book, [])]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ExtractionError(message)


def q(name: str) -> str:
    return f"{{{TEI}}}{name}"


def sha(value: bytes | str) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def words(text: str) -> list[str]:
    """Search's Unicode L/N start and L/M/N continuation word definition."""
    result, start = [], None
    for index, character in enumerate(text):
        category = unicodedata.category(character)[0]
        if start is None:
            if category in "LN":
                start = index
        elif category not in "LMN":
            result.append(text[start:index])
            start = None
    if start is not None:
        result.append(text[start:])
    return result


def container(element: ET.Element, allowed: set[str]) -> None:
    require(not (element.text or "").strip(), f"Substantive text outside paragraphs in {element.tag}")
    for child in element:
        require(child.tag in {q(name) for name in allowed}, f"Unexpected structural tag {child.tag}")
        require(not (child.tail or "").strip(), f"Substantive text outside paragraphs after {child.tag}")


def empty(element: ET.Element, name: str) -> None:
    require(not len(element) and not (element.text or ""), f"{name} marker contains text")


def source_info(xml_bytes: bytes, path: str) -> dict:
    return {"path": path, "sha256": sha(xml_bytes), "bytes": len(xml_bytes)}


def flatten_paragraph(paragraph: ET.Element, *, book: int, preface: bool) -> dict:
    """Retain both original paragraph coordinates and the running-text stream."""
    source_id = paragraph.get(XML_ID, "")
    prefix = "latin-preface" if preface else f"latin-book{book:02}"
    require(set(paragraph.attrib) == {XML_ID}
            and (re.fullmatch(rf"{prefix}-num[1-9]\d*[a-z]?", source_id) is not None
                 or book == 7 and source_id == "latin-book07-num"),
            f"Unexpected paragraph identity {source_id!r}")
    raw_text, flattened = "", ""
    pieces, boundaries, marks, markers, omitted = [], [], [], [], []
    counts = Counter()
    label = None
    ended = False

    def emit(text: str, *, kind: str = "source-text", element: ET.Element | None = None) -> None:
        nonlocal raw_text, flattened
        if not text:
            return
        raw_start, flat_start = len(raw_text), len(flattened)
        raw_text += text
        piece = {"kind": kind, "sourceTextStart": raw_start, "sourceTextEnd": len(raw_text)}
        if kind == "source-text":
            require(not ended or not text.strip(), f"{source_id}: running text after the Proem's Niese end marker")
            flattened += text
            piece.update({"flatStart": flat_start, "flatEnd": len(flattened)})
        else:
            piece["text"] = text
            if element is not None:
                piece["sourceTag"] = element.tag.removeprefix(q(""))
                piece["sourceAttributes"] = dict(element.attrib)
        pieces.append(piece)

    def walk(element: ET.Element, parent: str = "p") -> None:
        nonlocal label, ended
        tag = element.tag.removeprefix(q("")) if isinstance(element.tag, str) else "non-element"
        require(element.tag in {q(name) for name in INLINE_TAGS}
                and (book in (9, 10) or tag not in {"corr", "unclear", "expan", "cb"}),
                f"{source_id}: unexpected running-text markup {element.tag}")
        counts[tag] += 1
        start = len(flattened)
        marker = {"kind": tag, "sourceTextOffset": len(raw_text), "flatOffset": start,
                  "sourceAttributes": dict(element.attrib)}
        if book >= 6 and boundaries:
            marker["_activeSection"] = boundaries[-1]["section"]
        if tag == "num":
            require(parent == "p" and label is None and not flattened.strip() and not boundaries,
                    f"{source_id}: citation label must precede running text")
            require(not len(element) and not element.attrib, f"{source_id}: unexpected num markup")
            label = element.text or ""
            pattern = r"\[([ivxlcdm]+)\.([1-9]\d*)\]" if preface else r"\[(?:([IVXLCDM]+)\.)?([ivxlcdm]+)(?:\.([1-9]\d*))?\]"
            match = re.fullmatch(pattern, label)
            require(match is not None, f"{source_id}: unreviewed citation label {label!r}")
            niese = match.group(2 if preface else 3)
            if niese is not None and source_id not in CONTINUATIONS and source_id not in MILESTONE_STARTS:
                boundaries.append({"section": int(niese), "flatOffset": start, "startKind": "num",
                                   "sourceTextOffset": len(raw_text), "sourceLabel": label})
            emit(label, kind="excluded-label", element=element)
            return
        if tag == "note":
            accepted = ((source_id, dict(element.attrib), element.text or "") in BOOK_X_NOTES if book == 10 else
                        parent == "p" and label is None and element.get("source") in NOTE_SOURCES
                        and set(element.attrib) <= {"source", "type"}
                        and element.get("type") in (None, "certainty", "uncertainty"))
            require(not len(element) and accepted,
                    f"{source_id}: unreviewed running-text note")
            emit(element.text or "", kind="excluded-note", element=element)
            return
        if tag == "pb":
            empty(element, "Page")
            require(set(element.attrib) == {"n"} and re.fullmatch(r"[1-9]\d*[rv]", element.get("n", "")),
                    f"{source_id}: unreviewed page marker")
            markers.append(marker)
            return
        if tag == "cb":
            empty(element, "Column")
            require(book in (9, 10) and element.attrib in ({"n": "1/2"}, {"n": "2/2"}),
                    f"{source_id}: unreviewed column marker")
            markers.append(marker)
            return
        if tag == "milestone":
            empty(element, "Niese")
            if book in (9, 10) and set(element.attrib) == {"n"}:
                require(re.fullmatch(r"sbb00000114_\d{5}\.jpg", element.get("n", "")) is not None,
                        f"{source_id}: unreviewed source image marker")
                counts["imageMilestones"] += 1
                marker["kind"] = "image-milestone"
                markers.append(marker)
                return
            if element.get("unit") == "niese-end":
                require(preface and element.attrib == {"unit": "niese-end", XML_ID: "niese-latin-preface-end26"}
                        and not ended, f"{source_id}: unreviewed Niese end marker")
                ended = True
                marker["kind"] = "niese-end"
                markers.append(marker)
                counts["niese-end"] += 1
                return
            number = element.get("n", "")
            expected = {"unit": "niese", "n": number}
            if preface:
                expected[XML_ID] = f"niese-latin-preface-{number}"
            require(element.attrib == expected and re.fullmatch(r"[1-9]\d*", number) is not None,
                    f"{source_id}: unreviewed Niese milestone")
            require(label is not None and not ended, f"{source_id}: Niese milestone outside running text")
            boundaries.append({"section": int(number), "flatOffset": start, "startKind": "milestone",
                               "sourceTextOffset": len(raw_text), "sourceAttributes": dict(element.attrib)})
            return
        if tag == "anchor":
            empty(element, "Bamberg")
            number = re.fullmatch(r"b78-latin-B78-table1-row(\d{3})", element.get(XML_ID, ""))
            require(number is not None and element.attrib == {
                XML_ID: f"b78-latin-B78-table1-row{number.group(1)}", "type": "bamberg-boundary",
                "corresp": f"../structure.xml#B78-table1-row{number.group(1)}"},
                f"{source_id}: unreviewed Bamberg anchor")
            markers.append(marker)
            return
        if tag == "gap":
            empty(element, "Gap")
            require(element.attrib == {"reason": "omitted"}, f"{source_id}: unreviewed gap attributes")
            omitted.append(marker)
            markers.append(marker)
            return
        if tag == "add":
            allowed = [{}, {"hand": "post", "place": "interlinear"}]
            if book == 9:
                allowed += [{"hand": "?", "place": "interlinear"}, *({"hand": "post", "place": place}
                            for place in ("letter", "underscore", "margin right"))]
            if book == 10:
                allowed += [{"hand": "orig", "place": "marginright"}, *({"hand": "post", "place": place}
                            for place in ("margintop", "topmargin", "striketrough"))]
            require(element.attrib in allowed,
                    f"{source_id}: unreviewed addition attributes")
        elif tag == "del":
            allowed = [{}, {"hand": "orig", "rend": "strikethrough"}]
            if book == 9:
                allowed += [{"hand": "post", "rend": "strikethrough"}, {"hand": "?"},
                            {"hand": "?", "rend": "strikethrough"}, {"hand": "post", "rend": "scraping"}]
            if book == 10:
                allowed += [{"hand": "?", "rend": "scraping"}, {"hand": "?", "rend": "strikethrough"}]
            require(element.attrib in allowed,
                    f"{source_id}: unreviewed deletion attributes")
        elif tag in ("corr", "expan"):
            require(book in (9, 10) and not element.attrib, f"{source_id}: unreviewed {tag} markup")
        elif tag == "unclear":
            allowed = [{"reason": "faded"}] if book == 9 else [{}, *({"reason": reason}
                       for reason in ("fading", "uncertainty", "damage"))] if book == 10 else []
            require(element.attrib in allowed, f"{source_id}: unreviewed unclear attributes")
        elif tag == "s":
            require(not element.attrib, f"{source_id}: unreviewed sentence attributes")
        elif tag == "ref":
            require(set(element.attrib) == {"target"}
                    and re.fullmatch(r"note_[a-f0-9]{32}(?: note_[a-f0-9]{32})*", element.get("target", "")),
                    f"{source_id}: unreviewed reference attributes")
        emit(element.text or "")
        for child in element:
            require(child.tag != q("num") and (child.tag != q("note") or book == 10),
                    f"{source_id}: citation or note nested inside running markup")
            walk(child, tag)
            emit(child.tail or "")
        require(len(flattened) > start, f"{source_id}: empty substantive {tag} span")
        marks.append({"kind": tag, "flatStart": start, "flatEnd": len(flattened),
                      "sourceAttributes": dict(element.attrib)})

    emit(paragraph.text or "")
    for child in paragraph:
        walk(child)
        if child.tag == q("num") and source_id in OMISSION_NOTICE_IDS:
            require(book == 7 and child.tail == " Omitted in Bamberg MS",
                    f"{source_id}: unreviewed omission notice")
            emit(child.tail, kind="excluded-omission-notice")
            pieces[-1].update({"sourceTag": "#text", "sourceAttributes": {}})
            counts["omissionNotices"] += 1
        else:
            emit(child.tail or "")
    require(label is not None and counts["num"] == 1, f"{source_id}: missing citation num label")
    if source_id == "latin-book07-num":
        require(label == "[I.i.1]", "Unreviewed first Book VII paragraph citation")
    require(raw_text == "".join(paragraph.itertext()), f"{source_id}: parsing changed original paragraph characters")
    return {"sourceId": source_id, "rawText": raw_text, "flatText": flattened, "pieces": pieces,
            "boundaries": boundaries, "inlineMarks": marks, "structuralMarkers": markers,
            "omitted": omitted, "counts": counts, "label": label}


def extract_document(xml_bytes: bytes, *, book_number: int = 1, preface: bool = False,
                     order_offset: int | None = None, expected_range: list[int] | None = None,
                     expected_counts: dict | None = None, source_name: str | None = None) -> tuple[list[dict], dict]:
    require(book_number in BOOK_SPECS and (not preface or book_number == 1),
            "This extraction tranche accepts Antiquities I–X and their separate Proem only")
    spec = PREFACE_SPEC if preface else BOOK_SPECS[book_number]
    expected_range = spec["range"] if expected_range is None else expected_range
    if order_offset is None:
        order_offset = (0 if preface else 26) + sum(len(section_sequence(b, BOOK_SPECS[b]["range"]))
                                                   for b in range(1, book_number))
    require(isinstance(order_offset, int) and order_offset >= 0, "Global order offset must be a nonnegative integer")
    key = "preface" if preface else f"book-{book_number:02}"
    source_name = source_name or f"assets/xml/antiquities/Latin/{key}.xml"
    require(b"<!DOCTYPE" not in xml_bytes.upper() and b"<!ENTITY" not in xml_bytes.upper(),
            "DTD/entity declarations are outside the accepted source format")
    try:
        root = ET.fromstring(xml_bytes, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True)))
    except ET.ParseError as error:
        raise ExtractionError(f"XML is not well formed: {error}") from error
    require(root.tag == q("TEI") and not root.attrib, "Expected a plain TEI root")
    container(root, {"teiHeader", "text", "standOff"})
    require(len(root.findall(q("teiHeader"))) == 1 and len(root.findall(q("text"))) == 1
            and len(root.findall(q("standOff"))) <= 1, "Expected one header, one text and at most one standOff")
    text_node = root.find(q("text"))
    require(text_node.attrib == {XML_ID: f"{key}-text"}, "TEI text identity differs")
    container(text_node, {"body"})
    require(len(text_node) == 1 and not text_node[0].attrib, "Expected one plain TEI body")
    body = text_node[0]
    container(body, {"note", "div1"})
    require([e.tag for e in body] == [q("note"), q("div1")], "Source notice must precede one Latin book division")
    notice, book_node = body
    require(not len(notice) and not notice.attrib and notice.text == EDITION,
            "Unrecognised source notice; possible running text would be lost")
    source_prefix = "latin-preface" if preface else f"latin-book{book_number:02}"
    require(book_node.attrib == {"n": "Praefatio" if preface else "VIIII" if book_number == 9 else ROMANS[book_number], "subtype": "Latin",
                                 "type": "preface" if preface else "book", XML_ID: source_prefix},
            "Book identity differs")
    excluded = []
    for element in root:
        if element.tag == q("text"):
            continue
        content = "".join(element.itertext())
        excluded.append({"kind": element.tag.removeprefix(q("")), "reason": "outside running text",
                         "sourceAttributes": dict(element.attrib), "textCharacters": len(content), "textSha256": sha(content)})
    excluded.append({"kind": "source-notice", "text": notice.text, "textSha256": sha(notice.text)})
    paragraph_nodes, chapters = [], []
    excluded_structural_counts = Counter()
    if preface:
        container(book_node, {"p"})
        for p in book_node:
            if p.get(XML_ID):
                paragraph_nodes.append((p, None))
            else:
                content = "".join(p.itertext())
                require(not p.attrib and content in ("[Proemium]", "EXPLICITPRAEFATIOIOSEPPI;")
                        and all(child.tag == q("lb") and not child.attrib and not len(child)
                                and not (child.text or "") for child in p), "Unreviewed Proem heading or trailer")
                excluded.append({"kind": "proem-heading" if content == "[Proemium]" else "proem-trailer",
                                 "text": content, "textSha256": sha(content)})
    else:
        container(book_node, {"div2", "trailer"})
        for chapter in book_node:
            if chapter.tag == q("trailer"):
                content = "".join(chapter.itertext())
                attrs = {XML_ID: f"latin-{book_number}-trailer"} if book_number in (1, 3, 4) else {}
                require(not len(chapter) and chapter.attrib == attrs and content == TRAILERS[book_number],
                        "Unreviewed book trailer")
                excluded.append({"kind": "book-trailer", "text": content, "textSha256": sha(content)})
                continue
            number = chapter.get("n", "")
            chapter_attributes = {"n": number, "type": "chapter"}
            if book_number < 9 or number in ("0", "1"):
                chapter_attributes[XML_ID] = f"latin-book{book_number:02}-chapter{number}"
            require(re.fullmatch(r"0|[1-9]\d*", number) is not None and chapter.attrib == chapter_attributes,
                "Unreviewed chapter identity")
            next_chapter = [0, 1, 3, 4, 5, 8, 9, 10, 11, 12, 14][len(chapters)] if book_number == 10 and len(chapters) < 11 else None
            require(int(number) not in chapters and (int(number) == next_chapter if book_number == 10
                    else not chapters or int(number) == chapters[-1] + 1),
                    "Duplicate, missing or reordered chapter")
            chapters.append(int(number))
            container(chapter, {"head"} if book_number == 10 and number == "0" else {"p"})
            for p in chapter:
                if book_number == 9 and p.get(XML_ID) == "latin-book09-num51":
                    require(not len(p) and p.attrib == {XML_ID: "latin-book09-num51"} and p.text == LACUNA_NOTICE,
                            "Unreviewed Book IX lacuna notice")
                    excluded.append({"kind": "lacuna-notice", "sourceId": p.get(XML_ID),
                                     "sourceAttributes": dict(p.attrib), "text": p.text, "textSha256": sha(p.text),
                                     "missingSections": MISSING_SECTIONS[9]})
                    continue
                if p.get(XML_ID):
                    require(number != "0", "Running paragraph unexpectedly appears in title division")
                    paragraph_nodes.append((p, int(number)))
                else:
                    content = "".join(p.itertext())
                    if book_number == 9 and number == "0" and content == "  ":
                        expected_markers = [("milestone", {"n": "sbb00000114_00215.jpg"}),
                                            ("pb", {"n": "106r"}), ("cb", {"n": "1/2"})]
                        require(not p.attrib and [(c.tag.removeprefix(q("")), c.attrib) for c in p] == expected_markers
                                and all(not len(c) and not (c.text or "") for c in p),
                                "Unreviewed Book IX opening image/page/column markers")
                        excluded_structural_counts.update({"pb": 1, "cb": 1, "imageMilestones": 1})
                        excluded.append({"kind": "book-opening-markers", "text": content, "textSha256": sha(content),
                                         "markers": [{"sourceTag": tag, "sourceAttributes": attrs} for tag, attrs in expected_markers]})
                        continue
                    title_allowed = content in BOOK_X_HEADINGS if book_number == 10 else content == HEADINGS[book_number]
                    require(number == "0" and not p.attrib and title_allowed,
                            "Unreviewed unnumbered paragraph; possible running text would be lost")
                    if book_number == 1:
                        require(len(p) == 1 and p[0].tag == q("ref") and p[0].attrib == {
                            "target": "note_e9dd3996b6b4421398bd6417cbf51300"} and len(p[0]) == 1
                            and p[0][0].tag == q("pb") and p[0][0].attrib == {"n": "2r"}
                            and not (p[0].text or "") and not (p[0][0].text or "") and not len(p[0][0]),
                            "Unreviewed Book I incipit markup")
                    elif book_number in (7, 8):
                        require(len(p) == 1 and p[0].tag == q("pb") and p[0].attrib == {"n": "77r" if book_number == 7 else "91r"}
                                and not len(p[0]) and not (p[0].text or ""), "Unreviewed book title page marker")
                        excluded_structural_counts["pb"] += 1
                    elif book_number == 10 and content == BOOK_X_HEADINGS[0]:
                        expected_markers = [("milestone", {"n": "sbb00000114_00231.jpg"}),
                                            ("pb", {"n": "114r"}), ("cb", {"n": "2/2"})]
                        require([(c.tag.removeprefix(q("")), c.attrib) for c in p] == expected_markers
                                and all(not len(c) and not (c.text or "") for c in p),
                                "Unreviewed Book X heading image/page/column markers")
                        excluded_structural_counts.update({"pb": 1, "cb": 1, "imageMilestones": 1})
                    else:
                        require(not len(p), "Unreviewed book title markup")
                    excluded.append({"kind": "book-title", "text": content, "textSha256": sha(content)})

    records, paragraphs, separators, raw_paragraphs, running_paragraphs = [], [], [], [], []
    counts = Counter()
    active = None
    seen_ids = set()
    for paragraph_node, chapter in paragraph_nodes:
        parsed = flatten_paragraph(paragraph_node, book=book_number, preface=preface)
        source_id, flat = parsed["sourceId"], parsed["flatText"]
        require(source_id not in seen_ids, f"Duplicate paragraph identity {source_id}")
        seen_ids.add(source_id)
        counts.update(parsed["counts"])
        starts = list(parsed["boundaries"])
        begins_section = bool(starts and starts[0]["startKind"] == "num")
        if source_id in MILESTONE_STARTS:
            require(starts and MILESTONE_STARTS[source_id] == (book_number, parsed["label"], starts[0]["section"])
                    and starts[0]["startKind"] == "milestone" and not flat[:starts[0]["flatOffset"]].strip(),
                    f"{source_id}: unreviewed milestone-established paragraph start")
            begins_section = True
            counts["milestoneParagraphStarts"] += 1
        if not begins_section:
            require(CONTINUATIONS.get(source_id) == (book_number, parsed["label"], active["section"] if active else None),
                    f"{source_id}: unreviewed continuation paragraph or displaced boundary")
            starts.insert(0, {"section": active["section"], "flatOffset": 0, "startKind": "continuation"})
            counts["continuations"] += 1
        else:
            counts["citationParagraphs"] += 1
        require(starts[0]["flatOffset"] == 0 or not flat[:starts[0]["flatOffset"]].strip(),
                f"{source_id}: running text precedes a citation start")
        starts[0]["flatOffset"] = 0
        fragments = []
        for index, start in enumerate(starts):
            number, first = start["section"], start["flatOffset"]
            last = starts[index + 1]["flatOffset"] if index + 1 < len(starts) else len(flat)
            require(first <= last, f"{source_id}: source Niese boundaries are out of order")
            if start["startKind"] != "continuation":
                expected_sequence = section_sequence(book_number, expected_range)
                expected_number = expected_sequence[len(records)] if len(records) < len(expected_sequence) else None
                require(number == expected_number, f"{source_id}: expected consecutive Niese {expected_number}, found {number}")
                label = f"{ROMANS[book_number]}.{number}"
                reader_book = "preface" if preface else book_number
                active = {"id": f"{COLLECTION}-{book_number}-{number}", "work": "antiquities", "book": book_number,
                          "section": number, "language": "Latin", "edition": EDITION, "citationScheme": "niese",
                          "citationLabel": label, "citation": {"book": ROMANS[book_number], "section": number},
                          "text": "", "editorialMarks": [], "sourceMarkup": [], "textGaps": [], "phraseBreaks": [],
                          "url": f"/antiquities/?book={reader_book}&niese={number}",
                          "readerLink": {"path": "antiquities/", "params": {"book": reader_book, "niese": number}},
                          "sourceId": source_id, "sourceIds": [source_id], "sourcePath": source_name,
                          "order": order_offset + len(records)}
                if preface:
                    active["sourceDivision"] = "proem"
                    active["division"] = "proem"
                    active["citation"]["proem"] = True
                elif book_number == 1 and number == 27:
                    active.update({"breakBefore": True, "breakReason": "Book I narrative begins after the separately transmitted Proem."})
                elif book_number == 9 and number == 110:
                    active.update({"breakBefore": True, "breakReason": "The accepted source marks a lacuna for Antiquities IX.51–109 before IX.110."})
                records.append(active)
            require(active is not None and active["section"] == number, "No active Niese record")
            raw_fragment = flat[first:last]
            text = raw_fragment.strip()
            if book_number == 10 and number == 108:
                label_piece = next(piece for piece in parsed["pieces"] if piece["kind"] == "excluded-label")
                next_boundary = starts[index + 1] if index + 1 < len(starts) else None
                require(source_id == "latin-book10-num108" and start["startKind"] == "num"
                        and parsed["label"] == "[VII.iii.108]" and label_piece["sourceTextStart"] == 0
                        and label_piece["sourceTextEnd"] == 13 and raw_fragment == " "
                        and next_boundary is not None and next_boundary["section"] == 109
                        and next_boundary["sourceAttributes"] == {"unit": "niese", "n": "109"}
                        and next_boundary["sourceTextOffset"] == 14,
                        "Unreviewed empty source interval at X.108")
                active["emptySource"] = {
                    "kind": "empty-source-interval", "sourcePath": source_name, "sourceId": source_id,
                    "label": {"sourceTag": "num", "sourceAttributes": {}, "text": parsed["label"],
                              "sourceTextStart": label_piece["sourceTextStart"], "sourceTextEnd": label_piece["sourceTextEnd"]},
                    "nextBoundary": {"sourceTag": "milestone", "sourceAttributes": next_boundary["sourceAttributes"],
                                     "sourceTextOffset": next_boundary["sourceTextOffset"]},
                    "interveningText": raw_fragment,
                }
                active.update({"breakBefore": True, "breakReason": "No Latin text occurs between the citation label for X.108 and the next Niese marker."})
            left = len(raw_fragment) - len(raw_fragment.lstrip()) if text else len(raw_fragment)
            right = len(raw_fragment.rstrip()) if text else left
            text_first, text_last = first + left, first + right
            separator = PARAGRAPH_SEPARATOR if text and active["text"] else ""
            if separator:
                separators.append({"sourcePath": source_name, "sourceId": source_id, "section": number,
                                   "recordTextStart": len(active["text"]), "recordTextEnd": len(active["text"]) + len(separator),
                                   "separator": separator})
                active["text"] += separator
            record_start = len(active["text"])
            active["text"] += text
            if source_id not in active["sourceIds"]:
                active["sourceIds"].append(source_id)
            fragment = {"section": number, "startKind": start["startKind"], "flatStart": first, "flatEnd": last,
                        "textStart": text_first, "textEnd": text_last, "recordTextStart": record_start,
                        "recordTextEnd": len(active["text"]), "separatorBefore": separator,
                        "leadingWhitespace": raw_fragment[:left], "trailingWhitespace": raw_fragment[right:],
                        "rawFragmentSha256": sha(raw_fragment), "textSha256": sha(text)}
            fragments.append(fragment)
            for mark in parsed["inlineMarks"]:
                a, b = max(text_first, mark["flatStart"]), min(text_last, mark["flatEnd"])
                if a >= b:
                    continue
                aa, bb = record_start + a - text_first, record_start + b - text_first
                published = {"kind": mark["kind"], "start": utf16_length(active["text"][:aa]),
                             "end": utf16_length(active["text"][:bb]), "text": active["text"][aa:bb],
                             "sourceTag": mark["kind"], "sourceAttributes": mark["sourceAttributes"]}
                active["editorialMarks" if mark["kind"] in ("add", "del", "unclear") else "sourceMarkup"].append(published)
        require([word for f in fragments for word in words(flat[f["textStart"]:f["textEnd"]])] == words(flat),
                f"{source_id}: Niese boundary divides or changes an original word")
        by_section = {record["section"]: record for record in records}
        for marker in parsed["structuralMarkers"]:
            # Point markers at a new section's start belong to that new section.
            # Consecutive empty sections share a character offset, so retain the
            # original element order as well as its coordinate.
            marker_section = marker.pop("_activeSection", None)
            fragment = (next(f for f in fragments if f["section"] == marker_section) if marker_section is not None
                        else next(f for f in reversed(fragments) if f["flatStart"] <= marker["flatOffset"]))
            record = by_section[fragment["section"]]
            offset = fragment["recordTextStart"] + max(0, min(fragment["textEnd"], marker["flatOffset"]) - fragment["textStart"])
            marker.update({"section": record["section"], "recordTextOffset": offset,
                           "recordTextOffsetUTF16": utf16_length(record["text"][:offset])})
            if marker["kind"] == "gap":
                require(record["section"] in EMPTY_SECTIONS.get(book_number, []) and not record["text"],
                        "The reviewed explicit omissions are III.240 and VII.69–99")
                record["textGaps"].append({"kind": "tei-gap", "start": 0, "end": 0, "text": "",
                                           "sourceAttributes": marker["sourceAttributes"]})
                record.update({"phraseBreaks": [0], "breakBefore": True,
                               "breakReason": f"The accepted source explicitly omits the Latin text at Antiquities {ROMANS[book_number]}.{record['section']}."})
        segments = []
        for piece in parsed["pieces"]:
            if piece["kind"] != "source-text":
                segments.append(piece)
                continue
            for fragment in fragments:
                for kind, first, last in (("trimmed-edge-whitespace", fragment["flatStart"], fragment["textStart"]),
                                          ("source-text", fragment["textStart"], fragment["textEnd"]),
                                          ("trimmed-edge-whitespace", fragment["textEnd"], fragment["flatEnd"])):
                    a, b = max(first, piece["flatStart"]), min(last, piece["flatEnd"])
                    if a >= b:
                        continue
                    raw_start = piece["sourceTextStart"] + a - piece["flatStart"]
                    segment = {"kind": kind, "sourceTextStart": raw_start, "sourceTextEnd": raw_start + b - a}
                    if kind == "source-text":
                        start = fragment["recordTextStart"] + a - fragment["textStart"]
                        segment.update({"section": fragment["section"], "recordTextStart": start,
                                        "recordTextEnd": start + b - a, "textSha256": sha(flat[a:b])})
                    else:
                        segment["text"] = flat[a:b]
                    segments.append(segment)
        segments.sort(key=lambda s: (s["sourceTextStart"], s["sourceTextEnd"]))
        cursor, restored = 0, ""
        for segment in segments:
            require(segment["sourceTextStart"] == cursor, f"{source_id}: paragraph projection has a gap or overlap")
            part = by_section[segment["section"]]["text"][segment["recordTextStart"]:segment["recordTextEnd"]] if segment["kind"] == "source-text" else segment["text"]
            restored += part
            cursor = segment["sourceTextEnd"]
        require(restored == parsed["rawText"], f"{source_id}: exact paragraph restoration failed")
        paragraphs.append({"sourcePath": source_name, "sourceId": source_id, "sourceAttributes": dict(paragraph_node.attrib),
                           "chapterDivision": chapter, "sourceLabel": parsed["label"],
                           "establishesNieseStart": begins_section, "rawTextCharacters": len(parsed["rawText"]),
                           "rawTextSha256": sha(parsed["rawText"]), "runningTextSha256": sha(flat),
                           "segments": segments, "sections": fragments, "inlineMarks": parsed["inlineMarks"],
                           "structuralMarkers": parsed["structuralMarkers"],
                           "exactRestorationVerified": True, "wordSequenceVerified": True})
        raw_paragraphs.append(parsed["rawText"])
        running_paragraphs.append(flat)

    expected = section_sequence(book_number, expected_range)
    require([record["section"] for record in records] == expected, "Niese citation coverage differs from the reviewed range")
    for record in records:
        for first, last in literal_dot_gaps(record["text"]):
            record["textGaps"].append({"kind": "literal-dots", "start": utf16_length(record["text"][:first]),
                                       "end": utf16_length(record["text"][:last]), "text": record["text"][first:last]})
        if book_number >= 6:
            for match in re.finditer("…", record["text"]):
                record["textGaps"].append({"kind": "literal-ellipsis", "start": utf16_length(record["text"][:match.start()]),
                                           "end": utf16_length(record["text"][:match.end()]), "text": match.group()})
            for mark in record["editorialMarks"]:
                if mark["kind"] == "del" and mark["sourceAttributes"] == {"hand": "?", "rend": "scraping"} and re.fullmatch(r"\.+", mark["text"]):
                    require((book_number, record["section"]) == (10, 154), "Unreviewed punctuation-only erased source span")
                    record["textGaps"].append({"kind": "source-marked-dots", "start": mark["start"], "end": mark["end"],
                                               "text": mark["text"], "sourceTag": "del", "sourceAttributes": mark["sourceAttributes"]})
        record["textGaps"].sort(key=lambda mark: (mark["start"], mark["end"]))
        record["phraseBreaks"] = sorted({mark["start"] for mark in record["textGaps"]})
        for key in ("editorialMarks", "sourceMarkup"):
            record[key].sort(key=lambda mark: (mark["start"], -mark["end"], mark["kind"]))
        if book_number == 3 and record["section"] == 241:
            record.update({"breakBefore": True, "breakReason": "The preceding Latin Niese section III.240 is explicitly omitted."})
        if book_number == 7 and record["section"] == 100:
            record.update({"breakBefore": True, "breakReason": "The preceding Latin Niese sections VII.69–99 are explicitly omitted."})
        if book_number == 10 and record["section"] == 109:
            record.update({"breakBefore": True, "breakReason": "The preceding citation interval X.108 contains no Latin text in the accepted source."})
        if not record["text"]:
            require((record["section"] in EMPTY_SECTIONS.get(book_number, []) and record["textGaps"] == [
                {"kind": "tei-gap", "start": 0, "end": 0, "text": "", "sourceAttributes": {"reason": "omitted"}}])
                or (record["section"] in EMPTY_SOURCE_SECTIONS.get(book_number, []) and record.get("emptySource")
                    and not record["textGaps"] and not record["phraseBreaks"]),
                "An unmarked empty Niese section would silently lose source text")
        else:
            require(bool(words(record["text"])), "A nonempty section contains no searchable words")
    by_section = {r["section"]: r for r in records}
    restored_paragraphs = []
    for audit, raw in zip(paragraphs, raw_paragraphs, strict=True):
        restored = "".join(by_section[s["section"]]["text"][s["recordTextStart"]:s["recordTextEnd"]]
                           if s["kind"] == "source-text" else s["text"] for s in audit["segments"])
        require(restored == raw, f"{audit['sourceId']}: finished corpus cannot restore source")
        restored_paragraphs.append(restored)
    source_words = [word for text in running_paragraphs for word in words(text)]
    indexed_words = [word for record in records for word in words(record["text"])]
    source_content = re.sub(r"\s", "", "".join(running_paragraphs))
    display_content = re.sub(r"\s", "", "".join(r["text"] for r in records))
    require(source_words == indexed_words, "Full original word-sequence coverage failed")
    require(source_content == display_content, "Original running characters or punctuation changed")
    literal_gaps = sum(g["kind"] != "tei-gap" for r in records for g in r["textGaps"])
    niese_milestones = counts["milestone"] - counts["niese-end"] - counts["imageMilestones"]
    page_breaks = counts["pb"] + int(not preface and book_number == 1) + excluded_structural_counts["pb"]
    if expected_counts is not None:
        observed = {"paragraphs": len(paragraphs), "milestones": niese_milestones,
                    "chapters": len(chapters), "literalGaps": literal_gaps, "continuations": counts["continuations"],
                    **{key: counts[key] for key in ("add", "del", "note", "ref", "s", "anchor", "gap", "corr", "unclear", "expan", "omissionNotices", "milestoneParagraphStarts")},
                    "pb": page_breaks, "cb": counts["cb"] + excluded_structural_counts["cb"],
                    "imageMilestones": counts["imageMilestones"] + excluded_structural_counts["imageMilestones"]}
        for key, expected_value in expected_counts.items():
            if key != "range":
                require(observed.get(key) == expected_value,
                        f"Unexpected {key} count: expected {expected_value}, found {observed.get(key)}")
        require(counts["niese-end"] == (1 if preface else 0), "Unexpected Niese end marker count")
        require(sum(e["kind"] in ("book-title", "proem-heading") for e in excluded) == (2 if book_number == 10 else 1)
                and sum(e["kind"] in ("book-trailer", "proem-trailer") for e in excluded) == (0 if book_number == 9 else 1),
                "Reviewed book heading or trailer coverage differs")
        if book_number == 9:
            require(sum(e["kind"] == "lacuna-notice" for e in excluded) == 1,
                    "The reviewed Book IX lacuna notice is missing")
    empty_sections = [r["section"] for r in records if not r["text"]]
    report = {
        "schemaVersion": 4, "status": "PASS",
        "scope": {"work": "Antiquities", "book": book_number, "sourceDivision": "proem" if preface else "narrative",
                  "language": "Latin", "edition": EDITION, "unit": "Niese section", "citationScheme": "niese"},
        "source": source_info(xml_bytes, source_name),
        "rules": {
            "sourceOrderPreserved": True,
            "sectionReferenceMeaning": "The final Arabic component of the accepted num citation label, supplemented by every recursively encountered milestone unit=niese. Stable paragraph IDs do not establish section boundaries; six reviewed continuation labels contain no Niese number.",
            "textTransformations": "Exclude verified citation labels, source annotations, incipits, explicits and external metadata. Trim each section-fragment edge. Represent a continuing physical paragraph boundary by two newlines. Preserve every other source character and all original words exactly.",
            "editorialMarkup": "Retain add and del letters as searchable visible text, with their original source tags and attributes in editorialMarks. Do not silently apply a corrected reading or insert editorial punctuation.",
            "transparentMarkup": "Preserve s and ref text; retain their distinct spans and attributes in sourceMarkup. The s wrapper encloses internal Niese milestones102 and103; traverse recursively.",
            "structuralMarkup": "pb and Bamberg anchor contribute no characters or spaces. Internal Niese markers establish citations; the Proem niese-end terminates26. Report each marker and its original coordinate.",
            "phraseBoundaries": "Proem and narrative are separate source divisions: I.27 has breakBefore. III.240 is an explicitly omitted empty Latin unit, with a zero-width gap and phraseBreaks[0]; III.241 also has breakBefore. Six literal dot clusters conservatively block phrase adjacency without changing their scholarly interpretation. Ordinary consecutive sections and continuing paragraph fragments remain joinable in whole-book scope.",
            "unknownContent": "Unknown substantive markup, attributes, headings, continuation labels or unmarked empty sections stop extraction for review.",
            "sourceProjectionDefinition": "Every non-whitespace indexed character is original running source text. Each raw parsed paragraph is exactly restored from finished record slices plus recorded labels, notes and trimmed whitespace. Generated paragraph separators are whitespace only.",
            "offsetDefinition": "Audit sourceText, flat and recordText offsets are zero-based Python Unicode-character offsets, end exclusive. Published editorialMarks, sourceMarkup, textGaps and phraseBreaks use JavaScript UTF-16 offsets.",
            "tokenCountDefinition": "Unicode L/N start and L/M/N continuation, original word strings without normalization or stemming.",
            "readerRoute": "/antiquities/?book=preface&niese={section}" if preface else f"/antiquities/?book={book_number}&niese={{section}}",
        },
        "counts": {"bodyParagraphs": len(list(body.iter(q("p")))) if book_number >= 6 else len(paragraphs) + (2 if preface else 1), "numberedParagraphs": len(paragraphs),
                   "citationParagraphs": counts["citationParagraphs"], "continuationParagraphs": counts["continuations"],
                   "sections": len(records), "nieseMilestones": niese_milestones,
                   "nieseEndMilestones": counts["niese-end"], "chapterDivisions": len(chapters),
                   "pageBreaks": page_breaks,
                   "addedSpans": counts["add"], "deletedSpans": counts["del"], "sentenceSpans": counts["s"],
                   "referenceSpans": counts["ref"], "bambergAnchors": counts["anchor"],
                   "excludedAnnotationNotes": counts["note"], "sourceGapMarkers": counts["gap"],
                   "literalGapClusters": literal_gaps, "emptySections": len(empty_sections),
                   "breakBeforeUnits": sum(bool(r.get("breakBefore")) for r in records),
                   "paragraphSeparatorsInserted": len(separators), "runningWordTokens": len(indexed_words)},
        "coverage": {"missingSections": MISSING_SECTIONS.get(book_number, []), "unexpectedSections": [], "duplicateSections": [],
                     "completeRange": expected_range, "globalOrderRange": [order_offset, order_offset + len(records) - 1],
                     "sourceOrderIsConsecutive": not MISSING_SECTIONS.get(book_number), "paragraphsExactlyRestored": len(paragraphs),
                     "rawParagraphSequenceSha256": sha("\n".join(raw_paragraphs)),
                     "restoredParagraphSequenceSha256": sha("\n".join(restored_paragraphs)),
                     "sourceWordSequenceSha256": sha("\n".join(source_words)),
                     "indexedWordSequenceSha256": sha("\n".join(indexed_words)),
                     "sourceNonWhitespaceContentSha256": sha(source_content),
                     "indexedNonWhitespaceContentSha256": sha(display_content),
                     "sourceProjectionNonWhitespaceContentSha256": sha(display_content),
                     "displayNonWhitespaceContentSha256": sha(display_content),
                     "displayTextSequenceSha256": sha("\n".join(r["text"] for r in records)),
                     "sourceProjectionExactlyRestoresSource": True, "wordSequencePreserved": True,
                     "nonWhitespaceContentPreserved": True, "generatedDisplayGlyphs": 0,
                     "allSectionTextsNonempty": not empty_sections, "allowedEmptySections": empty_sections},
        "excluded": excluded, "paragraphs": paragraphs, "paragraphSeparators": separators,
        "sectionAudits": [{"recordId": r["id"], "section": r["section"], "sourcePath": source_name,
                           "sourceIds": r["sourceIds"], "displayTextSha256": sha(r["text"]),
                           "editorialMarks": r["editorialMarks"], "sourceMarkup": r["sourceMarkup"],
                           "textGaps": r["textGaps"], "phraseBreaks": r["phraseBreaks"],
                           "breakBefore": bool(r.get("breakBefore"))} for r in records],
    }
    if book_number >= 6:
        report["rules"].update({
            "sectionReferenceMeaning": "The accepted num citation label and explicit Niese milestones establish citations. Paragraph IDs are provenance only. VI has two chapter-only labels followed by section milestones; VIII has two continuing paragraphs; X's printed151 label is followed by explicit150. IX lacks51–109, which are declared missing without fabricated records.",
            "textTransformations": "Exclude verified citation labels, source annotations, the six English omission notices, the IX lacuna notice, incipits, explicits and external metadata. Trim section-fragment edges and represent continuing paragraph boundaries by two newlines. Preserve every other source character and original word exactly.",
            "editorialMarkup": "Retain add, del and unclear source content as searchable visible text with exact tags, attributes and clipped section spans in editorialMarks. Preserve accepted readings without silently correcting or completing them.",
            "transparentMarkup": "Preserve corr, expan, s and ref text with exact source tags and attributes in sourceMarkup. Traverse recursively, including the unclear wrapper across X.199–200 with its nested expansion.",
            "structuralMarkup": "Page, column and source-image markers contribute no characters or spaces. Only milestones with unit=niese establish citations. Preserve original marker attributes and paragraph coordinates.",
            "phraseBoundaries": "VII.69–99 retain explicit zero-width TEI gaps and VII.100 starts after them. IX.51–109 have no records and IX.110 starts after the declared lacuna. X.108 is an empty source-defined interval without a TEI gap; X.108 and109 have breakBefore. Source ASCII dot clusters, Unicode ellipses and the two scraped punctuation spans in X.154 block phrase adjacency. Uncertain sentence punctuation in X.65 and75 remains ordinarily joinable. Continuing paragraphs and other consecutive sections join in whole-book scope.",
            "unknownContent": "Unknown substantive markup, attributes, headings, notices, boundary exceptions or undeclared empty sections stop extraction for review.",
        })
        report["counts"].update({
            "columnBreaks": counts["cb"] + excluded_structural_counts["cb"],
            "imageMilestones": counts["imageMilestones"] + excluded_structural_counts["imageMilestones"],
            "correctedSpans": counts["corr"], "unclearSpans": counts["unclear"], "expandedSpans": counts["expan"],
            "milestoneParagraphStarts": counts["milestoneParagraphStarts"], "excludedOmissionNotices": counts["omissionNotices"],
            "excludedLacunaNotices": sum(e["kind"] == "lacuna-notice" for e in excluded),
            "literalDotClusters": sum(g["kind"] == "literal-dots" for r in records for g in r["textGaps"]),
            "literalEllipses": sum(g["kind"] == "literal-ellipsis" for r in records for g in r["textGaps"]),
            "sourceMarkedDotSpans": sum(g["kind"] == "source-marked-dots" for r in records for g in r["textGaps"]),
            "emptySourceIntervals": sum(bool(r.get("emptySource")) for r in records),
        })
        report["coverage"].update({"omittedSections": EMPTY_SECTIONS.get(book_number, []),
                                   "emptySourceIntervals": EMPTY_SOURCE_SECTIONS.get(book_number, [])})
        for record, audit in zip(records, report["sectionAudits"], strict=True):
            if "emptySource" in record:
                audit["emptySource"] = record["emptySource"]
    return records, report


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(value)
    temporary.replace(path)


def build_corpus(source_root: Path, output_dir: Path) -> dict:
    """Validate all eleven source documents before replacing any tranche output."""
    artifacts, combined, books = {}, [], []
    totals = Counter()
    for number, spec in BOOK_SPECS.items():
        book_records, document_reports = [], []
        if number == 1:
            path = "assets/xml/antiquities/Latin/preface.xml"
            records, report = extract_document((source_root / path).read_bytes(), book_number=1, preface=True,
                                              order_offset=len(combined), expected_counts=PREFACE_SPEC, source_name=path)
            book_records.extend(records)
            document_reports.append(report)
        path = f"assets/xml/antiquities/Latin/book-{number:02}.xml"
        records, report = extract_document((source_root / path).read_bytes(), book_number=number,
                                          order_offset=len(combined) + len(book_records), expected_counts=spec, source_name=path)
        book_records.extend(records)
        document_reports.append(report)
        sources = [r["source"] for r in document_reports]
        book_counts = Counter()
        for r in document_reports:
            book_counts.update(r["counts"])
        empty_sections = [r["section"] for r in book_records if not r["text"]]
        book_report = {
            "schemaVersion": 4, "status": "PASS",
            "scope": {"work": "Antiquities", "book": number, "language": "Latin", "edition": EDITION,
                      "unit": "Niese section", "citationScheme": "niese", "includesProem": number == 1},
            "source": sources[-1], "additionalSources": sources[:-1], "sources": sources,
            "rules": report["rules"], "counts": dict(book_counts),
            "coverage": {"completeRange": [1, spec["range"][1]], "missingSections": MISSING_SECTIONS.get(number, []), "unexpectedSections": [],
                         "duplicateSections": [], "globalOrderRange": [book_records[0]["order"], book_records[-1]["order"]],
                         "sourceOrderIsConsecutive": not MISSING_SECTIONS.get(number), "paragraphsExactlyRestored": sum(r["coverage"]["paragraphsExactlyRestored"] for r in document_reports),
                         "sourceProjectionExactlyRestoresSource": True, "wordSequencePreserved": True,
                         "nonWhitespaceContentPreserved": True, "generatedDisplayGlyphs": 0,
                         "allSectionTextsNonempty": not empty_sections, "allowedEmptySections": empty_sections},
            "documentReports": [{key: r[key] for key in ("source", "scope", "counts", "coverage", "excluded")} for r in document_reports],
            "paragraphs": [p for r in document_reports for p in r["paragraphs"]],
            "paragraphSeparators": [p for r in document_reports for p in r["paragraphSeparators"]],
            "sectionAudits": [p for r in document_reports for p in r["sectionAudits"]],
        }
        if number >= 6:
            book_report["coverage"].update({"omittedSections": EMPTY_SECTIONS.get(number, []),
                                            "emptySourceIntervals": EMPTY_SOURCE_SECTIONS.get(number, [])})
        corpus_name, report_name = f"book-{number:02}.corpus.json", f"book-{number:02}.extraction-report.json"
        corpus_bytes, report_bytes = json_bytes(book_records), json_bytes(book_report)
        artifacts[corpus_name], artifacts[report_name] = corpus_bytes, report_bytes
        books.append({"book": number, "status": "PASS", "source": sources[-1], "additionalSources": sources[:-1], "sources": sources,
                      "counts": dict(book_counts), "orderStart": len(combined), "orderEnd": len(combined) + len(book_records) - 1,
                      "corpus": {"path": f"{OUTPUT_PREFIX}/{corpus_name}", "sha256": sha(corpus_bytes),
                                 "bytes": len(corpus_bytes), "records": len(book_records)},
                      "extractionReport": {"path": f"{OUTPUT_PREFIX}/{report_name}", "sha256": sha(report_bytes), "bytes": len(report_bytes)}})
        combined.extend(book_records)
        totals.update(book_counts)
    require(len(combined) == 3415 and len({r["id"] for r in combined}) == 3415, "Combined Antiquities I–X coverage differs")
    require([r["order"] for r in combined] == list(range(3415)), "Combined source order is not continuous")
    combined_bytes = json_bytes(combined)
    artifacts["corpus.json"] = combined_bytes
    # Older reviewed per-book reports predate the explicit gap-kind breakdown;
    # preserve those bytes and compute the cumulative breakdown from all rows.
    totals["literalDotClusters"] = sum(g["kind"] == "literal-dots" for r in combined for g in r["textGaps"])
    report = {
        "schemaVersion": 4, "status": "PASS",
        "scope": {"work": "Antiquities", "books": list(BOOK_SPECS), "language": "Latin", "edition": EDITION,
                  "unit": "Niese section", "citationScheme": "niese", "includesProem": True},
        "counts": {"books": len(books), "sourceDocuments": 11, **dict(totals)},
        "coverage": {"paragraphsExactlyRestored": totals["numberedParagraphs"], "wordSequencePreserved": True,
                     "nonWhitespaceContentPreserved": True, "sourceProjectionExactlyRestoresSource": True,
                     "generatedDisplayGlyphs": 0, "globalIdsUnique": True, "globalOrderIsConsecutive": True,
                     "globalOrderRange": [0, 3414], "completeSectionCoverageByBook": {str(b): [1, spec["range"][1]] for b, spec in BOOK_SPECS.items()},
                     "missingSectionsByBook": {str(b): values for b, values in MISSING_SECTIONS.items()},
                     "allSectionTextsNonempty": False, "allowedEmptySections": [{"book": r["book"], "section": r["section"]} for r in combined if not r["text"]],
                     "sourceProjectionDefinition": "Running text from the accepted eleven XML documents is preserved exactly, except reversible edge whitespace and inserted paragraph-boundary newlines. No running source words or punctuation are generated, removed or corrected. The exact English omission notices and IX lacuna notice are excluded as annotated source evidence."},
        "corpus": {"path": f"{OUTPUT_PREFIX}/corpus.json", "sha256": sha(combined_bytes), "bytes": len(combined_bytes), "records": len(combined)},
        "books": books,
    }
    artifacts["extraction-report.json"] = json_bytes(report)
    for name, data in artifacts.items():
        write_bytes(output_dir / name, data)
    return report


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=directory.parent.parent)
    parser.add_argument("--output-dir", type=Path, default=directory / OUTPUT_PREFIX)
    args = parser.parse_args()
    report = build_corpus(args.source_root, args.output_dir)
    print(json.dumps({"status": report["status"], "corpusSha256": report["corpus"]["sha256"], "counts": report["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
