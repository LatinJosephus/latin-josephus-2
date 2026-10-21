#!/usr/bin/env python3
"""Extract the accepted Whiston Antiquities Proem and Books I–XX for search.

Explicit English Niese milestones govern the projection.  XML files and their
accepted boundaries are read only. Book XI retains its accepted physical
section order; no citation sorting or textual repair is performed.
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
COLLECTION = "antiquities-english-whiston"
EDITION = "Whiston"
OUTPUT_PREFIX = f"data/{COLLECTION}"
SOURCE_PREFIX = "assets/xml/antiquities/English"
SOURCE_CONTRACTS = {
    "preface": {"sha256": "d04712a2db72f2d2c39e175591b866308f93cb15d10f4ee3be70401f7dd614eb", "range": [1, 26]},
    1: {"sha256": "9cd8daf04bddfd94cd96f077c0b9336135c35d017fad029a56fd08e1fc2363f3", "range": [27, 346]},
    2: {"sha256": "70da231aafb85aecfec0510bc7489441ca8263b45e31dd33f3ed2f20237aa584", "range": [1, 349]},
    3: {"sha256": "0c663f9776a1249d85ceab2ad0bfa47dc3b537864598f4855a668e23e642df44", "range": [1, 322]},
    4: {"sha256": "6d58dfa865b47e1a1f347f8f322f578381e6f8a407c597e2f36ae3bd120c6554", "range": [1, 331]},
    5: {"sha256": "a8ab9d6b66e6d4a768f3fc247240d6423d5d9687a3f1026f327f9ea387560722", "range": [1, 362]},
    6: {"sha256": "116338d9f8a424bfb2ec63af5531b3c72941708ae00e7f327ba8909dc1e125eb", "range": [1, 378]},
    7: {"sha256": "d8109c20ceca61283dd5150bf2059f3cffda924f5f82625a4e6b1073b4c60eb3", "range": [1, 394]},
    8: {"sha256": "609cedd3dbab1f7af831877f2aea820781e2b34b6c998ab41b3ffa6cb0fb8289", "range": [1, 420]},
    9: {"sha256": "d973618661bacf96f0a7ea81f1d7e44147f7826ff1d247908467b238263edc36", "range": [1, 291]},
    10: {"sha256": "7f4fde2921f8c5fc670d688174f5c67f81eed7c264c63af89b6c7adb0725e7eb", "range": [1, 281]},
    11: {"sha256": "0bdcc522c1f227dab7a61b19a4bef09a590af2bf25cbdce581277469c082acb2", "range": [1, 347]},
    12: {"sha256": "ba4808e3b5e234c2ec1bbffd3e4b662a78b2fe41c1643be3e4e7e6662d583286", "range": [1, 434]},
    13: {"sha256": "01ff55a3e01bd82c6590ef8bbfa30c05a22a8ebc292086b10095011b552f91a9", "range": [1, 433]},
    14: {"sha256": "9f5ffef649c2922e54402ca7ab09795307fe0595c68d47754df8aefe47464ed1", "range": [1, 491]},
    15: {"sha256": "223b08bd399b58dd6da5929a5cbffacb31f461ee11d4d6dd4aa45b498283d579", "range": [1, 425]},
    16: {"sha256": "df3138bdceadb36ad8295445b37e7aa741c48f1d145f97b9073d6d53976991f8", "range": [1, 404]},
    17: {"sha256": "d6056846f61ae43003989a2d799501d5e9edb7c3b407d9292b3c89064df6a0ac", "range": [1, 355]},
    18: {"sha256": "ba1529509dddf72ec82a5eda63fb95f6d0f8d88dad87c69f5cf7a431536c63fa", "range": [1, 379]},
    19: {"sha256": "e025279ffb304a08f2f960845c6dca1e09162188bffd44f541cd787ae0aaf094", "range": [1, 366]},
    20: {"sha256": "8f5437db04d4423b79db151603187f50400a9d41938f94394a8da744842af673", "range": [1, 268]},
}
ROMANS = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII", 13: "XIII", 14: "XIV", 15: "XV", 16: "XVI", 17: "XVII", 18: "XVIII", 19: "XIX", 20: "XX"}
PUBLISHED_BOOKS = list(range(1, 21))
# This identity comes from its place between the accepted English milestones,
# not from a parallel Latin label. No unreviewed markerless narrative is inferred.
CONTINUATIONS = {4: {"english-book04-num276b": {"section": 276,
    "previousSourceId": "english-book04-num276", "nextSourceId": "english-book04-num277"}},
    8: {"english-book08-num255": {"section": 255, "previousSourceId": "english-book08-num251",
        "nextSourceId": "english-book08-num263", "firstMilestone": 256, "nextSection": 263}},
    12: {"english-book12-num148": {"section": 147, "previousSourceId": "english-book12-num145",
          "nextSourceId": "english-book12-num154", "firstMilestone": 148, "nextSection": 154},
         "english-book12-num225": {"section": 226, "previousSourceId": "english-book12-num223",
          "nextSourceId": "english-book12-num228", "firstMilestone": 227, "nextSection": 228}},
    14: {"english-book14-num237": {"section": 237, "previousSourceId": "english-book14-num236",
          "nextSourceId": "english-book14-num241", "firstMilestone": 238, "nextSection": 241}}}
CHAPTER_MILESTONES = {15: [(f"english-book15-num{paragraph}", str(chapter)) for chapter, paragraph in
    [(1, 1), (2, 11), (3, 39), (4, 88), (5, 106), (6, 121), (7, 121),
     (8, 161), (9, 194), (10, 213), (11, 299), (12, 326), (13, 380)]]}

CHAPTER_MILESTONES.update({16: [('english-book16-num1', '1'),
      ('english-book16-num12', '2'),
      ('english-book16-num16', '3'),
      ('english-book16-num27', '4'),
      ('english-book16-num58', '5'),
      ('english-book16-num58', '6'),
      ('english-book16-num66', '7'),
      ('english-book16-num73', '8'),
      ('english-book16-num104', '9'),
      ('english-book16-num136', '10'),
      ('english-book16-num162', '11'),
      ('english-book16-num179', '12'),
      ('english-book16-num261', '13'),
      ('english-book16-num271', '14'),
      ('english-book16-num271', '15'),
      ('english-book16-num286', '16')],
 17: [('english-book17-num1', '1'),
      ('english-book17-num12', '2'),
      ('english-book17-num32', '3'),
      ('english-book17-num46', '4'),
      ('english-book17-num52', '5'),
      ('english-book17-num61', '6'),
      ('english-book17-num61', '7'),
      ('english-book17-num83', '8'),
      ('english-book17-num131', '9'),
      ('english-book17-num146', '10'),
      ('english-book17-num182', '11'),
      ('english-book17-num188', '12'),
      ('english-book17-num188', '13'),
      ('english-book17-num193', '14'),
      ('english-book17-num196', '15'),
      ('english-book17-num206', '16'),
      ('english-book17-num213', '17'),
      ('english-book17-num250', '18'),
      ('english-book17-num299', '19')],
 18: [('english-book18-num1', '1'),
      ('english-book18-num1', '2'),
      ('english-book18-num1', '3'),
      ('english-book18-num1', '4'),
      ('english-book18-num11', '5'),
      ('english-book18-num26', '6'),
      ('english-book18-num29', '7'),
      ('english-book18-num29', '8'),
      ('english-book18-num55', '9'),
      ('english-book18-num65', '10'),
      ('english-book18-num88', '11'),
      ('english-book18-num88', '12'),
      ('english-book18-num90', '13'),
      ('english-book18-num96', '14'),
      ('english-book18-num106', '15'),
      ('english-book18-num130', '16'),
      ('english-book18-num240', '17'),
      ('english-book18-num257', '18'),
      ('english-book18-num257', '19'),
      ('english-book18-num261', '20'),
      ('english-book18-num310', '21')],
 19: [('english-book19-num1', '1'),
      ('english-book19-num162', '2'),
      ('english-book19-num236', '3'),
      ('english-book19-num274', '4'),
      ('english-book19-num292', '5'),
      ('english-book19-num299', '6'),
      ('english-book19-num326', '7'),
      ('english-book19-num335', '8')],
 20: [('english-book20-num1', '1'),
      ('english-book20-num1', '2'),
      ('english-book20-num1', '3'),
      ('english-book20-num10', '4'),
      ('english-book20-num17', '5'),
      ('english-book20-num49', '6'),
      ('english-book20-num100', '7'),
      ('english-book20-num100', '8'),
      ('english-book20-num105', '9'),
      ('english-book20-num118', '10'),
      ('english-book20-num125', '11'),
      ('english-book20-num134', '12'),
      ('english-book20-num137', '13'),
      ('english-book20-num148', '14'),
      ('english-book20-num167', '15'),
      ('english-book20-num173', '16'),
      ('english-book20-num182', '17'),
      ('english-book20-num189', '18'),
      ('english-book20-num197', '19'),
      ('english-book20-num215', '20')]})
STRUCTURAL_HEADINGS = {20: [{'kind': 'structural-heading',
       'element': 'head',
       'text': 'CONTAINING THE INTERVAL OF TWENTY-TWO YEARS. FROM FADUS THE PROCURATOR TO FLORUS.',
       'sourceAttributes': {'sameAs': '#latin-book20-chapter1-head'},
       'parentAttributes': {'n': '1',
                            'sameAs': '#latin-book20-chapter1',
                            'type': 'chapter',
                            '{http://www.w3.org/XML/1998/namespace}id': 'english-book20-chapter1'}}]}
TRANSPARENT_TAGS = {"hi", "emph", "seg", "ref", "q", "quote", "foreign", "s"}
STRUCTURAL_TAGS = {"anchor", "lb", "pb", "cb"}


class ExtractionError(ValueError):
    """Source text or structure falls outside the reviewed extraction contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ExtractionError(message)


