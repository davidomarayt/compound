---
title: "PIA Dividend vs Growth Portfolio: Which Builds More Wealth?"
seo_title: "PIA Dividend vs Growth Portfolio: Ireland 2027 Comparison"
slug: pia-dividend-vs-growth-portfolio
pillar: wealth
draft: false
publication_status: published
date: 2026-11-16
research_checked: 2026-11-16
research_review_pending: true
approved_by: "User explicitly requested build and publication on 16 November 2026"
summary: "Would a dividend portfolio or growth portfolio perform better inside Ireland's proposed PIA? Compare equal total returns, reinvestment, foreign withholding tax, fees and the annual 1% investment account tax with our interactive calculator."
meta_description: "PIA dividends vs growth in Ireland: compare after-tax portfolio values with our free calculator. Includes foreign withholding, reinvestment and proposed PIA 1% charge."
tags: [pia-ireland, personal-investment-account, dividend-investing, growth-investing, investment-tax, ireland]
related_tools: [pia-calculator, compound-interest-calculator, investment-fee-calculator]
hero_image_url: "https://images.pexels.com/photos/11391951/pexels-photo-11391951.jpeg?auto=compress&cs=tinysrgb&w=1600"
hero_image_alt: "Small green seedling growing between stacks of silver coins, illustrating long-term investment growth"
hero_image_credit: "Towfiqu barbhuiya / Pexels — Pexels License; illustrative finance photograph"
hero_image_source: "https://www.pexels.com/photo/green-plant-between-a-pile-of-silver-coins-11391951/"
require_pinned_hero: true
sources:
  - title: "Finance (No. 2) Bill 2026 as introduced, section 26, proposed Individual Investment Account"
    url: https://assets.gov.ie/static/documents/89edf30b/Finance_No._2_Bill_2026.pdf
  - title: "Department of Finance: Finance (No. 2) Bill 2026 Explanatory Memorandum"
    url: https://assets.gov.ie/static/documents/8ee6faff/Finance_No._2_Bill_2026_Explanatory_Memorandum.pdf
  - title: "Revenue: Irish Investment Account Technical Group Forum, 7 October 2026"
    url: https://www.revenue.ie/ga/corporate/press-office/press-releases/2026/pr-100726-irish-investment-account.aspx
  - title: "Revenue: Taxation of dividend income outside tax-advantaged investment accounts"
    url: https://www.revenue.ie/en/additional-incomes/dividend-income/index.aspx
  - title: "US Internal Revenue Service: Tax treaty tables for treaty withholding rates"
    url: https://www.irs.gov/individuals/international-taxpayers/tax-treaty-tables
---

**A dividend-paying share and a growth share do not automatically produce different wealth.** What matters is *total return* — capital appreciation plus distributions — after costs and taxes. The proposed Irish Personal Investment Account (PIA), called the **Individual Investment Account (IIA)** in the Finance (No. 2) Bill 2026, makes this comparison particularly interesting: eligible investment income and gains would generally be exempt from separate Irish taxes inside the account, while the annual account-value charge could still apply.

Under the **proposal**, dividends paid inside a qualifying account should not attract an additional Irish income-tax bill, but **foreign source-country withholding may still reduce the cash received**. So an investor comparing US dividend-paying shares with low-yield shares needs to ask how much of each payout survives foreign withholding, not assume a dividend is free money.

**Status at 16 November 2026:** This article models the Finance Bill **as introduced**, not enacted final rules. The planned 1 July 2027 start depends on legislation, commencement and provider readiness. Eligible securities, provider fees and access to foreign-market investments will also depend on the eventual offering.

## Compare dividend and growth portfolios: free PIA calculator

The calculator below keeps the **same assumed pre-tax total return** for both portfolios and lets you change dividend yield, withholding tax, investment horizon, contributions and provider fees. That is the fairest starting comparison: we do **not** quietly give growth investments a higher expected return.

