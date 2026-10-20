/** Independent Antiquities I–V source, token, and query acceptance.
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
`;

// Distinct from production tokenizeText: character-by-character, used also for
// unchanged Bellum index records in the mixed-work collection checks.
function independentTokens(text) {
  const result = [];
  let offset = 0, start = null, value = '';
  const emit = () => {
    if (start !== null) result.push({term: normalize(value), start, end: offset});
    start = null; value = '';
  };
  for (const character of text) {
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
const spanKey = spans => JSON.stringify(spans.map(span => [span.recordId, span.start, span.end]));
function makeOracle(records, suppliedTokens) {
  const byId = new Map(records.map((record, index) => [record.id, {record, index}]));
  const tokenLists = suppliedTokens || records.map(record => independentTokens(record.text));
  const all = [];
  const segments = new Map();
  records.forEach((record, index) => {
    const key = identity(record);
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
      all.push({...token, foldedTerm: normalize(token.term, true), recordId: record.id, recordIndex: index, bookKey: key, segment});
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
  const keyOf = (record, scope) => scope === 'section' ? record.id : identity(record);
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
        add(scope === 'section' ? token.recordId : token.bookKey, [token]);
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
          || (scope === 'section' && token.recordId !== first.recordId)
          || !matchers[j](fold ? token.foldedTerm : token.term)) {accepted = false; break;}
      }
      if (!accepted) continue;
      const spans = [];
      for (const token of all.slice(i, i + patterns.length)) {
        if (spans.at(-1)?.recordId === token.recordId) spans.at(-1).end = token.end;
        else spans.push({recordId: token.recordId, start: token.start, end: token.end});
      }
      add(scope === 'section' ? first.recordId : first.bookKey, spans);
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
  const groupKey = group => scope === 'section' ? group.recordIds[0]
    : group.work ? identity({work: group.work, book: group.book, language: group.language, edition: group.edition})
      : identity(oracle.records[0]);
  const actualGroups = new Map(actual.hitGroups.map(group => [groupKey(group), group]));
  check(`${category}UnitIdentity`, [...actualGroups.keys()].sort(), [...expected.keys()].sort(), context);
  const allTouched = new Set();
  const rank = id => oracle.byId.get(id).index;
  for (const [key, hits] of expected) {
    const group = actualGroups.get(key);
    check(`${category}Evidence`, group.hits.map(hit => spanKey(hit.spans)).sort(), [...hits].sort(), {...context, unit: key});
    const ids = scope === 'section' ? [key] : [...new Set([...hits].flatMap(hit => JSON.parse(hit).map(span => span[0])))].sort((a, b) => rank(a) - rank(b));
    ids.forEach(id => allTouched.add(id));
    check(`${category}RecordIds`, group.recordIds, ids, {...context, unit: key});
    check(`${category}Sections`, group.sections, ids.map(id => oracle.byId.get(id).record.section), {...context, unit: key});
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
  const context = {book: row.book, section: row.section};
  const isProem = row.readerBook === 'preface';
  const attributesFor = mark => ({kind: mark.kind, start: mark.start, end: mark.end, text: mark.text,
    sourceTag: mark.kind, sourceAttributes: mark.attributes});
  const expectedComplete = {
    id: `${collectionId}-${row.book}-${row.section}`, work: 'antiquities', book: row.book,
    section: row.section, language: 'Latin', edition: 'Bamberg Msc. Class. 78',
    citationScheme: 'niese', citationLabel: row.citationLabel,
    citation: {book: ['I', 'II', 'III', 'IV', 'V'][row.book - 1], section: row.section, ...(isProem ? {proem: true} : {})},
    text: row.text, editorialMarks: row.inlineMarks.filter(mark => ['add', 'del'].includes(mark.kind)).map(attributesFor),
    sourceMarkup: row.inlineMarks.filter(mark => ['s', 'ref'].includes(mark.kind)).map(attributesFor),
    textGaps: [...row.literalGaps, ...row.teiGaps.map(gap => ({kind: 'tei-gap', start: gap.offset, end: gap.offset,
      text: '', sourceAttributes: gap.attributes}))],
    phraseBreaks: row.phraseBreaks, url: row.url,
    readerLink: {path: 'antiquities/', params: {book: row.readerBook, niese: row.section}},
    sourceId: row.sourceId, sourceIds: row.sourceIds, sourcePath: row.sourceFile, order: index,
    ...(isProem ? {sourceDivision: 'proem', division: 'proem'} : {}),
    ...(row.breakBefore ? {breakBefore: true, breakReason: row.book === 1
      ? 'Book I narrative begins after the separately transmitted Proem.'
      : row.section === 240 ? 'The accepted source explicitly omits the Latin text at Antiquities III.240.'
        : 'The preceding Latin Niese section III.240 is explicitly omitted.'} : {}),
  };
  check('CompleteSourceRecord', record, expectedComplete, context);
  for (const [key, expected] of Object.entries({
    id: `${collectionId}-${row.book}-${row.section}`, work: 'antiquities', book: row.book,
    section: row.section, language: 'Latin', edition: 'Bamberg Msc. Class. 78',
    citationScheme: 'niese', citationLabel: row.citationLabel, text: row.text,
    sourceId: row.sourceId, order: index, url: row.url,
  })) check(`SourceRecord_${key}`, record[key], expected, context);
  check('RecordSourceIds', record.sourceIds || [record.sourceId], row.sourceIds, context);
  check('RecordPhraseBreaks', record.phraseBreaks || [], row.phraseBreaks, context);
  check('RecordBreakBefore', Boolean(record.breakBefore), Boolean(row.breakBefore), context);
  const editorial = row.inlineMarks.filter(mark => ['add', 'del'].includes(mark.kind))
    .map(({kind, start, end, text}) => ({kind, start, end, text}));
  check('OriginalEditorialCharactersAndOffsets', (record.editorialMarks || []).map(({kind, start, end, text}) => ({kind, start, end, text})), editorial, context);
  check('IndependentTokenizersAgree', independentTokens(record.text), row.tokens, context);
  check('ActualReaderLinkForEveryCitation', readerURL(record, 'https://latinjosephus.github.io/'),
    `https://latinjosephus.github.io${row.url}`, context);
  assert.ok(!/undefined|NaN/.test(passageDivisionLabel([record])), 'A search result must have a valid division label.');
  assertions++; counts.ValidPassageLabels = (counts.ValidPassageLabels || 0) + 1;
}

function inspectParagraphProjection(report, witnessFiles, records) {
  const paragraphs = witnessFiles.flatMap(file => file.paragraphs.map(paragraph => ({...paragraph, sourcePath: file.sourceFile})));
  const byKey = new Map(paragraphs.map(paragraph => [`${paragraph.sourcePath}#${paragraph.sourceId}`, paragraph]));
  const excluded = new Map(witnessFiles.flatMap(file => file.excluded.filter(item => item.sourceId)
    .map(item => [`${file.sourceFile}#${item.sourceId}:${item.rawStart}:${item.rawEnd}`, item])));
  check('ProjectionParagraphSet', report.paragraphs.map(p => `${p.sourcePath}#${p.sourceId}`).sort(), [...byKey.keys()].sort());
  const bySection = new Map(records.map(record => [record.section, record]));
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
        const record = bySection.get(part.section), row = sourceRows.get(record?.id);
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
          check('ProjectionExcludedKind', part.kind, omission.kind === 'num' ? 'excluded-label' : 'excluded-note', {key});
          check('ProjectionExcludedAttributes', part.sourceAttributes, omission.attributes, {key});
        }
        reconstructed.push(part.text);
      }
      cursor = part.sourceTextEnd;
    }
    check('ProjectionCompleteSourceCoverage', cursor, originalPoints.length, {key});
    check('ProjectionExactSourceRestoration', reconstructed.join(''), original.rawText, {key});
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
  assert.ok(config, 'The catalog must include Antiquities I–V.');
  const selectedEntries = catalog.books.filter(entry => entry.collectionId === collectionId);
  check('CatalogBookOrder', selectedEntries.map(entry => entry.number), [1, 2, 3, 4, 5]);
  check('CatalogCitationScheme', config.citationScheme, 'niese');
  for (const path of [readerPath, resolve(base, 'engine.mjs'), resolve(base, 'collection.mjs'),
    resolve(base, 'ui-utils.mjs'), resolve(base, 'vendor/lunr.cjs'), fileURLToPath(import.meta.url)]) preserve(path);
  const witness = JSON.parse(execFileSync(process.env.PYTHON || 'python3', ['-c', pythonWitness, root], {encoding: 'utf8', maxBuffer: 80 * 1024 * 1024}));
  check('IndependentCoverage', witness.totals, {books: 5, sourceFiles: 6, sections: 1710, wordTokens: 67657});
  check('CombinedRecordCount', corpus.length, 1710);
  sourceRows = new Map(witness.rows.map(row => [`${collectionId}-${row.book}-${row.section}`, row]));
  for (let index = 0; index < corpus.length; index++) compareSourceRecord(corpus[index], witness.rows[index], index);
  const combinedReportPath = preserve(resolve(base, config.extractionReportPath));
  const combinedReport = readJSON(combinedReportPath);
  const states = [];
  let adjacentPairs = 0, ordinaryPairs = 0, emptyPairs = 0, proemPairs = 0, barrierChecks = 0;

  for (const entry of selectedEntries) {
    const bookStarted = performance.now();
    const bundlePath = preserve(resolve(base, entry.path)), shardPath = preserve(resolve(base, entry.corpusPath));
    const sourcePath = preserve(resolve(root, `assets/xml/antiquities/Latin/book-${String(entry.number).padStart(2, '0')}.xml`));
    const additionalSources = entry.number === 1 ? [preserve(resolve(root, 'assets/xml/antiquities/Latin/preface.xml'))] : [];
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
        check('ExplicitEmptySectionIdentity', [records[index].book, records[index].section], [3, 240]);
        continue;
      }
      const start = Math.max(0, Math.floor(ts.length / 2) - 1);
      const ast = phrase(ts.slice(start, start + 3).map(token => token.term));
      for (const scope of ['section', 'book']) for (const fold of [false, true]) verify(engine, oracle, ast, {scope, fold}, 'WithinEveryNonemptyUnit');
    }
    const seamIndices = smoke ? [...new Set([0, 25, 177, 238, 239].filter(index => index < records.length - 1))] : records.slice(1).map((_, index) => index);
    for (const index of seamIndices) {
      adjacentPairs++;
      const leftTokens = oracle.tokenLists[index], rightTokens = oracle.tokenLists[index + 1];
      if (!leftTokens.length || !rightTokens.length) {
        emptyPairs++;
        check('EmptySectionMarksAnUnsearchablePhraseSeam', [entry.number, records[index].section, records[index + 1].section],
          leftTokens.length ? [3, 239, 240] : [3, 240, 241]);
        continue;
      }
      const ast = phrase([...leftTokens.slice(-1), ...rightTokens.slice(0, 1)].map(token => token.term));
      const matching = oracle.evaluate(ast, 'book', false);
      const ownSeam = [...matching.values()].flatMap(hits => [...hits]).some(hit => {
        const spans = JSON.parse(hit); return spans.length === 2 && spans[0][0] === records[index].id && spans[1][0] === records[index + 1].id;
      });
      const blocked = entry.number === 1 && records[index].section === 26;
      if (blocked) proemPairs++; else ordinaryPairs++;
      check('BoundaryOracleExpectation', ownSeam, !blocked, {book: entry.number, left: records[index].citationLabel, right: records[index + 1].citationLabel});
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, ast, {scope, fold}, blocked ? 'ProemNarrativeBoundaryBlocked' : 'EveryAdjacentUnitBoundary');
      const contextPhrase = phrase([...leftTokens.slice(-2), ...rightTokens.slice(0, 2)].map(token => token.term));
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, contextPhrase, {scope, fold}, 'ExtendedBoundaryContextPhrase');
    }
    for (const row of expectedRows) for (const marker of [...row.literalGaps, ...row.teiGaps.map(gap => ({start: gap.offset, end: gap.offset, text: ''}))]) {
      barrierChecks++;
      const recordId = `${collectionId}-${row.book}-${row.section}`;
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
      const key = scope === 'section' ? recordId : identity(records[recordIndex]);
      check('BooleanAcrossGapAllowed', oracle.evaluate(boolean, scope, false).has(key), true, {book: row.book, section: row.section, marker});
      verify(engine, oracle, boolean, {scope, fold: false}, 'BooleanAcrossGapAllowed');
    }
    states.push({entry, bundlePath, shardPath, sourcePath, reportPath, additionalSources, oracle, engine,
      vocabularyQueries: wordsToTest.length * 2, withinBookBoundaries: seamIndices.length});
    console.log(JSON.stringify({phase: 'Antiquities book complete', book: entry.number, vocabulary: oracle.vocabulary.length,
      queriesSoFar: totalQueries, seconds: Math.round((performance.now() - bookStarted) / 100) / 10}));
  }
  check('EverySourceGapExercised', barrierChecks, 7);
  if (!smoke) {
    check('AllAdjacentPairsExercised', adjacentPairs, 1705);
    check('AllOrdinaryPairsExercised', ordinaryPairs, 1702);
    check('BothEmptyCitationEdgesExercised', emptyPairs, 2);
    check('SeparateProemNarrativeEdgeExercised', proemPairs, 1);
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
        await verifyCollection(ast, selected, scope, fold, 'SelectedAntiquitiesCollection', query, selected.length === 5 && !fold);
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
    {collections: [collectionId], books: [`${collectionId}:6`]}]) {
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
    source: {books: 5, sourceFiles: 6, sections: 1710, tokens: 67657,
      uniqueLiteralVocabulary: new Set(states.flatMap(state => state.oracle.vocabulary)).size},
    sources: witness.files.map(file => ({path: file.sourceFile, sha256: file.sha256, sections: file.sections, tokens: file.wordTokens, stableIds: file.stableIds})),
    verifiedFiles: {corpus: evidence(corpusPath), catalog: evidence(catalogPath), engine: evidence(resolve(base, 'engine.mjs')),
      collection: evidence(resolve(base, 'collection.mjs')), lunr: evidence(resolve(base, 'vendor/lunr.cjs')),
      verifier: evidence(fileURLToPath(import.meta.url)), witness: evidence(witnessPath),
      extractionReport: evidence(combinedReportPath), originalReader: evidence(readerPath), uiUtils: evidence(resolve(base, 'ui-utils.mjs')),
      books: states.map(state => ({book: state.entry.number, bundle: evidence(state.bundlePath), corpus: evidence(state.shardPath),
        source: evidence(state.sourcePath), additionalSources: state.additionalSources.map(evidence), extractionReport: evidence(state.reportPath)}))},
    method: {source: 'Independent minidom text-node event stream over six SHA-pinned XML files, without production extractor imports. The complete witness is embedded and checked against its standalone file.',
      tokens: 'Every Unicode-category token and UTF-16 offset is checked against each bundle; a separate JavaScript character scanner agrees on every citation unit.',
      queries: 'Independent AST/set Boolean logic, regular-expression globs, and sequential phrase scanning. Phrase barriers derive from witness source marks and explicit source-division boundaries.',
      vocabulary: 'Every distinct source token in every book queried in source-spelling and u/v–i/j-folded modes.',
      boundaries: 'Every within-book adjacent citation pair, all six literal dot-clusters, the empty III.240 gap, the Proem-to-narrative boundary, and every book junction checked.',
      collection: 'All five Antiquities bundles, selected subsets and order, limited four-work integration queries, caching, invalid selection and unavailable-book rejection.'},
    boundaryCoverage: {withinBookPairs: adjacentPairs, ordinaryPairs, emptyCitationEdges: emptyPairs,
      proemNarrativeEdges: proemPairs, literalGapClusters: 6, teiGaps: 1, bookJunctions: 4},
    editorialCoverage: {add: 19, del: 23, sourceNotesExcluded: 12, emptyCitation: 'III.240',
      proemSections: 26, preservedNieseUnits: 1710, continuationSections: ['II.95', 'III.178', 'IV.106', 'IV.155', 'IV.276', 'V.32']},
    counts, totalQueries, assertions, failedAssertions: 0, examples,
    durationSeconds: Math.round((performance.now() - started) / 10) / 100,
    limitations: ['Automated Node/Python acceptance, not browser or visual acceptance.',
      'Reader URLs are verified with the actual UI URL helper; reader pages are not opened by this verifier.',
      'The accepted corrected project XML is preserved faithfully; this does not re-collate the text with manuscript images.',
      'Earlier collections receive limited mixed-work integration checks; their independent source-fidelity reports remain separately required.',
      'Literal dot-clusters conservatively suppress phrase adjacency without assigning new scholarly meanings or missing-text extents.'], failures: [],
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
