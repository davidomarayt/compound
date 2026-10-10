const assert = require("node:assert/strict");
const { estimateAnnualCost, clampNumber } = require("../compound/site/static/pia-providers.js");

const fee = {
  verified: true, account_annual_eur: 12, account_annual_pct: 0.2,
  custody_annual_pct: 0.1, fund_annual_pct: 0.3, trade_eur: 1
};
assert.equal(estimateAnnualCost(fee, 10000, 12), 84);
assert.equal(estimateAnnualCost({ ...fee, verified: false }, 10000, 12), null);
assert.equal(estimateAnnualCost({ ...fee, fund_annual_pct: undefined }, 10000, 12), null);
assert.equal(estimateAnnualCost({ verified: true, account_annual_eur: 0, account_annual_pct: 0, custody_annual_pct: 0, fund_annual_pct: 0, trade_eur: 0 }, 10000, 12), 0);
assert.equal(clampNumber(-3, 0, 100), 0);
assert.equal(estimateAnnualCost(fee, -500, 12), 24);
assert.equal(estimateAnnualCost(fee, 10000, 0), 72);
console.log("PIA provider fee scenario calculations passed");
