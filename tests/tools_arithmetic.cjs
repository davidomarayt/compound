'use strict';

const assert = require('node:assert/strict');
require('../compound/site/static/tools.js');
require('../compound/site/static/debt-repayment.js');

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
assert.equal(stampDutyResidential(1600000), 26000);

// 2026 standard USC example published by Revenue for €50,000.
close(usc2026(50000), 1032.82, 0.01, '2026 USC on €50,000');
assert.equal(usc2026(13000), 0);

// 2026 reduced USC: qualifying taxpayers use 0.5% to €12,012 and 2% on the balance,
// but the reduced regime must fall back to standard rates above the €60,000 income ceiling.
close(usc2026(50000, true), 819.82, 0.01, '2026 reduced USC on €50,000');
close(usc2026(61000, true), usc2026(61000), 0.001, 'reduced USC fallback above €60,000');

const uscReduced = calculators.usc_2026({income: 50000, reduced_rate: 'yes', __advanced: true});
assert.equal(uscReduced.usc, '€819.82');
assert.equal(uscReduced.rate_basis, 'Reduced 2026 rates');

const uscFallback = calculators.usc_2026({income: 61000, reduced_rate: 'yes', __advanced: true});
assert.equal(uscFallback.rate_basis, 'Standard 2026 rates');

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

// Advanced affordability: an optional net-income household budget can be tighter than the gross-income percentage.
const affordabilityBudget = calculators.mortgage_affordability({
  income: 80000, buyer_type: 'ftb', deposit: 40000, rate: 0, term: 10,
  max_payment_pct: 30, other_debt: 0, net_income_monthly: 5000,
  essential_spend_monthly: 3000, buffer_monthly: 500, stress_rate_add: 1,
  __advanced: true
});
assert.equal(affordabilityBudget.gross_payment_limit, '€2,000.00');
assert.equal(affordabilityBudget.net_budget_limit, '€1,500.00');
assert.equal(affordabilityBudget.payment_capacity, '€1,500.00');
assert.equal(affordabilityBudget.payment_based_mortgage, '€180,000.00');
assert.equal(affordabilityBudget.indicative_mortgage, '€180,000.00');
assert.equal(affordabilityBudget.indicative_price, '€220,000.00');
assert.equal(affordabilityBudget.binding_constraint, 'Payment budget');
assert.equal(affordabilityBudget.stress_rate, '1%');

// Rent-vs-buy must include the final mortgage payment and stop mortgage cash outflow after payoff.
const rentBuyPayoff = calculators.rent_vs_buy({
  monthly_rent: 0, annual_rent_growth: 0, buying_costs: 0, owner_fixed_annual: 0,
  house_price: 100000, deposit: 10000, mortgage_rate: 0, mortgage_years: 1,
  house_growth: 0, maintenance_pct: 0, renter_return: 0, selling_cost_pct: 0,
  years: 2, __advanced: true
});
assert.equal(rentBuyPayoff.mortgage_payment, '€7,500.00');
assert.equal(rentBuyPayoff.owner_equity, '€100,000.00');
assert.equal(rentBuyPayoff.renter_portfolio, '€101,000.00');
assert.equal(rentBuyPayoff.difference, '-€1,000.00');
assert.equal(rentBuyPayoff.remaining_mortgage, '€0.00');
assert.equal(rentBuyPayoff.first_crossover, 'Not reached in 2 years');

// Advanced home-buying cash plan separates transaction/setup spending from the retained reserve.
const buyingCosts = calculators.house_buying_costs({
  price: 400000, deposit_pct: 10, legal: 2500, survey: 600, valuation: 200,
  moving: 1500, other: 1000, insurance_setup: 500, furnishing: 5000,
  immediate_works: 10000, reserve: 10000, cash_available: 70000, __advanced: true
});
assert.equal(buyingCosts.deposit, '€40,000.00');
assert.equal(buyingCosts.stamp, '€4,000.00');
assert.equal(buyingCosts.professional_costs, '€3,300.00');
assert.equal(buyingCosts.moving_setup_costs, '€18,000.00');
assert.equal(buyingCosts.other_costs, '€21,300.00');
assert.equal(buyingCosts.total_upfront, '€65,300.00');
assert.equal(buyingCosts.mortgage_required, '€360,000.00');
assert.equal(buyingCosts.cash_target, '€75,300.00');
assert.equal(buyingCosts.cash_position, '-€5,300.00 shortfall');

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
assert.equal(fee.high_net_return, '5.4%');

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

