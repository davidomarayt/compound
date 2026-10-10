(function () {
  "use strict";
  var root = document.querySelector("[data-mx27-simulator]");
  if (!root) return;
  var tesla = root.querySelector("[data-mx27-tesla]");
  var spacex = root.querySelector("[data-mx27-spacex]");
  var tOut = root.querySelector("[data-mx27-tesla-value]");
  var sOut = root.querySelector("[data-mx27-spacex-value]");
  var tShare = root.querySelector("[data-mx27-tesla-share]");
  var sShare = root.querySelector("[data-mx27-spacex-share]");
  var bar = root.querySelector("[data-mx27-combined-bar]");
  if (!tesla || !spacex || !tOut || !sOut || !tShare || !sShare || !bar) return;
  function render() {
    var t = Number(tesla.value), s = Number(spacex.value);
    if (!Number.isFinite(t) || !Number.isFinite(s) || t <= 0 || s <= 0) return;
    var combined = t+s;
    var tPct = t/combined*100, sPct = s/combined*100;
    tOut.textContent = "$" + (t/1000).toFixed(2) + "tn";
    sOut.textContent = "$" + (s/1000).toFixed(2) + "tn";
    tShare.textContent = tPct.toFixed(1) + "%";
    sShare.textContent = sPct.toFixed(1) + "%";
    bar.style.width = tPct.toFixed(2)+"%";
    bar.setAttribute("aria-valuenow",tPct.toFixed(1));
    bar.setAttribute("aria-valuetext",tPct.toFixed(1)+" percent hypothetical Tesla existing shareholder ownership");
  }
  tesla.addEventListener("input",render);
  spacex.addEventListener("input",render);
  render();
}());