<div class="pdg" id="pia-dividend-growth-calculator" aria-label="PIA dividend versus growth portfolio calculator">
  <div class="pdg-head"><p class="pdg-kicker">COMPOUND WEALTH · INTERACTIVE MODEL</p><h3>Dividend vs growth: model the difference</h3><p>Hypothetical portfolios, same pre-tax total return. Dividends are automatically reinvested <em>after</em> assumed foreign withholding.</p></div>
  <form class="pdg-form" id="pdg-form">
    <div class="pdg-fields">
      <label>Starting PIA balance (€)<input name="starting" type="number" min="0" max="10000000" step="500" value="0" required></label>
      <label>Annual contribution (€)<input name="contribution" type="number" min="0" max="12000" step="500" value="12000" required><small>Proposed maximum: €12,000 a year</small></label>
      <label>Investment period (years)<input name="years" type="number" min="1" max="40" step="1" value="10" required></label>
      <label>Assumed pre-tax total return (%/year)<input name="return" type="number" min="-30" max="30" step=".25" value="7" required></label>
      <label>Provider / investment fee (%/year, both)<input name="fee" type="number" min="0" max="5" step=".05" value=".30" required></label>
      <label>Dividend portfolio yield (%/year)<input name="divyield" type="number" min="0" max="20" step=".5" value="4" required></label>
      <label>Growth portfolio yield (%/year)<input name="growthyield" type="number" min="0" max="20" step=".5" value=".5" required></label>
      <label>Dividend portfolio foreign withholding (%)<input name="divwht" type="number" min="0" max="100" step="5" value="15" required></label>
      <label>Growth portfolio foreign withholding (%)<input name="growthwht" type="number" min="0" max="100" step="5" value="15" required></label>
    </div>
    <div class="pdg-actions"><button type="submit">Calculate comparison</button><button type="button" id="pdg-reset">Reset assumptions</button></div>
    <p class="pdg-error" id="pdg-error" role="alert" hidden></p>
  </form>
  <div class="pdg-results" id="pdg-results" aria-live="polite">
    <div class="pdg-results-grid">
      <div><span>Dividend portfolio</span><strong id="pdg-div-result">—</strong></div>
      <div><span>Growth portfolio</span><strong id="pdg-growth-result">—</strong></div>
      <div><span>Growth minus dividend</span><strong id="pdg-gap-result">—</strong></div>
    </div>
    <p class="pdg-explain" id="pdg-explain"></p>
    <div class="pdg-chart" id="pdg-chart" role="img" aria-label="Projected portfolio balances over time"></div>
    <div class="pdg-table-wrap"><table><caption>Cumulative projected costs and contributions</caption><thead><tr><th>Measure</th><th>Dividend</th><th>Growth</th></tr></thead><tbody>
    <tr><th scope="row">Personal contributions</th><td id="pdg-contrib-div">—</td><td id="pdg-contrib-growth">—</td></tr>
    <tr><th scope="row">Foreign dividend withholding</th><td id="pdg-wht-div">—</td><td id="pdg-wht-growth">—</td></tr>
    <tr><th scope="row">Proposed PIA charge</th><td id="pdg-tax-div">—</td><td id="pdg-tax-growth">—</td></tr>
    <tr><th scope="row">Provider / investment fees</th><td id="pdg-fee-div">—</td><td id="pdg-fee-growth">—</td></tr>
    </tbody></table></div>
  </div>
  <p class="pdg-note">Model assumptions: constant annual return split into price appreciation and dividend yield; 12 equal monthly contributions and monthly reinvestment; percentage provider fees applied monthly; annual PIA charge of 1% on the amount by which the <strong>average of 12 month-end account values</strong> exceeds €50,000. Actual law proposes a <strong>daily</strong> average, so this is an approximation, not a provider tax calculation. The charge is deducted at each year-end. Currency and exchange-rate changes, trading costs, stamp duties, fund-level withholding, loss relief and final provider-specific terms are excluded. Illustrations are not forecasts.</p>
</div>

## How the two portfolio styles differ

