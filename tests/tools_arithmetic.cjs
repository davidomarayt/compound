'use strict';

const assert = require('node:assert/strict');
require('../compound/site/static/tools.js');

const {
  calculators,
  monthlyPayment,
  usc2026,
  annualClassA2026,
  selfEmployedNet2026,
  stampDutyResidential,
  mortgageOverpaymentProjection,
  mortgageSnapshot,
} = globalThis.CompoundToolsTest;

const close = (actual, expected, tolerance, message) => {
  assert.ok(Math.abs(actual - expected) <= tolerance, `${message}: expected ${expected}, got ${actual}`);
};

// Mortgage amortisation: €300k, 3.5%, 30 years.
close(monthlyPayment(300000, 3.5, 360), 1347.13, 0.02, 'mortgage payment');

// Mortgage overpayment timing: delaying regular extras costs interest; an early lump sum offsets that.
const overpayImmediate = mortgageOverpaymentProjection({
  balance: 250000, rate: 3.5, years: 25, overpayment: 100, __advanced: false
});
const overpayDelayed = mortgageOverpaymentProjection({
  balance: 250000, rate: 3.5, years: 25, overpayment: 100,
  overpayment_start_month: 12, lump_sum: 0, lump_sum_month: 12, __advanced: true
});
const overpayLump = mortgageOverpaymentProjection({
  balance: 250000, rate: 3.5, years: 25, overpayment: 100,
  overpayment_start_month: 12, lump_sum: 10000, lump_sum_month: 12, __advanced: true
});
close(overpayImmediate.base, 1251.5589, 0.001, 'overpayment base payment');
assert.equal(overpayImmediate.scenarioMonths, 267);
assert.equal(overpayDelayed.scenarioMonths, 269);
assert.equal(overpayLump.scenarioMonths, 253);
close(overpayImmediate.interest, 109858.14, 0.02, 'immediate overpayment interest');
close(overpayDelayed.interest, 111225.97, 0.02, 'delayed overpayment interest');
close(overpayLump.interest, 100575.47, 0.02, 'lump-sum overpayment interest');

// Standard residential Stamp Duty is progressive.
assert.equal(stampDutyResidential(400000), 4000);
assert.equal(stampDutyResidential(1200000), 14000);
assert.equal(stampDutyResidential(1600000), 28000);

// 2026 standard USC example published by Revenue for €50,000.
close(usc2026(50000), 1032.82, 0.01, '2026 USC on €50,000');
assert.equal(usc2026(13000), 0);

// Class A annual blend should use 39 weeks at 4.20% and 13 at 4.35%.
const prsi = annualClassA2026(50000);
close(prsi.annual, prsi.before * 39 + prsi.after * 13, 0.0001, '2026 PRSI blend');

// Self-employed non-PAYE USC includes the extra 3% surcharge above €100k.
const se100 = selfEmployedNet2026(100000, 0);
const se110 = selfEmployedNet2026(110000, 0);
const standardUscDelta = usc2026(110000) - usc2026(100000);
close((se110.usc - se100.usc) - standardUscDelta, 300, 0.01, 'non-PAYE USC surcharge');

// Mortgage affordability must respect LTI, payment capacity and 90% LTV deposit constraint.
const affordability = calculators.mortgage_affordability({
  income: 80000, buyer_type: 'ftb', deposit: 40000, rate: 4.5, term: 30,
  max_payment_pct: 30, other_debt: 0
});
assert.equal(affordability.lti_mortgage, '€320,000.00');
assert.equal(affordability.deposit_based_mortgage, '€360,000.00');
assert.equal(affordability.indicative_mortgage, '€320,000.00');
assert.equal(affordability.indicative_price, '€360,000.00');

const noDeposit = calculators.mortgage_affordability({
  income: 80000, buyer_type: 'ftb', deposit: 0, rate: 4.5, term: 30,
  max_payment_pct: 30, other_debt: 0
});
assert.equal(noDeposit.indicative_mortgage, '€0.00');
assert.equal(noDeposit.indicative_price, '€0.00');

