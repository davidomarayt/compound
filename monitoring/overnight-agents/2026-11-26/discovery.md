# Compound overnight discovery — 2026-11-26 (Europe/Dublin)

Production branch confirmed: `claude/clever-babbage-uibieq` (site.yml push target), base caf84557f698837f1021e8a345a274a85ba6ebd3. Read AGENTS.md, the runbook incl. 14 Nov efficiency gates, 20–25 Nov records and open PRs. Roster per routine: Technical SEO, Content Gap, Internal Linking, Content Freshness. Search Console Growth removed; no GSC/GA4 calls.

## 1. Technical SEO — measurable change staged (draft PR #289)

Followed up 25 Nov's open item ("further comma-bearing labels ... candidates for later verification"). Instead of spot checks, parsed every tool in `content/tools.yml` and listed dicts with stray null non-identifier keys, which is the YAML flow-map comma-truncation signature. Found exactly ten, in seven calculators: first-home-scheme (charges_to_year10), rent-vs-buy (buying_costs, owner_fixed_annual), house-buying-costs (other_costs, moving_setup_costs), myfuturefund (assume_opt_in), college-cost (student_living, setup_cost), mortgage-switch (switching_costs), lifetime-cost (leisure_monthly). Other content YAML files scanned: none.

Live evidence (public text snapshots fetched 26 Nov, HTTP 200): college-cost shows "Monthly food €" and "Books €"; lifetime-cost "Leisure €"; house-buying-costs "Professional —"; first-home-scheme "Illustrative service charges —". The other five are advanced-mode fields not present in the text snapshot; source parse proves the same defect.

[PR #289](https://github.com/davidomarayt/compound/pull/289) (draft) quotes the ten labels (10 lines, quotes only) and adds `tests/test_tool_label_flow_map_commas.py`: a sitewide guard over all tools plus exact label and unchanged-default assertions. Head 4d8caaf9b0941517b4ced2a269e901c2ba057e58. Locally: new test fails on base (2 failed) and passes on head; full `pytest -q` 423 passed + 2 subtests; `node tests/tools_arithmetic.cjs` passed. Local `compound build` stops on a pre-existing News image requirement (ireland-tax-statistics-2025-usc-fell, needs CI image cache), so static build is left to CI. `tool.html` renders field/result labels directly. No overlap with open #274/#270/#175 hunks (checked). Raw canonical/robots/sitemap not refetched (direct HTTP blocked); no index or canonical changes.

## 2. Content Gap — review-only, backlog updated

Deduplicated against 12–25 Nov discovery/content records and open PRs. No new page proposed. Backlog (fingerprint | source | checked | owner | priority | disposition):

- `/<7 calculators>/|comma-truncated-labels` | tools.yml parse + live snapshots | 26 Nov | Technical SEO | HIGH | STAGED #289. Closes 25 Nov MEDIUM item.
- `/news/bank-of-ireland-5-percent-savings-account/|savings-tool-links` | article source (published 25 Nov) | 26 Nov | Internal Linking | MEDIUM | RECOMMENDED, not staged (see content.md).
- `/myfuturefund-calculator/|2026-rules-freshness` | myfuturefund.ie, citizensinformation.ie, gov.ie | 26 Nov | Content Freshness | MEDIUM | BLOCKED_SOURCE_FETCH; retry from a session that can reach those sites. #175 still open on the same tool's guidance; do not duplicate.
- Carried, unchanged: #254 shares CGT, #168 rent credit, #175 MyFutureFund matching, #270 PIA, #274 fuel. No new query volumes, rankings or traffic claimed.

See [content.md](content.md).
