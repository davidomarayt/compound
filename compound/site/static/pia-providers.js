/* Progressive enhancement for Compound's factual PIA provider comparison.
 * Source statements and fees are pre-rendered: this script never invents prices.
 */
(function (root) {
  "use strict";

  function clampNumber(value, min, max) {
    const num = Number(value);
    return Number.isFinite(num) ? Math.min(max, Math.max(min, num)) : min;
  }
  function estimateAnnualCost(fees, balance, trades) {
    if (!fees || !fees.verified) return null;
    const keys = ["account_annual_eur", "account_annual_pct", "custody_annual_pct", "fund_annual_pct", "trade_eur"];
    if (keys.some(function (key) {
      return typeof fees[key] !== "number" || !Number.isFinite(fees[key]) || fees[key] < 0;
    })) return null;
    const amount = clampNumber(balance, 0, 10000000);
    const count = Math.floor(clampNumber(trades, 0, 1000));
    return fees.account_annual_eur +
      amount * (fees.account_annual_pct + fees.custody_annual_pct + fees.fund_annual_pct) / 100 +
      count * fees.trade_eur;
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { estimateAnnualCost: estimateAnnualCost, clampNumber: clampNumber };
  }
  if (typeof document === "undefined") return;
  const comparison = document.querySelector("[data-pia-comparison]");
  if (!comparison) return;
  const list = comparison.querySelector("[data-pia-provider-list]");
  const cards = Array.from(list.querySelectorAll("[data-pia-provider]"));
  const search = comparison.querySelector("[data-pia-filter-search]");
  const type = comparison.querySelector("[data-pia-filter-type]");
  const stage = comparison.querySelector("[data-pia-filter-stage]");
  const sort = comparison.querySelector("[data-pia-sort]");
  const resultCount = comparison.querySelector("[data-pia-results-count]");
  const noResults = comparison.querySelector("[data-pia-no-results]");
  const balanceInput = document.querySelector("[data-pia-balance]");
  const tradesInput = document.querySelector("[data-pia-trades]");
  const eur = new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR", maximumFractionDigits: 2 });

  function feeFor(card) {
    if (card.dataset.feesVerified !== "true") return null;
    return {
      verified: true,
      account_annual_eur: Number(card.dataset.accountEur),
      account_annual_pct: Number(card.dataset.accountPct),
      custody_annual_pct: Number(card.dataset.custodyPct),
      fund_annual_pct: Number(card.dataset.fundPct),
      trade_eur: Number(card.dataset.tradeEur)
    };
  }

  function update() {
    const balance = Number(balanceInput.value);
    const trades = Number(tradesInput.value);
    const query = search.value.trim().toLocaleLowerCase("en-IE");
    let shown = 0;
    cards.forEach(function (card) {
      const included = card.dataset.provider.includes(query) &&
        (type.value === "all" || card.dataset.type === type.value) &&
        (stage.value === "all" || card.dataset.stage === stage.value);
      card.hidden = !included;
      if (included) shown++;
      const fee = estimateAnnualCost(feeFor(card), balance, trades);
      const target = card.querySelector("[data-pia-estimate]");
      target.textContent = fee === null ? "Awaiting verified fees" : eur.format(fee) + " / year";
      card.dataset.scenarioFee = fee === null ? "" : String(fee);
    });
    const stageOrder = { "live": 0, "launch-planned": 1, "intent": 2 };
    cards.sort(function (a, b) {
      if (sort.value === "stage") {
        const rank = (stageOrder[a.dataset.stage] ?? 99) - (stageOrder[b.dataset.stage] ?? 99);
        if (rank) return rank;
      }
      if (sort.value.startsWith("fee-")) {
        const af = a.dataset.scenarioFee === "" ? Infinity : Number(a.dataset.scenarioFee);
        const bf = b.dataset.scenarioFee === "" ? Infinity : Number(b.dataset.scenarioFee);
        if (af !== bf) {
          if (af === Infinity) return 1;
          if (bf === Infinity) return -1;
          return sort.value === "fee-low" ? af - bf : bf - af;
        }
      }
      return a.dataset.provider.localeCompare(b.dataset.provider, "en-IE");
    });
    cards.forEach(function (card) { list.appendChild(card); });
    resultCount.textContent = shown + " of " + cards.length + " provider statements shown";
    noResults.hidden = shown !== 0;
  }

  [search, type, stage, sort, balanceInput, tradesInput].forEach(function (control) {
    if (control) {
      control.addEventListener(control === search || control === balanceInput || control === tradesInput ? "input" : "change", update);
    }
  });
  update();

  // GA4 measurement is optional and only occurs after explicitly granted consent.
  // Partner-side link attribution must be implemented by an actual signed affiliate URL.
  document.addEventListener("click", function (event) {
    const link = event.target.closest && event.target.closest("a[data-pia-referral]");
    if (!link) return;
    let consent = "";
    try { consent = root.localStorage.getItem("compound_analytics_consent"); } catch (error) { /* unavailable */ }
    if (consent !== "granted" || typeof root.gtag !== "function") return;
    root.gtag("event", "pia_provider_referral_click", {
      provider_slug: link.dataset.piaReferral,
      placement: "pia_comparison"
    });
  });
})(typeof window !== "undefined" ? window : {});
