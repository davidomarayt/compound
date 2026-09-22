## What this calculator is for

This calculator projects how an existing pension pot and future contributions could grow to a selected retirement age.

It is an accumulation model, not a provider forecast. The goal is to make the main drivers visible: time, employee contributions, employer contributions, additional personal contributions, fees, investment return and inflation.

Basic mode keeps the assumptions deliberately simple. Advanced mode adds contribution growth, annual AVCs, an editable fee and a lower-return stress scenario.

## Basic projection

Basic mode uses:

- the current pension value entered;
- the employee and employer monthly contributions entered;
- 6% annual gross investment return;
- 0.75% annual fund fee;
- level monthly contributions;
- 2% annual inflation.

The result shows both the future nominal pot and its value in today's money.

Those defaults are planning assumptions, not predictions.

## Contributions deserve separate attention

Long-term pension projections can become dominated by return assumptions because small percentage changes compound over decades.

But return is not the only driver, and it is not the one most people directly control.

The calculator therefore separates:

- employee/personal contributions;
- employer contributions;
- investment growth.

Advanced mode also shows the monthly employee and employer contribution reached in the final year when contribution growth is used.

This makes it easier to see whether a stronger result came from a more ambitious savings plan or simply from assuming a higher market return.

## Annual contribution growth

Advanced mode can increase both the employee and employer monthly contributions by the selected percentage once per year.

This can approximate a contribution rate that rises with salary, but it does not calculate salary or percentage-of-salary contributions directly.

For example, a 3% annual contribution-growth assumption takes a €400 monthly employee contribution to roughly €538 after 10 annual increases.

Use a realistic assumption. A contribution-growth rate that cannot be supported by future earnings will overstate the projection.

## Annual AVC or personal contribution

Advanced mode includes an additional annual employee/personal contribution.

This can represent an AVC or another yearly top-up paid into the pension.

The model adds it at the end of each projection year.

Do not assume the entire amount automatically qualifies for Income Tax relief. Revenue applies age-related contribution limits and a €115,000 earnings ceiling to employee/personal pension relief.

The dedicated [Pension Tax Relief Calculator](/pension-tax-relief-calculator/) is designed for that separate question.

## Revenue's relief limits

Revenue's current age-related employee/personal contribution limits are:

- under 30: 15% of relevant earnings;
- 30–39: 20%;
- 40–49: 25%;
- 50–54: 30%;
- 55–59: 35%;
- 60 or over: 40%.

The maximum earnings taken into account for this calculation are €115,000 per year.

Revenue also states that employer contributions are not counted against the employee's earnings threshold for this purpose.

Those rules affect tax relief, not the mathematical growth of money already inside the pension. That is why this projection calculator and the tax-relief calculator are separate tools.

## Fees compound too

The annual fund fee is applied multiplicatively to the gross annual growth factor.

In Advanced mode, Compound also runs a no-fee version of the same baseline scenario and shows the **fee drag** as the difference in ending balance.

That number can be larger than the simple sum of annual fees because money removed by fees also loses future investment growth.

Real pension products can have contribution charges, policy fees, adviser charges or other costs that are not represented by one annual percentage.

## Baseline versus lower-return scenario

Advanced mode lets you enter a lower-return scenario.

Both paths use the same contributions, contribution growth, AVC and fee. Only the gross investment return changes.

This is a useful sensitivity test because a projection that looks adequate only at one optimistic return assumption deserves more scrutiny.

The lower-return result is not a prediction of a bad market and the baseline is not a prediction of a normal market. They are deterministic scenarios.

## Nominal versus today's money

The future nominal pension pot is the amount of future euros projected by the model.

The today's-money figure discounts that balance by the compounded inflation assumption.

If a pension pot is projected to be €600,000 in 30 years, it does not follow that it will buy what €600,000 buys today.

The inflation-adjusted result is often the better figure for judging retirement purchasing power.

## Worked example

Suppose someone aged 35 has a €50,000 pension, contributes €400 per month and receives €300 per month from an employer.

Before any investment growth, 30 years of level future contributions would add €252,000.

