/**
 * Occurrence rows and a reproducible CSV, built from the engine's positive hits.
 * Display-card highlights are deliberately not an input: their merged ranges
 * cannot distinguish repeated or overlapping occurrences. All offsets below
 * address original record.text strings in JavaScript (UTF-16) string units.
 */
import { parseQuery, tokenizeText } from "./engine.mjs";
import { bookCitation, citationFor, readerURL, citationScheme, editorialMarksFor, editorialText } from "./ui-utils.mjs";

export const CONCORDANCE_SCHEMA_VERSION = 1;
const IDENTITY_FIELDS = ["collectionId", "work", "book", "language", "edition"];
const versionKey = (record) => JSON.stringify(IDENTITY_FIELDS.map((field) => String(record[field] ?? "")));
const engineBookId = (record) => `book:${[record.work, record.book, record.language || "", record.edition || ""].map(encodeURIComponent).join(":")}`;
const distinct = (values) => [...new Set(values)];
const gapJoin = (left, right) => left && right && !/\s$/u.test(left) && !/^\s/u.test(right) ? " " : "";

function sourceIndex(records) {
  const byId = new Map();
  const partitions = new Map();
  records.forEach((record, position) => {
    if (!record || typeof record.id !== "string" || !record.id || typeof record.text !== "string" || byId.has(record.id)) {
      throw new TypeError("Concordance records require unique IDs and original text strings.");
    }
    editorialMarksFor(record);
    const key = versionKey(record);
    if (!partitions.has(key)) partitions.set(key, { records: [], positions: new Map(), first: record.resultOrder ?? position });
    partitions.get(key).records.push({ record, position });
    byId.set(record.id, record);
  });
  const rank = new Map();
  const partitionByRecord = new Map();
  for (const partition of [...partitions.values()].sort((a, b) => a.first - b.first)) {
    partition.records.sort((a, b) => (a.record.order ?? a.record.resultOrder ?? a.position) - (b.record.order ?? b.record.resultOrder ?? b.position) || a.position - b.position);
    partition.records = partition.records.map(({ record }) => record);
    partition.records.forEach((record, position) => {
      partition.positions.set(record.id, position);
      partitionByRecord.set(record.id, partition);
      rank.set(record.id, rank.size);
    });
  }
  return { byId, partitions: [...partitions.values()], partitionByRecord, rank };
}

function groupRecords(group, scope, index) {
  const supplied = (group.recordIds || []).map((id) => {
    const record = index.byId.get(id);
    if (!record) throw new TypeError(`The concordance refers to an unknown source record: ${id}`);
    return record;
  });
  if (scope === "section") {
    if (supplied.length !== 1) throw new TypeError("A matching section must identify exactly one source record.");
    return supplied;
  }
  if (supplied.length) {
    const partition = index.partitionByRecord.get(supplied[0].id);
    if (supplied.some((record) => index.partitionByRecord.get(record.id) !== partition)) {
      throw new TypeError("A matching book cannot combine works, books, languages, or editions.");
    }
    return partition.records;
  }
  // A NOT-only book match intentionally has no recordIds or hits. Collection
  // results provide full identity metadata; raw engine results provide the
  // encoded book unit ID. Neither needs an invented occurrence or passage.
  const candidates = index.partitions.filter(({ records }) => {
    const first = records[0];
    const fields = IDENTITY_FIELDS.filter((field) => group[field] !== undefined);
    if (fields.length && !fields.every((field) => String(group[field]) === String(first[field] ?? ""))) return false;
    if (fields.includes("work") && fields.includes("book")) return true;
    const key = engineBookId(first);
    return group.unitId === key || group.unitId?.endsWith(`:${key}`);
  });
  if (candidates.length !== 1) throw new TypeError("The matching book's source identity is missing or ambiguous.");
  return candidates[0].records;
}

