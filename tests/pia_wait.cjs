"use strict";
const assert = require("node:assert/strict");
const { estimate, breakEvenReturn, daysUntil } = require("../compound/site/static/pia-wait.js");
const near = (actual, expected, message, tolerance = 0.6) =>
  assert.ok(Math.abs(actual - expected) <= tolerance, message + ": expected " + expected + ", got " + actual);
const baseline = {
  today_iso: "2026-11-17", launch_iso: "2027-07-01",
  capital: 5000, annual_return: 6, investment_fee: 0.25,
  trade_cost: 10, cash_rate: 2, cgt_allowance: 1270,
  asset: "shares", etf_exit_rate: 35
};
assert.equal(daysUntil("2026-11-17", "2027-07-01"), 226);
assert.equal(daysUntil("2027-07-01", "2027-07-01"), 0);
assert.equal(daysUntil("2027-08-01", "2027-07-01"), 0);
let result = estimate(baseline);
near(result.invest_after_tax, 5165, "Static example: +6% shares");
near(result.cash_after_tax, 5041, "Static savings example");
near(result.savings_before_tax, 5062, "Savings gross before DIRT");
near(result.investment_disposal_tax, 0, "Share CGT exemption on small gain", 0.001);
near(result.trading_costs, 10, "Combined trading fees", 0.001);
assert.equal(result.pia_from_invest, result.invest_after_tax);
assert.equal(result.days, 226);
for (const [rate, shares, etf] of [[-15,4505,4505],[0,4982,4982],[6,5165,5104],[12,5345,5220]]) {
  near(estimate({...baseline, annual_return:rate}).invest_after_tax, shares, "Shares "+rate+"%");
  near(estimate({...baseline, annual_return:rate, asset:"etf"}).invest_after_tax, etf, "ETF "+rate+"%");
}
let etf35=estimate({...baseline,asset:"etf",annual_return:12,etf_exit_rate:35});
let etf38=estimate({...baseline,asset:"etf",annual_return:12,etf_exit_rate:38});
assert.ok(etf35.invest_after_tax>etf38.invest_after_tax,"Proposed 35% ETF rate should help after-tax returns");
let noExemption=estimate({...baseline,capital:12000,annual_return:25,cgt_allowance:0});
let fullExemption=estimate({...baseline,capital:12000,annual_return:25,cgt_allowance:1270});
assert.ok(noExemption.investment_disposal_tax>fullExemption.investment_disposal_tax);
assert.ok(fullExemption.invest_after_tax>noExemption.invest_after_tax);
let negative=estimate({...baseline,annual_return:-15});
assert.ok(negative.invest_after_tax<negative.cash_after_tax,"Loss cases should not be presented as always beating cash");
let overflowing=estimate({...baseline,capital:12000,annual_return:50});
assert.equal(overflowing.pia_from_invest,12000);
assert.ok(overflowing.outside_from_invest>0,"Excess gains cannot exceed annual contribution room");
let breakEven=breakEvenReturn(baseline);
assert.ok(breakEven>0 && breakEven<10,"Plausible break-even annual return");
let matched=estimate({...baseline,annual_return:breakEven});
near(matched.invest_after_tax, matched.cash_after_tax,"Computed return matches post-DIRT cash",0.01);
let zero=estimate({...baseline,capital:0});
near(zero.invest_after_tax,0,"Zero investment");
near(zero.cash_after_tax,0,"Zero savings");
assert.equal(breakEvenReturn({...baseline, capital:0}),null);
let past=estimate({...baseline,today_iso:"2027-10-01"});
near(past.invest_after_tax,5000,"After target date returns unaltered capital");
near(past.cash_after_tax,5000,"After target date does not model past interest");
console.log("PIA invest-now versus wait calculations passed");
