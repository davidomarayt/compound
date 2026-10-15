/* Search verified earnings without rendering hundreds of cards on initial load. */
(function () {
  'use strict';
  const input = document.querySelector('[data-earnings-report-search]');
  const indexElement = document.querySelector('[data-earnings-report-index]');
  const recent = document.querySelector('[data-earnings-recent]');
  const results = document.querySelector('[data-earnings-report-results]');
  const status = document.querySelector('[data-earnings-report-status]');
  if (!input || !indexElement || !recent || !results || !status) return;

  let archive;
  try {
    archive = JSON.parse(indexElement.textContent);
  } catch (_) {
    status.textContent = 'Search is temporarily unavailable. Browse all companies below.';
    input.disabled = true;
    return;
  }
  if (!Array.isArray(archive)) return;
  const limit = 12;
  const normalise = value => String(value || '').normalize('NFKC').toLocaleLowerCase('en-IE');

  function cardFor(entry) {
    if (!/^\/stocks\/[a-z0-9-]+\/$/.test(entry.url)) return null;
    const article = document.createElement('article');
    article.className = 'earnings-card';
    const kicker = document.createElement('p');
    kicker.className = 'earnings-kicker';
    kicker.textContent = 'SEC-VERIFIED FINANCIAL REPORT · FILED ' + (entry.filed || 'Date unavailable');
    const heading = document.createElement('h3');
    const headingLink = document.createElement('a');
    headingLink.href = entry.url;
    headingLink.textContent = entry.name + ' (' + entry.ticker + ')';
    heading.appendChild(headingLink);
    const detail = document.createElement('p');
    detail.textContent = entry.period + ' · Period ended ' + entry.ended;
    const link = document.createElement('a');
    link.className = 'earnings-read';
    link.href = entry.url;
    link.textContent = 'Open company earnings →';
    article.append(kicker, heading, detail, link);
    return article;
  }

  function update() {
    const query = normalise(input.value.trim());
    const searching = Boolean(query);
    recent.hidden = searching;
    results.hidden = !searching;
    results.replaceChildren();
    if (!searching) {
      status.textContent = 'Showing ' + recent.querySelectorAll('[data-earnings-recent-card]').length +
        ' latest filings. Search to find earlier company reports.';
      return;
    }
    const matches = archive.filter(entry =>
      normalise(entry.name).includes(query) || normalise(entry.ticker).includes(query));
    const fragment = document.createDocumentFragment();
    for (const entry of matches.slice(0, limit)) {
      const card = cardFor(entry);
      if (card) fragment.appendChild(card);
    }
    results.appendChild(fragment);
    status.textContent = matches.length === 0
      ? 'No verified earnings reports found. Try another company or ticker.'
      : 'Showing ' + Math.min(matches.length, limit) + ' of ' + matches.length +
        ' matching verified report' + (matches.length === 1 ? '' : 's') + '.';
  }
  input.addEventListener('input', update);
  input.addEventListener('search', update);
  update();
})();
