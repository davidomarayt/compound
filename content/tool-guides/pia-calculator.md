## What the PIA Calculator does

This calculator models Ireland's planned **Personal Investment Account (PIA)** using the headline terms announced in Budget 2027.

It projects a starting PIA balance and annual contributions forward using the investment-return assumption you enter. It then estimates when the account may move above the **€50,000 PIA tax threshold** and calculates the proposed **1% annual charge on the portion of the modelled average account value above €50,000**.

The calculator is designed to answer practical questions such as:

- How large could my PIA become after 5, 10 or 20 years?
- When might I first cross the €50,000 threshold?
- What could the annual PIA charge look like once I cross it?
- How much PIA tax could be paid over the full projection?
- How much difference could provider and fund fees make?
- How much of the ending balance comes from contributions versus investment growth?
- How much does removing the annual PIA charge from the account reduce future compounding?

The full background, eligible investments, withdrawals, providers and outstanding legislative questions are covered in Compound's [Personal Investment Account Ireland guide](/wealth/personal-investment-account-ireland/).

The calculator is a planning tool. It is not an official Revenue calculator and it does not claim that the final legislation will use exactly the same valuation method.

## Budget 2027 assumptions used

The calculator currently encodes the main Personal Investment Account terms announced in Budget 2027 and the Department of Finance retail-investment roadmap.

The headline assumptions are:

- planned PIA launch from **1 July 2027**;
- maximum annual contribution of **€12,000**;
- no minimum contribution;
- a **€50,000 threshold** for the annual PIA charge;
- a **1% annual charge** on the relevant account value above €50,000;
- the PIA provider is expected to calculate, report and pay the account tax to Revenue;
- no eight-year deemed disposal inside the PIA under the published Department of Finance design;
- eligible investments are expected to include listed shares, listed bonds, suitable retail funds and ETFs;
- crypto-assets and derivatives are excluded under the proposed framework.

The account is not yet available. The Finance Bill still has to convert the announced framework into detailed law.

That distinction is important because a calculator can model the announced rate and threshold today, but it cannot know a valuation rule that has not yet been enacted.

When the final legislation and Revenue guidance are published, Compound will update this tool where necessary.

## How the projection works

The calculator works month by month so that contributions and investment growth are not treated as though they all happened on the final day of the year.

For each projection year, it:

1. starts with the balance carried forward from the previous year;
2. spreads the annual contribution evenly over 12 months;
3. applies the annual investment-return assumption through monthly compounding;
4. applies the annual percentage fee monthly in Advanced mode;
5. records the account value at each month end;
6. calculates the average of those 12 month-end values;
7. applies the proposed PIA charge to the portion of that average above €50,000;
8. deducts the estimated PIA charge at the end of the modelled year;
9. carries the remaining balance into the next year.

This produces a transparent planning model rather than pretending the contribution arrives in one lump sum at the start or end of every year.

The return assumption is deliberately editable. A 6% annual return is not a forecast and should not be interpreted as one. Real investment returns are volatile and can be negative.

For broader long-term growth modelling outside the PIA-specific tax system, use Compound's [Compound Interest Calculator](/compound-interest-calculator/).

## How the calculator estimates average account value

The Department of Finance design uses an **average account valuation over the taxable period**.

The detailed legislation still has to determine exactly how that average will be calculated.

For a clear and reproducible estimate, this calculator uses the average of the 12 month-end account values in each modelled full year.

That means the calculation is sensitive to when contributions enter the account.

For example, €12,000 contributed as €1,000 each month will normally produce a lower average account value during that year than €12,000 contributed on the first day of the year.

The final statutory rules may use different valuation dates or a different averaging convention.

The monthly-average approach used here is therefore a **modelling assumption**, clearly separated from the rules that have already been announced.

This is also why the result is described as an estimated PIA charge rather than an official tax liability.

## The PIA tax formula used

For every modelled year, the calculator applies:

**PIA charge = 1% × max(€0, modelled average account value − €50,000)**

If the modelled average account value is €50,000 or less, the annual PIA charge is €0.

If the modelled average account value is €75,000:

**€75,000 − €50,000 = €25,000**

**€25,000 × 1% = €250**