// Core mortgage/deposit arithmetic: standard Central Bank LTI/LTV constraints.
const borrowing = calculators.mortgage_borrowing({
  income: 80000, buyer_type: 'ftb', deposit: 40000, target_price: 400000, __advanced: true
});
assert.equal(borrowing.lti_multiple, '4× gross income');
assert.equal(borrowing.lti_limit, '€320,000.00');
assert.equal(borrowing.deposit_limit, '€400,000.00');
assert.equal(borrowing.purchase_price, '€360,000.00');
assert.equal(borrowing.binding_constraint, 'Income');
assert.equal(borrowing.target_mortgage, '€360,000.00');
assert.equal(borrowing.target_income, '€90,000.00');
assert.equal(borrowing.target_min_deposit, '€40,000.00');
assert.equal(borrowing.target_gap, '€40,000.00');

const deposit = calculators.house_deposit({
  price: 400000, buyer_type: 'home', deposit_available: 60000, __advanced: true
});
assert.equal(deposit.deposit_rate, '10%');
assert.equal(deposit.deposit, '€40,000.00');
assert.equal(deposit.mortgage, '€360,000.00');
assert.equal(deposit.ltv, '90%');
assert.equal(deposit.deposit_position, '+€20,000.00 above minimum');
assert.equal(deposit.resulting_ltv, '85%');
assert.equal(deposit.mortgage_with_available, '€340,000.00');

// Stamp Duty is progressive: €1m at 1% plus €200k at 2% = €14k.
const stamp = calculators.stamp_duty({price: 1200000});
assert.equal(stamp.band_1_duty, '€10,000.00');
assert.equal(stamp.band_2_duty, '€4,000.00');
assert.equal(stamp.band_6_duty, '€0.00');
assert.equal(stamp.duty, '€14,000.00');
assert.equal(stamp.total_cost, '€1,214,000.00');

// LPT band 3 basic charge is €333 under the 2026–2030 schedule.
const lpt = calculators.lpt({value: 400000, authority: 'meath'});
assert.equal(lpt.valuation_band, '€315,001–€420,000');
assert.equal(lpt.base_lpt, '€333.00');
assert.equal(lpt.local_factor, '0%');
assert.equal(lpt.lpt, '€333.00');
assert.equal(lpt.monthly_lpt, '€27.75');

// Local Adjustment Factor test: Dún Laoghaire-Rathdown is -15% in 2026.
const lptDlr = calculators.lpt({value: 400000, authority: 'dlr'});
assert.equal(lptDlr.adjustment, '-€49.95');
assert.equal(lptDlr.lpt, '€283.05');

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

// Tax/pay flagship outputs added in the September 2026 upgrade.
const hourly = calculators.salary_hourly({salary: 50000, hours: 39, weeks: 52, days: 5});
assert.equal(hourly.hourly, '€24.65');
assert.equal(hourly.annual_hours, '2,028 hours');

const takeHomeReduced = calculators.take_home_2026({
  salary: 50000, pension_pct: 0, band: 44000, other_credits: 0,
  usc_reduced: 'yes', __advanced: true
});
assert.equal(takeHomeReduced.usc, '€819.82');
assert.match(takeHomeReduced.deductions, /^€/);
assert.match(takeHomeReduced.effective_deductions, /%$/);
assert.match(takeHomeReduced.next_1000_net, /€/);

const prsiFlagship = calculators.prsi_2026({salary: 52000});
assert.equal(prsiFlagship.weekly_equivalent, '€1,000.00');
assert.equal(prsiFlagship.october_increase, '€19.50');

const rentCreditFlagship = calculators.rent_credit({
  rent: 12000, joint: 'no', income_tax_liability: 5000
});
assert.equal(rentCreditFlagship.credit, '€1,000.00');
assert.equal(rentCreditFlagship.rent_for_max, '€5,000.00');
assert.equal(rentCreditFlagship.unused_cap, '€0.00');

const contractorFlagship = calculators.contractor_vs_salary({
  salary: 70000, day_rate: 450, billable_days: 220,
  contractor_costs: 5000, contractor_pension: 0
});
assert.match(contractorFlagship.break_even_day_rate, /^€[\d,.]+\/day$/);


