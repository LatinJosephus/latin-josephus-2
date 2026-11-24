(() => {
  const root = document.getElementById('ljm-manuscripts');
  if (!root) return;

  const form = root.querySelector('.ljm-filters');
  const { query, work, online } = form.elements;
  const groups = [...root.querySelectorAll('.ljm-record-group')];
  const counter = root.querySelector('.ljm-result-count');
  const empty = root.querySelector('.ljm-empty');
  const fold = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const entries = [...root.querySelectorAll('tbody tr')].map(row => {
    const code = row.querySelector('.ljm-ms-id')?.textContent || '';
    return { row, searchText: fold(row.dataset.search + ' ' + code) };
  });

  function filter() {
    const terms = fold(query.value).trim().split(/\s+/).filter(Boolean);
    for (const { row, searchText } of entries) {
      const data = row.dataset;
      const matchesText = terms.every(term => searchText.includes(term));
      const matchesWork = !work.value || data.work.split(' ').includes(work.value);
      const matchesOnline = !online.value ||
        (online.value === 'none' ? data.linked === '0' : data[online.value] === '1');
      row.hidden = !(matchesText && matchesWork && matchesOnline);
    }

    const [main, related] = groups.map(group => {
      const count = group.querySelectorAll('tbody tr:not([hidden])').length;
      group.hidden = count === 0;
      return count;
    });
    const mainLabel = main === 1 ? 'manuscript record' : 'manuscript records';
    const relatedLabel = related === 1 ? 'related epitome witness' : 'related epitome witnesses';
    counter.textContent = main + ' ' + mainLabel + ' · ' + related + ' ' + relatedLabel;
    empty.hidden = main + related !== 0;
  }

  function revealLinkedRow() {
    const target = document.getElementById(location.hash.slice(1));
    const row = target?.closest('tbody tr[data-search]');
    if (!row || !root.contains(row) || !row.hidden) return;

    form.reset();
    filter();
    target.scrollIntoView({ block: 'start' });
  }

  query.addEventListener('input', filter);
  work.addEventListener('change', filter);
  online.addEventListener('change', filter);
  form.addEventListener('reset', () => setTimeout(filter, 0));
  window.addEventListener('hashchange', revealLinkedRow);
  filter();
  revealLinkedRow();
})();
