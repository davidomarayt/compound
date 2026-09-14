(function () {
  'use strict';
  const track = (name, parameters) => {
    if (analyticsChoice === 'granted' && typeof window.gtag === 'function') window.gtag('event', name, parameters || {});
  };
  const privacyBanner = document.querySelector('[data-privacy-banner]');
  let analyticsChoice = null;
  try { analyticsChoice = localStorage.getItem('compound_analytics_consent'); } catch (_) {}
  if (privacyBanner && !analyticsChoice) privacyBanner.hidden = false;
  document.querySelectorAll('[data-analytics-consent]').forEach(button => button.addEventListener('click', () => {
    const choice = button.dataset.analyticsConsent;
    analyticsChoice = choice;
    try { localStorage.setItem('compound_analytics_consent', choice); } catch (_) {}
    if (typeof window.gtag === 'function') window.gtag('consent', 'update', {analytics_storage: choice});
    if (choice === 'granted' && typeof window.compoundStartAnalytics === 'function') window.compoundStartAnalytics();
    if (privacyBanner) privacyBanner.hidden = true;
  }));
  document.querySelectorAll('[data-privacy-settings]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    if (privacyBanner) { privacyBanner.hidden = false; privacyBanner.querySelector('button').focus(); }
  }));
  const filters = document.querySelectorAll('[data-filter]');
  filters.forEach(button => button.addEventListener('click', () => {
    const value = button.dataset.filter;
    let count = 0;
    document.querySelectorAll('.latest-section .compound-story').forEach(card => {
      card.hidden = value !== 'all' && card.dataset.pillar !== value;
      if (!card.hidden) count++;
    });
    filters.forEach(item => { item.classList.toggle('active', item === button); item.setAttribute('aria-pressed', String(item === button)); });
    const countLabel = document.querySelector('.filter-count');
    if (countLabel) countLabel.textContent = count + (count === 1 ? ' story to explore' : ' stories to explore');
  }));
  const toc = document.getElementById('article-toc');
  if (toc) {
    const headings = Array.from(document.querySelectorAll('.article .article-prose h2'));
    headings.forEach((heading, i) => {
      if (!heading.id) heading.id = 'section-' + (i + 1);
      const link = document.createElement('a'); link.href = '#' + heading.id; link.textContent = heading.textContent;
      toc.appendChild(link);
    });
    if (headings.length) {
      toc.closest('.reading-nav').hidden = false;
      if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(entries => {
          entries.forEach(entry => { if (entry.isIntersecting) toc.querySelectorAll('a').forEach(a => a.classList.toggle('active', a.hash === '#' + entry.target.id)); });
        }, {rootMargin: '0px 0px -65% 0px'});
        headings.forEach(h => observer.observe(h));
      }
    }
  }
  const share = document.querySelector('[data-share]');
  if (share) share.addEventListener('click', async () => {
    const canonical = document.querySelector('link[rel=canonical]');
    const url = canonical ? canonical.href : location.href;
    const status = document.getElementById('share-status');
    try { await navigator.clipboard.writeText(url); share.textContent = 'Link copied ✓'; track('share_article', {method:'copy_link'}); if (status) status.textContent = 'Article link copied.'; }
    catch (_) { if (status) { status.classList.remove('sr-only'); status.textContent = 'Copy this link: ' + url; } }
  });
  const article = document.querySelector('.article');
  if (article) {
    const milestones = [25, 50, 75, 90], sent = new Set();
    const measureDepth = () => {
      const top = article.offsetTop, height = article.offsetHeight - innerHeight;
      const depth = height > 0 ? Math.max(0, Math.min(100, ((scrollY - top + innerHeight) / article.offsetHeight) * 100)) : 100;
      milestones.forEach(percent => { if (depth >= percent && !sent.has(percent)) { sent.add(percent); track('article_progress', {percent}); } });
    };
    addEventListener('scroll', measureDepth, {passive:true}); measureDepth();
    article.querySelectorAll('.sources a').forEach(link => link.addEventListener('click', () => {
      let domain = ''; try { domain = new URL(link.href).hostname; } catch (_) {}
      track('source_click', {source_domain:domain});
    }));
    article.querySelectorAll('.budget-calculator input,.hobby-picker select').forEach(control => control.addEventListener('change', () => {
      const tool = control.closest('.budget-calculator') ? 'budget_calculator' : 'hobby_picker';
      if (!control.closest('[data-tool-tracked]')) {
        const container = control.closest('.budget-calculator,.hobby-picker'); if (container) container.dataset.toolTracked = 'true';
        track('interactive_tool_used', {tool_name:tool});
      }
    }));
  }
  const source = document.getElementById('search-data');
  if (!source) return;
  const index = JSON.parse(source.textContent), input = document.getElementById('q'), results = document.getElementById('results'), status = document.getElementById('search-status');
  const wordsOf = s => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
  const el = (tag, cls, text) => { const node = document.createElement(tag); if (cls) node.className = cls; if (text) node.textContent = text; return node; };
  function run() {
    const query = wordsOf(input.value), words = query.split(/\s+/).filter(Boolean);
    const matches = index.map(a => { const hay = wordsOf(a.title + ' ' + a.summary + ' ' + a.tags.join(' ')); return {a, match: words.every(w => hay.includes(w)), score: words.filter(w => wordsOf(a.title).includes(w)).length}; }).filter(x => x.match).sort((a, b) => b.score - a.score);
    results.replaceChildren();
    status.textContent = query ? matches.length + (matches.length === 1 ? ' story found' : ' stories found') : 'All ' + index.length + ' stories';
    matches.forEach(({a}) => {
      const card = el('article', 'compound-story'), imageLink = el('a', 'card-image'); imageLink.href = a.url; imageLink.setAttribute('aria-label', 'Read ' + a.title);
      const img = el('img'); if (a.image) img.src = a.image; img.alt = ''; img.loading = 'lazy'; img.width = 800; img.height = 520; imageLink.append(img);
      const content = el('div', 'card-content'), meta = el('p', 'meta'); meta.append(el('span', 'category category-' + a.pillar.toLowerCase(), a.pillar), el('span', '', a.reading_minutes + ' min read'));
      const heading = el('h3'), link = el('a', '', a.title); link.href = a.url; heading.append(link);
      content.append(meta, heading, el('p', 'summary', a.description));
      const bottom = el('div', 'card-bottom'), date = el('time', '', a.date_label); date.dateTime = a.date;
      const read = el('a', '', 'Read story ↗'); read.href = a.url; read.setAttribute('aria-label', 'Read ' + a.title); bottom.append(date, read); content.append(bottom); if (a.image) card.append(imageLink); card.append(content); results.append(card);
    });
    if (!matches.length) results.append(el('p', 'empty', 'No stories found. Try a broader topic such as sleep, tax or wellbeing.'));
  }
  input.value = new URLSearchParams(location.search).get('q') || '';
  input.addEventListener('input', run);
  input.form.addEventListener('submit', event => { event.preventDefault(); run(); });
  document.querySelectorAll('[data-query]').forEach(button => button.addEventListener('click', () => { input.value = button.dataset.query; run(); input.focus(); }));
  run();
})();