// Mortgage switching: compare interest plus net switching cost over a five-year horizon.
const switchResult = calculators.mortgage_switch({
  balance: 250000, current_rate: 4.2, current_years: 20,
  new_rate: 3.4, new_years: 20,
  switching_costs: 1500, break_fee: 0, cashback: 0,
  comparison_years: 5, __advanced: true
});
assert.equal(switchResult.current_payment, '€1,541.43');
assert.equal(switchResult.new_payment, '€1,437.09');
assert.equal(switchResult.horizon_interest_current, '€48,077.63');
assert.equal(switchResult.horizon_interest_new, '€40,136.76');
assert.equal(switchResult.horizon_saving, '+€7,940.86');
assert.equal(switchResult.horizon_balance_difference, '+€3,180.40');
assert.equal(switchResult.lifetime_difference, '+€23,541.85');

// FIRE uses an implied real return when inputs are expressed in today's money.
const fire = calculators.fire_number({
  annual_spend: 36000, withdrawal_rate: 4, current: 100000,
  annual_contribution: 18000, return_rate: 6, inflation_rate: 2
});
assert.equal(fire.target, '€900,000.00');
assert.equal(fire.real_return, '3.92%');

// Investment fees are applied multiplicatively to the annual growth factor.
const fee = calculators.investment_fees({
  initial: 25000, monthly: 500, gross_return: 7, fee_low: 0.25, fee_high: 1.5, years: 25
});
assert.equal(fee.low_net_return, '6.73%');
assert.equal(fee.high_net_return, '5.40%');

// Pension projection should surface both nominal and inflation-adjusted outcomes.
const pension = calculators.pension_projection({
  age: 35, retirement_age: 65, current: 50000,
  monthly_employee: 400, monthly_employer: 300,
  return_rate: 6, annual_fee: 0.75, inflation_rate: 2
});
assert.match(pension.projected, /^€/);
assert.match(pension.projected_real, /^€/);
assert.notEqual(pension.projected, pension.projected_real);

// Retirement sustainability should report the deterministic horizon result.
const retirement = calculators.retirement_income({
  pot: 500000, withdrawal_rate: 4, state_pension: 0, other_income: 0,
  retirement_years: 30, return_rate: 4, inflation_rate: 2
});
assert.equal(retirement.portfolio_income, '€20,000.00');
assert.match(retirement.depletion, /(Not depleted|Depleted)/);

// LPT band 3 basic charge is €333 under the 2026–2030 schedule.
const lpt = calculators.lpt({value: 400000, authority: 'meath'});
assert.equal(lpt.base_lpt, '€333.00');
assert.equal(lpt.lpt, '€333.00');

// HTB: Local Authority Affordable Purchase contribution counts only in Advanced mode.
const htbBasic = calculators.help_to_buy({
  property_value: 400000, mortgage: 260000, tax_paid: 30000,
  la_affordable_contribution: 30000, __advanced: false
});
assert.equal(htbBasic.ltv, '65%');
assert.equal(htbBasic.claim, '€0.00');
assert.equal(htbBasic.eligibility, 'Qualifying finance is below 70%');

const htbAffordable = calculators.help_to_buy({
  property_value: 400000, mortgage: 260000, tax_paid: 30000,
  la_affordable_contribution: 30000, __advanced: true
});
assert.equal(htbAffordable.qualifying_finance, '€290,000.00');
assert.equal(htbAffordable.minimum_finance, '€280,000.00');
assert.equal(htbAffordable.ltv, '72.5%');
assert.equal(htbAffordable.claim, '€30,000.00');
assert.equal(htbAffordable.eligibility, 'Passes basic value/finance check');

// FHS: Meath ceiling, deposit/HTB funding stack and service-charge arithmetic.
const fhs = calculators.first_home_scheme({
  property_value: 400000, authority: 'meath', property_type: 'house',
  mortgage: 300000, deposit: 40000, htb: 'yes', htb_amount: 30000
});
assert.equal(fhs.price_ceiling, '€475,000.00');
assert.equal(fhs.gap, '€30,000.00');
assert.equal(fhs.share, '7.5%');
assert.equal(fhs.max_fhs, '€80,000.00');
assert.equal(fhs.year6_charge, '€525.00');
assert.equal(fhs.charges_to_year10, '€2,625.00');
assert.equal(fhs.check, 'Within calculator’s basic scheme range');

console.log('Calculator arithmetic regression checks passed.');
