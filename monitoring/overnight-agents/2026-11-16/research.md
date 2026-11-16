# Compound overnight research and private-company intelligence — 2026-11-16 (Europe/Dublin)

**Worker:** five-role Research + Engineering stage; this record owns **5. Original Research** and **6. Private Company Intelligence**. GitHub default and actual GitHub Pages publishing branch confirmed as `claude/clever-babbage-uibieq` from `get_repo` and `.github/workflows/site.yml` prior to any work. Read `AGENTS.md`, the efficiency/QA runbook, `EDITORIAL_TOPIC_INDEX.md`, `CONTENT_INVENTORY.md`, `data/content-inventory.json` (15 Nov source snapshot), the available 12–15 Nov overnight research records, 16 Nov discovery/content records, recent company publishing ledgers, current open PRs and existing templates. The preceding 30-day record search found no earlier nightly research record before 12 November. **No new article or live URL, no human-approval claim, no merge, no price/ad/privacy/schedule change.** A separate four-file draft engineering PR is [#150](https://github.com/davidomarayt/compound/pull/150), with independent QA and CI gates; see [engineering.md](engineering.md).

## 5. Original Research — NEW ATTRIBUTABLE PRIMARY-DATA BRIEF; review-only

### New source and question
The [CSO *Agricultural Land Prices 2025*, dated 13 November 2026 at 11am](https://www.cso.ie/en/releasesandpublications/ep/p-alp/agriculturallandprices2025/), is a materially **new** release relative to the preceding night's October CPI, September retail mortgage-rate and earlier analyses. Checked the [CSO key findings](https://www.cso.ie/en/releasesandpublications/ep/p-alp/agriculturallandprices2025/keyfindings/) and [CSO methodological background](https://www.cso.ie/en/releasesandpublications/ep/p-alp/agriculturallandprices2025/backgroundnotes/) on 16 Nov. Existing editorial index, inventory, 12–15 Nov research ledgers and open PRs do not document a canonical page or queued PR answering **how arable/grassland and regional medians differ in the newly released 2025 eligible agricultural-sale sample**. This is an unpublished source-linked brief, not a filler article or a ranking prediction.

### Published inputs and independently reproducible comparisons

| Measure | Published CSO value / source period | Derived reader-useful comparison |
| --- | --- | --- |
| Agricultural acreage sold nationally, 2025 | 56,613 acres | Total *eligible transacted area*, not acreage of Irish farmland |
| Total transaction value, 2025 | €561.8 million | Approximate value/acre across eligible sales: `€561,800,000 / 56,613 = €9,924` (rounded, **mean**, not median) |
| National median transaction price, 2025 | €10,143 per acre | Distinct statistic from volume-weighted mean; cannot multiply median by acreage to infer total market expenditure |
| Arable land median, 2025 | €16,942 per acre | `(16,942 / 9,959 - 1) × 100 = 70.1%` above the grassland median, or €6,983 per acre |
| Permanent grassland median, 2025 | €9,959 per acre | Different property/land type; no inference that arable land necessarily earns 70.1% more income |
| Dublin regional median, 2025 | €24,695 per acre | `24,695 / 7,374 = 3.35×` the West regional median |
| Mid-East median (Kildare, Louth, Meath, Wicklow), 2025 | €15,828 per acre | `15,828 / 7,374 = 2.15×` the West regional median |
| West median (Galway, Mayo, Roscommon), 2025 | €7,374 per acre | Regional median, not necessarily an equivalent parcel, grade or location |

The CSO also quotes a 2024 national median of €9,742/ac and a 2025 median of €10,143/ac (+4.1% as reported), but its **explicit caveat** is that changes in mean or median between years are *not suitable for measuring price evolution* because the mix of land transacted changes. Likewise, 56,613 acres is not a full-market valuation. Reported 2025 transaction value is €561.8m; multiplying €10,143 by the 56,613 acres would give €574.2m, illustrating why median × volume is not the official total.

### Provenance, exclusions, limits and editorial recommendation
CSO combines Revenue Stamp Duty Returns, property registry geolocation and Census of Agriculture classification. Eligible transactions exclude sales with attached dwellings, non-agricultural/development or forestry use, inheritance transfers, sales with entitlements, commonage and small plots under 0.2 hectares, among other criteria; see official [background notes](https://www.cso.ie/en/releasesandpublications/ep/p-alp/agriculturallandprices2025/backgroundnotes/). These are **sample composition differences**, not controlled causal effects or investment/annual yields. A useful future reader-facing *existing-page* enhancement, if a matching Irish land/property guide is found, would explain "median price, land type, location and what the CSO excludes" with methodology beside the numbers. **No article created or published tonight; no imperative content quota.** Fingerprint: `CSO-ALP-2025-2026-11-13/land-type-region-median`. Do not repeat this briefing unchanged on later nights.

**Outcome: REVIEW_ONLY — distinct attributable research brief, calculations and limitations documented; 0 site changes.**

## 6. Private Company Intelligence — NO_MATERIAL_PROFILE_CHANGE

- Read `content/company-watchlist.json` last source-checked **15 Nov** and the [15 Nov private publisher ledger](../../private-company-publications/2026-11-15.json) (at its examined state: three prepared pieces on OpenAI, Anthropic, Stripe, pending CI/release) plus the 14 Nov published ledger. The 07:00 publishing workflow independently owns new articles; this 03:00 role neither duplicates its topics nor pre-approves later release.
- Reviewed **16 Nov** primary issuer news indexes: [Anthropic News](https://www.anthropic.com/news) showed the **10 Nov** proposed IPO roadshow and **9 Nov** model release; a roadshow does *not itself* prove completion or actual public trading. [Stripe Newsroom](https://stripe.com/newsroom/news) showed the **10 Nov** HSBC announcement as latest on consulted index, already relevant to the pending publisher coverage. [Blue Origin News](https://www.blueorigin.com/news) showed the **10 Nov** hotfire update and **5 Nov** GS3/Northstar releases, previously within the tracked period. The checked listings showed no clearly new, financially material, independently primary-sourced update *not already queued or covered* on which to overwrite a canonical profile. This is a bounded search, **not** a comprehensive SEC filing or all-issuer audit.
- The watchlist classifies **SpaceX as listed** under `SPCX`, not one of the 13 private profiles. Source linked in the watchlist to its June 2026 IPO closing announcement; no private-equity claim or ticker remapping made. Anthropic's *proposed* IPO does not warrant a unilateral status change without fresh official registration/listing proof.
- No valuation, audited revenue, financing amount or market cap estimated from unverified rumours; no generated profiles/articles, backlinks or ad settings changed.

**Outcome: SKIPPED — `NO_MATERIAL_PROFILE_CHANGE`, 0 profile edits.**

## Conflict / release handoff

Draft [#149](https://github.com/davidomarayt/compound/pull/149) owns the 16 Nov PIA/CGT canonical page correction; it is not touched. Other inspected open PRs include #127, #120, #119, #57 and #43. The new single group engineering [draft #150](https://github.com/davidomarayt/compound/pull/150) concerns **earnings source classification**, no overlapping article URL or financial figures. Specialist PRs are not production publication. Independent 06:30 QA should compare exact PR head/build/CI and report the distinction clearly.
