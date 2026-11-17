import {sha256} from './milletCore.js?v=20261117-modernised';

export function createModernisedMilletLoader(base, fetcher = fetch) {
  let manifestRequest;
  const books = new Map();

  function manifest() {
    manifestRequest ??= (async () => {
      const response = await fetcher(new URL('manifest.json', base));
      if (!response.ok) throw new Error('Modernised Millet catalogue unavailable.');
      const catalogue = await response.json();
      if (catalogue.schema !== 'millet1556-modernised-reader/1') throw new Error('Unsupported modernised Millet catalogue.');
      return catalogue;
    })().catch(error => {
      manifestRequest = null;
      throw error;
    });
    return manifestRequest;
  }

  return async (number, historicalRelease) => {
    const catalogue = await manifest();
    if (catalogue.historical_release !== historicalRelease) throw new Error('Modernised Millet and the historical source do not match.');
    const record = catalogue.books.find(entry => entry.book === number);
    if (!record) throw new Error('Modernised Millet book unavailable.');
    if (!books.has(number)) {
      books.set(number, (async () => {
        const response = await fetcher(new URL(record.path, base));
        if (!response.ok) throw new Error('Modernised Millet book unavailable.');
        const bytes = await response.arrayBuffer();
        if (await sha256(bytes) !== record.sha256) throw new Error('Modernised Millet integrity check failed.');
        const book = JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(bytes));
        if (book.book !== number || book.schema !== 'millet1556-modernised-book/1') throw new Error('Unexpected modernised Millet book data.');
        return book;
      })().catch(error => {
        books.delete(number);
        throw error;
      }));
    }
    return books.get(number);
  };
}

export function modernisedMilletSelection(book, mode, view) {
  if (view.included) {
    return book.passages.filter(passage => Object.keys(passage.correspondences).some(id => view.included.has(id)));
  }
  if (mode === 'running' || mode === 'book') return book.passages;
  const lines = new Set(view.lines.map(line => line.TEI_line_id));
  return book.passages.filter(passage => passage.lines.some(line => lines.has(line)));
}