def q(name: str) -> str:
    return f"{{{TEI}}}{name}"


def sha(value: bytes | str) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def utf16_slice(text: str, start: int, end: int) -> str:
    return text.encode("utf-16-le")[start * 2:end * 2].decode("utf-16-le")


def words(text: str) -> list[str]:
    result: list[str] = []
    current = ""
    for char in text:
        category = unicodedata.category(char)[0]
        if category in {"L", "N"} or (current and category == "M"):
            current += char
        elif current:
            result.append(current)
            current = ""
    if current:
        result.append(current)
    return result


def source_info(xml_bytes: bytes, path: str) -> dict:
    return {"path": path, "sha256": sha(xml_bytes), "bytes": len(xml_bytes)}


def expected_sequence(book: int, preface: bool) -> list[int]:
    key = "preface" if preface else book
    require(key in SOURCE_CONTRACTS, f"Unreviewed Whiston source: {key}")
    first, last = SOURCE_CONTRACTS[key]["range"]
    if book == 11 and not preface:
        return list(range(1, 312)) + list(range(326, 343)) + list(range(312, 326)) + list(range(343, 348))
    return list(range(first, last + 1))


def flatten_paragraph(paragraph: ET.Element) -> dict:
    """Keep separate coordinates for raw itertext and searchable running text."""
    raw_chunks, flat_chunks, text_spans, exclusions, markers, structure = [], [], [], [], [], []
    raw_length = flat_length = 0

    def running(text: str | None) -> None:
        nonlocal raw_length, flat_length
        if not text:
            return
        text_spans.append({"rawStart": raw_length, "rawEnd": raw_length + len(text),
                           "flatStart": flat_length, "flatEnd": flat_length + len(text)})
        raw_chunks.append(text)
        flat_chunks.append(text)
        raw_length += len(text)
        flat_length += len(text)

    def visit(element: ET.Element) -> None:
        nonlocal raw_length
        running(element.text)
        for child in element:
            require(child.tag.startswith(f"{{{TEI}}}"), "Foreign XML namespace in Whiston narrative")
            name = child.tag.split("}", 1)[1]
            if name in {"num", "note"}:
                if name == "note":
                    require(child.get("type") == "whiston-footnote", "Unreviewed inline Whiston note")
                raw = "".join(child.itertext())
                exclusions.append({"rawStart": raw_length, "rawEnd": raw_length + len(raw),
                                   "kind": "citation-label" if name == "num" else "whiston-footnote",
                                   "text": raw, "sourceAttributes": dict(child.attrib)})
                raw_chunks.append(raw)
                raw_length += len(raw)
            elif name == "milestone":
                require(not len(child) and not (child.text or ""), "A Whiston milestone contains text")
                require(child.get("unit") in {"niese", "chapter"}
                        and re.fullmatch(r"[1-9][0-9]*", child.get("n", "")), "Unreviewed Whiston milestone")
                if child.get("unit") == "niese":
                    markers.append({"section": int(child.get("n")), "rawOffset": raw_length,
                                    "flatOffset": flat_length, "sourceAttributes": dict(child.attrib)})
                else:
                    structure.append({"kind": "milestone", "rawOffset": raw_length,
                                      "flatOffset": flat_length, "sourceAttributes": dict(child.attrib)})
            elif name in STRUCTURAL_TAGS:
                require(not len(child) and not (child.text or ""), f"A Whiston {name} marker contains text")
                structure.append({"kind": name, "rawOffset": raw_length, "flatOffset": flat_length,
                                  "sourceAttributes": dict(child.attrib)})
            elif name in TRANSPARENT_TAGS:
                visit(child)
            else:
                raise ExtractionError(f"Unreviewed Whiston inline element: {name}")
            running(child.tail)

    visit(paragraph)
    raw = "".join(paragraph.itertext())
    require("".join(raw_chunks) == raw, "Whiston paragraph traversal lost source text")
    return {"rawText": raw, "flatText": "".join(flat_chunks), "textSpans": text_spans,
            "exclusions": exclusions, "markers": markers, "structuralMarkers": structure}


