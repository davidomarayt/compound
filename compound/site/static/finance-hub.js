/* Optional search enhancement. All catalogue entries and source links remain in HTML without JS. */
(() => {
  const search = document.querySelector('[data-finance-search]');
  const output = document.querySelector('[data-finance-results]');
  const empty = document.querySelector('[data-finance-empty]');
  const groups = [...document.querySelectorAll('[data-finance-group]')];
  if (!search || !output || !groups.length) return;

  const normalise = (value) => String(value || '').normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().trim();
  const collections = groups.map(group => ({
    group,
    name: normalise(group.querySelector('.finance-library-group-title strong')?.textContent),
    items: [...group.querySelectorAll('[data-finance-item]')].map(node => ({
      node,
      content: normalise(node.textContent)
    }))
  }));
  const total = collections.reduce((sum, group) => sum + group.items.length, 0);

  function update() {
    const term = normalise(search.value);
    let count = 0;
    collections.forEach(({group, name, items}) => {
      let groupCount = 0;
      const wholeGroup = term && name.includes(term);
      items.forEach(({node, content}) => {
        const matches = !term || wholeGroup || content.includes(term);
        node.hidden = !matches;
        if (matches) groupCount++;
      });
      count += groupCount;
      group.hidden = !!term && groupCount === 0;
      if (term) group.open = groupCount > 0;
      else group.open = false;
    });
    output.textContent = term
      ? count + (count === 1 ? ' matching resource' : ' matching resources')
      : total + ' resources in the catalogue';
    if (empty) empty.hidden = count !== 0;
  }

  search.addEventListener('input', update);
  search.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && search.value) {
      search.value = '';
      update();
      event.preventDefault();
    }
  });
})();
