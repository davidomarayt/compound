/* Native public spending interactions. All published charts and data also work without JS.
 * No tracking calls, cookies, storage, user-input URLs, network requests or external chart libraries.
 */
(function () {
  'use strict';
  if (typeof document === 'undefined') return;
  var root = document.querySelector('[data-wx-root]');
  if (!root) return;
  var national = Number(root.dataset.wxNational), parent = Number(root.dataset.wxTotal);
  var mode = root.querySelector('#wx-mode'), input = root.querySelector('#wx-contribution');
  var format = new Intl.NumberFormat('en-IE', {style:'currency',currency:'EUR',maximumFractionDigits:2});
  var compact = function (value) {
    if (Math.abs(value) >= 1e9) return '€' + (value / 1e9).toFixed(3) + 'bn';
    if (Math.abs(value) >= 1e6) return '€' + (value / 1e6).toFixed(3) + 'm';
    return format.format(value);
  };
  if (mode && input && national > 0 && parent > 0) {
    root.querySelector('[data-wx-controls]').hidden = false;
    var note = root.querySelector('#wx-mode-note');
    var values = Array.prototype.slice.call(root.querySelectorAll('[data-wx-value]'));
    function render() {
      var personal = mode.value === 'personal', contribution = Number(input.value);
      root.querySelector('[data-wx-personal]').hidden = !personal;
      var invalid = personal && (!input.value.trim() || !Number.isFinite(contribution) || contribution < 0 || contribution > 10000000);
      input.setAttribute('aria-invalid', invalid ? 'true' : 'false');
      values.forEach(function (el) {
        var amount = Number(el.dataset.wxValue);
        el.textContent = invalid ? '—' : personal ? format.format(amount / national * contribution)
          : mode.value === 'share' ? (amount / parent * 100).toFixed(2) + '%' : compact(amount);
      });
      note.textContent = invalid ? 'Enter an annual contribution between €0 and €10,000,000. No personal allocation is shown until the value is valid.'
        : personal ? 'Illustration: your entered contribution × each published allocation ÷ the national total. Not earmarked payments or benefits received. Bars retain their published proportions.'
        : mode.value === 'share' ? 'Percentages use this page’s parent total. Missing source detail is not redistributed; component shares may not sum to 100%.'
        : 'Bars are scaled to the largest item. Percentages use the parent total, not the largest bar.';
    }
    mode.addEventListener('change',render); input.addEventListener('input',render); render();
  }
  var search = root.querySelector('#wx-search');
  if (search) {
    root.querySelector('[data-wx-search-wrap]').hidden = false;
    var items = Array.prototype.slice.call(root.querySelectorAll('[data-wx-search-item]'));
    var groups = Array.prototype.slice.call(root.querySelectorAll('[data-wx-search-group]'));
    var status = root.querySelector('#wx-search-status');
    search.addEventListener('input',function () {
      var terms = search.value.trim().toLocaleLowerCase('en-IE').split(/\s+/).filter(Boolean), count = 0;
      items.forEach(function (item) {
        var text = item.dataset.wxSearchText;
        var match = terms.every(function(term) {return text.indexOf(term) !== -1;});
        item.hidden = !match; if (match) count++;
      });
      groups.forEach(function(group) {
        group.hidden = !Array.prototype.some.call(group.querySelectorAll('[data-wx-search-item]'),function(item){return !item.hidden;});
      });
      status.textContent = terms.length ? count + ' matching programme' + (count===1?'':'s') + '. Clear the search to see every sector.' : '';
    });
  }
})();