function identity(record, group, scope, readerBase) {
  for (const field of IDENTITY_FIELDS) {
    if (group[field] !== undefined && record[field] !== undefined && String(group[field]) !== String(record[field])) {
      throw new TypeError(`The concordance hit's ${field} does not match its source record.`);
    }
  }
  return {
    unitId: group.unitId || record.id,
    unitLabel: citationScheme(record) === "chapter-paragraph" ? (scope === "book" ? bookCitation(record) : citationFor([record])) : group.unitLabel || (scope === "book" ? bookCitation(record) : citationFor([record])),
    scope,
    citationScheme: citationScheme(record),
    citationUnitLabel: record.citationUnitLabel || (citationScheme(record) === "chapter-paragraph" ? "citation unit" : "Niese section"),
    collectionId: record.collectionId ?? group.collectionId ?? "",
    work: record.work ?? group.work ?? "",
    book: record.book ?? group.book ?? "",
    bookId: record.bookId ?? group.bookId ?? (record.collectionId ? `${record.collectionId}:${record.book}` : ""),
    language: record.language ?? group.language ?? "",
    edition: record.edition ?? group.edition ?? "",
    readerURL: readerURL(record, readerBase, { section: scope !== "book" }),
  };
}

function queryTexts(hit) {
  return distinct([...(hit.queryTexts || []), hit.queryText].filter((value) => typeof value === "string" && value));
}

/**
 * buildConcordance(result, records=result.records, {readerBase, contextWords=10})
 *
 * rows contain one distinct hit geometry each; different overlapping spans
 * remain separate. Identical spans from multiple successful Boolean operands
 * share one row and retain every queryText. Only a leaf word or quoted phrase
 * receives an occurrenceCount; Boolean positive evidence is not a frequency.
 *
 * records are original record references, spans are original hit offsets,
 * and contextSpans identify the displayed source slices. left/match/right
 * preserve source spelling, punctuation, and whitespace, without ellipses.
 * A joining space is inserted between sections only when neither source side
 * supplies whitespace. Context never extends beyond the cited section(s).
 */
