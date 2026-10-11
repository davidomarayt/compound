
/* Insurance income interruption arithmetic. No input leaves this browser. */
(function () {
  "use strict";
  // Aggregate navigation events only, when a reader has explicitly consented.
  // No calculator values, identity, email address or full link URL is recorded.
  document.addEventListener("click",function (ev) {
    var target = ev.target && ev.target.closest ? ev.target.closest("a[data-ins-event]") : null;
    if (!target) return;
    var category = target.getAttribute("data-ins-event");
    var label = target.getAttribute("data-ins-label");
    var allowed = ["tool_open","guide_open","partner_interest","partner_email"];
    if (allowed.indexOf(category) < 0 || !/^[a-z_]{1,40}$/.test(label || "")) return;
    var consent = false;
    try { consent = localStorage.getItem("compound_analytics_consent") === "granted"; }
    catch (err) { consent = false; }
    if (!consent || typeof window.gtag !== "function") return;
    window.gtag("event","insurance_hub_navigation",{interaction_type:category,content_category:label});
  });
  var root = document.querySelector("[data-ins-gap]");
  if (!root) return;
  var ids = ["spending","other","months","sick","savings"];
  var fields = {};
  ids.forEach(function (id) { fields[id] = root.querySelector('[data-ins-field="'+id+'"]'); });
  var fmt = new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0});
  var refs = {
    gap: root.querySelector("[data-ins-result=gap]"),
    monthly: root.querySelector("[data-ins-result=monthly]"),
    months: root.querySelector("[data-ins-result=months]"),
    gross: root.querySelector("[data-ins-result=gross]"),
    savings: root.querySelector("[data-ins-result=savings]"),
    meter: root.querySelector("[data-ins-meter]")
  };
  function v(id,max) {
    var n = Number(fields[id].value);
    return Number.isFinite(n) ? Math.max(0,Math.min(n,max)) : 0;
  }
  function calc() {
    var spending = v("spending",100000),other=v("other",100000),
        period=v("months",120),sick=v("sick",120),savings=v("savings",10000000);
    var monthly = Math.max(0,spending-other);
    var uncovered = Math.max(0,period-Math.min(period,sick));
    var gross = monthly*uncovered;
    var gap=Math.max(0,gross-savings);
    refs.gap.textContent=fmt.format(gap);
    refs.monthly.textContent=fmt.format(monthly);
    refs.months.textContent=new Intl.NumberFormat("en-IE",{maximumFractionDigits:1}).format(uncovered);
    refs.gross.textContent=fmt.format(gross);
    refs.savings.textContent=fmt.format(savings);
    refs.meter.style.width=(gross>0?Math.min(100,100*savings/gross):100).toFixed(1)+"%";
    root.querySelector("[data-ins-summary]").textContent=gap>0?
      "Illustrative cash gap after the savings entered. This is not an insurer payout calculation.":
      "On the assumptions entered, your savings meet the modelled cash need.";
  }
  ids.forEach(function (id) { fields[id].addEventListener("input",calc);fields[id].addEventListener("change",calc); });
  calc();
})();
