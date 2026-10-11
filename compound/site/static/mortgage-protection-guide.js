/* Cost-difference arithmetic only; this is not an insurance quote tool. */
(function () {
  'use strict';
  var root = document.getElementById('mp26-savings');
  if (!root) return;
  var current = root.querySelector('#mp26-current');
  var alternative = root.querySelector('#mp26-alternative');
  var term = root.querySelector('#mp26-years');
  var result = root.querySelector('#mp26-difference');
  var direction = root.querySelector('#mp26-direction');
  var annual = root.querySelector('#mp26-annual');
  var totalA = root.querySelector('#mp26-total-a');
  var totalB = root.querySelector('#mp26-total-b');
  var barA = root.querySelector('#mp26-bar-a');
  var barB = root.querySelector('#mp26-bar-b');
  var money = new Intl.NumberFormat('en-IE', {style:'currency',currency:'EUR',maximumFractionDigits:0});
  function read(el,max) {
    var val = Number(el.value);
    return Number.isFinite(val) ? Math.max(0, Math.min(max,val)) : 0;
  }
  function recalculate() {
    var a = read(current,10000), b = read(alternative,10000), years = read(term,60);
    var oldCost = a * 12 * years, newCost = b * 12 * years;
    var diff = oldCost - newCost;
    result.textContent = money.format(Math.abs(diff));
    direction.textContent = diff > 0 ? 'Less paid over the selected term' : diff < 0 ? 'More paid over the selected term' : 'No difference over the selected term';
    annual.textContent = money.format(Math.abs(a - b) * 12) + (diff > 0 ? ' less per year' : diff < 0 ? ' more per year' : ' difference per year');
    totalA.textContent = money.format(oldCost);
    totalB.textContent = money.format(newCost);
    var max = Math.max(1,oldCost,newCost);
    barA.style.width = (100*oldCost/max).toFixed(2) + '%';
    barB.style.width = (100*newCost/max).toFixed(2) + '%';
  }
  [current,alternative,term].forEach(function (field) {
    field.addEventListener('input',recalculate);
    field.addEventListener('change',recalculate);
  });
  recalculate();
})();