# Compound independent Editor-in-Chief QA — 27 November 2026 (Europe/Dublin)

Automated QA, not human editorial review. Run started 06:17 Dublin; merges at ~06:21, `site` deploy finished 06:27, live checks completed after an API interruption (resumed 08:35). Production branch confirmed as `claude/clever-babbage-uibieq` (site.yml push target), base 1f4c70048a8dc2c83451e8b381e3b402c944d346. Read AGENTS.md, docs/overnight-agents.md and all four dated reports, which the workers committed on their PR branches: [discovery](discovery.md) and [content](content.md) via #304, [research](research.md) and [engineering](engineering.md) via #305; all four are now on production through those merges. No settings, secrets, accounts, ad placement or consent controls changed.

## Role outcomes (from worker reports, cross-checked)

| Role | Outcome |
| --- | --- |
| Technical SEO (discovery) | Changed: #304, 3 broken/legacy raw-HTML links fixed + link test extended to `href="/…"`. Merged, verified live. /stocks/mat/ 404 from the Mattel article flagged, not changed. |
| Content Gap | Review-only; backlog updated, no new page. |
| Internal Linking | Changed: #304, KickstartSaver article links DIRT, regular-savings and emergency-fund calculators (+ related_tools). Merged, verified live. |
| Content Freshness | Changed: #304, one sourced sentence citing Bank of Ireland's own €76.85 / €51.49 example. Revenue CGT checked (no change). MyFutureFund BLOCKED_SOURCE_FETCH again. |
| Original Research | Review-only: CSO Distribution of Earnings by Gender and County 2025 brief; nothing published. |
| Private Company Intelligence | NO_MATERIAL_PROFILE_CHANGE. |
| Technical SEO (engineering) | Changed: #305, seven article bodies no longer render extra `<h1>`s + sitewide guard test. Merged, verified live. |
| UX & Conversion | Same PR #305 (heading outline). No conversion figures claimed. |
| Revenue Optimisation | BLOCKED_DATA_ACCESS (backoff to 28 Nov). No query. |
| Editor-in-Chief QA | 2 approved, 2 merged, deployed, verified live; 0 held. |

## Release evidence

- [PR #304](https://github.com/davidomarayt/compound/pull/304) — head a5670a48a40880202725ec9660b8ebed0f305fc8. Diff checked: 3 link-target substitutions, 3 contextual calculator links, `related_tools` extended, one sentence of sourced context; publication date unchanged, no reviewed date added. Bank of Ireland KickstartSaver page fetched by QA 27 Nov: states €76.85 gross / ~€51.49 net for the €250-a-month example, 5% AER to €5,000, 2% above — matches. PR CI `test` + `performance` successful on exact head (runs 45916461671, 45916487606). Marked ready, merged with expected head → ba576bfa8be3c352c8254e4a681f5f511a8b8cf5.
- [PR #305](https://github.com/davidomarayt/compound/pull/305) — head 164407c50666ab3b0fc28acb850ba718c3e53d01. Diff checked: five repeated title lines removed, 13 `# ` headings demoted to `##`; no body text, title, URL, date, metadata or template change. Template `article.html`/`series_article.html` already render the title as `<h1>`. PR CI `test` + `performance` successful on exact head (runs 45935653154, 45935657737). No file overlap with #304. Merged with expected head → b358e27509b7d2175291523b86d1776cc928a6c3.
- Combined check: both branches merged locally onto 1f4c7004 with no conflicts; full `pytest -q` 431 passed + 2 subtests; `node tests/tools_arithmetic.cjs` passed.
- Licences/duplication: no images, no new articles; one new external source citation (Bank of Ireland's own product page, already the article's subject).
- Rollback: a normal revert PR of either merge commit; changes are independent. Never force.

## Deployment and live verification

- [site run 45951315712](https://github.com/davidomarayt/compound/actions/runs/45951315712) on b358e275: build, deploy (06:24:42 UTC), verify-finance-discovery, verify-live and mobile-audit all successful. The #304 site run 45951296085 was cancelled by concurrency; the later run deploys both.
- Public canonical pages fetched after deploy (HTTP 200, self-canonical, exactly one `<h1>`): the six pension chapters, /news/manchester-city-114-financial-rule-breaches-explained/ (was 13 `<h1>`), /life/, /insurance/, /life/commute-time-ireland-hidden-cost/, /news/bank-of-ireland-5-percent-savings-account/.
- New link targets live: /life/ → /news/workplace-stress-ireland-job-design-wellbeing-2026/ (200); /insurance/ → /news/health-insurance-price-rises-benefit-cuts-ireland/ (200); commute article → /life/remote-working-ireland-rights-request/ (200); KickstartSaver article → /dirt-calculator/, /regular-savings-calculator/, /emergency-fund-calculator/ (all 200) and shows the €76.85 sentence; /dirt-calculator/ now lists the article (reverse link).
- Ads/consent: every page above still carries the standard ad loader and consent markup in the served HTML; neither PR touched templates, ad or consent code. No ad-fill or compliance claim.

**Totals:** approved 2; merged 2; deployed 2; verified live 2; held 0 of tonight's candidates; skipped 0. Older open PRs were not part of tonight's run and were left untouched. Open backlog for editors: /stocks/mat/ 404 link in the Mattel article.
