(() => {
  const directory = document.querySelector('[data-conditions]');
  if (!directory) return;

  const controls = directory.querySelector('[data-condition-controls]');
  const search = directory.querySelector('#condition-search');
  const hasData = directory.querySelector('[data-condition-data]');
  const status = directory.querySelector('[data-condition-status]');
  const groups = Array.from(directory.querySelectorAll('[data-condition-group]'), group => {
    const entries = Array.from(group.querySelectorAll('[data-condition-entry]'));
    return { group, entries, jump: directory.querySelector(`a[href="#${group.id}"]`) };
  });

  function normalise(text) {
    return text.toLowerCase().normalize('NFD').replace(/\p{M}/gu, '').replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  }

  function filterTopics() {
    const terms = normalise(search.value).split(' ').filter(Boolean);
    let count = 0;
    for (const { group, entries, jump } of groups) {
      let groupCount = 0;
      for (const entry of entries) {
        const name = normalise(entry.dataset.search);
        const visible = terms.every(term => name.includes(term)) && (!hasData.checked || entry.dataset.hasEvidence === 'yes');
        entry.hidden = !visible;
        if (visible) groupCount++;
      }
      group.hidden = jump.hidden = groupCount === 0;
      count += groupCount;
    }
    status.textContent = terms.length || hasData.checked
      ? count ? `${count} matching ${count === 1 ? 'listing' : 'listings'}` : 'No matching topics. Try another term or clear the Irish data filter.'
      : '';
  }

  search.addEventListener('input', filterTopics);
  hasData.addEventListener('change', filterTopics);
  window.addEventListener('pageshow', filterTopics);
  controls.hidden = false;
  filterTopics();
})();
