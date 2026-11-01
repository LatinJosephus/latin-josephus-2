/* Lauro diplomatic coordinates stay independent of chapters and display flow. */
export const MODES = new Set(['running', 'book', 'source', 'chapter', 'page']);
export const codepoints = text => Array.from(text);
export function utf16Offset(text, cp) {
  const chars = codepoints(text);
  if (!Number.isSafeInteger(cp) || cp < 0 || cp > chars.length) throw new Error('Invalid Lauro codepoint offset.');
  return chars.slice(0, cp).join('').length;
}
export const canonicalIds = mapping => mapping.canonical_targets?.map(c => c.xml_id) || (mapping.canonical ? [mapping.canonical.xml_id] : []);

function checkSpan(line, fragment) {
  if (!line || !Number.isSafeInteger(fragment.start_cp) || !Number.isSafeInteger(fragment.end_cp)
    || fragment.start_cp < 0 || fragment.end_cp <= fragment.start_cp || fragment.end_cp > codepoints(line.text_exact).length
    || utf16Offset(line.text_exact, fragment.start_cp) !== fragment.start_utf16
    || utf16Offset(line.text_exact, fragment.end_cp) !== fragment.end_utf16) throw new Error('Invalid Lauro source span or coordinate conversion.');
}

export function validateBook(data) {
  if (data?.schema !== 'lauro1544-reader-book/1' || !Number.isInteger(data.book) || data.book < 1 || data.book > 5
    || typeof data.version !== 'string' || !data.version) throw new Error('Unsupported Lauro book data.');
  for (const key of ['lines', 'mappings', 'annotations', 'divisions', 'pages']) if (!Array.isArray(data[key])) throw new Error('Incomplete Lauro book data.');
  const lines = new Map(), ids = new Set(), mappings = new Map(), annotationIds = new Set();
  for (const line of data.lines) {
    if (typeof line.TEI_line_id !== 'string' || !line.TEI_line_id || typeof line.text_exact !== 'string'
      || lines.has(line.TEI_line_id) || !Number.isSafeInteger(line.source_index)
      || !Number.isSafeInteger(line.image_number) || line.image_number < 1 || line.image_number > 417) throw new Error('Invalid or duplicate Lauro source line.');
    lines.set(line.TEI_line_id, line);
  }
  for (const mapping of data.mappings) {
    if (typeof mapping.id !== 'string' || !mapping.id || mappings.has(mapping.id) || !Array.isArray(mapping.fragments)) throw new Error('Duplicate or malformed Lauro mapping.');
    const targets = canonicalIds(mapping);
    if (!targets.length) throw new Error('Lauro mapping has no canonical target.');
    for (const id of targets) {
      if (!/^latin-deh[1-5]-num[1-9]\d*$/.test(id)) throw new Error('Invalid canonical Lauro target.');
      ids.add(id);
    }
    if (!mapping.fragments.length && mapping.relation !== 'absent') throw new Error('Unexplained empty Lauro correspondence.');
    mapping.fragments.forEach(fragment => checkSpan(lines.get(fragment.line), fragment));
    mappings.set(mapping.id, mapping);
  }
  for (const annotation of data.annotations) {
    if (typeof annotation.id !== 'string' || !annotation.id || annotationIds.has(annotation.id)
      || annotation.primary_coverage !== false) throw new Error('Invalid secondary Lauro annotation.');
    annotationIds.add(annotation.id);
    (annotation.fragments || []).forEach(fragment => checkSpan(lines.get(fragment.line), fragment));
  }
  const pageIds = new Set(), divisionIds = new Set();
  for (const page of data.pages) {
    if (!Number.isSafeInteger(page.image_number) || page.image_number < 1 || page.image_number > 417 || pageIds.has(page.image_number)) throw new Error('Invalid Lauro page.');
    pageIds.add(page.image_number);
  }
  for (const division of data.divisions) {
    if (typeof division.id !== 'string' || divisionIds.has(division.id) || !Array.isArray(division.line_refs)
      || division.line_refs.some(id => !lines.has(id))) throw new Error('Invalid Lauro native division.');
    if (division.is_native_chapter && !Number.isSafeInteger(division.chapter_start_index)) throw new Error('Invalid Lauro chapter boundary.');
    divisionIds.add(division.id);
  }
  return {lines, mappings, canonicalIds: ids};
}

