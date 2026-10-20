/** Independent Antiquities I–XX source, token, and query acceptance.
 * The exact Python minidom witness is embedded and checked against the separate
 * witness file. No production extractor, tokenizer, parser or phrase matcher
 * is used to generate expected source content or expected query results.
 */
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync, mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {dirname, relative, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {performance} from 'node:perf_hooks';

let root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
let smoke = false, explicitReaderSHA = null;
const args = process.argv.slice(2);
const usage = 'Usage: node bin/search/tests/antiquities-corpus-qa.mjs [--smoke] [--root <repository>] [--expected-reader-sha256 <SHA-256>]';
for (let index = 0; index < args.length; index++) {
  if (args[index] === '--smoke') {assert.equal(smoke, false, usage); smoke = true;}
  else if (args[index] === '--root') {assert.ok(args[index + 1], usage); root = resolve(args[++index]);}
  else if (args[index] === '--expected-reader-sha256') {
    assert.ok(explicitReaderSHA === null && /^[a-f0-9]{64}$/i.test(args[index + 1] || ''), usage);
    explicitReaderSHA = args[++index].toLowerCase();
  } else assert.fail(usage);
}
const base = resolve(root, 'bin/search');
const collectionId = 'antiquities-latin-bamberg78';
const romanBooks = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX'];
const witnessRecordId = row => row.id ?? `${collectionId}-${row.book}-${row.section}`;
const destination = resolve(base, 'data', collectionId, 'qa-report.json');
const require = createRequire(import.meta.url);
const lunr = require(resolve(base, 'vendor/lunr.cjs'));
const {createEngine} = await import(pathToFileURL(resolve(base, 'engine.mjs')));
const {createCollection} = await import(pathToFileURL(resolve(base, 'collection.mjs')));
const {readerURL, passageDivisionLabel} = await import(pathToFileURL(resolve(base, 'ui-utils.mjs')));
const started = performance.now();
const hash = value => createHash('sha256').update(value).digest('hex');
const digest = path => hash(readFileSync(path));
const readJSON = path => JSON.parse(readFileSync(path, 'utf8'));
const evidence = path => ({path: relative(root, path).replaceAll('\\', '/'), sha256: digest(path), bytes: readFileSync(path).length});
const counts = {}, examples = [], checkedFiles = new Map();
let assertions = 0, totalQueries = 0;
let sourceRows = new Map();
function preserve(path) {
  const resolved = resolve(path);
  if (!checkedFiles.has(resolved)) checkedFiles.set(resolved, digest(resolved));
  return resolved;
}
function check(category, actual, expected, context = {}) {
  assertions++; counts[category] = (counts[category] || 0) + 1;
  assert.deepEqual(actual, expected, `${category}: ${JSON.stringify(context)}`);
}


const pythonWitness = String.raw`#!/usr/bin/env python3
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
`;

// Distinct from production tokenizeText: character-by-character, used also for
// unchanged Bellum index records in the mixed-work collection checks.
function independentTokens(text, splitOffsets = []) {
  const result = [];
  const interruptions = new Set(splitOffsets);
  let offset = 0, start = null, value = '';
  const emit = () => {
    if (start !== null) result.push({term: normalize(value), start, end: offset});
    start = null; value = '';
  };
  for (const character of text) {
    if (interruptions.has(offset)) emit();
    const canStart = /[\p{L}\p{N}]/u.test(character);
    const canContinue = /[\p{L}\p{M}\p{N}]/u.test(character);
    if (start !== null && canContinue) value += character;
    else {
      emit();
      if (canStart) {start = offset; value = character;}
    }
    offset += character.length;
  }
  emit();
  return result;
}
function normalize(value, fold = false) {
  let result = value.normalize('NFC').toLowerCase().replaceAll('ς', 'σ');
  if (fold) result = result.replaceAll('v', 'u').replaceAll('j', 'i');
  return result.normalize('NFC');
}
function glob(pattern, word) {
  const escaped = pattern.split('*').map(part => part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('.*');
  return new RegExp(`^(?:${escaped})$`, 'u').test(word);
}
const leaf = pattern => ({op: 'leaf', patterns: [pattern]});
const phrase = patterns => ({op: 'leaf', patterns, phrase: true});
const and = (left, right) => ({op: 'and', left, right});
const or = (left, right) => ({op: 'or', left, right});
const not = child => ({op: 'not', child});
function print(ast) {
  if (ast.op === 'leaf') return ast.phrase ? `"${ast.patterns.join(' ')}"` : ast.patterns[0];
  if (ast.op === 'not') return `NOT (${print(ast.child)})`;
  return `(${print(ast.left)} ${ast.op.toUpperCase()} ${print(ast.right)})`;
}
const identity = record => JSON.stringify([record.work, Number(record.book), record.language, record.edition]);
const sourceUnit = record => (sourceRows.get(record.id)?.citationUnitId ?? record.citationUnitId ?? record.id);
const spanKey = spans => JSON.stringify(spans.map(span => [span.recordId, span.start, span.end]));
function makeOracle(records, suppliedTokens) {
  const byId = new Map(records.map((record, index) => [record.id, {record, index}]));
  const tokenLists = suppliedTokens || records.map(record => independentTokens(record.text,
    sourceRows.has(record.id) ? sourceRows.get(record.id).teiGaps.map(gap => gap.offset)
      : (record.textGaps || []).filter(gap => gap.kind === 'tei-gap' && gap.start === gap.end).map(gap => gap.start)));
  const all = [];
  const segments = new Map();
  const previousUnits = new Map(), unitSegments = new Map();
  records.forEach((record, index) => {
    const key = identity(record);
    if (previousUnits.get(key) !== sourceUnit(record)) unitSegments.set(key, (unitSegments.get(key) || 0) + 1);
    previousUnits.set(key, sourceUnit(record));
    let segment = segments.get(key) || 0;
    // Antiquities barriers are derived from the independent XML witness,
    // never from production record metadata. Earlier collections only enter
    // limited integration checks and retain their separately verified data.
    const sourceRow = sourceRows.get(record.id);
    if (sourceRow ? sourceRow.breakBefore : record.breakBefore) segment++;
    const sourceBarriers = sourceRow ? sourceRow.phraseBreaks : (record.phraseBreaks || []);
    let barrierIndex = 0;
    for (const token of tokenLists[index]) {
      while (barrierIndex < sourceBarriers.length && sourceBarriers[barrierIndex] <= token.start) {
        segment++; barrierIndex++;
      }
      all.push({...token, foldedTerm: normalize(token.term, true), recordId: record.id, recordIndex: index, bookKey: key, segment,
        citationUnit: sourceUnit(record), unitSegment: unitSegments.get(key)});
    }
    // A source barrier after the last token also separates the next record.
    segment += sourceBarriers.length - barrierIndex;
    segments.set(key, segment);
  });
  const vocabulary = [...new Set(all.map(token => token.term))].sort();
  const tables = new Map([false, true].map(fold => {
    const table = new Map();
    for (const token of all) {
      const key = normalize(token.term, fold);
      if (!table.has(key)) table.set(key, []);
      table.get(key).push(token);
    }
    return [fold, table];
  }));
  const keyOf = (record, scope) => scope === 'section' ? sourceUnit(record) : identity(record);
  function leafMatches(ast, scope, fold) {
    const result = new Map();
    const add = (key, spans) => {
      if (!result.has(key)) result.set(key, new Set());
      result.get(key).add(spanKey(spans));
    };
    const patterns = ast.patterns.map(pattern => normalize(pattern, fold));
    if (!ast.phrase) {
      const pattern = patterns[0], table = tables.get(fold);
      const matches = pattern.includes('*') ? [...table.keys()].filter(word => glob(pattern, word)) : table.has(pattern) ? [pattern] : [];
      for (const word of matches) for (const token of table.get(word))
        add(scope === 'section' ? token.citationUnit : token.bookKey, [token]);
      return result;
    }
    const matchers = patterns.map(pattern => {
      if (!pattern.includes('*')) return word => word === pattern;
      const escaped = pattern.split('*').map(part => part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('.*');
      const regex = new RegExp(`^(?:${escaped})$`, 'u');
      return word => regex.test(word);
    });
    // Full sequential scan; does not share production rarest-word anchoring,
    // Lunr candidate selection, phrase match helpers, or query parser.
    for (let i = 0; i <= all.length - patterns.length; i++) {
      const first = all[i];
      let accepted = true;
      for (let j = 0; j < patterns.length; j++) {
        const token = all[i + j];
        if (token.bookKey !== first.bookKey || token.segment !== first.segment
          || (scope === 'section' && (token.citationUnit !== first.citationUnit || token.unitSegment !== first.unitSegment))
          || !matchers[j](fold ? token.foldedTerm : token.term)) {accepted = false; break;}
      }
      if (!accepted) continue;
      const spans = [];
      for (const token of all.slice(i, i + patterns.length)) {
        if (spans.at(-1)?.recordId === token.recordId) spans.at(-1).end = token.end;
        else spans.push({recordId: token.recordId, start: token.start, end: token.end});
      }
      add(scope === 'section' ? first.citationUnit : first.bookKey, spans);
    }
    return result;
  }
  function evaluate(ast, scope, fold, negated = false) {
    if (ast.op === 'not') return evaluate(ast.child, scope, fold, !negated);
    if (ast.op === 'leaf') {
      const hits = leafMatches(ast, scope, fold);
      if (!negated) return hits;
      return new Map([...new Set(records.map(record => keyOf(record, scope)))].filter(key => !hits.has(key)).map(key => [key, new Set()]));
    }
    const left = evaluate(ast.left, scope, fold, negated), right = evaluate(ast.right, scope, fold, negated);
    const operation = negated ? (ast.op === 'and' ? 'or' : 'and') : ast.op;
    const result = new Map();
    for (const key of new Set([...left.keys(), ...right.keys()])) {
      if (operation === 'and' && (!left.has(key) || !right.has(key))) continue;
      result.set(key, new Set([...(left.get(key) || []), ...(right.get(key) || [])]));
    }
    return result;
  }
  return {records, tokenLists, all, vocabulary, byId, evaluate};
}

function compareResults(actual, expected, oracle, options, category, query, example = false) {
  const context = {query, ...options};
  const scope = options.scope;
  check(`${category}MatchingUnits`, actual.matchingUnits, expected.size, context);
  check(`${category}Occurrences`, actual.occurrences, [...expected.values()].reduce((sum, hits) => sum + hits.size, 0), context);
  const groupKey = group => scope === 'section' ? sourceUnit(oracle.byId.get(group.recordIds[0]).record)
    : group.work ? identity({work: group.work, book: group.book, language: group.language, edition: group.edition})
      : identity(oracle.records[0]);
  const actualGroups = new Map(actual.hitGroups.map(group => [groupKey(group), group]));
  check(`${category}UnitIdentity`, [...actualGroups.keys()].sort(), [...expected.keys()].sort(), context);
  const allTouched = new Set();
  const rank = id => oracle.byId.get(id).index;
  for (const [key, hits] of expected) {
    const group = actualGroups.get(key);
    check(`${category}Evidence`, group.hits.map(hit => spanKey(hit.spans)).sort(), [...hits].sort(), {...context, unit: key});
    const ids = scope === 'section' ? oracle.records.filter(record => sourceUnit(record) === key).map(record => record.id)
      : [...new Set([...hits].flatMap(hit => JSON.parse(hit).map(span => span[0])))].sort((a, b) => rank(a) - rank(b));
    ids.forEach(id => allTouched.add(sourceUnit(oracle.byId.get(id).record)));
    check(`${category}RecordIds`, group.recordIds, ids, {...context, unit: key});
    check(`${category}Sections`, group.sections, [...new Set(ids.map(id => oracle.byId.get(id).record.section))], {...context, unit: key});
  }
  check(`${category}MatchingSections`, actual.matchingSections, allTouched.size, context);
  if (example) examples.push({...context, matchingUnits: actual.matchingUnits, matchingSections: actual.matchingSections, occurrences: actual.occurrences});
}
function verify(engine, oracle, ast, options, category, query = print(ast), example = false) {
  totalQueries++;
  counts[`${category}Queries`] = (counts[`${category}Queries`] || 0) + 1;
  compareResults(engine.search(query, options), oracle.evaluate(ast, options.scope, options.fold), oracle, options, category, query, example);
}


const readerPath = resolve(root, 'assets/js/renderTei.js');
const witnessPath = resolve(base, 'tests/antiquities-source-witness.py');
const acceptedReaders = new Map([
  ['03bfb9b0de5e13e6b07bd638413b2b82a9ed2f7b0cc7c33eb6c09dabde3c9294', 'corrected-source-2026-10-19'],
  ['25c00a11818fe5a71dcbffb516aeb8a6f02c6b61c218f4e85105a12eb310d0ed', 'approved-public-preview'],
]);
const observedReaderSHA = digest(readerPath), readerSHA = explicitReaderSHA || observedReaderSHA;
const readerBaseline = {expectedSha256: readerSHA, observedSha256: observedReaderSHA,
  provenance: explicitReaderSHA ? 'explicit-argument' : acceptedReaders.get(readerSHA),
  preservationDuringRunRequired: true, publicationInput: false};

function compareSourceRecord(record, row, index) {
  const context = {book: row.book, section: row.section, id: witnessRecordId(row)};
  const isProem = row.readerBook === 'preface';
  const attributesFor = mark => ({kind: mark.kind, start: mark.start, end: mark.end, text: mark.text,
    sourceTag: mark.kind, sourceAttributes: mark.attributes});
  const gaps = [...row.literalGaps, ...row.teiGaps.map(gap => ({kind: 'tei-gap', start: gap.offset, end: gap.offset,
    text: '', sourceAttributes: gap.attributes}))];
  if (row.book >= 11) gaps.sort((a, b) => a.start - b.start || a.end - b.end || a.kind.localeCompare(b.kind));
  const grouping = Object.fromEntries(['citationUnitId', 'citationUnitCitation', 'sourceOccurrence',
    'continuationRank', 'fragmentCount', 'sourcePassage', 'sourceBoundaryEvidence'].filter(key => Object.hasOwn(row, key)).map(key => [key, row[key]]));
  const expectedComplete = {
    id: witnessRecordId(row), work: 'antiquities', book: row.book,
    section: row.section, language: 'Latin', edition: 'Bamberg Msc. Class. 78',
    citationScheme: 'niese', citationLabel: row.citationLabel,
    citation: {book: romanBooks[row.book - 1], section: row.section, ...(isProem ? {proem: true} : {})},
    text: row.text, editorialMarks: row.inlineMarks.filter(mark => ['add', 'del', 'unclear'].includes(mark.kind)).map(attributesFor),
    sourceMarkup: row.inlineMarks.filter(mark => ['s', 'ref', 'corr', 'expan'].includes(mark.kind)).map(attributesFor),
    textGaps: gaps, phraseBreaks: row.phraseBreaks, url: row.url,
    readerLink: {path: 'antiquities/', params: {book: row.readerBook, niese: row.readerNiese ?? row.section}},
    sourceId: row.sourceId, sourceIds: row.sourceIds, sourcePath: row.sourceFile, order: index,
    ...(isProem ? {sourceDivision: 'proem', division: 'proem'} : {}),
    ...(row.emptySource ? {emptySource: row.emptySource} : {}),
    ...(row.breakBefore ? {breakBefore: true, breakReason: sourceBreakReason(row)} : {}),
    ...grouping,
  };
  check('CompleteSourceRecord', record, expectedComplete, context);
  for (const [key, expected] of Object.entries({
    id: witnessRecordId(row), work: 'antiquities', book: row.book,
    section: row.section, language: 'Latin', edition: 'Bamberg Msc. Class. 78',
    citationScheme: 'niese', citationLabel: row.citationLabel, text: row.text,
    sourceId: row.sourceId, order: index, url: row.url,
  })) check(`SourceRecord_${key}`, record[key], expected, context);
  check('RecordSourceIds', record.sourceIds || [record.sourceId], row.sourceIds, context);
  check('RecordPhraseBreaks', record.phraseBreaks || [], row.phraseBreaks, context);
  check('RecordBreakBefore', Boolean(record.breakBefore), Boolean(row.breakBefore), context);
  const editorial = row.inlineMarks.filter(mark => ['add', 'del', 'unclear'].includes(mark.kind))
    .map(({kind, start, end, text}) => ({kind, start, end, text}));
  check('OriginalEditorialCharactersAndOffsets', (record.editorialMarks || []).map(({kind, start, end, text}) => ({kind, start, end, text})), editorial, context);
  check('IndependentTokenizersAgree', independentTokens(record.text, row.teiGaps.map(gap => gap.offset)), row.tokens, context);
  check('ActualReaderLinkForEveryCitation', readerURL(record, 'https://latinjosephus.github.io/'),
    `https://latinjosephus.github.io${row.url}`, context);
  assert.ok(!/undefined|NaN/.test(passageDivisionLabel([record])), 'A search result must have a valid division label.');
  assertions++; counts.ValidPassageLabels = (counts.ValidPassageLabels || 0) + 1;
}

function sourceBreakReason(row) {
  if (row.book === 1 && row.section === 27) return 'Book I narrative begins after the separately transmitted Proem.';
  if (row.book === 3 && row.section === 240) return 'The accepted source explicitly omits the Latin text at Antiquities III.240.';
  if (row.book === 3 && row.section === 241) return 'The preceding Latin Niese section III.240 is explicitly omitted.';
  if (row.book === 7 && row.section >= 69 && row.section <= 99)
    return `The accepted source explicitly omits the Latin text at Antiquities VII.${row.section}.`;
  if (row.book === 7 && row.section === 100) return 'The preceding Latin Niese sections VII.69–99 are explicitly omitted.';
  if (row.book === 9 && row.section === 110) return 'The accepted source marks a lacuna for Antiquities IX.51–109 before IX.110.';
  if (row.book === 10 && row.section === 108) return 'No Latin text occurs between the citation label for X.108 and the next Niese marker.';
  if (row.book === 10 && row.section === 109) return 'The preceding citation interval X.108 contains no Latin text in the accepted source.';
  if (row.book === 16 && row.section === 200) return 'Literal [...] notation occurs after XVI.188 and before XVI.200 in the accepted transcription.';
  if (row.book === 20 && row.section === 37) return 'The accepted XX.26 end anchor precedes an inherited missing-text annotation before XX.37.';
  assert.fail(`Unreviewed source division boundary ${row.citationLabel}`);
}

function inspectParagraphProjection(report, witnessFiles, records) {
  const paragraphs = witnessFiles.flatMap(file => file.paragraphs.map(paragraph => ({...paragraph, sourcePath: file.sourceFile})));
  const byKey = new Map(paragraphs.map(paragraph => [`${paragraph.sourcePath}#${paragraph.sourceId}`, paragraph]));
  const excluded = new Map(witnessFiles.flatMap(file => file.excluded.filter(item => item.sourceId)
    .map(item => [`${file.sourceFile}#${item.sourceId}:${item.rawStart}:${item.rawEnd}`, item])));
  check('ProjectionParagraphSet', report.paragraphs.map(p => `${p.sourcePath}#${p.sourceId}`).sort(), [...byKey.keys()].sort());
  const bySection = new Map(records.map(record => [record.section, record]));
  const byRecordId = new Map(records.map(record => [record.id, record]));
  for (const paragraph of report.paragraphs) {
    const key = `${paragraph.sourcePath}#${paragraph.sourceId}`, original = byKey.get(key);
    const originalPoints = Array.from(original.rawText);
    check('ProjectionOriginalParagraphFingerprint', paragraph.rawTextSha256, original.rawTextSha256, {key});
    check('ProjectionOriginalParagraphLength', paragraph.rawTextCharacters, originalPoints.length, {key});
    let cursor = 0;
    const reconstructed = [];
    for (const part of paragraph.segments) {
      check('ProjectionSegmentContiguity', part.sourceTextStart, cursor, {key});
      assert.ok(Number.isInteger(part.sourceTextEnd) && part.sourceTextEnd > cursor && part.sourceTextEnd <= originalPoints.length);
      const sourceText = originalPoints.slice(cursor, part.sourceTextEnd).join('');
      if (part.kind === 'source-text') {
        const record = part.recordId ? byRecordId.get(part.recordId) : bySection.get(part.section), row = sourceRows.get(record?.id);
        assert.ok(record && row, 'A source segment must identify a current Niese section.');
        const value = Array.from(record.text).slice(part.recordTextStart, part.recordTextEnd).join('');
        check('ProjectionMatchesOriginalSourceSlice', value, sourceText, {key, section: part.section});
        check('ProjectionSourceSliceFingerprint', part.textSha256, hash(sourceText), {key, section: part.section});
        // Verify source identity and offsets against independently constructed
        // minidom spans, allowing equivalent partitions of consecutive text.
        let point = cursor;
        while (point < part.sourceTextEnd) {
          const span = row.sourceSpans.find(span => span.kind === 'text' && span.sourceId === paragraph.sourceId
            && span.rawStart <= point && point < span.rawEnd);
          assert.ok(span && row.sourceFile === paragraph.sourcePath, 'Audit source span belongs to its independently established Niese unit.');
          const displayPosition = Array.from(row.text.slice(0, span.start)).length + point - span.rawStart;
          check('ProjectionIndependentSourcePosition', part.recordTextStart + point - cursor, displayPosition, {key, section: part.section});
          point = Math.min(part.sourceTextEnd, span.rawEnd);
        }
        reconstructed.push(value);
      } else {
        check('ProjectionExcludedSourceText', part.text, sourceText, {key});
        if (part.kind === 'trimmed-edge-whitespace') assert.ok(/^\s*$/u.test(sourceText));
        else {
          const omission = excluded.get(`${key}:${cursor}:${part.sourceTextEnd}`);
          assert.ok(omission, 'An excluded non-whitespace span must be an independently observed label or note.');
          check('ProjectionExcludedKind', part.kind, omission.kind === 'num' ? 'excluded-label'
            : omission.kind === 'omission-notice' ? 'excluded-omission-notice'
              : omission.kind === 'chapter-annotation-before-first-registered-interval' ? 'excluded-chapter-annotation'
                : omission.kind === 'book-subscription' ? 'excluded-book-subscription'
                  : omission.kind === 'source-gap-notation' ? 'excluded-source-gap-notation'
                    : omission.kind === 'lacuna-notice' ? 'excluded-lacuna-notice' : 'excluded-note', {key});
          const expectedAttributes = Object.fromEntries(Object.entries(omission.attributes).map(([name, value]) =>
            [report.scope.book >= 11 && name === 'xml:id' ? '{http://www.w3.org/XML/1998/namespace}id' : name, value]));
          check('ProjectionExcludedAttributes', part.sourceAttributes, expectedAttributes, {key});
        }
        reconstructed.push(part.text);
      }
      cursor = part.sourceTextEnd;
    }
    check('ProjectionCompleteSourceCoverage', cursor, originalPoints.length, {key});
    check('ProjectionExactSourceRestoration', reconstructed.join(''), original.rawText, {key});
    if (report.scope.book >= 6) {
      const expectedMarkers = records.flatMap(record => sourceRows.get(record.id).structuralMarkers
        .filter(marker => marker.sourceId === paragraph.sourceId)
        .map(marker => ({kind: report.scope.book <= 10 && marker.kind === 'milestone' ? 'image-milestone' : marker.kind,
          sourceTextOffset: marker.rawOffset, sourceAttributes: Object.fromEntries(Object.entries(marker.attributes)
            .map(([name, value]) => [report.scope.book >= 11 && name === 'xml:id' ? '{http://www.w3.org/XML/1998/namespace}id' : name, value])),
          section: record.section, recordTextOffsetUTF16: marker.offset, ...(report.scope.book >= 11 ? {recordId: record.id} : {})})));
      for (const marker of witnessFiles.flatMap(file => file.unassignedStructuralMarkers || []).filter(marker => marker.sourceId === paragraph.sourceId)) {
        expectedMarkers.push({kind: marker.kind, sourceTextOffset: marker.rawOffset, sourceAttributes: marker.attributes,
          section: undefined, recordTextOffsetUTF16: undefined, recordId: undefined});
        const reported = paragraph.structuralMarkers.filter(item => item.kind === marker.kind
          && item.sourceTextOffset === marker.rawOffset && !item.recordId);
        check('ExcludedIntervalStructuralMarkerPath', reported.map(item => item.sourceXPath), [marker.sourceXPath], {key});
      }
      const actualMarkers = paragraph.structuralMarkers.map(({kind, sourceTextOffset, sourceAttributes, section, recordTextOffsetUTF16, recordId}) =>
        ({kind, sourceTextOffset, sourceAttributes, section, recordTextOffsetUTF16, ...(report.scope.book >= 11 ? {recordId} : {})}));
      const sortMarkers = values => values.sort((a, b) => a.sourceTextOffset - b.sourceTextOffset || String(a.section).localeCompare(String(b.section))
        || a.kind.localeCompare(b.kind) || JSON.stringify(a.sourceAttributes).localeCompare(JSON.stringify(b.sourceAttributes)));
      check('IndependentStructuralMarkerEvidence', sortMarkers(actualMarkers), sortMarkers(expectedMarkers), {key});
    }
  }
  const missing = witnessFiles.flatMap(file => (file.missingNieseRanges || []).flatMap(([start, end]) =>
    Array.from({length: end - start + 1}, (_, index) => start + index)));
  check('DeclaredMissingSourceSections', report.coverage.missingSections, missing, {book: report.scope.book});
  const primaryNumbers = records.map(record => sourceRows.get(record.id)).filter(row => !row.sourcePassage).map(row => row.section);
  check('SourceOrderConsecutiveness', report.coverage.sourceOrderIsConsecutive, primaryNumbers.every((number, index) => index === 0 || number === primaryNumbers[index - 1] + 1));
  const empty = records.filter(record => !sourceRows.get(record.id).text).map(record => record.section);
  check('DeclaredEmptySourceSections', report.coverage.allowedEmptySections, empty);
  if (report.scope.book >= 6 && report.scope.book <= 10) {
    check('DeclaredTEIOmissions', report.coverage.omittedSections,
      records.filter(record => sourceRows.get(record.id).teiGaps.length).map(record => record.section));
    check('DeclaredEmptyIntervals', report.coverage.emptySourceIntervals,
      records.filter(record => sourceRows.get(record.id).emptySource).map(record => record.section));
    const sourceNotices = witnessFiles.flatMap(file => file.excluded.filter(item => item.kind === 'lacuna-notice'));
    const reportedNotices = report.documentReports.flatMap(document => document.excluded.filter(item => item.kind === 'lacuna-notice'));
    check('IndependentLacunaNotices', reportedNotices.map(item => ({sourceId: item.sourceId, text: item.text, attributes: item.sourceAttributes})),
      sourceNotices.map(item => ({sourceId: item.sourceId, text: item.text, attributes: Object.fromEntries(Object.entries(item.attributes)
        .map(([name, value]) => [name === 'xml:id' ? '{http://www.w3.org/XML/1998/namespace}id' : name, value]))})));
  }
  if (report.scope.book >= 11) {
    const expectedRows = records.map(record => sourceRows.get(record.id));
    const expectedPassages = expectedRows.filter(row => row.sourcePassage);
    const available = new Set(expectedRows.filter(row => !row.sourcePassage).map(row => row.citationUnitId));
    check('RegisteredPhysicalSourceOrder', records.map(record => record.section), witnessFiles.flatMap(file => file.sourceOrder));
    check('RegisteredPhysicalOrderPreserved', report.coverage.physicalSourceOrderPreserved, true);
    check('RegistryUnavailableSections', report.coverage.unavailableSections, missing);
    check('RegistryUnavailableNotices', report.coverage.unavailableIdentities, witnessFiles.flatMap(file => file.unavailableLatinIdentities));
    check('RegisteredCanonicalSections', report.coverage.canonicalSections, available.size);
    check('RegisteredPrimarySpans', report.coverage.primarySourceSpans, expectedRows.length - expectedPassages.length);
    check('RegisteredInterpolationSpans', report.coverage.interpolatedSourcePassages, expectedPassages.length);
    check('RegisteredLogicalUnits', report.coverage.citationUnits, available.size + expectedPassages.length);
    check('RegisteredSourceDiscontinuityInventory', records.filter(record => record.breakBefore).map(record => record.section),
      report.scope.book === 16 ? [200] : report.scope.book === 20 ? [37] : []);
    if (report.scope.book >= 16) {
      check('IndependentRegisteredSourceBoundaryEvidence', records.filter(record => record.sourceBoundaryEvidence)
        .map(record => record.sourceBoundaryEvidence), witnessFiles.flatMap(file => file.explicitSourceBoundaries));
      check('IndependentRegisteredBoundaryReport', report.coverage.explicitSourceBoundaries,
        witnessFiles.flatMap(file => file.explicitSourceBoundaries));
      check('IndependentSourceGapExclusions', report.excluded.filter(item =>
        ['excluded-source-gap-notation', 'excluded-lacuna-notice'].includes(item.kind)),
      witnessFiles.flatMap(file => file.sourceGapExclusions));
      check('IndependentRegisteredTokenBoundaryEvidence', report.coverage.registeredTokenBoundaryEvidence,
        witnessFiles.flatMap(file => file.registeredTokenBoundaryEvidence));
    }
    check('RegisteredTEIGapCount', report.counts.sourceGapMarkers, expectedRows.reduce((sum, row) => sum + row.teiGaps.length, 0));
    check('RegisteredNarrativeParagraphCount', report.counts.narrativeParagraphs ?? report.counts.numberedParagraphs, paragraphs.length);
    check('IdentityRegistryPath', report.identityRegistry.path, witnessFiles[0].identityRegistry.path);
    check('IdentityRegistryFingerprint', report.identityRegistry.sha256, witnessFiles[0].identityRegistry.sha256);
  }

}


function verifyRegisteredCases(engine, oracle, rows) {
  const book = rows[0].book;
  function verifySeam(leftSection, rightSection, blocked, category) {
    const left = rows.find(row => row.section === leftSection), right = rows.find(row => row.section === rightSection);
    const leftId = witnessRecordId(left), rightId = witnessRecordId(right);
    check(`${category}PhysicalOrder`, oracle.byId.get(rightId).index, oracle.byId.get(leftId).index + 1);
    const ast = phrase([...left.tokens.slice(-2), ...right.tokens.slice(0, 2)].map(token => token.term));
    const matches = oracle.evaluate(ast, 'book', false);
    const ownSeam = [...matches.values()].flatMap(hits => [...hits]).some(hit => {
      const spans = JSON.parse(hit);
      return spans.length === 2 && spans[0][0] === leftId && spans[1][0] === rightId;
    });
    check(`${category}SourceAdjacency`, ownSeam, !blocked, {book, leftSection, rightSection});
    for (const scope of ['section', 'book']) for (const fold of [false, true])
      verify(engine, oracle, ast, {scope, fold}, category);
    const boolean = and(leaf(left.tokens.at(-1).term), leaf(right.tokens[0].term));
    check(`${category}BookBooleanSurvives`, oracle.evaluate(boolean, 'book', false).has(identity(oracle.records[0])), true);
    for (const fold of [false, true]) verify(engine, oracle, boolean, {scope: 'book', fold}, `${category}Boolean`);
  }
  if ([11, 16].includes(rows[0].book)) {
    const units = new Map();
    for (const row of rows.filter(row => !row.sourcePassage)) {
      if (!units.has(row.citationUnitId)) units.set(row.citationUnitId, []);
      units.get(row.citationUnitId).push(row);
    }
    const split = [...units.entries()].filter(([, parts]) => parts.length > 1);
    check('RegisteredFragmentedIdentitySet', split.map(([, parts]) => parts[0].section).sort((a, b) => a - b),
      rows[0].book === 11 ? [72, 312, 326, 342] : [294, 295, 351]);
    for (const [key, parts] of split) {
      const distinctive = parts.map(row => {
        const elsewhere = new Set(parts.filter(other => other !== row).flatMap(other => other.tokens.map(token => token.term)));
        return row.tokens.find(token => token.term.length > 2 && !elsewhere.has(token.term))?.term;
      });
      assert.ok(distinctive.every(Boolean), 'Every accepted displaced portion has independent distinctive wording.');
      const conjunction = and(leaf(distinctive[0]), leaf(distinctive[1]));
      const exclusion = and(leaf(distinctive[0]), not(leaf(distinctive[1])));
      check('DisplacedPortionsShareBooleanIdentity', oracle.evaluate(conjunction, 'section', false).has(key), true, {key});
      check('DisplacedPortionsShareNegationScope', oracle.evaluate(exclusion, 'section', false).has(key), false, {key});
      for (const ast of [conjunction, exclusion]) for (const fold of [false, true])
        verify(engine, oracle, ast, {scope: 'section', fold}, 'AcceptedFragmentBoolean');
      for (let index = 0; index < parts.length - 1; index++) {
        const left = parts[index], right = parts[index + 1];
        const leftId = witnessRecordId(left), rightId = witnessRecordId(right);
        const ast = phrase([left.tokens.at(-1).term, right.tokens[0].term]);
        const matches = oracle.evaluate(ast, 'section', false);
        const evidence = [...(matches.get(key) || [])].some(hit => {
          const spans = JSON.parse(hit);
          return spans.length === 2 && spans[0][0] === leftId && spans[1][0] === rightId;
        });
        const adjacent = oracle.byId.get(rightId).index === oracle.byId.get(leftId).index + 1;
        const blocked = right.breakBefore || left.phraseBreaks.some(offset => offset > left.tokens.at(-1).start)
          || right.phraseBreaks.some(offset => offset <= right.tokens[0].start);
        check('AcceptedFragmentPhysicalPhraseAdjacency', evidence, adjacent && !blocked, {key, leftId, rightId});
        for (const scope of ['section', 'book']) for (const fold of [false, true])
          verify(engine, oracle, ast, {scope, fold}, 'AcceptedFragmentPhrase');
      }
    }
  }
  if (rows[0].book === 11) {
    const interpolations = rows.filter(row => row.sourcePassage);
    check('AcceptedInterpolationIdentities', interpolations.map(row => row.section), ['BJ.IV.105a', 'BJ.IV.105b']);
    for (const row of interpolations) {
      check('InterpolationHasIndependentCitationIdentity', row.citationUnitId === `${collectionId}-11-${row.sourcePassage.association}`, false);
      check('InterpolationIsNotAntiquitiesIdentity', row.sourcePassage.AntiquitiesIdentity, false);
      const ast = phrase(row.tokens.slice(0, 3).map(token => token.term));
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, ast, {scope, fold}, 'AcceptedInterpolationPhrase');
    }
  }
  if (rows[0].book === 12) {
    const last = rows.at(-1);
    check('ExplicitNarrativeEndExcludesSubscription', last.text.endsWith('defunctus est.'), true);
    check('SubscriptionWordsExcludedFromLastCitation', /Flauii|iosepp|LIBER|EXPLICIT/u.test(last.text), false);
    const terminal = last.structuralMarkers.filter(marker => marker.kind === 'milestone' && marker.attributes.unit === 'niese-end');
    check('ExplicitNarrativeEndAtFinalTextOffset', terminal.map(marker => marker.offset), [last.text.length]);
    const ast = phrase(['est', 'Flauii']);
    for (const scope of ['section', 'book']) for (const fold of [false, true])
      verify(engine, oracle, ast, {scope, fold}, 'NarrativeEndSubscriptionExcluded');
  }
  if (book === 16 || book === 20) {
    verifySeam(book === 16 ? 188 : 26, book === 16 ? 200 : 37, true, 'RegisteredSourceDiscontinuity');
    const closures = rows.flatMap(row => row.structuralMarkers.filter(marker =>
      marker.attributes.unit === 'niese-range-end' || marker.attributes['xml:id'] === 'niese-latin-book20-end26')
      .map(marker => ({section: row.section, sourceId: marker.sourceId, sourceTextOffset: marker.rawOffset,
        offset: marker.offset, textLength: row.text.length, sourceIdOwnsText: row.sourceIds.includes(marker.sourceId)})));
    check('AcceptedRangeClosureInventory', closures, book === 16 ? [
      {section: 188, sourceId: 'latin-book16-num188', sourceTextOffset: 59, offset: 58, textLength: 58, sourceIdOwnsText: true},
      {section: 394, sourceId: 'latin-book16-num395', sourceTextOffset: 0, offset: 236, textLength: 236, sourceIdOwnsText: false},
    ] : [{section: 26, sourceId: 'latin-book20-num34', sourceTextOffset: 0, offset: 43, textLength: 43, sourceIdOwnsText: false}]);
  }
  const ordinarySkippedIdentities = {16: [[76, 78], [122, 124], [358, 360]], 18: [[215, 218]], 20: [[237, 239]]};
  for (const [left, right] of ordinarySkippedIdentities[book] || [])
    verifySeam(left, right, false, 'UnavailableIdentityDoesNotInventPhraseBreak');
  if (book === 17) {
    const left = rows.find(row => row.section === 41), right = rows.find(row => row.section === 42);
    check('AcceptedAdjacentLetterRunBoundary', [left.tokens.at(-1).term, right.tokens[0].term], ['eleuati', 'cum']);
    check('AcceptedAdjacentLetterRunRawOffsets', [left.sourceSpans.at(-1).rawEnd, right.sourceSpans[0].rawStart], [3308, 3308]);
    verifySeam(41, 42, false, 'RegisteredLetterRunBoundary');
    for (const fold of [false, true]) {
      verify(engine, oracle, leaf('eleuaticum'), {scope: 'section', fold}, 'RegisteredLetterRunDoesNotInventJoinedWord');
      check('RegisteredLetterRunJoinedWordAbsent', engine.search('eleuaticum', {scope: 'book', fold}).occurrences, 0);
    }
  }
  if (book === 16 || book === 20) {
    const row = rows.find(row => row.section === (book === 16 ? 170 : 263));
    if (book === 16) {
      check('XVISurvivingTEIGap', row.teiGaps.map(gap => ({sourceId: gap.sourceId, rawOffset: gap.rawOffset,
        offset: gap.offset, attributes: gap.attributes})),
      [{sourceId: 'latin-book16-num169', rawOffset: 434, offset: 154, attributes: {}}]);
    } else {
      check('XXSurvivingLiteralGap', row.literalGaps, [{kind: 'literal-dots', start: 78, end: 80, text: '..'}]);
      check('XXUnrestoredFragmentedWord', row.text.slice(72, 88), 'pro .n..e, etiam');
      check('XXInheritedEnglishAnnotationNotIndexed', rows.some(item => /\b(?:Niese|Blatt|largely|missing)\b/u.test(item.text)), false);
      check('AcceptedXXTerminalIdentity', rows.at(-1).section, 268);
    }
    const terms = book === 16 ? ['quo', 'nullo'] : ['n', 'e'];
    const phraseQuery = phrase(terms), boolean = and(leaf(terms[0]), leaf(terms[1]));
    check('NewInternalSourceGapBlocksPhrase', oracle.evaluate(phraseQuery, 'section', false).has(row.citationUnitId), false);
    check('NewInternalSourceGapKeepsWords', oracle.evaluate(boolean, 'section', false).has(row.citationUnitId), true);
    for (const ast of [phraseQuery, phrase([terms[0] + '*', terms[1] + '*']), boolean])
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, ast, {scope, fold}, 'NewInternalSourceGap');
  }
  for (const row of rows) for (const gap of row.teiGaps) {
    const left = row.tokens.find(token => token.end === gap.offset);
    const right = row.tokens.find(token => token.start === gap.offset);
    if (!left || !right) continue;
    check('ExplicitIntraWordGapSurvivingRuns', [row.book, row.section, left.term, right.term], [13, 393, 'res', 's']);
    const joined = leaf(left.term + right.term);
    check('ExplicitIntraWordGapDoesNotInventWord', oracle.evaluate(joined, 'section', false).has(row.citationUnitId), false);
    for (const ast of [joined, phrase([left.term, right.term]), phrase(['re*', right.term]), and(leaf(left.term), leaf(right.term))])
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, ast, {scope, fold}, 'AcceptedIntraWordGap');
  }
}

