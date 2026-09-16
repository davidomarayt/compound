(() => {
  'use strict';
  // Local arithmetic only. No submission, storage, analytics or external requests.
  function yearsTo100(value) {
    const raw = String(value).trim();
    const age = Number(raw);
    return /^\d+$/.test(raw) && Number.isInteger(age) && age >= 18 && age <= 100 ? 100 - age : null;
  }
  // Expose the same pure arithmetic to non-browser tests without loading a page.
  if (typeof module !== 'undefined' && module.exports) module.exports = { yearsTo100 };
  if (typeof document === 'undefined') return;
  const horizon = document.querySelector('[data-live100-horizon]');
  if (horizon) {
    ['chosen-age', 'retirement-age'].forEach(id => {
      const input = horizon.querySelector('#' + id);
      const output = horizon.querySelector('#' + id + '-result strong');
      const error = horizon.querySelector('#' + id + '-error');
      const update = () => {
        const years = yearsTo100(input.value);
        const valid = years !== null;
        input.setAttribute('aria-invalid', String(!valid));
        error.hidden = valid;
        output.textContent = valid ? String(years) : '—';
      };
      input.disabled = false;
      input.addEventListener('input', update);
      update();
    });
  }
  const timeline = document.querySelector('[data-live100-timeline]');
  if (!timeline) return;
  const controls = timeline.querySelector('.chapter-controls');
  const buttons = [...controls.querySelectorAll('button')];
  const panels = [...timeline.querySelectorAll('.chapter-panel')];
  const all = timeline.querySelector('[data-all-chapters]');
  const status = timeline.querySelector('[data-chapter-status]');
  let current = 'building';
  let showAll = false;
  function render(announce = true) {
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.chapter === current)));
    panels.forEach(panel => { panel.hidden = !showAll && panel.id !== 'chapter-' + current; });
    all.setAttribute('aria-pressed', String(showAll));
    all.textContent = showAll ? 'Show selected chapter' : 'Show all chapters';
    if (announce) status.textContent = showAll ? 'All five chapters are shown.' : timeline.querySelector('#chapter-' + current + ' h4').textContent + ' Chapter shown below the controls.';
  }
  buttons.forEach((button, index) => {
    button.addEventListener('click', () => { current = button.dataset.chapter; showAll = false; render(); });
    button.addEventListener('keydown', event => {
      let next = null;
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % buttons.length;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index + buttons.length - 1) % buttons.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = buttons.length - 1;
      if (next !== null) { event.preventDefault(); buttons[next].focus(); buttons[next].click(); }
    });
  });
  all.addEventListener('click', () => { showAll = !showAll; render(); });
  controls.hidden = false;
  all.hidden = false;
  render(false);
})();
