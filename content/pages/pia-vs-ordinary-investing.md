---
title: "PIA vs ETF vs Shares Calculator Ireland: After-Tax Comparison"
canonical_path: /pia/vs-ordinary-investing/
meta_description: "Ireland PIA vs ETF vs shares: free after-tax calculator and 5-, 10-, 20- and 30-year worked examples using CGT, proposed fund exit tax and PIA daily-value tax."
---

[PIA Centre](/pia/) · [PIA vs pension](/pia/vs-pension/) · [Irish investment-tax guide](/wealth/investment-tax-ireland/) · Updated 13 November 2026. This comparison uses proposals in the Finance (No. 2) Bill 2026 **as introduced**; it is not a statement of enacted 2027 rules.

## Should I buy ETFs or shares inside a PIA or outside it?

**Short answer:** For an eligible investment, Ireland's proposed **Personal Investment Account (PIA)** would charge **1% per year on the portion of its relevant average daily account value above €50,000**. An equivalent accumulating UCITS ETF held outside a PIA may face fund exit tax and **eight-year deemed disposal**, while directly owned shares generally face **Capital Gains Tax (CGT) when sold**, with dividends taxed separately. The better *after-tax* result depends on contributions, returns, the precise ETF's legal tax regime, investment expenses, personal CGT exemption use and the holding period. No structure is automatically best.

