const filter = document.querySelector('[data-claim-filter]');
if (filter) {
  const search = document.querySelector('#claim-search');
  const status = filter.querySelector('[data-claim-count]');
  const entries = [...document.querySelectorAll('#claim-results li')];
  const normalize = text => text.toLowerCase().normalize('NFD')
    .replace(/\p{Diacritic}/gu, '').replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  const labels = entries.map(entry => normalize(entry.textContent + ' ' + entry.dataset.keywords));

  search.addEventListener('input', () => {
    const terms = normalize(search.value).split(' ').filter(Boolean);
    let matches = 0;
    entries.forEach((entry, index) => {
      const matched = terms.every(term => labels[index].includes(term));
      entry.hidden = !matched;
      if (matched) matches += 1;
    });
    status.textContent = matches === 0 ? 'No matching supports. Try a different term.'
      : matches === 1 ? '1 matching support' : matches + ' matching supports';
  });
  filter.hidden = false;
}

document.querySelectorAll('[data-claim-tool], [data-claim-guide]').forEach(link => {
  link.addEventListener('click', () => {
    let consent;
    try { consent = localStorage.getItem('compound_analytics_consent'); } catch (_) { return; }
    if (consent !== 'granted' || typeof window.gtag !== 'function') return;
    if (link.dataset.claimGuide) {
      window.gtag('event', 'claims_guide_click', {
        calculator: link.dataset.claimSource,
        guide: link.dataset.claimGuide,
      });
    } else {
      window.gtag('event', 'claims_calculator_click', { tool: link.dataset.claimTool });
    }
  });
});
