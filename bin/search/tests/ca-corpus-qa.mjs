/**
 * Independent Contra Apionem source/index/query acceptance.
 * Run: node bin/search/tests/ca-corpus-qa.mjs
 * A reviewed reader may be selected with --expected-reader-sha256 <SHA-256>.
 * --smoke is a development check and never writes a publication QA report.
 *
 * This imports production entry points only to exercise them. The witness is
 * separately parsed with Python minidom, independently tokenized by Unicode
 * character categories, and matched by an explicit AST/set/full-scan oracle.
 * The embedded witness is part of this verifier's own checked fingerprint.
 * Its standalone ca-source-witness.py copy is also checked for byte identity.
 */
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {dirname, relative, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {performance} from 'node:perf_hooks';
import {createEngine} from '../engine.mjs';
import {createCollection} from '../collection.mjs';

const require = createRequire(import.meta.url);
const lunr = require('../vendor/lunr.cjs');
const base = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const root = resolve(base, '../..');
const collectionId = 'contra-apionem-latin-boysen';
const destination = resolve(base, 'data', collectionId, 'qa-report.json');
let smoke = false, explicitReaderSHA = null;
const args = process.argv.slice(2);
const usage = 'Usage: node bin/search/tests/ca-corpus-qa.mjs [--smoke] [--expected-reader-sha256 <accepted SHA-256>]';
for (let index = 0; index < args.length; index++) {
  if (args[index] === '--smoke') {
    assert.equal(smoke, false, usage);
    smoke = true;
  } else if (args[index] === '--expected-reader-sha256') {
    assert.ok(explicitReaderSHA === null && /^[a-f0-9]{64}$/i.test(args[index + 1] || ''), usage);
    explicitReaderSHA = args[++index].toLowerCase();
  } else assert.fail(usage);
}
const started = performance.now();
const hash = value => createHash('sha256').update(value).digest('hex');
const digest = path => hash(readFileSync(path));
const readJSON = path => JSON.parse(readFileSync(path, 'utf8'));
const evidence = path => ({path: relative(root, path).replaceAll('\\', '/'), sha256: digest(path)});
const counts = {};
let assertions = 0, totalQueries = 0;
const examples = [];
const checkedFiles = new Map();
function preserve(path) {
  const resolved = resolve(path);
  if (!checkedFiles.has(resolved)) checkedFiles.set(resolved, digest(resolved));
  return resolved;
}
function check(category, actual, expected, context = {}) {
  assertions++;
  counts[category] = (counts[category] || 0) + 1;
  assert.deepEqual(actual, expected, `${category}: ${JSON.stringify(context)}`);
}

// Exact independent minidom witness, bound into this verifier's fingerprint.
const pythonWitness = String.raw`#!/usr/bin/env python3
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
    // Derive CA barriers independently from verified source text and the two
    // SHA-pinned ana identities, not from the generated phraseBreaks metadata.
    const isCA = record.work === 'contra-apionem';
    if (isCA ? (Number(record.book) === 1 && [119, 147].includes(Number(record.section))) : record.breakBefore) segment++;
    const sourceBarriers = isCA ? [...record.text.matchAll(/\*(?:\s*\*)*/g)].map(match => match.index) : [];
    let barrierIndex = 0;
    for (const token of tokenLists[index]) {
      while (barrierIndex < sourceBarriers.length && sourceBarriers[barrierIndex] <= token.start) {
        segment++; barrierIndex++;
      }
      all.push({...token, recordId: record.id, recordIndex: index, bookKey: key, segment});
    }
    // An asterisk after the last token also separates the next record.
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
          || !matchers[j](normalize(token.term, fold))) {accepted = false; break;}
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
const witnessPath = resolve(base, 'tests/ca-source-witness.py');
const acceptedReaders = new Map([
  ['03bfb9b0de5e13e6b07bd638413b2b82a9ed2f7b0cc7c33eb6c09dabde3c9294', 'canonical-2026-10-14'],
  ['25c00a11818fe5a71dcbffb516aeb8a6f02c6b61c218f4e85105a12eb310d0ed', 'approved-public-preview'],
]);
const observedReaderSHA = digest(readerPath);
const readerSHA = explicitReaderSHA || observedReaderSHA;
const readerBaseline = {expectedSha256: readerSHA, observedSha256: observedReaderSHA,
  provenance: explicitReaderSHA ? 'explicit-argument' : acceptedReaders.get(readerSHA),
  preservationDuringRunRequired: true, publicationInput: false};

function expectedRecord(row, index) {
  const record = {
    id: `${collectionId}-${row.book}-${row.section}`, work: 'contra-apionem',
    book: row.book, section: row.section, language: 'Latin', edition: 'Boysen (1898)',
    citationScheme: 'niese', citationLabel: row.citationLabel,
    citation: {book: row.book === 1 ? 'I' : 'II', section: row.section},
    text: row.text,
    editorialMarks: row.editorialMarks.map(mark => ({...mark, sourceTag: 'add'})),
    sourceMarkup: row.inlineMarks.filter(mark => ['q', 'foreign'].includes(mark.kind)).map(mark => ({
      kind: mark.kind, start: mark.start, end: mark.end, text: mark.text,
      ...(mark.kind === 'foreign' ? {language: 'grc'} : {}),
    })),
    textGaps: row.asteriskMarkers.map(mark => ({...mark, kind: 'literal-asterisks'})),
    phraseBreaks: row.phraseBreaks, url: row.url,
    readerLink: {path: 'contra-apionem/', params: {book: row.book, niese: row.section}},
    sourceId: row.sourceId, order: index,
  };
  if (row.attributes.ana) record.sourceAnnotations = [row.attributes.ana];
  if (row.breakBefore) {
    record.breakBefore = true;
    record.breakReason = 'The source marks this Niese boundary within the preceding lacuna.';
  }
  return record;
}

function inspectProjection(report, witnessRows, records) {
  check('ExtractionReportUnitCount', report.paragraphs.length, witnessRows.length);
  for (let index = 0; index < witnessRows.length; index++) {
    const row = witnessRows[index], actual = report.paragraphs[index], record = records[index];
    const context = {book: row.book, section: row.section};
    check('ProjectionStableId', actual.sourceId, row.sourceId, context);
    check('ProjectionRawSourceHash', actual.rawTextSha256, row.rawTextSha256, context);
    check('ProjectionLeadingWhitespace', actual.leadingWhitespace, row.leadingWhitespace, context);
    check('ProjectionTrailingWhitespace', actual.trailingWhitespace, row.trailingWhitespace, context);
    check('ProjectionRawCharacterCount', actual.rawTextCharacters, Array.from(row.leadingWhitespace + row.text + row.trailingWhitespace).length, context);
    check('ProjectionRemovedPrefix', actual.removedPrefix, '', context);
    check('ProjectionDisplayHash', actual.displayTextSha256, hash(row.text), context);
    check('ProjectionSourceHash', actual.sourceProjectionSha256, hash(row.text), context);
    const expectedAttributes = Object.fromEntries(Object.entries(row.attributes).map(([key, value]) => [
      key === 'xml:id' ? '{http://www.w3.org/XML/1998/namespace}id' : key, value,
    ]));
    check('ProjectionSourceAttributes', actual.sourceAttributes, expectedAttributes, context);
    const points = Array.from(record.text), leading = Array.from(row.leadingWhitespace).length;
    let cursor = 0;
    const pieces = [];
    for (const segment of actual.segments) {
      check('ProjectionSegmentKind', segment.kind, 'source-text', context);
      check('ProjectionSegmentContiguity', segment.recordTextStart, cursor, context);
      assert.ok(Number.isInteger(segment.recordTextEnd) && segment.recordTextEnd > cursor && segment.recordTextEnd <= points.length);
      const text = points.slice(segment.recordTextStart, segment.recordTextEnd).join('');
      check('ProjectionSegmentSourceStart', segment.sourceTextStart, segment.recordTextStart + leading, context);
      check('ProjectionSegmentSourceEnd', segment.sourceTextEnd, segment.recordTextEnd + leading, context);
      check('ProjectionSegmentHash', segment.textSha256, hash(text), context);
      pieces.push(text); cursor = segment.recordTextEnd;
    }
    check('ProjectionSegmentFullCoverage', cursor, points.length, context);
    check('ProjectionExactSourceRestoration', hash(row.leadingWhitespace + pieces.join('') + row.trailingWhitespace), row.rawTextSha256, context);
    const markers = row.structuralMarkers.map(marker => {
      const offset = Math.max(0, Math.min(points.length, marker.rawOffset - leading));
      return {
        kind: marker.kind === 'milestone' ? 'chapter' : 'pb', sourceTextOffset: marker.rawOffset,
        ...(marker.kind === 'milestone' ? {number: Number(marker.attributes.n), edition: 'Boysen (1898)'} : {page: marker.attributes.n}),
        recordTextOffset: offset, recordTextOffsetUTF16: points.slice(0, offset).join('').length,
      };
    });
    check('ProjectionStructuralMarkers', actual.structuralMarkers, markers, context);
    const inline = row.inlineMarks.map(mark => ({kind: mark.kind,
      sourceTextStart: Array.from(row.text.slice(0, mark.start)).length + leading,
      sourceTextEnd: Array.from(row.text.slice(0, mark.end)).length + leading,
      ...(mark.kind === 'foreign' ? {language: 'grc'} : {}),
    }));
    check('ProjectionInlineMarkup', actual.inlineMarks, inline, context);
    check('ProjectionAsteriskSpans', actual.textGaps, record.textGaps, context);
    check('ProjectionPhraseBreaks', actual.phraseBreaks, row.phraseBreaks, context);
  }
}

const fixtures = [
  ['Iosephus', leaf('Iosephus')], ['sacerdot*', leaf('sacerdot*')], ['praecellentes', leaf('praecellentes')],
  ['"Sufficienter ut arbitror"', phrase(['Sufficienter', 'ut', 'arbitror'])],
  ['"ex nostris sacris libris"', phrase(['ex', 'nostris', 'sacris', 'libris'])],
  ['"languentium milia trecenta"', phrase(['languentium', 'milia', 'trecenta'])],
  ['"ἀπὸ τῆς ἱεροσυλίας"', phrase(['ἀπὸ', 'τῆς', 'ἱεροσυλίας'])],
  ['ἑϰατώμβω̩α', leaf('ἑϰατώμβω̩α')],
  ['"Amenofis annis"', phrase(['Amenofis', 'annis'])],
  ['"sacerdotes atque"', phrase(['sacerdotes', 'atque'])],
  ['"circumposuisse sibi"', phrase(['circumposuisse', 'sibi'])],
  ['"deos quam"', phrase(['deos', 'quam'])],
  ['"igitur si propter uirtutem legum"', phrase(['igitur', 'si', 'propter', 'uirtutem', 'legum'])],
  ['"is autem etiam seditionis"', phrase(['is', 'autem', 'etiam', 'seditionis'])],
  ['"nisi qu*"', phrase(['nisi', 'qu*'])],
  ['Iudae* OR Roman* AND sacerdot*', or(leaf('Iudae*'), and(leaf('Roman*'), leaf('sacerdot*')))],
  ['Ioseph* sacerdot* OR templ*', or(and(leaf('Ioseph*'), leaf('sacerdot*')), leaf('templ*'))],
  ['(Ioseph* OR sacerdot*) AND NOT templ*', and(or(leaf('Ioseph*'), leaf('sacerdot*')), not(leaf('templ*')))],
  ['NOT (Ioseph* OR NOT sacerdot*)', not(or(leaf('Ioseph*'), not(leaf('sacerdot*'))))],
  ['NOT NOT Iosephus', not(not(leaf('Iosephus')))],
  ['NOT zzzznonoccurrit', not(leaf('zzzznonoccurrit'))], ['NOT *', not(leaf('*'))],
  ['rex OR rex*', or(leaf('rex'), leaf('rex*'))],
  ['Amenofis AND annis', and(leaf('Amenofis'), leaf('annis'))],
  ['circumposuisse sibi', and(leaf('circumposuisse'), leaf('sibi'))],
  ['"duo et uiginti libri"', phrase(['duo', 'et', 'uiginti', 'libri'])],
];

async function main() {
  assert.ok(explicitReaderSHA || acceptedReaders.has(observedReaderSHA), 'Reader differs from both reviewed baseline fingerprints; review before explicitly supplying --expected-reader-sha256.');
  check('ReviewedReaderBaseline', observedReaderSHA, readerSHA);
  preserve(witnessPath);
  check('StandaloneWitnessMatchesEmbeddedFingerprint', readFileSync(witnessPath, 'utf8'), pythonWitness);
  const catalogPath = preserve(resolve(base, 'catalog.json'));
  const corpusPath = preserve(resolve(base, 'data', collectionId, 'corpus.json'));
  const catalog = readJSON(catalogPath), corpus = readJSON(corpusPath);
  const config = catalog.collections.find(collection => collection.id === collectionId);
  assert.ok(config, 'The catalog must include Contra Apionem before this verifier runs.');
  const selectedEntries = catalog.books.filter(entry => entry.collectionId === collectionId);
  check('CatalogBookOrder', selectedEntries.map(entry => entry.number), [1, 2]);
  check('CatalogCitationScheme', config.citationScheme, 'niese');
  check('AllThreeWorkBookCount', catalog.books.length, 14);
  preserve(readerPath); preserve(resolve(base, 'engine.mjs')); preserve(resolve(base, 'collection.mjs'));
  preserve(resolve(base, 'vendor/lunr.cjs')); preserve(fileURLToPath(import.meta.url));
  const witness = JSON.parse(execFileSync(process.env.PYTHON || 'python3', ['-c', pythonWitness, root], {encoding: 'utf8', maxBuffer: 40 * 1024 * 1024}));
  check('CanonicalStableIds', witness.stableIds, 620);
  check('CombinedRecordCount', corpus.length, 616);
  for (let index = 0; index < corpus.length; index++) {
    check('CompleteSourceRecord', corpus[index], expectedRecord(witness.rows[index], index), {index});
    check('IndependentTokenizersAgree', independentTokens(corpus[index].text), witness.rows[index].tokens, {id: corpus[index].id});
  }
  const combinedReportPath = preserve(resolve(base, config.extractionReportPath));
  const combinedReport = readJSON(combinedReportPath);
  check('CombinedExtractionSourceTotals', combinedReport.counts.runningWordTokens, 21018);
  check('CombinedExtractionAsteriskClusters', combinedReport.counts.asteriskMarkerClusters, 25);
  const states = [];
  let blockedSeams = 0, barrierChecks = 0;
  for (const entry of selectedEntries) {
    const bookStarted = performance.now();
    const bundlePath = preserve(resolve(base, entry.path)), shardPath = preserve(resolve(base, entry.corpusPath));
    const sourcePath = preserve(resolve(root, `assets/xml/contra-apionem/Latin/book-${String(entry.number).padStart(2, '0')}.xml`));
    const reportPath = preserve(resolve(base, 'data', collectionId, `book-${String(entry.number).padStart(2, '0')}.extraction-report.json`));
    const bundle = readJSON(bundlePath), shard = readJSON(shardPath), extractionReport = readJSON(reportPath);
    const expectedRows = witness.rows.filter(row => row.book === entry.number);
    const records = corpus.filter(record => record.book === entry.number);
    inspectProjection(extractionReport, expectedRows, records);
    check('ShardMatchesCombinedCorpus', shard, records, {book: entry.number});
    check('BundleMatchesShard', bundle.records, records.map(record => ({...record, breakBefore: Boolean(record.breakBefore)})), {book: entry.number});
    check('CatalogBundleHash', entry.sha256, digest(bundlePath), {book: entry.number});
    check('CatalogCorpusHash', entry.corpusSHA256, digest(shardPath), {book: entry.number});
    check('SourceFingerprint', digest(sourcePath), witness.books[entry.number - 1].sha256, {book: entry.number});
    check('AllIndexedTokenOffsets', bundle.tokens, expectedRows.map(row => row.tokens), {book: entry.number});
    check('ExpectedTokenCount', bundle.stats.tokens, witness.books[entry.number - 1].tokens, {book: entry.number});
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
      const tokens = oracle.tokenLists[index], start = Math.max(0, Math.floor(tokens.length / 2) - 1);
      const ast = phrase(tokens.slice(start, start + 3).map(token => token.term));
      for (const scope of ['section', 'book']) for (const fold of [false, true]) verify(engine, oracle, ast, {scope, fold}, 'WithinEveryUnit');
    }
    const seamIndices = smoke ? [0, 10, 117, 145].filter(index => index < records.length - 1) : records.slice(1).map((_, index) => index);
    for (const index of seamIndices) {
      // Probe the seam itself with its two immediate words. A four-word
      // context can encounter another source marker inside the preceding or
      // following unit (e.g. I.291), independently of the paragraph seam.
      const ast = phrase([...oracle.tokenLists[index].slice(-1), ...oracle.tokenLists[index + 1].slice(0, 1)].map(token => token.term));
      const matching = oracle.evaluate(ast, 'book', false);
      const ownSeam = [...matching.values()].flatMap(hits => [...hits]).some(hit => {
        const spans = JSON.parse(hit); return spans.length === 2 && spans[0][0] === records[index].id && spans[1][0] === records[index + 1].id;
      });
      const blocked = entry.number === 1 ? [118, 146].includes(records[index].section) : records[index].section === 11;
      if (blocked) blockedSeams++;
      check('BoundaryOracleExpectation', ownSeam, !blocked, {book: entry.number, left: records[index].citationLabel, right: records[index + 1].citationLabel});
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, ast, {scope, fold}, blocked ? 'MarkedLacunaSeamBlocked' : 'EveryAdjacentUnitBoundary');
      const contextPhrase = phrase([...oracle.tokenLists[index].slice(-2), ...oracle.tokenLists[index + 1].slice(0, 2)].map(token => token.term));
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, contextPhrase, {scope, fold}, 'ExtendedBoundaryContextPhrase');
    }
    // Each marker is checked with the closest words on both sides. Paragraph
    // edge markers deliberately select neighbors from the adjacent paragraph.
    for (const row of expectedRows) for (const marker of row.asteriskMarkers) {
      barrierChecks++;
      const recordId = `${collectionId}-${row.book}-${row.section}`;
      const recordIndex = records.findIndex(record => record.id === recordId);
      const split = oracle.all.findIndex(token => token.recordIndex > recordIndex || (token.recordIndex === recordIndex && token.start >= marker.start));
      assert.ok(split >= 1 && split < oracle.all.length, 'Each accepted asterisk has surviving words on both sides within its book.');
      const left = oracle.all.slice(Math.max(0, split - 2), split), right = oracle.all.slice(split, split + 2);
      assert.notEqual(left.at(-1).segment, right[0].segment, 'Independent asterisk segmentation must break adjacency.');
      const ast = phrase([...left, ...right].map(token => token.term));
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        verify(engine, oracle, ast, {scope, fold}, 'EveryAsteriskBarrierBlocked');
      const boolean = and(leaf(left.at(-1).term), leaf(right[0].term));
      const scope = left.at(-1).recordId === right[0].recordId ? 'section' : 'book';
      const key = scope === 'section' ? recordId : identity(records[recordIndex]);
      check('BooleanAcrossAsteriskAllowed', oracle.evaluate(boolean, scope, false).has(key), true, {book: row.book, section: row.section, marker});
      verify(engine, oracle, boolean, {scope, fold: false}, 'BooleanAcrossAsteriskAllowed');
    }
    states.push({entry, bundlePath, shardPath, sourcePath, reportPath, oracle, engine,
      vocabularyQueries: wordsToTest.length * 2, withinBookBoundaries: seamIndices.length});
    console.log(JSON.stringify({phase: 'Contra Apionem book complete', book: entry.number, vocabulary: oracle.vocabulary.length,
      queriesSoFar: totalQueries, seconds: Math.round((performance.now() - bookStarted) / 100) / 10}));
  }
  check('AllSourceAsteriskMarkersExercised', barrierChecks, 25);
  check('ThreeWithinBookGapSeamsExercised', blockedSeams, 3);

  const bundleEntries = new Map(catalog.books.map(entry => [new URL(entry.path, 'https://qa.invalid/assets/search/').pathname, entry]));
  const fetchCounts = new Map();
  const fetchImpl = async url => {
    const entry = bundleEntries.get(new URL(url).pathname);
    assert.ok(entry, `Unexpected bundle request: ${url}`);
    fetchCounts.set(entry.id, (fetchCounts.get(entry.id) || 0) + 1);
    const path = preserve(resolve(base, entry.path));
    return new Response(readFileSync(path), {status: 200});
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
    const matchedIds = new Set(scope === 'section' ? [...expected.keys()] : []);
    const expectedBookIds = ordered.filter(entry => scope === 'book' ? expected.has(identity(allEntryRecords.get(entry.id)[0]))
      : allEntryRecords.get(entry.id).some(record => matchedIds.has(record.id))).map(entry => entry.id);
    check(`${category}MatchingBookIdentity`, actual.matchingBooks, expectedBookIds, {query, scope, fold});
    check(`${category}UniqueRecordIdentity`, new Set(actual.records.map(record => record.id)).size, records.length);
    check(`${category}GlobalResultOrder`, actual.records.map(record => record.resultOrder), records.map((_, index) => index));
    return {actual, expected};
  }
  for (const selected of [[selectedEntries[0].id], [selectedEntries[1].id], selectedEntries.map(entry => entry.id).reverse()])
    for (const [query, ast] of fixtures.filter((_, index) => smoke ? [1, 6, 20].includes(index) : [0, 1, 2, 5, 6, 7, 10, 12, 15, 17, 20, 21, 23, 25].includes(index)))
      for (const scope of ['section', 'book']) for (const fold of [false, true])
        await verifyCollection(ast, selected, scope, fold, 'SelectedCACollection', query, selected.length === 2 && !fold);
  const junction = phrase([...states[0].oracle.all.slice(-3), ...states[1].oracle.all.slice(0, 3)].map(token => token.term));
  for (const scope of ['section', 'book']) for (const fold of [false, true]) {
    const checked = await verifyCollection(junction, selectedEntries.map(entry => entry.id), scope, fold, 'CrossBookPhraseBlocked');
    check('CrossBookPhraseAbsent', checked.expected.size, 0);
  }
  const leftOnly = states[0].oracle.vocabulary.find(word => word.length > 4 && !states[1].oracle.vocabulary.includes(word));
  const rightOnly = states[1].oracle.vocabulary.find(word => word.length > 4 && !states[0].oracle.vocabulary.includes(word));
  assert.ok(leftOnly && rightOnly);
  for (const scope of ['section', 'book']) {
    const checked = await verifyCollection(and(leaf(leftOnly), leaf(rightOnly)), selectedEntries.map(entry => entry.id), scope, false, 'CrossBookBooleanIsolation');
    check('CrossBookBooleanAbsent', checked.expected.size, 0, {leftOnly, rightOnly});
  }
  const bellum = catalog.books.filter(entry => entry.collectionId === 'bellum-latin-cardwell');
  const deh = catalog.books.filter(entry => entry.collectionId === 'deh-latin-ussani');
  check('ExistingCollectionsBookCounts', [bellum.length, deh.length], [7, 5]);
  const mixedSelections = [catalog.books.map(entry => entry.id), [selectedEntries[0].id, bellum[0].id, deh[0].id]];
  for (const selected of mixedSelections) for (const ast of [leaf('Iosephus'), leaf('sacerdot*'), phrase(['ex', 'nostris', 'sacris', 'libris']), not(leaf('zzzznonoccurrit'))])
    for (const scope of ['section', 'book']) for (const fold of [false, true])
      await verifyCollection(ast, selected, scope, fold, 'MixedThreeWorkCollection', print(ast), !fold && scope === 'book');
  for (const other of [bellum[0], deh[0]]) {
    const otherOracle = makeOracle(allEntryRecords.get(other.id)), caOracle = states[0].oracle;
    const caOnly = caOracle.vocabulary.find(word => word.length > 4 && !otherOracle.vocabulary.includes(word));
    const otherOnly = otherOracle.vocabulary.find(word => word.length > 4 && !caOracle.vocabulary.includes(word));
    assert.ok(caOnly && otherOnly);
    for (const scope of ['section', 'book']) {
      const checked = await verifyCollection(and(leaf(caOnly), leaf(otherOnly)), [selectedEntries[0].id, other.id], scope, false, 'CrossWorkBooleanIsolation');
      check('CrossWorkBooleanAbsent', checked.expected.size, 0, {caOnly, otherOnly, other: other.id});
      const ast = phrase([...otherOracle.all.slice(-3), ...caOracle.all.slice(0, 3)].map(token => token.term));
      const phraseChecked = await verifyCollection(ast, [other.id, selectedEntries[0].id], scope, false, 'CrossWorkPhraseBlocked');
      check('CrossWorkPhraseAbsent', phraseChecked.expected.size, 0, {other: other.id});
    }
  }
  check('BundleFetchCaching', [...fetchCounts.entries()].sort(), catalog.books.map(entry => [entry.id, 1]).sort());
  for (const invalid of [{collections: [collectionId], books: [1]}, {collections: [collectionId], books: [bellum[0].id]}, {collections: [collectionId], books: [deh[0].id]}]) {
    await assert.rejects(collection.search('sacerdot*', invalid));
    assertions++; counts.InvalidSelectionRejected = (counts.InvalidSelectionRejected || 0) + 1;
  }
  const failedLoad = createCollection(catalog, lunr, {baseURL: 'https://qa.invalid/assets/search/', fetchImpl: async url => {
    if (new URL(url).pathname.endsWith('/contra-apionem-latin-boysen/book-02.bundle.json')) return new Response('Unavailable', {status: 404});
    return new Response(readFileSync(resolve(base, bundleEntries.get(new URL(url).pathname).path)), {status: 200});
  }});
  await assert.rejects(failedLoad.search('sacerdot*', {collections: [collectionId], books: selectedEntries.map(entry => entry.id)}));
  assertions++; counts.MissingSelectedBookRejectsCompleteSearch = 1;
  for (const [path, sha256] of checkedFiles) check('InputUnchangedDuringQA', digest(path), sha256, {path: relative(root, path)});
  const report = {
    status: 'PASS', generatedAt: new Date().toISOString(), independentVerifier: 'bin/search/tests/ca-corpus-qa.mjs', readerBaseline,
    runtime: {node: process.versions.node, ...witness.runtime},
    source: {books: 2, sections: 616, tokens: 21018, stableIds: 620, embeddedGreekTokens: 7,
      uniqueLiteralVocabulary: new Set(states.flatMap(state => state.oracle.vocabulary)).size}, sources: witness.books,
    verifiedFiles: {corpus: evidence(corpusPath), catalog: evidence(catalogPath), engine: evidence(resolve(base, 'engine.mjs')),
      collection: evidence(resolve(base, 'collection.mjs')), lunr: evidence(resolve(base, 'vendor/lunr.cjs')),
      verifier: evidence(fileURLToPath(import.meta.url)), witness: evidence(witnessPath),
      extractionReport: evidence(combinedReportPath), originalReader: evidence(readerPath),
      books: states.map(state => ({book: state.entry.number, bundle: evidence(state.bundlePath), corpus: evidence(state.shardPath),
        source: evidence(state.sourcePath), extractionReport: evidence(state.reportPath)}))},
    method: {source: 'Independent minidom parse of two SHA-pinned accepted XML sources. The exact Python witness is embedded in the fingerprinted verifier and compared with its standalone copy; no production extractor imports.',
      tokens: 'Every Unicode-category token and UTF-16 offset is checked against the indexes; an independent JavaScript character scan agrees for all 616 units.',
      queries: 'AST/set semantics, independent regex globs, full sequential phrase scan; the source asterisk positions are derived from the independently verified text, not generated barrier metadata.',
      vocabulary: 'Every distinct source token in each book queried in both source-spelling and u/v–i/j-folded modes.',
      boundaries: 'All 614 within-book section pairs and all 25 source-asterisk markers checked; the three marked section-edge seams and the book junction cannot be crossed by a phrase.',
      collection: 'Actual checksum-verified loading, both CA books and all 14 books in three works, independent book/work identity, caching, unavailable-book and invalid-selection rejection.'},
    boundaryCoverage: {withinBookPairs: states.reduce((sum, state) => sum + state.withinBookBoundaries, 0),
      legalWholeBookPairs: 611, blockedSourceMarkedPairs: 3, asteriskMarkers: 25, interiorAsteriskMarkers: 22,
      asteriskMarkersAtSectionEdges: 3, bookJunctions: 1, mixedWorkJunctions: 2},
    editorialCoverage: {add: 1, quotedSpans: 1, foreignSpans: 3, sourceAsteriskClusters: 25,
      sourceAnnotations: 3, chapterMilestones: 76, pageMarkers: 140, wordInternalPageMarkers: 1,
      preservedNieseUnits: 616, sourceProjectionExactlyRestored: 616},
    counts, totalQueries, assertions, failedAssertions: 0, examples,
    durationSeconds: Math.round((performance.now() - started) / 10) / 100,
    limitations: ['Automated Node/Python verification, not browser or visual acceptance.',
      'Reader URLs are checked against canonical citation/ID structure; reader pages are not opened by this verifier.',
      'The accepted project XML is checked faithfully; no new collation with Boysen page images or new scholarly boundary decisions are undertaken.',
      'Bellum and DEH records in mixed-work checks are independently tokenized; their separate source-fidelity QA remains required.',
      'Asterisk barriers conservatively suppress phrase adjacency; they do not assign a precise scholarly meaning or a missing-text extent to every source mark.'], failures: [],
  };
  if (!smoke) writeFileSync(destination, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({status: smoke ? 'DEVELOPMENT_SMOKE_PASS' : 'PASS', source: report.source, totalQueries, assertions,
    failedAssertions: 0, durationSeconds: report.durationSeconds, publicationReportWritten: !smoke}));
}

if (!smoke) writeFileSync(destination, JSON.stringify({status: 'RUNNING', generatedAt: new Date().toISOString(), independentVerifier: 'bin/search/tests/ca-corpus-qa.mjs'}, null, 2) + '\n');
try { await main(); }
catch (error) {
  if (!smoke) writeFileSync(destination, JSON.stringify({status: 'FAIL', generatedAt: new Date().toISOString(), assertions,
    totalQueries, failedAssertions: 1, error: {name: error.name, message: error.message, stack: error.stack}}, null, 2) + '\n');
  console.error(error.stack || error);
  process.exitCode = 1;
}

