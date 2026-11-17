/* Launch-window decision model, not a prediction or individual investment advice.
 * No network requests. Never transmit entered values in analytics.
 */
(function (root, factory) {
  "use strict";
  var api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root && root.document) {
    if (root.document.readyState === "loading") {
      root.document.addEventListener("DOMContentLoaded", api.mount);
    } else {
      api.mount();
    }
  }
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";
  var LAUNCH = "2027-07-01";
  var CGT = 0.31;
  var DIRT = 0.33;

  function limit(value, fallback, minimum, maximum) {
    var number = Number(value);
    if (!Number.isFinite(number)) number = fallback;
    return Math.min(maximum, Math.max(minimum, number));
  }

  function daysUntil(todayISO, launchISO) {
    function utcDate(iso) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(String(iso))) return NaN;
      var parts = iso.split("-").map(Number);
      return Date.UTC(parts[0], parts[1] - 1, parts[2]);
    }
    var first = utcDate(todayISO), last = utcDate(launchISO || LAUNCH);
    if (!Number.isFinite(first) || !Number.isFinite(last)) return 0;
    return Math.max(0, Math.round((last - first) / 86400000));
  }

  function irishToday() {
    try {
      var pieces = new Intl.DateTimeFormat("en-GB", {
        timeZone: "Europe/Dublin", year: "numeric", month: "2-digit", day: "2-digit"
      }).formatToParts(new Date());
      var values = {};
      pieces.forEach(function (part) { values[part.type] = part.value; });
      return values.year + "-" + values.month + "-" + values.day;
    } catch (error) {
      return new Date().toISOString().slice(0, 10);
    }
  }

  function normalise(raw) {
    raw = raw || {};
    return {
      capital: limit(raw.capital, 5000, 0, 12000),
      annual_return: limit(raw.annual_return, 6, -50, 50),
      investment_fee: limit(raw.investment_fee, 0.25, 0, 5),
      trade_cost: limit(raw.trade_cost, 10, 0, 100),
      cash_rate: limit(raw.cash_rate, 2, 0, 15),
      cgt_allowance: limit(raw.cgt_allowance, 1270, 0, 1270),
      etf_exit_rate: limit(raw.etf_exit_rate, 35, 0, 60),
      asset: raw.asset === "etf" ? "etf" : "shares",
      today_iso: raw.today_iso || irishToday(),
      launch_iso: raw.launch_iso || LAUNCH
    };
  }

  function estimate(raw) {
    var p = normalise(raw);
    var days = daysUntil(p.today_iso, p.launch_iso);
    var fraction = days / 365.2425;
    var cashGrowth = p.capital * Math.pow(1 + p.cash_rate / 100, fraction);
    var dirt = Math.max(0, cashGrowth - p.capital) * DIRT;
    var cash = Math.max(0, cashGrowth - dirt);
    var buyCost = Math.min(p.capital, p.trade_cost / 2);
    var saleCost = Math.min(p.capital - buyCost, p.trade_cost / 2);
    var beforeSale = (p.capital - buyCost) *
      Math.pow(1 + p.annual_return / 100, fraction) *
      Math.pow(1 - p.investment_fee / 100, fraction);
    var afterSaleBeforeTax = Math.max(0, beforeSale - saleCost);
    var taxableGain = p.asset === "shares" ?
      Math.max(0, afterSaleBeforeTax - p.capital - p.cgt_allowance) :
      Math.max(0, beforeSale - (p.capital - buyCost));
    var rate = p.asset === "shares" ? CGT : p.etf_exit_rate / 100;
    var disposalTax = taxableGain * rate;
    var invest = Math.max(0, afterSaleBeforeTax - disposalTax);
    if (!days) {
      beforeSale = cash = invest = p.capital;
      dirt = disposalTax = taxableGain = buyCost = saleCost = 0;
    }
    return {
      days: days, fractional_years: fraction, today: p.today_iso, launch: p.launch_iso,
      invested_amount: p.capital, invest_before_disposal: beforeSale,
      invest_after_tax: invest, investment_disposal_tax: disposalTax,
      savings_before_tax: cashGrowth, savings_dirt: dirt, cash_after_tax: cash,
      difference: invest - cash, trading_costs: buyCost + saleCost,
      pia_from_invest: Math.min(12000, invest), pia_from_cash: Math.min(12000, cash),
      outside_from_invest: Math.max(0, invest - 12000),
      outside_from_cash: Math.max(0, cash - 12000),
      asset: p.asset, cgt_allowance: p.cgt_allowance, etf_exit_rate: p.etf_exit_rate
    };
  }

  function breakEvenReturn(raw) {
    var p = normalise(raw);
    if (!p.capital || !daysUntil(p.today_iso, p.launch_iso)) return null;
    var target = estimate(p).cash_after_tax;
    var low = -50, high = 50;
    function delta(annualReturn) {
      return estimate(Object.assign({}, p, {annual_return: annualReturn})).invest_after_tax - target;
    }
    if (delta(high) < 0) return null;
    if (delta(low) >= 0) return low;
    for (var i = 0; i < 65; i++) {
      var midpoint = (low + high) / 2;
      if (delta(midpoint) >= 0) high = midpoint;
      else low = midpoint;
    }
    return high;
  }

  function euro(value) {
    return new Intl.NumberFormat("en-IE", {
      style: "currency", currency: "EUR", maximumFractionDigits: 0
    }).format(value);
  }

  function mount() {
    var scope = document.querySelector("[data-pia-wait-tool]");
    if (!scope || scope.dataset.piwMounted) return;
    scope.dataset.piwMounted = "true";
    var form = scope.querySelector("[data-piw-form]");
    if (!form) return;
    function output(name, value) {
      var element = scope.querySelector('[data-piw-out="' + name + '"]');
      if (element) element.textContent = value;
    }
    function refresh() {
      if (!form.checkValidity()) return;
      var data = {};
      new FormData(form).forEach(function (value, key) { data[key] = value; });
      var result = estimate(data);
      var threshold = breakEvenReturn(data);
      output("days", String(result.days));
      output("invest", euro(result.invest_after_tax));
      output("cash", euro(result.cash_after_tax));
      output("disposal-tax", euro(result.investment_disposal_tax));
      output("dirt", euro(result.savings_dirt));
      output("before-sale", euro(result.invest_before_disposal));
      output("cash-before", euro(result.savings_before_tax));
      output("fees", euro(result.trading_costs));
      output("cash-to-pia", euro(result.pia_from_cash));
      output("invest-to-pia", euro(result.pia_from_invest));
      output("difference", (result.difference > 0 ? "+" : "") + euro(result.difference));
      output("break-even", threshold === null ? "Not available" : threshold.toFixed(2) + "%");
      var relative = result.difference > 0.5 ? "Investing first is ahead by " + euro(result.difference) :
        result.difference < -0.5 ? "Keeping cash is ahead by " + euro(-result.difference) :
        "Both routes are approximately level";
      output("summary", relative + " at the proposed opening date, using your assumptions. This is not a prediction.");
      output("asset-tax", result.asset === "shares" ? "Estimated CGT if sold" : "Estimated fund exit tax if sold");
      var overflow = Math.max(result.outside_from_cash, result.outside_from_invest);
      output("cap-note", (overflow > 0 ?
        "In at least one route, the proceeds exceed the proposed €12,000 annual PIA contribution cap. The amount above it must remain outside the PIA or be considered in a later contribution year, subject to the final rules." :
        "Both modelled proceeds fit within the proposed €12,000 calendar-year PIA contribution limit, assuming no other PIA contributions in 2027.") +
        " This tool stops at the proposed launch date; it does not deduct future PIA account taxes or provider fees.");
      var maximum = Math.max(result.invest_after_tax, result.cash_after_tax, 1);
      [["invest", result.invest_after_tax], ["cash", result.cash_after_tax]].forEach(function (part) {
        var bar = scope.querySelector('[data-piw-bar="' + part[0] + '"]');
        if (bar) bar.style.width = Math.max(0, 100 * part[1] / maximum).toFixed(2) + "%";
      });
      var expired = scope.querySelector("[data-piw-expired]");
      if (expired) expired.hidden = result.days > 0;
    }
    form.addEventListener("input", refresh);
    form.addEventListener("change", refresh);
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      refresh();
      try {
        if (localStorage.getItem("compound_analytics_consent") === "granted" &&
            typeof window.gtag === "function") {
          window.gtag("event", "pia_wait_compare", {tool_name: "pia-invest-now-or-wait"});
        }
      } catch (error) { /* Analytics is optional; no calculator values are sent. */ }
    });
    scope.querySelectorAll("[data-piw-preset]").forEach(function (button) {
      button.addEventListener("click", function () {
        var rateInput = form.elements.namedItem("annual_return");
        if (rateInput) rateInput.value = button.dataset.piwPreset;
        refresh();
      });
    });
    refresh();
  }

  return {estimate: estimate, breakEvenReturn: breakEvenReturn, daysUntil: daysUntil, mount: mount};
});