// Flagship loan: an extra €100/month plus a €1,000 month-12 lump sum shortens the schedule.
const loanAdvanced = calculators.loan({
  amount: 20000, rate: 7.5, years: 5, upfront_fee: 100,
  extra_monthly: 100, extra_start_month: 1, lump_sum: 1000, lump_sum_month: 12,
  __advanced: true
});
assert.equal(loanAdvanced.monthly, '€400.76');
assert.equal(loanAdvanced.payoff_time, '3 yr 8 mo');
assert.equal(loanAdvanced.scenario_interest, '€2,850.18');
assert.equal(loanAdvanced.interest_saved, '€1,195.35');
assert.equal(loanAdvanced.scenario_total, '€22,950.18');

// Fuel annualisation should use the same L/100km and pump-price assumptions.
const fuelAnnual = calculators.fuel({
  distance: 100, consumption: 6.5, price: 1.75, trips: 1,
  annual_distance: 15000, __advanced: true
});
assert.equal(fuelAnnual.cost_per_km, '€0.11');
assert.equal(fuelAnnual.annual_litres, '975 L');
assert.equal(fuelAnnual.annual_cost, '€1,706.25');

// Mixed EV charging: 80% at €0.20 and 20% at €0.60 = €0.28/kWh blended.
// 15,000 km at 18 kWh/100km with 10% charging losses = 3,000 grid kWh.
const evAnnual = calculators.ev({
  distance: 100, efficiency: 18, price: 0.20, loss: 10,
  home_share: 80, public_price: 0.60, annual_distance: 15000,
  ice_consumption: 6.5, fuel_price: 1.75, __advanced: true
});
assert.equal(evAnnual.blended_rate, '€0.28/kWh');
assert.equal(evAnnual.annual_wall_kwh, '3,000 kWh');
assert.equal(evAnnual.annual_cost, '€840.00');
assert.equal(evAnnual.ice_annual_cost, '€1,706.25');
assert.equal(evAnnual.annual_saving_vs_ice, '+€866.25');

// Appliance advanced mode: 2 kW × 1h × 30 days × 50% duty = 30 kWh;
// 50/50 split across €0.30 and €0.10 tariffs = €0.20/kWh.
const applianceAdvanced = calculators.electricity({
  watts: 2000, hours: 1, days: 30, price: 0.30,
  duty_cycle: 50, offpeak_share: 50, offpeak_rate: 0.10, __advanced: true
});
assert.equal(applianceAdvanced.kwh, '30 kWh');
assert.equal(applianceAdvanced.monthly, '€6.00');
assert.equal(applianceAdvanced.annual, '€72.00');
assert.equal(applianceAdvanced.annual_kwh, '360 kWh');
assert.equal(applianceAdvanced.blended_rate, '€0.20/kWh');

// 2026 retrofit: semi-detached heat pump with explicit central-heating grant + renewable-heat bonus.
// Base heat-pump grant €6,500 + conditional €6,000 + €350 assessment + €1,600 PM.
const retrofitAdvanced = calculators.retrofit_planner({
  home_type: 'semi', oss_eligible: true, first_time_buyer: false,
  annual_energy_bill: 3000, saving_pct: 35,
  attic: false, attic_cost: 2500, external_wall: false, wall_cost: 18000,
  windows: false, windows_cost: 12000, heat_pump: true, heat_pump_cost: 14000,
  central_heating_upgrade: true, renewable_heat_bonus: true,
  solar: false, solar_cost: 8000, solar_kwp: 4,
  doors: false, doors_cost: 3000, door_count: 2,
  ventilation: false, ventilation_cost: 5000,
  airtightness: false, airtightness_cost: 2500,
  other_cost: 3000, include_oss_services: true, __advanced: true
});
assert.equal(retrofitAdvanced.base_grants, '€6,500.00');
assert.equal(retrofitAdvanced.conditional_heat_grants, '€6,000.00');
assert.equal(retrofitAdvanced.oss_service_grants, '€1,950.00');
assert.equal(retrofitAdvanced.grants, '€14,450.00');
assert.equal(retrofitAdvanced.net_cost, '€2,550.00');


// Family & Life Planning + Health flagship regression coverage.
const childcareBasic = calculators.childcare_return({
  salary: 45000, pension_pct: 8, work_hours: 35, children: 1, childcare_hours: 40,
  childcare_fee: 8, ncs_rate: 2.14, childcare_weeks: 48, commute_weekly: 80,
  work_cost_weekly: 30, other_annual: 500, standard_rate_band: 50000,
  extra_tax_credits: 500, reduced_usc: 'no', __advanced: false
});
assert.equal(childcareBasic.work_costs, '€0.00');
assert.match(childcareBasic.monthly_gain, /^[+-]€/);
assert.match(childcareBasic.breakeven_salary, /^€/);

