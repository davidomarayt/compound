(function () {
  'use strict';
  const finder = document.querySelector('[data-wealth-tool-finder]');
  if (!finder) return;
  const input = finder.querySelector('[data-wealth-search]');
  const results = finder.querySelector('[data-wealth-results]');
  const status = finder.querySelector('[data-wealth-search-status]');
  if (!input || !results || !status) return;

  const normalize = (value) => String(value || '').toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  const priority = ['/pia-calculator/', '/compound-interest-calculator/', '/mortgage-calculator/',
    '/take-home-pay-calculator/', '/budget-2027-calculator/', '/net-worth-calculator/'];

  // Keep a link to each tool in the server-rendered sections for SEO and no-JS visitors.
  // Build quick-search options from those links so adding new Wealth tools is automatic.
  const tools = [];
  const seen = new Set();
  document.querySelectorAll('.wealth-category-tools a[href*="calculator"]').forEach((anchor) => {
    const href = anchor.getAttribute('href');
    if (!href || !href.startsWith('/') || seen.has(href)) return;
    const title = anchor.querySelector('h3')?.textContent?.trim() || anchor.textContent.trim();
    const category = anchor.closest('.wealth-category-section')?.querySelector('.wealth-category-header .eyebrow')?.textContent?.trim() || 'Financial calculator';
    const summary = anchor.querySelector('p')?.textContent?.trim() || '';
    if (!title) return;
    seen.add(href);
    tools.push({ href, title, category, summary,
      search: normalize([title, category, summary, href.replaceAll('-', ' ')].join(' ')) });
  });
  const sorted = [...tools].sort((a, b) => {
    const ar = priority.indexOf(a.href), br = priority.indexOf(b.href);
    return (ar < 0 ? 999 : ar) - (br < 0 ? 999 : br) || a.title.localeCompare(b.title);
  });
  const create = (tag, className, value) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (value != null) element.textContent = value;
    return element;
  };
  const render = () => {
    const query = normalize(input.value);
    const words = query.split(' ').filter(Boolean);
    const matches = words.length ? sorted.filter((item) => words.every((word) => item.search.includes(word))) : sorted;
    const shown = matches.slice(0, words.length ? 9 : 6);
    const fragment = document.createDocumentFragment();
    shown.forEach((item) => {
      const link = create('a');
      link.href = item.href;
      const copy = create('span', 'wealth-v2-result-copy', item.title);
      copy.append(create('small', '', item.category));
      link.append(copy, create('span', 'wealth-v2-result-arrow', '↗'));
      link.querySelector('.wealth-v2-result-arrow').setAttribute('aria-hidden', 'true');
      fragment.append(link);
    });
    if (!matches.length) fragment.append(create('p', 'wealth-v2-no-results', 'No matching calculator found. Try a broader term or browse all tools.'));
    results.replaceChildren(fragment);
    status.textContent = words.length
      ? matches.length + (matches.length === 1 ? ' calculator found' : ' calculators found') +
        (matches.length > shown.length ? ' · showing the first ' + shown.length : '')
      : 'Popular calculators · search ' + sorted.length + ' financial tools';
  };
  input.addEventListener('input', render);
  render();
})();