If the modelled average account value is €100,000:

**€100,000 − €50,000 = €50,000**

**€50,000 × 1% = €500**

The 1% rate is applied only to the amount above the threshold.

It is not applied to the full account once the account crosses €50,000.

It is also not a 1% tax on investment profit.

That distinction is central to understanding the proposed account.

## Worked example

Suppose an investor starts with no PIA balance and contributes the full announced annual allowance of **€12,000 per year**.

Assume:

- starting balance: €0;
- annual contribution: €12,000;
- investment horizon: 10 years;
- assumed annual investment return: 6%;
- no provider or investment fee in Basic mode;
- no withdrawals.

The calculator spreads the €12,000 contribution across the year as €1,000 per month and compounds the modelled return.

In the early years, the modelled average balance remains below €50,000, so no PIA charge is estimated.

Eventually, the growing account crosses the threshold.

The calculator reports the first year in which the **average account value**, not merely the year-end balance, moves far enough above €50,000 for a charge to arise.

It then continues calculating the annual charge in each later year.

The output separates:

- money contributed;
- modelled net investment growth;
- total PIA tax paid;
- final-year average account value;
- final-year PIA charge;
- and the projected ending account value.

Switching to Advanced mode lets the investor add, for example, a 0.25% annual provider/fund fee and a 2% inflation assumption.

The result will normally be lower because recurring fees remove capital that could otherwise compound.

Advanced mode also shows the projected final value in today's money and the **PIA tax drag**.

## What PIA tax drag means

The PIA tax drag is not simply the sum of annual PIA tax payments.

The calculator runs an equivalent projection without the PIA charge and compares the ending balances.

Why can the difference be larger than the tax paid?

Because every euro removed to pay the PIA charge is a euro that can no longer earn future investment returns.

For example, if €500 leaves the account several years before the end of the projection, the cost by the final year can exceed €500 because the foregone investment growth is also lost.

This is the same compounding principle that makes recurring fees important.

The tax-drag figure should not be read as a comparison with an ordinary investment account. A non-PIA investment can face a completely different Irish tax regime depending on the asset.

It simply shows the effect of the PIA charge inside this model.

## Provider and investment fees

The €50,000 threshold is a tax feature.

It does **not** mean the first €50,000 will necessarily be completely free to invest.

A PIA provider or the investments selected inside the account may charge:

- platform or account fees;
- fund management charges;
- dealing commissions;
- foreign-exchange costs;
- custody charges;
- advice fees;
- transfer fees.

Advanced mode lets you enter one recurring annual percentage fee.

The calculator applies that percentage through the year so that the effect compounds over time.

This is a simplification because real providers may use fixed fees, tiered fees, trading charges or a combination of charges.

Once actual PIA products launch, investors should compare the total cost rather than focusing on one headline fee.

For a more detailed fee comparison, use the [Investment Fee Impact Calculator](/investment-fee-calculator/).

## Why the threshold-crossing year matters

The first year in which a PIA charge appears can be more useful than looking only at the final tax figure.

Someone starting from €0 and contributing regularly may spend several years below the threshold.

Someone transferring or starting with a larger permitted balance, if the final rules allow it, may reach the threshold much sooner.

The crossing point depends on:

- starting balance;
- contribution level;
- contribution timing;
- investment return;
- fees;
- and the official valuation method.

A strong investment return can bring the threshold year forward.

A poor return can push it back.

That is why the calculator shows a projection rather than a guarantee.

## PIA versus ordinary investing

The PIA should not be compared with a normal investment account using one generic outside tax rate.

Irish investment taxation depends heavily on what the investor owns.

Direct shares are commonly subject to Capital Gains Tax on disposal, with dividend income taxed separately.

Relevant Irish and equivalent offshore investment funds can fall under a separate fund-tax regime and may be subject to deemed disposal.

A pension has a different tax framework again.

The PIA is intended to create a dedicated wrapper with its own account-level annual charge.

That means the correct comparison is not simply:

> 1% PIA tax versus 33% CGT.

Those percentages can apply to different tax bases and at different times.

Read Compound's [Investment Tax in Ireland guide](/wealth/investment-tax-ireland/) before making an after-tax comparison.

## PIA versus pension

