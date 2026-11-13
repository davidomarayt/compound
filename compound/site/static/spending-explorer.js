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
})();