def restore_pieces(flattened: dict, sections: list[dict], records_by_id: dict) -> tuple[list[dict], str]:
    """Reconstruct raw source from record slices and explicitly excluded bytes."""
    raw = flattened["rawText"]
    pieces = []
    for exclusion in flattened["exclusions"]:
        pieces.append({"kind": "excluded", "reason": exclusion["kind"], "text": exclusion["text"],
                       "sourceStart": exclusion["rawStart"], "sourceEnd": exclusion["rawEnd"],
                       "sourceAttributes": exclusion["sourceAttributes"]})
    for span in flattened["textSpans"]:
        cuts = {span["flatStart"], span["flatEnd"]}
        for section in sections:
            cuts.update(offset for offset in [section["textStart"], section["textEnd"]]
                        if span["flatStart"] < offset < span["flatEnd"])
        ordered = sorted(cuts)
        for left, right in zip(ordered, ordered[1:]):
            source_start = span["rawStart"] + left - span["flatStart"]
            source_end = source_start + right - left
            selected = next((section for section in sections
                             if section["textStart"] <= left and right <= section["textEnd"]), None)
            if selected:
                record = records_by_id[selected["recordId"]]
                record_start = selected.get("recordOffset", 0) + utf16_length(flattened["flatText"][selected["textStart"]:left])
                record_end = record_start + utf16_length(flattened["flatText"][left:right])
                pieces.append({"kind": "record", "recordId": record["id"],
                               "recordStart": record_start, "recordEnd": record_end,
                               "sourceStart": source_start, "sourceEnd": source_end})
            else:
                value = raw[source_start:source_end]
                before_first = right <= sections[0]["flatStart"]
                require(value.isspace() or before_first,
                        "Non-whitespace narrative text was excluded outside a citation interval")
                pieces.append({"kind": "excluded", "reason": "pre-marker-label-punctuation" if before_first
                               else "section-edge-whitespace", "text": value,
                               "sourceStart": source_start, "sourceEnd": source_end})
    pieces.sort(key=lambda piece: (piece["sourceStart"], piece["sourceEnd"]))
    restored = []
    cursor = 0
    for piece in pieces:
        require(piece["sourceStart"] == cursor, "Whiston restoration pieces overlap or leave source text uncovered")
        cursor = piece["sourceEnd"]
        value = (utf16_slice(records_by_id[piece["recordId"]]["text"], piece["recordStart"], piece["recordEnd"])
                 if piece["kind"] == "record" else piece["text"])
        require(value == raw[piece["sourceStart"]:piece["sourceEnd"]], "Whiston record slice differs from its source")
        restored.append(value)
        piece["sourceStart"] = utf16_length(raw[:piece["sourceStart"]])
        piece["sourceEnd"] = utf16_length(raw[:piece["sourceEnd"]])
        piece["textSHA256"] = sha(value)
    require(cursor == len(raw), "Whiston restoration misses final source text")
    rebuilt = "".join(restored)
    require(rebuilt == raw, "Whiston paragraph cannot be restored from its records")
    return pieces, rebuilt


