# Compound independent Editor-in-Chief QA — 26 November 2026 (Europe/Dublin)

Automated QA, not human editorial review. Run started late (scheduled ~06:17; the first attempt was cut off by an API error at 06:17 and resumed at 07:35 Dublin). Production branch confirmed as `claude/clever-babbage-uibieq` (site.yml push target), base caf84557f698837f1021e8a345a274a85ba6ebd3. Read AGENTS.md, docs/overnight-agents.md and all four dated reports. The worker reports were committed on their PR branches, not production: [discovery](discovery.md) and [content](content.md) via #289, [research](research.md) and [engineering](engineering.md) via #290; all four are now on production through those merges. No settings, secrets, accounts, ad placement or consent controls changed.

## Role outcomes (from worker reports, cross-checked)

| Role | Outcome |
| --- | --- |
| Technical SEO (discovery) | Changed: #289, ten comma-truncated calculator labels in seven tools. Merged, verified live. |
| Content Gap | Review-only; backlog updated, no new page. |
| Internal Linking | Review-only recommendation (KickstartSaver article → DIRT / regular-savings / emergency-fund calculators). Not staged. |
| Content Freshness | Review-only. Revenue DIRT 33% and HEA €2,350 checked; MyFutureFund check BLOCKED_SOURCE_FETCH (not verified). |
| Original Research | Review-only: CSO Fuel Excise Clearances Sept 2026 brief; nothing published. |
| Technical SEO (engineering) | Changed: #290, 54 legacy /happiness/ internal links → canonical /life/ URLs in 20 files, plus two 404 links fixed. Merged, verified live. |
| UX & Conversion | Same PR #290 (404 fixes). No conversion figures claimed. |
| Revenue Optimisation | BLOCKED_DATA_ACCESS (GA4/AdSense backoff to 28 Nov). No query. |
| Private Company Intelligence | No item in tonight's records; not assessed here. |
| Editor-in-Chief QA | 2 approved, 2 merged, deployed, verified live; 0 held. |

## Release evidence

- [PR #289](https://github.com/davidomarayt/compound/pull/289) — head a0b313b54d3055928df29fa509c5950176f81d81. Diff: ten YAML labels quoted (quotes only; defaults/min/max unchanged), new `tests/test_tool_label_flow_map_commas.py`, two report files. PR CI `test` + `performance` successful on that exact head (runs 45728198222, 45728203765). Marked ready, merged with expected head → merge 45888e5f4a68518b5a8f152bafd62c9c0a916780. Its own site run 45776999183 was cancelled by the next merge's run (concurrency), which deploys both.
- [PR #290](https://github.com/davidomarayt/compound/pull/290) — head faae55a8eefc00e6f576e97cbd74a4d4f8a0a31b. Diff independently checked: every changed content line is a pure link-target substitution (/happiness/<slug>/ → /life/<slug>/, /tools/glp-1-cost/ → /glp1-cost-calculator-ireland/, /wealth/investing-in-ireland/ → /wealth/how-to-start-investing-in-ireland/); no anchor text, metadata, dates, canonical, robots or template change. New `tests/test_content_internal_links.py`. PR CI `test` + `performance` successful on exact head (runs 45745697137, 45745731153). No file overlap with #289. Merged with expected head → merge 9db5c45804d1a6381d236ba529a8d6cc143334bb.
- Combined check: both branches merged locally onto caf84557 with no conflicts; full `pytest -q` 427 passed + 2 subtests; `node tests/tools_arithmetic.cjs` passed.
- Licences/duplication: no images, no new articles, no new sources. Duplicate branch `agents/discovery-content-2026-11-26-comma-labels` (commit 4d8caaf9, already contained in #289) has no PR; left in place, safe to delete.
- Rollback: a normal revert PR of either merge commit; changes are independent. Never force.

## Deployment and live verification

- [site run 45777005985](https://github.com/davidomarayt/compound/actions/runs/45777005985) on 9db5c458: build, deploy (07:43:41 UTC) and verify-finance-discovery, verify-live and mobile-audit all successful (run concluded success).
- Public canonical pages fetched after deploy (HTTP 200, self-canonical unchanged): /college-cost-calculator/, /lifetime-cost-calculator/, /house-buying-costs-calculator/, /first-home-scheme-calculator/, /rent-vs-buy-calculator/, /mortgage-switch-calculator/, /myfuturefund-calculator/ — all now show the full comma-bearing labels (e.g. "Monthly food, bills and personal costs", "Professional, moving & setup costs").
- /life/how-to-get-out-of-a-rut/ and /life/how-to-be-happier-evidence-ireland/: 0 links to /happiness/ (previously 3+ on the first). /wealth/eli-lilly-foundayo-europe-approval-glp1-2026/ links /glp1-cost-calculator-ireland/ (200). /news/irish-young-savers-investing-survey-2026/ links /wealth/how-to-start-investing-in-ireland/ (200); old 404 link gone.
- Ads/consent: every page above still carries the standard ad loader and consent markup in the served HTML; neither PR touched templates, ad or consent code. No ad-fill or compliance claim.

**Totals:** approved 2; merged 2; deployed 2; verified live 2; held 0 of tonight's candidates; skipped 0. Older open PRs (#281, #274, #270, #269, #254, #237, #235, #212, #188, #176, #175, #168, #157) were not part of tonight's run and were left untouched.