| Question | Dividend-focused portfolio | Growth-focused portfolio |
| --- | --- | --- |
| Where does most of the assumed return appear? | Partly in regular cash distributions | More in appreciation of the share price |
| Does receiving a dividend create wealth by itself? | No: the share value normally adjusts when cash leaves the business | No distribution is required for a company to create value |
| Irish tax on qualifying dividends or gains inside the proposed PIA? | Generally no separate Irish tax; the PIA charge replaces it | Generally no separate Irish capital gains tax; the same PIA charge applies |
| Foreign withholding exposure | Potentially significant if holding foreign dividend shares | Lower for a low-yield share, but not necessarily zero |
| Reinvestment decision | Cash payments must be reinvested to maintain market exposure | Retained business earnings remain invested inside the company |
| Main business risks | Dividend cuts, yield traps, sector concentration | Expensive valuations, weak reinvestment returns, volatility |

These are **investing styles**, not legal account categories. A company can pay dividends and grow rapidly. Another can pay no dividend and fail to grow. Neither label guarantees a specific outcome.

## What happens to a €100 US dividend in a PIA?

Take a hypothetical US-listed company paying a **€100 equivalent cash dividend**. If **15% US withholding** applies, €15 is deducted before the cash reaches your account and €85 remains available to reinvest. The actual treaty rate and documentation depend on the investor, security and intermediary; a US withholding rate of 15% is not universal.

Under the proposed PIA framework there would generally be **no additional Irish income tax, USC or PRSI on a qualifying dividend inside the account**, and Irish dividend withholding provisions are switched off for qualifying PIA holdings. That **does not remove foreign withholding**, fund-level deductions or possible non-creditable amounts.

For an Irish share, there may be no ordinary Irish dividend withholding in a compliant account under the proposed legislation, although the treatment depends on final law and provider implementation. Do not treat a quoted gross yield as guaranteed net cash.

**Contrast with ordinary investing:** outside a PIA, dividends, share gains and fund distributions can be subject to different Irish regimes. See [Dividend Investing in Ireland](/wealth/dividend-investing-ireland/), [Investment Tax in Ireland](/wealth/investment-tax-ireland/) and the [PIA versus ordinary investing calculator](/pia/vs-ordinary-investing/).

## Why the same total return is the right comparison

Imagine two portfolios each earning an assumed **7% total return before tax and fees** in a year. Portfolio A earns 4 percentage points of the return through dividends and 3 points through share-price movement. Portfolio B earns 0.5 points through dividends and 6.5 points from the share price. Before tax and fees, both provide the same total return.

With **15% foreign withholding on all their dividends**, Portfolio A loses about **0.60 percentage points** of its starting value to withholding in that illustrative year (4% × 15%). Portfolio B loses about **0.075 points** (0.5% × 15%). Assuming reinvestment and no other difference, Portfolio B retains more of the gross return. Over many years, the difference compounds.

But this does **not** mean growth stocks inherently outperform dividend stocks. If their underlying pre-tax returns differ, the outcome may reverse. A high-quality dividend-paying business can outperform a fashionable growth stock. The calculator deliberately separates **return assumptions** from **how returns are distributed**.

## Does the proposed 1% PIA charge favour either style?

**Not directly.** Under the Bill, the 1% investment account tax applies to the amount by which the account's relevant **average annual value** exceeds **€50,000**, regardless of whether the account owns dividend stocks or growth stocks. A dividend held as cash is still generally part of account value.

A hypothetical account averaging €80,000 would incur a charge of **€300**: (80,000 − 50,000) × 1%. A portfolio under the threshold is not charged simply because it paid a dividend. An account above the threshold can owe the charge even if its investments make a loss. The proposal is a **value-based account tax**, not a profits tax.

Our simulator deducts the annual charge using a 12-month average as a **simplification** of the Bill's daily-valuation method. In a real account, intra-month moves, contributions, withdrawals and timing may change the charge. For the mechanics, see [How the PIA daily valuation tax works](/pia/daily-valuation/) and the [main PIA calculator](/pia-calculator/).