export function buildConcordance(result, records = result?.records, { readerBase, contextWords = 10 } = {}) {
  if (!result || !Array.isArray(result.hitGroups) || !Array.isArray(records)) throw new TypeError("Search results and their original records are required.");
  if (result.scope !== "section" && result.scope !== "book") throw new TypeError("Concordance scope must be section or book.");
  if (!Number.isInteger(contextWords) || contextWords < 0) throw new TypeError("Context words must be a nonnegative integer.");
  const tree = parseQuery(result.query);
  const countKind = tree.type === "leaf" ? (tree.kind === "term" ? "word" : "phrase") : "evidence";
  const base = readerBase || new URL("../../", import.meta.url).href;
  const index = sourceIndex(records);
  const tokens = new Map();
  const tokensFor = (record) => {
    if (!tokens.has(record.id)) tokens.set(record.id, tokenizeText(record.text));
    return tokens.get(record.id);
  };
  const unique = new Map();
  const unhighlightedUnits = [];
  const unitKeys = new Set();

  for (const group of result.hitGroups) {
    if (!Array.isArray(group.hits)) throw new TypeError("A concordance group must provide its underlying hits.");
    const unitRecords = groupRecords(group, result.scope, index);
    const unitRecordIds = new Set(unitRecords.map((record) => record.id));
    if (!group.hits.length) {
      const key = `unit:${group.unitId || JSON.stringify(unitRecords.map((record) => record.id))}`;
      if (unitKeys.has(key)) continue;
      unitKeys.add(key);
      const first = unitRecords[0];
      unhighlightedUnits.push({
        ...identity(first, group, result.scope, base),
        key, kind: "matching-unit", citation: result.scope === "book" ? bookCitation(first) : citationFor(unitRecords),
        sourceOrder: index.rank.get(first.id),
        left: "", match: "", right: "", leftTruncated: false, rightTruncated: false,
        records: unitRecords, spans: [], queryTexts: [], contextSpans: [], editorialMarks: [],
      });
      continue;
    }
    for (const hit of group.hits) {
      if (!["term", "phrase"].includes(hit.kind) || !Array.isArray(hit.spans) || !hit.spans.length) {
        throw new TypeError("A positive concordance hit must contain its term or phrase spans.");
      }
      const spans = hit.spans.map(({ recordId, start, end }) => {
        const record = index.byId.get(recordId);
        if (!record || !unitRecordIds.has(recordId) || !Number.isInteger(start) || !Number.isInteger(end) || start < 0 || end <= start || end > record.text.length) {
          throw new TypeError("A concordance hit has an invalid original-text span.");
        }
        return { recordId, start, end };
      });
      const firstSpan = spans[0], lastSpan = spans.at(-1);
      const first = index.byId.get(firstSpan.recordId), last = index.byId.get(lastSpan.recordId);
      const partition = index.partitionByRecord.get(first.id);
      if (spans.some((span, position) => index.partitionByRecord.get(span.recordId) !== partition
        || (position && (partition.positions.get(spans[position - 1].recordId) > partition.positions.get(span.recordId)
          || (spans[position - 1].recordId === span.recordId && spans[position - 1].end > span.start))))) {
        throw new TypeError("Concordance spans must be in source order within one text and book.");
      }
      const citedRecords = partition.records.slice(partition.positions.get(first.id), partition.positions.get(last.id) + 1);
      if (citedRecords.slice(1).some((record) => record.breakBefore)) throw new TypeError("A concordance phrase cannot cross a declared text gap.");
      const key = JSON.stringify(spans.map((span) => [span.recordId, span.start, span.end]));
      if (unique.has(key)) {
        unique.get(key).queryTexts = distinct([...unique.get(key).queryTexts, ...queryTexts(hit)]);
        continue;
      }

      const before = tokensFor(first).filter((token) => token.end <= firstSpan.start);
      const after = tokensFor(last).filter((token) => token.start >= lastSpan.end);
      const contextStart = contextWords === 0 ? firstSpan.start : before.length <= contextWords ? 0 : before[before.length - contextWords].start;
      // Include punctuation and whitespace following the final context word,
      // stopping at the next excluded word, not halfway through a token.
      const contextEnd = contextWords === 0 ? lastSpan.end : after.length <= contextWords ? last.text.length : after[contextWords].start;
      let joined = "";
      const placements = new Map();
      const contextSpans = [];
      for (const record of citedRecords) {
        const joinBefore = gapJoin(joined, record.text);
        joined += joinBefore;
        placements.set(record.id, joined.length);
        joined += record.text;
        contextSpans.push({ recordId: record.id, start: record.id === first.id ? contextStart : 0,
          end: record.id === last.id ? contextEnd : record.text.length, joinBefore });
      }
      const matchStart = placements.get(first.id) + firstSpan.start;
      const matchEnd = placements.get(last.id) + lastSpan.end;
      const displayedEnd = placements.get(last.id) + contextEnd;
      const editorialMarks = citedRecords.flatMap((record) => editorialMarksFor(record).flatMap((mark) => {
        const start = Math.max(contextStart, placements.get(record.id) + mark.start);
        const end = Math.min(displayedEnd, placements.get(record.id) + mark.end);
        return start < end ? [{ ...mark, start: start - contextStart, end: end - contextStart, text: joined.slice(start, end),
          sourceRecordId: record.id, sourceStart: mark.start, sourceEnd: mark.end, sourceText: mark.text }] : [];
      }));
      unique.set(key, {
        ...identity(first, group, result.scope, base),
        key, kind: hit.kind, citation: citationFor(citedRecords),
        sourceOrder: index.rank.get(first.id),
        left: joined.slice(contextStart, matchStart), match: joined.slice(matchStart, matchEnd),
        right: joined.slice(matchEnd, placements.get(last.id) + contextEnd),
        leftTruncated: contextStart > 0, rightTruncated: contextEnd < last.text.length,
        readerURL: readerURL(first, base),
        records: citedRecords, spans, queryTexts: queryTexts(hit), contextSpans, editorialMarks,
      });
    }
  }
  const order = (a, b) => index.rank.get(a.records[0].id) - index.rank.get(b.records[0].id)
    || (a.spans[0]?.start ?? -1) - (b.spans[0]?.start ?? -1)
    || (a.spans[0]?.end ?? -1) - (b.spans[0]?.end ?? -1);
  const rows = [...unique.values()].sort(order);
  unhighlightedUnits.sort(order);
  return {
    schemaVersion: CONCORDANCE_SCHEMA_VERSION, contextWords, rows, unhighlightedUnits, countKind,
    occurrenceCount: countKind === "evidence" ? null : rows.length, positiveCount: rows.length,
  };
}

