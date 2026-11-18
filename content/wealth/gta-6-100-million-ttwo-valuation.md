---
title: 'What if GTA 6 sells 100 million copies? A Take-Two stock valuation'
seo_title: 'GTA 6 at 100 Million Copies: TTWO Stock Valuation Calculator'
slug: gta-6-100-million-ttwo-valuation
pillar: wealth
canonical_path: /wealth/gta-6-100-million-ttwo-valuation/
draft: false
publication_status: published
date: 2026-11-18
research_checked: 2026-11-18
editorial_review_status: pending
summary: 'At 100 million copies, GTA 6 could contribute about $4.16 per diluted share in its first 12 months under our assumptions. Use the calculator to see what those sales could be worth to Take-Two.'
meta_description: 'If GTA 6 sells 100 million copies, what happens to Take-Two earnings and TTWO stock? See the SEC-based valuation model and test your own assumptions.'
tags: [stocks, ttwo, take-two, gta-6, gaming, company-research, investing]
image: /static/images/evergreen/gta-6-100-million-ttwo-valuation.jpg
social_image: /static/images/evergreen/gta-6-100-million-ttwo-valuation.jpg
image_alt: Jason Duval and Lucia Caminos sit in a convertible at night in an official Grand Theft Auto VI promotional screenshot.
image_credit: 'Rockstar Games · Official GTA VI promotional screenshot from the Launch Gallery.'
image_source: https://www.rockstargames.com/newswire/article/39ak81277255o9/explore-the-grand-theft-auto-vi-launch-gallery
require_pinned_hero: true
sources:
- title: 'SEC EDGAR · Take-Two Form 10-Q for the quarter ended 30 September 2026'
  url: https://www.sec.gov/Archives/edgar/data/946581/000162828026072254/ttwo-20260930.htm
- title: 'SEC EDGAR · Take-Two Form 8-K, Exhibit 99.1, 9 November 2026'
  url: https://www.sec.gov/Archives/edgar/data/946581/000162828026072175/ttwo2q27earningsrelease.htm
- title: 'ChartExchange · TTWO historical closing prices'
  url: https://chartexchange.com/symbol/nasdaq-ttwo/historical/
- title: 'Take-Two · Rockstar’s GTA VI console preorder and pricing announcement'
  url: https://www.take2games.com/ir/news/rockstar-games-announces-pre-orders-grand-theft-auto-vi
- title: 'Rockstar Games · Official GTA VI media and downloadable screenshots'
  url: https://www.rockstargames.com/VI/media
