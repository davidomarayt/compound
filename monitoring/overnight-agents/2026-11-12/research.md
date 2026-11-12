# Compound overnight research — 12 November 2026

**Research worker:** completed primary-source research and exact calculations; no new article or company-profile change. **Branch checked:** `claude/clever-babbage-uibieq`, publishing workflow `.github/workflows/site.yml` deploys on pushes to this branch. **Inventory:** 11 November 2026 snapshot, 276 articles/guides, 64 tools, 511 listed-company profiles, 13 private-company profiles. This is a content count, not traffic. **New research publication:** 0.

## 1. Original Research Agent — Ireland's October 2026 inflation, with a reproducible purchasing-power illustration

**Primary source, released 11 November 2026 at 11:00 Irish time:** [CSO Consumer Price Index October 2026](https://www.cso.ie/en/releasesandpublications/ep/p-cpi/consumerpriceindexoctober2026/), including [linked PxStat tables](https://www.cso.ie/en/releasesandpublications/ep/p-cpi/consumerpriceindexoctober2026/data/).

Source-verified figures:
- CPI all-items annual inflation: **4.3%** in the 12 months to October 2026, versus **4.1%** annual in September 2026, a **0.2 percentage-point** increase in the annual rate. October's month-on-month CPI increase was **0.7%**.
- CPI excluding energy and unprocessed food: **3.1%** annual; this is an **alternative basket and weight set**, not an estimate of how many percentage points energy contributed to headline inflation.
- Housing, Water, Electricity, Gas & Other Fuels division: **+10.7%** annual; Transport **+9.0%**. These are division indices, not representative increases in all households' total bills.
- HICP annual October measure: **4.2%**; differs in coverage from the domestic CPI, notably its treatment of mortgage interest. Avoid presenting HICP and CPI as interchangeable.

**Independent, reproducible illustration:** A fixed illustrative CPI-representative basket priced at **€1,000 in October 2025** would cost approximately **€1,043 in October 2026** under a 4.3% index increase: `1000 × (1 + 0.043) = 1043`. That is **€43 per €1,000 of equivalent goods/services at these two points in time**, not the full year's accumulated expenditure, a forecast, or an individual's exact inflation. Actual household patterns, weights and substitutions differ.

**Editorial usefulness:** A source-led, dated update to existing `/news/personal-inflation-rate-ireland-households-2026/` or the existing inflation calculator context could explain why households experience different price changes; first check whether today's Irish news workflow has already covered the same 11 November CPI release. The inventory also lists `/news/ireland-inflation-september-2026-energy-prices/`; do **not** overwrite its historical September report with October data or create a duplicate news piece to meet a quota.

**Decision:** publish **no** standalone research article in this overnight worker; add the calculations as an evidence brief for the future canonical update/publishing agent after collision and source review. No review date changed.

## 2. Private Company Intelligence Agent — Anthropic proposed IPO, avoiding overlap

**Original company source dated 10 November 2026:** [Anthropic announced a proposed IPO roadshow](https://www.anthropic.com/news/roadshow-launch).
- The company described a **proposed**, not completed, Class A offering of **825,000,000 shares** at an indicative **$70–$78 per share**.
- Of those, **801,351,354 primary shares** would be issued by Anthropic; **23,648,646 secondary shares** would be sold by existing holders. Anthropic says it receives **no** proceeds from selling-shareholder shares.
- **Derived indicative gross deal size:** `825,000,000 × $70–$78` = **$57.750–$64.350 billion**. Indicative **primary gross issuance**: `801,351,354 × $70–$78` = **$56.095–$62.505 billion** before expenses. Indicative **secondary gross amount**: `23,648,646 × $70–$78` = **$1.655–$1.845 billion** to selling holders, not to Anthropic.
- The separate **123,750,000-share** overallotment option is excluded from the base figures. Do not infer market cap from offered shares because total outstanding diluted shares are not established by this announcement. The announced proposed ticker is **ANT**; do not call it an already-trading public ticker. Anthropic says the registration statement was not yet effective as of its 10 November announcement. Verify any later SEC effectiveness and pricing before updating that status.
- Existing canonical `/wealth/anthropic-loss-ipo-valuation/` discusses IPO valuation; check its thesis and date rather than creating a near-duplicate. Open [PR #107](https://github.com/davidomarayt/compound/pull/107) covers Anthropic model pricing and OpenAI commerce among three unpublished company articles; this worker made no overlapping content edit.
- **SpaceX correction to old topic classification:** It has been **publicly traded since 12 June 2026** under SPCX, per [SpaceX's June 15 issuer IPO closing release](https://ir.spacex.com/updates/releases-details/2026/Space-Exploration-Technologies-Corp--Announces-Closing-of-Initial-Public-Offering-Including-Full-Exercise-of-Underwriters-Option-to-Purchase-Additional-Shares-2026-RgoR-Y1Vwh/). Its canonical listing profile is `/stocks/spcx/`, not a privately held company listing. Future research should route through public-stock workflow.
- For OpenAI, the pending company article in PR #107 is already about 10 November Businesses in ChatGPT; no duplicate created.

**Decision:** research complete, no profile/article PR, merge or deployment. Dates are source/publication dates, not fabricated editorial approvals. If the 07:00 private-company workflow writes on Anthropic's IPO, it must dedupe existing canonical IPO coverage and independently verify the securities-registration stage.

## Coordination

Open PRs reviewed: [#107](https://github.com/davidomarayt/compound/pull/107) (private-company articles and profile template), [#115](https://github.com/davidomarayt/compound/pull/115) (buying-home link), [#57](https://github.com/davidomarayt/compound/pull/57) (solar freshness pilot). The engineering improvement from this group is separately documented in `engineering.md` and [draft PR #116](https://github.com/davidomarayt/compound/pull/116).

**Original Research status:** evidence brief recorded; 0 new published URLs. **Private Company Intelligence status:** source/date/math classification research recorded; 0 new published URLs. **No production or ads changes.**