const childcareAdvanced = calculators.childcare_return({
  salary: 45000, pension_pct: 5, work_hours: 35, children: 1, childcare_hours: 40,
  childcare_fee: 8, ncs_rate: 2.14, childcare_weeks: 48, commute_weekly: 80,
  work_cost_weekly: 30, other_annual: 500, standard_rate_band: 44000,
  extra_tax_credits: 0, reduced_usc: 'no', __advanced: true
});
assert.notEqual(childcareAdvanced.work_costs, '€0.00');
assert.match(childcareAdvanced.retained_pct, /%$/);

const lifetimeBasic = calculators.lifetime_cost({
  current_age: 30, end_age: 40, inflation: 2.5, housing_monthly: 1500, housing_until: 32,
  food_monthly: 600, utilities_monthly: 300, transport_monthly: 400, leisure_monthly: 300,
  travel_annual: 3000, insurance_health_annual: 2500, childcare_annual: 10000, childcare_years: 5,
  major_purchase: 30000, major_interval: 5, other_monthly: 500, __advanced: false
});
const lifetimeAdvanced = calculators.lifetime_cost({
  current_age: 30, end_age: 40, inflation: 2.5, housing_monthly: 1500, housing_until: 32,
  food_monthly: 600, utilities_monthly: 300, transport_monthly: 400, leisure_monthly: 300,
  travel_annual: 3000, insurance_health_annual: 2500, childcare_annual: 10000, childcare_years: 5,
  major_purchase: 30000, major_interval: 5, other_monthly: 500, __advanced: true
});
assert.equal(lifetimeBasic.major_total, '€0.00');
assert.notEqual(lifetimeAdvanced.major_total, '€0.00');
assert.match(lifetimeAdvanced.inflation_uplift, /^€/);

const weightLossBasic = calculators.weight_loss({
  current_weight: 100, height: 180, target_weight: 90, weekly_rate: 0.5,
  include_waist: false, waist: 100, __advanced: false
});
assert.equal(weightLossBasic.kg_to_target, '10 kg');
assert.equal(weightLossBasic.percentage_to_target, '10%');
assert.equal(weightLossBasic.milestone_10, '90 kg');
assert.equal(weightLossBasic.current_bmi_category, 'Obesity');
assert.equal(weightLossBasic.waist_height_ratio, 'Not included');

const weightLossAdvanced = calculators.weight_loss({
  current_weight: 100, height: 180, target_weight: 90, weekly_rate: 0.5,
  include_waist: true, waist: 90, __advanced: true
});
assert.match(weightLossAdvanced.estimated_time, /^20 weeks/);
assert.equal(weightLossAdvanced.waist_height_ratio, '0.5');
assert.match(weightLossAdvanced.waist_context, /0.5/);
assert.equal(weightLossAdvanced.__chart.series[0].values.length, 6);

const pregnancyCycle = calculators.pregnancy_timeline({
  lmp: '2026-01-01', assigned_due_date: '', cycle_length: 35, __advanced: true
});
assert.match(pregnancyCycle.due_date, /adjusted \+7 days for cycle length/);
assert.match(pregnancyCycle.pregnancy_progress, /%$/);
assert.match(pregnancyCycle.week42, /29 October 2026/);
assert.ok(pregnancyCycle.__chart.series[0].values.length === 2);

const nutritionBasic = calculators.nutrition_needs({
  sex: 'male', age: 35, weight: 75, height: 175, activity: '1.6',
  energy_scenario: 'lower10', protein_context: 'resistance', __advanced: false
});
assert.equal(nutritionBasic.protein_per_kg, '0.83 g/kg/day');
assert.equal(nutritionBasic.energy_delta, '+0 kcal/day');

const nutritionAdvanced = calculators.nutrition_needs({
  sex: 'male', age: 35, weight: 75, height: 175, activity: '1.6',
  energy_scenario: 'lower10', protein_context: 'resistance', __advanced: true
});
assert.equal(nutritionAdvanced.protein_per_kg, '1.6 g/kg/day');
assert.match(nutritionAdvanced.energy_delta, /^-/);