---
Even **100 million copies of Grand Theft Auto VI** could leave Take-Two shareholders looking for more. In our three-year scenario, those sales generate **$6.50 billion in player spending** and contribute an estimated **$4.16 per diluted TTWO share in the first 12 months**. The model values Take-Two at **$193.45 a share**, about **5.1% below** its **$203.93 close on 17 November 2026**. The biggest driver is what the company can earn after sales of the game slow. [TTWO historical prices](https://chartexchange.com/symbol/nasdaq-ttwo/historical/)

The 100 million is a scenario over three years. It includes 50 million copies in the first 12 months and 25 million in each of the next two years. Take-Two has not issued a 100-million-copy sales forecast. For the shorter release window, see [Compound’s GTA 6 launch sales estimates](/wealth/ttwo-gta-6-entertainment-launch-revenue/).

## Calculate your own TTWO valuation

Enter worldwide copies in millions and change the average selling price, publisher share or profitability. Open the additional assumptions to vary the timing, discount rate, balance sheet and share count. The comparison starts at the 17 November close and can be updated by entering a different share price. All amounts are in US dollars.

<form class="ttwo-model" data-ttwo-model aria-label="GTA 6 and TTWO valuation calculator">
<fieldset>
<legend>Sales and valuation assumptions</legend>
<div class="ttwo-model-grid">
<label>Copies sold (millions)<input type="number" name="copies" value="100" min="0" max="1000" step="0.1" required></label>
<label>Average selling price ($ per copy)<input type="number" name="price" value="65" min="0" max="250" step="0.01" required></label>
<label>Publisher share of player spending (%)<input type="number" name="publisherShare" value="70" min="0" max="100" step="0.1" required></label>
<label>Pre-tax operating margin on publisher sales (%)<input type="number" name="margin" value="45" min="-100" max="100" step="0.1" required></label>
<label>Ongoing annual free cash flow outside modelled copies ($bn)<input type="number" name="otherCash" value="1.65" min="0" max="25" step="0.01" required></label>
<label>Enterprise value / ongoing cash flow multiple (×)<input type="number" name="multiple" value="22" min="0.1" max="100" step="0.1" required></label>
</div>
</fieldset>
<details>
<summary>Timing, tax and other assumptions</summary>
<div class="ttwo-model-grid">
<label>Total years to sell the copies<input type="number" name="years" value="3" min="1" max="15" step="1" required></label>
<label>Share of sales in the first 12 months (%)<input type="number" name="yearOne" value="50" min="0" max="100" step="0.1" required></label>
<label>Effective tax rate (%)<input type="number" name="tax" value="23" min="0" max="100" step="0.1" required></label>
<label>After-tax earnings converted to free cash flow (%)<input type="number" name="conversion" value="90" min="0" max="200" step="0.1" required></label>
<label>Annual discount rate for title cash flow (%)<input type="number" name="discount" value="10" min="0" max="100" step="0.1" required></label>
<label>Net debt ($m, negative for net cash)<input type="number" name="netDebt" value="846.2" min="-20000" max="20000" step="0.1" required></label>
<label>Diluted shares (millions)<input type="number" name="shares" value="189.5" min="1" max="10000" step="0.1" required></label>
<label>TTWO comparison price ($)<input type="number" name="sharePrice" value="203.93" min="0.01" max="10000" step="0.01" required></label>
</div>
</details>
<button type="reset">Reset assumptions</button>
<p class="ttwo-model-status" data-ttwo-status role="status"></p>
<dl class="ttwo-model-results" data-ttwo-results>
<div><dt>Implied value per TTWO share</dt><dd><output data-result="value">$193.45</output></dd></div>
<div><dt>Difference from comparison price</dt><dd><output data-result="comparison">−5.1%</output></dd></div>
<div><dt>Title earnings per diluted share, first 12 months</dt><dd><output data-result="eps">$4.16</output></dd></div>
<div><dt>Player spending on copies</dt><dd><output data-result="spending">$6.50bn</output></dd></div>
<div><dt>Publisher proceeds before operating costs</dt><dd><output data-result="publisher">$4.55bn</output></dd></div>
<div><dt>Title after-tax earnings over sales period</dt><dd><output data-result="earnings">$1.58bn</output></dd></div>
<div><dt>Present value of title cash flow</dt><dd><output data-result="titleValue">$1.20bn</output></dd></div>
<div><dt>Title cash flow value per diluted share</dt><dd><output data-result="titlePerShare">$6.36</output></dd></div>
<div><dt>Ongoing annual cash flow needed to match comparison price</dt><dd><output data-result="breakEven">$1.74bn</output></dd></div>
</dl>
<noscript><p>The results shown use the default assumptions. Enable JavaScript to update them.</p></noscript>
</form>

## How 100 million copies flow through earnings

Rockstar announced US launch prices of **$79.99** for the standard edition and **$99.99** for the Ultimate Edition. Our **$65 blended price** is a worldwide, pre-sales-tax average over three years. Premium sales can lift that average and regional pricing and discounts can pull it down. [Take-Two’s preorder announcement](https://www.take2games.com/ir/news/rockstar-games-announces-pre-orders-grand-theft-auto-vi)

| Step | 100-million-copy case |
| --- | ---: |
| Consumer spending at $65 per copy | $6.50bn |
| Publisher proceeds at 70% of spending | $4.55bn |
| Operating contribution at a 45% margin on publisher proceeds | $2.05bn |
| After-tax operating contribution at a 23% tax rate | $1.58bn |
| First-12-month contribution with 50% of units sold | $788m |
| First-12-month contribution per 189.5m diluted shares | $4.16 |

The assumed margin allows for Take-Two’s costs after distribution, including development amortisation, marketing and support. Take-Two’s SEC filing reports **$2.58 billion of capitalised software development costs and licences across the group** at 30 September. That balance covers the portfolio. A separate GTA 6 budget and title-level margin are unavailable in the 10-Q. The model holds the unit economics constant across all three years, even though the real price and margin could change over time. [Take-Two’s September 10-Q, Note 7](https://www.sec.gov/Archives/edgar/data/946581/000162828026072254/ttwo-20260930.htm)

Take-Two’s November 8-K exhibit guided to **$7.98–$8.18 billion of GAAP revenue, $8.0–$8.2 billion of net bookings and $0.57–$0.75 of diluted GAAP EPS** for fiscal 2027. That company-wide outlook already includes the game’s November launch. It ends on **31 March 2027**, a little over four months into the game’s release. The **$4.16** in the table is a title contribution estimate for a 12-month window before financing effects. Adding it to March-year EPS guidance would double-count launch economics and mix reporting periods. [Take-Two’s 8-K, Exhibit 99.1](https://www.sec.gov/Archives/edgar/data/946581/000162828026072175/ttwo2q27earningsrelease.htm)

## How much could 100 million GTA 6 copies add to TTWO stock?

The model values the finite run of game-copy sales separately from the cash Take-Two could earn on an ongoing basis.

1. **GTA 6 copies.** Convert 90% of the title’s after-tax operating contribution into cash available before financing. Split it by the sales schedule and discount the annual cash flows at 10%, assuming they arrive at each year-end. This gives **$1.20 billion today**, or **$6.36 per diluted share**, for the 100-million-copy run. No residual value is assigned to those copies after the sales period.
2. **Ongoing business.** Apply a **22× enterprise value multiple** to **$1.65 billion of assumed annual free cash flow before financing**, excluding the GTA 6 copy profits already counted above. This gives **$36.30 billion** of ongoing enterprise value. The cash input is an illustrative hurdle for the rest of the business and any durable recurring economics a reader chooses to include. Neither it nor the multiple is a figure reported by Take-Two.
3. **Enterprise value to shares.** Add the title value to the ongoing enterprise value, subtract **$846.2 million** of net debt and divide by **189.5 million** diluted shares. The resulting equity value is approximately **$36.66 billion**, or **$193.45 per share**.

The net-debt calculation uses **$2.52 billion in short- and long-term debt carrying values**, less **$1.15 billion in unrestricted cash and cash equivalents** and **$524.2 million in short-term investments** at 30 September. The 8-K supplies the diluted share count. The 10-Q reports **187.21 million actual shares outstanding** as of 26 October, implying about **$38.18 billion** of basic equity market value at the reference close. We use the higher diluted count to spread the modelled equity value over potential dilution. [Take-Two’s 10-Q](https://www.sec.gov/Archives/edgar/data/946581/000162828026072254/ttwo-20260930.htm) · [Take-Two’s 8-K exhibit](https://www.sec.gov/Archives/edgar/data/946581/000162828026072175/ttwo2q27earningsrelease.htm)

For context, management expects **more than $1 billion in company-wide operating cash flow** and about **$290 million of capital expenditure** in fiscal 2027. At the stated operating-cash-flow threshold, the simple difference is about **$710 million**. That comparison includes the GTA 6 launch and uses reported cash-flow categories. The $1.65 billion model input is a longer-run assumption before financing and excludes the copy sales valued separately. [Take-Two’s 8-K exhibit](https://www.sec.gov/Archives/edgar/data/946581/000162828026072175/ttwo2q27earningsrelease.htm)

### What changes the valuation most?

| Copies sold in three years | Estimated first-year contribution per diluted share | Implied TTWO value at 22× ongoing cash flow |
| ---: | ---: | ---: |
| 60 million | $2.50 | $190.91 |
| 80 million | $3.33 | $192.18 |
| 100 million | $4.16 | $193.45 |
| 120 million | $4.99 | $194.72 |

Holding everything else fixed, **100 million rather than 60 million copies adds about $2.54 per diluted share** of present value. At 100 million copies, changing only the ongoing multiple to **18× or 26×** moves the total valuation to **$158.62 or $228.28**. The cash flows investors expect years after launch have the bigger effect in this model.

At **$203.93**, 100 million copies and a **22×** multiple, Take-Two would need about **$1.74 billion in annual ongoing cash flow outside the modelled copies** to match the reference share price. Sustained spending on an online offering could help reach that figure, alongside games and services elsewhere in the portfolio. The title cash-flow calculation assigns no separate cash flow to online purchases or add-ons. To test a recurring revenue thesis, increase ongoing free cash flow by the amount you estimate would remain after costs, tax and reinvestment.

Read the [Take-Two stock research page](/stocks/ttwo/) for company results and filings.