A PIA and a pension solve different problems.

A pension is designed for retirement and may offer Income Tax relief on qualifying personal contributions, as well as employer contributions where available.

The trade-off is restricted access.

A PIA is designed to keep the money accessible while providing a simplified investment-tax wrapper.

No pension-style upfront Income Tax relief has been announced for PIA contributions.

For someone investing specifically for retirement, pension benefits can therefore be highly valuable.

For money that may be needed before retirement, liquidity can make the PIA relevant.

The decision should reflect the goal rather than treating either wrapper as universally superior.

## Investment returns and volatility

The calculator uses a constant annual return because a planning model needs a repeatable input.

Markets do not produce constant returns.

A portfolio might rise sharply one year, fall the next and recover later.

That matters for a PIA because the annual charge is linked to account value rather than simply to realised profit.

A volatile path can therefore produce a different sequence of annual PIA charges from a smooth path with the same long-term average return.

Use several scenarios.

For example, test:

- a cautious return;
- a central return;
- a stronger return;
- higher fees;
- lower contributions.

A plan that only looks attractive under one optimistic assumption is less robust than one that works across several plausible outcomes.

## Frequently asked questions

### How much PIA tax will I pay on €100,000?

If the relevant average account value were €100,000 under the announced formula, the amount above the €50,000 threshold would be €50,000. At 1%, the illustrative annual PIA charge would be **€500**.

### Do I pay 1% on the whole account once it passes €50,000?

No under the announced design. The 1% annual charge applies only to the portion of the relevant account value above €50,000.

### Is the PIA tax 1% of my investment profit?

No. The proposed charge is based on account value above the threshold, not simply on realised investment profit.

### Does deemed disposal apply inside a PIA?

The Department of Finance roadmap says the existing retail-investment tax regime, including deemed disposal, will not apply inside the new account.

### How much can I contribute to a PIA each year?

Budget 2027 announced a maximum contribution of **€12,000 per year** and no minimum contribution.

### Does unused PIA contribution room carry forward?

That has not yet been settled clearly in the published high-level rules. The calculator therefore does not model carry-forward of unused allowance.

### Do withdrawals give me more contribution room?

The published design provides for flexible withdrawals, but the exact interaction between withdrawals and the annual contribution cap still requires final legislative detail. The calculator does not assume that withdrawn money can automatically be recontributed.

### Can I use this calculator before PIAs launch?

Yes, as a planning illustration. PIAs are planned for 1 July 2027 and the detailed legislation is not final, so results should not be treated as an official Revenue calculation.

### Does the calculator include provider fees?

Basic mode does not. Advanced mode lets you enter a recurring annual percentage fee. Actual provider and investment charges will vary.

### Can I compare two scenarios?

Yes. Use the calculator's **Save for comparison** feature, change your assumptions and compare the saved scenario with the current one.

### Is this a PIA versus ETF tax calculator?

No. ETFs held outside a PIA can be subject to different Irish tax treatment depending on their structure and domicile. This calculator focuses on the proposed PIA wrapper itself.

## Method and limitations

This is an educational scenario tool, not financial, investment or tax advice.

The model assumes:

- a constant annual investment return;
- level annual contributions spread evenly over 12 months;
- the Budget 2027 headline €12,000 contribution cap;
- the Budget 2027 €50,000 threshold;
- a 1% annual charge on the modelled average account value above that threshold;
- the annual charge is deducted from the account at year end;
- one recurring percentage fee in Advanced mode;
- no withdrawals;
- no change in tax residency;
- no provider-specific investment restrictions;
- no transfer of existing investments into the account;
- no future changes in law.

It does not model irregular market returns, intra-year withdrawals, contribution carry-forward, inheritance treatment, provider-specific fixed charges or the detailed tax consequences of moving assets into or out of the wrapper.

The most important limitation is the **average account valuation method**.

The Department of Finance has indicated an average-value approach, but the Finance Bill still has to finalise the legal mechanics. Compound uses the average of 12 modelled month-end balances because it is transparent and easy to reproduce.

Once enacted, the legislation and Revenue guidance should take precedence over this calculator.

The calculator runs entirely in your browser. Compound does not receive the figures you enter.