## What about an ETF that automatically accumulates dividends?

An *accumulating ETF* can hold shares that pay dividends, retain those payments **inside the fund**, and reinvest them rather than distribute cash to the ETF holder. That does not automatically eliminate foreign withholding at the fund's underlying stock level. Fund domicile, treaty access, index composition, replication approach and fees can all affect the **net fund return**.

**Important modelling distinction:** the calculator treats the entered dividend yield as a **distribution reaching the PIA** and the entered withholding rate as tax deducted before reinvestment at that point. If you are modelling an accumulating ETF, its published total-return figures may **already reflect** fund-level withholding. Do not deduct the same tax twice. You can set the yield input to zero when using an ETF total-return assumption already net of internal fund taxes.

An ETF's tax and cost profile therefore cannot be reduced to the words “dividend” or “growth”. The exact fund and provider matter.

## What if I want monthly dividend income instead of reinvesting?

The simulator assumes **all post-withholding dividends are reinvested**, so both portfolios are compared on accumulated wealth. If you withdraw dividends to spend, the PIA balance will be lower because that money leaves the investment; your **total economic benefit** includes both withdrawn cash and what remains invested. Withdrawing distributions is not necessarily an investment loss, but it reduces future compounding.

The proposed scheme does not require you to be a growth investor. Income-oriented holdings can make sense for investors prioritising cash flow, provided they consider sustainability, diversification, taxes and fees.

## Five pitfalls when building a PIA dividend portfolio

1. **Chasing headline yield.** A falling share price makes the quoted yield look larger, even if a cut is approaching.
2. **Forgetting withholding.** A 5% gross dividend yield is not necessarily a 5% reinvestable yield.
3. **Confusing distributions with performance.** Shares can decline by more than the cash they pay you.
4. **Ignoring sector concentration.** High dividend yields can cluster in particular industries, adding correlated risk.
5. **Treating the Bill as final.** Tax rules, investment eligibility and provider offerings may change before the targeted 2027 opening.

## Which should an Irish investor choose?

**Start with diversification, total expected return, risk and investment costs**, then decide whether you prefer regular cash distributions or company-level reinvestment. Inside the proposed PIA, the Irish tax regime would reduce the difference in the timing of domestic taxes on dividends versus gains. **Foreign withholding remains a meaningful variable** and is the central difference illustrated in our equal-total-return calculator.

A diversified portfolio can contain both dividend-paying and lower-yield companies or funds. The decision is not all-or-nothing. If you are choosing the account itself, start with the [PIA Centre](/pia/), check [which investments may be eligible](/pia/investment-eligibility/) and [compare provider announcements](/pia/providers/).

## Frequently asked questions

### Are dividends tax-free in an Irish PIA?
Under the Finance (No. 2) Bill 2026 **proposal**, qualifying investment income inside an IIA/PIA would generally be exempt from separate Irish income tax; the account-level 1% charge would apply to average value above €50,000. Foreign tax may still be withheld.

### Do you pay US withholding tax on dividends in a PIA?
Potentially, yes. The proposed Irish exemption does not force the US or another foreign country to waive its own withholding. Rates depend on treaties, the investment and account documentation.

### Is a dividend portfolio always less tax-efficient than a growth portfolio?
No. With **identical gross total returns** and higher non-recoverable withholding on one portfolio's distributions, that portfolio would usually compound to less. But actual stocks can have very different total returns, risks, costs and currency exposure.

### Do accumulating ETFs avoid withholding?
Not automatically. An accumulating fund may face foreign tax on dividends received from underlying holdings even if it does not pay cash to the account holder. Avoid modelling those internal taxes twice.

### Can I withdraw dividends from my PIA?
The proposed framework provides for withdrawals without a separate ordinary income or capital gains tax on qualifying account returns. Confirm final legislation, provider conditions, settlement timing and any costs.

*Educational analysis only, not personalised financial or tax advice. The PIA is proposed and is not available to open as at this article's publication date.*
