## What this calculator is for

Retirement planning has two separate questions:

1. **How much gross income could the assets and pensions entered provide in the first year?**
2. **What happens to the investment pot if withdrawals continue and rise over time?**

This calculator keeps those questions visible instead of collapsing them into one headline number.

Basic mode gives first-year gross income and a simple 30-year sustainability path. Advanced mode adds a target-income check, explicit annual fees and a lower-return stress scenario.

## First-year retirement income

The calculator begins with a percentage withdrawal from the starting portfolio:

**starting portfolio × withdrawal rate = first-year portfolio withdrawal**

It then adds the annual State Pension/social-welfare income and other retirement income entered.

The total is shown annually and as an average monthly gross amount.

These are **gross** figures. They are not equivalent to spendable after-tax income.

## State Pension input

The State Pension field defaults to zero deliberately.

Not everyone will qualify for the maximum contributory rate, not everyone will be modelling a period after State Pension age, and rates can change.

For current context, the Pensions Authority's 2026 pension-calculator assumptions use a maximum State Pension (Contributory) figure of €15,563.60 per year, or €299.30 per week, from 1 January 2026. That is a reference assumption, not a promise of individual entitlement.

Enter an amount only if it is appropriate to the retirement period you are modelling.

## Tax treatment matters

Revenue states that personal and occupational pensions are taxable income and are generally subject to Income Tax and USC, with PRSI depending on circumstances.

Department of Social Protection pensions are liable to Income Tax but are not liable to USC or PRSI.

That difference is one reason this calculator does not try to turn several income sources into one universal net-income figure. A proper after-tax result depends on age, credits, total income, pension type and other personal circumstances.

Use the output as a **gross retirement-income framework**.

## Optional target-income check

Advanced mode lets you enter an annual gross-income target.

The engine then compares first-year modelled income with that target and shows the surplus or shortfall.

It also calculates the amount the portfolio would need to provide after the State Pension and other income entered, plus the starting withdrawal rate that would be required from the portfolio.

For example, if the target is €45,000 and the State Pension plus other income totals €20,000, the portfolio needs to provide €25,000 in year one.

On a €500,000 pot that would require a 5% starting withdrawal.

This is not a recommendation to withdraw 5%; it exposes the arithmetic behind the target.

## The deterministic sustainability model

The portfolio path is intentionally simple.

Each year, the engine:

1. grows the portfolio at the selected constant annual return;
2. deducts the selected annual percentage fee in Advanced mode;
3. deducts the portfolio withdrawal;
4. increases the next year's withdrawal by the inflation assumption.

Basic mode uses a 4% annual portfolio return, 2% annual increase in withdrawals and no explicit fee for 30 years.

If the balance reaches zero, the calculator reports the first modelled year of depletion.

## Baseline versus lower-return stress

Advanced mode adds a second return assumption.

Both paths use the same starting pot, withdrawal, fee and inflation-linked spending pattern. Only the constant annual return changes.

This gives a direct stress comparison without pretending it is a full probability model.

If the baseline path survives 30 years but the lower-return path depletes in year 22, the useful conclusion is not that either path will occur. It is that the plan is sensitive to the return assumption.

## Sequence-of-returns risk remains missing

A stress scenario is still not the same as market reality.

Real returns are volatile. A retiree can experience a large market fall in the first few years, continue taking withdrawals, and permanently reduce the capital available to recover later.

That is sequence-of-returns risk.

Two retirees can earn the same average return over 30 years and finish with very different outcomes depending on the order of those returns.

A constant-return calculator cannot capture that.

## Fees are shown separately

Advanced mode applies an annual percentage fee after the modelled annual investment growth and before the withdrawal.

The calculator accumulates those modelled fee deductions and reports them.

The number is useful for seeing scale, but real providers can charge at different frequencies or through several layers. Use product-specific documentation for an actual pension or investment.

## Today's-money ending pot

A nominal balance remaining after 30 years can look large while representing much less purchasing power.

Advanced mode therefore converts the ending portfolio into today's money using the inflation assumption.

This does not change the actual nominal path. It gives a second view of what the ending value might mean economically.

## Retirement lump sums are separate

This calculator assumes the full starting pot entered is available for the drawdown scenario.

In reality, pension benefits can involve retirement lump sums and different post-retirement options.

Revenue notes that a personal pension can provide a retirement lump sum of 25% of the fund, while occupational-scheme lump-sum rules can depend on salary and service. Revenue also applies lifetime tax limits to retirement lump sums.

If you plan to take a lump sum, enter the **post-lump-sum amount actually intended for the drawdown portfolio** rather than the pre-lump-sum pension value.

## Common mistakes to avoid

Do not treat the State Pension as available before the relevant age.

Do not compare gross retirement income with current net salary.

Do not assume a smooth 4% return arrives every year.

Do not ignore product fees because the withdrawal rate looks conservative.

Do not enter the full pension pot if part of it will be taken as a lump sum and spent or held elsewhere.

And do not regard “not depleted in 30 years” as proof that the plan is safe. It only means the deterministic path did not hit zero under those inputs.

## Related Compound tools

Use the [Pension Projection Calculator](/pension-projection-calculator/) for the accumulation phase, the [FIRE Number Calculator](/fire-number-calculator/) for a portfolio target, the [Pension Tax Relief Calculator](/pension-tax-relief-calculator/) for contribution relief limits and the [Investment Fee Calculator](/investment-fee-calculator/) to isolate fee drag.

## Frequently asked questions

### Does the calculator include tax?
No. It reports gross income.

### Does it increase the State Pension with inflation?
No. The State Pension and other income inputs are used for the first-year income calculation and target comparison. The sustainability path models the portfolio withdrawal separately.

### Why not let other income reduce every future portfolio withdrawal automatically?
Because the start dates and escalation rules for different income sources vary. A single automatic rule would create false precision.

### What does the lower-return scenario tell me?
It shows how the same withdrawal plan behaves under a different constant return assumption. It is a sensitivity test, not a forecast.

## Method and limitations

The first-year portfolio withdrawal is the starting pot multiplied by the selected withdrawal rate.

The baseline and stress simulations then run once per year. The portfolio receives the selected constant annual return, the annual percentage fee is deducted, and the inflation-linked withdrawal is taken.

The withdrawal amount itself starts from the selected percentage of the original pot and grows with the inflation assumption each year.

The target-income outputs do not change the sustainability-path withdrawal automatically; they show the arithmetic required to meet the separate target. This avoids silently overriding the withdrawal rate selected by the user.

The model excludes tax, sequence-of-returns volatility, changing asset allocation, annuity pricing, ARF-specific rules, future State Pension changes and product-specific restrictions.

### Useful sources

- [Revenue — Taxation of pensions](https://www.revenue.ie/en/jobs-and-pensions/pension/private/index.aspx)
- [Revenue — Taxation of Department of Social Protection pensions](https://www.revenue.ie/en/jobs-and-pensions/pension/dsp/index.aspx)
- [Revenue — Taxation of retirement lump sums](https://www.revenue.ie/en/jobs-and-pensions/pension/private/retirement-lump-sums.aspx)
- [Pensions Authority — Pension calculator assumptions](https://pensionsauthority.ie/scheme-members-and-prsa-contributors/pension-calculator/assumptions/)
