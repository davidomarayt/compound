(() => {
  "use strict";

  const form = document.querySelector("[data-ttwo-model]");
  if (!form) return;

  const results = form.querySelector("[data-ttwo-results]");
  const status = form.querySelector("[data-ttwo-status]");
  const inputs = Array.from(form.querySelectorAll("input"));
  const outputs = Array.from(results.querySelectorAll("output"));
  const format = (options) => new Intl.NumberFormat("en-US", options).format;
  const dollars = format({ style: "currency", currency: "USD", minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const percent = format({ style: "percent", signDisplay: "exceptZero", maximumFractionDigits: 1 });
  const billions = (amount) => dollars(amount / 1000) + "bn";

  function update() {
    const invalid = inputs.find((input) => !input.validity.valid);
    if (invalid) {
      results.hidden = true;
      status.textContent = invalid.labels[0].textContent.trim() + " needs a value within the allowed range.";
      return;
    }

    const value = (name) => form.elements.namedItem(name).valueAsNumber;
    const years = value("years");
    const yearOne = years === 1 ? 1 : value("yearOne") / 100;
    const copies = value("copies");
    const spending = copies * value("price");
    const publisher = spending * value("publisherShare") / 100;
    const earnings = publisher * value("margin") / 100 * (1 - value("tax") / 100);
    const cash = earnings * value("conversion") / 100;
    const discount = 1 + value("discount") / 100;

    let titleValue = cash * yearOne / discount;
    if (years > 1) {
      const laterAnnualCash = cash * (1 - yearOne) / (years - 1);
      for (let year = 2; year <= years; year += 1) {
        titleValue += laterAnnualCash / discount ** year;
      }
    }

    const shares = value("shares");
    const netDebt = value("netDebt");
    const multiple = value("multiple");
    const equity = value("otherCash") * 1000 * multiple + titleValue - netDebt;
    const perShare = Math.max(0, equity / shares);
    const sharePrice = value("sharePrice");
    const breakEvenCash = (sharePrice * shares + netDebt - titleValue) / multiple;

    const display = {
      value: dollars(perShare),
      comparison: percent(perShare / sharePrice - 1),
      eps: dollars(earnings * yearOne / shares),
      spending: billions(spending),
      publisher: billions(publisher),
      earnings: billions(earnings),
      titleValue: billions(titleValue),
      titlePerShare: dollars(titleValue / shares),
      breakEven: billions(breakEvenCash),
    };
    outputs.forEach((output) => { output.textContent = display[output.dataset.result]; });
    status.textContent = years === 1 ? "The one-year scenario places all sales in year one." : "";
    results.hidden = false;
  }

  form.addEventListener("input", update);
  form.addEventListener("submit", (event) => event.preventDefault());
  form.addEventListener("reset", () => window.setTimeout(update, 0));
  update();
})();