const alcoholBasic = calculators.alcohol_ireland({
  guideline_group: 'woman', beer_pints: 2, beer_abv: 12, wine_glasses: 0, wine_ml: 300,
  wine_abv: 20, spirits: 0, spirit_ml: 100, spirit_abv: 80, cans: 0, can_ml: 1000,
  can_abv: 12, weekly_spend: 100, reduction_pct: 50, __advanced: false
});
assert.equal(alcoholBasic.annual_spend, '€0.00');
assert.equal(alcoholBasic.reduced_drinks, alcoholBasic.standard_drinks);
assert.match(alcoholBasic.guideline, /HSE weekly low-risk limit/);

const alcoholAdvanced = calculators.alcohol_ireland({
  guideline_group: 'woman', beer_pints: 2, beer_abv: 12, wine_glasses: 0, wine_ml: 300,
  wine_abv: 20, spirits: 0, spirit_ml: 100, spirit_abv: 80, cans: 0, can_ml: 1000,
  can_abv: 12, weekly_spend: 100, reduction_pct: 50, __advanced: true
});
assert.equal(alcoholAdvanced.annual_spend, '€5,200.00');
assert.notEqual(alcoholAdvanced.reduced_drinks, alcoholAdvanced.standard_drinks);


// Solar flagship Basic/Advanced behaviour.
const solarBasic = calculators.solar_payback({
  system_cost: 9000, grant_eligible: true, kwp: 4, generation_per_kwp: 850,
  annual_home_kwh: 4200, direct_solar_pct: 35, import_rate: 0.30, export_rate: 0.15,
  has_ev: true, annual_ev_km: 15000, ev_efficiency: 18, ev_loss_pct: 10,
  ev_home_charge_pct: 80, ev_solar_share_pct: 50, ev_alternative_rate: 0.10,
  has_battery: true, battery_cost: 4500, battery_kwh: 5, battery_efficiency: 90,
  solar_to_battery_pct: 60, night_charge: true, night_rate: 0.10,
  night_battery_kwh_day: 3, __advanced: false
});
assert.equal(solarBasic.grant, '€1,800.00');
assert.equal(solarBasic.net_cost, '€7,200.00');
assert.equal(solarBasic.total_demand, '4,200 kWh');
assert.equal(solarBasic.battery_incremental_value, 'Not included');
assert.equal(solarBasic.solar_annual, undefined);
assert.match(solarBasic.self_consumption, /%$/);
assert.equal(solarBasic.twenty_year_net, '+€6,570.00');

const solarAdvanced = calculators.solar_payback({
  system_cost: 9000, grant_eligible: true, kwp: 4, generation_per_kwp: 850,
  annual_home_kwh: 4200, direct_solar_pct: 35, import_rate: 0.30, export_rate: 0.15,
  has_ev: true, annual_ev_km: 15000, ev_efficiency: 18, ev_loss_pct: 10,
  ev_home_charge_pct: 80, ev_solar_share_pct: 50, ev_alternative_rate: 0.10,
  has_battery: true, battery_cost: 4500, battery_kwh: 5, battery_efficiency: 90,
  solar_to_battery_pct: 60, night_charge: true, night_rate: 0.10,
  night_battery_kwh_day: 3, __advanced: true
});
assert.equal(solarAdvanced.net_cost, '€11,700.00');
assert.notEqual(solarAdvanced.total_demand, '4,200 kWh');
assert.notEqual(solarAdvanced.battery_incremental_value, 'Not included');
assert.match(solarAdvanced.battery_incremental_payback, /(years|Not reached)$/);

const optimiserBasicNoEv = calculators.solar_optimizer({
  solar_cost: 9000, grant_eligible: true, kwp: 4, generation_per_kwp: 850,
  home_kwh: 4200, direct_home_pct: 90, day_rate: 0.30, export_rate: 0.15,
  has_ev: false, ev_km: 15000, ev_efficiency: 40, ev_loss_pct: 35,
  ev_home_pct: 20, ev_solar_pct: 100, ev_grid_rate: 0.10, smart_ev_cost: 1000,
  battery_cost: 4500, battery_kwh: 5, battery_efficiency: 60,
  solar_capture_pct: 100, use_night_charge: true, night_rate: 0.10,
  night_kwh_day: 8, __advanced: false
});
assert.equal(optimiserBasicNoEv.solar_annual, '€688.50');
assert.equal(optimiserBasicNoEv.solar_benefit, '+€6,570.00');
assert.equal(optimiserBasicNoEv.ev_payback, 'EV not included');
assert.equal(optimiserBasicNoEv.ev_benefit, 'EV not included');
assert.equal(optimiserBasicNoEv.__chart.labels.length, 2);
assert.match(optimiserBasicNoEv.best_margin, /^\+€/);