def extract_document(xml_bytes: bytes, *, book_number: int = 1, preface: bool = False,
                     order_offset: int = 0, source_path: str | None = None,
                     verify_source: bool = True, expected_sections: list[int] | None = None) -> tuple[list[dict], dict]:
    key = "preface" if preface else book_number
    require(key in SOURCE_CONTRACTS, f"Unreviewed Whiston source: {key}")
    wanted = expected_sequence(book_number, preface) if expected_sections is None else expected_sections
    require(wanted and all(isinstance(value, int) and value > 0 for value in wanted),
            "Expected Whiston sections must be positive integer identities")
    require(not preface or book_number == 1, "The Whiston Proem belongs with Book I")
    path = source_path or f"{SOURCE_PREFIX}/{'preface' if preface else f'book-{book_number:02d}'}.xml"
    if verify_source:
        require(sha(xml_bytes.replace(b"\r\n", b"\n")) == SOURCE_CONTRACTS[key]["sha256"],
                f"Whiston source differs from the accepted source: {path}")
    root = ET.fromstring(xml_bytes)
    require(root.tag == q("TEI"), "Whiston source has no TEI root")
    bodies = root.findall(f".//{q('body')}")
    require(len(bodies) == 1, "Whiston source needs exactly one body")
    body = bodies[0]
    allowed = {q(tag) for tag in {"body", "div1", "div2", "p", "head", "note", "num", "milestone"}
               | STRUCTURAL_TAGS | TRANSPARENT_TAGS}
    require(all(element.tag in allowed for element in body.iter()), "Unreviewed Whiston body element")
    parents = {child: parent for parent in body.iter() for child in parent}
    containers = {q("body"), q("div1"), q("div2")}
    structural_headings = []
    for element in body.iter():
        parent = parents.get(element)
        if element.tag in containers:
            require(element is body or parent.tag in containers, "Whiston division is nested in narrative text")
            require(not (element.text or "").strip(), "Unclassified text outside Whiston paragraphs")
            require(all(not (child.tail or "").strip() for child in element),
                    "Unclassified tail text outside Whiston paragraphs")
        elif element.tag == q("p"):
            require(parent.tag in containers, "Whiston paragraph is outside a reviewed division")
        elif element.tag == q("head"):
            require(parent.tag == q("div2") and parent[0] is element and not len(element),
                    "Whiston structural heading is outside its accepted location or contains markup")
            structural_headings.append({"kind": "structural-heading", "element": "head",
                                        "text": element.text or "", "sourceAttributes": dict(element.attrib),
                                        "parentAttributes": dict(parent.attrib)})
        else:
            ancestor = parent
            while ancestor is not None and ancestor.tag != q("p"):
                ancestor = parents.get(ancestor)
            require(ancestor is not None or (element.tag == q("note") and parent is body),
                    "Unclassified Whiston inline element outside a paragraph")
    require(structural_headings == STRUCTURAL_HEADINGS.get(book_number, []),
            "Whiston structural headings differ from the accepted source")
    records, paragraphs, excluded_blocks, source_words, source_content = [], [], [], [], []
    raw_paragraphs, restored_paragraphs = [], []
    source_ids = set()
    counts = Counter(bodyParagraphs=len(body.findall(f".//{q('p')}")), narrativeParagraphs=0,
                     excludedHeadingParagraphs=0, excludedFootnotes=0, excludedCitationLabels=0,
                     excludedSourceNotes=0, nieseMilestones=0, structuralMarkers=0)
    for element in body.iter():
        if element.tag == q("note") and parents.get(element) is body:
            require("".join(element.itertext()).strip() == "William Whiston (1737)", "Unreviewed Whiston source notice")
            excluded_blocks.append({"kind": "source-note", "text": "".join(element.itertext()),
                                    "sourceAttributes": dict(element.attrib)})
            counts["excludedSourceNotes"] += 1
    if structural_headings:
        excluded_blocks.extend(structural_headings)
        counts["excludedStructuralHeadings"] = len(structural_headings)
    source_paragraphs = body.findall(f".//{q('p')}")
    for number, paragraph in enumerate(source_paragraphs):
        require(not paragraph.findall(f".//{q('p')}"), "Nested Whiston paragraphs are unreviewed")
        markers = paragraph.findall(f".//{q('milestone')}[@unit='niese']")
        continuation = CONTINUATIONS.get(book_number, {}).get(paragraph.get(XML_ID)) if not preface else None
        if not markers and not continuation:
            value = "".join(paragraph.itertext())
            heading = (not paragraph.get(XML_ID) or paragraph.get("rend") == "whiston-chapter-heading")
            require(heading and not paragraph.findall(f".//{q('milestone')}"),
                    "Unclassified Whiston paragraph without a Niese marker")
            require(re.match(r"(?:BOOK\b|CHAPTER\b|CONTAINING\b|Antiquities of the Jews -- Preface$)", value.strip(), re.I),
                    "Unreviewed Whiston heading paragraph")
            excluded_blocks.append({"kind": "heading", "text": value, "sourceAttributes": dict(paragraph.attrib),
                                    "paragraphOrdinal": number})
            counts["excludedHeadingParagraphs"] += 1
            continue
        require(paragraph.get(XML_ID), "Whiston narrative paragraph needs its accepted source ID")
        require(paragraph.get(XML_ID) not in source_ids, "Duplicate Whiston narrative source ID")
        source_ids.add(paragraph.get(XML_ID))
        flat = flatten_paragraph(paragraph)
        join = None
        if continuation:
            require(records, "Whiston continuation must follow an existing citation")
            if "firstMilestone" in continuation:
                require(flat["markers"] and flat["markers"][0]["section"] == continuation["firstMilestone"]
                        == continuation["section"] + 1, "Whiston prefix continuation has an unexpected first milestone")
            else:
                require(not markers and not flat["markers"], "Whiston continuation must have no invented milestone")
            require(number > 0 and number + 1 < len(source_paragraphs)
                    and source_paragraphs[number - 1].get(XML_ID) == continuation["previousSourceId"]
                    and source_paragraphs[number + 1].get(XML_ID) == continuation["nextSourceId"]
                    and records[-1]["section"] == continuation["section"], "Whiston continuation is outside its accepted physical location")
            next_markers = source_paragraphs[number + 1].findall(f".//{q('milestone')}[@unit='niese']")
            require(next_markers and int(next_markers[0].get("n")) == continuation.get("nextSection", continuation["section"] + 1),
                    "Whiston continuation has an unexpected following milestone")
        prefix = flat["flatText"][:flat["markers"][0]["flatOffset"]] if flat["markers"] and not continuation else ""
        require(re.fullmatch(r"[\s.]*", prefix), "Narrative words occur before the first Whiston milestone")
        sections = []
        interval_markers = ([{"section": continuation["section"], "flatOffset": 0}] if continuation else []) + flat["markers"]
        for index, marker in enumerate(interval_markers):
            continuing = continuation is not None and index == 0
            start = marker["flatOffset"]
            end = interval_markers[index + 1]["flatOffset"] if index + 1 < len(interval_markers) else len(flat["flatText"])
            fragment = flat["flatText"][start:end]
            text = fragment.strip()
            require(text, f"Empty Whiston citation interval: {book_number}.{marker['section']}")
            left = len(fragment) - len(fragment.lstrip())
            text_start, text_end = start + left, start + left + len(text)
            section = marker["section"]
            reader_book = "preface" if preface else book_number
            if continuing:
                record = records[-1]
                separator_start = utf16_length(record["text"])
                join = {"kind": "paragraph-separator", "recordId": record["id"], "start": separator_start,
                        "end": separator_start + 2, "text": "\n\n"}
                record["text"] += join["text"] + text
                record["sourceIds"].append(paragraph.get(XML_ID))
            else:
                record = {"id": f"{COLLECTION}-{book_number}-{section}", "work": "antiquities", "book": book_number,
                      "section": section, "language": "English", "edition": EDITION, "citationScheme": "niese",
                      "citationLabel": f"{ROMANS[book_number]}.{section}",
                      "citation": {"book": ROMANS[book_number], "section": section, **({"proem": True} if preface else {})},
                      "text": text, "editorialMarks": [], "sourceMarkup": [], "textGaps": [], "phraseBreaks": [],
                      "url": f"/antiquities/?book={reader_book}&niese={section}&english=whiston",
                      "readerLink": {"path": "antiquities/", "params": {"book": reader_book, "niese": section, "english": "whiston"}},
                      "sourceId": paragraph.get(XML_ID), "sourceIds": [paragraph.get(XML_ID)], "sourcePath": path,
                      "order": order_offset + len(records)}
                if preface:
                    record.update(sourceDivision="proem", division="proem")
                elif book_number == 1 and section == 27:
                    record.update(breakBefore=True, breakReason="Book I narrative begins after the separately transmitted Proem.")
                records.append(record)
            sections.append({"recordId": record["id"], "section": section, "flatStart": start, "flatEnd": end,
                             "textStart": text_start, "textEnd": text_end, "leadingWhitespace": fragment[:left],
                             "trailingWhitespace": fragment[left + len(text):], "textSHA256": sha(text)})
            if continuing:
                sections[-1]["recordOffset"] = join["end"]
        by_id = {record["id"]: record for record in records}
        pieces, restored = restore_pieces(flat, sections, by_id)
        projected = flat["flatText"][len(prefix):]
        source_words.extend(words(projected))
        source_content.append(re.sub(r"\s", "", projected))
        raw_paragraphs.append(flat["rawText"])
        restored_paragraphs.append(restored)
        for marker in flat["markers"] + flat["structuralMarkers"]:
            marker["sourceTextOffset"] = utf16_length(flat["rawText"][:marker.pop("rawOffset")])
            marker["runningTextOffset"] = utf16_length(flat["flatText"][:marker.pop("flatOffset")])
        # Only the externally useful audit coordinates use UTF-16; Python
        # slicing coordinates are retained explicitly under distinct names.
        for section in sections:
            for coordinate in ["flatStart", "flatEnd", "textStart", "textEnd"]:
                section[coordinate + "CodePoints"] = section.pop(coordinate)
        paragraphs.append({"sourceId": paragraph.get(XML_ID), "sourcePath": path, "paragraphOrdinal": number,
                           "rawText": flat["rawText"], "runningText": projected,
                           "sourcePieces": pieces, "sections": sections,
                           "nieseMarkers": flat["markers"], "structuralMarkers": flat["structuralMarkers"],
                           "exactRestorationVerified": restored == flat["rawText"]})
        if continuation:
            paragraphs[-1].update(continuationOf={"recordId": join["recordId"], **continuation}, recordJoin=join)
            counts["continuationParagraphs"] += 1
        counts.update(narrativeParagraphs=1, nieseMilestones=len(flat["markers"]),
                      structuralMarkers=len(flat["structuralMarkers"]),
                      excludedFootnotes=sum(item["kind"] == "whiston-footnote" for item in flat["exclusions"]),
                      excludedCitationLabels=sum(item["kind"] == "citation-label" for item in flat["exclusions"]))
    chapter_milestones = [(paragraph["sourceId"], marker["sourceAttributes"]["n"])
                          for paragraph in paragraphs for marker in paragraph["structuralMarkers"]
                          if marker["kind"] == "milestone" and marker["sourceAttributes"].get("unit") == "chapter"]
    require(chapter_milestones == CHAPTER_MILESTONES.get(book_number, []),
            "Whiston chapter milestones differ from the accepted source")
    actual = [record["section"] for record in records]
    require(actual == wanted, f"Whiston milestone identities or physical order differ in {path}")
    require(len({record["id"] for record in records}) == len(records), "Duplicate Whiston record identity")
    require({p["sourceId"] for p in paragraphs if "continuationOf" in p} == set(CONTINUATIONS.get(book_number, {})),
            "Whiston source omits a reviewed continuation paragraph")
    indexed_words = [word for record in records for word in words(record["text"])]
    indexed_content = "".join(re.sub(r"\s", "", record["text"]) for record in records)
    require(source_words == indexed_words, "Whiston interval boundaries changed the source word sequence")
    require("".join(source_content) == indexed_content, "Whiston projection lost non-whitespace running text")
    counts.update(sections=len(records), runningWordTokens=len(indexed_words),
                  numberedParagraphs=counts["narrativeParagraphs"], breakBeforeUnits=sum(bool(r.get("breakBefore")) for r in records))
    coverage = {"completeRange": [min(wanted), max(wanted)], "sourceSectionOrder": actual,
                "missingSections": [], "unexpectedSections": [], "duplicateSections": [],
                "allSectionTextsNonempty": all(record["text"] for record in records),
                "paragraphsExactlyRestored": len(restored_paragraphs), "wordSequencePreserved": source_words == indexed_words,
                "nonWhitespaceContentPreserved": "".join(source_content) == indexed_content,
                "rawParagraphSequenceSha256": sha("\n".join(raw_paragraphs)),
                "restoredParagraphSequenceSha256": sha("\n".join(restored_paragraphs)),
                "sourceWordSequenceSha256": sha("\n".join(source_words)),
                "indexedWordSequenceSha256": sha("\n".join(indexed_words)),
                "sourceNonWhitespaceContentSha256": sha("".join(source_content)),
                "indexedNonWhitespaceContentSha256": sha(indexed_content)}
    report = {"schemaVersion": 1, "status": "PASS", "scope": {"work": "Antiquities", "book": book_number,
              "language": "English", "edition": EDITION, "unit": "Niese section", "citationScheme": "niese", "proem": preface},
              "source": source_info(xml_bytes, path), "sourceContract": {"normalizedSHA256": SOURCE_CONTRACTS[key]["sha256"],
              "hashMode": "CRLF-to-LF only", "verified": verify_source}, "counts": dict(counts), "coverage": coverage,
              "excludedBlocks": excluded_blocks, "paragraphs": paragraphs}
    return records, report


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def aggregate_evidence(records: list[dict], documents: list[dict], ranges: dict) -> tuple[Counter, list[dict], dict]:
    counts = Counter()
    for report in documents:
        counts.update(report["counts"])
    paragraphs = [paragraph for report in documents for paragraph in report["paragraphs"]]
    by_id = {record["id"]: record for record in records}
    restored = ["".join(utf16_slice(by_id[piece["recordId"]]["text"], piece["recordStart"], piece["recordEnd"])
                        if piece["kind"] == "record" else piece["text"] for piece in paragraph["sourcePieces"])
                for paragraph in paragraphs]
    source_words = [word for paragraph in paragraphs for word in words(paragraph["runningText"])]
    indexed_words = [word for record in records for word in words(record["text"])]
    source_content = "".join(re.sub(r"\s", "", paragraph["runningText"]) for paragraph in paragraphs)
    indexed_content = "".join(re.sub(r"\s", "", record["text"]) for record in records)
    coverage = {**ranges, "missingSections": [], "unexpectedSections": [], "duplicateSections": [],
                "allSectionTextsNonempty": all(record["text"] for record in records), "paragraphsExactlyRestored": len(restored),
                "wordSequencePreserved": source_words == indexed_words, "nonWhitespaceContentPreserved": source_content == indexed_content,
                "rawParagraphSequenceSha256": sha("\n".join(p["rawText"] for p in paragraphs)),
                "restoredParagraphSequenceSha256": sha("\n".join(restored)),
                "sourceWordSequenceSha256": sha("\n".join(source_words)), "indexedWordSequenceSha256": sha("\n".join(indexed_words)),
                "sourceNonWhitespaceContentSha256": sha(source_content), "indexedNonWhitespaceContentSha256": sha(indexed_content)}
    for first, second in [("rawParagraphSequenceSha256", "restoredParagraphSequenceSha256"),
                          ("sourceWordSequenceSha256", "indexedWordSequenceSha256"),
                          ("sourceNonWhitespaceContentSha256", "indexedNonWhitespaceContentSha256")]:
        require(coverage[first] == coverage[second], f"Whiston combined coverage failed: {first}")
    return counts, paragraphs, coverage


