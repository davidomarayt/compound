## What this calculator is for

Investment charges are easy to underestimate because a percentage that looks small is deducted repeatedly from a changing balance. The cost is not only the euro amount charged: every euro removed from the account also loses the chance to compound in later years.

This calculator compares two otherwise identical investment paths. Basic mode changes only the annual percentage fee. Advanced mode can also include a fixed annual charge, a charge on each new contribution and an inflation assumption so the final balance gap can be shown in today's money.

## How to read the result

Start with the two projected balances and the **ending balance difference**. That is the clearest expression of fee drag under the assumptions entered.

The effective annual net-return figures show how the annual percentage fee interacts with the gross return. Compound uses the multiplicative relationship:

**net growth factor = (1 + gross return) × (1 − annual percentage fee)**

That is slightly different from simply subtracting the fee from the return.

Advanced mode then reports the modelled charges paid. Those totals include the percentage charge, fixed annual charge and contribution charge separately modelled by the engine. The difference between the ending balances can be larger than the difference between cumulative fees paid because the higher-fee option also loses future growth on money that was removed earlier.

## Worked example

Suppose two investments start with €25,000, receive €500 per month and both earn 7% a year before fees.

If one option charges 0.25% annually and the other charges 1.5%, the higher-fee portfolio does not merely pay an extra 1.25% of the original €25,000 each year. The charge is applied to a changing balance over a long period, and the deducted money stops compounding.

Add a 1% contribution charge or a fixed €100 annual account fee and the difference changes again. This is why product comparisons should be based on the **all-in charging structure**, not one headline percentage.

## Irish context

Irish investment products can contain several layers of cost: fund management charges, platform or policy fees, adviser charges, transaction costs, contribution charges and fixed administration charges.

The CCPC advises investors to understand both charges and tax before investing. A lower fee can improve the mathematical outcome when everything else is equal, but everything else is rarely perfectly equal: investment strategy, diversification, risk, service, tax treatment and tracking quality can all differ.

This calculator therefore holds the before-fee return constant on purpose. It answers a narrow question: **what would these two charging structures do if the underlying investment return and contribution plan were otherwise the same?**

It is not a recommendation to choose whichever side ends with the larger number.

## Percentage fees versus fixed charges

A percentage fee grows in euro terms as the portfolio grows. A €100 annual fixed charge does not.

That means a fixed charge can be especially significant on a small account while a percentage charge can become more expensive in euro terms on a large account. Advanced mode lets you put both into the same comparison.

The engine deducts the fixed annual charge monthly for modelling purposes. Real providers can deduct charges at different times or use different bases, so provider illustrations should take precedence where you are comparing an actual product.

## Contribution charges

A contribution charge is a fee taken from new money before all of that contribution reaches the investment.

If you contribute €500 and there is a 2% contribution charge, only €490 is added to the account in this simplified model. The €10 is counted as a charge and also loses all future compounding.

This matters particularly for regular savers because the charge repeats with each contribution.

## Why the inflation-adjusted gap matters

A €50,000 difference 25 years from now will not have the same purchasing power as €50,000 today.

Advanced mode therefore converts the ending balance difference into today's money using the inflation assumption entered. This does not change the nominal account balances; it gives a second perspective on the economic size of the difference.

## Common mistakes to avoid

Do not double-count a fee that is already reflected in the return figure you enter. If a provider quotes performance net of a particular fund charge and you then enter that same charge again, the model will overstate fee drag.

Do not assume the lowest-cost product must be best. Cost is important, but so are risk, diversification, product structure and tax.

Do not compare a percentage charge on one product with an apparently similar percentage on another without checking what each percentage actually covers.

And do not treat a smooth 7% return as a forecast. The purpose of the tool is to isolate fee mechanics, not predict market performance.

## Related Compound tools

Use the [Regular Savings Calculator](/regular-savings-calculator/) to model one saving plan in more detail, the [Pension Projection Calculator](/pension-projection-calculator/) for retirement accumulation and the [Inflation Calculator](/inflation-calculator/) for a deeper look at nominal versus real values.

## Frequently asked questions

### Why can the ending gap be larger than cumulative fees?
Because money paid in fees is no longer invested. The lost future growth on those amounts compounds over time.

### Does the calculator include Irish investment tax?
No. Tax can materially alter real-world outcomes and differs by product and investor circumstances.

### Are annual percentage charges deducted exactly this way in real products?
Not necessarily. Providers can calculate and deduct charges at different frequencies and on different bases.

### What should I enter as the gross return?
Use a consistent before-fee return for both options if your goal is to isolate cost. The number is a scenario assumption, not a forecast.

## Test the fee gap as a return hurdle

Another useful way to read the result is to ask how much extra investment return the more expensive option would need to generate just to overcome its higher charges.

If two products hold broadly similar assets but one has materially higher ongoing costs, the higher-cost option starts with a structural disadvantage. It may still be appropriate because of advice, asset allocation, guarantees or other features, but those benefits should be identified explicitly rather than assumed.

Run the calculator with the same gross-return assumption for both options first. That isolates the fee effect. Only then test different return assumptions if the products genuinely pursue different investment strategies.

For pension decisions, combine fee analysis with the [Pension Projection Calculator](/pension-projection-calculator/) so the long-term effect of contributions and charges can be viewed together.

## Method and limitations

The engine converts the gross annual return into an equivalent monthly growth rate. The annual percentage fee is converted into an equivalent monthly fee factor so that the combined annual effect matches the stated annual percentage assumption.

For each month, the model:

1. grows the existing balance by the monthly gross return;
2. applies the percentage fee factor;
3. deducts one-twelfth of any fixed annual charge in Advanced mode;
4. deducts any contribution charge from that month's new contribution;
5. adds the remaining contribution to the account.

The same process is run independently for both fee options.

Cumulative fees are tracked as the amount explicitly deducted by those three charging mechanisms. The model does not include bid/offer spreads, trading slippage, taxes, performance fees, tiered charging bands or product-specific charging rules.

### Useful sources

- [CCPC — Thinking of investing](https://www.ccpc.ie/manage-your-money/saving-and-investments/investments/thinking-of-investing)
- [ESMA — Costs and performance of retail investment products](https://www.esma.europa.eu/publications-and-data/market-analysis/costs-and-performance-retail-investment-products)
