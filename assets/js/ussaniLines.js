// Printed positions are an independent display layer; canonical TEI is unchanged.
const checkbox = document.getElementById('ussani-line-numbers');
const pane = document.getElementById('latin');
if (checkbox && pane) {
  const requests = new Map();
  let generation = 0;
  let visibleMarkers = 0;
  const applyVisibility = () => pane.classList.toggle('ussani-lines-visible', checkbox.checked && visibleMarkers > 0);
  const readPreference = () => {
    const param = new URL(location.href).searchParams.get('ussaniLines');
    try { checkbox.checked = param !== null ? param === '1' : localStorage.getItem('deh-ussani-line-numbers') === '1'; }
    catch (_) { checkbox.checked = param === '1'; }
    applyVisibility();
  };
  readPreference();
  checkbox.addEventListener('change', () => {
    try { localStorage.setItem('deh-ussani-line-numbers', checkbox.checked ? '1' : '0'); } catch (_) {}
    const url = new URL(location.href);
    if (checkbox.checked) url.searchParams.set('ussaniLines', '1');
    else url.searchParams.delete('ussaniLines');
    history.replaceState({}, '', url);
    applyVisibility();
  });
  window.addEventListener('popstate', readPreference);
  const load = book => {
    if (![1,2,3,4,5].includes(book)) return Promise.resolve(null);
    if (!requests.has(book)) requests.set(book, fetch(new URL(`../data/deh-ussani-lines/book-${String(book).padStart(2,'0')}.json?v=20261122-full`, import.meta.url))
      .then(response => { if (!response.ok) throw new Error('Printed line positions unavailable'); return response.json(); })
      .then(data => {
        if (data.schema !== 1 || data.book !== book || data.status !== 'verified') throw new Error('Invalid printed line map');
        return data;
      }).catch(error => { requests.delete(book); console.warn(error.message); return null; }));
    return requests.get(book);
  };
  const textNodes = paragraph => {
    const nodes = [];
    const walker = document.createTreeWalker(paragraph, NodeFilter.SHOW_TEXT, node =>
      node.parentElement.closest('tei-num, [data-original], a, button, tei-note, tei-unclear, .ussani-line-number, .text-annotations')
        ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT);
    let node, offset = 0;
    while ((node = walker.nextNode())) {
      nodes.push({node,start:offset,end:offset+node.data.length});
      offset += node.data.length;
    }
    return nodes;
  };
  const hash = async text => [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))]
    .map(byte => byte.toString(16).padStart(2,'0')).join('');
  document.addEventListener('deh-view-rendered', async event => {
    const mine = ++generation;
    pane.dataset.ussaniLineStatus = 'loading';
    checkbox.disabled = true;
    const data = await load(Number(event.detail.book));
    if (mine !== generation) return;
    visibleMarkers = 0;
    pane.querySelectorAll('.ussani-line-number').forEach(marker => marker.remove());
    pane.dataset.ussaniLineStatus = 'loading';
    for (const paragraph of pane.querySelectorAll('tei-p[id]')) {
      const record = data?.paragraphs[paragraph.id];
      if (!record) continue;
      const nodes = textNodes(paragraph);
      const text = nodes.map(({node}) => node.data).join('');
      // Do not apply a citation offset to a changed or differently rendered text.
      if (text.length !== record.length || await hash(text) !== record.sha256) {
        paragraph.dataset.ussaniLineStatus = 'text-mismatch';
        continue;
      }
      if (mine !== generation || !pane.contains(paragraph)) return;
      for (const position of [...record.lines].sort((a,b) => b.offset-a.offset)) {
        if (!Number.isInteger(position.offset) || position.offset < 0 || position.offset >= text.length) continue;
        const entry = nodes.find(({start,end}) => position.offset >= start && position.offset < end);
        if (!entry) continue;
        const marker = document.createElement('span');
        marker.className = 'ussani-line-number';
        marker.dataset.line = String(position.line);
        marker.dataset.page = String(position.page);
        marker.setAttribute('role','note');
        marker.setAttribute('aria-label',`Ussani p. ${position.page}, line ${position.line}`);
        marker.title = `Ussani p. ${position.page}, line ${position.line}`;
        entry.node.splitText(position.offset-entry.start).before(marker);
        visibleMarkers++;
      }
      paragraph.dataset.ussaniLineStatus = 'verified';
    }
    if (mine !== generation) return;
    checkbox.disabled = !data;
    pane.dataset.ussaniLineStatus = data ? 'ready' : 'unavailable';
    applyVisibility();
  });
}