def build_book_report(records: list[dict], documents: list[dict], book_number: int) -> dict:
    section_range = [1, SOURCE_CONTRACTS[book_number]["range"][1]]
    counts, paragraphs, coverage = aggregate_evidence(records, documents, {"completeRange": section_range})
    sources = [report["source"] for report in documents]
    # Books I–XV retain their original reviewed report bytes as well as their corpora.
    # Historical scope statements describe those releases, not the expanded catalog.
    published_scope = ("Proem and Book I only. IX and XI are extraction-test inputs, not indexed pilot books."
                       if book_number == 1 else f"Book {ROMANS[book_number]}. The collection covers the Proem and Books I–V; IX and XI remain test-only."
                       if book_number <= 5 else f"Book {ROMANS[book_number]}. The collection covers the Proem and Books I–X; XI remains test-only."
                       if book_number <= 10 else f"Book {ROMANS[book_number]}. The collection covers the Proem and Books I–XV."
                       if book_number <= 15 else f"Book {ROMANS[book_number]}. The collection covers the Proem and Books I–XX.")
    book_report = {"schemaVersion": 1, "status": "PASS", "scope": {"work": "Antiquities", "book": book_number, "language": "English",
                   "edition": EDITION, "unit": "Niese section", "citationScheme": "niese", "includesProem": book_number == 1},
                   "source": sources[-1], "additionalSources": sources[:-1], "sources": sources,
                   "rules": {"boundaries": "Accepted English milestone unit=niese positions; never inferred from Latin IDs or gaps.",
                   "text": "Preserve running source characters; trim interval edges; exclude documented headings, num labels and footnotes.",
                   "prefixPunctuation": "Only whitespace and periods before a paragraph's first accepted Niese milestone are excluded; exact source positions and characters remain in sourcePieces. Punctuation after that milestone is preserved.",
                   "phraseBoundaries": ("Book I narrative begins after the separate Proem; no phrase crosses I.26–27."
                                        if book_number == 1 else "Exact phrases follow the accepted English source order within this book; they never cross to another book."),
                   "coordinates": "sourcePieces sourceStart/sourceEnd and recordStart/recordEnd are original-text UTF-16 offsets.",
                   "publishedScope": published_scope},
                   "counts": dict(counts), "coverage": coverage, "documentReports": documents, "paragraphs": paragraphs}
    if book_number in CONTINUATIONS:
        book_report["rules"]["paragraphContinuations"] = ("The explicitly reviewed markerless paragraph continues its preceding Niese interval. Two display newlines preserve its paragraph boundary; recordJoin documents this separator and sourcePieces retain exact original-text spans."
            if book_number == 4 else "The explicitly reviewed paragraph prefix continues VIII.255 until the existing milestone256. No Niese marker is invented. Two display newlines preserve the paragraph boundary; recordJoin documents this separator and sourcePieces retain exact original-text spans."
            if book_number == 8 else "Explicitly reviewed paragraph prefixes continue their preceding accepted Niese intervals until the next existing milestones. No marker is invented. Two display newlines preserve paragraph boundaries; recordJoin documents each separator and sourcePieces retain exact original-text spans.")
    return book_report