const optimiserAdvancedEv = calculators.solar_optimizer({
  solar_cost: 9000, grant_eligible: true, kwp: 4, generation_per_kwp: 850,
  home_kwh: 4200, direct_home_pct: 35, day_rate: 0.30, export_rate: 0.15,
  has_ev: true, ev_km: 15000, ev_efficiency: 18, ev_loss_pct: 10,
  ev_home_pct: 80, ev_solar_pct: 35, ev_grid_rate: 0.10, smart_ev_cost: 1000,
  battery_cost: 4500, battery_kwh: 5, battery_efficiency: 90,
  solar_capture_pct: 60, use_night_charge: true, night_rate: 0.10,
  night_kwh_day: 3, __advanced: true
});
assert.notEqual(optimiserAdvancedEv.ev_payback, 'EV not included');
assert.notEqual(optimiserAdvancedEv.combined_benefit, 'EV not included');
assert.equal(optimiserAdvancedEv.__chart.labels.length, 4);


// Final simple-calculator flagship output regression coverage.
const mortgageCore = calculators.mortgage({amount: 300000, rate: 3.5, years: 30});
assert.equal(mortgageCore.monthly, '€1,347.13');
assert.equal(mortgageCore.annual_repayment, '€16,165.61');
assert.equal(mortgageCore.first_year_interest, '€10,408.22');
assert.equal(mortgageCore.first_year_principal, '€5,757.38');
assert.equal(mortgageCore.balance_5y, '€269,091.22');
assert.equal(mortgageCore.stress_1pp, '€1,520.06');
assert.equal(mortgageCore.stress_2pp, '€1,703.37');
assert.equal(mortgageCore.payment_per_100k, '€449.04');

const vatCore = calculators.vat({amount: 100, direction: 'net', rate: '23'});
assert.equal(vatCore.vat, '€23.00');
assert.equal(vatCore.gross, '€123.00');
assert.equal(vatCore.vat_share_gross, '18.7%');
assert.equal(vatCore.multiplier, '1.23×');

assert.equal(hourly.fortnightly, '€1,923.08');
assert.equal(hourly.workday_hours, '7.8 hours');
assert.equal(hourly.weekly_hours_share, '23.21%');

assert.equal(prsiFlagship.annual_if_old_rate, '€2,184.00');
assert.equal(prsiFlagship.annual_if_new_rate, '€2,262.00');
assert.equal(prsiFlagship.monthly_equivalent, '€183.63');

assert.equal(rentCreditFlagship.binding_limit, '2026 statutory cap');
assert.equal(rentCreditFlagship.effective_rent_relief, '8.33%');

const berCore = calculators.ber_energy({
  area: 120, current_kwh_m2: 180, target_kwh_m2: 90, energy_price: 0.18
});
assert.equal(berCore.current_use, '21,600 kWh');
assert.equal(berCore.target_use, '10,800 kWh');
assert.equal(berCore.saving, '+€1,944.00');
assert.equal(berCore.monthly_saving, '+€162.00');
assert.equal(berCore.energy_reduction, '50%');
assert.equal(berCore.ten_year_saving, '+€19,440.00');


// Direct regression examples for engines previously covered only indirectly.
const overpayDirect = calculators.mortgage_overpayment({
  balance: 250000, rate: 3.5, years: 25, overpayment: 100,
  overpayment_start_month: 0, lump_sum: 0, lump_sum_month: 12, __advanced: false
});
assert.match(overpayDirect.payment, /^€/);
assert.match(overpayDirect.interest_saved, /^€/);
assert.notEqual(overpayDirect.time_saved, 'Already reached');

const savingsGoalDirect = calculators.savings_goal({
  target: 1000, current: 0, monthly: 100, rate: 0,
  annual_contribution_growth: 0, annual_lump: 0, target_growth: 0, __advanced: false
});
assert.equal(savingsGoalDirect.time, '10 months');
assert.equal(savingsGoalDirect.contributions, '€1,000.00');
assert.equal(savingsGoalDirect.growth, '€0.00');