const fixtures = [
  ['"Historiam conscribere disponentibus"', phrase(['Historiam', 'conscribere', 'disponentibus'])],
  ['"In principio creauit deus"', phrase(['In', 'principio', 'creauit', 'deus'])],
  ['"noctem et aliud"', phrase(['noctem', 'et', 'aliud'])],
  ['"quem consparsa"', phrase(['quem', 'consparsa'])],
  ['"con perit"', phrase(['con', 'perit'])],
  ['"del em"', phrase(['del', 'em'])],
  ['"f s"', phrase(['f', 's'])],
  ['"se ba"', phrase(['se', 'ba'])],
  ['"ba apud"', phrase(['ba', 'apud'])],
  ['"Herculis fecit"', phrase(['Herculis', 'fecit'])],
  ['Ioseph*', leaf('Ioseph*')], ['sacerdot*', leaf('sacerdot*')],
  ['Moyses OR Moses', or(leaf('Moyses'), leaf('Moses'))],
  ['Iudae* OR Roman* AND sacerdot*', or(leaf('Iudae*'), and(leaf('Roman*'), leaf('sacerdot*')))],
  ['Ioseph* sacerdot* OR templ*', or(and(leaf('Ioseph*'), leaf('sacerdot*')), leaf('templ*'))],
  ['(Ioseph* OR sacerdot*) AND NOT templ*', and(or(leaf('Ioseph*'), leaf('sacerdot*')), not(leaf('templ*')))],
  ['NOT (Ioseph* OR NOT sacerdot*)', not(or(leaf('Ioseph*'), not(leaf('sacerdot*'))))],
  ['NOT NOT Iosephus', not(not(leaf('Iosephus')))],
  ['NOT zzzznonoccurrit', not(leaf('zzzznonoccurrit'))], ['NOT *', not(leaf('*'))],
  ['rex OR rex*', or(leaf('rex'), leaf('rex*'))],
  ['"nisi qu*"', phrase(['nisi', 'qu*'])],
  ['quem AND consparsa', and(leaf('quem'), leaf('consparsa'))],
  ['con perit', and(leaf('con'), leaf('perit'))],
  ['"efficere Tunc"', phrase(['efficere', 'Tunc'])],
  ['"interfecit Dum"', phrase(['interfecit', 'Dum'])],
  ['"regu riter"', phrase(['regu', 'riter'])],
  ['"sepe lisset"', phrase(['sepe', 'lisset'])],
  ['"Huc ergo causa delectationis"', phrase(['Huc', 'ergo', 'causa', 'delectationis'])],
  ['"Nam uerba uesaniae"', phrase(['Nam', 'uerba', 'uesaniae'])],
  ['Omitted OR Bamberg OR Blatt', or(or(leaf('Omitted'), leaf('Bamberg')), leaf('Blatt'))],
];