export function indexBook(data) {
  const checked = validateBook(data), byCanonical = new Map(), byLine = new Map();
  for (const mapping of data.mappings) {
    for (const id of canonicalIds(mapping)) {
      if (!byCanonical.has(id)) byCanonical.set(id, []);
      byCanonical.get(id).push(mapping);
    }
    for (const fragment of mapping.fragments) {
      if (!byLine.has(fragment.line)) byLine.set(fragment.line, []);
      byLine.get(fragment.line).push({...fragment, mapping: mapping.id});
    }
  }
  return {...checked, byCanonical, byLine};
}

// Every source character appears once even where links or annotations overlap.
export function lineAtoms(line, fragments = [], annotations = []) {
  [...fragments, ...annotations].forEach(fragment => checkSpan(line, fragment));
  const length = codepoints(line.text_exact).length;
  const boundaries = [...new Set([0, length, ...fragments.flatMap(f => [f.start_cp, f.end_cp]), ...annotations.flatMap(f => [f.start_cp, f.end_cp])])].sort((a, b) => a - b);
  return boundaries.slice(0, -1).map((start, i) => {
    const end = boundaries[i + 1];
    return {start_cp: start, end_cp: end, start_utf16: utf16Offset(line.text_exact, start), end_utf16: utf16Offset(line.text_exact, end),
      text: codepoints(line.text_exact).slice(start, end).join(''),
      mappings: [...new Set(fragments.filter(f => f.start_cp <= start && f.end_cp >= end).map(f => f.mapping))],
      annotations: [...new Set(annotations.filter(f => f.start_cp <= start && f.end_cp >= end).map(f => f.annotation))]};
  });
}

export function visibleLines(data, {mode = 'running', chapter = null, page = null} = {}) {
  if (mode === 'page') return data.lines.filter(line => line.image_number === Number(page));
  if (mode === 'chapter') {
    const chapters = data.divisions.filter(d => d.is_native_chapter);
    const i = chapters.findIndex(d => d.id === chapter);
    if (i < 0) return [];
    const start = chapters[i].chapter_start_index, end = chapters[i + 1]?.chapter_start_index ?? Infinity;
    return data.lines.filter(line => line.source_index >= start && line.source_index < end && (line.primary || line.source_region_type === 'heading'));
  }
  if (mode === 'source') return data.lines;
  const range = data.native?.narrative_image_range;
  const headingLines = new Set(data.divisions.filter(d => d.is_native_chapter || (range && d.image_number >= range[0] && d.image_number <= range[1])).flatMap(d => d.line_refs));
  return data.lines.filter(line => line.primary || headingLines.has(line.TEI_line_id));
}
export const chapterMappings = (data, chapter) => data.mappings.filter(mapping => (mapping.canonical_targets || [mapping.canonical]).some(c => String(c.chapter) === String(chapter)));
export function readingView(data, view, navigation, canonical) {
  const lines = visibleLines(data, view);
  if (view.mode !== 'running' || !['section-level', 'chapter-level'].includes(navigation.level)) return {lines, included: null};
  const mappings = navigation.level === 'chapter-level' ? chapterMappings(data, navigation.chapter) : data.mappings.filter(m => canonicalIds(m).includes(canonical));
  if (!mappings.length) return {lines: [], included: new Set()};
  const ids = new Set(mappings.flatMap(mapping => mapping.fragments.map(fragment => fragment.line)));
  return {lines: lines.filter(line => ids.has(line.TEI_line_id)), included: new Set(mappings.map(mapping => mapping.id))};
}

// Reading flow changes visibility only. Source/page views use the full literals.
export function flowSeparator(previous, next) {
  return !previous || /¬\s*$/.test(previous) || /\s$/.test(previous) || /^\s/.test(next) ? '' : ' ';
}
export function readingParts(text, start = 0, end = text.length) {
  const tail = text.search(/¬\s*$/); let offset = start;
  return text.slice(start, end).split(/(¬)/).map(part => {
    const entry = {text: part, hidden: part === '¬' || (tail >= 0 && offset >= tail)};
    offset += part.length;
    return entry;
  });
}
export function flowGroups(lines) {
  const groups = []; let last;
  for (const line of lines) {
    const same = last && last.source_region_type === line.source_region_type && last.region_id === line.region_id && last.image_number === line.image_number;
    const pageContinuation = last && last.image_number !== line.image_number && last.source_region_type === 'paragraph' && line.source_region_type === 'paragraph';
    const continuedWord = last && last.source_region_type === line.source_region_type && /¬\s*$/.test(last.text_exact);
    if (!same && !pageContinuation && !continuedWord) groups.push({type: line.source_region_type, lines: []});
    groups.at(-1).lines.push(line); last = line;
  }
  return groups;
}
// Presentation only: source strings and their one-codepoint coordinates stay exact.
export const readerText = text => text.replaceAll('ſ', 's');
export function editorialLabel(annotation) {
  const text = annotation.title || (typeof annotation.original === 'string' ? annotation.original
    : /suppl/i.test(annotation.kind || annotation.annotation_kind || '') ? 'Bracketed letters are editorially supplied.' : 'Editorial annotation.');
  return readerText(text.replace('; it is not certified as printed.', '.'));
}
// User-supplied anchors: images 3=2r, 29=15r and 417=209r.
export function folioLabel(image) {
  if (!Number.isSafeInteger(image) || image < 1 || image > 417) throw new Error('Invalid Lauro image number.');
  return `f. ${Math.ceil(image / 2)}${image % 2 ? 'r' : 'v'}`;
}
export function folioLabels(data) {
  return new Map(data.pages.map(page => [page.image_number, folioLabel(page.image_number)]));
}