const netWorthDirect = calculators.net_worth({
  cash: 10000, investments: 20000, pensions: 30000, home_value: 400000,
  other_property: 0, vehicles: 0, business_value: 0, other_assets: 0,
  mortgage: 200000, other_property_mortgage: 0, loans: 10000,
  credit_cards: 5000, other_debt: 5000, tax_liabilities: 0, __advanced: false
});
assert.equal(netWorthDirect.total_assets, '€460,000.00');
assert.equal(netWorthDirect.total_liabilities, '€220,000.00');
assert.equal(netWorthDirect.net_worth, '€240,000.00');
assert.equal(netWorthDirect.property_equity, '€200,000.00');

const regularSavingsDirect = calculators.regular_savings({
  current: 0, monthly: 100, years: 1, rate: 0,
  annual_contribution_growth: 0, annual_fee: 0, inflation_rate: 0, __advanced: false
});
assert.equal(regularSavingsDirect.final, '€1,200.00');
assert.equal(regularSavingsDirect.contributed, '€1,200.00');
assert.equal(regularSavingsDirect.growth, '€0.00');

const pensionReliefDirect = calculators.pension_relief({
  age: 35, earnings: 60000, contribution: 6000, existing_contributions: 0,
  tax_rate: '40', __advanced: false
});
assert.equal(pensionReliefDirect.age_percentage, '20%');
assert.equal(pensionReliefDirect.limit, '€12,000.00');
assert.equal(pensionReliefDirect.relief, '€2,400.00');
assert.equal(pensionReliefDirect.net_cost, '€3,600.00');

const cgtDirect = calculators.cgt({
  sale: 30000, purchase: 15000, costs: 0, losses: 0, exemption_used: 0, __advanced: false
});
assert.equal(cgtDirect.gain, '€15,000.00');
assert.equal(cgtDirect.taxable, '€13,730.00');
assert.equal(cgtDirect.tax, '€4,530.90');

const inflationDirect = calculators.inflation({
  amount: 1000, rate: 0, years: 10, nominal_return: 0, __advanced: false
});
assert.equal(inflationDirect.future_cost, '€1,000.00');
assert.equal(inflationDirect.purchasing_power, '€1,000.00');
assert.equal(inflationDirect.lost_power, '€0.00');
assert.equal(inflationDirect.price_multiplier, '1×');

const emergencyDirect = calculators.emergency({
  expenses: 2000, months: '6', annual_essentials: 0, extra_buffer: 0,
  current: 3000, monthly: 300, interest_rate: 0, deadline_months: 24, __advanced: false
});
assert.equal(emergencyDirect.target, '€12,000.00');
assert.equal(emergencyDirect.gap, '€9,000.00');
assert.equal(emergencyDirect.time, '2 yr 6 mo');
assert.equal(emergencyDirect.interest_growth, '€0.00');

const incomeTaxDirect = calculators.income_tax_2026({
  income: 60000, pension: 0, band: 44000, credits: 4000, __advanced: false
});
assert.equal(incomeTaxDirect.tax20, '€8,800.00');
assert.equal(incomeTaxDirect.tax40, '€6,400.00');
assert.equal(incomeTaxDirect.gross_tax, '€15,200.00');
assert.equal(incomeTaxDirect.final_tax, '€11,200.00');

const catDirect = calculators.cat({
  benefit: 500000, prior: 0, group: 'A', benefit_type: 'inheritance',
  small_gift_used: 0, __advanced: false
});
assert.equal(catDirect.threshold, '€400,000.00');
assert.equal(catDirect.current_taxable_value, '€500,000.00');
assert.equal(catDirect.cat, '€33,000.00');

const dirtDirect = calculators.dirt({
  interest: 1000, deposit: 50000, gross_rate: 3, years: 5, __advanced: false
});
assert.equal(dirtDirect.dirt, '€330.00');
assert.equal(dirtDirect.net, '€670.00');
assert.equal(dirtDirect.retained, '67%');

const myFutureFundDirect = calculators.myfuturefund({
  employment_status: 'employee', age: 30, salary: 50000, workplace_pension: false,
  assume_opt_in: false, current_fund: 0, retirement_age: 66,
  salary_growth: 2, return_rate: 5, inflation_rate: 2, __advanced: false
});
assert.equal(myFutureFundDirect.status, 'Likely auto-enrolled');
assert.equal(myFutureFundDirect.employee_2026, '€750.00');
assert.equal(myFutureFundDirect.employer_2026, '€750.00');
assert.equal(myFutureFundDirect.state_2026, '€250.00');
assert.equal(myFutureFundDirect.total_2026, '€1,750.00');

