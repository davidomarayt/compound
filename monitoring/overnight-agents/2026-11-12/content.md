# Compound overnight existing-content improvements — 2026-11-12

**Worker status:** Internal Linking = one narrow unmerged draft PR; Content Freshness = primary-source spot checks completed, no speculative correction. **Publishing branch:** `claude/clever-babbage-uibieq` (verified repository default at start). No production deployment or new article publication claimed.

## 3. Internal Linking Agent

- **Canonical source:** [Buying a Home in Ireland: Budget, Deposit and Upfront Costs](https://compound.ie/wealth/buying-home-budget-deposit-ireland/), source `content/wealth/buying-home-budget-deposit-ireland.md`, original date and `reviewed` both **2026-09-23** and preserved.
- **Canonical destination:** [House Deposit Calculator Ireland](https://compound.ie/house-deposit-calculator/), listed in `data/content-inventory.json` and fetched publicly on 2026-11-12; standard principal-home maximum LTV 90%, buy-to-let 70%, clearly a *standard mortgage-deposit calculation* rather than lender credit approval.
- **Reader need:** After explaining first/subsequent buyer 10% and buy-to-let 30% minimum deposits, readers can now open an applicable calculator rather than manually applying a rule. The added text explicitly excludes stamp duty, legal costs and emergency reserve from deposit cash and says the calculator does not certify loan approval.
- **PR:** [#115 — Connect Irish deposit-rule guide to existing deposit calculator](https://github.com/davidomarayt/compound/pull/115). Status when checked: **OPEN, DRAFT, NOT MERGED**; exact PR head `11599f3a960f59fa7d9fec14563271cef0a09e2b`. Target base: `claude/clever-babbage-uibieq`. One changed file and two inserted Markdown lines; no altered existing prose, dates, titles, tracked metadata, ads, consent, JS, URL routes or calculator code.
- **Preflight on edited source:** unique insertion anchor exactly once; one new link `/house-deposit-calculator/`; all previous article content matches after removing the inserted paragraph; frontmatter and existing `date`/`reviewed` fields unchanged. Public target page and parent guide were fetched independently; canonical target appears in the inventory.
- **Primary-source basis:** Central Bank of Ireland mortgage measures: https://www.centralbank.ie/consumer-hub/explainers/what-are-the-mortgage-measures ; standard LTV requires 10% deposit for first-time/subsequent homebuyers and 30% for buy-to-let. Reviewed 2026-11-12.
- **CI evidence at last worker checkpoint:** Vercel commit status *success* on this head; GitHub Actions `ci` workflow run [43125849624](https://github.com/davidomarayt/compound/actions/runs/43125849624) was **in_progress**. Its **test** job had completed successfully, while **performance** remained in progress. This is not yet complete CI or production publication. Independent QA must re-check the exact PR head, the completed suite, rendered link and any deployment before deciding readiness.
- **Risk/rollback:** low, one existing guide and one contextual link; revert the single change. No new content and no human review claimed. **No worker merge or live change.**

## 4. Content Freshness Agent

Verified sampled values against authoritative current pages on 2026-11-12. This is a spot check, **not a complete audit of all site content**.

| Existing canonical and claim | Original source checked | Result |
| --- | --- | --- |
| `/wealth/buying-home-budget-deposit-ireland/`: standard 10% owner-occupier/30% buy-to-let mortgage deposit | [Central Bank mortgage measures](https://www.centralbank.ie/consumer-hub/explainers/what-are-the-mortgage-measures) | Consistent; no correction |
| Same article: residential stamp duty 1% up to €1m, 2% on €1m–€1.5m band, 6% above €1.5m | [Revenue residential Stamp Duty rates](https://www.revenue.ie/en/property/stamp-duty/property/stamp-duty-property/rates.aspx) | Consistent; no correction |
| `/wealth/investment-tax-ireland/`: 38% investment fund tax for qualifying individual funds from 1 January 2026 | [Revenue eBrief 016/26, 22 January 2026](https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-0162026.aspx) | Consistent for relevant fund regime; no blanket claim for all products |
| Same article: Irish-resident individual DIRT 33% | [Revenue DIRT guidance, published 24 April 2026](https://www.revenue.ie/en/additional-incomes/dirt/what-dirt-rate-is-applicable.aspx) | Consistent; no correction |
| `/wealth/pension-vs-investing-ireland/`: employee pension age-related relief ceilings and €115,000 earnings cap | [Revenue pension tax relief limits, published 15 October 2026](https://www.revenue.ie/en/jobs-and-pensions/pension/relief/tax-relief-limits.aspx) | Consistent; no correction |

### Deferred high-priority factual review

`/wealth/personal-investment-account-ireland/` source has `reviewed: 2026-11-07` but still displays “Last checked: 6 October 2026” within the article body; other wording refers generically to a forthcoming Finance Bill despite the **19 October 2026 Finance (No. 2) Bill**. This is a candidate for an evidence-backed consolidation of the *existing* PIA guide after reading the official bill and checking against new existing PIA pages. Do not quietly change the review date without the actual substantive review, and do not treat a Bill as enacted. Sources for follow-up included in `discovery.md`. Not edited today to keep PR #115 narrow.

## Publication and advertising controls

Existing standard-ad publisher policy remains intact; no ad, consent, privacy, author or editor-approval field was changed. Recent merged PR #113 separately addressed standard advertising on articles and covered profiles; this worker did not independently validate an end-to-end production ad slot fill and does not claim AdSense policy clearance or that every impression receives an ad.

**Run outcome:** PR opened **1**; new articles **0**; content updates merged **0**; public URLs verified as changed **0**. The scheduled QA agent owns the merge/deploy verification decision.
