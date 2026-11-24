# Compound overnight content — 2026-11-24 (Europe/Dublin)

Publishing/default branch `claude/clever-babbage-uibieq` confirmed before work. One substantive [draft PR #267](https://github.com/davidomarayt/compound/pull/267), exact head `f4593494147aa223a3b222d7b6cd24eb9eb24677`, creation base `2256f30ddb40da9d4ab7523c13e32ce870e4b8f8`.

## 3. Internal Linking — review-only

Public [pension lump-sum guide](https://compound.ie/wealth/pension-lump-sum-tax-ireland/) links to [calculator](https://compound.ie/pension-lump-sum-calculator-ireland/), and calculator guide source links back to the original guide and pension-projection calculator. Existing two-way guide/calculator navigation verified through public text/source; no forced redundant links. Investment tax and CGT pages likewise already link to relevant tools. No additional links staged; no new live links claimed. Raw HTML canonical and rendered regression checks are pending independent QA.

## 4. Content Freshness — measurable change staged

Revenue's [Taxation of retirement lump-sums](https://www.revenue.ie/en/jobs-and-pensions/pension/private/retirement-lump-sums.aspx), published **15 October 2026**, checked 24 November, confirms cumulative lifetime €200,000 tax-free allowance, 20% band to €500,000 and PAYE on the excess. Existing calculator help and guide already contain correct thresholds; actual public field and result labels were truncated to €500. No assertion that calculation results are wrong. Verified root cause in `content/tools.yml`: unquoted comma in 3 YAML flow-map labels.

PR #267 quotes exactly 3 labels (marginal_rate, above_500, marginal_tax) and adds `tests/test_pension_lump_sum_labels.py`. No tax formula, defaults, route, source/review date or ad/consent/other settings changed. Other checks: [CGT guide](https://compound.ie/wealth/capital-gains-tax-ireland/) and [investment-tax guide](https://compound.ie/wealth/investment-tax-ireland/) agree with [Revenue eBrief 142/26](https://www.revenue.ie/en/tax-professionals/ebrief/2026/no-1422026.aspx), 6 October 2026; PIA centre appropriately warns scheme is not yet law and points to pending parliamentary stages. No separate company/earnings claims changed: 23 Nov publisher ledgers and completed/active PRs inspected, avoid overlap. No new issuer-level factual correction independently qualified in this limited pass.

## Validation and PR handoff

Source preflight: each replacement anchor matched once; exact diff only two intended files (3 additions/3 deletions in tools.yml; 24-line regression). Local PyYAML minimal-flow-map reproduction passed for all 3 before/after labels. This is not a full exact-head test run. GitHub independently re-read PR state and diff: OPEN / DRAFT / UNMERGED; mergeable true at check (not an approval). Exact-head [PR CI 45295514482](https://github.com/davidomarayt/compound/actions/runs/45295514482) and [push CI 45295496622](https://github.com/davidomarayt/compound/actions/runs/45295496622) in progress at checkpoint; full pytest, static build, rendered controls and canonical/metadata checks not yet confirmed. No live deployment by worker. Low risk, label-only; revert 2-file change to roll back. Independent QA must recheck exact head and latest base, completed CI, generated tool page labels, existing formula/defaults, links, mobile, sitemap/canonical and ad/consent as applicable. Current public page still reflects prior build. No production settings, secrets, advertising placements, consent, tracking or other automations altered. Standard ads remain independent of human review. No actual ad-fill/compliance claim.

**Totals:** one substantive draft PR, zero new pages, zero worker merges, zero deployments, zero changed pages verified live.