Investment returns can lift the result materially above that total, but fees reduce the amount retained.

If contributions increase over time or annual AVCs are added, more of the ending pot will come from actual contributions rather than the return assumption.

That distinction is valuable because it separates a controllable saving decision from an uncertain market outcome.

## Your provider's projection matters

The Pensions Authority explains that pension projections depend on assumptions about future contributions, investment returns and other economic factors, and that actual benefits will only be known close to retirement.

Modern occupational pension benefit statements can provide more scheme-specific estimates than a general public calculator because the provider knows the actual fund, charges and contribution structure.

Use Compound to test scenarios and understand mechanics; use the scheme/provider statement for product-specific planning.

## Retirement age and access

The target retirement age in this calculator is simply the end of the accumulation projection.

It does not determine whether a specific pension arrangement can legally be accessed at that age.

Different occupational schemes, PRSAs and other arrangements can have different access conditions. Check the rules for the actual pension product.

## Common mistakes to avoid

Do not enter a return that is already net of the fee and then also enter the same fee separately.

Do not treat the future nominal balance as today's purchasing power.

Do not assume an annual AVC is fully tax-relievable without checking Revenue limits.

Do not assume employer contributions will continue unchanged if your employment changes.

Do not use one high-return scenario as the retirement plan. Compare a range.

And do not judge retirement adequacy from the pot alone: State Pension, other assets, retirement duration, tax and withdrawal strategy all matter.

## Related Compound tools

Use the [Pension Tax Relief Calculator](/pension-tax-relief-calculator/) to check the Revenue contribution-relief ceiling, the [Retirement Income Calculator](/retirement-income-calculator/) to model the spending phase, the [MyFutureFund Calculator](/myfuturefund-calculator/) for auto-enrolment and the [Investment Fee Calculator](/investment-fee-calculator/) for a dedicated cost comparison.

## Frequently asked questions

### Is the projected pension pot guaranteed?

No. The projection assumes a constant annual return and fee. Real investment returns vary from year to year, so the result is a planning scenario rather than a forecast or promise.

### Does the projection include the State Pension?

No. The calculator projects the private pension contributions and starting fund entered. State Pension entitlement and future rates are separate and should be considered when you later model retirement income.

### Why is the today's-money figure lower than the nominal pot?

Inflation reduces future purchasing power. The nominal result shows future euros; the today's-money result discounts that amount using the inflation assumption so it can be compared more meaningfully with current spending.

### Are employer and employee contributions treated differently in the growth projection?

Once contributed, both are added to the modelled pension fund and compound in the same way. Their tax treatment and eligibility rules can differ outside the projection, which is why the separate Pension Tax Relief Calculator should be used for employee/personal relief limits.

## Method and limitations

The engine calculates the number of complete years between the current age and target retirement age.

For each scenario it combines the gross annual return and annual percentage fee into a net annual growth factor, converts that to an equivalent monthly rate and compounds the fund monthly.

Employee and employer contributions are added each month. The Advanced annual AVC is added at the end of each projection year. Contribution growth is applied once per year for the following year.

The baseline, lower-return and no-fee comparison all use the same contribution plan.

The today's-money result divides the final nominal baseline pot by the compounded inflation factor.

The model does not simulate market volatility, sequence of returns, salary directly, changing employer policy, tax at retirement, pension-access rules or all possible product charges.

### Useful sources

- [Revenue — Tax relief limits on pension contributions](https://www.revenue.ie/en/jobs-and-pensions/pension/relief/tax-relief-limits.aspx)
- [Revenue — Tax relief on pension contributions](https://www.revenue.ie/en/jobs-and-pensions/pension/relief/index.aspx)
- [Pensions Authority — Statement of reasonable projection](https://pensionsauthority.ie/scheme-members-and-prsa-contributors/understanding-pensions/your_right_to_information/statement_of_reasonable_projection/)
- [Pensions Authority — Pension calculator assumptions](https://pensionsauthority.ie/scheme-members-and-prsa-contributors/pension-calculator/assumptions/)