def build_corpus(source_root: Path, output_dir: Path) -> dict:
    records, documents, books = [], [], []
    for book_number in PUBLISHED_BOOKS:
        book_records, book_documents = [], []
        filenames = [(f"book-{book_number:02d}", False)]
        if book_number == 1:
            filenames.insert(0, ("preface", True))
        for name, preface in filenames:
            relative = f"{SOURCE_PREFIX}/{name}.xml"
            part, document = extract_document((source_root / relative).read_bytes(), book_number=book_number,
                                              preface=preface, order_offset=len(records) + len(book_records), source_path=relative)
            book_records.extend(part)
            book_documents.append(document)
        expected_book_order = list(range(1, 347)) if book_number == 1 else expected_sequence(book_number, False)
        require([record["section"] for record in book_records] == expected_book_order,
                f"Whiston Book {ROMANS[book_number]} coverage or physical order differs")
        book_report = build_book_report(book_records, book_documents, book_number)
        corpus_bytes, book_report_bytes = json_bytes(book_records), json_bytes(book_report)
        stem = f"book-{book_number:02d}"
        write_bytes(output_dir / f"{stem}.corpus.json", corpus_bytes)
        write_bytes(output_dir / f"{stem}.extraction-report.json", book_report_bytes)
        books.append({"book": book_number, "status": "PASS", "source": book_report["source"],
                      "additionalSources": book_report["additionalSources"], "sources": book_report["sources"],
                      "counts": book_report["counts"], "orderStart": len(records), "orderEnd": len(records) + len(book_records) - 1,
                      "corpus": {"path": f"{OUTPUT_PREFIX}/{stem}.corpus.json", "sha256": sha(corpus_bytes), "bytes": len(corpus_bytes), "records": len(book_records)},
                      "extractionReport": {"path": f"{OUTPUT_PREFIX}/{stem}.extraction-report.json", "sha256": sha(book_report_bytes), "bytes": len(book_report_bytes)}})
        records.extend(book_records)
        documents.extend(book_documents)
    counts, _, coverage = aggregate_evidence(records, documents, {"completeRangesByBook":
                                             {str(book): [1, SOURCE_CONTRACTS[book]["range"][1]] for book in PUBLISHED_BOOKS}})
    corpus_bytes = json_bytes(records)
    write_bytes(output_dir / "corpus.json", corpus_bytes)
    combined = {"schemaVersion": 1, "status": "PASS", "scope": {"work": "Antiquities", "books": PUBLISHED_BOOKS, "language": "English",
                "edition": EDITION, "unit": "Niese section", "citationScheme": "niese", "includesProem": True},
                "counts": {"books": len(PUBLISHED_BOOKS), "sourceDocuments": len(documents), **dict(counts)},
                "coverage": {**coverage, "globalIdsUnique": len({record["id"] for record in records}) == len(records),
                "globalOrderIsConsecutive": [record["order"] for record in records] == list(range(len(records)))},
                "corpus": {"path": f"{OUTPUT_PREFIX}/corpus.json", "sha256": sha(corpus_bytes), "bytes": len(corpus_bytes), "records": len(records)},
                "books": books}
    write_bytes(output_dir / "extraction-report.json", json_bytes(combined))
    return combined


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=here.parent.parent)
    parser.add_argument("--output-dir", type=Path, default=here / "data" / COLLECTION)
    args = parser.parse_args()
    report = build_corpus(args.source_root.resolve(), args.output_dir.resolve())
    print(json.dumps({"status": report["status"], "scope": report["scope"], "counts": report["counts"], "corpus": report["corpus"]}, indent=2))


if __name__ == "__main__":
    main()
