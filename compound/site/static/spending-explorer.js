/* Compound Where's My Money? public spending explorer.
   No external charting dependencies, HTTP requests or telemetry of tax inputs. */
(function () {
  'use strict';
  if (typeof document === 'undefined') return;
  var euro = new Intl.NumberFormat('en-IE', {style:'currency',currency:'EUR',maximumFractionDigits:0});
  document.querySelectorAll('[data-spending-personal]').forEach(function (panel) {
    var input = panel.querySelector('[data-contribution]');
    var error = panel.querySelector('[data-validation]');
    if (!input || !error) return;
    var outputs = Array.prototype.slice.call(panel.querySelectorAll('[data-equivalent]'));
    function render() {
      var raw = input.value.trim();
      var amount = Number(raw);
      var valid = raw !== '' && Number.isFinite(amount) && amount >= 0 && amount <= 10000000;
      error.hidden = valid;
      error.textContent = valid ? '' : 'Enter a valid annual total between €0 and €10 million.';
      outputs.forEach(function (output) {
        var holder = output.closest('[data-share]') || output;
        var ratio = Number(holder.getAttribute('data-share'));
        output.textContent = valid && Number.isFinite(ratio) && ratio >= 0 && ratio <= 1
          ? euro.format(amount * ratio) : '—';
      });
    }
    input.addEventListener('input', render);
    render();
  });

  /* Client-side finding only; all canonical programme links are server-rendered. */
  var search = document.querySelector('[data-programme-search]');
  if (search) {
    var cards = Array.prototype.slice.call(document.querySelectorAll('[data-programme-card]'));
    var groups = Array.prototype.slice.call(document.querySelectorAll('[data-programme-group]'));
    var counter = document.querySelector('[data-programme-count]');
    var empty = document.querySelector('[data-programme-empty]');
    function filterProgrammes() {
      var query = search.value.trim().toLocaleLowerCase('en-IE');
      var visible = 0;
      cards.forEach(function (card) {
        var match = !query || (card.dataset.programmeText || '').indexOf(query) !== -1;
        card.hidden = !match;
        if (match) visible++;
      });
      groups.forEach(function (group) {
        group.hidden = !Array.prototype.some.call(group.querySelectorAll('[data-programme-card]'), function (card) {
          return !card.hidden;
        });
      });
      if (counter) counter.textContent = visible + ' of ' + cards.length + ' published programme allocations shown';
      if (empty) empty.hidden = visible !== 0;
    }
    search.addEventListener('input', filterProgrammes);
    filterProgrammes();
  }

  /* All Vote rows remain server-rendered and indexable. Filter only the view. */
  var voteSearch = document.querySelector('[data-vote-search]');
  if (voteSearch) {
    var votes = Array.prototype.slice.call(document.querySelectorAll('[data-vote-row]'));
    var voteCount = document.querySelector('[data-vote-count]');
    function filterVotes() {
      var query = voteSearch.value.trim().toLocaleLowerCase('en-IE');
      var visible = 0;
      votes.forEach(function (vote) {
        var match = !query || (vote.dataset.voteText || '').indexOf(query) !== -1;
        vote.hidden = !match;
        if (match) visible++;
      });
      if (voteCount) voteCount.textContent = visible + ' of ' + votes.length + ' Dáil Votes shown';
    }
    voteSearch.addEventListener('input', filterVotes);
    filterVotes();
  }
})();
