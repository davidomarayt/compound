(function () {
 'use strict';
 const root = document.getElementById('budget-tax-calculator');
 if (!root) return;
 const input = root.querySelector('#budget-taxable-pay');
 const result = root.querySelector('#budget-result');
 if (!input || !result) return;
 const euro = new Intl.NumberFormat('en-IE', {style:'currency', currency:'EUR', minimumFractionDigits:2, maximumFractionDigits:2});
 function update() {
  if (input.validity.badInput) {
   result.textContent = 'Enter a valid annual amount of zero or more.';
   input.setAttribute('aria-invalid', 'true');
   return;
  }
  if (input.value.trim() === '') {
   result.textContent = 'Enter an amount to see the illustration.';
   input.removeAttribute('aria-invalid');
   return;
  }
  const income = Number(input.value);
  if (!Number.isFinite(income) || income < 0) {
   result.textContent = 'Enter a valid annual amount of zero or more.';
   input.setAttribute('aria-invalid', 'true');
   return;
  }
  input.removeAttribute('aria-invalid');
  const saving = Math.min(Math.max(income - 44000, 0), 2000) * 0.2;
  result.textContent = euro.format(saving) + ' per year · ' + euro.format(saving / 12) + ' per month' + (saving === 0 ? '. This band change alone would not reduce your income tax.' : '. Illustrative saving from the band change alone.');
 }
 input.addEventListener('input', update);
 window.addEventListener('pageshow', function () { input.value = ''; update(); });
 update();
})();