async function main() {
  assert.ok(explicitReaderSHA || acceptedReaders.has(observedReaderSHA), 'Unreviewed reader fingerprint.');
  check('ReviewedReaderBaseline', observedReaderSHA, readerSHA);
  preserve(witnessPath);
  check('StandaloneWitnessMatchesEmbeddedFingerprint', readFileSync(witnessPath, 'utf8'), pythonWitness);
  const catalogPath = preserve(resolve(base, 'catalog.json'));
  const corpusPath = preserve(resolve(base, 'data', collectionId, 'corpus.json'));
  const catalog = readJSON(catalogPath), corpus = readJSON(corpusPath);
  const config = catalog.collections.find(collection => collection.id === collectionId);
  assert.ok(config, 'The catalog must include Antiquities I–XX.');
  const selectedEntries = catalog.books.filter(entry => entry.collectionId === collectionId);
  check('CatalogBookOrder', selectedEntries.map(entry => entry.number), Array.from({length: 20}, (_, index) => index + 1));
  check('CatalogCitationScheme', config.citationScheme, 'niese');
  for (const path of [readerPath, resolve(base, 'engine.mjs'), resolve(base, 'collection.mjs'),
    resolve(base, 'ui-utils.mjs'), resolve(base, 'vendor/lunr.cjs'), fileURLToPath(import.meta.url)]) preserve(path);
  const witness = JSON.parse(execFileSync(process.env.PYTHON || 'python3', ['-c', pythonWitness, root], {encoding: 'utf8', maxBuffer: 80 * 1024 * 1024}));
  check('IndependentCoverage', witness.totals, {books: 20, sourceFiles: 21, sections: 7283, wordTokens: 265023});
  check('CombinedRecordCount', corpus.length, 7283);
  sourceRows = new Map(witness.rows.map(row => [witnessRecordId(row), row]));
  check('UniqueWitnessRecordIds', sourceRows.size, witness.rows.length);
  for (let index = 0; index < corpus.length; index++) compareSourceRecord(corpus[index], witness.rows[index], index);
  const combinedReportPath = preserve(resolve(base, config.extractionReportPath));
  const combinedReport = readJSON(combinedReportPath);
  const states = [];
  let adjacentPairs = 0, ordinaryPairs = 0, emptyPairs = 0, proemPairs = 0, lacunaPairs = 0, literalBoundaryPairs = 0, registeredSourcePairs = 0, barrierChecks = 0, emptyIntervalChecks = 0;

  for (const entry of selectedEntries) {
    const bookStarted = performance.now();
    const bundlePath = preserve(resolve(base, entry.path)), shardPath = preserve(resolve(base, entry.corpusPath));
    const sourcePath = preserve(resolve(root, `assets/xml/antiquities/Latin/book-${String(entry.number).padStart(2, '0')}.xml`));
    const additionalSources = entry.number === 1 ? [preserve(resolve(root, 'assets/xml/antiquities/Latin/preface.xml'))]
      : entry.number >= 11 ? [preserve(resolve(root, `assets/xml/antiquities/niese/book-${String(entry.number).padStart(2, '0')}.json`))] : [];
    const reportPath = preserve(resolve(base, 'data', collectionId, `book-${String(entry.number).padStart(2, '0')}.extraction-report.json`));
    const bundle = readJSON(bundlePath), shard = readJSON(shardPath);
    const expectedRows = witness.rows.filter(row => row.book === entry.number);
    const records = corpus.filter(record => record.book === entry.number);
    inspectParagraphProjection(readJSON(reportPath), witness.files.filter(file => file.book === entry.number), records);
    check('ShardMatchesCombinedCorpus', shard, records, {book: entry.number});
    check('BundleMatchesShard', bundle.records, records.map(record => ({...record, breakBefore: Boolean(record.breakBefore)})), {book: entry.number});
    check('CatalogBundleHash', entry.sha256, digest(bundlePath), {book: entry.number});
    check('CatalogCorpusHash', entry.corpusSHA256, digest(shardPath), {book: entry.number});
    check('AllIndexedTokenOffsets', bundle.tokens, expectedRows.map(row => row.tokens), {book: entry.number});
    check('ExpectedTokenCount', bundle.stats.tokens, expectedRows.reduce((sum, row) => sum + row.tokens.length, 0), {book: entry.number});
    const oracle = makeOracle(records, expectedRows.map(row => row.tokens)), engine = createEngine(bundle, lunr);
    const wordsToTest = smoke ? oracle.vocabulary.filter((_, index) => index % Math.max(1, Math.floor(oracle.vocabulary.length / 12)) === 0) : oracle.vocabulary;
    for (const word of wordsToTest) for (const fold of [false, true])
      verify(engine, oracle, leaf(word), {scope: 'section', fold}, 'ExhaustiveVocabulary');
    for (const [query, ast] of fixtures) for (const scope of ['section', 'book']) for (const fold of [false, true])
      verify(engine, oracle, ast, {scope, fold}, 'Fixture', query, !fold && scope === 'book');
    const sampledWords = oracle.vocabulary.filter(word => word.length >= 5).filter((_, index) => index % Math.max(1, Math.floor(oracle.vocabulary.length / (smoke ? 4 : 35))) === 0);
    const patterns = new Set(['*', '**', 'sacerdot*', '*ae', 'i*us', '*iud*', 'r*x', 'zzzznonoccurrit*']);
    for (const word of sampledWords) {
      patterns.add(word.slice(0, 3) + '*'); patterns.add('*' + word.slice(-3));
      patterns.add(word.slice(0, 2) + '*' + word.slice(-2)); patterns.add(word.slice(0, 2) + '**' + word.slice(2));
    }
    for (const pattern of patterns) for (const scope of ['section', 'book']) for (const fold of [false, true])
      verify(engine, oracle, leaf(pattern), {scope, fold}, 'Wildcard');
    const unitIndices = smoke ? [0, Math.floor(records.length / 2), records.length - 1] : records.map((_, index) => index);
    for (const index of unitIndices) {
      const ts = oracle.tokenLists[index];
      if (!ts.length) {
        const row = expectedRows[index];
        check('ExplicitEmptySectionEvidence', Boolean(row.teiGaps.length || row.emptySource), true,
          {book: row.book, section: row.section});
        continue;
      }
      const start = Math.max(0, Math.floor(ts.length / 2) - 1);
      const ast = phrase(ts.slice(start, start + 3).map(token => token.term));
      for (const scope of ['section', 'book']) for (const fold of [false, true]) verify(engine, oracle, ast, {scope, fold}, 'WithinEveryNonemptyUnit');
    }
    const seamIndices = smoke ? [...new Set([0, 25, 49, 53, 67, 68, 98, 106, 107, 139, 177, 238, 239].filter(index => index < records.length - 1))] : records.slice(1).map((_, index) => index);
    for (const index of seamIndices) {
      adjacentPairs++;
      const leftTokens = oracle.tokenLists[index], rightTokens = oracle.tokenLists[index + 1];
      if (!leftTokens.length || !rightTokens.length) {
        emptyPairs++;
        check('EmptySectionMarksAnUnsearchablePhraseSeam',
          Boolean(!leftTokens.length && (expectedRows[index].teiGaps.length || expectedRows[index].emptySource)
            || !rightTokens.length && (expectedRows[index + 1].teiGaps.length || expectedRows[index + 1].emptySource)), true,
          {book: entry.number, left: records[index].section, right: records[index + 1].section});
        continue;
      }
      const ast = phrase([...leftTokens.slice(-1), ...rightTokens.slice(0, 1)].map(token => token.term));
      const matching = oracle.evaluate(ast, 'book', false);
      const ownSeam = [...matching.values()].flatMap(hits => [...hits]).some(hit => {
        const spans = JSON.parse(hit); return spans.length === 2 && spans[0][0] === records[index].id && spans[1][0] === records[index + 1].id;
      });
      const leftSource = expectedRows[index], rightSource = expectedRows[index + 1];
      const blocked = rightSource.breakBefore || leftSource.phraseBreaks.some(offset => offset > leftTokens.at(-1).start)
        || rightSource.phraseBreaks.some(offset => offset <= rightTokens[0].start);
      if (entry.number === 1 && records[index].section === 26) proemPairs++;
      else if (entry.number === 9 && records[index].section === 50) lacunaPairs++;
      else if (rightSource.sourceBoundaryEvidence) registeredSourcePairs++;
      else if (blocked) literalBoundaryPairs++;
      else ordinaryPairs++;
      check('BoundaryOracleExpectation', ownSeam, !blocked, {book: entry.number, left: records[index].citationLabel, right: records[index + 1].citationLabel});
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, ast, {scope, fold}, blocked ? 'SourceBoundaryBlocked' : 'EveryAdjacentUnitBoundary');
      const contextPhrase = phrase([...leftTokens.slice(-2), ...rightTokens.slice(0, 2)].map(token => token.term));
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, contextPhrase, {scope, fold}, 'ExtendedBoundaryContextPhrase');
    }
    for (const row of expectedRows.filter(row => row.emptySource)) {
      emptyIntervalChecks++;
      const index = records.findIndex(record => record.section === row.section);
      const left = oracle.tokenLists[index - 1].slice(-2), right = oracle.tokenLists[index + 1].slice(0, 2);
      const ast = phrase([...left, ...right].map(token => token.term));
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, ast, {scope, fold}, 'EmptySourceIntervalBlocksPhrase');
      const boolean = and(leaf(left.at(-1).term), leaf(right[0].term));
      check('BooleanAcrossEmptyIntervalAllowed', oracle.evaluate(boolean, 'book', false).has(identity(records[index])), true);
      verify(engine, oracle, boolean, {scope: 'book', fold: false}, 'BooleanAcrossEmptyIntervalAllowed');
    }
    for (const row of expectedRows) for (const marker of [...row.literalGaps, ...row.teiGaps.map(gap => ({start: gap.offset, end: gap.offset, text: ''}))]) {
      barrierChecks++;
      const recordId = witnessRecordId(row);
      const recordIndex = records.findIndex(record => record.id === recordId);
      const split = oracle.all.findIndex(token => token.recordIndex > recordIndex || (token.recordIndex === recordIndex && token.start >= marker.start));
      assert.ok(split >= 1 && split < oracle.all.length, 'Each accepted gap has surviving words on both sides within its book.');
      const left = oracle.all.slice(Math.max(0, split - 2), split), right = oracle.all.slice(split, split + 2);
      assert.notEqual(left.at(-1).segment, right[0].segment, 'Independent gap segmentation must break adjacency.');
      const ast = phrase([...left, ...right].map(token => token.term));
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, ast, {scope, fold}, 'EverySourceGapBarrierBlocked');
      const boolean = and(leaf(left.at(-1).term), leaf(right[0].term));
      const scope = left.at(-1).recordId === right[0].recordId ? 'section' : 'book';
      const key = scope === 'section' ? sourceUnit(records[recordIndex]) : identity(records[recordIndex]);
      check('BooleanAcrossGapAllowed', oracle.evaluate(boolean, scope, false).has(key), true, {book: row.book, section: row.section, marker});
      verify(engine, oracle, boolean, {scope, fold: false}, 'BooleanAcrossGapAllowed');
    }
    verifyRegisteredCases(engine, oracle, expectedRows);
    states.push({entry, bundlePath, shardPath, sourcePath, reportPath, additionalSources, oracle, engine,
      vocabularyQueries: wordsToTest.length * 2, withinBookBoundaries: seamIndices.length});
    console.log(JSON.stringify({phase: 'Antiquities book complete', book: entry.number, vocabulary: oracle.vocabulary.length,
      queriesSoFar: totalQueries, seconds: Math.round((performance.now() - bookStarted) / 100) / 10}));
  }
  check('EverySourceGapExercised', barrierChecks, 63);
  check('EveryEmptySourceIntervalExercised', emptyIntervalChecks, 1);
  check('EveryAcceptedIntraWordGapExercised', counts.ExplicitIntraWordGapSurvivingRuns || 0, 1);
  if (!smoke) {
    check('AllAdjacentPairsExercised', adjacentPairs, 7263);
    check('AllOrdinaryPairsExercised', ordinaryPairs, 7220);
    check('AllEmptyCitationEdgesExercised', emptyPairs, 36);
    check('SeparateProemNarrativeEdgeExercised', proemPairs, 1);
    check('DeclaredLacunaEdgeExercised', lacunaPairs, 1);
    check('LiteralBoundaryEdgesExercised', literalBoundaryPairs, 3);
    check('RegisteredSourceDiscontinuityEdgesExercised', registeredSourcePairs, 2);
  }

  const bundleEntries = new Map(catalog.books.map(entry => [new URL(entry.path, 'https://qa.invalid/assets/search/').pathname, entry]));
  const fetchCounts = new Map();
  const fetchImpl = async url => {
    const entry = bundleEntries.get(new URL(url).pathname);
    assert.ok(entry, `Unexpected bundle request: ${url}`);
    fetchCounts.set(entry.id, (fetchCounts.get(entry.id) || 0) + 1);
    return new Response(readFileSync(preserve(resolve(base, entry.path))), {status: 200});
  };
  const collection = createCollection(catalog, lunr, {baseURL: 'https://qa.invalid/assets/search/', fetchImpl});
  const allEntryRecords = new Map(catalog.books.map(entry => [entry.id, readJSON(preserve(resolve(base, entry.path))).records]));
  async function verifyCollection(ast, selected, scope, fold, category, query = print(ast), example = false) {
    totalQueries++; counts[`${category}Queries`] = (counts[`${category}Queries`] || 0) + 1;
    const selectedSet = new Set(selected), ordered = catalog.books.filter(entry => selectedSet.has(entry.id));
    const records = ordered.flatMap(entry => allEntryRecords.get(entry.id)), oracle = makeOracle(records);
    const expected = oracle.evaluate(ast, scope, fold), collections = [...new Set(ordered.map(entry => entry.collectionId))];
    const actual = await collection.search(query, {collections, books: selected, scope, fold});
    compareResults(actual, expected, oracle, {scope, fold, selectedBooks: selected}, category, query, example);
    check(`${category}SelectionOrder`, actual.selectedBooks, ordered.map(entry => entry.id));
    check(`${category}UniqueRecordIdentity`, new Set(actual.records.map(record => record.id)).size, records.length);
    return {actual, expected};
  }
  for (const selected of selectedEntries.map(entry => [entry.id]).concat([selectedEntries.map(entry => entry.id).reverse()]))
    for (const [query, ast] of fixtures.filter((_, index) => [0, 1, 10, 11, 15, 18, 19, 20].includes(index)))
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        await verifyCollection(ast, selected, scope, fold, 'SelectedAntiquitiesCollection', query, selected.length === 20 && !fold);
  for (let index = 0; index < states.length - 1; index++) {
    const junction = phrase([...states[index].oracle.all.slice(-3), ...states[index + 1].oracle.all.slice(0, 3)].map(token => token.term));
    for (const scope of ['section', 'book']) for (const fold of [false, true]) {
      const checked = await verifyCollection(junction, [states[index].entry.id, states[index + 1].entry.id], scope, fold, 'CrossBookPhraseBlocked');
      check('CrossBookPhraseAbsent', checked.expected.size, 0);
    }
  }
  const oldCollections = ['bellum-latin-cardwell', 'deh-latin-ussani', 'contra-apionem-latin-boysen'];
  check('PriorCollectionsRetained', oldCollections.map(id => catalog.books.filter(entry => entry.collectionId === id).length), [7, 5, 2]);
  const mixed = catalog.books.map(entry => entry.id);
  for (const ast of [leaf('sacerdot*'), not(leaf('zzzznonoccurrit'))])
    for (const scope of ['section', 'book']) for (const fold of [false, true])
      await verifyCollection(ast, mixed, scope, fold, 'MixedFourWorkCollection', print(ast), !fold);
  for (const otherId of oldCollections) {
    const other = catalog.books.find(entry => entry.collectionId === otherId);
    const otherOracle = makeOracle(allEntryRecords.get(other.id)), antOracle = states[0].oracle;
    const antOnly = antOracle.vocabulary.find(word => word.length > 4 && !otherOracle.vocabulary.includes(word));
    const otherOnly = otherOracle.vocabulary.find(word => word.length > 4 && !antOracle.vocabulary.includes(word));
    assert.ok(antOnly && otherOnly);
    for (const scope of ['section', 'book']) {
      const checked = await verifyCollection(and(leaf(antOnly), leaf(otherOnly)), [selectedEntries[0].id, other.id], scope, false, 'CrossWorkBooleanIsolation');
      check('CrossWorkBooleanAbsent', checked.expected.size, 0, {antOnly, otherOnly, other: other.id});
    }
  }
  check('BundleFetchCaching', [...fetchCounts.entries()].sort(), catalog.books.map(entry => [entry.id, 1]).sort());
  for (const invalid of [{collections: [collectionId], books: [1]}, {collections: [collectionId], books: [catalog.books[0].id]},
    {collections: [collectionId], books: [`${collectionId}:21`]}]) {
    await assert.rejects(collection.search('sacerdot*', invalid));
    assertions++; counts.InvalidSelectionRejected = (counts.InvalidSelectionRejected || 0) + 1;
  }
  const failedLoad = createCollection(catalog, lunr, {baseURL: 'https://qa.invalid/assets/search/', fetchImpl: async url => {
    const entry = bundleEntries.get(new URL(url).pathname);
    return entry.id === selectedEntries.at(-1).id ? new Response('Unavailable', {status: 404})
      : new Response(readFileSync(resolve(base, entry.path)), {status: 200});
  }});
  await assert.rejects(failedLoad.search('sacerdot*', {collections: [collectionId], books: selectedEntries.map(entry => entry.id)}));
  assertions++; counts.MissingSelectedBookRejectsCompleteSearch = 1;
  for (const [path, sha256] of checkedFiles) check('InputUnchangedDuringQA', digest(path), sha256, {path: relative(root, path)});
  const report = {
    status: 'PASS', generatedAt: new Date().toISOString(), independentVerifier: 'bin/search/tests/antiquities-corpus-qa.mjs', readerBaseline,
    runtime: {node: process.versions.node, ...witness.runtime},
    source: {books: 20, sourceFiles: 21, sections: 7283, tokens: 265023,
      uniqueLiteralVocabulary: new Set(states.flatMap(state => state.oracle.vocabulary)).size},
    sources: witness.files.map(file => ({path: file.sourceFile, sha256: file.sha256, sections: file.sections, tokens: file.wordTokens, stableIds: file.stableIds})),
    verifiedFiles: {corpus: evidence(corpusPath), catalog: evidence(catalogPath), engine: evidence(resolve(base, 'engine.mjs')),
      collection: evidence(resolve(base, 'collection.mjs')), lunr: evidence(resolve(base, 'vendor/lunr.cjs')),
      verifier: evidence(fileURLToPath(import.meta.url)), witness: evidence(witnessPath),
      extractionReport: evidence(combinedReportPath), originalReader: evidence(readerPath), uiUtils: evidence(resolve(base, 'ui-utils.mjs')),
      books: states.map(state => ({book: state.entry.number, bundle: evidence(state.bundlePath), corpus: evidence(state.shardPath),
        source: evidence(state.sourcePath), additionalSources: state.additionalSources.map(evidence), extractionReport: evidence(state.reportPath)}))},
    method: {source: 'Independent minidom text-node event stream over twenty-one SHA-pinned XML files and ten accepted Niese identity registries, without production extractor imports. The complete witness is embedded and checked against its standalone file.',
      tokens: 'Every Unicode-category token and UTF-16 offset is checked against each bundle; a separate JavaScript character scanner agrees on every physical source span, including zero-width TEI gaps within a character run.',
      queries: 'Independent AST/set Boolean logic, regular-expression globs, and sequential phrase scanning. Phrase barriers derive from witness source marks and explicit source-division boundaries.',
      vocabulary: 'Every distinct source token in every book queried in source-spelling and u/v–i/j-folded modes.',
      boundaries: 'Every within-book adjacent physical pair, all 27 literal source interruptions, all 36 TEI gaps, X.108 empty interval, IX missing 51–109, the Proem-to-narrative boundary, the two explicit registered source discontinuities, the XVII.41–42 letter-run seam, and every book junction checked. Displaced fragments share Boolean citation identity while phrases follow physical order. Uncertain sentence punctuation remains ordinarily joinable.',
      collection: 'All twenty Antiquities bundles, selected subsets and order, limited four-work integration queries, caching, invalid selection and unavailable-book rejection.'},
    boundaryCoverage: {withinBookPairs: adjacentPairs, ordinaryPairs, emptyCitationEdges: emptyPairs,
      proemNarrativeEdges: proemPairs, declaredLacunaEdges: lacunaPairs, literalBoundaryEdges: literalBoundaryPairs,
      registeredSourceDiscontinuityEdges: registeredSourcePairs, registeredLetterRunBoundaries: 1,
      literalGapClusters: 27, literalDots: 20, literalEllipses: 5, sourceMarkedDotSpans: 2, teiGaps: 36,
      emptySourceIntervals: emptyIntervalChecks, bookJunctions: 19},
    editorialCoverage: {add: 260, del: 77, unclear: 115, corr: 59, expan: 28, sourceNotesExcluded: 43,
      emptyCitations: witness.rows.filter(row => !row.text).map(row => row.citationLabel),
      missingSectionsByBook: Object.fromEntries(witness.files.filter(file => file.missingNieseRanges?.length).map(file => [String(file.book), file.missingNieseRanges.flatMap(([first, last]) => Array.from({length: last - first + 1}, (_, index) => first + index))])),
      unavailableLatinIdentities: witness.files.flatMap(file => (file.unavailableLatinIdentities || []).map(identity => ({book: file.book, ...identity}))),
      omissionNoticesExcluded: 6, lacunaNoticesExcluded: 2, sourceGapNotationsExcluded: 3, proemSections: 26, preservedNieseUnits: 7273,
      physicalSourceRecords: 7283, independentInterpolationPassages: 2,
      explicitSourceBoundaries: witness.files.flatMap(file => file.explicitSourceBoundaries || []),
      registeredTokenBoundaryEvidence: witness.files.flatMap(file => file.registeredTokenBoundaryEvidence || []),
      excludedSourceGapEvidence: witness.files.flatMap(file => file.sourceGapExclusions || []),
      taggedBookTrailersExcluded: witness.files.flatMap(file => file.excluded.filter(item => item.kind === 'trailer')
        .map(item => ({book: file.book, sourcePath: file.sourceFile, sourceXPath: item.sourceXPath, text: item.text}))),
      romanChapterLettersPolicy: 'Untagged or added Roman chapter letters within accepted narrative spans are retained exactly. Explicit num labels, notes, headings and trailers are excluded; no numeral is heuristically removed or reclassified.',
      endSubscriptionsExcluded: witness.files.flatMap(file => file.excluded.filter(item => item.kind === 'book-subscription')).map(item => ({sourceId: item.sourceId, text: item.text, attributes: item.attributes})),
      continuationSections: witness.rows.filter(row => row.sourceSpans.some(span => span.kind === 'separator')).map(row => row.citationLabel)},
    counts, totalQueries, assertions, failedAssertions: 0, examples,
    durationSeconds: Math.round((performance.now() - started) / 10) / 100,
    limitations: ['Automated Node/Python acceptance, not browser or visual acceptance.',
      'Reader URLs are verified with the actual UI URL helper; reader pages are not opened by this verifier.',
      'The accepted corrected project XML is preserved faithfully; this does not re-collate the text with manuscript images.',
      'Earlier collections receive limited mixed-work integration checks; their independent source-fidelity reports remain separately required.',
      'Literal source interruptions conservatively suppress phrase adjacency without assigning new scholarly meanings or missing-text extents.'], failures: [],
  };
  if (!smoke) writeFileSync(destination, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({status: smoke ? 'DEVELOPMENT_SMOKE_PASS' : 'PASS', source: report.source,
    totalQueries, assertions, failedAssertions: 0, durationSeconds: report.durationSeconds, publicationReportWritten: !smoke}));
}
if (!smoke) {
  mkdirSync(dirname(destination), {recursive: true});
  writeFileSync(destination, JSON.stringify({status: 'RUNNING', generatedAt: new Date().toISOString(), independentVerifier: 'bin/search/tests/antiquities-corpus-qa.mjs'}, null, 2) + '\n');
}
try {await main();}
catch (error) {
  if (!smoke) writeFileSync(destination, JSON.stringify({status: 'FAIL', generatedAt: new Date().toISOString(), assertions,
    totalQueries, failedAssertions: 1, error: {name: error.name, message: error.message, stack: error.stack}}, null, 2) + '\n');
  console.error(error.stack || error); process.exitCode = 1;
}