const carFinanceDirect = calculators.car_finance({
  car_price: 40000, deposit: 8000, term_years: 4,
  loan_rate: 6.5, hp_rate: 6.9, pcp_rate: 4.9, pcp_balloon: 18000,
  loan_term_years: 4, hp_term_years: 4, pcp_term_years: 3,
  loan_fee: 0, hp_doc_fee: 75, hp_completion_fee: 75,
  pcp_doc_fee: 75, pcp_completion_fee: 75, estimated_value: 21000,
  annual_mileage_limit: 15000, expected_annual_mileage: 18000,
  excess_km_charge: 0.10, condition_charge: 0, __advanced: false
});
assert.match(carFinanceDirect.loan_monthly, /^€/);
assert.match(carFinanceDirect.hp_monthly, /^€/);
assert.match(carFinanceDirect.pcp_monthly, /^€/);
assert.match(carFinanceDirect.pcp_equity, /Switch to Advanced/);
assert.match(carFinanceDirect.ownership_summary, /Loan: owned from day 1/);


const redundancyDirect = calculators.redundancy_ireland({
  years: 10, weekly_pay: 800, ex_gratia: 50000, avg_annual_pay: 60000,
  pension_lump_sum: 0, prior_exempt: 0, increased_eligible: true, __advanced: true
});
assert.equal(redundancyDirect.statutory, '€12,600.00');
assert.equal(redundancyDirect.scsb, '€40,000.00');
assert.equal(redundancyDirect.tax_free_ex_gratia, '€40,000.00');
assert.equal(redundancyDirect.taxable_ex_gratia, '€10,000.00');

const selfEmployedDirect = calculators.self_employed_tax_ireland({
  gross_income: 50000, expenses: 10000, age: 35, pension: 0, __advanced: false
});
assert.equal(selfEmployedDirect.profit, '€40,000.00');
assert.equal(selfEmployedDirect.income_tax, '€4,000.00');
assert.equal(selfEmployedDirect.usc, '€732.82');
assert.equal(selfEmployedDirect.prsi, '€1,695.00');
assert.equal(selfEmployedDirect.net_income, '€33,572.18');

const pensionLumpDirect = calculators.pension_lump_sum_ireland({
  fund: 1200000, previous_lump_sums: 100000, custom_lump_sum: 0,
  marginal_rate: 40, __advanced: false
});
assert.equal(pensionLumpDirect.gross_lump, '€300,000.00');
assert.equal(pensionLumpDirect.tax_free_current, '€100,000.00');
assert.equal(pensionLumpDirect.at_20, '€200,000.00');
assert.equal(pensionLumpDirect.total_tax, '€40,000.00');
assert.equal(pensionLumpDirect.net_lump, '€260,000.00');


// Dedicated debt payoff engine: strategy target selection and payoff invariants.
const {chooseTarget: chooseDebtTarget, simulate: simulateDebt} = globalThis.CompoundDebtTest;
const debtChoice = [
  {name:'High APR', balance:2000, apr:20, minimum:60, index:0},
  {name:'Small balance', balance:500, apr:5, minimum:30, index:1}
];
assert.equal(chooseDebtTarget(debtChoice, 'avalanche').name, 'High APR');
assert.equal(chooseDebtTarget(debtChoice, 'snowball').name, 'Small balance');

const debtScenario = [
  {name:'High APR', balance:4000, apr:19.9, minimum:120},
  {name:'Personal loan', balance:3000, apr:8.5, minimum:100},
  {name:'Small loan', balance:900, apr:5, minimum:50}
];
const debtAvalanche = simulateDebt(debtScenario, 150, 'avalanche');
const debtSnowball = simulateDebt(debtScenario, 150, 'snowball');
assert.equal(debtAvalanche.success, true);
assert.equal(debtSnowball.success, true);
assert.ok(debtAvalanche.interest <= debtSnowball.interest + 0.01);
assert.equal(debtAvalanche.schedule[0], 7900);
assert.ok(debtAvalanche.schedule.at(-1) <= 0.005);
assert.equal(debtAvalanche.payoffOrder.length, 3);

console.log('Calculator arithmetic regression checks passed.');
