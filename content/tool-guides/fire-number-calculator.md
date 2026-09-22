## What this calculator is for

A FIRE number is a planning target for financial independence: the amount of invested capital that might support a chosen level of annual portfolio-funded spending at a chosen starting withdrawal rate.

The calculator goes further than multiplying spending by 25. It separates spending that must actually come from the portfolio, shows progress from the current portfolio, converts investment returns into real terms and estimates a today’s-money path to the target.

Advanced mode can also include an ongoing income source, a separate capital reserve, annual investment fees and real growth in future contributions.

## The core FIRE equation

The basic relationship is:

**portfolio-funded annual spending ÷ withdrawal rate = base FIRE target**

At a 4% withdrawal rate, €40,000 of annual portfolio-funded spending implies €1,000,000.

At 3.5%, the same spending implies about €1.14 million.

At 3%, it implies about €1.33 million.

That sensitivity is why the withdrawal-rate assumption deserves more attention than a neat “25× spending” slogan.

Advanced mode shows 3%, 3.5% and 4% target values side by side using the spending assumptions entered.

## Spending that the portfolio actually needs to fund

In Basic mode, all annual spending is assumed to come from the investment portfolio.

Advanced mode lets you enter **ongoing annual income available from the target date**. The engine subtracts that amount from spending before applying the withdrawal rate.

This input should be used carefully.

If your financial-independence target is age 50 but the State Pension will not start until later, it would be misleading to subtract the State Pension from every year beginning at age 50. Only include income that is expected to be available throughout the period represented by the target.

For a plan with different income phases, run separate scenarios rather than forcing one number to represent the whole retirement.

## A separate capital reserve

Some large future costs do not fit neatly into an annual withdrawal budget: major home work, a replacement car, support for family, or a deliberately separate safety reserve.

Advanced mode can add an **extra one-off capital reserve** on top of the spending-based FIRE target.

The reserve is not divided by the withdrawal rate. It is simply added to the target.

## Worked example

Assume annual spending of €36,000 and a 4% withdrawal rate.

The base target is €900,000.

If you enter €6,000 of ongoing annual income available from the target date, the portfolio-funded spending falls to €30,000 and the base target becomes €750,000.

If you then add a €50,000 separate capital reserve, the total target becomes €800,000.

The calculator then compares that target with the current invested assets and models the accumulation path.

## Nominal return, fees and inflation

FIRE discussions often mix nominal and real numbers.

If spending is expressed in today's euros, the accumulation path should also be interpreted in today's purchasing power. Compound therefore converts the nominal return into a real return.

In Advanced mode, the engine first reduces the nominal growth factor by the annual fee and then adjusts for inflation:

**real return = (1 + nominal return after fee) ÷ (1 + inflation) − 1**

This is more accurate than simply subtracting inflation from return.

Basic mode assumes 2% inflation and no explicit annual fee.

## Contributions are also treated in today's money

The annual contribution input is a today’s-money amount.

In Basic mode it remains constant in real terms. Economically, that means the nominal amount would rise with inflation over time.

Advanced mode can grow the contribution further in **real** terms. A 2% real contribution-growth assumption means the saving effort increases faster than inflation.

Use this carefully. A high contribution-growth assumption can make a target appear much closer even though it depends on future income growth and saving discipline.

## Where the 4% idea came from

Popular FIRE discussions often refer to historical US withdrawal research, including William Bengen's 1994 work and later studies using US asset-market history.

That research is useful context, but it is not an Irish guarantee and it is not a universal law.

A withdrawal rate that worked in a particular historical dataset depends on the assets used, the period studied, retirement length, inflation sequence, fees and spending rules.

Irish investors can also face different tax treatment and product structures from the US assumptions behind much of the popular research.

For that reason, Compound asks you to choose the withdrawal rate rather than presenting 4% as “the answer”.

## Irish pension and State Pension context

Pension assets can have access rules that differ from ordinary taxable investments. Retirement income can also be taxable.

The Pensions Authority's own calculator assumptions are presented in today's-money terms and explicitly treat future pension values as assumptions rather than certainty.

