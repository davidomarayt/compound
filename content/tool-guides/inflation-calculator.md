## What this calculator is for

Inflation changes what a euro can buy.

This calculator looks at that effect from both directions:

- how much a cost expressed in today's money could become in the future under a constant inflation assumption;
- how much purchasing power a fixed nominal euro amount could lose over the same period.

Advanced mode adds a third question: if savings or investments grow at a nominal rate, what is the exact inflation-adjusted real return?

The calculator is a scenario tool, not an inflation forecast.

## Ireland's official inflation measure

The Central Statistics Office describes the Consumer Price Index as Ireland's official and most widely used measure of consumer inflation.

The CPI measures changes in the average prices paid for a representative basket of goods and services. It is published monthly and uses expenditure weights intended to reflect household consumption patterns.

That makes CPI useful for economy-wide context.

It does not mean every household experiences exactly the same inflation rate.

A household spending heavily on rent, childcare or energy can experience a different change in living costs from a household with a paid-off home and different spending mix.

## Future cost

The future-cost calculation asks:

**If something costs €X today and its price rises at Y% every year, what would the same amount cost after N years?**

At 3% inflation, €10,000 becomes about €13,439 after 10 years.

The important feature is compounding. The second year's 3% increase applies to the already-increased first-year price.

Over long periods, small differences in the inflation assumption create large differences in future prices.

## Purchasing power

Purchasing power reverses the question.

If you hold €10,000 in nominal cash for 10 years while prices rise by 3% annually, that €10,000 does not disappear, but it buys less.

In today's-money terms its purchasing power falls to roughly €7,441 under that constant-rate scenario.

The calculator reports both the purchasing power and the amount of purchasing power lost.

## Worked example

Take €20,000, 2.5% annual inflation and a 15-year horizon.

The future cost of a basket costing €20,000 today would rise because the price level compounds every year.

Meanwhile, a fixed €20,000 nominal balance would buy progressively less of that basket.

Now switch to Advanced mode and enter a 5% nominal investment return.

The calculator compares 5% nominal growth with 2.5% inflation using the exact real-return relationship. The real return is not exactly 2.5%; it is slightly lower because the two growth factors divide rather than simply subtract.

That distinction is small over one year but can matter when compounded over decades.

## Nominal return versus real return

The precise relationship is:

**real return = (1 + nominal return) ÷ (1 + inflation) − 1**

For example, a 5% nominal return with 3% inflation produces a real return of about 1.94%, not exactly 2%.

Subtracting inflation from return is a useful mental shortcut when rates are small, but the exact compounding formula is better for a calculator.

Advanced mode uses the exact relationship.

## Future nominal value and today's-money value

Advanced mode also grows the starting amount at the nominal return for the selected period.

It then divides that future value by the compounded inflation factor.

This creates two complementary values:

- the nominal future balance;
- the same balance expressed in today's purchasing power.

A large nominal number decades from now can look impressive while supporting a much smaller real lifestyle than the same number supports today.

## Inflation is not constant in real life

The calculator applies one rate every year.

Actual inflation does not behave that way.

Ireland can experience periods of low inflation, high inflation and occasional price falls in particular categories. The composition of the CPI basket and its weights are also updated over time.

Use the entered rate as a planning scenario.

For a long-term decision, compare more than one case rather than assuming the current annual CPI rate continues indefinitely.

## Personal inflation can differ from CPI

CPI is designed as a broad average index.

Your own spending pattern can make your effective inflation experience different.

If housing represents a very large share of spending, housing-cost changes may dominate the household budget. Families with childcare costs can experience different pressures from retirees. Commuting patterns, healthcare needs and energy use also matter.

The calculator therefore does not fetch the current CPI and impose it on the user. You choose the rate appropriate to the scenario.

## Inflation and cash savings

A savings account can increase in nominal euros while still losing purchasing power if the retained interest rate is below inflation.

For example, if a deposit account earns 2% after tax while inflation is 3%, the nominal balance rises but the real value declines.

That is why the Advanced return field is useful even for cash savers.

For Irish deposit accounts, DIRT can reduce the interest retained. The [Regular Savings Calculator](/regular-savings-calculator/) discusses how to model a net deposit return.

## Inflation and investment returns

A positive real return means the investment assumption is growing faster than the inflation assumption.

A negative real return means purchasing power is falling despite what may be a positive nominal return.

Neither result is guaranteed. Investments can produce volatile returns and inflation can change materially.

This calculator deliberately avoids presenting a market-return assumption as a forecast.

## Inflation and debt

Inflation can also change the real burden of fixed nominal debt, but this calculator is not a debt model.

A fixed mortgage balance may become smaller relative to future nominal wages and prices, but the real household effect depends on income growth, interest rates and repayment terms.

Use the [Mortgage Calculator](/mortgage-calculator/) for mortgage cash flows rather than treating inflation alone as a debt strategy.

## Common mistakes to avoid

Do not compare a nominal investment return with a real spending target.

Do not assume today's inflation rate will persist for decades.

Do not assume CPI exactly matches your personal household costs.

Do not simply subtract inflation from a nominal return when you need a precise long-run result.

And do not interpret the future-cost figure as a forecast of a specific product or house price; it is the result of the constant rate you entered.

## Related Compound tools

Use the [Regular Savings Calculator](/regular-savings-calculator/) for contribution-based saving, the [Pension Projection Calculator](/pension-projection-calculator/) for retirement accumulation, the [FIRE Number Calculator](/fire-number-calculator/) for today's-money financial-independence targets and the [Lifetime Cost Calculator](/lifetime-cost-calculator/) for long-horizon household spending.

## Frequently asked questions

### Is CPI the same as my personal inflation rate?
No. CPI is a broad representative index.

### Can inflation be negative?
Yes. Prices can fall over some periods or categories, although sustained economy-wide deflation is different from temporary price declines.

### Why does the calculator show both future cost and purchasing power?
They answer opposite questions: what today's basket might cost later, and what a fixed future euro amount would be worth in today's terms.

### Does the real-return result include tax or fees?
No. Enter a nominal return consistent with the product you want to model.

## Method and limitations

Future cost is calculated as:

**amount × (1 + inflation rate)^years**

Purchasing power is calculated as:

**amount ÷ (1 + inflation rate)^years**

Advanced real return uses the exact relationship **(1 + nominal return) ÷ (1 + inflation) − 1**.

The future nominal investment/savings value is the starting amount compounded at the nominal return. Its today's-money value divides that result by the inflation factor.

The chart plots the future cost and purchasing power at annual points.

The model uses constant rates, does not fetch live CPI, does not model tax or fees and does not estimate a household-specific inflation basket.

### Useful sources

- [CSO — Consumer Price Index methodology](https://www.cso.ie/en/methods/prices/consumerpriceindex/methodologydocuments/csoconsumerpriceindexmethodology/)
- [CSO — Consumer Price Index](https://www.cso.ie/en/methods/prices/consumerpriceindex/)
- [CSO — CPI frequently asked questions](https://www.cso.ie/en/methods/prices/consumerpriceindex/methodologydocuments/frequentlyaskedquestions/)