const URL_KEYS = ['italian', 'lauro-view', 'lauro-chapter', 'lauro-page', 'lauro-unit', 'lauro-align', 'lauro-folios', 'lauro-select'];
export function locationFromUrl(url) {
  const p = new URL(url).searchParams;
  return {enabled: p.get('italian') === 'lauro1544', mode: MODES.has(p.get('lauro-view')) ? p.get('lauro-view') : 'running',
    chapter: p.get('lauro-chapter'), page: p.get('lauro-page'), canonical: p.get('lauro-unit'), alignment: p.get('lauro-align') !== '0', folios: p.get('lauro-folios') === '1'};
}
export function updateLauroUrl(url, state) {
  const u = new URL(url);
  URL_KEYS.forEach(key => u.searchParams.delete(key));
  if (!state.enabled) return u;
  if (!MODES.has(state.mode)) throw new Error('Invalid Lauro viewing mode.');
  u.searchParams.set('italian', 'lauro1544');
  if (state.mode !== 'running') u.searchParams.set('lauro-view', state.mode);
  if (state.mode === 'chapter' && state.chapter) u.searchParams.set('lauro-chapter', state.chapter);
  if (state.mode === 'page' && state.page) u.searchParams.set('lauro-page', state.page);
  if (state.canonical) u.searchParams.set('lauro-unit', state.canonical);
  if (!state.alignment) u.searchParams.set('lauro-align', '0');
  if (state.folios) u.searchParams.set('lauro-folios', '1');
  return u;
}
export async function sha256(bytes) {
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)].map(n => n.toString(16).padStart(2, '0')).join('');
}
export function createLauroLoader(base, fetcher = fetch) {
  let manifestPromise; const cache = new Map();
  const manifest = () => manifestPromise ||= (async () => {
    const response = await fetcher(new URL('manifest.json', base));
    if (!response.ok) throw new Error('The Lauro source catalogue is unavailable.');
    const data = await response.json();
    if (data.schema !== 'lauro1544-reader/1' || !['LOCAL_PREVIEW_READY', 'INTEGRATION_READY'].includes(data.authority?.status)
      || typeof data.version !== 'string' || !data.version || !Array.isArray(data.books)
      || data.books.length !== 5 || new Set(data.books.map(book => book.book)).size !== 5
      || data.books.some(book => ![1, 2, 3, 4, 5].includes(book.book) || typeof book.path !== 'string' || !/^book-0[1-5]\.json$/.test(book.path) || !/^[a-f0-9]{64}$/.test(book.sha256))) throw new Error('The Lauro source catalogue has not passed integration checks.');
    return data;
  })().catch(error => { manifestPromise = null; throw error; });
  const book = async number => {
    const m = await manifest(), key = Number(number), record = m.books.find(item => item.book === key);
    if (!record) throw new Error('This Lauro book is unavailable.');
    if (!cache.has(key)) cache.set(key, (async () => {
      const response = await fetcher(new URL(record.path, base));
      if (!response.ok) throw new Error('The Lauro book is unavailable.');
      const bytes = await response.arrayBuffer();
      if (await sha256(bytes) !== record.sha256) throw new Error('Lauro book integrity check failed.');
      const data = JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(bytes));
      if (data.book !== key || data.version !== m.version) throw new Error('Stale Lauro book data.');
      validateBook(data);
      return data;
    })().catch(error => { cache.delete(key); throw error; }));
    return cache.get(key);
  };
  return {manifest, book};
}