The Irish State Pension can be an important part of later-life income, but entitlement and rates depend on the person and can change. If it begins after your proposed FIRE date, think of the plan as a bridge phase followed by a later phase rather than subtracting the full State Pension from day one.

## Sequence-of-returns risk

The accumulation side of this calculator uses a constant real return.

The withdrawal-rate target itself also does not simulate future year-by-year returns.

That means one of the biggest retirement risks is not captured: **sequence-of-returns risk**.

Two portfolios can earn the same average return over 30 years and produce very different outcomes if one experiences large losses early in retirement while withdrawals are being taken.

A deterministic FIRE number therefore tells you about scale, not certainty.

## Tax matters

The tool does not calculate Irish tax on investment returns or retirement withdrawals.

This is a major limitation. A household that needs €40,000 of after-tax spending may need more than €40,000 of gross withdrawals, depending on the assets and tax treatment involved.

Build the spending input around the lifestyle you actually need to fund, then separately consider how tax affects the gross cash that must be generated.

## How to use the target sensitivity results

Advanced mode shows the target implied by 3%, 3.5% and 4% withdrawal rates.

Do not read those as three forecasts. Use them as a range-testing tool.

If a small change in withdrawal rate moves the target by hundreds of thousands of euro, that is useful information: it shows how sensitive the plan is to a single assumption.

## Common mistakes to avoid

Do not include the value of your home unless the plan genuinely converts that home equity into spendable resources.

Do not count pension assets as freely accessible before the relevant access conditions.

Do not subtract future income that will not begin until years after the FIRE date.

Do not use an optimistic return assumption to compensate for a low saving rate.

And do not treat “years to target” as a predicted date. It is the result of a constant-return scenario.

## Related Compound tools

Use the [Retirement Income Calculator](/retirement-income-calculator/) to test the drawdown phase, the [Pension Projection Calculator](/pension-projection-calculator/) for pension accumulation, the [Investment Fee Calculator](/investment-fee-calculator/) to isolate cost drag and the [Inflation Calculator](/inflation-calculator/) for nominal-versus-real comparisons.

## Frequently asked questions

### Is a 4% withdrawal rate guaranteed to be safe?

No. The 4% figure is a planning reference derived from historical retirement research, not a guarantee for every market, retirement length, portfolio, tax position or spending pattern. Use the 3%, 3.5% and 4% sensitivity outputs to see how strongly the target depends on this assumption.

### Should I subtract the State Pension from my FIRE spending?

Only when the income is relevant to the period being modelled. The Advanced ongoing-income input assumes that income is available to offset portfolio-funded spending from the financial-independence point. Do not use a future State Pension starting years later as though it were available from day one.

### Should my pension pot count towards my current FIRE portfolio?

It can be part of long-term retirement wealth, but access timing matters. If you want financial independence before pension assets can be accessed, you may need enough accessible assets to bridge the gap separately. The calculator does not model pension-access ages or account-specific restrictions.

### Why does the calculator use today's money?

Expressing the target and projection in today's purchasing power makes spending and portfolio values easier to compare. The model converts the entered nominal return, after any Advanced annual fee, into a real return using the inflation assumption.

## Method and limitations

The engine calculates portfolio-funded spending as annual spending less any Advanced ongoing-income amount, floored at zero.

It divides that amount by the chosen withdrawal rate and adds any separate capital reserve.

The nominal annual return is reduced by the Advanced annual fee using a multiplicative growth factor. The result is converted to a real annual return using the inflation assumption and then to an equivalent monthly rate.

The portfolio is stepped forward monthly. Contributions are added monthly. Advanced contribution growth is applied annually in real terms.

The path stops when the target is reached or after 100 years.

The model does not simulate variable returns, tax, pension-access rules, future policy changes, changing spending, one-off withdrawals beyond the separate reserve or a phased State Pension start.

### Useful sources

- [Bengen, 1994 — Determining Withdrawal Rates Using Historical Data](https://www.retailinvestor.org/pdf/Bengen1.pdf)
- [Pensions Authority — Pension calculator assumptions](https://pensionsauthority.ie/scheme-members-and-prsa-contributors/pension-calculator/assumptions/)
- [Revenue — Taxation of pensions](https://www.revenue.ie/en/jobs-and-pensions/pension/private/index.aspx)