const CSV_COLUMNS = [
  "citation", "left_context", "matched_text", "right_context", "edition", "language", "reader_url",
  "row_type", "match_kind", "count_kind", "occurrence_count", "positive_evidence_count", "matching_units",
  "matching_sections", "units_without_positive_hits", "work", "book", "collection_id", "book_id",
  "unit_id", "unit_label", "query", "query_json", "matched_query_operands_json", "scope", "spelling_equivalence",
  "selected_collection_ids_json", "selected_book_ids_json", "search_url", "exported_at_utc", "context_words",
  "left_truncated", "right_truncated", "record_ids_json", "source_segments_json", "hit_spans_json",
  "original_context_json", "offset_unit", "book_bundle_sha256", "book_corpus_sha256", "collection_corpus_sha256",
  "collection_manifest_sha256", "catalog_manifest_sha256", "engine_sha256", "engine_schema_version",
  "catalog_schema_version", "lunr_version", "concordance_schema_version", "selected_sources_json", "csv_cell_encoding", "escaped_columns_json",
];
const EDITORIAL_CSV_COLUMNS = ["citation_scheme", "left_context_editorial", "matched_text_editorial", "right_context_editorial", "editorial_notes"];
const EDITORIAL_LEGEND = "Editorial notation: [supplied text]; ⟦deleted text⟧; † unresolved text. Literal context columns retain all indexed letters.";

// Quoting alone does not prevent spreadsheet formula evaluation. Scalar cells
// beginning with a formula marker (including after whitespace/control chars),
// or with tab/CR/LF, receive one leading apostrophe. escaped_columns_json names
// exactly those cells; remove that one prefix to recover their original value.
// Original context, query, and source slices also have lossless JSON columns.
// JSON strings escape embedded controls and begin with a quote, bracket, or
// brace, so those recovery columns never need a formula-neutralizing prefix.
const needsFormulaEscape = (value) => /^[\t\r\n]/u.test(value) || /^[\s\u0000-\u001f\u007f-\u009f]*[=+\-@]/u.test(value);
function csvRow(values, columns = CSV_COLUMNS) {
  const escaped = [];
  const cells = columns.map((column) => {
    let value = String(values[column] ?? "");
    if (column !== "escaped_columns_json" && needsFormulaEscape(value)) {
      value = `'${value}`;
      escaped.push(column);
    }
    return value;
  });
  cells[columns.indexOf("escaped_columns_json")] = JSON.stringify(escaped);
  return cells.map((value) => `"${value.replace(/"/g, '""')}"`).join(",");
}

function exportedSegments(row) {
  if (row.kind === "matching-unit" && row.scope === "book") return [];
  const byId = new Map(row.records.map((record) => [record.id, record]));
  const spans = row.kind === "matching-unit"
    ? row.records.map((record) => ({ recordId: record.id, start: 0, end: record.text.length, joinBefore: "" }))
    : row.contextSpans;
  return spans.map((span) => {
    const record = byId.get(span.recordId);
    return { recordId: record.id, sourceId: record.sourceId ?? "", section: record.section,
      sourceURL: record.url ?? "", start: span.start, end: span.end, joinBefore: span.joinBefore,
      text: record.text.slice(span.start, span.end),
      ...(citationScheme(record) === "chapter-paragraph" || record.editorialMarks !== undefined ? { citationScheme: citationScheme(record), citationLabel: record.citationLabel,
        chapter: record.chapter, paragraph: record.paragraph,
        editorialMarks: editorialMarksFor(record, span.start, span.end).map((mark) => ({ ...mark })) } : {}),
    };
  });
}

