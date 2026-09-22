## What this calculator is for

This calculator projects what a starting balance plus regular monthly saving or investing could become over a chosen period.

Basic mode answers the simplest version of the question: if the starting balance, monthly contribution and annual return remain constant, what is the projected balance?

Advanced mode adds three assumptions that often matter over longer periods: annual growth in the monthly contribution, an annual percentage fee and inflation.

The result is therefore useful for both cash-saving scenarios and simplified long-term investment illustrations, provided the return and tax assumptions match what you are actually modelling.

## How to read the result

The projected nominal balance is only one part of the answer.

Compound also separates:

- total money contributed;
- estimated net growth;
- the implied annual return after the Advanced fee;
- the final balance in today's money;
- the monthly contribution reached in the final year;
- the modelled reduction in ending balance caused by the annual fee.

That separation matters because contributions are a decision while investment returns are uncertain.

A result that depends mainly on increasing contributions has a different risk profile from one that depends on a high assumed return.

## Worked example

Suppose you start with €5,000, save €300 per month for 10 years and assume a 4% annual return.

Before growth, the starting balance plus 120 monthly contributions represents €41,000 of money actually added.

The calculator compounds the balance monthly, so the ending value can exceed €41,000 if the return is positive.

Now switch to Advanced mode. If the monthly contribution rises by 3% each year, the saving rate itself compounds. If an annual fee is also applied, part of the gross return is lost. If inflation is 2%, the future nominal balance is then translated back into today's purchasing power.

The point is not to find one “correct” future number. It is to see which assumptions are doing the work.

## Irish deposit savings and DIRT

Revenue states that Irish-resident individuals generally pay DIRT at 33% on deposit interest, subject to exemptions and specific circumstances.

Basic mode does not calculate DIRT automatically. If you are modelling an ordinary taxable deposit account, use a return assumption that reflects the interest you expect to retain after DIRT.

For example, a 3% gross deposit rate subject fully to 33% DIRT leaves about 2.01% before any other relevant tax considerations.

Do not apply that shortcut to every investment. Irish tax treatment can differ materially between direct shares, funds, pension assets and other products.

## Gross return and Advanced fee

In Advanced mode, the return input is explicitly **before the annual fee**.

The calculator combines the return and fee multiplicatively rather than simply subtracting the percentages.

That means:

**net annual growth factor = (1 + gross return) × (1 − annual fee)**

If the gross return is 6% and the fee is 1%, the implied net return is slightly below 5%, because the 1% fee is applied to the value after growth in the model.

The [Investment Fee Calculator](/investment-fee-calculator/) provides a deeper side-by-side comparison of different charging structures.

## Contribution growth

Many long-term saving plans do not remain fixed in cash terms.

A person may increase saving after a salary rise, redirect a finished loan repayment or deliberately raise pension/investment contributions every year.

Advanced mode can increase the monthly contribution annually by a percentage.

A €300 monthly contribution growing at 3% per year becomes €309 after the first increase, then about €318.27 after the next.

Because those contributions themselves have more time to compound, gradual increases can make a meaningful difference over long horizons.

But the contribution-growth rate is still an assumption. Do not enter a rate that the household budget cannot sustain.

## Nominal versus real balance

A future balance is normally quoted in future euros.

Inflation means those euros may buy less than the same number today.

Advanced mode therefore divides the ending nominal balance by the compounded inflation factor and reports the result in today's money.

This is particularly important over 20, 30 or 40 years, where the difference between nominal and real values can be large.

The inflation rate is not a prediction. The CSO's CPI is Ireland's official measure of consumer inflation, but actual inflation changes over time and an individual household can experience a different personal cost pattern.

## Fee drag

The Advanced fee-drag result compares the chosen plan with an otherwise identical projection at a zero annual percentage fee.

The difference is not simply the sum of the fees that might have been charged. It also includes the future compounding lost because those amounts were no longer in the account.

That is why small recurring fees can become significant over long periods.

## Deposit account versus investment account

A deterministic calculator can make a higher-return investment appear superior because it only sees the assumed average rate.

It does not see risk.

Deposit savings can offer capital stability and access but rates can change and interest may be taxed. Investments can provide higher long-run expected returns but can fall sharply and may have product-specific tax and fee rules.

Match the assumption to the purpose of the money.

A short-term house deposit and a 30-year retirement investment should not automatically be modelled with the same return.

## What can change the answer

The most important variables are time, contribution size and the return retained after fees and tax.

Long horizons magnify both positive compounding and fee drag.

Inflation changes the economic meaning of the final balance.

Contribution increases can offset weak returns, while contribution pauses can materially reduce the outcome.

Run multiple scenarios rather than relying on one set of inputs.

## Common mistakes to avoid

Do not enter a return already net of fees and then enter the same fee again in Advanced mode.

Do not compare a gross investment return with an after-DIRT deposit return.

Do not assume the future nominal balance has today's purchasing power.

Do not treat a smooth annual return as a guaranteed market path.

And do not forget that contribution growth is a commitment by the saver, not a return generated by the account.

## Related Compound tools

Use the [Savings Goal Calculator](/savings-goal-calculator/) when you need a target date, the [Investment Fee Calculator](/investment-fee-calculator/) for cost comparisons, the [Inflation Calculator](/inflation-calculator/) for real purchasing power and the [Compound Interest Calculator](/compound-interest-calculator/) for a broader flagship compounding model.

## Frequently asked questions

### Are contributions added at the beginning or end of each month?
They are added after that month's growth in this model.

### Does the calculator include DIRT?
No. For a taxable Irish deposit scenario, enter the net return you expect to retain or adjust the gross interest yourself.

### Does the Advanced annual fee include every product cost?
No. It is one percentage fee. Fixed, transaction or contribution charges require separate consideration.

### Can I use this for a pension?
It can illustrate compounding, but the [Pension Projection Calculator](/pension-projection-calculator/) is better because it separates employee and employer contributions and pension-specific assumptions.

## Method and limitations

The return is treated as an effective annual rate.

In Basic mode, Compound converts it into an equivalent monthly rate using **(1 + annual return)^(1/12) − 1**, compounds the existing balance and adds the monthly contribution at the end of each month.

In Advanced mode, the annual percentage fee is combined multiplicatively with the gross return before the equivalent monthly rate is calculated.

The monthly contribution can be increased at each 12-month point. The projected real balance is the final nominal balance divided by **(1 + inflation)^years**.

Fee drag is measured by rerunning the same contribution plan with a zero annual percentage fee and comparing the ending balance.

The model does not calculate Irish investment taxes, changing interest rates, market volatility, transaction charges, contribution holidays or withdrawals.

### Useful sources

- [CCPC — About savings](https://www.ccpc.ie/manage-your-money/saving-and-investments/savings)
- [Revenue — Deposit Interest Retention Tax](https://www.revenue.ie/en/additional-incomes/dirt/index.aspx)
- [Revenue — What DIRT rate is applicable?](https://www.revenue.ie/en/additional-incomes/dirt/what-dirt-rate-is-applicable.aspx)
- [CSO — Consumer Price Index methodology](https://www.cso.ie/en/methods/prices/consumerpriceindex/methodologydocuments/csoconsumerpriceindexmethodology/)