The currently applicable 2026 rate for many Irish/equivalent offshore funds is **38%**. The [Finance (No. 2) Bill 2026, section 29](https://assets.gov.ie/static/documents/89edf30b/Finance_No._2_Bill_2026.pdf) proposes **35% for relevant chargeable events from 1 January 2027**, subject to enactment. The standard Irish CGT rate is **31% for most applicable disposals from 7 October 2026**. A rate comparison alone is misleading because each tax uses a different basis and timing.

Our free calculator below uses the **same pre-tax hypothetical return across all three approaches**, so the illustration isolates tax and fee assumptions. You can use an accumulating ETF or a direct-share example without treating every ETF or share as identical.

<section id="pia-investing-tool" data-pia-investing-tool aria-labelledby="pit-heading">
<p class="pit-eyebrow">FREE INDEPENDENT CALCULATOR · IRELAND</p>
<h2 id="pit-heading">PIA vs ETF vs shares: after-tax calculator</h2>
<p class="pit-lede">What might be left after tax if you invest the same amount in a proposed PIA, an accumulating ETF outside the PIA, or direct shares outside it? Change the return, time horizon, fees and tax assumptions. The examples are illustrative—not guaranteed returns or a product recommendation.</p>
<noscript><p>Enable JavaScript for interactive calculations; the sourced comparison and four worked scenarios below are readable without JavaScript.</p></noscript>
<div class="pit-layout">
<form class="pit-form" data-pit-form>
<label>Monthly investment (€)
<input type="number" name="monthly" value="500" min="0" max="1000" step="10" required>
<small>Capped at €1,000/month to respect the announced €12,000 annual PIA contribution limit.</small></label>
<label>Investment horizon
<select name="years"><option value="5">5 years</option><option value="10" selected>10 years</option><option value="20">20 years</option><option value="30">30 years</option></select></label>
<label>Assumed total annual investment return, before taxes and fees (%)
<input type="number" name="annual_return" value="6" min="-20" max="30" step="0.5" required>
<small>Identical hypothetical pre-tax total return for all three wrappers. Market returns may be negative.</small></label>
<label>ETF/fund exit tax outside the PIA
<select name="etf_exit_rate"><option value="35" selected>35% — proposed from 2027, not yet law</option><option value="38">38% — current 2026 rate for relevant funds</option></select>
<small>Only relevant Irish/equivalent offshore accumulating funds are represented. Other ETFs may follow different regimes.</small></label>
<details class="pit-advanced"><summary>Advanced: fees, dividends and CGT</summary>
<div class="pit-fields">
<label>Annual PIA account and investment fee (%)
<input name="pia_fee" type="number" min="0" max="5" step="0.05" value="0.25" required></label>
<label>Annual outside ETF and fund fee (%)
<input name="etf_fee" type="number" min="0" max="5" step="0.05" value="0.25" required></label>
<label>Annual outside shares/broker fee (%)
<input name="shares_fee" type="number" min="0" max="5" step="0.05" value="0.25" required></label>
<label>Unused personal CGT exemption at disposal (€)
<input name="cgt_exemption" type="number" min="0" max="1270" step="10" value="1270" required>
<small>2026 standard annual exemption is €1,270 per person, not for each share or each year of unrealised gains. Set to zero if already used elsewhere.</small></label>
<label>Direct shares: annual dividend yield (%)
<input name="dividend_yield" type="number" min="0" max="15" step="0.5" value="0" required>
<small>Part of the *same total return*, not an extra return. Zero models non-dividend-paying shares.</small></label>
<label>Direct shares: effective personal tax on dividends (%)
<input name="dividend_tax" type="number" min="0" max="65" step="1" value="40" required>
<small>Illustrative combined Income Tax/USC/PRSI assumption; real dividends and foreign tax credits vary.</small></label>
</div></details>
<button type="submit">Calculate after-tax comparison</button>
</form>
<div class="pit-results">
<div class="pit-cards" aria-live="polite">
<div class="pit-card pit-card-pia"><span>PIA (after proposed charge)</span><strong data-pit-result="pia">—</strong></div>
<div class="pit-card"><span>Outside accumulating ETF (net if sold)</span><strong data-pit-result="etf">—</strong></div>
<div class="pit-card"><span>Outside direct shares (net if sold)</span><strong data-pit-result="shares">—</strong></div>
</div>
<p class="pit-lede" data-pit-explain aria-live="polite"></p>
<div class="pit-chart-wrap">
<h3>Illustrative after-tax liquidation value</h3>
<div class="pit-chart" data-pit-chart></div>
<p class="pit-legend"><b>PIA</b><b>Outside ETF</b><b>Direct shares</b></p>
</div>
<div class="pit-breakdown">
<h3>Contribution and tax breakdown</h3>
<dl>
<dt>Contributed per wrapper</dt><dd data-pit-result="contributed">—</dd>
<dt>PIA taxes deducted over the period</dt><dd data-pit-result="pia-tax">—</dd>
<dt>Outside ETF: 8-year deemed-disposal and sale taxes</dt><dd data-pit-result="etf-tax">—</dd>
<dt>Outside ETF holding before final sale tax</dt><dd data-pit-result="etf-gross">—</dd>
<dt>Direct shares: dividend tax and final CGT</dt><dd data-pit-result="shares-tax">—</dd>
<dt>Direct shares holding before final CGT</dt><dd data-pit-result="shares-gross">—</dd>
</dl>
</div>
<div class="pit-breakdown pit-table-wrap">
<h3>Year-by-year reference values</h3>
<table><thead><tr><th scope="col">Period</th><th scope="col">PIA</th><th scope="col">Outside ETF after sale</th><th scope="col">Shares after sale</th></tr></thead><tbody data-pit-rows></tbody></table>
</div>
<p class="pit-warning" data-pit-warning></p>
</div>
</div>
<p class="pit-notes"><strong>Important:</strong> This model assumes smooth returns, 365-day years and 12 month-end contributions. The PIA charge is based on modelled average daily account values above €50,000. The outside ETF example represents an accumulating fund within the relevant exit-tax/deemed-disposal regime and approximates tax on each monthly purchase lot at 8-year anniversaries, funding tax from the holding and resetting its remaining basis; actual deemed-disposal credits, losses and fund administration may differ. Shares incur standard CGT on positive gain upon final disposal, with one remaining personal exemption; optional dividend yield is taxed and the net dividend reinvested. Flat brokerage, trading, FX, foreign withholding, tax losses and the partial 2027 opening year are not modelled. The PIA and 2027 fund tax changes remain subject to legislation. <a href="#pit-methodology">Full calculation methodology</a>.</p>
</section>

## Worked example: how the tax differences compound

Suppose an Irish-resident adult contributes **€500 per month**, earns an *illustrative* **6% annual total return** before fees and tax, and pays **0.25% annually in combined investment/provider fees** in every wrapper. There are no starting assets, dividends on the direct-share example, sales before the comparison date or additional brokerage/FX fees. The ETF is a **relevant accumulating UCITS-style fund**, modelled with **35% proposed exit tax from 2027** and taxable eight-year anniversaries for each monthly purchase lot. The direct shares use 31% standard CGT at the final sale and the **remaining €1,270 annual personal exemption** once at that sale. The PIA applies its proposed 1% account-value charge annually.

<!-- pia-investing-examples:start -->

| Holding period | Contributed to each | PIA after account charge | Outside accumulating ETF after sale tax | Direct shares after CGT |
| --- | ---: | ---: | ---: | ---: |
| 5 years | €30,000 | €34,524 | €32,940 | €33,515 |
| 10 years | €60,000 | €79,685 | €73,012 | €74,297 |
| 20 years | €120,000 | €208,455 | €180,723 | €189,488 |
| 30 years | €180,000 | €412,420 | €339,697 | €376,792 |

<!-- pia-investing-examples:end -->

These are **after-tax liquidation comparisons**: the outside ETF and share columns deduct illustrative final disposal tax at each horizon, not simply show pre-tax brokerage balances. The PIA column reflects its annual account charges, with no assumed extra CGT or fund exit tax inside the proposed wrapper. All amounts are rounded and are illustrative, not forecasts.

For a 30-year horizon this model also estimates cumulative PIA account charges, outside ETF deemed-disposal charges and final taxes. Those cumulative totals **cannot be compared directly to final account values**: tax deducted in year eight also reduces the money that could otherwise have compounded. All figures should be regenerated from the calculator if assumptions change.

## Which investments are being compared?

| Investment route | Modelled tax treatment | Important limitations |
| --- | --- | --- |
| **Eligible ETF or shares inside a PIA** | Proposed 1% yearly tax on the portion of average daily account value above €50,000; no ordinary CGT/ETF exit-tax event within the wrapper in the draft design | €12,000 announced annual contribution limit, restricted eligible investments and provider menus, and PIA-specific fees; not yet law |
| **Accumulating ETF outside a PIA** | Relevant Irish/equivalent offshore fund exit tax at the chosen 35% (proposed 2027) or 38% (current 2026), including approximated eight-year deemed-disposal events | Not every ETF uses this regime; domicile, structure, holding method, credits and losses require individual review |
| **Directly held shares outside a PIA** | Standard 31% CGT on realised net gains after available €1,270 personal annual exemption; taxable dividends if paid | Dividends can incur Income Tax, USC, PRSI and foreign withholding; concentration risk and company losses differ from a diversified fund |

**The investable asset matters as much as the wrapper.** A diversified UCITS ETF is not equivalent in risk to one volatile share. The calculator deliberately gives the options the same total return to compare taxes, **not to imply equivalent real-world risk**. For security-level eligibility, see [which shares, bonds and ETFs might qualify](/pia/investment-eligibility/) and confirm the exact ISIN with any future provider.

## Does eight-year deemed disposal change the answer?

Yes. In the applicable outside-fund regime, an eight-year deemed-disposal event can create a liability even without an actual sale. With monthly purchases, each lot has its own acquisition anniversary, not just one universal anniversary for the account. We model this at 96-month multiples for each purchase lot.

For readability, our estimate assumes positive unrealised gains are taxed on each deemed event and that the amount is **paid from that holding**, reducing its future compounding. The remaining lot's tax basis is reset for later positive-gain calculations. Actual Revenue rules involve credit and offset mechanics and could produce different results on losses, switches, gifts, transfers or partial disposals. The current model **does not** claim to reproduce every statutory credit or loss-relief case.

Importantly, ordinary direct shares do **not** automatically incur eight-year deemed disposal. A final-sale CGT illustration cannot be equated to the ETF regime simply by comparing 31% versus 35%.

## Is the PIA automatically better for an S&P 500 ETF?

No. A PIA would change the *account's* tax mechanics, not guarantee ETF eligibility or a low-cost S&P 500 product. Check the particular fund's legal structure and the chosen provider's investment list. If its actual management costs are higher, its net outcome could differ materially. A PIA also has the proposed €12,000 yearly contribution limit and investment account tax based on value, which can arise in a poor investment year if its average account value remains above €50,000.

See our [PIA provider tracker](/pia/providers/) for verified announcements and [PIA fee comparison examples](/pia/compare-fee-quotes/) for hypothetical fixed versus percentage costs. Provider-specific prices are unknown where they have not been published.

## What if I hold dividend-paying shares?

Direct shares are not taxed exclusively on disposal. Some pay dividends that may be subject to Income Tax, USC and PRSI, and foreign dividends can involve foreign withholding and tax-credit arrangements. In **Advanced** mode, set a dividend yield and an *illustrative effective personal dividend-tax rate*. The model splits the same total return into price growth and dividends, taxes the dividends as they arise, and reinvests the after-tax amount. That reinvested amount increases the share portfolio's CGT cost basis.

The default 0% dividend yield is deliberately a **non-dividend-paying share illustration**. It is not a realistic dividend assumption for every individual share, index, or ETF. The fund example assumes an *accumulating* ETF whose internal distributions remain inside the fund and are reflected in growth.

## How is the PIA versus ordinary investing calculator calculated? {#pit-methodology}

**Monthly contributions:** All three wrappers receive equal new money at 12 modelled month ends. The maximum input is €1,000 per month to stay within the proposed annual PIA allowance. There are no opening contributions, top-ups, transfers or withdrawals.

**Growth and fees:** A constant annual total return is converted to an illustrative daily compounding rate. The separate percentage fee for each account is deducted daily. Actual securities move irregularly and providers may charge fixed dealing fees and foreign exchange charges.

**PIA tax:** The model records 365 daily closing balances, averages them for each full modelled year, and deducts **1% × max(0, average − €50,000)** at that year's end. The planned 1 July 2027 opening and part-year rules are *not* included.

**ETF outside a PIA:** Each contribution creates a separately tracked purchase lot. At each 96-month anniversary the model applies the selected fund exit-tax rate on positive gains since that lot's prior taxable event, subtracts tax from the investment and resets the remaining lot's cost base for subsequent modelled gains. At each displayed horizon it estimates a hypothetical full liquidation, charging the selected rate on remaining positive gains. This approximation does not model all tax credits, refunds, losses or administration rules.

**Direct shares outside a PIA:** Cost base is tracked for contributions and reinvested after-tax dividends. At each displayed horizon the tool estimates a *single final sale*, subtracting the remaining personal annual CGT exemption once, then applying 31% to the positive chargeable gain. No other gains or losses are included.

**Tax rates and law:** The 35% 2027 fund rate and PIA are **proposals in the Finance (No. 2) Bill**; the tool also allows the current 38% ETF/fund regime rate. No automatic 2027 rate change is assumed for mid-horizon years. The standard CGT rate and personal exemption are held constant for illustration, not a prediction of future budgets.

**Tax drag versus cumulative tax:** The model reports cumulative charges paid and final after-tax value. A tax paid early can also remove future investment growth, so cumulative tax is not the same as the reduction in final value. Past and future rates can change.

## Primary sources and editorial standards

Compound is an independent Irish publisher, not a pension provider, PIA provider or investment adviser. The figures here are **original simulations** from the interactive engine; regression tests validate baseline arithmetic, deemed disposal lot timing, the CGT exemption, dividend taxation, fee sensitivity and the published static examples.

- [Finance (No. 2) Bill 2026, as introduced — sections 26, 28, 29](https://assets.gov.ie/static/documents/89edf30b/Finance_No._2_Bill_2026.pdf) — proposed individual investment account, ETF arrangements and 35% fund-rate change.
- [Finance Bill 2026 explanatory memorandum](https://assets.gov.ie/static/documents/8ee6faff/Finance_No._2_Bill_2026_Explanatory_Memorandum.pdf) — published explanation of the proposed 35% fund rate from 1 January 2027.
- [Revenue eBrief 016/26](https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-0162026.aspx) — reduction to the currently applicable 38% relevant fund rate from 1 January 2026.
- [Revenue eBrief 142/26](https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx) — 31% standard CGT on applicable disposals from 7 October 2026.
- [Revenue: taxation of domestic and offshore funds](https://www.revenue.ie/en/companies-and-charities/financial-services/collective-investment-vehicles/funds.aspx) — why fund domicile and category matter.
- [Compound's editorial policy](/editorial-policy/) — sourcing, corrections and independence.

The models are educational scenarios, not tax advice, broker quotes or guaranteed returns. Review the final legislation and Revenue/provider guidance before acting.

## Continue your research

Compare the proposed PIA against [a pension using the same take-home cost](/pia/vs-pension/), estimate the [PIA account charge alone](/pia-calculator/), read the [full Personal Investment Account guide](/wealth/personal-investment-account-ireland/), or examine [Irish share and ETF tax rules](/wealth/investment-tax-ireland/).