/**
 * Export every model row, independently of display view or pagination.
 * metadata: {catalog, searchURL, exportedAt: Date|string}; exportedAt defaults
 * to the current time. Returns {text,mimeType,filename,rowCount}.
 *
 * The CSV has a UTF-8 BOM and CRLF record delimiters. Embedded original source
 * line endings stay unchanged inside quoted cells. A NOT-only book contributes
 * one matching-unit row with its identity, fingerprints, and reader link;
 * source_segments_json is empty because there is no occurrence excerpt. A
 * NOT-only section additionally retains its complete original section text.
 * A zero-result export has one search-summary row to retain the query settings.
 * selected_sources_json on the first data row records fingerprints for every
 * searched source, including books with no matches; it is not repeated on
 * subsequent rows. Individual result rows also identify their own source.
 */
export function exportConcordance(model, result, metadata = {}) {
  const exportedAt = new Date(metadata.exportedAt ?? Date.now()).toISOString();
  const catalog = metadata.catalog || {};
  const collections = new Map((catalog.collections || []).map((entry) => [entry.id, entry]));
  const books = new Map((catalog.books || []).map((entry) => [entry.id, entry]));
  const allRows = [...model.rows, ...model.unhighlightedUnits];
  const selectedCollections = result.selectedCollections ?? distinct(allRows.map((row) => row.collectionId).filter(Boolean));
  const selectedBooks = result.selectedBooks ?? distinct(allRows.map((row) => row.bookId).filter(Boolean));
  const includeEditorialColumns = selectedCollections.some((id) => collections.get(id)?.citationScheme === "chapter-paragraph")
    || allRows.some((row) => row.citationScheme === "chapter-paragraph" || row.editorialMarks?.length)
    || (result.records || []).some((record) => citationScheme(record) === "chapter-paragraph" || record.editorialMarks?.length);
  // Keep the accepted 51-column contract for Bellum-only exports. Extended
  // exports explicitly identify both citation systems and editorial rendering.
  const columns = includeEditorialColumns ? [...CSV_COLUMNS.slice(0, 7), ...EDITORIAL_CSV_COLUMNS, ...CSV_COLUMNS.slice(7)] : CSV_COLUMNS;
  const selectedSources = JSON.stringify({
    collections: (catalog.collections || []).filter((entry) => selectedCollections.includes(entry.id)).map((entry) => ({
      id: entry.id, work: entry.work, language: entry.language, edition: entry.edition,
      corpusPath: entry.corpusPath, corpusSHA256: entry.corpusSHA256, manifestSHA256: entry.manifestSHA256,
      ...(includeEditorialColumns ? { citationScheme: citationScheme(entry), unitLabel: entry.unitLabel || "Niese section", unitLabelPlural: entry.unitLabelPlural || "Niese sections" } : {}),
    })),
    books: (catalog.books || []).filter((entry) => selectedBooks.includes(entry.id)).map((entry) => ({
      id: entry.id, collectionId: entry.collectionId, number: entry.number,
      path: entry.path, sha256: entry.sha256, corpusPath: entry.corpusPath, corpusSHA256: entry.corpusSHA256,
    })),
  });
  const common = {
    count_kind: model.countKind, occurrence_count: model.occurrenceCount ?? "", positive_evidence_count: model.positiveCount,
    matching_units: result.matchingUnits, matching_sections: result.matchingSections,
    units_without_positive_hits: model.unhighlightedUnits.length,
    query: result.query, query_json: JSON.stringify(result.query), scope: result.scope,
    spelling_equivalence: result.fold ? "u/v and i/j equivalent" : "original spelling",
    selected_collection_ids_json: JSON.stringify(selectedCollections), selected_book_ids_json: JSON.stringify(selectedBooks),
    search_url: metadata.searchURL ? String(metadata.searchURL) : "", exported_at_utc: exportedAt, context_words: model.contextWords,
    offset_unit: "UTF-16 code units; start inclusive, end exclusive",
    catalog_manifest_sha256: catalog.source?.manifestSHA256, engine_sha256: catalog.source?.engineSHA256,
    engine_schema_version: catalog.engineSchemaVersion, catalog_schema_version: catalog.schemaVersion,
    lunr_version: catalog.source?.lunrVersion, concordance_schema_version: model.schemaVersion,
    csv_cell_encoding: "apostrophe-prefix-for-formula-like-cells-v1; see escaped_columns_json",
  };
  // The source records remain shared references in the model. Only the short
  // displayed source slices are serialized per occurrence, not entire sections.
  const order = (row) => row.sourceOrder ?? row.records[0].resultOrder ?? row.records[0].order ?? 0;
  allRows.sort((a, b) => order(a) - order(b) || (a.spans[0]?.start ?? -1) - (b.spans[0]?.start ?? -1));
  const body = allRows.map((row, rowIndex) => {
    const collection = collections.get(row.collectionId);
    const book = books.get(row.bookId || `${row.collectionId}:${row.book}`);
    const segments = exportedSegments(row);
    const markedText = { text: row.left + row.match + row.right, editorialMarks: row.editorialMarks || [] };
    const marks = row.kind === "matching-unit" ? segments.flatMap((segment) => segment.editorialMarks || []) : markedText.editorialMarks;
    const editorialKinds = distinct(marks.map((mark) => ({ del: "deleted", supplied: "supplied", unclear: "unresolved" })[mark.kind]));
    return csvRow({
      ...common,
      citation: row.citation, left_context: row.left, matched_text: row.match, right_context: row.right,
      edition: row.edition, language: row.language, reader_url: row.readerURL,
      citation_scheme: row.citationScheme || "niese",
      left_context_editorial: editorialText(markedText, 0, row.left.length),
      matched_text_editorial: editorialText(markedText, row.left.length, row.left.length + row.match.length),
      right_context_editorial: editorialText(markedText, row.left.length + row.match.length, markedText.text.length),
      editorial_notes: editorialKinds.length ? `This excerpt includes ${editorialKinds.join(", ")} text. ${EDITORIAL_LEGEND}` : (includeEditorialColumns && rowIndex === 0 ? EDITORIAL_LEGEND : ""),
      row_type: row.kind === "matching-unit" ? "matching-unit" : model.countKind === "evidence" ? "positive-evidence" : "occurrence",
      match_kind: row.kind === "matching-unit" ? "" : row.kind,
      work: row.work, book: row.book, collection_id: row.collectionId, book_id: row.bookId,
      unit_id: row.unitId, unit_label: row.unitLabel, matched_query_operands_json: JSON.stringify(row.queryTexts),
      left_truncated: row.leftTruncated, right_truncated: row.rightTruncated,
      record_ids_json: JSON.stringify(row.records.map((record) => record.id)), source_segments_json: JSON.stringify(segments),
      hit_spans_json: JSON.stringify(row.spans), original_context_json: JSON.stringify({ left: row.left, match: row.match, right: row.right }),
      book_bundle_sha256: book?.sha256, book_corpus_sha256: book?.corpusSHA256,
      collection_corpus_sha256: collection?.corpusSHA256, collection_manifest_sha256: collection?.manifestSHA256,
      selected_sources_json: rowIndex === 0 ? selectedSources : "",
    }, columns);
  });
  if (!body.length) body.push(csvRow({ ...common, row_type: "search-summary", selected_sources_json: selectedSources,
    ...(includeEditorialColumns ? { editorial_notes: EDITORIAL_LEGEND } : {}) }, columns));
  return {
    text: `\uFEFF${columns.map((value) => `"${value}"`).join(",")}\r\n${body.join("\r\n")}\r\n`,
    mimeType: "text/csv;charset=utf-8", filename: `LatinJosephus-search-${exportedAt.slice(0, 10)}.csv`, rowCount: allRows.length,
  };
}
