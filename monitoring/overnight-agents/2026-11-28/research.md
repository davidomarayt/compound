# Compound overnight research — 28 November 2026 (Europe/Dublin)

Production branch `claude/clever-babbage-uibieq` (GitHub Pages workflow `site`), base 9fbe32794fa9990341ff458730feb2c5bf742b0f (merge of #318). Read the runbook incl. 14 Nov efficiency gates, AGENTS.md, 12–27 Nov research/engineering records, tonight's discovery/content (on draft #319) and all 18 open PRs. No merges, no publishing.

## 5. Original Research — REVIEW-ONLY, distinct primary release

Fingerprint: `CSO-RSI-October-2026-release-2026-11-27|value-vs-volume-implied-price`. Source: [CSO Retail Sales Index October 2026 (Provisional) and September 2026 (Final)](https://www.cso.ie/en/releasesandpublications/ep/p-rsi/retailsalesindexoctober2026provisionalandseptember2026final/), "CSO statistical release, 27 November 2026, 11am" (fetched 28 Nov ~02:55 Dublin).

Deduplication: no overnight record (12–27 Nov), content file, title-index entry, Irish finance ledger (25–27 Nov) or open PR references the Retail Sales Index. Earlier CPI work (12 and 14 Nov) used the October CPI release; this uses a different release and does not reuse those figures.

Reader question: when the CSO says Irish shoppers spent 6.2% more than a year ago, how much of that was buying more, and how much was paying more?

CSO Table 1, seasonally adjusted, base 2021 = 100:

| Series | Volume Oct 2026 | Value Oct 2026 | Volume Oct 2025 | Value Oct 2025 | Volume y/y | Value y/y |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All businesses | 119.0 | 134.6 | 114.5 | 126.7 | +3.9% | +6.2% |
| Excl. motor trades | 117.0 | 131.5 | 113.2 | 124.2 | +3.3% | +5.9% |

Our derivation (not a CSO figure): implied retail price index = value index ÷ volume index.
- All businesses: 134.6 / 119.0 = 1.1311 (Oct 2026) vs 126.7 / 114.5 = 1.1066 (Oct 2025), so implied prices +2.2% in the year. Check: 1.062 / 1.039 − 1 = 2.2%.
- Excl. motor trades: 131.5 / 117.0 = 1.1239 vs 124.2 / 113.2 = 1.0972, so +2.4%.
- Month: all businesses Sep 2026 134.1 / 119.1 = 1.1259, so Oct implied prices +0.5% while volume fell 0.1%.

So roughly two thirds of the year's spending growth was more goods bought (3.9 of 6.2 points) and about one third was higher prices. Sector extremes as published (volume, y/y): Other Retail Sales +9.2%, Pharmaceuticals, Medical & Cosmetic +5.7%, Motor Trades +5.6%; Books, Newspapers & Stationery −8.1%, Bars −6.5%. Food, Beverages & Tobacco volume −2.4%.

Limits: October is provisional (early returns from sample retailers; four weeks 4–31 Oct). Indices are published rounded to one decimal, so the implied price figure carries about ±0.1 point of rounding error. The value/volume ratio is an implied retail deflator, not the CPI, and covers retail goods only (no rent, energy bills or services). The CSO has announced a coming revision to all volume indices for the new CPI classification. Fuel is a retail sector here, not household energy. No inference about household finances or real incomes is drawn from this alone.

Disposition: review-only. Possible use as one sourced paragraph in Irish money news or a cost-of-living explainer, subject to the content group's deduplication and editorial gate. Owner Original Research, priority low–medium, checked 28 Nov. No search or analytics metrics claimed.

Carried: 27 Nov CSO earnings-by-county brief (`CSO-DEA-2025`) still review-only.

## 6. Private Company Intelligence — SKIPPED / NO_MATERIAL_PROFILE_CHANGE

Listing status: Anthropic is listed (Nasdaq ANT, 19 Nov 2026) and SpaceX is listed (SPCX); both belong to the stocks workflow. OpenAI remains private. The [OpenAI news RSS feed](https://openai.com/news/rss.xml), fetched 28 Nov ~02:55 Dublin, still has no item newer than 24 Nov 13:00 GMT; the 24 Nov items were assessed on 25 Nov. Note for QA: there is no `monitoring/private-company-publications/2026-11-27.json` on the production branch (latest is 26 Nov), so the 06:43 publisher's 27 Nov output could not be checked from its ledger; not investigated further here to avoid duplicating that task. No profile edited; no estimate or rumour promoted to fact.
