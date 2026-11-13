/* PIA versus pension: transparent illustrative projection, not personal advice.
 * Proposed PIA tax: 1% * max(0, mean(365 daily closing values) - €50,000).
 * Pension amounts reflect an equal after-income-tax monthly budget and a manually
 * entered additional employer contribution. Actual pension tax relief limits,
 * fund access and retirement withdrawal taxes are outside this model.
 */
(function (root) {
  "use strict";

  const DEFAULTS = Object.freeze({
    monthlyBudget: 500, years: 20, relief: 40, employerMonthly: 0,
    annualReturn: 6, piaFee: 0.5, pensionFee: 0.75, withdrawalTax: 20
  });

  const RANGES = {
    monthlyBudget: [25, 1000], years: [1, 40], employerMonthly: [0, 2000],
    annualReturn: [-20, 20], piaFee: [0, 5], pensionFee: [0, 5],
    withdrawalTax: [0, 60]
  };

  function validate(raw) {
    const input = {};
    Object.keys(RANGES).forEach(function (key) {
      const range = RANGES[key];
      const val = raw[key];
      if (val === "" || val === null || val === undefined || !Number.isFinite(Number(val)) ||
          Number(val) < range[0] || Number(val) > range[1]) {
        throw new RangeError("Check " + key + ": enter a number between " + range[0] + " and " + range[1] + ".");
      }
      input[key] = Number(val);
    });
    if (!Number.isInteger(input.years)) throw new RangeError("Years invested must be a whole number.");
    if (![0, 20, 40].includes(Number(raw.relief))) {
      throw new RangeError("Choose a valid pension Income Tax relief assumption.");
    }
    input.relief = Number(raw.relief);
    return input;
  }

  function calculate(raw) {
    const input = validate(raw);
    const piaMonthly = input.monthlyBudget;
    const pensionEmployeeMonthly = piaMonthly / (1 - input.relief / 100);
    const pensionMonthly = pensionEmployeeMonthly + input.employerMonthly;
    const grossDaily = Math.pow(1 + input.annualReturn / 100, 1 / 365);
    const piaFeeDaily = Math.pow(1 - input.piaFee / 100, 1 / 365);
    const pensionFeeDaily = Math.pow(1 - input.pensionFee / 100, 1 / 365);
    const contributionDays = new Set();
    for (let m = 1; m <= 12; m++) contributionDays.add(Math.round(m * 365 / 12));

    let pia = 0, pension = 0, piaTaxTotal = 0, piaFeesTotal = 0, pensionFeesTotal = 0;
    const rows = [{
      year: 0, pia: 0, pensionGross: 0, pensionIllustrativeNet: 0,
      piaTax: 0, averagePiaDaily: 0
    }];

    for (let year = 1; year <= input.years; year++) {
      let dailyClosingSum = 0;
      for (let day = 1; day <= 365; day++) {
        const piaBeforeFee = pia * grossDaily;
        const pensionBeforeFee = pension * grossDaily;
        pia = piaBeforeFee * piaFeeDaily;
        pension = pensionBeforeFee * pensionFeeDaily;
        piaFeesTotal += piaBeforeFee - pia;
        pensionFeesTotal += pensionBeforeFee - pension;

        // Contributions are credited at the end of each modelled month.
        if (contributionDays.has(day)) {
          pia += piaMonthly;
          pension += pensionMonthly;
        }
        dailyClosingSum += pia;
      }
      const meanDailyClosing = dailyClosingSum / 365;
      const piaTax = Math.max(0, meanDailyClosing - 50000) * 0.01;
      pia = Math.max(0, pia - piaTax);
      piaTaxTotal += piaTax;
      rows.push({
        year: year,
        pia: pia,
        pensionGross: pension,
        pensionIllustrativeNet: pension * (1 - input.withdrawalTax / 100),
        piaTax: piaTax,
        averagePiaDaily: meanDailyClosing
      });
    }
    const last = rows[rows.length - 1];
    return {
      input: input,
      piaMonthly: piaMonthly,
      pensionEmployeeMonthly: pensionEmployeeMonthly,
      pensionMonthly: pensionMonthly,
      piaValue: last.pia,
      pensionGross: last.pensionGross,
      pensionIllustrativeNet: last.pensionIllustrativeNet,
      piaContributions: piaMonthly * 12 * input.years,
      pensionEmployeeContributions: pensionEmployeeMonthly * 12 * input.years,
      employerTotal: input.employerMonthly * 12 * input.years,
      piaTaxTotal: piaTaxTotal,
      piaFeesTotal: piaFeesTotal,
      pensionFeesTotal: pensionFeesTotal,
      rows: rows
    };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { calculate: calculate, validate: validate, DEFAULTS: DEFAULTS };
  }
  if (typeof document === "undefined") return;

  const container = document.querySelector("[data-pia-pension-tool]");
  if (!container) return;
  const form = container.querySelector("[data-pia-form]");
  const results = container.querySelector("[data-pia-results]");
  const error = container.querySelector("[data-pia-tool-error]");
  const presets = Array.from(container.querySelectorAll("[data-pia-example]"));
  const euro = new Intl.NumberFormat("en-IE", {
    style: "currency", currency: "EUR", maximumFractionDigits: 0
  });
  const euroMonthly = new Intl.NumberFormat("en-IE", {
    style: "currency", currency: "EUR", minimumFractionDigits: 2, maximumFractionDigits: 2
  });
  const fieldNames = Object.keys(DEFAULTS);

  function currentInputs() {
    const data = {};
    fieldNames.forEach(function (name) {
      const field = form.elements.namedItem(name);
      data[name] = field ? field.value : undefined;
    });
    return data;
  }

  function output(name, value) {
    const el = container.querySelector('[data-pia-out="' + name + '"]');
    if (el) el.textContent = String(value);
  }

  function render(model) {
    output("years", model.input.years);
    output("withdrawalRate", model.input.withdrawalTax + "%");
    output("piaValue", euro.format(model.piaValue));
    output("pensionGross", euro.format(model.pensionGross));
    output("pensionIllustrativeNet", euro.format(model.pensionIllustrativeNet));
    output("piaBar", euro.format(model.piaValue));
    output("grossBar", euro.format(model.pensionGross));
    output("netBar", euro.format(model.pensionIllustrativeNet));
    output("grossMonthly", euroMonthly.format(model.pensionEmployeeMonthly));
    output("employerTotal", euro.format(model.employerTotal));
    output("piaContributions", euro.format(model.piaContributions));
    output("piaTaxTotal", euro.format(model.piaTaxTotal));
    output("piaFeesTotal", euro.format(model.piaFeesTotal));
    output("pensionFeesTotal", euro.format(model.pensionFeesTotal));
    output("assumptions", euro.format(model.input.monthlyBudget) +
      " a month after Income Tax, " + model.input.relief + "% assumed full pension relief, " +
      model.input.annualReturn + "% annual return before fees.");

    const maximum = Math.max(model.piaValue, model.pensionGross, model.pensionIllustrativeNet, 1);
    ["piaValue", "pensionGross", "pensionIllustrativeNet"].forEach(function (key) {
      const bar = container.querySelector('[data-pia-bar="' + key + '"]');
      if (bar) bar.style.width = (Math.max(0, model[key]) / maximum * 100).toFixed(2) + "%";
    });
    const bars = container.querySelector(".pia-pension-tool__bar-chart");
    if (bars) bars.setAttribute("aria-label",
      "Modelled PIA balance " + euro.format(model.piaValue) + ", gross pension " +
      euro.format(model.pensionGross) + ", pension after hypothetical withdrawal tax " +
      euro.format(model.pensionIllustrativeNet) + ".");

    const body = container.querySelector("[data-pia-milestones]");
    if (body) {
      body.textContent = "";
      const years = new Set([1, 5, 10, 15, 20, 25, 30, 35, 40, model.input.years]);
      Array.from(years).filter(function (year) { return year <= model.input.years; })
        .sort(function (a, b) { return a - b; })
        .forEach(function (year) {
          const data = model.rows[year];
          const tr = document.createElement("tr");
          const th = document.createElement("th");
          th.scope = "row";
          th.textContent = String(year);
          tr.appendChild(th);
          [data.pia, data.pensionGross, data.pensionIllustrativeNet].forEach(function (value) {
            const td = document.createElement("td");
            td.textContent = euro.format(value);
            tr.appendChild(td);
          });
          body.appendChild(tr);
        });
    }
    results.hidden = false;
  }

  function run(eventName) {
    error.hidden = true;
    error.textContent = "";
    const invalid = Array.from(form.querySelectorAll("[required]")).find(function (field) {
      return !field.checkValidity();
    });
    if (invalid) {
      results.hidden = true;
      error.textContent = "Check the highlighted input. Values must be within the displayed limits.";
      error.hidden = false;
      invalid.reportValidity();
      return;
    }
    try {
      const result = calculate(currentInputs());
      render(result);
      if (eventName) {
        // Only record the *kind* of action, never monetary inputs or scenarios.
        try {
          if (root.localStorage && root.localStorage.getItem("compound_analytics_consent") === "granted" &&
              typeof root.gtag === "function") {
            root.gtag("event", "pia_pension_compare", { comparison_type: "pia_vs_pension" });
          }
        } catch (_err) { /* analytics never blocks calculator use */ }
      }
    } catch (err) {
      results.hidden = true;
      error.textContent = err.message || "Unable to model these assumptions.";
      error.hidden = false;
    }
  }

  function choosePreset(code) {
    const values = Object.assign({}, DEFAULTS);
    if (code === "basic20") values.relief = 20;
    else if (code === "match") {
      values.relief = 20;
      values.employerMonthly = 100;
    }
    fieldNames.forEach(function (name) { form.elements.namedItem(name).value = values[name]; });
    presets.forEach(function (button) {
      button.setAttribute("aria-pressed", button.dataset.piaExample === code ? "true" : "false");
    });
    run("preset");
  }

  presets.forEach(function (button) {
    button.addEventListener("click", function () { choosePreset(button.dataset.piaExample); });
  });
  form.addEventListener("input", function () {
    presets.forEach(function (button) { button.setAttribute("aria-pressed", "false"); });
  });
  form.addEventListener("change", function () {
    presets.forEach(function (button) { button.setAttribute("aria-pressed", "false"); });
  });
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    run("submit");
  });
  form.addEventListener("reset", function () {
    // A reset event precedes the browser restoring default form values.
    root.setTimeout(function () { choosePreset("basic40"); }, 0);
  });
  run(null); // Display the default illustration without logging a user action.
})(typeof window !== "undefined" ? window : this);
